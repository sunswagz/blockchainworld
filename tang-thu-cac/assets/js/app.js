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
  /* Lớp tri thức nền — knowledge-os/sinh.mjs ghi ra assets/js/v/tri-thuc.js,
     mang cả dữ liệu lẫn hàm vẽ nên khuôn giống hệt mọi cung khác. Nó KHÔNG
     đụng con số nào; việc duy nhất là nói phòng này đang đo VIỆC KINH TẾ
     gì, và mỗi câu giải nghĩa đến từ đâu. Thiếu file thì phòng vẫn vẽ đủ. */
  var TT = window.TRI_THUC || null;

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
    /* Kho gốc giữ nguyên chỗ cũ (VI.skill). Kho chính chủ thứ hai và
       về sau tra trong VI.dichKho, khoá theo TÊN KHO trước rồi mới
       tới tên skill — đúng luật ghi ở đầu glossary.js: tên trùng giữa
       các kho là chuyện thường, tra thẳng theo tên là có ngày một
       skill mượn bản dịch của skill khác hẳn. */
    if (s.kho === KHO_DA_DICH) return VI.skill[s.ten] || null;
    var m = VI.dichKho && VI.dichKho[s.kho];
    return (m && m[s.ten]) || null;
  }

  /* ── chỉ mục bản dịch cho DANH SÁCH ────────────────
     Bản dịch đầy đủ nằm trong assets/data/dich/<kho>.json, nạp lười khi
     mở hồ sơ. Danh sách không đợi được kiểu đó: nó phải biết NGAY skill
     nào đã dịch để đếm, để lọc, và để hiện câu công dụng tiếng Việt.
     Nên có thêm assets/data/dich-tom.json — chỉ id → câu "nó là gì",
     sinh bằng scripts/build-dich-tom.mjs.

     Nạp SAU khi vẽ xong lần đầu, không chặn: trang mở ra ngay với mô tả
     gốc, chỉ mục về tới đâu thì vẽ lại tới đó. Trước khi có nó, bộ đếm
     chỉ thấy 42 skill dịch tay trong glossary.js — đúng cái đã làm màn
     danh mục báo "còn nguyên bản gốc 2859" trong khi 2.859 bản dịch nằm
     sẵn trên đĩa. */
  var TOM = null;
  function napTom() {
    fetch("./assets/data/dich-tom.json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        if (!j || !j.tom) return;
        TOM = j.tom;
        ve();                     /* vẽ lại màn đang mở với số liệu đúng */
      })
      .catch(function () {});
  }
  /* Câu công dụng tiếng Việt, ưu tiên bản dịch tay đủ bốn mục. */
  function tomVi(s) {
    var d = dichCua(s);
    if (d && d.tom) return d.tom;
    return (TOM && TOM[s.id]) || null;
  }
  function daDich(s) { return !!tomVi(s); }

  /* ── thanh bên ────────────────────────────────────── */
  var IC = {
    "tong-quan": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>',
    "danh-muc": '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>',
    "xep-hang": '<path d="M3 21h18"/><rect x="4.6" y="12.4" width="3.6" height="6.4" rx="1.1"/><rect x="10.2" y="7" width="3.6" height="11.8" rx="1.1"/><rect x="15.8" y="10" width="3.6" height="8.8" rx="1.1"/>',
    "xu-huong": '<path d="M3.5 16.5 9 11l4 4 7.5-7.5"/><path d="M15 7.5h5.5V13"/>',
    "lich-su": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.2V12l3.2 2"/>'
  };
  function demMuc(ma) {
    if (ma === "danh-muc") return SK.length;
    if (ma === "xep-hang") return KHO.length;
    if (ma === "lich-su") return (D.doiGanNhat || []).length;
    return null;
  }
  function veBen() {
    var host = $("#benMuc");
    host.innerHTML = "";
    var lab = el("div", "blab");
    lab.textContent = "Tra cứu";
    host.appendChild(lab);
    ["tong-quan", "danh-muc", "xep-hang", "xu-huong", "lich-su"].forEach(function (ma) {
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
    var ct = SK.filter(daDich).length;
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
        '<div class="tt-o"><span>Skill trong danh mục</span><b>' + SK.length + "</b>" +
          "<i>từ " + (D.soKhoQuet || 0) + " kho · đã gộp bản trùng</i></div>" +
        '<div class="tt-o"><span>Đã dịch tiếng Việt</span><b style="color:var(--acc)">' + ct + "</b>" +
          "<i>viết tay từ mô tả gốc, không dịch máy</i></div>" +
        '<div class="tt-o"><span>Kho đang theo dõi</span><b>' + KHO.length + "</b>" +
          "<i>xếp theo sao, làm mới được</i></div>" +
      "</div>" +
      '<div class="luoi-nhom">' + thuTu.map(function (n) {
        var g = nhomCua(n);
        var trong = SK.filter(function (s) { return s.nhom === n; });
        var ctN = trong.filter(daDich).length;
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
    var ct = SK.filter(daDich).length;
    chip(wg, "Tất cả", null, "nguon", "all");
    chip(wg, "Đã dịch tiếng Việt", ct, "nguon", "ct");
    chip(wg, "Còn nguyên bản gốc", SK.length - ct, "nguon", "cd");

    var q = norm(state.q.trim());
    var ds = SK.filter(function (s) {
      if (state.nhom !== "all" && s.nhom !== state.nhom) return false;
      if (state.nguon === "ct" && !daDich(s)) return false;
      if (state.nguon === "cd" && daDich(s)) return false;
      if (q) {
        /* Tìm cả trong bản dịch: gõ "gỡ lỗi" phải ra skill có mô tả gốc
           là "debug". Đó là toàn bộ lý do có bản dịch. */
        var d = dichCua(s);
        var hay = [s.ten, s.moTa, s.kho, tomVi(s), d && d.ban].join(" ");
        if (norm(hay).indexOf(q) === -1) return false;
      }
      return true;
    });
    $("#dem").textContent = ds.length + " / " + SK.length + " skill";

    var host2 = $("#ds");
    if (!ds.length) { veTrongDanhMuc(host2); return; }
    host2.innerHTML = "";
    ds.slice(0, 400).forEach(function (s) {
      var g = nhomCua(s.nhom), tv = tomVi(s);
      var b = el("button", "sk");
      b.type = "button";
      b.style.setProperty("--m", g.mau);
      b.innerHTML =
        '<div class="sk-dinh"><span class="sk-cham"></span>' +
        '<span class="sk-ten">' + esc(s.ten) + "</span>" +
        (s.chinhChu ? '<span class="the-nho the-ct">' + esc(VI.nhan.chinhChu) + "</span>" : "") +
        (tv ? "" : '<span class="the-nho the-cd">' + esc(VI.nhan.chuaDich) + "</span>") +
        (s.trungTen ? '<span class="the-nho the-tr" title="Có skill khác cùng tên nhưng nội dung khác">' +
          esc(VI.nhan.trungTen) + "</span>" : "") +
        (s.soBanSao ? '<span class="the-nho the-bs" title="Kho khác cũng có bản y hệt">' +
          s.soBanSao + " bản sao</span>" : "") +
        '<span class="sk-sao">★ ' + so(s.sao) + "</span></div>" +
        (tv ? '<p class="sk-tom">' + esc(tv) + "</p>"
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

  /* ── Ô TRỐNG CỦA DANH MỤC ──────────────────────────
     Hai màn kia đã tự giải thích khi trống: Xu hướng nói vì sao chưa
     đủ mốc, Lịch sử nói nhật ký bắt đầu từ đâu. Màn này thì không —
     nó chỉ có một câu "Không có skill nào khớp.", đúng nhưng không
     dùng được.

     Ba bộ lọc chồng nhau (nhóm việc · nguồn · từ khoá) và chỉ một
     trong ba nằm trong tầm mắt: chip nhóm và chip nguồn ở trên đầu
     danh sách, còn ô tìm nằm tận thanh đỉnh và KHÔNG bị xoá khi đổi
     phòng. Nên ca thường gặp nhất là gõ một từ ở phòng khác, quay
     lại đây, thấy danh sách rỗng mà không thấy lý do ở đâu cả.

     Nên: kể ĐỦ điều kiện đang bật, rồi cho MỘT lối ra. Không giấu ô
     trống đi — nó vẫn trống, chỉ là trống có nói. */
  function veTrongDanhMuc(host2) {
    var dk = [];
    if (state.nhom !== "all") dk.push("nhóm việc <b>" + esc(nhomCua(state.nhom).ten) + "</b>");
    if (state.nguon === "ct") dk.push("nguồn <b>đã dịch tiếng Việt</b>");
    if (state.nguon === "cd") dk.push("nguồn <b>còn nguyên bản gốc</b>");
    var tq = state.q.trim();
    if (tq) dk.push("từ khoá <b>“" + esc(tq) + "”</b>");

    /* Không điều kiện nào bật mà vẫn rỗng: lỗi nằm ở bản chụp, không
       nằm ở người dùng. Đừng mời họ xoá bộ lọc không có. */
    if (!dk.length) {
      host2.innerHTML = '<div class="trong-loc"><b>Danh mục đang trống.</b>' +
        "<p>Bản chụp gần nhất không giữ được skill nào — không phải do bộ lọc, " +
        "vì hiện không có bộ lọc nào bật. Bản cập nhật kế tiếp (4 lượt mỗi ngày) " +
        "sẽ dựng lại danh mục.</p></div>";
      return;
    }

    host2.innerHTML = '<div class="trong-loc"><b>Không skill nào khớp ' +
      (dk.length > 1 ? "cả " + dk.length + " điều kiện" : "điều kiện") + " đang bật.</b>" +
      "<ul>" + dk.map(function (x) { return "<li>" + x + "</li>"; }).join("") + "</ul>" +
      "<p>Danh mục có " + SK.length + " skill. Bỏ bớt một điều kiện ở trên, " +
      "hoặc xoá hết để xem lại toàn bộ.</p>" +
      '<button class="nut-phu" id="xoaLoc" type="button">Xoá hết điều kiện · xem cả ' +
      SK.length + " skill</button></div>";

    var nut = $("#xoaLoc");
    if (nut) nut.addEventListener("click", function () {
      state.nhom = "all"; state.nguon = "all"; state.q = "";
      /* Ô tìm nằm ở thanh đỉnh, ngoài vùng ve() vẽ lại — không tự tay
         xoá nó thì từ khoá vẫn nằm đó trong khi danh sách đã bỏ lọc,
         và lần gõ tiếp theo lọc theo một chuỗi người dùng tưởng đã mất. */
      var o = $("#q");
      if (o) o.value = "";
      ve();
    });
  }

  /* ── hồ sơ skill ──────────────────────────────────── */
  /* ── BẢNG TUA ─────────────────────────────────────
     Skill không phải app để quay màn hình — nó là bản hướng dẫn cho
     agent. Nên "trailer" dựng từ chính cấu trúc bài viết: đề mục là
     các chặng, khối lệnh là hành động.

     Để trong file riêng theo kho, nạp khi mở skill. data.js đã 1,5 MB
     và nằm trong SHELL nên ai mở trang cũng tải; nhét thêm bảng tua
     cho 2.901 skill là bắt cả người không bao giờ mở chi tiết phải
     trả giá. */
  var kbCache = {};
  var dichCache = {};
  var hoSoHienTai = null;   /* skill đang mở — chặn kết quả nạp về muộn */

  /* ── BẢN DỊCH MÁY ─────────────────────────────────
     Ba mức, và người đọc PHẢI phân biệt được:

       1. dịch tay  — 42 skill chính chủ, đủ bốn mục kể cả "Với hệ
                      thống của bạn". Tôi đã đọc từng SKILL.md.
       2. dịch máy  — Haiku 4.5 dịch mô tả gốc. Ba mục, KHÔNG có
                      "Với hệ thống của bạn": mục đó đòi biết hệ này
                      có gì, máy sinh ra chỉ là bịa.
       3. bản gốc   — chưa dịch, để nguyên tiếng Anh.

     Trộn ba mức mà không gắn nhãn là kiểu lừa dối im lặng tệ nhất:
     người đọc tưởng mọi dòng tiếng Việt đều đã có người đọc qua. */
  function napDich(kho) {
    if (dichCache[kho]) return dichCache[kho];
    dichCache[kho] = fetch("./assets/data/dich/" + tenFileKb(kho))
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
    return dichCache[kho];
  }

  /* d.may = 1 → API dịch máy, chưa ai đọc. Không có cờ đó → tôi đọc
     mô tả rồi viết, và thường viết được cả mục "Với hệ thống của
     bạn" — thứ máy không thể có vì nó không biết hệ này có gì. */
  function veDichMay(d) {
    var may = !!d.may;
    var h = '<div class="hs-h">Nó là gì' +
      (may ? ' <span class="nhan-may">máy dịch</span>' : "") + "</div>" +
      '<p class="hs-p">' + esc(d.tom) + "</p>";
    if (d.lam && d.lam.length) {
      h += '<div class="hs-h" style="margin-top:12px">Làm được gì</div><ul class="hs-lam">' +
        d.lam.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
    }
    if (d.khi) h += '<div class="hs-h" style="margin-top:12px">Khi nào Claude tự bật nó</div>' +
      '<p class="hs-khi">' + esc(d.khi) + "</p>";
    if (d.ban) h += '<div class="hs-h" style="margin-top:12px">Với hệ thống của bạn</div>' +
      '<p class="hs-ban">' + esc(d.ban) + "</p>";
    h += '<div class="hs-h" style="margin-top:12px">Mô tả gốc</div>' +
      '<p class="hs-goc">' + esc(d.goc) + "</p>";
    h += '<p class="tua-luu">' + (may
      ? "Các mục trên do <b>máy dịch</b> từ chính mô tả gốc bên dưới — chưa ai đọc lại. " +
        "Cố ý thiếu mục “Với hệ thống của bạn”: mục đó đòi biết hệ thống của bạn có gì, " +
        "máy sinh ra chỉ có thể là bịa."
      : "Các mục trên viết tay từ mô tả gốc bên dưới, không phải máy dịch. " +
        "Khác với 42 skill chính chủ ở chỗ tôi đọc <b>mô tả</b> chứ chưa đọc hết " +
        "<code>SKILL.md</code> — nên đối chiếu bản gốc bên dưới nếu cần chắc.") + "</p>";
    return h;
  }
  function tenFileKb(kho) {
    return kho.replace(/\//g, "__").replace(/[^A-Za-z0-9_.-]/g, "_") + ".json";
  }
  function napKb(kho) {
    if (kbCache[kho]) return kbCache[kho];
    kbCache[kho] = fetch("./assets/data/kb/" + tenFileKb(kho))
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
    return kbCache[kho];
  }

  var NANG_TEN = { 3: "cần đọc kỹ", 2: "đáng chú ý", 1: "bình thường" };

  function veTua(t) {
    if (!t) {
      return '<p class="hs-thin">Chưa có bảng tua cho skill này — bản quét kế tiếp ' +
        "của bot sẽ dựng. Trong lúc đó xem thẳng SKILL.md ở mục Nguồn bên dưới.</p>";
    }
    var h = "";

    /* Các chặng. Đề mục cấp 3 thụt vào một bậc, để nhìn ra ngay đâu
       là chương chính đâu là mục con — giống mục lục của video. */
    if (t.buoc && t.buoc.length) {
      h += '<ol class="tua">' + t.buoc.map(function (b) {
        return '<li class="tua-b' + (b.c > 1 ? " tua-con" : "") + '">' + esc(b.t) + "</li>";
      }).join("") + "</ol>";
    } else {
      h += '<p class="hs-thin">SKILL.md không chia đề mục — đọc thẳng bản gốc.</p>';
    }

    /* Khối lệnh: thứ nó thật sự chạy. 0 khối = thuần hướng dẫn, và
       đó là thông tin quan trọng chứ không phải chỗ trống. */
    if (t.lenh && t.lenh.length) {
      h += '<div class="tua-lenh"><b>Lệnh nó chạy</b>' + t.lenh.map(function (x) {
        return '<code><i>' + esc(x.ng) + "</i>" + esc(x.d) + "</code>";
      }).join("") + "</div>";
    }

    /* Hồ sơ an toàn */
    var nang = 0;
    (t.co || []).forEach(function (c) { if (c.n > nang) nang = c.n; });
    h += '<div class="tua-at"><b>Nó đụng vào gì</b>';
    if (t.co && t.co.length) {
      h += '<ul class="tua-co">' + t.co.map(function (c) {
        return '<li class="n' + c.n + '">' + esc(c.t) + "</li>";
      }).join("") + "</ul>";
    } else {
      h += '<p class="tua-sach">Không thấy lệnh nào chạm tới mạng, hệ thống hay bí mật.</p>';
    }
    var d = [];
    if (t.chay && t.chay.length) d.push("<b>kèm " + t.chay.length + " file chạy được</b> (" +
      t.chay.slice(0, 4).map(esc).join(", ") + (t.chay.length > 4 ? "…" : "") + ")");
    else d.push("không kèm file chạy được");
    /* soTep là số ĐẾM THẬT; t.kem là danh sách đã cắt cho nhẹ. Lấy
       t.kem.length làm số tệp thì mọi skill lớn đều báo đúng "24" —
       sai giống hệt nhau nên gần như không ai nhận ra. */
    var n = t.soTep != null ? t.soTep : (t.kem ? t.kem.length : 0);
    if (n) d.push(n + " tệp trong thư mục skill");
    if (t.congCu) d.push("xin công cụ: <code>" + esc(t.congCu) + "</code>");
    if (t.dai) d.push(Math.round(t.dai / 1000) + "k ký tự");
    h += '<p class="hs-thin">' + d.join(" · ") + "</p>";

    /* Câu này KHÔNG được bỏ. Quét tĩnh chỉ thấy thứ được viết ra;
       skill là chỉ dẫn cho agent, agent có thể làm việc không nằm
       nguyên văn trong file. Gắn tick xanh ở đây là nói dối. */
    h += '<p class="tua-luu">Đây là quét tĩnh trong khối lệnh của SKILL.md, ' +
      "<b>không phải chứng nhận an toàn</b>. Không có dấu hiệu nào không có nghĩa là " +
      "vô hại — skill là chỉ dẫn cho agent, và agent có thể làm việc không viết thẳng " +
      "trong file. Cách chắc chắn duy nhất vẫn là đọc SKILL.md.</p>";
    h += "</div>";
    return h;
  }

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
      /* Chỗ này có thể được thay bằng bản dịch máy sau khi nạp xong
         (xem napDich bên dưới). Bản gốc hiện trước để panel mở ngay,
         không đợi mạng. */
      h += '<div class="hs" id="hsDich"><div class="hs-h">Mô tả gốc — chưa dịch</div>' +
        '<p class="hs-goc">' + esc(s.moTa) + "</p>" +
        '<p class="hs-p" style="margin-top:9px;font-size:12.4px;color:var(--ink-3)">' +
        "42 skill chính chủ của Anthropic được đọc và diễn giải tay, đủ bốn mục kể cả " +
        "<b>Với hệ thống của bạn</b>. Skill cộng đồng thì nhiều quá không đọc tay nổi.</p></div>";
    }

    /* Bảng tua đặt NGAY SAU phần mô tả, trước mọi thứ khác: đây là
       thứ trả lời "nó làm được gì" nhanh nhất, nên nó phải nằm chỗ
       mắt chạm tới đầu tiên chứ không nằm dưới đáy. */
    h += '<div class="hs"><div class="hs-h">Bảng tua — nó sẽ dắt agent đi qua đâu</div>' +
      '<div id="hsTua"><p class="hs-thin">Đang nạp…</p></div></div>';

    if (s.trungTen) {
      h += '<div class="hs"><div class="hs-h">Lưu ý khi tra</div>' +
        '<p class="hs-khi">Có skill khác <b>cùng tên</b> trong danh mục nhưng <b>nội dung khác</b>. ' +
        "Tàng Thư Các cố ý không gộp chúng — gộp theo tên sẽ xoá mất skill thật. " +
        "Đọc kỹ mô tả và kho nguồn trước khi cài.</p></div>";
    }

    if (s.banSao && s.banSao.length) {
      h += '<div class="hs"><div class="hs-h">Kho khác cũng có bản y hệt</div>' +
        '<div class="bansao">' + s.banSao.map(function (b) {
          return '<a href="https://github.com/' + esc(b.kho) + "/tree/main/" + esc(b.duong) +
            '" target="_blank" rel="noopener">' + esc(b.kho) + "/" + esc(b.duong) + "</a>";
        }).join("") + "</div>" +
        '<p class="hs-thin">Nội dung giống hệt bản chính, nên danh mục chỉ giữ một. ' +
        "Bản chính chọn theo: kho chính thức trước, rồi sao cao hơn, rồi đường dẫn gốc " +
        "(không phải thư mục gương hay bản dịch).</p></div>";
    }

    var repo = "https://github.com/" + s.kho;
    var duongDay = repo + "/tree/main/" + s.duong;
    /* Lệnh mặc định cài vào .claude/skills/ của DỰ ÁN, không phải
       ~/.claude/skills/. Bản cũ làm ngược: chép thẳng vào thư mục
       chung, tức skill lạ chưa đọc lập tức có hiệu lực ở mọi dự án
       kể cả những repo quan trọng. Thử trong một dự án nháp trước là
       thói quen đúng, nên mặc định phải là cái đó. */
    h += '<div class="hs"><div class="hs-h">Cách cài — thử ở dự án nháp trước</div>' +
      '<pre class="cai" id="lenhCai">git clone --depth 1 ' + esc(repo) + ".git /tmp/sk\n" +
      "mkdir -p .claude/skills\n" +
      "cp -r /tmp/sk/" + esc(s.duong) + " .claude/skills/</pre>" +
      '<button class="nut-chep" id="chepCai" type="button">Chép lệnh</button>' +
      '<p class="hs-p" style="margin-top:10px;font-size:12.4px;color:var(--ink-3)">' +
      "Lệnh trên cài vào <code>.claude/skills/</code> của <b>thư mục hiện tại</b> — chỉ dự án " +
      "đó thấy. Chạy nó trong một dự án nháp, mở Claude Code mà <b>đừng bật tự động duyệt " +
      "quyền</b>, rồi ra một yêu cầu chạm đúng skill để xem nó xin làm gì.<br><br>" +
      "Ưng rồi thì chép sang <code>~/.claude/skills/</code> để dùng cho mọi dự án. " +
      "Đừng làm bước đó trước — skill chưa đọc mà đặt ở thư mục chung là nó có hiệu lực " +
      "ngay cả trong những repo bạn không muốn nó đụng vào.</p></div>";

    h += '<div class="hs"><div class="hs-h">Nguồn</div><p class="hs-p">' +
      '<a href="' + esc(duongDay) + '" target="_blank" rel="noopener">Xem SKILL.md trên GitHub ↗</a><br>' +
      '<a href="' + esc(repo) + '" target="_blank" rel="noopener">Kho ' + esc(s.kho) + " ↗</a></p>" +
      (s.giayPhep ? '<p class="hs-p" style="margin-top:8px;font-size:12.2px;color:var(--ink-3)">Giấy phép: ' +
        esc(s.giayPhep) + "</p>" : "") + "</div>";

    $("#hosoTen").textContent = s.ten;
    $("#hosoTag").innerHTML =
      '<span class="the-nho" style="background:' + g.mau + '22;color:' + g.mau + '">' + esc(g.ten) + "</span>" +
      (s.chinhChu ? '<span class="the-nho the-ct">' + esc(VI.nhan.chinhChu) + "</span>" : "") +
      /* Chỉ mục đã biết skill này có bản dịch thì gắn nhãn "đã dịch"
         ngay, đừng hiện "nguyên bản gốc" rồi đổi lại sau khi tệp kho về
         — nháy một nhịp như vậy làm người đọc tưởng mình nhìn nhầm. */
      (dichCua(s) ? ""
        : tomVi(s) ? '<span class="the-nho the-tay">đã dịch</span>'
        : '<span class="the-nho the-cd">' + esc(VI.nhan.chuaDich) + "</span>") +
      '<span style="font-size:11.5px;color:var(--ink-3)">★ ' + so(s.sao) + "</span>";
    $("#hosoBody").innerHTML = h;

    /* Nạp bảng tua sau khi khung đã hiện: hồ sơ mở ra ngay, phần tua
       điền vào sau. Chờ mạng xong mới mở panel thì mỗi lần bấm skill
       lại đứng hình một nhịp.
       Kiểm lại id trước khi ghi: người dùng có thể đã bấm sang skill
       khác trong lúc chờ, ghi bừa là hiện bảng tua của skill trước. */
    hoSoHienTai = s.id;

    /* Bản dịch máy: chỉ nạp khi skill này CHƯA có bản dịch tay.
       Skill dịch tay không bao giờ bị bản máy đè lên — bản tay có
       đủ bốn mục và đã qua mắt người. */
    if (!d) {
      napDich(s.kho).then(function (kho) {
        if (hoSoHienTai !== s.id) return;
        var o = $("#hsDich");
        if (!o || $("#hoso").dataset.open !== "1") return;
        var t = kho && kho.skills ? kho.skills[s.id] : null;
        if (!t) return;                     /* chưa dịch — giữ nguyên bản gốc */
        t.goc = s.moTa;
        o.innerHTML = veDichMay(t);
        var n = $("#hosoTag .the-cd, #hosoTag .the-tay");
        if (n) {
          n.textContent = t.may ? "máy dịch" : "đã dịch";
          n.className = "the-nho " + (t.may ? "the-may" : "the-tay");
        }
      });
    }

    napKb(s.kho).then(function (kb) {
      /* So với biến NGOÀI hàm, không so s.id với chính nó: `s` nằm
         trong closure nên s.id không bao giờ đổi, phép so kiểu đó
         luôn đúng và không chặn được gì. */
      if (hoSoHienTai !== s.id) return;
      var o = $("#hsTua");
      if (!o || $("#hoso").dataset.open !== "1") return;
      var t = kb && kb.skills ? kb.skills.find(function (x) { return x.id === s.id; }) : null;
      o.innerHTML = veTua(t);
    });

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
     4. XU HƯỚNG
     GitHub KHÔNG có API cho số sao trong quá khứ, nên xu hướng là
     hiệu giữa hai mốc do chính build tự ghi mỗi lần chạy. Hệ quả:
     ngày đầu chưa có gì, số 24 giờ có sau một ngày, 7 ngày có sau
     một tuần. Nói thẳng chuyện đó thay vì hiện bảng trống khó hiểu.
     ══════════════════════════════════════════════════ */
  var KY = [
    { ma: "24h", ten: "24 giờ" },
    { ma: "7d", ten: "7 ngày" },
    { ma: "30d", ten: "30 ngày" }
  ];

  function mhXuHuong(host) {
    var X = D.xuHuong || {};
    if (!state.ky) state.ky = "24h";

    host.innerHTML = '<p class="giaithich">' + dan("xu-huong") + "</p>" +
      '<div class="tabs" id="tabs" role="tablist"></div>' +
      '<section class="khoi"><div class="loc"><span class="loc-lab">Mốc so sánh</span>' +
      '<span class="goiy" id="mocTin"></span><span class="dem" id="dem"></span></div>' +
      '<div class="bangwrap" id="bang"></div></section>';

    veTabs(KY.map(function (k) {
      var x = X[k.ma];
      return { ma: k.ma, ten: k.ten, so: x && x.du ? x.muc.length : 0 };
    }), state.ky, function (k) { state.ky = k; ve(); });

    var x = X[state.ky];
    if (!x || !x.du) {
      var moc = X.soMoc || 0;
      var tu = X.mocDau ? " Mốc đầu tiên ghi lúc " + ngayGio(X.mocDau) + "." : "";
      $("#bang").innerHTML = '<div class="trong" style="text-align:left;padding:22px 20px">' +
        "<b>Chưa đủ dữ liệu cho khoảng " + esc(nhanKy(state.ky)) + ".</b><br><br>" +
        "GitHub không cho biết một kho có bao nhiêu sao <i>trong quá khứ</i> — chỉ có số hiện tại. " +
        "Nên Tàng Thư Các phải tự ghi lại một mốc mỗi lần cập nhật, rồi lấy hiệu giữa hai mốc.<br><br>" +
        "Hiện đã ghi <b>" + moc + " mốc</b>." + esc(tu) +
        " Cập nhật chạy 4 lần mỗi ngày, nên số <b>24 giờ</b> có sau khoảng một ngày, " +
        "<b>7 ngày</b> sau một tuần, <b>30 ngày</b> sau một tháng.</div>";
      $("#mocTin").textContent = "";
      $("#dem").textContent = moc + " mốc đã ghi";
      return;
    }

    $("#mocTin").textContent = "so với mốc cách đây " + x.tuoiGio + " giờ";
    $("#dem").textContent = x.muc.length + " kho đổi số sao";

    var t = el("table", "bang");
    t.innerHTML = '<thead><tr><th class="l">#</th><th class="l">Kho</th>' +
      "<th>Sao thêm</th><th>Tăng</th><th>Sao hiện tại</th><th>Skill</th></tr></thead>";
    var tb = el("tbody");
    var demSkill = {};
    SK.forEach(function (y) { demSkill[y.kho] = (demSkill[y.kho] || 0) + 1; });

    x.muc.forEach(function (m, i) {
      var r = el("tr");
      var k = KHO.filter(function (y) { return y.id === m.id; })[0] || {};
      r.innerHTML =
        '<td class="l hang">' + (i + 1) + "</td>" +
        '<td class="l"><a class="kho-ten" href="https://github.com/' + esc(m.id) +
          '" target="_blank" rel="noopener">' + esc(m.id) + "</a>" +
          (k.moTa ? '<span class="kho-mo">' + esc(k.moTa) + "</span>" : "") + "</td>" +
        '<td class="' + (m.them >= 0 ? "len" : "xuong") + '"><b>' +
          (m.them >= 0 ? "+" : "") + so(m.them) + "</b></td>" +
        '<td class="' + (m.them >= 0 ? "len" : "xuong") + '">' +
          (typeof m.pt === "number" ? (m.pt >= 0 ? "+" : "") + (m.pt * 100).toFixed(2) + "%" : "—") + "</td>" +
        "<td>" + so(m.sao) + "</td>" +
        "<td>" + (demSkill[m.id] != null ? demSkill[m.id] : '<span class="hang">chưa quét</span>') + "</td>";
      tb.appendChild(r);
    });
    t.appendChild(tb);
    $("#bang").innerHTML = "";
    $("#bang").appendChild(t);
  }

  function nhanKy(ma) {
    for (var i = 0; i < KY.length; i++) if (KY[i].ma === ma) return KY[i].ten;
    return ma;
  }
  function ngayGio(sec) {
    var d = new Date(sec * 1000), p = function (n) { return String(n).padStart(2, "0"); };
    return p(d.getUTCDate()) + "/" + p(d.getUTCMonth() + 1) + " " + p(d.getUTCHours()) + ":" + p(d.getUTCMinutes()) + " UTC";
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
      b.innerHTML = esc(t.ten) + (t.so ? '<span class="n">' + t.so + "</span>" : "");
      b.addEventListener("click", function () { doi(t.ma); });
      host.appendChild(b);
    });
  }

  /* ══════════════════════════════════════════════════
     5. LỊCH SỬ CẬP NHẬT
     Nhật ký của chính Tàng Thư Các: mỗi lần cập nhật đã thêm/bớt
     kho nào, skill nào. Chỉ ghi lần nào CÓ đổi thật — lần chạy
     không đổi gì mà vẫn ghi một dòng thì nhật ký thành rác.
     ══════════════════════════════════════════════════ */
  function mhLichSu(host) {
    var DS = D.doiGanNhat || [];
    host.innerHTML = '<p class="giaithich">' + dan("lich-su") + "</p>" +
      '<section class="khoi"><div class="khoi-dinh"><h2>Những lần có thay đổi</h2>' +
      '<span class="khoi-n">' + DS.length + " lần gần nhất</span></div>" +
      '<div id="ds"></div></section>';

    if (!DS.length) {
      $("#ds").innerHTML = '<p class="trong">Chưa ghi được lần đổi nào. ' +
        "Nhật ký bắt đầu từ lần cập nhật đầu tiên sau khi tính năng này lên.</p>";
      return;
    }

    $("#ds").innerHTML = DS.map(function (x) {
      var d = [];
      if (x.khoThem && x.khoThem.length) {
        d.push('<div class="ls-nhom"><span class="ls-dau len">+' + x.khoThem.length + " kho</span>" +
          '<div class="ls-ds">' + x.khoThem.slice(0, 12).map(function (k) {
            return '<a href="https://github.com/' + esc(k) + '" target="_blank" rel="noopener">' + esc(k) + "</a>";
          }).join("") + (x.khoThem.length > 12 ? '<span class="ls-them">…và ' + (x.khoThem.length - 12) + " kho nữa</span>" : "") + "</div></div>");
      }
      if (x.khoBot && x.khoBot.length) {
        d.push('<div class="ls-nhom"><span class="ls-dau xuong">−' + x.khoBot.length + " kho</span>" +
          '<div class="ls-ds">' + x.khoBot.slice(0, 12).map(function (k) {
            return "<span>" + esc(k) + "</span>";
          }).join("") + "</div></div>");
      }
      if (x.soSkillThem) {
        d.push('<div class="ls-nhom"><span class="ls-dau len">+' + x.soSkillThem + " skill</span>" +
          '<div class="ls-ds">' + (x.skillThem || []).slice(0, 14).map(function (y) {
            return "<span><b>" + esc(y.ten) + "</b> " + esc(y.kho) + "</span>";
          }).join("") + (x.soSkillThem > 14 ? '<span class="ls-them">…và ' + (x.soSkillThem - 14) + " skill nữa</span>" : "") + "</div></div>");
      }
      if (x.soSkillBot) {
        d.push('<div class="ls-nhom"><span class="ls-dau xuong">−' + x.soSkillBot + " skill</span>" +
          '<div class="ls-ds">' + (x.skillBot || []).slice(0, 14).map(function (y) {
            return "<span><b>" + esc(y.ten) + "</b> " + esc(y.kho) + "</span>";
          }).join("") + "</div></div>");
      }
      return '<div class="ls-muc">' +
        '<div class="ls-dinh"><b>' + esc(ngayGio(x.luc)) + "</b>" +
        '<span class="ls-tong">' + so(x.tongSkill) + " skill · " + x.tongKho + " kho</span>" +
        (x.suyGiam ? '<span class="the-nho the-cd">lần chạy suy giảm</span>' : "") + "</div>" +
        d.join("") + "</div>";
    }).join("");
  }

  /* ══════════════════════════════════════════════════
     ĐIỀU PHỐI
     ══════════════════════════════════════════════════ */
  var MH = {
    "tong-quan": mhTongQuan, "danh-muc": mhDanhMuc, "xep-hang": mhXepHang,
    "xu-huong": mhXuHuong, "lich-su": mhLichSu
  };

  function ve() {
    var t = VI.muc[state.muc] || { ten: state.muc };
    $("#tieu").textContent = t.ten;
    document.title = "Tàng Thư Các · " + t.ten;
    veBen();
    (MH[state.muc] || MH["tong-quan"])($("#than"));
    if (TT && TT.them) TT.them($("#than"), state.muc);
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
    if (ma !== state.muc) { state.muc = ma; state.nhom = "all"; state.nguon = "all"; state.ky = "24h"; }
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
    napTom();          /* sau doiTuyen: trang hiện ngay, dịch về sau */
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
