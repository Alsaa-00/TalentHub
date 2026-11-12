from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.interview import InterviewSlot
from app.models.application import Application
from app.models.job import JobListing

class InterviewRepository:
    @staticmethod
    def get_by_id(db: Session, interview_id: int) -> Optional[InterviewSlot]:
        return db.query(InterviewSlot).filter(InterviewSlot.id == interview_id).first()

    @staticmethod
    def get_by_application(db: Session, application_id: int) -> List[InterviewSlot]:
        return db.query(InterviewSlot).filter(
            InterviewSlot.application_id == application_id
        ).order_by(InterviewSlot.round_no.asc()).all()

    @staticmethod
    def get_by_application_and_round(db: Session, application_id: int, round_no: int) -> Optional[InterviewSlot]:
        return db.query(InterviewSlot).filter(
            InterviewSlot.application_id == application_id,
            InterviewSlot.round_no == round_no
        ).first()

    @staticmethod
    def get_by_student(db: Session, student_id: int) -> List[InterviewSlot]:
        return db.query(InterviewSlot).join(
            Application, InterviewSlot.application_id == Application.id
        ).filter(
            Application.student_id == student_id
        ).order_by(InterviewSlot.scheduled_at.asc()).all()

    @staticmethod
    def get_by_company(db: Session, company_id: int) -> List[InterviewSlot]:
        return db.query(InterviewSlot).join(
            Application, InterviewSlot.application_id == Application.id
        ).join(
            JobListing, Application.job_id == JobListing.id
        ).filter(
            JobListing.company_id == company_id
        ).order_by(InterviewSlot.scheduled_at.asc()).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 200) -> List[InterviewSlot]:
        return db.query(InterviewSlot).order_by(InterviewSlot.scheduled_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, interview: InterviewSlot) -> InterviewSlot:
        db.add(interview)
        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    def update(db: Session, interview: InterviewSlot) -> InterviewSlot:
        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    def count(db: Session) -> int:
        return db.query(InterviewSlot).count()
