import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent
ENV_PATH = BACKEND_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

# Configuration values with defaults
PROJECT_NAME: str = os.getenv("PROJECT_NAME", "TalentHub – Campus Placement Management System")
API_V1_STR: str = os.getenv("API_V1_STR", "/api")
SECRET_KEY: str = os.getenv("SECRET_KEY", "talenthub_secure_key_change_in_production_2026")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
CURRENT_SEASON: str = os.getenv("CURRENT_SEASON", "2026-2027")

# Database Path
DB_DIR = ROOT_DIR / "database"
try:
    DB_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
DEFAULT_DB_FILE = DB_DIR / "talenthub.db"

DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE.as_posix()}")

# Ensure sqlite relative URL is properly formatted if passed
if DATABASE_URL.startswith("sqlite:///../../database/"):
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"
