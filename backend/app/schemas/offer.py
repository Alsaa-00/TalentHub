from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class OfferCreate(BaseModel):
    application_id: int
    designation: str = Field(min_length=2, max_length=150)
    package_lpa: float = Field(ge=0.0)
    joining_date: Optional[str] = "July 2027"
    terms: Optional[str] = None

class OfferDecision(BaseModel):
    decision: str = Field(description="'ACCEPT' or 'DECLINE'")

class OfferOut(BaseModel):
    id: int
    application_id: int
    designation: str
    package_lpa: float
    offer_letter_key: str
    joining_date: Optional[str] = None
    terms: Optional[str] = None
    accepted: bool
    declined: bool
    issued_at: datetime
    decision_at: Optional[datetime] = None

    # Context fields
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    student_usn: Optional[str] = None
    student_branch: Optional[str] = None
    company_name: Optional[str] = None
    job_role: Optional[str] = None
    job_id: Optional[int] = None

    class Config:
        from_attributes = True
