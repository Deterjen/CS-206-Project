import ast
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('../.env.local')


class UniversityRecommendationDataIngestor:
    def __init__(
            self,
            supabase_url: str,
            supabase_key: str,
            edge_function_url: str = None,
            auto_setup: bool = True
    ):
        """
        Initialize the data ingestor with Supabase credentials.

        Args:
            supabase_url: Your Supabase project URL
            supabase_key: Your Supabase service role key (needs full access)
            edge_function_url: URL to the embeddings edge function
            auto_setup: If True, check and create tables if they don't exist
        """
        self.supabase = create_client(supabase_url, supabase_key)
        self.edge_function_url = edge_function_url or f"{supabase_url}/functions/v1/embed"
        self.users_columns = None  # Will be populated with column names from the users table

        if auto_setup:
            self.setup_database()

    def setup_database(self):
        """
        Check if required tables exist and create them if necessary.
        This helps ensure the database is properly set up before ingestion.
        """
        try:
            # Check if users table exists
            try:
                # Use a valid Supabase query syntax
                self.supabase.from_("users").select("id", count="exact").limit(1).execute()
                print("✓ Users table exists")
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    print("Creating users table...")
                    self._create_users_table()
                else:
                    print(f"Error checking users table: {e}")

            # Check if user_activities table exists
            try:
                self.supabase.from_("user_activities").select("id", count="exact").limit(1).execute()
                print("✓ User activities table exists")
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    print("Creating user_activities table...")
                    self._create_user_activities_table()
                else:
                    print(f"Error checking user_activities table: {e}")

            # Check if universities table exists
            try:
                self.supabase.from_("universities").select("id", count="exact").limit(1).execute()
                print("✓ Universities table exists")
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    print("Creating universities table...")
                    self._create_universities_table()
                else:
                    print(f"Error checking universities table: {e}")

            # Check if user_selections table exists
            try:
                self.supabase.from_("user_selections").select("id", count="exact").limit(1).execute()
                print("✓ User selections table exists")
            except Exception as e:
                if "relation" in str(e) and "does not exist" in str(e):
                    print("Creating user_selections table...")
                    self._create_user_selections_table()
                else:
                    print(f"Error checking user_selections table: {e}")

            # Now that tables exist, get schema information
            self._get_database_schema()

        except Exception as e:
            print(f"Error during database setup: {e}")

    def _create_users_table(self):
        """Create the users table with required schema"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),

            -- Basic Information
            age TEXT,
            gender TEXT,
            nationality TEXT,
            student_status TEXT,
            prior_qualification TEXT,
            prior_gpa TEXT,

            -- Learning & School Preferences
            learning_style TEXT,
            preferred_population TEXT,
            preferred_campus TEXT,
            plans_further_education NUMERIC,

            -- Academic & Career
            school TEXT,
            career_goal TEXT,

            -- Financial
            cost_importance INTEGER,
            has_scholarship INTEGER,
            funding_source TEXT,
            scholarship_significance INTEGER,

            -- Social & Extra-curricular
            personality TEXT,
            leadership_role INTEGER,
            extracurricular_hours INTEGER,
            extracurricular_type TEXT,
            cca_count INTEGER,

            -- Influence Factors
            family_influence INTEGER,
            friend_influence INTEGER,
            social_media_influence INTEGER,
            ranking_influence INTEGER,
            extracurricular_importance INTEGER,
            culture_importance INTEGER,
            internship_importance INTEGER,

            -- Residence & Experience
            residence TEXT,
            internship_participation INTEGER,

            -- Embeddings
            profile_embedding VECTOR(384),
            preferences_embedding VECTOR(384)
        );

        -- Create HNSW index on profile embedding
        CREATE INDEX IF NOT EXISTS idx_users_profile_embedding 
        ON users USING hnsw (profile_embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);

        -- Create HNSW index on preferences embedding
        CREATE INDEX IF NOT EXISTS idx_users_preferences_embedding 
        ON users USING hnsw (preferences_embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
        """

        try:
            # Execute SQL through Supabase
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            print("Users table created successfully")
        except Exception as e:
            print(f"Error creating users table: {e}")

    def _create_universities_table(self):
        """Create the universities table with required schema"""
        sql = """
        CREATE TABLE IF NOT EXISTS universities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),

            name TEXT NOT NULL,
            abbreviation TEXT,
            location TEXT,

            description TEXT,
            student_population INTEGER,
            campus_type TEXT,

            -- Academic Info
            available_schools TEXT[],
            research_focus TEXT[],
            teaching_style TEXT,

            -- Campus Life
            campus_culture TEXT,
            extracurricular_offerings TEXT[],
            housing_options TEXT[],

            -- Rankings & Reputation
            overall_ranking INTEGER,
            reputation_score NUMERIC,

            -- Financial
            tuition_domestic NUMERIC,
            tuition_international NUMERIC,
            scholarship_availability TEXT,

            -- Embeddings
            profile_embedding VECTOR(384)
        );

        -- Create HNSW index on university profile embedding
        CREATE INDEX IF NOT EXISTS idx_universities_profile_embedding 
        ON universities USING hnsw (profile_embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
        """

        try:
            # Execute SQL through Supabase
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            print("Universities table created successfully")
        except Exception as e:
            print(f"Error creating universities table: {e}")

    def _create_user_activities_table(self):
        """Create the user_activities table with required schema"""
        sql = """
        CREATE TABLE IF NOT EXISTS user_activities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,

            cca_list TEXT[],
            cca_types TEXT[],

            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );

        -- Create index on user_id for faster lookups
        CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id);
        """

        try:
            # Execute SQL through Supabase
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            print("User activities table created successfully")
        except Exception as e:
            print(f"Error creating user_activities table: {e}")

    def _create_user_selections_table(self):
        """Create the user_selections table with required schema"""
        sql = """
        CREATE TABLE IF NOT EXISTS user_selections (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            university_id UUID REFERENCES universities(id) ON DELETE CASCADE,

            is_attending BOOLEAN,
            is_second_choice BOOLEAN,

            satisfaction_rating INTEGER,
            satisfaction_group TEXT,
            university_description TEXT,
            selection_criteria TEXT[],

            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),

            UNIQUE(user_id, university_id)
        );

        -- Create indexes for faster lookups
        CREATE INDEX IF NOT EXISTS idx_user_selections_user_id ON user_selections(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_selections_university_id ON user_selections(university_id);
        """

        try:
            # Execute SQL through Supabase
            self.supabase.rpc('exec_sql', {'sql': sql}).execute()
            print("User selections table created successfully")
        except Exception as e:
            print(f"Error creating user_selections table: {e}")

    def _get_database_schema(self):
        """
        Fetch the actual database schema to validate columns before insertion.
        This helps prevent errors from mismatched schema definitions.
        """
        try:
            # Try a simple select with a limit to get column information
            response = self.supabase.from_("users").select("*").limit(1).execute()

            if response and hasattr(response, 'data') and len(response.data) > 0:
                # Get column names from the first row
                self.users_columns = set(response.data[0].keys())
                print(f"Retrieved schema with {len(self.users_columns)} columns")
            else:
                # If no data exists, create a minimal required schema set
                # These are the essential columns we need for the system to work
                print("No user data found. Using default schema set.")
                self.users_columns = set([
                    'id', 'created_at', 'updated_at', 'age', 'gender',
                    'student_status', 'learning_style', 'preferred_population',
                    'cost_importance', 'has_scholarship', 'residence',
                    'culture_importance', 'school', 'plans_further_education',
                    'career_goal', 'internship_importance', 'internship_participation',
                    'family_influence', 'friend_influence', 'social_media_influence',
                    'ranking_influence', 'extracurricular_importance', 'personality',
                    'leadership_role', 'extracurricular_hours', 'extracurricular_type',
                    'profile_embedding', 'preferences_embedding'
                ])

        except Exception as e:
            print(f"Error retrieving database schema: {e}")
            # Fallback to safe default columns that match our table creation SQL
            print("Using fallback schema definition")
            self.users_columns = set([
                'id', 'created_at', 'updated_at', 'age', 'gender', 'nationality',
                'student_status', 'prior_qualification', 'prior_gpa',
                'learning_style', 'preferred_population', 'preferred_campus',
                'plans_further_education', 'school', 'career_goal',
                'cost_importance', 'has_scholarship', 'funding_source',
                'scholarship_significance', 'personality', 'leadership_role',
                'extracurricular_hours', 'extracurricular_type', 'cca_count',
                'family_influence', 'friend_influence', 'social_media_influence',
                'ranking_influence', 'extracurricular_importance', 'culture_importance',
                'internship_importance', 'residence', 'internship_participation',
                'profile_embedding', 'preferences_embedding'
            ])

    def _parse_list_column(self, column_value: str) -> List[str]:
        """Parse string representations of lists into actual Python lists."""
        if pd.isna(column_value) or not column_value:
            return []
        try:
            if isinstance(column_value, str):
                if column_value.startswith('[') and column_value.endswith(']'):
                    return ast.literal_eval(column_value)
                else:
                    return [item.strip() for item in column_value.split(',') if item.strip()]
            elif isinstance(column_value, list):
                return column_value
        except (SyntaxError, ValueError) as e:
            print(f"Error parsing list column: {e}")
            return []
        return []

    def _generate_profile_text(self, user_data: Dict[str, Any]) -> str:
        """
        Generate a text description of a user's profile for embedding.

        Args:
            user_data: Dictionary containing user data

        Returns:
            String containing a natural language description of the user's profile
        """
        profile_parts = []

        # Basic information
        if user_data.get('age'):
            profile_parts.append(f"Age group: {user_data['age']}.")

        if user_data.get('gender'):
            profile_parts.append(f"Gender: {user_data['gender']}.")

        if user_data.get('student_status'):
            profile_parts.append(f"{user_data['student_status']} student.")

        # Academic information
        if user_data.get('school'):
            profile_parts.append(f"Studies in the field of {user_data['school']}.")

        if user_data.get('career_goal'):
            profile_parts.append(f"Career goal: {user_data['career_goal']}.")

        if user_data.get('plans_further_education') is not None:
            if user_data['plans_further_education'] == 1:
                profile_parts.append("Plans to pursue further education after current degree.")
            elif user_data['plans_further_education'] == 0:
                profile_parts.append("Does not plan to pursue further education after current degree.")
            else:
                profile_parts.append("Undecided about pursuing further education after current degree.")

        # Personality and engagement
        if user_data.get('personality'):
            profile_parts.append(f"Describes self as {user_data['personality']}.")

        if user_data.get('leadership_role') == 1:
            profile_parts.append("Has leadership experience.")

        if user_data.get('extracurricular_hours') is not None:
            profile_parts.append(
                f"Spends approximately {user_data['extracurricular_hours']} hours per week on extracurricular activities.")

        if user_data.get('extracurricular_type'):
            profile_parts.append(f"Prefers {user_data['extracurricular_type']} activities.")

        if user_data.get('cca_count') and user_data.get('cca_count') > 0:
            cca_list = self._parse_list_column(user_data.get('cca_list', '[]'))
            if cca_list:
                activities = ', '.join(cca_list)
                profile_parts.append(f"Participates in: {activities}.")

        # Financial considerations
        if user_data.get('has_scholarship') == 1:
            profile_parts.append("Currently receives a scholarship.")

        if user_data.get('funding_source'):
            profile_parts.append(f"Education funded by: {user_data['funding_source']}.")

        return ' '.join(profile_parts)

    def _generate_preferences_text(self, user_data: Dict[str, Any]) -> str:
        """
        Generate a text description of a user's preferences for embedding.

        Args:
            user_data: Dictionary containing user data

        Returns:
            String containing a natural language description of the user's preferences
        """
        preference_parts = []

        # Learning preferences
        if user_data.get('learning_style'):
            preference_parts.append(f"Prefers {user_data['learning_style']} learning style.")

        if user_data.get('preferred_population'):
            preference_parts.append(f"Prefers {user_data['preferred_population'].lower()} student population.")

        # University selection criteria
        selection_criteria = self._parse_list_column(user_data.get('selection_criteria_list', '[]'))
        if selection_criteria:
            criteria_text = ', '.join(selection_criteria)
            preference_parts.append(f"Values these criteria in university selection: {criteria_text}.")

        # Financial preferences
        if user_data.get('cost_importance') is not None:
            importance = self._rate_importance(user_data['cost_importance'])
            preference_parts.append(f"Cost of education is {importance} important.")

        if user_data.get('scholarship_significance') is not None:
            significance = self._rate_importance(user_data['scholarship_significance'])
            preference_parts.append(f"Scholarship availability is {significance} significant.")

        # Cultural and social preferences
        if user_data.get('culture_importance') is not None:
            importance = self._rate_importance(user_data['culture_importance'])
            preference_parts.append(f"Campus culture is {importance} important.")

        if user_data.get('residence'):
            preference_parts.append(f"Prefers to {user_data['residence'].lower()}.")

        # Influence factors
        influence_factors = []
        if user_data.get('family_influence') and user_data['family_influence'] >= 3:
            influence_factors.append("family")

        if user_data.get('friend_influence') and user_data['friend_influence'] >= 3:
            influence_factors.append("friends")

        if user_data.get('social_media_influence') and user_data['social_media_influence'] >= 3:
            influence_factors.append("social media")

        if user_data.get('ranking_influence') and user_data['ranking_influence'] >= 3:
            influence_factors.append("university rankings")

        if influence_factors:
            influences = ', '.join(influence_factors)
            preference_parts.append(f"Influenced by {influences} when making university decisions.")

        # Career and development preferences
        if user_data.get('internship_importance') is not None:
            importance = self._rate_importance(user_data['internship_importance'])
            preference_parts.append(f"Internship and job placement opportunities are {importance} important.")

        if user_data.get('extracurricular_importance') is not None:
            importance = self._rate_importance(user_data['extracurricular_importance'])
            preference_parts.append(f"Availability of extracurricular activities is {importance} important.")

        return ' '.join(preference_parts)

    def _rate_importance(self, score: int) -> str:
        """Convert numerical importance scores to descriptive text."""
        if score is None:
            return "moderately"
        if score <= 2:
            return "minimally"
        elif score <= 4:
            return "somewhat"
        elif score <= 6:
            return "moderately"
        elif score <= 8:
            return "very"
        else:
            return "extremely"

    def generate_embeddings(self, users_data: List[Dict[str, Any]], batch_mode: bool = True) -> List[Dict[str, Any]]:
        """
        Generate embeddings for each user's profile and preferences.

        Args:
            users_data: List of dictionaries containing user data
            batch_mode: Whether to use batch mode for the embedding API

        Returns:
            List of dictionaries with user data including embeddings
        """
        headers = {"Content-Type": "application/json"}

        if batch_mode:
            # Prepare data for batch embedding
            texts_batch = []
            for user in users_data:
                profile_text = self._generate_profile_text(user)
                preferences_text = self._generate_preferences_text(user)
                texts_batch.append([profile_text, preferences_text])

            # Call the embedding function in batch mode
            # Sanitize the payload to ensure it's JSON serializable
            texts_batch_sanitized = []
            for profile_text, pref_text in texts_batch:
                # Ensure the texts are strings
                profile_text_safe = str(profile_text) if profile_text is not None else ""
                pref_text_safe = str(pref_text) if pref_text is not None else ""
                texts_batch_sanitized.append([profile_text_safe, pref_text_safe])

            payload = {"texts": texts_batch_sanitized, "batchMode": True}

            try:
                response = requests.post(self.edge_function_url, headers=headers, json=payload)

                if response.status_code != 200:
                    raise Exception(f"Error generating embeddings: {response.text}")

                results = response.json()
                embeddings_batch = results.get("embeddings", [])
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                # Fallback to empty embedding results
                embeddings_batch = []
            except Exception as e:
                print(f"Error calling embedding function: {e}")
                # Fallback to empty embedding results
                embeddings_batch = []

            # Associate embeddings with users
            for i, user in enumerate(users_data):
                if i < len(embeddings_batch):
                    user["profile_embedding"] = embeddings_batch[i][0]
                    user["preferences_embedding"] = embeddings_batch[i][1]
                else:
                    # Fallback for missing embeddings
                    user["profile_embedding"] = [0.0] * 384
                    user["preferences_embedding"] = [0.0] * 384

        else:
            # Process one user at a time
            for user in users_data:
                profile_text = self._generate_profile_text(user)
                preferences_text = self._generate_preferences_text(user)

                payload = {"texts": [profile_text, preferences_text], "batchMode": False}
                response = requests.post(self.edge_function_url, headers=headers, json=payload)

                if response.status_code != 200:
                    print(f"Warning: Error generating embeddings for a user: {response.text}")
                    # Fallback embeddings
                    user["profile_embedding"] = [0.0] * 384
                    user["preferences_embedding"] = [0.0] * 384
                    continue

                results = response.json()
                embeddings = results.get("embeddings", [[0.0] * 384, [0.0] * 384])
                user["profile_embedding"] = embeddings[0]
                user["preferences_embedding"] = embeddings[1]

        return users_data

    def _prepare_user_for_insert(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare user data for database insertion, handling special columns.

        Args:
            user_data: Dictionary containing user data

        Returns:
            Dictionary with properly formatted user data for database insertion
        """
        db_user = user_data.copy()

        # Parse list columns if needed
        if "selection_criteria_list" in db_user:
            db_user["selection_criteria"] = self._parse_list_column(db_user.pop("selection_criteria_list"))

        if "cca_list" in db_user:
            db_user["cca_list"] = self._parse_list_column(db_user["cca_list"])

        # Fetch schema if we haven't already
        if self.users_columns is None:
            self._get_database_schema()

        # Remove columns that don't exist in the database schema
        if self.users_columns:
            # Keep only columns that exist in the database schema
            # Plus 'cca_list' which we handle separately
            keys_to_keep = set(self.users_columns).union({'cca_list'})
            for key in list(db_user.keys()):
                if key not in keys_to_keep:
                    db_user.pop(key, None)
        else:
            # Fallback: remove known problematic columns
            columns_to_remove = [
                'satisfaction_group',
                'financial_consideration',
                'external_influence',
                'engagement_level',
                'engagement_category'
            ]
            for column in columns_to_remove:
                if column in db_user:
                    db_user.pop(column)

        # Handle float values to ensure JSON compliance
        for key, value in list(db_user.items()):
            if isinstance(value, float):
                if not np.isfinite(value):  # Check for NaN, Inf, -Inf
                    if np.isnan(value):
                        db_user[key] = None
                    elif np.isposinf(value):
                        db_user[key] = 1e38  # Use a very large but JSON-compliant value
                    elif np.isneginf(value):
                        db_user[key] = -1e38  # Use a very small but JSON-compliant value

        # Add timestamps
        now = datetime.now().isoformat()
        db_user["created_at"] = now
        db_user["updated_at"] = now

        return db_user

    def _store_user_activities(self, user_id: str, cca_list: List[str],
                               extracurricular_type: Optional[str]) -> bool:
        """
        Store user activities in the dedicated table.

        Args:
            user_id: UUID of the user
            cca_list: List of CCAs the user participates in
            extracurricular_type: Type of extracurricular activities the user prefers

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure cca_list is actually a list
            if isinstance(cca_list, str):
                cca_list = self._parse_list_column(cca_list)

            # Ensure extracurricular_type is a string
            if extracurricular_type is not None:
                extracurricular_type = str(extracurricular_type)

            activity_data = {
                "user_id": user_id,
                "cca_list": cca_list,
                "cca_types": [extracurricular_type] if extracurricular_type else []
            }

            # Handle empty arrays for PostgreSQL compatibility
            if not activity_data["cca_list"]:
                activity_data["cca_list"] = []
            if not activity_data["cca_types"]:
                activity_data["cca_types"] = []

            self.supabase.from_("user_activities").insert(activity_data).execute()
            return True
        except Exception as e:
            print(f"Error storing user activities: {e}")
            return False

    def ingest_survey_data(self, csv_path: str) -> Tuple[int, int, List[str]]:
        """
        Process survey data from CSV, generate embeddings, and store in database.

        Args:
            csv_path: Path to the CSV file containing survey data

        Returns:
            Tuple containing (number of processed records, number of successful inserts, errors)
        """
        # Ensure we have up-to-date schema information
        self._get_database_schema()

        # Read CSV data
        df = pd.read_csv(csv_path)

        # Pre-process to handle NaN and infinite values
        # Replace NaN with None for better JSON compatibility
        df = df.replace({np.nan: None})

        # Handle infinite values
        for col in df.select_dtypes(include=[np.float64]).columns:
            df[col] = df[col].apply(lambda x: None if x is None else
            (1e38 if np.isposinf(x) else
             (-1e38 if np.isneginf(x) else x)))

        # Convert to list of dictionaries
        users_data = df.to_dict(orient='records')
        print(f"Loaded {len(users_data)} user records from {csv_path}")

        # Generate embeddings
        try:
            users_with_embeddings = self.generate_embeddings(users_data)
            print(f"Generated embeddings for {len(users_with_embeddings)} users")
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return 0, 0, [str(e)]

        # Insert data into database
        successful_inserts = 0
        errors = []

        for user in users_with_embeddings:
            try:
                # Prepare user data
                db_user = self._prepare_user_for_insert(user)

                # Extract and remove data for the user_activities table
                cca_list = user.get("cca_list", [])
                if "cca_list" in db_user:
                    db_user.pop("cca_list")
                extracurricular_type = db_user.get("extracurricular_type")

                # Debug information - useful for troubleshooting
                print(f"Inserting user with fields: {list(db_user.keys())}")

                # Ensure embeddings are converted to proper format if needed
                for embed_field in ['profile_embedding', 'preferences_embedding']:
                    if embed_field in db_user and db_user[embed_field] is not None:
                        # Ensure it's a list of floats within JSON-compatible range
                        if isinstance(db_user[embed_field], list):
                            db_user[embed_field] = [
                                min(max(float(v), -1e38), 1e38) if v is not None else 0.0
                                for v in db_user[embed_field]
                            ]

                # Insert into users table
                try:
                    response = self.supabase.from_("users").insert(db_user).execute()

                    # Get the user ID
                    if not response.data or len(response.data) == 0:
                        print("Warning: No response data from user insert, but no error thrown")
                        successful_inserts += 1
                        continue

                    user_id = response.data[0]["id"]

                    # Store user activities
                    activity_success = self._store_user_activities(user_id, cca_list, extracurricular_type)
                    if not activity_success:
                        print(f"Warning: User inserted but activities storage failed")

                    successful_inserts += 1

                except Exception as db_error:
                    # More specific error for database insertion
                    raise Exception(f"Database insertion error: {str(db_error)}")

            except Exception as e:
                error_msg = f"Error inserting user: {str(e)}"
                print(error_msg)
                errors.append(error_msg)

        print(f"Successfully inserted {successful_inserts} out of {len(users_with_embeddings)} users")
        return len(users_with_embeddings), successful_inserts, errors

    def ingest_university_data(self, universities_data: List[Dict[str, Any]]) -> Tuple[int, List[str]]:
        """
        Process and store university data.

        Args:
            universities_data: List of dictionaries containing university data

        Returns:
            Tuple containing (number of successful inserts, errors)
        """
        successful_inserts = 0
        errors = []

        for univ in universities_data:
            try:
                # Generate university profile text for embedding
                profile_text = self._generate_university_profile(univ)

                # Get embedding for university profile
                payload = {"texts": [profile_text, ""], "batchMode": False}
                headers = {"Content-Type": "application/json"}
                response = requests.post(self.edge_function_url, headers=headers, json=payload)

                if response.status_code != 200:
                    raise Exception(f"Error generating embedding: {response.text}")

                embedding_data = response.json()
                univ["profile_embedding"] = embedding_data.get("embeddings", [[0.0] * 384])[0]

                # Insert into database
                response = self.supabase.from_("universities").insert(univ).execute()
                successful_inserts += 1

            except Exception as e:
                error_msg = f"Error inserting university {univ.get('name', 'unknown')}: {str(e)}"
                errors.append(error_msg)

        return successful_inserts, errors

    def _generate_university_profile(self, univ: Dict[str, Any]) -> str:
        """
        Generate a text profile of a university for embedding.

        Args:
            univ: Dictionary containing university data

        Returns:
            String containing a natural language description of the university
        """
        profile_parts = []

        if univ.get('name'):
            profile_parts.append(f"University name: {univ['name']}.")

        if univ.get('abbreviation'):
            profile_parts.append(f"Also known as {univ['abbreviation']}.")

        if univ.get('location'):
            profile_parts.append(f"Located in {univ['location']}.")

        if univ.get('description'):
            profile_parts.append(univ['description'])

        if univ.get('student_population'):
            pop_size = "small"
            if univ['student_population'] > 10000:
                pop_size = "medium"
            if univ['student_population'] > 25000:
                pop_size = "large"
            profile_parts.append(f"Has a {pop_size} student population of {univ['student_population']}.")

        if univ.get('campus_type'):
            profile_parts.append(f"Campus type: {univ['campus_type']}.")

        if univ.get('available_schools') and isinstance(univ['available_schools'], list):
            schools = ', '.join(univ['available_schools'])
            profile_parts.append(f"Offers programs in: {schools}.")

        if univ.get('research_focus') and isinstance(univ['research_focus'], list):
            focus_areas = ', '.join(univ['research_focus'])
            profile_parts.append(f"Research focus areas: {focus_areas}.")

        if univ.get('teaching_style'):
            profile_parts.append(f"Teaching style: {univ['teaching_style']}.")

        if univ.get('campus_culture'):
            profile_parts.append(f"Campus culture: {univ['campus_culture']}.")

        if univ.get('overall_ranking'):
            profile_parts.append(f"Ranked {univ['overall_ranking']} overall.")

        if univ.get('tuition_domestic') or univ.get('tuition_international'):
            profile_parts.append(f"Tuition: Domestic ${univ.get('tuition_domestic', 'N/A')}, "
                                 f"International ${univ.get('tuition_international', 'N/A')}.")

        if univ.get('scholarship_availability'):
            profile_parts.append(f"Scholarship availability: {univ['scholarship_availability']}.")

        return ' '.join(profile_parts)

    # Example usage
    def recommend_universities(self, user_id=None, user_profile=None, limit=5):
        """
        Get university recommendations for a user based on vector similarity.

        Args:
            user_id: UUID of an existing user in the database (optional)
            user_profile: Dictionary containing user profile data (optional)
            limit: Maximum number of recommendations to return

        Returns:
            List of recommended universities with similarity scores
        """
        if not user_id and not user_profile:
            raise ValueError("Either user_id or user_profile must be provided")

        # Case 1: Get embeddings for an existing user
        if user_id:
            try:
                response = self.supabase.from_("users").select("profile_embedding").eq("id", user_id).execute()
                if not response.data or len(response.data) == 0:
                    raise ValueError(f"User with ID {user_id} not found")

                user_embedding = response.data[0].get("profile_embedding")
                if not user_embedding:
                    raise ValueError(f"User with ID {user_id} has no profile embedding")
            except Exception as e:
                raise Exception(f"Error retrieving user embedding: {e}")

        # Case 2: Generate embeddings for a new user profile
        else:
            # Generate profile text
            profile_text = self._generate_profile_text(user_profile)
            preferences_text = self._generate_preferences_text(user_profile)

            # Get embeddings
            payload = {"texts": [profile_text, preferences_text], "batchMode": False}
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(self.edge_function_url, headers=headers, json=payload)

                if response.status_code != 200:
                    raise Exception(f"Error generating embeddings: {response.text}")

                results = response.json()
                embeddings = results.get("embeddings", [[0.0] * 384, [0.0] * 384])
                user_embedding = embeddings[0]  # Use the profile embedding
            except Exception as e:
                raise Exception(f"Error generating embeddings: {e}")

        # Query for similar universities using vector similarity
        try:
            # Ensure the embedding is properly formatted for the query
            embedding_str = json.dumps(user_embedding)

            # Use RPC to find similar universities
            response = self.supabase.rpc(
                'find_similar_universities',
                {
                    'user_profile_embedding': user_embedding,
                    'limit_num': limit
                }
            ).execute()

            return response.data

        except Exception as e:
            raise Exception(f"Error finding similar universities: {e}")


if __name__ == "__main__":
    ingestor = UniversityRecommendationDataIngestor(
        supabase_url=os.environ.get("SUPABASE_URL"),
        supabase_key=os.environ.get("SUPABASE_SERVICE_KEY"),
        edge_function_url=os.environ.get("EMBED_FUNCTION_URL"),
        auto_setup=True  # Automatically set up tables if they don't exist
    )

    # Step 1: Ingest survey data
    print("\n=== INGESTING SURVEY DATA ===")
    processed, inserted, errors = ingestor.ingest_survey_data("../data/analysis_ready_survey_data.csv")

    print(f"Processed {processed} records")
    print(f"Successfully inserted {inserted} records")

    if errors:
        print(f"Encountered {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")

    # Step 2: Example of getting recommendations for a user
    print("\n=== EXAMPLE RECOMMENDATION ===")
    if inserted > 0:
        try:
            # Get the first user's ID
            user_response = ingestor.supabase.table("users").select("id").limit(1).execute()
            if user_response.data and len(user_response.data) > 0:
                user_id = user_response.data[0]["id"]
                print(f"Getting recommendations for user {user_id}")

                recommendations = ingestor.recommend_universities(user_id=user_id, limit=3)
                print(f"Found {len(recommendations)} recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec['university_name']} (Similarity: {rec['similarity']:.4f})")
        except Exception as e:
            print(f"Error demonstrating recommendations: {e}")
