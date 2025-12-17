"""Configuration-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ConfigResponse(BaseModel):
    """Configuration response schema."""
    target_companies: List[str]
    target_states: List[str]
    last_ingestion: Optional[datetime] = None
    last_detection: Optional[datetime] = None


class CompanyListRequest(BaseModel):
    """Request schema for setting company list."""
    companies: List[str] = Field(..., min_items=1, description="List of company names to track")


class StateListRequest(BaseModel):
    """Request schema for setting state list."""
    states: List[str] = Field(..., min_items=1, description="List of US state codes (e.g., CA, NY)")

