const CACHE_NAME = "accord-cache-v1";
const ASSETS = [
  "/",
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/js/serviceworker.js",
  "/static/icons/icon-128x128.png",
  "/static/icons/icon-192x192.png",
  "/static/icons/icon-384x384.png",
  "/static/icons/icon-512x512.png"
];

// Install event: cache all assets
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate event: clean old caches
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch event: use cache first, fall back to network
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => 
      response || fetch(event.request)
    )
  );
});