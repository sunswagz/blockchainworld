/* ═══════════════════════════════════════════════════════
   Service worker — Kinh Thành
   Chiến lược:
     · vỏ ứng dụng (html/css/js/icon) : cache trước, chạy offline
     · phông chữ Google              : cache khi dùng lần đầu
     · api.llama.fi                  : luôn gọi mạng, không cache
   Đổi CACHE_VERSION mỗi lần phát hành để đẩy bản mới xuống máy.
   ═══════════════════════════════════════════════════════ */

var CACHE_VERSION = "v1";
var SHELL_CACHE = "kinh-thanh-shell-" + CACHE_VERSION;
var FONT_CACHE = "kinh-thanh-fonts-" + CACHE_VERSION;

var SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/css/app.css",
  "./assets/css/app-shell.css",
  "./assets/css/l2beat.css",
  "./assets/css/provenance.css",
  "./assets/js/data/chains.js",
  "./assets/js/data/strength.js",
  "./assets/js/data/live.js",
  "./assets/js/data/provenance.js",
  "./assets/data/history.json",
  "./assets/js/data/entities.js",
  "./assets/js/data/cities.js",
  "./assets/js/l2beat.js",
  "./assets/js/provenance.js",
  "./assets/js/app.js",
  "./assets/js/pwa.js",
  "./assets/icons/icon-192.png",
  "./assets/icons/icon-512.png",
  "./assets/icons/icon-maskable-512.png",
  "./assets/icons/apple-touch-icon.png",
  "./assets/icons/favicon-32.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(SHELL_CACHE).then(function (c) {
      // addAll là all-or-nothing; thêm từng cái để một file lỗi không phá cả bản cài
      return Promise.all(SHELL.map(function (u) {
        return c.add(new Request(u, { cache: "reload" })).catch(function () {});
      }));
    })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k !== SHELL_CACHE && k !== FONT_CACHE) return caches.delete(k);
      }));
    }).then(function () {
      return self.clients.claim();
    })
  );
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

  // số liệu trực tiếp — không bao giờ cache
  if (url.host === "api.llama.fi") return;

  // phông chữ — dùng bản đã lưu, nền tải bản mới
  if (isFont(url)) {
    e.respondWith(
      caches.open(FONT_CACHE).then(function (c) {
        return c.match(req).then(function (hit) {
          var net = fetch(req).then(function (res) {
            if (res && (res.ok || res.type === "opaque")) c.put(req, res.clone());
            return res;
          }).catch(function () { return hit; });
          return hit || net;
        });
      })
    );
    return;
  }

  if (url.origin !== self.location.origin) return;

  // số liệu tự cập nhật — mạng trước, hỏng mạng mới dùng bản đã lưu.
  // Ngược hẳn với phần còn lại của app: số liệu đổi mỗi 6 giờ nên
  // luôn phải hỏi mạng, không thì người dùng xem số của lần mở trước.
  if (url.pathname.indexOf("/assets/js/data/live.js") !== -1 ||
      url.pathname.indexOf("/assets/js/data/provenance.js") !== -1 ||
      url.pathname.indexOf("/assets/data/history.json") !== -1) {
    e.respondWith(
      fetch(req).then(function (res) {
        if (res && res.ok) {
          var copy = res.clone();
          caches.open(SHELL_CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      }).catch(function () {
        return caches.match(req, { ignoreSearch: true });
      })
    );
    return;
  }

  // điều hướng — offline thì trả vỏ ứng dụng
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req).catch(function () {
        return caches.match("./index.html", { ignoreSearch: true });
      })
    );
    return;
  }

  // tài nguyên cùng nguồn — cache trước, cập nhật nền
  e.respondWith(
    caches.match(req, { ignoreSearch: true }).then(function (hit) {
      var net = fetch(req).then(function (res) {
        if (res && res.ok) {
          var copy = res.clone();
          caches.open(SHELL_CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      });
      return hit || net;
    })
  );
});
