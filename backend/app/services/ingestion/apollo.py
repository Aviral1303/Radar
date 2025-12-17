"""Apollo.io API implementation."""
import httpx
from typing import List, Optional, Dict
from app.services.ingestion.base import PeopleDataProvider
from app.schemas.profile import ProfileData, EducationData, WorkHistoryData
from app.config import settings


class ApolloProvider(PeopleDataProvider):
    """
    Apollo.io API provider implementation.
    
    Documentation: https://apolloio.github.io/apollo-api-docs/
    """
    
    BASE_URL = "https://api.apollo.io/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Apollo provider.
        
        Args:
            api_key: Apollo API key (defaults to settings)
        """
        self.api_key = api_key or settings.APOLLO_API_KEY
        if not self.api_key:
            raise ValueError("APOLLO_API_KEY must be set")
    
    async def search_by_company(
        self, 
        company: str, 
        filters: Optional[Dict] = None
    ) -> List[ProfileData]:
        """
        Search for people by company using Apollo.io API.
        
        Uses the /mixed_people/search endpoint with POST request.
        
        Args:
            company: Company name to search
            filters: Additional filters (e.g., {'state': 'CA'})
            
        Returns:
            List of ProfileData objects
        """
        filters = filters or {}
        
        # Build request body for Apollo API
        body = {
            "q_organization_name": company,
            "page": 1,
            "per_page": 25,
        }
        
        # Add location filters if provided
        if "state" in filters and filters["state"]:
            # Apollo uses person_locations for state filtering
            body["person_locations"] = [f"United States, {filters['state']}"]
        
        # Headers with API key (Apollo requires X-Api-Key header)
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        
        all_profiles = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Paginate through results (limit to first 3 pages for safety)
            max_pages = 3
            
            while body["page"] <= max_pages:
                try:
                    # Use /people/search endpoint (available on free plans)
                    response = await client.post(
                        f"{self.BASE_URL}/people/search",
                        json=body,
                        headers=headers
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    people = data.get("people", [])
                    if not people:
                        break
                    
                    # Convert Apollo format to ProfileData
                    for person in people:
                        profile = self._convert_apollo_person(person)
                        if profile:
                            all_profiles.append(profile)
                    
                    # Check if there are more pages
                    pagination = data.get("pagination", {})
                    total_pages = pagination.get("total_pages", 1)
                    
                    if body["page"] >= total_pages:
                        break
                    
                    body["page"] += 1
                    
                except httpx.HTTPStatusError as e:
                    print(f"Apollo API error: {e.response.status_code} - {e.response.text}")
                    raise
        
        return all_profiles
    
    async def get_profile(self, profile_id: str) -> ProfileData:
        """
        Get a single profile by Apollo person ID.
        
        Args:
            profile_id: Apollo person ID
            
        Returns:
            ProfileData object
        """
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/people/{profile_id}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            person = data.get("person", {})
            profile = self._convert_apollo_person(person)
            if not profile:
                raise ValueError(f"Invalid profile data for ID: {profile_id}")
            
            return profile
    
    async def bulk_refresh(self, profile_ids: List[str]) -> List[ProfileData]:
        """
        Refresh multiple profiles in bulk.
        
        Args:
            profile_ids: List of Apollo person IDs
            
        Returns:
            List of updated ProfileData objects
        """
        profiles = []
        # Apollo doesn't have a true bulk endpoint, so we fetch individually
        # In production, consider batching with asyncio.gather
        for profile_id in profile_ids:
            try:
                profile = await self.get_profile(profile_id)
                profiles.append(profile)
            except Exception as e:
                # Log error but continue with other profiles
                print(f"Error refreshing profile {profile_id}: {e}")
                continue
        
        return profiles
    
    def _convert_apollo_person(self, person: dict) -> Optional[ProfileData]:
        """
        Convert Apollo.io person object to ProfileData.
        
        Args:
            person: Apollo person dictionary
            
        Returns:
            ProfileData object or None if invalid
        """
        if not person:
            return None
        
        # Extract education
        education = []
        schools = person.get("schools", [])
        for school in schools:
            if school.get("name"):
                education.append(EducationData(
                    institution=school.get("name", ""),
                    graduation_year=school.get("graduation_year"),
                    degree_type=school.get("degree")
                ))
        
        # Extract work history
        work_history = []
        experiences = person.get("experience", [])
        for exp in experiences:
            work_history.append(WorkHistoryData(
                title=exp.get("title", ""),
                company=exp.get("organization_name"),
                start_date=self._parse_date(exp.get("started_at")),
                end_date=self._parse_date(exp.get("ended_at")),
                is_current=exp.get("is_current", False)
            ))
        
        # Extract location state
        location_state = None
        location = person.get("city_state", "") or person.get("state", "")
        if location:
            # Try to extract state code (e.g., "San Francisco, CA" -> "CA")
            parts = location.split(",")
            if len(parts) > 1:
                location_state = parts[-1].strip()[:2].upper()
            elif len(location) == 2:
                location_state = location.upper()
        
        return ProfileData(
            external_id=str(person.get("id", "")),
            full_name=person.get("name", ""),
            current_title=person.get("title"),
            current_company=person.get("organization_name"),
            location_state=location_state,
            education=education,
            work_history=work_history
        )
    
    @staticmethod
    def _parse_date(date_str: Optional[str]):
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            from datetime import datetime
            # Apollo typically returns ISO format dates
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.date()
        except:
            return None

