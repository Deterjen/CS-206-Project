from typing import List, Dict, Any, Optional

from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_KEY


class SupabaseDB:
    """
    A client class to interface with the Supabase database for the University Recommendation System.
    Memory-optimized version with minimal caching.
    """

    def __init__(self, url: str, key: str):
        """
        Initialize the Supabase client with URL and API key.

        Args:
            url: Supabase project URL
            key: Supabase API key
        """
        self.supabase: Client = create_client(url, key)

        # Limited cache size to reduce memory usage
        self._max_cache_size = 25  # Small cache size
        self._university_cache = {}

        # No program cache - fetch directly when needed

    @classmethod
    def from_env(cls):
        """
        Create a SupabaseDB instance using environment variables.

        Returns:
            SupabaseDB: An initialized SupabaseDB instance
        """
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

        return cls(SUPABASE_URL, SUPABASE_KEY)

    def _manage_cache_size(self, cache_dict):
        """Helper method to ensure cache doesn't exceed maximum size"""
        if len(cache_dict) >= self._max_cache_size:
            # Simple eviction strategy: remove oldest item (first key)
            if cache_dict:
                oldest_key = next(iter(cache_dict))
                cache_dict.pop(oldest_key)

    # ===== Account Operations =====
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email.

        Args:
            email: The email of the user

        Returns:
            User record or None if not found
        """
        response = self.supabase.table("users").select("*").eq("email", email).limit(1).execute()
        if response.data:
            return response.data[0]
        return None

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by username.

        Args:
            username: The username of the user

        Returns:
            User record or None if not found
        """
        response = self.supabase.table("users").select("*").eq("username", username).limit(1).execute()
        if response.data:
            return response.data[0]
        return None

    async def signup_user(self, data: Dict) -> Optional[Dict[str, Any]]:
        """
        Sign up a new user.

        Args:
            data: User data including username, email, and password

        Returns:
            The user data if created, or None if failed
        """
        response = self.supabase.table("users").insert([data]).execute()

        if response:
            new_user = response.data[0]  # Get the newly created user
            user_id = new_user["id"]  # Get the new user's ID

            # Insert into aspiring_students with user_id as the foreign key
            aspiring_student_data = {"user_id": user_id}
            student_response = self.supabase.table("aspiring_students").insert([aspiring_student_data]).execute()

            if student_response is None:
                raise Exception("Failed to create aspiring student entry")

            return new_user

        return None

    async def update_user(self, username: str, update_data: dict):
        """
        Update user details in the 'users' table.

        Args:
            username: The username of the user to update
            update_data: Dictionary with fields to update

        Returns:
            The updated user record or None if not found
        """
        try:
            response = self.supabase.table("users").update(update_data).eq("username", username).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")

    async def delete_user(self, username: str):
        """
        Delete a user from the 'users' table.

        Args:
            username: The username of the user to delete

        Returns:
            The deleted user record or None if not found
        """
        try:
            # Await the result of get_user_by_username since it is an async function
            user = await self.get_user_by_username(username)
            user_id = user["id"]

            # First, delete the related aspiring_students record
            response2 = self.supabase.table("aspiring_students").delete().eq("user_id", user_id).execute()

            # Now, proceed with deleting the user from the 'users' table
            response = self.supabase.table("users").delete().eq("username", username).execute()

            return response
        except Exception as e:
            raise Exception(f"Error deleting user from users table: {str(e)}")

    # ===== University Operations =====

    def get_universities(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get a list of universities.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of university records
        """
        # Use a smaller limit to reduce memory usage
        actual_limit = min(limit, 50)  # Cap maximum fetched at once

        response = self.supabase.table("universities").select("*").limit(actual_limit).offset(offset).execute()
        return response.data

    def get_university_by_id(self, university_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a university by ID.

        Args:
            university_id: The ID of the university

        Returns:
            University record or None if not found
        """
        # Check cache first
        if university_id in self._university_cache:
            return self._university_cache[university_id]

        # If not in cache, fetch from database
        response = self.supabase.table("universities").select("*").eq("id", university_id).limit(1).execute()

        if response.data:
            # Manage cache size before adding new entry
            self._manage_cache_size(self._university_cache)

            # Update cache
            self._university_cache[university_id] = response.data[0]
            return response.data[0]

        return None

    def get_universities_by_ids(self, university_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple universities by their IDs in a single query.
        Returns a dictionary mapping university IDs to university data.
        """
        # Check which IDs we need to fetch (not in cache)
        ids_to_fetch = [uid for uid in university_ids if uid not in self._university_cache]

        # If we need to fetch any IDs
        results = {}
        if ids_to_fetch:
            # Split into smaller batches if needed
            batch_size = 20  # Smaller batch size

            for i in range(0, len(ids_to_fetch), batch_size):
                batch_ids = ids_to_fetch[i:i + batch_size]
                response = self.supabase.table("universities").select("*").in_("id", batch_ids).execute()

                # Update cache with new data
                for univ in response.data:
                    # Manage cache size before adding
                    self._manage_cache_size(self._university_cache)

                    # Add to cache
                    self._university_cache[univ["id"]] = univ
                    results[univ["id"]] = univ

        # Add cached universities to results
        for uid in university_ids:
            if uid in self._university_cache and uid not in results:
                results[uid] = self._university_cache[uid]

        return results

    def get_universities_by_criteria(self, criteria: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get universities that match specific criteria.

        Args:
            criteria: Dictionary of criteria to filter by
            limit: Maximum number of records to return

        Returns:
            List of university records
        """
        query = self.supabase.table("universities").select("*")

        # Apply filters based on criteria
        for key, value in criteria.items():
            if key == "location" and value:
                query = query.ilike("location", f"%{value}%")
            elif key == "size" and value:
                query = query.eq("size", value)
            elif key == "setting" and value:
                query = query.eq("setting", value)

        response = query.limit(limit).execute()
        return response.data

    def create_university(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new university record.

        Args:
            data: University data to insert

        Returns:
            The created university record
        """
        response = self.supabase.table("universities").insert(data).execute()
        return response.data[0]

    def update_university(self, university_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a university record.

        Args:
            university_id: The ID of the university to update
            data: The updated university data

        Returns:
            The updated university record
        """
        response = self.supabase.table("universities").update(data).eq("id", university_id).execute()

        # Update cache if the university is cached
        if university_id in self._university_cache:
            self._university_cache[university_id] = response.data[0]

        return response.data[0]

    def delete_university(self, university_id: int) -> Dict[str, Any]:
        """
        Delete a university record.

        Args:
            university_id: The ID of the university to delete

        Returns:
            The deleted university record
        """
        response = self.supabase.table("universities").delete().eq("id", university_id).execute()

        # Remove from cache if present
        if university_id in self._university_cache:
            del self._university_cache[university_id]

        return response.data[0]

    # ===== Program Operations =====

    def get_programs(self, university_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[
        Dict[str, Any]]:
        """
        Get a list of programs, optionally filtered by university.

        Args:
            university_id: Optional ID of the university to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of program records
        """
        # Use a smaller limit to reduce memory usage
        actual_limit = min(limit, 30)  # Cap maximum fetched at once

        query = self.supabase.table("programs").select("*")

        if university_id is not None:
            query = query.eq("university_id", university_id)

        response = query.limit(actual_limit).offset(offset).execute()
        return response.data

    def create_program(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new program record.

        Args:
            data: Program data to insert

        Returns:
            The created program record
        """
        response = self.supabase.table("programs").insert(data).execute()
        return response.data[0]

    # ===== Existing Student Operations =====
    def get_university_student_counts(self):
        """Get counts of students per university"""
        response = self.supabase.rpc('get_university_student_counts').execute()
        return response.data

    def get_balanced_student_sample(self, students_per_university=50):
        """
        Get a balanced sample of students across universities with minimal queries.
        Memory-optimized version with reduced sample size.

        Returns:
            List of student IDs
        """
        # Get a small list of universities (limit to top 5)
        universities = self.get_universities(limit=5)
        all_student_ids = []

        # Reduce students per university
        students_per_university = min(students_per_university, 15)  # Cap at 15 students per university

        for university in universities:
            uni_id = university["id"]

            # Get a small sample of students from each program
            programs = self.get_programs(university_id=uni_id, limit=3)

            if programs:
                # Get fewer students from each program
                students_per_program = max(2, students_per_university // (len(programs) * 2))
                program_ids = [p["id"] for p in programs]

                # Use a single query with IN operator for all programs
                program_sample = self.supabase.table("existing_students") \
                    .select("id") \
                    .eq("university_id", uni_id) \
                    .in_("program_id", program_ids) \
                    .limit(students_per_program * len(program_ids)) \
                    .execute()

                all_student_ids.extend([s["id"] for s in program_sample.data])

            # Get another sample from this university using year of study
            years_sample = (self.supabase.table("existing_students")
                            .select("id")
                            .eq("university_id", uni_id)
                            .order("id")
                            .limit(students_per_university // 4)  # Reduced sample size
                            .execute())

            all_student_ids.extend([s["id"] for s in years_sample.data])

        # Remove duplicates while maintaining order
        seen = set()
        unique_student_ids = []
        for student_id in all_student_ids:
            if student_id not in seen and student_id is not None:
                seen.add(student_id)
                unique_student_ids.append(student_id)

        # Further limit total size
        max_total_students = 150  # Hard limit on total students
        return unique_student_ids[:max_total_students]

    def get_complete_existing_students_batch(self, student_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple existing students with all their sections in a minimal number of queries.

        Args:
            student_ids: List of student IDs to fetch

        Returns:
            Dictionary mapping student IDs to complete student data
        """
        if not student_ids:
            return {}

        # Limit the number of student IDs to process
        student_ids = student_ids[:min(len(student_ids), 100)]  # Process at most 100 students

        # Create a dictionary to store results by student ID
        students_data = {student_id: {} for student_id in student_ids}

        # Fetch core student data
        core_response = self.supabase.table("existing_students").select("*").in_("id", student_ids).execute()

        # Initialize with core data
        for student in core_response.data:
            student_id = student["id"]
            students_data[student_id]["core"] = student

        # Batch sections to reduce query count
        section_batches = [
            ["university_info", "academic", "social"],  # Batch 1
            ["career", "financial", "facilities"],  # Batch 2
            ["reputation", "personal_fit", "selection_criteria", "additional_insights"]  # Batch 3
        ]

        # Process each batch
        for batch in section_batches:
            for section in batch:
                table_name = f"existing_students_{section}"
                section_response = self.supabase.table(table_name).select("*").in_("student_id", student_ids).execute()

                # Map section data to the appropriate student
                for record in section_response.data:
                    student_id = record["student_id"]
                    if student_id in students_data:
                        students_data[student_id][section] = record

        return students_data

    def get_aspiring_student_complete(self, student_id: int) -> Dict[str, Any]:
        """
        Get a complete aspiring student profile with a single efficient query.

        Args:
            student_id: ID of the aspiring student

        Returns:
            Dictionary with complete student data
        """
        # Define sections to fetch
        sections = [
            "aspiring_students",
            "aspiring_students_academic",
            "aspiring_students_social",
            "aspiring_students_career",
            "aspiring_students_financial",
            "aspiring_students_geographic",
            "aspiring_students_facilities",
            "aspiring_students_reputation",
            "aspiring_students_personal_fit"
        ]

        # Initialize result
        result = {}

        # Fetch each section with a single efficient query
        for section in sections:
            # For the core table, use 'id' as the key
            id_field = "id" if section == "aspiring_students" else "student_id"

            response = self.supabase.table(section) \
                .select("*") \
                .eq(id_field, student_id) \
                .limit(1) \
                .execute()

            if response.data:
                # Store section type in the result
                section_type = section.replace("aspiring_students_", "") if section != "aspiring_students" else "core"
                result[section_type] = response.data[0]

        return result

    async def get_aspiring_student(self, username) -> Dict[str, Any]:
        """
        Get aspiring student by username.

        Args:
            username: Username of the user

        Returns:
            Aspiring student record
        """
        user = await self.get_user_by_username(username)
        user_id = user["id"]

        response = self.supabase.table("aspiring_students").select("*").eq("user_id", user_id).limit(1).execute()
        data = response.data

        if not data:
            raise ValueError(f"No aspiring student found with user_id {user_id}")

        return data

    async def create_aspiring_student_complete(self, username: str, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete aspiring student record with all related sections.

        Args:
            username: Username of the user
            student_data: A dictionary containing all student data with sections

        Returns:
            Dictionary with all created records
        """
        results = {}

        # Get the aspiring student
        aspiring_student = await self.get_aspiring_student(username)

        if aspiring_student is None:
            return {"error": "No aspiring student found"}
        aspiring_student_id = aspiring_student[0]["id"]

        # Add student_id to all section data
        for section in ["academic", "social", "career", "financial",
                        "geographic", "facilities", "reputation", "personal_fit"]:
            if section in student_data:
                section_data = student_data[section]
                section_data["student_id"] = aspiring_student_id

                # Insert section data
                table_name = f"aspiring_students_{section}"
                section_response = self.supabase.table(table_name).insert(section_data).execute()
                results[section] = section_response.data[0]

        return results

    # ===== Recommendation Operations =====
    def save_recommendations_batch(self, aspiring_student_id: int, recommendations: List[Dict[str, Any]]) -> List[
        Dict[str, Any]]:
        """
        Save multiple recommendations and their similar students with minimal queries.

        Args:
            aspiring_student_id: The ID of the aspiring student
            recommendations: List of recommendation data

        Returns:
            List of created recommendation records
        """
        if not recommendations:
            return []

        # Limit the number of recommendations to save
        recommendations = recommendations[:min(len(recommendations), 10)]  # Process at most 10 recommendations

        # Prepare recommendation records
        rec_data = []
        for rec in recommendations:
            rec_data.append({
                "aspiring_student_id": aspiring_student_id,
                "university_id": rec["university_id"],
                "overall_score": rec["overall_score"],
                "academic_score": rec.get("academic_score", 0),
                "social_score": rec.get("social_score", 0),
                "financial_score": rec.get("financial_score", 0),
                "career_score": rec.get("career_score", 0),
                "geographic_score": rec.get("geographic_score", 0),
                "facilities_score": rec.get("facilities_score", 0),
                "reputation_score": rec.get("reputation_score", 0),
                "personal_fit_score": rec.get("personal_fit_score", 0)
            })

        # Insert all recommendations in a single batch
        rec_response = self.supabase.table("recommendations").insert(rec_data).execute()
        saved_recs = rec_response.data

        # Collect all similar students for all recommendations
        all_similar_students = []

        for i, rec in enumerate(recommendations):
            if i >= len(saved_recs):
                break

            recommendation_id = saved_recs[i]["id"]

            # Limit to top 3 similar students per recommendation (reduced from original)
            top_similar = rec.get("similar_students", [])[:3]

            for student in top_similar:
                all_similar_students.append({
                    "recommendation_id": recommendation_id,
                    "existing_student_id": student["student_id"],
                    "similarity_score": student["overall_similarity"],
                    "academic_similarity": student.get("academic_similarity", 0),
                    "social_similarity": student.get("social_similarity", 0),
                    "financial_similarity": student.get("financial_similarity", 0),
                    "career_similarity": student.get("career_similarity", 0),
                    "geographic_similarity": student.get("geographic_similarity", 0),
                    "facilities_similarity": student.get("facilities_similarity", 0),
                    "reputation_similarity": student.get("reputation_similarity", 0),
                    "personal_fit_similarity": student.get("personal_fit_similarity", 0)
                })

        # Process similar students in smaller batches if there are many
        if all_similar_students:
            batch_size = 20  # Smaller batch size
            for i in range(0, len(all_similar_students), batch_size):
                batch = all_similar_students[i:i + batch_size]
                self.supabase.table("similar_students").insert(batch).execute()

        return saved_recs

    def get_all_recommendations_with_details(self, aspiring_student_id: int) -> List[Dict[str, Any]]:
        """
        Get all recommendations for an aspiring student with focused similar student details.
        Memory-optimized with batch processing.

        Args:
            aspiring_student_id: The ID of the aspiring student

        Returns:
            List of recommendation data with university and similar student details
        """
        # First, get all recommendations for this student
        rec_response = self.supabase.table("recommendations") \
            .select("*") \
            .eq("aspiring_student_id", aspiring_student_id) \
            .order("overall_score", desc=True) \
            .execute()

        if not rec_response.data:
            return []

        recommendations = rec_response.data
        recommendation_ids = [r["id"] for r in recommendations]
        university_ids = [r["university_id"] for r in recommendations]

        # Get universities in a single query
        univ_response = self.supabase.table("universities") \
            .select("*") \
            .in_("id", university_ids) \
            .execute()

        universities = {u["id"]: u for u in univ_response.data}

        # Process recommendations in batches to reduce memory usage
        batch_size = 5  # Process 5 recommendations at a time
        detailed_recommendations = []

        for i in range(0, len(recommendation_ids), batch_size):
            batch_rec_ids = recommendation_ids[i:i + batch_size]

            # Get similar students for this batch
            ss_response = self.supabase.table("similar_students") \
                .select("*") \
                .in_("recommendation_id", batch_rec_ids) \
                .execute()

            # Get all student IDs from similar students
            all_student_ids = [ss["existing_student_id"] for ss in ss_response.data]

            # Get only the required student data from the complete view
            student_data = {}
            if all_student_ids:
                # Only select essential fields
                student_data_response = self.supabase.table("existing_students_complete_view") \
                    .select("id, university_id, program_id, year_of_study, learning_styles, " +
                            "extracurricular_activities, typical_student_traits") \
                    .in_("id", all_student_ids) \
                    .execute()

                student_data = {s["id"]: s for s in student_data_response.data}

            # Organize similar students by recommendation ID
            similar_students_by_rec = {}
            for ss in ss_response.data:
                rec_id = ss["recommendation_id"]
                student_id = ss["existing_student_id"]

                # Combine similarity scores with student data
                student_details = student_data.get(student_id, {})
                complete_student_data = {**ss, **student_details}

                if rec_id not in similar_students_by_rec:
                    similar_students_by_rec[rec_id] = []

                similar_students_by_rec[rec_id].append(complete_student_data)

            # Build the complete recommendation data for this batch
            for rec in recommendations[i:i + batch_size]:
                rec_id = rec["id"]
                university_id = rec["university_id"]

                detailed_rec = {
                    "recommendation": rec,
                    "university": universities.get(university_id, {}),
                    "similar_students": similar_students_by_rec.get(rec_id, [])
                }

                detailed_recommendations.append(detailed_rec)

        return detailed_recommendations

    def get_recommendation_with_details(self, recommendation_id: int) -> Dict[str, Any]:
        """
        Get a single recommendation with all its details efficiently.

        Args:
            recommendation_id: The ID of the recommendation

        Returns:
            Recommendation data with university and similar student details
        """
        # Get the recommendation
        rec_response = self.supabase.table("recommendations") \
            .select("*") \
            .eq("id", recommendation_id) \
            .limit(1) \
            .execute()

        if not rec_response.data:
            return {}

        recommendation = rec_response.data[0]
        university_id = recommendation["university_id"]

        # Get the university (use cache if available)
        university = self.get_university_by_id(university_id)

        # Step 1: Get similar students for this recommendation
        ss_response = self.supabase.table("similar_students") \
            .select("*") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        similar_students = []
        if ss_response.data:
            # Step 2: Get existing student IDs
            student_ids = [ss["existing_student_id"] for ss in ss_response.data]

            # Step 3: Get only the required student data
            # Select only essential fields to reduce data transfer
            student_data_response = self.supabase.table("existing_students_complete_view") \
                .select("id, university_id, program_id, year_of_study, learning_styles, " +
                        "extracurricular_activities, typical_student_traits") \
                .in_("id", student_ids) \
                .execute()

            # Create a lookup for student data
            student_data_map = {s["id"]: s for s in student_data_response.data}

            # Step 4: Get program names for each student
            program_ids = list(set([s["program_id"] for s in student_data_response.data if s.get("program_id")]))

            program_names = {}
            if program_ids:
                # Only select what we need (id, name)
                prog_response = self.supabase.table("programs").select("id, name").in_("id", program_ids).execute()
                program_names = {p["id"]: p["name"] for p in prog_response.data}

            # Step 5: Combine all data
            for ss in ss_response.data:
                student_id = ss["existing_student_id"]
                student_data = student_data_map.get(student_id, {})

                # Add program name
                prog_id = student_data.get("program_id")
                student_data["program_name"] = program_names.get(prog_id,
                                                                 "Unknown Program") if prog_id else "Unknown Program"

                # Combine similarity scores with student data
                similar_student = {**ss, **student_data}
                similar_students.append(similar_student)

        # Return combined data
        result = {
            "recommendation": recommendation,
            "university": university,
            "similar_students": similar_students
        }

        return result

    def save_recommendation_feedback(self, recommendation_id: int, rating: int, text: str) -> Dict[str, Any]:
        """
        Save feedback for a recommendation.

        Args:
            recommendation_id: The ID of the recommendation
            rating: Feedback rating (1-5)
            text: Feedback text

        Returns:
            Created feedback record
        """
        data = {
            "recommendation_id": recommendation_id,
            "feedback_rating": rating,
            "feedback_text": text
        }

        response = self.supabase.table("recommendation_feedback").insert(data).execute()
        return response.data[0]

    def get_recommendation_justification(self, recommendation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a recommendation justification from the database.

        Args:
            recommendation_id: The ID of the recommendation

        Returns:
            Justification record or None if not found
        """
        try:
            response = self.supabase.table("recommendation_justifications").select("*").eq("recommendation_id",
                                                                                           recommendation_id).limit(
                1).execute()

            if response.data:
                justification = response.data[0]
                # Format it to match the structure expected by the frontend
                return {
                    "Pros": justification.get("pros", []),
                    "Cons": justification.get("cons", []),
                    "Conclusion": justification.get("conclusion", "")
                }

            return None
        except Exception as e:
            print(f"Error retrieving recommendation justification: {e}")
            return None

    def save_recommendation_justification(self, recommendation_id: int, justification_data: Dict[str, Any]) -> Dict[
        str, Any]:
        """
        Save a recommendation justification to the database.

        Args:
            recommendation_id: The ID of the recommendation
            justification_data: Dictionary containing pros, cons, and conclusion

        Returns:
            Created justification record
        """
        # Handle potential different formats for pros
        pros = justification_data.get("Pros", [])
        if not isinstance(pros, list):
            pros = [pros] if pros else []

        # Handle potential different formats for cons
        cons = justification_data.get("Cons", [])
        if not isinstance(cons, list):
            cons = [cons] if cons else []

        # Handle potential different formats for conclusion
        conclusion = justification_data.get("Conclusion", "")
        if isinstance(conclusion, list):
            conclusion = conclusion[0] if conclusion else ""

        data = {
            "recommendation_id": recommendation_id,
            "pros": pros,
            "cons": cons,
            "conclusion": conclusion
        }

        try:
            # Check if justification already exists
            existing = self.get_recommendation_justification(recommendation_id)
            if existing:
                # Update existing justification
                response = self.supabase.table("recommendation_justifications").update(data).eq("recommendation_id",
                                                                                                recommendation_id).execute()
            else:
                # Insert new justification
                response = self.supabase.table("recommendation_justifications").insert(data).execute()

            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving recommendation justification: {e}")
            return None

    # Additional methods for the SupabaseDB class

    # ===== Performance Optimization Methods =====

    def refresh_top_university_students(self):
        """
        Refresh the top_university_students materialized view.
        This is a database-side operation that doesn't impact client memory usage.
        """
        self.supabase.rpc('refresh_top_university_students').execute()

    def get_aspiring_student_complete_with_single_query(self, student_id: int) -> Dict[str, Any]:
        """
        Get complete aspiring student data with all sections in a single query.
        Uses the database view for efficiency.

        Args:
            student_id: ID of the aspiring student

        Returns:
            Complete aspiring student record
        """
        # Using the existing view for efficient retrieval
        query = f"""
        SELECT *
        FROM aspiring_student_complete_view
        WHERE id = $1
        LIMIT 1
        """

        response = self.supabase.rpc('run_query', {'query': query, 'params': [student_id]}).execute()

        if not response.data or len(response.data) == 0:
            return None

        return response.data[0]

    def get_similar_students_for_recommendation(self, recommendation_id: int) -> List[Dict[str, Any]]:
        """
        Get all similar students for a recommendation with minimal student details.
        Memory-optimized version that selects only essential fields.

        Args:
            recommendation_id: The ID of the recommendation

        Returns:
            List of similar student records with basic existing student details
        """
        # Select only essential fields for similar students
        response = self.supabase.table("similar_students") \
            .select("id, existing_student_id, similarity_score, academic_similarity, social_similarity") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        # If we need basic student info, fetch it separately with minimal fields
        student_ids = [s["existing_student_id"] for s in response.data]

        if student_ids:
            student_info = self.supabase.table("existing_students") \
                .select("id, university_id, year_of_study") \
                .in_("id", student_ids) \
                .execute()

            # Create lookup for student info
            student_lookup = {s["id"]: s for s in student_info.data}

            # Enhance similar students with basic info
            for student in response.data:
                student["student_info"] = student_lookup.get(student["existing_student_id"], {})

        return response.data

    def batch_get_existing_students(self, student_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple existing students with essential sections in a batch.
        Memory-optimized version that only retrieves the most critical sections.

        Args:
            student_ids: List of student IDs to fetch

        Returns:
            Dictionary mapping student IDs to student data
        """
        if not student_ids:
            return {}

        # Limit the number of student IDs to process
        student_ids = student_ids[:min(len(student_ids), 50)]  # Process at most 50 students

        # Get core student data
        core_response = self.supabase.table("existing_students").select("*").in_("id", student_ids).execute()

        # Create a dictionary of students by ID
        students = {student["id"]: {"core": student} for student in core_response.data}

        # Get only essential sections in batch queries (academic, social, and career)
        essential_sections = ["academic", "social", "career"]

        for section in essential_sections:
            table_name = f"existing_students_{section}"
            section_response = self.supabase.table(table_name).select("*").in_("student_id", student_ids).execute()

            # Add section data to the appropriate student
            for section_data in section_response.data:
                student_id = section_data["student_id"]
                if student_id in students:
                    students[student_id][section] = section_data

        return students

    def get_existing_student_complete(self, student_id: int) -> Dict[str, Any]:
        """
        Get a complete existing student record with essential sections.
        Memory-optimized version that prioritizes key sections.

        Args:
            student_id: The ID of the student

        Returns:
            Dictionary with student records
        """
        results = {}

        # Get core student data
        core_response = self.supabase.table("existing_students").select("*").eq("id", student_id).limit(1).execute()
        if not core_response.data:
            return None

        results["core"] = core_response.data[0]

        # Prioritize essential sections first
        essential_sections = ["academic", "social", "career", "personal_fit"]
        for section in essential_sections:
            table_name = f"existing_students_{section}"
            section_response = self.supabase.table(table_name).select("*").eq("student_id", student_id).limit(
                1).execute()

            if section_response.data:
                results[section] = section_response.data[0]

        # Get additional sections if the essential ones were successfully retrieved
        if len(results) > 1:  # If we have more than just core data
            additional_sections = ["university_info", "financial", "facilities",
                                   "reputation", "selection_criteria", "additional_insights"]
            for section in additional_sections:
                table_name = f"existing_students_{section}"
                section_response = self.supabase.table(table_name).select("*").eq("student_id", student_id).limit(
                    1).execute()

                if section_response.data:
                    results[section] = section_response.data[0]

        return results

    def create_existing_student_complete(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete existing student record with all related sections.
        Memory-optimized by processing in stages.

        Args:
            student_data: A dictionary containing all student data with sections

        Returns:
            Dictionary with all created records
        """
        # Start with core data
        results = {}

        # Insert core student data
        core_response = self.supabase.table("existing_students").insert(student_data["core"]).execute()
        student_id = core_response.data[0]["id"]
        results["core"] = core_response.data[0]

        # Process sections in batches to reduce memory pressure
        section_batches = [
            ["university_info", "academic", "social"],  # Essential academic info
            ["career", "financial", "facilities"],  # Financial and facilities
            ["reputation", "personal_fit"],  # Personal aspects
            ["selection_criteria", "additional_insights"]  # Additional feedback
        ]

        # Process each batch
        for batch in section_batches:
            batch_data = {}

            # Prepare data for this batch
            for section in batch:
                if section in student_data:
                    section_data = student_data[section].copy()  # Create a copy to avoid modifying original
                    section_data["student_id"] = student_id

                    # Insert section data
                    table_name = f"existing_students_{section}"
                    section_response = self.supabase.table(table_name).insert(section_data).execute()
                    results[section] = section_response.data[0]

        return results

    def save_similar_student(self, recommendation_id: int, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a similar student record with only essential similarity scores.
        Memory-optimized version that stores only the most important scores.

        Args:
            recommendation_id: The ID of the recommendation
            student_data: Dictionary containing similarity data

        Returns:
            Created similar student record
        """
        # Only include essential similarity data
        data = {
            "recommendation_id": recommendation_id,
            "existing_student_id": student_data["student_id"],
            "similarity_score": student_data["overall_similarity"],
            "academic_similarity": student_data.get("academic_similarity", 0),
            "social_similarity": student_data.get("social_similarity", 0),
            "financial_similarity": student_data.get("financial_similarity", 0),
            "career_similarity": student_data.get("career_similarity", 0)
            # Excluding less critical similarity scores
        }

        response = self.supabase.table("similar_students").insert(data).execute()
        return response.data[0]

    def get_recommendation_with_university_and_students(self, recommendation_id: int) -> Dict[str, Any]:
        """
        Get a recommendation with university and similar students details.
        Memory-optimized version that fetches minimal data for each entity.

        Args:
            recommendation_id: The ID of the recommendation

        Returns:
            Basic recommendation data with university and similar students
        """
        # Get the recommendation
        recommendation_response = self.supabase.table("recommendations").select("*").eq("id",
                                                                                        recommendation_id).limit(
            1).execute()

        if not recommendation_response.data:
            return None

        recommendation = recommendation_response.data[0]

        # Get university data (from cache if possible)
        university_id = recommendation["university_id"]
        university = self.get_university_by_id(university_id)

        # Get similar students with minimal data
        similar_students_response = self.supabase.table("similar_students") \
            .select("id, existing_student_id, similarity_score") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        # Get minimal student info in a separate query if needed
        student_ids = [s["existing_student_id"] for s in similar_students_response.data]
        student_info = {}

        if student_ids:
            student_response = self.supabase.table("existing_students") \
                .select("id, university_id, year_of_study") \
                .in_("id", student_ids) \
                .execute()

            student_info = {s["id"]: s for s in student_response.data}

        # Process similar students with university data
        similar_students = []
        for student in similar_students_response.data:
            student_id = student["existing_student_id"]
            student_data = student_info.get(student_id, {})

            similar_students.append({
                "id": student["id"],
                "existing_student_id": student_id,
                "similarity_score": student["similarity_score"],
                "university_id": student_data.get("university_id"),
                "year_of_study": student_data.get("year_of_study")
            })

        # Return combined data
        return {
            "recommendation": recommendation,
            "university": university,
            "similar_students": similar_students
        }

    def get_students_by_university(self, university_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get a sample of existing students for a university with basic profiles.
        Memory-optimized version that fetches only essential data.

        Args:
            university_id: The ID of the university
            limit: Maximum number of records to return

        Returns:
            List of student records with essential sections
        """
        # Use a smaller limit to reduce memory usage
        actual_limit = min(limit, 30)

        # Get student IDs for the university
        response = self.supabase.table("existing_students") \
            .select("id") \
            .eq("university_id", university_id) \
            .limit(actual_limit) \
            .execute()

        student_ids = [student["id"] for student in response.data]

        if not student_ids:
            return []

        # Use batch query to get essential student data
        students_data = self.batch_get_existing_students(student_ids)

        # Convert to list format
        return list(students_data.values())
