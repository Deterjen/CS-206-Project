import re
from collections import Counter

import numpy as np
import pandas as pd


def clean_survey_data(file_path):
    """
    Clean and prepare survey preprocessing for analysis

    Parameters:
    file_path (str): Path to the CSV file

    Returns:
    pd.DataFrame: Cleaned and processed dataframe
    """
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Make a copy to preserve original preprocessing
    df_cleaned = df.copy()

    # Drop empty columns
    empty_cols = ['Column 25', 'Column 31', 'Column 39',
                  'Did you consider other universities before selecting this one?',
                  'Did you receive a scholarship?']
    df_cleaned = df_cleaned.drop(columns=empty_cols)

    # Rename columns to make them more concise
    column_rename_map = {
        'What is your age?': 'age',
        'What is your gender?': 'gender',
        'What is your Nationality? ': 'nationality',
        'Are you a domestic or International Student?': 'student_status',
        'What is your highest academic qualification before joining university?': 'prior_qualification',
        'What was your GPA/Grade of your highest qualification? (E.g. 3.6/4.0 GPA, 70/90 Rank Points)': 'prior_gpa',
        ' Which university are you currently attending or have graduated from?  ': 'university',
        'What was your second-choice university? ': 'second_choice_university',
        'What were your top three criteria for selecting this university?': 'selection_criteria',
        'What is your preferred learning style?': 'learning_style',
        'Do you prefer a large or small student population?': 'preferred_population',
        'How satisfied are you with your university?': 'satisfaction_rating',
        'Provide some phrases to describe your university ("Research Oriented", "Vibrant Student Lifestyle", "Collaborative Environment", etc)': 'university_description',
        'Which campus setting do you prefer?': 'preferred_campus',
        'How important was the cost of education in your decision': 'cost_importance',
        'Do you live on campus or commute?': 'residence',
        'How important is campus culture in your university choice?': 'culture_importance',
        'What is your school of study?': 'school',
        'Do you plan to pursue further education after this degree?': 'further_education',
        'What is your career goal?': 'career_goal',
        'How much importance do you place on internship/job placement opportunities?': 'internship_importance',
        'Have you participated in any university-sponsored internships or job programs?': 'internship_participation',
        'Did family influence your university choice?': 'family_influence',
        'Did friends influence your university choice?': 'friend_influence',
        'How much did social media/marketing influence your choice?': 'social_media_influence',
        'Did university rankings influence your decision?': 'ranking_influence',
        'How important was the availability of specific extracurricular activities (e.g., sports, arts, clubs) in your decision?': 'extracurricular_importance',
        'How would you describe your personality?': 'personality',
        'Are you involved in any leadership roles (e.g., student council, club president)?': 'leadership_role',
        ' How many hours per week do you dedicate to extracurricular activities?': 'extracurricular_hours',
        'What type of extracurricular activities do you prioritize?': 'extracurricular_type',
        ' What CCAs (Co-Curricular Activities) are you currently involved in? (Comma-separated, e.g., Debate Club, Basketball, Volunteer Work, None)  ': 'ccas',
        'What sources did you rely on to fund your university education?': 'funding_source',
        'How significant was the availability of financial aid or scholarships in your university choice?': 'scholarship_significance'
    }
    df_cleaned = df_cleaned.rename(columns=column_rename_map)

    # Keep age as categorical labels
    def clean_age(age_str):
        if isinstance(age_str, str):
            # Standardize formatting but keep as categorical
            if 'under' in age_str.lower() or '<' in age_str:
                return "Under 18"
            elif ' - ' in age_str:
                return age_str.strip()
            elif 'over' in age_str.lower() or '>' in age_str:
                return "Over 30"
            # If it's just a number, categorize it
            age_digits = re.findall(r'\d+', age_str)
            if age_digits:
                age = int(age_digits[0])
                if age < 18:
                    return "Under 18"
                elif age <= 24:
                    return "18 - 24"
                elif age <= 30:
                    return "25 - 30"
                else:
                    return "Over 30"
        return age_str

    df_cleaned['age'] = df_cleaned['age'].apply(clean_age)

    # Standardize gender values
    df_cleaned['gender'] = df_cleaned['gender'].str.strip().str.title()

    # Standardize nationality
    def clean_nationality(nationality):
        if nationality.lower() in ['singaporean', 'singapore']:
            return 'Singaporean'
        return nationality.strip().title()

    df_cleaned['nationality'] = df_cleaned['nationality'].apply(clean_nationality)

    # Standardize student status
    df_cleaned['student_status'] = df_cleaned['student_status'].str.strip().str.title()

    # Standardize university names
    def clean_university(uni):
        uni = uni.strip()
        # Create abbreviation mapping
        uni_map = {
            'National University of Singapore': 'NUS',
            'Nanyang Technological University': 'NTU',
            'Singapore Management University': 'SMU',
            'Singapore Institute of Technology': 'SIT',
            'Singapore Institute of Management': 'SIM',
            'Singapore University of Technology and Design': 'SUTD',
            'Singapore University of Social Sciences': 'SUSS'
        }

        # Check if university name contains abbreviation in parentheses
        if '(' in uni and ')' in uni:
            abbr = uni[uni.find("(") + 1:uni.find(")")]
            if abbr in ['NUS', 'NTU', 'SMU', 'SIT', 'SIM', 'SUTD', 'SUSS']:
                return abbr

        # Check for full names
        for full_name, abbr in uni_map.items():
            if full_name.lower() in uni.lower():
                return abbr

        return uni

    df_cleaned['university'] = df_cleaned['university'].apply(clean_university)
    df_cleaned['second_choice_university'] = df_cleaned['second_choice_university'].apply(clean_university)

    # Keep selection criteria as a list without standardization
    def extract_criteria(criteria_str):
        if isinstance(criteria_str, str):
            criteria_list = [c.strip() for c in criteria_str.split(',')]
            return criteria_list
        return []

    df_cleaned['selection_criteria_list'] = df_cleaned['selection_criteria'].apply(extract_criteria)

    # Standardize learning style
    df_cleaned['learning_style'] = df_cleaned['learning_style'].str.strip().str.lower()

    # Standardize preferred population size
    def standardize_population(pop):
        pop = pop.lower().strip()
        if pop in ['small', 'smaller']:
            return 'Small'
        elif pop in ['medium', 'moderate']:
            return 'Medium'
        elif pop in ['large', 'larger']:
            return 'Large'
        else:
            return 'Other'

    df_cleaned['preferred_population'] = df_cleaned['preferred_population'].apply(standardize_population)

    # Standardize campus preference
    df_cleaned['preferred_campus'] = df_cleaned['preferred_campus'].str.strip().str.title()

    # Convert ratings to integers where appropriate
    rating_columns = ['satisfaction_rating', 'cost_importance', 'culture_importance',
                      'internship_importance', 'family_influence', 'friend_influence',
                      'social_media_influence', 'ranking_influence',
                      'extracurricular_importance', 'extracurricular_hours',
                      'scholarship_significance']

    for col in rating_columns:
        df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')

    # Standardize yes/no responses
    binary_columns = ['internship_participation', 'leadership_role']
    for col in binary_columns:
        df_cleaned[col] = df_cleaned[col].str.strip().str.lower()
        df_cleaned[col] = df_cleaned[col].map({'yes': 1, 'no': 0})

    # Create a flag for scholarship recipients from funding source
    df_cleaned['has_scholarship'] = df_cleaned['funding_source'].str.lower().str.contains('scholarship').astype(int)

    # Extract CCAs into a list, preserving original entries
    def extract_ccas(cca_str):
        if pd.isna(cca_str) or cca_str.lower() == 'none':
            return []
        return [c.strip() for c in cca_str.split(',')]

    df_cleaned['cca_list'] = df_cleaned['ccas'].apply(extract_ccas)
    df_cleaned['cca_count'] = df_cleaned['cca_list'].apply(len)

    # For use in analysis, preserve the original extracurricular_type
    df_cleaned['extracurricular_type_original'] = df_cleaned['extracurricular_type']

    # Create indicators for further education plans
    df_cleaned['plans_further_education'] = df_cleaned['further_education'].apply(
        lambda x: 1 if x.lower() == 'yes' else (0 if x.lower() == 'no' else 0.5)  # 0.5 for undecided
    )

    # Preserve original career goals without standardization
    # Only clean up whitespace and formatting
    df_cleaned['career_goal'] = df_cleaned['career_goal'].str.strip()

    # For backward compatibility, create a column that stores the original value
    df_cleaned['career_goal_original'] = df_cleaned['career_goal']

    # Create dummy variables for categorical fields
    categorical_cols = ['university', 'student_status', 'learning_style',
                        'preferred_population', 'preferred_campus',
                        'residence', 'personality', 'career_goal_category']

    # Optionally create dummy variables
    # Uncomment this section if you want one-hot encoding
    """
    for col in categorical_cols:
        dummies = pd.get_dummies(df_cleaned[col], prefix=col)
        df_cleaned = pd.concat([df_cleaned, dummies], axis=1)
    """

    return df_cleaned


