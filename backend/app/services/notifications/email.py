"""Resend email notification implementation."""
from typing import List
from datetime import datetime
import resend
from app.services.notifications.base import NotificationProvider
from app.models import FounderEvent
from app.config import settings


class ResendEmailProvider(NotificationProvider):
    """
    Resend API email notification provider.
    
    Sends daily digest emails with founder transition information.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Resend provider.
        
        Args:
            api_key: Resend API key (defaults to settings)
        """
        api_key = api_key or settings.RESEND_API_KEY
        if not api_key:
            raise ValueError("RESEND_API_KEY must be set")
        
        resend.api_key = api_key
    
    async def send_founder_digest(self, events: List[FounderEvent]) -> bool:
        """
        Send email digest of founder transitions.
        
        Args:
            events: List of founder events to include
            
        Returns:
            True if email was sent successfully
        """
        if not events:
            return True  # No events to send, consider it successful
        
        # Build email content
        subject = f"Founder Transitions Detected - {datetime.now().strftime('%b %d, %Y')}"
        body = self._build_email_body(events)
        
        try:
            # Send email via Resend
            params = resend.Emails.SendParams(
                from_=settings.EMAIL_FROM,
                to=settings.EMAIL_TO,
                subject=subject,
                html=body,
            )
            
            result = resend.Emails.send(params)
            
            # Check if send was successful
            return result is not None and hasattr(result, 'id')
        
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _build_email_body(self, events: List[FounderEvent]) -> str:
        """
        Build HTML email body from founder events.
        
        Args:
            events: List of founder events
            
        Returns:
            HTML email body string
        """
        count = len(events)
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>{count} new founder transition{'' if count == 1 else 's'} detected:</h2>
            <ul style="list-style: none; padding: 0;">
        """
        
        for i, event in enumerate(events, 1):
            profile = event.profile
            location = profile.location_state or "N/A"
            
            old_role = event.old_title or "Unknown"
            if event.old_title and profile.current_company:
                old_role = f"{event.old_title} at {profile.current_company}"
            
            new_role = event.new_title
            if event.new_company:
                new_role = f"{event.new_title} at {event.new_company}"
            
            html += f"""
            <li style="margin-bottom: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
                <strong>{i}. {profile.full_name} ({location})</strong><br>
                Previously: {old_role}<br>
                Now: <strong>{new_role}</strong>
            </li>
            """
        
        html += """
            </ul>
            <p style="margin-top: 30px; color: #666;">
                <a href="http://localhost:5173/transitions" style="color: #007bff;">View all transitions in dashboard</a>
            </p>
        </body>
        </html>
        """
        
        return html

