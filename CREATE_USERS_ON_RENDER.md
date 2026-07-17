# Create Test Users on Render - QUICK GUIDE

## 🎯 Problem

Your **local database** has the test users, but **Render has a separate database** without them. That's why login fails on production!

## ✅ Solution - 3 Options (Choose One)

---

### Option 1: Use Render Shell (EASIEST) ⭐

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click on your "agrivision" service

2. **Open Shell**
   - Click the "Shell" tab
   - Wait for shell to connect

3. **Run Command**
   ```bash
   python create_test_accounts.py
   ```

4. **Verify**
   ```bash
   python check_users_simple.py
   ```

**Done!** Test users are now in production database.

---

### Option 2: Use Registration API (FASTEST) ⚡

Run these commands from your local terminal:

```bash
# Create Farmer Account
curl -X POST https://agrivision2.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"farmer@test.com\",\"password\":\"password123\",\"full_name\":\"Test Farmer\",\"role\":\"farmer\"}"

# Create Admin Account
curl -X POST https://agrivision2.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@test.com\",\"password\":\"password123\",\"full_name\":\"Test Admin\",\"role\":\"admin\"}"

# Create Expert Account
curl -X POST https://agrivision2.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"expert@test.com\",\"password\":\"password123\",\"full_name\":\"Test Expert\",\"role\":\"expert\"}"
```

**For Windows PowerShell**, use:
```powershell
# Farmer
Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"email":"farmer@test.com","password":"password123","full_name":"Test Farmer","role":"farmer"}'

# Admin
Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"email":"admin@test.com","password":"password123","full_name":"Test Admin","role":"admin"}'

# Expert
Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"email":"expert@test.com","password":"password123","full_name":"Test Expert","role":"expert"}'
```

---

### Option 3: Use Frontend Registration (MANUAL) 📝

1. **Visit Registration Page**
   - Go to https://agri-vision1.vercel.app/auth/register

2. **Create Farmer Account**
   - Email: `farmer@test.com`
   - Password: `password123`
   - Full Name: `Test Farmer`
   - Role: `Farmer`
   - Click "Sign Up"

3. **Logout** (if auto-logged in)

4. **Create Admin Account**
   - Email: `admin@test.com`
   - Password: `password123`
   - Full Name: `Test Admin`
   - Role: `Admin`
   - Click "Sign Up"

5. **Logout**

6. **Create Expert Account**
   - Email: `expert@test.com`
   - Password: `password123`
   - Full Name: `Test Expert`
   - Role: `Expert`
   - Click "Sign Up"

---

## 🧪 Test Login After Creating Users

1. Visit https://agri-vision1.vercel.app/auth/login
2. Enter:
   - Email: `farmer@test.com`
   - Password: `password123`
3. Click "Sign In"
4. Should redirect to dashboard ✅

---

## 🔍 Verify Users Created

### Using Render Shell
```bash
python check_users_simple.py
```

Should show farmer@test.com, admin@test.com, expert@test.com

### Using API
```bash
# This will fail with 401 (expected - need token), but confirms endpoint exists
curl https://agrivision2.onrender.com/api/v1/auth/me
```

---

## ⚠️ Important Notes

### Render Free Tier
- Uses **ephemeral storage**
- Database resets on service restart
- Users will be **lost** when service restarts
- **Solutions:**
  1. Upgrade to Render paid plan with persistent disk
  2. Use Render PostgreSQL (free tier available)
  3. Recreate users after each restart

### Database Differences
- **Local:** `backend/agrivision.db` (SQLite file)
- **Render:** Separate SQLite file on Render's server
- They are **completely independent**

---

## 🎯 Recommended Workflow

**Best approach:**

1. **Use Option 2 (API)** - Run the PowerShell commands now
2. **Test login** immediately on production site
3. **If it works** - You're done! 🎉
4. **If Render service restarts** - Just re-run the commands

---

## 📝 Quick Commands (Copy-Paste)

For Windows PowerShell - Run all three at once:

```powershell
$headers = @{"Content-Type"="application/json"}
$base = "https://agrivision2.onrender.com/api/v1/auth/register"

# Create all three users
@(
    @{email="farmer@test.com";password="password123";full_name="Test Farmer";role="farmer"},
    @{email="admin@test.com";password="password123";full_name="Test Admin";role="admin"},
    @{email="expert@test.com";password="password123";full_name="Test Expert";role="expert"}
) | ForEach-Object {
    $body = $_ | ConvertTo-Json
    try {
        $result = Invoke-RestMethod -Uri $base -Method POST -Headers $headers -Body $body
        Write-Host "✓ Created: $($_.email)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed: $($_.email) - $($_.Exception.Message)" -ForegroundColor Red
    }
}
```

---

## 🎉 After Creating Users

Test accounts available:
- **Farmer:** farmer@test.com / password123
- **Admin:** admin@test.com / password123  
- **Expert:** expert@test.com / password123

**Login should now work on production!** 🚀
