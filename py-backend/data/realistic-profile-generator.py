import random
from collections import Counter
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


@dataclass
class StudentProfile:
    # Core demographic fields
    age: str
    gender: str
    student_status: str
    university: str

    # Academic fields
    satisfaction_rating: int
    learning_style: str
    preferred_population: str
    school: str
    plans_further_education: float
    career_goal: str

    # Importance ratings
    cost_importance: int
    culture_importance: int
    internship_importance: int
    ranking_influence: int
    extracurricular_importance: int
    family_influence: int
    friend_influence: int
    social_media_influence: int
    scholarship_significance: int

    # Financial fields
    has_scholarship: int
    funding_source: str
    financial_consideration: float

    # Location/Housing
    residence: str

    # Engagement/Activities
    personality: str
    leadership_role: int
    extracurricular_hours: int
    extracurricular_type: str
    cca_count: int
    engagement_level: int
    engagement_category: str

    # Participation
    internship_participation: int

    # External influence
    external_influence: float

    # Lists
    selection_criteria_list: str
    cca_list: str

    # Derived categorization
    satisfaction_group: str


class UniversityProfileGenerator:
    def __init__(self):
        self.setup_university_profiles()

    def setup_university_profiles(self):
        """Set up comprehensive profile weights for each university"""

        self.UNIVERSITY_PROFILES = {
            'NUS': {
                # Demographic tendencies
                'age_weights': {'Under 18': 0.05, '18 - 24': 0.8, '25 - 30': 0.1, 'Over 30': 0.05},
                'gender_weights': {'Male': 0.48, 'Female': 0.48, 'Non-binary': 0.02, 'Prefer not to say': 0.02},
                'student_status_weights': {'Domestic': 0.6, 'International': 0.4},

                # Academic characteristics
                'satisfaction_base': 4.2,
                'learning_style_weights': {
                    'Hands-on/Practical': 0.2,
                    'Visual': 0.2,
                    'Auditory': 0.1,
                    'Theoretical': 0.3,
                    'Group-based': 0.1,
                    'Self-paced/Individual': 0.1
                },
                'preferred_population': 'Large',
                'school_weights': {
                    'Computing': 0.25,
                    'Engineering': 0.25,
                    'Sciences': 0.2,
                    'Business': 0.1,
                    'Medicine': 0.1,
                    'Arts': 0.05,
                    'Social Sciences': 0.05
                },
                'further_education_weights': {1: 0.6, 0.5: 0.3, 0: 0.1},  # High research focus
                'career_goal_weights': {
                    'Software Engineer': 0.3,
                    'Data Scientist': 0.2,
                    'Researcher': 0.2,
                    'Product Manager': 0.1,
                    'Business Analyst': 0.1,
                    'Consultant': 0.05,
                    'Entrepreneur': 0.05
                },

                # Importance ratings baselines (out of 10)
                'importance_baselines': {
                    'cost': 7,
                    'culture': 8,
                    'internship': 8,
                    'ranking': 9,
                    'extracurricular': 7,
                    'family': 7,
                    'friend': 6,
                    'social_media': 5,
                    'scholarship': 8
                },

                # Financial characteristics
                'scholarship_rate': 0.4,
                'funding_source_weights': {
                    'Scholarship': 0.4,
                    'Family': 0.3,
                    'Loan': 0.2,
                    'Self-funded': 0.1
                },

                # Residence preferences
                'residence_weights': {
                    'On campus': 0.4,
                    'Off campus': 0.3,
                    'Commute': 0.3
                },

                # Engagement characteristics
                'personality_weights': {
                    'Extroverted': 0.4,
                    'Introverted': 0.3,
                    'Ambivert': 0.3
                },
                'leadership_rate': 0.4,
                'extracurricular_hours_base': 15,
                'extracurricular_type_weights': {
                    'Academic': 0.3,
                    'Professional': 0.3,
                    'Sports': 0.15,
                    'Arts': 0.1,
                    'Community': 0.1,
                    'Social': 0.05
                },
                'cca_count_base': 3,

                # Participation rates
                'internship_rate': 0.85,

                # Common selection criteria
                'selection_criteria_weights': {
                    'Academic Reputation': 0.2,
                    'Research Opportunities': 0.15,
                    'Global Recognition': 0.15,
                    'Industry Connections': 0.1,
                    'Career Services': 0.1,
                    'Faculty Quality': 0.1,
                    'Scholarship Opportunities': 0.1,
                    'International Exposure': 0.1
                },

                # Common CCAs
                'cca_weights': {
                    'Academic Society': 0.25,
                    'Research Group': 0.2,
                    'Professional Club': 0.2,
                    'Sports Club': 0.15,
                    'Cultural Club': 0.1,
                    'Social Club': 0.1
                }
            },

            'NTU': {
                # Similar structure with different weights...
                'age_weights': {'Under 18': 0.05, '18 - 24': 0.75, '25 - 30': 0.15, 'Over 30': 0.05},
                'gender_weights': {'Male': 0.5, 'Female': 0.45, 'Non-binary': 0.03, 'Prefer not to say': 0.02},
                'student_status_weights': {'Domestic': 0.65, 'International': 0.35},

                'satisfaction_base': 4.1,
                'learning_style_weights': {
                    'Hands-on/Practical': 0.3,
                    'Visual': 0.2,
                    'Auditory': 0.1,
                    'Theoretical': 0.2,
                    'Group-based': 0.1,
                    'Self-paced/Individual': 0.1
                },
                'preferred_population': 'Large',
                'school_weights': {
                    'Engineering': 0.3,
                    'Sciences': 0.2,
                    'Computing': 0.2,
                    'Business': 0.15,
                    'Arts': 0.1,
                    'Social Sciences': 0.05
                },
                'further_education_weights': {1: 0.5, 0.5: 0.3, 0: 0.2},
                'career_goal_weights': {
                    'Software Engineer': 0.25,
                    'Engineer': 0.25,
                    'Researcher': 0.15,
                    'Data Scientist': 0.15,
                    'Product Manager': 0.1,
                    'Business Analyst': 0.1
                },

                'importance_baselines': {
                    'cost': 7,
                    'culture': 7,
                    'internship': 8,
                    'ranking': 8,
                    'extracurricular': 7,
                    'family': 6,
                    'friend': 6,
                    'social_media': 5,
                    'scholarship': 7
                },

                'scholarship_rate': 0.35,
                'funding_source_weights': {
                    'Scholarship': 0.35,
                    'Family': 0.35,
                    'Loan': 0.2,
                    'Self-funded': 0.1
                },

                'residence_weights': {
                    'On campus': 0.45,
                    'Off campus': 0.25,
                    'Commute': 0.3
                },

                'personality_weights': {
                    'Extroverted': 0.35,
                    'Introverted': 0.35,
                    'Ambivert': 0.3
                },
                'leadership_rate': 0.35,
                'extracurricular_hours_base': 14,
                'extracurricular_type_weights': {
                    'Academic': 0.25,
                    'Professional': 0.25,
                    'Sports': 0.2,
                    'Arts': 0.15,
                    'Community': 0.1,
                    'Social': 0.05
                },
                'cca_count_base': 3,

                'internship_rate': 0.8,

                'selection_criteria_weights': {
                    'Academic Reputation': 0.15,
                    'Research Opportunities': 0.15,
                    'Industry Connections': 0.15,
                    'Campus Facilities': 0.15,
                    'Career Services': 0.1,
                    'Faculty Quality': 0.1,
                    'International Exposure': 0.1,
                    'Location': 0.1
                },

                'cca_weights': {
                    'Academic Society': 0.2,
                    'Sports Club': 0.2,
                    'Professional Club': 0.2,
                    'Research Group': 0.15,
                    'Cultural Club': 0.15,
                    'Social Club': 0.1
                }
            },

            'SMU': {
                # Distinctive business/professional focus...
                'age_weights': {'Under 18': 0.05, '18 - 24': 0.8, '25 - 30': 0.1, 'Over 30': 0.05},
                'gender_weights': {'Male': 0.45, 'Female': 0.5, 'Non-binary': 0.03, 'Prefer not to say': 0.02},
                'student_status_weights': {'Domestic': 0.7, 'International': 0.3},

                'satisfaction_base': 4.0,
                'learning_style_weights': {
                    'Group-based': 0.3,
                    'Hands-on/Practical': 0.2,
                    'Visual': 0.2,
                    'Theoretical': 0.1,
                    'Auditory': 0.1,
                    'Self-paced/Individual': 0.1
                },
                'preferred_population': 'Medium',
                'school_weights': {
                    'Business': 0.4,
                    'Computing': 0.2,
                    'Social Sciences': 0.2,
                    'Law': 0.2
                },
                'further_education_weights': {1: 0.3, 0.5: 0.4, 0: 0.3},
                'career_goal_weights': {
                    'Business Analyst': 0.25,
                    'Consultant': 0.25,
                    'Entrepreneur': 0.2,
                    'Product Manager': 0.15,
                    'Data Scientist': 0.15
                },

                'importance_baselines': {
                    'cost': 8,
                    'culture': 9,
                    'internship': 9,
                    'ranking': 8,
                    'extracurricular': 8,
                    'family': 7,
                    'friend': 7,
                    'social_media': 6,
                    'scholarship': 7
                },

                'scholarship_rate': 0.3,
                'funding_source_weights': {
                    'Family': 0.4,
                    'Scholarship': 0.3,
                    'Loan': 0.2,
                    'Self-funded': 0.1
                },

                'residence_weights': {
                    'Commute': 0.5,
                    'Off campus': 0.3,
                    'On campus': 0.2
                },

                'personality_weights': {
                    'Extroverted': 0.5,
                    'Ambivert': 0.3,
                    'Introverted': 0.2
                },
                'leadership_rate': 0.5,
                'extracurricular_hours_base': 16,
                'extracurricular_type_weights': {
                    'Professional': 0.4,
                    'Social': 0.2,
                    'Community': 0.2,
                    'Sports': 0.1,
                    'Arts': 0.1
                },
                'cca_count_base': 4,

                'internship_rate': 0.9,

                'selection_criteria_weights': {
                    'Industry Connections': 0.2,
                    'Career Services': 0.2,
                    'Academic Reputation': 0.15,
                    'Location': 0.15,
                    'Campus Culture': 0.1,
                    'International Exposure': 0.1,
                    'Alumni Network': 0.1
                },

                'cca_weights': {
                    'Professional Club': 0.3,
                    'Business Society': 0.25,
                    'Community Service': 0.15,
                    'Sports Club': 0.15,
                    'Social Club': 0.15
                }
            },
            'SUTD': {
                'age_weights': {'Under 18': 0.05, '18 - 24': 0.85, '25 - 30': 0.08, 'Over 30': 0.02},
                'gender_weights': {'Male': 0.55, 'Female': 0.4, 'Non-binary': 0.03, 'Prefer not to say': 0.02},
                'student_status_weights': {'Domestic': 0.75, 'International': 0.25},

                'satisfaction_base': 3.9,
                'learning_style_weights': {
                    'Hands-on/Practical': 0.4,
                    'Visual': 0.2,
                    'Group-based': 0.2,
                    'Theoretical': 0.1,
                    'Self-paced/Individual': 0.05,
                    'Auditory': 0.05
                },
                'preferred_population': 'Small',
                'school_weights': {
                    'Engineering': 0.4,
                    'Computing': 0.3,
                    'Arts': 0.3
                },
                'further_education_weights': {1: 0.4, 0.5: 0.4, 0: 0.2},
                'career_goal_weights': {
                    'Software Engineer': 0.3,
                    'Product Manager': 0.2,
                    'Engineer': 0.2,
                    'Design Engineer': 0.2,
                    'Entrepreneur': 0.1
                },

                'importance_baselines': {
                    'cost': 7,
                    'culture': 8,
                    'internship': 8,
                    'ranking': 7,
                    'extracurricular': 8,
                    'family': 6,
                    'friend': 6,
                    'social_media': 5,
                    'scholarship': 7
                },

                'scholarship_rate': 0.4,
                'funding_source_weights': {
                    'Scholarship': 0.4,
                    'Family': 0.3,
                    'Loan': 0.2,
                    'Self-funded': 0.1
                },

                'residence_weights': {
                    'On campus': 0.6,
                    'Off campus': 0.2,
                    'Commute': 0.2
                },

                'personality_weights': {
                    'Extroverted': 0.4,
                    'Introverted': 0.3,
                    'Ambivert': 0.3
                },
                'leadership_rate': 0.4,
                'extracurricular_hours_base': 15,
                'extracurricular_type_weights': {
                    'Professional': 0.3,
                    'Arts': 0.3,
                    'Academic': 0.2,
                    'Sports': 0.1,
                    'Community': 0.1
                },
                'cca_count_base': 3,

                'internship_rate': 0.8,

                'selection_criteria_weights': {
                    'Innovation Culture': 0.2,
                    'Hands-on Learning': 0.2,
                    'Industry Connections': 0.15,
                    'Technology Focus': 0.15,
                    'Small Class Size': 0.1,
                    'Research Opportunities': 0.1,
                    'Campus Facilities': 0.1
                },

                'cca_weights': {
                    'Technology Club': 0.3,
                    'Design Club': 0.2,
                    'Innovation Lab': 0.2,
                    'Sports Club': 0.15,
                    'Arts Group': 0.15
                }
            },

            'SIT': {
                'age_weights': {'Under 18': 0.02, '18 - 24': 0.7, '25 - 30': 0.2, 'Over 30': 0.08},
                'gender_weights': {'Male': 0.5, 'Female': 0.45, 'Non-binary': 0.03, 'Prefer not to say': 0.02},
                'student_status_weights': {'Domestic': 0.85, 'International': 0.15},

                'satisfaction_base': 3.8,
                'learning_style_weights': {
                    'Hands-on/Practical': 0.5,
                    'Group-based': 0.2,
                    'Visual': 0.15,
                    'Self-paced/Individual': 0.1,
                    'Theoretical': 0.03,
                    'Auditory': 0.02
                },
                'preferred_population': 'Medium',
                'school_weights': {
                    'Engineering': 0.35,
                    'Computing': 0.35,
                    'Sciences': 0.3
                },
                'further_education_weights': {1: 0.2, 0.5: 0.3, 0: 0.5},
                'career_goal_weights': {
                    'Software Engineer': 0.3,
                    'Engineer': 0.3,
                    'Data Scientist': 0.2,
                    'Product Manager': 0.1,
                    'Entrepreneur': 0.1
                },

                'importance_baselines': {
                    'cost': 8,
                    'culture': 7,
                    'internship': 9,
                    'ranking': 6,
                    'extracurricular': 6,
                    'family': 7,
                    'friend': 6,
                    'social_media': 4,
                    'scholarship': 8
                },

                'scholarship_rate': 0.25,
                'funding_source_weights': {
                    'Family': 0.4,
                    'Loan': 0.3,
                    'Scholarship': 0.2,
                    'Self-funded': 0.1
                },

                'residence_weights': {
                    'Commute': 0.6,
                    'Off campus': 0.3,
                    'On campus': 0.1
                },

                'personality_weights': {
                    'Introverted': 0.4,
                    'Ambivert': 0.35,
                    'Extroverted': 0.25
                },
                'leadership_rate': 0.3,
                'extracurricular_hours_base': 12,
                'extracurricular_type_weights': {
                    'Professional': 0.4,
                    'Academic': 0.3,
                    'Community': 0.15,
                    'Sports': 0.1,
                    'Arts': 0.05
                },
                'cca_count_base': 2,

                'internship_rate': 0.9,

                'selection_criteria_weights': {
                    'Industry Experience': 0.25,
                    'Practical Skills': 0.2,
                    'Internship Opportunities': 0.15,
                    'Affordability': 0.15,
                    'Job Prospects': 0.15,
                    'Location': 0.1
                },

                'cca_weights': {
                    'Professional Society': 0.3,
                    'Industry Project': 0.25,
                    'Technical Club': 0.2,
                    'Sports Club': 0.15,
                    'Community Service': 0.1
                }
            },

            'SUSS': {
                'age_weights': {'Under 18': 0.01, '18 - 24': 0.5, '25 - 30': 0.3, 'Over 30': 0.19},
                'gender_weights': {'Male': 0.4, 'Female': 0.55, 'Non-binary': 0.03, 'Prefer not to say': 0.02},
                'student_status_weights': {'Domestic': 0.9, 'International': 0.1},

                'satisfaction_base': 3.7,
                'learning_style_weights': {
                    'Self-paced/Individual': 0.3,
                    'Hands-on/Practical': 0.25,
                    'Visual': 0.2,
                    'Group-based': 0.15,
                    'Auditory': 0.05,
                    'Theoretical': 0.05
                },
                'preferred_population': 'Medium',
                'school_weights': {
                    'Business': 0.3,
                    'Social Sciences': 0.4,
                    'Education': 0.3
                },
                'further_education_weights': {1: 0.2, 0.5: 0.3, 0: 0.5},
                'career_goal_weights': {
                    'Business Analyst': 0.25,
                    'Social Worker': 0.25,
                    'Educator': 0.25,
                    'Counselor': 0.15,
                    'Entrepreneur': 0.1
                },

                'importance_baselines': {
                    'cost': 9,
                    'culture': 6,
                    'internship': 7,
                    'ranking': 5,
                    'extracurricular': 5,
                    'family': 8,
                    'friend': 6,
                    'social_media': 4,
                    'scholarship': 8
                },

                'scholarship_rate': 0.2,
                'funding_source_weights': {
                    'Self-funded': 0.4,
                    'Family': 0.3,
                    'Loan': 0.2,
                    'Scholarship': 0.1
                },

                'residence_weights': {
                    'Commute': 0.8,
                    'Off campus': 0.15,
                    'On campus': 0.05
                },

                'personality_weights': {
                    'Ambivert': 0.4,
                    'Introverted': 0.35,
                    'Extroverted': 0.25
                },
                'leadership_rate': 0.25,
                'extracurricular_hours_base': 8,
                'extracurricular_type_weights': {
                    'Community': 0.35,
                    'Professional': 0.25,
                    'Social': 0.2,
                    'Academic': 0.1,
                    'Sports': 0.1
                },
                'cca_count_base': 2,

                'internship_rate': 0.7,

                'selection_criteria_weights': {
                    'Flexibility': 0.25,
                    'Affordability': 0.2,
                    'Work-Life Balance': 0.15,
                    'Course Offerings': 0.15,
                    'Location': 0.15,
                    'Support Services': 0.1
                },

                'cca_weights': {
                    'Community Service': 0.3,
                    'Professional Development': 0.25,
                    'Social Club': 0.2,
                    'Support Group': 0.15,
                    'Interest Group': 0.1
                }
            }
        }

    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Make a weighted random choice from a dictionary of options and weights"""
        options = list(weights.keys())
        weight_values = list(weights.values())
        return random.choices(options, weights=weight_values, k=1)[0]

    def generate_profile(self, university: str) -> StudentProfile:
        """Generate a single student profile using the university's weights"""

        uni_profile = self.UNIVERSITY_PROFILES[university]

        # Generate basic demographics using weights
        age = self._weighted_choice(uni_profile['age_weights'])
        gender = self._weighted_choice(uni_profile['gender_weights'])
        student_status = self._weighted_choice(uni_profile['student_status_weights'])

        # Generate academic characteristics
        satisfaction = max(1, min(5, int(np.random.normal(
            uni_profile['satisfaction_base'],
            0.3  # Reduced noise for more distinct profiles
        ))))

        learning_style = self._weighted_choice(uni_profile['learning_style_weights'])
        school = self._weighted_choice(uni_profile['school_weights'])
        career_goal = self._weighted_choice(uni_profile['career_goal_weights'])
        plans_further_education = self._weighted_choice(uni_profile['further_education_weights'])

        # Generate importance ratings with small noise
        importance_ratings = {}
        for key, base_value in uni_profile['importance_baselines'].items():
            importance_ratings[key] = max(1, min(10, int(base_value + np.random.normal(0, 0.5))))

        # Generate engagement metrics
        personality = self._weighted_choice(uni_profile['personality_weights'])
        leadership_role = int(random.random() < uni_profile['leadership_rate'])
        extracurricular_hours = max(0, int(np.random.normal(
            uni_profile['extracurricular_hours_base'],
            2
        )))

        extracurricular_type = self._weighted_choice(uni_profile['extracurricular_type_weights'])
        cca_count = max(1, int(np.random.normal(uni_profile['cca_count_base'], 1)))

        # Generate lists using weighted selection
        selection_criteria = random.choices(
            list(uni_profile['selection_criteria_weights'].keys()),
            weights=list(uni_profile['selection_criteria_weights'].values()),
            k=3
        )

        cca_list = random.choices(
            list(uni_profile['cca_weights'].keys()),
            weights=list(uni_profile['cca_weights'].values()),
            k=min(cca_count, len(uni_profile['cca_weights']))
        )

        # Calculate engagement level and category
        engagement_level = int((extracurricular_hours / 20 + leadership_role + cca_count / 4) * 2)
        if engagement_level > 5:
            engagement_category = 'High'
        elif engagement_level > 2:
            engagement_category = 'Medium'
        else:
            engagement_category = 'Low'

        # Generate profile
        return StudentProfile(
            # Demographics
            age=age,
            gender=gender,
            student_status=student_status,
            university=university,

            # Academic
            satisfaction_rating=satisfaction,
            learning_style=learning_style,
            preferred_population=uni_profile['preferred_population'],
            school=school,
            plans_further_education=plans_further_education,
            career_goal=career_goal,

            # Importance ratings
            cost_importance=importance_ratings['cost'],
            culture_importance=importance_ratings['culture'],
            internship_importance=importance_ratings['internship'],
            ranking_influence=importance_ratings['ranking'],
            extracurricular_importance=importance_ratings['extracurricular'],
            family_influence=importance_ratings['family'],
            friend_influence=importance_ratings['friend'],
            social_media_influence=importance_ratings['social_media'],
            scholarship_significance=importance_ratings['scholarship'],

            # Financial
            has_scholarship=int(random.random() < uni_profile['scholarship_rate']),
            funding_source=self._weighted_choice(uni_profile['funding_source_weights']),
            financial_consideration=float((importance_ratings['cost'] + importance_ratings['scholarship']) / 2),

            # Location
            residence=self._weighted_choice(uni_profile['residence_weights']),

            # Engagement
            personality=personality,
            leadership_role=leadership_role,
            extracurricular_hours=extracurricular_hours,
            extracurricular_type=extracurricular_type,
            cca_count=cca_count,
            engagement_level=engagement_level,
            engagement_category=engagement_category,

            # Participation
            internship_participation=int(random.random() < uni_profile['internship_rate']),

            # Influence
            external_influence=float(sum([
                importance_ratings['family'],
                importance_ratings['friend'],
                importance_ratings['social_media']
            ]) / 3),

            # Lists
            selection_criteria_list=str(selection_criteria),
            cca_list=str(cca_list),

            # Categories
            satisfaction_group='Satisfied' if satisfaction > 3 else 'Neutral' if satisfaction == 3 else 'Dissatisfied'
        )

    def generate_dataset(self, profile_counts: Dict[str, int], output_path: str = 'synthetic_profiles.csv'):
        """Generate profiles for multiple universities and save to CSV"""

        all_profiles = []

        # Generate profiles for each university
        for university, count in profile_counts.items():
            print(f"Generating {count} profiles for {university}...")

            # Generate profiles
            university_profiles = [self.generate_profile(university) for _ in range(count)]
            all_profiles.extend(university_profiles)

            # Calculate and print statistics
            avg_satisfaction = np.mean([p.satisfaction_rating for p in university_profiles])
            engagement_dist = Counter([p.engagement_category for p in university_profiles])
            leadership_pct = sum(p.leadership_role for p in university_profiles) / len(university_profiles) * 100

            print(f"\n{university} Summary Statistics:")
            print(f"Average Satisfaction: {avg_satisfaction:.2f}")
            print(f"Engagement Distribution: {dict(engagement_dist)}")
            print(f"Leadership Percentage: {leadership_pct:.1f}%")

        # Convert to DataFrame and save
        df = pd.DataFrame([vars(p) for p in all_profiles])
        df.to_csv(output_path, index=False)
        print(f"\nSaved {len(all_profiles)} profiles to {output_path}")

        return df


def main():
    """Generate synthetic profiles for model evaluation"""
    generator = UniversityProfileGenerator()

    # Define number of profiles per university
    profile_counts = {
        'NUS': 500,
        'NTU': 500,
        'SMU': 500,
        'SUTD': 500,
        'SIT': 500,
        'SUSS': 500
    }

    # Generate and save profiles
    df = generator.generate_dataset(profile_counts, './synthetic_data/synthetic_profiles.csv')

    # Print overall statistics
    print("\nOverall Dataset Statistics:")
    print(f"Total Profiles: {len(df)}")
    print("\nSatisfaction by University:")
    print(df.groupby('university')['satisfaction_rating'].mean().round(2))
    print("\nEngagement Categories:")
    print(df['engagement_category'].value_counts(normalize=True).round(3))
    print("\nTop Career Goals:")
    print(df['career_goal'].value_counts().head())


if __name__ == '__main__':
    main()
