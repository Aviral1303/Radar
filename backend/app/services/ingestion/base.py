"""Abstract base class for people data providers."""
from abc import ABC, abstractmethod
from typing import List
from app.schemas.profile import ProfileData


class PeopleDataProvider(ABC):
    """
    Abstract interface for people data providers.
    
    This abstraction allows swapping between different providers
    (Apollo.io, Proxycurl, People Data Labs) without changing
    the rest of the codebase.
    """
    
    @abstractmethod
    async def search_by_company(
        self, 
        company: str, 
        filters: dict = None
    ) -> List[ProfileData]:
        """
        Search for profiles by company name.
        
        Args:
            company: Company name to search for
            filters: Additional filters (e.g., location, state)
            
        Returns:
            List of ProfileData objects
        """
        pass
    
    @abstractmethod
    async def get_profile(self, profile_id: str) -> ProfileData:
        """
        Get a single profile by ID.
        
        Args:
            profile_id: External provider's profile ID
            
        Returns:
            ProfileData object
        """
        pass
    
    @abstractmethod
    async def bulk_refresh(self, profile_ids: List[str]) -> List[ProfileData]:
        """
        Refresh multiple profiles in bulk.
        
        Args:
            profile_ids: List of external provider profile IDs
            
        Returns:
            List of updated ProfileData objects
        """
        pass

