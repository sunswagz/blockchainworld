/* Vỏ ứng dụng Tàng Thư Các: service worker, nút cài, báo bản mới.
   Bỏ file này đi thì app vẫn chạy, chỉ mất cài đặt và offline. */
(function () {
  "use strict";

  var isHttp = location.protocol === "http:" || location.protocol === "https:";

  function toast(text, label, onClick) {
    var t = document.createElement("div");
    t.className = "sw-toast";
    var s = document.createElement("span");
    s.textContent = text;
    t.appendChild(s);
    if (label) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = label;
      b.addEventListener("click", onClick);
      t.appendChild(b);
    }
    document.body.appendChild(t);
    requestAnimationFrame(function () { t.dataset.open = "1"; });
  }

  if ("serviceWorker" in navigator && isHttp) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").then(function (reg) {
        reg.addEventListener("updatefound", function () {
          var sw = reg.installing;
          if (!sw) return;
          sw.addEventListener("statechange", function () {
            if (sw.state === "installed" && navigator.serviceWorker.controller) {
              toast("Đã có bản mới.", "Tải lại", function () { sw.postMessage("skip-waiting"); });
            }
          });
        });
      }).catch(function () {});

      var reloading = false;
      navigator.serviceWorker.addEventListener("controllerchange", function () {
        if (reloading) return;
        reloading = true;
        window.location.reload();
      });
    });
  }

  /* nút cài — nối vào cuối mục "Các cung", nên phải đợi halls.js dựng xong */
  var deferred = null, btn = null;

  function gan() {
    var strip = document.getElementById("cungNav");
    if (!strip || btn || !deferred) return;
    btn = document.createElement("button");
    btn.type = "button";
    btn.className = "install-tt";
    btn.dataset.show = "1";
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" ' +
      'stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5v11"/>' +
      '<path d="m7.5 10 4.5 4.5 4.5-4.5"/><path d="M4.5 16.5v2a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-2"/></svg>' +
      '<span>Cài ứng dụng</span>';
    btn.addEventListener("click", function () {
      if (!deferred) return;
      deferred.prompt();
      deferred.userChoice.then(function () { deferred = null; btn.dataset.show = "0"; });
    });
    strip.appendChild(btn);
  }

  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", gan);
    else gan();
  });

  window.addEventListener("appinstalled", function () {
    deferred = null;
    if (btn) btn.dataset.show = "0";
  });
})();
