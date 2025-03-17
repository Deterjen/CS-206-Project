# University Recommendation System

A sophisticated recommendation system designed to match aspiring students with universities based on comprehensive questionnaire data from existing students.

## Overview

The University Recommendation System uses a hybrid approach to provide personalized university recommendations to prospective students. By analyzing questionnaire responses from both aspiring and existing students, the system identifies universities where students with similar preferences and characteristics have had positive experiences.

## How It Works

### Recommendation Model Architecture

The system employs a hybrid recommendation approach that combines:

1. **Profile Matching**: Direct comparison between aspiring and existing student profiles
2. **Content-Based Filtering**: Consideration of university attributes that match student preferences
3. **Embedding-Based Text Similarity**: Analysis of free-text responses using semantic similarity

### Key Components

- **Data Processing Pipeline**: Handles questionnaire responses and transforms them into structured data
- **Similarity Computation Engine**: Calculates multi-dimensional similarity scores across various aspects:
  - Academic experience
  - Social and cultural fit
  - Financial feasibility
  - Career prospects
  - Geographic preferences
  - Campus facilities
  - University reputation
  - Personal fit
- **Recommendation Generator**: Creates ranked university recommendations with detailed scoring
- **Similar Student Finder**: Identifies existing students with similar preferences and experiences
- **Supabase Database Client**: Manages data persistence and retrieval

### Similarity Calculation

For each category, the system uses appropriate similarity metrics:

- **Categorical Data**: Jaccard similarity for multiple-choice questions
- **Numerical Data**: Weighted comparisons based on importance ratings
- **Text Data**: Semantic similarity using sentence embeddings and HNSW indexing

## Requirements

### System Requirements

- Python 3.8+
- C++ Build Tools (for HNSW installation)

### Dependencies

```
supabase~=1.0.3
pydantic~=1.10.8
sentence-transformers~=2.2.2
hnswlib~=0.7.0
python-dotenv~=1.0.0
numpy~=1.24.3
```

## Installation

1. **Install C++ Build Tools**

   For Windows:
   - Download Build Tools for Visual Studio 2022 from [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/)
   - Select "Desktop Development with C++" during installation

   For macOS:
   - Install Xcode Command Line Tools: `xcode-select --install`

   For Linux:
   - Install the build essentials package: `sudo apt-get install build-essential`

2. **Set up Python environment**

   ```bash
   # Create and activate virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up and Configure Supabase**

   a. **Install Supabase CLI and Dependencies**
   
   You'll need Docker installed on your system before proceeding. Then:

   ```bash
   # Install Supabase CLI globally
   npm install supabase --save-dev
   
   # Initialize Supabase in your project
   npx supabase init
   
   # Start a local Supabase instance
   npx supabase start
   ```
   
   After running these commands, you'll see output containing your local Supabase URL and keys.

   b. **Configure Environment Variables**
   
   Create a `.env.local` file in the project root with your Supabase credentials:

   ```
   # For local development with Supabase CLI
   SUPABASE_URL=http://localhost:54321
   SUPABASE_KEY=your_local_anon_key_from_supabase_start_output
   
   # Or for Supabase cloud
   # SUPABASE_URL=your_supabase_url
   # SUPABASE_KEY=your_supabase_key
   ```

## Database Schema

The system uses a relational database schema with the following main tables:

- **Universities**: Information about universities
- **Programs**: Academic programs offered by universities
- **ExistingStudents**: Current student information with various subsections
- **AspiringStudents**: Prospective student information with preference subsections
- **Recommendations**: Generated university recommendations with similarity scores
- **SimilarStudents**: Links between aspiring students and similar existing students

### Setting Up Database Schema

After starting your local Supabase instance, you need to set up the database schema:

1. Access the Supabase Studio at http://localhost:54323
2. Go to the SQL Editor
3. Execute the schema creation SQL file:
   - Load the `postgres.sql` file from the project root
   - Execute the SQL to create all necessary tables and relationships

### Loading Test Data

To populate the database with sample data for testing:

1. In the Supabase SQL Editor, load the `tempdata.sql` file
2. Execute the SQL to insert test universities, programs, existing students, and their questionnaire responses
3. This test data enables you to immediately test the recommendation system functionality

You can also execute these files from the command line:

```bash
# Execute schema creation
psql -h localhost -p 5432 -U postgres -d postgres -f postgres.sql

