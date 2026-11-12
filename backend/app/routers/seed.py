from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.seed_data import seed_database

router = APIRouter(prefix="/seed", tags=["Demo Data & Seeding"])

@router.post("")
def reset_and_seed(db: Session = Depends(get_db)):
    """Reset database and populate realistic placement season demonstration data."""
    return seed_database(db)
