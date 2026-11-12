from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.models.application import Application, ApplicationStatus
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationOut,
    ShortlistRunResult,
)
from app.services.application_service import ApplicationService
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.utils.dependencies import (
    get_current_user,
    get_current_student,
    get_current_company,
    get_current_coordinator,
)

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_for_job(
    req: ApplicationCreate,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """FR-5.1: Student applies for an eligible campus placement job drive."""
    return ApplicationService.apply_for_job(db, current_student, req.job_id)

@router.get("/me", response_model=List[ApplicationOut])
def get_my_applications(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """FR-5.5: Student views all their applications with statuses and timelines."""
    return ApplicationRepository.get_by_student(db, current_student.id)

@router.get("/job/{job_id}", response_model=List[ApplicationOut])
def get_job_applications(
    job_id: int,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """View all applicants for a specific recruitment drive."""
    job = JobRepository.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if current_user.role == "company" and (not current_user.company or current_user.company.id != job.company_id):
        raise HTTPException(status_code=403, detail="Access denied: You can only view applicants for your company's drives.")

    return ApplicationRepository.get_by_job(db, job_id, status=status_filter)

@router.post("/job/{job_id}/shortlist", response_model=ShortlistRunResult)
def run_shortlisting(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR-6.1 to FR-6.5: Automated batch shortlisting run. Evaluates all APPLIED candidates against drive criteria."""
    job = JobRepository.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if current_user.role == "company" and (not current_user.company or current_user.company.id != job.company_id):
        raise HTTPException(status_code=403, detail="Unauthorized.")
    elif current_user.role not in ["company", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    return ApplicationService.shortlist_students(db, job_id)

@router.put("/{application_id}/status", response_model=ApplicationOut)
def update_application_status(
    application_id: int,
    req: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update application workflow status with state transition validation."""
    if current_user.role not in ["company", "admin"]:
        raise HTTPException(status_code=403, detail="Only companies or coordinators can advance applicant statuses.")

    return ApplicationService.update_application_status(db, application_id, req.status, req.ineligibility_reason)

@router.get("/{application_id}", response_model=ApplicationOut)
def get_application_by_id(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full details of an application."""
    app = ApplicationRepository.get_by_id(db, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")

    # Authorization
    if current_user.role == "student" and app.student_id != current_user.student.id:
        raise HTTPException(status_code=403, detail="Access denied.")
    if current_user.role == "company" and app.job.company_id != current_user.company.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return app
