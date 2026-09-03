/* ═══════════════════════════════════════════════════════
   CÔNG BỘ — bộ đồ nghề, Việt hoá từ tools.l2beat.com.

   Dữ liệu: window.CB_DATA        (chỉ mục, tự sinh)
            window.CB_DIFF        (nguyên văn diff, NẠP THEO YÊU CẦU)
   Giải mã: window.CB_DECODE      (chạy hẳn trong trình duyệt)

   Ba công cụ:
     #/giai-ma   Giải mã lời gọi  — tự viết, không cần máy chủ
     #/nhat-ky   Nhật ký đổi thay — hợp đồng on-chain đổi những gì
     #/kinh-lup  Kính lúp hồ sơ   — dự án nào còn thiếu hạng mục nào

   Định tuyến bằng hash vì trang này còn được pin lên IPFS, mà
   gateway IPFS không có server để rewrite URL.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.CB_DATA, VI = window.CB_VI;
  if (!D || !VI) return;

  var LOGO = "../do-sat-vien/assets/logos/";
  var state = { muc: "giai-ma", q: "", duAn: "all" };
  /* Lớp tri thức nền — knowledge-os/sinh.mjs ghi ra assets/js/v/tri-thuc.js,
     mang cả dữ liệu lẫn hàm vẽ nên khuôn giống hệt mọi cung khác. Nó KHÔNG
     đụng con số nào; việc duy nhất là nói phòng này đang đo VIỆC KINH TẾ
     gì, và mỗi câu giải nghĩa đến từ đâu. Thiếu file thì phòng vẫn vẽ đủ. */
  var TT = window.TRI_THUC || null;


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
  function usd(v) {
    if (v == null || isNaN(v)) return "—";
    if (v >= 1e9) return "$" + (v / 1e9).toFixed(2) + "b";
    if (v >= 1e6) return "$" + Math.round(v / 1e6) + "m";
    if (v >= 1e3) return "$" + Math.round(v / 1e3) + "k";
    return "$" + Math.round(v);
  }
  function ngay(ts) {
    var d = new Date(ts * 1000), p = function (n) { return String(n).padStart(2, "0"); };
    return p(d.getUTCDate()) + "/" + p(d.getUTCMonth() + 1) + " " + p(d.getUTCHours()) + ":" + p(d.getUTCMinutes());
  }
  /* Bản quét của L2BEAT không phải lúc nào cũng kèm tên hợp đồng và địa
     chỉ: 15/450 dòng nhật ký thiếu tên, 14/450 thiếu địa chỉ. Đó là hụt
     Ở NGUỒN, không phải hụt ở đường ống của repo này — và hai chuyện đó
     phải đọc ra khác nhau. Một dấu gạch thì không phân biệt được; hai
     chữ thì có, và `title` nói luôn hụt từ đâu. */
  function thieu(chu, viSao) {
    return '<i class="khuyet" title="' + esc(viSao) + '">' + esc(chu) + "</i>";
  }
  function rutGon(a) { return a ? esc(a.slice(0, 8) + "…" + a.slice(-6)) : thieu("không kèm", "Bản quét L2BEAT cho dòng đổi này không kèm địa chỉ hợp đồng."); }

  /* Bộ lọc cắt hết thì bảng CŨ vẫn dựng ra: đủ hàng tiêu đề, thân rỗng —
     trang trông như vừa hỏng chứ không như vừa lọc. Ô đếm bên trên có ghi
     "0 / 450", nhưng đó là một con số chứ không phải một câu: nó không nói
     bộ lọc NÀO đang cắt, cũng không nói cách gỡ. Cả ba thứ phải nằm đúng
     chỗ đáng lẽ có dữ liệu, vì đó là chỗ người ta đang nhìn. */
  function khongKhop(dau, dieuKien, loiRa) {
    var ds = dieuKien.filter(Boolean);
    var p = el("p", "trong");
    p.innerHTML = dau + " " + (ds.length ? ds.join(" và ") : "bộ lọc hiện tại") + ". " + loiRa;
    return p;
  }

  /* Logo dùng chung với Đô Sát Viện — 200 file đã tải sẵn ở đó,
     chép sang đây là nhân đôi 1 MB trong repo mà chẳng được gì. */
  function duongLogo(id) {
    var p = (window.DSV_LOGO_MAP || {})[id];
    if (p) return LOGO + p;
    var b = (window.CB_LOGO_BU || {})[id];
    return b ? "assets/logos/" + b : null;   // ảnh tải bù cho dự án đã ngừng
  }
  function logoHTML(id, ten) {
    var p = duongLogo(id);
    if (p) return '<img src="' + esc(p) + '" alt="" loading="lazy" width="19" height="19">';
    return '<span class="khonglogo">' + esc(String(ten || id || "?").trim().charAt(0).toUpperCase()) + "</span>";
  }

  /* ══════════════════════════════════════════════════
     THANH BÊN
     ══════════════════════════════════════════════════ */
  var CAY = [
    { nhom: "Đồ nghề", muc: ["giai-ma", "xuong-huy-hieu"] },
    { nhom: "Theo dõi", muc: ["nhat-ky", "kinh-lup"] },
    { nhom: "Ngoài trang", muc: ["di-noi-khac"] }
  ];
  var IC = {
    "giai-ma": '<path d="M8 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h2M16 4h2a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-2"/><path d="M10 9.5 12 12l-2 2.5M13.5 14.5h1.5"/>',
    "nhat-ky": '<path d="M4.5 5.5h15M4.5 12h15M4.5 18.5h15"/><circle cx="8" cy="5.5" r="1.8" fill="currentColor"/><circle cx="15" cy="12" r="1.8" fill="currentColor"/><circle cx="10" cy="18.5" r="1.8" fill="currentColor"/>',
    "kinh-lup": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.6-4.6"/><path d="M8 10.5h5M10.5 8v5"/>',
    "xuong-huy-hieu": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/>' +
      '<rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/>',
    "di-noi-khac": '<path d="M14 4h6v6"/><path d="M20 4l-9 9"/>' +
      '<path d="M18 14v5a1.8 1.8 0 0 1-1.8 1.8H5A1.8 1.8 0 0 1 3.2 19V7.8A1.8 1.8 0 0 1 5 6h5"/>'
  };
  function demMuc(ma) {
    if (ma === "nhat-ky") return (D.nhatKy || []).length;
    if (ma === "kinh-lup") return (D.kinhLup || []).length;
    if (ma === "xuong-huy-hieu") return (D.kinhLup || []).length;
    if (ma === "di-noi-khac") return NGOAI.length;
    return null;
  }
  function veBen() {
    var host = $("#benMuc");
    host.innerHTML = "";
    CAY.forEach(function (g) {
      var lab = el("div", "blab");
      lab.textContent = g.nhom;
      host.appendChild(lab);
      g.muc.forEach(function (ma) {
        var t = VI.muc[ma] || { ten: ma };
        var a = el("a", "bmuc");
        a.href = "#/" + ma;
        a.title = t.y || t.ten;
        if (state.muc === ma) a.setAttribute("aria-current", "page");
        var n = demMuc(ma);
        a.innerHTML = '<span class="bic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
          'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' + (IC[ma] || "") + "</svg></span>" +
          "<span>" + esc(t.ten) + "</span>" + (n != null ? '<span class="bn">' + n + "</span>" : "");
        host.appendChild(a);
      });
    });
  }

  function dan(ma) {
    var t = VI.muc[ma];
    if (!t) return "";
    return "<b>" + esc(t.ten) + "</b>" + (t.y ? " — " + esc(t.y) : "") +
      (t.vn ? '<span class="vn">' + esc(t.vn) + "</span>" : "");
  }

  /* ══════════════════════════════════════════════════
     1. GIẢI MÃ LỜI GỌI
     ══════════════════════════════════════════════════ */
  var MAU = "0xa9059cbb0000000000000000000000005b38da6a701c568545dcfcb03fcb875f56beddc40000000000000000000000000000000000000000000000000de0b6b3a7640000";

  function mhGiaiMa(host) {
    host.innerHTML =
      '<p class="giaithich">' + dan("giai-ma") + "</p>" +
      '<section class="khoi"><div class="form">' +
        '<label class="nhan" for="cd">Dữ liệu lời gọi (calldata)</label>' +
        '<textarea class="o" id="cd" spellcheck="false" placeholder="0x…"></textarea>' +
        '<label class="nhan" style="margin-top:14px" for="ky">Chữ ký hàm — để trống thì tự tra</label>' +
        '<input class="o" id="ky" spellcheck="false" placeholder="transfer(address,uint256)">' +
        '<div class="hang-nut">' +
          '<button class="nut" id="bGiai" type="button">Giải mã</button>' +
          '<button class="nut-phu" id="bMau" type="button">Dán thử một mẫu</button>' +
          '<button class="nut-phu" id="bXoa" type="button">Xoá</button>' +
          '<span class="goiy">' + VI.soHamSan + ' hàm tra sẵn, không cần mạng</span>' +
        "</div>" +
      '</div><div class="kq" id="kq" hidden></div></section>';

    $("#bMau").addEventListener("click", function () { $("#cd").value = MAU; $("#ky").value = ""; giai(); });
    $("#bXoa").addEventListener("click", function () {
      $("#cd").value = ""; $("#ky").value = ""; $("#kq").hidden = true;
    });
    $("#bGiai").addEventListener("click", giai);
    $("#cd").addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") giai();
    });
  }

  function giai() {
    var kq = $("#kq");
    kq.hidden = false;
    var g = window.CB_DECODE.giaiMa($("#cd").value);
    if (g.loi) { kq.innerHTML = '<div class="kq-loi">' + esc(g.loi) + "</div>"; return; }

    var tay = $("#ky").value.trim();
    kq.innerHTML = '<p class="hs-p">Đang tra tên hàm…</p>';

    var xong = function (ky, tu) {
      var head = '<div class="kq-dinh">' +
        '<span class="kq-ten">' + esc(ky ? window.CB_DECODE.tachKieu(ky).ten : "hàm chưa rõ") + "</span>" +
        '<span class="kq-sel">' + esc(g.sel) + "</span>" +
        (tu ? '<span class="kq-tu">tra từ ' + esc(tu) + "</span>" : "") +
      "</div>";
      if (g.canhBao) {
        kq.innerHTML = head + '<div class="kq-loi">' + esc(g.canhBao) + "</div>";
        return;
      }
      if (!ky) {
        kq.innerHTML = head +
          '<div class="kq-loi">Không tra được tên hàm cho selector này. Nếu bạn biết chữ ký, ' +
          "điền vào ô bên trên rồi bấm Giải mã lại — phần tham số sẽ đọc được ngay.</div>" +
          '<p class="hs-p" style="margin-top:12px">Phần tham số thô: <b>' + g.soTu +
          "</b> từ 32 byte.</p>";
        return;
      }
      var r = window.CB_DECODE.docThamSo(ky, g.than);
      var rows = r.thamSo.map(function (p, i) {
        var v;
        if (p.v === null) v = '<span class="ts-chua">' + esc(p.ghi || "chưa đọc được") + "</span>";
        else if (Array.isArray(p.v)) v = "<ol>" + p.v.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ol>";
        else v = esc(p.v);
        return "<tr><td class=\"ts-i\">" + i + '</td><td class="ts-k">' + esc(p.kieu) + "</td>" +
          '<td class="ts-v">' + v +
          (p.ghi && p.v !== null ? '<span class="ts-ghi">' + esc(p.ghi) + "</span>" : "") +
          '<span class="ts-tho">từ thô: ' + esc(p.tho) + "</span></td></tr>";
      }).join("");
      kq.innerHTML = head + '<div class="kq-ky">' + esc(ky) + "</div>" +
        (r.thamSo.length
          ? '<table class="ts"><thead><tr><th>#</th><th>Kiểu</th><th>Giá trị</th></tr></thead><tbody>' + rows + "</tbody></table>"
          : '<p class="hs-p">Hàm này không có tham số.</p>');
    };

    if (tay) { xong(tay, "bạn tự điền"); return; }
    window.CB_DECODE.traTen(g.sel).then(function (o) { xong(o.ky, o.tu); });
  }

  /* ══════════════════════════════════════════════════
     2. NHẬT KÝ ĐỔI THAY
     ══════════════════════════════════════════════════ */
  function mhNhatKy(host) {
    var NK = D.nhatKy || [];
    if (!NK.length) {
      host.innerHTML = '<p class="giaithich">' + dan("nhat-ky") + "</p>" +
        '<section class="khoi"><p class="trong">Chưa lấy được nhật ký.</p></section>';
      return;
    }
    host.innerHTML = '<p class="giaithich">' + dan("nhat-ky") + "</p>" +
      '<section class="khoi"><div class="loc"><span class="loc-lab">Dự án</span>' +
      '<div class="chips" id="chips" style="display:flex;gap:6px;flex-wrap:wrap"></div>' +
      '<span class="dem" id="dem"></span></div>' +
      '<div class="bangwrap" id="bang"></div></section>';

    /* chỉ hiện chip cho vài dự án đổi nhiều nhất, còn lại dồn vào ô tìm */
    var dem = {};
    NK.forEach(function (x) { dem[x.duAn] = (dem[x.duAn] || 0) + 1; });
    var top = Object.entries(dem).sort(function (a, b) { return b[1] - a[1]; }).slice(0, 7);

    var wrap = $("#chips");
    var all = el("button", "chip");
    all.type = "button";
    all.textContent = "Tất cả";
    all.setAttribute("aria-pressed", String(state.duAn === "all"));
    all.addEventListener("click", function () { state.duAn = "all"; ve(); });
    wrap.appendChild(all);
    top.forEach(function (e) {
      var b = el("button", "chip");
      b.type = "button";
      b.innerHTML = esc(e[0]) + '<span class="n">' + e[1] + "</span>";
      b.setAttribute("aria-pressed", String(state.duAn === e[0]));
      b.addEventListener("click", function () { state.duAn = e[0]; ve(); });
      wrap.appendChild(b);
    });

    var q = norm(state.q.trim());
    var hang = NK.filter(function (x) {
      if (state.duAn !== "all" && x.duAn !== state.duAn) return false;
      if (q && norm([x.duAn, x.hopDong, x.diaChi].join(" ")).indexOf(q) === -1) return false;
      return true;
    });
    $("#dem").textContent = hang.length + " / " + NK.length + " thay đổi";

    var t = el("table", "bang");
    t.innerHTML = "<thead><tr><th class=\"l\">Dự án</th><th class=\"l\">Hợp đồng</th>" +
      "<th class=\"l\">Địa chỉ</th><th>Dòng đổi</th><th class=\"l\">Lúc</th></tr></thead>";
    var tb = el("tbody");
    hang.slice(0, 300).forEach(function (x) {
      var i = NK.indexOf(x);
      var r = el("tr");
      r.tabIndex = 0;
      r.innerHTML =
        '<td class="l"><span class="duan">' + logoHTML(x.duAn, x.duAn) + "<b>" + esc(x.duAn) + "</b></span></td>" +
        '<td class="l hd">' + (x.hopDong ? esc(x.hopDong)
             : thieu("không tên", "Bản quét L2BEAT không đặt tên cho hợp đồng bị đổi ở dòng này.")) +
          (x.chuoi ? "<i>" + esc(x.chuoi) + "</i>" : "") + "</td>" +
        '<td class="l dd">' + rutGon(x.diaChi) + "</td>" +
        '<td><span class="tm">+' + x.them + '</span> <span class="bt">−' + x.bot + "</span></td>" +
        '<td class="l luc">' + esc(ngay(x.luc)) + "</td>";
      r.addEventListener("click", function () { moDiff(i); });
      r.addEventListener("keydown", function (e) { if (e.key === "Enter") moDiff(i); });
      tb.appendChild(r);
    });
    t.appendChild(tb);
    $("#bang").innerHTML = "";
    if (!hang.length) {
      /* Lối ra phải kể đúng những bộ lọc ĐANG bật. Bảo "bấm Tất cả" khi
         người ta chưa hề chọn dự án nào là chỉ sang một cái nút không
         liên quan, và một câu hướng dẫn sai chỗ thì tệ hơn không có câu
         nào — nó bắt người đọc tự kiểm chứng cả phần còn lại. */
      var cD = state.duAn !== "all";
      $("#bang").appendChild(khongKhop("Không dòng đổi nào khớp", [
        cD ? "dự án <b>" + esc(state.duAn) + "</b>" : null,
        q ? "chữ tìm <b>" + esc(state.q.trim()) + "</b>" : null
      ], (cD && q ? "Bấm <b>Tất cả</b> ở trên và xoá ô tìm"
        : cD ? "Bấm <b>Tất cả</b> ở trên"
        : "Xoá ô tìm ở đỉnh trang") + " để xem lại " + NK.length + " thay đổi."));
      return;
    }
    $("#bang").appendChild(t);
    if (hang.length > 300) {
      var p = el("p", "trong");
      p.textContent = "Hiện 300 mục đầu. Lọc theo dự án hoặc tìm để thu hẹp.";
      $("#bang").appendChild(p);
    }
  }

  /* tô màu diff: + xanh, - đỏ, dòng tiêu đề vàng */
  function toDiff(s) {
    return s.replace(/^```diff\n?/, "").replace(/```$/, "").split("\n").map(function (d) {
      var c = "d-tt";
      if (/^\s*\+\+\+/.test(d)) c = "d-hd";
      else if (/^\s*\+/.test(d)) c = "d-them";
      else if (/^\s*---/.test(d)) c = "d-hd";
      else if (/^\s*-/.test(d)) c = "d-bot";
      else if (/^\s*contract\s/.test(d)) c = "d-hd";
      return '<span class="' + c + '">' + esc(d || " ") + "</span>";
    }).join("");
  }

  function moDiff(i) {
    var x = (D.nhatKy || [])[i];
    if (!x) return;
    var ve2 = function () {
      var d = (window.CB_DIFF || [])[i];
      var body = d
        ? '<pre class="diff">' + toDiff(d) + "</pre>" +
          (x.daiGoc ? '<p class="cat">Diff gốc dài ' + Math.round(x.daiGoc / 1024) +
            " KB, đã cắt còn 6 KB cho nhẹ trang. Bản đầy đủ xem ở L2BEAT.</p>" : "")
        : '<p class="trong">Không nạp được nguyên văn diff.</p>';
      $("#hosoBody").innerHTML =
        '<div class="hs"><div class="hs-h">Thay đổi</div>' +
        '<p class="hs-p">Hợp đồng <b>' + esc(x.hopDong || "—") + "</b>" +
        (x.diaChi ? ' tại <b class="mono">' + esc(x.diaChi) + "</b>" : "") +
        (x.chuoi ? " trên chuỗi <b>" + esc(x.chuoi) + "</b>" : "") + "</p></div>" +
        '<div class="hs"><div class="hs-h">Nguyên văn diff của L2BEAT</div>' + body + "</div>" +
        '<div class="hs"><div class="hs-h">Nguồn</div><p class="hs-p">' +
        (x.diaChi ? '<a href="https://etherscan.io/address/' + esc(x.diaChi) +
          '" target="_blank" rel="noopener">Xem hợp đồng trên Etherscan ↗</a><br>' : "") +
        '<a href="https://l2beat.com/scaling/projects/' + encodeURIComponent(x.duAn) +
        '" target="_blank" rel="noopener">Hồ sơ dự án trên L2BEAT ↗</a></p></div>';
    };
    $("#hosoTen").textContent = x.duAn;
    $("#hosoTag").innerHTML = "<span>" + esc(ngay(x.luc)) + "</span>" +
      '<span class="tm">+' + x.them + '</span><span class="bt">−' + x.bot + "</span>";
    $("#hosoBody").innerHTML = '<p class="trong">Đang nạp diff…</p>';
    $("#hoso").dataset.open = "1";
    $("#scrim").dataset.open = "1";
    $("#hosoDong").focus();
    napDiff(function () { ve2(); });
  }

  var dangNapDiff = null;
  function napDiff(xong) {
    if (window.CB_DIFF) return xong();
    if (dangNapDiff) { dangNapDiff.push(xong); return; }
    dangNapDiff = [xong];
    var s = document.createElement("script");
    s.src = "assets/js/v/nhat-ky.js";
    s.onload = s.onerror = function () {
      var ds = dangNapDiff; dangNapDiff = null;
      ds.forEach(function (f) { f(); });
    };
    document.head.appendChild(s);
  }

  /* ══════════════════════════════════════════════════
     3. KÍNH LÚP HỒ SƠ
     ══════════════════════════════════════════════════ */
  function mhKinhLup(host) {
    var KL = D.kinhLup || [];
    if (!KL.length) {
      host.innerHTML = '<p class="giaithich">' + dan("kinh-lup") + "</p>" +
        '<section class="khoi"><p class="trong">Chưa lấy được kính lúp hồ sơ.</p></section>';
      return;
    }
    var tong = (D.hangMuc || []).length;
    var day = KL.filter(function (p) { return !p.thieu.length; }).length;

    host.innerHTML = '<p class="giaithich">' + dan("kinh-lup") + "</p>" +
      '<section class="khoi"><div class="khoi-dinh"><h2>Hồ sơ đủ cả ' + tong + " hạng mục</h2>" +
      '<span class="khoi-n">' + day + " / " + KL.length + " dự án</span></div>" +
      '<div class="loc"><span class="loc-lab">' + tong + " hạng mục</span>" +
      '<span class="dem" id="dem"></span></div>' +
      '<div class="bangwrap" id="bang"></div></section>';

    var q = norm(state.q.trim());
    var hang = q ? KL.filter(function (p) { return norm(p.ten + " " + (p.dang || "")).indexOf(q) !== -1; }) : KL;
    $("#dem").textContent = hang.length + " / " + KL.length + " dự án";

    var t = el("table", "bang");
    t.innerHTML = '<thead><tr><th class="l">#</th><th class="l">Dự án</th>' +
      '<th class="l">Dạng</th><th class="l">Hạng mục</th><th>Đủ</th><th>Tài sản</th></tr></thead>';
    var tb = el("tbody");
    hang.forEach(function (p, i) {
      var r = el("tr");
      r.tabIndex = 0;
      var o = (D.hangMuc || []).map(function (h) {
        return '<span data-c="' + (p.co.indexOf(h) !== -1 ? 1 : 0) + '" title="' +
          esc((VI.hangMuc[h] || {}).ten || h) + '"></span>';
      }).join("");
      var pt = Math.round(p.co.length / tong * 100);
      r.innerHTML =
        '<td class="l" style="color:var(--ink-3)">' + (i + 1) + "</td>" +
        '<td class="l"><span class="duan">' + logoHTML(p.id, p.ten) + "<b>" + esc(p.ten) + "</b></span></td>" +
        '<td class="l" style="color:var(--ink-3);font-size:12px">' +
          (p.dang ? esc(p.dang) : thieu("chưa phân loại", "L2BEAT chưa xếp dự án này vào dạng nào.")) + "</td>" +
        '<td class="l"><span class="hm">' + o + "</span></td>" +
        '<td class="tyle"><b>' + p.co.length + "</b><i>/" + tong + "</i>" +
        '<div class="thanh"><span style="width:' + pt + '%"></span></div></td>' +
        "<td>" + usd(p.tvs) + "</td>";
      r.addEventListener("click", function () { moKinhLup(p); });
      r.addEventListener("keydown", function (e) { if (e.key === "Enter") moKinhLup(p); });
      tb.appendChild(r);
    });
    t.appendChild(tb);
    $("#bang").innerHTML = "";
    if (!hang.length) {
      $("#bang").appendChild(khongKhop("Không dự án nào khớp", [
        q ? "chữ tìm <b>" + esc(state.q.trim()) + "</b>" : null
      ], "Xoá ô tìm ở đỉnh trang để xem lại " + KL.length + " dự án."));
      return;
    }
    $("#bang").appendChild(t);
  }

  function moKinhLup(p) {
    var tong = (D.hangMuc || []).length;
    $("#hosoTen").textContent = p.ten;
    $("#hosoTag").innerHTML = "<span>" + esc(p.dang || "—") + "</span><span>" +
      p.co.length + "/" + tong + " hạng mục</span><span>" + usd(p.tvs) + "</span>";
    $("#hosoBody").innerHTML =
      '<div class="hs"><div class="hs-h">Từng hạng mục hồ sơ</div><div class="hmlist">' +
      (D.hangMuc || []).map(function (h) {
        var co = p.co.indexOf(h) !== -1;
        var g = VI.hangMuc[h] || { ten: h };
        return '<div><em data-c="' + (co ? 1 : 0) + '"></em><span>' + esc(g.ten) +
          (g.y ? "<i> — " + esc(g.y) + "</i>" : "") + "</span></div>";
      }).join("") + "</div></div>" +
      '<div class="hs"><div class="hs-h">Nguồn</div><p class="hs-p">' +
      '<a href="https://l2beat.com/scaling/projects/' + encodeURIComponent(p.slug) +
      '" target="_blank" rel="noopener">Hồ sơ dự án trên L2BEAT ↗</a></p></div>';
    $("#hoso").dataset.open = "1";
    $("#scrim").dataset.open = "1";
    $("#hosoDong").focus();
  }


  /* ══════════════════════════════════════════════════
     4. XƯỞNG HUY HIỆU
     Xếp logo thành một tấm rồi tải về PNG. Vẽ bằng canvas,
     198 logo đã nằm sẵn trong repo nên không gọi mạng lần nào.
     ══════════════════════════════════════════════════ */
  var xh = { tang: { L2: true, L3: false }, ngung: false, co: 64, cot: 10, bo: "" };

  function mhXuong(host) {
    host.innerHTML =
      '<p class="giaithich">' + dan("xuong-huy-hieu") + "</p>" +
      '<section class="khoi"><div class="form">' +
        '<div class="hang-nut" style="margin-top:0">' +
          '<button class="chip" id="xL2" type="button">Tầng 2</button>' +
          '<button class="chip" id="xL3" type="button">Tầng 3</button>' +
          '<button class="chip" id="xNg" type="button">Kể cả đã ngừng</button>' +
        "</div>" +
        '<div class="hang-nut">' +
          '<label class="nhan" style="margin:0">Cỡ <b id="xCoN"></b>px</label>' +
          '<input type="range" id="xCo" min="24" max="128" step="8">' +
          '<label class="nhan" style="margin:0 0 0 10px">Số cột <b id="xCotN"></b></label>' +
          '<input type="range" id="xCot" min="4" max="20" step="1">' +
        "</div>" +
        '<label class="nhan" style="margin-top:12px" for="xBo">Bỏ bớt — gõ slug, cách nhau bằng dấu phẩy</label>' +
        '<input class="o" id="xBo" spellcheck="false" placeholder="base, arbitrum">' +
        '<div class="hang-nut">' +
          '<button class="nut" id="xTai" type="button">Tải về PNG</button>' +
          '<span class="goiy" id="xDem"></span>' +
        "</div>" +
      "</div>" +
      '<div class="kq"><div id="xLuoi"></div></div></section>';

    function nutTang(id, k) {
      var b = $(id);
      b.setAttribute("aria-pressed", String(xh.tang[k]));
      b.addEventListener("click", function () { xh.tang[k] = !xh.tang[k]; ve(); });
    }
    nutTang("#xL2", "L2");
    nutTang("#xL3", "L3");
    var bn = $("#xNg");
    bn.setAttribute("aria-pressed", String(xh.ngung));
    bn.addEventListener("click", function () { xh.ngung = !xh.ngung; ve(); });

    $("#xCo").value = xh.co; $("#xCoN").textContent = xh.co;
    $("#xCot").value = xh.cot; $("#xCotN").textContent = xh.cot;
    $("#xBo").value = xh.bo;
    $("#xCo").addEventListener("input", function (e) { xh.co = +e.target.value; ve(); });
    $("#xCot").addEventListener("input", function (e) { xh.cot = +e.target.value; ve(); });
    $("#xBo").addEventListener("input", function (e) { xh.bo = e.target.value; ve(); });
    $("#xTai").addEventListener("click", taiPNG);

    var ds = chonLogo();
    $("#xDem").textContent = ds.length + " huy hiệu";
    $("#xLuoi").innerHTML = ds.length
      ? '<div class="luoi-hh" style="grid-template-columns:repeat(' + xh.cot +
        ",minmax(0,1fr))\">" + ds.map(function (p) {
          return '<img src="' + esc(p.duong) + '" alt="' + esc(p.ten) + '" title="' + esc(p.ten) +
            '" width="' + xh.co + '" height="' + xh.co + '" loading="lazy">';
        }).join("") + "</div>"
      : '<p class="trong">Không có dự án nào khớp bộ lọc.</p>';
  }

  function chonLogo() {
    var bo = xh.bo.split(",").map(function (x) { return x.trim().toLowerCase(); }).filter(Boolean);
    return (D.kinhLup || []).filter(function (p) {
      if (!xh.tang[p.loai]) return false;
      if (!xh.ngung && p.luuTru) return false;
      if (bo.indexOf(String(p.slug).toLowerCase()) !== -1) return false;
      return !!duongLogo(p.id);
    }).map(function (p) {
      return { ten: p.ten, duong: duongLogo(p.id) };
    });
  }

  /* Vẽ ra canvas rồi tải xuống. Ảnh cùng nguồn nên canvas không bị
     "vấy bẩn" — toBlob chạy được. */
  function taiPNG() {
    var ds = chonLogo();
    if (!ds.length) return;
    var o = 8, cot = xh.cot, co = xh.co;
    var hang = Math.ceil(ds.length / cot);
    var c = document.createElement("canvas");
    c.width = cot * (co + o) + o;
    c.height = hang * (co + o) + o;
    var g = c.getContext("2d");
    var con = ds.length;
    var nut = $("#xTai");
    nut.textContent = "Đang vẽ…";
    ds.forEach(function (p, i) {
      var im = new Image();
      im.onload = im.onerror = function () {
        if (im.naturalWidth) {
          g.drawImage(im, o + (i % cot) * (co + o), o + Math.floor(i / cot) * (co + o), co, co);
        }
        if (--con === 0) {
          c.toBlob(function (b) {
            var u = URL.createObjectURL(b);
            var a = document.createElement("a");
            a.href = u;
            a.download = "huy-hieu-" + ds.length + "-" + co + "px.png";
            a.click();
            setTimeout(function () { URL.revokeObjectURL(u); }, 4000);
            nut.textContent = "Tải về PNG";
          }, "image/png");
        }
      };
      im.src = p.duong;
    });
  }

  /* ══════════════════════════════════════════════════
     5. ĐI NƠI KHÁC
     Bốn mục trong danh sách của tools.l2beat.com thật ra là
     liên kết trỏ sang ứng dụng khác. Liệt kê cho đủ, kèm lý do
     vì sao không dựng lại được ở đây.
     ══════════════════════════════════════════════════ */
  var NGOAI = [
    { ten: "/disco-ui", url: "https://disco.l2beat.com/ui",
      y: "Giao diện xem kết quả máy quét hợp đồng của L2BEAT.",
      sao: "Là một ứng dụng riêng ở tên miền khác, không nằm trong bundle của tools.l2beat.com. Máy chủ của nó không trả header CORS nên trang này cũng không gọi sang được." },
    { ten: "/diffovery", url: "https://disco.l2beat.com/diff",
      y: "So sánh hai bản quét hợp đồng để thấy đã đổi gì.",
      sao: "Cùng ứng dụng với /disco-ui. Phần dữ liệu thay đổi thì Nhật ký đổi thay ở đây đã phủ rồi." },
    { ten: "/uops-analyzer", url: "https://uops.l2beat.com/",
      y: "Phân tích thao tác người dùng mỗi giây (UOPS) theo từng chuỗi.",
      sao: "Ứng dụng Next.js riêng, không có API công khai đọc được. Số UOPS theo dự án thì Đô Sát Viện đã có ở mục Hoạt động." },
    { ten: "/flat-etherscan", url: "https://chromewebstore.google.com/detail/flat-etherscan-source/ndbkhchcbfbonadoibanllelgnmcljme",
      y: "Tiện ích Chrome làm phẳng mã nguồn hợp đồng trên Etherscan.",
      sao: "Là tiện ích trình duyệt, không phải trang web — không có gì để dựng lại." }
  ];

  function mhNgoai(host) {
    host.innerHTML = '<p class="giaithich">' + dan("di-noi-khac") + "</p>" +
      '<section class="khoi"><div class="ngoai">' +
      NGOAI.map(function (x) {
        return '<a class="ng-muc" href="' + esc(x.url) + '" target="_blank" rel="noopener">' +
          '<div class="ng-dinh"><b>' + esc(x.ten) + "</b>" +
          '<span class="ng-di">mở ở tab mới ↗</span></div>' +
          "<p>" + esc(x.y) + "</p>" +
          '<p class="ng-sao"><b>Vì sao không dựng lại:</b> ' + esc(x.sao) + "</p>" +
          '<span class="ng-url">' + esc(x.url) + "</span></a>";
      }).join("") + "</div>" +
      '<p class="trong" style="text-align:left;padding:14px 18px;border-top:1px solid var(--line-2)">' +
      "Còn một công cụ nữa của họ là <b>/simulator</b> — mô phỏng giao dịch trước khi gửi. " +
      "Nó gọi Tenderly (<code>api.tenderly.co</code>), cần khoá riêng. Có khoá thì nối được; " +
      "chưa có thì để nút bấm vào không ra gì còn tệ hơn không có nút.</p>" +
      "</section>";
  }

  /* ══════════════════════════════════════════════════
     ĐIỀU PHỐI
     ══════════════════════════════════════════════════ */
  var MH = {
    "giai-ma": mhGiaiMa, "nhat-ky": mhNhatKy, "kinh-lup": mhKinhLup,
    "xuong-huy-hieu": mhXuong, "di-noi-khac": mhNgoai
  };

  /* Ô tìm ở đỉnh trang chỉ lọc HAI phòng. Ba phòng kia không đọc state.q
     một lần nào, nên ô ấy đứng đó ở mọi phòng mà gõ vào thì không có gì
     xảy ra: một ô nhập câm, không lỗi, không phản hồi — người dùng chỉ có
     thể kết luận là trang hỏng, hoặc là mình gõ sai. Nó cũng ăn một điểm
     dừng Tab ở mỗi phòng để đổi lấy không gì cả.

     Và ở hai phòng nó thật sự làm việc, hai phòng ấy tìm trong HAI BỘ
     TRƯỜNG khác nhau — nhật ký tìm cả địa chỉ hợp đồng, kính lúp thì
     không có địa chỉ nào để tìm. Một chữ "Tìm…" dùng chung không phân
     biệt được, nên người ta dán một địa chỉ vào kính lúp rồi tưởng dự án
     đó không có trong danh sách. */
  var TIM = {
    "nhat-ky": "Tìm dự án, hợp đồng, địa chỉ…",
    "kinh-lup": "Tìm dự án, dạng…"
  };
  function veTim(ma) {
    var g = TIM[ma] || null, o = $(".tim"), q = $("#q");
    if (o) o.hidden = !g;
    if (q && g) { q.placeholder = g; q.setAttribute("aria-label", g.replace(/…$/, "")); }
  }

  function ve() {
    var host = $("#than"), ma = state.muc;
    var t = VI.muc[ma] || { ten: ma };
    $("#tieu").textContent = t.ten;
    document.title = "Công Bộ · " + t.ten;
    veTim(ma);
    veBen();
    (MH[ma] || MH["giai-ma"])(host);
    if (TT && TT.them) TT.them(host, ma);
  }

  function doiTuyen() {
    var h = (location.hash || "").replace(/^#\/?/, "").split("?")[0] || "giai-ma";
    if (!VI.muc[h]) h = "giai-ma";
    if (h !== state.muc) { state.muc = h; state.duAn = "all"; }
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

    document.addEventListener("error", function (e) {
      var t = e.target;
      if (t && t.tagName === "IMG" && t.parentNode && /duan/.test(t.parentNode.className)) {
        var b = t.parentNode.querySelector("b");
        var s = document.createElement("span");
        s.className = "khonglogo";
        s.textContent = b ? b.textContent.trim().charAt(0).toUpperCase() : "?";
        t.parentNode.replaceChild(s, t);
      }
    }, true);

    var hong = [];
    if (!D.coNhatKy) hong.push("nhật ký đổi thay");
    if (!D.coKinhLup) hong.push("kính lúp hồ sơ");
    if (hong.length) {
      var c = $("#canhBao");
      c.hidden = false;
      c.textContent = "Lần cập nhật gần nhất không lấy được: " + hong.join(", ") +
        ". Đang hiện bản trước đó. (fe-stag là host staging của L2BEAT, tắt lúc nào không báo.)";
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
