from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

class StudentBase(BaseModel):
    usn: str
    full_name: str
    email: str = Field(pattern=EMAIL_PATTERN)
    branch: str
    cgpa: float = Field(ge=0.0, le=10.0)
    active_backlogs: int = Field(default=0, ge=0)
    cleared_backlogs: int = Field(default=0, ge=0)
    phone: Optional[str] = None
    skills: Optional[str] = None
    resume_url: Optional[str] = None

class StudentCreate(StudentBase):
    user_id: int
    consent_given: bool = True

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    active_backlogs: Optional[int] = Field(default=None, ge=0)
    cleared_backlogs: Optional[int] = Field(default=None, ge=0)
    phone: Optional[str] = None
    skills: Optional[str] = None
    resume_url: Optional[str] = None

class StudentOut(StudentBase):
    id: int
    user_id: int
    has_accepted_offer: bool
    consent_given: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
