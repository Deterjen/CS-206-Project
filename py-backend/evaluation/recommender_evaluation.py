import logging
import os
import tempfile
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from university_recommender import UniversityRecommender


class RecommenderEvaluator:
    """Evaluation framework for the University Recommender System"""

    def __init__(self, data_path: str):
        """
        Initialize the evaluator

        Args:
            data_path: Path to the synthetic dataset
        """
        self.data = pd.read_csv(data_path)
        self.logger = logging.getLogger(__name__)
        self.recommender = None

    def prepare_train_test_split(self, test_size=0.2, random_state=42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split the dataset into training and testing sets and initialize recommender with only training data
        """
        train_data, test_data = train_test_split(
            self.data,
            test_size=test_size,
            random_state=random_state,
            stratify=self.data['university']  # Stratify by university to maintain distribution
        )

        # Create a temporary file to store training data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp_file:
            train_data.to_csv(tmp_file.name, index=False)
            # Initialize recommender with only training data
            self.recommender = UniversityRecommender(tmp_file.name)

        # Clean up temporary file
        os.unlink(tmp_file.name)

        return train_data, test_data

    def evaluate_recommendations(self, test_data: pd.DataFrame, k: int = 5) -> Dict:
        """
        Evaluate recommendations using various metrics

        Args:
            test_data: Test dataset
            k: Number of recommendations to generate

        Returns:
            Dictionary containing evaluation metrics
        """
        if self.recommender is None:
            raise ValueError("Recommender not initialized. Run prepare_train_test_split first.")

        metrics = {
            'profile_based': {
                'ndcg': [], 'precision': [], 'recall': [],
                'diversity': [], 'coverage': set(), 'personalization': []
            },
            'embedding': {
                'ndcg': [], 'precision': [], 'recall': [],
                'diversity': [], 'coverage': set(), 'personalization': []
            },
            'hybrid': {
                'ndcg': [], 'precision': [], 'recall': [],
                'diversity': [], 'coverage': set(), 'personalization': []
            }
        }

        # Use only universities from training data for coverage calculation
        train_universities = set(uni['name'] for uni in self.recommender.universities)
        all_recommendations = []

        # Evaluate each test user
        for idx, user in test_data.iterrows():
            # Convert row to dictionary, excluding the actual university
            user_dict = user.drop('university').to_dict()

            # Get recommendations using different methods
            try:
                methods = {
                    'profile_based': self.recommender.get_profile_based_recommendations,
                    'embedding': self.recommender.get_embedding_recommendations,
                    'hybrid': self.recommender.get_hybrid_recommendations
                }

                all_recommendations = {method: [] for method in methods.keys()}
                actual_university = user['university']

                for method_name, recommender_method in methods.items():
                    try:
                        recommendations = recommender_method(user_dict, k)

                        # Store recommendations for personalization calculation
                        all_recommendations[method_name].append([rec['name'] for rec in recommendations])

                        # Update coverage
                        metrics[method_name]['coverage'].update([rec['name'] for rec in recommendations])

                        # Calculate relevance metrics
                        predicted_universities = [rec['name'] for rec in recommendations]

                        # NDCG calculation
                        relevance = [1 if uni == actual_university else 0 for uni in predicted_universities]
                        if sum(relevance) > 0:
                            metrics[method_name]['ndcg'].append(self._calculate_ndcg(relevance))

                        # Precision and Recall
                        precision = 1 if actual_university in predicted_universities else 0
                        metrics[method_name]['precision'].append(precision)
                        metrics[method_name]['recall'].append(precision)

                        # Calculate diversity of recommendations
                        metrics[method_name]['diversity'].append(self._calculate_diversity(recommendations))

                    except Exception as e:
                        self.logger.warning(f"Error with {method_name} recommendations for user {idx}: {str(e)}")
                        continue

            except Exception as e:
                self.logger.warning(f"Error generating recommendations for user {idx}: {str(e)}")
                continue

        # Calculate personalization and aggregate metrics for each method
        evaluation_results = {}

        for method_name in ['profile_based', 'embedding', 'hybrid']:
            method_metrics = metrics[method_name]

            # Calculate personalization for this method
            method_metrics['personalization'] = self._calculate_personalization(
                [recs for recs in all_recommendations[method_name] if recs]  # Filter out empty recommendations
            )

            # Calculate coverage percentage
            coverage_percentage = len(method_metrics['coverage']) / len(train_universities) * 100

            # Aggregate metrics for this method
            evaluation_results[method_name] = {
                'ndcg@k': np.mean(method_metrics['ndcg']) if method_metrics['ndcg'] else 0,
                'precision@k': np.mean(method_metrics['precision']) if method_metrics['precision'] else 0,
                'recall@k': np.mean(method_metrics['recall']) if method_metrics['recall'] else 0,
                'diversity': np.mean(method_metrics['diversity']) if method_metrics['diversity'] else 0,
                'coverage_percentage': coverage_percentage,
                'personalization': method_metrics['personalization']
            }

        return evaluation_results

    def _calculate_ndcg(self, relevance: List[int], k: int = None) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        if k is None:
            k = len(relevance)
        dcg = sum((2 ** rel - 1) / np.log2(i + 2) for i, rel in enumerate(relevance[:k]))
        idcg = sum((2 ** rel - 1) / np.log2(i + 2) for i, rel in enumerate(sorted(relevance, reverse=True)[:k]))
        return dcg / idcg if idcg > 0 else 0

    def _calculate_diversity(self, recommendations: List[Dict]) -> float:
        """
        Calculate diversity score based on recommendation attributes
        """
        unique_attributes = set()
        for rec in recommendations:
            # Extract key attributes that contribute to diversity
            if 'description' in rec:
                unique_attributes.update(rec['description'].split())
        return len(unique_attributes) / (len(recommendations) * 10)  # Normalize

    def _calculate_personalization(self, all_recommendations: List[List[str]]) -> float:
        """
        Calculate personalization by comparing recommendations across users
        """
        if len(all_recommendations) < 2:
            return 0.0

        similarity_sum = 0
        comparison_count = 0

        for i in range(len(all_recommendations)):
            for j in range(i + 1, len(all_recommendations)):
                set_i = set(all_recommendations[i])
                set_j = set(all_recommendations[j])
                jaccard_sim = len(set_i.intersection(set_j)) / len(set_i.union(set_j))
                similarity_sum += jaccard_sim
                comparison_count += 1

        # Return dissimilarity (1 - similarity) as personalization score
        return 1 - (similarity_sum / comparison_count) if comparison_count > 0 else 0


# Example usage:
def main():
    # Initialize evaluator
    evaluator = RecommenderEvaluator('../data/synthetic_data/all_profiles.csv')

    # Prepare data and train recommender
    train_data, test_data = evaluator.prepare_train_test_split()
    print(f"Training set size: {len(train_data)}")
    print(f"Test set size: {len(test_data)}")

    # Evaluate recommendations
    metrics = evaluator.evaluate_recommendations(test_data)
    print("\nRecommendation Metrics by Method:")
    for method_name, metrics in metrics.items():
        print(f"\n{method_name.upper()} Method:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()
