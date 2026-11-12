from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.application import Application, ApplicationStatus

class ApplicationRepository:
    @staticmethod
    def get_by_id(db: Session, application_id: int) -> Optional[Application]:
        return db.query(Application).filter(Application.id == application_id).first()

    @staticmethod
    def get_by_student_and_job(db: Session, student_id: int, job_id: int) -> Optional[Application]:
        return db.query(Application).filter(
            Application.student_id == student_id,
            Application.job_id == job_id
        ).first()

    @staticmethod
    def get_by_student(db: Session, student_id: int) -> List[Application]:
        return db.query(Application).filter(
            Application.student_id == student_id
        ).order_by(Application.applied_at.desc()).all()

    @staticmethod
    def get_by_job(db: Session, job_id: int, status: Optional[str] = None) -> List[Application]:
        query = db.query(Application).filter(Application.job_id == job_id)
        if status:
            query = query.filter(Application.status == status)
        return query.order_by(Application.applied_at.asc()).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 200, status: Optional[str] = None) -> List[Application]:
        query = db.query(Application)
        if status:
            query = query.filter(Application.status == status)
        return query.order_by(Application.applied_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, application: Application) -> Application:
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def update(db: Session, application: Application) -> Application:
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def count(db: Session) -> int:
        return db.query(Application).count()

    @staticmethod
    def count_by_status(db: Session) -> Dict[str, int]:
        counts = db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
        result = {
            ApplicationStatus.APPLIED: 0,
            ApplicationStatus.SHORTLISTED: 0,
            ApplicationStatus.INTERVIEW_SCHEDULED: 0,
            ApplicationStatus.INTERVIEWED: 0,
            ApplicationStatus.OFFERED: 0,
            ApplicationStatus.ACCEPTED: 0,
            ApplicationStatus.REJECTED: 0,
        }
        for status, c in counts:
            result[status] = c
        return result
