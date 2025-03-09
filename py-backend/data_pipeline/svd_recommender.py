from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from sklearn.preprocessing import StandardScaler

from data_pipeline.user_profile_embedding_manager import embedding_manager


class SVDRecommender:
    """SVD-based recommender using embeddings for university recommendations"""

    def __init__(self, data_df: pd.DataFrame, n_components: int = 50, batch_size: int = 128):
        """Initialize the SVD recommender with training data

        Args:
            data_df (pd.DataFrame): DataFrame with student survey data
            n_components (int): Number of SVD components to keep
            batch_size (int): Batch size for processing embeddings
        """
        self.data_df = data_df
        self.n_components = n_components
        self.batch_size = batch_size
        self.embedding_manager = embedding_manager
        self.universities = list(data_df['university'].unique())

        # Initialize embeddings and SVD model
        self._prepare_embedding_data()
        self._train_svd_model()

    def _prepare_embedding_data(self):
        """Prepare embedding data for SVD training using existing embedding manager"""
        print("Preparing embedding data...")

        # Process in batches
        total_rows = len(self.data_df)
        combined_embeddings = []

        for start_idx in range(0, total_rows, self.batch_size):
            end_idx = min(start_idx + self.batch_size, total_rows)
            batch_df = self.data_df.iloc[start_idx:end_idx]

            for _, row in batch_df.iterrows():
                # Use embedding manager to get embeddings
                embeddings = self.embedding_manager.get_user_embeddings(row.to_dict())
                # Use only profile embeddings for consistency
                combined_embeddings.append(embeddings['profile'])

            print(f"Processed {end_idx}/{total_rows} profiles")

        # Convert to numpy array
        self.combined_embeddings = np.array(combined_embeddings)

        # Scale the embeddings
        self.scaler = StandardScaler()
        self.scaled_embeddings = self.scaler.fit_transform(self.combined_embeddings)

        # Get university embeddings
        print("Getting university embeddings...")
        self.university_embeddings = {}

        for uni in self.universities:
            uni_embedding = self.embedding_manager.get_university_embedding(
                uni.lower().replace(' ', '_'),
                self._get_university_description(uni)
            )
            # Ensure university embedding has same dimensions
            self.university_embeddings[uni] = uni_embedding

        print("Embedding data preparation complete")

    def _get_user_transformed_embedding(self, user_data: Dict) -> np.ndarray:
        """Get transformed embedding for a user in SVD space"""
        # Get user embeddings using embedding manager
        embeddings = self.embedding_manager.get_user_embeddings(user_data)
        # Use only profile embeddings for consistency with university embeddings
        profile_embedding = embeddings['profile']

        # Scale and transform
        scaled = self.scaler.transform(profile_embedding.reshape(1, -1))
        transformed = scaled @ self.Vt.T @ np.diag(1 / self.s)

        return transformed.flatten()

    def _train_svd_model(self):
        """Train SVD model on the prepared embeddings"""
        print("Training SVD model...")

        # Apply SVD to the scaled embeddings
        U, s, Vt = np.linalg.svd(self.scaled_embeddings, full_matrices=False)

        # Keep top components
        self.n_components = min(self.n_components, len(s))
        self.U = U[:, :self.n_components]
        self.s = s[:self.n_components]
        self.Vt = Vt[:self.n_components, :]

        # Store transformed embeddings
        self.transformed_embeddings = self.U @ np.diag(self.s)

        # Transform university embeddings
        self.transformed_universities = {}
        for uni_name, uni_embedding in self.university_embeddings.items():
            # Scale the university embedding
            scaled_uni = self.scaler.transform(uni_embedding.reshape(1, -1))
            # Project into SVD space
            transformed_uni = scaled_uni @ self.Vt.T @ np.diag(1 / self.s)
            self.transformed_universities[uni_name] = transformed_uni.flatten()

        print("SVD model training complete")

    def _get_university_description(self, university: str) -> str:
        """Get university description for embedding generation"""
        uni_data = self.data_df[self.data_df['university'] == university]

        if len(uni_data) == 0:
            return f"University {university}"

        # Calculate key metrics
        avg_satisfaction = uni_data['satisfaction_rating'].mean()
        top_schools = uni_data['school'].value_counts().nlargest(3).index.tolist()
        learning_styles = uni_data['learning_style'].value_counts()
        top_style = learning_styles.index[0] if not learning_styles.empty else "varied"

        # Create description
        description = (
            f"{university} university has an average satisfaction rating of {avg_satisfaction:.1f}/5. "
            f"Known for {top_style} learning environment. "
            f"Strong programs in {', '.join(top_schools)}. "
        )

        return description

    def get_similar_universities(self, user_data: Dict, n: int = 5) -> List[Dict]:
        """Get similar universities using SVD-transformed embeddings"""
        try:
            # Get user transformed embedding
            user_transformed = self._get_user_transformed_embedding(user_data)

            # Calculate similarities with universities
            similarities = []
            for uni_name, uni_transformed in self.transformed_universities.items():
                similarity = 1 - cosine(user_transformed, uni_transformed)

                similarities.append({
                    'university_id': uni_name.lower().replace(' ', '_'),
                    'name': uni_name,
                    'score': similarity,
                    'description': self._get_university_description(uni_name),
                    'avg_satisfaction': self.data_df[
                        self.data_df['university'] == uni_name
                        ]['satisfaction_rating'].mean()
                })

            # Sort by similarity and return top n
            recommendations = sorted(similarities, key=lambda x: x['score'], reverse=True)[:n]

            # Add confidence scores
            max_score = max(r['score'] for r in recommendations)
            min_score = min(r['score'] for r in recommendations)
            score_range = max_score - min_score if max_score > min_score else 1

            for rec in recommendations:
                rec['confidence'] = ((rec['score'] - min_score) / score_range) * 100

            return recommendations

        except Exception as e:
            print(f"Error in get_similar_universities: {str(e)}")
            return []

    def find_similar_profiles(self, user_data: Dict, n: int = 5) -> List[Dict]:
        """Find similar student profiles using SVD-transformed embeddings"""
        try:
            # Get user transformed embedding
            user_transformed = self._get_user_transformed_embedding(user_data)

            # Calculate similarities with all profiles
            similarities = []
            for i, profile_transformed in enumerate(self.transformed_embeddings):
                similarity = 1 - cosine(user_transformed, profile_transformed)
                profile_data = self.data_df.iloc[i]

                similarities.append({
                    'profile_id': f"student_{i}",
                    'university': profile_data['university'],
                    'satisfaction': profile_data['satisfaction_rating'],
                    'similarity': similarity,
                    'school': profile_data['school'],
                    'career_goal': profile_data['career_goal']
                })

            # Sort by similarity and return top n
            similar_profiles = sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:n]

            # Add match percentage
            max_sim = max(p['similarity'] for p in similar_profiles)
            min_sim = min(p['similarity'] for p in similar_profiles)
            sim_range = max_sim - min_sim if max_sim > min_sim else 1

            for profile in similar_profiles:
                profile['match_percentage'] = ((profile['similarity'] - min_sim) / sim_range) * 100

            return similar_profiles

        except Exception as e:
            print(f"Error in find_similar_profiles: {str(e)}")
            return []
