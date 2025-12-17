"""Abstract base class for notification providers."""
from abc import ABC, abstractmethod
from typing import List
from app.models import FounderEvent


class NotificationProvider(ABC):
    """
    Abstract interface for notification providers.
    
    This abstraction allows swapping between different providers
    (Resend, Slack, webhooks) without changing the rest of the codebase.
    """
    
    @abstractmethod
    async def send_founder_digest(self, events: List[FounderEvent]) -> bool:
        """
        Send daily digest of founder transitions.
        
        Args:
            events: List of founder events to include in digest
            
        Returns:
            True if notification was sent successfully
        """
        pass

