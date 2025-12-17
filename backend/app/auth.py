"""Basic authentication middleware for FastAPI."""
from fastapi import HTTPException, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config import settings


security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Security(security)) -> str:
    """
    Verify HTTP Basic Authentication credentials.
    
    Args:
        credentials: HTTP Basic Auth credentials from request
        
    Returns:
        Username if credentials are valid
        
    Raises:
        HTTPException: If credentials are invalid
    """
    if (
        credentials.username != settings.BASIC_AUTH_USERNAME
        or credentials.password != settings.BASIC_AUTH_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

