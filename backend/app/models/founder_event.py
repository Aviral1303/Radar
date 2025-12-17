"""Founder event model for tracking founder transitions."""
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FounderEvent(Base):
    """Founder transition event model."""
    
    __tablename__ = "founder_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transition details
    old_title = Column(String, nullable=True)  # Previous role
    new_title = Column(String, nullable=False)  # New founder role
    new_company = Column(String, nullable=True)  # Company name if available
    
    # Detection metadata
    detected_at = Column(Date, server_default=func.current_date(), nullable=False, index=True)
    notified = Column(Boolean, default=False, nullable=False, index=True)  # Whether notification was sent
    
    # Relationship
    profile = relationship("Profile", back_populates="founder_events")
    
    def __repr__(self):
        return f"<FounderEvent(id={self.id}, profile={self.profile_id}, detected={self.detected_at})>"

