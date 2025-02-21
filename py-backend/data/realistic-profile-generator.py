import random
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np


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
    selection_criteria_list: str  # Stored as string representation of list
    cca_list: str  # Stored as string representation of list

    # Derived categorization
    satisfaction_group: str  # Categorized satisfaction level


class RealisticProfileGenerator:
    """Generates realistic student profiles with correlated attributes"""

    def __init__(self):
        self.setup_distributions()

    def setup_distributions(self):
        """Set up realistic probability distributions"""

        # Core demographic distributions
        self.DEMOGRAPHICS = {
            'age': {'18 - 24': 0.85, '25 - 30': 0.12, 'Over 30': 0.03},
            'gender': {'Male': 0.51, 'Female': 0.49},
            'student_status': {'Domestic': 0.75, 'International': 0.25}
        }

        # Academic distributions
        self.SCHOOLS = {
            'Engineering': 0.25,
            'Business': 0.20,
            'Computing': 0.15,
            'Science': 0.12,
            'Arts & Social Sciences': 0.10,
            'Medicine': 0.08,
            'Design': 0.05,
            'Law': 0.05
        }

        self.LEARNING_STYLES = {
            'hands-on': 0.35,
            'visual': 0.25,
            'auditory': 0.20,
            'reading/writing': 0.20
        }

        self.POPULATION_PREFERENCES = {
            'Large': 0.4,
            'Medium': 0.4,
            'Small': 0.2
        }

        self.RESIDENCE_OPTIONS = {
            'On campus': 0.3,
            'Commute': 0.7
        }

        self.PERSONALITY_TYPES = {
            'Extroverted': 0.3,
            'Introverted': 0.3,
            'Ambivert': 0.4
        }

        self.EXTRACURRICULAR_TYPES = {
            'Sports': 0.25,
            'Arts': 0.20,
            'Academic': 0.25,
            'Community Service': 0.15,
            'Leadership': 0.15
        }

        # University-specific characteristics
        self.UNIVERSITY_PROFILES = {
            'NUS': {
                'satisfaction_dist': {'mean': 4.2, 'std': 0.5},
                'engagement_dist': {'mean': 4.0, 'std': 0.8},
                'importance_factors': {
                    'ranking_influence': {'mean': 8, 'std': 1},
                    'internship_importance': {'mean': 8, 'std': 1},
                    'culture_importance': {'mean': 7, 'std': 1.5}
                },
                'scholarship_rate': 0.4,
                'internship_rate': 0.8,
                'preferred_population': {'Large': 0.8, 'Medium': 0.15, 'Small': 0.05}
            },
            'NTU': {
                'satisfaction_dist': {'mean': 4.1, 'std': 0.5},
                'engagement_dist': {'mean': 3.8, 'std': 0.9},
                'importance_factors': {
                    'ranking_influence': {'mean': 7.5, 'std': 1.2},
                    'internship_importance': {'mean': 7.8, 'std': 1},
                    'culture_importance': {'mean': 7.2, 'std': 1.5}
                },
                'scholarship_rate': 0.35,
                'internship_rate': 0.75,
                'preferred_population': {'Large': 0.75, 'Medium': 0.20, 'Small': 0.05}
            }
            # Add other universities...
        }

    def _generate_importance_rating(self, profile: Dict, factor: str) -> int:
        """Generate correlated importance ratings"""
        base = random.randint(5, 8)  # Base importance

        # Add correlations based on student characteristics
        if factor == 'internship_importance':
            if profile['school'] in ['Business', 'Engineering', 'Computing']:
                base += random.randint(1, 2)
        elif factor == 'culture_importance':
            if profile['personality'] == 'Extroverted':
                base += random.randint(1, 2)

        return min(max(base, 1), 10)  # Ensure within 1-10 range

    def _generate_derived_fields(self, profile: Dict) -> Dict:
        """Generate derived fields based on profile data"""

        # Calculate financial_consideration
        profile['financial_consideration'] = (profile['cost_importance'] +
                                              profile['scholarship_significance']) / 2

        # Calculate external_influence
        profile['external_influence'] = (profile['family_influence'] +
                                         profile['friend_influence'] +
                                         profile['social_media_influence']) / 3

        # Determine satisfaction_group
        if profile['satisfaction_rating'] <= 2:
            profile['satisfaction_group'] = 'Dissatisfied'
        elif profile['satisfaction_rating'] == 3:
            profile['satisfaction_group'] = 'Neutral'
        else:
            profile['satisfaction_group'] = 'Satisfied'

        # Determine engagement_category based on engagement_level
        if profile['engagement_level'] <= 2:
            profile['engagement_category'] = 'Low'
        elif profile['engagement_level'] <= 4:
            profile['engagement_category'] = 'Medium'
        else:
            profile['engagement_category'] = 'High'

        return profile

    def generate_profile(self, university: Optional[str] = None) -> StudentProfile:
        """Generate a complete student profile with correlated attributes"""

        # Get university profile if specified
        uni_profile = self.UNIVERSITY_PROFILES.get(university, {}) if university else {}

        # Generate base profile
        profile = {
            'age': self._weighted_choice(self.DEMOGRAPHICS['age']),
            'gender': self._weighted_choice(self.DEMOGRAPHICS['gender']),
            'student_status': self._weighted_choice(self.DEMOGRAPHICS['student_status']),
            'university': university or self._weighted_choice(
                {u: 1 for u in self.UNIVERSITY_PROFILES.keys()}
            ),
            'satisfaction_rating': self._generate_satisfaction(uni_profile),
            'learning_style': self._weighted_choice(self.LEARNING_STYLES),
            'preferred_population': self._weighted_choice(
                uni_profile.get('preferred_population', self.POPULATION_PREFERENCES)
            ),
            'school': self._weighted_choice(self.SCHOOLS),
            'plans_further_education': random.choice([0, 0.5, 1]),  # No, Maybe, Yes
            'career_goal': self._generate_career_goal(),
            'residence': self._weighted_choice(self.RESIDENCE_OPTIONS),
            'personality': self._weighted_choice(self.PERSONALITY_TYPES),

            # Generate importance ratings
            'cost_importance': random.randint(1, 10),
            'culture_importance': random.randint(1, 10),
            'internship_importance': random.randint(1, 10),
            'ranking_influence': random.randint(1, 10),
            'extracurricular_importance': random.randint(1, 10),
            'family_influence': random.randint(1, 10),
            'friend_influence': random.randint(1, 10),
            'social_media_influence': random.randint(1, 10),
            'scholarship_significance': random.randint(1, 10),

            # Generate engagement metrics
            'leadership_role': random.choice([0, 1]),
            'extracurricular_hours': random.randint(0, 20),
            'extracurricular_type': self._weighted_choice(self.EXTRACURRICULAR_TYPES),
            'engagement_level': random.randint(1, 5),

            # Generate participation info
            'internship_participation': random.choice([0, 1]),

            # Generate financial info
            'has_scholarship': random.choice([0, 1]),
            'funding_source': random.choice(['Family', 'Scholarship', 'Loan', 'Self-funded']),

            # Generate lists
            'selection_criteria_list': str(['Academic Excellence', 'Job Prospects', 'Campus Life']),
            'cca_list': str(['Sports Club', 'Academic Society']),
        }

        # Add derived fields
        profile['cca_count'] = len(eval(profile['cca_list']))
        profile = self._generate_derived_fields(profile)

        return StudentProfile(**profile)

    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        """Make a weighted random choice from a dictionary of options and weights"""
        options = list(choices.keys())
        weights = list(choices.values())
        return random.choices(options, weights=weights, k=1)[0]

    def _generate_satisfaction(self, uni_profile: Dict) -> int:
        """Generate satisfaction rating based on university profile"""
        if not uni_profile:
            return random.randint(3, 5)

        dist = uni_profile.get('satisfaction_dist', {'mean': 4.0, 'std': 0.5})
        rating = int(round(np.random.normal(dist['mean'], dist['std'])))
        return max(min(rating, 5), 1)

    def _generate_career_goal(self) -> str:
        """Generate a career goal based on school and other factors"""
        goals = {
            'Software Engineer': 0.2,
            'Data Scientist': 0.15,
            'Business Analyst': 0.15,
            'Researcher': 0.1,
            'Consultant': 0.1,
            'Product Manager': 0.1,
            'Entrepreneur': 0.1,
            'Other': 0.1
        }
        return self._weighted_choice(goals)

    def generate_dataset(self, size: int = 1000) -> List[StudentProfile]:
        """Generate a dataset of student profiles"""
        profiles = []
        for _ in range(size):
            profile = self.generate_profile()
            profiles.append(profile)
        return profiles

    def save_to_csv(self, profiles: Dict[str, List[StudentProfile]], output_dir: str = 'synthetic_data'):
        """Save generated profiles to CSV files in the format expected by university_recommender"""
        import os
        import pandas as pd

        os.makedirs(output_dir, exist_ok=True)

        all_records = []

        # Convert profiles to DataFrame format
        for university, uni_profiles in profiles.items():
            records = []
            for profile in uni_profiles:
                record = profile.__dict__
                # Convert lists to strings
                record['selection_criteria_list'] = str(record.pop('selection_criteria_list'))
                record['cca_list'] = str(record.pop('cca_list'))
                records.append(record)
                all_records.append(record)

            df = pd.DataFrame(records)
            output_file = os.path.join(output_dir, f'{university.lower()}_profiles.csv')
            df.to_csv(output_file, index=False)
            print(f"Saved {len(records)} profiles for {university} to {output_file}")

        # Save all profiles to a single CSV file
        all_df = pd.DataFrame(all_records)
        all_output_file = os.path.join(output_dir, 'all_profiles.csv')
        all_df.to_csv(all_output_file, index=False)
        print(f"Saved all profiles to {all_output_file}")


def main():
    """Generate synthetic profiles for model evaluation"""
    generator = RealisticProfileGenerator()

    # Generate profiles for each university
    university_profiles = {}
    profile_counts = {
        'NUS': 500,
        'NTU': 500,
        'SMU': 500,
        'SUTD': 500,
        'SIT': 500,
        'SUSS': 500
    }

    for university, count in profile_counts.items():
        print(f"\nGenerating {count} profiles for {university}...")
        profiles = [generator.generate_profile(university) for _ in range(count)]
        university_profiles[university] = profiles

        # Print summary statistics
        print(f"{university} Profile Characteristics:")
        print(f"Top 3 Schools: {Counter([p.school for p in profiles]).most_common(3)}")
        print(f"Learning Styles: {Counter([p.learning_style for p in profiles]).most_common()}")
        print(f"Average Engagement Level: {sum(p.engagement_level for p in profiles) / len(profiles):.2f}")

    # Save all profiles to CSV files
    print("\nSaving profiles to CSV...")
    generator.save_to_csv(university_profiles, output_dir='synthetic_data')


if __name__ == "__main__":
    from collections import Counter

    main()
