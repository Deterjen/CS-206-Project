import os
from supabase import create_client
from dotenv import load_dotenv
from models import User
from utils import get_hashed_password

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_user(username: str):
    """Fetch user from Supabase users table."""
    response = supabase.table("users").select("*").eq("username", username).execute()
    
    if response.data and len(response.data) > 0:
        user_data = response.data[0]
        return User(
            username=user_data["username"],
            email=user_data["email"],
            name=user_data["name"],
            password=user_data["password"],  # Hashed password stored in Supabase
            disabled=user_data["disabled"]
        )
    return None

def insert_user(username: str, email: str, name: str, password: str):
    # Check if the username already exists
    existing_user = supabase.table("users").select("*").eq("username", username).execute()
    if existing_user.data:  # If user already exists with the same username
        return {"error": "Username already exists"}

    # Check if the email already exists
    existing_email = supabase.table("users").select("*").eq("email", email).execute()
    if existing_email.data:  # If user already exists with the same email
        return {"error": "Email already exists"}

    # Proceed with inserting the new user if no existing username
    hashed_password = get_hashed_password(password)
    user_data = {
        "username": username,
        "email": email,
        "name": name,
        "password": hashed_password,
        "disabled": False
    }

    # Insert the new user into the database
    response = supabase.table("users").insert(user_data).execute()

    # Print the entire response to inspect its structure
    print("Full Response:", response)
    print("Response Data:", response.data)  # This should contain the inserted user data
    print("Response Status Code (if available):", getattr(response, 'status_code', 'No status_code attribute'))
    print("Response Count:", getattr(response, 'count', 'No count attribute'))  # Check if count exists

    # Check if there is an error in the response
    if hasattr(response, 'error') and response.error:
        return {"error": response.error.message}  # Handle the error if exists

    # If no error and response contains data, return the success message and user data
    return {"message": "User created successfully", "user_data": response.data[0] if response.data else {}}

async def update_user(username: str, new_username: str = None, new_email: str = None):
    """Update user details (username or email) in Supabase users table."""
    user = await get_user(username)
    if not user:
        return {"error": "User not found"}

    # Check if new_username or new_email is already taken
    if new_username:
        existing_user = await get_user(new_username)
        if existing_user:
            return {"error": "Username already exists"}

    if new_email:
        existing_email = supabase.table("users").select("*").eq("email", new_email).execute()
        if existing_email.data:
            return {"error": "Email already exists"}

    # Prepare the updated fields
    updated_data = {}
    if new_username:
        updated_data["username"] = new_username
    if new_email:
        updated_data["email"] = new_email

    # Only attempt to update if there is data to update
    if updated_data:
        response = supabase.table("users").update(updated_data).eq("username", username).execute()

        if hasattr(response, 'error') and response.error:
            return {"error": response.error.message}  # Handle the error if exists

        return {"message": "User updated successfully", "user_data": response.data[0] if response.data else {}}
    else:
        return {"error": "No valid fields to update"}

async def delete_user(username: str):
    try:
        # Fetch the user from Supabase
        response = supabase.table('users').select('*').eq('username', username).execute()
        if not response.data:
            return {"error": "User not found"}

        # Delete the user from Supabase
        delete_response = supabase.table('users').delete().eq('username', username).execute()

        if delete_response.error:
            return {"error": delete_response.error.message}

        return {"message": "User deleted successfully"}
    except Exception as e:
        return {"error": str(e)}
