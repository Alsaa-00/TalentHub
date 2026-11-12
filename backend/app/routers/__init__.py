from app.routers.auth import router as auth_router
from app.routers.students import router as students_router
from app.routers.companies import router as companies_router
from app.routers.jobs import router as jobs_router
from app.routers.applications import router as applications_router
from app.routers.interviews import router as interviews_router
from app.routers.offers import router as offers_router
from app.routers.dashboard import router as dashboard_router
from app.routers.reports import router as reports_router
from app.routers.seed import router as seed_router

__all__ = [
    "auth_router",
    "students_router",
    "companies_router",
    "jobs_router",
    "applications_router",
    "interviews_router",
    "offers_router",
    "dashboard_router",
    "reports_router",
    "seed_router",
]
