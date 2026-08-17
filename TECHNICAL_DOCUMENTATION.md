# 🌾 AgriVision AI - Technical Documentation

**Complete Technical Stack & Data Flow Documentation**

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Overview](#architecture-overview)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [AI/ML Pipeline](#aiml-pipeline)
7. [Authentication & Security](#authentication--security)
8. [Deployment Architecture](#deployment-architecture)
9. [API Endpoints](#api-endpoints)
10. [File Storage](#file-storage)

---

## 🎯 Project Overview

**AgriVision AI** is a full-stack web application for AI-powered tomato leaf disease detection using drone-captured imagery.

### **Key Features:**
- 🤖 AI disease detection (10 disease classes)
- 📸 Drone imagery analysis
- 📊 Admin dashboard with analytics
- 💬 Farmer-to-admin contact system
- 🌍 Multi-language support (10+ Indian languages)
- 📱 Responsive mobile-first design
- 🌙 Dark/Light theme support
- 📄 PDF report generation

---

## 🛠️ Technology Stack

### **Frontend**

#### **Core Framework**
- **Next.js 14.2.5** - React framework with App Router
- **React 18.3.1** - UI library
- **React DOM 18.3.1** - DOM rendering

#### **Styling**
- **TailwindCSS 3.4.4** - Utility-first CSS framework
- **PostCSS 8.4.38** - CSS preprocessing
- **Autoprefixer 10.4.19** - CSS vendor prefixing

#### **State Management & Data Fetching**
- **TanStack Query (React Query) 5.51.1** - Server state management
- **Axios 1.7.2** - HTTP client

#### **UI & Animation**
- **Framer Motion 11.2.10** - Animation library
- **Lucide React 0.395.0** - Icon library (500+ icons)

#### **Development Tools**
- **ESLint 8.57.0** - Code linting
- **Next.js ESLint Config** - Next.js specific linting rules

---

### **Backend**

#### **Core Framework**
- **FastAPI 0.109.0** - Modern async web framework
- **Uvicorn 0.27.0** - ASGI server with standard extras
- **Python 3.11** - Programming language

#### **Data Validation**
- **Pydantic 2.5.0** - Data validation
- **Pydantic Settings 2.1.0** - Settings management
- **Email Validator 2.2.0** - Email validation

#### **Database**
- **SQLAlchemy 2.0.25** - ORM (Object-Relational Mapping)
- **Aiosqlite 0.19.0** - Async SQLite driver (development)
- **Asyncpg 0.29.0+** - Async PostgreSQL driver (production)
- **Alembic 1.13.1** - Database migrations

#### **Authentication & Security**
- **Python-Jose[cryptography] 3.3.0** - JWT token handling
- **Bcrypt 4.0.1** - Password hashing

#### **Machine Learning**
- **PyTorch 2.0.0-2.2.0** - Deep learning framework
- **TorchVision 0.15.0-0.17.0** - Computer vision models
- **Ultralytics 8.0.0+** - YOLOv8 object detection
- **NumPy 1.24.0-2.0.0** - Numerical computing
- **Pillow 10.0.0-11.0.0** - Image processing

#### **Utilities**
- **HTTPx 0.26.0** - Async HTTP client
- **Python-multipart 0.0.6** - File upload handling
- **Python-dotenv 1.0.0** - Environment variable management
- **ReportLab 4.0.0** - PDF generation

---

### **AI/ML Models**

#### **Disease Classification**
- **Model:** EfficientNetB0 (Pretrained on ImageNet, Fine-tuned)
- **Input:** 224x224 RGB images
- **Output:** 10 disease classes
- **Format:** PyTorch state_dict (.pth)
- **Size:** ~16 MB
- **Classes:**
  1. Healthy
  2. Early Blight
  3. Late Blight
  4. Bacterial Spot
  5. Tomato Mosaic Virus
  6. Leaf Mold
  7. Septoria Leaf Spot
  8. Spider Mites (Two-Spotted)
  9. Target Spot
  10. Tomato Yellow Leaf Curl Virus

#### **Leaf Detection (Optional)**
- **Model:** YOLOv8n (Nano)
- **Purpose:** Detect if image contains leaves before classification
- **Format:** PyTorch (.pt)
- **Size:** ~6 MB

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│  (Web Browser - Desktop/Mobile/Tablet)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                     FRONTEND (Next.js)                          │
│            Deployed on: Vercel                                  │
│            URL: https://agri-vision1.vercel.app                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Components:                                              │  │
│  │ - Landing Page                                           │  │
│  │ - Auth Pages (Login/Register)                            │  │
│  │ - Dashboard (Role-based)                                 │  │
│  │ - Scan Page (Image upload)                               │  │
│  │ - History (Predictions)                                  │  │
│  │ - Admin Panel (Analytics, Users, Predictions, Messages)  │  │
│  │ - Profile, FAQ, Tips, Contact                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Context Providers:                                       │  │
│  │ - AuthContext (JWT authentication)                       │  │
│  │ - ThemeContext (Dark/Light mode)                         │  │
│  │ - I18nContext (Multi-language)                           │  │
│  │ - QueryClient (TanStack Query)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API (JSON)
                         │ Authorization: Bearer <JWT>
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│            Deployed on: Render                                  │
│            URL: https://agrivision-ay2y.onrender.com            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Routes:                                              │  │
│  │ - /api/v1/auth (Login, Register, Profile)               │  │
│  │ - /api/v1/predictions (Upload, Analyze, History)        │  │
│  │ - /api/v1/admin (Analytics, Users, Predictions, Msgs)   │  │
│  │ - /contact (Contact messages)                            │  │
│  │ - /faq (FAQs)                                            │  │
│  │ - /chat (AI Assistant)                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Services:                                                │  │
│  │ - ML Inference (PyTorch model)                           │  │
│  │ - Storage (Local file system)                            │  │
│  │ - Recommendation Engine                                  │  │
│  │ - PDF Report Generator                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────┬───────────────┬──────────────┬──────────────────────────┘
         │               │              │
         │               │              │
         ▼               ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  Database   │  │   Storage    │  │   AI Model   │
│  (SQLite/   │  │  (/uploads)  │  │ (PyTorch)    │
│  PostgreSQL)│  │              │  │              │
│             │  │  - Images    │  │ - EfficientB0│
│ - Users     │  │  - PDFs      │  │ - YOLOv8     │
│ - Diseases  │  │              │  │              │
│ - Predictions│  │              │  │ 10 classes  │
│ - Reports   │  │              │  │ ~16MB model │
│ - Messages  │  │              │  │              │
└─────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔄 Data Flow

### **1. User Registration/Login Flow**

```
User enters credentials
        ↓
Frontend validates input
        ↓
POST /api/v1/auth/register OR /api/v1/auth/login
        ↓
Backend validates credentials
        ↓
Password hashed with bcrypt (12 rounds)
        ↓
User stored in database
        ↓
JWT token generated (30 days expiry)
        ↓
Token returned to frontend
        ↓
Stored in AuthContext (memory)
        ↓
Included in all subsequent API requests
```

### **2. Disease Prediction Flow**

```
User uploads image(s) on /scan page
        ↓
Frontend validates (file type, size <15MB)
        ↓
POST /api/v1/predictions/upload
        ↓
Backend receives file(s)
        ↓
File saved to /uploads/ directory
        ↓
Unique filename generated (UUID)
        ↓
Image URL created: {BACKEND_URL}/uploads/{UUID}.jpg
        ↓
URL returned to frontend
        ↓
POST /api/v1/predictions/analyze
        ↓
Backend loads PyTorch model (singleton, cached)
        ↓
Image preprocessed:
  - Resize to 224x224
  - Normalize (ImageNet mean/std)
  - Convert to tensor
        ↓
Model inference (EfficientNetB0)
        ↓
Softmax → Top prediction + confidence
        ↓
Disease ID mapped to database
        ↓
Recommendation fetched (pesticides, fertilizers)
        ↓
Prediction saved to database:
  - User ID
  - Image URL
  - Disease ID
  - Confidence score
  - Timestamp
        ↓
Response with:
  - Disease name
  - Confidence score
  - Symptoms
  - Treatment recommendations
        ↓
Frontend displays results
        ↓
Redirects to /history
```

### **3. Admin Analytics Flow**

```
Admin logs in
        ↓
Navigates to /admin
        ↓
GET /api/v1/admin/analytics
        ↓
Backend queries database:
  - COUNT(users)
  - COUNT(predictions)
  - AVG(confidence_score)
  - GROUP BY disease
        ↓
SQL aggregation queries executed
        ↓
JSON response with:
  - total_users
  - total_predictions
  - average_confidence
  - disease_distribution[]
  - recent_audits[]
        ↓
Frontend renders charts and cards
```

### **4. Contact Message Flow**

```
Farmer fills contact form
        ↓
POST /contact
        ↓
Message saved to database:
  - name
  - email
  - phone
  - message
  - timestamp
        ↓
Admin views messages:
        ↓
GET /api/v1/admin/contact-messages
        ↓
All messages returned (sorted by newest)
        ↓
Admin panel displays in table format
```

---

## 🗄️ Database Schema

### **Current Database: SQLite**
**Location (Local):** `d:\AgriVision\backend\agrivision.db`
**Location (Render):** Ephemeral filesystem (resets on deploy)

### **Production Database: PostgreSQL**
**Recommendation:** Use Render PostgreSQL addon for persistence

---

### **Tables & Relationships**

#### **1. users**
```sql
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'farmer',  -- 'farmer', 'expert', 'admin'
    farm_name VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **2. diseases**
```sql
CREATE TABLE diseases (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    symptoms TEXT,
    causes TEXT,
    severity_level VARCHAR(50),  -- 'Low', 'Medium', 'High'
    reference_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **3. predictions**
```sql
CREATE TABLE predictions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    image_url VARCHAR(500) NOT NULL,
    disease_id INTEGER REFERENCES diseases(id),
    confidence_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **4. pesticides**
```sql
CREATE TABLE pesticides (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    active_ingredient VARCHAR(255),
    dosage VARCHAR(255),
    application_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **5. fertilizers**
```sql
CREATE TABLE fertilizers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    composition VARCHAR(255),
    dosage VARCHAR(255),
    application_stage VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **6. recommendations**
```sql
CREATE TABLE recommendations (
    id VARCHAR(255) PRIMARY KEY,
    prediction_id VARCHAR(255) REFERENCES predictions(id),
    pesticide_id INTEGER REFERENCES pesticides(id),
    fertilizer_id INTEGER REFERENCES fertilizers(id),
    custom_advice TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **7. reports**
```sql
CREATE TABLE reports (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id),
    prediction_ids TEXT,  -- JSON array
    pdf_url VARCHAR(500),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **8. contact_messages**
```sql
CREATE TABLE contact_messages (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **9. audit_logs**
```sql
CREATE TABLE audit_logs (
    id VARCHAR(255) PRIMARY KEY,
    admin_id VARCHAR(255) REFERENCES users(id),
    action VARCHAR(100),  -- 'CREATE', 'UPDATE', 'DELETE'
    entity VARCHAR(100),  -- 'disease', 'pesticide', 'fertilizer'
    entity_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **10. disease_pesticide** (Many-to-Many)
```sql
CREATE TABLE disease_pesticide (
    disease_id INTEGER REFERENCES diseases(id),
    pesticide_id INTEGER REFERENCES pesticides(id),
    PRIMARY KEY (disease_id, pesticide_id)
);
```

#### **11. disease_fertilizer** (Many-to-Many)
```sql
CREATE TABLE disease_fertilizer (
    disease_id INTEGER REFERENCES diseases(id),
    fertilizer_id INTEGER REFERENCES fertilizers(id),
    PRIMARY KEY (disease_id, fertilizer_id)
);
```

---

### **Entity Relationship Diagram**

```
┌─────────┐      ┌──────────────┐      ┌──────────┐
│  users  │──────│ predictions  │──────│ diseases │
│         │ 1:N  │              │ N:1  │          │
│ - id    │      │ - id         │      │ - id     │
│ - name  │      │ - user_id    │      │ - name   │
│ - email │      │ - image_url  │      │ - symptoms│
│ - role  │      │ - disease_id │      │          │
└─────────┘      │ - confidence │      └────┬─────┘
                 └──────┬───────┘           │
                        │                   │ M:N
                        │ 1:N               │
                        ▼                   ▼
              ┌─────────────────┐   ┌──────────────┐
              │ recommendations │   │  pesticides  │
              │                 │   │              │
              │ - prediction_id │   │  fertilizers │
              │ - pesticide_id  │   │              │
              │ - fertilizer_id │   └──────────────┘
              └─────────────────┘
```

---

## 🤖 AI/ML Pipeline

### **Model Architecture**

```
Input Image (RGB, any size)
        ↓
Preprocessing:
  - Resize to 224x224
  - Normalize: mean=[0.485, 0.456, 0.406]
               std=[0.229, 0.224, 0.225]
  - Convert to Tensor
        ↓
EfficientNetB0 Backbone
  - 7 MBConv blocks
  - Squeeze-and-Excitation
  - Depthwise separable convolutions
        ↓
Global Average Pooling
        ↓
Fully Connected Layer (10 classes)
        ↓
Softmax Activation
        ↓
Output: [P(class_0), P(class_1), ..., P(class_9)]
        ↓
argmax → Predicted Class
max → Confidence Score
```

### **Model Training Details**

- **Dataset:** PlantVillage Tomato Leaf Dataset
- **Training Images:** ~18,000 images
- **Validation Split:** 20%
- **Augmentations:**
  - Random rotation (±15°)
  - Random horizontal flip
  - Random brightness/contrast
  - Color jitter
- **Optimizer:** Adam (lr=0.001)
- **Loss Function:** CrossEntropyLoss
- **Epochs:** 50
- **Best Validation Accuracy:** ~95%

### **Inference Performance**

| Environment | Device | Time per Image | Throughput |
|-------------|--------|----------------|------------|
| Local Dev | CPU (i5/Ryzen) | ~2-3 seconds | ~20-30 img/min |
| Render Free | Shared CPU | ~5-10 seconds | ~6-12 img/min |
| Render GPU | NVIDIA T4 | ~0.5 seconds | ~120 img/min |
| Modal API | Serverless GPU | ~0.3 seconds | ~200 img/min |

---

## 🔐 Authentication & Security

### **Authentication Flow**

1. **Registration:**
   - User provides: name, email, password, role, farm_name, phone
   - Password hashed with bcrypt (cost factor: 12)
   - User record created in database
   - Auto-login after registration

2. **Login:**
   - User provides: email, password
   - Backend fetches user by email
   - bcrypt verifies password hash
   - JWT token generated with:
     - `sub`: user ID
     - `email`: user email
     - `role`: user role
     - `exp`: expiration (30 days)
   - Token signed with `SUPABASE_JWT_SECRET`
   - Token returned to frontend

3. **Authorization:**
   - Frontend stores token in memory (AuthContext)
   - Every API request includes: `Authorization: Bearer {token}`
   - Backend verifies token signature
   - Extracts user ID from token
   - Fetches user from database
   - Checks role permissions
   - Allows/denies request

### **Role-Based Access Control (RBAC)**

| Role | Permissions |
|------|-------------|
| **farmer** | - Upload images<br>- View own predictions<br>- View own profile<br>- Contact admin<br>- View tips/FAQ |
| **expert** | - View all predictions<br>- Respond to farmer queries<br>- View analytics<br>- Generate reports |
| **admin** | - Full system access<br>- Manage users<br>- View all predictions<br>- CRUD diseases/pesticides/fertilizers<br>- View contact messages<br>- Platform analytics |

### **Security Measures**

- ✅ HTTPS only (Vercel/Render SSL)
- ✅ JWT tokens (signed, expires in 30 days)
- ✅ Bcrypt password hashing (12 rounds)
- ✅ CORS configured (Vercel domain only)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ File upload validation (type, size <15MB)
- ✅ Rate limiting (Render platform level)
- ✅ Environment variables for secrets

---

## 🚀 Deployment Architecture

### **Development Environment**

```
Local Machine
├── Backend
│   ├── Python 3.11 (.venv)
│   ├── FastAPI dev server (port 8000)
│   ├── SQLite database (agrivision.db)
│   ├── PyTorch model loaded
│   └── /uploads/ directory
└── Frontend
    ├── Node.js 18+
    ├── Next.js dev server (port 3000)
    └── .env.local (API_URL=http://localhost:8000)
```

### **Production Environment**

```
┌─────────────────────────────────────────────────────────┐
│                    VERCEL (Frontend)                    │
│  URL: https://agri-vision1.vercel.app                   │
│  ────────────────────────────────────────────────────   │
│  Deployment:                                            │
│  - Auto-deploy from GitHub (main branch)                │
│  - Build: next build                                    │
│  - Output: Static + Server Components                   │
│  - CDN: Global edge network                             │
│  - Environment Variables:                               │
│    * NEXT_PUBLIC_API_URL                                │
│  ────────────────────────────────────────────────────   │
│  Features:                                              │
│  - Automatic HTTPS                                      │
│  - Edge caching                                         │
│  - Image optimization                                   │
│  - Preview deployments                                  │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS REST API
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   RENDER (Backend)                      │
│  URL: https://agrivision-ay2y.onrender.com             │
│  ────────────────────────────────────────────────────   │
│  Deployment:                                            │
│  - Auto-deploy from GitHub (main branch)                │
│  - Build Command: pip install -r requirements.txt      │
│  - Start Command: uvicorn app.main:app --host 0.0.0.0  │
│  - Runtime: Python 3.11                                 │
│  - Instance: Free tier (512MB RAM, shared CPU)          │
│  ────────────────────────────────────────────────────   │
│  Environment Variables (MUST SET):                      │
│  ✅ BACKEND_URL=https://agrivision-ay2y.onrender.com    │
│  Optional:                                              │
│  - DATABASE_URL (for PostgreSQL)                        │
│  - MODAL_API_URL (for GPU inference)                    │
│  - AI_API_KEY (for chatbot)                             │
│  ────────────────────────────────────────────────────   │
│  Storage:                                               │
│  - SQLite: /workspace/agrivision.db (ephemeral)         │
│  - Uploads: /workspace/uploads/ (ephemeral)             │
│  - Model: /workspace/app/ml/*.pth (in repo)             │
│  ────────────────────────────────────────────────────   │
│  Features:                                              │
│  - Automatic HTTPS                                      │
│  - Health checks                                        │
│  - Auto-restart on crash                                │
│  - Free tier sleeps after 15min inactivity              │
└─────────────────────────────────────────────────────────┘
```

### **Data Storage Strategy**

#### **Current (Development/Testing):**
```
Location: Render Ephemeral Filesystem
Database: SQLite (agrivision.db)
Uploads: Local filesystem (/uploads/)
Issue: Resets on every deployment
```

#### **Recommended (Production):**
```
Location: Render + PostgreSQL Addon
Database: PostgreSQL (persistent)
Uploads: Cloudflare R2 or AWS S3
Benefits: No data loss, scalable, reliable
```

---

## 📡 API Endpoints

### **Base URL**
- **Production:** `https://agrivision-ay2y.onrender.com/api/v1`
- **Development:** `http://localhost:8000/api/v1`

### **Authentication Endpoints**

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | None | Register new user |
| POST | `/auth/login` | None | Login and get JWT token |
| GET | `/auth/me` | Required | Get current user profile |
| POST | `/auth/change-password` | Required | Change password |
| POST | `/auth/forgot-password` | None | Request password reset |
| POST | `/auth/reset-password` | None | Reset password with token |

### **Prediction Endpoints**

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/predictions/upload` | Required | Upload images to storage |
| POST | `/predictions/analyze` | Required | Analyze uploaded images with AI |
| GET | `/predictions/` | Required | Get user's predictions |
| GET | `/predictions/{id}` | Required | Get specific prediction |
| DELETE | `/predictions/{id}` | Required | Delete prediction |

### **Admin Endpoints**

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/analytics` | Admin | Platform analytics |
| GET | `/admin/users` | Admin | Get all users |
| GET | `/admin/predictions` | Admin | Get all predictions |
| GET | `/admin/contact-messages` | Admin | Get farmer messages |
| GET | `/admin/diseases` | Admin | Get all diseases |
| POST | `/admin/diseases` | Admin | Create disease |
| PUT | `/admin/diseases/{id}` | Admin | Update disease |
| DELETE | `/admin/diseases/{id}` | Admin | Delete disease |
| GET | `/admin/pesticides` | Admin | Get all pesticides |
| POST | `/admin/pesticides` | Admin | Create pesticide |
| PUT | `/admin/pesticides/{id}` | Admin | Update pesticide |
| DELETE | `/admin/pesticides/{id}` | Admin | Delete pesticide |
| GET | `/admin/fertilizers` | Admin | Get all fertilizers |
| POST | `/admin/fertilizers` | Admin | Create fertilizer |
| PUT | `/admin/fertilizers/{id}` | Admin | Update fertilizer |
| DELETE | `/admin/fertilizers/{id}` | Admin | Delete fertilizer |

### **Misc Endpoints**

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/contact` | None | Submit contact message |
| GET | `/faq` | None | Get FAQs |
| POST | `/chat` | Required | AI assistant chatbot |

---

## 📁 File Storage

### **Current Implementation (Development)**

```
Backend Server (Render)
└── /workspace/
    ├── agrivision.db (SQLite)
    ├── uploads/
    │   ├── {uuid-1}.jpg
    │   ├── {uuid-2}.jpg
    │   └── ...
    └── app/
        └── ml/
            ├── best_efficientnetb0.pth (16MB)
            ├── best.pt (YOLOv8, 6MB)
            └── class_names.json
```

**Image URL Format:**
```
{BACKEND_URL}/uploads/{filename}
Example: https://agrivision-ay2y.onrender.com/uploads/abc123.jpg
```

**Limitations:**
- ❌ Ephemeral filesystem (resets on deployment)
- ❌ No backup
- ❌ Not scalable
- ❌ Single server only

### **Recommended Implementation (Production)**

```
Cloudflare R2 / AWS S3
└── agrivision-images/
    ├── predictions/
    │   ├── {uuid-1}.jpg
    │   ├── {uuid-2}.jpg
    │   └── ...
    └── reports/
        ├── {uuid-1}.pdf
        ├── {uuid-2}.pdf
        └── ...
```

**Benefits:**
- ✅ Persistent storage
- ✅ Automatic backups
- ✅ CDN acceleration
- ✅ Scalable (unlimited storage)
- ✅ Cost-effective ($0.015/GB/month)

---

## 📊 Database: Current vs Production

### **Current Setup (Development/Testing)**

```yaml
Type: SQLite
Location: /workspace/agrivision.db (Render ephemeral filesystem)
Driver: aiosqlite (async)
Persistence: ❌ Resets on every deployment
Backup: ❌ None
Concurrency: ⚠️ Limited (file-based)
Best For: Development, testing, prototyping
```

**Pros:**
- ✅ Zero configuration
- ✅ No external dependencies
- ✅ File-based (portable)
- ✅ Fast for small datasets

**Cons:**
- ❌ Data lost on every Render deployment
- ❌ Not suitable for production
- ❌ Limited concurrent writes
- ❌ No replication/backup

---

### **Recommended Setup (Production)**

```yaml
Type: PostgreSQL
Location: Render PostgreSQL Addon (persistent)
Driver: asyncpg (async, high performance)
Persistence: ✅ Fully persistent across deployments
Backup: ✅ Automatic daily backups
Concurrency: ✅ Excellent (MVCC)
Best For: Production, multi-user, data integrity
```

**Pros:**
- ✅ Data persists across deployments
- ✅ Automatic backups
- ✅ Excellent concurrency
- ✅ ACID compliance
- ✅ Scalable (vertical + horizontal)
- ✅ Full-text search
- ✅ JSON support

**Setup:**
1. Add PostgreSQL addon on Render (free tier available)
2. Copy `DATABASE_URL` from addon
3. Set as environment variable on Render
4. Alembic auto-migrates schema
5. Seed data automatically runs

**Migration Command:**
```bash
# Backend auto-handles both SQLite and PostgreSQL
# Just set DATABASE_URL environment variable
DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

---

## 🔄 Migration Path: SQLite → PostgreSQL

### **Step-by-Step Guide:**

1. **Add PostgreSQL Addon on Render:**
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Select free tier
   - Name: `agrivision-db`
   - Create database

2. **Get Connection String:**
   ```
   Internal: postgresql://user:pass@hostname:5432/agrivision_db
   External: postgresql://user:pass@hostname.external:5432/agrivision_db
   ```

3. **Set Environment Variable:**
   ```bash
   Key:   DATABASE_URL
   Value: postgresql://user:pass@hostname:5432/agrivision_db
   ```

4. **Deploy Backend:**
   - Render auto-detects env var change
   - Redeploys backend
   - SQLAlchemy auto-connects to PostgreSQL
   - Alembic runs migrations
   - Seed script populates data

5. **Verify Migration:**
   ```bash
   # Check Render logs for:
   "[INFO] Connected to PostgreSQL"
   "[SUCCESS] Database seeding completed successfully"
   ```

---

## 📈 Performance Optimization

### **Current Performance**

| Metric | Value | Notes |
|--------|-------|-------|
| Page Load | ~1-2s | Next.js SSR + CDN |
| Image Upload | ~500ms | <15MB per image |
| AI Prediction | ~5-10s | CPU on Render free tier |
| Database Query | <100ms | Simple queries, SQLite |
| API Response | <200ms | Excluding ML inference |

### **Optimization Strategies**

#### **1. Faster Predictions:**
- Use Modal API with GPU (~0.3s per image)
- Upgrade Render to GPU instance
- Quantize model to INT8 (4x smaller, 2x faster)
- Use ONNX Runtime

#### **2. Database Performance:**
- Migrate to PostgreSQL (better concurrency)
- Add database indexes on frequently queried fields
- Use connection pooling

#### **3. Image Loading:**
- Migrate to Cloudflare R2 (CDN-backed)
- Implement image compression
- Use Next.js Image component (automatic optimization)

#### **4. Caching:**
- Cache frequently accessed data (TanStack Query)
- Implement Redis for session storage
- CDN caching for static assets

---

## 🎨 Frontend Architecture

### **Directory Structure**

```
frontend/src/
├── app/                    # Next.js App Router
│   ├── admin/             # Admin dashboard
│   ├── auth/              # Login/Register pages
│   ├── contact/           # Contact form
│   ├── dashboard/         # User dashboard
│   ├── faq/               # FAQ page
│   ├── history/           # Prediction history
│   ├── profile/           # User profile
│   ├── scan/              # Image upload & analysis
│   ├── tips/              # Farming tips
│   ├── layout.js          # Root layout
│   ├── page.js            # Landing page
│   └── providers.js       # Context providers
├── components/            # Reusable components
│   ├── landing/           # Landing page sections
│   ├── ui/                # UI components
│   ├── Chatbot.js         # AI assistant
│   ├── Layout.js          # App layout (sidebar, nav)
│   ├── UserMenu.js        # User dropdown menu
│   └── ...
├── contexts/              # React Context providers
│   ├── AuthContext.js     # Authentication state
│   ├── ThemeContext.js    # Dark/Light theme
│   └── I18nContext.js     # Multi-language
└── lib/
    └── api.js             # Axios API client
```

### **State Management**

- **Server State:** TanStack Query (React Query)
  - Caching
  - Background refetching
  - Optimistic updates
  
- **Client State:** React Context API
  - Auth state (user, token, profile)
  - Theme state (dark/light)
  - Language state (en, hi, mr, etc.)

---

## 🔧 Backend Architecture

### **Directory Structure**

```
backend/app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── admin.py          # Admin CRUD, analytics
│   │   │   ├── auth.py           # Login, register, profile
│   │   │   └── predictions.py    # Upload, analyze, history
│   │   └── api.py                # API router aggregator
│   └── deps.py                   # Dependency injection
├── core/
│   ├── config.py                 # Settings, env vars
│   └── security.py               # JWT, password hashing
├── db/
│   ├── base_class.py             # SQLAlchemy base
│   └── session.py                # Database session
├── ml/
│   ├── best_efficientnetb0.pth   # Disease classification model
│   ├── best.pt                   # YOLOv8 leaf detector
│   ├── class_names.json          # Disease class names
│   ├── labels.json               # Disease ID mapping
│   ├── model_loader.py           # PyTorch model loader
│   └── yolo_detector.py          # YOLO inference
├── models/                       # SQLAlchemy models (database tables)
│   ├── user.py
│   ├── disease.py
│   ├── prediction.py
│   ├── pesticide.py
│   ├── fertilizer.py
│   ├── recommendation.py
│   ├── report.py
│   ├── contact.py
│   └── audit_log.py
├── schemas/                      # Pydantic schemas (API validation)
│   ├── user.py
│   ├── disease.py
│   ├── prediction.py
│   ├── pesticide.py
│   └── fertilizer.py
├── services/                     # Business logic
│   ├── ml_inference.py           # ML prediction service
│   ├── storage.py                # File storage service
│   ├── recommendation.py         # Treatment recommendations
│   └── pdf_report.py             # PDF generation
└── main.py                       # FastAPI app entry point
```

---

## 🌐 Multi-Language Support

**Supported Languages (10+):**
1. English (en)
2. Hindi (hi) - हिन्दी
3. Marathi (mr) - मराठी
4. Telugu (te) - తెలుగు
5. Tamil (ta) - தமிழ்
6. Bengali (bn) - বাংলা
7. Gujarati (gu) - ગુજરાતી
8. Kannada (kn) - ಕನ್ನಡ
9. Malayalam (ml) - മലയാളം
10. Punjabi (pa) - ਪੰਜਾਬੀ
11. Odia (or) - ଓଡ଼ିଆ

**Implementation:**
- Google Translate API integration
- Client-side translation
- Language selector in header (visible on mobile)
- Persistent language preference

---

## 📄 Summary

| Component | Technology | Location | Status |
|-----------|-----------|----------|--------|
| **Frontend** | Next.js 14 + React 18 | Vercel | ✅ Deployed |
| **Backend** | FastAPI + Python 3.11 | Render | ✅ Deployed |
| **Database (Current)** | SQLite | Render (ephemeral) | ⚠️ Resets on deploy |
| **Database (Recommended)** | PostgreSQL | Render addon | 💡 To implement |
| **Storage (Current)** | Local filesystem | Render (ephemeral) | ⚠️ Resets on deploy |
| **Storage (Recommended)** | Cloudflare R2 / S3 | Cloud | 💡 To implement |
| **AI Model** | EfficientNetB0 | In repo (16MB) | ✅ Deployed |
| **Authentication** | JWT + bcrypt | Backend | ✅ Working |
| **File Uploads** | Multipart form | Backend + storage | ✅ Working |

---

## 🎯 Next Steps for Production

1. **Set BACKEND_URL** ⏳ (Critical for image loading)
2. **Migrate to PostgreSQL** 💡 (Data persistence)
3. **Implement Cloudflare R2** 💡 (Persistent image storage)
4. **Use Modal API for GPU** 💡 (Faster predictions)
5. **Add monitoring** 💡 (Sentry, LogRocket)
6. **Implement CI/CD tests** 💡 (Pytest, Jest)
7. **Add rate limiting** 💡 (Prevent abuse)
8. **Implement caching** 💡 (Redis)

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintained By:** AgriVision AI Team
