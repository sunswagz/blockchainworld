/* ═══════════════════════════════════════════════════════
   Service worker — Đài Quan Trắc
     · vỏ ứng dụng      : cache trước, chạy offline
     · scan.js · do.js  : mạng trước (bot ghi 4 lượt/ngày)
     · phông chữ        : cache khi dùng lần đầu
   Đổi CACHE_VERSION mỗi lần phát hành.
   ═══════════════════════════════════════════════════════ */

var CACHE_VERSION = "v27";
var SHELL_CACHE = "dqt-shell-" + CACHE_VERSION;
var FONT_CACHE = "dqt-fonts-" + CACHE_VERSION;

var SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/css/app.css",
  "./assets/css/app-shell.css",
  "./assets/css/halls.css",
  "./assets/js/khung.js",
  "./assets/js/data.js",
  "./assets/js/soi.js",
  "./assets/js/tq/data.js",
  "./assets/js/tq/soi.js",
  "./assets/js/scan.js",
  "./assets/js/app.js",
  "./assets/js/halls.js",
  "./assets/js/pwa.js",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",
  "./assets/icons/icon-maskable-512.png",
  "./assets/icons/apple-touch-icon.png"
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
      if (k !== SHELL_CACHE && k !== FONT_CACHE) return caches.delete(k);
    }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("message", function (e) {
  if (e.data === "skip-waiting") self.skipWaiting();
});

function isFont(url) {
  return url.host === "fonts.googleapis.com" || url.host === "fonts.gstatic.com";
}

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);

  if (isFont(url)) {
    e.respondWith(caches.open(FONT_CACHE).then(function (c) {
      return c.match(req).then(function (hit) {
        var net = fetch(req).then(function (res) {
          if (res && (res.ok || res.type === "opaque")) c.put(req, res.clone());
          return res;
        }).catch(function () { return hit; });
        return hit || net;
      });
    }));
    return;
  }

  if (url.origin !== self.location.origin) return;

  // ── File bot ghi lại 4 lượt/ngày: LUÔN hỏi mạng trước ──
  // Thiếu một tên ở đây là lỗi im lặng và rất khó lần: file vẫn
  // lên site đúng giờ, curl vẫn thấy bản mới, Actions vẫn xanh —
  // nhưng máy đã cài app giữ bản cũ tới lần nâng CACHE_VERSION
  // kế tiếp. Repo đã dính đúng vậy với cong-bo/assets/js/logos.js.
  //
  // Danh sách, không phải một tên, để lần thêm file bot sau chỉ
  // là thêm một chuỗi. Giữ khớp với mục "File do workflow tự sinh"
  // trong CLAUDE.md.
  var MANG_TRUOC = ["/assets/js/scan.js", "/assets/js/do.js",
                  "/assets/js/tq/scan.js", "/assets/js/tq/do.js"];
  if (MANG_TRUOC.some(function (p) { return url.pathname.indexOf(p) !== -1; })) {
    e.respondWith(fetch(req).then(function (res) {
      if (res && res.ok) {
        var copy = res.clone();
        caches.open(SHELL_CACHE).then(function (c) { c.put(req, copy); });
      }
      return res;
    }).catch(function () {
      return caches.match(req, { ignoreSearch: true });
    }));
    return;
  }

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
