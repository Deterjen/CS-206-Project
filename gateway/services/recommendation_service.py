import logging
from typing import List, Dict, Any, Optional

from .recommendation_model import UniversityRecommender
from .supabase_client import SupabaseDB

logger = logging.getLogger(__name__)


class UniversityRecommendationService:
    """
    Enhanced service class that connects the database client with the recommendation model.
    This class orchestrates the recommendation process, managing data flow between
    the database and the recommender model with improved efficiency and accuracy.
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
        Optimized to load a representative sample of data in minimal queries.

        Args:
            category_weights: Optional custom weights for recommendation categories
        """
        # Create a fresh recommender (or update weights if provided)
        if category_weights:
            self.recommender = UniversityRecommender(category_weights=category_weights)

        # Load all necessary data in bulk (3-4 queries max)
        self._load_all_data()

        # Provide this data to the recommender
        self.recommender.set_data(
            list(self._universities_cache.values()),
            list(self._existing_students_cache.values()),
            list(self._programs_cache.values())
        )

        logger.info(f"Recommender initialized with {len(self._universities_cache)} universities, "
                    f"{len(self._programs_cache)} programs, and "
                    f"{len(self._existing_students_cache)} student profiles")

    def _load_all_data(self):
        """
        Load and cache all necessary data from the database in an optimized way.
        Uses a representative sample approach for student profiles to ensure
        diversity and representativeness while minimizing database load.
        """
        # Clear existing caches
        self._universities_cache = {}
        self._programs_cache = {}
        self._existing_students_cache = {}

        # 1. Load all universities in a single query
        logger.info("Loading all universities...")
        universities = self.db.get_universities(limit=1000)
        self._universities_cache = {u["id"]: u for u in universities}
        logger.info(f"Loaded {len(universities)} universities")

        # 2. Load all programs in a single query
        logger.info("Loading all programs...")
        programs = self.db.get_programs(limit=1000)
        self._programs_cache = {p["id"]: p for p in programs}
        logger.info(f"Loaded {len(programs)} programs")

        # 3. Load a diverse, representative sample of existing students
        logger.info("Loading representative student profiles for vector similarity index...")
        self._load_representative_student_sample()

    def _load_representative_student_sample(self):
        """
        Load a representative sample of student profiles for recommendation
        """
        # Get a balanced and diverse sample across universities and programs
        student_ids = self.db.get_balanced_student_sample(students_per_university=100)

        total_students = len(student_ids)
        logger.info(f"Selected {total_students} diverse student profiles for vector indexing")

        # Process in batches to avoid memory issues
        batch_size = 100
        for i in range(0, total_students, batch_size):
            batch_ids = student_ids[i:i + batch_size]
            logger.info(f"Loading student batch {i + 1}-{min(i + batch_size, total_students)} of {total_students}...")

            # Get complete data for these students with minimal queries
            student_batch = self.db.get_complete_existing_students_batch(batch_ids)

            # Process each student and convert to flat format for the recommender
            for student_id, student_data in student_batch.items():
                if "core" in student_data:  # Make sure we have the core data
                    flat_student = self._flatten_existing_student(student_data)
                    self._existing_students_cache[student_id] = flat_student

        logger.info(f"Successfully loaded {len(self._existing_students_cache)} complete student profiles")

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

    def _flatten_aspiring_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flatten a nested aspiring student profile for the recommender.

        Args:
            student_data: Nested dictionary with aspiring student data

        Returns:
            Flat dictionary with all attributes
        """
        flat_data = {}

        # Copy data from each section
        for section in ["core", "academic", "social", "career", "financial",
                        "geographic", "facilities", "reputation", "personal_fit"]:
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

    async def process_questionnaire(self, username: str, aspiring_student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete aspiring student questionnaire.

        Args:
            username: Username of the aspiring student
            aspiring_student_data: Dictionary with all questionnaire responses

        Returns:
            Created aspiring student record
        """
        # Validate and format the data
        try:
            formatted_data = self._format_aspiring_student_data(aspiring_student_data)

            # Create the aspiring student record
            result = await self.db.create_aspiring_student_complete(username, formatted_data)
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
            # "core": {},
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

    async def get_aspiring_student_profile(self, username: str) -> Dict[str, Any]:
        """
        Get a complete aspiring student profile for the recommender.
        Optimized to use a single query and return a flat structure.

        Args:
            username: Username of the aspiring student

        Returns:
            Flat dictionary with all student attributes
        """
        # Get the aspiring student ID from the username
        aspiring_student_id = await self._get_aspiring_student_id_from_username(username)

        # Get the complete profile data with a single optimized query
        profile_data = self.db.get_aspiring_student_complete(aspiring_student_id)

        if not profile_data:
            raise ValueError(f"Aspiring student with ID {aspiring_student_id} not found")

        # Convert to flat structure for the recommender
        flat_profile = self._flatten_aspiring_student(profile_data)

        return flat_profile

    async def _get_aspiring_student_id_from_username(self, username: str) -> int:
        """
        Get the aspiring student ID from a username.

        Args:
            username: Username of the aspiring student

        Returns:
            ID of the aspiring student
        """
        aspiring_student = await self.db.get_aspiring_student(username)
        if not aspiring_student or not aspiring_student[0]:
            raise ValueError(f"Aspiring student with username {username} not found")

        return aspiring_student[0]["id"]

    async def generate_recommendations(self, username: str, top_n: int = 10):
        """
        Generate university recommendations for an aspiring student.
        Uses vector similarity search for more accurate recommendations
        with minimal database queries.

        Args:
            username: Username of the aspiring student
            top_n: Number of recommendations to generate

        Returns:
            List of university recommendations with scores
        """
        # Get the aspiring student's profile (1 query)
        logger.info(f"Fetching aspiring student profile for username {username}")
        aspiring_profile = await self.get_aspiring_student_profile(username)
        print("aspiring student: ", aspiring_profile)

        # Generate recommendations using the in-memory recommender with improved vector similarity (0 queries)
        logger.info("Generating recommendations using vector similarity search")
        raw_recommendations = self.recommender.recommend_universities(aspiring_profile, top_n=top_n)
        print("raw recommendations: ", raw_recommendations)

        # Log stats
        unique_universities = len(raw_recommendations)
        logger.info(f"Generated {unique_universities} unique university recommendations")

        # Get the aspiring student ID from the username for saving recommendations
        aspiring_student_id = await self._get_aspiring_student_id_from_username(username)
        print("aid: ", aspiring_student_id)

        # Save all recommendations and similar students in a batch (1-2 queries)
        logger.info("Saving recommendations and similar students in batch")
        saved_recommendations = self.db.save_recommendations_batch(aspiring_student_id, raw_recommendations)

        logger.info(f"Successfully saved {len(saved_recommendations)} recommendations")
        return saved_recommendations

    def get_similar_students(self, recommendation_id: int) -> List[Dict[str, Any]]:
        """
        Get similar students for a recommendation.
        Note: This is now handled by get_recommendation_with_details for efficiency.

        Args:
            recommendation_id: ID of the recommendation

        Returns:
            List of similar students
        """
        # Get recommendation details which includes similar students
        details = self.db.get_recommendation_with_details(recommendation_id)
        return details.get("similar_students", [])

    def get_recommendation_details(self, recommendation_id: int) -> Dict[str, Any]:
        """
        Get comprehensive details for a recommendation.
        Uses a single optimized query.

        Args:
            recommendation_id: ID of the recommendation

        Returns:
            Comprehensive recommendation data
        """
        return self.db.get_recommendation_with_details(recommendation_id)

    async def get_recommendations_details(self, username: str) -> List[Dict[str, Any]]:
        """
        Get all recommendations for an aspiring student with details.
        Uses a minimal number of optimized queries.

        Args:
            username: Username of the aspiring student

        Returns:
            List of comprehensive recommendation data
        """
        # Get the aspiring student ID from the username
        aspiring_student_id = await self._get_aspiring_student_id_from_username(username)

        return self.db.get_recommendations_with_details(aspiring_student_id)

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
        Call this periodically to ensure recommendations stay current.
        """
        logger.info("Refreshing recommender data...")
        self.initialize_recommender(self.recommender.category_weights)
        logger.info("Recommender data refresh complete")
