from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.job import JobListing
from app.models.student import Student
from app.repositories.job_repository import JobRepository
from app.repositories.application_repository import ApplicationRepository
from app.schemas.job import JobListingCreate, JobListingUpdate, JobListingWithEligibility, JobListingOut
from app.services.eligibility_service import EligibilityService

class JobService:
    @staticmethod
    def create_job(db: Session, company_id: int, req: JobListingCreate) -> JobListing:
        job = JobListing(
            company_id=company_id,
            role=req.role.strip(),
            description=req.description,
            season=req.season.strip(),
            package_lpa=round(req.package_lpa, 2),
            min_cgpa=round(req.min_cgpa, 2),
            max_backlogs=req.max_backlogs,
            drive_date=req.drive_date.strip(),
            location=req.location,
            is_open=req.is_open,
        )
        return JobRepository.create(db, job, branches=req.allowed_branches)

    @staticmethod
    def get_job_by_id(db: Session, job_id: int) -> JobListing:
        job = JobRepository.get_by_id(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job listing with ID {job_id} not found."
            )
        return job

    @staticmethod
    def update_job(db: Session, job: JobListing, req: JobListingUpdate) -> JobListing:
        # Check rule FR-3.5: Eligibility criteria editable only before drive date
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if job.drive_date < today_str and (req.min_cgpa is not None or req.max_backlogs is not None or req.allowed_branches is not None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Eligibility criteria cannot be modified after the recruitment drive date has passed."
            )

        if req.role is not None:
            job.role = req.role.strip()
        if req.description is not None:
            job.description = req.description
        if req.season is not None:
            job.season = req.season.strip()
        if req.package_lpa is not None:
            job.package_lpa = round(req.package_lpa, 2)
        if req.min_cgpa is not None:
            job.min_cgpa = round(req.min_cgpa, 2)
        if req.max_backlogs is not None:
            job.max_backlogs = req.max_backlogs
        if req.drive_date is not None:
            job.drive_date = req.drive_date.strip()
        if req.location is not None:
            job.location = req.location
        if req.is_open is not None:
            job.is_open = req.is_open

        if req.allowed_branches is not None:
            JobRepository.set_branches(db, job.id, req.allowed_branches)

        return JobRepository.update(db, job)

    @staticmethod
    def delete_job(db: Session, job_id: int) -> bool:
        success = JobRepository.delete(db, job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job listing with ID {job_id} not found."
            )
        return True

    @staticmethod
    def list_jobs(db: Session, is_open: Optional[bool] = None) -> List[JobListing]:
        return JobRepository.get_all(db, is_open=is_open)

    @staticmethod
    def list_jobs_by_company(db: Session, company_id: int) -> List[JobListing]:
        return JobRepository.get_by_company(db, company_id)

    @staticmethod
    def list_jobs_with_eligibility_for_student(db: Session, student: Student) -> List[JobListingWithEligibility]:
        """Lists all open jobs with computed eligibility and existing application status for the student."""
        jobs = JobRepository.get_all(db, is_open=True)
        results = []

        for job in jobs:
            eligibility = EligibilityService.check_eligibility(student, job)
            app = ApplicationRepository.get_by_student_and_job(db, student.id, job.id)

            item = JobListingWithEligibility(
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
                eligibility=eligibility,
                has_applied=app is not None,
                application_id=app.id if app else None,
                application_status=app.status if app else None,
            )
            results.append(item)

        return results
