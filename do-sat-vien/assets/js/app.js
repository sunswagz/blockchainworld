/* ═══════════════════════════════════════════════════════
   ĐÔ SÁT VIỆN — bảng xét các thành phố Layer 2.

   Dữ liệu: window.DSV_DATA (tự sinh, xem scripts/build-l2beat.mjs)
   Chú giải: window.DSV_VI  (bản dịch và diễn giải, glossary.js)

   Bố cục bám theo l2beat.com/scaling/summary: sidebar trái,
   biểu đồ tài sản, ba tab Rollup / Validium / Khác, bảng có
   rosette 5 cánh rủi ro.

   Nhãn nào L2BEAT thêm mới mà chú giải chưa có thì hiện nguyên
   bản tiếng Anh và đánh dấu "chưa dịch" — không bịa nghĩa.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.DSV_DATA, VI = window.DSV_VI;
  if (!D || !VI) return;

  var P = D.projects || [];
  var LOGO = "assets/logos/";
  var state = { q: "", tab: "rollup", thang: "all", sort: "tvs", desc: true };

  var MAU = { good: "#3DBB69", warning: "#F2B94A", bad: "#F05252", neutral: "#B4B5BC" };
  var MAU_TVS = { native: "#FF46A2", canonical: "#8B7FE8", external: "#F5C23E" };

  /* ── tiện ích ─────────────────────────────────────── */
  function $(s) { return document.querySelector(s); }
  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function norm(s) {
    /* ̀-ͯ viết dạng escape, KHÔNG viết dấu tổ hợp thẳng vào
       regex: chúng vô hình trong trình soạn thảo và hay bị công cụ
       chuẩn hoá lại thành ký tự khác, làm bộ tìm kiếm hỏng lặng lẽ. */
    return String(s).toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "").replace(/\u0111/g, "d");
  }
  function usd(v) {
    if (v == null) return "—";
    if (v >= 1e9) return "$" + (v / 1e9).toFixed(2) + "b";
    if (v >= 1e6) return "$" + Math.round(v / 1e6) + "m";
    if (v >= 1e3) return "$" + Math.round(v / 1e3) + "k";
    return "$" + Math.round(v);
  }
  function pct(v, s) {
    if (typeof v !== "number") return "";
    return '<i data-d="' + (v >= 0 ? "up" : "down") + '">' +
      (v >= 0 ? "+" : "") + (v * 100).toFixed(1) + "%" + (s || "") + "</i>";
  }

  /* tra chú giải — không có thì trả nguyên bản, đánh dấu chưa dịch */
  function tra(nhom, key) {
    var g = VI[nhom] && VI[nhom][key];
    if (!g) return { nhan: key || "—", y: null, vn: null, thieu: true };
    if (typeof g === "string") return { nhan: g, y: null, vn: null };
    return g;
  }

  /* Cùng một chuỗi giá trị có thể mang nghĩa khác nhau tuỳ chiều rủi ro
     ("None" ở Exit Window ≠ "None" ở State Validation), nên tra bảng
     riêng của chiều đó trước, không có mới dùng bảng chung. */
  function traGia(chieu, giaTri) {
    var o = VI.giaTheoChieu && VI.giaTheoChieu[chieu] && VI.giaTheoChieu[chieu][giaTri];
    return o || tra("gia", giaTri);
  }

  function stageNum(s) {
    if (!s) return -1;
    if (s.indexOf("Stage") === 0) return parseInt(s.slice(-1), 10);
    return -1;
  }

  function svgIc(paths, w) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="' +
      (w || 1.7) + '" stroke-linecap="round" stroke-linejoin="round">' + paths + "</svg>";
  }

  /* ── rosette 5 cánh ───────────────────────────────────
     Năm chiều rủi ro thành năm múi quạt quanh một tâm. Nhìn một
     cái là thấy dự án yếu ở đâu, khỏi phải mở hồ sơ. Đây là hình
     nhận diện của L2BEAT. */
  function rosette(ruiRo, cao) {
    var r = (cao || 24) / 2, n = 5, buoc = (Math.PI * 2) / n;
    var s = '<svg viewBox="0 0 ' + (r * 2) + " " + (r * 2) + '" aria-hidden="true">';
    for (var i = 0; i < n; i++) {
      var rr = ruiRo[i];
      var mau = rr ? (MAU[rr.s] || MAU.neutral) : "#E4E5EA";
      /* -90° để múi đầu tiên bắt đầu từ đỉnh */
      var a0 = -Math.PI / 2 + i * buoc, a1 = a0 + buoc;
      var x0 = r + r * Math.cos(a0), y0 = r + r * Math.sin(a0);
      var x1 = r + r * Math.cos(a1), y1 = r + r * Math.sin(a1);
      s += '<path d="M' + r.toFixed(2) + " " + r.toFixed(2) +
        "L" + x0.toFixed(2) + " " + y0.toFixed(2) +
        "A" + r.toFixed(2) + " " + r.toFixed(2) + " 0 0 1 " + x1.toFixed(2) + " " + y1.toFixed(2) +
        'Z" fill="' + mau + '" stroke="#fff" stroke-width="1"/>';
    }
    s += "</svg>";
    return s;
  }

  function rosetteTitle(ruiRo) {
    return ruiRo.map(function (r) {
      return tra("chieu", r.n).nhan + ": " + traGia(r.n, r.v).nhan;
    }).join("\n");
  }

  /* ── biểu đồ tài sản theo thời gian ───────────────────
     Ba lớp chồng (gốc bản địa / cầu chính thức / cầu ngoài).
     Vẽ bằng SVG thuần — không kéo thư viện biểu đồ nào về. */
  function veBieuDo() {
    var host = $("#bd");
    if (!host) return;
    var B = D.bieuDo;
    if (!B || !B.diem || !B.diem.length) {
      host.innerHTML = '<p class="the-ghi">Chưa có dữ liệu biểu đồ.</p>';
      return;
    }

    var cot = B.cot || [];
    var iN = cot.indexOf("native"), iC = cot.indexOf("canonical"), iE = cot.indexOf("external");
    if (iN < 0 || iC < 0 || iE < 0) { iN = 1; iC = 2; iE = 3; }

    var d = B.diem, W = 600, H = 170, PB = 18;
    var tong = d.map(function (p) { return (p[iN] || 0) + (p[iC] || 0) + (p[iE] || 0); });
    var max = Math.max.apply(null, tong) * 1.06 || 1;
    var x = function (i) { return (i / (d.length - 1)) * W; };
    var y = function (v) { return H - PB - (v / max) * (H - PB); };

    /* chồng từ dưới lên: native → canonical → external */
    var lop = [
      { k: iN, mau: MAU_TVS.native },
      { k: iC, mau: MAU_TVS.canonical },
      { k: iE, mau: MAU_TVS.external }
    ];
    var duoi = d.map(function () { return 0; });
    var s = '<svg viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" role="img" ' +
      'aria-label="Tài sản đang giữ theo thời gian">';

    lop.forEach(function (L) {
      var tren = d.map(function (p, i) { return duoi[i] + (p[L.k] || 0); });
      var path = "M0 " + y(duoi[0]).toFixed(1);
      for (var i = 0; i < d.length; i++) path += "L" + x(i).toFixed(1) + " " + y(tren[i]).toFixed(1);
      for (var j = d.length - 1; j >= 0; j--) path += "L" + x(j).toFixed(1) + " " + y(duoi[j]).toFixed(1);
      path += "Z";
      s += '<path d="' + path + '" fill="' + L.mau + '" fill-opacity=".82"/>';
      duoi = tren;
    });

    /* Lưới ngang trong SVG, nhưng NHÃN GIÁ TRỊ dựng bằng HTML đè lên.
       SVG này có preserveAspectRatio="none" để giãn hết bề ngang, nên
       mọi thứ bên trong bị kéo méo theo — chữ thành bẹt và nét viền
       thành vệt. Nhãn HTML nằm ngoài phép giãn đó nên luôn sắc nét. */
    var nhanY = [];
    [0.5, 1].forEach(function (f) {
      var v = max * f, yy = y(v);
      s += '<line x1="0" x2="' + W + '" y1="' + yy.toFixed(1) + '" y2="' + yy.toFixed(1) +
        '" stroke="#D8D9E0" stroke-width="1" stroke-dasharray="3 3"/>';
      nhanY.push('<span class="bd-nhan" style="top:' + (yy / H * 100).toFixed(2) + '%">' +
        esc(usd(v)) + "</span>");
    });

    /* mốc thời gian: đầu, giữa, cuối */
    [0, Math.floor(d.length / 2), d.length - 1].forEach(function (i, k) {
      var t = new Date(d[i][0] * 1000);
      var nhan = String(t.getUTCDate()).padStart(2, "0") + "/" + String(t.getUTCMonth() + 1).padStart(2, "0");
      var anchor = k === 0 ? "start" : (k === 2 ? "end" : "middle");
      s += '<text class="bd-truc" x="' + x(i).toFixed(0) + '" y="' + (H - 5) +
        '" text-anchor="' + anchor + '">' + nhan + "</text>";
    });
    s += "</svg>";

    var cuoi = d[d.length - 1];
    var tongCuoi = (cuoi[iN] || 0) + (cuoi[iC] || 0) + (cuoi[iE] || 0);
    var dau = d[0];
    var tongDau = (dau[iN] || 0) + (dau[iC] || 0) + (dau[iE] || 0);
    var doi = tongDau ? (tongCuoi - tongDau) / tongDau : null;

    /* Khoảng thời gian tính từ chính mốc thời gian, KHÔNG suy từ số
       điểm: L2BEAT lấy mẫu 6 giờ một lần, nên 122 điểm là 30 ngày
       chứ không phải 122 ngày. */
    var ngay = Math.round((cuoi[0] - dau[0]) / 86400);

    host.innerHTML = s + nhanY.join("");
    $("#bdSo").textContent = usd(tongCuoi);
    $("#bdDoi").innerHTML = typeof doi === "number"
      ? '<span data-d="' + (doi >= 0 ? "up" : "down") + '">' + (doi >= 0 ? "+" : "") +
        (doi * 100).toFixed(1) + "% · " + ngay + " ngày qua</span>" : "";

    $("#bdChu").innerHTML =
      '<span><i style="background:' + MAU_TVS.native + '"></i>gốc bản địa</span>' +
      '<span><i style="background:' + MAU_TVS.canonical + '"></i>cầu chính thức</span>' +
      '<span><i style="background:' + MAU_TVS.external + '"></i>cầu bên ngoài</span>';
  }

  /* ── thẻ tổng bên phải ────────────────────────────── */
  function veTong() {
    var s = { native: 0, canonical: 0, external: 0 };
    P.forEach(function (p) {
      if (!p.chiaTvs) return;
      s.native += p.chiaTvs.native || 0;
      s.canonical += p.chiaTvs.canonical || 0;
      s.external += p.chiaTvs.external || 0;
    });
    var tong = s.native + s.canonical + s.external;

    $("#tongSo").textContent = usd(tong);
    $("#tongSos").innerHTML =
      [["native", "gốc bản địa"], ["canonical", "cầu chính thức"], ["external", "cầu bên ngoài"]]
        .map(function (k) {
          return '<div class="so-hang"><span><em style="background:' + MAU_TVS[k[0]] + '"></em>' +
            k[1] + "</span><b>" + usd(s[k[0]]) + "  ·  " +
            (tong ? Math.round((s[k[0]] / tong) * 100) : 0) + "%</b></div>";
        }).join("");

    var l2 = P.filter(function (p) { return p.loai !== "layer3"; })
      .reduce(function (a, p) { return a + (p.tvs || 0); }, 0);
    $("#tongGhi").innerHTML = esc(VI.ghiChuTong || "") +
      " Chỉ tính tầng 2 thì tổng là <b>" + usd(l2) + "</b>.";
  }

  /* ── bộ lọc ───────────────────────────────────────── */
  function loc() {
    var q = norm(state.q.trim());
    return P.filter(function (p) {
      if (state.tab !== "all" && (p.tab || "khac") !== state.tab) return false;
      if (state.thang !== "all" && (p.thang || "Not applicable") !== state.thang) return false;
      if (q) {
        var hay = norm([p.ten, p.dang, p.stack, p.me, p.thang,
          p.heCM && p.heCM.ten, (p.stacks || []).join(" ")].join(" "));
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    }).sort(function (a, b) {
      var v;
      if (state.sort === "ten") v = String(a.ten).localeCompare(String(b.ten));
      else if (state.sort === "thang") v = stageNum(a.thang) - stageNum(b.thang);
      else if (state.sort === "uops") v = (a.uops ? a.uops.sl : -1) - (b.uops ? b.uops.sl : -1);
      else v = (a.tvs || 0) - (b.tvs || 0);
      return state.desc ? -v : v;
    });
  }

  function logoHTML(p, cls) {
    if (p.logo) {
      return '<img src="' + LOGO + esc(p.logo) + '" alt="" loading="lazy" width="20" height="20">';
    }
    return '<span class="khonglogo">' + esc(String(p.ten || "?").trim().charAt(0).toUpperCase()) + "</span>";
  }

  function tenHTML(p) {
    return '<span class="ten">' + logoHTML(p) + "<b>" + esc(p.ten) + "</b>" +
      (p.loai === "layer3" ? '<span class="l3">' + esc(VI.nhan.layer3) + "</span>" : "") +
      (p.xemXet ? '<span class="xx">' + esc(VI.nhan.xemXet) + "</span>" : "") +
      (p.baoDong ? '<span class="bd0">' + esc(VI.nhan.baoDong) + "</span>" : "") +
      "</span>";
  }

  function thangHTML(p) {
    var g = tra("thang", p.thang || "Not applicable");
    return '<span class="thang" data-s="' + esc(stageNum(p.thang)) + '">' + esc(g.nhan) + "</span>";
  }

  /* ── bảng ─────────────────────────────────────────── */
  var COT = [
    { k: "rank", n: "#", cls: "l" },
    { k: "ten", n: "Thành phố", cls: "l", sort: 1 },
    { k: "ros", n: "Rủi ro", cls: "c" },
    { k: "hecm", n: "Hệ chứng minh", cls: "l" },
    { k: "thang", n: "Thang tự trị", cls: "l", sort: 1 },
    { k: "tvs", n: "Tài sản đang giữ", sort: 1 },
    { k: "uops", n: "Thao tác/giây 24h", sort: 1 }
  ];

  function veBang() {
    var rows = loc();
    var host = $("#bang");
    host.innerHTML = "";

    $("#dem").textContent = rows.length + " / " + P.length + " thành phố";

    if (!rows.length) {
      var e = el("p", "trong");
      e.textContent = "Không có thành phố nào khớp bộ lọc.";
      host.appendChild(e);
      return;
    }

    var t = el("table", "bang");
    var thead = el("thead"), tr = el("tr");
    COT.forEach(function (c) {
      var th = el("th", c.cls || "");
      th.textContent = c.n;
      if (c.sort) {
        th.classList.add("sortable");
        th.tabIndex = 0;
        if (state.sort === c.k) th.dataset.sorted = state.desc ? "desc" : "asc";
        var doi = function () {
          if (state.sort === c.k) state.desc = !state.desc;
          else { state.sort = c.k; state.desc = c.k !== "ten"; }
          veBang();
        };
        th.addEventListener("click", doi);
        th.addEventListener("keydown", function (ev) {
          if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); doi(); }
        });
      }
      tr.appendChild(th);
    });
    thead.appendChild(tr);
    t.appendChild(thead);

    var tb = el("tbody");
    rows.forEach(function (p, i) {
      var r = el("tr");
      r.tabIndex = 0;
      if (p.baoDong) r.dataset.baodong = "1";
      r.addEventListener("click", function () { moHoSo(p); });
      r.addEventListener("keydown", function (ev) { if (ev.key === "Enter") moHoSo(p); });

      var c1 = el("td", "l hang"); c1.textContent = i + 1; r.appendChild(c1);

      var c2 = el("td", "l"); c2.innerHTML = tenHTML(p); r.appendChild(c2);

      var c3 = el("td", "c");
      c3.innerHTML = '<span class="ros" title="' + esc(rosetteTitle(p.ruiRo || [])) + '">' +
        rosette(p.ruiRo || []) + "</span>";
      r.appendChild(c3);

      var c4 = el("td", "l hecm");
      if (p.heCM && p.heCM.loai) {
        c4.innerHTML = "<b>" + esc(tra("heCM", p.heCM.loai).nhan) + "</b>" +
          (p.heCM.ten ? "<i>" + esc(p.heCM.ten) + "</i>" : "");
      } else {
        c4.innerHTML = '<span class="khong">—</span>';
      }
      r.appendChild(c4);

      var c5 = el("td", "l"); c5.innerHTML = thangHTML(p); r.appendChild(c5);

      var c6 = el("td", "ts");
      var ch = p.chiaTvs, tot = p.tvs || 0;
      var bar = "";
      if (ch && tot > 0) {
        var w = function (v) { return ((v || 0) / tot * 100).toFixed(1) + "%"; };
        bar = '<span class="tsbar">' +
          '<span class="n" style="width:' + w(ch.native) + '"></span>' +
          '<span class="c" style="width:' + w(ch.canonical) + '"></span>' +
          '<span class="e" style="width:' + w(ch.external) + '"></span></span>' +
          '<div class="tsghi">' + Math.round(((ch.external || 0) + (ch.native || 0)) / tot * 100) +
          "% ngoài cầu chính thức</div>";
      }
      c6.innerHTML = "<b>" + usd(p.tvs) + "</b>" + pct(p.d7) + bar;
      r.appendChild(c6);

      var c7 = el("td", "uops");
      c7.innerHTML = p.uops
        ? "<b>" + p.uops.sl.toFixed(2) + "</b>" + pct(p.uops.doi)
        : '<span class="khong">' + esc(VI.nhan.khongUops) + "</span>";
      r.appendChild(c7);

      tb.appendChild(r);
    });
    t.appendChild(tb);
    host.appendChild(t);
  }

  /* ── hồ sơ chi tiết ───────────────────────────────── */
  function moHoSo(p) {
    var b = $("#hosoBody");
    b.innerHTML = "";

    $("#hosoTen").innerHTML = tenHTML(p);
    var g = tra("thang", p.thang || "Not applicable");
    $("#hosoTag").innerHTML = thangHTML(p) +
      '<span class="thang" data-s="-1">' + esc(tra("tab", p.tab || "khac").nhan) + "</span>" +
      '<span class="thang" data-s="-1">' + esc(tra("dang", p.dang || "Other").nhan) + "</span>";

    function sec(tieu, noi) {
      var s = el("div", "hs");
      s.innerHTML = '<div class="hs-h">' + esc(tieu) + "</div>" + noi;
      b.appendChild(s);
      return s;
    }

    /* mô tả gốc của L2BEAT */
    if (p.moTa) sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(p.moTa) + "</p>");

    /* thang tự trị + còn thiếu gì để lên thang sau */
    var thangHtml = '<p class="hs-p">' + esc(g.y || "") + "</p>" +
      (g.vn ? '<p class="hs-vn"><b>Với người gửi tiền:</b> ' + esc(g.vn) + "</p>" : "");
    if (p.thieu && p.thieu.dieuKien && p.thieu.dieuKien.length) {
      thangHtml += '<div class="hs-h" style="margin-top:14px">' +
        esc(VI.nhan.thangSau) + " (" + esc(p.thieu.thangSau || "") + ")</div>" +
        '<ul class="hs-thieu">' +
        p.thieu.dieuKien.map(function (d) { return "<li>" + esc(d) + "</li>"; }).join("") +
        "</ul>" +
        '<p class="hs-thin">Nguyên văn tiêu chí của L2BEAT — cố ý không dịch, vì đây là điều kiện kỹ thuật họ dùng để chấm.</p>';
    }
    sec("Thang tự trị", thangHtml);

    /* hệ chứng minh */
    if (p.heCM && p.heCM.loai) {
      var h = tra("heCM", p.heCM.loai);
      var gt = p.heCM.giaoThuc ? tra("giaoThuc", p.heCM.giaoThuc) : null;
      sec("Hệ chứng minh",
        '<p class="hs-p"><b>' + esc(h.nhan) + "</b>" +
        (p.heCM.ten ? " · " + esc(p.heCM.ten) : "") + "</p>" +
        (h.y ? '<p class="hs-p" style="margin-top:6px;color:var(--ink-2)">' + esc(h.y) + "</p>" : "") +
        (h.vn ? '<p class="hs-vn"><b>Với người gửi tiền:</b> ' + esc(h.vn) + "</p>" : "") +
        (gt ? '<p class="hs-thin"><b>Tranh chấp ' + esc(gt.nhan).toLowerCase() + ":</b> " + esc(gt.y || "") + "</p>" : ""));
    }

    /* tài sản */
    var chia = p.chiaTvs || {};
    sec("Tài sản đang giữ",
      '<div class="hs-so"><b>' + usd(p.tvs) + "</b>" +
      (typeof p.d7 === "number"
        ? '<i data-d="' + (p.d7 >= 0 ? "up" : "down") + '">' + (p.d7 >= 0 ? "+" : "") +
          (p.d7 * 100).toFixed(1) + "% trong 7 ngày</i>" : "") + "</div>" +
      '<div class="hs-chia">' +
        '<span><span><em style="background:' + MAU_TVS.native + '"></em>gốc bản địa</span><b>' + usd(chia.native) + "</b></span>" +
        '<span><span><em style="background:' + MAU_TVS.canonical + '"></em>cầu chính thức</span><b>' + usd(chia.canonical) + "</b></span>" +
        '<span><span><em style="background:' + MAU_TVS.external + '"></em>cầu bên ngoài</span><b>' + usd(chia.external) + "</b></span>" +
      "</div>" +
      (p.uops ? '<p class="hs-thin">Thao tác mỗi giây trong 24h qua: <b>' + p.uops.sl.toFixed(2) +
        "</b>" + (typeof p.uops.doi === "number"
          ? " (" + (p.uops.doi >= 0 ? "+" : "") + (p.uops.doi * 100).toFixed(1) + "% so với " +
            esc(p.uops.ky || "kỳ trước") + ")" : "") + "</p>" : ""));

    /* năm chiều rủi ro */
    var s3 = el("div", "hs");
    s3.innerHTML = '<div class="hs-h">Năm chiều rủi ro</div>' +
      '<div style="display:flex;align-items:center;gap:11px;margin-bottom:11px">' +
      '<span class="ros" style="width:44px;height:44px">' + rosette(p.ruiRo || [], 44) + "</span>" +
      '<span style="font-size:12px;color:var(--ink-3);line-height:1.5">' +
      "Mỗi múi là một chiều. Xanh là ổn, vàng cần lưu ý, đỏ đáng ngại.</span></div>";
    (p.ruiRo || []).forEach(function (r) {
      var c = tra("chieu", r.n), v = traGia(r.n, r.v);
      var row = el("div", "hs-rr");
      row.dataset.sent = r.s || "neutral";
      row.innerHTML =
        '<div class="rr-top"><span class="rr-n">' + esc(c.nhan) + "</span>" +
        '<span class="rr-v">' + esc(v.nhan) + (v.thieu ? " <em>chưa dịch</em>" : "") + "</span></div>" +
        (c.y ? '<p class="rr-q">' + esc(c.y) + "</p>" : "") +
        (v.y ? '<p class="rr-y">' + esc(v.y) + "</p>" : "") +
        (r.d ? '<details class="rr-goc"><summary>nguyên văn L2BEAT</summary><p>' + esc(r.d) + "</p></details>" : "");
      s3.appendChild(row);
    });
    b.appendChild(s3);

    /* bản vẽ xây dựng */
    var st = (p.stacks && p.stacks.length) ? p.stacks : (p.stack ? [p.stack] : []);
    if (st.length) {
      sec("Bản vẽ xây dựng", st.map(function (x) {
        var v = tra("stack", x);
        return '<p class="hs-p"><b>' + esc(x) + "</b> — " + esc(v.nhan) + "</p>";
      }).join(""));
    }

    sec("Nguồn",
      '<p class="hs-p"><a href="https://l2beat.com/scaling/projects/' + encodeURIComponent(p.slug) +
      '" target="_blank" rel="noopener">Hồ sơ đầy đủ trên L2BEAT ↗</a></p>' +
      '<p class="hs-thin">Đô Sát Viện dịch và diễn giải, không tự chấm điểm. Mọi đánh giá rủi ro là của L2BEAT.</p>');

    $("#hoso").dataset.open = "1";
    $("#scrim").dataset.open = "1";
    $("#hosoDong").focus();
  }

  function dongHoSo() {
    $("#hoso").dataset.open = "0";
    $("#scrim").dataset.open = "0";
  }

  /* ── tab ──────────────────────────────────────────── */
  function veTab() {
    var host = $("#tabs");
    host.innerHTML = "";
    var thuTu = ["rollup", "validium", "khac"];
    thuTu.forEach(function (k) {
      var n = (D.demTab && D.demTab[k]) || P.filter(function (p) { return p.tab === k; }).length;
      var b = el("button", "tab");
      b.type = "button";
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(state.tab === k));
      b.innerHTML = esc(tra("tab", k).nhan) + '<span class="n">' + n + "</span>";
      b.addEventListener("click", function () {
        state.tab = k; veTab(); veGiaiThich(); veChip(); veBang();
      });
      host.appendChild(b);
    });
  }

  function veGiaiThich() {
    var g = tra("tab", state.tab);
    $("#giaithich").innerHTML = "<b>" + esc(g.nhan) + "</b> — " + esc(g.y || "") +
      (g.vn ? '<span class="vn">' + esc(g.vn) + "</span>" : "");
  }

  /* ── chip lọc thang ───────────────────────────────── */
  function veChip() {
    var trongTab = P.filter(function (p) {
      return state.tab === "all" || (p.tab || "khac") === state.tab;
    });
    var counts = trongTab.reduce(function (m, p) {
      var k = p.thang || "Not applicable"; m[k] = (m[k] || 0) + 1; return m;
    }, {});

    var wrap = $("#chipThang");
    wrap.innerHTML = "";

    var all = el("button", "chip");
    all.type = "button";
    all.textContent = "Tất cả";
    all.setAttribute("aria-pressed", String(state.thang === "all"));
    all.addEventListener("click", function () { state.thang = "all"; veChip(); veBang(); });
    wrap.appendChild(all);

    ["Stage 2", "Stage 1", "Stage 0", "Not applicable"].forEach(function (k) {
      if (!counts[k]) return;
      var b = el("button", "chip");
      b.type = "button";
      b.innerHTML = esc(tra("thang", k).nhan) + '<span class="n">' + counts[k] + "</span>";
      b.setAttribute("aria-pressed", String(state.thang === k));
      b.addEventListener("click", function () { state.thang = k; veChip(); veBang(); });
      wrap.appendChild(b);
    });

    /* thang đang chọn có thể không tồn tại trong tab mới */
    if (state.thang !== "all" && !counts[state.thang]) state.thang = "all";
  }

  /* ── chú giải cuối trang ──────────────────────────── */
  function veChuGiai() {
    var host = $("#chugiai");
    var nhom = [
      ["Ba nhóm của L2BEAT", "tab", ["rollup", "validium", "khac"]],
      ["Thang tự trị", "thang", ["Stage 2", "Stage 1", "Stage 0", "Not applicable"]],
      ["Hệ chứng minh", "heCM", ["Optimistic", "Validity"]],
      ["Năm chiều rủi ro", "chieu", ["Sequencer Failure", "State Validation", "Data Availability", "Exit Window", "Proposer Failure"]]
    ];
    nhom.forEach(function (n) {
      var box = el("div", "cg-nhom");
      box.innerHTML = "<h3>" + esc(n[0]) + "</h3>";
      n[2].forEach(function (k) {
        var g = tra(n[1], k);
        var d = el("div", "cg-muc");
        d.innerHTML = "<b>" + esc(g.nhan) + '</b><span class="goc">' + esc(k) + "</span>" +
          (g.y ? "<p>" + esc(g.y) + "</p>" : "") +
          (g.vn ? '<p class="vn">' + esc(g.vn) + "</p>" : "");
        box.appendChild(d);
      });
      host.appendChild(box);
    });
  }

  /* ── thanh bên trên di động ───────────────────────── */
  function ganBen() {
    var ben = $("#ben"), nut = $("#benMo");
    if (!ben || !nut) return;
    nut.addEventListener("click", function () {
      ben.dataset.mo = ben.dataset.mo === "1" ? "0" : "1";
    });
    ben.addEventListener("click", function (e) {
      if (e.target.closest("a")) ben.dataset.mo = "0";
    });
    document.addEventListener("click", function (e) {
      if (window.innerWidth > 900) return;
      if (ben.dataset.mo !== "1") return;
      if (ben.contains(e.target) || nut.contains(e.target)) return;
      ben.dataset.mo = "0";
    });
  }

  /* ── khởi động ────────────────────────────────────── */
  function boot() {
    $("#ngay").textContent = "bản chụp " + (D.date || "—");
    $("#benSo").textContent = P.length;

    $("#q").addEventListener("input", function (e) { state.q = e.target.value; veBang(); });
    $("#hosoDong").addEventListener("click", dongHoSo);
    $("#scrim").addEventListener("click", dongHoSo);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") dongHoSo();
    });

    /* logo hỏng thì thay bằng chữ cái đầu, đừng để ô vỡ ảnh */
    document.addEventListener("error", function (e) {
      var t = e.target;
      if (t && t.tagName === "IMG" && t.parentNode && t.parentNode.classList.contains("ten")) {
        var s = document.createElement("span");
        s.className = "khonglogo";
        s.textContent = (t.parentNode.querySelector("b") || {}).textContent
          ? t.parentNode.querySelector("b").textContent.trim().charAt(0).toUpperCase() : "?";
        t.parentNode.replaceChild(s, t);
      }
    }, true);

    veBieuDo();
    veTong();
    veTab();
    veGiaiThich();
    veChip();
    veBang();
    veChuGiai();
    ganBen();

    if (!D.coSSR) {
      var c = $("#canhBao");
      if (c) {
        c.hidden = false;
        c.textContent = "Lần cập nhật gần nhất không đọc được dữ liệu trang L2BEAT — " +
          "logo, nhóm, hệ chứng minh và thao tác/giây đang lấy từ bản trước.";
      }
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
