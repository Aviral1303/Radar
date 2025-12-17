"""Profile-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class EducationData(BaseModel):
    """Education record data."""
    institution: str
    graduation_year: Optional[int] = None
    degree_type: Optional[str] = None


class WorkHistoryData(BaseModel):
    """Work history record data."""
    title: str
    company: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False


class ProfileData(BaseModel):
    """
    Profile data structure from external providers.
    This is the standardized format used across all providers.
    """
    external_id: str = Field(..., description="Stable ID from external provider")
    full_name: str
    current_title: Optional[str] = None
    current_company: Optional[str] = None
    location_state: Optional[str] = Field(None, max_length=2, description="US state code (CA, NY, etc.)")
    education: List[EducationData] = Field(default_factory=list)
    work_history: List[WorkHistoryData] = Field(default_factory=list)


class ProfileResponse(BaseModel):
    """Profile response schema for API."""
    id: str
    external_id: str
    full_name: str
    current_title: Optional[str]
    current_company: Optional[str]
    location_state: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    """Paginated profile list response."""
    profiles: List[ProfileResponse]
    total: int
    page: int
    page_size: int

