from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_disabled: Optional[bool] = False

class RecommendationRequest(BaseModel):
    algorithm: Optional[str] = "hybrid"
    num_results: Optional[int] = 5
    # Academic section
    preferred_fields: List[str]
    learning_style: str
    career_goals: List[str]
    further_education: str
    # Social section
    culture_importance: int
    interested_activities: List[str]
    weekly_extracurricular_hours: int
    passionate_actvities: List[str]
    # Career section
    internship_importance: int
    leadership_interest: bool
    alumni_network_value: int
    # Financial section
    affordability_importance: int
    yearly_budget: int
    financial_aid_interest: bool
    # Geographic section
    preferred_region: str
    preferred_setting: str
    preferred_living_arrangement: str
    # Facilities section
    important_facilities: List[str]
    modern_amenities_importance: int
    # Reputation section
    ranking_importance: int
    alumni_testimonial_influence: int
    important_selection_factors: List[str]
    # Personal fit section
    personality_traits: List[str]
    preferred_student_population: str
    lifestyle_preferences: str