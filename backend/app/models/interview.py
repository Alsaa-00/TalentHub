from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class InterviewSlot(Base):
    __tablename__ = "interview_slots"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    round_no = Column(Integer, nullable=False, default=1)
    round_name = Column(String(100), nullable=False, default="Technical Round 1")
    scheduled_at = Column(DateTime, nullable=False)
    venue = Column(String(200), nullable=False)  # e.g., "Seminar Hall 2 / Google Meet"
    passed = Column(Boolean, nullable=True)      # None = pending, True = passed, False = failed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="interview_slots")

    __table_args__ = (
        UniqueConstraint("application_id", "round_no", name="uq_app_round_no"),
    )

    def __repr__(self):
        return f"<InterviewSlot round={self.round_no} app={self.application_id} passed={self.passed}>"
