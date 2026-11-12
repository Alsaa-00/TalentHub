from typing import Optional, List, Dict
from pydantic import BaseModel
from app.schemas.job import JobListingOut
from app.schemas.application import ApplicationOut
from app.schemas.interview import InterviewSlotOut
from app.schemas.offer import OfferOut

class StudentDashboardOut(BaseModel):
    student_id: int
    full_name: str
    usn: str
    branch: str
    cgpa: float
    active_backlogs: int
    has_accepted_offer: bool
    total_eligible_jobs: int
    total_applications: int
    total_interviews: int
    total_offers: int
    recent_applications: List[ApplicationOut] = []
    upcoming_interviews: List[InterviewSlotOut] = []
    received_offers: List[OfferOut] = []

class CompanyDashboardOut(BaseModel):
    company_id: int
    company_name: str
    total_jobs: int
    total_applicants: int
    total_shortlisted: int
    total_interviews_scheduled: int
    total_offers_issued: int
    total_offers_accepted: int
    recent_jobs: List[JobListingOut] = []

class AdminDashboardOut(BaseModel):
    total_students: int
    total_companies: int
    total_jobs: int
    total_applications: int
    total_shortlisted: int
    total_interviews: int
    total_offers: int
    total_placed_students: int
    placement_percentage: float
    average_package_lpa: float
    highest_package_lpa: float
    branch_wise_placed: Dict[str, int] = {}
    season: str
