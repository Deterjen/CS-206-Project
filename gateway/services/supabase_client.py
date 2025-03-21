import os
from typing import List, Dict, Any, Optional

from supabase import create_client, Client


class SupabaseDB:
    """
    A client class to interface with the Supabase database for the University Recommendation System.
    """

    def __init__(self, url: str, key: str):
        """
        Initialize the Supabase client with URL and API key.

        Args:
            url: Supabase project URL
            key: Supabase API key
        """
        self.supabase: Client = create_client(url, key)

        # Add caching to reduce database hits
        self._university_cache = {}
        self._program_cache = {}

    @classmethod
    def from_env(cls):
        """
        Create a SupabaseDB instance using environment variables.

        Returns:
            SupabaseDB: An initialized SupabaseDB instance
        """
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

        return cls(url, key)
    
    # ===== Account Oppertaions =====
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
            email: The email of the user
            password: The password of the user

        Returns:
            The user data if created, or None if failed
        """
        # print(f"Data to be inserted: {data}")
        # print("Before insert request")
        response = self.supabase.table("users").insert([data]).execute()
        # print("After insert request")
        # print(response.data)

        if response:
            new_user = response.data[0]  # Get the newly created user
            user_id = new_user["id"]  # Get the new user's ID

            # Insert into aspiring_students with user_id as the foreign key
            aspiring_student_data = {"user_id": user_id}  # Add more fields if necessary
            # print("Before insert request2")
            student_response = self.supabase.table("aspiring_students").insert([aspiring_student_data]).execute()
            # print("After insert request2")

            if student_response is None:
                # print(f"Error inserting aspiring student: {student_response.error}")
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
            user = await self.get_user_by_username(username)  # Make sure to await it
            user_id = user["id"]  # Access the user id after the user is fetched

            # First, delete the related aspiring_students record
            response2 = self.supabase.table("aspiring_students").delete().eq("user_id", user_id).execute()
            if not response2.data:
                print(f"No related aspiring_students record found for user {username}.")

            # Now, proceed with deleting the user from the 'users' table
            response = self.supabase.table("users").delete().eq("username", username).execute()
            if response.data:
                print(f"User {username} deleted successfully.")
            else:
                print(f"User {username} not found or failed to delete.")

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
        response = self.supabase.table("universities").select("*").limit(limit).offset(offset).execute()

        # Update cache with fetched universities
        for univ in response.data:
            self._university_cache[univ["id"]] = univ

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
            # Update cache
            self._university_cache[university_id] = response.data[0]
            return response.data[0]

    def get_universities_by_ids(self, university_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple universities by their IDs in a single query.
        Returns a dictionary mapping university IDs to university data.
        """
        # Check which IDs we need to fetch (not in cache)
        ids_to_fetch = [uid for uid in university_ids if uid not in self._university_cache]

        # If we need to fetch any IDs
        if ids_to_fetch:
            response = self.supabase.table("universities").select("*").in_("id", ids_to_fetch).execute()

            # Update cache with new data
            for univ in response.data:
                self._university_cache[univ["id"]] = univ

        # Return requested universities from cache
        return {uid: self._university_cache[uid] for uid in university_ids if uid in self._university_cache}

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
        query = self.supabase.table("programs").select("*")

        if university_id is not None:
            query = query.eq("university_id", university_id)

        response = query.limit(limit).offset(offset).execute()

        # Update program cache
        for program in response.data:
            self._program_cache[program["id"]] = program

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
    def get_balanced_student_sample(self, students_per_university: int = 50) -> List[int]:
        """
        Get a balanced sample of students across universities to ensure diversity.
        Enhanced to retrieve students based on their similarity potential rather than
        fixed sampling.

        Args:
            students_per_university: Maximum number of students to fetch per university

        Returns:
            List of student IDs
        """
        # Get list of universities
        universities = self.get_universities(limit=1000)

        all_student_ids = []

        for university in universities:
            uni_id = university["id"]

            # Fetch a variety of student profiles with diverse programs, years of study, etc.
            # This approach yields more representative samples

            # First, get programs offered at this university
            programs = self.get_programs(university_id=uni_id)
            program_ids = [p["id"] for p in programs]

            if not program_ids:
                continue

            # Strategy 1: Get students from each program (diversity by subject area)
            for program_id in program_ids:
                # Get a small sample from each program
                program_sample = self.supabase.table("existing_students") \
                    .select("id") \
                    .eq("university_id", uni_id) \
                    .eq("program_id", program_id) \
                    .limit(max(2, students_per_university // len(program_ids))) \
                    .execute()

                student_ids_from_program = [s["id"] for s in program_sample.data]
                all_student_ids.extend(student_ids_from_program)

            # Strategy 2: Get students with high satisfaction (quality responses)
            satisfied_students = self.supabase.table("existing_students") \
                .select("id") \
                .eq("university_id", uni_id) \
                .order("id", desc=True) \
                .limit(students_per_university // 4) \
                .execute()

            all_student_ids.extend([s["id"] for s in satisfied_students.data])

            # Strategy 3: Get students from different years of study (diversity by experience)
            years = ["1st year", "2nd year", "3rd year", "4th year", "5+ years", "Postgraduate"]
            for year in years:
                year_sample = self.supabase.table("existing_students") \
                    .select("id") \
                    .eq("university_id", uni_id) \
                    .eq("year_of_study", year) \
                    .limit(students_per_university // len(years)) \
                    .execute()

                all_student_ids.extend([s["id"] for s in year_sample.data])

            # Ensure we don't exceed the maximum per university
            # De-duplicate IDs we may have retrieved in multiple queries
            uni_student_ids = list(set(id for id in all_student_ids if id is not None))

            # If we have more than we need, sample down to the limit
            if len(uni_student_ids) > students_per_university:
                import random
                uni_student_ids = random.sample(uni_student_ids, students_per_university)

        # Remove duplicates from the final list while maintaining order
        seen = set()
        unique_student_ids = []
        for student_id in all_student_ids:
            if student_id not in seen and student_id is not None:
                seen.add(student_id)
                unique_student_ids.append(student_id)

        return unique_student_ids

    def get_complete_existing_students_batch(self, student_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple existing students with all their sections in a single operation.
        Uses a more efficient approach with fewer queries.

        Args:
            student_ids: List of student IDs to fetch

        Returns:
            Dictionary mapping student IDs to complete student data
        """
        if not student_ids:
            return {}

        # Define all the sections we need
        sections = [
            "existing_students",
            "existing_students_university_info",
            "existing_students_academic",
            "existing_students_social",
            "existing_students_career",
            "existing_students_financial",
            "existing_students_facilities",
            "existing_students_reputation",
            "existing_students_personal_fit",
            "existing_students_selection_criteria",
            "existing_students_additional_insights"
        ]

        # Create a dictionary to store results by student ID
        students_data = {student_id: {} for student_id in student_ids}

        # Fetch each section in a single batch query
        for section in sections:
            # For the core table, use 'id' as the key
            id_field = "id" if section == "existing_students" else "student_id"

            # Fetch all records in this section for the given student IDs
            response = self.supabase.table(section) \
                .select("*") \
                .in_(id_field, student_ids) \
                .execute()

            # Map section data to the appropriate student
            for record in response.data:
                student_id = record["id"] if section == "existing_students" else record["student_id"]

                # Skip if student ID not in our target list
                if student_id not in students_data:
                    continue

                # Store section type in the student data
                section_type = section.replace("existing_students_", "") if section != "existing_students" else "core"
                students_data[student_id][section_type] = record

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

    def batch_get_existing_students(self, student_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple existing students with all their sections in a batch.
        Returns a dictionary mapping student IDs to flattened student data.
        """
        if not student_ids:
            return {}

        # Get core student data
        core_response = self.supabase.table("existing_students").select("*").in_("id", student_ids).execute()

        # Create a dictionary of students by ID
        students = {student["id"]: {"core": student} for student in core_response.data}

        # Get all sections in batch queries
        sections = [
            "university_info", "academic", "social", "career",
            "financial", "facilities", "reputation", "personal_fit",
            "selection_criteria", "additional_insights"
        ]

        for section in sections:
            table_name = f"existing_students_{section}"
            section_response = self.supabase.table(table_name).select("*").in_("student_id", student_ids).execute()

            # Add section data to the appropriate student
            for section_data in section_response.data:
                student_id = section_data["student_id"]
                if student_id in students:
                    students[student_id][section] = section_data

        return students

    def create_existing_student(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new existing student record.

        Args:
            data: Core existing student data to insert

        Returns:
            The created existing student record
        """
        response = self.supabase.table("existing_students").insert(data).execute()
        return response.data[0]

    def create_existing_student_complete(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete existing student record with all related sections.

        Args:
            student_data: A dictionary containing all student data with sections like:
                {
                    "core": {...},  # Core student data
                    "university_info": {...},  # University info section
                    "academic": {...},  # Academic section
                    ...
                }

        Returns:
            Dictionary with all created records
        """
        # Start a transaction (not directly supported in supabase-py, mock implementation)
        results = {}

        # Insert core student data
        core_response = self.supabase.table("existing_students").insert(student_data["core"]).execute()
        student_id = core_response.data[0]["id"]
        results["core"] = core_response.data[0]

        # Add student_id to all section data
        for section in ["university_info", "academic", "social", "career",
                        "financial", "facilities", "reputation", "personal_fit",
                        "selection_criteria", "additional_insights"]:
            if section in student_data:
                section_data = student_data[section]
                section_data["student_id"] = student_id

                # Insert section data
                table_name = f"existing_students_{section}"
                section_response = self.supabase.table(table_name).insert(section_data).execute()
                results[section] = section_response.data[0]

        return results

    def get_existing_student_complete(self, student_id: int) -> Dict[str, Any]:
        """
        Get a complete existing student record with all related sections.

        Args:
            student_id: The ID of the student

        Returns:
            Dictionary with all student records
        """
        results = {}

        # Get core student data
        core_response = self.supabase.table("existing_students").select("*").eq("id", student_id).limit(1).execute()
        if not core_response.data:
            return None

        results["core"] = core_response.data[0]

        # Get all sections
        for section in ["university_info", "academic", "social", "career",
                        "financial", "facilities", "reputation", "personal_fit",
                        "selection_criteria", "additional_insights"]:
            table_name = f"existing_students_{section}"
            section_response = self.supabase.table(table_name).select("*").eq("student_id", student_id).limit(
                1).execute()

            if section_response.data:
                results[section] = section_response.data[0]

        return results

    # ===== Aspiring Student Operations =====

    # def create_aspiring_student(self, data: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     Create a new aspiring student record.

    #     Args:
    #         data: Core aspiring student data to insert

    #     Returns:
    #         The created aspiring student record
    #     """
    #     response = self.supabase.table("aspiring_students").insert(data).execute()
    #     return response.data[0]

    async def get_aspiring_student(self, username) -> Dict[str, Any]:
        user = await self.get_user_by_username(username)

        user_id = user["id"]

        response = self.supabase.table("aspiring_students").select("*").eq("user_id", user_id).limit(1).execute()

        # Get the data from the APIResponse object
        data = response.data  # This will give you the actual data from the response.

        # Handle the case where no data is found
        if not data:
            raise ValueError(f"No aspiring student found with user_id {user_id}")

        # Return or process the data
        return data


    async def create_aspiring_student_complete(self, username: str, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete aspiring student record with all related sections.

        Args:
            student_data: A dictionary containing all student data with sections like:
                {
                    "core": {...},  # Core student data
                    "academic": {...},  # Academic section
                    "social": {...},  # Social section
                    ...
                }

        Returns:
            Dictionary with all created records
        """
        # Start a transaction (not directly supported in supabase-py, mock implementation)
        results = {}

        # Insert core student data
        # core_response = self.supabase.table("aspiring_students").insert(student_data.get("core", {})).execute()
        # student_id = core_response.data[0]["id"]
        # results["core"] = core_response.data[0]

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
        Save multiple recommendations and their similar students in a single batch operation.

        Args:
            aspiring_student_id: The ID of the aspiring student
            recommendations: List of recommendation data

        Returns:
            List of created recommendation records
        """
        if not recommendations:
            return []

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

        # Insert all recommendations in one batch
        rec_response = self.supabase.table("recommendations").insert(rec_data).execute()
        saved_recs = rec_response.data

        # Prepare similar student records
        similar_student_data = []

        for i, rec in enumerate(recommendations):
            recommendation_id = saved_recs[i]["id"]

            # Add similar students for this recommendation
            for student in rec.get("similar_students", []):
                similar_student_data.append({
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

        # Save all similar students in one batch if there are any
        if similar_student_data:
            self.supabase.table("similar_students").insert(similar_student_data).execute()

        return saved_recs

    def save_recommendations(self, aspiring_student_id: int, recommendations: List[Dict[str, Any]]) -> List[
        Dict[str, Any]]:
        """
        Save university recommendations for an aspiring student.

        Args:
            aspiring_student_id: The ID of the aspiring student
            recommendations: List of recommendation data

        Returns:
            List of created recommendation records
        """
        results = []

        for rec in recommendations:
            # Prepare recommendation data
            rec_data = {
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
            }

            # Insert recommendation record
            rec_response = self.supabase.table("recommendations").insert(rec_data).execute()
            recommendation_id = rec_response.data[0]["id"]
            rec_result = rec_response.data[0]

            # Save similar students if provided
            if "similar_students" in rec and rec["similar_students"]:
                similar_students = []

                for student in rec["similar_students"]:
                    student_data = {
                        "recommendation_id": recommendation_id,
                        "existing_student_id": student["student_id"],
                        "similarity_score": student["similarity"]
                    }

                    student_response = self.supabase.table("similar_students").insert(student_data).execute()
                    similar_students.append(student_response.data[0])

                rec_result["similar_students"] = similar_students

            results.append(rec_result)

        return results

    def get_all_recommendations_with_details(self, aspiring_student_id: int) -> List[Dict[str, Any]]:
        """
        Get all recommendations for an aspiring student with university and similar student details
        in a minimal number of queries.

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

        # Get all similar students in a single query
        similar_students_response = self.supabase.table("similar_students") \
            .select("*") \
            .in_("recommendation_id", recommendation_ids) \
            .execute()

        # Organize similar students by recommendation ID
        similar_students_by_rec = {}
        for ss in similar_students_response.data:
            rec_id = ss["recommendation_id"]
            if rec_id not in similar_students_by_rec:
                similar_students_by_rec[rec_id] = []
            similar_students_by_rec[rec_id].append(ss)

        # Build the complete recommendation data
        detailed_recommendations = []
        for rec in recommendations:
            rec_id = rec["id"]
            university_id = rec["university_id"]

            detailed_rec = {
                "recommendation": rec,
                "university": universities.get(university_id, {}),
                "similar_students": similar_students_by_rec.get(rec_id, [])
            }

            detailed_recommendations.append(detailed_rec)

        return detailed_recommendations

    def save_similar_student(self, recommendation_id: int, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a similar student record with detailed similarity scores.

        Args:
            recommendation_id: The ID of the recommendation
            student_data: Dictionary containing similarity data

        Returns:
            Created similar student record
        """
        data = {
            "recommendation_id": recommendation_id,
            "existing_student_id": student_data["student_id"],
            "similarity_score": student_data["overall_similarity"],
            "academic_similarity": student_data.get("academic_similarity", 0),
            "social_similarity": student_data.get("social_similarity", 0),
            "financial_similarity": student_data.get("financial_similarity", 0),
            "career_similarity": student_data.get("career_similarity", 0),
            "geographic_similarity": student_data.get("geographic_similarity", 0),
            "facilities_similarity": student_data.get("facilities_similarity", 0),
            "reputation_similarity": student_data.get("reputation_similarity", 0),
            "personal_fit_similarity": student_data.get("personal_fit_similarity", 0)
        }

        response = self.supabase.table("similar_students").insert(data).execute()
        return response.data[0]

    def get_similar_students_for_recommendation(self, recommendation_id: int) -> List[Dict[str, Any]]:
        """
        Get all similar students for a recommendation with their details.

        Args:
            recommendation_id: The ID of the recommendation

        Returns:
            List of similar student records with existing student details
        """
        response = self.supabase.table("similar_students") \
            .select("*, existing_students(*)") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        return response.data

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

        # Get similar students
        ss_response = self.supabase.table("similar_students") \
            .select("*") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        similar_students = ss_response.data

        # Combine all data
        result = {
            "recommendation": recommendation,
            "university": university,
            "similar_students": similar_students
        }

        return result

    def get_recommendation_with_university_and_students(self, recommendation_id: int) -> Dict[str, Any]:
        """
        Get a recommendation with university and similar students details in a single efficient query.

        Args:
            recommendation_id: The ID of the recommendation

        Returns:
            Complete recommendation data with university and similar students
        """
        # Get the recommendation
        recommendation_response = self.supabase.table("recommendations").select("*").eq("id", recommendation_id).limit(
            1).execute()

        if not recommendation_response.data:
            return None

        recommendation = recommendation_response.data[0]

        # Get university data (from cache if possible)
        university_id = recommendation["university_id"]
        university = self.get_university_by_id(university_id)

        # Get similar students with a JOIN to existing_students
        similar_students_response = self.supabase.table("similar_students") \
            .select("*, existing_students!inner(*)") \
            .eq("recommendation_id", recommendation_id) \
            .execute()

        # Collect all university IDs from similar students
        university_ids = [s["existing_students"]["university_id"] for s in similar_students_response.data]

        # Fetch all universities in a single query
        universities_map = self.get_universities_by_ids(university_ids)

        # Process similar students with university data
        similar_students = []
        for student in similar_students_response.data:
            student_university_id = student["existing_students"]["university_id"]
            student_university = universities_map.get(student_university_id, {"name": "Unknown University"})

            similar_students.append({
                "id": student["id"],
                "existing_student_id": student["existing_student_id"],
                "similarity_score": student["similarity_score"],
                "academic_similarity": student.get("academic_similarity", 0),
                "social_similarity": student.get("social_similarity", 0),
                "financial_similarity": student.get("financial_similarity", 0),
                "career_similarity": student.get("career_similarity", 0),
                "geographic_similarity": student.get("geographic_similarity", 0),
                "facilities_similarity": student.get("facilities_similarity", 0),
                "reputation_similarity": student.get("reputation_similarity", 0),
                "personal_fit_similarity": student.get("personal_fit_similarity", 0),
                "existing_student": student["existing_students"],
                "university": student_university
            })

        # Return combined data
        return {
            "recommendation": recommendation,
            "university": university,
            "similar_students": similar_students
        }

    # ===== Feedback Operations =====

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

    # ===== Advanced Query Operations =====

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

    def get_students_by_university(self, university_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all existing students for a university with their complete profiles.

        Args:
            university_id: The ID of the university
            limit: Maximum number of records to return

        Returns:
            List of student records with all related sections
        """
        # Get student IDs for the university
        response = self.supabase.table("existing_students") \
            .select("id") \
            .eq("university_id", university_id) \
            .limit(limit) \
            .execute()

        student_ids = [student["id"] for student in response.data]
        complete_students = []

        # Get complete profile for each student
        for student_id in student_ids:
            student = self.get_existing_student_complete(student_id)
            if student:
                complete_students.append(student)

        return complete_students
