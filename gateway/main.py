import logging
import time
from datetime import timedelta
from typing import Dict

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from auth import authenticate, create_token, get_current_active_user
from config import ALLOWED_ORIGINS, JAMAIBASE_PROJECT_ID, JAMAIBASE_PAT, ENVIRONMENT
from models import Token, User, RecommendationRequest
from services.llm_justification import JustificationGenerator
from services.recommendation_service import UniversityRecommendationService
from services.supabase_client import SupabaseDB
from services.utils.heartbeat_service import heartbeat_service
from utils import get_hashed_password

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Allow frontend requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Supabase client with the necessary parameters
supabase_client = SupabaseDB.from_env()

recommendation_service = UniversityRecommendationService(supabase_client)
logger.info("UniversityRecommendationService initialized.")

# Initialize the recommender with data
recommendation_service.initialize_recommender()
logger.info("Recommender initialized.")

# Initialize the recommender with data
justificationGenerator = JustificationGenerator(JAMAIBASE_PROJECT_ID, JAMAIBASE_PAT)
logger.info("JustificationGenerator initialized.")


# Add this at the end of your main.py file, after all routes are defined
@app.on_event("startup")
async def startup_event():
    """Runs when the FastAPI application starts up."""
    logger.info("Starting up University Recommender API")

    # Start the heartbeat manager
    await heartbeat_service.start()
    logger.info("Self-pinging heartbeat manager started")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the FastAPI application is shutting down."""
    logger.info("Shutting down University Recommender API")

    # Stop the heartbeat manager
    await heartbeat_service.stop()
    logger.info("Heartbeat manager stopped")


@app.get("/health")
async def heartbeat_endpoint():
    """
    Lightweight endpoint that returns basic status information
    while maintaining minimal performance impact.
    """
    return {
        "status": "healthy",
        "service": "University Recommender API",
        "timestamp": time.time(),
        "environment": ENVIRONMENT
    }


# Login route
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
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


# Saving questionnaire route
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
        response = await recommendation_service.process_questionnaire(username, dict(questionnaire_result))
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Generate recommendation route
@app.get("/recommendation/{username}")
async def generate_recommendation(
        username: str,
        number_of_results: int,
        current_user: User = Depends(get_current_active_user),  # Depend on logged-in user
):
    try:
        # Ensure the username in the request matches the authenticated user's username
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only get recommendation for your own account")

        # Proceed with requesting for a recommendation if user is authenticated and authorized
        response = await recommendation_service.generate_recommendations(username, number_of_results)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Getting all recommendation detail route
@app.get("/recommendation/all_details/{username}")
async def get_recommendation_details(
        username: str,
        current_user: User = Depends(get_current_active_user),  # Depend on logged-in user
):
    try:
        # Ensure the username in the request matches the authenticated user's username
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only get recommendation for your own account")

        # Proceed with requesting for all recommendations if user is authenticated and authorized
        response = await recommendation_service.get_all_recommendations_details(username)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Getting a single recommendation detail route
@app.get("/recommendation/detail/{username}/{recommendation_id}")
async def get_recommendation_details(
        username: str,
        recommendation_id: int,
        current_user: User = Depends(get_current_active_user),  # Depend on logged-in user
):
    try:
        # Ensure the username in the request matches the authenticated user's username
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only get recommendation for your own account")

        # Proceed with requesting for a recommendation if user is authenticated and authorized
        response = recommendation_service.get_recommendation_details(recommendation_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Getting similar student route
@app.get("/recommendation/similar_student/{username}/{recommendation_id}")
async def get_recommendation_details(
        username: str,
        recommendation_id: int,
        current_user: User = Depends(get_current_active_user),  # Depend on logged-in user
):
    try:
        # Ensure the username in the request matches the authenticated user's username
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only get recommendation for your own account")

        # Proceed with requesting for bunch of similar students to user, if user is authenticated and authorized
        response = recommendation_service.get_similar_students(recommendation_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/recommendation/justification/{username}/{recommendation_id}")
async def get_recommendation_justification(
        username: str,
        recommendation_id: int,
        current_user: User = Depends(get_current_active_user),
):
    try:
        # Ensure the username in the request matches the authenticated user's username
        if username != current_user["username"]:
            raise HTTPException(status_code=403, detail="You can only get justification for your own recommendations")

        # First, check if a justification already exists in the database
        existing_justification = supabase_client.get_recommendation_justification(recommendation_id)

        # If a justification exists, return it
        if existing_justification:
            logger.info(f"Retrieved existing justification for recommendation {recommendation_id}")
            return existing_justification

        logger.info(f"No existing justification found for recommendation {recommendation_id}, generating new one")

        # If no justification exists, generate it
        # Get recommendation details
        recommendation_details = recommendation_service.get_recommendation_details(recommendation_id)
        if not recommendation_details:
            raise HTTPException(status_code=404, detail=f"Recommendation with ID {recommendation_id} not found")

        # Get aspiring student profile
        aspiring_student_profile = await recommendation_service.get_aspiring_student_profile(username)

        # Get similar students
        similar_students = recommendation_service.get_similar_students(recommendation_id)

        # Generate justification
        justification = justificationGenerator.generate_justification(
            student_profile=aspiring_student_profile,
            recommended_university=recommendation_details["university"],
            similar_students={"students": similar_students}
        )

        # Save the justification to the database
        saved_justification = supabase_client.save_recommendation_justification(recommendation_id, justification)
        if saved_justification:
            logger.info(f"Successfully saved justification for recommendation {recommendation_id}")
        else:
            logger.warning(f"Failed to save justification for recommendation {recommendation_id}")

        return justification
    except Exception as e:
        logger.error(f"Error processing recommendation justification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
