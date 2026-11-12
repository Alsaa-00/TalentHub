from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferDecision, OfferOut
from app.services.offer_service import OfferService
from app.repositories.offer_repository import OfferRepository
from app.utils.dependencies import (
    get_current_user,
    get_current_student,
    get_current_company,
    get_current_coordinator,
)

router = APIRouter(prefix="/offers", tags=["Offers"])

@router.post("", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
def issue_placement_offer(
    req: OfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR-8.1: Issue a formal campus placement offer to an INTERVIEWED candidate."""
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized to issue offers.")

    offer = OfferService.issue_offer(db, req)
    return OfferService.format_offer_out(offer)

@router.get("/me", response_model=List[OfferOut])
def get_my_offers(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """Student views all job offers received."""
    offers = OfferRepository.get_by_student(db, current_student.id)
    return [OfferService.format_offer_out(o) for o in offers]

@router.get("/company", response_model=List[OfferOut])
def get_company_offers(
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    """Company representative views all offers issued by their company."""
    offers = OfferRepository.get_by_company(db, current_company.id)
    return [OfferService.format_offer_out(o) for o in offers]

@router.get("", response_model=List[OfferOut])
def list_all_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    coordinator: User = Depends(get_current_coordinator),
):
    """Placement coordinator views all offers across companies."""
    offers = OfferRepository.get_all(db, skip=skip, limit=limit)
    return [OfferService.format_offer_out(o) for o in offers]

@router.put("/{offer_id}/decision", response_model=OfferOut)
def record_offer_decision(
    offer_id: int,
    req: OfferDecision,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """FR-8.4 & FR-8.5: Student accepts or declines an offer. Accepting excludes student from other drives."""
    offer = OfferService.decide_offer(db, current_student, offer_id, req.decision)
    return OfferService.format_offer_out(offer)

@router.get("/{offer_id}", response_model=OfferOut)
def get_offer_by_id(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single offer details."""
    offer = OfferRepository.get_by_id(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found.")
    return OfferService.format_offer_out(offer)
