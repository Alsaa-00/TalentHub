from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    usn = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    branch = Column(String(50), nullable=False)  # CSE, ECE, ISE, MECH, CIVIL, CSAI, etc.
    cgpa = Column(Float, nullable=False)
    active_backlogs = Column(Integer, default=0, nullable=False)
    cleared_backlogs = Column(Integer, default=0, nullable=False)
    has_accepted_offer = Column(Boolean, default=False, nullable=False)
    phone = Column(String(20), nullable=True)
    skills = Column(String(255), nullable=True)
    resume_url = Column(String(255), nullable=True)
    consent_given = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="student")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.usn} {self.full_name}>"
