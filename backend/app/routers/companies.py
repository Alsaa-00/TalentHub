from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.schemas.company import CompanyOut, CompanyCreate, CompanyUpdate
from app.services.company_service import CompanyService
from app.services.auth_service import AuthService
from app.schemas.auth import CompanyRegisterRequest
from app.utils.dependencies import get_current_user, get_current_company, get_current_coordinator

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=List[CompanyOut])
def get_all_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all registered companies visiting the campus."""
    return CompanyService.list_companies(db, skip=skip, limit=limit)

@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company_by_coordinator(
    req: CompanyRegisterRequest,
    db: Session = Depends(get_db),
    coordinator: User = Depends(get_current_coordinator),
):
    """FR-3.1: Placement Coordinator registers a company."""
    _, company = AuthService.register_company(db, req)
    return company

@router.get("/me", response_model=CompanyOut)
def get_my_company_profile(
    current_company: Company = Depends(get_current_company),
):
    """Company representative views their own company profile."""
    return current_company

@router.put("/me", response_model=CompanyOut)
def update_my_company_profile(
    req: CompanyUpdate,
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    """Company representative updates their profile information."""
    return CompanyService.update_profile(db, current_company, req)

@router.get("/{company_id}", response_model=CompanyOut)
def get_company_by_id(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get company profile by ID."""
    return CompanyService.get_company_by_id(db, company_id)
