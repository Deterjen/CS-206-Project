import logging
from typing import List, Dict, Any, Optional

from .recommendation_model import UniversityRecommender
from .supabase_client import SupabaseDB

logger = logging.getLogger(__name__)


class UniversityRecommendationService:
    """
    Service class that connects the database client with the recommendation model.
    This class orchestrates the recommendation process, managing data flow between
    the database and the recommender model.
    """

    def __init__(self, supabase_client: SupabaseDB):
        """
        Initialize the service with a Supabase client.

        Args:
            supabase_client: Initialized SupabaseDB client
        """
        self.db = supabase_client
        self.recommender = UniversityRecommender()

        # Cache for frequently accessed data
        self._universities_cache = {}
        self._programs_cache = {}
        self._existing_students_cache = {}

    def initialize_recommender(self, category_weights: Optional[Dict[str, float]] = None):
        """
        Initialize the recommendation model with data from the database.

        Args:
            category_weights: Optional custom weights for recommendation categories
        """
        # Create a fresh recommender (or update weights if provided)
        if category_weights:
            self.recommender = UniversityRecommender(category_weights=category_weights)

        # Load all necessary data from the database in a single operation
        # This dramatically reduces database calls during recommendation
        self._load_all_data()

        # Provide this data to the recommender
        self.recommender.set_data(
            list(self._universities_cache.values()),
            list(self._existing_students_cache.values()),
            list(self._programs_cache.values())
        )

    def _load_all_data(self):
        """Load and cache all necessary data from the database in an optimized way"""
        # Clear existing caches
        self._universities_cache = {}
        self._programs_cache = {}
        self._existing_students_cache = {}

        # 1. Load all universities in a single query
        logger.info("Loading all universities...")
        universities = self.db.get_universities(limit=1000)
        self._universities_cache = {u["id"]: u for u in universities}

        # 2. Load all programs in a single query
        logger.info("Loading all programs...")
        programs = self.db.get_programs(limit=1000)
        self._programs_cache = {p["id"]: p for p in programs}

        # 3. Load all existing students with optimized queries
        logger.info("Loading existing student profiles...")
        self._load_existing_students_optimized()

    def _load_existing_students_optimized(self):
        """Load all existing students with optimized batch queries"""
        # Get all existing student IDs first
        response = self.db.supabase.table("existing_students").select("id").execute()
        student_ids = [student["id"] for student in response.data]

        # Use batch processing to reduce the number of queries
        batch_size = 50  # Adjust based on your database performance
        total_students = len(student_ids)

        logger.info(f"Loading {total_students} student profiles in batches of {batch_size}...")

        # Load sections in batches to minimize database roundtrips
        for i in range(0, total_students, batch_size):
            batch_ids = student_ids[i:i + batch_size]
            logger.info(f"Loading student batch {i + 1}-{min(i + batch_size, total_students)}...")

            # Load core student data
            core_data = self._batch_load_section("existing_students", batch_ids)

            # Load all sections with a single query per section
            sections = {
                "university_info": self._batch_load_section("existing_students_university_info", batch_ids),
                "academic": self._batch_load_section("existing_students_academic", batch_ids),
                "social": self._batch_load_section("existing_students_social", batch_ids),
                "career": self._batch_load_section("existing_students_career", batch_ids),
                "financial": self._batch_load_section("existing_students_financial", batch_ids),
                "facilities": self._batch_load_section("existing_students_facilities", batch_ids),
                "reputation": self._batch_load_section("existing_students_reputation", batch_ids),
                "personal_fit": self._batch_load_section("existing_students_personal_fit", batch_ids),
                "selection_criteria": self._batch_load_section("existing_students_selection_criteria", batch_ids),
                "additional_insights": self._batch_load_section("existing_students_additional_insights", batch_ids)
            }

            # Combine and process each student
            for core in core_data:
                student_id = core["id"]
                student_data = {"core": core}

                # Add each section data
                for section_name, section_data in sections.items():
                    student_section = next((s for s in section_data if s["student_id"] == student_id), None)
                    if student_section:
                        student_data[section_name] = student_section

                # Flatten the student data for the recommender
                flat_student = self._flatten_existing_student(student_data)
                self._existing_students_cache[student_id] = flat_student

    def _batch_load_section(self, table_name, student_ids):
        """Load a section of student data for multiple students at once"""
        # For core table, use 'id in (...)' filter
        if table_name == "existing_students":
            response = self.db.supabase.table(table_name) \
                .select("*") \
                .in_("id", student_ids) \
                .execute()
        # For section tables, use 'student_id in (...)' filter
        else:
            response = self.db.supabase.table(table_name) \
                .select("*") \
                .in_("student_id", student_ids) \
                .execute()

        return response.data

    def _flatten_existing_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten a nested student profile into a single dictionary for easier processing.

        Args:
            student_data: A nested dictionary with student data sections

        Returns:
            A flat dictionary with all student attributes
        """
        flat_data = {"id": student_data["core"]["id"]}

        # Copy core data
        for key, value in student_data["core"].items():
            if key != "id":  # Already have this
                flat_data[key] = value

        # Copy data from each section
        for section in ["university_info", "academic", "social", "career",
                        "financial", "facilities", "reputation", "personal_fit",
                        "selection_criteria", "additional_insights"]:
            if section in student_data and student_data[section]:
                for key, value in student_data[section].items():
                    if key not in ["id", "student_id", "created_at"]:
                        flat_data[key] = value

        return flat_data

    def get_university_by_id(self, university_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a university by ID from cache or database.

        Args:
            university_id: ID of the university

        Returns:
            University data or None if not found
        """
        # Check cache first
        if university_id in self._universities_cache:
            return self._universities_cache[university_id]

        # If not in cache, try to fetch from database
        university = self.db.get_university_by_id(university_id)

        # Update cache if found
        if university:
            self._universities_cache[university_id] = university

        return university

    def process_questionnaire(self, aspiring_student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete aspiring student questionnaire.

        Args:
            aspiring_student_data: Dictionary with all questionnaire responses

        Returns:
            Created aspiring student record
        """
        # Validate and format the data
        try:
            formatted_data = self._format_aspiring_student_data(aspiring_student_data)

            # Create the aspiring student record
            result = self.db.create_aspiring_student_complete(formatted_data)
            return result
        except Exception as e:
            # Log the error
            logger.error(f"Error processing questionnaire: {e}")
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

    def get_aspiring_student_profile(self, student_id: int) -> Dict[str, Any]:
        """
        Get a complete aspiring student profile in a format suitable for the recommender.

        Args:
            student_id: ID of the aspiring student

        Returns:
            A flat dictionary with all student attributes
        """
        # Get all the data from the database
        profile_data = {}

        # Get core data in a single query
        core_response = self.db.supabase.table("aspiring_students").select("*").eq("id", student_id).limit(1).execute()
        if not core_response.data:
            raise ValueError(f"Aspiring student with ID {student_id} not found")

        # Get all sections in a more efficient way
        sections = [
            "academic", "social", "career", "financial",
            "geographic", "facilities", "reputation", "personal_fit"
        ]

        for section in sections:
            table_name = f"aspiring_students_{section}"
            section_response = self.db.supabase.table(table_name).select("*").eq("student_id", student_id).limit(
                1).execute()

            if section_response.data:
                # Extract all fields except id and student_id
                section_data = section_response.data[0]
                for key, value in section_data.items():
                    if key not in ["id", "student_id", "created_at"]:
                        profile_data[key] = value

        return profile_data

    def generate_recommendations(self, aspiring_student_id: int, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Generate university recommendations for an aspiring student.
        Similar students are saved but not included in the response for modularity.

        Args:
            aspiring_student_id: ID of the aspiring student
            top_n: Number of recommendations to generate

        Returns:
            List of university recommendations with scores
        """
        # Get the aspiring student's profile
        aspiring_profile = self.get_aspiring_student_profile(aspiring_student_id)

        # Generate recommendations using the recommender
        raw_recommendations = self.recommender.recommend_universities(aspiring_profile, top_n=top_n)

        # Process and save recommendations
        saved_recommendations = []

        for rec in raw_recommendations:
            # Prepare recommendation data without similar students
            rec_data = {
                "aspiring_student_id": aspiring_student_id,
                "university_id": rec["university_id"],
                "overall_score": rec["overall_score"],
                "academic_score": rec["academic_score"],
                "social_score": rec["social_score"],
                "financial_score": rec["financial_score"],
                "career_score": rec["career_score"],
                "geographic_score": rec["geographic_score"],
                "facilities_score": rec["facilities_score"],
                "reputation_score": rec["reputation_score"],
                "personal_fit_score": rec["personal_fit_score"]
            }

            # Insert recommendation record
            rec_response = self.db.supabase.table("recommendations").insert(rec_data).execute()
            recommendation_id = rec_response.data[0]["id"]
            saved_rec = rec_response.data[0]

            # Save similar students separately with detailed similarity scores
            for student in rec.get("similar_students", []):
                student_data = {
                    "recommendation_id": recommendation_id,
                    "existing_student_id": student["student_id"],
                    "similarity_score": student["overall_similarity"],
                    "academic_similarity": student.get("academic_similarity", 0),
                    "social_similarity": student.get("social_similarity", 0),
                    "financial_similarity": student.get("financial_similarity", 0),
                    "career_similarity": student.get("career_similarity", 0),
                    "geographic_similarity": student.get("geographic_similarity", 0),
                    "facilities_similarity": student.get("facilities_similarity", 0),
                    "reputation_similarity": student.get("reputation_similarity", 0),
                    "personal_fit_similarity": student.get("personal_fit_similarity", 0)
                }

                self.db.supabase.table("similar_students").insert(student_data).execute()

            saved_recommendations.append(saved_rec)

        return saved_recommendations

    def get_similar_students(self, recommendation_id: int) -> List[Dict[str, Any]]:
        """
        Get all similar students for a specific recommendation.

        Args:
            recommendation_id: ID of the recommendation

        Returns:
            List of similar students with detailed similarity scores
        """
        # Get similar students from the database with an optimized query
        response = self.db.supabase.table("similar_students") \
            .select("*, existing_students(*)") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        similar_students = response.data

        # Transform the data to match the expected format
        formatted_students = []
        for student in similar_students:
            # Get university for this student from cache or database
            student_university_id = student["existing_students"]["university_id"]
            university = self.get_university_by_id(student_university_id)

            # Create the formatted student object
            formatted_student = {
                "student_id": student["existing_student_id"],
                "university_id": student_university_id,
                "university_name": university["name"],
                "overall_similarity": student["similarity_score"],
                "academic_similarity": student["academic_similarity"],
                "social_similarity": student["social_similarity"],
                "financial_similarity": student["financial_similarity"],
                "career_similarity": student["career_similarity"],
                "geographic_similarity": student["geographic_similarity"],
                "facilities_similarity": student["facilities_similarity"],
                "reputation_similarity": student["reputation_similarity"],
                "personal_fit_similarity": student["personal_fit_similarity"]
            }
            formatted_students.append(formatted_student)

        return formatted_students

    def get_recommendation_details(self, recommendation_id: int) -> Dict[str, Any]:
        """
        Get comprehensive details for a recommendation including university and similar students.

        Args:
            recommendation_id: ID of the recommendation

        Returns:
            Comprehensive recommendation data
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
        university = self.get_university_by_id(university_id)

        # Get similar students with formatted structure
        similar_students = self.get_similar_students(recommendation_id)

        # Combine all data
        result = {
            "recommendation": recommendation,
            "university": university,
            "similar_students": similar_students
        }

        return result

    def get_recommendations_details(self, aspiring_student_id: int) -> List[Dict[str, Any]]:
        """
        Get all recommendations for an aspiring student with university and similar student details.

        Args:
            aspiring_student_id: ID of the aspiring student

        Returns:
            List of comprehensive recommendation data
        """
        # Get all recommendations for this student
        response = self.db.supabase.table("recommendations") \
            .select("*") \
            .eq("aspiring_student_id", aspiring_student_id) \
            .order("overall_score", desc=True) \
            .execute()

        recommendations = response.data

        # Get details for each recommendation
        detailed_recommendations = []
        for rec in recommendations:
            detailed_rec = self.get_recommendation_details(rec["id"])
            detailed_recommendations.append(detailed_rec)

        return detailed_recommendations

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

    def refresh_recommender(self):
        """
        Refresh the recommender with the latest data from the database.
        Call this when significant changes have been made to the data.
        """
        self.initialize_recommender(self.recommender.category_weights)
