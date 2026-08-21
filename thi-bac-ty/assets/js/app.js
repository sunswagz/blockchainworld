/* Thị Bạc Ty — cung tĩnh.
 *
 * Đọc `window.CANG_PHI` do `thi-bac-ty-runtime/bac/snapshot.py` ghi ra. Không
 * gọi mạng, không nút nào đặt lệnh — cung QUAN SÁT, runtime ĐIỀU KHIỂN.
 *
 * Luật của cả file: **chưa có lát cắt thì phải NÓI RA**. Trang hiện bảng
 * trống với mọi đèn xanh là kiểu hỏng tệ nhất một bảng điều khiển có thể có —
 * nó không sai, nó im lặng, và người xem không phân biệt được với "thị trường
 * hôm nay không có gì".
 */
(function () {
  "use strict";

  var D = window.CANG_PHI || null;

  function $(s) { return document.querySelector(s); }
  function el(t, c, x) {
    var e = document.createElement(t);
    if (c) e.className = c;
    if (x != null) e.textContent = x;
    return e;
  }
  function so(v, n, hau) {
    if (v == null || (typeof v === "number" && !isFinite(v))) return "—";
    return Number(v).toFixed(n == null ? 2 : n) + (hau || "");
  }
  function dau(v, n) {
    if (v == null || !isFinite(v)) return "—";
    return (v >= 0 ? "+" : "") + Number(v).toFixed(n == null ? 2 : n);
  }
  function lop(v) { return v == null ? "nhat" : (v >= 0 ? "duong" : "am"); }
  function gio(g) {
    if (g == null) return "—";
    if (g < 60) return Math.round(g) + " giây";
    if (g < 3600) return (g / 60).toFixed(1) + " phút";
    if (g < 86400) return (g / 3600).toFixed(1) + " giờ";
    return (g / 86400).toFixed(1) + " ngày";
  }

  function bang(cot, hang) {
    var w = el("div", "cuon"), t = el("table"), th = el("thead"), tr = el("tr");
    cot.forEach(function (c) { tr.appendChild(el("th", c.trai ? "trai" : null, c.t)); });
    th.appendChild(tr); t.appendChild(th);
    var tb = el("tbody");
    hang.forEach(function (h) {
      var r = el("tr");
      h.forEach(function (o) {
        var td = el("td", o.c || null, o.t);
        if (o.title) td.title = o.title;
        r.appendChild(td);
      });
      tb.appendChild(r);
    });
    t.appendChild(tb); w.appendChild(t);
    return w;
  }

  function giai(t) { return el("p", "giai", t); }

  function trong(nhan) {
    var d = document.createDocumentFragment();
    d.appendChild(el("p", "trong", nhan));
    return d;
  }

  /* ── chưa có lát cắt ────────────────────────────────────────────── */
  function chua_co() {
    var c = $("#canh-tinh");
    c.hidden = false;
    c.className = "canh-tinh nang";
    c.textContent =
      "CHƯA CÓ LÁT CẮT NÀO. File assets/js/v/cang-phi.js chưa được sinh, nên "
      + "mọi bảng dưới đây trống vì THIẾU DỮ LIỆU — không phải vì thị trường "
      + "không có chênh lệch. Sinh bằng: cd thi-bac-ty-runtime && python -m bac.snapshot";

    ["#oCoHoi", "#oViSao", "#oBaoGia", "#oCang"].forEach(function (s) {
      $(s).replaceChildren(trong("chưa có dữ liệu — xem dải cảnh báo ở trên"));
    });
    $("#dauSo").replaceChildren(el("span", "vien xau", "chưa có lát cắt"));
    $("#chanNhac").textContent =
      "Cung tĩnh này chỉ đọc một file đã commit. Nó không gọi sàn nào.";
  }

  /* ── đỉnh trang ─────────────────────────────────────────────────── */
  function ve_dinh() {
    var s = $("#dauSo"), ds = [];
    ds.push(["lát cắt " + (D.date || "—"), ""]);
    ds.push(["chế độ " + (D.che || "—"), D.che === "quan-sat" ? "" : "canh"]);
    var song = (D.cang || []).filter(function (c) { return c.songSot; }).length;
    var tong = (D.cang || []).length;
    ds.push([song + "/" + tong + " cảng", song === tong ? "on" : "xau"]);
    ds.push([(D.soDuyet || 0) + " cặp qua cửa", (D.soDuyet || 0) ? "on" : ""]);
    s.replaceChildren.apply(s, ds.map(function (x) {
      return el("span", "vien" + (x[1] ? " " + x[1] : ""), x[0]);
    }));
  }

  function ve_canh() {
    var c = $("#canh-tinh"), ds = [];
    var chet = (D.cang || []).filter(function (x) { return !x.songSot; });
    if (chet.length)
      ds.push("MÙ MỘT MẮT lúc chụp: " + chet.map(function (x) { return x.ten; }).join(", ")
              + " chưa lấy được dữ liệu lần nào — bảng dưới thiếu cảng.");
    if (D.loiVongCuoi) ds.push("vòng quét gần nhất lỗi: " + D.loiVongCuoi);

    // Lát cắt cũ: số liệu funding hết hạn rất nhanh, một lát cắt tuần trước
    // nói về một thế giới đã qua. Nói thẳng tuổi của nó.
    var tuoi = null;
    if (D.generatedAt) {
      var t = Date.parse(D.generatedAt);
      if (!isNaN(t)) tuoi = (Date.now() - t) / 1000;
    }
    if (tuoi != null && tuoi > 86400)
      ds.push("lát cắt đã " + gio(tuoi) + " tuổi — funding đổi theo giờ, "
              + "nên đây là ảnh của một thế giới đã qua.");

    if (!ds.length) { c.hidden = true; return; }
    c.hidden = false;
    c.className = "canh-tinh" + (chet.length ? " nang" : "");
    c.textContent = ds.join("  ·  ");
  }

  /* ── cơ hội ─────────────────────────────────────────────────────── */
  function ve_co_hoi() {
    var ds = D.coHoi || [], n = $("#oCoHoi");
    if (!ds.length) {
      n.replaceChildren(trong(
        "lát cắt này chưa cân được cặp nào — cần ít nhất hai cảng cùng trả về "
        + "một mã thì mới ghép được một cặp"));
      return;
    }

    var f = document.createDocumentFragment();

    var l = el("div", "luoi");
    [["cặp đã cân", ds.length],
     ["qua cửa rủi ro", D.soDuyet || 0],
     ["cửa sổ giữ giả định", so(D.giuGio, 0) + " giờ"],
     ["mã theo dõi", (D.ma || []).length]
    ].forEach(function (x) {
      var d = el("div", "so");
      d.appendChild(el("div", "n", String(x[1])));
      d.appendChild(el("div", "t", x[0]));
      l.appendChild(d);
    });
    f.appendChild(l);

    f.appendChild(bang(
      [{ t: "Mã", trai: 1 }, { t: "LONG", trai: 1 }, { t: "SHORT", trai: 1 },
       { t: "gross bps/ngày" }, { t: "mốc L+S" }, { t: "thu bps" },
       { t: "phí bps" }, { t: "NET bps" }, { t: "lệch mark" },
       { t: "cửa", trai: 1 }, { t: "vì sao", trai: 1 }],
      ds.map(function (c) {
        var km = (c.soMocLong || 0) + (c.soMocShort || 0);
        return [
          { t: c.ma, c: "trai" },
          { t: c.sanLong, c: "trai" },
          { t: c.sanShort, c: "trai" },
          { t: dau(c.grossBpsNgay) },
          { t: (c.soMocLong || 0) + "+" + (c.soMocShort || 0),
            c: km ? null : "am",
            title: km ? "" : "không mốc kết toán nào rơi vào cửa sổ giữ" },
          { t: dau(c.thuBps), c: lop(c.thuBps) },
          { t: so(c.phiBps), c: "nhat" },
          { t: dau(c.netBps), c: lop(c.netBps) },
          { t: c.lechMarkBps == null ? "—" : so(c.lechMarkBps, 1),
            c: c.lechMarkBps == null ? "am" : "nhat" },
          { t: c.duyet ? "QUA" : "chặn", c: c.duyet ? "qua" : "chan" },
          { t: (c.lyDo || []).join(" · ") || "—", c: "vi" }
        ];
      })));

    f.appendChild(giai(
      "Cột NET là funding thực thu trừ phí và trượt giá — thứ duy nhất đáng "
      + "xếp hạng. Cột gross chỉ là chênh lệch thô đã chuẩn hoá, chưa trừ gì. "
      + "Cột 'mốc L+S' bằng 0+0 nghĩa là giữ hết cửa sổ mà thu đúng bằng "
      + "không, dù gross trông vẫn to — xem mục Hai phép tính."));
    n.replaceChildren(f);
  }

  function ve_vi_sao() {
    var vs = D.viSaoTuChoi || {}, k = Object.keys(vs), n = $("#oViSao");
    if (!k.length) {
      n.replaceChildren(trong("không cặp nào bị chặn trong lát cắt này"));
      return;
    }
    k.sort(function (a, b) { return vs[b] - vs[a]; });
    var f = document.createDocumentFragment();
    f.appendChild(bang(
      [{ t: "Lý do", trai: 1 }, { t: "số cặp" }],
      k.map(function (x) { return [{ t: x, c: "trai" }, { t: String(vs[x]) }]; })));
    f.appendChild(giai(
      "Bảng cơ hội trống mà không có bảng này thì người xem đọc thành \"thị "
      + "trường hôm nay không có gì\". Thường sự thật là: có chênh lệch, "
      + "nhưng phí ăn hết — và đó là hai kết luận rất khác nhau."));
    n.replaceChildren(f);
  }

  function ve_bao_gia() {
    var ds = (D.baoGia || []).slice(), n = $("#oBaoGia");
    if (!ds.length) {
      n.replaceChildren(trong("lát cắt này không có báo giá nào"));
      return;
    }
    ds.sort(function (a, b) {
      return a.ma === b.ma ? (b.moiNgayBps - a.moiNgayBps) : (a.ma < b.ma ? -1 : 1);
    });
    var f = document.createDocumentFragment();
    f.appendChild(bang(
      [{ t: "Mã", trai: 1 }, { t: "Cảng", trai: 1 }, { t: "rate / chu kỳ" },
       { t: "chu kỳ" }, { t: "bps/ngày" }, { t: "mark" }, { t: "tuổi" },
       { t: "ghi chú", trai: 1 }],
      ds.map(function (q) {
        return [
          { t: q.ma, c: "trai" },
          { t: q.san, c: "trai" },
          { t: (q.rate * 100).toFixed(5) + "%" },
          { t: so(q.intervalGio, 0) + "h" + (q.intervalSuyRa ? " ?" : ""),
            c: q.intervalSuyRa ? "am" : null,
            title: q.intervalSuyRa ? "chu kỳ phải ĐOÁN — sàn không công bố" : "" },
          { t: dau(q.moiNgayBps), c: lop(q.moiNgayBps) },
          { t: q.markPx == null ? "—" : so(q.markPx, 4),
            c: q.markPx == null ? "am" : null },
          { t: q.tuoiGiay == null ? "—" : gio(q.tuoiGiay), c: "nhat" },
          { t: q.ghiChu || "", c: "vi" }
        ];
      })));
    f.appendChild(giai(
      "Cột 'rate / chu kỳ' là con số sàn công bố; 'bps/ngày' là sau khi chia "
      + "cho chu kỳ thật rồi quy về ngày. So hai cảng bằng cột đầu là sai — "
      + "0,08%/8h nhỏ hơn 0,015%/1h, dù nhìn số thô thì ngược lại."));
    n.replaceChildren(f);
  }

  function ve_cang() {
    var ds = D.cang || [], n = $("#oCang");
    if (!ds.length) { n.replaceChildren(trong("không có cảng nào")); return; }
    var f = document.createDocumentFragment();
    f.appendChild(bang(
      [{ t: "Cảng", trai: 1 }, { t: "trạng thái", trai: 1 }, { t: "lượt hỏi" },
       { t: "lỗi" }, { t: "trễ TB" }, { t: "phí taker" }, { t: "trượt giá" },
       { t: "lỗi cuối", trai: 1 }],
      ds.map(function (c) {
        var p = (D.phiSan || {})[c.ten] || {};
        return [
          { t: c.ten, c: "trai" },
          { t: c.songSot ? "sống" : "CHƯA BAO GIỜ",
            c: c.songSot ? "qua" : "am" },
          { t: String(c.tongLuot == null ? "—" : c.tongLuot) },
          { t: String(c.soLoi == null ? "—" : c.soLoi),
            c: c.soLoi ? "am" : "nhat" },
          { t: so(c.treTrungBinhMs, 0) + " ms" },
          { t: so(p.phiTakerBps, 1) + " bps" },
          { t: so(p.truotGiaBps, 1) + " bps" },
          { t: c.loiCuoi || "", c: "vi" }
        ];
      })));
    f.appendChild(giai(
      "Phí và trượt giá là THAM SỐ trong config.json của runtime, không phải "
      + "số đo được từ sàn. Đặt quá thấp là tự vẽ ra lợi nhuận không có thật."));
    n.replaceChildren(f);
  }

  function ve_chan() {
    var t = [];
    if (D.tomTat) t.push(D.tomTat);
    if (D.vong != null) t.push("vòng quét thứ " + D.vong);
    if (D.chayDuocGiay != null) t.push("runtime chạy được " + gio(D.chayDuocGiay));
    if (D.so && D.so.soLuot) t.push(D.so.soLuot + " lượt quét đã ghi sổ");
    $("#chanNhac").textContent =
      t.join(" · ") + (t.length ? ". " : "") + (D.loiNhac || "");
  }

  function ve() {
    if (!D) { chua_co(); return; }
    // Dựng từng ô trong try riêng: một ô hỏng không được kéo theo cả trang,
    // và chỗ hỏng phải HIỆN ra chứ không để lại một khoảng trắng.
    [["đỉnh", ve_dinh], ["cảnh báo", ve_canh], ["cơ hội", ve_co_hoi],
     ["vì sao", ve_vi_sao], ["báo giá", ve_bao_gia], ["cảng", ve_cang],
     ["chân trang", ve_chan]
    ].forEach(function (x) {
      try { x[1](); }
      catch (e) {
        var c = $("#canh-tinh");
        c.hidden = false;
        c.className = "canh-tinh nang";
        c.textContent = "Ô «" + x[0] + "» vẽ hỏng: " + (e && e.message || e)
          + " — lát cắt vẫn còn nguyên trong assets/js/v/cang-phi.js.";
      }
    });
  }

  /* ── thanh bên trên máy hẹp ─────────────────────────────────────── */
  var ben = $("#ben"), nut = $("#benNut");
  if (nut) nut.addEventListener("click", function () {
    ben.setAttribute("data-mo", ben.getAttribute("data-mo") === "1" ? "0" : "1");
  });
  document.addEventListener("click", function (e) {
    if (window.innerWidth > 900) return;
    if (e.target.closest("#ben a")) ben.setAttribute("data-mo", "0");
    else if (!e.target.closest("#ben") && !e.target.closest("#benNut"))
      ben.setAttribute("data-mo", "0");
  });

  ve();
})();
