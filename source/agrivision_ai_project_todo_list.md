# AgriVision AI — Project Todo List

This document outlines the atomic, sequentially ordered implementation tasks for building **AgriVision AI**. 

## Tech Stack Summary
- **Frontend**: Next.js 15 (App Router) + plain JavaScript + Tailwind CSS + TanStack Query + Framer Motion.
- **Backend**: FastAPI (Python) + SQLAlchemy 2.0 (async) + Pydantic v2 + PostgreSQL (Neon/Supabase serverless).
- **Authentication**: Supabase Auth (Client-validated JWT).
- **Image Storage**: Cloudflare R2 (S3-compatible bucket).
- **ML Inference**: EfficientNetB0 (TensorFlow/Keras) deployed on Modal (Serverless GPU).
- **Recommendation Engine**: Cosine similarity via `scikit-learn` over TF-IDF vectorized treatment profiles.
- **Reporting**: Backend PDF generation (ReportLab or WeasyPrint).

---

## Task Dependency Map & Sequential Order

| Task ID | Component | Task Name | Dependencies |
| :--- | :--- | :--- | :--- |
| **TASK-01** | Backend | Initialize Backend Repository & Config | None |
| **TASK-02** | Backend | Configure Docker for Local API Development | TASK-01 |
| **TASK-03** | Database | Spin up Serverless PostgreSQL Instance | TASK-01 |
| **TASK-04** | Backend | Initialize Alembic & SQLAlchemy Engine | TASK-02, TASK-03 |
| **TASK-05** | Database | Database Migration: `users` Table | TASK-04 |
| **TASK-06** | Database | Database Migration: `diseases` Table | TASK-04 |
| **TASK-07** | Database | Database Migration: `pesticides` and `fertilizers` Tables | TASK-04 |
| **TASK-08** | Database | Database Migration: Junction Mapping Tables | TASK-06, TASK-07 |
| **TASK-09** | Database | Database Migration: `predictions` Table | TASK-05, TASK-06 |
| **TASK-10** | Database | Database Migration: `recommendations` & `reports` Tables | TASK-07, TASK-09 |
| **TASK-11** | Database | Database Migration: `audit_logs` Table | TASK-05 |
| **TASK-12** | Backend | Seed Script: Initial Disease & Agrochemical Catalog | TASK-08 |
| **TASK-13** | Backend | Implement Supabase Auth Middleware in FastAPI | TASK-05 |
| **TASK-14** | Backend | Build Authenticated Profile Routes (`/auth/register`, `/auth/me`) | TASK-13 |
| **TASK-15** | Backend | Implement Role-Based Access Control (RBAC) Dependency | TASK-14 |
| **TASK-16** | ML / Infra | Store EfficientNetB0 Model Artifacts in Object Storage | TASK-01 |
| **TASK-17** | ML / Infra | Code Modal GPU Worker Script | TASK-16 |
| **TASK-18** | ML / Infra | Deploy and Verify ML Inference Service on Modal | TASK-17 |
| **TASK-19** | Backend | Implement Cloudflare R2 Storage Client Wrapper | TASK-01 |
| **TASK-20** | Backend | Build Multipart Image Upload Endpoint `/predictions/upload` | TASK-19 |
| **TASK-21** | Backend | Implement Cosine Similarity Recommendation Service | TASK-08 |
| **TASK-22** | Backend | Build Inference & Recommendation Pipeline Orchestrator | TASK-10, TASK-18, TASK-20, TASK-21 |
| **TASK-23** | Backend | Build GET Prediction History Endpoints | TASK-22 |
| **TASK-24** | Backend | Code Server-side PDF Report Layout Service | TASK-01 |
| **TASK-25** | Backend | Build GET PDF Report Generation Endpoint | TASK-10, TASK-24 |
| **TASK-26** | Frontend | Initialize Next.js 15 Project with Tailwind | None |
| **TASK-27** | Frontend | Configure Tailwind and CSS Styling Variables | TASK-26 |
| **TASK-28** | Frontend | Install Core UI Dependencies (Framer Motion, Lucide) | TASK-26 |
| **TASK-29** | Frontend | Build Desktop Sidebar / Mobile Bottom Tab App Shell | TASK-27, TASK-28 |
| **TASK-30** | Frontend | Configure Supabase Auth Client on Frontend | TASK-26 |
| **TASK-31** | Frontend | Build Login and Registration Pages | TASK-29, TASK-30 |
| **TASK-32** | Frontend | Build Farmer Dashboard Landing Page | TASK-29, TASK-31 |
| **TASK-33** | Frontend | Build Image Upload & Selection Screen | TASK-32 |
| **TASK-34** | Frontend | Build Analysis Processing Loader & Progress Indicator | TASK-33 |
| **TASK-35** | Frontend | Build Diagnostic Results Screen (Confidence Ring) | TASK-34 |
| **TASK-36** | Frontend | Build Recommendation Detail Cards & Instructions | TASK-35 |
| **TASK-37** | Frontend | Build Prediction History Grid & Search Filters | TASK-32 |
| **TASK-38** | Frontend | Integrate PDF Report Download Action | TASK-36, TASK-37 |
| **TASK-39** | Backend | Build Admin CRUD API Endpoints | TASK-15 |
| **TASK-40** | Backend | Build Admin Analytics API Endpoint | TASK-15 |
| **TASK-41** | Frontend | Build Admin App Shell and Layout | TASK-29 |
| **TASK-42** | Frontend | Build Admin Catalog Management Screens | TASK-39, TASK-41 |
| **TASK-43** | Frontend | Build Admin Analytics Dashboard Charts | TASK-40, TASK-41 |
| **TASK-44** | Testing | Set Up Playwright/Cypress & Write E2E Tests | TASK-38, TASK-42, TASK-43 |
| **TASK-45** | Frontend | Execute Accessibility, Contrast, and Asset Optimization Pass | TASK-38, TASK-42 |
| **TASK-46** | Backend | Deploy Production Database Migrations | TASK-12 |
| **TASK-47** | Backend | Deploy API Backend to Railway | TASK-12, TASK-25 |
| **TASK-48** | Frontend | Deploy Next.js Web App to Vercel | TASK-38, TASK-43 |
| **TASK-49** | Testing | Run Manual End-to-End Verification Walkthrough | TASK-47, TASK-48 |

