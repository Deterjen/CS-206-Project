import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from utils import verify_password
from database import get_user, insert_user
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

async def authenticate(username: str, password: str):
    """Validate user credentials from Supabase."""
    user = await get_user(username)
    if not user or not verify_password(password, user.password):
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

    user = await get_user(username)
    if user is None or user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user

def create_token(data: dict, expires_delta):
    """Generate JWT token for authentication."""
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def create_user(username: str, email: str, name: str, password: str):
    response = insert_user(username, email, name, password)

    # If there's an error in the response (e.g., username already exists), raise an HTTPException
    if response.get("error"):
        raise HTTPException(status_code=400, detail=response["error"])

    # Ensure that the response contains a success message and user data
    return {"message": response["message"], "user_data": response.get("data")}
