from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.schemas.dashboard import StudentDashboardOut, CompanyDashboardOut, AdminDashboardOut
from app.services.report_service import ReportService
from app.utils.dependencies import (
    get_current_student,
    get_current_company,
    get_current_coordinator,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/student", response_model=StudentDashboardOut)
def get_student_dashboard(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """Retrieve summarized dashboard statistics for the logged-in student."""
    return ReportService.get_student_dashboard(db, current_student)

@router.get("/company", response_model=CompanyDashboardOut)
def get_company_dashboard(
    db: Session = Depends(get_db),
    current_company: Company = Depends(get_current_company),
):
    """Retrieve recruitment metrics for the logged-in company."""
    return ReportService.get_company_dashboard(db, current_company)

@router.get("/admin", response_model=AdminDashboardOut)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    coordinator: User = Depends(get_current_coordinator),
):
    """Retrieve overall campus placement statistics for the coordinator."""
    return ReportService.get_admin_dashboard(db)
