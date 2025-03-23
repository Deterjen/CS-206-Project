import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from models import User
from utils import verify_password
from dotenv import load_dotenv
from datetime import datetime
from services.supabase_client import SupabaseDB

load_dotenv()

# Load Supabase URL and Key from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Initialize the Supabase client with the necessary parameters
supabase_client = SupabaseDB(url=supabase_url, key=supabase_key)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

async def authenticate(username: str, password: str):
    """Validate user credentials from Supabase."""
    user = await supabase_client.get_user_by_username(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return user

async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    """Decode JWT and fetch the user from Supabase."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Get user data from Supabase based on the decoded username (sub)
    user = await supabase_client.get_user_by_username(username)
    if user is None or user.get("disabled", False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user

def create_token(data: dict, expires_delta):
    """Generate JWT token for authentication."""
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)