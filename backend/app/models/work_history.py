"""Work history model for storing employment snapshots."""
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WorkHistory(Base):
    """Work history snapshot model - stores historical employment data."""
    
    __tablename__ = "work_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Employment details
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False, nullable=False)
    
    # Snapshot metadata - when this record was captured
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationship
    profile = relationship("Profile", back_populates="work_history")
    
    def __repr__(self):
        return f"<WorkHistory(id={self.id}, title={self.title}, company={self.company}, snapshot={self.snapshot_date})>"

