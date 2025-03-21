-- Core tables
CREATE TABLE universities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    size TEXT, -- Small (<5K), Medium (~10K), Large (>20K)
    setting TEXT, -- Urban or Rural
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities (id),
    name TEXT NOT NULL,
    department TEXT,
    degree_level TEXT, -- Undergraduate, Graduate, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Existing Students tables
CREATE TABLE existing_students (
    id SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities (id),
    program_id INTEGER REFERENCES programs (id),
    year_of_study TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_university_info (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    overall_satisfaction INTEGER, -- 1-10
    university_match INTEGER, -- 1-10
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_academic (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    teaching_quality INTEGER, -- 1-10
    learning_styles TEXT [], -- Array of selected options
    professor_accessibility INTEGER, -- 1-10
    academic_resources INTEGER, -- 1-10
    academic_credentials JSONB, -- To store various credential fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_social (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    campus_culture TEXT [], -- Array of selected options
    extracurricular_activities TEXT [], -- Array of selected options
    weekly_extracurricular_hours TEXT,
    social_groups_ease INTEGER, -- 1-10
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_career (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    job_placement_support INTEGER, -- 1-10
    internship_experience BOOLEAN,
    career_services_helpfulness INTEGER, -- 1-10
    alumni_network_strength INTEGER, -- 1-10
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_financial (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    affordability INTEGER, -- 1-10
    received_financial_aid BOOLEAN,
    financial_aid_percentage TEXT, -- 0-25%, 26-50%, etc.
    campus_employment_availability INTEGER, -- 1-10
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_facilities (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    facilities_quality INTEGER, -- 1-10
    regularly_used_facilities TEXT [], -- Array of selected options
    housing_quality INTEGER, -- 1-10, with N/A option
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_reputation (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    ranking_importance INTEGER, -- 1-10
    employer_value_perception INTEGER, -- 1-10
    important_reputation_aspects TEXT [], -- Array of selected options
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_personal_fit (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    personality_match INTEGER, -- 1-10
    typical_student_traits TEXT [], -- Array of selected options
    would_choose_again TEXT,
    thriving_student_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_selection_criteria (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    important_decision_factors TEXT [], -- Array of selected options
    retrospective_important_factors TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_additional_insights (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES existing_students (id),
    university_strengths TEXT,
    university_weaknesses TEXT,
    prospective_student_advice TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User to track account
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- is_disabled BOOLEAN NOT NUll DEFAULT FALSE
);

-- Aspiring Students tables
CREATE TABLE aspiring_students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id), -- Add foreign key to users table
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


CREATE TABLE aspiring_students_academic (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    preferred_fields TEXT [], -- Array of selected options
    learning_style TEXT,
    career_goals TEXT,
    further_education TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_social (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    culture_importance INTEGER, -- 1-10
    interested_activities TEXT [], -- Array of selected options
    weekly_extracurricular_hours TEXT,
    passionate_activities TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_career (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    internship_importance INTEGER, -- 1-10
    leadership_interest BOOLEAN,
    alumni_network_value INTEGER, -- 1-10
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_financial (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    affordability_importance INTEGER, -- 1-10
    yearly_budget NUMERIC,
    financial_aid_interest BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_geographic (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    preferred_region TEXT,
    preferred_setting TEXT, -- Urban or Rural
    preferred_living_arrangement TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_facilities (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    important_facilities TEXT [], -- Array of selected options
    modern_amenities_importance INTEGER, -- 1-10
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_reputation (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    ranking_importance INTEGER, -- 1-10
    alumni_testimonial_influence INTEGER, -- 1-10
    important_selection_factors TEXT [], -- Array of selected options
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_personal_fit (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES aspiring_students (id),
    personality_traits TEXT [], -- Array of selected options
    preferred_student_population TEXT,
    lifestyle_preferences TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recommendations tracking
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    aspiring_student_id INTEGER REFERENCES aspiring_students (id),
    university_id INTEGER REFERENCES universities (id),
    overall_score FLOAT,
    academic_score FLOAT,
    social_score FLOAT,
    financial_score FLOAT,
    career_score FLOAT,
    geographic_score FLOAT,
    facilities_score FLOAT,
    reputation_score FLOAT,
    personal_fit_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE similar_students (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations(id),
    existing_student_id INTEGER REFERENCES existing_students(id),
    similarity_score FLOAT,
    academic_similarity FLOAT,
    social_similarity FLOAT, 
    financial_similarity FLOAT,
    career_similarity FLOAT,
    geographic_similarity FLOAT,
    facilities_similarity FLOAT,
    reputation_similarity FLOAT,
    personal_fit_similarity FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback tracking for model improvement
CREATE TABLE recommendation_feedback (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations (id),
    feedback_rating INTEGER, -- 1-5
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);