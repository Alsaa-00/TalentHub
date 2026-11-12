from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.company import Company

class CompanyRepository:
    @staticmethod
    def get_by_id(db: Session, company_id: int) -> Optional[Company]:
        return db.query(Company).filter(Company.id == company_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[Company]:
        return db.query(Company).filter(Company.user_id == user_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Company]:
        return db.query(Company).filter(Company.name.ilike(name.strip())).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
        return db.query(Company).order_by(Company.name).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, company: Company) -> Company:
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def update(db: Session, company: Company) -> Company:
        db.commit()
        db.refresh(company)
        return company

    @staticmethod
    def count(db: Session) -> int:
        return db.query(Company).count()
