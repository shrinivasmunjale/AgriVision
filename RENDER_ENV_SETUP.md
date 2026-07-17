# 🚀 Render Environment Variable Setup

## ✅ CRITICAL FIX FOR IMAGE LOADING

Your images are not loading because the `BACKEND_URL` environment variable is not set on Render.

### Steps to Fix (Takes 2 minutes):

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Select your backend service**: `agrivision2`
3. **Click "Environment" tab** (left sidebar)
4. **Click "Add Environment Variable"**
5. **Add this variable**:
   - Key: `BACKEND_URL`
   - Value: `https://agrivision2.onrender.com`
6. **Click "Save Changes"**
7. **Wait for automatic redeploy** (2-3 minutes)

### ✅ After Setup:

- **Upload a NEW image** to test (old images still have localhost URLs in database)
- New predictions will have correct image URLs: `https://agrivision2.onrender.com/uploads/xxx.jpg`
- Images will load properly in the frontend

### 📝 What This Does:

The code now dynamically generates image URLs using the `BACKEND_URL` environment variable:
- **Development**: Uses `http://localhost:8000` (default)
- **Production**: Uses `https://agrivision2.onrender.com` (when env var is set)

### 🔍 Code Changes Made:

1. **backend/app/services/storage.py**: Now uses `os.getenv('BACKEND_URL')` for dynamic URLs
2. **backend/app/core/config.py**: Added `BACKEND_URL` setting with default value
3. **backend/.env.example**: Documented the new environment variable

---

## 🎯 Current System Status:

✅ Authentication working (login/register)
✅ Prediction flow working (upload → analyze → results)
✅ Disease database seeded (4 diseases, 4 pesticides, 3 fertilizers)
✅ Test users created (farmer@test.com, admin@test.com, expert@test.com)
✅ Frontend deployed on Vercel
✅ Backend deployed on Render
⚠️ **NEED TO SET**: `BACKEND_URL` environment variable on Render

---

## 📌 Next Steps After Setting Env Var:

1. Wait for Render to redeploy (watch the logs)
2. Test by uploading a new image at: https://agri-vision1.vercel.app/scan
3. Verify the image loads in history page
4. Old predictions will still have localhost URLs (database issue - those need manual cleanup or re-upload)
