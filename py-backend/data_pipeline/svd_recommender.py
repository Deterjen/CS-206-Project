from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from surprise import Dataset, Reader, SVD

from data_pipeline.text_embedder import TextEmbedder
from data_pipeline.user_profile_embedding_manager import embedding_manager


class SVDRecommender:
    """SVD-based collaborative filtering recommender using Surprise library"""

    def __init__(self, data_df, batch_size=128):
        """Initialize the SVD recommender with training data

        Args:
            data_df (pd.DataFrame): DataFrame with student survey data
        """
        self.batch_size = batch_size
        self.data_df = data_df
        self.text_embedder = TextEmbedder('all-MiniLM-L6-v2')
        self.svd_model = None
        self.users_encoded = None
        self.universities = list(data_df['university'].unique())
        self.embedding_manager = embedding_manager

        # Initialize and train the model
        self._prepare_training_data()
        self._train_svd_model()

    def _prepare_training_data(self):
        """Prepare training data by encoding categorical features and creating user profiles with batch processing"""
        # Extract features for encoding
        categorical_features = ['age', 'gender', 'student_status', 'learning_style',
                                'preferred_population', 'residence', 'personality',
                                'school']

        # One-hot encode categorical features
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_features = encoder.fit_transform(self.data_df[categorical_features])
        encoded_df = pd.DataFrame(
            encoded_features,
            columns=encoder.get_feature_names_out(categorical_features)
        )

        # Process list columns using batch text embeddings
        texts_to_embed = []
        row_mapping = []  # Keep track of which row each text belongs to

        for idx, row in self.data_df.iterrows():
            # Convert selection criteria and CCAs to strings
            criteria = []
            if isinstance(row['selection_criteria_list'], str):
                try:
                    criteria = eval(row['selection_criteria_list'])
                except:
                    criteria = []
            elif isinstance(row['selection_criteria_list'], list):
                criteria = row['selection_criteria_list']

            ccas = []
            if isinstance(row['cca_list'], str):
                try:
                    ccas = eval(row['cca_list'])
                except:
                    ccas = []
            elif isinstance(row['cca_list'], list):
                ccas = row['cca_list']

            # Create a combined text for embedding
            criteria_text = ' '.join(criteria) if criteria else ''
            ccas_text = ' '.join(ccas) if ccas else ''
            combined_text = f"{criteria_text} {ccas_text}".strip()

            texts_to_embed.append(combined_text if combined_text else "empty")
            row_mapping.append(idx)

        # Process embeddings in batches
        list_embeddings = []
        batch_size = 32

        for i in range(0, len(texts_to_embed), batch_size):
            batch_texts = texts_to_embed[i:i + batch_size]
            try:
                batch_embeddings = self.text_embedder.encode(batch_texts, 20)
                list_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error in batch embedding generation for batch {i // batch_size}: {e}")
                # Fill failed embeddings with zeros
                list_embeddings.extend([np.zeros(20) for _ in batch_texts])

        # Convert embeddings to DataFrame
        embedding_df = pd.DataFrame(
            list_embeddings,
            index=row_mapping,
            columns=[f'text_embedding_{i}' for i in range(20)]
        )

        # Combine all features
        numerical_features = ['cost_importance', 'culture_importance',
                              'internship_importance', 'ranking_influence',
                              'extracurricular_importance', 'leadership_role',
                              'extracurricular_hours']

        # Scale numerical features
        numerical_df = self.data_df[numerical_features].copy()
        for col in numerical_df.columns:
            if numerical_df[col].max() > 0:
                numerical_df[col] = numerical_df[col] / numerical_df[col].max()

        # Combine all features
        self.users_encoded = pd.concat(
            [encoded_df, embedding_df, numerical_df.reset_index(drop=True)],
            axis=1
        )

        # Prepare interaction data for SVD
        interactions = []
        for idx, row in self.data_df.iterrows():
            user_id = f"student_{idx}"
            university = row['university']
            rating = row['satisfaction_rating']
            if pd.notna(rating):
                interactions.append({
                    'user': user_id,
                    'university': university,
                    'rating': rating
                })

        self.interactions_df = pd.DataFrame(interactions)

    def _train_svd_model(self):
        """Train the SVD model using Surprise library"""
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            self.interactions_df[['user', 'university', 'rating']],
            reader
        )
        trainset = data.build_full_trainset()

        # Initialize and train SVD model
        self.svd_model = SVD(n_factors=20, n_epochs=20, lr_all=0.005, reg_all=0.02)
        self.svd_model.fit(trainset)

    def _encode_user(self, user_data):
        """Encode a new user's data to match the training format

        Args:
            user_data (dict): User profile and preferences

        Returns:
            dict: Encoded user features
        """
        # Create a DataFrame with one row for the user
        user_df = pd.DataFrame([user_data])

        # Encode categorical features (same as in training)
        categorical_features = ['age', 'gender', 'student_status', 'learning_style',
                                'preferred_population', 'residence', 'personality',
                                'school']

        # Handle missing values in categorical features
        for feature in categorical_features:
            if feature not in user_df or pd.isna(user_df[feature].iloc[0]):
                user_df[feature] = 'unknown'

        # One-hot encode categorical features
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoder.fit(self.data_df[categorical_features])
        encoded_features = encoder.transform(user_df[categorical_features])

        # Process list columns using text embeddings
        criteria = ' '.join(user_data.get('selection_criteria', []))
        ccas = ' '.join(user_data.get('ccas', []))
        combined_text = f"{criteria} {ccas}".strip()

        if combined_text:
            text_embedding = self.text_embedder.encode(combined_text)[:20]
        else:
            text_embedding = np.zeros(20)

        # Get numerical features
        numerical_features = ['cost_importance', 'culture_importance',
                              'internship_importance', 'ranking_influence',
                              'extracurricular_importance', 'leadership_role',
                              'extracurricular_hours']

        numerical_values = []
        for feature in numerical_features:
            value = user_data.get(feature, 0)
            # Scale based on training data max
            max_val = self.data_df[feature].max()
            if max_val > 0:
                value = value / max_val
            numerical_values.append(value)

        # Combine all features
        combined_features = np.concatenate([
            encoded_features[0],
            text_embedding,
            numerical_values
        ])

        return combined_features

    def find_similar_profiles(self, user_data: Dict, n: int = 5) -> List[Dict]:
        """Find similar student profiles based on encoded features."""
        return self.embedding_manager.find_similar_profiles(
            user_data=user_data,
            profiles_df=self.data_df,
            n=n
        )

    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0

        return dot_product / (norm_a * norm_b)

    def predict_ratings(self, user_id, universities=None):
        """Predict user ratings for universities using SVD model

        Args:
            user_id (str): User ID
            universities (list): List of universities to predict ratings for
                                If None, predict for all universities

        Returns:
            list: Predicted ratings for each university
        """
        if universities is None:
            universities = self.universities

        predictions = []
        for uni in universities:
            pred = self.svd_model.predict(user_id, uni)
            predictions.append({
                'university': uni,
                'predicted_rating': pred.est,
                'details': pred
            })

        return sorted(predictions, key=lambda x: x['predicted_rating'], reverse=True)
