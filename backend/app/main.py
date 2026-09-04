import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text

from app.core.config import settings
from app.api.v1.api import api_router

from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.models.user import User

import seed

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Existing deployments compatibility upgrade
            if conn.dialect.name == "postgresql":
                # Predictions
                await conn.execute(text(
                    "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS crop_age_days INTEGER"
                ))
                await conn.execute(text(
                    "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS life_stage VARCHAR(50)"
                ))
                await conn.execute(text(
                    "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS bounding_boxes JSONB"
                ))
                # Pesticides
                await conn.execute(text(
                    "ALTER TABLE pesticides ADD COLUMN IF NOT EXISTS active_ingredient VARCHAR(255) DEFAULT ''"
                ))
                await conn.execute(text(
                    "ALTER TABLE pesticides ADD COLUMN IF NOT EXISTS dosage VARCHAR(255) DEFAULT ''"
                ))
                await conn.execute(text(
                    "ALTER TABLE pesticides ADD COLUMN IF NOT EXISTS application_method VARCHAR(512) DEFAULT ''"
                ))
                await conn.execute(text(
                    "ALTER TABLE pesticides ADD COLUMN IF NOT EXISTS suitable_life_stages TEXT DEFAULT '[]'"
                ))
                # Fertilizers
                await conn.execute(text(
                    "ALTER TABLE fertilizers ADD COLUMN IF NOT EXISTS active_ingredient VARCHAR(255) DEFAULT ''"
                ))
                await conn.execute(text(
                    "ALTER TABLE fertilizers ADD COLUMN IF NOT EXISTS dosage VARCHAR(255) DEFAULT ''"
                ))
                await conn.execute(text(
                    "ALTER TABLE fertilizers ADD COLUMN IF NOT EXISTS application_method VARCHAR(512) DEFAULT ''"
                ))
                await conn.execute(text(
                    "ALTER TABLE fertilizers ADD COLUMN IF NOT EXISTS suitable_life_stages TEXT DEFAULT '[]'"
                ))
                # Users
                await conn.execute(text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)"
                ))
                await conn.execute(text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ))
            elif conn.dialect.name == "sqlite":
                for stmt in [
                    "ALTER TABLE predictions ADD COLUMN bounding_boxes JSON",
                    "ALTER TABLE predictions ADD COLUMN crop_age_days INTEGER",
                    "ALTER TABLE predictions ADD COLUMN life_stage VARCHAR(50)",
                    "ALTER TABLE pesticides ADD COLUMN active_ingredient VARCHAR(255) DEFAULT ''",
                    "ALTER TABLE pesticides ADD COLUMN dosage VARCHAR(255) DEFAULT ''",
                    "ALTER TABLE pesticides ADD COLUMN application_method VARCHAR(512) DEFAULT ''",
                    "ALTER TABLE pesticides ADD COLUMN suitable_life_stages TEXT DEFAULT '[]'",
                    "ALTER TABLE fertilizers ADD COLUMN active_ingredient VARCHAR(255) DEFAULT ''",
                    "ALTER TABLE fertilizers ADD COLUMN dosage VARCHAR(255) DEFAULT ''",
                    "ALTER TABLE fertilizers ADD COLUMN application_method VARCHAR(512) DEFAULT ''",
                    "ALTER TABLE fertilizers ADD COLUMN suitable_life_stages TEXT DEFAULT '[]'",
                    "ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)",
                    "ALTER TABLE users ADD COLUMN updated_at TIMESTAMP",
                ]:
                    try:
                        await conn.execute(text(stmt))
                    except Exception:
                        pass

        async with SessionLocal() as db:
            result = await db.execute(select(User))
            user = result.scalars().first()

            if user is None:
                print("Database empty. Running seed...")
                await seed.seed_data()
            else:
                print("Database already initialized.")
    except Exception as e:
        logger.error(f"[STARTUP ERROR] Database initialization failed: {e}", exc_info=True)
        print(f"[STARTUP ERROR] Database initialization failed: {e}")

    # Pre-warm ML models once at application startup
    try:
        from app.ml.model_loader import pytorch_model_loader
        from app.ml.yolo_detector import yolo_leaf_detector
        print(f"[STARTUP] PyTorch model status: ready={pytorch_model_loader.is_ready()}")
        print(f"[STARTUP] YOLOv8 model status: ready={yolo_leaf_detector.is_ready}")
    except Exception as e:
        print(f"[STARTUP WARNING] Model pre-warm notice: {e}")

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "https://agri-vision1.vercel.app",
        "https://agri-vision1-git-main-shrinivasmunjales-projects.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix=settings.API_V1_STR)



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "2.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
    }



@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "project": "AgriVision AI",
        "version": "2.0.1",
        "deployed_at": "2026-09-04",
    }
