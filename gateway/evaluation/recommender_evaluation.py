import concurrent.futures
import logging
import os
import tempfile
from typing import List, Dict
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

    def evaluate_batch(self, batch_data: pd.DataFrame, methods: Dict, k: int) -> List[Dict]:
        """
        Evaluate a batch of test data
        """
        batch_results = []

        for idx, user in batch_data.iterrows():
            # Convert row to dictionary, excluding the actual university
            user_dict = user.drop('university').to_dict()
            actual_university = user['university']

            # Store results for this user
            user_results = {
                'idx': idx,
                'actual_university': actual_university,
                'method_results': {}
            }

            # Try each recommendation method
            for method_name, recommender_method in methods.items():
                try:
                    recommendations = recommender_method(user_dict, k)
                    predicted_universities = [rec['name'] for rec in recommendations]

                    # Calculate metrics
                    relevance = [1 if uni == actual_university else 0 for uni in predicted_universities]
                    precision = 1 if actual_university in predicted_universities else 0

                    user_results['method_results'][method_name] = {
                        'recommendations': recommendations,
                        'predicted_unis': predicted_universities,
                        'relevance': relevance,
                        'precision': precision,
                        'ndcg': self._calculate_ndcg(relevance) if sum(relevance) > 0 else 0,
                        'diversity': self._calculate_diversity(recommendations)
                    }

                except Exception as e:
                    self.logger.warning(f"Error with {method_name} recommendations for user {idx}: {str(e)}")
                    user_results['method_results'][method_name] = None

            batch_results.append(user_results)

        return batch_results

    def evaluate_recommendations(self, test_data: pd.DataFrame, k: int = 5, n_workers: int = 4,
                                 batch_size: int = 128) -> Dict:
        """
        Evaluate recommendations using parallel processing
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

        # Precompute embeddings for test data
        logger.info("Precomputing embeddings for test data...")
        self.recommender.embedding_manager.precompute_embeddings(test_data, self.recommender.universities)
        logger.info("Finished precomputing test data embeddings")

        # Define methods to evaluate
        methods = {
            'profile_based': self.recommender.get_profile_based_recommendations,
            'embedding': self.recommender.get_embedding_recommendations,
            'hybrid': self.recommender.get_hybrid_recommendations
        }

        # Create batches
        n_samples = len(test_data)
        n_batches = (n_samples + batch_size - 1) // batch_size

        # Process batches in parallel
        all_results = []
        with tqdm(total=n_batches, desc="Processing batches") as pbar:
            with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
                # Create batch tasks
                future_to_batch = {}
                for i in range(0, n_samples, batch_size):
                    batch = test_data.iloc[i:i + batch_size]
                    future = executor.submit(self.evaluate_batch, batch, methods, k)
                    future_to_batch[future] = i // batch_size

                # Process completed batches
                for future in concurrent.futures.as_completed(future_to_batch):
                    batch_idx = future_to_batch[future]
                    try:
                        batch_results = future.result()
                        all_results.extend(batch_results)
                        pbar.update(1)
                        pbar.set_postfix({'batch': f"{batch_idx + 1}/{n_batches}"})
                    except Exception as e:
                        self.logger.error(f"Error processing batch {batch_idx}: {str(e)}")

        # Aggregate results
        for result in all_results:
            for method_name in methods:
                method_result = result['method_results'].get(method_name)
                if method_result:
                    method_metrics = metrics[method_name]
                    method_metrics['ndcg'].append(method_result['ndcg'])
                    method_metrics['precision'].append(method_result['precision'])
                    method_metrics['recall'].append(method_result['precision'])
                    method_metrics['diversity'].append(method_result['diversity'])
                    method_metrics['coverage'].update(method_result['predicted_unis'])

        # Calculate final metrics
        train_universities = set(uni['name'] for uni in self.recommender.universities)
        evaluation_results = {}

        for method_name in methods:
            method_metrics = metrics[method_name]

            # Calculate personalization
            method_recommendations = [
                r['method_results'][method_name]['predicted_unis']
                for r in all_results
                if r['method_results'].get(method_name)
            ]
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
    evaluator = RecommenderEvaluator('../data/synthetic_data/synthetic_profiles.csv')

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