---

## Detailed Task Specifications

### Phase 1: Environment Setup & Infrastructure Foundations

#### TASK-01: Initialize Backend Repository & Config
- **Description**: Setup a clean repository containing a FastAPI application scaffold using Python 3.11+. Configure dotenv configurations, linting rules, and virtual environments.
- **Objective**: Create the baseline server app file structure.
- **Acceptance Criteria**: 
  - Git repository initialized.
  - Baseline virtual env setup with a `requirements.txt` file containing fastapi, uvicorn, pydantic, and python-dotenv.
  - Server starts locally via `uvicorn main:app --reload`.
- **Dependencies**: None

#### TASK-02: Configure Docker for Local API Development
- **Description**: Create a Dockerfile for the FastAPI app and a docker-compose setup to orchestrate local development.
- **Objective**: Ensure containerized parity across developers and environments.
- **Acceptance Criteria**: 
  - Dockerfile builds the python environment correctly.
  - `docker-compose up` spins up the backend on port 8000 successfully.
- **Dependencies**: TASK-01

#### TASK-03: Spin up Serverless PostgreSQL Instance
- **Description**: Provision a Postgres serverless database cluster on Neon or Supabase and retrieve connection URIs.
- **Objective**: Establish the live database target.
- **Acceptance Criteria**: 
  - Database cluster active.
  - Connection string stored securely in backend `.env` variables.
  - Verified connection capability using a simple database query client tool.
- **Dependencies**: TASK-01

---

### Phase 2: Database Schema & Migration Setup

#### TASK-04: Initialize Alembic & Database Engine
- **Description**: Configure SQLAlchemy 2.0 with an async database engine block. Initialize Alembic migrations in the directory.
- **Objective**: Ready the project for schema migrations.
- **Acceptance Criteria**: 
  - `alembic init alembic` executed.
  - `env.py` configured to read the db connection URL from local settings.
  - Alembic is capable of connecting and detecting models.
- **Dependencies**: TASK-02, TASK-03

