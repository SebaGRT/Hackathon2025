# PWA Setup Documentation for SafeSite

## Overview

SafeSite has been configured as a Progressive Web App (PWA), allowing users to install it on their mobile devices and use it like a native app.

## Features Implemented

### 1. Web App Manifest
- **Location**: `seguridad/static/pwa/manifest.json`
- **Purpose**: Defines app metadata, icons, and behavior
- **Key Features**:
  - App name: "SafeSite - Sistema de Seguridad"
  - Standalone display mode (full-screen app experience)
  - Portrait orientation for mobile
  - Theme color: #3b82f6 (blue)
  - Background color: #0a0a0a (dark)
  - App shortcuts for quick access to:
    - Nuevo Reporte
    - Dashboard
    - Bitácora

### 2. Service Worker
- **Location**: `seguridad/static/pwa/sw.js`
- **Purpose**: Enables offline functionality and caching
- **Features**:
  - Network-first caching strategy
  - Offline fallback support
  - Automatic cache updates
  - Background sync capability (for offline form submissions)
  - Push notification support (ready for implementation)
  - Runtime caching of visited pages

### 3. App Icons
- **Location**: `seguridad/static/pwa/`
- **Formats**: SVG (scalable, smaller file size)
- **Sizes**: 72x72, 96x96, 128x128, 144x144, 152x152, 192x192, 384x384, 512x512
- **Special Icons**:
  - `apple-touch-icon.svg`: iOS home screen icon
  - `favicon.svg`: Browser tab icon

### 4. PWA Meta Tags
Added to `base.html`:
- `theme-color`: Defines browser UI color
- `apple-mobile-web-app-capable`: Enables standalone mode on iOS
- `apple-mobile-web-app-status-bar-style`: iOS status bar styling
- Manifest link
- Icon links for various platforms

### 5. Install Prompt
- **Automatic Detection**: Shows when user visits on mobile
- **Custom Banner**: Attractive install prompt with:
  - App icon
  - "Install SafeSite" message
  - Install and dismiss buttons
  - Auto-dismiss after 30 seconds
- **Session Management**: Respects user's "not now" choice

## How It Works

### For Users

#### Mobile Installation (Android)
1. Visit SafeSite from Chrome/Edge on Android
2. A banner appears at the bottom: "Instala SafeSite en tu dispositivo"
3. Tap "Instalar" button
4. Confirm installation
5. SafeSite icon appears on home screen
6. Tap icon to open app in standalone mode

