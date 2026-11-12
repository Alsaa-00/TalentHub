from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    season = Column(String(50), nullable=False, default="2026-2027")
    package_lpa = Column(Float, nullable=False, default=0.0)
    min_cgpa = Column(Float, nullable=False, default=0.0)
    max_backlogs = Column(Integer, nullable=False, default=0)
    drive_date = Column(String(50), nullable=False)  # ISO Date YYYY-MM-DD
    location = Column(String(100), nullable=True)
    is_open = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    company = relationship("Company", back_populates="job_listings")
    allowed_branches_rel = relationship("JobAllowedBranch", back_populates="job", cascade="all, delete-orphan", lazy="joined")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    @property
    def allowed_branches(self):
        """Returns list of allowed branch codes. Empty list = pool drive (all branches)."""
        return [b.branch for b in self.allowed_branches_rel]

    def __repr__(self):
        return f"<JobListing {self.id}: {self.role} @ {self.company_id}>"

class JobAllowedBranch(Base):
    """Normalized table for job branch eligibility (BCNF)."""
    __tablename__ = "job_allowed_branches"

    job_id = Column(Integer, ForeignKey("job_listings.id", ondelete="CASCADE"), primary_key=True)
    branch = Column(String(50), primary_key=True)

    job = relationship("JobListing", back_populates="allowed_branches_rel")

    __table_args__ = (
        PrimaryKeyConstraint("job_id", "branch"),
    )

    def __repr__(self):
        return f"<JobAllowedBranch job={self.job_id} branch={self.branch}>"
