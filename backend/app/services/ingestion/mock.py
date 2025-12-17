"""Mock provider for testing without API access."""
from typing import List, Optional, Dict
from app.services.ingestion.base import PeopleDataProvider
from app.schemas.profile import ProfileData, EducationData, WorkHistoryData
from datetime import date
import random


class MockProvider(PeopleDataProvider):
    """
    Mock provider for testing the system without real API access.
    
    Generates sample profiles based on search parameters.
    """
    
    # Sample data for generating mock profiles
    FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Chris", "Lisa", "Alex", "Rachel"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Martinez", "Wilson"]
    TITLES = ["Software Engineer", "Product Manager", "Data Scientist", "Engineering Manager", "VP Engineering", "Director of Product"]
    FOUNDER_TITLES = ["Founder", "Co-Founder", "CEO", "Founding Engineer", "Owner"]
    UNIVERSITIES = ["Stanford University", "MIT", "Harvard University", "UC Berkeley", "Carnegie Mellon", "Georgia Tech"]
    
    async def search_by_company(
        self, 
        company: str, 
        filters: Optional[Dict] = None
    ) -> List[ProfileData]:
        """Generate mock profiles for a company search."""
        filters = filters or {}
        state = filters.get("state", "CA")
        
        # Generate 5-10 mock profiles per company
        num_profiles = random.randint(5, 10)
        profiles = []
        
        for i in range(num_profiles):
            # Randomly decide if this person has become a founder (10% chance)
            is_founder = random.random() < 0.1
            
            first_name = random.choice(self.FIRST_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            
            # Current role
            if is_founder:
                current_title = random.choice(self.FOUNDER_TITLES)
                current_company = f"{first_name}'s Startup Inc."
            else:
                current_title = random.choice(self.TITLES)
                current_company = company
            
            # Generate graduation year (7-15 years ago)
            graduation_year = 2024 - random.randint(7, 15)
            
            profiles.append(ProfileData(
                external_id=f"mock-{company.lower().replace(' ', '-')}-{i}-{random.randint(1000, 9999)}",
                full_name=f"{first_name} {last_name}",
                current_title=current_title,
                current_company=current_company,
                location_state=state if isinstance(state, str) else state[0] if state else "CA",
                education=[
                    EducationData(
                        institution=random.choice(self.UNIVERSITIES),
                        graduation_year=graduation_year,
                        degree_type="Bachelor's"
                    )
                ],
                work_history=[
                    WorkHistoryData(
                        title=current_title,
                        company=current_company,
                        is_current=True
                    ),
                    WorkHistoryData(
                        title=random.choice(self.TITLES),
                        company=company,
                        is_current=False
                    )
                ]
            ))
        
        return profiles
    
    async def get_profile(self, profile_id: str) -> ProfileData:
        """Get a mock profile by ID."""
        return ProfileData(
            external_id=profile_id,
            full_name="Mock Person",
            current_title="Software Engineer",
            current_company="Mock Company",
            location_state="CA",
            education=[
                EducationData(
                    institution="Stanford University",
                    graduation_year=2015,
                    degree_type="Bachelor's"
                )
            ],
            work_history=[]
        )
    
    async def bulk_refresh(self, profile_ids: List[str]) -> List[ProfileData]:
        """Refresh mock profiles - generates new random data."""
        profiles = []
        for profile_id in profile_ids:
            profile = await self.get_profile(profile_id)
            profiles.append(profile)
        return profiles

