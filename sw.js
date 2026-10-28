// Officinews : mode hors ligne.
// Pages et données (articles.json, dispo.json) : réseau d'abord, dernière version enregistrée si pas de réseau.
// Images, icônes et polices : cache d'abord, rafraîchi en arrière-plan.
const VERSION = "officinews-v2";
const ESSENTIELS = ["./", "index.html", "manifest.webmanifest", "logo-mark.png", "favicon.png",
  "icon-180.png", "icon-192.png", "articles.json", "dispo.json", "vaccins.json"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(ESSENTIELS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((cles) => Promise.all(cles.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

const sansParametres = (url) => url.origin + url.pathname;

async function reseauDabord(req, url) {
  const cache = await caches.open(VERSION);
  try {
    const rep = await fetch(req);
    if (rep.ok) cache.put(sansParametres(url), rep.clone());
    return rep;
  } catch (err) {
    const enCache = await cache.match(sansParametres(url), { ignoreSearch: true });
    if (enCache) return enCache;
    if (req.mode === "navigate") {
      const page = await cache.match(new URL("./", self.registration.scope).href);
      if (page) return page;
    }
    throw err;
  }
}

async function cacheDabord(req) {
  const cache = await caches.open(VERSION);
  const enCache = await cache.match(req);
  const maj = fetch(req).then((rep) => {
    if (rep.ok || rep.type === "opaque") cache.put(req, rep.clone());
    return rep;
  }).catch(() => enCache);
  return enCache || maj;
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const memeSite = url.origin === self.location.origin;
  if (memeSite && (req.mode === "navigate" || url.pathname.endsWith(".json") || url.pathname.endsWith(".html") || url.pathname.endsWith("/"))) {
    e.respondWith(reseauDabord(req, url));
  } else if (memeSite || url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(cacheDabord(req));
  }
});
