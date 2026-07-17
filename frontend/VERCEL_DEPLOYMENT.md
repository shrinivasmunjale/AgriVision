# Vercel Deployment Guide for AgriVision AI Frontend

## Prerequisites
- Backend deployed on Render (or another platform)
- Vercel account created
- GitHub repository connected to Vercel

## Step 1: Environment Variables

In your Vercel project dashboard, add these environment variables:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com/api/v1
```

**Important:** Replace `your-backend-url.onrender.com` with your actual Render backend URL.

## Step 2: Deploy Settings

### Framework Preset
- **Framework Preset:** Next.js

### Build & Development Settings
- **Build Command:** `npm run build`
- **Output Directory:** `.next` (default)
- **Install Command:** `npm install`
- **Development Command:** `npm run dev`

### Root Directory
- If deploying from monorepo: Set root directory to `frontend`
- If deploying frontend only: Leave as default (root)

## Step 3: Deploy

1. **Connect Repository**
   - Go to Vercel dashboard
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**
   - Set root directory (if needed): `frontend`
   - Add environment variable: `NEXT_PUBLIC_API_URL`
   - Keep all other settings as default

3. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Visit your deployment URL

## Step 4: Verify Deployment

After deployment, check:
1. ✅ Landing page redirects to dashboard
2. ✅ Dashboard loads without errors
3. ✅ Can access scan page
4. ✅ Images from backend load correctly
5. ✅ API calls work (check Network tab)

## Troubleshooting

### Issue: "Module not found: Can't resolve '@/lib/api'"

**Solution:** This should be fixed with the new configuration files:
- `vercel.json` - Specifies build settings
- `next.config.js` - Enhanced webpack aliases
- `jsconfig.json` - Explicit path mappings
- `.vercelignore` - Ensures src files aren't excluded

### Issue: 404 on all routes

**Cause:** Vercel can't find pages

**Solution:**
1. Ensure root directory is set to `frontend` (if deploying from monorepo)
2. Verify `src/app` directory structure is correct
3. Check build logs for compilation errors

### Issue: API calls failing (CORS errors)

**Cause:** Backend not configured for frontend domain

**Solution:** Update backend CORS settings to allow your Vercel domain:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Environment variables not working

**Solution:**
1. Go to Vercel project → Settings → Environment Variables
2. Add `NEXT_PUBLIC_API_URL` with your backend URL
3. Redeploy the project (Deployments → Three dots → Redeploy)

## Build Verification (Local)

Before deploying to Vercel, always test locally:

```bash
cd frontend
npm run build
npm run start
```

Visit `http://localhost:3000` and verify everything works.

## Post-Deployment

1. **Update Backend CORS:** Add your Vercel URL to backend's allowed origins
2. **Test All Features:**
   - Landing page redirect
   - Dashboard access
   - Image upload
   - Prediction history
   - PDF report download
3. **Monitor Build Logs:** Check Vercel dashboard for any warnings

## Support

If deployment issues persist:
1. Check Vercel build logs for specific errors
2. Verify all configuration files are committed to git
3. Ensure `src/lib/api.js` exists in repository
4. Test build locally first

## Files Modified for Vercel Compatibility

- ✅ `vercel.json` - Build configuration
- ✅ `next.config.js` - Enhanced webpack aliases
- ✅ `jsconfig.json` - Explicit path mappings
- ✅ `.vercelignore` - Build exclusions
- ✅ `src/app/page.js` - Landing page redirects to dashboard
- ✅ `src/app/dashboard/page.js` - Public access (no auth required)