#### TASK-05: Database Migration: `users` Table
- **Description**: Write a SQLAlchemy model and run a database migration to create the `users` table.
- **Objective**: Store user credentials and details.
- **Acceptance Criteria**: 
  - Table fields match: `id` (UUID/Text PK), `name` (string), `email` (string, unique), `role` (enum: "Farmer", "Admin"), `farm_name` (nullable string), `phone` (nullable string), `created_at` (timestamp).
  - Migration script generated, applied via `alembic upgrade head`, and table verified in DB.
- **Dependencies**: TASK-04

#### TASK-06: Database Migration: `diseases` Table
- **Description**: Create the model and migration for the `diseases` knowledge base table.
- **Objective**: Store structured disease information.
- **Acceptance Criteria**: 
  - Table fields match: `id` (integer/UUID PK), `name` (string, unique), `description` (text), `symptoms` (text), `causes` (text), `severity_level` (string), `reference_image_url` (nullable string).
  - Migration applied successfully.
- **Dependencies**: TASK-04

#### TASK-07: Database Migration: `pesticides` and `fertilizers` Tables
- **Description**: Write models and migrations for the agrochemical catalogs.
- **Objective**: Store pesticide and fertilizer records.
- **Acceptance Criteria**: 
  - `pesticides` table: `id` (PK), `name` (string), `active_ingredient` (string), `dosage` (string), `application_method` (string).
  - `fertilizers` table: `id` (PK), `name` (string), `composition` (string), `dosage` (string), `application_stage` (string).
  - Migrations applied successfully.
- **Dependencies**: TASK-04

#### TASK-08: Database Migration: Junction Mapping Tables
- **Description**: Write models and migrations for the M:N junction tables matching diseases to pesticides and fertilizers.
- **Objective**: Establish the relational links for recommendation lookup queries.
- **Acceptance Criteria**: 
  - Create table `disease_pesticide` with composite PK/FK (`disease_id`, `pesticide_id`).
  - Create table `disease_fertilizer` with composite PK/FK (`disease_id`, `fertilizer_id`).
  - Migrations applied successfully.
- **Dependencies**: TASK-06, TASK-07

#### TASK-09: Database Migration: `predictions` Table
- **Description**: Create the model and migration for prediction logs.
- **Objective**: Persist classification metadata.
- **Acceptance Criteria**: 
  - Table fields: `id` (UUID PK), `user_id` (FK to `users`), `image_url` (string), `disease_id` (nullable FK to `diseases`), `confidence_score` (float), `created_at` (timestamp).
  - Migration applied successfully.
- **Dependencies**: TASK-05, TASK-06

#### TASK-10: Database Migration: `recommendations` & `reports` Tables
- **Description**: Build schemas storing generated recommendations and PDF report metadata.
- **Objective**: Track recommended items and downloadable exports.
- **Acceptance Criteria**: 
  - `recommendations`: `id` (PK), `prediction_id` (FK to `predictions`), `pesticide_id` (nullable FK to `pesticides`), `fertilizer_id` (nullable FK to `fertilizers`), `similarity_score` (float).
  - `reports`: `id` (PK), `prediction_id` (FK to `predictions`), `file_url` (string), `generated_at` (timestamp).
  - Migrations applied successfully.
- **Dependencies**: TASK-07, TASK-09

#### TASK-11: Database Migration: `audit_logs` Table
- **Description**: Setup table to audit changes to the catalog made by admins.
- **Objective**: Trace administrative actions.
- **Acceptance Criteria**: 
  - Table fields: `id` (PK), `admin_id` (FK to `users`), `action` (string), `entity` (string), `entity_id` (string), `timestamp` (timestamp).
  - Migration applied.
- **Dependencies**: TASK-05

#### TASK-12: Seed Script: Initial Disease & Agrochemical Catalog
- **Description**: Write a Python database seed script populating common tomato leaf diseases and their matching treatment catalogs.
- **Objective**: Establish dummy data for testing.
- **Acceptance Criteria**: 
  - Populates at least 5 disease profiles (e.g. Healthy, Early Blight, Late Blight, Bacterial Spot, Mosaic Virus).
  - Populates matching pesticide and fertilizer items.
  - Connects links in `disease_pesticide` and `disease_fertilizer` tables.
  - Run command `python seed.py` completes without errors.
- **Dependencies**: TASK-08

---

### Phase 3: Backend API Foundations & Authentication

