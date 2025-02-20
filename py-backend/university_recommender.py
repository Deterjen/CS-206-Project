"""
University Recommendation System MVP
===================================
This system recommends universities to prospective students based on similarity to existing students,
considering personality, learning preferences, academic interests, career goals, and other factors.
"""

import json
import logging
import os
from ast import literal_eval
from typing import List, Dict

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from scipy.spatial.distance import cosine
from supabase import create_client

from data_pipeline.svd_recommender import SVDRecommender

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables and initialize Supabase client
load_dotenv('.env.local')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')


class UniversityRecommender:
    """University recommendation system based on student profile similarity and preferences."""

    def __init__(self, data_path: str = "./data/analysis_ready_survey_data.csv"):
        """Initialize the recommender system.

        Args:
            data_path: Path to the survey data CSV file
        """
        # Initialize Supabase client
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        self.data = self._load_data(data_path)
        self.universities = self._extract_universities()
        self.user_profiles = self._extract_user_profiles()
        self.university_features = self._extract_university_features()
        self.embeddings_cache = {}  # Cache for embeddings to avoid redundant API calls

        # Initialize SVD recommender
        self.svd_recommender = SVDRecommender(self.data)

        logger.info(f"Loaded {len(self.data)} student records")
        logger.info(f"Found {len(self.universities)} universities")

    def _load_data(self, data_path: str) -> pd.DataFrame:
        """Load and preprocess the survey data."""
        try:
            df = pd.read_csv(data_path)
            # Clean the data
            df = df.dropna(subset=['university'])

            # Convert string lists to actual lists
            list_columns = ['selection_criteria_list', 'cca_list']
            for col in list_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: literal_eval(x) if isinstance(x, str) else [])

            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def _extract_universities(self) -> List[Dict]:
        """Extract unique universities with their characteristics from the dataset."""
        universities = []
        for uni_name in self.data['university'].unique():
            if pd.notna(uni_name):
                # Get all students from this university
                uni_students = self.data[self.data['university'] == uni_name]

                # Calculate university characteristics based on student population
                uni_info = {
                    'id': uni_name.lower().replace(' ', '_'),
                    'name': uni_name,
                    'student_count': len(uni_students),
                    'avg_satisfaction': uni_students['satisfaction_rating'].mean(),
                    'satisfaction_distribution': uni_students['satisfaction_group'].value_counts().to_dict(),

                    # Student demographics
                    'age_distribution': uni_students['age'].value_counts().to_dict(),
                    'gender_distribution': uni_students['gender'].value_counts().to_dict(),
                    'personality_distribution': uni_students['personality'].value_counts().to_dict(),

                    # Academic characteristics
                    'learning_styles': uni_students['learning_style'].value_counts().to_dict(),
                    'schools': uni_students['school'].value_counts().to_dict(),
                    'top_career_goals': uni_students['career_goal'].value_counts().head(3).index.tolist(),

                    # Student preferences
                    'avg_cost_importance': uni_students['cost_importance'].mean(),
                    'avg_culture_importance': uni_students['culture_importance'].mean(),
                    'avg_internship_importance': uni_students['internship_importance'].mean(),
                    'avg_ranking_influence': uni_students['ranking_influence'].mean(),
                    'avg_extracurricular_importance': uni_students['extracurricular_importance'].mean(),

                    # Common patterns
                    'common_population_preference': uni_students['preferred_population'].mode()[0] if not uni_students[
                        'preferred_population'].empty else None,
                    'residence_distribution': uni_students['residence'].value_counts().to_dict(),

                    # Student engagement
                    'leadership_percentage': (uni_students[
                                                  'leadership_role'].mean() * 100) if 'leadership_role' in uni_students.columns else 0,
                    'avg_engagement_level': uni_students[
                        'engagement_level'].mean() if 'engagement_level' in uni_students.columns else 0,
                    'engagement_distribution': uni_students[
                        'engagement_category'].value_counts().to_dict() if 'engagement_category' in uni_students.columns else {},

                    # Selection criteria (aggregate from all students)
                    'common_selection_criteria': self._aggregate_selection_criteria(uni_students),

                    # Activities (aggregate from all students)
                    'popular_ccas': self._aggregate_ccas(uni_students)
                }

                # Generate a text description of the university
                uni_info['description'] = self._generate_university_description(uni_info)

                universities.append(uni_info)

        return universities

    def _aggregate_selection_criteria(self, uni_students: pd.DataFrame) -> Dict[str, int]:
        """Aggregate selection criteria from all students at a university."""
        all_criteria = []
        for criteria_list in uni_students['selection_criteria_list']:
            if isinstance(criteria_list, list):
                all_criteria.extend(criteria_list)

        return dict(pd.Series(all_criteria).value_counts())

    def _aggregate_ccas(self, uni_students: pd.DataFrame) -> Dict[str, int]:
        """Aggregate CCAs from all students at a university."""
        all_ccas = []
        for cca_list in uni_students['cca_list']:
            if isinstance(cca_list, list):
                all_ccas.extend(cca_list)

        return dict(pd.Series(all_ccas).value_counts())

    def _generate_university_description(self, uni_info: Dict) -> str:
        """Generate a text description of a university based on its characteristics."""
        # Get the most common attributes
        top_personality = max(uni_info['personality_distribution'].items(), key=lambda x: x[1])[0] if uni_info[
            'personality_distribution'] else "diverse"
        top_learning_style = max(uni_info['learning_styles'].items(), key=lambda x: x[1])[0] if uni_info[
            'learning_styles'] else "various"
        top_schools = list(uni_info['schools'].keys())[:3] if uni_info['schools'] else ["various disciplines"]

        # Format the description
        description = f"{uni_info['name']} is known for its {top_learning_style} learning environment. "
        description += f"The university has a student population that tends to be {top_personality}. "
        description += f"It is particularly strong in {', '.join(top_schools)}. "
        description += f"Students rate their satisfaction at {uni_info['avg_satisfaction']:.1f}/5 on average. "

        # Add information about important factors
        description += f"Students here value "
        factors = []
        if uni_info['avg_internship_importance'] > 7:
            factors.append("internship opportunities")
        if uni_info['avg_culture_importance'] > 7:
            factors.append("campus culture")
        if uni_info['avg_ranking_influence'] > 7:
            factors.append("university rankings")
        if uni_info['avg_cost_importance'] > 7:
            factors.append("affordability")
        if uni_info['avg_extracurricular_importance'] > 7:
            factors.append("extracurricular activities")

        if factors:
            description += ", ".join(factors) + ". "
        else:
            description += "a balanced university experience. "

        # Add career information if available
        if uni_info['top_career_goals']:
            description += f"Many students aim for careers as {', '.join(uni_info['top_career_goals'])}. "

        # Add engagement information
        if uni_info['leadership_percentage'] > 30:
            description += f"There is strong student leadership, with {uni_info['leadership_percentage']:.0f}% of students in leadership roles. "

        # Add popular activities if available
        popular_ccas = list(uni_info['popular_ccas'].keys())[:3] if uni_info['popular_ccas'] else []
        if popular_ccas:
            description += f"Popular activities include {', '.join(popular_ccas)}."

        return description

    def _extract_user_profiles(self) -> List[Dict]:
        """Extract complete user profiles from the dataset."""
        profiles = []

        for idx, row in self.data.iterrows():
            profile = {
                'id': f"student_{idx}",
                'university': row['university'],
                'satisfaction': row['satisfaction_rating'],
                'demographic': {
                    'age': row['age'],
                    'gender': row['gender'],
                    'personality': row['personality'],
                    'student_status': row['student_status']
                },
                'academic': {
                    'learning_style': row['learning_style'],
                    'school': row['school'],
                    'career_goal': row['career_goal'],
                    'plans_further_education': row['plans_further_education']
                },
                'preferences': {
                    'preferred_population': row['preferred_population'],
                    'residence': row['residence'],
                    'cost_importance': row['cost_importance'],
                    'culture_importance': row['culture_importance'],
                    'internship_importance': row['internship_importance'],
                    'ranking_influence': row['ranking_influence'],
                    'extracurricular_importance': row['extracurricular_importance'],
                    'family_influence': row['family_influence'],
                    'friend_influence': row['friend_influence'],
                    'social_media_influence': row['social_media_influence'],
                },
                'engagement': {
                    'leadership_role': row['leadership_role'],
                    'extracurricular_hours': row['extracurricular_hours'],
                    'extracurricular_type': row['extracurricular_type'],
                    'cca_count': row['cca_count'],
                    'engagement_level': row['engagement_level'] if 'engagement_level' in row else None,
                    'engagement_category': row['engagement_category'] if 'engagement_category' in row else None
                },
                'selection_criteria': row['selection_criteria_list'],
                'ccas': row['cca_list']
            }

            # Create text representations for embedding generation
            profile['profile_text'] = self._create_profile_text(profile)
            profile['preferences_text'] = self._create_preferences_text(profile)

            profiles.append(profile)

        return profiles

    def _extract_university_features(self) -> Dict[str, Dict]:
        """Extract feature vectors for each university based on student characteristics."""
        features = {}

        for uni in self.universities:
            # Get all students from this university
            uni_students = [p for p in self.user_profiles if p['university'] == uni['name']]

            if not uni_students:
                continue

            # Calculate statistical features about this university's student body
            features[uni['id']] = {
                'name': uni['name'],
                'avg_satisfaction': np.mean([s['satisfaction'] for s in uni_students if s['satisfaction'] is not None]),

                # Preference importances (averages)
                'avg_cost_importance': np.mean([s['preferences']['cost_importance'] for s in uni_students if
                                                s['preferences']['cost_importance'] is not None]),
                'avg_culture_importance': np.mean([s['preferences']['culture_importance'] for s in uni_students if
                                                   s['preferences']['culture_importance'] is not None]),
                'avg_internship_importance': np.mean([s['preferences']['internship_importance'] for s in uni_students if
                                                      s['preferences']['internship_importance'] is not None]),
                'avg_ranking_importance': np.mean([s['preferences']['ranking_influence'] for s in uni_students if
                                                   s['preferences']['ranking_influence'] is not None]),
                'avg_extracurricular_importance': np.mean(
                    [s['preferences']['extracurricular_importance'] for s in uni_students if
                     s['preferences']['extracurricular_importance'] is not None]),

                # Engagement metrics
                'avg_leadership': np.mean([s['engagement']['leadership_role'] for s in uni_students if
                                           s['engagement']['leadership_role'] is not None]),
                'avg_extracurricular_hours': np.mean([s['engagement']['extracurricular_hours'] for s in uni_students if
                                                      s['engagement']['extracurricular_hours'] is not None]),
                'avg_cca_count': np.mean(
                    [s['engagement']['cca_count'] for s in uni_students if s['engagement']['cca_count'] is not None]),

                # External influence averages
                'avg_family_influence': np.mean([s['preferences']['family_influence'] for s in uni_students if
                                                 s['preferences']['family_influence'] is not None]),
                'avg_friend_influence': np.mean([s['preferences']['friend_influence'] for s in uni_students if
                                                 s['preferences']['friend_influence'] is not None]),
                'avg_social_media_influence': np.mean(
                    [s['preferences']['social_media_influence'] for s in uni_students if
                     s['preferences']['social_media_influence'] is not None]),

                # Distributions
                'learning_styles': self._counter_to_distribution(
                    [s['academic']['learning_style'] for s in uni_students]),
                'personality_types': self._counter_to_distribution(
                    [s['demographic']['personality'] for s in uni_students]),
                'career_goals': self._counter_to_distribution([s['academic']['career_goal'] for s in uni_students]),
                'residence_types': self._counter_to_distribution([s['preferences']['residence'] for s in uni_students]),
                'population_preferences': self._counter_to_distribution(
                    [s['preferences']['preferred_population'] for s in uni_students]),

                # Feature vectors for machine learning
                'feature_vector': self._create_university_feature_vector(uni_students)
            }

        return features

    def _counter_to_distribution(self, items: List) -> Dict[str, float]:
        """Convert a list of items to a probability distribution."""
        counter = {}
        for item in items:
            if item is not None:
                counter[item] = counter.get(item, 0) + 1

        total = sum(counter.values())
        return {k: v / total for k, v in counter.items()} if total > 0 else {}

    def _create_university_feature_vector(self, students: List[Dict]) -> np.ndarray:
        """Create a numerical feature vector representing a university's student body."""
        # Extract numerical features
        features = []
        for s in students:
            student_features = [
                s['satisfaction'] if s['satisfaction'] is not None else 0,
                s['preferences']['cost_importance'] if s['preferences']['cost_importance'] is not None else 0,
                s['preferences']['culture_importance'] if s['preferences']['culture_importance'] is not None else 0,
                s['preferences']['internship_importance'] if s['preferences'][
                                                                 'internship_importance'] is not None else 0,
                s['preferences']['ranking_influence'] if s['preferences']['ranking_influence'] is not None else 0,
                s['preferences']['extracurricular_importance'] if s['preferences'][
                                                                      'extracurricular_importance'] is not None else 0,
                s['engagement']['leadership_role'] if s['engagement']['leadership_role'] is not None else 0,
                s['engagement']['extracurricular_hours'] if s['engagement']['extracurricular_hours'] is not None else 0,
                s['engagement']['cca_count'] if s['engagement']['cca_count'] is not None else 0,
                s['preferences']['family_influence'] if s['preferences']['family_influence'] is not None else 0,
                s['preferences']['friend_influence'] if s['preferences']['friend_influence'] is not None else 0,
                s['preferences']['social_media_influence'] if s['preferences'][
                                                                  'social_media_influence'] is not None else 0
            ]
            features.append(student_features)

        # Calculate average feature vector
        if features:
            return np.mean(features, axis=0)
        else:
            return np.zeros(12)  # Default empty vector

    def _create_profile_text(self, profile: Dict) -> str:
        """Create a text representation of user profile for embedding."""
        demographic = profile.get('demographic', {})
        academic = profile.get('academic', {})
        engagement = profile.get('engagement', {})

        profile_parts = [
            f"Age: {demographic.get('age', 'Not specified')}",
            f"Gender: {demographic.get('gender', 'Not specified')}",
            f"Personality: {demographic.get('personality', 'Not specified')}",
            f"Student type: {demographic.get('student_status', 'Not specified')}",
            f"Learning style: {academic.get('learning_style', 'Not specified')}",
            f"School/Major: {academic.get('school', 'Not specified')}",
            f"Career goal: {academic.get('career_goal', 'Not specified')}",
            f"Plans further education: {academic.get('plans_further_education', 'Not specified')}",
            f"Leadership role: {'Yes' if engagement.get('leadership_role') else 'No'}",
            f"Extracurricular type: {engagement.get('extracurricular_type', 'None')}",
            f"Extracurricular hours: {engagement.get('extracurricular_hours', 0)}",
            f"Number of CCAs: {engagement.get('cca_count', 0)}"
        ]

        ccas = profile.get('ccas', [])
        if ccas and len(ccas) > 0:
            profile_parts.append(f"Activities: {', '.join(ccas)}")

        return ". ".join([p for p in profile_parts if p])

    def _create_preferences_text(self, profile: Dict) -> str:
        """Create a text representation of user preferences for embedding."""
        preferences = profile.get('preferences', {})

        pref_parts = [
            f"Preferred population: {preferences.get('preferred_population', 'Not specified')}",
            f"Preferred residence: {preferences.get('residence', 'Not specified')}",
            f"Cost importance: {preferences.get('cost_importance', 5)}/10",
            f"Culture importance: {preferences.get('culture_importance', 5)}/10",
            f"Internship importance: {preferences.get('internship_importance', 5)}/10",
            f"Ranking importance: {preferences.get('ranking_influence', 5)}/10",
            f"Extracurricular importance: {preferences.get('extracurricular_importance', 5)}/10",
            f"Family influence: {preferences.get('family_influence', 5)}/10",
            f"Friend influence: {preferences.get('friend_influence', 5)}/10",
            f"Social media influence: {preferences.get('social_media_influence', 5)}/10"
        ]

        selection_criteria = profile.get('selection_criteria', [])
        if selection_criteria and len(selection_criteria) > 0:
            pref_parts.append(f"Selection criteria: {', '.join(selection_criteria)}")

        return ". ".join([p for p in pref_parts if p])

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using Supabase edge function."""
        # Check cache first
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]

        try:
            # Call the Supabase edge function for embedding generation
            response = self.supabase.functions.invoke(
                "embed",
                invoke_options={
                    "body": {'texts': [text], 'batchMode': False},
                }
            )

            # Parse the response
            response_data = json.loads(response.decode('utf-8'))
            embedding = np.array(response_data['embeddings'][0])

            # Normalize the vector if needed
            if np.linalg.norm(embedding) > 0:
                embedding = embedding / np.linalg.norm(embedding)

            # Cache the result
            self.embeddings_cache[text] = embedding
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(384)

    def _find_similar_profiles(self, user_data: Dict, n: int = 5) -> List[Dict]:
        """Find existing students with similar profiles to the input user using SVD.

        Args:
            user_data: User profile and preferences
            n: Number of similar profiles to return

        Returns:
            List of similar student profiles with similarity scores
        """
        return self.svd_recommender.find_similar_profiles(user_data, n)

    def _extract_user_features(self, user_data: Dict) -> List[float]:
        """Extract feature vector from user data for similarity comparison."""
        return [
            user_data.get('cost_importance', 0),
            user_data.get('culture_importance', 0),
            user_data.get('internship_importance', 0),
            user_data.get('ranking_influence', 0),
            user_data.get('extracurricular_importance', 0),
            user_data.get('leadership_role', 0),
            user_data.get('extracurricular_hours', 0)
        ]

    def get_profile_based_recommendations(self, user_data: Dict, n: int = 5) -> List[Dict]:
        """Get university recommendations based on SVD collaborative filtering.

        Args:
            user_data: User profile and preferences
            n: Number of recommendations to return

        Returns:
            List of recommended universities with scores
        """
        # Create a temporary user ID for prediction
        temp_user_id = f"temp_user_{id(user_data)}"

        # Get similar profiles using our feature-based approach
        similar_profiles = self._find_similar_profiles(user_data, n=10)

        # Use SVD to predict ratings for all universities
        predicted_ratings = self.svd_recommender.predict_ratings(temp_user_id)

        # Blend the approaches - weight SVD predictions by similar user insights
        university_scores = {}

        # First, use SVD predictions as base scores
        for pred in predicted_ratings:
            uni = pred['university']
            university_scores[uni] = {
                'name': uni,
                'score': pred['predicted_rating'] * 0.6,  # Base weight for SVD prediction
                'count': 1,
                'svd_score': pred['predicted_rating']
            }

        # Add weighted scores from similar users
        for profile in similar_profiles:
            uni = profile['university']
            sim_score = profile['similarity']
            satisfaction = profile['satisfaction'] if profile['satisfaction'] is not None else 3

            # Weight by similarity and satisfaction
            weight = sim_score * (satisfaction / 5.0) * 0.4  # Weight for similar user component

            if uni in university_scores:
                university_scores[uni]['score'] += weight
                university_scores[uni]['count'] += 1
            else:
                university_scores[uni] = {
                    'name': uni,
                    'score': weight,
                    'count': 1,
                    'svd_score': 0
                }

        # Calculate final scores
        recommendations = []
        for uni, data in university_scores.items():
            # Normalize based on count
            normalized_score = data['score'] / data['count'] if data['count'] > 0 else 0

            # Get university description and additional info
            uni_info = next((u for u in self.universities if u['name'] == uni), None)
            description = uni_info[
                'description'] if uni_info else f"{uni} is recommended based on collaborative filtering."

            recommendations.append({
                'university_id': uni.lower().replace(' ', '_'),
                'name': uni,
                'score': normalized_score,
                'svd_score': data['svd_score'],
                'match_confidence': min(normalized_score * 100, 100),  # Convert to percentage with cap
                'similar_students_count': data['count'] - 1,  # Subtract 1 for the SVD base score
                'description': description,
                'algorithm': 'svd_collaborative_filtering'
            })

        # Sort by score and return top n
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:n]

    def get_embedding_recommendations(self, user_data: Dict, n: int = 5) -> List[Dict]:
        """Get recommendations using embedding similarity."""
        # Create user profile and preferences text
        # First convert user_data to expected format
        formatted_user = {
            'demographic': {
                'age': user_data.get('age'),
                'gender': user_data.get('gender'),
                'personality': user_data.get('personality'),
                'student_status': user_data.get('student_status')
            },
            'academic': {
                'learning_style': user_data.get('learning_style'),
                'school': user_data.get('school'),
                'career_goal': user_data.get('career_goal'),
                'plans_further_education': user_data.get('plans_further_education')
            },
            'preferences': {
                'preferred_population': user_data.get('preferred_population'),
                'residence': user_data.get('residence'),
                'cost_importance': user_data.get('cost_importance'),
                'culture_importance': user_data.get('culture_importance'),
                'internship_importance': user_data.get('internship_importance'),
                'ranking_influence': user_data.get('ranking_influence'),
                'extracurricular_importance': user_data.get('extracurricular_importance'),
                'family_influence': user_data.get('family_influence'),
                'friend_influence': user_data.get('friend_influence'),
                'social_media_influence': user_data.get('social_media_influence')
            },
            'engagement': {
                'leadership_role': user_data.get('leadership_role'),
                'extracurricular_hours': user_data.get('extracurricular_hours'),
                'extracurricular_type': user_data.get('extracurricular_type'),
                'cca_count': user_data.get('cca_count', 0)
            },
            'selection_criteria': user_data.get('selection_criteria', []),
            'ccas': user_data.get('ccas', [])
        }

        profile_text = self._create_profile_text(formatted_user)
        preferences_text = self._create_preferences_text(formatted_user)

        # Use batch mode of the edge function to get both embeddings in one call
        try:
            # Get user embeddings
            profile_embedding = self._get_embedding(profile_text)
            preferences_embedding = self._get_embedding(preferences_text)
        except Exception as e:
            logger.error(f"Error generating user embeddings: {e}")
            # Return profile-based recommendations as fallback
            return self.get_profile_based_recommendations(user_data, n)

        # Calculate similarity with each university
        similarities = []
        for uni in self.universities:
            # Get university embedding
            uni_description = uni['description']
            try:
                uni_embedding = self._get_embedding(uni_description)
            except Exception as e:
                logger.error(f"Error generating university embedding: {e}")
                continue

            # Calculate similarity with user preferences (primary) and profile (secondary)
            pref_similarity = 1 - cosine(preferences_embedding, uni_embedding)
            profile_similarity = 1 - cosine(profile_embedding, uni_embedding)

            # Weighted combination (70% preferences, 30% profile)
            combined_similarity = 0.7 * pref_similarity + 0.3 * profile_similarity

            similarities.append({
                'university_id': uni['id'],
                'name': uni['name'],
                'score': combined_similarity,
                'description': uni['description'],
                'algorithm': 'embedding'
            })

        # Sort and return top n recommendations
        return sorted(similarities, key=lambda x: x['score'], reverse=True)[:n]

    def get_hybrid_recommendations(self, user_data: Dict, n: int = 5) -> List[Dict]:
        """Get recommendations using a hybrid approach combining profile matching and embeddings."""
        # Get profile-based recommendations
        profile_recs = self.get_profile_based_recommendations(user_data, n=n)

        # Get embedding-based recommendations
        embedding_recs = self.get_embedding_recommendations(user_data, n=n)

        # Combine recommendations
        combined_recs = {}

        # Find max scores to normalize
        max_profile_score = max([rec['score'] for rec in profile_recs]) if profile_recs else 1.0
        max_embedding_score = max([rec['score'] for rec in embedding_recs]) if embedding_recs else 1.0

        # Process profile recommendations
        for rec in profile_recs:
            # Normalize profile score to 0-1 range
            normalized_profile_score = min(rec['score'] / max_profile_score, 1.0) if max_profile_score > 0 else 0

            combined_recs[rec['university_id']] = {
                'university_id': rec['university_id'],
                'name': rec['name'],
                'profile_score': normalized_profile_score,
                'embedding_score': 0,
                'description': rec['description'],
                'algorithm': 'hybrid'
            }

        # Process embedding recommendations
        for rec in embedding_recs:
            # Normalize embedding score to 0-1 range
            normalized_embedding_score = min(rec['score'] / max_embedding_score, 1.0) if max_embedding_score > 0 else 0

            if rec['university_id'] in combined_recs:
                combined_recs[rec['university_id']]['embedding_score'] = normalized_embedding_score
            else:
                combined_recs[rec['university_id']] = {
                    'university_id': rec['university_id'],
                    'name': rec['name'],
                    'profile_score': 0,
                    'embedding_score': normalized_embedding_score,
                    'description': rec['description'],
                    'algorithm': 'hybrid'
                }

        # Calculate final scores
        # Weights can be adjusted based on system performance
        profile_weight = 0.6
        embedding_weight = 0.4

        recommendations = []
        for uni_id, rec in combined_recs.items():
            final_score = (rec['profile_score'] * profile_weight) + (rec['embedding_score'] * embedding_weight)
            recommendations.append({
                'university_id': uni_id,
                'name': rec['name'],
                'score': final_score,
                'profile_match': rec['profile_score'] * 100,  # Convert to percentage (0-100)
                'semantic_match': rec['embedding_score'] * 100,  # Convert to percentage (0-100)
                'description': rec['description'],
                'algorithm': 'hybrid'
            })

        # Sort and return top n recommendations
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:n]

    def _analyze_university_compatibility(self, user_data: Dict, university: Dict) -> Dict:
        """Analyze compatibility between user and university on different factors."""
        compatibility = {}

        # Analyze learning style compatibility
        if user_data.get('learning_style') and university.get('learning_styles'):
            user_style = user_data['learning_style']
            if user_style in university['learning_styles']:
                compatibility['learning_style'] = university['learning_styles'][user_style]
            else:
                compatibility['learning_style'] = 0.2  # Low compatibility

        # Analyze career goal compatibility
        if user_data.get('career_goal') and university.get('top_career_goals'):
            user_goal = user_data['career_goal']
            if user_goal in university['top_career_goals']:
                compatibility['career_goal'] = 0.9
            else:
                compatibility['career_goal'] = 0.3

        # Analyze personality compatibility
        if user_data.get('personality') and university.get('personality_distribution'):
            user_personality = user_data['personality']
            if user_personality in university['personality_distribution']:
                compatibility['personality'] = university['personality_distribution'][user_personality]
            else:
                compatibility['personality'] = 0.2

        # Analyze importance factors alignment
        importance_factors = [
            ('cost_importance', 'avg_cost_importance'),
            ('culture_importance', 'avg_culture_importance'),
            ('internship_importance', 'avg_internship_importance'),
            ('ranking_influence', 'avg_ranking_influence'),
            ('extracurricular_importance', 'avg_extracurricular_importance')
        ]

        for user_factor, uni_factor in importance_factors:
            if user_data.get(user_factor) is not None and university.get(uni_factor) is not None:
                # Calculate how closely aligned the importance ratings are (on 1-10 scale)
                difference = abs(user_data[user_factor] - university[uni_factor])
                compatibility[user_factor] = 1 - (difference / 10)

        # Overall compatibility score
        if compatibility:
            compatibility['overall'] = sum(compatibility.values()) / len(compatibility)
        else:
            compatibility['overall'] = 0.5  # Default medium compatibility

        return compatibility

    def recommend(self, user_data: Dict, algorithm: str = 'hybrid', n: int = 5) -> List[Dict]:
        """Get university recommendations for a user.

        Args:
            user_data: User profile and preferences data
            algorithm: Which algorithm to use ('profile', 'embedding', or 'hybrid')
            n: Number of recommendations to return

        Returns:
            List of recommended universities with scores
        """
        if algorithm == 'profile':
            return self.get_profile_based_recommendations(user_data, n)
        elif algorithm == 'embedding':
            return self.get_embedding_recommendations(user_data, n)
        else:  # default to hybrid
            return self.get_hybrid_recommendations(user_data, n)

    def explain_recommendation(self, user_data: Dict, university_id: str) -> Dict:
        """Explain why a university was recommended to a user."""
        # Find university data
        university = next((u for u in self.universities if u['id'] == university_id), None)
        if not university:
            return {"error": "University not found"}

        # Get similar student profiles at this university
        similar_profiles = self._find_similar_profiles(user_data, n=3)
        similar_at_uni = [p for p in similar_profiles if p['university'].lower().replace(' ', '_') == university_id]

        # Analyze compatibility factors
        compatibility = self._analyze_university_compatibility(user_data, university)

        # Generate embedding-based similarity if available
        semantic_similarity = 0
        try:
            # Create text representations
            formatted_user = {
                'demographic': {
                    'age': user_data.get('age'),
                    'gender': user_data.get('gender'),
                    'personality': user_data.get('personality'),
                    'student_status': user_data.get('student_status')
                },
                'academic': {
                    'learning_style': user_data.get('learning_style'),
                    'school': user_data.get('school'),
                    'career_goal': user_data.get('career_goal'),
                    'plans_further_education': user_data.get('plans_further_education')
                },
                'preferences': {
                    'preferred_population': user_data.get('preferred_population'),
                    'residence': user_data.get('residence'),
                    'cost_importance': user_data.get('cost_importance'),
                    'culture_importance': user_data.get('culture_importance'),
                    'internship_importance': user_data.get('internship_importance'),
                    'ranking_influence': user_data.get('ranking_influence'),
                    'extracurricular_importance': user_data.get('extracurricular_importance'),
                    'family_influence': user_data.get('family_influence', 0),
                    'friend_influence': user_data.get('friend_influence', 0),
                    'social_media_influence': user_data.get('social_media_influence', 0)
                },
                'engagement': {
                    'leadership_role': user_data.get('leadership_role', 0),
                    'extracurricular_hours': user_data.get('extracurricular_hours', 0),
                    'extracurricular_type': user_data.get('extracurricular_type'),
                    'cca_count': user_data.get('cca_count', 0)
                },
                'selection_criteria': user_data.get('selection_criteria', []),
                'ccas': user_data.get('ccas', [])
            }

            profile_text = self._create_profile_text(formatted_user)
            preferences_text = self._create_preferences_text(formatted_user)

            # Get embeddings
            profile_embedding = self._get_embedding(profile_text)
            preferences_embedding = self._get_embedding(preferences_text)
            uni_embedding = self._get_embedding(university['description'])

            # Calculate similarity
            pref_similarity = 1 - cosine(preferences_embedding, uni_embedding)
            profile_similarity = 1 - cosine(profile_embedding, uni_embedding)
            semantic_similarity = 0.7 * pref_similarity + 0.3 * profile_similarity
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")

        # Prepare explanation
        explanation = {
            'university_id': university_id,
            'name': university['name'],
            'description': university['description'],
            'compatibility': compatibility,
            'semantic_similarity': semantic_similarity,
            'similar_students': len(similar_at_uni),
            'avg_satisfaction': university.get('avg_satisfaction', 0),
            'strengths': [],
            'considerations': []
        }

        # Identify strengths
        if user_data.get('learning_style') in university.get('learning_styles', {}):
            explanation['strengths'].append(
                f"Learning style match: The university has many {user_data['learning_style']} learners")

        if user_data.get('personality') in university.get('personality_distribution', {}):
            explanation['strengths'].append(
                f"Personality match: The university has many {user_data['personality']} students")

        if user_data.get('career_goal') in university.get('top_career_goals', []):
            explanation['strengths'].append(
                f"Career goal alignment: Many students aim for careers as {user_data['career_goal']}")

        # Check importance alignments
        for factor, label in [
            ('culture_importance', 'campus culture'),
            ('internship_importance', 'internship opportunities'),
            ('ranking_influence', 'university rankings'),
            ('extracurricular_importance', 'extracurricular activities')
        ]:
            user_value = user_data.get(factor)
            uni_value = university.get(f"avg_{factor}")
            if user_value is not None and uni_value is not None:
                if user_value > 7 and uni_value > 7:
                    explanation['strengths'].append(f"Strong alignment on {label} importance")
                elif abs(user_value - uni_value) > 3 and user_value > 7:
                    explanation['considerations'].append(
                        f"You value {label} highly, but students at this university typically don't")

        return explanation

    def retrain_svd_model(self):
        """Retrain the SVD model with latest data"""
        logger.info("Retraining SVD recommender model...")
        self.svd_recommender = SVDRecommender(self.data)
        logger.info("SVD model retraining complete")
