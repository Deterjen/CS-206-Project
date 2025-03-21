import os
from typing import Dict
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate, create_token, get_current_active_user
# from database import update_user, delete_user
from models import Token, User, RecommendationRequest
from datetime import timedelta
from utils import get_hashed_password
import httpx

# Import your service and dependencies
from services.recommendation_service import UniversityRecommendationService
from services.supabase_client import SupabaseDB  # Make sure this import is correct

app = FastAPI()

# Load Supabase URL and Key from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Initialize the Supabase client with the necessary parameters
supabase_client = SupabaseDB(url=supabase_url, key=supabase_key)

# Initialize the UniversityRecommendationService
university_recommender_service = UniversityRecommendationService(supabase_client)

# Login route
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create a new JWT token for the authenticated user
    access_token_expires = timedelta(minutes=30)  # Adjust as needed
    access_token = create_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

# Register an account route
@app.post("/register/")
async def register_user(user_data: User):
    # Check if the email already exists in the 'auth.users' table
    existing_email = await supabase_client.get_user_by_email(user_data.email)
    
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the username already exists in the 'users' table
    existing_username = await supabase_client.get_user_by_username(user_data.username)
    
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create the user using Supabase authentication API
    try:
        # Sign up the user via Supabase authentication (this creates an entry in 'auth.users' table)
        response = await supabase_client.signup_user({"username": user_data.username,
                                                       "email": user_data.email,
                                                       "password": get_hashed_password(user_data.password)
                                                        })

        return {"message": "User registered successfully", "user": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")

# Updating account credentials route
@app.put("/user/update/{username}", response_model=User)
async def update_user_details(
    username: str,
    new_username: str = None,
    new_email: str = None,
    current_user: User = Depends(get_current_active_user),
):
    # Ensure the current user can only update their own details
    if username != current_user["username"]:
        raise HTTPException(status_code=403, detail="You can only update your own account")

    try:
        update_data = {}
        if new_username:
            update_data["username"] = new_username
        if new_email:
            update_data["email"] = new_email

        # Update the user in the custom 'users' table
        updated_user = await supabase_client.update_user(username, update_data)

        if not updated_user:
            raise HTTPException(status_code=400, detail="Failed to update user data")

        return updated_user

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

# Delete account route
@app.delete("/user/delete/{username}", response_model=Dict[str, str])
async def delete_user_from_db(
    username: str,
    current_user: User = Depends(get_current_active_user),
):
    # Ensure the current user can only delete their own account
    if username != current_user["username"]:
        raise HTTPException(status_code=403, detail="You can only delete your own account")

    try:
        # First, delete the user from the custom 'users' table
        delete_user_response = await supabase_client.delete_user(username)

        if not delete_user_response:
            raise HTTPException(status_code=400, detail="Failed to delete user data from users table")

        return {"message": "User deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

# University recommendation request
@app.post("/save_questionaire/{username}")
async def save_questionnaire(
    username: str,
    questionnaire_result: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),  # Depend on logged-in user
):
    try:
        # Ensure the username in the request matches the authenticated user's username
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only save questionnaire for your own account")

        # Proceed with processing the questionnaire if user is authenticated and authorized
        response = await university_recommender_service.process_questionnaire(username, dict(questionnaire_result))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/recommend/{username}")
async def get_recommendation(
    username: str,
    current_user: User = Depends(get_current_active_user),  # Depend on logged-in user
):
    try:
        # Ensure the username in the request matches the authenticated user's username
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only get recommendation for your own account")

        # Proceed with requesting for a recommendation if user is authenticated and authorized
        response = await university_recommender_service.generate_recommendations(username, 3)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")