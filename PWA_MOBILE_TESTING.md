# PWA Mobile Testing Quick Reference

## Quick Test Checklist for SafeSite PWA

### ✅ Pre-Deployment Checklist

Before testing on mobile:

1. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Commit and Push to Vercel**
   ```bash
   git add .
   git commit -m "Add PWA support"
   git push origin main
   ```

3. **Wait for Vercel Deployment**
   - Check Vercel dashboard for deployment status
   - Verify deployment is successful (green checkmark)
   - Note the production URL

---

## 📱 Testing on Android

### Chrome/Edge on Android (Full PWA Support)

1. **Open the app**
   - Visit your Vercel URL: `https://your-app.vercel.app`
   - Navigate through a few pages (to cache content)

2. **Look for the install banner**
   - Should appear at bottom of screen
   - Shows: "Instala SafeSite en tu dispositivo"
   - With "Instalar" and "Ahora no" buttons

3. **Install the app**
   - Tap "Instalar" button
   - Confirm installation in browser prompt
   - App icon appears on home screen

4. **Test the installed app**
   - Tap the SafeSite icon on home screen
   - Should open in standalone mode (no browser UI)
   - Test navigation between pages
   - Check that theme toggle works
   - Verify icons display correctly

5. **Test offline functionality**
   - While app is open, enable Airplane mode
   - Navigate to pages you've previously visited
   - Should load from cache
   - Try to create a report (should show offline message)
   - Disable Airplane mode
   - Verify app reconnects

### Alternative Install Method (Chrome)

If banner doesn't appear:
1. Open Chrome menu (⋮)
2. Look for "Install app" or "Add to Home screen"
3. Tap to install
4. Confirm installation

---

## 🍎 Testing on iOS

### Safari on iOS (Limited PWA Support)

**Note**: iOS doesn't show automatic install prompts. Users must manually add to home screen.

1. **Open the app**
   - Visit your Vercel URL in Safari
   - Navigate through pages

2. **Add to Home Screen**
   - Tap the Share button (□ with arrow)
   - Scroll down and tap "Add to Home Screen"
   - Edit name if desired (default: SafeSite)
   - Tap "Add" in top right

3. **Test the installed app**
   - Tap SafeSite icon on home screen
   - Opens in standalone mode
   - Test navigation
   - Verify icons and theme

4. **Limitations on iOS**
   - No automatic install prompt
   - No push notifications (yet)
   - Service worker has limited capabilities
   - Must use Safari (not Chrome iOS)

---

## 💻 Testing on Desktop

### Chrome/Edge on Desktop

1. **Open DevTools**
   - Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)

2. **Check Application Tab**
   - Click "Application" tab
   - Verify items in left sidebar:

   **Manifest**:
   - Should show "SafeSite - Sistema de Seguridad"
   - Icons: 8 icons listed
   - Check for errors (red text)

   **Service Workers**:
   - Status should be "activated and is running"
   - Source: `/static/pwa/sw.js`
   - Can click "Update" to refresh
   - Can click "Unregister" to remove

   **Storage > Cache Storage**:
   - Should see "safesite-v1" cache
   - Click to view cached resources

3. **Run Lighthouse Audit**
   - Click "Lighthouse" tab in DevTools
   - Select "Progressive Web App" category
   - Click "Analyze page load"
   - Review PWA score and recommendations

4. **Install on Desktop**
   - Look for install icon in address bar (⊕ or computer icon)
   - Click to install
   - App opens in standalone window
   - Can pin to taskbar/dock

---

## 🔍 Common Testing Scenarios

### Scenario 1: First-Time User
1. Visit site on mobile
2. Wait for install banner (may take a few seconds)
3. Dismiss banner ("Ahora no")
4. Continue using site
5. Banner should not appear again this session

### Scenario 2: Returning User
1. Visit site that was previously dismissed
2. Use site for a while
3. Banner may appear again after cooldown period
4. Install when ready

### Scenario 3: Offline Usage
1. Install app
2. Browse several pages while online
3. Enable Airplane mode
4. Open installed app
5. Navigate to previously visited pages
6. Should load from cache
7. Try to access new page → offline message
8. Disable Airplane mode
9. App should reconnect automatically

