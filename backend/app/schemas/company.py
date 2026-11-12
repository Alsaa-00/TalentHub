from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None

class CompanyCreate(CompanyBase):
    user_id: int

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None

class CompanyOut(CompanyBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
