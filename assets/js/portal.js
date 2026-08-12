/* ═══════════════════════════════════════════════════════
   Cổng Thành — đọc ngày cập nhật của từng cung, service
   worker, nút cài.

   Ngày lấy trực tiếp từ file dữ liệu của mỗi cung, không
   chép cứng sang đây: cung nào cập nhật thì thẻ của nó tự
   đổi theo, không phải sửa hai chỗ.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var isHttp = location.protocol === "http:" || location.protocol === "https:";

  /* ── ngày cập nhật của từng cung ────────────────────── */
  function stamp(id, text) {
    var e = document.getElementById(id);
    if (e && text) e.textContent = text;
  }

  function ddmmyyyy(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) return null;
    var p = function (n) { return String(n).padStart(2, "0"); };
    return p(d.getUTCDate()) + "/" + p(d.getUTCMonth() + 1) + "/" + d.getUTCFullYear();
  }

  // Kinh Thành: live.js chứa "date": "dd/mm/yyyy"
  fetch("kinh-thanh/assets/js/data/live.js", { cache: "no-store" })
    .then(function (r) { return r.ok ? r.text() : null; })
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"date":\s*"([^"]+)"/);
      if (m) stamp("ktDate", "cập nhật " + m[1]);
    })
    .catch(function () {});

  // Đài Quan Trắc: scan.js chứa "generatedAt": ISO (null nếu chưa quét)
  fetch("dai-quan-trac/assets/js/scan.js", { cache: "no-store" })
    .then(function (r) { return r.ok ? r.text() : null; })
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"generatedAt":\s*"([^"]+)"/);
      stamp("dqtDate", m ? "quét " + (ddmmyyyy(m[1]) || m[1]) : "chưa quét lần nào");
    })
    .catch(function () {});

  // đếm số cung đã dựng, lấy từ chính DOM
  var built = document.querySelectorAll(".hall:not([data-soon])").length;
  stamp("hallCount", String(built).padStart(2, "0"));

  /* ── service worker ─────────────────────────────────── */
  if ("serviceWorker" in navigator && isHttp) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").catch(function () {});
    });
  }

  /* ── nút cài ────────────────────────────────────────── */
  var deferred = null;
  var btn = document.getElementById("installGate");

  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
    if (btn) btn.dataset.show = "1";
  });

  if (btn) {
    btn.addEventListener("click", function () {
      if (!deferred) return;
      deferred.prompt();
      deferred.userChoice.then(function () {
        deferred = null;
        btn.dataset.show = "0";
      });
    });
  }

  window.addEventListener("appinstalled", function () {
    deferred = null;
    if (btn) btn.dataset.show = "0";
  });
})();
