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
            'ndcg': [],
            'precision': [],
            'recall': [],
            'diversity': [],
            'coverage': set(),
            'personalization': []
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
                hybrid_recs = self.recommender.get_hybrid_recommendations(user_dict, k)

                # Store recommendations for personalization calculation
                all_recommendations.append([rec['name'] for rec in hybrid_recs])

                # Update coverage
                metrics['coverage'].update([rec['name'] for rec in hybrid_recs])

                # Calculate relevance metrics
                actual_university = user['university']
                predicted_universities = [rec['name'] for rec in hybrid_recs]

                # NDCG calculation
                relevance = [1 if uni == actual_university else 0 for uni in predicted_universities]
                if sum(relevance) > 0:  # Only calculate if the actual university is in recommendations
                    metrics['ndcg'].append(self._calculate_ndcg(relevance))

                # Precision and Recall
                precision = 1 if actual_university in predicted_universities else 0
                metrics['precision'].append(precision)
                metrics['recall'].append(precision)  # For single ground truth, precision = recall

                # Calculate diversity of recommendations
                metrics['diversity'].append(self._calculate_diversity(hybrid_recs))

            except Exception as e:
                self.logger.warning(f"Error generating recommendations for user {idx}: {str(e)}")
                continue

        # Calculate personalization across all recommendations
        metrics['personalization'] = self._calculate_personalization(all_recommendations)

        # Calculate coverage percentage based on training universities
        coverage_percentage = len(metrics['coverage']) / len(train_universities) * 100

        # Aggregate metrics
        evaluation_results = {
            'ndcg@k': np.mean(metrics['ndcg']) if metrics['ndcg'] else 0,
            'precision@k': np.mean(metrics['precision']),
            'recall@k': np.mean(metrics['recall']),
            'diversity': np.mean(metrics['diversity']),
            'coverage_percentage': coverage_percentage,
            'personalization': metrics['personalization']
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
    print("\nRecommendation Metrics:")
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

    # Test cold-start scenarios
    sparse_profiles = [
        {'school': 'Engineering'},
        {'career_goal': 'Data Scientist'},
        {'personality': 'Extroverted', 'learning_style': 'hands-on'}
    ]

    cold_start_results = evaluator.evaluate_cold_start(sparse_profiles)
    print("\nCold-Start Evaluation:")
    for metric, value in cold_start_results.items():
        print(f"{metric}: {value:.4f}")


if __name__ == "__main__":
    main()
