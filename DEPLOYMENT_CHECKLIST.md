# AgriVision AI - Deployment Checklist

## ✅ Backend Deployment (Render)

### Status: COMPLETED ✓

- [x] Backend deployed on Render
- [x] Database migrations applied
- [x] Test users created
- [x] Static file serving configured
- [x] Environment variables set
- [x] Health check endpoint working

**Backend URL:** Update with your actual URL
**Health Check:** `https://your-backend.onrender.com/` should return JSON

---

## 🚀 Frontend Deployment (Vercel)

### Pre-Deployment Checklist

- [x] **Configuration files created:**
  - `vercel.json` - Build configuration
  - `next.config.js` - Enhanced module resolution
  - `jsconfig.json` - Path mappings
  - `.vercelignore` - Build exclusions

- [x] **Code ready for production:**
  - Landing page redirects to dashboard
  - Dashboard accessible without login
  - All API endpoints using `@/lib/api`
  - Build succeeds locally (`npm run build`)

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Fix: Vercel deployment configuration"
   git push origin main
   ```

2. **Configure Vercel Project**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - **Root Directory:** `frontend` (if monorepo) or leave empty
   - **Framework Preset:** Next.js (auto-detected)
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
   - **Install Command:** `npm install` (default)

3. **Set Environment Variables**
   - Click "Environment Variables"
   - Add variable:
     - **Name:** `NEXT_PUBLIC_API_URL`
     - **Value:** `https://your-backend-url.onrender.com/api/v1`
   - Click "Add"

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)
   - Check build logs for errors

### Post-Deployment Verification

- [ ] Landing page loads and redirects to dashboard
- [ ] Dashboard displays without login
- [ ] Drone imagery section appears
- [ ] Can navigate to all pages
- [ ] Images load from backend
- [ ] API calls work (check browser console)
- [ ] Upload functionality works
- [ ] Can view prediction history
- [ ] PDF reports download correctly

### If Issues Occur

#### Build Fails with "Module not found: @/lib/api"

**Solution:**
1. Verify `frontend/src/lib/api.js` exists in git
2. Check `.gitignore` doesn't exclude `src/lib/`
3. Ensure all config files are committed
4. Try manual redeploy from Vercel dashboard

#### 404 on All Routes

**Solution:**
1. Verify root directory is set correctly
2. Check build logs for compilation errors
3. Ensure `src/app/` structure is correct
4. Verify no middleware blocking routes

#### CORS Errors

**Solution:** Update backend CORS settings:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy backend on Render.

#### Environment Variables Not Working

**Solution:**
1. Go to Vercel Project Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` is set
3. Click "Redeploy" on latest deployment

---

## 🔧 Backend CORS Update

After getting your Vercel URL:

1. Update `backend/app/main.py`:
   ```python
   allow_origins=[
       "https://your-vercel-app.vercel.app",
       "https://your-vercel-app-*.vercel.app",  # Preview deployments
       "http://localhost:3001",
   ]
   ```

2. Commit and push to trigger Render redeploy:
   ```bash
   git add backend/app/main.py
   git commit -m "Update CORS for Vercel deployment"
   git push origin main
   ```

---

## 🎯 Final Testing

Once both are deployed:

### Test User Accounts
```
Farmer Account:
Email: farmer@test.com
Password: password123

Admin Account:
Email: admin@test.com
Password: password123

Expert Account:
Email: expert@test.com
Password: password123
```

### Feature Testing
1. **Landing Page**
   - [ ] Redirects to dashboard automatically
   
2. **Dashboard**
   - [ ] Loads without login required
   - [ ] Shows drone imagery section
   - [ ] Statistics displayed (even if zero)
   
3. **Scan Feature**
   - [ ] Can upload tomato leaf image
   - [ ] Prediction returns disease (not "Healthy")
   - [ ] Treatment recommendations shown
   - [ ] Confidence score displayed (65-98%)
   
4. **History**
   - [ ] Shows previous predictions
   - [ ] Can click to view details
   - [ ] Images display correctly
   
5. **Authentication**
   - [ ] Can register new account
   - [ ] Can login with credentials
   - [ ] Can logout
   
6. **Admin Panel** (admin@test.com only)
   - [ ] Can access admin page
   - [ ] Analytics displayed
   - [ ] Farmer cannot access

---

## 📝 URLs to Update

After deployment, update these in your documentation:

- **Frontend URL:** https://_____.vercel.app
- **Backend URL:** https://_____.onrender.com
- **API Base URL:** https://_____.onrender.com/api/v1

---

## 🎉 Deployment Complete!

If all checks pass:
- ✅ Backend running on Render
- ✅ Frontend deployed on Vercel
- ✅ CORS configured correctly
- ✅ All features working
- ✅ Test users can login

**Your AgriVision AI platform is now live!** 🚀
