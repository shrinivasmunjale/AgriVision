# ✅ CORRECT RENDER SETUP

## 🎯 Your Backend URL

**Backend:** https://agrivision-ay2y.onrender.com
**Frontend:** https://agri-vision1.vercel.app

---

## 🚨 CRITICAL: Set This Environment Variable

Go to Render Dashboard and set this **EXACT** value:

1. **Go to:** https://dashboard.render.com/
2. **Click:** Your service `agrivision-ay2y`
3. **Click:** "Environment" tab
4. **Add Environment Variable:**
   ```
   Key:   BACKEND_URL
   Value: https://agrivision-ay2y.onrender.com
   ```
5. **Click:** "Save Changes"
6. **Wait:** 2-3 minutes for automatic redeploy

---

## 📋 What This Fixes

### **Before Setting BACKEND_URL:**
```javascript
// Image URL in database:
"http://localhost:8000/uploads/abc123.jpg"  ❌

// Frontend tries to load:
http://localhost:8000/uploads/abc123.jpg
// Result: ERR_CONNECTION_REFUSED
```

### **After Setting BACKEND_URL:**
```javascript
// Image URL in database:
"https://agrivision-ay2y.onrender.com/uploads/abc123.jpg"  ✅

// Frontend loads:
https://agrivision-ay2y.onrender.com/uploads/abc123.jpg
// Result: Image displays!
```

---

## 🚀 Push Latest Code

After setting the environment variable, push the latest code:

```bash
cd d:\AgriVision
git add .
git commit -m "Fix: Contact messages, hide admin scan button, optimize images"
git push origin main
```

This will deploy:
- ✅ Contact messages endpoint
- ✅ Hidden scan button for admin
- ✅ All other fixes

---

## 🧪 Testing Steps

### **1. Test Image Loading**
```bash
# Login as farmer
https://agri-vision1.vercel.app/auth/login
Email: farmer@test.com
Password: password123

# Upload NEW image
Go to /scan
Upload tomato leaf image
Wait for analysis
Go to /history
✅ Image should load (not broken icon)
```

### **2. Test Contact Messages**
```bash
# As farmer, submit message
Go to /contact
Fill: Name, Email, Phone, Message
Click Submit

# As admin, view message
Logout
Login: admin@test.com / password123
Go to /admin
Click "Contact Messages" tab
✅ Your message should appear
```

### **3. Test Admin Dashboard**
```bash
# As admin
Go to /dashboard
✅ Should NOT see "Scan Tomato Leaves Now" button

# As farmer
Go to /dashboard
✅ Should see "Scan Tomato Leaves Now" button
```

---

## ⚠️ Important Notes

### **Old Images Won't Fix**
- Old predictions already have `localhost:8000` URLs in database
- Setting `BACKEND_URL` only affects NEW uploads
- Old images will remain broken (test data anyway)

### **Database Resets on Deploy**
- Render free tier = ephemeral storage
- Every deployment resets SQLite database
- Test users auto-recreate
- Predictions/messages lost
- **Solution:** Use PostgreSQL for persistence (optional)

### **Cold Starts**
- Render free tier sleeps after 15min inactivity
- First request takes 30-60 seconds to wake up
- Subsequent requests are fast
- **Solution:** Upgrade to paid tier or accept delay

---

## 📊 Verification Checklist

After setting BACKEND_URL and pushing code:

- [ ] Render shows "Live" status
- [ ] Environment shows: `BACKEND_URL=https://agrivision-ay2y.onrender.com`
- [ ] Upload NEW image as farmer
- [ ] NEW image displays in history (not broken)
- [ ] Submit contact message as farmer
- [ ] Message appears in admin panel
- [ ] Admin dashboard has no scan button
- [ ] Farmer dashboard has scan button

---

## 🔧 If Issues Persist

### **Images Still Broken?**
1. Check environment variable is exactly: `https://agrivision-ay2y.onrender.com` (no trailing slash)
2. Upload a BRAND NEW image (old ones can't be fixed)
3. Check browser console for image URL (should start with https://agrivision-ay2y.onrender.com)

### **Contact Messages Not Showing?**
1. Check Render logs for deployment success
2. Try endpoint directly: `GET /api/v1/admin/contact-messages` with admin token
3. Verify message was submitted (check network tab in DevTools)

### **Admin Still Sees Scan Button?**
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Verify logged in as admin (check profile role)

---

## 💡 Quick Debug Commands

### **Check if backend is up:**
```bash
curl https://agrivision-ay2y.onrender.com/
# Should return: {"status":"healthy","project":"AgriVision AI",...}
```

### **Check image URL:**
```bash
# Open browser DevTools (F12)
# Go to Network tab
# Upload image
# Look for /upload request
# Check response for image_url
# Should start with: https://agrivision-ay2y.onrender.com/uploads/
```

### **Check contact endpoint:**
```bash
# As admin, open browser console
# Run:
fetch('https://agrivision-ay2y.onrender.com/api/v1/admin/contact-messages', {
  headers: {
    'Authorization': 'Bearer YOUR_ADMIN_TOKEN_HERE'
  }
})
.then(r => r.json())
.then(console.log)
```

---

## ✅ Final Action Items

1. **Set BACKEND_URL on Render** ⏳ (Do this first!)
   ```
   Key:   BACKEND_URL
   Value: https://agrivision-ay2y.onrender.com
   ```

2. **Push code to GitHub** ⏳
   ```bash
   git add .
   git commit -m "Fix: Contact messages, admin UI, images"
   git push origin main
   ```

3. **Wait for deploy** ⏳ (2-3 minutes)

4. **Test everything** ⏳ (Use checklist above)

---

**Your correct backend URL is:** `https://agrivision-ay2y.onrender.com`

**Set it now in Render dashboard!** 🚀
