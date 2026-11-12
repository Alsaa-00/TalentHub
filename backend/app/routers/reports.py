from typing import List
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.reports import PlacementStatisticsOut, PlacedStudentOut
from app.services.report_service import ReportService
from app.utils.dependencies import get_current_user, get_current_coordinator

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/placement-statistics", response_model=PlacementStatisticsOut)
def get_placement_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve campus placement metrics: percentage placed, packages, branch breakdown."""
    return ReportService.get_placement_statistics(db)

@router.get("/placed-students", response_model=List[PlacedStudentOut])
def get_placed_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all students who have secured and accepted offers this season."""
    return ReportService.get_placed_students(db)

@router.get("/job/{job_id}/export-csv")
def export_job_applicants_csv(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR-9.3: Export the applicant list and shortlisting results of a drive as a CSV file."""
    try:
        csv_data = ReportService.export_job_shortlist_csv(db, job_id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=job_{job_id}_shortlist.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
