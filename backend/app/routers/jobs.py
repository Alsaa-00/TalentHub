from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.student import Student
from app.models.job import JobListing
from app.schemas.job import (
    JobListingCreate,
    JobListingUpdate,
    JobListingOut,
    JobListingWithEligibility,
)
from app.services.job_service import JobService
from app.services.eligibility_service import EligibilityService
from app.repositories.application_repository import ApplicationRepository
from app.utils.dependencies import (
    get_current_user,
    get_current_student,
    get_current_company,
    get_current_coordinator,
)

router = APIRouter(prefix="/jobs", tags=["Job Listings"])

@router.post("", response_model=JobListingOut, status_code=status.HTTP_201_CREATED)
def create_job(
    req: JobListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new campus recruitment drive job listing."""
    if current_user.role == "company" and current_user.company:
        company_id = current_user.company.id
    elif current_user.role == "admin":
        # Coordinator creating a job listing: requires first company or company exists
        company_id = 1
        if not db.query(Company).filter(Company.id == company_id).first():
            raise HTTPException(status_code=400, detail="No registered companies exist to associate with job.")
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only registered companies or placement coordinators can create job listings."
        )

    job = JobService.create_job(db, company_id, req)
    return JobListingOut(
        id=job.id,
        company_id=job.company_id,
        company_name=job.company.name if job.company else None,
        role=job.role,
        description=job.description,
        season=job.season,
        package_lpa=job.package_lpa,
        min_cgpa=job.min_cgpa,
        max_backlogs=job.max_backlogs,
        drive_date=job.drive_date,
        location=job.location,
        is_open=job.is_open,
        allowed_branches=job.allowed_branches,
        created_at=job.created_at,
        total_applications=len(job.applications),
    )

@router.get("", response_model=List[JobListingOut])
def list_jobs(
    is_open: Optional[bool] = Query(None, description="Filter by open/closed status"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List job listings with company details."""
    if company_id:
        jobs = JobService.list_jobs_by_company(db, company_id)
    elif current_user.role == "company" and current_user.company:
        # FR-1.4: Company rep sees only their company's drives by default
        jobs = JobService.list_jobs_by_company(db, current_user.company.id)
    else:
        jobs = JobService.list_jobs(db, is_open=is_open)

    return [
        JobListingOut(
            id=j.id,
            company_id=j.company_id,
            company_name=j.company.name if j.company else None,
            role=j.role,
            description=j.description,
            season=j.season,
            package_lpa=j.package_lpa,
            min_cgpa=j.min_cgpa,
            max_backlogs=j.max_backlogs,
            drive_date=j.drive_date,
            location=j.location,
            is_open=j.is_open,
            allowed_branches=j.allowed_branches,
            created_at=j.created_at,
            total_applications=len(j.applications),
        )
        for j in jobs
    ]

@router.get("/student/eligible", response_model=List[JobListingWithEligibility])
def list_jobs_for_student(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student),
):
    """FR-4.6 & FR-4.7: Returns all drives with dynamic eligibility calculation & breakdown for logged-in student."""
    return JobService.list_jobs_with_eligibility_for_student(db, current_student)

@router.get("/{job_id}", response_model=JobListingOut)
def get_job_by_id(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single job listing details."""
    job = JobService.get_job_by_id(db, job_id)
    return JobListingOut(
        id=job.id,
        company_id=job.company_id,
        company_name=job.company.name if job.company else None,
        role=job.role,
        description=job.description,
        season=job.season,
        package_lpa=job.package_lpa,
        min_cgpa=job.min_cgpa,
        max_backlogs=job.max_backlogs,
        drive_date=job.drive_date,
        location=job.location,
        is_open=job.is_open,
        allowed_branches=job.allowed_branches,
        created_at=job.created_at,
        total_applications=len(job.applications),
    )

@router.put("/{job_id}", response_model=JobListingOut)
def update_job(
    job_id: int,
    req: JobListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a job listing. (Allowed only for company owner or coordinator)"""
    job = JobService.get_job_by_id(db, job_id)
    if current_user.role == "company" and (not current_user.company or current_user.company.id != job.company_id):
        raise HTTPException(status_code=403, detail="You can only edit drives for your own company.")
    elif current_user.role not in ["company", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    updated = JobService.update_job(db, job, req)
    return JobListingOut(
        id=updated.id,
        company_id=updated.company_id,
        company_name=updated.company.name if updated.company else None,
        role=updated.role,
        description=updated.description,
        season=updated.season,
        package_lpa=updated.package_lpa,
        min_cgpa=updated.min_cgpa,
        max_backlogs=updated.max_backlogs,
        drive_date=updated.drive_date,
        location=updated.location,
        is_open=updated.is_open,
        allowed_branches=updated.allowed_branches,
        created_at=updated.created_at,
        total_applications=len(updated.applications),
    )

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a job listing."""
    job = JobService.get_job_by_id(db, job_id)
    if current_user.role == "company" and (not current_user.company or current_user.company.id != job.company_id):
        raise HTTPException(status_code=403, detail="You can only delete drives for your own company.")
    elif current_user.role not in ["company", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    JobService.delete_job(db, job_id)
    return {"message": "Job listing deleted successfully."}