def create_analysis_ready_dataset(df):
    """
    Create a simplified, analysis-ready dataset with key variables

    Parameters:
    df (pd.DataFrame): Cleaned dataframe

    Returns:
    pd.DataFrame: Analysis-ready dataframe with key variables
    """
    # Select key variables for analysis
    analysis_cols = [
        'age', 'gender', 'student_status', 'university',
        'satisfaction_rating', 'learning_style', 'preferred_population',
        'cost_importance', 'has_scholarship', 'residence',
        'culture_importance', 'school', 'plans_further_education',
        'career_goal', 'internship_importance', 'internship_participation',
        'family_influence', 'friend_influence', 'social_media_influence',
        'ranking_influence', 'extracurricular_importance', 'personality',
        'leadership_role', 'extracurricular_hours', 'extracurricular_type',
        'cca_count', 'funding_source', 'scholarship_significance',
        'selection_criteria_list', 'cca_list'
    ]

    # Create analysis dataframe
    df_analysis = df[analysis_cols].copy()

    # Create derived variables that might be useful for analysis

    # Student satisfaction groups
    df_analysis['satisfaction_group'] = pd.cut(
        df_analysis['satisfaction_rating'],
        bins=[0, 2, 3, 5],
        labels=['Dissatisfied', 'Neutral', 'Satisfied']
    )

    # Financial consideration level (composite of cost importance and scholarship significance)
    df_analysis['financial_consideration'] = (
                                                     df_analysis['cost_importance'] + df_analysis[
                                                 'scholarship_significance']
                                             ) / 2

    # External influence level (composite of family, friend, social media influence)
    df_analysis['external_influence'] = (
                                                df_analysis['family_influence'] +
                                                df_analysis['friend_influence'] +
                                                df_analysis['social_media_influence']
                                        ) / 3

    # Engagement level (based on extracurricular hours and leadership)
    df_analysis['engagement_level'] = df_analysis['extracurricular_hours'] * (df_analysis['leadership_role'] + 1)
    df_analysis['engagement_category'] = pd.cut(
        df_analysis['engagement_level'],
        bins=[0, 5, 15, float('inf')],
        labels=['Low', 'Medium', 'High']
    )

    return df_analysis


