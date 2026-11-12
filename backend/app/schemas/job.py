from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.eligibility import EligibilityResult

class JobListingBase(BaseModel):
    role: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    season: str = Field(default="2026-2027")
    package_lpa: float = Field(default=0.0, ge=0.0)
    min_cgpa: float = Field(default=6.0, ge=0.0, le=10.0)
    max_backlogs: int = Field(default=0, ge=0)
    drive_date: str = Field(description="ISO Date YYYY-MM-DD")
    location: Optional[str] = "Bengaluru / Hybrid"
    is_open: bool = True
    allowed_branches: List[str] = Field(default_factory=list, description="Empty list means all branches eligible")

class JobListingCreate(JobListingBase):
    pass

class JobListingUpdate(BaseModel):
    role: Optional[str] = None
    description: Optional[str] = None
    season: Optional[str] = None
    package_lpa: Optional[float] = None
    min_cgpa: Optional[float] = None
    max_backlogs: Optional[int] = None
    drive_date: Optional[str] = None
    location: Optional[str] = None
    is_open: Optional[bool] = None
    allowed_branches: Optional[List[str]] = None

class JobListingOut(JobListingBase):
    id: int
    company_id: int
    company_name: Optional[str] = None
    created_at: datetime
    total_applications: Optional[int] = 0

    class Config:
        from_attributes = True

class JobListingWithEligibility(JobListingOut):
    eligibility: Optional[EligibilityResult] = None
    has_applied: bool = False
    application_id: Optional[int] = None
    application_status: Optional[str] = None
