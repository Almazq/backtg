import os
from typing import List

from dotenv import load_dotenv


def load_environment() -> None:
    # Loads variables from a .env file if present
    load_dotenv()


def get_bot_token() -> str:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Add it to your environment or .env file.")
    return token


def get_cors_origins() -> List[str]:
    """
    Returns list of allowed origins for CORS.
    Use comma-separated domains in CORS_ORIGINS env (e.g., https://yourapp.com,http://localhost:5173)
    '*' allows all origins (development only).
    """
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


