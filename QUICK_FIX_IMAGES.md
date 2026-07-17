# 🚨 QUICK FIX - Images Not Loading

## Current Issue

Images still showing: `http://localhost:8000/uploads/...`

This means **BACKEND_URL is not set on Render yet**.

## Quick Fix - Set Environment Variable NOW

### Step 1: Go to Render
1. Visit: https://dashboard.render.com
2. Login
3. Click on your "agrivision" service

### Step 2: Add Environment Variable
1. Click **"Environment"** tab on the left
2. Scroll down to "Environment Variables"
3. Click **"Add Environment Variable"**
4. Enter:
   - **Key:** `BACKEND_URL`
   - **Value:** `https://agrivision2.onrender.com`
5. Click **"Save Changes"**

### Step 3: Wait for Redeploy
- Render will automatically redeploy (takes 2-3 minutes)
- Watch for "Deploy succeeded" message

## Verify It's Set

After redeploy, check the logs on Render. You should see:
```
BACKEND_URL: https://agrivision2.onrender.com
```

## Test After Setting

1. Go to: https://agri-vision1.vercel.app
2. Login: farmer@test.com / password123
3. Upload new image
4. Check image URL in browser console
5. Should now be: `https://agrivision2.onrender.com/uploads/...` ✅

## Alternative: Test Locally First

If you want to test now without waiting for Render:

### Local Backend:
```bash
cd backend
# On Windows CMD:
set BACKEND_URL=http://localhost:8000
# On PowerShell:
$env:BACKEND_URL="http://localhost:8000"
# Start backend:
uvicorn app.main:app --reload --port 8000
```

### Local Frontend:
```bash
cd frontend
npm run dev
```

Then visit: http://localhost:3001

## Why This Happens

**Default behavior:**
- storage.py uses: `os.getenv('BACKEND_URL', 'http://localhost:8000')`
- If `BACKEND_URL` not set → defaults to localhost
- Result: Wrong URLs on production ❌

**After setting BACKEND_URL:**
- storage.py uses: `os.getenv('BACKEND_URL')` 
- Gets: `https://agrivision2.onrender.com`
- Result: Correct URLs on production ✅

## Current vs Expected

**Current (Wrong):**
```
http://localhost:8000/uploads/abc123.jpg
→ ERR_CONNECTION_REFUSED (localhost doesn't exist in browser)
```

**Expected (Correct):**
```
https://agrivision2.onrender.com/uploads/abc123.jpg
→ Loads successfully! ✅
```

## Summary

**Problem:** BACKEND_URL environment variable not set on Render

**Solution:** 
1. Go to Render Dashboard
2. Environment tab
3. Add: `BACKEND_URL=https://agrivision2.onrender.com`
4. Save
5. Wait 2-3 minutes
6. Upload new image
7. Images will load! 🎉

---

**This is a one-time setup. After setting it, all future images will have correct URLs!**
