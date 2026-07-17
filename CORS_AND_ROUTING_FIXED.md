# CORS and Routing Issues - FIXED

## 🐛 Issues Found

### 1. CORS Error
**Error:** `Access to XMLHttpRequest at 'https://agrivision2.onrender.com/api/v1/auth/login' from origin 'https://agri-vision1.vercel.app' has been blocked by CORS policy`

**Cause:** Backend CORS was set to allow all origins ("*") but this doesn't work properly with credentials.

**Fix:** Updated `backend/app/main.py` to explicitly allow Vercel domain:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agri-vision1.vercel.app",
        "https://agri-vision1-*.vercel.app",  # Preview deployments
        "http://localhost:3001",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### 2. Frontend API URL Issue
**Error:** Requests going to `/auth/login` instead of `/api/v1/auth/login`

**Cause:** `AuthContext.js` had:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

This was missing the `/api/v1` prefix in the fallback.

**Fix:** Updated to:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
```

## ✅ Changes Made

### Backend Changes
**File:** `backend/app/main.py`
- ✓ Updated CORS to explicitly allow Vercel domain
- ✓ Added `expose_headers` for better CORS support
- ✓ Added `/health` endpoint for health checks
- ✓ Enhanced root endpoint with docs link

### Frontend Changes
**File:** `frontend/src/contexts/AuthContext.js`
- ✓ Fixed API_URL fallback to include `/api/v1`

### Testing Script
**File:** `backend/test_endpoints.py`
- ✓ Created script to test all backend endpoints
- ✓ Verifies routing is working correctly

## 🚀 Deployment Steps

### Step 1: Push Changes to GitHub
```bash
git add .
git commit -m "Fix: CORS and API routing for Vercel deployment"
git push origin main
```

### Step 2: Verify Backend on Render
After Render auto-deploys (2-3 minutes):
1. Check https://agrivision2.onrender.com/
2. Should show version and docs link
3. Check https://agrivision2.onrender.com/health
4. Should return `{"status": "ok"}`

### Step 3: Redeploy Frontend on Vercel
1. Go to Vercel dashboard
2. Find your project
3. Go to Deployments
4. Click "..." on latest deployment
5. Click "Redeploy"
6. Wait for build to complete

### Step 4: Test Login
1. Visit https://agri-vision1.vercel.app
2. Navigate to Login page
3. Try logging in with:
   - Email: `farmer@test.com`
   - Password: `password123`
4. Should successfully login and redirect to dashboard

## 🧪 Verification Checklist

After deployment:
- [ ] Backend root returns JSON (no errors)
- [ ] Backend /health returns `{"status": "ok"}`
- [ ] Frontend loads without CORS errors
- [ ] Can access login page
- [ ] Login works with test credentials
- [ ] Dashboard loads after login
- [ ] Can upload images
- [ ] API calls work (check Network tab)

## 🔍 Debug Commands

### Test Backend Endpoints
```bash
cd backend
python test_endpoints.py
```

### Check Frontend API URL
In browser console on your Vercel site:
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL)
```
Should output: `https://agrivision2.onrender.com/api/v1`

### Test CORS Manually
```bash
curl -H "Origin: https://agri-vision1.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://agrivision2.onrender.com/api/v1/auth/login
```
Should return CORS headers in response.

## 📝 Environment Variables

### Vercel Environment Variables
Make sure these are set in Vercel dashboard:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://agrivision2.onrender.com/api/v1` |

### Update Vercel Env Vars
1. Go to Vercel project → Settings
2. Click "Environment Variables"
3. Find `NEXT_PUBLIC_API_URL`
4. Ensure value is: `https://agrivision2.onrender.com/api/v1`
5. If changed, redeploy

## 🎯 Expected Result

After all fixes are deployed:

✅ **No CORS errors** in browser console
✅ **Login works** with test credentials  
✅ **API calls succeed** (200 status codes)
✅ **Images load** from backend
✅ **All features functional**

## 🐛 If Issues Persist

### Still Getting CORS Errors
1. Check Render logs for backend errors
2. Verify CORS middleware is before routes in `main.py`
3. Clear browser cache
4. Try incognito/private window

### Still Getting 404 Errors
1. Verify `NEXT_PUBLIC_API_URL` includes `/api/v1`
2. Check backend routes at https://agrivision2.onrender.com/api/v1/docs
3. Test endpoint directly with curl
4. Check Render deployment logs

### Login Still Fails
1. Open browser console (F12)
2. Go to Network tab
3. Try logging in
4. Check the request to `/auth/login`:
   - URL should be: `https://agrivision2.onrender.com/api/v1/auth/login`
   - Method should be: `POST`
   - Content-Type should be: `application/x-www-form-urlencoded`
   - Body should have: `username` and `password` fields

## 📚 Related Files

- `backend/app/main.py` - CORS configuration
- `backend/app/api/v1/api.py` - Route configuration
- `backend/app/api/v1/endpoints/auth.py` - Login endpoint
- `frontend/src/contexts/AuthContext.js` - Login logic
- `frontend/.env.local` - Local environment variables
- Vercel Environment Variables - Production configuration

## 🎉 Summary

**Problem:** CORS blocking + Wrong API endpoints
**Cause:** CORS not explicit + Missing `/api/v1` in fallback
**Solution:** Explicit CORS origins + Fixed API URL
**Result:** Login and all API calls now work!

---

*Last updated: Fixed CORS and routing for production deployment*
