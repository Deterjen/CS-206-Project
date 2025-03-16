import enum
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator


# ===== Enum Definitions =====

class YearOfStudy(str, enum.Enum):
    FIRST = "1st year"
    SECOND = "2nd year"
    THIRD = "3rd year"
    FOURTH = "4th year"
    FIFTH_PLUS = "5+ years"
    POSTGRADUATE = "Postgraduate"


class UniversitySize(str, enum.Enum):
    SMALL = "Small"  # <5K students
    MEDIUM = "Medium"  # ~10K students
    LARGE = "Large"  # >20K students


class SettingType(str, enum.Enum):
    URBAN = "Urban"
    RURAL = "Rural"


class LearningStyle(str, enum.Enum):
    HANDS_ON = "Hands-on/Practical"
    LECTURE = "Lecture-based"
    PROJECT = "Project-based"
    RESEARCH = "Research-oriented"
    SEMINAR = "Seminar-based"
    ONLINE = "Online/Remote"
    VISUAL = "Visual"
    AUDITORY = "Auditory"
    THEORETICAL = "Theoretical"
    GROUP = "Group-based"
    SELF_PACED = "Self-paced/Individual"


class WeeklyHours(str, enum.Enum):
    NONE = "0 (None)"
    ONE_TO_FIVE = "1–5 hours"
    SIX_TO_TEN = "6–10 hours"
    ELEVEN_TO_FIFTEEN = "11–15 hours"
    SIXTEEN_TO_TWENTY = "16–20 hours"
    TWENTY_PLUS = "20+ hours"


class FinancialAidPercentage(str, enum.Enum):
    ZERO_TO_25 = "0-25%"
    TWENTY_SIX_TO_50 = "26-50%"
    FIFTY_ONE_TO_75 = "51-75%"
    SEVENTY_SIX_TO_100 = "76-100%"


class LivingArrangement(str, enum.Enum):
    ON_CAMPUS = "On Campus"
    OFF_CAMPUS = "Off Campus"
    COMMUTE = "Commute from Home"


class WouldChooseAgain(str, enum.Enum):
    DEFINITELY_YES = "Definitely Yes"
    PROBABLY_YES = "Probably Yes"
    UNSURE = "Unsure"
    PROBABLY_NOT = "Probably Not"
    DEFINITELY_NOT = "Definitely Not"


# ===== Base Models =====

class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    created_at: Optional[datetime] = None


class IDModel(TimestampedModel):
    """Base model with ID and timestamp fields."""
    id: Optional[int] = None


# ===== Core Models =====

class University(IDModel):
    """University model."""
    name: str
    location: str
    size: Optional[UniversitySize] = None
    setting: Optional[SettingType] = None


class Program(IDModel):
    """Program/major model."""
    university_id: int
    name: str
    department: Optional[str] = None
    degree_level: Optional[str] = None


# ===== Existing Student Models =====

class ExistingStudent(IDModel):
    """Core existing student model."""
    university_id: int
    program_id: int
    year_of_study: YearOfStudy


class ExistingStudentUniversityInfo(IDModel):
    """Existing student university information section."""
    student_id: int
    overall_satisfaction: int = Field(..., ge=1, le=10)
    university_match: int = Field(..., ge=1, le=10)


class ExistingStudentAcademic(IDModel):
    """Existing student academic section."""
    student_id: int
    teaching_quality: int = Field(..., ge=1, le=10)
    learning_styles: List[str]
    professor_accessibility: int = Field(..., ge=1, le=10)
    academic_resources: int = Field(..., ge=1, le=10)
    academic_credentials: Dict[str, Any]

    @validator('learning_styles')
    def validate_learning_styles(cls, v):
        """Validate learning styles."""
        valid_styles = [style.value for style in LearningStyle]
        for style in v:
            if style not in valid_styles and not style.startswith("Other:"):
                raise ValueError(f"Invalid learning style: {style}")
        return v