#### TASK-13: Implement Supabase Auth Middleware in FastAPI
- **Description**: Implement authentication helper dependencies in FastAPI that read headers and validate Supabase-issued JWTs using python-jose.
- **Objective**: Safeguard API endpoints.
- **Acceptance Criteria**: 
  - Dependency verifies signatures against Supabase's JWKS endpoint.
  - Extracts the Supabase `sub` (user UID) and returns it.
  - Rejects missing, invalid, or expired tokens with a `401 Unauthorized` HTTP code.
- **Dependencies**: TASK-05

#### TASK-14: Build Authenticated Profile Routes (`/auth/register`, `/auth/me`)
- **Description**: Construct endpoints to onboard users authenticated via Supabase and read their profile statuses.
- **Objective**: Bind external auth users to local database models.
- **Acceptance Criteria**: 
  - `/api/v1/auth/register` (POST) creates a record in the local `users` table using details from the Supabase auth token.
  - `/api/v1/auth/me` (GET) returns user record profiles.
  - All return objects utilize clean Pydantic v2 validation models.
- **Dependencies**: TASK-13

#### TASK-15: Implement Role-Based Access Control (RBAC) Dependency
- **Description**: Create a FastAPI dependency that checks the user's role from the local `users` table.
- **Objective**: Gate admin-only endpoints.
- **Acceptance Criteria**: 
  - Verification functions accept a list of roles (e.g. `["Admin"]`).
  - If a user's record doesn't match the required role, throw an HTTP `403 Forbidden` error.
- **Dependencies**: TASK-14

---

### Phase 4: ML Inference Service Setup (Modal)

#### TASK-16: Store EfficientNetB0 Model Artifacts in Object Storage
- **Description**: Upload a benchmarked TensorFlow/Keras EfficientNetB0 model (`.keras` format) to a public or private bucket on Cloudflare R2.
- **Objective**: Make the model weights available to serverless workers.
- **Acceptance Criteria**: 
  - Object visible in R2 console.
  - URL accessible from the development environment (authenticated or signed).
- **Dependencies**: TASK-01

#### TASK-17: Code Modal GPU Worker Script
- **Description**: Program a Modal deployment script using python. It should:
  1. Define a container image loaded with `tensorflow`, `opencv-python-headless`, and `numpy`.
  2. Cache the model download on startup using Modal lifecycle hooks.
  3. Define a web-exposed function parsing image files, resizing to 224x224, performing normalization, and running inference.
- **Objective**: Establish the isolated serverless GPU runtime.
- **Acceptance Criteria**: 
  - Modal app runs successfully locally in sandbox mode using `modal serve`.
  - Exposes an endpoint accepting a JSON array of image URLs and returning classification probabilities.
- **Dependencies**: TASK-16

#### TASK-18: Deploy and Verify ML Inference Service on Modal
- **Description**: Deploy the worker script as a persistent service on Modal. Write a test script sending sample images to verify the endpoint outputs.
- **Objective**: Host the ML model on live serverless GPUs.
- **Acceptance Criteria**: 
  - Deploy command `modal deploy worker.py` completes.
  - Python test request returns structured JSON arrays containing labels ("Early Blight", "Healthy") and confidence decimals.
- **Dependencies**: TASK-17

---

### Phase 5: Core Image Upload & Storage Integration (Cloudflare R2)

#### TASK-19: Implement Cloudflare R2 Storage Client Wrapper
- **Description**: Build a Python module wrapping AWS S3 connection engines (using `boto3` or `aioboto3` client libraries) using custom endpoint URLs referencing Cloudflare R2 targets.
- **Objective**: Abstract image uploads to object storage.
- **Acceptance Criteria**: 
  - Client initializes using standard environment variables (`R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_ENDPOINT_URL`).
  - Helper functions support putting raw image bytes and returning URLs.
- **Dependencies**: TASK-01

#### TASK-20: Build Multipart Image Upload Endpoint `/predictions/upload`
- **Description**: Write a FastAPI route that handles single or batch image uploads, validates sizes/formats, and pushes them to R2.
- **Objective**: Accept drone images from the frontend client.
- **Acceptance Criteria**: 
  - Endpoints take file multipart form data.
  - Validates extension is `PNG`, `JPG`, or `TIFF`.
  - Rejects payloads exceeding 15MB.
  - Uploads validated assets, returns a list containing public bucket URLs.
