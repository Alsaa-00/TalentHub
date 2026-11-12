from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), unique=True, nullable=False)
    designation = Column(String(150), nullable=False)
    package_lpa = Column(Float, nullable=False)
    offer_letter_key = Column(String(100), unique=True, nullable=False)
    joining_date = Column(String(50), nullable=True)
    terms = Column(Text, nullable=True)
    accepted = Column(Boolean, default=False, nullable=False)
    declined = Column(Boolean, default=False, nullable=False)
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    decision_at = Column(DateTime, nullable=True)

    application = relationship("Application", back_populates="offer")

    def __repr__(self):
        return f"<Offer {self.id}: app={self.application_id} lpa={self.package_lpa} accepted={self.accepted}>"
