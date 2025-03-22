-- Core tables
CREATE TABLE universities
(
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    location   TEXT NOT NULL,
    size       TEXT, -- Small (<5K), Medium (~10K), Large (>20K)
    setting    TEXT, -- Urban or Rural
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE programs
(
    id            SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities (id),
    name          TEXT NOT NULL,
    department    TEXT,
    degree_level  TEXT, -- Undergraduate, Graduate, etc.
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Existing Students tables
CREATE TABLE existing_students
(
    id            SERIAL PRIMARY KEY,
    university_id INTEGER REFERENCES universities (id),
    program_id    INTEGER REFERENCES programs (id),
    year_of_study TEXT,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_university_info
(
    id                   SERIAL PRIMARY KEY,
    student_id           INTEGER REFERENCES existing_students (id),
    overall_satisfaction INTEGER, -- 1-10
    university_match     INTEGER, -- 1-10
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_academic
(
    id                      SERIAL PRIMARY KEY,
    student_id              INTEGER REFERENCES existing_students (id),
    teaching_quality        INTEGER, -- 1-10
    learning_styles         TEXT[],  -- Array of selected options
    professor_accessibility INTEGER, -- 1-10
    academic_resources      INTEGER, -- 1-10
    academic_credentials    JSONB,   -- To store various credential fields
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_social
(
    id                           SERIAL PRIMARY KEY,
    student_id                   INTEGER REFERENCES existing_students (id),
    campus_culture               TEXT[],  -- Array of selected options
    extracurricular_activities   TEXT[],  -- Array of selected options
    weekly_extracurricular_hours TEXT,
    social_groups_ease           INTEGER, -- 1-10
    created_at                   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_career
(
    id                          SERIAL PRIMARY KEY,
    student_id                  INTEGER REFERENCES existing_students (id),
    job_placement_support       INTEGER, -- 1-10
    internship_experience       BOOLEAN,
    career_services_helpfulness INTEGER, -- 1-10
    alumni_network_strength     INTEGER, -- 1-10
    created_at                  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_financial
(
    id                             SERIAL PRIMARY KEY,
    student_id                     INTEGER REFERENCES existing_students (id),
    affordability                  INTEGER, -- 1-10
    received_financial_aid         BOOLEAN,
    financial_aid_percentage       TEXT,    -- 0-25%, 26-50%, etc.
    campus_employment_availability INTEGER, -- 1-10
    created_at                     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_facilities
(
    id                        SERIAL PRIMARY KEY,
    student_id                INTEGER REFERENCES existing_students (id),
    facilities_quality        INTEGER, -- 1-10
    regularly_used_facilities TEXT[],  -- Array of selected options
    housing_quality           INTEGER, -- 1-10, with N/A option
    created_at                TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_reputation
(
    id                           SERIAL PRIMARY KEY,
    student_id                   INTEGER REFERENCES existing_students (id),
    ranking_importance           INTEGER, -- 1-10
    employer_value_perception    INTEGER, -- 1-10
    important_reputation_aspects TEXT[],  -- Array of selected options
    created_at                   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_personal_fit
(
    id                     SERIAL PRIMARY KEY,
    student_id             INTEGER REFERENCES existing_students (id),
    personality_match      INTEGER, -- 1-10
    typical_student_traits TEXT[],  -- Array of selected options
    would_choose_again     TEXT,
    thriving_student_type  TEXT,
    created_at             TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_selection_criteria
(
    id                              SERIAL PRIMARY KEY,
    student_id                      INTEGER REFERENCES existing_students (id),
    important_decision_factors      TEXT[], -- Array of selected options
    retrospective_important_factors TEXT,
    created_at                      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE existing_students_additional_insights
(
    id                         SERIAL PRIMARY KEY,
    student_id                 INTEGER REFERENCES existing_students (id),
    university_strengths       TEXT,
    university_weaknesses      TEXT,
    prospective_student_advice TEXT,
    created_at                 TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User to track account
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_social
(
    id                           SERIAL PRIMARY KEY,
    student_id                   INTEGER REFERENCES aspiring_students (id),
    culture_importance           INTEGER, -- 1-10
    interested_activities        TEXT[],  -- Array of selected options
    weekly_extracurricular_hours TEXT,
    passionate_activities        TEXT,
    created_at                   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_career
(
    id                    SERIAL PRIMARY KEY,
    student_id            INTEGER REFERENCES aspiring_students (id),
    internship_importance INTEGER, -- 1-10
    leadership_interest   BOOLEAN,
    alumni_network_value  INTEGER, -- 1-10
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_financial
(
    id                       SERIAL PRIMARY KEY,
    student_id               INTEGER REFERENCES aspiring_students (id),
    affordability_importance INTEGER, -- 1-10
    yearly_budget            NUMERIC,
    financial_aid_interest   BOOLEAN,
    created_at               TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_geographic
(
    id                           SERIAL PRIMARY KEY,
    student_id                   INTEGER REFERENCES aspiring_students (id),
    preferred_region             TEXT,
    preferred_setting            TEXT, -- Urban or Rural
    preferred_living_arrangement TEXT,
    created_at                   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_facilities
(
    id                          SERIAL PRIMARY KEY,
    student_id                  INTEGER REFERENCES aspiring_students (id),
    important_facilities        TEXT[],  -- Array of selected options
    modern_amenities_importance INTEGER, -- 1-10
    created_at                  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_reputation
(
    id                           SERIAL PRIMARY KEY,
    student_id                   INTEGER REFERENCES aspiring_students (id),
    ranking_importance           INTEGER, -- 1-10
    alumni_testimonial_influence INTEGER, -- 1-10
    important_selection_factors  TEXT[],  -- Array of selected options
    created_at                   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE aspiring_students_personal_fit
(
    id                           SERIAL PRIMARY KEY,
    student_id                   INTEGER REFERENCES aspiring_students (id),
    personality_traits           TEXT[], -- Array of selected options
    preferred_student_population TEXT,
    lifestyle_preferences        TEXT,
    created_at                   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recommendations tracking
CREATE TABLE recommendations
(
    id                  SERIAL PRIMARY KEY,
    aspiring_student_id INTEGER REFERENCES aspiring_students (id),
    university_id       INTEGER REFERENCES universities (id),
    overall_score       FLOAT,
    academic_score      FLOAT,
    social_score        FLOAT,
    financial_score     FLOAT,
    career_score        FLOAT,
    geographic_score    FLOAT,
    facilities_score    FLOAT,
    reputation_score    FLOAT,
    personal_fit_score  FLOAT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE similar_students
(
    id                      SERIAL PRIMARY KEY,
    recommendation_id       INTEGER REFERENCES recommendations (id),
    existing_student_id     INTEGER REFERENCES existing_students (id),
    similarity_score        FLOAT,
    academic_similarity     FLOAT,
    social_similarity       FLOAT,
    financial_similarity    FLOAT,
    career_similarity       FLOAT,
    geographic_similarity   FLOAT,
    facilities_similarity   FLOAT,
    reputation_similarity   FLOAT,
    personal_fit_similarity FLOAT,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback tracking for model improvement
CREATE TABLE recommendation_feedback
(
    id                SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations (id),
    feedback_rating   INTEGER, -- 1-5
    feedback_text     TEXT,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- No need to modify existing tables as they already capture all required fields from questionnaires

-- Add additional index to improve recommendation queries performance
CREATE INDEX idx_recommendations_aspiring_student_id ON recommendations (aspiring_student_id);
CREATE INDEX idx_similar_students_recommendation_id ON similar_students (recommendation_id);
CREATE INDEX idx_similar_students_existing_student_id ON similar_students (existing_student_id);

-- Add index on universities to speed up recommendation lookups
CREATE INDEX idx_universities_location ON universities (location);
CREATE INDEX idx_universities_setting ON universities (setting);
CREATE INDEX idx_universities_size ON universities (size);

-- Add logging table to track recommendation performance
CREATE TABLE recommendation_performance_logs
(
    id                       SERIAL PRIMARY KEY,
    aspiring_student_id      INTEGER REFERENCES aspiring_students (id),
    timestamp                TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    universities_recommended INTEGER,
    top_similarity_score     FLOAT,
    average_similarity_score FLOAT,
    processing_time_ms       INTEGER,
    metadata                 JSONB
);

-- Add view to easily query student profiles with universities
CREATE VIEW student_university_view AS
SELECT es.id  as student_id,
       u.id   as university_id,
       u.name as university_name,
       u.location,
       u.size,
       u.setting,
       es.year_of_study,
       p.name as program_name,
       p.department,
       p.degree_level
FROM existing_students es
         JOIN
     universities u ON es.university_id = u.id
         JOIN
     programs p ON es.program_id = p.id;

-- Add view to easily query recommendation statistics
CREATE VIEW recommendation_statistics AS
SELECT r.aspiring_student_id,
       COUNT(DISTINCT r.university_id) as unique_universities,
       AVG(r.overall_score)            as avg_recommendation_score,
       MAX(r.overall_score)            as max_recommendation_score,
       MIN(r.overall_score)            as min_recommendation_score,
       COUNT(ss.id)                    as total_similar_students,
       AVG(ss.similarity_score)        as avg_similarity_score
FROM recommendations r
         LEFT JOIN
     similar_students ss ON r.id = ss.recommendation_id
GROUP BY r.aspiring_student_id;

-- Create indexes to optimize recommendation queries
CREATE INDEX IF NOT EXISTS idx_existing_students_university_id ON existing_students(university_id);

-- Create materialized view to cache top students per university for faster recommendations
CREATE MATERIALIZED VIEW IF NOT EXISTS top_university_students AS
WITH ranked_students AS (
    SELECT
        es.id AS student_id,
        es.university_id,
        esui.overall_satisfaction,
        esa.teaching_quality,
        esc.job_placement_support,
        ROW_NUMBER() OVER (PARTITION BY es.university_id ORDER BY
            (esui.overall_satisfaction + esa.teaching_quality + esc.job_placement_support) / 3.0 DESC
        ) AS rank
    FROM
        existing_students es
    JOIN
        existing_students_university_info esui ON es.id = esui.student_id
    JOIN
        existing_students_academic esa ON es.id = esa.student_id
    JOIN
        existing_students_career esc ON es.id = esc.student_id
)
SELECT
    student_id,
    university_id,
    overall_satisfaction,
    teaching_quality,
    job_placement_support,
    rank
FROM
    ranked_students
WHERE
    rank <= 100; -- Keep top 100 students per university

-- Create index on the materialized view
CREATE INDEX IF NOT EXISTS idx_top_university_students_university_id ON top_university_students(university_id);

-- Create a refresh function for the materialized view
CREATE OR REPLACE FUNCTION refresh_top_university_students()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW top_university_students;
END;
$$ LANGUAGE plpgsql;

-- Add a trigger to update the materialized view when needed
CREATE OR REPLACE FUNCTION check_refresh_top_university_students()
RETURNS TRIGGER AS $$
BEGIN
    -- Determine if refresh is needed based on change count
    IF (SELECT count(*) FROM recommendation_performance_logs WHERE timestamp >
        (SELECT COALESCE(MAX(timestamp), NOW() - INTERVAL '1 day')
         FROM recommendation_performance_logs
         WHERE metadata->>'refreshed_views' = 'true')) > 10 THEN

        -- Refresh the view and log it
        PERFORM refresh_top_university_students();

        -- Log the refresh
        INSERT INTO recommendation_performance_logs (
            aspiring_student_id,
            timestamp,
            universities_recommended,
            top_similarity_score,
            average_similarity_score,
            metadata
        ) VALUES (
            NULL,
            NOW(),
            0,
            0,
            0,
            '{"refreshed_views": "true", "reason": "threshold_reached"}'::jsonb
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger on recommendation logs
DROP TRIGGER IF EXISTS trg_check_refresh_top_university_students ON recommendation_performance_logs;
CREATE TRIGGER trg_check_refresh_top_university_students
AFTER INSERT ON recommendation_performance_logs
FOR EACH ROW
EXECUTE FUNCTION check_refresh_top_university_students();

-- Create database functions and views to support efficient queries


-- 2. View for existing students complete data
-- Create the complete view for existing students (used for efficient data retrieval)
CREATE OR REPLACE VIEW existing_students_complete_view AS
SELECT
    es.id,
    es.university_id,
    es.program_id,
    es.year_of_study,
    es.created_at,

    -- University Info
    esui.overall_satisfaction,
    esui.university_match,

    -- Academic
    esa.teaching_quality,
    esa.learning_styles,
    esa.professor_accessibility,
    esa.academic_resources,
    esa.academic_credentials,

    -- Social
    ess.campus_culture,
    ess.extracurricular_activities,
    ess.weekly_extracurricular_hours,
    ess.social_groups_ease,

    -- Career
    esc.job_placement_support,
    esc.internship_experience,
    esc.career_services_helpfulness,
    esc.alumni_network_strength,

    -- Financial
    esf.affordability,
    esf.received_financial_aid,
    esf.financial_aid_percentage,
    esf.campus_employment_availability,

    -- Facilities
    esfa.facilities_quality,
    esfa.regularly_used_facilities,
    esfa.housing_quality,

    -- Reputation
    esr.ranking_importance,
    esr.employer_value_perception,
    esr.important_reputation_aspects,

    -- Personal Fit
    espf.personality_match,
    espf.typical_student_traits,
    espf.would_choose_again,
    espf.thriving_student_type,

    -- Selection Criteria
    essc.important_decision_factors,
    essc.retrospective_important_factors,

    -- Additional Insights
    esai.university_strengths,
    esai.university_weaknesses,
    esai.prospective_student_advice
FROM
    existing_students es
LEFT JOIN
    existing_students_university_info esui ON es.id = esui.student_id
LEFT JOIN
    existing_students_academic esa ON es.id = esa.student_id
LEFT JOIN
    existing_students_social ess ON es.id = ess.student_id
LEFT JOIN
    existing_students_career esc ON es.id = esc.student_id
LEFT JOIN
    existing_students_financial esf ON es.id = esf.student_id
LEFT JOIN
    existing_students_facilities esfa ON es.id = esfa.student_id
LEFT JOIN
    existing_students_reputation esr ON es.id = esr.student_id
LEFT JOIN
    existing_students_personal_fit espf ON es.id = espf.student_id
LEFT JOIN
    existing_students_selection_criteria essc ON es.id = essc.student_id
LEFT JOIN
    existing_students_additional_insights esai ON es.id = esai.student_id;


-- 4. View for aspiring student complete data
CREATE OR REPLACE VIEW aspiring_student_complete_view AS
SELECT
    as1.id,
    as1.created_at,

    -- Academic
    asa.preferred_fields,
    asa.learning_style,
    asa.career_goals,
    asa.further_education,

    -- Social
    ass.culture_importance,
    ass.interested_activities,
    ass.weekly_extracurricular_hours,
    ass.passionate_activities,

    -- Career
    ascareer.internship_importance,
    ascareer.leadership_interest,
    ascareer.alumni_network_value,

    -- Financial
    asf.affordability_importance,
    asf.yearly_budget,
    asf.financial_aid_interest,

    -- Geographic
    asg.preferred_region,
    asg.preferred_setting,
    asg.preferred_living_arrangement,

    -- Facilities
    asfa.important_facilities,
    asfa.modern_amenities_importance,

    -- Reputation
    asr.ranking_importance,
    asr.alumni_testimonial_influence,
    asr.important_selection_factors,

    -- Personal Fit
    aspf.personality_traits,
    aspf.preferred_student_population,
    aspf.lifestyle_preferences
FROM
    aspiring_students as1
LEFT JOIN
    aspiring_students_academic asa ON as1.id = asa.student_id
LEFT JOIN
    aspiring_students_social ass ON as1.id = ass.student_id
LEFT JOIN
    aspiring_students_career ascareer ON as1.id = ascareer.student_id
LEFT JOIN
    aspiring_students_financial asf ON as1.id = asf.student_id
LEFT JOIN
    aspiring_students_geographic asg ON as1.id = asg.student_id
LEFT JOIN
    aspiring_students_facilities asfa ON as1.id = asfa.student_id
LEFT JOIN
    aspiring_students_reputation asr ON as1.id = asr.student_id
LEFT JOIN
    aspiring_students_personal_fit aspf ON as1.id = aspf.student_id;


-- 6. View for recommendation details
CREATE OR REPLACE VIEW recommendation_details_view AS
SELECT
    r.id,
    r.aspiring_student_id,
    r.university_id,
    r.overall_score,
    r.academic_score,
    r.social_score,
    r.financial_score,
    r.career_score,
    r.geographic_score,
    r.facilities_score,
    r.reputation_score,
    r.personal_fit_score,
    r.created_at,

    -- University data as JSON
    jsonb_build_object(
        'id', u.id,
        'name', u.name,
        'location', u.location,
        'size', u.size,
        'setting', u.setting,
        'created_at', u.created_at
    ) AS university,

    -- Similar students as JSON array
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'id', ss.id,
                'student_id', ss.existing_student_id,
                'overall_similarity', ss.similarity_score,
                'academic_similarity', ss.academic_similarity,
                'social_similarity', ss.social_similarity,
                'financial_similarity', ss.financial_similarity,
                'career_similarity', ss.career_similarity,
                'geographic_similarity', ss.geographic_similarity,
                'facilities_similarity', ss.facilities_similarity,
                'reputation_similarity', ss.reputation_similarity,
                'personal_fit_similarity', ss.personal_fit_similarity,
                'university_id', es.university_id,
                'university_name', u2.name
            )
        )
        FROM similar_students ss
        JOIN existing_students es ON ss.existing_student_id = es.id
        JOIN universities u2 ON es.university_id = u2.id
        WHERE ss.recommendation_id = r.id),
        '[]'::jsonb
    ) AS similar_students
FROM
    recommendations r
JOIN
    universities u ON r.university_id = u.id;