from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.schemas.student import StudentOut, StudentUpdate
from app.services.student_service import StudentService
from app.utils.dependencies import get_current_user, get_current_student, get_current_coordinator

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=List[StudentOut])
def get_all_students(
    branch: Optional[str] = Query(None, description="Filter by branch code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List students with optional branch filtering. (Accessible to Admin & Company)"""
    return StudentService.list_students(db, skip=skip, limit=limit, branch=branch)

@router.get("/me", response_model=StudentOut)
def get_my_profile(
    current_student: Student = Depends(get_current_student),
):
    """FR-2.5: Student views their own academic profile and eligibility metrics."""
    return current_student

@router.put("/me", response_model=StudentOut)
def update_my_profile(
    req: StudentUpdate,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """Student updates their profile details (phone, skills, resume)."""
    return StudentService.update_profile(db, current_student, req)

@router.get("/{student_id}", response_model=StudentOut)
def get_student_by_id(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get student details by ID."""
    return StudentService.get_student_by_id(db, student_id)

@router.put("/{student_id}", response_model=StudentOut)
def update_student_admin(
    student_id: int,
    req: StudentUpdate,
    db: Session = Depends(get_db),
    coordinator: User = Depends(get_current_coordinator),
):
    """FR-2.3: Placement Coordinator updates student record (CGPA, backlogs, etc.)."""
    student = StudentService.get_student_by_id(db, student_id)
    return StudentService.update_profile(db, student, req)
