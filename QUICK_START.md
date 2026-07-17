# AgriVision AI - Quick Start Guide

## 🚀 Installation Steps

### Step 1: Install Frontend Dependencies

Open PowerShell and run:

```powershell
cd D:\AgriVision
.\install-frontend.bat
```

This will:
- Clean npm cache
- Remove old dependencies  
- Install fresh compatible versions

**Expected Output**: "Frontend installation complete!"

---

### Step 2: Install Backend Dependencies

⚠️ **IMPORTANT**: Check your Python version first!

```powershell
python --version
```

- ✅ **Python 3.11 or 3.12**: Perfect! Continue below
- ❌ **Python 3.14**: See "Python 3.14 Issue" section below

If you have Python 3.11 or 3.12, run:

```powershell
cd D:\AgriVision
.\setup-backend.bat
```

This will:
- Create virtual environment
- Install all dependencies
- Set up database
- Seed test data

**Expected Output**: "Backend setup complete!"

---

### Step 3: Start Development Servers

```powershell
cd D:\AgriVision
.\start-dev.bat
```

This opens TWO windows:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

---

## 🎯 Access the Application

1. Open browser: **http://localhost:3000**

2. **Test Accounts**:
   - Admin: `admin@agrivision.com` / `admin123`
   - Farmer: `farmer@example.com` / `farmer123`

3. **API Documentation**: http://localhost:8000/docs

---

## ⚠️ Python 3.14 Issue

If you see Python 3.14, you have TWO options:

### Option A: Install Python 3.11 (RECOMMENDED - 5 minutes)

1. Download: https://www.python.org/downloads/
2. Run installer, check "Add Python to PATH"
3. Open NEW PowerShell window
4. Verify: `python --version` should show 3.11.x
5. Continue with Step 2 above

### Option B: Install Build Tools (Takes longer)

1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
2. Install "Desktop development with C++"
3. Restart computer
4. Continue with Step 2 above

---

## 🔧 Troubleshooting

### Frontend: "ERESOLVE unable to resolve dependency"

Run the cleanup script:
```powershell
cd D:\AgriVision\frontend
rmdir /s /q node_modules
del package-lock.json
npm cache clean --force
npm install
```

### Backend: "No module named 'sqlalchemy'"

Virtual environment not activated. Run:
```powershell
cd D:\AgriVision\backend
.venv\Scripts\activate.bat
```

Then verify: `python -m pip list` should show installed packages

### Backend: "alembic: command not found"

Use full path:
```powershell
.venv\Scripts\alembic.exe upgrade head
```

### Both: Port already in use

Close the existing server:
- Find the process: `netstat -ano | findstr :8000` (or :3000)
- Kill it: `taskkill /PID <number> /F`

---

## 📁 Project Structure

```
AgriVision/
├── backend/               # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config & security
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── .env              # Environment variables
│   └── requirements.txt   # Python dependencies
│
├── frontend/              # Next.js + React
│   ├── src/
│   │   ├── app/          # Pages (App Router)
│   │   ├── components/   # Reusable components
│   │   ├── contexts/     # Auth context
│   │   └── lib/          # API client
│   └── package.json       # Node dependencies
│
└── source/                # Documentation
```

---

## 🎨 Features Implemented

✅ **User Management**
- Registration & Login
- Role-based access (Admin, Expert, Farmer)
- Profile management

✅ **Disease Detection**
- Image upload (drag & drop)
- AI prediction (mock mode ready)
- Confidence scores

✅ **Recommendations**
- Pesticide suggestions
- Fertilizer recommendations  
- Custom similarity matching

✅ **Reports**
- PDF generation
- History tracking
- Detailed analysis

✅ **Admin Panel**
- User management
- Disease library
- Audit logs

---

## 🔐 Mock Mode (No External Services)

The project works WITHOUT:
- Supabase
- Modal AI
- Cloudflare R2

Perfect for development and testing!

---

## 📝 Next Steps After Installation

1. **Test the scan feature**: Upload a tomato leaf image
2. **Check admin panel**: Login as admin
3. **View history**: See past predictions
4. **Generate report**: Download PDF

---

## ❓ Need Help?

- API docs: http://localhost:8000/docs
- Check logs in terminal windows
- Review `.env` file in backend folder

**The code is 100% complete and ready to run!**

The only requirement is:
1. ✅ Frontend: Compatible Node.js and npm
2. ✅ Backend: Python 3.11/3.12 (or build tools for 3.14)