#### Mobile Installation (iOS)
1. Visit SafeSite from Safari on iOS
2. Tap the "Share" button (square with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Customize name if desired
5. Tap "Add"
6. SafeSite icon appears on home screen

#### Desktop Installation (Chrome/Edge)
1. Visit SafeSite
2. Look for install icon in address bar
3. Click to install
4. App opens in standalone window

### For Developers

#### Service Worker Registration
The service worker is automatically registered on page load:

```javascript
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/pwa/sw.js')
        .then(registration => {
            console.log('ServiceWorker registered:', registration.scope);
        });
}
```

#### Cache Strategy
- **Network First**: Always tries to fetch from network
- **Cache Fallback**: Uses cached version if offline
- **Runtime Caching**: Caches responses for faster subsequent loads

#### Offline Support
- Cached pages work offline
- Forms can queue for background sync
- Graceful degradation when network unavailable

## Files Added/Modified

### New Files
```
seguridad/static/pwa/
├── manifest.json          # PWA manifest
├── sw.js                  # Service worker
├── icon-72x72.svg        # Icons (various sizes)
├── icon-96x96.svg
├── icon-128x128.svg
├── icon-144x144.svg
├── icon-152x152.svg
├── icon-192x192.svg
├── icon-384x384.svg
├── icon-512x512.svg
├── apple-touch-icon.svg  # iOS icon
└── favicon.svg           # Browser favicon

generate_pwa_icons.py      # Icon generation script
PWA_SETUP.md              # This documentation
```

### Modified Files
```
seguridad/templates/seguridad/base.html
├── Added PWA meta tags (lines 8-48)
├── Added manifest link
├── Added icon links
└── Added service worker registration (lines 594-723)

core/settings.py
└── Added STATICFILES_DIRS configuration

core/urls.py
└── Added static files serving for development
```

## Testing

### Local Testing

1. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

2. **Test on mobile device**:
   - Connect phone to same network as development machine
   - Visit `http://[YOUR_IP]:8000`
   - Look for install prompt

3. **Test in Chrome DevTools**:
   - Open DevTools (F12)
   - Go to "Application" tab
   - Check "Manifest" section
   - Check "Service Workers" section
   - Use "Lighthouse" to audit PWA compliance

### Production Testing (Vercel)

1. **Deploy to Vercel**:
   ```bash
   git add .
   git commit -m "Add PWA support"
   git push
   ```

2. **Verify PWA on mobile**:
   - Visit production URL on mobile
   - Install prompt should appear
   - Install and test offline functionality

## PWA Audit Checklist

Run Lighthouse audit to verify:
- ✅ Web app manifest exists
- ✅ Service worker registered
- ✅ Icons provided (192x192 and 512x512 minimum)
- ✅ Theme color set
- ✅ Viewport configured
- ✅ HTTPS enabled (required in production)
- ✅ Page loads fast
- ✅ Works offline

## Troubleshooting

### Install Prompt Not Showing

**Possible causes**:
1. Already installed
2. Prompt dismissed recently (has cooldown period)
3. Not using HTTPS (required in production)
4. Browser doesn't support PWA
5. Manifest or service worker errors

**Solutions**:
- Check DevTools Console for errors
- Check Application > Manifest in DevTools
- Verify service worker is registered
- Clear site data and reload

### Service Worker Not Updating

**Solution**:
1. Open DevTools > Application > Service Workers
2. Check "Update on reload"
3. Click "Unregister" and refresh page
4. Or increment version in `sw.js` (CACHE_NAME)

### Icons Not Loading

**Solution**:
1. Run `python manage.py collectstatic`
2. Verify files in `staticfiles/pwa/`
3. Check browser console for 404 errors
4. Verify STATIC_URL and STATICFILES_DIRS in settings.py

### Offline Mode Not Working

**Solution**:
1. Check service worker is active
2. Visit pages while online first (to cache them)
3. Check Network tab > Offline mode in DevTools
4. Verify service worker fetch handler

## Advanced Features (Future Enhancements)

### 1. Background Sync
Implement offline form submission queuing:
```javascript
// In sw.js - already has placeholder
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-reports') {
    event.waitUntil(syncPendingReports());
  }
});
```

### 2. Push Notifications
Enable real-time alerts for emergencies:
- Request notification permission
- Subscribe to push service
- Handle push events in service worker
- Display notifications with actions

### 3. Periodic Background Sync
Check for updates while app is closed:
- Sync data periodically
- Update cached content
- Notify users of important changes

### 4. Share Target API
Allow sharing to SafeSite from other apps:
- Add to manifest.json
- Handle shared content
- Process shared images/files

## Security Considerations

1. **HTTPS Required**: PWAs require HTTPS in production (Vercel provides this)
2. **Service Worker Scope**: Limited to `/` origin
3. **Cache Security**: Sensitive data should not be cached
4. **Content Security Policy**: Review and update as needed

## Performance Tips

1. **Cache Strategy**: Network-first ensures fresh data
2. **Precaching**: Only essential assets precached
3. **Runtime Caching**: Visited pages cached automatically
4. **Cache Expiration**: Old caches cleaned on activation
5. **Icon Optimization**: SVG format keeps file sizes small

## Browser Support

### Full Support
- Chrome 40+ (Android)
- Edge 79+
- Chrome 72+ (Desktop)
- Samsung Internet 4+

### Partial Support
- Safari 11.3+ (iOS) - Add to Home Screen only
- Firefox 44+ - Limited PWA features

### Not Supported
- Internet Explorer
- Opera Mini

## Resources

- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)

## Maintenance

### Regular Tasks
1. **Update icons** if branding changes
2. **Update manifest** when adding new features/shortcuts
3. **Monitor service worker** for errors in production
4. **Update cache version** when deploying major changes
5. **Test PWA audit** regularly with Lighthouse

### Version Management
When updating the PWA:
1. Update `CACHE_NAME` in `sw.js`
2. Update `version` in manifest (if added)
3. Test install/update flow
4. Monitor for issues post-deployment

## Support

For issues or questions about the PWA implementation:
1. Check browser DevTools Console and Application tabs
2. Review this documentation
3. Test with Lighthouse PWA audit
4. Check service worker status in DevTools

---

**Last Updated**: December 20, 2024
**Version**: 1.0
**Status**: ✅ Production Ready