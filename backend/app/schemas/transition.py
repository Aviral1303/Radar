"""Founder transition-related Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class FounderEventResponse(BaseModel):
    """Founder event response schema."""
    id: int
    profile_id: str
    profile_name: str
    profile_location: Optional[str]
    old_title: Optional[str]
    new_title: str
    new_company: Optional[str]
    detected_at: date
    notified: bool
    
    class Config:
        from_attributes = True


class FounderEventListResponse(BaseModel):
    """Paginated founder event list response."""
    events: List[FounderEventResponse]
    total: int
    page: int
    page_size: int

