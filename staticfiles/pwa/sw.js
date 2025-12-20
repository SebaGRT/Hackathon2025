// Service Worker for SafeSite PWA
const CACHE_NAME = "safesite-v1";
const RUNTIME_CACHE = "safesite-runtime";

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  "/",
  "/static/pwa/manifest.json",
  "/static/pwa/icon-192x192.svg",
  "/static/pwa/icon-512x512.svg",
];

// Install event - precache assets
self.addEventListener("install", (event) => {
  console.log("[ServiceWorker] Install event");
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log("[ServiceWorker] Pre-caching assets");
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting()),
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("[ServiceWorker] Activate event");
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
              console.log("[ServiceWorker] Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }
          }),
        );
      })
      .then(() => self.clients.claim()),
  );
});

// Fetch event - network first, fall back to cache
self.addEventListener("fetch", (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== "GET") {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Try network first
      return fetch(event.request)
        .then((networkResponse) => {
          // Cache successful responses
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(RUNTIME_CACHE).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // Network failed, return cached version if available
          if (cachedResponse) {
            return cachedResponse;
          }

          // Return offline page for navigation requests
          if (event.request.mode === "navigate") {
            return caches.match("/");
          }

          // For other requests, return a basic response
          return new Response("Offline - content not available", {
            status: 503,
            statusText: "Service Unavailable",
            headers: new Headers({
              "Content-Type": "text/plain",
            }),
          });
        });
    }),
  );
});

// Handle messages from the client
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }

  if (event.data && event.data.type === "CLEAR_CACHE") {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName)),
        );
      }),
    );
  }
});

// Background sync for offline form submissions
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-reports") {
    event.waitUntil(syncReports());
  }
});

async function syncReports() {
  // This would sync any pending reports that were created while offline
  console.log("[ServiceWorker] Syncing reports...");
  // Implementation would depend on your specific requirements
}

// Push notification support
self.addEventListener("push", (event) => {
  const options = {
    body: event.data ? event.data.text() : "Nueva notificación de SafeSite",
    icon: "/static/pwa/icon-192x192.svg",
    badge: "/static/pwa/icon-72x72.svg",
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1,
    },
    actions: [
      {
        action: "explore",
        title: "Ver más",
        icon: "/static/pwa/icon-96x96.svg",
      },
      {
        action: "close",
        title: "Cerrar",
        icon: "/static/pwa/icon-96x96.svg",
      },
    ],
  };

  event.waitUntil(self.registration.showNotification("SafeSite", options));
});

// Handle notification clicks
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  if (event.action === "explore") {
    event.waitUntil(clients.openWindow("/"));
  }
});
