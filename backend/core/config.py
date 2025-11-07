import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/recipe")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_ALG: str = "HS256"
    CORS_ORIGINS: list[str] = [o for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o]

settings = Settings()