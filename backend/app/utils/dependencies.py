from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.repositories.user_repository import UserRepository
from app.utils.security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Authenticates JWT token from Bearer header and retrieves current User."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserRepository.get_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user

def get_current_student(
    current_user: User = Depends(get_current_user),
) -> Student:
    """FR-1.2 & FR-1.3: Ensures current user has student role and returns Student record."""
    if current_user.role != "student" or not current_user.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: This action is only permitted for registered students."
        )
    return current_user.student

def get_current_company(
    current_user: User = Depends(get_current_user),
) -> Company:
    """FR-1.2 & FR-1.4: Ensures current user has company role and returns Company record."""
    if current_user.role != "company" or not current_user.company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: This action is only permitted for registered companies."
        )
    return current_user.company

def get_current_coordinator(
    current_user: User = Depends(get_current_user),
) -> User:
    """FR-1.2 & FR-1.5: Ensures current user has admin / coordinator role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Placement Coordinator / Administrator privileges required."
        )
    return current_user