class ExistingStudentSocial(IDModel):
    """Existing student social section."""
    student_id: int
    campus_culture: List[str]
    extracurricular_activities: List[str]
    weekly_extracurricular_hours: WeeklyHours
    social_groups_ease: int = Field(..., ge=1, le=10)


class ExistingStudentCareer(IDModel):
    """Existing student career section."""
    student_id: int
    job_placement_support: int = Field(..., ge=1, le=10)
    internship_experience: bool
    career_services_helpfulness: int = Field(..., ge=1, le=10)
    alumni_network_strength: int = Field(..., ge=1, le=10)


class ExistingStudentFinancial(IDModel):
    """Existing student financial section."""
    student_id: int
    affordability: int = Field(..., ge=1, le=10)
    received_financial_aid: bool
    financial_aid_percentage: Optional[FinancialAidPercentage] = None
    campus_employment_availability: int = Field(..., ge=1, le=10)


class ExistingStudentFacilities(IDModel):
    """Existing student facilities section."""
    student_id: int
    facilities_quality: int = Field(..., ge=1, le=10)
    regularly_used_facilities: List[str]
    housing_quality: Optional[int] = Field(None, ge=1, le=10)


class ExistingStudentReputation(IDModel):
    """Existing student reputation section."""
    student_id: int
    ranking_importance: int = Field(..., ge=1, le=10)
    employer_value_perception: int = Field(..., ge=1, le=10)
    important_reputation_aspects: List[str]


class ExistingStudentPersonalFit(IDModel):
    """Existing student personal fit section."""
    student_id: int
    personality_match: int = Field(..., ge=1, le=10)
    typical_student_traits: List[str]
    would_choose_again: WouldChooseAgain
    thriving_student_type: str


class ExistingStudentSelectionCriteria(IDModel):
    """Existing student selection criteria section."""
    student_id: int
    important_decision_factors: List[str]
    retrospective_important_factors: str


class ExistingStudentAdditionalInsights(IDModel):
    """Existing student additional insights section."""
    student_id: int
    university_strengths: str
    university_weaknesses: str
    prospective_student_advice: str


# ===== Aspiring Student Models =====

class AspiringStudent(IDModel):
    """Core aspiring student model."""
    pass


class AspiringStudentAcademic(IDModel):
    """Aspiring student academic section."""
    student_id: int
    preferred_fields: List[str]
    learning_style: LearningStyle
    career_goals: str
    further_education: str


class AspiringStudentSocial(IDModel):
    """Aspiring student social section."""
    student_id: int
    culture_importance: int = Field(..., ge=1, le=10)
    interested_activities: List[str]
    weekly_extracurricular_hours: WeeklyHours
    passionate_activities: str


class AspiringStudentCareer(IDModel):
    """Aspiring student career section."""
    student_id: int
    internship_importance: int = Field(..., ge=1, le=10)
    leadership_interest: bool
    alumni_network_value: int = Field(..., ge=1, le=10)


class AspiringStudentFinancial(IDModel):
    """Aspiring student financial section."""
    student_id: int
    affordability_importance: int = Field(..., ge=1, le=10)
    yearly_budget: float
    financial_aid_interest: bool


class AspiringStudentGeographic(IDModel):
    """Aspiring student geographic section."""
    student_id: int
    preferred_region: str
    preferred_setting: SettingType
    preferred_living_arrangement: LivingArrangement


class AspiringStudentFacilities(IDModel):
    """Aspiring student facilities section."""
    student_id: int
    important_facilities: List[str]
    modern_amenities_importance: int = Field(..., ge=1, le=10)


class AspiringStudentReputation(IDModel):
    """Aspiring student reputation section."""
    student_id: int
    ranking_importance: int = Field(..., ge=1, le=10)
    alumni_testimonial_influence: int = Field(..., ge=1, le=10)
    important_selection_factors: List[str]


