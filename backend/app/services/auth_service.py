from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.repositories.user_repository import UserRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.company_repository import CompanyRepository
from app.schemas.auth import StudentRegisterRequest, CompanyRegisterRequest, Token
from app.utils.security import hash_password, verify_password, create_access_token

class AuthService:
    @staticmethod
    def register_student(db: Session, req: StudentRegisterRequest) -> Tuple[User, Student]:
        # Check if email exists
        if UserRepository.get_by_email(db, req.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email '{req.email}' already exists."
            )

        # Check if USN exists
        if StudentRepository.get_by_usn(db, req.usn):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with USN '{req.usn}' already exists."
            )

        # Create User
        user = User(
            email=req.email.lower().strip(),
            hashed_password=hash_password(req.password),
            role="student",
            is_active=True
        )
        user = UserRepository.create(db, user)

        # Create Student profile
        student = Student(
            user_id=user.id,
            usn=req.usn.strip().upper(),
            full_name=req.full_name.strip(),
            email=req.email.lower().strip(),
            branch=req.branch.strip().upper(),
            cgpa=round(req.cgpa, 2),
            active_backlogs=req.active_backlogs,
            cleared_backlogs=req.cleared_backlogs,
            phone=req.phone,
            skills=req.skills,
            consent_given=req.consent_given,
            has_accepted_offer=False
        )
        student = StudentRepository.create(db, student)
        return user, student

    @staticmethod
    def register_company(db: Session, req: CompanyRegisterRequest) -> Tuple[User, Company]:
        # Check if email exists
        if UserRepository.get_by_email(db, req.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email '{req.email}' already exists."
            )

        # Check if company name exists
        if CompanyRepository.get_by_name(db, req.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A company named '{req.name}' is already registered."
            )

        # Create User
        user = User(
            email=req.email.lower().strip(),
            hashed_password=hash_password(req.password),
            role="company",
            is_active=True
        )
        user = UserRepository.create(db, user)

        # Create Company profile
        company = Company(
            user_id=user.id,
            name=req.name.strip(),
            description=req.description,
            website=req.website,
            contact_email=req.contact_email or req.email,
            location=req.location,
            industry=req.industry
        )
        company = CompanyRepository.create(db, company)
        return user, company

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        user = UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Please contact the administrator."
            )
        return user

    @staticmethod
    def create_token_for_user(user: User) -> Token:
        token_data = {
            "sub": user.email,
            "role": user.role,
            "user_id": user.id,
        }

        name = user.email
        profile_id = None

        if user.role == "student" and user.student:
            token_data["student_id"] = user.student.id
            token_data["name"] = user.student.full_name
            name = user.student.full_name
            profile_id = user.student.id
        elif user.role == "company" and user.company:
            token_data["company_id"] = user.company.id
            token_data["name"] = user.company.name
            name = user.company.name
            profile_id = user.company.id
        elif user.role == "admin":
            name = "Placement Coordinator"
            profile_id = user.id

        token_str = create_access_token(token_data)
        return Token(
            access_token=token_str,
            token_type="bearer",
            role=user.role,
            user_id=user.id,
            email=user.email,
            name=name,
            profile_id=profile_id,
        )