### Scenario 4: App Updates
1. Developer pushes update with new CACHE_NAME
2. User opens installed app
3. Service worker detects update
4. New version downloads in background
5. On next app restart, new version active

---

## 🐛 Troubleshooting Guide

### Install Banner Not Appearing

**Check**:
- [ ] Using HTTPS (required in production)
- [ ] Valid manifest.json (check DevTools)
- [ ] Service worker registered (check DevTools)
- [ ] Not already installed
- [ ] Not recently dismissed (has cooldown)
- [ ] Using supported browser (Chrome/Edge on Android)

**Fix**:
```javascript
// In DevTools Console, manually trigger (for testing):
// Note: Only works if deferredPrompt is available
```

### Service Worker Not Working

**Check**:
- [ ] `/static/pwa/sw.js` accessible
- [ ] No JavaScript errors in Console
- [ ] Service worker registered in Application tab

**Fix**:
1. Open DevTools > Application > Service Workers
2. Check "Update on reload"
3. Click "Unregister"
4. Refresh page
5. Service worker re-registers

### Icons Not Loading

**Check**:
- [ ] Icons exist in `/staticfiles/pwa/`
- [ ] manifest.json paths correct
- [ ] No 404 errors in Network tab

**Fix**:
```bash
python manage.py collectstatic --noinput
git add staticfiles/
git commit -m "Update static files"
git push
```

### Offline Not Working

**Check**:
- [ ] Service worker active
- [ ] Pages visited while online (to cache)
- [ ] Cache storage not cleared

**Test**:
1. Open DevTools > Application > Cache Storage
2. Should see "safesite-v1" and "safesite-runtime"
3. Click to verify files cached
4. Use DevTools > Network > Offline to simulate

---

## 📊 Success Metrics

### Installation Success
- ✅ Install prompt appears on mobile
- ✅ App installs to home screen
- ✅ Icon displays correctly
- ✅ App name shows as "SafeSite"
- ✅ Opens in standalone mode

### Offline Functionality
- ✅ Previously visited pages load offline
- ✅ Graceful error for unavailable content
- ✅ Reconnects when online

### Performance
- ✅ Lighthouse PWA score > 90
- ✅ Fast load times
- ✅ Smooth navigation
- ✅ No console errors

### User Experience
- ✅ Install banner is clear and attractive
- ✅ Easy to install
- ✅ Feels like native app
- ✅ Theme matches website
- ✅ Icons look professional

---

## 📝 Test Report Template

Copy and fill this out after testing:

```
PWA Test Report - SafeSite
Date: ___________
Tested By: ___________
URL: ___________

DEVICE TESTING
--------------
Android Device: ___________
OS Version: ___________
Browser: Chrome/Edge ___________

[ ] Install prompt appeared
[ ] Successfully installed
[ ] Icon displays correctly
[ ] Opens in standalone mode
[ ] Offline mode works
[ ] Theme toggle works
[ ] Navigation smooth

iOS Device: ___________
OS Version: ___________

[ ] Added to home screen
[ ] Icon displays correctly
[ ] Opens in standalone mode
[ ] Basic offline works

DESKTOP TESTING
---------------
Browser: ___________

[ ] Manifest valid (DevTools)
[ ] Service worker active
[ ] Lighthouse PWA score: ___/100
[ ] Can install on desktop
[ ] Cache working

ISSUES FOUND
------------
1. 
2. 
3. 

OVERALL STATUS
--------------
[ ] PASS - Ready for users
[ ] NEEDS WORK - Issues to fix
[ ] FAIL - Major problems

Notes:
___________________________________________
___________________________________________
___________________________________________
```

---

## 🚀 Quick Commands Reference

```bash
# Generate icons (if needed)
python generate_pwa_icons.py

# Collect static files
python manage.py collectstatic --noinput

# Run PWA verification tests
python test_pwa.py

# Check Django configuration
python manage.py check

# Deploy to Vercel
git add .
git commit -m "PWA updates"
git push origin main

# View Vercel logs
vercel logs
```

---

## 📞 Support Resources

- **PWA Documentation**: See `PWA_SETUP.md`
- **Chrome DevTools**: F12 > Application tab
- **Lighthouse**: DevTools > Lighthouse tab
- **Can I Use PWA**: https://caniuse.com/web-app-manifest

---

**Last Updated**: December 20, 2024
**Version**: 1.0