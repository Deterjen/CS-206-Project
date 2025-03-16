import logging
import os

from dotenv import load_dotenv

from services.recommendation_service import UniversityRecommendationService
from services.supabase_db import SupabaseDB

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv('.env.local')

# Log the loaded environment variables
logging.debug(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
logging.debug(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')}")

if __name__ == '__main__':
    # Initialize the service
    logging.debug("Initializing SupabaseDB from environment.")
    supabase_db = SupabaseDB.from_env()
    logging.debug("SupabaseDB initialized.")

    logging.debug("Initializing UniversityRecommendationService.")
    recommendation_service = UniversityRecommendationService(supabase_db)
    logging.debug("UniversityRecommendationService initialized.")

    # Initialize the recommender with data
    logging.debug("Initializing recommender with data.")
    recommendation_service.initialize_recommender()
    logging.debug("Recommender initialized.")

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
    logging.debug("Processing questionnaire submission.")
    student_record = recommendation_service.process_questionnaire(questionnaire_data)
    student_id = student_record["core"]["id"]
    logging.debug(f"Questionnaire processed. Student ID: {student_id}")

    # Generate recommendations
    logging.debug("Generating recommendations.")
    recommendations = recommendation_service.generate_recommendations(student_id, top_n=5)
    logging.debug(f"Recommendations generated: {recommendations}")

    # Get similar students
    logging.debug("Getting similar students.")
    similar_students = recommendation_service.get_similar_students(student_id, top_n=3)
    logging.debug(f"Similar students found: {similar_students}")

    # Get recommendation details
    logging.debug("Getting recommendation details.")
    recommendation_details = recommendation_service.get_recommendation_details(recommendations[0]["id"])
    logging.debug(f"Recommendation details: {recommendation_details}")

    # Collect feedback
    logging.debug("Collecting feedback.")
    feedback = recommendation_service.collect_feedback(
        recommendations[0]["id"],
        rating=4,
        text="This recommendation was very helpful and matched my preferences well!"
    )
    logging.debug(f"Feedback collected: {feedback}")
