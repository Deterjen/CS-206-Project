"""
University Recommendation Model Evaluation
=========================================
This script evaluates the performance of the university recommendation system
using leave-one-out cross-validation and relevance metrics.
"""

import json
import time
from typing import List, Dict

import numpy as np
import pandas as pd
from tqdm import tqdm

from university_recommender import UniversityRecommender


class RecommendationEvaluator:
    """Evaluates performance of university recommendation system."""

    def __init__(self, data_path: str = "analysis_ready_survey_data.csv", k_values: List[int] = [1, 3, 5, 10]):
        """Initialize the evaluation framework.

        Args:
            data_path: Path to the evaluation dataset
            k_values: List of k values for calculating Precision@k and Recall@k
        """
        self.data_path = data_path
        self.k_values = k_values
        self.data = pd.read_csv(data_path)
        self.recommender = UniversityRecommender(data_path)
        self.algorithms = ['profile', 'embedding', 'hybrid']

        # Ensure we have needed columns
        required_cols = ['university', 'satisfaction_rating']
        if not all(col in self.data.columns for col in required_cols):
            raise ValueError(f"Dataset must contain these columns: {required_cols}")

        # Preprocess data for evaluation
        self._preprocess_data()
        print(f"Loaded {len(self.data)} records for evaluation")

    def _preprocess_data(self):
        """Prepare data for evaluation."""
        # Drop records with missing university or satisfaction rating
        self.data = self.data.dropna(subset=['university', 'satisfaction_rating'])

        # Consider universities with 4+ rating as "relevant" for this user
        self.data['relevant'] = self.data['satisfaction_rating'] >= 4

        # Convert string lists to actual lists if needed
        list_columns = ['selection_criteria_list', 'cca_list']
        for col in list_columns:
            if col in self.data.columns:
                self.data[col] = self.data[col].apply(
                    lambda x: eval(x) if isinstance(x, str) else x)

    def _user_dict_from_row(self, row) -> Dict:
        """Convert a dataframe row to user dictionary format."""
        user_data = {}

        # Basic demographic information
        for col in ['age', 'gender', 'personality', 'student_status']:
            if col in row and pd.notna(row[col]):
                user_data[col] = row[col]

        # Academic information
        for col in ['learning_style', 'school', 'career_goal', 'plans_further_education']:
            if col in row and pd.notna(row[col]):
                user_data[col] = row[col]

        # Preferences
        for col in ['preferred_population', 'residence', 'cost_importance',
                    'culture_importance', 'internship_importance', 'ranking_influence',
                    'extracurricular_importance', 'family_influence', 'friend_influence',
                    'social_media_influence']:
            if col in row and pd.notna(row[col]):
                user_data[col] = row[col]

        # Engagement
        for col in ['leadership_role', 'extracurricular_hours',
                    'extracurricular_type', 'cca_count']:
            if col in row and pd.notna(row[col]):
                user_data[col] = row[col]

        # Lists
        if 'selection_criteria_list' in row and isinstance(row['selection_criteria_list'], list):
            user_data['selection_criteria'] = row['selection_criteria_list']
        else:
            user_data['selection_criteria'] = []

        if 'cca_list' in row and isinstance(row['cca_list'], list):
            user_data['ccas'] = row['cca_list']
        else:
            user_data['ccas'] = []

        # Make sure all expected fields are present
        if 'leadership_role' not in user_data:
            user_data['leadership_role'] = 0
        if 'extracurricular_hours' not in user_data:
            user_data['extracurricular_hours'] = 0

        return user_data

    def leave_one_out_evaluation(self, sample_size: int = None):
        """Evaluate using leave-one-out cross-validation.

        For each user, hide their university and try to predict it using their profile.

        Args:
            sample_size: Optional number of samples to use (for quicker testing)
        """
        # Use a subset of data if requested
        eval_data = self.data
        if sample_size and sample_size < len(self.data):
            eval_data = self.data.sample(sample_size, random_state=42)

        results = {
            'hit_ratio': {algo: [] for algo in self.algorithms},
            'precision_at_k': {algo: {k: [] for k in self.k_values} for algo in self.algorithms},
            'recall_at_k': {algo: {k: [] for k in self.k_values} for algo in self.algorithms},
            'ndcg_at_k': {algo: {k: [] for k in self.k_values} for algo in self.algorithms},
            'prediction_time': {algo: [] for algo in self.algorithms}
        }

        # Group by university to create ground truth for each user
        university_groups = eval_data.groupby('university')
        university_satisfaction = {}

        # Create university satisfaction lookup
        for uni, group in university_groups:
            university_satisfaction[uni] = group['satisfaction_rating'].mean()

        # For each user, evaluate recommendations
        for idx, row in tqdm(eval_data.iterrows(), total=len(eval_data), desc="Evaluating users"):
            # The target university (ground truth) for this user
            target_university = row['university']
            actual_satisfaction = row['satisfaction_rating']

            # Convert row to user dictionary, removing the university
            user_data = self._user_dict_from_row(row)

            # For each algorithm, generate recommendations and evaluate
            for algo in self.algorithms:
                start_time = time.time()

                # Get recommendations
                recommendations = self.recommender.recommend(
                    user_data=user_data,
                    algorithm=algo,
                    n=max(self.k_values)
                )

                prediction_time = time.time() - start_time
                results['prediction_time'][algo].append(prediction_time)

                # Check if the target university is in the recommendations
                hit = any(rec['name'] == target_university for rec in recommendations)
                results['hit_ratio'][algo].append(1 if hit else 0)

                # Calculate precision and recall at different k values
                for k in self.k_values:
                    if k <= len(recommendations):
                        top_k_recs = recommendations[:k]

                        # For precision@k and recall@k, we consider a university "relevant"
                        # if the user would rate it 4 or above (based on actual ratings)
                        relevant_recs = [rec for rec in top_k_recs
                                         if rec['name'] in university_satisfaction and
                                         university_satisfaction[rec['name']] >= 4]

        try:
            # Calculate precision@k
            precision = len(relevant_recs) / min(k, len(top_k_recs)) if top_k_recs else 0
            results['precision_at_k'][algo][k].append(precision)

            # Calculate recall@k (assuming there's only one relevant item per user in LOO CV)
            recall = 1 if target_university in [rec['name'] for rec in top_k_recs] else 0
            results['recall_at_k'][algo][k].append(recall)

            # Calculate NDCG@k
            ndcg = self._calculate_ndcg(
                recommendations=top_k_recs,
                target_university=target_university,
                actual_satisfaction=actual_satisfaction,
                university_satisfaction=university_satisfaction,
                k=k
            )
            results['ndcg_at_k'][algo][k].append(ndcg)
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            # Add default values on error
            results['precision_at_k'][algo][k].append(0)
            results['recall_at_k'][algo][k].append(0)
            results['ndcg_at_k'][algo][k].append(0)

        # Calculate average metrics
        summary = self._summarize_results(results)
        return results, summary

    def _calculate_ndcg(self, recommendations, target_university, actual_satisfaction,
                        university_satisfaction, k):
        """Calculate Normalized Discounted Cumulative Gain for recommendations."""
        # Ensure k doesn't exceed the number of recommendations
        k = min(k, len(recommendations))
        if k == 0:
            return 0

        # Create relevance scores for recommendations
        relevance = []
        for rec in recommendations[:k]:
            uni_name = rec['name']
            # If this is the target university, use actual satisfaction
            if uni_name == target_university:
                relevance.append(actual_satisfaction)
            # Otherwise use average satisfaction from other users if available
            elif uni_name in university_satisfaction:
                relevance.append(university_satisfaction[uni_name])
            # If no data, assume neutral satisfaction
            else:
                relevance.append(3)

        # Calculate DCG
        dcg = 0
        for i, rel in enumerate(relevance):
            # Normalize satisfaction score to 0-1 range (assuming 1-5 scale)
            normalized_rel = (rel - 1) / 4
            dcg += normalized_rel / np.log2(i + 2)  # +2 because i starts at 0

        # Calculate ideal DCG (perfect ranking)
        ideal_relevance = sorted(relevance, reverse=True)
        idcg = 0
        for i, rel in enumerate(ideal_relevance):
            normalized_rel = (rel - 1) / 4
            idcg += normalized_rel / np.log2(i + 2)

        # Avoid division by zero
        if idcg == 0:
            return 0

        return dcg / idcg

    def _summarize_results(self, results):
        """Summarize evaluation results."""
        summary = {}

        # Calculate average hit ratio
        summary['hit_ratio'] = {
            algo: np.mean(results['hit_ratio'][algo])
            for algo in self.algorithms
        }

        # Calculate average precision@k
        summary['precision_at_k'] = {
            algo: {
                k: np.mean(results['precision_at_k'][algo][k])
                for k in self.k_values
            }
            for algo in self.algorithms
        }

        # Calculate average recall@k
        summary['recall_at_k'] = {
            algo: {
                k: np.mean(results['recall_at_k'][algo][k])
                for k in self.k_values
            }
            for algo in self.algorithms
        }

        # Calculate average NDCG@k
        summary['ndcg_at_k'] = {
            algo: {
                k: np.mean(results['ndcg_at_k'][algo][k])
                for k in self.k_values
            }
            for algo in self.algorithms
        }

        # Calculate average prediction time
        summary['prediction_time'] = {
            algo: np.mean(results['prediction_time'][algo])
            for algo in self.algorithms
        }

        return summary

    def content_coverage_evaluation(self):
        """Evaluate content coverage - what percentage of universities get recommended."""
        # Get all universities in the dataset
        all_universities = set(self.data['university'].unique())
        total_universities = len(all_universities)

        # Sample users for evaluation
        sample_size = min(50, len(self.data))
        sample_users = self.data.sample(sample_size, random_state=42)

        coverage_results = {algo: set() for algo in self.algorithms}

        # For each sampled user, get recommendations using each algorithm
        for idx, row in tqdm(sample_users.iterrows(), total=len(sample_users),
                             desc="Evaluating coverage"):
            user_data = self._user_dict_from_row(row)

            for algo in self.algorithms:
                recommendations = self.recommender.recommend(
                    user_data=user_data,
                    algorithm=algo,
                    n=10  # Get top 10 recommendations
                )

                # Add recommended universities to the coverage set
                for rec in recommendations:
                    coverage_results[algo].add(rec['name'])

        # Calculate coverage percentage
        coverage_percentage = {
            algo: (len(universities) / total_universities) * 100
            for algo, universities in coverage_results.items()
        }

        # Get most and least recommended universities
        recommendation_counts = {uni: {algo: 0 for algo in self.algorithms}
                                 for uni in all_universities}

        for idx, row in tqdm(sample_users.iterrows(), total=len(sample_users),
                             desc="Counting recommendations"):
            user_data = self._user_dict_from_row(row)

            for algo in self.algorithms:
                recommendations = self.recommender.recommend(
                    user_data=user_data,
                    algorithm=algo,
                    n=5  # Top 5 for frequency analysis
                )

                for rec in recommendations:
                    if rec['name'] in recommendation_counts:
                        recommendation_counts[rec['name']][algo] += 1

        # Convert to dataframe for analysis
        rec_count_df = pd.DataFrame(
            [(uni, algo, count)
             for uni, algo_counts in recommendation_counts.items()
             for algo, count in algo_counts.items()],
            columns=['university', 'algorithm', 'count']
        )

        return {
            'coverage_percentage': coverage_percentage,
            'recommendation_counts': rec_count_df,
            'total_universities': total_universities
        }

    def user_segmentation_evaluation(self, segment_cols=None):
        """Evaluate recommendation performance across different user segments."""
        if segment_cols is None:
            segment_cols = ['age', 'gender', 'personality', 'learning_style']

        # Initialize results structure
        segment_results = {col: {} for col in segment_cols}

        # Sample size for quicker evaluation
        sample_size = min(100, len(self.data))
        sample_data = self.data.sample(sample_size, random_state=42)

        # For each segmentation column
        for col in segment_cols:
            if col not in sample_data.columns:
                continue

            # Group by segment
            segments = sample_data[col].unique()
            for segment in segments:
                segment_data = sample_data[sample_data[col] == segment]
                if len(segment_data) < 5:  # Skip very small segments
                    continue

                segment_hit_ratio = {algo: [] for algo in self.algorithms}
                segment_ndcg = {algo: [] for algo in self.algorithms}

                # Evaluate for each user in this segment
                for idx, row in segment_data.iterrows():
                    target_university = row['university']
                    user_data = self._user_dict_from_row(row)

                    for algo in self.algorithms:
                        recommendations = self.recommender.recommend(
                            user_data=user_data,
                            algorithm=algo,
                            n=5
                        )

                        # Check hit
                        hit = any(rec['name'] == target_university for rec in recommendations)
                        segment_hit_ratio[algo].append(1 if hit else 0)

                        # Calculate NDCG@5
                        ndcg = self._calculate_ndcg(
                            recommendations=recommendations,
                            target_university=target_university,
                            actual_satisfaction=row['satisfaction_rating'],
                            university_satisfaction={},  # Simplified for this analysis
                            k=5
                        )
                        segment_ndcg[algo].append(ndcg)

                # Calculate average metrics for this segment
                segment_results[col][segment] = {
                    'count': len(segment_data),
                    'hit_ratio': {algo: np.mean(vals) for algo, vals in segment_hit_ratio.items()},
                    'ndcg@5': {algo: np.mean(vals) for algo, vals in segment_ndcg.items()}
                }

        return segment_results

    def explanation_quality_evaluation(self, sample_size=20):
        """Evaluate the quality and relevance of recommendation explanations."""
        # Sample users for evaluation
        sample_users = self.data.sample(min(sample_size, len(self.data)), random_state=42)

        explanation_metrics = []

        for idx, row in tqdm(sample_users.iterrows(), total=len(sample_users),
                             desc="Evaluating explanations"):
            user_data = self._user_dict_from_row(row)

            # Get hybrid recommendations (which provide explanations)
            recommendations = self.recommender.get_hybrid_recommendations(user_data, n=3)

            if not recommendations:
                continue

            # For each recommendation, get and evaluate explanation
            for rec in recommendations:
                university_id = rec['university_id']
                explanation = self.recommender.explain_recommendation(user_data, university_id)

                # Skip if explanation failed
                if 'error' in explanation:
                    continue

                # Evaluate explanation quality
                metrics = {
                    'university': rec['name'],
                    'num_strengths': len(explanation['strengths']),
                    'num_considerations': len(explanation['considerations']),
                    'compatibility_score': explanation['compatibility']['overall'],
                    'semantic_similarity': explanation['semantic_similarity'],
                    'similar_students': explanation['similar_students'],
                    'has_learning_style_match': any('learning style' in s.lower() for s in explanation['strengths']),
                    'has_personality_match': any('personality' in s.lower() for s in explanation['strengths']),
                    'has_career_match': any('career' in s.lower() for s in explanation['strengths']),
                    'has_importance_alignment': any('alignment' in s.lower() for s in explanation['strengths'])
                }

                explanation_metrics.append(metrics)

        # Convert to dataframe for analysis
        explanation_df = pd.DataFrame(explanation_metrics)

        # Calculate summary statistics
        summary = {
            'avg_strengths_per_rec': explanation_df['num_strengths'].mean(),
            'avg_considerations_per_rec': explanation_df['num_considerations'].mean(),
            'avg_compatibility_score': explanation_df['compatibility_score'].mean(),
            'avg_semantic_similarity': explanation_df['semantic_similarity'].mean(),
            'avg_similar_students': explanation_df['similar_students'].mean(),
            'explanations_with_learning_style': explanation_df['has_learning_style_match'].mean() * 100,
            'explanations_with_personality': explanation_df['has_personality_match'].mean() * 100,
            'explanations_with_career': explanation_df['has_career_match'].mean() * 100,
            'explanations_with_importance_alignment': explanation_df['has_importance_alignment'].mean() * 100
        }

        return {
            'metrics': explanation_df,
            'summary': summary
        }

    def leave_fields_out_evaluation(self, sample_size=20, fields_to_test=None):
        """
        A simplified approach to evaluate recommendation performance with missing fields.

        This method tests how recommendations change when specific fields are removed,
        one at a time, allowing for easier debugging and analysis.

        Args:
            sample_size: Number of user profiles to test
            fields_to_test: Specific fields to test omitting (if None, uses default important fields)

        Returns:
            Dictionary with performance metrics for each field omission scenario
        """
        # Use a subset of data
        eval_data = self.data.sample(sample_size, random_state=42) if sample_size else self.data

        # Fields to test omitting (high-impact fields that might be missing in real scenarios)
        if fields_to_test is None:
            fields_to_test = [
                'personality',
                'learning_style',
                'career_goal',
                'culture_importance',
                'internship_importance',
                'extracurricular_hours',
                'ranking_influence'
            ]

        # Ensure all fields exist in the dataset
        fields_to_test = [f for f in fields_to_test if f in eval_data.columns]

        # Initialize results structure
        results = {
            'baseline': {algo: {'hit_ratio': [], 'ndcg_5': []} for algo in self.algorithms},
            'field_omissions': {
                field: {algo: {'hit_ratio': [], 'ndcg_5': []} for algo in self.algorithms}
                for field in fields_to_test
            }
        }

        # Group by university to create ground truth for satisfaction
        university_satisfaction = eval_data.groupby('university')['satisfaction_rating'].mean().to_dict()

        # For each user, evaluate recommendations with different field omissions
        for idx, row in tqdm(eval_data.iterrows(), total=len(eval_data),
                             desc="Evaluating field omissions"):
            # Get target university and actual satisfaction
            target_university = row['university']
            actual_satisfaction = row['satisfaction_rating']

            # First get baseline performance (all fields present except university)
            baseline_user = self._user_dict_from_row(row)

            for algo in self.algorithms:
                try:
                    # Get baseline recommendations
                    baseline_recs = self.recommender.recommend(
                        user_data=baseline_user,
                        algorithm=algo,
                        n=5  # Focus on top 5 recommendations
                    )

                    # Calculate baseline metrics
                    hit = any(rec['name'] == target_university for rec in baseline_recs)
                    results['baseline'][algo]['hit_ratio'].append(1 if hit else 0)

                    # Calculate NDCG@5
                    try:
                        ndcg = self._calculate_ndcg(
                            recommendations=baseline_recs,
                            target_university=target_university,
                            actual_satisfaction=actual_satisfaction,
                            university_satisfaction=university_satisfaction,
                            k=5
                        )
                        results['baseline'][algo]['ndcg_5'].append(ndcg)
                    except Exception as e:
                        print(f"Error calculating baseline NDCG: {e}")
                        results['baseline'][algo]['ndcg_5'].append(0)

                    # Now test each field omission
                    for field in fields_to_test:
                        # Create user data with this field omitted
                        test_user = baseline_user.copy()
                        if field in test_user:
                            test_user.pop(field)

                        try:
                            # Get recommendations with field omitted
                            test_recs = self.recommender.recommend(
                                user_data=test_user,
                                algorithm=algo,
                                n=5
                            )

                            # Calculate hit ratio
                            hit = any(rec['name'] == target_university for rec in test_recs)
                            results['field_omissions'][field][algo]['hit_ratio'].append(1 if hit else 0)

                            # Calculate NDCG@5
                            try:
                                ndcg = self._calculate_ndcg(
                                    recommendations=test_recs,
                                    target_university=target_university,
                                    actual_satisfaction=actual_satisfaction,
                                    university_satisfaction=university_satisfaction,
                                    k=5
                                )
                                results['field_omissions'][field][algo]['ndcg_5'].append(ndcg)
                            except Exception as e:
                                print(f"Error calculating NDCG for {field} omission: {e}")
                                results['field_omissions'][field][algo]['ndcg_5'].append(0)

                        except Exception as rec_error:
                            print(f"Error getting recommendations with {field} omitted: {rec_error}")
                            # Add zero values on error
                            results['field_omissions'][field][algo]['hit_ratio'].append(0)
                            results['field_omissions'][field][algo]['ndcg_5'].append(0)

                except Exception as algo_error:
                    print(f"Error processing algorithm {algo}: {algo_error}")
                    results['baseline'][algo]['hit_ratio'].append(0)
                    results['baseline'][algo]['ndcg_5'].append(0)

                    for field in fields_to_test:
                        results['field_omissions'][field][algo]['hit_ratio'].append(0)
                        results['field_omissions'][field][algo]['ndcg_5'].append(0)

        # Calculate summary metrics
        summary = self._summarize_field_omission_simplified(results, fields_to_test)

        return results, summary

    def _summarize_field_omission_simplified(self, results, fields_tested):
        """
        Calculate summary metrics from field omission evaluation results.

        Args:
            results: Raw evaluation results
            fields_tested: List of fields that were tested

        Returns:
            Dictionary of summary metrics
        """
        summary = {
            'performance_impact': {},
            'algorithm_robustness': {}
        }

        # Calculate average performance for baseline
        baseline_perf = {}
        for algo in self.algorithms:
            baseline_perf[algo] = {
                'hit_ratio': np.mean(results['baseline'][algo]['hit_ratio']),
                'ndcg_5': np.mean(results['baseline'][algo]['ndcg_5'])
            }

        # Calculate performance impact of each field omission
        field_impact = {}
        for field in fields_tested:
            field_impact[field] = {}

            for algo in self.algorithms:
                # Calculate average performance with this field omitted
                omission_hit_ratio = np.mean(results['field_omissions'][field][algo]['hit_ratio'])
                omission_ndcg = np.mean(results['field_omissions'][field][algo]['ndcg_5'])

                # Calculate drop in performance
                hit_ratio_drop = baseline_perf[algo]['hit_ratio'] - omission_hit_ratio
                ndcg_drop = baseline_perf[algo]['ndcg_5'] - omission_ndcg

                # Normalize drops as percentages
                hit_ratio_drop_pct = (hit_ratio_drop / baseline_perf[algo]['hit_ratio'] * 100) if baseline_perf[algo][
                                                                                                      'hit_ratio'] > 0 else 0
                ndcg_drop_pct = (ndcg_drop / baseline_perf[algo]['ndcg_5'] * 100) if baseline_perf[algo][
                                                                                         'ndcg_5'] > 0 else 0

                field_impact[field][algo] = {
                    'hit_ratio_drop': hit_ratio_drop,
                    'hit_ratio_drop_pct': hit_ratio_drop_pct,
                    'ndcg_drop': ndcg_drop,
                    'ndcg_drop_pct': ndcg_drop_pct,
                    'baseline_hit_ratio': baseline_perf[algo]['hit_ratio'],
                    'baseline_ndcg': baseline_perf[algo]['ndcg_5'],
                    'omission_hit_ratio': omission_hit_ratio,
                    'omission_ndcg': omission_ndcg
                }

        # Calculate average impact across algorithms
        for field in fields_tested:
            avg_ndcg_drop = np.mean([field_impact[field][algo]['ndcg_drop'] for algo in self.algorithms])
            avg_ndcg_drop_pct = np.mean([field_impact[field][algo]['ndcg_drop_pct'] for algo in self.algorithms])

            field_impact[field]['average'] = {
                'ndcg_drop': avg_ndcg_drop,
                'ndcg_drop_pct': avg_ndcg_drop_pct
            }

        # Sort fields by impact
        sorted_fields = sorted(
            fields_tested,
            key=lambda f: field_impact[f]['average']['ndcg_drop'],
            reverse=True
        )

        # Calculate algorithm robustness (which algorithm is least affected by missing fields)
        algo_robustness = {}
        for algo in self.algorithms:
            # Average impact across all fields
            avg_ndcg_drop_pct = np.mean([field_impact[field][algo]['ndcg_drop_pct']
                                         for field in fields_tested])

            # Maximum impact from any single field
            max_field_impact = max([field_impact[field][algo]['ndcg_drop_pct']
                                    for field in fields_tested])

            # Robustness score (lower drop = higher robustness)
            robustness_score = 100 - avg_ndcg_drop_pct

            algo_robustness[algo] = {
                'avg_performance_drop_pct': avg_ndcg_drop_pct,
                'max_field_impact_pct': max_field_impact,
                'robustness_score': robustness_score
            }

        # Compile final summary
        summary['performance_impact'] = {
            'sorted_by_impact': sorted_fields,
            'field_impact': field_impact
        }
        summary['algorithm_robustness'] = algo_robustness

        return summary

    def run_comprehensive_evaluation(self, sample_size=50):
        """Run a comprehensive evaluation of the recommendation system."""
        print("Starting comprehensive evaluation...")
        results = {}

        # 1. Leave-one-out evaluation
        print("\n1. Running leave-one-out evaluation...")
        loo_results, loo_summary = self.leave_one_out_evaluation(sample_size=sample_size)
        results['leave_one_out'] = loo_summary

        # 2. Content coverage evaluation
        print("\n2. Evaluating content coverage...")
        coverage_results = self.content_coverage_evaluation()
        results['coverage'] = coverage_results

        # 3. User segmentation evaluation
        print("\n3. Evaluating performance across user segments...")
        segment_results = self.user_segmentation_evaluation()
        results['segmentation'] = segment_results

        # 4. Explanation quality evaluation
        print("\n4. Evaluating explanation quality...")
        explanation_results = self.explanation_quality_evaluation(sample_size=min(20, sample_size))
        results['explanation'] = explanation_results['summary']

        # Generate evaluation report
        self.generate_evaluation_report(results)

        return results

    def generate_evaluation_report(self, results):
        """Generate a comprehensive evaluation report."""
        print("\n" + "=" * 50)
        print("UNIVERSITY RECOMMENDATION SYSTEM EVALUATION REPORT")
        print("=" * 50)

        # 1. Overall Performance
        print("\n1. OVERALL PERFORMANCE")
        print("---------------------")
        loo = results['leave_one_out']

        print("\nHit Ratio (ability to recommend the user's actual university):")
        for algo, ratio in loo['hit_ratio'].items():
            print(f"  {algo.capitalize()}: {ratio:.2%}")

        print("\nNDCG@5 (ranking quality, higher is better):")
        for algo, scores in loo['ndcg_at_k'].items():
            print(f"  {algo.capitalize()}: {scores[5]:.4f}")

        print("\nPrediction Time (seconds):")
        for algo, time in loo['prediction_time'].items():
            print(f"  {algo.capitalize()}: {time:.4f}s")

        # 2. Coverage Analysis
        print("\n2. COVERAGE ANALYSIS")
        print("-------------------")
        coverage = results['coverage']

        print(f"\nTotal universities in dataset: {coverage['total_universities']}")
        print("\nPercentage of universities recommended:")
        for algo, percentage in coverage['coverage_percentage'].items():
            print(f"  {algo.capitalize()}: {percentage:.1f}%")

        # 3. Performance by User Segment
        print("\n3. PERFORMANCE BY USER SEGMENT")
        print("-----------------------------")
        segments = results['segmentation']

        for segment_type, segment_data in segments.items():
            print(f"\n{segment_type.capitalize()} Segments:")
            for segment, metrics in segment_data.items():
                print(f"  {segment} (n={metrics['count']}):")
                best_algo = max(metrics['hit_ratio'].items(), key=lambda x: x[1])[0]
                print(f"    Best algorithm: {best_algo.capitalize()}")
                print(f"    Hit ratio: {metrics['hit_ratio'][best_algo]:.2%}")
                print(f"    NDCG@5: {metrics['ndcg@5'][best_algo]:.4f}")

        # 4. Explanation Quality
        print("\n4. EXPLANATION QUALITY")
        print("---------------------")
        explanation = results['explanation']

        print(f"\nAverage strengths per recommendation: {explanation['avg_strengths_per_rec']:.2f}")
        print(f"Average considerations per recommendation: {explanation['avg_considerations_per_rec']:.2f}")
        print(f"Average compatibility score: {explanation['avg_compatibility_score']:.2f}")
        print(f"Average semantic similarity: {explanation['avg_semantic_similarity']:.2f}")

        print("\nExplanation content breakdown:")
        print(f"  Learning style matches: {explanation['explanations_with_learning_style']:.1f}%")
        print(f"  Personality matches: {explanation['explanations_with_personality']:.1f}%")
        print(f"  Career goal matches: {explanation['explanations_with_career']:.1f}%")
        print(f"  Importance alignment: {explanation['explanations_with_importance_alignment']:.1f}%")

        # 5. Algorithm Comparison Summary
        print("\n5. ALGORITHM COMPARISON SUMMARY")
        print("------------------------------")

        # Determine best algorithm for different metrics
        best_hit_ratio = max(loo['hit_ratio'].items(), key=lambda x: x[1])[0]
        best_precision = max([(algo, scores[5]) for algo, scores in loo['precision_at_k'].items()],
                             key=lambda x: x[1])[0]
        best_recall = max([(algo, scores[5]) for algo, scores in loo['recall_at_k'].items()],
                          key=lambda x: x[1])[0]
        best_ndcg = max([(algo, scores[5]) for algo, scores in loo['ndcg_at_k'].items()],
                        key=lambda x: x[1])[0]
        fastest = min(loo['prediction_time'].items(), key=lambda x: x[1])[0]
        best_coverage = max(coverage['coverage_percentage'].items(), key=lambda x: x[1])[0]

        print("\nBest algorithm by metric:")
        print(f"  Hit Ratio: {best_hit_ratio.capitalize()}")
        print(f"  Precision@5: {best_precision.capitalize()}")
        print(f"  Recall@5: {best_recall.capitalize()}")
        print(f"  NDCG@5: {best_ndcg.capitalize()}")
        print(f"  Speed: {fastest.capitalize()}")
        print(f"  Coverage: {best_coverage.capitalize()}")

        # Overall recommendation
        print("\nOVERALL RECOMMENDATION:")
        algorithms = list(loo['hit_ratio'].keys())
        scores = {}

        for algo in algorithms:
            # Normalize scores between 0-1 where higher is better
            hit_ratio_norm = loo['hit_ratio'][algo] / max(loo['hit_ratio'].values())
            ndcg_norm = loo['ndcg_at_k'][algo][5] / max([scores[5] for scores in loo['ndcg_at_k'].values()])
            coverage_norm = coverage['coverage_percentage'][algo] / max(coverage['coverage_percentage'].values())
            speed_norm = min(loo['prediction_time'].values()) / loo['prediction_time'][
                algo]  # Invert so faster is better

            # Calculate weighted score (can adjust weights as needed)
            scores[algo] = (hit_ratio_norm * 0.3 +
                            ndcg_norm * 0.3 +
                            coverage_norm * 0.2 +
                            speed_norm * 0.2)

        best_overall = max(scores.items(), key=lambda x: x[1])[0]
        print(f"Based on overall evaluation, the recommended algorithm is: {best_overall.capitalize()}")

        # Final recommendation
        print("\nRECOMMENDATION FOR DEPLOYMENT:")
        if best_overall == 'hybrid':
            print("The hybrid approach provides the best balance of accuracy and coverage.")
        elif best_overall == 'profile':
            print("The profile-based approach provides the best performance, especially for new users.")
        else:
            print("The embedding-based approach provides the best semantic understanding of user preferences.")

        print("\nNOTES:")
        if loo['prediction_time']['hybrid'] > 0.5:
            print("- Consider optimizing the hybrid approach for faster predictions")
        if min(coverage['coverage_percentage'].values()) < 50:
            print("- Some universities are rarely recommended - consider addressing coverage issues")

        print("\n" + "=" * 50)


def main():
    """Run evaluation script."""
    print("University Recommendation System Evaluation")
    print("==========================================")

    evaluator = RecommendationEvaluator("./data/analysis_ready_survey_data.csv")

    # Run quick evaluation with small sample size
    results = evaluator.run_comprehensive_evaluation(sample_size=30)

    # Save results to file
    with open('evaluation_results.json', 'w') as f:
        json.dump({
            'leave_one_out': {
                k: {algo: float(v) if isinstance(v, (np.float64, np.float32))
                else {k2: float(v2) for k2, v2 in v.items()} if isinstance(v, dict) else v
                    for algo, v in d.items()}
                for k, d in results['leave_one_out'].items()
            },
            'coverage': {
                'coverage_percentage': {k: float(v) for k, v in results['coverage']['coverage_percentage'].items()},
                'total_universities': results['coverage']['total_universities']
            },
            'explanation': {k: float(v) for k, v in results['explanation'].items()}
        }, f, indent=2)

    print("\nEvaluation complete. Results saved to evaluation_results.json")


if __name__ == "__main__":
    main()
