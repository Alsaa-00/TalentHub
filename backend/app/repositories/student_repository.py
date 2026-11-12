from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.student import Student

class StudentRepository:
    @staticmethod
    def get_by_id(db: Session, student_id: int) -> Optional[Student]:
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[Student]:
        return db.query(Student).filter(Student.user_id == user_id).first()

    @staticmethod
    def get_by_usn(db: Session, usn: str) -> Optional[Student]:
        return db.query(Student).filter(Student.usn.ilike(usn.strip())).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Student]:
        return db.query(Student).filter(Student.email.ilike(email.strip())).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 200, branch: Optional[str] = None) -> List[Student]:
        query = db.query(Student)
        if branch:
            query = query.filter(Student.branch == branch)
        return query.order_by(Student.usn).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, student: Student) -> Student:
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def update(db: Session, student: Student) -> Student:
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def count(db: Session) -> int:
        return db.query(Student).count()

    @staticmethod
    def count_placed(db: Session) -> int:
        return db.query(Student).filter(Student.has_accepted_offer.is_(True)).count()