- **Dependencies**: TASK-19

---

### Phase 6: Recommendation Engine & Backend Analysis Pipeline

#### TASK-21: Implement Cosine Similarity Recommendation Service
- **Description**: Build the recommendation system service.
- **Objective**: Match predictions with corresponding pesticides/fertilizers.
- **Acceptance Criteria**: 
  - Extracts the text profile of the predicted disease (symptoms, description) and candidate pesticide/fertilizer records.
  - Vectorizes text blocks using `scikit-learn`'s `TfidfVectorizer`.
  - Computes cosine similarity values.
  - Returns ranked listings of matched recommendations.
- **Dependencies**: TASK-08

#### TASK-22: Build Inference & Recommendation Pipeline Orchestrator
- **Description**: Construct the orchestrator endpoint `/api/v1/predictions/analyze`.
- **Objective**: Tie upload, classification, recommendation, and database logging in a single API transaction.
- **Acceptance Criteria**: 
  - Receives uploaded image URLs.
  - Pushes URLs to the live Modal inference endpoint.
  - Collects results. If confidence is < 60%, appends warning labels.
  - Runs the cosine similarity matching against local seed data.
  - Writes records to `predictions` and `recommendations` tables.
  - Responds with user-facing JSON detailing crop health.
- **Dependencies**: TASK-10, TASK-18, TASK-20, TASK-21

#### TASK-23: Build GET Prediction History Endpoints
- **Description**: Create routes to retrieve historical predictions.
- **Objective**: Display historical data trends.
- **Acceptance Criteria**: 
  - `/api/v1/predictions` (GET) returns a paginated list of user predictions, with query filters for `date_from`, `date_to`, and `disease_id`.
  - `/api/v1/predictions/{id}` (GET) returns the comprehensive details of a single scan (image, diagnosis, recommended pesticide/fertilizer items).
- **Dependencies**: TASK-22

---

### Phase 7: Backend PDF Report Generation

#### TASK-24: Code Server-side PDF Report Layout Service
- **Description**: Code a helper module utilizing ReportLab or WeasyPrint to compose a high-fidelity document layout matching the design guidelines.
- **Objective**: Render printable crop diagnostic reports.
- **Acceptance Criteria**: 
  - Output documents contain: AgriVision AI Branding, date, farmer profile details, uploaded leaf photo, disease classification, confidence level status, description, and list of recommended treatments.
- **Dependencies**: TASK-01

#### TASK-25: Build GET PDF Report Generation Endpoint
- **Description**: Add `/api/v1/predictions/{id}/report` route to generate the PDF and upload it to storage.
- **Objective**: Provide file downloads.
- **Acceptance Criteria**: 
  - Triggers the PDF generator using prediction database records.
  - Uploads the PDF file to Cloudflare R2.
  - Creates a record in the `reports` metadata table.
  - Serves the file as an attachment with correct MIME headers (`application/pdf`).
- **Dependencies**: TASK-10, TASK-24

---

### Phase 8: Frontend Initialization, Design System, & Routing

#### TASK-26: Initialize Next.js 15 Project with Tailwind
- **Description**: Setup frontend project directory scaffolding utilizing `create-next-app` in non-interactive configurations.
- **Objective**: Scaffolds the client codebase.
- **Acceptance Criteria**: 
  - Scaffolds using Next.js 15, App Router, standard JS, and Tailwind CSS configuration setup.
  - Replaced target placeholder contents with a base layout.
  - Run command `npm run dev` boots server.
- **Dependencies**: None

#### TASK-27: Configure Tailwind and CSS Styling Variables
- **Description**: Define custom token declarations in `tailwind.config.js` and CSS variables in `app/globals.css` referencing visual specifications in `DESIGN.md`.
- **Objective**: Establish the design system color scheme and typography.
- **Acceptance Criteria**: 
  - Brand green shades (`#0B2B1E`, `#1B4332`, `#297B5C`, `#34A65F`, `#A2F4C8`) and neutral backgrounds (`#1E1F22`, `#202124`, `#2A2E2B`) available as Tailwind utilities.
  - Web fonts configured (Manrope/Inter).
- **Dependencies**: TASK-26

