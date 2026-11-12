from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserLogin,
    Token,
    UserOut,
    StudentRegisterRequest,
    CompanyRegisterRequest,
)
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register/student", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_student(req: StudentRegisterRequest, db: Session = Depends(get_db)):
    """Register a new student account and create student profile."""
    user, _ = AuthService.register_student(db, req)
    return AuthService.create_token_for_user(user)

@router.post("/register/company", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_company(req: CompanyRegisterRequest, db: Session = Depends(get_db)):
    """Register a new company account and create company profile."""
    user, _ = AuthService.register_company(db, req)
    return AuthService.create_token_for_user(user)

@router.post("/login", response_model=Token)
def login(req: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with email and password and issue JWT token."""
    user = AuthService.authenticate_user(db, req.email, req.password)
    return AuthService.create_token_for_user(user)

@router.get("/me", response_model=Token)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Retrieve details and token payload for the currently authenticated user."""
    return AuthService.create_token_for_user(current_user)
