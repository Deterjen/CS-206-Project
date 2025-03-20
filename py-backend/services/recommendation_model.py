import hnswlib
import numpy as np
from sentence_transformers import SentenceTransformer


class UniversityRecommender:
    """
    A model for generating university recommendations based on similarity between
    aspiring student profiles and existing student experiences.

    This class handles only the algorithmic aspects of recommendation without
    knowledge of data persistence.
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

        # Initialize text embedding model
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Storage for data
        self.universities = []
        self.existing_students = []
        self.programs = []

        # HNSW indexes for text embeddings
        self.text_indexes = {}

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

        # Build text embedding indexes
        self._build_text_indexes()

    def _build_text_indexes(self):
        """Build HNSW indexes for text fields for efficient similarity search"""
        text_fields = [
            'thriving_student_type',
            'retrospective_important_factors',
            'university_strengths',
            'university_weaknesses',
            'prospective_student_advice'
        ]

        self.text_indexes = {}

        for field in text_fields:
            # Get non-null text values
            texts = [s.get(field) for s in self.existing_students if s.get(field)]
            if not texts:
                continue

            # Create embeddings
            embeddings = self.text_model.encode(texts)

            # Create HNSW index
            dim = embeddings.shape[1]
            index = hnswlib.Index(space='cosine', dim=dim)
            index.init_index(max_elements=len(embeddings), ef_construction=200, M=16)
            index.add_items(embeddings, np.arange(len(embeddings)))

            # Store index and mapping to student IDs
            self.text_indexes[field] = {
                'index': index,
                'student_ids': [s.get('id') for s in self.existing_students if s.get(field)]
            }

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

    def find_similar_students(self, aspiring_profile, top_n=5):
        """Find existing students most similar to the aspiring student"""
        similarities = []

        for existing_student in self.existing_students:
            # Find university data for this student
            university = next((u for u in self.universities if u.get('id') == existing_student.get('university_id')),
                              {})

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

            similarities.append({
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
            })

        # Sort by overall similarity
        similarities.sort(key=lambda x: x['overall_similarity'], reverse=True)

        return similarities[:top_n]

    def recommend_universities(self, aspiring_profile, top_n=10):
        """Recommend universities based on aspiring student profile"""
        # Find similar students
        similar_students = self.find_similar_students(aspiring_profile, top_n=50)

        # Aggregate by university
        university_scores = {}
        for student in similar_students:
            uni_id = student['university_id']

            if uni_id not in university_scores:
                # Find university name
                university_name = "Unknown University"
                for uni in self.universities:
                    if uni.get('id') == uni_id:
                        university_name = uni.get('name', 'Unknown University')
                        break

                university_scores[uni_id] = {
                    'university_id': uni_id,
                    'university_name': university_name,
                    'count': 0,
                    'overall_score': 0,
                    'academic_score': 0,
                    'social_score': 0,
                    'financial_score': 0,
                    'career_score': 0,
                    'geographic_score': 0,
                    'facilities_score': 0,
                    'reputation_score': 0,
                    'personal_fit_score': 0,
                    'similar_students': []
                }

            # Add to university scores
            university_scores[uni_id]['count'] += 1
            university_scores[uni_id]['overall_score'] += student['overall_similarity']
            university_scores[uni_id]['academic_score'] += student['academic_similarity']
            university_scores[uni_id]['social_score'] += student['social_similarity']
            university_scores[uni_id]['financial_score'] += student['financial_similarity']
            university_scores[uni_id]['career_score'] += student['career_similarity']
            university_scores[uni_id]['geographic_score'] += student['geographic_similarity']
            university_scores[uni_id]['facilities_score'] += student['facilities_similarity']
            university_scores[uni_id]['reputation_score'] += student['reputation_similarity']
            university_scores[uni_id]['personal_fit_score'] += student['personal_fit_similarity']

            # Add to similar students list if in top 3 for this university
            if len(university_scores[uni_id]['similar_students']) < 3:
                university_scores[uni_id]['similar_students'].append(student)

        # Calculate average scores and normalize by student count
        results = []
        for uni_id, scores in university_scores.items():
            count = max(1, scores['count'])  # Avoid division by zero

            avg_scores = {
                'university_id': scores['university_id'],
                'university_name': scores['university_name'],
                'overall_score': scores['overall_score'] / count,
                'academic_score': scores['academic_score'] / count,
                'social_score': scores['social_score'] / count,
                'financial_score': scores['financial_score'] / count,
                'career_score': scores['career_score'] / count,
                'geographic_score': scores['geographic_score'] / count,
                'facilities_score': scores['facilities_score'] / count,
                'reputation_score': scores['reputation_score'] / count,
                'personal_fit_score': scores['personal_fit_score'] / count,
                'matching_student_count': count,
                'similar_students': scores['similar_students']
            }

            results.append(avg_scores)

        # Sort by overall score
        results.sort(key=lambda x: x['overall_score'], reverse=True)

        return results[:top_n]
