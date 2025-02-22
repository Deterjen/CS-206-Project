"""
Centralized embedding management for user profiles and universities.
This module handles all embedding-related operations and similarity searches across the recommendation system.
"""

import logging
from typing import Dict, List

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class UserProfileEmbeddingManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            logger.info("Creating new UserProfileEmbeddingManager instance")
            cls._instance = super(UserProfileEmbeddingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.info("Initializing UserProfileEmbeddingManager")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings_cache = {}
            self.profile_embeddings_cache = {}
            self.university_embeddings_cache = {}
            self._initialized = True

    def create_profile_text(self, profile: Dict) -> str:
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

    def create_preferences_text(self, profile: Dict) -> str:
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

    def format_user_data(self, user_data: Dict) -> Dict:
        """Format raw user data into standardized profile structure."""
        return {
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

    def batch_get_embeddings(self, texts: List[str], batch_size: int = 512) -> Dict[str, np.ndarray]:
        """Get embeddings for multiple texts in batches with caching."""
        # Remove duplicates while preserving order
        unique_texts = list(dict.fromkeys(texts))

        # Check cache first
        uncached_texts = []
        embeddings_dict = {}
        for text in unique_texts:
            if text in self.embeddings_cache:
                embeddings_dict[text] = self.embeddings_cache[text]
            else:
                uncached_texts.append(text)

        # Process uncached texts in batches
        for i in range(0, len(uncached_texts), batch_size):
            batch = uncached_texts[i:i + batch_size]
            try:
                batch_embeddings = self.model.encode(batch)

                # Normalize and cache results
                for text, embedding in zip(batch, batch_embeddings):
                    if np.linalg.norm(embedding) > 0:
                        embedding = embedding / np.linalg.norm(embedding)
                    self.embeddings_cache[text] = embedding
                    embeddings_dict[text] = embedding
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                # Fill failed embeddings with zeros
                for text in batch:
                    if text not in embeddings_dict:
                        embeddings_dict[text] = np.zeros(384)
                        self.embeddings_cache[text] = embeddings_dict[text]

        return embeddings_dict

    def get_user_embeddings(self, user_data: Dict) -> Dict[str, np.ndarray]:
        """Get both profile and preferences embeddings for a user."""
        formatted_user = self.format_user_data(user_data)
        profile_text = self.create_profile_text(formatted_user)
        preferences_text = self.create_preferences_text(formatted_user)

        embeddings = self.batch_get_embeddings([profile_text, preferences_text])
        return {
            'profile': embeddings[profile_text],
            'preferences': embeddings[preferences_text]
        }

    def get_university_embedding(self, university_id: str, description: str) -> np.ndarray:
        """Get embedding for a university using its ID and description."""
        if university_id in self.university_embeddings_cache:
            return self.university_embeddings_cache[university_id]

        embeddings = self.batch_get_embeddings([description])
        embedding = embeddings[description]
        self.university_embeddings_cache[university_id] = embedding
        return embedding

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            # Check if either vector is all zeros
            if np.all(a == 0) or np.all(b == 0):
                return 0.0

            # Calculate dot product and magnitudes
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            # Check for zero magnitudes
            if norm_a == 0 or norm_b == 0:
                return 0.0

            # Calculate cosine similarity
            similarity = dot_product / (norm_a * norm_b)

            # Ensure the result is between 0 and 1
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.warning(f"Error calculating cosine similarity: {e}")
            return 0.0

    def precompute_embeddings(self, profiles_df: pd.DataFrame, universities: List[Dict]):
        """Precompute embeddings for all profiles and universities in the training data."""
        logger.info("Precomputing embeddings for training data...")

        # Precompute profile embeddings
        batch_size = 512
        total_profiles = len(profiles_df)
        profile_batches = (total_profiles + batch_size - 1) // batch_size

        logger.info(f"Processing {total_profiles} profiles in {profile_batches} batches")

        for start_idx in range(0, total_profiles, batch_size):
            batch_df = profiles_df.iloc[start_idx:start_idx + batch_size]

            # Create profile texts for the batch
            batch_profiles = []
            batch_preferences = []
            batch_ids = []

            for idx, row in batch_df.iterrows():
                formatted_profile = self.format_user_data(row.to_dict())
                profile_text = self.create_profile_text(formatted_profile)
                preferences_text = self.create_preferences_text(formatted_profile)

                batch_profiles.append(profile_text)
                batch_preferences.append(preferences_text)
                batch_ids.append(idx)

            # Get embeddings for the batch
            profile_embeddings = self.batch_get_embeddings(batch_profiles)
            preferences_embeddings = self.batch_get_embeddings(batch_preferences)

            # Cache the embeddings
            for i, idx in enumerate(batch_ids):
                self.profile_embeddings_cache[idx] = {
                    'profile': profile_embeddings[batch_profiles[i]],
                    'preferences': preferences_embeddings[batch_preferences[i]]
                }

        # Precompute university embeddings
        logger.info(f"Processing {len(universities)} universities")
        for uni in universities:
            if uni['id'] not in self.university_embeddings_cache:
                self.university_embeddings_cache[uni['id']] = self.get_university_embedding(
                    uni['id'],
                    uni['description']
                )

        logger.info(
            f"Finished precomputing embeddings for {len(profiles_df)} profiles and {len(universities)} universities")

    def find_similar_profiles(self, user_data: Dict, profiles_df: pd.DataFrame, n: int = 5) -> List[Dict]:
        """Find similar student profiles based on profile and preferences embeddings."""
        try:
            # Get user embeddings
            user_embeddings = self.get_user_embeddings(user_data)

            # Calculate similarities for each profile in the dataset
            similarities = []

            for idx, row in profiles_df.iterrows():
                if idx in self.profile_embeddings_cache:
                    cached_embeddings = self.profile_embeddings_cache[idx]

                    # Calculate similarity scores
                    profile_similarity = self._cosine_similarity(
                        user_embeddings['profile'],
                        cached_embeddings['profile']
                    )
                    preferences_similarity = self._cosine_similarity(
                        user_embeddings['preferences'],
                        cached_embeddings['preferences']
                    )

                    # Weighted combination of similarities
                    combined_similarity = (0.3 * profile_similarity +
                                           0.7 * preferences_similarity)

                    similarities.append({
                        'profile_id': f"student_{idx}",
                        'university': row['university'],
                        'satisfaction': row['satisfaction_rating'],
                        'similarity': combined_similarity,
                        'profile_similarity': profile_similarity,
                        'preferences_similarity': preferences_similarity
                    })

            # Sort by similarity and return top n
            return sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:n]

        except Exception as e:
            logger.error(f"Error in find_similar_profiles: {e}")
            return []


# Create a global instance
embedding_manager = UserProfileEmbeddingManager()
