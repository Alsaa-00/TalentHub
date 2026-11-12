import mimetypes
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from contextlib import asynccontextmanager

from app.config import PROJECT_NAME, API_V1_STR
from app.database import engine, Base, SessionLocal
from app.models import User
from app.seed_data import seed_database
from app.routers import (
    auth_router,
    students_router,
    companies_router,
    jobs_router,
    applications_router,
    interviews_router,
    offers_router,
    dashboard_router,
    reports_router,
    seed_router,
)

# Root directory paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed initial demo dataset if users table is empty
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            print("[TalentHub] Empty database detected. Populating demo placement dataset...")
            seed_database(db)
            print("[TalentHub] Database initialized successfully.")
    except Exception as e:
        print(f"[TalentHub] Database initialization warning: {e}")
    finally:
        db.close()
    
    yield

app = FastAPI(
    title=PROJECT_NAME,
    description="Full-stack campus placement management system powering student eligibility verification, company recruitment drives, interview pipelines, and placement analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for flexible local development and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(auth_router, prefix=API_V1_STR)
app.include_router(students_router, prefix=API_V1_STR)
app.include_router(companies_router, prefix=API_V1_STR)
app.include_router(jobs_router, prefix=API_V1_STR)
app.include_router(applications_router, prefix=API_V1_STR)
app.include_router(interviews_router, prefix=API_V1_STR)
app.include_router(offers_router, prefix=API_V1_STR)
app.include_router(dashboard_router, prefix=API_V1_STR)
app.include_router(reports_router, prefix=API_V1_STR)
app.include_router(seed_router, prefix=API_V1_STR)

# --- Robust Frontend & Static Asset Serving (Zero async file threadpool dependencies) ---

def _get_mime_type(path: Path) -> str:
    """Determine MIME type with proper charset for web assets."""
    mime, _ = mimetypes.guess_type(str(path))
    if mime:
        if "text" in mime or "javascript" in mime:
            return f"{mime}; charset=utf-8"
        return mime
    
    suffix = path.suffix.lower()
    if suffix == ".css":
        return "text/css; charset=utf-8"
    elif suffix == ".js":
        return "application/javascript; charset=utf-8"
    elif suffix == ".svg":
        return "image/svg+xml"
    elif suffix == ".html":
        return "text/html; charset=utf-8"
    elif suffix == ".png":
        return "image/png"
    elif suffix in (".jpg", ".jpeg"):
        return "image/jpeg"
    elif suffix == ".json":
        return "application/json"
    return "application/octet-stream"

@app.get("/static/{file_path:path}", include_in_schema=False)
def serve_static(file_path: str):
    """Serve static CSS, JS, images safely with synchronous reading."""
    try:
        resolved_path = (FRONTEND_DIR / file_path).resolve()
        # Security: verify path stays within FRONTEND_DIR
        if not str(resolved_path).startswith(str(FRONTEND_DIR.resolve())):
            return Response(status_code=403, content=b"Access denied", media_type="text/plain")
        if not resolved_path.is_file():
            return Response(status_code=404, content=b"Asset not found", media_type="text/plain")
        
        content = resolved_path.read_bytes()
        media_type = _get_mime_type(resolved_path)
        return Response(content=content, media_type=media_type, headers={"Cache-Control": "no-cache"})
    except Exception as e:
        return Response(status_code=500, content=f"Error reading asset: {e}".encode("utf-8"), media_type="text/plain")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_index():
    """Serve landing index page."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.is_file():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>TalentHub Placement Portal is Running</h2><p><a href='/docs'>Swagger API Documentation</a></p>")

@app.get("/{page_name}.html", response_class=HTMLResponse, include_in_schema=False)
def serve_html(page_name: str):
    """Serve root level HTML pages (e.g. login.html, register.html)."""
    page_file = (FRONTEND_DIR / f"{page_name}.html").resolve()
    if page_file.is_file() and str(page_file).startswith(str(FRONTEND_DIR.resolve())):
        return HTMLResponse(content=page_file.read_text(encoding="utf-8"))
    # Fallback to index if not found
    index_file = FRONTEND_DIR / "index.html"
    if index_file.is_file():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(status_code=404, content="<h1>Page Not Found</h1>")

@app.get("/{role}/{page_name}.html", response_class=HTMLResponse, include_in_schema=False)
def serve_role_html(role: str, page_name: str):
    """Serve role-specific HTML pages (e.g. student/dashboard.html, company/jobs.html)."""
    page_file = (FRONTEND_DIR / role / f"{page_name}.html").resolve()
    if page_file.is_file() and str(page_file).startswith(str(FRONTEND_DIR.resolve())):
        return HTMLResponse(content=page_file.read_text(encoding="utf-8"))
    # Fallback
    index_file = FRONTEND_DIR / "index.html"
    if index_file.is_file():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(status_code=404, content="<h1>Page Not Found</h1>")

@app.get("/{role}/{page_name}", response_class=HTMLResponse, include_in_schema=False)
def serve_role_html_no_ext(role: str, page_name: str):
    """Serve role-specific pages without .html extension in URL."""
    return serve_role_html(role, page_name)

