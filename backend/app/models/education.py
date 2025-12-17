"""Education model for storing educational background."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Education(Base):
    """Education record model."""
    
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Education details
    institution = Column(String, nullable=False)
    graduation_year = Column(Integer, nullable=True)  # Nullable in case year is unknown
    degree_type = Column(String, nullable=True)  # e.g., "Bachelor's", "Master's"
    
    # Relationship
    profile = relationship("Profile", back_populates="education")
    
    def __repr__(self):
        return f"<Education(id={self.id}, institution={self.institution}, year={self.graduation_year})>"

