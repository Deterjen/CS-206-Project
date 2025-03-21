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
        return response.data

    def get_university_by_id(self, university_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a university by ID.

        Args:
            university_id: The ID of the university

        Returns:
            University record or None if not found
        """
        response = self.supabase.table("universities").select("*").eq("id", university_id).limit(1).execute()
        if response.data:
            return response.data[0]
        return None

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

    def get_recommendations_for_student(self, aspiring_student_id: int) -> List[Dict[str, Any]]:
        """
        Get all recommendations for an aspiring student with university details.

        Args:
            aspiring_student_id: The ID of the aspiring student

        Returns:
            List of recommendation records with university details
        """
        # Get recommendations
        response = self.supabase.table("recommendations") \
            .select("*, universities(*)") \
            .eq("aspiring_student_id", aspiring_student_id) \
            .execute()

        recommendations = response.data

        # For each recommendation, get similar students
        for rec in recommendations:
            similar_students_response = self.supabase.table("similar_students") \
                .select("*, existing_students(*)") \
                .eq("recommendation_id", rec["id"]) \
                .execute()

            rec["similar_students"] = similar_students_response.data

        return recommendations

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
        Get a recommendation with university and similar student details.

        Args:
            recommendation_id: The ID of the recommendation

        Returns:
            Recommendation record with related details
        """
        # Get the recommendation
        recommendation_response = self.supabase.table("recommendations").select("*").eq("id", recommendation_id).limit(
            1).execute()

        if not recommendation_response.data:
            return None

        recommendation = recommendation_response.data[0]

        # Get the university
        university_id = recommendation["university_id"]
        university = self.get_university_by_id(university_id)

        # Get similar students
        similar_students = self.get_similar_students_for_recommendation(recommendation_id)

        # Combine all data
        result = {
            "recommendation": recommendation,
            "university": university,
            "similar_students": similar_students
        }

        return result

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
