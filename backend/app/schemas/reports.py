from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class PlacedStudentOut(BaseModel):
    student_id: int
    usn: str
    full_name: str
    branch: str
    cgpa: float
    company_name: str
    job_role: str
    package_lpa: float
    offer_letter_key: str
    accepted_date: Optional[datetime] = None

class BranchStatistics(BaseModel):
    branch: str
    total_students: int
    placed_students: int
    placement_percentage: float
    average_package_lpa: float
    highest_package_lpa: float

class PlacementStatisticsOut(BaseModel):
    season: str
    total_registered_students: int
    total_placed_students: int
    overall_placement_percentage: float
    total_companies_visiting: int
    total_jobs_posted: int
    total_applications: int
    total_offers_issued: int
    total_offers_accepted: int
    average_package_lpa: float
    highest_package_lpa: float
    lowest_package_lpa: float
    branch_breakdown: List[BranchStatistics] = []
    status_distribution: Dict[str, int] = {}