# Load test data
psql -h localhost -p 5432 -U postgres -d postgres -f tempdata.sql
```

## Usage

### Basic Usage

```python
from services.supabase_client import SupabaseDB
from services.recommendation_service import UniversityRecommendationService

# Initialize the service
supabase_db = SupabaseDB.from_env()
recommendation_service = UniversityRecommendationService(supabase_db)

# Initialize the recommender with data
recommendation_service.initialize_recommender()

# Process an aspiring student questionnaire
questionnaire_data = {
    "preferred_fields": ["Business", "Computing/IT"],
    "learning_style": "Hands-on/Practical",
    "career_goals": "Technology entrepreneurship",
    # ... other questionnaire responses
}

# Save the student profile and get the ID
student_record = recommendation_service.process_questionnaire(questionnaire_data)
student_id = student_record["core"]["id"]

# Generate university recommendations
recommendations = recommendation_service.generate_recommendations(student_id, top_n=5)

# Get similar existing students
similar_students = recommendation_service.get_similar_students(student_id, top_n=3)

# Get detailed recommendation information
recommendation_details = recommendation_service.get_recommendation_details(recommendations[0]["id"])
```

### Example Script

See `main2.py` for a complete example of how to use the recommendation service.

## Customization

### Adjusting Category Weights

You can customize the importance of different categories by providing custom weights:

```python
custom_weights = {
    'academic': 0.25,
    'social': 0.15,
    'financial': 0.2,
    'career': 0.15,
    'geographic': 0.1,
    'facilities': 0.05,
    'reputation': 0.05,
    'personal_fit': 0.05
}

recommendation_service.initialize_recommender(category_weights=custom_weights)
```

## Questionnaire Structure

### Existing Student Questionnaire

The questionnaire for current students is divided into 10 sections:
1. University Information & Overall Satisfaction
2. Academic Experience
3. Social and Cultural Experience
4. Career Development
5. Financial Aspects
6. Campus Facilities
7. Reputation and Value
8. Personal Fit and Reflection
9. Selection Criteria
10. Additional Insights

### Aspiring Student Questionnaire

The questionnaire for prospective students is divided into 8 sections:
1. Academic Interest Similarity
2. Social and Cultural Compatibility
3. Career Prospects
4. Financial Feasibility
5. Geographic Preferences
6. Campus Facilities
7. Reputation and Brand Value
8. Personal Fit

## How the Recommendation Works

1. An aspiring student completes their questionnaire
2. The system processes and structures their responses
3. It compares the aspiring student's profile with existing student profiles
4. Similarity scores are calculated across multiple dimensions
5. Universities are ranked based on the overall similarity and category-specific scores
6. The system identifies the most similar existing students for each recommended university
7. Detailed recommendations are provided with similarity breakdowns

## Project Structure

```
py-backend/
├── main2.py                         # Example script
├── schemas/                         # Data models
│   └── schema.py                    # Pydantic schema definitions
├── services/
│   ├── recommendation_model.py      # Core recommendation algorithm
│   ├── recommendation_service.py    # Service layer connecting DB and model
│   └── supabase_client.py           # Database client
```

## Advanced Features

### Text Embedding and Efficient Similarity Search

For free-text responses, the system uses:
- **Sentence Transformers**: Converts text to numerical embeddings
- **HNSW (Hierarchical Navigable Small World)**: Enables efficient similarity search in high-dimensional spaces

### Feedback Loop

The system includes a feedback mechanism to collect user ratings on recommendations, which can be used to improve the model over time.

## Performance Considerations

- The HNSW indexing enables efficient similarity search even with large numbers of student profiles
- The system is designed to balance precision with computational efficiency
- For large deployments, consider scaling the database and possibly implementing caching

## Contributing

Contributions to improve the system are welcome. Please feel free to submit issues or pull requests.

## License

[Insert your license information here]