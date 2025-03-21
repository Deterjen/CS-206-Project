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
- Node.js and npm (for Supabase CLI)
- Docker (for running Supabase locally)

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
    # Supabase credentials
    SUPABASE_URL=http://localhost:54321
    SUPABASE_KEY=your_local_anon_key_from_supabase_start_output
    
    # Authentication settings
    SECRET_KEY=your_secret_key_for_jwt
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    
    # JamAIbase integration (for recommendation justification)
    JAMAIBASE_KEY=your_jamaibase_key
    JAMAIBASE_PAT=your_jamaibase_pat
    JAMAIBASE_PROJECT_ID=your_jamaibase_project_id
    
    # For Supabase cloud (if not using local)
    # SUPABASE_URL=your_supabase_url
    # SUPABASE_KEY=your_supabase_key
   ```

## Running the Gateway

To run the FastAPI gateway:

```bash
# Navigate to the gateway directory
cd gateway

# Run the FastAPI application with hot-reload
uvicorn main:app --reload
```

The API will be available at http://localhost:8000. You can access the interactive API documentation at http://localhost:8000/docs.

## Resetting the Supabase Database

If you need to reset your local Supabase database and populate it with fresh data:

1. **Reset the database**:
   ```bash
   npx supabase db reset
   ```

2. **Run the schema creation script**:
   ```bash
   # Option 1: Using the Supabase Studio UI
   # Access http://localhost:54323
   # Go to the SQL Editor
   # Load and execute postgres.sql

   # Option 2: Using the command line
   psql -h localhost -p 5432 -U postgres -d postgres -f postgres.sql
   ```

3. **Generate and insert synthetic data**:
   ```bash
   # Generate synthetic data
   cd gateway
   python -m data.synthetic_data_generator --total 500

   # Insert the generated data
   psql -h localhost -p 5432 -U postgres -d postgres -f data/out/insert_statements.sql
   ```

## Database Schema

The system uses a relational database schema with the following main tables:

- **Universities**: Information about universities
- **Programs**: Academic programs offered by universities
- **ExistingStudents**: Current student information with various subsections
- **AspiringStudents**: Prospective student information with preference subsections
- **Recommendations**: Generated university recommendations with similarity scores
- **SimilarStudents**: Links between aspiring students and similar existing students

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

This data forms the knowledge base for the recommendation system.

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

## Recommendation Output

The system provides comprehensive recommendation results including:

1. **Ranked Universities**: Based on overall similarity and fit
2. **Category-Specific Scores**: Detailed breakdown of similarity across 8 dimensions:
   - Academic Interest Similarity
   - Social and Cultural Compatibility
   - Financial Feasibility
   - Career Prospects
   - Geographic Preferences
   - Campus Facilities
   - Reputation and Brand Value
   - Personal Fit
3. **Similar Existing Students**: Profiles of current students with similar preferences
4. **Justification**: Natural language explanation of why each university is recommended

## API Endpoints

The system provides the following key endpoints:

- **POST /register/**: Register a new user account
- **POST /token**: Login and get an access token
- **POST /save_questionaire/{username}**: Save a completed aspiring student questionnaire
- **GET /recommendation/{username}**: Generate university recommendations
- **GET /recommendation/all_details/{username}**: Get comprehensive details for all recommendations
- **GET /recommendation/detail/{username}/{recommendation_id}**: Get details for a specific recommendation
- **GET /recommendation/similar_student/{username}/{recommendation_id}**: Get similar students for a recommendation

For a complete list of endpoints, refer to the Swagger documentation at http://localhost:8000/docs when running the API.

## Advanced Features

### Text Embedding and Efficient Similarity Search

For free-text responses, the system uses:
- **Sentence Transformers**: Converts text to numerical embeddings
- **HNSW (Hierarchical Navigable Small World)**: Enables efficient similarity search in high-dimensional spaces

### Vector-Based Recommendations

The system utilizes vector similarity search for efficient and accurate matching:
1. Student profiles are converted to high-dimensional vectors
2. Fast HNSW indexing enables efficient similarity computation
3. Weighted category scores ensure personalized recommendations

### Customizable Weights

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

## Performance Considerations

- The HNSW indexing enables efficient similarity search even with large numbers of student profiles
- The system is designed to balance precision with computational efficiency
- For large deployments, consider scaling the database and possibly implementing caching

## Contributing

Contributions to improve the system are welcome. Please feel free to submit issues or pull requests.

## License

[Insert your license information here]