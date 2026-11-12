from app.schemas.auth import (
    UserLogin,
    Token,
    UserOut,
    StudentRegisterRequest,
    CompanyRegisterRequest,
)
from app.schemas.student import StudentBase, StudentCreate, StudentUpdate, StudentOut
from app.schemas.company import CompanyBase, CompanyCreate, CompanyUpdate, CompanyOut
from app.schemas.eligibility import EligibilityResult
from app.schemas.job import JobListingBase, JobListingCreate, JobListingUpdate, JobListingOut, JobListingWithEligibility
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate, ApplicationOut, ShortlistRunResult
from app.schemas.interview import InterviewSlotCreate, InterviewSlotUpdate, InterviewSlotOut
from app.schemas.offer import OfferCreate, OfferDecision, OfferOut
from app.schemas.dashboard import StudentDashboardOut, CompanyDashboardOut, AdminDashboardOut
from app.schemas.reports import PlacedStudentOut, PlacementStatisticsOut, BranchStatistics

__all__ = [
    "UserLogin",
    "Token",
    "UserOut",
    "StudentRegisterRequest",
    "CompanyRegisterRequest",
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentOut",
    "CompanyBase",
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyOut",
    "EligibilityResult",
    "JobListingBase",
    "JobListingCreate",
    "JobListingUpdate",
    "JobListingOut",
    "JobListingWithEligibility",
    "ApplicationCreate",
    "ApplicationStatusUpdate",
    "ApplicationOut",
    "ShortlistRunResult",
    "InterviewSlotCreate",
    "InterviewSlotUpdate",
    "InterviewSlotOut",
    "OfferCreate",
    "OfferDecision",
    "OfferOut",
    "StudentDashboardOut",
    "CompanyDashboardOut",
    "AdminDashboardOut",
    "PlacedStudentOut",
    "PlacementStatisticsOut",
    "BranchStatistics",
]
