"""Profile model for storing professional profile data."""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Profile(Base):
    """Professional profile model."""
    
    __tablename__ = "profiles"
    
    # Primary key - UUID string
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # External provider ID (e.g., Apollo person ID)
    external_id = Column(String, unique=True, nullable=False, index=True)
    
    # Profile information
    full_name = Column(String, nullable=False)
    current_title = Column(String, nullable=True)
    current_company = Column(String, nullable=True)
    location_state = Column(String(2), nullable=True, index=True)  # US state code (CA, NY, etc.)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    work_history = relationship("WorkHistory", back_populates="profile", cascade="all, delete-orphan")
    founder_events = relationship("FounderEvent", back_populates="profile", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, name={self.full_name}, external_id={self.external_id})>"

