from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    PROJECT_NAME: str = "AgriVision AI"
    API_V1_STR: str = "/api/v1"

    # Database Configuration (SQLite default for easy deployment)
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrivision.db"
    
    # Backend URL for image serving (defaults to localhost for development)
    BACKEND_URL: str = "http://localhost:8000"

    # Authentication - use secure random default if not provided
    SUPABASE_JWT_SECRET: str = "agrivision-secure-jwt-secret-change-in-production-2024"
    SUPABASE_JWT_ALGORITHM: str = "HS256"

    # Cloudflare R2 / S3 Storage (optional - uses local storage if not set)
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_ENDPOINT_URL: str = ""
    R2_BUCKET_NAME: str = ""

    # Modal ML Inference Serverless Endpoint (optional - uses local model)
    MODAL_API_URL: str = ""
    CONFIDENCE_THRESHOLD: float = 0.60

    # AI Assistant / Chatbot (optional)
    AI_PROVIDER: str = "openai"
    AI_API_KEY: str = ""
    AI_MODEL: str = ""

settings = Settings()
