CREATE EXTENSION vector;

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    age integer,
    gender text,
    nationality text,
    qualification text,
    high_school_gpa double precision,
    university text,
    major text,
    selection_criteria text[],
    considered_others boolean,
    second_choice text,
    satisfaction integer,
    university_tags text[],
    learning_style text,
    population_preference text,
    campus_setting text,
    cost_importance integer,
    scholarship boolean,
    living text,
    career_goal text,
    internship_importance integer,
    university_internship boolean,
    family_influence integer,
    friend_influence integer,
    social_media_influence integer,
    ranking_influence integer,
    user_embedding public.vector(384)
);

CREATE TABLE public.universities (
    id integer NOT NULL,
    university_name text NOT NULL,
    selection_criteria text[],
    average_satisfaction double precision,
    university_embedding public.vector(384),
    university_tags text[]
);

-- Create HNSW index for faster similarity search
CREATE INDEX idx_profiles_embedding_hnsw 
ON user_profiles 
USING hnsw (user_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Add composite index for frequently queried fields
CREATE INDEX idx_profiles_university_satisfaction 
ON user_profiles(university, satisfaction);

-- Add GiST index for vector search
CREATE INDEX idx_profiles_embedding 
ON user_profiles USING ivfflat (user_embedding vector_cosine_ops)
WITH (lists = 100);

-- Drop the existing function if it exists
DROP FUNCTION IF EXISTS match_user_profiles;

-- Create the function with corrected types
CREATE OR REPLACE FUNCTION match_user_profiles(
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  similarity float,
  university varchar(255),  -- Changed from text to varchar to match table schema
  satisfaction int,        -- Explicitly set as int
  selection_criteria varchar[],  -- Changed from text[] to varchar[] to match table schema
  university_tags varchar[]      -- Changed from text[] to varchar[] to match table schema
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    1 - (up.user_embedding <=> query_embedding) as similarity,
    up.university::varchar(255),  -- Explicit cast to varchar
    up.satisfaction,
    up.selection_criteria::varchar[],  -- Explicit cast to varchar array
    up.university_tags::varchar[]      -- Explicit cast to varchar array
  FROM user_profiles up
  WHERE 1 - (up.user_embedding <=> query_embedding) > match_threshold
  AND up.user_embedding IS NOT NULL
  ORDER BY up.user_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;