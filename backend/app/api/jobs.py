"""Job execution API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.auth import verify_credentials
from app.services.detection.founder_detector import FounderDetector
from app.services.notifications.factory import get_notifier
from app.models import TrackingMetadata


router = APIRouter()


@router.post("/run-detection")
async def run_detection(
    db: Session = Depends(get_db),
    username: str = Depends(verify_credentials),
):
    """
    Manually trigger founder detection job.
    
    Runs the detection engine and sends notifications for new transitions.
    
    Args:
        db: Database session
        username: Authenticated username
        
    Returns:
        Success message with detection results
    """
    # Run detection
    detector = FounderDetector(db)
    new_events = detector.detect_transitions()
    
    # Send notifications for new events
    notified_count = 0
    if new_events:
        notifier = get_notifier()
        success = await notifier.send_founder_digest(new_events)
        
        if success:
            # Mark events as notified
            for event in new_events:
                event.notified = True
            db.commit()
            notified_count = len(new_events)
    
    # Update last detection timestamp
    config = db.query(TrackingMetadata).first()
    if config:
        config.last_detection = datetime.now()
        db.commit()
    
    return {
        "message": "Detection job completed",
        "new_transitions_detected": len(new_events),
        "notifications_sent": notified_count,
    }

