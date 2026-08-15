# 🔧 Render Deployment Troubleshooting

## 🚨 Current Issue: Login Failing on Production

**Error Messages:**
```
POST https://agrivision2.onrender.com/api/v1/auth/login 401 (Unauthorized)
Login error: {detail: 'Incorrect email or password'}
POST https://agrivision2.onrender.com/api/v1/auth/login net::ERR_CONNECTION_CLOSED
```

**What this means:**
- Render backend is either not running or crashed during deployment
- Most likely: PyTorch installation failed or timed out
- Database may not have been seeded

---

## ✅ What I Just Fixed

1. **Changed Python version:** `3.11.11` → `3.11.0` (Render compatibility)
2. **Updated PyTorch:** Used version ranges for flexibility
3. **Pushed to GitHub:** Render will auto-redeploy

---

## 📋 Steps to Fix Now

### **Step 1: Check Render Deployment Status**

1. Go to: https://dashboard.render.com/
2. Click on: `agrivision2` service
3. Check the status:
   - 🟢 **"Live"** = Good! Continue to Step 2
   - 🟡 **"Deploying"** = Wait (10-15 min for PyTorch)
   - 🔴 **"Build failed"** or **"Deploy failed"** = See Step 3

### **Step 2: Check Render Logs** 📊

Click "Logs" tab and look for:

#### ✅ **Success Messages (what you want to see):**
```
==> Installing dependencies from Pipfile.lock
==> Installing torch...
==> Installing torchvision...
[LABELS] Loaded 10 classes from class_names.json
[MODEL] Found deployed model at: backend/app/ml/best_efficientnetb0.pth
[SUCCESS] EfficientNet-B0 model loaded successfully from state dict!
[SUCCESS] Database seeding completed successfully.
Your service is live 🎉
```

#### ❌ **Error Messages (what might be wrong):**

**Error 1: Out of Memory**
```
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
```
**Solution:** PyTorch too large for free tier. See "Option A" below.

**Error 2: Python Version Not Found**
```
Could not find a version that satisfies the requirement python-3.11.11
```
**Solution:** Already fixed! Wait for redeploy.

**Error 3: Build Timeout**
```
Build exceeded maximum time limit
```
**Solution:** PyTorch installation too slow. See "Option B" below.

**Error 4: Model File Not Found**
```
[INFO] No PyTorch model file found in...
```
**Solution:** Model didn't get pushed to GitHub. See "Option C" below.

---

## 🛠️ Solutions

### **Option A: Remove PyTorch (Use Dummy Predictions Temporarily)**

If PyTorch keeps failing to install:

1. Edit `backend/requirements.txt` - **remove these lines:**
   ```
   torch>=2.0.0,<2.2.0
   torchvision>=0.15.0,<0.17.0
   Pillow>=10.0.0,<11.0.0
   ```

2. Commit and push:
   ```bash
   git add backend/requirements.txt
   git commit -m "Temporarily remove PyTorch for deployment"
   git push origin main
   ```

3. Wait for Render to redeploy (2-3 min)
4. System will use dummy predictions but **everything else will work**

**Pros:** Fast deployment, everything works except real predictions  
**Cons:** No real AI predictions (falls back to mock data)

---

### **Option B: Use Render Paid Tier**

Free tier limitations:
- 512 MB RAM (PyTorch needs ~800MB)
- Slower build machines
- Build timeout issues

**Upgrade to Starter ($7/month):**
- 1 GB RAM
- Faster builds
- PyTorch will install successfully

Go to: Dashboard → Service Settings → Change Instance Type

---

### **Option C: Verify Model File on GitHub**

1. Go to: https://github.com/shrinivasmunjale/AgriVision/tree/main/backend/app/ml
2. Check if these files exist:
   - ✅ `best_efficientnetb0.pth` (~16 MB)
   - ✅ `class_names.json`
   - ✅ `model_loader.py`

**If files are missing:**
```bash
cd d:\AgriVision
git add backend/app/ml/best_efficientnetb0.pth
git add backend/app/ml/class_names.json
git commit -m "Add model files"
git push origin main
```

---

### **Option D: Manual Render Deploy**

Force a fresh deploy:

