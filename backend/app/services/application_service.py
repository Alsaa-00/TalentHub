from typing import Optional, List, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.application import Application, ApplicationStatus
from app.models.student import Student
from app.models.job import JobListing
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.services.eligibility_service import EligibilityService
from app.schemas.application import ShortlistRunResult

VALID_TRANSITIONS = {
    ApplicationStatus.APPLIED: [ApplicationStatus.SHORTLISTED, ApplicationStatus.REJECTED],
    ApplicationStatus.SHORTLISTED: [ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.REJECTED],
    ApplicationStatus.INTERVIEW_SCHEDULED: [ApplicationStatus.INTERVIEWED, ApplicationStatus.REJECTED],
    ApplicationStatus.INTERVIEWED: [ApplicationStatus.OFFERED, ApplicationStatus.REJECTED],
    ApplicationStatus.OFFERED: [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED],
    ApplicationStatus.ACCEPTED: [],  # Terminal state
    ApplicationStatus.REJECTED: [],  # Terminal state
}

class ApplicationService:
    @staticmethod
    def apply_for_job(db: Session, student: Student, job_id: int) -> Application:
        job = JobRepository.get_by_id(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job listing with ID {job_id} not found."
            )

        if not job.is_open:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This job drive is closed for new applications."
            )

        # Check if already applied to this specific job
        existing_app = ApplicationRepository.get_by_student_and_job(db, student.id, job.id)
        if existing_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already submitted an application for this job drive."
            )

        # Check if student already applied to the same company in the season (FR-5.3)
        company_jobs = JobRepository.get_by_company(db, job.company_id)
        company_job_ids = [j.id for j in company_jobs if j.season == job.season and j.id != job.id]
        if company_job_ids:
            prior_app = db.query(Application).filter(
                Application.student_id == student.id,
                Application.job_id.in_(company_job_ids)
            ).first()
            if prior_app:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A student cannot apply to the same company more than once in the {job.season} placement season."
                )

        # Check eligibility via single source of truth
        eligibility = EligibilityService.check_eligibility(student, job)
        if not eligibility.eligible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Eligibility check failed: {eligibility.reason}"
            )

        # Create application
        application = Application(
            student_id=student.id,
            job_id=job.id,
            status=ApplicationStatus.APPLIED,
            ineligibility_reason=None
        )
        return ApplicationRepository.create(db, application)

    @staticmethod
    def shortlist_students(db: Session, job_id: int) -> ShortlistRunResult:
        """
        Batch shortlisting run for a job drive (FR-6.1 - FR-6.5).
        Evaluates applicants, moves eligible from APPLIED to SHORTLISTED,
        records reasons for ineligible students, commits in a single transaction.
        """
        job = JobRepository.get_by_id(db, job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job listing {job_id} not found.")

        applications = ApplicationRepository.get_by_job(db, job_id)

        shortlisted_count = 0
        ineligible_count = 0
        already_shortlisted = 0
        details = []

        for app in applications:
            if app.status == ApplicationStatus.SHORTLISTED:
                already_shortlisted += 1
                details.append({
                    "application_id": app.id,
                    "student_usn": app.student.usn,
                    "student_name": app.student.full_name,
                    "status": app.status,
                    "action": "already_shortlisted",
                    "reason": "Student was previously shortlisted."
                })
                continue

            # Only process APPLIED applications
            if app.status == ApplicationStatus.APPLIED:
                eligibility = EligibilityService.check_eligibility(app.student, job)
                if eligibility.eligible:
                    app.status = ApplicationStatus.SHORTLISTED
                    app.ineligibility_reason = None
                    shortlisted_count += 1
                    details.append({
                        "application_id": app.id,
                        "student_usn": app.student.usn,
                        "student_name": app.student.full_name,
                        "status": ApplicationStatus.SHORTLISTED,
                        "action": "shortlisted",
                        "reason": eligibility.reason
                    })
                else:
                    app.status = ApplicationStatus.REJECTED
                    app.ineligibility_reason = eligibility.reason
                    ineligible_count += 1
                    details.append({
                        "application_id": app.id,
                        "student_usn": app.student.usn,
                        "student_name": app.student.full_name,
                        "status": ApplicationStatus.REJECTED,
                        "action": "rejected_ineligible",
                        "reason": eligibility.reason
                    })

        # Single transaction commit (FR-6.4)
        db.commit()

        return ShortlistRunResult(
            job_id=job_id,
            total_processed=len(applications),
            shortlisted_count=shortlisted_count,
            ineligible_count=ineligible_count,
            already_shortlisted_count=already_shortlisted,
            details=details
        )

    @staticmethod
    def update_application_status(db: Session, application_id: int, new_status: str, reason: Optional[str] = None) -> Application:
        application = ApplicationRepository.get_by_id(db, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} not found."
            )

        current = application.status
        allowed = VALID_TRANSITIONS.get(current, [])
        if new_status not in allowed and new_status != current:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid state transition: Cannot change application status from '{current}' to '{new_status}'. Allowed next states: {allowed}"
            )

        application.status = new_status
        if reason:
            application.ineligibility_reason = reason
        return ApplicationRepository.update(db, application)
