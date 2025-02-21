from university_recommender import UniversityRecommender


def main():
    """Run example recommendation scenarios."""
    print("University Recommendation System - MVP Example")
    print("=============================================")

    # Initialize the recommender
    recommender = UniversityRecommender('./data/analysis_ready_survey_data.csv')
    print(f"Loaded recommender with {len(recommender.universities)} universities")

    # Create an example user
    example_user = {
        'age': '18 - 24',
        'gender': 'Female',
        'personality': 'Extroverted',
        'learning_style': 'hands-on',
        'school': 'Business',
        'career_goal': 'Entrepreneur',
        'student_status': 'Domestic',
        'preferred_population': 'Large',
        'cost_importance': 7,
        'culture_importance': 9,
        'internship_importance': 8,
        'ranking_influence': 6,
        'extracurricular_importance': 8,
        'residence': 'On campus',
        'leadership_role': 1,
        'extracurricular_hours': 10,
        'selection_criteria': ['Campus Culture', 'Internship Opportunities', 'Reputation']
    }

    # Get profile-based recommendations
    print("\nGenerating profile-based recommendations...")
    profile_recs = recommender.get_profile_based_recommendations(example_user, n=3)
    print_recommendations(profile_recs, "PROFILE-BASED RECOMMENDATIONS")

    # Get embedding-based recommendations
    print("\nGenerating embedding-based recommendations...")
    embedding_recs = recommender.get_embedding_recommendations(example_user, n=3)
    print_recommendations(embedding_recs, "EMBEDDING-BASED RECOMMENDATIONS")

    # Get hybrid recommendations
    print("\nGenerating hybrid recommendations...")
    hybrid_recs = recommender.get_hybrid_recommendations(example_user, n=3)
    print_recommendations(hybrid_recs, "HYBRID RECOMMENDATIONS")

    # Get recommendation explanation for top university
    if hybrid_recs:
        university_id = hybrid_recs[0]['university_id']
        print(f"\nWhy we recommend {hybrid_recs[0]['name']}:")
        explanation = recommender.explain_recommendation(example_user, university_id)

        # Display strengths
        print("\nStrengths:")
        for strength in explanation['strengths']:
            print(f"✓ {strength}")

        # Display considerations
        if explanation['considerations']:
            print("\nConsiderations:")
            for consideration in explanation['considerations']:
                print(f"! {consideration}")

        # Display compatibility score
        compatibility = explanation['compatibility']['overall']
        print(f"\nOverall compatibility: {compatibility:.2f} ({int(compatibility * 100)}%)")
        print(f"Semantic similarity: {explanation['semantic_similarity']:.2f}")
        print(f"Similar students found: {explanation['similar_students']}")
        print(f"Average satisfaction at this university: {explanation['avg_satisfaction']:.1f}/5")


def print_recommendations(recommendations, title):
    """Print formatted recommendations."""
    print(f"\n{title}")
    print("=" * len(title))
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['name']} (Score: {rec['score']:.2f})")
        if 'profile_match' in rec:
            print(f"   Profile match: {rec['profile_match']:.2f}")
            print(f"   Semantic match: {rec['semantic_match']:.2f}")
        if 'match_confidence' in rec:
            print(f"   Match confidence: {rec['match_confidence']:.1f}%")
        if 'similar_students_count' in rec:
            print(f"   Similar students: {rec['similar_students_count']}")
        print(f"   {rec['description'][:150]}...")


# Run the example
if __name__ == "__main__":
    main()