class AspiringStudentPersonalFit(IDModel):
    """Aspiring student personal fit section."""
    student_id: int
    personality_traits: List[str]
    preferred_student_population: UniversitySize
    lifestyle_preferences: str


# ===== Recommendation Models =====

class Recommendation(IDModel):
    """University recommendation model."""
    aspiring_student_id: int
    university_id: int
    overall_score: float = Field(..., ge=0, le=1)
    academic_score: float = Field(..., ge=0, le=1)
    social_score: float = Field(..., ge=0, le=1)
    financial_score: float = Field(..., ge=0, le=1)
    career_score: float = Field(..., ge=0, le=1)
    geographic_score: float = Field(..., ge=0, le=1)
    facilities_score: float = Field(..., ge=0, le=1)
    reputation_score: float = Field(..., ge=0, le=1)
    personal_fit_score: float = Field(..., ge=0, le=1)


class SimilarStudent(IDModel):
    """Similar student model for recommendations."""
    recommendation_id: int
    existing_student_id: int
    similarity_score: float = Field(..., ge=0, le=1)


class RecommendationFeedback(IDModel):
    """Feedback for recommendations."""
    recommendation_id: int
    feedback_rating: int = Field(..., ge=1, le=5)
    feedback_text: str


# ===== Composite Models =====

class CompleteExistingStudent(BaseModel):
    """Complete existing student model with all sections."""
    core: ExistingStudent
    university_info: Optional[ExistingStudentUniversityInfo] = None
    academic: Optional[ExistingStudentAcademic] = None
    social: Optional[ExistingStudentSocial] = None
    career: Optional[ExistingStudentCareer] = None
    financial: Optional[ExistingStudentFinancial] = None
    facilities: Optional[ExistingStudentFacilities] = None
    reputation: Optional[ExistingStudentReputation] = None
    personal_fit: Optional[ExistingStudentPersonalFit] = None
    selection_criteria: Optional[ExistingStudentSelectionCriteria] = None
    additional_insights: Optional[ExistingStudentAdditionalInsights] = None


class CompleteAspiringStudent(BaseModel):
    """Complete aspiring student model with all sections."""
    core: AspiringStudent
    academic: Optional[AspiringStudentAcademic] = None
    social: Optional[AspiringStudentSocial] = None
    career: Optional[AspiringStudentCareer] = None
    financial: Optional[AspiringStudentFinancial] = None
    geographic: Optional[AspiringStudentGeographic] = None
    facilities: Optional[AspiringStudentFacilities] = None
    reputation: Optional[AspiringStudentReputation] = None
    personal_fit: Optional[AspiringStudentPersonalFit] = None


class CompleteRecommendation(BaseModel):
    """Complete recommendation model with university and similar students."""
    recommendation: Recommendation
    university: University
    similar_students: List[SimilarStudent] = []


# Example usage for validation and conversion between DB and API:
'''
# Create a university from API data
university_data = {
    "name": "Stanford University",
    "location": "California, USA",
    "size": "Large",
    "setting": "Urban"
}
university_model = University(**university_data)

# Convert back to dict for database
university_dict = university_model.dict(exclude_none=True)

# Create an existing student profile with validation
existing_student_data = {
    "core": {
        "university_id": 1,
        "program_id": 1,
        "year_of_study": "3rd year"
    },
    "academic": {
        "student_id": 1,
        "teaching_quality": 8,
        "learning_styles": ["Lecture-based", "Project-based"],
        "professor_accessibility": 7,
        "academic_resources": 9,
        "academic_credentials": {"GPA": "3.8", "SAT": "1450"}
    }
}

# Validate each section
core = ExistingStudent(**existing_student_data["core"])
academic = ExistingStudentAcademic(**existing_student_data["academic"])

# Validate entire profile
complete_profile = CompleteExistingStudent(
    core=core,
    academic=academic
)

# Convert to dict for database operations
profile_dict = {
    "core": complete_profile.core.dict(exclude_none=True),
    "academic": complete_profile.academic.dict(exclude_none=True)
}
'''
