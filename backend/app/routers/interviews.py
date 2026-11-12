from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.models.interview import InterviewSlot
from app.schemas.interview import (
    InterviewSlotCreate,
    InterviewSlotUpdate,
    InterviewSlotOut,
)
from app.services.interview_service import InterviewService
from app.repositories.interview_repository import InterviewRepository
from app.repositories.application_repository import ApplicationRepository
from app.utils.dependencies import (
    get_current_user,
    get_current_student,
    get_current_company,
    get_current_coordinator,
)

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("", response_model=InterviewSlotOut, status_code=status.HTTP_201_CREATED)
def schedule_interview(
    req: InterviewSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR-7.1: Schedule an interview round for a shortlisted candidate."""
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized to schedule interviews.")

    slot = InterviewService.schedule_interview(db, req)
    return InterviewService.format_interview_out(slot)

@router.get("/me", response_model=List[InterviewSlotOut])
def get_my_interview_schedule(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """FR-7.4: Student views their upcoming and past interview schedules."""
    slots = InterviewRepository.get_by_student(db, current_student.id)
    return [InterviewService.format_interview_out(s) for s in slots]

@router.get("/company", response_model=List[InterviewSlotOut])
def get_company_interviews(
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    """Company representative views all interview rounds scheduled for their company."""
    slots = InterviewRepository.get_by_company(db, current_company.id)
    return [InterviewService.format_interview_out(s) for s in slots]

@router.get("", response_model=List[InterviewSlotOut])
def list_all_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    coordinator: User = Depends(get_current_coordinator),
):
    """Placement coordinator views all campus interview slots."""
    slots = InterviewRepository.get_all(db, skip=skip, limit=limit)
    return [InterviewService.format_interview_out(s) for s in slots]

@router.put("/{interview_id}", response_model=InterviewSlotOut)
def record_interview_result(
    interview_id: int,
    req: InterviewSlotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR-7.3: Record interview outcome (Passed / Failed) and feedback notes."""
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    slot = InterviewService.record_result(db, interview_id, req)
    return InterviewService.format_interview_out(slot)

@router.get("/{interview_id}", response_model=InterviewSlotOut)
def get_interview_slot(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single interview round details."""
    slot = InterviewRepository.get_by_id(db, interview_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Interview slot not found.")
    return InterviewService.format_interview_out(slot)
