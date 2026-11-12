from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class InterviewSlotCreate(BaseModel):
    application_id: int
    round_no: int = Field(default=1, ge=1)
    round_name: str = Field(default="Technical Round 1")
    scheduled_at: datetime
    venue: str = Field(default="Main Placement Cell / Online Meet")
    notes: Optional[str] = None

class InterviewSlotUpdate(BaseModel):
    passed: Optional[bool] = None
    notes: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    venue: Optional[str] = None
    round_name: Optional[str] = None

class InterviewSlotOut(BaseModel):
    id: int
    application_id: int
    round_no: int
    round_name: str
    scheduled_at: datetime
    venue: str
    passed: Optional[bool] = None
    notes: Optional[str] = None
    created_at: datetime

    # Denormalized context for frontend display convenience
    student_name: Optional[str] = None
    student_usn: Optional[str] = None
    student_branch: Optional[str] = None
    company_name: Optional[str] = None
    job_role: Optional[str] = None

    class Config:
        from_attributes = True
