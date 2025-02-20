from flask import Flask, render_template, request, jsonify

from university_recommender import UniversityRecommender

app = Flask(__name__)
recommender = UniversityRecommender('./data/analysis_ready_survey_data.csv')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Parse form data
        form_data = request.form.to_dict()

        # Process lists
        selection_criteria = request.form.getlist('selection_criteria')
        ccas = form_data.get('ccas', '').split(',')
        ccas = [cca.strip() for cca in ccas if cca.strip()]

        # Convert numeric fields
        numeric_fields = [
            'cost_importance', 'culture_importance', 'internship_importance',
            'ranking_influence', 'extracurricular_importance', 'family_influence',
            'friend_influence', 'social_media_influence', 'leadership_role',
            'extracurricular_hours'
        ]

        for field in numeric_fields:
            if field in form_data and form_data[field]:
                form_data[field] = int(form_data[field])

        # Handle plans_further_education
        if 'plans_further_education' in form_data:
            value_map = {'yes': 1.0, 'no': 0.0, 'undecided': 0.5}
            form_data['plans_further_education'] = value_map.get(form_data['plans_further_education'], 0.5)

        # Add lists to form data
        form_data['selection_criteria'] = selection_criteria
        form_data['ccas'] = ccas

        # Choose algorithm based on form data
        algorithm = form_data.pop('algorithm', 'hybrid')
        num_results = int(form_data.pop('num_results', 3))

        # Get recommendations
        recommendations = recommender.recommend(
            user_data=form_data,
            algorithm=algorithm,
            n=num_results
        )

        # Get explanation for top recommendation if any
        explanation = None
        if recommendations:
            explanation = recommender.explain_recommendation(
                form_data,
                recommendations[0]['university_id']
            )

        return render_template(
            'results.html',
            recommendations=recommendations,
            explanation=explanation,
            user_data=form_data,
            algorithm=algorithm
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    try:
        # Parse JSON data
        user_data = request.json
        algorithm = user_data.pop('algorithm', 'hybrid')
        num_results = user_data.pop('num_results', 3)

        # Get recommendations
        recommendations = recommender.recommend(
            user_data=user_data,
            algorithm=algorithm,
            n=num_results
        )

        # Get explanation for top recommendation if any
        explanation = None
        if recommendations:
            explanation = recommender.explain_recommendation(
                user_data,
                recommendations[0]['university_id']
            )

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'explanation': explanation
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
