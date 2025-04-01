import logging

import hnswlib
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class UniversityRecommender:
    """
    Memory-optimized recommender model for generating university recommendations based on similarity
    between aspiring student profiles and existing student experiences.
    """

    def __init__(self, category_weights=None):
        """
        Initialize the recommendation model.

        Args:
            category_weights: Optional weights for each category in the calculation
        """
        # Initialize with default or provided category weights
        self.category_weights = category_weights or {
            'academic': 0.2,
            'social': 0.15,
            'financial': 0.15,
            'career': 0.15,
            'geographic': 0.1,
            'facilities': 0.05,
            'reputation': 0.1,
            'personal_fit': 0.1
        }

        # Initialize text embedding model (only when needed)
        self.text_model = None

        # Storage for data
        self.universities = []
        self.existing_students = []
        self.programs = []

        # HNSW indexes
        self.text_indexes = {}
        self.student_profile_index = None
        self.student_vectors = []
        self.student_ids = []

    def _init_text_model(self):
        """Initialize text embedding model only when needed"""
        if self.text_model is None:
            logger.info("Initializing text embedding model")
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')

    def set_data(self, universities, existing_students, programs):
        """
        Set the data for recommendation processing.

        Args:
            universities: List of university data
            existing_students: List of existing student profiles
            programs: List of program data
        """
        self.universities = universities
        self.existing_students = existing_students
        self.programs = programs

        # Only build student profile index (more essential)
        # Skip text indexes to save memory
        self._build_student_profile_index()

    def _build_text_indexes(self, fields=None):
        """
        Build HNSW indexes only for specified text fields to save memory.
        If fields is None, build only for the most important fields.
        """
        # Initialize text model if needed
        self._init_text_model()

        # If fields not specified, use only essential ones
        if fields is None:
            # Only use the most useful fields for recommendations
            fields = ['thriving_student_type', 'university_strengths']

        self.text_indexes = {}

        for field in fields:
            # Get non-null text values
            texts = [s.get(field) for s in self.existing_students if s.get(field)]
            if not texts:
                continue

            # Create embeddings
            embeddings = self.text_model.encode(texts)

            # Create HNSW index with memory-efficient parameters
            dim = embeddings.shape[1]
            index = hnswlib.Index(space='cosine', dim=dim)
            # Use smaller M value and ef_construction for memory efficiency
            index.init_index(max_elements=len(embeddings), ef_construction=100, M=8)
            index.add_items(embeddings, np.arange(len(embeddings)))

            # Store index and mapping to student IDs
            self.text_indexes[field] = {
                'index': index,
                'student_ids': [s.get('id') for s in self.existing_students if s.get(field)]
            }

    def _build_student_profile_index(self):
        """
        Build an HNSW index for efficient similarity search across student profiles.
        Memory-optimized version with reduced parameters.
        """
        logger.info("Building student profile vector index...")

        # Skip if no existing students
        if not self.existing_students:
            logger.warning("No existing students available to build profile index")
            return

        # Create vector representations for all student profiles
        self.student_vectors = []
        self.student_ids = []

        # Set a maximum number of vectors to include to limit memory usage
        max_vectors = min(len(self.existing_students), 300)

        for student in self.existing_students[:max_vectors]:
            # Create a vector representation of the student profile
            vector = self._create_student_vector(student)
            if vector is not None:
                self.student_vectors.append(vector)
                self.student_ids.append(student.get('id'))

        # Convert to numpy array
        if not self.student_vectors:
            logger.warning("No valid student vectors created")
            return

        vectors_array = np.array(self.student_vectors)

        # Create HNSW index with memory-optimized parameters
        if len(vectors_array) > 0:
            dim = vectors_array.shape[1]
            self.student_profile_index = hnswlib.Index(space='cosine', dim=dim)
            # Reduced parameters: M=8 (vs 16), ef_construction=100 (vs 200)
            self.student_profile_index.init_index(max_elements=len(vectors_array), ef_construction=100, M=8)
            self.student_profile_index.add_items(vectors_array, np.arange(len(vectors_array)))
            # Lower ef value for faster search with small accuracy trade-off
            self.student_profile_index.set_ef(50)

            logger.info(f"Built student profile index with {len(self.student_vectors)} vectors of dimension {dim}")

    def _create_student_vector(self, student):
        """
        Create a vector representation of a student profile based on various attributes.

        Args:
            student: Student profile data

        Returns:
            Vector representation as a numpy array
        """
        # Define features to include in the vector
        features = []

        # Academic features
        if 'learning_styles' in student:
            # One-hot encoding for learning styles
            learning_styles = [
                'Lecture-based', 'Hands-on/Practical', 'Project-based',
                'Research-oriented', 'Seminar-based', 'Online/Remote'
            ]
            for style in learning_styles:
                features.append(1.0 if style in student.get('learning_styles', []) else 0.0)
        else:
            # Pad with zeros if not available
            features.extend([0.0] * 6)

        # Teaching quality
        features.append(student.get('teaching_quality', 5) / 10.0)

        # Professor accessibility
        features.append(student.get('professor_accessibility', 5) / 10.0)

        # Social features
        if 'extracurricular_activities' in student:
            # One-hot encoding for activities
            activities = [
                'Sports', 'Arts & Culture', 'Academic Clubs',
                'Community Service', 'Professional/Career Clubs'
            ]
            for activity in activities:
                features.append(1.0 if activity in student.get('extracurricular_activities', []) else 0.0)
        else:
            # Pad with zeros if not available
            features.extend([0.0] * 5)

        # Weekly hours mapping
        hours_mapping = {
            '0 (None)': 0.0,
            '1–5 hours': 0.2,
            '6–10 hours': 0.4,
            '11–15 hours': 0.6,
            '16–20 hours': 0.8,
            '20+ hours': 1.0
        }
        features.append(hours_mapping.get(student.get('weekly_extracurricular_hours', '0 (None)'), 0.0))

        # Career features
        features.append(student.get('job_placement_support', 5) / 10.0)
        features.append(1.0 if student.get('internship_experience', False) else 0.0)
        features.append(student.get('alumni_network_strength', 5) / 10.0)

        # Financial features
        features.append(student.get('affordability', 5) / 10.0)
        features.append(1.0 if student.get('received_financial_aid', False) else 0.0)

        # Facilities features
        features.append(student.get('facilities_quality', 5) / 10.0)

        # Reputation features
        features.append(student.get('employer_value_perception', 5) / 10.0)

        # Personal fit features
        features.append(student.get('personality_match', 5) / 10.0)

        # Personality traits
        if 'typical_student_traits' in student:
            # One-hot encoding for personality traits
            traits = [
                'Ambitious', 'Creative', 'Analytical', 'Collaborative',
                'Competitive', 'Introverted', 'Extroverted', 'Independent'
            ]
            for trait in traits:
                features.append(1.0 if trait in student.get('typical_student_traits', []) else 0.0)
        else:
            # Pad with zeros if not available
            features.extend([0.0] * 8)

        # Convert to numpy array
        return np.array(features)

    def _create_aspiring_student_vector(self, aspiring_profile):
        """
        Create a vector representation of an aspiring student profile.
        This should be compatible with the existing student vectors.

        Args:
            aspiring_profile: Aspiring student profile data

        Returns:
            Vector representation as a numpy array
        """
        # Define features to include in the vector - must match _create_student_vector
        features = []

        # Academic features
        if 'learning_style' in aspiring_profile:
            # One-hot encoding for learning style
            learning_styles = [
                'Lecture-based', 'Hands-on/Practical', 'Project-based',
                'Research-oriented', 'Seminar-based', 'Online/Remote'
            ]
            for style in learning_styles:
                features.append(1.0 if style == aspiring_profile.get('learning_style', '') else 0.0)
        else:
            # Pad with zeros if not available
            features.extend([0.0] * 6)

        # Teaching quality expectation (default to mid-range)
        features.append(0.5)

        # Professor accessibility expectation (default to mid-range)
        features.append(0.5)

        # Social features
        if 'interested_activities' in aspiring_profile:
            # One-hot encoding for activities
            activities = [
                'Sports', 'Arts & Culture', 'Academic Clubs',
                'Community Service', 'Professional/Career Clubs'
            ]
            for activity in activities:
                features.append(1.0 if activity in aspiring_profile.get('interested_activities', []) else 0.0)
        else:
            # Pad with zeros if not available
            features.extend([0.0] * 5)

        # Weekly hours mapping
        hours_mapping = {
            '0 (None)': 0.0,
            '1–5 hours': 0.2,
            '6–10 hours': 0.4,
            '11–15 hours': 0.6,
            '16–20 hours': 0.8,
            '20+ hours': 1.0
        }
        features.append(hours_mapping.get(aspiring_profile.get('weekly_extracurricular_hours', '0 (None)'), 0.0))

        # Career features (default to importance values or mid-range)
        features.append(aspiring_profile.get('internship_importance', 5) / 10.0)
        features.append(1.0 if aspiring_profile.get('leadership_interest', False) else 0.0)
        features.append(aspiring_profile.get('alumni_network_value', 5) / 10.0)

        # Financial features
        features.append(aspiring_profile.get('affordability_importance', 5) / 10.0)
        features.append(1.0 if aspiring_profile.get('financial_aid_interest', False) else 0.0)

        # Facilities features
        features.append(aspiring_profile.get('modern_amenities_importance', 5) / 10.0)

        # Reputation features
        features.append(aspiring_profile.get('ranking_importance', 5) / 10.0)

        # Personal fit features (default to mid-range)
        features.append(0.5)

        # Personality traits
        if 'personality_traits' in aspiring_profile:
            # One-hot encoding for personality traits
            traits = [
                'Ambitious', 'Creative', 'Analytical', 'Collaborative',
                'Competitive', 'Introverted', 'Extroverted', 'Independent'
            ]
            for trait in traits:
                features.append(1.0 if trait in aspiring_profile.get('personality_traits', []) else 0.0)
        else:
            # Pad with zeros if not available
            features.extend([0.0] * 8)

        # Convert to numpy array
        return np.array(features)

    def find_similar_students_vector(self, aspiring_profile, top_k=100):
        """
        Find the most similar students to an aspiring student using vector similarity.
        Optimized version with lower memory usage.

        Args:
            aspiring_profile: Aspiring student profile
            top_k: Number of similar students to return

        Returns:
            List of (student_id, similarity_score) tuples
        """
        if self.student_profile_index is None or len(self.student_vectors) == 0:
            logger.warning("Student profile index not available for similarity search")
            return []

        # Create vector for aspiring student
        aspiring_vector = self._create_aspiring_student_vector(aspiring_profile)

        # Find nearest neighbors - limit k to available vectors
        k = min(top_k, len(self.student_vectors), 50)  # Further limit to max 50 neighbors
        labels, distances = self.student_profile_index.knn_query(aspiring_vector.reshape(1, -1), k=k)

        # Convert to student IDs and similarity scores
        similar_students = []
        for i in range(len(labels[0])):
            student_idx = labels[0][i]
            distance = distances[0][i]
            student_id = self.student_ids[student_idx]
            # Convert distance to similarity (1 - normalized distance)
            similarity = 1.0 - min(1.0, distance)
            similar_students.append((student_id, similarity))

        return similar_students

    def compute_academic_similarity(self, aspiring_profile, existing_profile):
        """Calculate academic similarity based on field of study, learning style, etc."""
        score = 0.0
        total_weight = 0.0

        # Field of study match (30%)
        if set(aspiring_profile.get('preferred_fields', [])) & set(existing_profile.get('learning_styles', [])):
            score += 0.3
        total_weight += 0.3

        # Learning style match (25%)
        if aspiring_profile.get('learning_style') in existing_profile.get('learning_styles', []):
            score += 0.25
        total_weight += 0.25

        # Teaching quality importance (20%)
        # Higher weight if the existing student reports good teaching quality
        teaching_quality_score = existing_profile.get('teaching_quality', 0) / 10.0
        score += 0.2 * teaching_quality_score
        total_weight += 0.2

        # Professor accessibility (15%)
        accessibility_score = existing_profile.get('professor_accessibility', 0) / 10.0
        score += 0.15 * accessibility_score
        total_weight += 0.15

        # Academic resources (10%)
        resources_score = existing_profile.get('academic_resources', 0) / 10.0
        score += 0.1 * resources_score
        total_weight += 0.1

        # Normalize to 0-1 scale
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_social_similarity(self, aspiring_profile, existing_profile):
        """Calculate social and cultural compatibility"""
        score = 0.0
        total_weight = 0.0

        # Extracurricular activities overlap (40%)
        aspiring_activities = set(aspiring_profile.get('interested_activities', []))
        existing_activities = set(existing_profile.get('extracurricular_activities', []))

        if aspiring_activities and existing_activities:
            # Jaccard similarity for activity overlap
            overlap = len(aspiring_activities & existing_activities)
            union = len(aspiring_activities | existing_activities)
            if union > 0:
                activity_score = overlap / union
                score += 0.4 * activity_score
        total_weight += 0.4

        # Weekly hours for activities match (20%)
        if aspiring_profile.get('weekly_extracurricular_hours') == existing_profile.get('weekly_extracurricular_hours'):
            score += 0.2
        total_weight += 0.2

        # Campus culture importance (20%)
        # Check if aspiring student's culture importance is satisfied by university
        culture_importance = aspiring_profile.get('culture_importance', 0) / 10.0
        social_groups_ease = existing_profile.get('social_groups_ease', 0) / 10.0
        score += 0.2 * min(1.0, social_groups_ease / max(0.1, culture_importance))
        total_weight += 0.2

        # Personality match (20%)
        aspiring_traits = set(aspiring_profile.get('personality_traits', []))
        existing_traits = set(existing_profile.get('typical_student_traits', []))
        if aspiring_traits and existing_traits:
            trait_match = len(aspiring_traits & existing_traits) / len(aspiring_traits)
            score += 0.2 * trait_match
        total_weight += 0.2

        # Normalize
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_financial_similarity(self, aspiring_profile, existing_profile):
        """Calculate financial feasibility"""
        score = 0.0
        total_weight = 0.0

        # Affordability importance vs actual affordability (40%)
        affordability_importance = aspiring_profile.get('affordability_importance', 0) / 10.0
        actual_affordability = existing_profile.get('affordability', 0) / 10.0

        # If affordability is important and university is affordable, high score
        # If affordability is not important, the score is less affected
        affordability_match = 1.0 - max(0, affordability_importance - actual_affordability)
        score += 0.4 * affordability_match
        total_weight += 0.4

        # Financial aid match (30%)
        if aspiring_profile.get('financial_aid_interest', False) and existing_profile.get('received_financial_aid',
                                                                                          False):
            score += 0.3
        elif not aspiring_profile.get('financial_aid_interest', False) and not existing_profile.get(
                'received_financial_aid', False):
            score += 0.15  # Half points for matching on not needing aid
        total_weight += 0.3

        # Budget vs. actual cost (30%)
        # This would require additional data on actual university costs
        # Placeholder for demonstration
        campus_employment = existing_profile.get('campus_employment_availability', 0) / 10.0
        score += 0.3 * campus_employment  # Higher score if campus jobs available
        total_weight += 0.3

        # Normalize
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_career_similarity(self, aspiring_profile, existing_profile):
        """Calculate career prospects similarity"""
        score = 0.0
        total_weight = 0.0

        # Internship importance vs. availability (35%)
        internship_importance = aspiring_profile.get('internship_importance', 0) / 10.0
        has_internship = 1.0 if existing_profile.get('internship_experience', False) else 0.0
        job_placement = existing_profile.get('job_placement_support', 0) / 10.0

        internship_score = min(1.0, (has_internship + job_placement) / max(0.1, internship_importance * 2))
        score += 0.35 * internship_score
        total_weight += 0.35

        # Alumni network value vs. strength (35%)
        alumni_importance = aspiring_profile.get('alumni_network_value', 0) / 10.0
        alumni_strength = existing_profile.get('alumni_network_strength', 0) / 10.0

        alumni_score = min(1.0, alumni_strength / max(0.1, alumni_importance))
        score += 0.35 * alumni_score
        total_weight += 0.35

        # Leadership interest vs. opportunity (30%)
        # Assuming leadership opportunities correlate with career services
        leadership_interest = 1.0 if aspiring_profile.get('leadership_interest', False) else 0.5
        career_services = existing_profile.get('career_services_helpfulness', 0) / 10.0

        leadership_score = min(1.0, career_services / leadership_interest)
        score += 0.3 * leadership_score
        total_weight += 0.3

        # Normalize
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_geographic_similarity(self, aspiring_profile, existing_profile, university):
        """Calculate geographic preference similarity"""
        score = 0.0
        total_weight = 0.0

        # Region match (50%)
        if aspiring_profile.get('preferred_region', '').lower() in university.get('location', '').lower():
            score += 0.5
        total_weight += 0.5

        # Urban/Rural setting match (30%)
        if aspiring_profile.get('preferred_setting') == university.get('setting'):
            score += 0.3
        total_weight += 0.3

        # Living arrangement compatibility (20%)
        housing_quality = existing_profile.get('housing_quality')

        # Check if aspiring student wants to live on campus
        if aspiring_profile.get('preferred_living_arrangement') == 'On Campus':
            # If existing student has housing data and it's good quality
            if housing_quality is not None and housing_quality > 5:
                score += 0.2
            # If existing student doesn't have housing data (doesn't live on campus)
            elif housing_quality is None:
                # Partial match - they might know about off-campus options
                score += 0.05
        # If aspiring student wants to live off campus
        elif aspiring_profile.get('preferred_living_arrangement') == 'Off Campus':
            # Assume off-campus is always an option
            score += 0.2
            # Bonus if existing student also lives off campus (has knowledge)
            if housing_quality is None:
                score += 0.05  # Small bonus, capped at 0.2 total
        # If aspiring student wants to commute
        elif aspiring_profile.get('preferred_living_arrangement') == 'Commute from Home':
            # Partial match - commuting is generally always an option
            score += 0.15

        total_weight += 0.2

        # Normalize
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_facilities_similarity(self, aspiring_profile, existing_profile):
        """Calculate campus facilities similarity"""
        score = 0.0
        total_weight = 0.0

        # Important facilities match (60%)
        aspiring_facilities = set(aspiring_profile.get('important_facilities', []))
        existing_facilities = set(existing_profile.get('regularly_used_facilities', []))

        if aspiring_facilities and existing_facilities:
            facilities_overlap = len(aspiring_facilities & existing_facilities) / len(aspiring_facilities)
            score += 0.6 * facilities_overlap
        total_weight += 0.6

        # Modern amenities importance vs. quality (40%)
        amenities_importance = aspiring_profile.get('modern_amenities_importance', 0) / 10.0
        facilities_quality = existing_profile.get('facilities_quality', 0) / 10.0

        amenities_score = min(1.0, facilities_quality / max(0.1, amenities_importance))
        score += 0.4 * amenities_score
        total_weight += 0.4

        # Normalize
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_reputation_similarity(self, aspiring_profile, existing_profile):
        """Calculate reputation and brand value similarity"""
        score = 0.0
        total_weight = 0.0

        # Ranking importance match (40%)
        aspiring_ranking = aspiring_profile.get('ranking_importance', 0) / 10.0
        existing_ranking = existing_profile.get('ranking_importance', 0) / 10.0
        employer_value = existing_profile.get('employer_value_perception', 0) / 10.0

        # If rankings are important to the aspiring student, check if the university delivers
        ranking_score = min(1.0, employer_value / max(0.1, aspiring_ranking))
        score += 0.4 * ranking_score
        total_weight += 0.4

        # Selection factors overlap (40%)
        aspiring_factors = set(aspiring_profile.get('important_selection_factors', []))
        existing_factors = set(existing_profile.get('important_decision_factors', []))

        if aspiring_factors and existing_factors:
            factors_overlap = len(aspiring_factors & existing_factors) / len(aspiring_factors)
            score += 0.4 * factors_overlap
        total_weight += 0.4

        # Alumni testimonial influence (20%)
        # If testimonials matter to aspiring student, check if existing students would recommend
        testimonial_importance = aspiring_profile.get('alumni_testimonial_influence', 0) / 10.0
        would_choose_again = existing_profile.get('would_choose_again', '')
        choice_score = 1.0 if would_choose_again in ['Definitely Yes',
                                                     'Probably Yes'] else 0.5 if would_choose_again == 'Unsure' else 0.0

        testimonial_score = testimonial_importance * choice_score
        score += 0.2 * testimonial_score
        total_weight += 0.2

        # Normalize
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_personal_fit_similarity(self, aspiring_profile, existing_profile, university):
        """Calculate personal fit similarity"""
        score = 0.0
        total_weight = 0.0

        # Personality traits match (40%)
        aspiring_traits = set(aspiring_profile.get('personality_traits', []))
        existing_traits = set(existing_profile.get('typical_student_traits', []))

        if aspiring_traits and existing_traits:
            trait_match = len(aspiring_traits & existing_traits) / len(aspiring_traits)
            score += 0.4 * trait_match
        total_weight += 0.4

        # Student population preference (30%)
        university_size = university.get('size', '')
        preferred_size = aspiring_profile.get('preferred_student_population', '')

        if university_size == preferred_size:
            score += 0.3
        total_weight += 0.3

        # Personality match with university (30%)
        personality_match = existing_profile.get('personality_match', 0) / 10.0
        score += 0.3 * personality_match
        total_weight += 0.3

        # Normalize
        if total_weight > 0:
            return score / total_weight
        return 0.0

    def compute_student_similarity(self, aspiring_profile, existing_student):
        """Compute overall similarity between aspiring student and existing student"""
        # Find university data for this student
        university = next((u for u in self.universities if u.get('id') == existing_student.get('university_id')), {})

        # Compute category similarities
        academic_sim = self.compute_academic_similarity(aspiring_profile, existing_student)
        social_sim = self.compute_social_similarity(aspiring_profile, existing_student)
        financial_sim = self.compute_financial_similarity(aspiring_profile, existing_student)
        career_sim = self.compute_career_similarity(aspiring_profile, existing_student)
        geographic_sim = self.compute_geographic_similarity(aspiring_profile, existing_student, university)
        facilities_sim = self.compute_facilities_similarity(aspiring_profile, existing_student)
        reputation_sim = self.compute_reputation_similarity(aspiring_profile, existing_student)
        personal_sim = self.compute_personal_fit_similarity(aspiring_profile, existing_student, university)

        # Weighted average
        overall_sim = (
                self.category_weights['academic'] * academic_sim +
                self.category_weights['social'] * social_sim +
                self.category_weights['financial'] * financial_sim +
                self.category_weights['career'] * career_sim +
                self.category_weights['geographic'] * geographic_sim +
                self.category_weights['facilities'] * facilities_sim +
                self.category_weights['reputation'] * reputation_sim +
                self.category_weights['personal_fit'] * personal_sim
        )

        return {
            'student_id': existing_student.get('id'),
            'university_id': existing_student.get('university_id'),
            'university_name': university.get('name', 'Unknown University'),
            'overall_similarity': overall_sim,
            'academic_similarity': academic_sim,
            'social_similarity': social_sim,
            'financial_similarity': financial_sim,
            'career_similarity': career_sim,
            'geographic_similarity': geographic_sim,
            'facilities_similarity': facilities_sim,
            'reputation_similarity': reputation_sim,
            'personal_fit_similarity': personal_sim
        }

    def recommend_universities_vector_based(self, aspiring_profile, top_n=10):
        """
        Generate university recommendations using vector similarity search.
        Memory-optimized version that processes results in smaller chunks.

        Args:
            aspiring_profile: Aspiring student profile data
            top_n: Number of universities to recommend

        Returns:
            List of university recommendations with scores
        """
        logger.info("Generating vector-based recommendations")

        # 1. FIND SIMILAR STUDENTS: Use vector similarity to find most similar students
        # Limit to 100 instead of 200 to save memory
        similar_student_ids_scores = self.find_similar_students_vector(aspiring_profile, top_k=100)

        if not similar_student_ids_scores:
            logger.warning("No similar students found using vector search, falling back to standard method")
            # Fall back to original method if no similar students found
            return self._prefilter_universities_recommend(aspiring_profile, top_n)

        logger.info(f"Found {len(similar_student_ids_scores)} similar students using vector similarity")

        # 2. GET DETAILED STUDENT DATA: Retrieve student data for the similar students
        similar_students_data = []
        student_id_to_similarity = dict(similar_student_ids_scores)

        for student_id, _ in similar_student_ids_scores:
            student = next((s for s in self.existing_students if s.get('id') == student_id), None)
            if student:
                # Add vector similarity score
                student['vector_similarity'] = student_id_to_similarity[student_id]
                similar_students_data.append(student)

        # 3. GROUP BY UNIVERSITY: Aggregate scores by university
        university_scores = {}
        university_students = {}

        for student in similar_students_data:
            university_id = student.get('university_id')

            # Skip if missing university ID
            if not university_id:
                continue

            # Calculate detailed similarity scores
            similarity_data = self.compute_student_similarity(aspiring_profile, student)

            # Add vector similarity to the data
            similarity_data['vector_similarity'] = student.get('vector_similarity', 0.0)

            # Update university trackers
            if university_id not in university_scores:
                university = next((u for u in self.universities if u.get('id') == university_id), None)
                if not university:
                    continue

                university_scores[university_id] = {
                    'university_id': university_id,
                    'university_name': university.get('name', 'Unknown University'),
                    'location': university.get('location', ''),
                    'size': university.get('size', ''),
                    'setting': university.get('setting', ''),
                    'overall_score': 0.0,
                    'academic_score': 0.0,
                    'social_score': 0.0,
                    'financial_score': 0.0,
                    'career_score': 0.0,
                    'geographic_score': 0.0,
                    'facilities_score': 0.0,
                    'reputation_score': 0.0,
                    'personal_fit_score': 0.0,
                    'student_count': 0,
                    'similar_students': []
                }
                university_students[university_id] = []

            # Add student to university's similar students list
            university_students[university_id].append(similarity_data)

            # Increment student count
            university_scores[university_id]['student_count'] += 1

        # 4. CALCULATE FINAL SCORES: Compute average scores and top similar students
        for university_id, students in university_students.items():
            # Sort students by overall similarity
            students.sort(key=lambda x: x['overall_similarity'], reverse=True)

            # Take top students per university (limited to 3 instead of 5 to save memory)
            top_students = students[:3]

            if not top_students:
                continue

            # Calculate average scores from detailed similarities
            university_scores[university_id]['overall_score'] = sum(
                s['overall_similarity'] for s in top_students) / len(top_students)
            university_scores[university_id]['academic_score'] = sum(
                s['academic_similarity'] for s in top_students) / len(top_students)
            university_scores[university_id]['social_score'] = sum(s['social_similarity'] for s in top_students) / len(
                top_students)
            university_scores[university_id]['financial_score'] = sum(
                s['financial_similarity'] for s in top_students) / len(top_students)
            university_scores[university_id]['career_score'] = sum(s['career_similarity'] for s in top_students) / len(
                top_students)
            university_scores[university_id]['geographic_score'] = sum(
                s['geographic_similarity'] for s in top_students) / len(top_students)
            university_scores[university_id]['facilities_score'] = sum(
                s['facilities_similarity'] for s in top_students) / len(top_students)
            university_scores[university_id]['reputation_score'] = sum(
                s['reputation_similarity'] for s in top_students) / len(top_students)
            university_scores[university_id]['personal_fit_score'] = sum(
                s['personal_fit_similarity'] for s in top_students) / len(top_students)

            # Set similar students (limited to top 3 for output)
            university_scores[university_id]['similar_students'] = top_students[:3]

            # Set matching_student_count for compatibility with existing code
            university_scores[university_id]['matching_student_count'] = university_scores[university_id][
                'student_count']

        # Convert to list and sort by overall score
        final_scores = list(university_scores.values())
        final_scores.sort(key=lambda x: x['overall_score'], reverse=True)

        logger.info(f"Generated {len(final_scores)} university recommendations based on vector similarity")

        # Return top_n recommendations
        return final_scores[:top_n]

    def recommend_universities(self, aspiring_profile, top_n=10):
        """
        Primary method to generate university recommendations.
        Uses vector-based similarity search when possible, with fallback to tier-based approach.

        Args:
            aspiring_profile: Aspiring student profile data
            top_n: Number of universities to recommend

        Returns:
            List of university recommendations with scores
        """
        # Try the improved vector-based approach first
        if self.student_profile_index is not None and len(self.student_vectors) > 0:
            return self.recommend_universities_vector_based(aspiring_profile, top_n)
        else:
            logger.warning("Vector similarity not available, using standard recommendation approach")
            return self._prefilter_universities_recommend(aspiring_profile, top_n)

    def compute_student_similarity(self, aspiring_profile, existing_student):
        """Compute overall similarity between aspiring student and existing student"""
        # Find university data for this student
        university = next((u for u in self.universities if u.get('id') == existing_student.get('university_id')), {})

        # Compute category similarities
        academic_sim = self.compute_academic_similarity(aspiring_profile, existing_student)
        social_sim = self.compute_social_similarity(aspiring_profile, existing_student)
        financial_sim = self.compute_financial_similarity(aspiring_profile, existing_student)
        career_sim = self.compute_career_similarity(aspiring_profile, existing_student)
        geographic_sim = self.compute_geographic_similarity(aspiring_profile, existing_student, university)
        facilities_sim = self.compute_facilities_similarity(aspiring_profile, existing_student)
        reputation_sim = self.compute_reputation_similarity(aspiring_profile, existing_student)
        personal_sim = self.compute_personal_fit_similarity(aspiring_profile, existing_student, university)

        # Weighted average
        overall_sim = (
                self.category_weights['academic'] * academic_sim +
                self.category_weights['social'] * social_sim +
                self.category_weights['financial'] * financial_sim +
                self.category_weights['career'] * career_sim +
                self.category_weights['geographic'] * geographic_sim +
                self.category_weights['facilities'] * facilities_sim +
                self.category_weights['reputation'] * reputation_sim +
                self.category_weights['personal_fit'] * personal_sim
        )

        return {
            'student_id': existing_student.get('id'),
            'university_id': existing_student.get('university_id'),
            'university_name': university.get('name', 'Unknown University'),
            'overall_similarity': overall_sim,
            'academic_similarity': academic_sim,
            'social_similarity': social_sim,
            'financial_similarity': financial_sim,
            'career_similarity': career_sim,
            'geographic_similarity': geographic_sim,
            'facilities_similarity': facilities_sim,
            'reputation_similarity': reputation_sim,
            'personal_fit_similarity': personal_sim
        }

    # Additional similarity computation methods would be included here
    # (compute_social_similarity, compute_financial_similarity, etc.)

    def _prefilter_universities(self, aspiring_profile):
        """
        TIER 1: Quickly pre-filter universities based on essential criteria
        before performing detailed similarity calculations.
        Returns a list of (university_id, metadata) tuples sorted by initial match score.

        Memory-optimized version that operates on smaller datasets.
        """
        candidates = []

        # Process each university with lightweight filtering
        for university in self.universities:
            uni_id = university.get('id')
            if not uni_id:
                continue

            # Calculate a quick match score based on key factors
            match_score = 0.0
            match_factors = 0

            # 1. Geographic match (high weight - very important)
            if aspiring_profile.get('preferred_region', '').lower() in university.get('location', '').lower():
                match_score += 3.0
                match_factors += 1

            # 2. University size preference match
            if aspiring_profile.get('preferred_student_population') == university.get('size'):
                match_score += 1.0
                match_factors += 1

            # 3. Setting match (urban/rural)
            if aspiring_profile.get('preferred_setting') == university.get('setting'):
                match_score += 1.0
                match_factors += 1

            # Normalize score if we have factors to consider
            initial_score = match_score / max(1, match_factors) if match_factors > 0 else 0

            # Add to candidates with initial score and university data
            candidates.append((uni_id, {
                'initial_score': initial_score,
                'location': university.get('location', ''),
                'size': university.get('size', ''),
                'setting': university.get('setting', '')
            }))

        # If we have candidates, sort by initial score
        if candidates:
            candidates.sort(key=lambda x: x[1]['initial_score'], reverse=True)

        return candidates

    def _prefilter_universities_recommend(self, aspiring_profile, top_n=10):
        """
        Legacy recommendation method as fallback, uses the original tier-based approach.
        Memory-optimized version that processes smaller batches.
        """
        # TIER 1: FAST PRE-FILTERING
        # First, quickly filter universities based on essential criteria
        candidate_universities = self._prefilter_universities(aspiring_profile)

        # Limit candidates to a smaller number (adjusted for memory)
        max_candidates = min(20, len(candidate_universities))  # Reduced from 30
        candidate_universities = candidate_universities[:max_candidates]

        # TIER 2: DETAILED EVALUATION
        # Process each candidate university more thoroughly
        university_scores = []

        for uni_id, uni_metadata in candidate_universities:
            university = next((u for u in self.universities if u.get('id') == uni_id), None)
            if not university:
                continue

            # Find the students from this university
            uni_students = [s for s in self.existing_students if s.get('university_id') == uni_id]

            # If too many students, sample them (for memory efficiency)
            sample_size = min(20, len(uni_students))  # Reduced from 50
            if len(uni_students) > sample_size:
                import random
                uni_students = random.sample(uni_students, sample_size)

            # TIER 3: DETAILED STUDENT SIMILARITY
            # Calculate full similarity scores for these students
            student_similarities = []
            for student in uni_students:
                similarity_data = self.compute_student_similarity(aspiring_profile, student)
                student_similarities.append(similarity_data)

            # Skip if no similar students
            if not student_similarities:
                continue

            # Sort by similarity and take top matches
            student_similarities.sort(key=lambda x: x['overall_similarity'], reverse=True)
            top_students = student_similarities[:3]  # Reduced from top 5

            # Calculate average scores
            avg_overall = sum(s['overall_similarity'] for s in top_students) / len(top_students)
            avg_academic = sum(s['academic_similarity'] for s in top_students) / len(top_students)
            avg_social = sum(s['social_similarity'] for s in top_students) / len(top_students)
            avg_financial = sum(s['financial_similarity'] for s in top_students) / len(top_students)
            avg_career = sum(s['career_similarity'] for s in top_students) / len(top_students)
            avg_geographic = sum(s['geographic_similarity'] for s in top_students) / len(top_students)
            avg_facilities = sum(s['facilities_similarity'] for s in top_students) / len(top_students)
            avg_reputation = sum(s['reputation_similarity'] for s in top_students) / len(top_students)
            avg_personal = sum(s['personal_fit_similarity'] for s in top_students) / len(top_students)

            # Add to university scores
            university_scores.append({
                'university_id': uni_id,
                'university_name': university.get('name', 'Unknown University'),
                'location': university.get('location', ''),
                'size': university.get('size', ''),
                'setting': university.get('setting', ''),
                'overall_score': avg_overall,
                'academic_score': avg_academic,
                'social_score': avg_social,
                'financial_score': avg_financial,
                'career_score': avg_career,
                'geographic_score': avg_geographic,
                'facilities_score': avg_facilities,
                'reputation_score': avg_reputation,
                'personal_fit_score': avg_personal,
                'matching_student_count': len(top_students),
                'similar_students': top_students
            })

        # Sort by overall score
        university_scores.sort(key=lambda x: x['overall_score'], reverse=True)

        # Return top_n universities
        return university_scores[:top_n]

    def find_similar_students(self, aspiring_profile, top_n=5):
        """Find existing students most similar to the aspiring student"""
        # Try vector similarity approach first
        if self.student_profile_index is not None and len(self.student_vectors) > 0:
            vector_similar_ids = self.find_similar_students_vector(aspiring_profile, top_k=top_n * 2)

            if vector_similar_ids:
                similar_students = []

                for student_id, vector_sim in vector_similar_ids:
                    student = next((s for s in self.existing_students if s.get('id') == student_id), None)
                    if student:
                        similarity_data = self.compute_student_similarity(aspiring_profile, student)
                        # Boost similarity score with vector similarity
                        similarity_data['overall_similarity'] = 0.7 * similarity_data[
                            'overall_similarity'] + 0.3 * vector_sim
                        similar_students.append(similarity_data)

                # Sort by overall similarity
                similar_students.sort(key=lambda x: x['overall_similarity'], reverse=True)
                return similar_students[:top_n]

        # Fallback to original method
        similarities = []

        # Limit computation to a subset of students for memory efficiency
        max_students = min(100, len(self.existing_students))
        for existing_student in self.existing_students[:max_students]:
            similarity_data = self.compute_student_similarity(aspiring_profile, existing_student)
            similarities.append(similarity_data)

        # Sort by overall similarity
        similarities.sort(key=lambda x: x['overall_similarity'], reverse=True)

        return similarities[:top_n]
