import logging
import os
import tempfile
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from university_recommender import UniversityRecommender

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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

    from typing import List, Dict
    import pandas as pd

    def evaluate_recommendations(self, test_data: pd.DataFrame, k: int = 5) -> Dict:
        """
        Evaluate recommendations using various metrics
        """
        if self.recommender is None:
            raise ValueError("Recommender not initialized. Run prepare_train_test_split first.")

        # Initialize metrics
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

        # Precompute embeddings for test data with progress bar
        logger.info("Precomputing embeddings for test data...")
        self.recommender.embedding_manager.precompute_embeddings(test_data, self.recommender.universities)
        logger.info("Finished precomputing test data embeddings")

        # Use only universities from training data for coverage calculation
        train_universities = set(uni['name'] for uni in self.recommender.universities)
        all_recommendations = []

        # Define methods to evaluate
        methods = {
            'profile_based': self.recommender.get_profile_based_recommendations,
            'embedding': self.recommender.get_embedding_recommendations,
            'hybrid': self.recommender.get_hybrid_recommendations
        }

        # Create progress bar for test data evaluation
        total_iterations = len(test_data) * len(methods)
        with tqdm(total=total_iterations, desc="Evaluating recommendations") as pbar:
            # Evaluate each test user
            for idx, user in test_data.iterrows():
                # Convert row to dictionary, excluding the actual university
                user_dict = user.drop('university').to_dict()
                actual_university = user['university']

                # Initialize recommendations storage for this iteration
                current_recommendations = {method: [] for method in methods.keys()}

                # Try each recommendation method
                for method_name, recommender_method in methods.items():
                    try:
                        recommendations = recommender_method(user_dict, k)

                        # Store recommendations for personalization calculation
                        current_recommendations[method_name] = [rec['name'] for rec in recommendations]

                        # Update coverage
                        metrics[method_name]['coverage'].update(current_recommendations[method_name])

                        # Calculate relevance metrics
                        relevance = [1 if uni == actual_university else 0 for uni in
                                     current_recommendations[method_name]]
                        if sum(relevance) > 0:
                            metrics[method_name]['ndcg'].append(self._calculate_ndcg(relevance))

                        # Precision and Recall
                        precision = 1 if actual_university in current_recommendations[method_name] else 0
                        metrics[method_name]['precision'].append(precision)
                        metrics[method_name]['recall'].append(precision)

                        # Calculate diversity
                        metrics[method_name]['diversity'].append(self._calculate_diversity(recommendations))

                    except Exception as e:
                        self.logger.warning(f"Error with {method_name} recommendations for user {idx}: {str(e)}")

                    # Update progress bar
                    pbar.update(1)
                    pbar.set_postfix({
                        'method': method_name,
                        'user': idx
                    })

                # Store recommendations for personalization calculation
                for method_name in methods:
                    if current_recommendations[method_name]:
                        all_recommendations.append({
                            'method': method_name,
                            'recommendations': current_recommendations[method_name]
                        })

        # Calculate final metrics
        evaluation_results = {}
        for method_name in methods:
            method_metrics = metrics[method_name]

            # Calculate personalization
            method_recommendations = [r['recommendations'] for r in all_recommendations if r['method'] == method_name]
            method_metrics['personalization'] = self._calculate_personalization(method_recommendations)

            # Calculate coverage percentage
            coverage_percentage = len(method_metrics['coverage']) / len(train_universities) * 100

            # Aggregate metrics
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
