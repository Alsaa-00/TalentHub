from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.student import StudentOut
from app.schemas.job import JobListingOut

class ApplicationCreate(BaseModel):
    job_id: int

class ApplicationStatusUpdate(BaseModel):
    status: str
    ineligibility_reason: Optional[str] = None

class ApplicationOut(BaseModel):
    id: int
    student_id: int
    job_id: int
    status: str
    ineligibility_reason: Optional[str] = None
    applied_at: datetime
    updated_at: datetime

    student: Optional[StudentOut] = None
    job: Optional[JobListingOut] = None

    class Config:
        from_attributes = True

class ShortlistRunResult(BaseModel):
    job_id: int
    total_processed: int
    shortlisted_count: int
    ineligible_count: int
    already_shortlisted_count: int
    details: List[dict]
