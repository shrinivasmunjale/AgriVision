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

    # Database Configuration
    DATABASE_URL: str
    
    # Backend URL for image serving (defaults to localhost for development)
    BACKEND_URL: str = "http://localhost:8000"

    # Authentication (Supabase)
    SUPABASE_JWT_SECRET: str
    SUPABASE_JWT_ALGORITHM: str = "HS256"

    # Cloudflare R2 / S3 Storage
    R2_ACCESS_KEY: str
    R2_SECRET_KEY: str
    R2_ENDPOINT_URL: str
    R2_BUCKET_NAME: str

    # Modal ML Inference Serverless Endpoint
    MODAL_API_URL: str
    CONFIDENCE_THRESHOLD: float = 0.60

settings = Settings()
