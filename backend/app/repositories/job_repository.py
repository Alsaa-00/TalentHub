from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.job import JobListing, JobAllowedBranch

class JobRepository:
    @staticmethod
    def get_by_id(db: Session, job_id: int) -> Optional[JobListing]:
        return db.query(JobListing).filter(JobListing.id == job_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, is_open: Optional[bool] = None) -> List[JobListing]:
        query = db.query(JobListing)
        if is_open is not None:
            query = query.filter(JobListing.is_open == is_open)
        return query.order_by(JobListing.drive_date.desc(), JobListing.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_company(db: Session, company_id: int) -> List[JobListing]:
        return db.query(JobListing).filter(JobListing.company_id == company_id).order_by(JobListing.drive_date.desc()).all()

    @staticmethod
    def create(db: Session, job: JobListing, branches: Optional[List[str]] = None) -> JobListing:
        db.add(job)
        db.flush()  # assign id to job

        if branches:
            for b in branches:
                if b.strip():
                    db.add(JobAllowedBranch(job_id=job.id, branch=b.strip().upper()))

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def set_branches(db: Session, job_id: int, branches: List[str]):
        # Clear existing
        db.query(JobAllowedBranch).filter(JobAllowedBranch.job_id == job_id).delete()
        for b in branches:
            if b.strip():
                db.add(JobAllowedBranch(job_id=job_id, branch=b.strip().upper()))
        db.commit()

    @staticmethod
    def update(db: Session, job: JobListing) -> JobListing:
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def delete(db: Session, job_id: int) -> bool:
        job = db.query(JobListing).filter(JobListing.id == job_id).first()
        if job:
            db.delete(job)
            db.commit()
            return True
        return False

    @staticmethod
    def count(db: Session) -> int:
        return db.query(JobListing).count()
