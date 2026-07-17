# Production Deployment Steps - FIX LOGIN

## 🚨 Current Issue

Login fails on production because:
1. ✅ Local test users created
2. ❌ Render backend needs latest code
3. ❌ Render database needs test users

## 🔄 Step-by-Step Fix

### Step 1: Wait for Render Auto-Deploy (2-3 minutes)

Render should auto-deploy since you pushed to GitHub:

1. Go to https://dashboard.render.com
2. Click your "agrivision" service
3. Check "Events" or "Logs" tab
4. Wait for "Deploy succeeded" message

**Latest commits pushed:**
- Fix: CORS and API routing for Vercel deployment
- Fix: Add test user creation scripts

### Step 2: Verify Backend is Running

Test the backend health check:

```bash
curl https://agrivision2.onrender.com/
curl https://agrivision2.onrender.com/health
```

Should return JSON, not errors.

### Step 3: Create Test Users on Render

**Option A - Using Render Shell (Recommended):**

1. Open Render Dashboard → Your Service → Shell tab
2. Run:
```bash
python create_test_accounts.py
```

**Option B - Using API (If Shell doesn't work):**

Run this PowerShell command:

```powershell
$users = @(
    @{email="farmer@test.com";password="password123";full_name="Test Farmer";role="farmer"},
    @{email="admin@test.com";password="password123";full_name="Test Admin";role="admin"},
    @{email="expert@test.com";password="password123";full_name="Test Expert";role="expert"}
)

foreach ($user in $users) {
    $body = $user | ConvertTo-Json
    try {
        Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/register" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body
        Write-Host "✓ Created: $($user.email)" -ForegroundColor Green
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Yellow
    }
}
```

### Step 4: Test Login

1. Visit https://agri-vision1.vercel.app/auth/login
2. Email: `farmer@test.com`
3. Password: `password123`
4. Click "Sign In"
5. Should redirect to dashboard

### Step 5: Verify Everything Works

- ✅ Login successful
- ✅ Dashboard loads
- ✅ Can upload images
- ✅ Predictions work
- ✅ History shows data
- ✅ Admin panel works (for admin@test.com)

---

## 🐛 If Render Deploy Fails

### Check Render Logs

1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Look for error messages

### Common Issues

**Issue: Database migrations failed**
```bash
# In Render Shell
alembic upgrade head
```

**Issue: Dependencies not installed**
```bash
# In Render Shell
pip install -r requirements.txt
```

**Issue: Service won't start**
- Check if `runtime.txt` has correct Python version
- Check if `requirements.txt` has all dependencies
- Check environment variables are set

---

## 📋 Render Configuration Checklist

Verify these settings in Render:

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables
```
SUPABASE_JWT_SECRET=your-secret-key
DATABASE_URL=sqlite+aiosqlite:///./agrivision.db
```

### Runtime
- **Python Version:** 3.11 or 3.12 (from runtime.txt)

---

## 🔍 Debug Commands

### Test Backend Endpoints

```bash
# Health check
curl https://agrivision2.onrender.com/health

# API docs
curl https://agrivision2.onrender.com/api/v1/docs

# Try login (should return 422 without data - that's expected)
curl -X POST https://agrivision2.onrender.com/api/v1/auth/login
```

### Test Registration

```bash
curl -X POST https://agrivision2.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User","role":"farmer"}'
```

If this returns 500 error, check Render logs for the actual error message.

---

## ⚠️ Important: Render Free Tier Limitations

### Ephemeral Storage
- Database file is **not persistent**
- Resets on every deploy
- Resets on service restart

### Solutions

**Option 1: Use Render PostgreSQL (Recommended)**
- Create PostgreSQL database on Render (free tier available)
- Update `DATABASE_URL` environment variable
- Update `requirements.txt` to use `psycopg2-binary`
- Update database URL format

**Option 2: Keep SQLite + Recreate Users**
- Accept that users reset
- Run `create_test_accounts.py` after each restart
- Document this in your deployment notes

**Option 3: Upgrade to Paid Plan**
- Get persistent disk storage
- Database persists across restarts

---

## 🎯 Quick Summary

1. ⏳ **Wait** for Render to auto-deploy (2-3 min)
2. ✅ **Verify** backend is running (curl health check)
3. 🔧 **Create** test users (Render Shell or API)
4. 🧪 **Test** login on production
5. 🎉 **Done!**

---

## 📞 If Still Having Issues

1. **Check Render Logs** - Look for Python errors
2. **Verify CORS** - Should allow agri-vision1.vercel.app
3. **Test API directly** - Use curl to isolate issue
4. **Check database** - Run check_users_simple.py in Render Shell

**Most likely issue:** Render hasn't deployed latest code yet. Just wait a few minutes!
