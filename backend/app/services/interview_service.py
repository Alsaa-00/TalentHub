from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.interview import InterviewSlot
from app.models.application import Application, ApplicationStatus
from app.repositories.interview_repository import InterviewRepository
from app.repositories.application_repository import ApplicationRepository
from app.schemas.interview import InterviewSlotCreate, InterviewSlotUpdate, InterviewSlotOut

class InterviewService:
    @staticmethod
    def schedule_interview(db: Session, req: InterviewSlotCreate) -> InterviewSlot:
        application = ApplicationRepository.get_by_id(db, req.application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {req.application_id} not found."
            )

        if application.status not in [ApplicationStatus.SHORTLISTED, ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEWED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot schedule interview: Application must be in SHORTLISTED state (current: '{application.status}')."
            )

        # Check unique round_no within application
        existing_round = InterviewRepository.get_by_application_and_round(db, req.application_id, req.round_no)
        if existing_round:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Round {req.round_no} is already scheduled for this application."
            )

        slot = InterviewSlot(
            application_id=req.application_id,
            round_no=req.round_no,
            round_name=req.round_name.strip(),
            scheduled_at=req.scheduled_at,
            venue=req.venue.strip(),
            notes=req.notes,
            passed=None
        )
        slot = InterviewRepository.create(db, slot)

        # Transition application status to INTERVIEW_SCHEDULED
        application.status = ApplicationStatus.INTERVIEW_SCHEDULED
        db.commit()

        return slot

    @staticmethod
    def record_result(db: Session, interview_id: int, req: InterviewSlotUpdate) -> InterviewSlot:
        slot = InterviewRepository.get_by_id(db, interview_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview slot with ID {interview_id} not found."
            )

        if req.passed is not None:
            slot.passed = req.passed
        if req.notes is not None:
            slot.notes = req.notes
        if req.scheduled_at is not None:
            slot.scheduled_at = req.scheduled_at
        if req.venue is not None:
            slot.venue = req.venue
        if req.round_name is not None:
            slot.round_name = req.round_name

        slot = InterviewRepository.update(db, slot)

        # Update application state
        app = slot.application
        if slot.passed is True:
            # Mark application as INTERVIEWED (ready for offer or next stage)
            app.status = ApplicationStatus.INTERVIEWED
        elif slot.passed is False:
            # Mark application as REJECTED
            app.status = ApplicationStatus.REJECTED
            app.ineligibility_reason = f"Candidate did not pass {slot.round_name}."

        db.commit()
        return slot

    @staticmethod
    def format_interview_out(slot: InterviewSlot) -> InterviewSlotOut:
        app = slot.application
        return InterviewSlotOut(
            id=slot.id,
            application_id=slot.application_id,
            round_no=slot.round_no,
            round_name=slot.round_name,
            scheduled_at=slot.scheduled_at,
            venue=slot.venue,
            passed=slot.passed,
            notes=slot.notes,
            created_at=slot.created_at,
            student_name=app.student.full_name if app and app.student else None,
            student_usn=app.student.usn if app and app.student else None,
            student_branch=app.student.branch if app and app.student else None,
            company_name=app.job.company.name if app and app.job and app.job.company else None,
            job_role=app.job.role if app and app.job else None,
        )
