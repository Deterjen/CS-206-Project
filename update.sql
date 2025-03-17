-- Create new table with desired structure
CREATE TABLE similar_students_new (
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

-- Copy data from old to new table
INSERT INTO similar_students_new (id, recommendation_id, existing_student_id, similarity_score, created_at)
SELECT id, recommendation_id, existing_student_id, similarity_score, created_at FROM similar_students;

-- Drop old table and rename new one
DROP TABLE similar_students;
ALTER TABLE similar_students_new RENAME TO similar_students;

-- Start a transaction
BEGIN;

-- Truncate all tables in the correct order (reverse dependency order)
TRUNCATE TABLE 
    similar_students,
    recommendation_feedback,
    recommendations,
    existing_students_additional_insights,
    existing_students_selection_criteria,
    existing_students_personal_fit,
    existing_students_reputation,
    existing_students_facilities,
    existing_students_financial,
    existing_students_career,
    existing_students_social,
    existing_students_academic,
    existing_students_university_info,
    aspiring_students_personal_fit,
    aspiring_students_reputation,
    aspiring_students_facilities,
    aspiring_students_geographic,
    aspiring_students_financial,
    aspiring_students_career,
    aspiring_students_social,
    aspiring_students_academic,
    existing_students,
    aspiring_students,
    programs,
    universities
CASCADE;

-- Reset all sequences to start from 1
ALTER SEQUENCE universities_id_seq RESTART WITH 1;
ALTER SEQUENCE programs_id_seq RESTART WITH 1;
ALTER SEQUENCE existing_students_id_seq RESTART WITH 1;
ALTER SEQUENCE aspiring_students_id_seq RESTART WITH 1;
ALTER SEQUENCE recommendations_id_seq RESTART WITH 1;
ALTER SEQUENCE similar_students_id_seq RESTART WITH 1;
-- Add any other sequences that need resetting

-- Commit the transaction
COMMIT;