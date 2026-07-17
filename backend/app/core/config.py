from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "AgriVision AI"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrivision.db"

    # Authentication
    SUPABASE_JWT_SECRET: str = "dev-secret"
    SUPABASE_JWT_ALGORITHM: str = "HS256"

    # Cloudflare R2 (Optional)
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_ENDPOINT_URL: str = ""
    R2_BUCKET_NAME: str = ""

    # Backend URL for image serving
    BACKEND_URL: str = "http://localhost:8000"

    # Modal (Optional)
    MODAL_API_URL: str = ""

    CONFIDENCE_THRESHOLD: float = 0.60

settings = Settings()