/* ═══════════════════════════════════════════════════════
   Service worker — Cổng Thành

   CỐ Ý chỉ cache trang cổng, KHÔNG cache các cung bên trong.
   Mỗi cung có service worker riêng với phạm vi riêng
   (/kinh-thanh/, /dai-quan-trac/, /do-sat-vien/) và tự lo phần offline của
   nó. Cache chồng lấn ở đây sẽ khiến hai worker tranh nhau
   phục vụ cùng một file, và bản cũ của cung có thể bị cổng
   giữ lại sau khi cung đã cập nhật.
   ═══════════════════════════════════════════════════════ */

var CACHE_VERSION = "v4";
var SHELL_CACHE = "cong-thanh-" + CACHE_VERSION;

var SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/css/portal.css",
  "./assets/js/portal.js",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",
  "./assets/icons/icon-maskable-512.png",
  "./assets/icons/apple-touch-icon.png",
  "./assets/icons/favicon-32.png"
];

self.addEventListener("install", function (e) {
  // đẩy bản mới xuống ngay, đừng nằm chờ người dùng bấm gì
  // (cùng với clients.claim() ở activate và controllerchange ở pwa.js)
  self.skipWaiting();
  e.waitUntil(caches.open(SHELL_CACHE).then(function (c) {
    return Promise.all(SHELL.map(function (u) {
      return c.add(new Request(u, { cache: "reload" })).catch(function () {});
    }));
  }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.map(function (k) {
      if (k !== SHELL_CACHE) return caches.delete(k);
    }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("message", function (e) {
  if (e.data === "skip-waiting") self.skipWaiting();
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // để yên cho service worker của từng cung
  if (url.pathname.indexOf("/kinh-thanh/") !== -1) return;
  if (url.pathname.indexOf("/dai-quan-trac/") !== -1) return;
  if (url.pathname.indexOf("/do-sat-vien/") !== -1) return;

  if (req.mode === "navigate") {
    e.respondWith(fetch(req).catch(function () {
      return caches.match("./index.html", { ignoreSearch: true });
    }));
    return;
  }

  e.respondWith(caches.match(req, { ignoreSearch: true }).then(function (hit) {
    var net = fetch(req).then(function (res) {
      if (res && res.ok) {
        var copy = res.clone();
        caches.open(SHELL_CACHE).then(function (c) { c.put(req, copy); });
      }
      return res;
    });
    return hit || net;
  }));
});
