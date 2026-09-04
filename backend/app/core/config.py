import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH) if ENV_PATH.exists() else ".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    PROJECT_NAME: str = "AgriVision AI"
    API_V1_STR: str = "/api/v1"

    # Database Configuration (Supabase PostgreSQL supported, SQLite fallback)
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrivision.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if not v or not isinstance(v, str) or v.startswith("prisma+"):
            # A local SQLite file is convenient while developing, but it is
            # ephemeral on hosted services such as Render/Railway.  Falling
            # back to it in production makes registration appear successful
            # while users are saved outside Supabase and disappear on restart.
            hosted_environment = any(
                os.getenv(name)
                for name in ("RENDER", "RENDER_EXTERNAL_URL", "RAILWAY_ENVIRONMENT", "K_SERVICE", "DYNO", "WEBSITE_HOSTNAME", "CONTAINER_APP_NAME")
            )
            if hosted_environment:
                print(
                    "[CONFIG WARNING] DATABASE_URL is not explicitly configured in this environment. "
                    "Using SQLite fallback. Configure DATABASE_URL in Azure/hosting settings for persistent production database."
                )
            v = "sqlite+aiosqlite:///./agrivision.db"
        
        # Supabase / Azure PostgreSQL URI conversion: postgres:// or postgresql:// -> postgresql+asyncpg://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("sqlite://") and not v.startswith("sqlite+aiosqlite://"):
            v = v.replace("sqlite://", "sqlite+aiosqlite://", 1)
            
        # Clean query parameters unsupported by asyncpg (e.g. ?pgbouncer=true)
        if "?pgbouncer=true" in v:
            v = v.replace("?pgbouncer=true", "")
        elif "&pgbouncer=true" in v:
            v = v.replace("&pgbouncer=true", "")

        # Check if persistent disk exists (/var/data or /data) for SQLite
        if "sqlite" in v and "./agrivision.db" in v:
            for persistent_dir in ["/var/data", "/data"]:
                if Path(persistent_dir).is_dir():
                    return f"sqlite+aiosqlite:///{persistent_dir}/agrivision.db"
                    
        return v

    # Backend URL for image serving (defaults to localhost for development)
    BACKEND_URL: str = "http://localhost:8000"

    @field_validator("BACKEND_URL", mode="before")
    @classmethod
    def assemble_backend_url(cls, v: Optional[str]) -> str:
        if v and v.strip() and v != "http://localhost:8000":
            return v.rstrip("/")
        # Check automatic platform environment variables (Render / Railway)
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url.rstrip("/")
        railway_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_url:
            return f"https://{railway_url}".rstrip("/")
        return v or "http://localhost:8000"

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
    CONFIDENCE_THRESHOLD: float = 0.50

    # AI Assistant / Chatbot (optional)
    AI_PROVIDER: str = "openai"
    AI_API_KEY: str = ""
    AI_MODEL: str = ""

settings = Settings()

