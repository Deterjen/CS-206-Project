from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: EmailStr
    name: str
    password: str
    disabled: bool

class RecommendationRequest(BaseModel):
    selection_criteria: List[str]  # 3 items (e.g., cost, ranking, career support)
    ccas: List[str]  # List of extracurricular activities
    cost_importance: int
    culture_importance: int
    internship_importance: int
    ranking_influence: int
    extracurricular_importance: int
    family_influence: int
    friend_influence: int
    social_media_influence: int
    leadership_role: int
    extracurricular_hours: int
    plans_further_education: str  # "yes", "no", "undecided"
    preferred_fields: List[str]  # Preferred study fields
    learning_style: str  # Preferred learning style
    weekly_extracurricular_hours: int
    affordability_importance: int
    financial_aid_interest: bool
    internship_experience: bool
    job_placement_support: int
    alumni_network_value: int
    leadership_interest: bool
    preferred_region: str  # Location preference
    preferred_setting: str  # "Urban", "Rural", etc.
    preferred_living_arrangement: str  # "On Campus", "Off Campus"
    important_facilities: List[str]  # List of must-have campus facilities
    modern_amenities_importance: int
    ranking_importance: int
    important_selection_factors: List[str]  # List of top decision factors
    personality_traits: List[str]  # Personal traits
    preferred_student_population: str
    algorithm: Optional[str] = "hybrid"
    num_results: Optional[int] = 5
