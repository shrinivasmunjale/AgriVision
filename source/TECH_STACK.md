# AgriVision AI Tech Stack

This project is a full-stack AI-powered crop disease detection platform for tomato leaf analysis and agricultural recommendations. The codebase currently implements the following technology stack.

## 1. Frontend

- Next.js 14
- React 18
- JavaScript
- Tailwind CSS
- TanStack React Query
- Framer Motion
- Lucide React icons
- Axios
- Supabase JavaScript client

The frontend is located in the [frontend](../frontend) app and is configured to run as a Next.js web application.

## 2. Backend

- Python
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- Uvicorn
- Gunicorn
- Alembic
- Python-Jose
- bcrypt
- python-multipart
- email-validator

The backend is implemented in [backend/app](../backend/app) and exposes REST endpoints through FastAPI.

## 3. Database

- PostgreSQL-ready architecture
- SQLAlchemy async database layer
- Prisma schema present for database tooling
- SQLite fallback for local development
- AioSQLite for async local database support

The project uses environment-driven database configuration in [backend/app/core/config.py](../backend/app/core/config.py), with support for PostgreSQL and local SQLite fallback.

## 4. AI / Machine Learning

- PyTorch
- TorchVision
- Ultralytics YOLOv8
- NumPy
- Pillow
- ReportLab

The ML-related code is under [backend/app/ml](../backend/app/ml) and includes model loading, detection, and disease prediction logic.

## 5. Authentication & Security

- JWT-based auth configuration
- Supabase-compatible auth settings
- password hashing via bcrypt
- CORS enabled for local and hosted frontend origins

## 6. Storage & File Handling

- Local uploads folder for processed images and documents
- Static file serving via FastAPI
- Cloud storage support is planned / configured for optional R2/S3 integration

## 7. Development & Deployment Tools

- Node.js / npm for frontend
- Python virtual environment for backend
- Docker support configured for backend services
- Git for version control
- Prisma CLI included in the root package configuration
- Vercel-friendly frontend deployment and Render/Railway-style backend deployment readiness

## 8. Summary

The project combines:

- Frontend: Next.js + React + Tailwind
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: PostgreSQL-first, SQLite fallback
- AI: PyTorch + Ultralytics + image-based disease detection
- Auth: JWT / Supabase-ready
- Deployment: container-friendly, cloud-ready web application

This is a modern AI-based agricultural monitoring application built for image analysis, disease classification, and recommendation services.