#### TASK-28: Install Core UI Dependencies (Framer Motion, Lucide)
- **Description**: Install UI libraries and configure TanStack Query wrapper client settings.
- **Objective**: Support animations and state queries.
- **Acceptance Criteria**: 
  - Packages `framer-motion`, `lucide-react`, and `@tanstack/react-query` successfully installed and set up.
- **Dependencies**: TASK-26

#### TASK-29: Build Desktop Sidebar / Mobile Bottom Tab App Shell
- **Description**: Code a responsive master container shell utilizing responsive Tailwind styling.
- **Objective**: Render adaptive app navigation layout.
- **Acceptance Criteria**: 
  - Viewports `< 640px` render a bottom navigation bar with icons and labels (Home, Scan, History, Profile).
  - Viewports `>= 1024px` hide bottom navigation and render a persistent left sidebar panel.
- **Dependencies**: TASK-27, TASK-28

---

### Phase 9: Frontend Authentication & Profile Management

#### TASK-30: Configure Supabase Auth Client on Frontend
- **Description**: Initialize the Supabase JS client wrapper and create provider wrappers to share session scopes across client pages.
- **Objective**: Secure client sessions.
- **Acceptance Criteria**: 
  - Environment variables set.
  - User session states exposed dynamically via React context helpers.
- **Dependencies**: TASK-26

#### TASK-31: Build Login and Registration Pages
- **Description**: Build visual login and registration screens mirroring styling specs in `DESIGN.md`.
- **Objective**: Onboard users securely.
- **Acceptance Criteria**: 
  - Login view features split-panel design with brand graphics and dark card container inputs.
  - Buttons trigger sign-in routes and handle validation states.
  - Interacts with Supabase Auth correctly.
- **Dependencies**: TASK-29, TASK-30

---

### Phase 10: Frontend Farmer Dashboard & Upload Flow

#### TASK-32: Build Farmer Dashboard Landing Page
- **Description**: Implement `/dashboard` route compiling metrics and active card feeds.
- **Objective**: Create user landing views.
- **Acceptance Criteria**: 
  - Top displays: Total analyzed, Healthy ratio %, and weather tips.
  - Shows list layouts of recent prediction records.
  - Quick-action buttons redirect to the scan upload view.
- **Dependencies**: TASK-29, TASK-31

#### TASK-33: Build Image Upload & Selection Screen
- **Description**: Code the `/scan` page with drag-and-drop support.
- **Objective**: Handle user drone images.
- **Acceptance Criteria**: 
  - Custom dashed drop zone highlights visual borders (`primary-400`) during drag-over events.
  - Displays thumbnail previews of loaded files.
  - "Analyze" button is disabled until files are queued.
- **Dependencies**: TASK-32

#### TASK-34: Build Analysis Processing Loader & Progress Indicator
- **Description**: Implement a loading state screen for the upload flow.
- **Objective**: Keep users informed during model computation.
- **Acceptance Criteria**: 
  - Animate state changes showing upload progress.
  - Display micro-animations like skeleton frames.
- **Dependencies**: TASK-33

---

### Phase 11: Frontend Detection Results & Recommendations Display

#### TASK-35: Build Diagnostic Results Screen (Confidence Ring)
- **Description**: Render classification findings.
- **Objective**: Inform crop statuses.
- **Acceptance Criteria**: 
  - Animated SVG circular gauge representing the model's confidence percentage.
  - Flags low-confidence results with a warning badge.
- **Dependencies**: TASK-34

#### TASK-36: Build Recommendation Detail Cards & Instructions
- **Description**: Render treatment layouts.
- **Objective**: Guide crop actions.
- **Acceptance Criteria**: 
  - Custom card tabs list pesticide and fertilizer profiles.
  - Renders steps for active ingredients, dosages, and prevention tips.
- **Dependencies**: TASK-35

---

### Phase 12: Frontend Prediction History & PDF Download

#### TASK-37: Build Prediction History Grid & Search Filters
- **Description**: Build the history listing page.
- **Objective**: Enable review of past predictions.
- **Acceptance Criteria**: 
  - Display grid panels sorting items by timestamp.
  - Dropdown options filter list indices by specific diseases or field identifiers.
- **Dependencies**: TASK-32

