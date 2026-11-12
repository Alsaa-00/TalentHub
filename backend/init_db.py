import sys
import os
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Base, engine, SessionLocal
from app.models import User, Student, Company, JobListing, Application, InterviewSlot, Offer
from app.seed_data import seed_database

print("Creating database schema...")
Base.metadata.create_all(bind=engine)
print("Schema created successfully!")

print("Seeding database with demo records...")
db = SessionLocal()
try:
    result = seed_database(db)
    print("Seed result:", result)
finally:
    db.close()

print("TalentHub Database initialization complete!")
