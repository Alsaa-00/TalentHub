import secrets
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.offer import Offer
from app.models.application import Application, ApplicationStatus
from app.models.student import Student
from app.repositories.offer_repository import OfferRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.offer import OfferCreate, OfferOut

class OfferService:
    @staticmethod
    def issue_offer(db: Session, req: OfferCreate) -> Offer:
        application = ApplicationRepository.get_by_id(db, req.application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {req.application_id} not found."
            )

        # Rule FR-8.1 & FR-8.2: Offer can only be issued when application is INTERVIEWED
        if application.status != ApplicationStatus.INTERVIEWED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot issue offer: Application must be in INTERVIEWED status (current status: '{application.status}')."
            )

        # Rule FR-8.6: An application shall have at most one offer
        existing_offer = OfferRepository.get_by_application_id(db, req.application_id)
        if existing_offer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An offer has already been issued for this application."
            )

        # Generate unpredictable secure key (FR-8.3)
        company_tag = "".join(filter(str.isalnum, application.job.company.name))[:4].upper() if application.job and application.job.company else "CMP"
        offer_key = f"TH-{application.job.season[:4]}-{company_tag}-{secrets.token_hex(4).upper()}"

        offer = Offer(
            application_id=req.application_id,
            designation=req.designation.strip(),
            package_lpa=round(req.package_lpa, 2),
            offer_letter_key=offer_key,
            joining_date=req.joining_date,
            terms=req.terms,
            accepted=False,
            declined=False
        )
        offer = OfferRepository.create(db, offer)

        # Transition application status to OFFERED
        application.status = ApplicationStatus.OFFERED
        db.commit()

        return offer

    @staticmethod
    def decide_offer(db: Session, student: Student, offer_id: int, decision: str) -> Offer:
        offer = OfferRepository.get_by_id(db, offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Offer with ID {offer_id} not found."
            )

        # Rule FR-8.4: Check that the offer belongs to the student
        if offer.application.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to decide on this offer."
            )

        if offer.accepted or offer.declined:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A decision has already been recorded for this offer."
            )

        now = datetime.now(timezone.utc)
        decision_clean = decision.strip().upper()

        if decision_clean == "ACCEPT":
            offer.accepted = True
            offer.declined = False
            offer.decision_at = now
            offer.application.status = ApplicationStatus.ACCEPTED
            
            # Rule FR-8.4 & FR-8.5: Mark student's has_accepted_offer flag
            student.has_accepted_offer = True
            StudentRepository.update(db, student)

        elif decision_clean == "DECLINE":
            offer.declined = True
            offer.accepted = False
            offer.decision_at = now
            offer.application.status = ApplicationStatus.REJECTED
            offer.application.ineligibility_reason = "Student declined placement offer."

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid decision. Must be 'ACCEPT' or 'DECLINE'."
            )

        OfferRepository.update(db, offer)
        db.commit()
        return offer

    @staticmethod
    def format_offer_out(offer: Offer) -> OfferOut:
        app = offer.application
        return OfferOut(
            id=offer.id,
            application_id=offer.application_id,
            designation=offer.designation,
            package_lpa=offer.package_lpa,
            offer_letter_key=offer.offer_letter_key,
            joining_date=offer.joining_date,
            terms=offer.terms,
            accepted=offer.accepted,
            declined=offer.declined,
            issued_at=offer.issued_at,
            decision_at=offer.decision_at,
            student_id=app.student_id if app else None,
            student_name=app.student.full_name if app and app.student else None,
            student_usn=app.student.usn if app and app.student else None,
            student_branch=app.student.branch if app and app.student else None,
            company_name=app.job.company.name if app and app.job and app.job.company else None,
            job_role=app.job.role if app and app.job else None,
            job_id=app.job_id if app else None,
        )
