from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class ApplicationStatus:
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEWED = "INTERVIEWED"
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_listings.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default=ApplicationStatus.APPLIED)
    ineligibility_reason = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    student = relationship("Student", back_populates="applications")
    job = relationship("JobListing", back_populates="applications")
    interview_slots = relationship("InterviewSlot", back_populates="application", cascade="all, delete-orphan", order_by="InterviewSlot.round_no")
    offer = relationship("Offer", back_populates="application", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("student_id", "job_id", name="uq_student_job_application"),
    )

    def __repr__(self):
        return f"<Application {self.id}: student={self.student_id} job={self.job_id} status={self.status}>"
