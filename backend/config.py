import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "database", "cybershield.db"))
    RATE_LIMIT = os.getenv("RATE_LIMIT", "60 per minute")
    MAX_CONTENT_LENGTH = 32 * 1024  # reject request bodies over 32 KB
    MAX_URL_LENGTH = 2048
    MAX_TEXT_LENGTH = 5000
