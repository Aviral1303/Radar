"""Founder detection engine."""
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models import Profile, WorkHistory, FounderEvent


# Founder title keywords - case-insensitive matching
FOUNDER_TITLES = {
    "founder",
    "co-founder",
    "cofounder",
    "ceo",
    "chief executive officer",
    "founding engineer",
    "founding",
    "owner",
}


class FounderDetector:
    """
    Detects founder transitions by comparing current role with previous snapshots.
    
    A founder transition is detected when:
    1. Previous role did NOT contain founder keywords
    2. Current role DOES contain founder keywords
    """
    
    def __init__(self, db: Session):
        """
        Initialize detector with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def detect_transitions(self) -> List[FounderEvent]:
        """
        Detect founder transitions for all tracked profiles.
        
        Compares current work history with previous snapshots to identify
        transitions into founder roles.
        
        Returns:
            List of newly created FounderEvent records
        """
        new_events = []
        
        # Get all tracked profiles
        profiles = self.db.query(Profile).all()
        
        for profile in profiles:
            # Get current work history (most recent snapshot)
            current_work = self._get_current_work(profile.id)
            
            if not current_work:
                continue
            
            # Get previous work history (second most recent snapshot)
            previous_work = self._get_previous_work(profile.id)
            
            # Check if this is a founder transition
            if self._is_founder_transition(previous_work, current_work):
                # Check if we've already detected this transition
                if not self._already_detected(profile.id, current_work.title):
                    event = self._create_event(profile, previous_work, current_work)
                    new_events.append(event)
                    self.db.add(event)
        
        self.db.commit()
        return new_events
    
    def _get_current_work(self, profile_id: str) -> Optional[WorkHistory]:
        """Get most recent work history snapshot for a profile."""
        return (
            self.db.query(WorkHistory)
            .filter(WorkHistory.profile_id == profile_id)
            .order_by(WorkHistory.snapshot_date.desc())
            .first()
        )
    
    def _get_previous_work(self, profile_id: str) -> Optional[WorkHistory]:
        """Get second most recent work history snapshot for a profile."""
        return (
            self.db.query(WorkHistory)
            .filter(WorkHistory.profile_id == profile_id)
            .order_by(WorkHistory.snapshot_date.desc())
            .offset(1)
            .first()
        )
    
    def _is_founder_transition(
        self,
        previous_work: Optional[WorkHistory],
        current_work: WorkHistory
    ) -> bool:
        """
        Check if current work represents a founder transition.
        
        Args:
            previous_work: Previous work history (None if first snapshot)
            current_work: Current work history
            
        Returns:
            True if this is a founder transition
        """
        current_title_normalized = self._normalize_title(current_work.title)
        is_current_founder = any(
            keyword in current_title_normalized
            for keyword in FOUNDER_TITLES
        )
        
        # If current role is not a founder role, no transition
        if not is_current_founder:
            return False
        
        # If no previous work, this might be a founder transition
        # (though we can't be sure it's a transition vs. initial state)
        if previous_work is None:
            return True
        
        # Check if previous role was also a founder role
        previous_title_normalized = self._normalize_title(previous_work.title)
        was_previous_founder = any(
            keyword in previous_title_normalized
            for keyword in FOUNDER_TITLES
        )
        
        # Transition detected if previous was NOT founder and current IS founder
        return not was_previous_founder and is_current_founder
    
    def _normalize_title(self, title: str) -> str:
        """
        Normalize job title for comparison.
        
        Args:
            title: Job title string
            
        Returns:
            Lowercase, normalized title
        """
        if not title:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        normalized = title.lower().strip()
        
        # Remove common punctuation
        normalized = normalized.replace("-", " ").replace("/", " ")
        
        return normalized
    
    def _already_detected(self, profile_id: str, new_title: str) -> bool:
        """
        Check if this transition has already been detected.
        
        Args:
            profile_id: Profile ID
            new_title: New title to check
            
        Returns:
            True if event already exists
        """
        existing = (
            self.db.query(FounderEvent)
            .filter(
                FounderEvent.profile_id == profile_id,
                FounderEvent.new_title == new_title
            )
            .first()
        )
        return existing is not None
    
    def _create_event(
        self,
        profile: Profile,
        previous_work: Optional[WorkHistory],
        current_work: WorkHistory
    ) -> FounderEvent:
        """
        Create a new founder event record.
        
        Args:
            profile: Profile model
            previous_work: Previous work history
            current_work: Current work history
            
        Returns:
            New FounderEvent instance
        """
        return FounderEvent(
            profile_id=profile.id,
            old_title=previous_work.title if previous_work else None,
            new_title=current_work.title,
            new_company=current_work.company,
            detected_at=date.today(),
            notified=False
        )

