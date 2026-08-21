from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text

from app.core.config import settings
from app.api.v1.api import api_router

from app.db.base_class import Base
from app.db.session import engine, SessionLocal
from app.models.user import User

import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Existing deployments created before scan context was introduced do
        # not receive new columns from create_all(). Keep this compatibility
        # upgrade here so a Render restart can serve scans before Alembic is
        # run as part of the deployment command.
        if conn.dialect.name == "postgresql":
            await conn.execute(text(
                "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS crop_age_days INTEGER"
            ))
            await conn.execute(text(
                "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS life_stage VARCHAR(50)"
            ))

    async with SessionLocal() as db:
        result = await db.execute(select(User))
        user = result.scalars().first()

        if user is None:
            print("Database empty. Running seed...")
            await seed.seed_data()
        else:
            print("Database already initialized.")

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
        "success": True,
        "message": "Server is healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
