const CACHE = "neurolab-shell-v46";
const ASSETS = ["./", "./index.html", "./manifest.json", "./icon.svg", "./astronomy.browser.min.js"];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);

  // Leave third-party APIs and imagery to their own fetch handlers. Returning
  // index.html for a failed NASA/NOAA request makes the response type invalid
  // and can hide the real offline condition from the app.
  if (url.origin !== self.location.origin) return;

  const isAppShell =
    event.request.mode === "navigate" ||
    url.pathname.endsWith("/index.html") ||
    url.pathname.endsWith("/Neuro-Lab/") ||
    url.pathname.endsWith("/Neuro-Lab");

  if (isAppShell) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.ok) {
            caches.open(CACHE).then(cache => cache.put("./index.html", response.clone()));
          }
          return response;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  // Cache local assets when available. If an uncached asset cannot be fetched,
  // let the request fail normally instead of substituting HTML for that asset.
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        if (response && response.ok) {
          caches.open(CACHE).then(cache => cache.put(event.request, response.clone()));
        }
        return response;
      });
    })
  );
});
