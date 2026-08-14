/* ═══════════════════════════════════════════════════════
   Service worker — Công Bộ
   Chiến lược:
     · vỏ ứng dụng (html/css/js/icon) : cache trước, chạy offline
     · phông chữ Google              : cache khi dùng lần đầu
     · assets/js/data.js             : mạng trước — ~240 KB số liệu
                                       tự sinh, đổi mỗi 6 giờ
     · assets/logos/*.png            : cache khi dùng lần đầu

   CỐ Ý không nạp sẵn 106 logo (521 KB) vào SHELL: gấp đôi dung
   lượng cài đặt để lấy về ảnh mà phần lớn người dùng không cuộn
   tới. Chúng rơi vào nhánh cache-trước-cập-nhật-nền ở cuối file,
   nên xem tới đâu lưu tới đó và lần sau vẫn chạy offline.

   Đổi CACHE_VERSION mỗi lần phát hành để đẩy bản mới xuống máy.
   ═══════════════════════════════════════════════════════ */

var CACHE_VERSION = "v7";
var SHELL_CACHE = "cong-bo-shell-" + CACHE_VERSION;
var FONT_CACHE = "cong-bo-fonts-" + CACHE_VERSION;

var SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/css/app.css",
  "./assets/css/halls.css",
  "./assets/js/data.js",
  "./assets/js/logos.js",
  "./assets/js/glossary.js",
  "./assets/js/decoder.js",
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

  /* Số liệu tự cập nhật — mạng trước, hỏng mạng mới dùng bản đã lưu.
     logos.js cũng phải nằm đây: nó do build-congbo.mjs sinh 4 lượt/ngày
     như data.js. Để nó ở nhánh cache-trước thì máy đã cài app giữ bảng
     tra logo cũ cho tới lần nâng CACHE_VERSION kế tiếp — nghĩa là logo
     dự án mới không bao giờ hiện, dù ảnh đã lên site. */
  if (url.pathname.indexOf("/assets/js/data.js") !== -1 ||
      url.pathname.indexOf("/assets/js/logos.js") !== -1 ||
      url.pathname.indexOf("/assets/js/v/") !== -1) {
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