#### TASK-38: Integrate PDF Report Download Action
- **Description**: Bind click buttons to API report generation routes.
- **Objective**: Save file reports offline.
- **Acceptance Criteria**: 
  - Button switches to a loading spinner.
  - Triggers browser file savings containing structured PDF data.
- **Dependencies**: TASK-36, TASK-37

---

### Phase 13: Backend Admin APIs & Analytics Queries

#### TASK-39: Build Admin CRUD API Endpoints
- **Description**: Construct `/api/v1/admin/diseases`, `pesticides`, and `fertilizers` write actions (`POST`, `PUT`, `DELETE`).
- **Objective**: Manage database libraries.
- **Acceptance Criteria**: 
  - Restricted to role credentials verified as Admin.
  - Writes to audit logs table.
- **Dependencies**: TASK-15

#### TASK-40: Build Admin Analytics API Endpoint
- **Description**: Build `/api/v1/admin/analytics` querying calculations across databases.
- **Objective**: Review usage and health.
- **Acceptance Criteria**: 
  - Compiles total users, scan rates, disease occurrences, and average confidence levels.
- **Dependencies**: TASK-15

---

### Phase 14: Frontend Admin Panel & Catalog CRUD

#### TASK-41: Build Admin App Shell and Layout
- **Description**: Scaffold the admin dashboard layouts.
- **Objective**: Separate administrative controls.
- **Acceptance Criteria**: 
  - Restricted page routes.
  - Sidebar links direct users to Catalog, Users, and Analytics screens.
- **Dependencies**: TASK-29

#### TASK-42: Build Admin Catalog Management Screens
- **Description**: Implement UI tables to list and update disease/treatment catalogs.
- **Objective**: Enable admin updates.
- **Acceptance Criteria**: 
  - Tabbed screens display list structures with options to edit item inputs.
  - Modals support file uploads for reference image fields.
- **Dependencies**: TASK-39, TASK-41

#### TASK-43: Build Admin Analytics Dashboard Charts
- **Description**: Code interactive graphs showing usage data trends.
- **Objective**: Summarize platform KPIs.
- **Acceptance Criteria**: 
  - Line graphs map daily uploads.
  - Pie charts show disease distributions.
- **Dependencies**: TASK-40, TASK-41

---

### Phase 15: Platform-wide Integration, Testing, & Optimization

#### TASK-44: Set Up Playwright/Cypress & Write E2E Tests
- **Description**: Build verification suites running end-to-end user browser interactions.
- **Objective**: Validate platform stability.
- **Acceptance Criteria**: 
  - Verified tests complete registration, scan analysis, history search, and catalog edits.
- **Dependencies**: TASK-38, TASK-42, TASK-43

#### TASK-45: Execute Accessibility, Contrast, and Asset Optimization Pass
- **Description**: Audit color contrasts and compress web assets.
- **Objective**: Meet accessibility standards.
- **Acceptance Criteria**: 
  - Contrast ratios meet WCAG AA standards.
  - Next.js image caching controls configured.
- **Dependencies**: TASK-38, TASK-42

---

### Phase 16: Deployment & Launch Preparation

#### TASK-46: Deploy Production Database Migrations
- **Description**: Execute Alembic migration updates on the production database.
- **Objective**: Set up the live database schema.
- **Acceptance Criteria**: 
  - Migrations execute cleanly against production connections.
  - Production tables seeded.
- **Dependencies**: TASK-12

#### TASK-47: Deploy API Backend to Railway
- **Description**: Host FastAPI on Railway with environment variables.
- **Objective**: Run backend services live.
- **Acceptance Criteria**: 
  - Server successfully deploys and exposes endpoints.
- **Dependencies**: TASK-12, TASK-25

#### TASK-48: Deploy Next.js Web App to Vercel
- **Description**: Link frontend repos to Vercel deploy targets.
- **Objective**: Host the client application.
- **Acceptance Criteria**: 
  - Deploy completes.
  - Frontend client redirects to production API targets.
- **Dependencies**: TASK-38, TASK-43

#### TASK-49: Run Manual End-to-End Verification Walkthrough
- **Description**: Perform manual verification of the production environment.
- **Objective**: Guarantee launch quality.
- **Acceptance Criteria**: 
  - The application is functional on live URLs.
- **Dependencies**: TASK-47, TASK-48
