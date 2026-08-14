/* ═══════════════════════════════════════════════════════
   TÀNG THƯ CÁC — kho tra cứu Claude Skills.

   Dữ liệu: window.TT_DATA  (tự sinh, xem scripts/build-tangthu.mjs)
   Chú giải: window.TT_VI   (bản dịch tay, sửa được)

   Ba màn hình:
     #/tong-quan  lưới nhóm việc — nhìn một cái là biết có gì
     #/danh-muc   tra từng skill, có hồ sơ chi tiết
     #/xep-hang   bảng xếp hạng kho theo sao

   ── LÀM MỚI TỪ GITHUB ─────────────────────────────────
   Khác các cung kia: api.github.com có CORS mở, nên trang này gọi
   thẳng được từ trình duyệt. Bản chụp lúc build luôn có sẵn (mở là
   thấy ngay, offline vẫn xem được), còn nút "Làm mới" thì lấy số
   sao mới nhất tại chỗ. Hạn mức 60 lượt/giờ mỗi IP — quá đủ cho
   một người dùng, và hết hạn mức thì chỉ mất phần làm mới chứ
   không mất bản chụp.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.TT_DATA, VI = window.TT_VI;
  if (!D || !VI) return;

  var state = { muc: "tong-quan", q: "", nhom: "all", nguon: "all" };
  var SK = D.skills || [], KHO = D.kho || [];

  function $(s) { return document.querySelector(s); }
  function el(t, c) { var e = document.createElement(t); if (c) e.className = c; return e; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function norm(s) {
    return String(s).toLowerCase().normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "").replace(/\u0111/g, "d");
  }
  function so(n) {
    if (n == null || isNaN(n)) return "—";
    if (n >= 1e6) return (n / 1e6).toFixed(1) + "tr";
    if (n >= 1e3) return (n / 1e3).toFixed(1) + "k";
    return String(n);
  }
  function ngay(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) return "—";
    var p = function (n) { return String(n).padStart(2, "0"); };
    return p(d.getUTCDate()) + "/" + p(d.getUTCMonth() + 1) + "/" + d.getUTCFullYear();
  }
  function nhomCua(ma) { return VI.nhom[ma] || { ten: ma, mau: "#7A7A88", y: "" }; }
  /* Bản dịch tay viết cho ĐÚNG kho anthropics/skills sau khi đọc
     từng SKILL.md. Tra theo tên không thôi là sai: tên trùng giữa
     các kho rất thường, và skill cùng tên ở kho khác làm việc khác. */
  var KHO_DA_DICH = "anthropics/skills";
  function dichCua(s) {
    return s.kho === KHO_DA_DICH ? VI.skill[s.ten] : null;
  }

  /* ── thanh bên ────────────────────────────────────── */
  var IC = {
    "tong-quan": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>',
    "danh-muc": '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>',
    "xep-hang": '<path d="M3 21h18"/><rect x="4.6" y="12.4" width="3.6" height="6.4" rx="1.1"/><rect x="10.2" y="7" width="3.6" height="11.8" rx="1.1"/><rect x="15.8" y="10" width="3.6" height="8.8" rx="1.1"/>'
  };
  function demMuc(ma) {
    if (ma === "danh-muc") return SK.length;
    if (ma === "xep-hang") return KHO.length;
    return null;
  }
  function veBen() {
    var host = $("#benMuc");
    host.innerHTML = "";
    var lab = el("div", "blab");
    lab.textContent = "Tra cứu";
    host.appendChild(lab);
    ["tong-quan", "danh-muc", "xep-hang"].forEach(function (ma) {
      var t = VI.muc[ma] || { ten: ma };
      var a = el("a", "bmuc");
      a.href = "#/" + ma;
      a.title = t.y || t.ten;
      if (state.muc === ma) a.setAttribute("aria-current", "page");
      var n = demMuc(ma);
      a.innerHTML = '<span class="bic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' + IC[ma] + "</svg></span>" +
        "<span>" + esc(t.ten) + "</span>" + (n != null ? '<span class="bn">' + n + "</span>" : "");
      host.appendChild(a);
    });
  }

  function dan(ma) {
    var t = VI.muc[ma];
    if (!t) return "";
    return "<b>" + esc(t.ten) + "</b>" + (t.y ? " — " + esc(t.y) : "") +
      (t.vn ? '<span class="vn">' + esc(t.vn) + "</span>" : "");
  }

  /* ══════════════════════════════════════════════════
     1. TỔNG QUAN — lưới nhóm việc
     ══════════════════════════════════════════════════ */
  function mhTongQuan(host) {
    var ct = SK.filter(function (s) { return dichCua(s); }).length;
    var thuTu = Object.keys(VI.nhom).filter(function (n) { return (D.demNhom || {})[n]; })
      .sort(function (a, b) {
        /* "khac" luôn xuống cuối dù đông nhất: nhóm rác dẫn đầu thì
           màn Tổng quan trông như chưa phân loại được gì. */
        if (a === "khac") return 1;
        if (b === "khac") return -1;
        return (D.demNhom[b] || 0) - (D.demNhom[a] || 0);
      });

    host.innerHTML =
      '<p class="giaithich">' + dan("tong-quan") + "</p>" +
      '<div class="tomtat">' +
        '<div class="tt-o"><span>Skill quét được</span><b>' + SK.length + "</b>" +
          "<i>từ " + (D.soKhoQuet || 0) + " kho trên GitHub</i></div>" +
        '<div class="tt-o"><span>Đã dịch tiếng Việt</span><b style="color:var(--acc)">' + ct + "</b>" +
          "<i>kho anthropics/skills, đọc từng cái</i></div>" +
        '<div class="tt-o"><span>Kho đang theo dõi</span><b>' + KHO.length + "</b>" +
          "<i>xếp theo sao, làm mới được</i></div>" +
      "</div>" +
      '<div class="luoi-nhom">' + thuTu.map(function (n) {
        var g = nhomCua(n);
        var trong = SK.filter(function (s) { return s.nhom === n; });
        var ctN = trong.filter(function (s) { return dichCua(s); }).length;
        return '<a class="o-nhom" href="#/danh-muc?nhom=' + encodeURIComponent(n) +
          '" style="--m:' + g.mau + '">' +
          '<div class="on-dinh"><h3>' + esc(g.ten) + '</h3><span class="on-so">' + trong.length + "</span></div>" +
          "<p>" + esc(g.y || "") + "</p>" +
          (ctN ? '<span class="on-ct">' + ctN + " cái đã dịch tiếng Việt</span>" : "") +
          "</a>";
      }).join("") + "</div>";
  }

  /* ══════════════════════════════════════════════════
     2. DANH MỤC SKILL
     ══════════════════════════════════════════════════ */
  function mhDanhMuc(host) {
    host.innerHTML = '<p class="giaithich">' + dan("danh-muc") + "</p>" +
      '<section class="khoi">' +
      '<div class="loc"><span class="loc-lab">Nhóm việc</span>' +
      '<div class="chips" id="chipNhom" style="display:flex;gap:6px;flex-wrap:wrap"></div></div>' +
      '<div class="loc"><span class="loc-lab">Nguồn</span>' +
      '<div class="chips" id="chipNguon" style="display:flex;gap:6px;flex-wrap:wrap"></div>' +
      '<span class="dem" id="dem"></span></div>' +
      '<div class="ds-skill" id="ds"></div></section>';

    /* chip nhóm */
    var wn = $("#chipNhom");
    function chip(host2, nhan, dang, key, val) {
      var b = el("button", "chip");
      b.type = "button";
      b.innerHTML = nhan + (dang != null ? '<span class="n">' + dang + "</span>" : "");
      b.setAttribute("aria-pressed", String(state[key] === val));
      b.addEventListener("click", function () { state[key] = val; ve(); });
      host2.appendChild(b);
    }
    chip(wn, "Tất cả", SK.length, "nhom", "all");
    Object.keys(VI.nhom).forEach(function (n) {
      var c = (D.demNhom || {})[n];
      if (c) chip(wn, esc(nhomCua(n).ten), c, "nhom", n);
    });

    var wg = $("#chipNguon");
    /* Lọc theo CÓ BẢN DỊCH hay không, chứ không theo chủ kho:
       người đọc quan tâm "cái nào đọc được tiếng Việt", không quan
       tâm ai sở hữu repo. */
    var ct = SK.filter(function (s) { return dichCua(s); }).length;
    chip(wg, "Tất cả", null, "nguon", "all");
    chip(wg, "Đã dịch tiếng Việt", ct, "nguon", "ct");
    chip(wg, "Còn nguyên bản gốc", SK.length - ct, "nguon", "cd");

    var q = norm(state.q.trim());
    var ds = SK.filter(function (s) {
      if (state.nhom !== "all" && s.nhom !== state.nhom) return false;
      if (state.nguon === "ct" && !dichCua(s)) return false;
      if (state.nguon === "cd" && dichCua(s)) return false;
      if (q) {
        var d = dichCua(s);
        var hay = [s.ten, s.moTa, s.kho, d && d.tom, d && d.ban].join(" ");
        if (norm(hay).indexOf(q) === -1) return false;
      }
      return true;
    });
    $("#dem").textContent = ds.length + " / " + SK.length + " skill";

    var host2 = $("#ds");
    if (!ds.length) { host2.innerHTML = '<p class="trong">Không có skill nào khớp.</p>'; return; }
    host2.innerHTML = "";
    ds.slice(0, 400).forEach(function (s) {
      var g = nhomCua(s.nhom), d = dichCua(s);
      var b = el("button", "sk");
      b.type = "button";
      b.style.setProperty("--m", g.mau);
      b.innerHTML =
        '<div class="sk-dinh"><span class="sk-cham"></span>' +
        '<span class="sk-ten">' + esc(s.ten) + "</span>" +
        (s.chinhChu ? '<span class="the-nho the-ct">' + esc(VI.nhan.chinhChu) + "</span>" : "") +
        (dichCua(s) ? "" : '<span class="the-nho the-cd">' + esc(VI.nhan.chuaDich) + "</span>") +
        (s.trung ? '<span class="the-nho the-tr">' + esc(VI.nhan.trung) + "</span>" : "") +
        '<span class="sk-sao">★ ' + so(s.sao) + "</span></div>" +
        (d ? '<p class="sk-tom">' + esc(d.tom) + "</p>"
           : '<p class="sk-tom goc">' + esc(String(s.moTa).slice(0, 190)) +
             (s.moTa.length > 190 ? "…" : "") + "</p>") +
        '<div style="margin-top:6px"><span class="sk-kho">' + esc(s.kho) + "/" + esc(s.duong) + "</span></div>";
      b.addEventListener("click", function () { moHoSo(s); });
      host2.appendChild(b);
    });
    if (ds.length > 400) {
      var p = el("p", "trong");
      p.textContent = "Hiện 400 skill đầu. Lọc theo nhóm hoặc tìm để thu hẹp.";
      host2.appendChild(p);
    }
  }

  /* ── hồ sơ skill ──────────────────────────────────── */
  function moHoSo(s) {
    var d = dichCua(s), g = nhomCua(s.nhom);
    var h = "";

    if (d) {
      h += '<div class="hs"><div class="hs-h">Nó là gì</div><p class="hs-p">' + esc(d.tom) + "</p></div>";
      if (d.lam && d.lam.length) {
        h += '<div class="hs"><div class="hs-h">Làm được gì</div><ul class="hs-lam">' +
          d.lam.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>";
      }
      if (d.khi) h += '<div class="hs"><div class="hs-h">Khi nào Claude tự bật nó</div>' +
        '<p class="hs-khi">' + esc(d.khi) + "</p></div>";
      if (d.ban) h += '<div class="hs"><div class="hs-h">Với hệ thống của bạn</div>' +
        '<p class="hs-ban">' + esc(d.ban) + "</p></div>";
      h += '<div class="hs"><div class="hs-h">Mô tả gốc (tiếng Anh)</div>' +
        '<p class="hs-goc">' + esc(s.moTa) + "</p></div>";
    } else {
      h += '<div class="hs"><div class="hs-h">Mô tả gốc — chưa dịch tay</div>' +
        '<p class="hs-goc">' + esc(s.moTa) + "</p>" +
        '<p class="hs-p" style="margin-top:9px;font-size:12.4px;color:var(--ink-3)">' +
        "Chỉ 17 skill trong kho <code>anthropics/skills</code> được dịch và diễn giải tay, " +
        "vì tôi đã đọc từng SKILL.md của chúng. Những skill còn lại — kể cả skill do Anthropic " +
        "sở hữu ở kho khác — giữ nguyên bản gốc: bịa mô tả tiếng Việt cho skill chưa đọc kỹ " +
        "còn tệ hơn để nguyên bản.</p></div>";
    }

    var repo = "https://github.com/" + s.kho;
    var duongDay = repo + "/tree/main/" + s.duong;
    h += '<div class="hs"><div class="hs-h">Cách cài</div>' +
      '<pre class="cai" id="lenhCai">git clone --depth 1 ' + esc(repo) + '.git /tmp/sk\n' +
      "cp -r /tmp/sk/" + esc(s.duong) + " ~/.claude/skills/</pre>" +
      '<button class="nut-chep" id="chepCai" type="button">Chép lệnh</button>' +
      '<p class="hs-p" style="margin-top:10px;font-size:12.4px;color:var(--ink-3)">' +
      "Đặt vào <code>~/.claude/skills/</code> là dùng cho mọi dự án; đặt vào " +
      "<code>.claude/skills/</code> trong repo thì chỉ dự án đó thấy.</p></div>";

    h += '<div class="hs"><div class="hs-h">Nguồn</div><p class="hs-p">' +
      '<a href="' + esc(duongDay) + '" target="_blank" rel="noopener">Xem SKILL.md trên GitHub ↗</a><br>' +
      '<a href="' + esc(repo) + '" target="_blank" rel="noopener">Kho ' + esc(s.kho) + " ↗</a></p>" +
      (s.giayPhep ? '<p class="hs-p" style="margin-top:8px;font-size:12.2px;color:var(--ink-3)">Giấy phép: ' +
        esc(s.giayPhep) + "</p>" : "") + "</div>";

    $("#hosoTen").textContent = s.ten;
    $("#hosoTag").innerHTML =
      '<span class="the-nho" style="background:' + g.mau + '22;color:' + g.mau + '">' + esc(g.ten) + "</span>" +
      (s.chinhChu ? '<span class="the-nho the-ct">' + esc(VI.nhan.chinhChu) + "</span>" : "") +
      (dichCua(s) ? "" : '<span class="the-nho the-cd">' + esc(VI.nhan.chuaDich) + "</span>") +
      '<span style="font-size:11.5px;color:var(--ink-3)">★ ' + so(s.sao) + "</span>";
    $("#hosoBody").innerHTML = h;
    $("#hoso").dataset.open = "1";
    $("#scrim").dataset.open = "1";
    $("#hosoDong").focus();

    var nut = $("#chepCai");
    if (nut) nut.addEventListener("click", function () {
      var t = $("#lenhCai").textContent;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(t).then(function () {
          nut.textContent = "Đã chép";
          setTimeout(function () { nut.textContent = "Chép lệnh"; }, 1800);
        }).catch(function () { nut.textContent = "Không chép được — bôi đen rồi Ctrl+C"; });
      } else {
        nut.textContent = "Trình duyệt không cho chép — bôi đen rồi Ctrl+C";
      }
    });
  }

  /* ══════════════════════════════════════════════════
     3. XẾP HẠNG KHO
     ══════════════════════════════════════════════════ */
  function mhXepHang(host) {
    host.innerHTML = '<p class="giaithich">' + dan("xep-hang") + "</p>" +
      '<section class="khoi"><div class="loc">' +
      '<button class="nut-phu" id="lamMoi" type="button">Làm mới số sao từ GitHub</button>' +
      '<span class="goiy" id="tinhTrang"></span>' +
      '<span class="dem" id="dem"></span></div>' +
      '<div class="bangwrap" id="bang"></div></section>';

    $("#lamMoi").addEventListener("click", lamMoi);
    veBangKho();
  }

  function veBangKho() {
    var q = norm(state.q.trim());
    var demSkill = {};
    SK.forEach(function (s) { demSkill[s.kho] = (demSkill[s.kho] || 0) + 1; });

    var ds = KHO.filter(function (k) {
      return !q || norm(k.id + " " + (k.moTa || "")).indexOf(q) !== -1;
    }).slice().sort(function (a, b) { return b.sao - a.sao; });
    $("#dem").textContent = ds.length + " / " + KHO.length + " kho";

    var t = el("table", "bang");
    t.innerHTML = '<thead><tr><th class="l">#</th><th class="l">Kho</th>' +
      "<th>Sao</th><th>Nhánh rẽ</th><th>Skill quét được</th><th class=\"l\">Đổi lần cuối</th></tr></thead>";
    var tb = el("tbody");
    ds.forEach(function (k, i) {
      var r = el("tr");
      r.innerHTML =
        '<td class="l hang">' + (i + 1) + "</td>" +
        '<td class="l"><a class="kho-ten" href="https://github.com/' + esc(k.id) +
          '" target="_blank" rel="noopener">' + esc(k.id) + "</a>" +
          (k.chinhChu ? ' <span class="the-nho the-ct">' + esc(VI.nhan.chinhChu) + "</span>" : "") +
          (k.moTa ? '<span class="kho-mo">' + esc(k.moTa) + "</span>" : "") + "</td>" +
        "<td><b>" + so(k.sao) + "</b></td>" +
        "<td>" + so(k.fork) + "</td>" +
        "<td>" + (demSkill[k.id] != null ? demSkill[k.id] : '<span class="hang">chưa quét</span>') + "</td>" +
        '<td class="l hang">' + esc(ngay(k.doiLuc)) + "</td>";
      tb.appendChild(r);
    });
    t.appendChild(tb);
    $("#bang").innerHTML = "";
    $("#bang").appendChild(t);
  }

  /* Gọi thẳng GitHub từ trình duyệt. Chỉ cập nhật SỐ SAO và ngày
     đổi — không quét lại skill, vì quét lại tốn hàng chục lượt gọi
     mà hạn mức không token chỉ có 60/giờ. */
  function lamMoi() {
    var nut = $("#lamMoi"), tt = $("#tinhTrang");
    nut.disabled = true;
    nut.textContent = "Đang hỏi GitHub…";
    tt.textContent = "";
    fetch("https://api.github.com/search/repositories" +
      "?q=topic:claude-skills&sort=stars&order=desc&per_page=" + Math.min(KHO.length, 60),
      { headers: { accept: "application/vnd.github+json" } })
      .then(function (r) {
        if (r.status === 403 || r.status === 429) throw new Error("hết hạn mức GitHub (60 lượt/giờ mỗi IP)");
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (j) {
        var moi = {};
        (j.items || []).forEach(function (x) { moi[x.full_name] = x; });
        var doi = 0;
        KHO.forEach(function (k) {
          var m = moi[k.id];
          if (!m) return;
          if (m.stargazers_count !== k.sao) doi++;
          k.sao = m.stargazers_count;
          k.fork = m.forks_count;
          k.doiLuc = m.pushed_at || m.updated_at;
        });
        veBangKho();
        tt.textContent = doi
          ? doi + " kho đổi số sao · lúc " + new Date().toLocaleTimeString("vi-VN")
          : "không kho nào đổi · lúc " + new Date().toLocaleTimeString("vi-VN");
      })
      .catch(function (e) {
        tt.textContent = "Không làm mới được: " + e.message + " — bảng vẫn là bản chụp lúc build.";
      })
      .then(function () {
        nut.disabled = false;
        nut.textContent = "Làm mới số sao từ GitHub";
      });
  }

  /* ══════════════════════════════════════════════════
     ĐIỀU PHỐI
     ══════════════════════════════════════════════════ */
  var MH = { "tong-quan": mhTongQuan, "danh-muc": mhDanhMuc, "xep-hang": mhXepHang };

  function ve() {
    var t = VI.muc[state.muc] || { ten: state.muc };
    $("#tieu").textContent = t.ten;
    document.title = "Tàng Thư Các · " + t.ten;
    veBen();
    (MH[state.muc] || MH["tong-quan"])($("#than"));
  }

  function doiTuyen() {
    var h = (location.hash || "").replace(/^#\/?/, "");
    var phan = h.split("?");
    var ma = phan[0] || "tong-quan";
    if (!VI.muc[ma]) ma = "tong-quan";
    /* #/danh-muc?nhom=giao-dien — ô nhóm ở Tổng quan nhảy thẳng
       sang Danh mục đã lọc sẵn, khỏi bắt người dùng lọc lại tay. */
    var loc = {};
    (phan[1] || "").split("&").forEach(function (kv) {
      var p = kv.split("=");
      if (p[0]) loc[p[0]] = decodeURIComponent(p[1] || "");
    });
    if (ma !== state.muc) { state.muc = ma; state.nhom = "all"; state.nguon = "all"; }
    if (loc.nhom) state.nhom = loc.nhom;
    ve();
    var b = $("#ben");
    if (b) b.dataset.mo = "0";
    window.scrollTo(0, 0);
  }

  function dong() {
    $("#hoso").dataset.open = "0";
    $("#scrim").dataset.open = "0";
  }

  function boot() {
    $("#ngay").textContent = "bản chụp " + (D.date || "—");
    $("#q").addEventListener("input", function (e) { state.q = e.target.value; ve(); });
    $("#hosoDong").addEventListener("click", dong);
    $("#scrim").addEventListener("click", dong);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") dong(); });

    if (D.soKhoHong) {
      var c = $("#canhBao");
      c.hidden = false;
      c.textContent = D.soKhoHong + " kho không quét được lần cập nhật gần nhất " +
        "(kho bị xoá, đổi tên, hoặc hết hạn mức GitHub giữa chừng). Danh mục vẫn đủ phần quét được.";
    }

    var nut = $("#benMoNut"), ben = $("#ben");
    if (nut && ben) {
      nut.addEventListener("click", function () { ben.dataset.mo = ben.dataset.mo === "1" ? "0" : "1"; });
      document.addEventListener("click", function (e) {
        if (window.innerWidth > 900 || ben.dataset.mo !== "1") return;
        if (ben.contains(e.target) || nut.contains(e.target)) return;
        ben.dataset.mo = "0";
      });
    }

    window.addEventListener("hashchange", doiTuyen);
    doiTuyen();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
