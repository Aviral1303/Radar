"""Factory for creating people data provider instances."""
from typing import Optional
from app.services.ingestion.base import PeopleDataProvider
from app.services.ingestion.apollo import ApolloProvider
from app.services.ingestion.mock import MockProvider
from app.config import settings


def get_provider(provider_name: Optional[str] = None) -> PeopleDataProvider:
    """
    Factory function to get the appropriate people data provider.
    
    Args:
        provider_name: Name of provider (defaults to settings)
        
    Returns:
        PeopleDataProvider instance
        
    Raises:
        ValueError: If provider name is not recognized
    """
    provider_name = provider_name or settings.PEOPLE_DATA_PROVIDER
    
    if provider_name == "apollo":
        return ApolloProvider()
    elif provider_name == "mock":
        return MockProvider()
    # Future providers can be added here:
    # elif provider_name == "proxycurl":
    #     return ProxycurlProvider()
    # elif provider_name == "pdl":
    #     return PDLProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Valid options: apollo, mock")

