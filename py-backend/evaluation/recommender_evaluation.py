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

    def evaluate_recommendations(self, test_data: pd.DataFrame, k: int = 5, batch_size: int = 32) -> Dict:
        """
        Evaluate recommendations using various metrics

        Args:
            test_data: Test dataset
            k: Number of recommendations to generate
            batch_size: Size of batches for embedding generation
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
        all_recommendations = {method: [] for method in ['profile_based', 'embedding', 'hybrid']}

        # Process test data in batches
        for start_idx in range(0, len(test_data), batch_size):
            batch_data = test_data.iloc[start_idx:start_idx + batch_size]

            # Convert batch to list of user dictionaries
            user_dicts = [user.drop('university').to_dict() for _, user in batch_data.iterrows()]
            actual_universities = batch_data['university'].tolist()

            try:
                # Get recommendations for each method
                profile_recs = [self.recommender.get_profile_based_recommendations(user, k)
                                for user in user_dicts]
                embedding_recs = self.recommender.get_embedding_recommendations_batch(user_dicts, k)
                hybrid_recs = self.recommender.get_hybrid_recommendations_batch(user_dicts, k)

                # Process metrics for each user in the batch
                for idx, actual_uni in enumerate(actual_universities):
                    for method_name, recs in [
                        ('profile_based', profile_recs[idx]),
                        ('embedding', embedding_recs[idx]),
                        ('hybrid', hybrid_recs[idx])
                    ]:
                        if not recs:  # Skip if no recommendations
                            continue

                        # Store recommendations for personalization calculation
                        all_recommendations[method_name].append([rec['name'] for rec in recs])

                        # Update coverage
                        metrics[method_name]['coverage'].update([rec['name'] for rec in recs])

                        # Calculate relevance metrics
                        predicted_universities = [rec['name'] for rec in recs]

                        # NDCG calculation
                        relevance = [1 if uni == actual_uni else 0 for uni in predicted_universities]
                        if sum(relevance) > 0:
                            metrics[method_name]['ndcg'].append(self._calculate_ndcg(relevance))

                        # Precision and Recall
                        precision = 1 if actual_uni in predicted_universities else 0
                        metrics[method_name]['precision'].append(precision)
                        metrics[method_name]['recall'].append(precision)

                        # Calculate diversity of recommendations
                        metrics[method_name]['diversity'].append(self._calculate_diversity(recs))

            except Exception as e:
                self.logger.warning(f"Error processing batch starting at index {start_idx}: {str(e)}")
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

    def perform_scenario_testing(self, scenarios: List[Dict]) -> Dict:
        """
        Test specific scenarios to evaluate recommender behavior

        Args:
            scenarios: List of test scenarios with expected outcomes

        Returns:
            Dictionary containing scenario test results
        """
        if self.recommender is None:
            raise ValueError("Recommender not initialized. Run prepare_train_test_split first.")

        results = {}

        for i, scenario in enumerate(scenarios):
            scenario_name = scenario.get('name', f'Scenario {i + 1}')
            user_profile = scenario['profile']
            expected_traits = scenario.get('expected_traits', [])

            # Get recommendations
            try:
                recommendations = self.recommender.get_hybrid_recommendations(user_profile)

                # Check if recommendations match expected traits
                matches = []
                for trait in expected_traits:
                    trait_found = any(
                        trait.lower() in rec['description'].lower()
                        for rec in recommendations
                    )
                    matches.append(trait_found)

                results[scenario_name] = {
                    'success_rate': sum(matches) / len(matches) if matches else 0,
                    'recommendations': [rec['name'] for rec in recommendations],
                    'matched_traits': [trait for trait, match in zip(expected_traits, matches) if match]
                }
            except Exception as e:
                self.logger.warning(f"Error in scenario {scenario_name}: {str(e)}")
                results[scenario_name] = {
                    'error': str(e),
                    'success_rate': 0,
                    'recommendations': [],
                    'matched_traits': []
                }

        return results

    def evaluate_cold_start(self, sparse_profiles: List[Dict]) -> Dict:
        """
        Evaluate recommender performance on cold-start scenarios

        Args:
            sparse_profiles: List of user profiles with minimal information

        Returns:
            Dictionary containing cold-start evaluation metrics
        """
        if self.recommender is None:
            raise ValueError("Recommender not initialized. Run prepare_train_test_split first.")

        results = {
            'coverage': [],
            'diversity': [],
            'confidence_scores': []
        }

        for profile in sparse_profiles:
            try:
                recommendations = self.recommender.get_hybrid_recommendations(profile)

                # Calculate metrics
                results['coverage'].append(len(recommendations))
                results['diversity'].append(self._calculate_diversity(recommendations))
                results['confidence_scores'].append(
                    [rec.get('match_confidence', 0) for rec in recommendations]
                )
            except Exception as e:
                self.logger.warning(f"Error in cold start evaluation: {str(e)}")
                continue

        # Aggregate results
        return {
            'avg_coverage': np.mean(results['coverage']) if results['coverage'] else 0,
            'avg_diversity': np.mean(results['diversity']) if results['diversity'] else 0,
            'avg_confidence': np.mean([np.mean(scores) for scores in results['confidence_scores']]) if results[
                'confidence_scores'] else 0
        }


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

    # Test specific scenarios
    scenarios = [
        {
            'name': 'Engineering Student',
            'profile': {
                'school': 'Engineering',
                'learning_style': 'hands-on',
                'career_goal': 'Software Engineer',
                'personality': 'Introverted'
            },
            'expected_traits': ['technical', 'engineering', 'practical']
        },
        {
            'name': 'Business Leader',
            'profile': {
                'school': 'Business',
                'personality': 'Extroverted',
                'leadership_role': 1,
                'career_goal': 'Entrepreneur'
            },
            'expected_traits': ['business', 'leadership', 'entrepreneurship']
        }
    ]

    scenario_results = evaluator.perform_scenario_testing(scenarios)
    print("\nScenario Testing Results:")
    for scenario, results in scenario_results.items():
        print(f"\n{scenario}:")
        print(f"Success Rate: {results['success_rate']:.2f}")
        print(f"Matched Traits: {', '.join(results['matched_traits'])}")


if __name__ == "__main__":
    main()
