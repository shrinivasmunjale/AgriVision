# ✅ Image URL Fix - Production Images Will Load

## Problem Found

Image URLs were hardcoded to `http://localhost:8000/uploads/` in the storage service.

**Result:**
- Images uploaded on production returned: `http://localhost:8000/uploads/xyz.jpg`
- Frontend tried to load from localhost (which doesn't exist)
- Error: `net::ERR_CONNECTION_REFUSED`

## Solution Applied

### Made URLs Dynamic

**File:** `backend/app/services/storage.py`

**Before:**
```python
return f"http://localhost:8000/uploads/{unique_filename}"
```

**After:**
```python
backend_url = settings.BACKEND_URL
return f"{backend_url}/uploads/{unique_filename}"
```

### Added Configuration

**File:** `backend/app/core/config.py`

Added new setting:
```python
BACKEND_URL: str = "http://localhost:8000"
```

### Environment Variable

**File:** `backend/.env.example`

```env
# Local Development
BACKEND_URL=http://localhost:8000

# Production (Render)
BACKEND_URL=https://agrivision2.onrender.com
```

## How It Works Now

### Local Development:
1. Upload image
2. Saved to `backend/uploads/abc123.jpg`
3. Returns: `http://localhost:8000/uploads/abc123.jpg`
4. Frontend loads from local backend ✅

### Production (Render):
1. Upload image
2. Saved to Render's `uploads/abc123.jpg`
3. Returns: `https://agrivision2.onrender.com/uploads/abc123.jpg`
4. Frontend loads from Render backend ✅

## Render Configuration

**You need to set this environment variable on Render:**

1. Go to https://dashboard.render.com
2. Click your AgriVision service
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Add:
   - **Key:** `BACKEND_URL`
   - **Value:** `https://agrivision2.onrender.com`
6. Click "Save Changes"
7. Render will redeploy automatically

## After Setting Environment Variable

### Test Image Upload:
1. Visit: https://agri-vision1.vercel.app/auth/login
2. Login: farmer@test.com / password123
3. Go to "New Scan"
4. Upload image
5. Analyze
6. Go to History
7. **Images should load now!** ✅

### Expected Image URLs:
```
Production: https://agrivision2.onrender.com/uploads/abc123.jpg
Local:      http://localhost:8000/uploads/abc123.jpg
```

## Timeline

- ✅ **Now:** Code fixed and pushed
- ⏳ **+2 min:** Render auto-deploys
- ⏳ **Manual:** Set BACKEND_URL environment variable on Render
- ⏳ **+2 min:** Render redeploys with new env var
- ✅ **Done:** Upload image and see it load!

## Summary

**Root Cause:** Hardcoded localhost URL in storage service

**Fix:**
- ✅ Made URL dynamic using settings.BACKEND_URL
- ✅ Added BACKEND_URL to config
- ✅ Created .env.example with instructions

**Action Required:**
1. Wait for Render to deploy code (~2 min)
2. Set `BACKEND_URL=https://agrivision2.onrender.com` in Render environment
3. Wait for redeploy (~2 min)
4. Test image upload - images will load! 🎉

**After this fix, all uploaded images will have correct URLs and load properly!**
