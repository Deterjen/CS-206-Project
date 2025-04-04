import logging
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

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
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://unify-blue.vercel.app/").split(",")

# Heartbeat service configuration (to prevent idle shutdown on Render)
ENABLE_HEARTBEAT = os.getenv("ENABLE_HEARTBEAT", "True").lower() in ("true", "1", "t")
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "600"))
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL", "http://localhost:8000")  # URL to ping, defaults to own health endpoint


# Create a function to validate the configuration
def validate_config() -> List[str]:
    """
    Validates the configuration and returns a list of missing required variables.

    Returns:
        List[str]: List of missing required variables
    """
    required_vars = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY,
        "SECRET_KEY": SECRET_KEY,
        "JAMAIBASE_PROJECT_ID": JAMAIBASE_PROJECT_ID,
        "JAMAIBASE_PAT": JAMAIBASE_PAT
    }

    # In production, all variables are strictly required
    if ENVIRONMENT == "production":
        return [key for key, value in required_vars.items() if not value]

    # In development, just log warnings
    missing = [key for key, value in required_vars.items() if not value]
    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")

    return missing


# Validate the configuration when the module is imported
missing_vars = validate_config()
if ENVIRONMENT == "production" and missing_vars:
    raise ValueError(f"Required environment variables not set: {', '.join(missing_vars)}")
