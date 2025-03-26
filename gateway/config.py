import os
from pathlib import Path

from dotenv import load_dotenv

# Try to load .env file if it exists (for local development)
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try .env.local as fallback
    local_env_path = Path('.env.local')
    if local_env_path.exists():
        load_dotenv(local_env_path)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Authentication configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default to HS256

# JamAI configuration
JAMAIBASE_PROJECT_ID = os.getenv("JAMAIBASE_PROJECT_ID")
JAMAIBASE_PAT = os.getenv("JAMAIBASE_PAT")

# Deployment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL).split(",")

# Validation of required environment variables
required_vars = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "SECRET_KEY",
    "JAMAIBASE_PROJECT_ID",
    "JAMAIBASE_PAT"
]

missing_vars = [var for var in required_vars if not globals().get(var)]
if missing_vars:
    raise ValueError(f"Required environment variables not set: {', '.join(missing_vars)}")
