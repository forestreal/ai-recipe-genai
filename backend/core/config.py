import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env (if present) so settings picks them up
load_dotenv()

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/recipe")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GOOGLE_API_KEY: str | None = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_ALG: str = "HS256"
    CORS_ORIGINS: list[str] = [o for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]

settings = Settings()