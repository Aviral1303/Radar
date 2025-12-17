"""Founder transition API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_credentials
from app.models import FounderEvent
from app.schemas.transition import FounderEventResponse, FounderEventListResponse


router = APIRouter()


@router.get("/transitions", response_model=FounderEventListResponse)
async def list_transitions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    notified: bool = Query(None, description="Filter by notification status"),
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials),
):
    """
    List founder transition events with pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        notified: Filter by notification status (optional)
        db: Database session
        username: Authenticated username
        
    Returns:
        Paginated list of founder events
    """
    offset = (page - 1) * page_size
    
    # Build query
    query = db.query(FounderEvent)
    
    if notified is not None:
        query = query.filter(FounderEvent.notified == notified)
    
    # Get total count
    total = query.count()
    
    # Get paginated events
    events = (
        query
        .order_by(FounderEvent.detected_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    # Convert to response format
    event_responses = []
    for event in events:
        profile = event.profile
        event_responses.append(FounderEventResponse(
            id=event.id,
            profile_id=event.profile_id,
            profile_name=profile.full_name,
            profile_location=profile.location_state,
            old_title=event.old_title,
            new_title=event.new_title,
            new_company=event.new_company,
            detected_at=event.detected_at,
            notified=event.notified,
        ))
    
    return FounderEventListResponse(
        events=event_responses,
        total=total,
        page=page,
        page_size=page_size,
    )

