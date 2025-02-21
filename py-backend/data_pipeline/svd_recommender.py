from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from surprise import Dataset, Reader, SVD
from surprise.model_selection import GridSearchCV


class SVDRecommender:
    """Enhanced SVD-based collaborative filtering recommender"""

    def __init__(self, data_df: pd.DataFrame, batch_size: int = 128):
        """Initialize the improved SVD recommender with training data

        Args:
            data_df (pd.DataFrame): DataFrame with student survey data
            batch_size (int): Batch size for processing
        """
        self.batch_size = batch_size
        self.data_df = data_df
        self.scaler = StandardScaler()
        self.svd_model = None
        self.feature_importances = {}
        self.confidence_scores = {}

        # Initialize and train the model
        self._prepare_training_data()
        self._tune_and_train_svd_model()

    def _prepare_training_data(self):
        """Prepare training data with improved feature engineering"""
        # Extract and normalize numerical features
        numerical_features = [
            'cost_importance', 'culture_importance', 'internship_importance',
            'ranking_influence', 'extracurricular_importance', 'leadership_role',
            'extracurricular_hours'
        ]

        # Scale numerical features
        scaled_features = self.scaler.fit_transform(self.data_df[numerical_features])
        self.scaled_df = pd.DataFrame(
            scaled_features,
            columns=numerical_features,
            index=self.data_df.index
        )

        # Calculate feature importance based on correlation with satisfaction
        for feature in numerical_features:
            correlation = np.abs(np.corrcoef(
                self.data_df[feature],
                self.data_df['satisfaction_rating']
            )[0, 1])
            self.feature_importances[feature] = correlation

        # Normalize feature importances
        total_importance = sum(self.feature_importances.values())
        self.feature_importances = {
            k: v / total_importance
            for k, v in self.feature_importances.items()
        }

        # Prepare interaction data with confidence scores
        self.interactions = []
        for idx, row in self.data_df.iterrows():
            user_id = f"student_{idx}"
            university = row['university']
            rating = row['satisfaction_rating']

            # Calculate confidence score based on feature completeness
            confidence = self._calculate_confidence_score(row)
            self.confidence_scores[(user_id, university)] = confidence

            if pd.notna(rating):
                self.interactions.append({
                    'user': user_id,
                    'university': university,
                    'rating': rating,
                    'confidence': confidence
                })

    def _calculate_confidence_score(self, user_data: pd.Series) -> float:
        """Calculate confidence score for a user's ratings based on data completeness"""
        # Check completeness of important fields
        important_fields = [
            'learning_style', 'school', 'career_goal', 'preferred_population',
            'cost_importance', 'culture_importance', 'internship_importance'
        ]

        # Calculate basic completeness score
        completeness = sum(1 for field in important_fields if pd.notna(user_data.get(field))) / len(important_fields)

        # Add bonus for engagement indicators
        engagement_bonus = 0
        if user_data.get('leadership_role') == 1:
            engagement_bonus += 0.1
        if user_data.get('extracurricular_hours', 0) > 5:
            engagement_bonus += 0.1
        if user_data.get('cca_count', 0) > 2:
            engagement_bonus += 0.1

        # Final confidence score (between 0 and 1)
        confidence = min(completeness + engagement_bonus, 1.0)
        return confidence

    def _tune_and_train_svd_model(self):
        """Tune SVD parameters using cross-validation and train final model"""
        # Prepare data for Surprise
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            pd.DataFrame(self.interactions)[['user', 'university', 'rating']],
            reader
        )

        # Define parameter grid
        param_grid = {
            'n_epochs': [20, 30, 40],
            'lr_all': [0.002, 0.005, 0.007],
            'reg_all': [0.02, 0.04, 0.06],
            'n_factors': [20, 30, 40]
        }

        # Perform grid search with cross-validation
        gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=5)
        gs.fit(data)

        # Get best parameters
        best_params = gs.best_params['rmse']

        # Train final model with best parameters
        trainset = data.build_full_trainset()
        self.svd_model = SVD(
            n_factors=best_params['n_factors'],
            n_epochs=best_params['n_epochs'],
            lr_all=best_params['lr_all'],
            reg_all=best_params['reg_all']
        )
        self.svd_model.fit(trainset)

        # Store cross-validation scores
        self.cv_rmse = gs.best_score['rmse']
        self.cv_mae = gs.best_score['mae']

    def predict_ratings(self, user_id: str, universities: List[str] = None) -> List[Dict]:
        """Predict user ratings for universities with confidence scores

        Args:
            user_id (str): User ID
            universities (list): List of universities to predict ratings for

        Returns:
            list: Predicted ratings with confidence scores
        """
        if universities is None:
            universities = self.data_df['university'].unique()

        predictions = []
        for uni in universities:
            # Get base prediction from SVD
            pred = self.svd_model.predict(user_id, uni)

            # Get confidence score
            confidence = self.confidence_scores.get((user_id, uni), 0.5)

            # Adjust prediction based on confidence
            adjusted_rating = pred.est * confidence + 3.0 * (1 - confidence)

            predictions.append({
                'university': uni,
                'predicted_rating': adjusted_rating,
                'base_prediction': pred.est,
                'confidence': confidence,
                'details': pred
            })

        return sorted(predictions, key=lambda x: x['predicted_rating'], reverse=True)

    def get_model_metrics(self) -> Dict:
        """Get model performance metrics"""
        return {
            'cv_rmse': self.cv_rmse,
            'cv_mae': self.cv_mae,
            'feature_importances': self.feature_importances,
            'average_confidence': np.mean(list(self.confidence_scores.values()))
        }
