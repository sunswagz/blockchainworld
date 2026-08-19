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

  // Hộ Bộ: dong-tien.js ~54 KB. Ba khoá cần đọc — date, tomTat —
  // được build-hobu.mjs cố ý xếp ngay đầu object vì chỗ này chỉ đọc
  // 900 byte rồi huỷ dòng tải. Đổi thứ tự khoá bên đó là thẻ này mất
  // ngày cập nhật, và mất im lặng.
  dauFile("ho-bo/assets/js/v/dong-tien.js", 900)
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"date":\s*"([^"]+)"/);
      if (m) stamp("hbDate", "cập nhật " + m[1]);
      var n = t.match(/"tomTat":\s*"(\d+) chuỗi/);
      if (n) stamp("hbSo", n[1] + " chuỗi");
    })
    .catch(function () {});

  // Thái Bộc Tự: doan-tau.js ~17 KB. `date` và `tomTat` được
  // build-thaiboc.mjs cố ý xếp ngay đầu object vì chỗ này chỉ đọc
  // 900 byte rồi huỷ dòng tải — cùng bẫy như Hộ Bộ.
  dauFile("thai-boc-tu/assets/js/v/doan-tau.js", 900)
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"date":\s*"([^"]+)"/);
      if (m) stamp("tbDate", "cập nhật " + m[1]);
      var n = t.match(/"tomTat":\s*"([^"]+)"/);
      if (n) stamp("tbSo", n[1]);
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

  // Tử Cấm Thành: phien.js là lát cắt phiên giao dịch, `generatedAt` nằm ngay
  // đầu file. Cũng sinh tay như Hoàng Thành — runtime cần khoá API và một tiến
  // trình dài nên Actions không chạy được; chưa chạy lần nào thì generatedAt là
  // null và thẻ không hiện ngày, đúng như vậy chứ đừng bịa ra một ngày.
  dauFile("tu-cam-thanh/assets/js/v/phien.js", 900)
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"generatedAt":\s*"([^"]+)"/);
      if (m) stamp("tctDate", "phiên " + (ddmmyyyy(m[1]) || m[1]));
    })
    .catch(function () {});

  // Hoàng Thành: data.js ~380 KB, ngày và tổng số chương nằm ở đoạn đầu.
  // Khác bốn cung trên ở chỗ file này KHÔNG do workflow sinh — nguồn nằm
  // ngoài repo nên phải chạy `npm run hoangthanh` bằng tay rồi commit.
  dauFile("hoang-thanh/assets/js/data.js", 900)
    .then(function (t) {
      if (!t) return;
      var m = t.match(/"date":\s*"([^"]+)"/);
      if (m) stamp("htDate", "cập nhật " + m[1]);
      var n = t.match(/"xong":\s*(\d+)/);
      if (n) stamp("htSo", Number(n[1]).toLocaleString("vi-VN") + " chương");
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