def main():
    """
    Main function to execute the preprocessing cleaning and preparation process
    """
    input_file = '../data/raw.csv'

    # Clean the preprocessing
    cleaned_data = clean_survey_data(input_file)

    # Create analysis dataset
    analysis_data = create_analysis_ready_dataset(cleaned_data)

    # Save cleaned datasets
    cleaned_data.to_csv('cleaned_survey_data.csv', index=False)
    analysis_data.to_csv('analysis_ready_survey_data.csv', index=False)

    print(f"Data cleaning complete. Saved cleaned preprocessing to 'cleaned_survey_data.csv'")
    print(f"Analysis-ready dataset saved to 'analysis_ready_survey_data.csv'")

    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total number of respondents: {len(cleaned_data)}")
    print(f"Universities represented: {cleaned_data['university'].nunique()}")
    print(f"Average satisfaction rating: {cleaned_data['satisfaction_rating'].mean():.2f}")

    # Handle leadership roles differently since we might have modified the format
    if 'leadership_role' in cleaned_data.columns and cleaned_data['leadership_role'].dtype in [np.int64, np.float64]:
        print(f"Percentage with leadership roles: {cleaned_data['leadership_role'].mean() * 100:.1f}%")

    # Print age distribution
    print("\nAge Distribution:")
    age_counts = cleaned_data['age'].value_counts()
    for age_group, count in age_counts.items():
        print(f"  {age_group}: {count} respondents ({count / len(cleaned_data) * 100:.1f}%)")

    # Print most common CCAs
    print("\nTop CCAs:")
    all_ccas = [cca for cca_list in cleaned_data['cca_list'] for cca in cca_list if cca_list]
    cca_counter = Counter(all_ccas)
    for cca, count in cca_counter.most_common(5):
        print(f"  {cca}: {count} participants")

    return cleaned_data, analysis_data


if __name__ == "__main__":
    cleaned_data, analysis_data = main()