1. Go to Render Dashboard → `agrivision2`
2. Click: **Manual Deploy** → **Deploy latest commit**
3. Watch logs carefully
4. If it fails again, check logs for specific error

---

## 🎯 Quick Test: Is Backend Actually Running?

Open this URL in browser:
```
https://agrivision2.onrender.com/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "project": "AgriVision AI",
  "version": "2.0.0",
  "docs": "/api/v1/docs"
}
```

**If you see this:** Backend is running! Problem is with database/auth  
**If you see error:** Backend is down/crashed

---

## 🔍 Specific Error Debugging

### **Error: "401 Unauthorized" on Login**

**Possible causes:**
1. Database not seeded (no test users)
2. Password hashing mismatch
3. JWT secret not configured

**Test directly:**
```bash
# Try to login with curl
curl -X POST https://agrivision2.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"farmer@test.com","password":"password123"}'
```

**Expected:** JSON with `access_token`  
**If error:** Check Render logs for database seed messages

### **Error: "ERR_CONNECTION_CLOSED"**

**This means:** Backend crashed or out of memory

**Check Render logs for:**
- `Killed` = Out of memory
- `Segmentation fault` = Code crash
- Nothing = Service didn't start

**Solution:** Reduce memory usage (remove PyTorch) or upgrade tier

---

## 📊 Current Deployment Strategy

### **Recommendation: Two-Phase Approach**

**Phase 1: Get Everything Working (No AI)**
1. Remove PyTorch from requirements.txt
2. Deploy successfully
3. Test: Login, Upload, History (uses dummy predictions)
4. Verify: All features work except real AI

**Phase 2: Add AI Model (Upgrade Tier)**
1. Upgrade Render to Starter tier ($7/mo)
2. Add PyTorch back to requirements.txt
3. Redeploy with model
4. Test: Real AI predictions

This ensures you have a **working system** while figuring out the PyTorch deployment.

---

## 🎯 Action Plan (Do This Now)

### **Immediate Actions:**

1. **Check Render Dashboard**
   - Is it deploying? → Wait 10 more minutes
   - Is it failed? → Read the error logs

2. **Test Backend Health**
   - Open: https://agrivision2.onrender.com/
   - Does it respond? → Good!
   - Does it error? → Backend is down

3. **Check GitHub Repo**
   - Verify model file exists
   - Check if latest commit is there

4. **Decision Point:**
   - If PyTorch keeps failing → Use Option A (remove it temporarily)
   - If you need AI now → Use Option B (upgrade tier)
   - If backend won't start → Use Option D (manual deploy)

---

## 💡 Why It Works Locally But Not on Render

| Factor | Local | Render Free Tier |
|--------|-------|------------------|
| RAM | Your PC (probably 8-16GB) | 512 MB |
| Disk Space | Plenty | Limited |
| Build Time | No limit | Timeout after 15 min |
| PyTorch Size | ~700 MB download | Struggles |
| Network Speed | Your internet | Render's network |

**Bottom line:** Render's free tier is great for small apps, but PyTorch is on the edge of what it can handle.

---

## ✅ Success Checklist

Once it's working, you should see:

- [ ] Render shows "Live" status
- [ ] https://agrivision2.onrender.com/ returns JSON
- [ ] Can login at https://agri-vision1.vercel.app/auth/login
- [ ] Can upload images
- [ ] Predictions show (even if dummy data)
- [ ] Images load in history
- [ ] No 401/500 errors in console

---

## 🆘 Still Not Working?

**Share these with me:**
1. Render deployment status (Live/Failed/Deploying?)
2. Last 50 lines of Render logs
3. What happens when you visit https://agrivision2.onrender.com/
4. Which option you want to try (A, B, C, or D)

I'll help debug the specific issue!

---

## 📝 Quick Commands Reference

```bash
# Check what's on GitHub
git log --oneline -5

# Force push if needed
git push origin main --force

# Add all changes
git add .
git commit -m "Fix deployment"
git push origin main

# Check file size
ls -lh backend/app/ml/best_efficientnetb0.pth
```

---

**Remember:** It's normal for the first deployment with PyTorch to take 10-15 minutes. Be patient and watch the logs! 🚀
