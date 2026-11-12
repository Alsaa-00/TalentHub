from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyUpdate

class CompanyService:
    @staticmethod
    def get_company_by_id(db: Session, company_id: int) -> Company:
        company = CompanyRepository.get_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found."
            )
        return company

    @staticmethod
    def get_company_by_user_id(db: Session, user_id: int) -> Company:
        company = CompanyRepository.get_by_user_id(db, user_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company profile not found for the logged-in user."
            )
        return company

    @staticmethod
    def update_profile(db: Session, company: Company, update_data: CompanyUpdate) -> Company:
        if update_data.name is not None:
            existing = CompanyRepository.get_by_name(db, update_data.name)
            if existing and existing.id != company.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A company named '{update_data.name}' already exists."
                )
            company.name = update_data.name.strip()
        if update_data.description is not None:
            company.description = update_data.description
        if update_data.website is not None:
            company.website = update_data.website
        if update_data.contact_email is not None:
            company.contact_email = update_data.contact_email
        if update_data.location is not None:
            company.location = update_data.location
        if update_data.industry is not None:
            company.industry = update_data.industry

        return CompanyRepository.update(db, company)

    @staticmethod
    def list_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
        return CompanyRepository.get_all(db, skip=skip, limit=limit)
