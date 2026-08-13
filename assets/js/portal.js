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

  // Đô Sát Viện: data.js nặng ~180 KB, mà tất cả những gì cần đều nằm
  // trong đoạn đầu. Đọc một khúc rồi huỷ luôn dòng tải, không kéo hết file.
  function dauFile(url, byte) {
    return fetch(url, { cache: "no-store" }).then(function (r) {
      if (!r.ok) return null;
      if (!r.body || !r.body.getReader) return r.text();  // trình duyệt cũ
      var reader = r.body.getReader(), dec = new TextDecoder(), got = "";
      return (function doc() {
        return reader.read().then(function (b) {
          if (b.done) return got;
          got += dec.decode(b.value, { stream: true });
          if (got.length >= byte) { reader.cancel(); return got; }
          return doc();
        });
      })();
    });
  }

  dauFile("do-sat-vien/assets/js/data.js", 900)
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"date":\s*"([^"]+)"/);
      if (m) stamp("dsvDate", "cập nhật " + m[1]);
      var n = t.match(/(\d+)\s+dự án/);
      if (n) stamp("dsvSo", n[1] + " thành phố");
    })
    .catch(function () {});

  // Công Bộ: data.js ~130 KB, ngày và số thay đổi đều nằm ở đoạn đầu
  dauFile("cong-bo/assets/js/data.js", 900)
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"date":\s*"([^"]+)"/);
      if (m) stamp("cbDate", "cập nhật " + m[1]);
      var n = t.match(/(\d+) thay đổi/);
      if (n) stamp("cbSo", n[1] + " thay đổi");
    })
    .catch(function () {});

  // Tàng Thư Các: data.js ~230 KB, ngày và số skill nằm ở đoạn đầu
  dauFile("tang-thu-cac/assets/js/data.js", 900)
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"date":\s*"([^"]+)"/);
      if (m) stamp("ttDate", "cập nhật " + m[1]);
      var n = t.match(/(\d+) skill từ/);
      if (n) stamp("ttSo", n[1] + " skill");
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

    /* sw.js gọi skipWaiting() ngay lúc cài, nên bản mới chiếm quyền
       điều khiển liền. Tải lại một lần để trang đang mở dùng bản
       mới thay vì bản cũ trong cache — cờ `daTai` chặn vòng lặp
       nếu bản mới lại kích hoạt lần nữa. */
    var daTai = false;
    navigator.serviceWorker.addEventListener("controllerchange", function () {
      if (daTai) return;
      daTai = true;
      window.location.reload();
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
