from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.offer import Offer
from app.models.application import Application
from app.models.job import JobListing

class OfferRepository:
    @staticmethod
    def get_by_id(db: Session, offer_id: int) -> Optional[Offer]:
        return db.query(Offer).filter(Offer.id == offer_id).first()

    @staticmethod
    def get_by_application_id(db: Session, application_id: int) -> Optional[Offer]:
        return db.query(Offer).filter(Offer.application_id == application_id).first()

    @staticmethod
    def get_by_student(db: Session, student_id: int) -> List[Offer]:
        return db.query(Offer).join(
            Application, Offer.application_id == Application.id
        ).filter(
            Application.student_id == student_id
        ).order_by(Offer.issued_at.desc()).all()

    @staticmethod
    def get_by_company(db: Session, company_id: int) -> List[Offer]:
        return db.query(Offer).join(
            Application, Offer.application_id == Application.id
        ).join(
            JobListing, Application.job_id == JobListing.id
        ).filter(
            JobListing.company_id == company_id
        ).order_by(Offer.issued_at.desc()).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 200) -> List[Offer]:
        return db.query(Offer).order_by(Offer.issued_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, offer: Offer) -> Offer:
        db.add(offer)
        db.commit()
        db.refresh(offer)
        return offer

    @staticmethod
    def update(db: Session, offer: Offer) -> Offer:
        db.commit()
        db.refresh(offer)
        return offer

    @staticmethod
    def count(db: Session) -> int:
        return db.query(Offer).count()

    @staticmethod
    def count_accepted(db: Session) -> int:
        return db.query(Offer).filter(Offer.accepted.is_(True)).count()
