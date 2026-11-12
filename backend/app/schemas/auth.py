from typing import Optional
from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class UserLogin(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    email: str
    name: Optional[str] = None
    profile_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class StudentRegisterRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str = Field(min_length=6)
    usn: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=150)
    branch: str = Field(min_length=2, max_length=50)  # e.g., 'CSE', 'ECE', 'ISE', 'MECH', 'CIVIL', 'CSAI'
    cgpa: float = Field(ge=0.0, le=10.0)
    active_backlogs: int = Field(default=0, ge=0)
    cleared_backlogs: int = Field(default=0, ge=0)
    phone: Optional[str] = None
    skills: Optional[str] = None
    consent_given: bool = True

class CompanyRegisterRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN)
    password: str = Field(min_length=6)
    name: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
