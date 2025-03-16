from typing import List, Dict, Any, Optional

from .recommendation_model import UniversityRecommender
from .supabase_db import SupabaseDB


class UniversityRecommendationService:
    """
    Service class that connects the database client with the recommendation model.
    This class handles the business logic for university recommendations.
    """

    def __init__(self, supabase_client: SupabaseDB):
        """
        Initialize the service with a Supabase client.

        Args:
            supabase_client: Initialized SupabaseDB client
        """
        self.db = supabase_client
        self.recommender = UniversityRecommender()

    def initialize_recommender(self, category_weights: Optional[Dict[str, float]] = None):
        """
        Initialize the recommendation model with data from the database.

        Args:
            category_weights: Optional custom weights for recommendation categories
        """
        self.recommender = UniversityRecommender(category_weights=category_weights)
        # Load data into the recommender
        self.recommender.load_data(self.db.supabase)

    def process_questionnaire(self, aspiring_student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete aspiring student questionnaire.

        Args:
            aspiring_student_data: Dictionary with all questionnaire responses

        Returns:
            Created aspiring student record
        """
        # Validate and format the data using Pydantic models
        try:
            # Parse the data into appropriate sections
            formatted_data = self._format_aspiring_student_data(aspiring_student_data)

            # Create the aspiring student record
            result = self.db.create_aspiring_student_complete(formatted_data)
            return result
        except Exception as e:
            # Log the error
            print(f"Error processing questionnaire: {e}")
            raise

    def _format_aspiring_student_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw questionnaire data into structured sections for database storage.

        Args:
            raw_data: Raw questionnaire data

        Returns:
            Formatted data grouped by sections
        """
        # Initialize sections
        formatted_data = {
            "core": {},
            "academic": {},
            "social": {},
            "career": {},
            "financial": {},
            "geographic": {},
            "facilities": {},
            "reputation": {},
            "personal_fit": {}
        }

        # Map questions to sections based on questionnaire structure
        # Academic section
        if "preferred_fields" in raw_data:
            formatted_data["academic"]["preferred_fields"] = raw_data["preferred_fields"]
        if "learning_style" in raw_data:
            formatted_data["academic"]["learning_style"] = raw_data["learning_style"]
        if "career_goals" in raw_data:
            formatted_data["academic"]["career_goals"] = raw_data["career_goals"]
        if "further_education" in raw_data:
            formatted_data["academic"]["further_education"] = raw_data["further_education"]

        # Social section
        if "culture_importance" in raw_data:
            formatted_data["social"]["culture_importance"] = raw_data["culture_importance"]
        if "interested_activities" in raw_data:
            formatted_data["social"]["interested_activities"] = raw_data["interested_activities"]
        if "weekly_extracurricular_hours" in raw_data:
            formatted_data["social"]["weekly_extracurricular_hours"] = raw_data["weekly_extracurricular_hours"]
        if "passionate_activities" in raw_data:
            formatted_data["social"]["passionate_activities"] = raw_data["passionate_activities"]

        # Career section
        if "internship_importance" in raw_data:
            formatted_data["career"]["internship_importance"] = raw_data["internship_importance"]
        if "leadership_interest" in raw_data:
            formatted_data["career"]["leadership_interest"] = raw_data["leadership_interest"]
        if "alumni_network_value" in raw_data:
            formatted_data["career"]["alumni_network_value"] = raw_data["alumni_network_value"]

        # Financial section
        if "affordability_importance" in raw_data:
            formatted_data["financial"]["affordability_importance"] = raw_data["affordability_importance"]
        if "yearly_budget" in raw_data:
            formatted_data["financial"]["yearly_budget"] = raw_data["yearly_budget"]
        if "financial_aid_interest" in raw_data:
            formatted_data["financial"]["financial_aid_interest"] = raw_data["financial_aid_interest"]

        # Geographic section
        if "preferred_region" in raw_data:
            formatted_data["geographic"]["preferred_region"] = raw_data["preferred_region"]
        if "preferred_setting" in raw_data:
            formatted_data["geographic"]["preferred_setting"] = raw_data["preferred_setting"]
        if "preferred_living_arrangement" in raw_data:
            formatted_data["geographic"]["preferred_living_arrangement"] = raw_data["preferred_living_arrangement"]

        # Facilities section
        if "important_facilities" in raw_data:
            formatted_data["facilities"]["important_facilities"] = raw_data["important_facilities"]
        if "modern_amenities_importance" in raw_data:
            formatted_data["facilities"]["modern_amenities_importance"] = raw_data["modern_amenities_importance"]

        # Reputation section
        if "ranking_importance" in raw_data:
            formatted_data["reputation"]["ranking_importance"] = raw_data["ranking_importance"]
        if "alumni_testimonial_influence" in raw_data:
            formatted_data["reputation"]["alumni_testimonial_influence"] = raw_data["alumni_testimonial_influence"]
        if "important_selection_factors" in raw_data:
            formatted_data["reputation"]["important_selection_factors"] = raw_data["important_selection_factors"]

        # Personal fit section
        if "personality_traits" in raw_data:
            formatted_data["personal_fit"]["personality_traits"] = raw_data["personality_traits"]
        if "preferred_student_population" in raw_data:
            formatted_data["personal_fit"]["preferred_student_population"] = raw_data["preferred_student_population"]
        if "lifestyle_preferences" in raw_data:
            formatted_data["personal_fit"]["lifestyle_preferences"] = raw_data["lifestyle_preferences"]

        return formatted_data

    def generate_recommendations(self, aspiring_student_id: int, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Generate university recommendations for an aspiring student.

        Args:
            aspiring_student_id: ID of the aspiring student
            top_n: Number of recommendations to generate

        Returns:
            List of university recommendations with scores
        """
        # Get the aspiring student's complete profile
        aspiring_profile = self._get_aspiring_student_profile(aspiring_student_id)

        # Generate recommendations using the recommendation model
        recommendations = self.recommender.recommend_universities(aspiring_profile, top_n=top_n)

        # Save recommendations to the database
        saved_recommendations = self.db.save_recommendations(aspiring_student_id, recommendations)

        return saved_recommendations

    def _get_aspiring_student_profile(self, student_id: int) -> Dict[str, Any]:
        """
        Convert an aspiring student's database record to a profile format for the recommender.

        Args:
            student_id: ID of the aspiring student

        Returns:
            Profile dictionary formatted for the recommendation model
        """
        # Get the aspiring student's complete record
        student_data = {}

        # Get core data
        core_response = self.db.supabase.table("aspiring_students").select("*").eq("id", student_id).limit(1).execute()
        if not core_response.data:
            raise ValueError(f"Aspiring student with ID {student_id} not found")

        # Get all sections
        for section in ["academic", "social", "career", "financial",
                        "geographic", "facilities", "reputation", "personal_fit"]:
            table_name = f"aspiring_students_{section}"
            section_response = self.db.supabase.table(table_name).select("*").eq("student_id", student_id).limit(
                1).execute()

            if section_response.data:
                # Extract all fields except id and student_id
                section_data = section_response.data[0]
                for key, value in section_data.items():
                    if key not in ["id", "student_id", "created_at"]:
                        student_data[key] = value

        return student_data

    def get_similar_students(self, aspiring_student_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Find existing students who are most similar to the aspiring student.

        Args:
            aspiring_student_id: ID of the aspiring student
            top_n: Number of similar students to find

        Returns:
            List of similar students with similarity scores
        """
        # Get the aspiring student's profile
        aspiring_profile = self._get_aspiring_student_profile(aspiring_student_id)

        # Use the recommender to find similar students
        similar_students = self.recommender.find_similar_students(aspiring_profile, top_n=top_n)

        return similar_students

    def get_recommendation_details(self, recommendation_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a recommendation.

        Args:
            recommendation_id: ID of the recommendation

        Returns:
            Detailed recommendation information
        """
        # Get the recommendation
        recommendation_response = self.db.supabase.table("recommendations").select("*").eq("id",
                                                                                           recommendation_id).limit(
            1).execute()

        if not recommendation_response.data:
            raise ValueError(f"Recommendation with ID {recommendation_id} not found")

        recommendation = recommendation_response.data[0]

        # Get the university
        university_id = recommendation["university_id"]
        university = self.db.get_university_by_id(university_id)

        # Get similar students
        similar_students_response = self.db.supabase.table("similar_students") \
            .select("*, existing_students(*)") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        similar_students = similar_students_response.data

        # Combine all data
        result = {
            "recommendation": recommendation,
            "university": university,
            "similar_students": similar_students
        }

        return result

    def collect_feedback(self, recommendation_id: int, rating: int, text: str) -> Dict[str, Any]:
        """
        Collect feedback on a recommendation for model improvement.

        Args:
            recommendation_id: ID of the recommendation
            rating: Feedback rating (1-5)
            text: Feedback text

        Returns:
            Created feedback record
        """
        return self.db.save_recommendation_feedback(recommendation_id, rating, text)


# Example usage:
'''
# Initialize the service
supabase_db = SupabaseDB.from_env()
recommendation_service = UniversityRecommendationService(supabase_db)

# Initialize the recommender with data
recommendation_service.initialize_recommender()

# Process a questionnaire submission
questionnaire_data = {
    "preferred_fields": ["Business", "Computing/IT"],
    "learning_style": "Hands-on/Practical",
    "career_goals": "Technology entrepreneurship",
    "further_education": "Yes",
    "culture_importance": 8,
    "interested_activities": ["Sports", "Professional/Career Clubs"],
    "weekly_extracurricular_hours": "6–10 hours",
    "passionate_activities": "Basketball, coding competitions",
    "internship_importance": 9,
    "leadership_interest": True,
    "alumni_network_value": 8,
    "affordability_importance": 7,
    "yearly_budget": 30000,
    "financial_aid_interest": True,
    "preferred_region": "California",
    "preferred_setting": "Urban",
    "preferred_living_arrangement": "On Campus",
    "important_facilities": ["Libraries and Study Spaces", "Modern Amenities"],
    "modern_amenities_importance": 8,
    "ranking_importance": 7,
    "alumni_testimonial_influence": 8,
    "important_selection_factors": ["Academic Reputation", "Internship Opportunities"],
    "personality_traits": ["Ambitious", "Analytical", "Extroverted"],
    "preferred_student_population": "Large",
    "lifestyle_preferences": "Active campus life with balance between academics and social"
}

# Process the questionnaire
student_record = recommendation_service.process_questionnaire(questionnaire_data)
student_id = student_record["core"]["id"]

# Generate recommendations
recommendations = recommendation_service.generate_recommendations(student_id, top_n=5)

# Get similar students
similar_students = recommendation_service.get_similar_students(student_id, top_n=3)

# Get recommendation details
recommendation_details = recommendation_service.get_recommendation_details(recommendations[0]["id"])

# Collect feedback
feedback = recommendation_service.collect_feedback(
    recommendations[0]["id"],
    rating=4,
    text="This recommendation was very helpful and matched my preferences well!"
)
'''
