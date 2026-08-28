/* ═══════════════════════════════════════════════════════
   Service worker — Tạo Biện Xứ
   Chiến lược:
     · vỏ ứng dụng (html/css/js/icon) : cache trước, chạy offline
     · phông chữ Google              : cache khi dùng lần đầu

   `assets/js/data.js` là bản thiết kế VIẾT TAY, đổi cùng nhịp với
   mã, nên nó nằm thẳng trong SHELL.

   Nhưng `assets/js/v/van-hanh.js` thì ngược hẳn: bot ghi đè nó sau
   mỗi lượt GitHub Actions (4 lượt/ngày). Để nó ở nhánh cache-trước
   là Bảng vận hành hiện số của hôm qua cho tới lần nâng
   CACHE_VERSION kế tiếp — tức là một bảng điều khiển nói dối, thứ
   tệ hơn hẳn không có bảng nào. Đúng cái bẫy đã cắn logos.js của
   Công Bộ. Nên nó đi nhánh MẠNG-TRƯỚC và KHÔNG nằm trong SHELL.

   Đổi CACHE_VERSION mỗi lần phát hành để đẩy bản mới xuống máy.
   Quên nâng thì máy đã cài cứ dùng bản cũ — xem mục "Sửa file
   trong SHELL thì phải nâng CACHE_VERSION" trong CLAUDE.md.
   ═══════════════════════════════════════════════════════ */

var CACHE_VERSION = "v18";
var SHELL_CACHE = "tao-bien-xu-shell-" + CACHE_VERSION;
var FONT_CACHE = "tao-bien-xu-fonts-" + CACHE_VERSION;

var SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/css/app.css",
  "./assets/css/halls.css",
  "./assets/js/data.js",
  "./assets/js/app.js",
  "./assets/js/pwa.js",
  "./assets/js/halls.js",
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
    // addAll là all-or-nothing; thêm từng cái để một file lỗi không phá cả bản cài
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

  /* Mạng trước, cache chỉ là lưới đỡ lúc mất mạng. `npm run kiem`
     và `npm run nang` đều đọc chính dòng indexOf() này để biết file
     nào được MIỄN luật nâng CACHE_VERSION — đừng đổi cách viết. */
  if (url.pathname.indexOf("/assets/js/v/") !== -1) {
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
