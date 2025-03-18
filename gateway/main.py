import os
from typing import Dict
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from auth import authenticate, create_token, get_current_active_user, create_user
from database import update_user, delete_user
from models import Token, User, RecommendationRequest
from datetime import timedelta
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

    access_token_expires = timedelta(minutes=30)
    access_token = create_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

# Register an account route
@app.post("/register/")
async def register_user(username: str, email: str, name: str, password: str):
    response = await create_user(username, email, name, password)

    # If there's an error in the response (e.g., username already exists), raise an HTTPException
    if response.get("error"):
        raise HTTPException(status_code=400, detail=response["error"])

    # Ensure that the response contains a success message and user data
    return {"message": response["message"], "user_data": response.get("data")}

# Update profile for an account route
@app.put("/users/{username}", response_model=User)
async def update_user_details(
    username: str,
    new_username: str = None,
    new_email: str = None,
    current_user: User = Depends(get_current_active_user),
):
    # Ensure the current user can only update their own details
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="You can only update your own account")

    # Call the update function from database.py
    response = await update_user(username, new_username, new_email)

    if response.get("error"):
        raise HTTPException(status_code=400, detail=response["error"])

    # Return the full user data after the update
    updated_user = response.get("user_data")
    return updated_user  # This should be the full user data, matching the User model

# Delete account route
@app.delete("/users/{username}", response_model=Dict[str, str])
async def delete_user_from_db(
    username: str,
    current_user: User = Depends(get_current_active_user),
):
    # Ensure the current user can only delete their own account
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="You can only delete your own account")

    # Call the delete function from the database module
    delete_response = await delete_user(username)

    if delete_response.get("error"):
        raise HTTPException(status_code=400, detail=delete_response["error"])

    return {"message": "User deleted successfully"}

# University recommendation request
@app.post("/recommend")
async def get_recommendations(user_data: RecommendationRequest):
    json_payload = jsonable_encoder(user_data)
    print("Received user data:", json_payload)  # Debugging output

    # You can use the university_recommender_service to generate recommendations
    try:
        # Assuming the recommendation service has a method like this
        recommendations = university_recommender_service.generate_recommendations(
            aspiring_student_id=user_data.id, top_n=10
        )

        # Return the recommendations
        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation service error: {str(e)}")