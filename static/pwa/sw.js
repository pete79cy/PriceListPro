/* static/pwa/sw.js */
const CACHE_VERSION = "v10";
const STATIC_CACHE = `static-${CACHE_VERSION}`;
const RUNTIME_CACHE = `runtime-${CACHE_VERSION}`;

const PRECACHE_URLS = [
  "/offline",
  "/static/pwa/manifest.webmanifest",
  "/static/pwa/icons/icon-192.png",
  "/static/pwa/icons/icon-512.png"
];

const NO_CACHE_PATHS = [
  "/login",
  "/logout",
  "/admin",
  "/api",
  "/customers",
  "/products",
  "/suppliers",
  "/quotation",
  "/orders",
  "/invoices",
  "/upload",
  "/create",
  "/edit",
  "/company-settings",
  "/viber",
  "/pending",
  "/addenda"
];

function shouldCacheHTML(pathname) {
  return !NO_CACHE_PATHS.some(p => pathname.startsWith(p));
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      if (self.registration.navigationPreload) {
        await self.registration.navigationPreload.enable();
      }
      
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => ![STATIC_CACHE, RUNTIME_CACHE].includes(k))
          .map((k) => caches.delete(k))
      );
      
      const runtimeCache = await caches.open(RUNTIME_CACHE);
      const cachedRequests = await runtimeCache.keys();
      await Promise.all(
        cachedRequests
          .filter((req) => {
            const url = new URL(req.url);
            return !shouldCacheHTML(url.pathname);
          })
          .map((req) => runtimeCache.delete(req))
      );
    })()
  );
  self.clients.claim();
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

function isStaticAsset(url) {
  return (
    url.pathname.startsWith("/static/") ||
    url.pathname.endsWith(".css") ||
    url.pathname.endsWith(".js") ||
    url.pathname.endsWith(".png") ||
    url.pathname.endsWith(".jpg") ||
    url.pathname.endsWith(".jpeg") ||
    url.pathname.endsWith(".svg") ||
    url.pathname.endsWith(".ico") ||
    url.pathname.endsWith(".woff") ||
    url.pathname.endsWith(".woff2")
  );
}

self.addEventListener("fetch", (event) => {
  const req = event.request;

  if (req.method !== "GET") return;

  const url = new URL(req.url);

  if (url.origin !== self.location.origin) return;

  if (req.mode === "navigate") {
    if (!shouldCacheHTML(url.pathname)) {
      event.respondWith(
        (async () => {
          try {
            const preloadResponse = event.preloadResponse;
            const networkResponse = preloadResponse ? await preloadResponse : await fetch(req);
            return networkResponse;
          } catch (e) {
            return caches.match("/offline");
          }
        })()
      );
      return;
    }
    
    event.respondWith(
      (async () => {
        const cache = await caches.open(RUNTIME_CACHE);
        const cachedResponse = await cache.match(req);
        
        const fetchPromise = (async () => {
          try {
            const preloadResponse = event.preloadResponse;
            const networkResponse = preloadResponse ? await preloadResponse : await fetch(req);
            if (networkResponse.ok) {
              cache.put(req, networkResponse.clone());
            }
            return networkResponse;
          } catch (e) {
            return null;
          }
        })();
        
        if (cachedResponse) {
          fetchPromise.catch(() => {});
          return cachedResponse;
        }
        
        const networkResponse = await fetchPromise;
        if (networkResponse) {
          return networkResponse;
        }
        
        return caches.match("/offline");
      })()
    );
    return;
  }

  if (isStaticAsset(url)) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(STATIC_CACHE).then((cache) => cache.put(req, copy));
          return res;
        });
      })
    );
    return;
  }

  event.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(RUNTIME_CACHE).then((cache) => cache.put(req, copy));
        return res;
      })
      .catch(() => caches.match(req))
  );
});
