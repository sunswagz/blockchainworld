/* ═══════════════════════════════════════════════════════
   ĐÔ SÁT VIỆN — bản Việt hoá của L2BEAT.

   Dữ liệu: window.DSV_DATA          (chỉ mục chung, tự sinh)
            window.DSV_V["<mã>"]     (từng mục, NẠP THEO YÊU CẦU)
   Chú giải: window.DSV_VI           (bản dịch, sửa tay được)

   Bố cục bám theo l2beat.com; lời diễn giải theo lối Kinh Thành:
   mỗi nhãn kỹ thuật đi kèm một câu "với người gửi tiền thì sao".

   ── ĐỊNH TUYẾN ────────────────────────────────────────
   Dùng hash (#/rui-ro) chứ không phải History API. Trang này
   còn được pin lên IPFS, mà gateway IPFS không có server để
   rewrite URL — mọi kiểu định tuyến khác đều vỡ ở đó.

   ── NẠP THEO YÊU CẦU ──────────────────────────────────
   Gộp cả 21 mục vào một file là ~1 MB. Mỗi mục nằm ở
   assets/js/v/<mã>.js và chỉ được chèn thẻ <script> khi người
   dùng bấm vào mục đó. Đã nạp rồi thì không nạp lại.

   Nhãn nào L2BEAT thêm mới mà chú giải chưa có thì hiện nguyên
   bản tiếng Anh kèm dấu "chưa dịch" — không bịa nghĩa.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.DSV_DATA, VI = window.DSV_VI;
  if (!D || !VI) return;

  var P = D.duAn || [];
  var LOGO = "assets/logos/";
  var BY = {};
  P.forEach(function (p) { BY[p.id] = p; });

  var MAU = { good: "#3DBB69", warning: "#F2B94A", bad: "#F05252", neutral: "#B4B5BC" };
  var MAU_TVS = { native: "#FF46A2", canonical: "#8B7FE8", external: "#F5C23E" };

  var state = { muc: "tong-quan", q: "", tab: null, thang: "all", sort: null, desc: true };

  /* ── tiện ích ─────────────────────────────────────── */
  function $(s) { return document.querySelector(s); }
  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function norm(s) {
    /* dấu tổ hợp viết dạng escape, KHÔNG viết thẳng vào regex: chúng
       vô hình trong trình soạn thảo và hay bị công cụ chuẩn hoá lại. */
    return String(s).toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "").replace(/\u0111/g, "d");
  }
  function usd(v) {
    if (v == null || isNaN(v)) return "—";
    if (v >= 1e9) return "$" + (v / 1e9).toFixed(2) + "b";
    if (v >= 1e6) return "$" + Math.round(v / 1e6) + "m";
    if (v >= 1e3) return "$" + Math.round(v / 1e3) + "k";
    return "$" + Math.round(v);
  }
  function byte(v) {
    if (v == null || isNaN(v)) return "—";
    var u = ["B", "KB", "MB", "GB", "TB"], i = 0;
    while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
    return (i ? v.toFixed(1) : Math.round(v)) + " " + u[i];
  }
  function giay(s) {
    if (s == null || isNaN(s)) return "—";
    if (s < 60) return Math.round(s) + "s";
    if (s < 3600) return Math.floor(s / 60) + "m " + Math.round(s % 60) + "s";
    if (s < 86400) return Math.floor(s / 3600) + "h " + Math.round((s % 3600) / 60) + "m";
    return (s / 86400).toFixed(1) + " ngày";
  }
  function num(v, d) {
    if (v == null || isNaN(v)) return "—";
    return Number(v).toLocaleString("vi-VN", { maximumFractionDigits: d == null ? 2 : d });
  }
  function pct(v, s) {
    if (typeof v !== "number" || isNaN(v)) return "";
    return '<i data-d="' + (v >= 0 ? "up" : "down") + '">' +
      (v >= 0 ? "+" : "") + (v * 100).toFixed(1) + "%" + (s || "") + "</i>";
  }

  function tra(nhom, key) {
    var g = VI[nhom] && VI[nhom][key];
    if (!g) return { nhan: key == null ? "—" : String(key), y: null, vn: null, thieu: key != null };
    if (typeof g === "string") return { nhan: g, y: null, vn: null };
    return g;
  }
  /* Cùng một chuỗi mang nghĩa khác nhau tuỳ chiều ("None" ở Exit Window
     ≠ ở State Validation), nên tra bảng riêng của chiều trước. */
  function traGia(chieu, giaTri) {
    var o = VI.giaTheoChieu && VI.giaTheoChieu[chieu] && VI.giaTheoChieu[chieu][giaTri];
    return o || tra("gia", giaTri);
  }
  function stageNum(s) {
    if (!s) return -1;
    return s.indexOf("Stage") === 0 ? parseInt(s.slice(-1), 10) : -1;
  }

  /* ── mảnh dùng lại ────────────────────────────────── */
  function logoHTML(logo, ten) {
    if (logo) return '<img src="' + LOGO + esc(logo) + '" alt="" loading="lazy" width="20" height="20">';
    return '<span class="khonglogo">' + esc(String(ten || "?").trim().charAt(0).toUpperCase()) + "</span>";
  }
  function tenHTML(o) {
    return '<span class="ten">' + logoHTML(o.logo, o.ten) + "<b>" + esc(o.ten) + "</b>" +
      (o.ten2 ? '<i class="ten2">' + esc(o.ten2) + "</i>" : "") +
      (o.l3 || o.loai === "layer3" ? '<span class="l3">' + esc(VI.nhan.layer3) + "</span>" : "") +
      (o.xemXet ? '<span class="xx">' + esc(VI.nhan.xemXet) + "</span>" : "") +
      (o.baoDong ? '<span class="bd0">' + esc(VI.nhan.baoDong) + "</span>" : "") +
      "</span>";
  }
  function thangHTML(thang) {
    return '<span class="thang" data-s="' + esc(stageNum(thang)) + '">' +
      esc(tra("thang", thang || "Not applicable").nhan) + "</span>";
  }

  /* ── rosette 5 cánh ───────────────────────────────── */
  function rosette(ruiRo, cao) {
    var r = (cao || 24) / 2, n = Math.max(ruiRo.length, 5), buoc = (Math.PI * 2) / n;
    var s = '<svg viewBox="0 0 ' + (r * 2) + " " + (r * 2) + '" aria-hidden="true">';
    for (var i = 0; i < n; i++) {
      var rr = ruiRo[i];
      var mau = rr ? (MAU[rr.s] || MAU.neutral) : "#E4E5EA";
      var a0 = -Math.PI / 2 + i * buoc, a1 = a0 + buoc;
      s += '<path d="M' + r.toFixed(2) + " " + r.toFixed(2) +
        "L" + (r + r * Math.cos(a0)).toFixed(2) + " " + (r + r * Math.sin(a0)).toFixed(2) +
        "A" + r.toFixed(2) + " " + r.toFixed(2) + " 0 0 1 " +
        (r + r * Math.cos(a1)).toFixed(2) + " " + (r + r * Math.sin(a1)).toFixed(2) +
        'Z" fill="' + mau + '" stroke="#fff" stroke-width="1"/>';
    }
    return s + "</svg>";
  }
  function rosetteO(ruiRo, cao) {
    if (!ruiRo || !ruiRo.length) return "";
    var tip = ruiRo.map(function (r) {
      return tra("chieu", r.n).nhan + ": " + traGia(r.n, r.v).nhan;
    }).join("\n");
    return '<span class="ros"' + (cao ? ' style="width:' + cao + "px;height:" + cao + 'px"' : "") +
      ' title="' + esc(tip) + '">' + rosette(ruiRo, cao) + "</span>";
  }

  /* Ô rủi ro trong bảng: giá trị đã dịch + màu theo cảm quan.
     `tho` = ô chứa DỮ LIỆU TỰ DO chứ không phải nhãn liệt kê
     ("3466 sequencers", "1m 12s", tên dự án như EigenDA). Ở đó vẫn
     tra bảng để dịch nếu có, nhưng KHÔNG đóng dấu "chưa dịch" —
     dấu đó chỉ có nghĩa khi L2BEAT thêm một nhãn mới mà mình chưa
     kịp dịch, còn đóng lên một con số thì chỉ gây hoang mang. */
  function oRuiRo(chieu, x, tho) {
    if (!x || x.v == null) return '<span class="mo">—</span>';
    var g = traGia(chieu, x.v);
    var laSo = /\d/.test(String(x.v));   /* xem ghi chú ở dauThieu() */
    var im = tho || laSo;
    var nhan = (im && g.thieu) ? String(x.v) : g.nhan;
    return '<span class="rrO" data-s="' + esc(x.s || "neutral") + '" title="' + esc(x.v) + '">' +
      esc(nhan) + (g.thieu && !im ? ' <em>chưa dịch</em>' : "") + "</span>" +
      (x.v2 ? '<i class="rr2">' + esc(x.v2) + "</i>" : "");
  }

  /* Vì sao "có chữ số thì không đóng dấu chưa dịch":
     Nhãn liệt kê của L2BEAT không bao giờ chứa số ("None",
     "Self sequence", "Enshrined"). Thứ có số luôn là số đo —
     "9d", "1/2", "3466 sequencers", "200 K AZTEC". Đóng dấu
     "chưa dịch" lên một con số chỉ làm người đọc tưởng trang
     bị lỗi. Ngoại lệ duy nhất là "Fraud proofs (1R, ZK)", nhưng
     nhãn đó đã dịch rồi nên không bao giờ chạm nhánh này. */

  /* ══════════════════════════════════════════════════
     BỘ MÁY BẢNG DÙNG CHUNG
     cot: [{ n, cls, sort, ve(hang, i) }]
     ══════════════════════════════════════════════════ */
  function veBang(host, hang, cot, trong) {
    host.innerHTML = "";
    if (!hang.length) {
      var e = el("p", "trong");
      e.textContent = trong || "Không có mục nào khớp bộ lọc.";
      host.appendChild(e);
      return;
    }
    var t = el("table", "bang"), thead = el("thead"), tr = el("tr");
    cot.forEach(function (c) {
      var th = el("th", c.cls || "");
      th.textContent = c.n;
      if (c.sort) {
        th.classList.add("sortable");
        th.tabIndex = 0;
        if (state.sort === c.sort) th.dataset.sorted = state.desc ? "desc" : "asc";
        var doi = function () {
          if (state.sort === c.sort) state.desc = !state.desc;
          else { state.sort = c.sort; state.desc = true; }
          ve();
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
    hang.forEach(function (h, i) {
      var r = el("tr");
      if (h.baoDong) r.dataset.baodong = "1";
      if (h.__mo) {
        r.tabIndex = 0;
        r.style.cursor = "pointer";
        r.addEventListener("click", function () { h.__mo(); });
        r.addEventListener("keydown", function (ev) { if (ev.key === "Enter") h.__mo(); });
      }
      cot.forEach(function (c) {
        var td = el("td", c.cls || "");
        td.innerHTML = c.ve(h, i);
        r.appendChild(td);
      });
      tb.appendChild(r);
    });
    t.appendChild(tb);
    host.appendChild(t);
  }

  /* cột "#" và "tên" dùng ở hầu hết bảng */
  var COT_STT = { n: "#", cls: "l hang", ve: function (h, i) { return String(i + 1); } };
  function cotTen(nhan) {
    return { n: nhan || "Thành phố", cls: "l", sort: "ten", ve: function (h) { return tenHTML(h); } };
  }

  /* sắp xếp chung */
  function sapXep(arr, mac) {
    var k = state.sort || mac;
    var d = state.desc;
    return arr.slice().sort(function (a, b) {
      var v;
      if (k === "ten") v = String(a.ten || "").localeCompare(String(b.ten || ""));
      else if (k === "thang") v = stageNum(a.thang) - stageNum(b.thang);
      else v = (Number(a[k]) || 0) - (Number(b[k]) || 0);
      return d ? -v : v;
    });
  }

  function locQ(arr, truong) {
    var q = norm(state.q.trim());
    if (!q) return arr;
    return arr.filter(function (x) {
      return norm((truong || ["ten"]).map(function (k) { return x[k]; }).join(" ")).indexOf(q) !== -1;
    });
  }

  /* ══════════════════════════════════════════════════
     CÂY THANH BÊN
     ══════════════════════════════════════════════════ */
  var CAY = [
    { nhom: "Lớp 2", muc: [
      "tong-quan",
      { nhom2: "Phân tích rủi ro", muc: ["rui-ro", "kiem-chung", "du-lieu", "xep-thu-tu"] },
      "hoat-dong", "do-song", "luu-tru"
    ] },
    { nhom: "Liên thông", muc: ["lt-tong-quan", "lt-khung-token", "lt-cau-y-dinh"] },
    { nhom: "Quyền riêng tư", muc: ["rieng-tu"] },
    { nhom: "Dữ liệu sẵn có", muc: ["dl-tong-quan", "dl-rui-ro", "dl-thong-luong", "dl-do-song", "dl-luu-tru"] },
    { nhom: "Bằng chứng", muc: ["zk"] },
    { nhom: "Hệ sinh thái", muc: ["st-arbitrum-orbit", "st-elastic", "st-superchain", "st-agglayer"] },
    { nhom: "Tra cứu", muc: ["tu-dien"] }
  ];

  function demMuc(ma) {
    if (ma === "tong-quan") return P.length;
    if (ma === "tu-dien") return (D.tuDien || []).length;
    var m = (D.dsMuc || []).filter(function (x) { return x.ma === ma; })[0];
    return m && m.so != null ? m.so : null;
  }

  function veBen() {
    var host = $("#benMuc");
    host.innerHTML = "";
    CAY.forEach(function (g) {
      var lab = el("div", "blab");
      lab.textContent = g.nhom;
      host.appendChild(lab);
      g.muc.forEach(function (m) {
        if (typeof m === "string") { host.appendChild(dongBen(m)); return; }
        var lab2 = el("div", "blab2");
        lab2.textContent = m.nhom2;
        host.appendChild(lab2);
        var box = el("div", "bcon");
        m.muc.forEach(function (x) { box.appendChild(dongBen(x)); });
        host.appendChild(box);
      });
    });
  }
  function dongBen(ma) {
    var t = VI.muc[ma] || { ten: ma };
    var a = el("a", "bmuc");
    a.href = "#/" + ma;
    a.title = t.y || t.ten;
    if (state.muc === ma) a.setAttribute("aria-current", "page");
    var n = demMuc(ma);
    a.innerHTML = "<span>" + esc(t.ten) + "</span>" +
      (n != null ? '<span class="bn">' + n + "</span>" : "");
    return a;
  }

  /* ══════════════════════════════════════════════════
     NẠP MỤC THEO YÊU CẦU
     ══════════════════════════════════════════════════ */
  var dangNap = {};
  function nap(ma, xong) {
    window.DSV_V = window.DSV_V || {};
    if (window.DSV_V[ma]) return xong(null);
    if (dangNap[ma]) { dangNap[ma].push(xong); return; }
    dangNap[ma] = [xong];
    var s = document.createElement("script");
    s.src = "assets/js/v/" + ma + ".js";
    s.onload = function () {
      var ds = dangNap[ma]; delete dangNap[ma];
      ds.forEach(function (f) { f(window.DSV_V[ma] ? null : new Error("file nạp được nhưng không có dữ liệu")); });
    };
    s.onerror = function () {
      var ds = dangNap[ma]; delete dangNap[ma];
      ds.forEach(function (f) { f(new Error("không tải được assets/js/v/" + ma + ".js")); });
    };
    document.head.appendChild(s);
  }

  /* ══════════════════════════════════════════════════
     KHUNG MỘT MÀN HÌNH
     ══════════════════════════════════════════════════ */
  function khung(o) {
    /* o: { tieu, dan, tabs, loc, than } */
    var h = "";
    if (o.dan) h += '<p class="giaithich">' + o.dan + "</p>";
    if (o.tabs) h += '<div class="tabs" id="tabs" role="tablist"></div>';
    h += '<section class="khoi">';
    if (o.loc !== false) {
      h += '<div class="loc"><span class="loc-lab" id="locLab"></span>' +
        '<div class="chips" id="chips"></div><span class="dem" id="dem"></span></div>';
    }
    h += '<div class="bangwrap" id="bang"></div></section>';
    return h;
  }

  function dan(ma) {
    var t = VI.muc[ma];
    if (!t) return "";
    return "<b>" + esc(t.ten) + "</b>" + (t.y ? " — " + esc(t.y) : "");
  }

  function veTabs(ds, chon, doi) {
    var host = $("#tabs");
    if (!host) return;
    host.innerHTML = "";
    ds.forEach(function (t) {
      var b = el("button", "tab");
      b.type = "button";
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(chon === t.ma));
      b.innerHTML = esc(t.ten) + '<span class="n">' + t.so + "</span>";
      b.addEventListener("click", function () { doi(t.ma); });
      host.appendChild(b);
    });
  }

  function demHTML(n, tong, dv) {
    var e = $("#dem");
    if (e) e.textContent = n + (tong != null && tong !== n ? " / " + tong : "") + " " + (dv || "mục");
  }

  /* ══════════════════════════════════════════════════
     HỒ SƠ (ngăn kéo phải)
     ══════════════════════════════════════════════════ */
  function moHoSo(tieu, tag, than) {
    $("#hosoTen").innerHTML = tieu;
    $("#hosoTag").innerHTML = tag || "";
    $("#hosoBody").innerHTML = than;
    $("#hoso").dataset.open = "1";
    $("#scrim").dataset.open = "1";
    $("#hosoDong").focus();
  }
  function dongHoSo() {
    $("#hoso").dataset.open = "0";
    $("#scrim").dataset.open = "0";
  }
  function sec(h, noi) { return '<div class="hs"><div class="hs-h">' + esc(h) + "</div>" + noi + "</div>"; }
  function dongRuiRo(ruiRo) {
    return (ruiRo || []).map(function (r) {
      var c = tra("chieu", r.n), v = traGia(r.n, r.v);
      return '<div class="hs-rr" data-sent="' + esc(r.s || "neutral") + '">' +
        '<div class="rr-top"><span class="rr-n">' + esc(c.nhan) + "</span>" +
        '<span class="rr-v">' + esc(v.nhan) + (v.thieu ? " <em>chưa dịch</em>" : "") + "</span></div>" +
        (c.y ? '<p class="rr-q">' + esc(c.y) + "</p>" : "") +
        (v.y ? '<p class="rr-y">' + esc(v.y) + "</p>" : "") +
        (r.d ? '<details class="rr-goc"><summary>nguyên văn L2BEAT</summary><p>' + esc(r.d) + "</p></details>" : "") +
        "</div>";
    }).join("");
  }

  /* ══════════════════════════════════════════════════
     MÀN HÌNH 1 — TỔNG QUAN
     ══════════════════════════════════════════════════ */
  function mhTongQuan(host) {
    host.innerHTML =
      '<section class="tren">' +
        '<div class="the"><div class="the-dinh"><h2>Tài sản đang giữ</h2>' +
          '<span class="the-so" id="bdSo">—</span></div>' +
          '<div class="the-doi" id="bdDoi"></div><div class="bd" id="bd"></div>' +
          '<div class="bd-chu" id="bdChu"></div></div>' +
        '<div class="the"><div class="the-dinh"><h2>Tiền vào bằng đường nào</h2>' +
          '<span class="the-so" id="tongSo">—</span></div>' +
          '<div class="sos" id="tongSos"></div><p class="the-ghi" id="tongGhi"></p></div>' +
      "</section>" + khung({ tabs: true, dan: dan("tong-quan") });

    veBieuDo(); veTongThe();
    if (!state.tab) state.tab = "rollup";

    function lai() {
      veTabs(["rollup", "validium", "khac"].map(function (k) {
        return { ma: k, ten: tra("tab", k).nhan, so: (D.demTab && D.demTab[k]) || 0 };
      }), state.tab, function (k) { state.tab = k; state.thang = "all"; ve(); });

      $("#locLab").textContent = "Thang tự trị";
      var g = tra("tab", state.tab);
      $(".giaithich").innerHTML = "<b>" + esc(g.nhan) + "</b> — " + esc(g.y || "") +
        (g.vn ? '<span class="vn">' + esc(g.vn) + "</span>" : "");

      var trongTab = P.filter(function (p) { return p.tab === state.tab; });
      veChipThang(trongTab, function () { ve(); });

      var hang = sapXep(locQ(trongTab.filter(function (p) {
        return state.thang === "all" || (p.thang || "Not applicable") === state.thang;
      }), ["ten", "dang", "stack", "me"]), "tvs");

      hang.forEach(function (p) { p.__mo = function () { hoSoDuAn(p); }; });
      demHTML(hang.length, P.length, "thành phố");

      veBang($("#bang"), hang, [
        COT_STT, cotTen(),
        { n: "Rủi ro", cls: "c", ve: function (h) { return rosetteO(h.ruiRo); } },
        { n: "Hệ chứng minh", cls: "l hecm", ve: function (h) {
          if (!h.heCM || !h.heCM.loai) return '<span class="khong">—</span>';
          return "<b>" + esc(tra("heCM", h.heCM.loai).nhan) + "</b>" +
            (h.heCM.ten ? "<i>" + esc(h.heCM.ten) + "</i>" : "");
        } },
        { n: "Thang tự trị", cls: "l", sort: "thang", ve: function (h) { return thangHTML(h.thang); } },
        { n: "Tài sản đang giữ", sort: "tvs", cls: "ts", ve: function (h) {
          var ch = h.chiaTvs, tot = h.tvs || 0, bar = "";
          if (ch && tot > 0) {
            var w = function (v) { return ((v || 0) / tot * 100).toFixed(1) + "%"; };
            bar = '<span class="tsbar"><span class="n" style="width:' + w(ch.native) +
              '"></span><span class="c" style="width:' + w(ch.canonical) +
              '"></span><span class="e" style="width:' + w(ch.external) + '"></span></span>' +
              '<div class="tsghi">' + Math.round(((ch.external || 0) + (ch.native || 0)) / tot * 100) +
              "% ngoài cầu chính thức</div>";
          }
          return "<b>" + usd(h.tvs) + "</b>" + pct(h.d7) + bar;
        } },
        { n: "Thao tác/giây 24h", cls: "uops", sort: "uopsSo", ve: function (h) {
          return h.uops ? "<b>" + num(h.uops.sl) + "</b>" + pct(h.uops.doi)
            : '<span class="khong">' + esc(VI.nhan.khongUops) + "</span>";
        } }
      ]);
    }
    P.forEach(function (p) { p.uopsSo = p.uops ? p.uops.sl : -1; });
    lai();
  }

  function veChipThang(trongTab, doi) {
    var counts = trongTab.reduce(function (m, p) {
      var k = p.thang || "Not applicable"; m[k] = (m[k] || 0) + 1; return m;
    }, {});
    var wrap = $("#chips");
    if (!wrap) return;
    wrap.innerHTML = "";
    var all = el("button", "chip");
    all.type = "button";
    all.textContent = "Tất cả";
    all.setAttribute("aria-pressed", String(state.thang === "all"));
    all.addEventListener("click", function () { state.thang = "all"; doi(); });
    wrap.appendChild(all);
    ["Stage 2", "Stage 1", "Stage 0", "Not applicable"].forEach(function (k) {
      if (!counts[k]) return;
      var b = el("button", "chip");
      b.type = "button";
      b.innerHTML = esc(tra("thang", k).nhan) + '<span class="n">' + counts[k] + "</span>";
      b.setAttribute("aria-pressed", String(state.thang === k));
      b.addEventListener("click", function () { state.thang = k; doi(); });
      wrap.appendChild(b);
    });
    if (state.thang !== "all" && !counts[state.thang]) state.thang = "all";
  }

  function hoSoDuAn(p) {
    var g = tra("thang", p.thang || "Not applicable");
    var chia = p.chiaTvs || {};
    var h = "";
    if (p.moTa) h += sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(p.moTa) + "</p>");
    var tq = '<p class="hs-p">' + esc(g.y || "") + "</p>" +
      (g.vn ? '<p class="hs-vn"><b>Với người gửi tiền:</b> ' + esc(g.vn) + "</p>" : "");
    if (p.thieu && p.thieu.dieuKien && p.thieu.dieuKien.length) {
      tq += '<div class="hs-h" style="margin-top:14px">' + esc(VI.nhan.thangSau) +
        " (" + esc(p.thieu.thangSau || "") + ")</div><ul class=\"hs-thieu\">" +
        p.thieu.dieuKien.map(function (d) { return "<li>" + esc(d) + "</li>"; }).join("") +
        '</ul><p class="hs-thin">Nguyên văn tiêu chí của L2BEAT — cố ý không dịch, vì đây là điều kiện kỹ thuật họ dùng để chấm.</p>';
    }
    h += sec("Thang tự trị", tq);
    if (p.heCM && p.heCM.loai) {
      var hc = tra("heCM", p.heCM.loai);
      var gt = p.heCM.giaoThuc ? tra("giaoThuc", p.heCM.giaoThuc) : null;
      h += sec("Hệ chứng minh",
        '<p class="hs-p"><b>' + esc(hc.nhan) + "</b>" + (p.heCM.ten ? " · " + esc(p.heCM.ten) : "") + "</p>" +
        (hc.y ? '<p class="hs-p" style="margin-top:6px;color:var(--ink-2)">' + esc(hc.y) + "</p>" : "") +
        (hc.vn ? '<p class="hs-vn"><b>Với người gửi tiền:</b> ' + esc(hc.vn) + "</p>" : "") +
        (gt ? '<p class="hs-thin"><b>Tranh chấp ' + esc(gt.nhan).toLowerCase() + ":</b> " + esc(gt.y || "") + "</p>" : ""));
    }
    h += sec("Tài sản đang giữ",
      '<div class="hs-so"><b>' + usd(p.tvs) + "</b>" +
      (typeof p.d7 === "number" ? '<i data-d="' + (p.d7 >= 0 ? "up" : "down") + '">' +
        (p.d7 >= 0 ? "+" : "") + (p.d7 * 100).toFixed(1) + "% trong 7 ngày</i>" : "") + "</div>" +
      '<div class="hs-chia">' +
      [["native", "gốc bản địa"], ["canonical", "cầu chính thức"], ["external", "cầu bên ngoài"]].map(function (k) {
        return '<span><span><em style="background:' + MAU_TVS[k[0]] + '"></em>' + k[1] +
          "</span><b>" + usd(chia[k[0]]) + "</b></span>";
      }).join("") + "</div>" +
      (p.uops ? '<p class="hs-thin">Thao tác mỗi giây trong 24h qua: <b>' + num(p.uops.sl) + "</b></p>" : ""));
    h += sec("Năm chiều rủi ro",
      '<div style="display:flex;align-items:center;gap:11px;margin-bottom:11px">' +
      rosetteO(p.ruiRo, 44) +
      '<span style="font-size:12px;color:var(--ink-3);line-height:1.5">Mỗi múi là một chiều. Xanh là ổn, vàng cần lưu ý, đỏ đáng ngại.</span></div>' +
      dongRuiRo(p.ruiRo));
    var st = (p.stacks && p.stacks.length) ? p.stacks : (p.stack ? [p.stack] : []);
    if (st.length) {
      h += sec("Bản vẽ xây dựng", st.map(function (x) {
        return '<p class="hs-p"><b>' + esc(x) + "</b> — " + esc(tra("stack", x).nhan) + "</p>";
      }).join(""));
    }
    h += sec("Nguồn",
      '<p class="hs-p"><a href="https://l2beat.com/scaling/projects/' + encodeURIComponent(p.slug) +
      '" target="_blank" rel="noopener">Hồ sơ đầy đủ trên L2BEAT ↗</a></p>' +
      '<p class="hs-thin">Đô Sát Viện dịch và diễn giải, không tự chấm điểm. Mọi đánh giá rủi ro là của L2BEAT.</p>');
    moHoSo(tenHTML(p), thangHTML(p.thang) +
      '<span class="thang" data-s="-1">' + esc(tra("tab", p.tab || "khac").nhan) + "</span>", h);
  }

  /* ── biểu đồ tài sản ──────────────────────────────── */
  function veBieuDo() {
    var host = $("#bd");
    if (!host) return;
    var B = D.bieuDo;
    if (!B || !B.diem || !B.diem.length) { host.innerHTML = '<p class="the-ghi">Chưa có dữ liệu biểu đồ.</p>'; return; }
    var cot = B.cot || [];
    var iN = cot.indexOf("native"), iC = cot.indexOf("canonical"), iE = cot.indexOf("external");
    if (iN < 0 || iC < 0 || iE < 0) { iN = 1; iC = 2; iE = 3; }
    var d = B.diem, W = 600, H = 170, PB = 18;
    var max = Math.max.apply(null, d.map(function (p) {
      return (p[iN] || 0) + (p[iC] || 0) + (p[iE] || 0);
    })) * 1.06 || 1;
    var x = function (i) { return (i / (d.length - 1)) * W; };
    var y = function (v) { return H - PB - (v / max) * (H - PB); };
    var duoi = d.map(function () { return 0; });
    var s = '<svg viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" role="img" aria-label="Tài sản đang giữ theo thời gian">';
    [{ k: iN, mau: MAU_TVS.native }, { k: iC, mau: MAU_TVS.canonical }, { k: iE, mau: MAU_TVS.external }]
      .forEach(function (L) {
        var tren = d.map(function (p, i) { return duoi[i] + (p[L.k] || 0); });
        var path = "M0 " + y(duoi[0]).toFixed(1);
        for (var i = 0; i < d.length; i++) path += "L" + x(i).toFixed(1) + " " + y(tren[i]).toFixed(1);
        for (var j = d.length - 1; j >= 0; j--) path += "L" + x(j).toFixed(1) + " " + y(duoi[j]).toFixed(1);
        s += '<path d="' + path + 'Z" fill="' + L.mau + '" fill-opacity=".82"/>';
        duoi = tren;
      });
    /* Lưới trong SVG, NHÃN bằng HTML đè lên: svg này giãn
       preserveAspectRatio="none" nên chữ bên trong bị kéo méo. */
    var nhanY = [];
    [0.5, 1].forEach(function (f) {
      var v = max * f, yy = y(v);
      s += '<line x1="0" x2="' + W + '" y1="' + yy.toFixed(1) + '" y2="' + yy.toFixed(1) +
        '" stroke="#D8D9E0" stroke-width="1" stroke-dasharray="3 3"/>';
      nhanY.push('<span class="bd-nhan" style="top:' + (yy / H * 100).toFixed(2) + '%">' + esc(usd(v)) + "</span>");
    });
    [0, Math.floor(d.length / 2), d.length - 1].forEach(function (i, k) {
      var t = new Date(d[i][0] * 1000);
      s += '<text class="bd-truc" x="' + x(i).toFixed(0) + '" y="' + (H - 5) + '" text-anchor="' +
        (k === 0 ? "start" : k === 2 ? "end" : "middle") + '">' +
        String(t.getUTCDate()).padStart(2, "0") + "/" + String(t.getUTCMonth() + 1).padStart(2, "0") + "</text>";
    });
    s += "</svg>";
    var cuoi = d[d.length - 1], dau = d[0];
    var tc = (cuoi[iN] || 0) + (cuoi[iC] || 0) + (cuoi[iE] || 0);
    var td = (dau[iN] || 0) + (dau[iC] || 0) + (dau[iE] || 0);
    var doi = td ? (tc - td) / td : null;
    /* Khoảng thời gian tính từ mốc thật, KHÔNG suy từ số điểm:
       L2BEAT lấy mẫu 6 giờ/lần nên 122 điểm là 30 ngày. */
    var ngay = Math.round((cuoi[0] - dau[0]) / 86400);
    host.innerHTML = s + nhanY.join("");
    $("#bdSo").textContent = usd(tc);
    $("#bdDoi").innerHTML = typeof doi === "number"
      ? '<span data-d="' + (doi >= 0 ? "up" : "down") + '">' + (doi >= 0 ? "+" : "") +
        (doi * 100).toFixed(1) + "% · " + ngay + " ngày qua</span>" : "";
    $("#bdChu").innerHTML = [["native", "gốc bản địa"], ["canonical", "cầu chính thức"], ["external", "cầu bên ngoài"]]
      .map(function (k) { return '<span><i style="background:' + MAU_TVS[k[0]] + '"></i>' + k[1] + "</span>"; }).join("");
  }

  function veTongThe() {
    var s = { native: 0, canonical: 0, external: 0 };
    P.forEach(function (p) {
      if (!p.chiaTvs) return;
      s.native += p.chiaTvs.native || 0;
      s.canonical += p.chiaTvs.canonical || 0;
      s.external += p.chiaTvs.external || 0;
    });
    var tong = s.native + s.canonical + s.external;
    $("#tongSo").textContent = usd(tong);
    $("#tongSos").innerHTML = [["native", "gốc bản địa"], ["canonical", "cầu chính thức"], ["external", "cầu bên ngoài"]]
      .map(function (k) {
        return '<div class="so-hang"><span><em style="background:' + MAU_TVS[k[0]] + '"></em>' + k[1] +
          "</span><b>" + usd(s[k[0]]) + "  ·  " + (tong ? Math.round(s[k[0]] / tong * 100) : 0) + "%</b></div>";
      }).join("");
    var l2 = P.filter(function (p) { return p.loai !== "layer3"; })
      .reduce(function (a, p) { return a + (p.tvs || 0); }, 0);
    $("#tongGhi").innerHTML = esc(VI.ghiChuTong || "") + " Chỉ tính tầng 2 thì tổng là <b>" + usd(l2) + "</b>.";
  }

  /* ══════════════════════════════════════════════════
     MÀN HÌNH DÙNG BỘ MÁY CHUNG
     Mỗi mục khai: cột, cách gom hàng, tab (nếu có).
     ══════════════════════════════════════════════════ */

  /* gộp thông tin nhận dạng từ chỉ mục chung vào hàng của mục */
  function gan(x) {
    var p = BY[x.id];
    return p ? Object.assign({}, p, x) : Object.assign({ ten: x.id }, x);
  }

  function banTheoTab(host, ma, cot, doiTen) {
    var V = window.DSV_V[ma];
    var muc = (V.muc || []).map(gan);
    if (!state.tab) state.tab = "rollup";
    var dem = { rollup: 0, validium: 0, khac: 0 };
    muc.forEach(function (m) { dem[m.tab || "khac"] = (dem[m.tab || "khac"] || 0) + 1; });
    veTabs(["rollup", "validium", "khac"].map(function (k) {
      return { ma: k, ten: tra("tab", k).nhan, so: dem[k] || 0 };
    }), state.tab, function (k) { state.tab = k; state.thang = "all"; ve(); });

    $("#locLab").textContent = "Thang tự trị";
    var trongTab = muc.filter(function (m) { return (m.tab || "khac") === state.tab; });
    veChipThang(trongTab, function () { ve(); });
    var hang = sapXep(locQ(trongTab.filter(function (m) {
      return state.thang === "all" || (m.thang || "Not applicable") === state.thang;
    }), ["ten", "dang", "stack"]), "tvs");
    hang.forEach(function (h) { if (BY[h.id]) h.__mo = function () { hoSoDuAn(BY[h.id]); }; });
    demHTML(hang.length, muc.length, doiTen || "thành phố");
    veBang($("#bang"), hang, cot);
  }

  var MH = {

    /* ── Lớp 2 · rủi ro tổng hợp ── */
    "rui-ro": function (host) {
      host.innerHTML = khung({ tabs: true, dan: dan("rui-ro") });
      var chieu = [
        ["xepLich", "Sequencer Failure"], ["kiemChung", "State Validation"],
        ["duLieu", "Data Availability"], ["cuaThoat", "Exit Window"],
        ["chotSo", "Proposer Failure"]
      ];
      banTheoTab(host, "rui-ro", [COT_STT, cotTen(),
        { n: "Rủi ro", cls: "c", ve: function (h) { return rosetteO(h.ruiRo); } }
      ].concat(chieu.map(function (c) {
        return { n: tra("chieu", c[1]).nhan, cls: "l", ve: function (h) { return oRuiRo(c[1], h.rr && h.rr[c[0]]); } };
      })));
    },

    /* ── Lớp 2 · kiểm chứng trạng thái ── */
    "kiem-chung": function (host) {
      host.innerHTML = khung({ tabs: true, dan: dan("kiem-chung") });
      var V = window.DSV_V["kiem-chung"];
      var nhom = [
        { ma: "hopLe", ten: "Bằng chứng hợp lệ", so: (V.hopLe || []).length },
        { ma: "lacQuan", ten: "Chứng minh gian lận", so: (V.lacQuan || []).length },
        { ma: "khongCM", ten: "Không có cơ chế", so: (V.khongCM || []).length }
      ];
      if (["hopLe", "lacQuan", "khongCM"].indexOf(state.tab) === -1) state.tab = "hopLe";
      veTabs(nhom, state.tab, function (k) { state.tab = k; ve(); });
      $("#locLab").textContent = "";
      $("#chips").innerHTML = "";

      var hang = sapXep(locQ((V[state.tab] || []).map(gan), ["ten"]), "tvsOrder");
      hang.forEach(function (h) { if (BY[h.id]) h.__mo = function () { hoSoDuAn(BY[h.id]); }; });
      demHTML(hang.length, null, "thành phố");

      var cot = [COT_STT, cotTen()];
      if (state.tab === "hopLe") {
        cot.push(
          { n: "Hệ chứng minh", cls: "l hecm", ve: function (h) {
            return h.he ? "<b>" + esc(tra("heCM", h.he.loai).nhan) + "</b><i>" + esc(h.he.ten || "") + "</i>" : "—"; } },
          { n: "Tập lệnh máy ảo", cls: "l", ve: function (h) { return esc(h.isa || "—"); } },
          { n: "Nghi lễ khởi tạo", ve: function (h) {
            return h.soNghiLe ? "<b>" + h.soNghiLe + "</b>" : '<span class="mo">không cần</span>'; } });
      } else if (state.tab === "lacQuan") {
        cot.push(
          { n: "Hệ chứng minh", cls: "l hecm", ve: function (h) {
            return h.he ? "<b>" + esc(tra("heCM", h.he.loai).nhan) + "</b><i>" + esc(h.he.ten || "") + "</i>" : "—"; } },
          { n: "Tranh chấp", cls: "l", ve: function (h) {
            return h.he && h.he.gt ? esc(tra("giaoThuc", h.he.gt).nhan) : "—"; } },
          { n: "Hạn khiếu nại", sort: "hanKhieuNai", ve: function (h) { return giay(h.hanKhieuNai); } },
          { n: "Trễ thi hành", ve: function (h) { return h.treThiHanh ? giay(h.treThiHanh) : "—"; } },
          { n: "Thế chấp (ETH)", ve: function (h) { return h.theChap != null ? esc(h.theChap) : "—"; } },
          { n: "Ai được tố cáo", cls: "l", ve: function (h) {
            return h.xinPhep ? '<span class="rrO" data-s="warning">phải xin phép</span>'
              : '<span class="rrO" data-s="good">bất kỳ ai</span>'; } });
      } else {
        cot.push({ n: "Tài sản đang giữ", sort: "tvs", ve: function (h) { return "<b>" + usd(h.tvs) + "</b>"; } });
      }
      veBang($("#bang"), hang, cot);
    },

    /* ── Lớp 2 · dữ liệu sẵn có ── */
    "du-lieu": function (host) {
      host.innerHTML = khung({ tabs: true, dan: dan("du-lieu") });
      banTheoTab(host, "du-lieu", [COT_STT, cotTen(),
        { n: tra("chieu", "DA Layer").nhan, cls: "l", ve: function (h) { return oRuiRo("Data Availability", h.lop, true); } },
        { n: tra("chieu", "DA Bridge").nhan, cls: "l", ve: function (h) { return oRuiRo("DA Bridge", h.cau, true); } },
        { n: "Đăng cái gì", cls: "l", ve: function (h) {
          if (!h.che) return '<span class="mo">—</span>';
          return esc(tra("gia", h.che.v).nhan) + (h.che.v2 ? '<i class="rr2">' + esc(h.che.v2) + "</i>" : ""); } },
        { n: "Dữ liệu đăng 24h", sort: "dangSo", ve: function (h) {
          return h.dang ? "<b>" + byte(h.dang.v) + "</b>" + pct(h.dang.d) : "—"; } }
      ]);
    },

    /* ── Lớp 2 · xếp thứ tự ── */
    "xep-thu-tu": function (host) {
      host.innerHTML = khung({ dan: dan("xep-thu-tu") });
      $("#locLab").textContent = "";
      var hang = (window.DSV_V["xep-thu-tu"].muc || []).map(gan);
      hang.forEach(function (h) { if (BY[h.id]) h.__mo = function () { hoSoDuAn(BY[h.id]); }; });
      demHTML(hang.length, null, "chuỗi");
      veBang($("#bang"), hang, [COT_STT, cotTen("Chuỗi"),
        { n: "Số bên xếp lịch", cls: "l", ve: function (h) { return oRuiRo("x", h.soXepLich, true); } },
        { n: "Ai được tạo khối", cls: "l", ve: function (h) { return oRuiRo("x", h.quyenTaoKhoi); } },
        { n: "Điều kiện tham gia", cls: "l", ve: function (h) { return oRuiRo("x", h.dieuKienVao, true); } },
        { n: "Nhịp khối", ve: function (h) { return h.nhipKhoi ? esc(h.nhipKhoi.v) : "—"; } },
        { n: "Luân phiên", ve: function (h) { return h.luanPhien ? esc(h.luanPhien.v) : "—"; } },
        { n: "Cách tạo khối", cls: "l", ve: function (h) { return oRuiRo("x", h.cachTaoKhoi); } }
      ]);
    },

    /* ── Lớp 2 · hoạt động ── */
    "hoat-dong": function (host) {
      host.innerHTML = khung({ tabs: true, dan: dan("hoat-dong") });
      banTheoTab(host, "hoat-dong", [COT_STT, cotTen(),
        { n: "Dạng", cls: "l mo", ve: function (h) { return esc(tra("dang", h.dang || "Other").nhan); } },
        { n: "Thao tác/giây 24h", sort: "uopsSo", ve: function (h) {
          return h.uops ? "<b>" + num(h.uops.v) + "</b>" + pct(h.uops.d) : "—"; } },
        { n: "Giao dịch/giây 24h", ve: function (h) { return h.tps ? num(h.tps.v) : "—"; } },
        { n: "Gộp 30 ngày", ve: function (h) { return h.gop30d ? num(h.gop30d.v, 0) : "—"; } },
        { n: "Đỉnh từng đạt", ve: function (h) { return h.dinh != null ? num(h.dinh) : "—"; } }
      ]);
    },

    /* ── Lớp 2 · độ sống ── */
    "do-song": function (host) {
      host.innerHTML = khung({ tabs: true, dan: dan("do-song") });
      function o(g) { return g ? "<b>" + giay(g.tb) + "</b>" + '<div class="tsghi">' + giay(g.min) + " – " + giay(g.max) + "</div>" : "—"; }
      banTheoTab(host, "do-song", [COT_STT, cotTen(),
        { n: "Dạng", cls: "l mo", ve: function (h) { return esc(tra("dang", h.dang || "Other").nhan); } },
        { n: "Gửi lô giao dịch (30d)", ve: function (h) { return o(h.goiLo30d); } },
        { n: "Cập nhật trạng thái (30d)", ve: function (h) { return o(h.capNhat30d); } }
      ]);
    },

    /* ── Lớp 2 · đã ngừng ── */
    "luu-tru": function (host) {
      host.innerHTML = khung({ dan: dan("luu-tru") });
      $("#locLab").textContent = "";
      var muc = (window.DSV_V["luu-tru"].muc || []).map(gan);
      var hang = locQ(muc, ["ten", "dang"]);
      hang.forEach(function (h) {
        h.__mo = function () {
          moHoSo(tenHTML(h), "", (h.moTa ? sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(h.moTa) + "</p>") : "") +
            sec("Năm chiều rủi ro", rosetteO(h.ruiRo, 44) + dongRuiRo(h.ruiRo)));
        };
      });
      demHTML(hang.length, muc.length, "thành phố");
      veBang($("#bang"), hang, [COT_STT, cotTen(),
        { n: "Rủi ro", cls: "c", ve: function (h) { return rosetteO(h.ruiRo); } },
        { n: "Dạng", cls: "l mo", ve: function (h) { return esc(tra("dang", h.dang || "Other").nhan); } },
        { n: "Hệ chứng minh", cls: "l hecm", ve: function (h) {
          return h.he ? "<b>" + esc(tra("heCM", h.he.loai).nhan) + "</b><i>" + esc(h.he.ten || "") + "</i>" : "—"; } },
        { n: "Mục đích", cls: "l mo", ve: function (h) { return esc((h.mucDich || []).join(", ") || "—"); } },
        { n: "Bản vẽ", cls: "l mo", ve: function (h) { return esc((h.stacks || []).join(", ") || "—"); } }
      ]);
    },

    /* ── Dữ liệu sẵn có · tổng quan ── */
    "dl-tong-quan": function (host) { dlBang(host, "dl-tong-quan", true); },
    "dl-rui-ro": function (host) { dlBang(host, "dl-rui-ro", false); },
    "dl-luu-tru": function (host) { dlBang(host, "dl-luu-tru", false); },

    "dl-thong-luong": function (host) {
      host.innerHTML = khung({ dan: dan("dl-thong-luong") });
      $("#locLab").textContent = "";
      var muc = window.DSV_V["dl-thong-luong"].muc || [];
      var hang = locQ(muc, ["ten"]);
      demHTML(hang.length, null, "lớp");
      veBang($("#bang"), hang, [COT_STT, cotTen("Lớp dữ liệu"),
        { n: "Chung kết sau", cls: "l mo", ve: function (h) { return esc(h.chungThuc || "—"); } },
        { n: "Đăng trong 24h", sort: "dang24h", ve: function (h) {
          return "<b>" + byte(h.dang24h) + "</b>" + pct(h.doi); } },
        { n: "Tốc độ trung bình", ve: function (h) { return h.tocDo ? byte(h.tocDo) + "/s" : "—"; } },
        { n: "Trần", ve: function (h) {
          return h.tran === "NO_CAP" ? '<span class="mo">không giới hạn</span>'
            : (h.tran ? byte(h.tran) + "/s" : "—"); } },
        { n: "Chỉ riêng Layer 2", ve: function (h) { return byte(h.chiL2); } },
        { n: "Đăng nhiều nhất", cls: "l mo", ve: function (h) {
          return h.dangNhieuNhat ? esc(h.dangNhieuNhat.ten) + " (" + h.dangNhieuNhat.pt + "%)" : "—"; } }
      ]);
    },

    "dl-do-song": function (host) {
      host.innerHTML = khung({ dan: dan("dl-do-song") });
      $("#locLab").textContent = "";
      var muc = window.DSV_V["dl-do-song"].muc || [];
      var hang = locQ(muc, ["ten"]);
      hang.forEach(function (h) {
        h.__mo = function () {
          moHoSo(tenHTML(h), "", (h.moTa ? sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(h.moTa) + "</p>") : "") +
            sec("Cầu dữ liệu", (h.cau || []).map(function (c) {
              return '<p class="hs-p"><b>' + esc(c.ten) + "</b> — " + usd(c.tvs) + "</p>";
            }).join("") || '<p class="hs-thin">Không có cầu nào.</p>'));
        };
      });
      demHTML(hang.length, null, "lớp");
      veBang($("#bang"), hang, [COT_STT, cotTen("Lớp dữ liệu"),
        { n: "Tài sản bảo đảm", sort: "tvs", ve: function (h) { return "<b>" + usd(h.tvs) + "</b>"; } },
        { n: "Số cầu", ve: function (h) { return String((h.cau || []).length); } }
      ]);
    },

    /* ── Liên thông ── */
    "lt-tong-quan": function (host) {
      var V = window.DSV_V["lt-tong-quan"];
      host.innerHTML = '<p class="giaithich">' + dan("lt-tong-quan") + "</p>" +
        the2("Chuỗi có mặt trong bản đồ liên thông", V.chuoi.length, luoiThe(V.chuoi, function (x) {
          return (x.sapCo ? '<span class="xx">sắp có</span>' : "");
        })) +
        the2("Giao thức liên thông", V.giaoThuc.length, luoiThe(V.giaoThuc));
    },
    "lt-khung-token": function (host) {
      var V = window.DSV_V["lt-khung-token"];
      host.innerHTML = '<p class="giaithich">' + dan("lt-khung-token") + "</p>" +
        the2("Khung token", V.khung.length, luoiThe(V.khung, function (x) {
          return x.nhan ? '<span class="l3">' + esc(x.nhan) + "</span>" : "";
        }));
    },
    "lt-cau-y-dinh": function (host) {
      host.innerHTML = khung({ dan: dan("lt-cau-y-dinh") });
      $("#locLab").textContent = "";
      var muc = window.DSV_V["lt-cau-y-dinh"].cau || [];
      var hang = locQ(muc, ["ten"]);
      hang.forEach(function (h) {
        h.__mo = function () {
          moHoSo(tenHTML(h), "", (h.moTa ? sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(h.moTa) + "</p>") : "") +
            sec("Bốn chiều", dongRuiRo([
              { n: "Mô hình", v: h.moHinh && h.moHinh.v, s: h.moHinh && h.moHinh.s, d: h.moHinh && h.moHinh.d },
              { n: "Cứu hồi cho người dùng", v: h.cuuHoi && h.cuuHoi.v, s: h.cuuHoi && h.cuuHoi.s, d: h.cuuHoi && h.cuuHoi.d },
              { n: "Ai được nhận đơn", v: h.quyenGiaiQuyet && h.quyenGiaiQuyet.v, s: h.quyenGiaiQuyet && h.quyenGiaiQuyet.s, d: h.quyenGiaiQuyet && h.quyenGiaiQuyet.d },
              { n: "Cách thanh toán", v: h.thanhToan && h.thanhToan.v, s: h.thanhToan && h.thanhToan.s, d: h.thanhToan && h.thanhToan.d }
            ])));
        };
      });
      demHTML(hang.length, null, "cầu");
      veBang($("#bang"), hang, [COT_STT, cotTen("Cầu"),
        { n: "Mô hình", cls: "l", ve: function (h) { return oRuiRo("x", h.moHinh); } },
        { n: "Cứu hồi cho người dùng", cls: "l", ve: function (h) { return oRuiRo("x", h.cuuHoi); } },
        { n: "Ai được nhận đơn", cls: "l", ve: function (h) { return oRuiRo("x", h.quyenGiaiQuyet); } },
        { n: "Cách thanh toán", cls: "l", ve: function (h) { return oRuiRo("x", h.thanhToan); } }
      ]);
    },

    /* ── Quyền riêng tư ── */
    "rieng-tu": function (host) {
      host.innerHTML = khung({ dan: dan("rieng-tu") });
      $("#locLab").textContent = "";
      var muc = window.DSV_V["rieng-tu"].muc || [];
      var hang = locQ(muc, ["ten"]);
      hang.forEach(function (h) {
        h.__mo = function () {
          moHoSo(tenHTML(h), "", (h.moTa ? sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(h.moTa) + "</p>") : "") +
            (h.nghiLe ? sec("Nghi lễ khởi tạo tin cậy",
              '<p class="hs-p"><b>' + esc(h.nghiLe.ten) + "</b> · " + num(h.nghiLe.soNguoi, 0) + " người tham gia</p>" +
              (h.nghiLe.moTa ? '<p class="hs-goc">' + esc(h.nghiLe.moTa) + "</p>" : "") +
              '<p class="hs-vn"><b>Vì sao quan trọng:</b> nếu nghi lễ này từng bị thao túng, người biết bí mật có thể làm giả bằng chứng mà không ai phát hiện.</p>') : ""));
        };
      });
      demHTML(hang.length, null, "giao thức");
      veBang($("#bang"), hang, [COT_STT, cotTen("Giao thức"),
        { n: "Nghi lễ khởi tạo", cls: "l", ve: function (h) {
          if (!h.nghiLe) return '<span class="mo">không cần</span>';
          return '<span class="rrO" data-s="' + (h.nghiLe.rui === "green" ? "good" : h.nghiLe.rui === "red" ? "bad" : "warning") +
            '">' + esc(h.nghiLe.ten) + "</span>"; } },
        { n: "Người tham gia", ve: function (h) { return h.nghiLe ? num(h.nghiLe.soNguoi, 0) : "—"; } },
        { n: "Cửa thoát", cls: "l", ve: function (h) { return oRuiRo("Exit Window", h.cuaThoat); } },
        { n: "Dựng lại được mạch", cls: "l", ve: function (h) { return oRuiRo("x", h.taiLap); } }
      ]);
    },

    /* ── Danh mục ZK ── */
    "zk": function (host) {
      host.innerHTML = khung({ dan: dan("zk") });
      $("#locLab").textContent = "";
      var muc = window.DSV_V["zk"].muc || [];
      var hang = sapXep(locQ(muc, ["ten", "tacGia"]), "tvs");
      hang.forEach(function (h) {
        h.__mo = function () {
          var bo = function (t, a) {
            if (!a || !a.length) return "";
            return sec(t, a.map(function (x) {
              return '<p class="hs-p"><b>' + esc(x.ten) + '</b> <span class="mo">' + esc(x.dang) + "</span>" +
                (x.moTa ? '<br><span style="font-size:12.4px;color:var(--ink-2)">' + esc(x.moTa) + "</span>" : "") + "</p>";
            }).join(""));
          };
          moHoSo(tenHTML(h), "", (h.moTa ? sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(h.moTa) + "</p>") : "") +
            sec("Đang bảo đảm", '<div class="hs-so"><b>' + usd(h.tvs) + "</b><i>" + num(h.soDuAn, 0) + " dự án</i></div>") +
            bo("Máy ảo sinh bằng chứng", h.zkVM) + bo("Vòng bọc cuối", h.boc));
        };
      });
      demHTML(hang.length, null, "hệ");
      veBang($("#bang"), hang, [COT_STT, cotTen("Hệ chứng minh"),
        { n: "Tác giả", cls: "l mo", ve: function (h) { return esc(h.tacGia || "—"); } },
        { n: "Đang bảo đảm", sort: "tvs", ve: function (h) { return "<b>" + usd(h.tvs) + "</b>"; } },
        { n: "Số dự án dùng", sort: "soDuAn", ve: function (h) { return num(h.soDuAn, 0); } },
        { n: "Nền tảng", cls: "l mo", ve: function (h) {
          return esc((h.zkVM || []).map(function (x) { return x.ten; }).slice(0, 3).join(", ") || "—"); } }
      ]);
    },

    /* ── Từ điển ── */
    "tu-dien": function (host) {
      var T = D.tuDien || [];
      host.innerHTML = '<p class="giaithich">' + dan("tu-dien") +
        '<span class="vn">Đây là định nghĩa gốc của L2BEAT, cố ý giữ nguyên tiếng Anh: dịch thuật ngữ mật mã học ra tiếng Việt dễ làm sai lệch hơn là giúp. Phần diễn giải tiếng Việt nằm ở từng bảng.</span></p>' +
        '<section class="khoi"><div class="loc"><span class="loc-lab"></span><div class="chips"></div>' +
        '<span class="dem" id="dem"></span></div><div class="tudien" id="tudien"></div></section>';
      var q = norm(state.q.trim());
      var ds = q ? T.filter(function (t) {
        return norm(t.ten + " " + (t.khop || []).join(" ") + " " + t.dn).indexOf(q) !== -1;
      }) : T;
      demHTML(ds.length, T.length, "thuật ngữ");
      $("#tudien").innerHTML = ds.length ? ds.map(function (t) {
        return '<div class="td-muc"><b>' + esc(t.ten) + "</b>" +
          ((t.khop || []).length ? '<span class="td-khop">' + esc(t.khop.join(" · ")) + "</span>" : "") +
          "<p>" + esc(t.dn) + "</p></div>";
      }).join("") : '<p class="trong">Không có thuật ngữ nào khớp.</p>';
    }
  };

  /* ── bảng lớp dữ liệu sẵn có (3 mục dùng chung) ── */
  function dlBang(host, ma, coSo) {
    host.innerHTML = khung({ tabs: true, dan: dan(ma) });
    var muc = window.DSV_V[ma].muc || [];
    if (["cong", "rieng"].indexOf(state.tab) === -1) state.tab = "cong";
    var dem = { cong: 0, rieng: 0 };
    muc.forEach(function (m) { dem[m.cong ? "cong" : "rieng"]++; });
    veTabs([{ ma: "cong", ten: "Dùng chung", so: dem.cong }, { ma: "rieng", ten: "Riêng của dự án", so: dem.rieng }],
      state.tab, function (k) { state.tab = k; ve(); });
    $("#locLab").textContent = "";
    $("#chips").innerHTML = "";
    var hang = sapXep(locQ(muc.filter(function (m) {
      return state.tab === "cong" ? m.cong : !m.cong;
    }), ["ten"]), "tvs");
    hang.forEach(function (h) {
      h.__mo = function () {
        moHoSo(tenHTML(h), "", (h.moTa ? sec("L2BEAT mô tả", '<p class="hs-goc">' + esc(h.moTa) + "</p>") : "") +
          sec("Các chiều rủi ro", rosetteO(h.ruiRo, 44) + dongRuiRo(h.ruiRo)) +
          ((h.cau || []).length ? sec("Cầu dữ liệu", h.cau.map(function (c) {
            return '<p class="hs-p"><b>' + esc(c.ten) + "</b>" +
              (c.tvs != null ? " — " + usd(c.tvs) : "") + "</p>" + dongRuiRo(c.ruiRo);
          }).join("")) : ""));
      };
    });
    demHTML(hang.length, muc.length, "lớp");
    var cot = [COT_STT, cotTen("Lớp dữ liệu"),
      { n: "Rủi ro", cls: "c", ve: function (h) { return rosetteO(h.ruiRo); } }];
    if (coSo) {
      /* Cột này là SỐ TIỀN đặt cọc, khác với chiều rủi ro cùng tên
         (chiều đó là đánh giá tốt/xấu). Gọi khác nhau để hai cột
         không đứng cạnh nhau với cùng một nhãn. */
      cot.push({ n: "Giá trị đặt cọc", sort: "anNinhKinhTe", ve: function (h) { return usd(h.anNinhKinhTe); } });
    }
    /* Cột rủi ro lấy HỢP của mọi hàng đang hiện, không suy từ hàng
       đầu: mỗi lớp dữ liệu khai một bộ chiều khác nhau, lấy theo
       hàng đầu thì vừa thiếu chiều vừa trùng tên cột. Tra theo TÊN
       chiều chứ không theo vị trí, vì thứ tự không bảo đảm. */
    var ten = [], thay = {};
    hang.forEach(function (h) {
      (h.ruiRo || []).forEach(function (r) {
        if (!r.n || thay[r.n]) return;
        thay[r.n] = true;
        ten.push(r.n);
      });
    });
    /* Bỏ chiều nào trùng nhãn với cột đã có: "DA Layer" dịch ra
       cũng là "Lớp dữ liệu" — đúng tên cột chứa tên hàng — nên để
       cả hai thì bảng có hai cột cùng tiêu đề mà khác nội dung. */
    var daCo = {};
    cot.forEach(function (c) { daCo[c.n] = true; });
    var them = 0;
    ten.forEach(function (n) {
      if (them >= 4) return;
      var nhan = tra("chieu", n).nhan;
      if (daCo[nhan]) return;
      daCo[nhan] = true;
      them++;
      cot.push({ n: nhan, cls: "l", ve: function (h) {
        var r = (h.ruiRo || []).filter(function (x) { return x.n === n; })[0];
        return r ? oRuiRo(n, { v: r.v, s: r.s, v2: r.v2 }) : '<span class="mo">—</span>';
      } });
    });
    cot.push({ n: "Tài sản bảo đảm", sort: "tvs", ve: function (h) { return "<b>" + usd(h.tvs) + "</b>"; } });
    veBang($("#bang"), hang, cot);
  }

  /* ── hệ sinh thái (4 mục dùng chung) ── */
  function stMH(ma) {
    return function (host) {
      var V = window.DSV_V[ma];
      var duAn = (V.duAnSong || []).map(function (id) { return BY[id] || { id: id, ten: id }; });
      var tong = duAn.reduce(function (a, p) { return a + (p.tvs || 0); }, 0);
      host.innerHTML = '<p class="giaithich">' + dan(ma) +
        (V.moTa ? '<span class="vn">' + esc(V.moTa) + "</span>" : "") + "</p>" +
        '<section class="tren"><div class="the"><div class="the-dinh"><h2>Tổng tài sản trong họ chuỗi</h2>' +
        '<span class="the-so">' + usd(tong) + "</span></div>" +
        '<p class="the-ghi">' + duAn.length + " chuỗi đang chạy. Cùng một bản vẽ nghĩa là nâng cấp chảy xuống tất cả — và lỗi cũng vậy.</p></div>" +
        (V.raas && V.raas.length ? '<div class="the"><div class="the-dinh"><h2>Ai dựng hộ</h2></div>' +
          '<div class="sos">' + V.raas.map(function (r) {
            return '<div class="so-hang"><span>' + esc(r.ten) + "</span><b>" + r.duAn.length + " chuỗi</b></div>";
          }).join("") + "</div></div>" : "") +
        "</section>" +
        the2("Chuỗi trong họ", duAn.length, luoiThe(duAn.map(function (p) {
          return { ten: p.ten, logo: p.logo, id: p.id, tvs: p.tvs };
        }), function (x) { return x.tvs ? '<span class="the-tvs">' + usd(x.tvs) + "</span>" : ""; })) +
        (V.cotMoc && V.cotMoc.length ? the2("Mốc thời gian", V.cotMoc.length,
          '<ol class="cotmoc">' + V.cotMoc.map(function (m) {
            return "<li><b>" + esc(m.ten || "") + "</b>" +
              (m.ngay ? '<span class="cm-ngay">' + esc(String(m.ngay).slice(0, 10)) + "</span>" : "") +
              (m.moTa ? "<p>" + esc(m.moTa) + "</p>" : "") + "</li>";
          }).join("") + "</ol>") : "");
    };
  }
  ["st-arbitrum-orbit", "st-elastic", "st-superchain", "st-agglayer"].forEach(function (ma) {
    MH[ma] = stMH(ma);
  });

  /* ── mảnh: khối tiêu đề + lưới thẻ ── */
  function the2(tieu, so, noi) {
    return '<section class="khoi khoi2"><div class="khoi-dinh"><h2>' + esc(tieu) +
      '</h2><span class="khoi-n">' + so + "</span></div>" + noi + "</section>";
  }
  function luoiThe(ds, phu) {
    if (!ds || !ds.length) return '<p class="trong">Không có mục nào.</p>';
    return '<div class="luoi">' + ds.map(function (x) {
      return '<div class="the-nho">' + logoHTML(x.logo, x.ten) +
        "<b>" + esc(x.ten) + "</b>" + (phu ? phu(x) : "") + "</div>";
    }).join("") + "</div>";
  }

  /* ══════════════════════════════════════════════════
     ĐIỀU PHỐI
     ══════════════════════════════════════════════════ */
  function ve() {
    var host = $("#than");
    var ma = state.muc;
    var t = VI.muc[ma] || { ten: ma };
    $("#tieu").textContent = t.ten;
    document.title = "Đô Sát Viện · " + t.ten;
    veBen();

    if (ma === "tong-quan") { mhTongQuan(host); return; }
    if (ma === "tu-dien") { MH["tu-dien"](host); return; }

    var f = MH[ma];
    if (!f) { host.innerHTML = '<p class="trong">Chưa có mục này.</p>'; return; }

    if (window.DSV_V && window.DSV_V[ma]) { f(host); return; }
    host.innerHTML = '<p class="trong">Đang nạp…</p>';
    nap(ma, function (loi) {
      if (state.muc !== ma) return;          // người dùng đã bấm sang mục khác
      if (loi) {
        host.innerHTML = '<p class="trong">Không nạp được mục này.<br>' +
          '<span style="font-size:12px">' + esc(loi.message) + "</span></p>";
        return;
      }
      f(host);
    });
  }

  function tuHash() {
    var h = (location.hash || "").replace(/^#\/?/, "").split("?")[0];
    return h || "tong-quan";
  }
  function doiTuyen() {
    var ma = tuHash();
    if (!VI.muc[ma]) ma = "tong-quan";
    if (ma !== state.muc) { state.muc = ma; state.tab = null; state.thang = "all"; state.sort = null; state.desc = true; }
    ve();
    var b = $("#ben");
    if (b) b.dataset.mo = "0";
    window.scrollTo(0, 0);
  }

  /* ── thanh bên trên di động ───────────────────────── */
  function ganBen() {
    var ben = $("#ben"), nut = $("#benMoNut");
    if (!ben || !nut) return;
    nut.addEventListener("click", function () { ben.dataset.mo = ben.dataset.mo === "1" ? "0" : "1"; });
    document.addEventListener("click", function (e) {
      if (window.innerWidth > 900 || ben.dataset.mo !== "1") return;
      if (ben.contains(e.target) || nut.contains(e.target)) return;
      ben.dataset.mo = "0";
    });
  }

  function boot() {
    $("#ngay").textContent = "bản chụp " + (D.date || "—");

    $("#q").addEventListener("input", function (e) { state.q = e.target.value; ve(); });
    $("#hosoDong").addEventListener("click", dongHoSo);
    $("#scrim").addEventListener("click", dongHoSo);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") dongHoSo(); });

    /* logo hỏng thì thay bằng chữ cái đầu, đừng để ô vỡ ảnh */
    document.addEventListener("error", function (e) {
      var t = e.target;
      if (t && t.tagName === "IMG" && t.parentNode && /ten|the-nho/.test(t.parentNode.className)) {
        var b = t.parentNode.querySelector("b");
        var s = document.createElement("span");
        s.className = "khonglogo";
        s.textContent = b ? b.textContent.trim().charAt(0).toUpperCase() : "?";
        t.parentNode.replaceChild(s, t);
      }
    }, true);

    if (!D.coSSR) {
      var c = $("#canhBao");
      if (c) {
        c.hidden = false;
        c.textContent = "Lần cập nhật gần nhất không đọc được dữ liệu trang L2BEAT — " +
          "logo, nhóm và hệ chứng minh đang lấy từ bản trước.";
      }
    }
    var hong = (D.dsMuc || []).filter(function (m) { return !m.ok; });
    if (hong.length) {
      var c2 = $("#canhBao");
      if (c2) {
        c2.hidden = false;
        c2.textContent = (c2.textContent ? c2.textContent + " " : "") +
          hong.length + " mục chưa lấy được: " + hong.map(function (m) {
            return (VI.muc[m.ma] || {}).ten || m.ma;
          }).join(", ") + ".";
      }
    }

    ganBen();
    window.addEventListener("hashchange", doiTuyen);
    doiTuyen();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
