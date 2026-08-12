/* ═══════════════════════════════════════════════════════
   Vỏ ứng dụng: đăng ký service worker, nút cài đặt, báo bản mới.
   Tách riêng khỏi app.js để bản đồ vẫn chạy y nguyên khi bỏ file này
   (ví dụ khi đóng gói bằng Capacitor, lúc đó không cần service worker).
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var isHttp = location.protocol === "http:" || location.protocol === "https:";
  var standalone = window.matchMedia("(display-mode: standalone)").matches ||
                   window.navigator.standalone === true;
  if (standalone) document.documentElement.dataset.standalone = "1";

  /* ── báo có bản mới ─────────────────────────────────── */
  function toast(text, actionLabel, onAction) {
    var t = document.createElement("div");
    t.className = "toast";
    var s = document.createElement("span");
    s.textContent = text;
    t.appendChild(s);
    if (actionLabel) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = actionLabel;
      b.addEventListener("click", onAction);
      t.appendChild(b);
    }
    document.body.appendChild(t);
    requestAnimationFrame(function () { t.dataset.open = "1"; });
    return t;
  }

  /* ── service worker ─────────────────────────────────── */
  if ("serviceWorker" in navigator && isHttp) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").then(function (reg) {
        reg.addEventListener("updatefound", function () {
          var sw = reg.installing;
          if (!sw) return;
          sw.addEventListener("statechange", function () {
            // chỉ báo khi đã có bản cũ đang chạy, tránh báo ở lần cài đầu
            if (sw.state === "installed" && navigator.serviceWorker.controller) {
              toast("Đã có bản mới.", "Tải lại", function () {
                sw.postMessage("skip-waiting");
              });
            }
          });
        });
      }).catch(function () { /* offline hoặc bị chặn — bản đồ vẫn chạy bình thường */ });

      var reloading = false;
      navigator.serviceWorker.addEventListener("controllerchange", function () {
        if (reloading) return;
        reloading = true;
        window.location.reload();
      });
    });
  }

  /* ── nút cài ứng dụng (Android / Chrome / Edge) ─────── */
  var deferred = null;
  var btn = null;

  function makeButton() {
    if (btn) return btn;
    var foot = document.querySelector(".nav-foot");
    if (!foot) return null;
    btn = document.createElement("button");
    btn.type = "button";
    btn.className = "install";
    btn.title = "Cài lên màn hình chính";
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" ' +
      'stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M12 3.5v11"/><path d="m7.5 10 4.5 4.5 4.5-4.5"/>' +
      '<path d="M4.5 16.5v2a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-2"/></svg>' +
      '<span>Cài ứng dụng</span>';
    btn.addEventListener("click", function () {
      if (!deferred) return;
      deferred.prompt();
      deferred.userChoice.then(function () {
        deferred = null;
        btn.dataset.show = "0";
      });
    });
    foot.parentNode.insertBefore(btn, foot);
    return btn;
  }

  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
    var b = makeButton();
    if (b) b.dataset.show = "1";
  });

  window.addEventListener("appinstalled", function () {
    deferred = null;
    if (btn) btn.dataset.show = "0";
  });
})();
