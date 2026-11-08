"""Configuration loaded from environment variables (and an optional .env file)."""
import os

from dotenv import load_dotenv

load_dotenv()

FATSECRET_CLIENT_ID = os.getenv("FATSECRET_CLIENT_ID")
FATSECRET_CLIENT_SECRET = os.getenv("FATSECRET_CLIENT_SECRET")
TOKEN_URL = os.getenv("FATSECRET_TOKEN_URL", "https://oauth.fatsecret.com/connect/token")
API_URL = os.getenv("FATSECRET_API_URL", "https://platform.fatsecret.com/rest/server.api")
REQUEST_TIMEOUT = float(os.getenv("FATSECRET_TIMEOUT", "10"))
