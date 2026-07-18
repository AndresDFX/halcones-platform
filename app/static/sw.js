/* Service Worker — Halcones Paracaidismo (app server-rendered).
   Estrategia:
   - Navegación (HTML): network-first con fallback a /offline si no hay red.
   - Estáticos (css/js/img/fuentes): cache-first con relleno bajo demanda.
   No se cachean POST ni respuestas de /api, /uploads dinámicos, etc.
*/
const CACHE = "halcones-v1";
const PRECACHE = [
  "/offline",
  "/static/css/app.css",
  "/static/js/app.js",
  "/static/img/logo-mark.png",
  "/static/img/icon-192.png",
  "/static/img/favicon.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(PRECACHE).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE).map((n) => caches.delete(n)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.protocol !== "http:" && url.protocol !== "https:") return;
  // No interferir con API ni descargas de archivos.
  if (url.pathname.startsWith("/api") || url.pathname.startsWith("/uploads")) return;

  // Navegación → network-first, fallback offline.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(() => caches.match("/offline").then(
        (r) => r || new Response("Sin conexión", { status: 503, headers: { "Content-Type": "text/plain" } })
      ))
    );
    return;
  }

  // Estáticos → cache-first.
  if (url.pathname.startsWith("/static/")) {
    event.respondWith(
      caches.match(request).then((cached) =>
        cached || fetch(request).then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(request, clone)).catch(() => {});
          }
          return res;
        })
      )
    );
    return;
  }

  // Google Fonts → cache-first.
  if (url.hostname.includes("fonts.googleapis.com") || url.hostname.includes("fonts.gstatic.com")) {
    event.respondWith(
      caches.match(request).then((cached) =>
        cached || fetch(request).then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(request, clone)).catch(() => {});
          }
          return res;
        }).catch(() => cached)
      )
    );
  }
});
