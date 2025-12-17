"""Factory for creating notification provider instances."""
from typing import Optional
from app.services.notifications.base import NotificationProvider
from app.services.notifications.email import ResendEmailProvider
from app.config import settings


def get_notifier(provider_name: Optional[str] = None) -> NotificationProvider:
    """
    Factory function to get the appropriate notification provider.
    
    Args:
        provider_name: Name of provider (defaults to settings)
        
    Returns:
        NotificationProvider instance
        
    Raises:
        ValueError: If provider name is not recognized
    """
    provider_name = provider_name or settings.NOTIFICATION_PROVIDER
    
    if provider_name == "resend":
        return ResendEmailProvider()
    # Future providers can be added here:
    # elif provider_name == "slack":
    #     return SlackProvider()
    # elif provider_name == "webhook":
    #     return WebhookProvider()
    else:
        raise ValueError(f"Unknown notification provider: {provider_name}")

