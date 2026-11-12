from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.student import Student
from app.repositories.student_repository import StudentRepository
from app.schemas.student import StudentUpdate

class StudentService:
    @staticmethod
    def get_student_by_id(db: Session, student_id: int) -> Student:
        student = StudentRepository.get_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} not found."
            )
        return student

    @staticmethod
    def get_student_by_user_id(db: Session, user_id: int) -> Student:
        student = StudentRepository.get_by_user_id(db, user_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found for the logged-in user."
            )
        return student

    @staticmethod
    def update_profile(db: Session, student: Student, update_data: StudentUpdate) -> Student:
        if update_data.full_name is not None:
            student.full_name = update_data.full_name.strip()
        if update_data.branch is not None:
            student.branch = update_data.branch.strip().upper()
        if update_data.cgpa is not None:
            student.cgpa = round(update_data.cgpa, 2)
        if update_data.active_backlogs is not None:
            student.active_backlogs = update_data.active_backlogs
        if update_data.cleared_backlogs is not None:
            student.cleared_backlogs = update_data.cleared_backlogs
        if update_data.phone is not None:
            student.phone = update_data.phone
        if update_data.skills is not None:
            student.skills = update_data.skills
        if update_data.resume_url is not None:
            student.resume_url = update_data.resume_url

        return StudentRepository.update(db, student)

    @staticmethod
    def list_students(db: Session, skip: int = 0, limit: int = 200, branch: Optional[str] = None) -> List[Student]:
        return StudentRepository.get_all(db, skip=skip, limit=limit, branch=branch)
