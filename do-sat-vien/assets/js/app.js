/* ═══════════════════════════════════════════════════════
   ĐÔ SÁT VIỆN — bảng xét 107 thành phố Layer 2.

   Dữ liệu: window.DSV_DATA (tự sinh, xem scripts/build-l2beat.mjs)
   Chú giải: window.DSV_VI  (bản dịch và diễn giải, glossary.js)

   Nhãn nào L2BEAT thêm mới mà chú giải chưa có thì hiện nguyên
   bản tiếng Anh và đánh dấu "chưa dịch" — không bịa nghĩa.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.DSV_DATA, VI = window.DSV_VI;
  if (!D || !VI) return;

  var P = D.projects || [];
  var state = { q: "", thang: "all", dang: "all", sort: "tvs", desc: true };

  /* ── tiện ích ─────────────────────────────────────── */
  function $(s) { return document.querySelector(s); }
  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function norm(s) {
    return String(s).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d");
  }
  function usd(v) {
    if (v == null) return "—";
    if (v >= 1e9) return "$" + (v / 1e9).toFixed(2) + "b";
    if (v >= 1e6) return "$" + Math.round(v / 1e6) + "m";
    if (v >= 1e3) return "$" + Math.round(v / 1e3) + "k";
    return "$" + Math.round(v);
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

  /* ── bộ lọc ───────────────────────────────────────── */
  function loc() {
    var q = norm(state.q.trim());
    return P.filter(function (p) {
      if (state.thang !== "all" && (p.thang || "Not applicable") !== state.thang) return false;
      if (state.dang !== "all" && (p.dang || "Other") !== state.dang) return false;
      if (q) {
        var hay = norm([p.ten, p.dang, p.stack, p.me, p.thang].join(" "));
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    }).sort(function (a, b) {
      var v;
      if (state.sort === "ten") v = String(a.ten).localeCompare(String(b.ten));
      else if (state.sort === "thang") v = stageNum(a.thang) - stageNum(b.thang);
      else v = (a.tvs || 0) - (b.tvs || 0);
      return state.desc ? -v : v;
    });
  }

  /* ── bảng ─────────────────────────────────────────── */
  function veBang() {
    var rows = loc();
    var host = $("#bang");
    host.innerHTML = "";

    $("#dem").textContent = rows.length + "/" + P.length + " thành phố";
    var tong = rows.reduce(function (s, p) { return s + (p.tvs || 0); }, 0);
    $("#tong").textContent = usd(tong);

    if (!rows.length) {
      var e = el("p", "trong");
      e.textContent = "Không có thành phố nào khớp bộ lọc.";
      host.appendChild(e);
      return;
    }

    var t = el("table", "bang");
    var thead = el("thead");
    var tr = el("tr");
    [
      { k: "rank", n: "#", l: 1 },
      { k: "ten", n: "Thành phố", l: 1 },
      { k: "thang", n: "Thang tự trị", l: 1 },
      { k: "dang", n: "Dạng", l: 1 },
      { k: "me", n: "Chuỗi mẹ", l: 1 },
      { k: "tvs", n: "Tài sản đang giữ" }
    ].forEach(function (c) {
      var th = el("th", c.l ? "l" : "");
      th.textContent = c.n;
      if (c.k === "ten" || c.k === "thang" || c.k === "tvs") {
        th.classList.add("sortable");
        if (state.sort === c.k) th.dataset.sorted = state.desc ? "desc" : "asc";
        th.addEventListener("click", function () {
          if (state.sort === c.k) state.desc = !state.desc;
          else { state.sort = c.k; state.desc = c.k !== "ten"; }
          veBang();
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
      r.addEventListener("click", function () { moHoSo(p); });
      r.addEventListener("keydown", function (e) { if (e.key === "Enter") moHoSo(p); });

      var c1 = el("td", "l num"); c1.textContent = i + 1; r.appendChild(c1);

      var c2 = el("td", "l");
      c2.innerHTML = '<b>' + esc(p.ten) + '</b>' +
        (p.loai === "layer3" ? '<span class="l3">tầng 3</span>' : '') +
        (p.xemXet ? '<span class="xx">đang xem xét</span>' : '');
      r.appendChild(c2);

      var g = tra("thang", p.thang || "Not applicable");
      var c3 = el("td", "l");
      c3.innerHTML = '<span class="thang" data-s="' + esc(stageNum(p.thang)) + '">' + esc(g.nhan) + '</span>';
      r.appendChild(c3);

      var c4 = el("td", "l mo");
      c4.textContent = tra("dang", p.dang || "Other").nhan;
      r.appendChild(c4);

      var c5 = el("td", "l mo");
      c5.textContent = p.me || "—";
      r.appendChild(c5);

      var c6 = el("td", "num");
      c6.innerHTML = '<b>' + usd(p.tvs) + '</b>' +
        (typeof p.d7 === "number"
          ? '<i data-d="' + (p.d7 >= 0 ? "up" : "down") + '">' +
            (p.d7 >= 0 ? "+" : "") + (p.d7 * 100).toFixed(1) + '%</i>'
          : '');
      r.appendChild(c6);

      tb.appendChild(r);
    });
    t.appendChild(tb);
    host.appendChild(t);
  }

  /* ── hồ sơ chi tiết ───────────────────────────────── */
  function moHoSo(p) {
    var d = $("#hoso"), b = $("#hosoBody");
    b.innerHTML = "";

    $("#hosoTen").textContent = p.ten;
    var g = tra("thang", p.thang || "Not applicable");
    $("#hosoTag").innerHTML =
      '<span class="thang" data-s="' + esc(stageNum(p.thang)) + '">' + esc(g.nhan) + '</span>' +
      '<span class="mo">' + esc(tra("dang", p.dang || "Other").nhan) + '</span>';

    /* thang tự trị nghĩa là gì */
    var s1 = el("div", "hs-sec");
    s1.innerHTML = '<div class="hs-h">Thang tự trị</div>' +
      '<p class="hs-p">' + esc(g.y || "") + '</p>' +
      (g.vn ? '<p class="hs-vn"><b>Với người gửi tiền:</b> ' + esc(g.vn) + '</p>' : '');
    b.appendChild(s1);

    /* số */
    var s2 = el("div", "hs-sec");
    var chia = p.chiaTvs || {};
    s2.innerHTML = '<div class="hs-h">Tài sản đang giữ</div>' +
      '<div class="hs-so"><b>' + usd(p.tvs) + '</b>' +
      (typeof p.d7 === "number"
        ? '<i data-d="' + (p.d7 >= 0 ? "up" : "down") + '">' + (p.d7 >= 0 ? "+" : "") +
          (p.d7 * 100).toFixed(1) + '% trong 7 ngày</i>' : '') + '</div>' +
      '<div class="hs-chia">' +
        '<span>gốc bản địa <b>' + usd(chia.native) + '</b></span>' +
        '<span>cầu chính thức <b>' + usd(chia.canonical) + '</b></span>' +
        '<span>cầu bên ngoài <b>' + usd(chia.external) + '</b></span>' +
      '</div>';
    b.appendChild(s2);

    /* năm chiều rủi ro */
    var s3 = el("div", "hs-sec");
    s3.innerHTML = '<div class="hs-h">Năm chiều rủi ro</div>';
    (p.ruiRo || []).forEach(function (r) {
      var c = tra("chieu", r.n), v = traGia(r.n, r.v);
      var row = el("div", "hs-rr");
      row.dataset.sent = r.s || "neutral";
      row.innerHTML =
        '<div class="rr-top"><span class="rr-n">' + esc(c.nhan) + '</span>' +
        '<span class="rr-v">' + esc(v.nhan) + (v.thieu ? ' <em>chưa dịch</em>' : '') + '</span></div>' +
        (c.y ? '<p class="rr-q">' + esc(c.y) + '</p>' : '') +
        (v.y ? '<p class="rr-y">' + esc(v.y) + '</p>' : '') +
        (r.d ? '<details class="rr-goc"><summary>nguyên văn L2BEAT</summary><p>' + esc(r.d) + '</p></details>' : '');
      s3.appendChild(row);
    });
    b.appendChild(s3);

    /* stack */
    if (p.stack) {
      var st = tra("stack", p.stack);
      var s4 = el("div", "hs-sec");
      s4.innerHTML = '<div class="hs-h">Bản vẽ xây dựng</div>' +
        '<p class="hs-p"><b>' + esc(p.stack) + '</b> — ' + esc(st.nhan) + '</p>';
      b.appendChild(s4);
    }

    var s5 = el("div", "hs-sec");
    s5.innerHTML = '<div class="hs-h">Nguồn</div>' +
      '<p class="hs-p"><a href="https://l2beat.com/scaling/projects/' + encodeURIComponent(p.slug) +
      '" target="_blank" rel="noopener">Hồ sơ đầy đủ trên L2BEAT ↗</a></p>' +
      '<p class="hs-thin">Đô Sát Viện dịch và diễn giải, không tự chấm điểm. Mọi đánh giá rủi ro là của L2BEAT.</p>';
    b.appendChild(s5);

    d.dataset.open = "1";
    $("#scrim").dataset.open = "1";
  }

  function dongHoSo() {
    $("#hoso").dataset.open = "0";
    $("#scrim").dataset.open = "0";
  }

  /* ── chú giải cuối trang ──────────────────────────── */
  function veChuGiai() {
    var host = $("#chugiai");
    var nhom = [
      ["Thang tự trị", "thang", ["Stage 2", "Stage 1", "Stage 0", "Not applicable"]],
      ["Dạng kỹ thuật", "dang", ["Optimistic Rollup", "ZK Rollup", "Validium", "Optimium", "Other"]],
      ["Năm chiều rủi ro", "chieu", ["Sequencer Failure", "State Validation", "Data Availability", "Exit Window", "Proposer Failure"]]
    ];
    nhom.forEach(function (n) {
      var box = el("div", "cg-nhom");
      box.innerHTML = '<h3>' + esc(n[0]) + '</h3>';
      n[2].forEach(function (k) {
        var g = tra(n[1], k);
        var d = el("div", "cg-muc");
        d.innerHTML = '<b>' + esc(g.nhan) + '</b><span class="goc">' + esc(k) + '</span>' +
          (g.y ? '<p>' + esc(g.y) + '</p>' : '') +
          (g.vn ? '<p class="vn">' + esc(g.vn) + '</p>' : '');
        box.appendChild(d);
      });
      host.appendChild(box);
    });
  }

  /* ── chip lọc ─────────────────────────────────────── */
  function veChip() {
    var dem = function (f) {
      return P.reduce(function (m, p) { var k = f(p); m[k] = (m[k] || 0) + 1; return m; }, {});
    };
    var byThang = dem(function (p) { return p.thang || "Not applicable"; });
    var byDang = dem(function (p) { return p.dang || "Other"; });

    function nhomChip(host, key, counts, thuTu) {
      var wrap = $(host);
      wrap.innerHTML = "";
      var all = el("button", "chip");
      all.type = "button";
      all.textContent = "Tất cả";
      all.setAttribute("aria-pressed", String(state[key] === "all"));
      all.addEventListener("click", function () { state[key] = "all"; veChip(); veBang(); });
      wrap.appendChild(all);

      thuTu.forEach(function (k) {
        if (!counts[k]) return;
        var b = el("button", "chip");
        b.type = "button";
        b.innerHTML = esc(tra(key === "thang" ? "thang" : "dang", k).nhan) +
          ' <span class="n">' + counts[k] + '</span>';
        b.setAttribute("aria-pressed", String(state[key] === k));
        b.addEventListener("click", function () { state[key] = k; veChip(); veBang(); });
        wrap.appendChild(b);
      });
    }

    nhomChip("#chipThang", "thang", byThang, ["Stage 2", "Stage 1", "Stage 0", "Not applicable"]);
    nhomChip("#chipDang", "dang", byDang, ["Optimistic Rollup", "ZK Rollup", "Validium", "Optimium", "Other"]);
  }

  /* ── khởi động ────────────────────────────────────── */
  function boot() {
    $("#ngay").textContent = D.date || "—";
    $("#tongAll").textContent = usd(D.tongTvs);
    $("#soAll").textContent = P.length;

    $("#q").addEventListener("input", function (e) { state.q = e.target.value; veBang(); });
    $("#hosoDong").addEventListener("click", dongHoSo);
    $("#scrim").addEventListener("click", dongHoSo);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") dongHoSo();
    });

    veChip();
    veBang();
    veChuGiai();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
