/* ═══════════════════════════════════════════════════════
   HỘ BỘ — giao diện.

   Tám phòng, một tuyến hash, không khung nào ngoài trình duyệt.

   ── BA LUẬT CHẠY XUYÊN FILE ───────────────────────────

   1. KHÔNG BỊA SỐ. Thiếu dữ liệu thì vẽ "—", không vẽ 0. Một ô
      trống nói "chưa đo được"; một số 0 nói "đo được và bằng
      không". Hai câu đó khác nhau, và trộn chúng lại là kiểu nói
      dối khó phát hiện nhất trên một bảng điều khiển.

   2. MỌI CON SỐ PHẢI TRUY NGƯỢC ĐƯỢC. Mỗi ngưỡng cảnh báo hiện
      kèm giá trị đã dùng để chấm; mỗi chỉ số ghép hiện kèm các
      thành phần. Không đồng ý với cách chấm thì vẫn thấy được dữ
      liệu thô mà tự chấm lại.

   3. MÀU KHÔNG BAO GIỜ ĐỨNG MỘT MÌNH. Xem đầu app.css.

   ── VÌ SAO CUNG NÀY KHÔNG CÓ NÚT NÀO CHẠM VÍ ──────────
   Đây là trang tĩnh công khai trên GitHub Pages. Một trang như thế
   mà nối ví hoặc giữ khoá thì khoá đã ra tới trình duyệt. Hộ Bộ
   quan sát; việc thực thi thuộc chỗ khác và nằm ngoài repo này.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.HOBU || null;
  var NG = window.HOBU_NGUON || { LOP: [], TOOL: [] };
  /* Lớp tri thức nền — `knowledge-os/sinh.mjs` ghi ra assets/js/v/tri-thuc.js.
     Nó KHÔNG đụng công thức nào: TVL, lợi suất, chế độ rủi ro, ngưỡng cảnh
     báo đều tính y như cũ. Việc duy nhất của nó là nói mỗi phòng đang đo
     VIỆC KINH TẾ nào, và mỗi câu giải nghĩa đến từ đâu. Thiếu file thì
     phòng vẫn vẽ đủ, chỉ không có dải giải nghĩa. */
  var TT = window.TRI_THUC || null;

  /* ═══════════════ ĐỊNH DẠNG ═══════════════ */

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function so(x, d) {
    if (x == null || !isFinite(x)) return "—";
    return Number(x).toLocaleString("vi-VN", { minimumFractionDigits: d, maximumFractionDigits: d });
  }

  /* Tiền theo bậc tiếng Việt. Số càng to thì càng ít chữ số lẻ:
     "1.234,5 tỷ" không thông tin hơn "1.235 tỷ" chút nào, chỉ dài
     hơn và làm cột lệch. */
  function tien(n) {
    if (n == null || !isFinite(n)) return "—";
    var a = Math.abs(n);
    if (a >= 1e12) return so(n / 1e12, 2) + " ngh.tỷ $";
    if (a >= 1e9) return so(n / 1e9, a >= 1e11 ? 0 : 1) + " tỷ $";
    if (a >= 1e6) return so(n / 1e6, a >= 1e8 ? 0 : 1) + " tr $";
    if (a >= 1e3) return so(n / 1e3, 0) + " ng $";
    return so(n, 0) + " $";
  }

  function phanTram(n, d) {
    if (n == null || !isFinite(n)) return "—";
    return (n > 0 ? "+" : "") + so(n, d == null ? 2 : d) + "%";
  }

  var MUI_LEN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V6M5.5 12.5 12 6l6.5 6.5"/></svg>';
  var MUI_XUONG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v13M5.5 11.5 12 18l6.5-6.5"/></svg>';

  /* Chip đổi giá. `nguong` là vùng coi như đứng yên — dưới ngưỡng
     đó thì vẽ xám và không mũi tên, vì gắn mũi tên cho một biến
     động 0,04% là mời người đọc tìm ý nghĩa ở chỗ không có. */
  function chip(n, nhan, nguong) {
    var ng = nguong == null ? 0.15 : nguong;
    if (n == null || !isFinite(n)) {
      return '<span class="d" data-h="trong">—' + (nhan ? " " + esc(nhan) : "") + "</span>";
    }
    var h = Math.abs(n) < ng ? "phang" : n > 0 ? "len" : "xuong";
    var mui = h === "len" ? MUI_LEN : h === "xuong" ? MUI_XUONG : "";
    return '<span class="d" data-h="' + h + '">' + mui + phanTram(n) +
      (nhan ? ' <span style="opacity:.7">' + esc(nhan) + "</span>" : "") + "</span>";
  }

  /* ═══════════════ ĐƯỜNG NẾN ═══════════════
     Vẽ tay chứ không kéo thư viện: một đường gấp khúc 90 điểm là
     một vòng lặp, còn một thư viện đồ thị là vài trăm KB cho máy
     người xem tải về — mà cả cung này mới có 54 KB số liệu. */
  function nenSvg(arr, w, h) {
    if (!arr || arr.length < 2) return "";
    var W = w || 86, H = h || 24, n = arr.length;
    var min = Infinity, max = -Infinity, i;
    for (i = 0; i < n; i++) { if (arr[i] < min) min = arr[i]; if (arr[i] > max) max = arr[i]; }
    var bien = max - min || 1;
    var buoc = W / (n - 1), d = "", nn = "";
    for (i = 0; i < n; i++) {
      var x = (i * buoc).toFixed(1);
      var y = (H - 2 - ((arr[i] - min) / bien) * (H - 4)).toFixed(1);
      d += (i ? "L" : "M") + x + " " + y;
    }
    nn = d + "L" + W + " " + H + "L0 " + H + "Z";
    var mau = arr[n - 1] >= arr[0] ? "var(--len)" : "var(--xuong)";
    return '<svg class="nen" viewBox="0 0 ' + W + " " + H + '" preserveAspectRatio="none" aria-hidden="true">' +
      '<path class="nen-nen" d="' + nn + '" fill="' + mau + '"/>' +
      '<path class="duong" d="' + d + '" stroke="' + mau + '"/></svg>';
  }

  /* ═══════════════ KIM CHỈ CHẾ ĐỘ ═══════════════ */
  function toaDo(cx, cy, r, gocDo) {
    var g = (gocDo * Math.PI) / 180;
    return [cx + r * Math.cos(g), cy - r * Math.sin(g)];
  }
  function cung(cx, cy, r, a1, a2) {
    var p1 = toaDo(cx, cy, r, a1), p2 = toaDo(cx, cy, r, a2);
    var lon = Math.abs(a2 - a1) > 180 ? 1 : 0;
    return "M" + p1[0].toFixed(2) + " " + p1[1].toFixed(2) +
      "A" + r + " " + r + " 0 " + lon + " 1 " + p2[0].toFixed(2) + " " + p2[1].toFixed(2);
  }

  var BANG_MAU = [
    [0, 22, "var(--xuong)"], [22, 42, "var(--canh)"], [42, 58, "var(--fg-3)"],
    [58, 78, "var(--len)"], [78, 100, "var(--tien)"]
  ];

  function kimSvg(diem) {
    var cx = 100, cy = 100, r = 78, s = "";
    /* Điểm 0 nằm bên TRÁI (góc 180°), 100 bên phải (góc 0°). */
    var goc = function (v) { return 180 - (Math.max(0, Math.min(100, v)) / 100) * 180; };
    for (var i = 0; i < BANG_MAU.length; i++) {
      var b = BANG_MAU[i];
      s += '<path d="' + cung(cx, cy, r, goc(b[0]), goc(b[1])) + '" fill="none" stroke="' + b[2] +
        '" stroke-width="13" stroke-linecap="butt" opacity=".9"/>';
    }
    var g = goc(diem);
    var dau = toaDo(cx, cy, r - 20, g), goc2 = toaDo(cx, cy, 8, g - 90), goc3 = toaDo(cx, cy, 8, g + 90);
    s += '<path d="M' + goc2[0].toFixed(1) + " " + goc2[1].toFixed(1) +
      "L" + dau[0].toFixed(1) + " " + dau[1].toFixed(1) +
      "L" + goc3[0].toFixed(1) + " " + goc3[1].toFixed(1) + 'Z" fill="var(--fg)"/>';
    s += '<circle cx="' + cx + '" cy="' + cy + '" r="7" fill="var(--card-3)" stroke="var(--fg)" stroke-width="2"/>';
    s += '<text x="14" y="116" class="bd-so">0</text><text x="176" y="116" class="bd-so">100</text>';
    return '<svg viewBox="0 0 200 120" role="img" aria-label="Chế độ thị trường ' + diem +
      ' trên 100">' + s + "</svg>";
  }

  /* ═══════════════ BẢN ĐỒ DÒNG TIỀN ═══════════════
     Sankey hai cột dựng từ ma trận chuỗi × nhóm ngành trong
     dong-tien.js. Bề dày mỗi dải TỶ LỆ THUẬN với vốn, nên bản đồ
     đọc được bằng mắt mà không cần đọc số.

     Tổng của bản đồ này lớn hơn TVL ở bảng Kho Bạc và điều đó là
     đúng — xem khối giải thích ngay dưới bản đồ trong veDongTien. */
  var MAU_CHUOI = ["#16BDA1", "#5A8DD6", "#A78BFA", "#E8A33D", "#3FBF7F",
    "#E5748D", "#4FC3D9", "#C9A227", "#8FA3BF", "#D97757"];

  function banDoSvg(luoi) {
    if (!luoi || !luoi.length) return '<p class="trong">Chưa có dữ liệu bản đồ.</p>';

    var traiT = {}, phaiT = {}, i, o;
    for (i = 0; i < luoi.length; i++) {
      o = luoi[i];
      traiT[o.chuoi] = (traiT[o.chuoi] || 0) + o.tvl;
      phaiT[o.nhom] = (phaiT[o.nhom] || 0) + o.tvl;
    }
    var trai = Object.keys(traiT).sort(function (a, b) { return traiT[b] - traiT[a]; });
    var phai = Object.keys(phaiT).sort(function (a, b) { return phaiT[b] - phaiT[a]; });
    var tong = 0;
    for (i = 0; i < trai.length; i++) tong += traiT[trai[i]];
    if (!tong) return '<p class="trong">Chưa có dữ liệu bản đồ.</p>';

    var W = 900, KHE = 9, RONG = 12, TREN = 26;
    /* Chiều cao co theo số nút, để cột nào cũng có chỗ thở. */
    var H = Math.max(360, Math.max(trai.length, phai.length) * 46);
    var caoT = H - KHE * (trai.length - 1), caoP = H - KHE * (phai.length - 1);
    var tl = Math.min(caoT, caoP) / tong;

    var xT = 132, xP = W - 132 - RONG;
    var yT = {}, yP = {}, y = TREN + (H - (tong * tl + KHE * (trai.length - 1))) / 2;
    var caoNut = {};
    for (i = 0; i < trai.length; i++) {
      yT[trai[i]] = y; caoNut["T" + trai[i]] = traiT[trai[i]] * tl;
      y += traiT[trai[i]] * tl + KHE;
    }
    y = TREN + (H - (tong * tl + KHE * (phai.length - 1))) / 2;
    for (i = 0; i < phai.length; i++) {
      yP[phai[i]] = y; caoNut["P" + phai[i]] = phaiT[phai[i]] * tl;
      y += phaiT[phai[i]] * tl + KHE;
    }

    var mauCua = {};
    for (i = 0; i < trai.length; i++) mauCua[trai[i]] = MAU_CHUOI[i % MAU_CHUOI.length];

    /* Dải nối vẽ bằng NÉT ĐẬM chứ không phải hình khép kín: một
       đường bezier có stroke-width bằng đúng bề dày cần thiết cho
       ra hình y hệt, với một phần tư số phép tính. */
    var oT = {}, oP = {}, s = "";
    var sap = luoi.slice().sort(function (a, b) {
      if (a.chuoi !== b.chuoi) return trai.indexOf(a.chuoi) - trai.indexOf(b.chuoi);
      return b.tvl - a.tvl;
    });
    for (i = 0; i < sap.length; i++) {
      o = sap[i];
      var t = o.tvl * tl;
      var y1 = yT[o.chuoi] + (oT[o.chuoi] || 0) + t / 2;
      var y2 = yP[o.nhom] + (oP[o.nhom] || 0) + t / 2;
      oT[o.chuoi] = (oT[o.chuoi] || 0) + t;
      oP[o.nhom] = (oP[o.nhom] || 0) + t;
      var x1 = xT + RONG, x2 = xP, xm = (x1 + x2) / 2;
      s += '<path class="bd-noi" data-c="' + esc(o.chuoi) + '" data-n="' + esc(o.nhom) + '"' +
        ' d="M' + x1 + " " + y1.toFixed(1) + "C" + xm + " " + y1.toFixed(1) +
        " " + xm + " " + y2.toFixed(1) + " " + x2 + " " + y2.toFixed(1) + '"' +
        ' stroke="' + mauCua[o.chuoi] + '" stroke-width="' + Math.max(1, t).toFixed(1) +
        '" stroke-opacity=".34"><title>' + esc(o.chuoi) + " → " + esc(o.nhom) + ": " +
        tien(o.tvl) + "</title></path>";
    }

    function nut(ten, x, yy, cao, mau, giaTri, ben) {
      var neo = ben === "T" ? x - 9 : x + RONG + 9;
      var canh = ben === "T" ? "end" : "start";
      var g = '<g class="bd-nut bd-o" data-' + (ben === "T" ? "c" : "n") + '="' + esc(ten) + '">';
      g += '<rect x="' + x + '" y="' + yy.toFixed(1) + '" width="' + RONG + '" height="' +
        Math.max(2, cao).toFixed(1) + '" rx="3" fill="' + mau + '"/>';
      g += '<text class="bd-ten" x="' + neo + '" y="' + (yy + cao / 2 - 1).toFixed(1) +
        '" text-anchor="' + canh + '">' + esc(ten) + "</text>";
      g += '<text class="bd-so" x="' + neo + '" y="' + (yy + cao / 2 + 11).toFixed(1) +
        '" text-anchor="' + canh + '">' + tien(giaTri) + "</text>";
      g += "</g>";
      return g;
    }
    for (i = 0; i < trai.length; i++) {
      s += nut(trai[i], xT, yT[trai[i]], caoNut["T" + trai[i]], mauCua[trai[i]], traiT[trai[i]], "T");
    }
    for (i = 0; i < phai.length; i++) {
      s += nut(phai[i], xP, yP[phai[i]], caoNut["P" + phai[i]], "var(--card-3)", phaiT[phai[i]], "P");
    }
    s += '<text class="bd-cot" x="' + (xT + RONG) + '" y="14" text-anchor="end">Chuỗi</text>';
    s += '<text class="bd-cot" x="' + xP + '" y="14">Nhóm ngành</text>';

    return '<svg viewBox="0 0 ' + W + " " + (H + TREN + 18) + '" role="img" ' +
      'aria-label="Bản đồ vốn theo chuỗi và nhóm ngành">' + s + "</svg>";
  }

  /* ═══════════════ MẢNH DÙNG LẠI ═══════════════ */

  function oSo(nhan, to, duoi) {
    return '<div class="o-so"><div class="nhan">' + esc(nhan) + "</div>" +
      '<div class="to">' + to + "</div>" +
      (duoi ? '<div class="duoi">' + duoi + "</div>" : "") + "</div>";
  }

  /* ── dải tri thức nền cho một phòng ───────────────────
     Bốn nhãn nguồn, và gộp bất kỳ hai nhãn nào cũng là nói dối:

         sách      tác giả mô tả, tra lại được bằng chương/trang
         tác giả   lập trường riêng của tác giả, không phải số đo
         phân tích SUNSWaGz suy ra — sách không nói gì về repo này
         repo      đo được từ chính repo/runtime này, năm 2026

     Sách viết năm 2018. Bỏ nhãn đi thì một quan sát 2026 đọc thành
     lời tác giả, và câu đó vẫn đúng ngữ pháp nên không ai bắt được.
     Cùng luật 2 ở đầu file: mọi thứ hiện ra phải truy ngược được. */
  var TEN_GOC = { sach: "sách", tacGia: "tác giả", phanTich: "phân tích", repo: "repo", web: "web" };

  function chipGoc(g) {
    return '<i class="tt-g" data-g="' + esc(g) + '">' + esc(TEN_GOC[g] || g) + "</i>";
  }

  function viTriSach(k) {
    if (!k.chuong || !k.chuong.length) return k.nguon || "";
    return "ch." + k.chuong.join(",") + (k.trang && k.trang.length ? " tr." + k.trang.join(",") : "");
  }

  function triThuc(ma) {
    if (!TT || !TT.phong) return "";
    var p = null, i;
    for (i = 0; i < TT.phong.length; i++) if (TT.phong[i].ma === ma) p = TT.phong[i];
    if (!p) return "";                       // phòng chưa ánh xạ — không vẽ gì, đừng vẽ khung rỗng

    var the = p.khaiNiem.map(function (id) {
      var k = TT.khaiNiem[id];
      if (!k) return "";
      var vt = viTriSach(k);
      return '<div class="tt-k"><div class="tt-kd"><b>' + esc(k.vi) + "</b>" + chipGoc(k.goc) +
        (vt ? '<span class="tt-vt">' + esc(vt) + "</span>" : "") + "</div>" +
        "<p>" + esc(k.nghia) + "</p></div>";
    }).join("");

    /* Lớp 2018→2026 vẽ RIÊNG dưới một tiêu đề riêng. Trộn nó vào lưới
       trên là đúng cái nhầm mà cả lớp này dựng ra để chặn. */
    var noi = (TT.lop2026 || []).filter(function (r) {
      return p.khaiNiem.indexOf(r.den) !== -1;
    }).map(function (r) {
      var tu = TT.khaiNiem[r.tu], den = TT.khaiNiem[r.den];
      return "<p><b>" + esc(tu ? tu.vi : r.tu) + "</b>" + chipGoc(r.goc) +
        '<span class="tt-loai">' + esc(r.loai) + "</span><b>" + esc(den ? den.vi : r.den) + "</b>" +
        '<span class="tt-tin">tin ' + esc(r.tin) + "</span>" +
        '<span class="tt-vi">' + esc(r.vi) + "</span></p>";
    }).join("");

    return '<section class="khoi tt"><div class="khoi-dinh"><h2>Vấn đề kinh tế gốc</h2>' +
      '<span class="n">' + p.khaiNiem.length + " khái niệm</span></div>" +
      '<p class="tt-y">' + esc(p.y) + "</p>" +
      (the ? '<div class="tt-luoi">' + the + "</div>" : "") +
      (noi ? '<div class="tt-26"><h3>2018 → 2026</h3>' + noi + "</div>" : "") +
      '<p class="tt-chan">Nền: «' + esc(TT.nguon.sach.ten) + "» (" + esc(TT.nguon.sach.tacGia) +
      ", " + esc(TT.nguon.sach.nam) + "). Ánh xạ khái niệm sang phòng là <b>phân tích</b> của " +
      "SUNSWaGz — sách không nói gì về repo này. Sinh từ <code>knowledge-os/</code>.</p></section>";
  }

  function khoi(tieu, n, than, y) {
    return '<section class="khoi"><div class="khoi-dinh"><h2>' + esc(tieu) + "</h2>" +
      (n ? '<span class="n">' + esc(n) + "</span>" : "") + "</div>" +
      (y ? '<div class="khoi-y">' + y + "</div>" : "") + than + "</section>";
  }

  function bang(cot, hang, id) {
    /* `data-sap` chỉ là DẤU "cột này sắp được"; vị trí cột thì đọc
       từ DOM lúc bấm. Nhét sẵn chỉ số vào đây là tạo bản sao thứ
       hai của cùng một sự thật, và nó sẽ lệch ngay lần đầu có ai
       chèn thêm một cột. */
    /* Cột sắp được thì tiêu đề là một <button> THẬT, không phải <th>
       gắn onclick. Trước bản này chỉ CHUỘT mới sắp được bảng: <th>
       không nằm trong luồng Tab và không nhận Enter/Space, nên người
       dùng bàn phím — và người đọc màn hình — nghe `aria-sort` nói
       bảng ĐANG sắp thế nào mà không có đường nào đổi nó. Nút gốc
       mang sẵn cả ba thứ đó (điểm dừng Tab, phím Enter/Space, vai
       trò "button" đọc được), nên không phải dựng lại bằng tay. */
    var th = cot.map(function (c) {
      var trong = c.sap
        ? '<button class="sap" type="button">' + esc(c.t) +
          '<span class="mui" aria-hidden="true"></span></button>'
        : esc(c.t);
      return "<th" + (c.sap ? ' data-sap="1"' : "") + (c.rong ? ' style="width:' + c.rong + '"' : "") +
        ">" + trong + "</th>";
    }).join("");
    return '<div class="cuon"><table class="bang"' + (id ? ' id="' + id + '"' : "") +
      "><thead><tr>" + th + "</tr></thead><tbody>" + hang + "</tbody></table></div>";
  }

  /* Tên ở cột đầu của một dòng MỞ ĐƯỢC hồ sơ phải là <button> thật.
     Cùng lý do đã ghi ở `bang()` cho tiêu đề cột sắp xếp, và cùng
     một chỗ hổng: `<tr>` không nằm trong luồng Tab và không nhận
     Enter/Space, nên trước bản này bốn bảng dẫn vào ngăn hồ sơ —
     Đại Sảnh, Dòng Tiền, Kho Bạc, Nhóm Ngành — chỉ mở được bằng
     CHUỘT. Hồ sơ là chỗ duy nhất nói một chuỗi gồm những giao thức
     nào, nên mất nó là mất hẳn một tầng của cung chứ không phải mất
     một lối tắt.

     Cú bấm vẫn nổi bọt lên `tr[data-mo]` nên bấm đâu trong dòng cũng
     mở như cũ; không có nhánh xử lý thứ hai để mà lệch nhau. */
  function tenMo(ten, loai) {
    return '<button class="ten-mo" type="button" aria-label="Mở hồ sơ ' +
      esc(loai) + " " + esc(ten) + '"><b>' + esc(ten) + "</b></button>";
  }

  function theCanh(c) {
    var ten = { g: "BÌNH THƯỜNG", y: "ĐÁNG CHÚ Ý", r: "NGHIÊM TRỌNG" };
    return '<article class="canh" data-muc="' + esc(c.muc) + '">' +
      '<div class="canh-dinh"><span class="canh-den" aria-hidden="true"></span>' +
      "<h3>" + esc(c.ten) + "</h3>" +
      '<span class="canh-muc">' + ten[c.muc] + "</span></div>" +
      '<div class="canh-so">' + esc(c.so) + "</div>" +
      '<p class="canh-y">' + esc(c.y) + "</p></article>";
  }

  /* ═══════════════ CÁC PHÒNG ═══════════════ */

  function veTongQuan() {
    var t = D.tong, cd = D.cheDo;
    var xau = D.canhBao.filter(function (c) { return c.muc !== "g"; });

    var so1 = '<div class="luoi-so">' +
      oSo("Tài sản đang khoá", tien(t.tvl), chip(t.tvl_d7, "7 ngày") + chip(t.tvl_d30, "30 ngày")) +
      oSo("Tiền chờ · stablecoin", tien(t.stable), chip(t.stable_d7, "7 ngày") + chip(t.stable_d30, "30 ngày")) +
      oSo("Khối lượng DEX 24 giờ", tien(t.dex_24h), chip(t.dex_7d7d, "tuần/tuần")) +
      oSo("Phí trả 24 giờ", tien(t.phi_24h), chip(t.phi_7d7d, "tuần/tuần")) +
      oSo("Mất vì tấn công · 30 ngày", tien(D.mat30), "<span>12 tháng: " + tien(D.mat365) + "</span>") +
      oSo("Đèn không xanh", xau.length + " / " + D.canhBao.length,
        "<span>" + (xau.length ? xau.map(function (c) { return esc(c.ten); }).join(" · ") : "không có gì") + "</span>") +
      "</div>";

    var tp = cd.thanhPhan.map(function (p) {
      var co = p.diem !== null;
      var rong = co ? Math.abs(p.diem) * 50 : 0;
      var trai = co ? (p.diem >= 0 ? 50 : 50 - rong) : 50;
      return '<div class="tp-d"' + (co ? "" : ' data-trong="1"') + '>' +
        '<span class="tp-t" title="' + esc(p.y) + '">' + esc(p.ten) + "</span>" +
        '<span class="tp-b"><i data-h="' + (p.diem >= 0 ? "len" : "xuong") +
        '" style="left:' + trai + '%;width:0"  data-rong="' + rong + '"></i></span>' +
        '<span class="tp-v">' + (p.gt == null ? "—" : phanTram(p.gt, 1)) + "</span></div>";
    }).join("");

    var che = '<div class="che"><div class="che-kim">' + kimSvg(cd.diem) +
      '<div class="che-so"><b>' + cd.diem + '</b><span>' + esc(cd.nhan) + "</span></div></div>" +
      '<div><p class="che-y"><b>' + esc(cd.nhan) + ".</b> " + esc(cd.y) +
      " Chấm bằng " + cd.do + " thành phần đo được trên " + cd.tong +
      ", mỗi thành phần cho một điểm từ −1 tới +1 rồi lấy trung bình.</p>" +
      '<div class="tp">' + tp + "</div></div></div>";

    var dong = D.chuoi.slice().filter(function (c) { return c.d7 !== null; })
      .sort(function (a, b) { return b.d7 - a.d7; });
    var len = dong.slice(0, 5), xuong = dong.slice(-5).reverse();
    function hangDong(a) {
      return a.map(function (c) {
        return "<tr data-mo=\"chuoi\" data-ten=\"" + esc(c.ten) + '"><td><div class="o-ten"><b>' +
          esc(c.ten) + "</b></div></td><td>" + tien(c.tvl) + "</td><td>" + chip(c.d7) + "</td></tr>";
      }).join("");
    }

    return '<p class="giaithich">Cung này trả lời năm câu, theo đúng thứ tự đó: <b>tiền đang ở đâu</b>,' +
      " <b>đang chảy đi đâu</b>, <b>ai đang chuyển</b>, <b>vì sao dòng tiền đổi</b>, và" +
      " <b>rủi ro nào đang hình thành</b>. Mọi con số đều đo được và truy ngược được về nguồn —" +
      " không có mục nào chạy bằng phán đoán." +
      '<span class="vn">Đây không phải một bảng giá. Giá thì CoinGecko và TradingView đã làm quá tốt.' +
      " Chỗ này nhìn <b>vốn</b>: nó nằm ở chuỗi nào, ngành nào, và nó vừa dịch chuyển ra sao.</span></p>" +
      so1 +
      khoi("Chế độ thị trường", "kim chỉ ghép từ " + cd.tong + " thành phần", che,
        "Kim này <b>không dự báo giá</b> — nó chỉ tóm lại vốn đang vào hay đang ra." +
        " Điểm cao nghĩa là tiền đang chảy vào và lan rộng, chứ không nghĩa là nên mua;" +
        " lúc vốn vào mạnh nhất cũng thường là lúc một sai lầm phải trả giá đắt nhất.") +
      khoi("Đèn cảnh báo", xau.length + " / " + D.canhBao.length + " không xanh",
        '<div class="khoi-than"><div class="luoi-canh">' +
        D.canhBao.map(theCanh).join("") + "</div></div>",
        "Toàn bộ là <b>so ngưỡng số học</b>, không có mô hình nào đoán ở đây." +
        " Mỗi đèn hiện kèm con số đã dùng để chấm, nên không đồng ý với ngưỡng thì vẫn tự chấm lại được.") +
      '<div style="display:grid;gap:15px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">' +
      khoi("Chuỗi hút vốn mạnh nhất tuần", "7 ngày",
        bang([{ t: "Chuỗi" }, { t: "TVL" }, { t: "7 ngày" }], hangDong(len))) +
      khoi("Chuỗi mất vốn mạnh nhất tuần", "7 ngày",
        bang([{ t: "Chuỗi" }, { t: "TVL" }, { t: "7 ngày" }], hangDong(xuong))) +
      "</div>";
  }

  function veDongTien() {
    var hang = D.chuoi.map(function (c, i) {
      var y = c.tyle == null ? "—"
        : c.tyle >= 8 ? "đường chuyển tiền"
          : c.tyle >= 3 ? "nhiều tiền chờ"
            : c.tyle >= 1.2 ? "cân bằng" : "vốn đang làm việc";
      return '<tr data-mo="chuoi" data-ten="' + esc(c.ten) + '"><td><div class="o-ten">' +
        '<span class="hang">' + (i + 1) + "</span><b>" + esc(c.ten) + "</b></div></td>" +
        "<td>" + tien(c.tvl) + "</td><td>" + chip(c.d7) + "</td>" +
        "<td>" + tien(c.stable) + "</td>" +
        "<td>" + (c.tyle == null ? "—" : so(c.tyle, 1) + "×") + "</td>" +
        '<td class="mo">' + y + "</td></tr>";
    }).join("");

    return '<p class="giaithich">Vốn không biến mất, nó <b>đổi chỗ</b>. Bản đồ dưới đây cho thấy trên mỗi' +
      " chuỗi lớn, tiền đang nằm trong những ngành nào — bề dày mỗi dải tỷ lệ thuận với số vốn," +
      " nên đọc được bằng mắt trước khi đọc số. Rê chuột vào một nút để tách riêng dòng của nó." +
      '<span class="vn">Hai câu hỏi khác nhau: <b>“chuỗi nào giàu”</b> thì xem Kho Bạc,' +
      " còn <b>“tiền trên chuỗi đó đang làm gì”</b> thì xem ở đây.</span></p>" +
      khoi("Bản đồ dòng tiền", "chuỗi × nhóm ngành",
        '<div class="bando" id="bando">' + banDoSvg(D.luoi) + "</div>",
        "<b>Tổng của bản đồ này lớn hơn TVL ở Kho Bạc, và cả hai đều đúng.</b>" +
        " TVL chuỗi đếm từ phía chuỗi: một đô chỉ được tính một lần. Bản đồ đếm từ phía giao thức:" +
        " một đồng ETH đem stake ở Lido rồi lấy stETH thế chấp ở Aave là một đô nằm ở hai chỗ, và câu" +
        " “ngành nào đang giữ vốn” thì phải đếm cả hai. Ép hai phép đo về một số là chọn một con số" +
        " sai để hai bảng trông hợp nhau.") +
      khoi("Tiền chờ so với vốn đang làm việc", D.chuoi.length + " chuỗi",
        bang([{ t: "Chuỗi" }, { t: "TVL" }, { t: "7 ngày" }, { t: "Stablecoin" },
          { t: "Chờ / khoá" }, { t: "Đọc là" }], hang),
        "Cột <b>chờ / khoá</b> là stablecoin lưu hành trên chuỗi chia cho TVL của chính chuỗi đó." +
        " Vượt 1× là chuyện bình thường chứ không phải lỗi — stablecoin không nằm trong TVL." +
        " Tron cao vọt vì nó gần như chỉ để chuyển USDT chứ hầu như không có DeFi; Base thấp vì" +
        " tiền tới đó là để vào việc ngay.");
  }

  function veKhoBac() {
    var hang = D.chuoi.map(function (c, i) {
      return '<tr data-mo="chuoi" data-ten="' + esc(c.ten) + '"><td><div class="o-ten">' +
        '<span class="hang">' + (i + 1) + "</span><b>" + esc(c.ten) + "</b>" +
        (c.ma ? '<span class="ma">' + esc(c.ma) + "</span>" : "") + "</div></td>" +
        '<td data-v="' + (c.tvl || 0) + '">' + tien(c.tvl) + "</td>" +
        '<td data-v="' + (c.d1 == null ? -1e9 : c.d1) + '">' + chip(c.d1) + "</td>" +
        '<td data-v="' + (c.d7 == null ? -1e9 : c.d7) + '">' + chip(c.d7) + "</td>" +
        '<td data-v="' + (c.d30 == null ? -1e9 : c.d30) + '">' + chip(c.d30) + "</td>" +
        '<td data-v="' + (c.dex24h || 0) + '">' + tien(c.dex24h) + "</td>" +
        '<td data-v="' + (c.phi24h || 0) + '">' + tien(c.phi24h) + "</td>" +
        "<td>" + nenSvg(c.nen) + "</td></tr>";
    }).join("");

    var t = D.tong;
    return '<div class="luoi-so">' +
      oSo("Tổng tài sản khoá", tien(t.tvl), chip(t.tvl_d1, "24 giờ") + chip(t.tvl_d7, "7 ngày")) +
      oSo("Chuỗi lớn nhất", esc(D.chuoi[0] ? D.chuoi[0].ten : "—"),
        "<span>" + tien(D.chuoi[0] ? D.chuoi[0].tvl : null) + " · " +
        so(D.chuoi[0] && t.tvl ? (D.chuoi[0].tvl / t.tvl) * 100 : null, 1) + "% toàn thị trường</span>") +
      oSo("Phí trả 24 giờ", tien(t.phi_24h), chip(t.phi_d1, "24 giờ")) +
      oSo("Khối lượng DEX 24 giờ", tien(t.dex_24h), chip(t.dex_d1, "24 giờ")) +
      "</div>" +
      khoi("Kho bạc từng chuỗi", D.chuoi.length + " chuỗi lớn nhất",
        bang([{ t: "Chuỗi" }, { t: "TVL", sap: 1 }, { t: "24 giờ", sap: 1 }, { t: "7 ngày", sap: 1 },
          { t: "30 ngày", sap: 1 }, { t: "DEX 24h", sap: 1 }, { t: "Phí 24h", sap: 1 },
          { t: "90 ngày", rong: "96px" }], hang, "bangChuoi"),
        "Tiêu đề cột có mũi tên là <b>nút bấm được</b> — bấm chuột, hoặc Tab tới rồi Enter," +
        " để sắp xếp. Bấm một dòng để mở hồ sơ chuỗi." +
        " Cột <b>phí</b> là thứ người dùng thật sự trả — nó thường nguội trước khi vốn kịp rút," +
        " nên một chuỗi TVL đứng yên mà phí sụt nhanh là dấu hiệu sớm.");
  }

  function veNhom() {
    var tongN = D.nhom.reduce(function (n, g) { return n + g.tvl; }, 0);
    var hang = D.nhom.map(function (g, i) {
      var phan = tongN ? (g.tvl / tongN) * 100 : 0;
      return '<tr data-mo="nhom" data-ten="' + esc(g.ten) + '"><td><div class="o-ten">' +
        '<span class="hang">' + (i + 1) + "</span><b>" + esc(g.ten) + "</b></div></td>" +
        '<td data-v="' + g.tvl + '">' + tien(g.tvl) + "</td>" +
        '<td data-v="' + phan + '">' + so(phan, 1) + "%</td>" +
        '<td data-v="' + (g.d1 == null ? -1e9 : g.d1) + '">' + chip(g.d1) + "</td>" +
        '<td data-v="' + (g.d7 == null ? -1e9 : g.d7) + '">' + chip(g.d7) + "</td>" +
        '<td data-v="' + g.so + '">' + so(g.so, 0) + "</td></tr>";
    }).join("");

    function cotGT(a) {
      return a.map(function (p) {
        return '<tr><td><div class="o-ten"><b>' + esc(p.ten) + "</b></div>" +
          '<div style="font-size:11px;color:var(--fg-3);margin-left:0">' +
          esc(p.nhom || "—") + " · " + esc(p.chuoi || "—") + "</div></td>" +
          "<td>" + tien(p.tvl) + "</td><td>" + chip(p.d7) + "</td></tr>";
      }).join("");
    }

    return '<p class="giaithich">Vốn xoay giữa các ngành trước khi xoay giữa các chuỗi. Bảng này cộng TVL' +
      " của mọi giao thức theo nhóm ngành, rồi đo mức đổi bằng cách <b>cộng vốn hai mốc rồi mới chia</b>" +
      " — chứ không lấy trung bình các phần trăm." +
      '<span class="vn">Vì sao chỗ đó đáng nói: bản đầu tiên lấy trung bình % và ra “Dexs +47,4%/tuần”' +
      " trong một tuần bình lặng. Thủ phạm là một giao thức 6 triệu đô tăng 74.493% vì tuần trước nó mới" +
      " có 8 nghìn đô. Cộng vốn rồi chia thì con số ấy về đúng <b>+0,2%</b>.</span></p>" +
      khoi("Vốn theo nhóm ngành", D.nhom.length + " nhóm",
        bang([{ t: "Nhóm ngành" }, { t: "TVL", sap: 1 }, { t: "Tỷ trọng", sap: 1 },
          { t: "24 giờ", sap: 1 }, { t: "7 ngày", sap: 1 }, { t: "Số giao thức", sap: 1 }],
        hang, "bangNhom"),
        "<b>Đã bỏ hẳn nhóm CEX.</b> Đó là dự trữ ví sàn tập trung — hơn 250 tỷ đô, gấp ba phần còn" +
        " lại cộng lại — và nó không phải vốn nằm trong hợp đồng on-chain. Để nguyên thì biểu đồ chỉ" +
        " còn một cột và mọi ngành thật bị ép thành vạch mờ dưới đáy.") +
      '<div style="display:grid;gap:15px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))">' +
      khoi("Giao thức hút vốn mạnh nhất", "TVL từ 50 triệu $, 7 ngày",
        bang([{ t: "Giao thức" }, { t: "TVL" }, { t: "7 ngày" }], cotGT(D.giaoThuc.len))) +
      khoi("Giao thức mất vốn mạnh nhất", "TVL từ 50 triệu $, 7 ngày",
        bang([{ t: "Giao thức" }, { t: "TVL" }, { t: "7 ngày" }], cotGT(D.giaoThuc.xuong))) +
      "</div>";
  }

  function veOnDinh() {
    var t = D.tong;
    var hang = D.stable.map(function (s, i) {
      var trang = s.tich
        ? '<span class="the" data-k="lam">tích lãi</span>'
        : s.lech == null ? '<span class="the">không neo USD</span>'
          : Math.abs(s.lech) < 0.2 ? '<span class="the" data-k="len">bám neo</span>'
            : s.lech < 0 ? '<span class="the" data-k="xuong">chiết khấu</span>'
              : '<span class="the" data-k="canh">trên mệnh giá</span>';
      return '<tr><td><div class="o-ten"><span class="hang">' + (i + 1) + "</span><b>" +
        esc(s.ma) + '</b><span class="ma">' + esc(s.loai || "—") + "</span></div>" +
        '<div style="font-size:11px;color:var(--fg-3)">' + esc(s.ten) + "</div></td>" +
        '<td data-v="' + s.cung + '">' + tien(s.cung) + "</td>" +
        '<td data-v="' + (s.d7 == null ? -1e9 : s.d7) + '">' + chip(s.d7) + "</td>" +
        '<td data-v="' + (s.d30 == null ? -1e9 : s.d30) + '">' + chip(s.d30) + "</td>" +
        "<td>" + (s.gia == null ? "—" : so(s.gia, 4)) + "</td>" +
        "<td>" + (s.lech == null ? "—" : phanTram(s.lech)) + "</td>" +
        "<td>" + trang + "</td></tr>";
    }).join("");

    return '<p class="giaithich">Stablecoin là <b>tiền chờ</b>: vốn đã vào hệ nhưng chưa chọn chỗ đứng.' +
      " Tổng cung phình lên nghĩa là tiền mới đang vào và đợi; co lại nghĩa là tiền rời hệ thật —" +
      " khác hẳn việc vốn chỉ xoay từ tài sản này sang tài sản khác." +
      '<span class="vn">Vì sao cột lệch neo chỉ đọc chiều <b>giảm</b>: stablecoin rẻ hơn mệnh giá' +
      " nghĩa là thị trường nghi ngờ khả năng đổi lại — đó mới là chuyện đáng sợ. Đắt hơn mệnh giá" +
      " thì thường chỉ là token <b>tích lãi</b> (USYC, USDY), lãi cộng dồn thẳng vào giá token đúng" +
      " như thiết kế. Chấm chung hai chiều là bật đèn đỏ vĩnh viễn cho một chuyện hoàn toàn bình" +
      " thường — và đèn đỏ vĩnh viễn thì dạy người ta bỏ qua đèn đỏ.</span></p>" +
      '<div class="luoi-so">' +
      oSo("Tổng tiền chờ", tien(t.stable), chip(t.stable_d7, "7 ngày") + chip(t.stable_d30, "30 ngày")) +
      oSo("Đồng lớn nhất", esc(D.stable[0] ? D.stable[0].ma : "—"),
        "<span>" + tien(D.stable[0] ? D.stable[0].cung : null) + "</span>") +
      oSo("So với tài sản khoá",
        (t.stable && t.tvl ? so(t.stable / t.tvl, 2) + "×" : "—"),
        "<span>tiền chờ trên mỗi đô đang làm việc</span>") +
      "</div>" +
      khoi("Tổng cung stablecoin · 180 ngày", "toàn thị trường",
        '<div class="khoi-than" style="padding:18px 17px">' +
        (t.nen_stable && t.nen_stable.length
          ? '<div style="height:110px">' +
            nenSvg(t.nen_stable, 900, 110).replace('class="nen"', 'class="nen" style="width:100%;height:110px"') +
            "</div>"
          : '<p class="trong">Chưa có chuỗi thời gian.</p>') + "</div>") +
      khoi("Từng đồng stablecoin", D.stable.length + " đồng lớn nhất",
        bang([{ t: "Đồng" }, { t: "Đang lưu hành", sap: 1 }, { t: "7 ngày", sap: 1 },
          { t: "30 ngày", sap: 1 }, { t: "Giá" }, { t: "Lệch mệnh giá" }, { t: "Trạng thái" }],
        hang, "bangStable"));
  }

  function veLoiSuat() {
    var hang = D.loiSuat.map(function (p) {
      var deu = p.dao == null ? "—" : p.dao < 0.3 ? "đều" : p.dao < 1 ? "dao động" : "răng cưa";
      var kDeu = p.dao == null ? "" : p.dao < 0.3 ? "len" : p.dao < 1 ? "canh" : "xuong";
      return "<tr><td><div class=\"o-ten\"><b>" + esc(p.ho) + "</b>" +
        (p.on ? '<span class="the" data-k="lam">ổn định</span>' : "") + "</div>" +
        '<div style="font-size:11px;color:var(--fg-3)">' + esc(p.duAn) + " · " + esc(p.chuoi) + "</div></td>" +
        '<td data-v="' + p.tvl + '">' + tien(p.tvl) + "</td>" +
        '<td data-v="' + p.apy + '">' + so(p.apy, 2) + "%</td>" +
        "<td>" + (p.goc == null ? "—" : so(p.goc, 2) + "%") + "</td>" +
        "<td>" + (p.thuong == null ? "—" : so(p.thuong, 2) + "%") + "</td>" +
        '<td data-v="' + (p.dao == null ? 1e9 : p.dao) + '"><span class="the"' +
        (kDeu ? ' data-k="' + kDeu + '"' : "") + ">" + deu + "</span></td>" +
        "<td>" + esc(p.il || "—") + "</td></tr>";
    }).join("");

    return '<p class="giaithich">Cột APY <b>không phải lời hứa</b>. Nó là suy ra từ lợi suất mấy ngày' +
      " gần nhất rồi nhân lên cả năm — hồ nào thưởng bằng token đang xả thì con số ấy sống được vài" +
      " tuần là cùng." +
      '<span class="vn">Nên bảng này tách <b>gốc</b> khỏi <b>thưởng</b>, và thêm hẳn một cột' +
      " <b>độ đều</b> lấy từ độ lệch chuẩn của APY 30 ngày. Một hồ “8% đều” và một hồ “8% trung bình" +
      " của đường răng cưa” hiện lên giống hệt nhau nếu chỉ nhìn cột APY — mà chúng là hai thứ" +
      " hoàn toàn khác.</span></p>" +
      khoi("Hồ lợi suất", D.loiSuat.length + " hồ, TVL từ 3 triệu $",
        bang([{ t: "Hồ" }, { t: "TVL", sap: 1 }, { t: "APY", sap: 1 }, { t: "Gốc" }, { t: "Thưởng" },
          { t: "Độ đều", sap: 1 }, { t: "Rủi ro IL" }], hang, "bangLS"),
        "Ba lớp lọc đã chạy trước khi bảng này hiện: TVL từ 3 triệu $ (hồ nhỏ thì APY nhảy theo" +
        " một lệnh hoán đổi), APY tối đa 150% (trên mức đó gần như luôn là thưởng token đang xả)," +
        " và bỏ hồ chết. <b>Đây không phải lời khuyên đầu tư</b> — vào hồ nào là thao tác tầng 3," +
        " xem thang quyền ví ở Kho Nguồn.");
  }

  function veAnNinh() {
    var hangLoi = D.loi.map(function (h) {
      return "<tr><td><div class=\"o-ten\"><b>" + esc(h.ten) + "</b></div>" +
        '<div style="font-size:11px;color:var(--fg-3)">' + esc(h.chuoi || "—") + "</div></td>" +
        "<td>" + esc(h.ngay) + "</td>" +
        '<td data-v="' + (h.mat || 0) + '">' + tien(h.mat) + "</td>" +
        '<td class="mo">' + esc(h.cach || "—") + "</td>" +
        '<td class="mo">' + esc(h.loai || "—") + "</td></tr>";
    }).join("");

    return '<p class="giaithich">Ra-đa này <b>không thay Đô Sát Viện</b>. Đô Sát Viện xét kiến trúc và' +
      " quyền lực của từng Layer 2; chỗ này chỉ đọc <b>tín hiệu tài chính</b> có liên quan tới an" +
      " toàn — vốn rút đột ngột, neo giá lệch, tiền mất vì tấn công." +
      '<span class="vn">Bảy đèn dưới đây đều là <b>phép so số học</b>, không có mô hình nào đoán.' +
      " Chỗ nào số trả lời được thì đừng để mô hình trả lời — đó cũng là luật của Đài Quan Trắc" +
      " trong kinh đô này.</span></p>" +
      khoi("Ra-đa rủi ro", D.canhBao.filter(function (c) { return c.muc !== "g"; }).length +
        " / " + D.canhBao.length + " không xanh",
        '<div class="khoi-than"><div class="luoi-canh">' + D.canhBao.map(theCanh).join("") + "</div></div>") +
      khoi("Vụ mất tiền đã xác nhận", D.loi.length + " vụ gần nhất",
        bang([{ t: "Nơi bị tấn công" }, { t: "Ngày" }, { t: "Mất", sap: 1 },
          { t: "Cách" }, { t: "Loại" }], hangLoi, "bangLoi"),
        "Nguồn là bảng vụ việc của DefiLlama, <b>chỉ gồm vụ đã xác nhận</b> — nên con số này là" +
        " sàn chứ không phải trần. Cột <b>cách</b> đáng đọc nhất: phần lớn tiền mất không phải vì" +
        " lỗi toán học cao siêu mà vì khoá riêng bị lộ.");
  }

  var locLop = "tat-ca", locTang = "tat-ca", locTim = "";

  function veKhoNguon() {
    var THANG = [
      { t: 0, ten: "Chỉ đọc dữ liệu công khai", y: "Mở trang, xem số. Ví của bạn không xuất hiện ở bất kỳ đâu trong luồng này.", vd: ["DefiLlama", "CoinGecko", "L2BEAT", "Glassnode"] },
      { t: 1, ten: "Dán địa chỉ ví công khai", y: "Bạn gõ một địa chỉ vào ô tìm để xem nó giữ gì. Địa chỉ ví là thông tin công khai — vẫn chưa chạm tới quyền nào.", vd: ["Arkham", "Nansen", "DeBank"] },
      { t: 2, ten: "Nối ví, ký đăng nhập", y: "Trang đọc được địa chỉ của bạn và xin một chữ ký để xác thực. Chữ ký đăng nhập không chuyển tiền — nhưng đây là lúc phải đọc kỹ nội dung đang ký.", vd: ["ChainList", "Zapper", "phần lớn dApp"] },
      { t: 3, ten: "Duyệt chi · hoán đổi · bắc cầu", y: "Tiền thật rời ví. Duyệt chi không giới hạn là cách phổ biến nhất để một ví bị rút sạch, và ngắt kết nối dApp KHÔNG tự thu hồi những quyền đã cấp.", vd: ["Whales Market", "MiniBridge", "CoinTool", "mọi thao tác hoán đổi"] }
    ];
    var thang = THANG.map(function (m) {
      return '<div class="th-d" data-t="' + m.t + '"><div><span class="th-so">' + m.t + "</span></div>" +
        '<div class="th-n"><h3>Tầng ' + m.t + " · " + esc(m.ten) + "</h3><p>" + esc(m.y) + "</p>" +
        '<div class="th-vd">' + m.vd.map(function (v) {
          return '<span class="the">' + esc(v) + "</span>";
        }).join("") + "</div></div></div>" +
        (m.t === 2 ? '<div class="th-ranh"><b>Ranh giới thật nằm ở đây.</b> Trên vạch này, sai lầm' +
          " tệ nhất là đọc phải số liệu sai. Dưới vạch này, sai lầm tệ nhất là mất tiền và không" +
          " lấy lại được. Một trang <b>có thật</b> và một thao tác <b>an toàn</b> là hai câu khác" +
          " nhau hoàn toàn.</div>" : "");
    }).join("");

    var lopNut = '<button type="button" data-lop="tat-ca" aria-pressed="' +
      (locLop === "tat-ca") + '">Tất cả<span class="dem">' + NG.TOOL.length + "</span></button>" +
      NG.LOP.map(function (l) {
        var n = NG.TOOL.filter(function (t) { return t.lop === l.ma; }).length;
        return '<button type="button" data-lop="' + esc(l.ma) + '" aria-pressed="' +
          (locLop === l.ma) + '">' + esc(l.ten) + '<span class="dem">' + n + "</span></button>";
      }).join("");

    var tangNut = '<button type="button" data-tang="tat-ca" aria-pressed="' +
      (locTang === "tat-ca") + '">Mọi tầng</button>' +
      [0, 1, 2, 3].map(function (t) {
        var n = NG.TOOL.filter(function (x) { return x.tang === t; }).length;
        return '<button type="button" data-tang="' + t + '" aria-pressed="' +
          (locTang === String(t)) + '">Tầng ' + t + '<span class="dem">' + n + "</span></button>";
      }).join("");

    return '<p class="giaithich">Bốn mươi bảy công cụ, xếp theo <b>việc chúng làm</b> và' +
      " <b>quyền chúng đòi ở ví bạn</b> — chứ không theo thứ tự ai nổi hơn ai. Đây không phải trang" +
      " bookmark: một danh sách link không nói được công cụ đó nhìn cái gì, tin được tới đâu, và" +
      " hỏi câu nào thì mở nó." +
      '<span class="vn"><b>Luật không có ngoại lệ:</b> KHÔNG công cụ nào trong danh sách này cần' +
      " seed phrase hay khoá riêng tư của bạn. Ai hỏi tới, dừng ngay — người có seed phrase là" +
      " người sở hữu tài sản, và không có cách nào lấy lại.</span></p>" +
      khoi("Thang quyền ví", "4 tầng", '<div class="thang">' + thang + "</div>",
        "Cột <b>tầng</b> trên mỗi thẻ bên dưới đọc theo thang này. Nó đo mức thiệt hại nếu mọi" +
        " chuyện đi sai, <b>không phải</b> đo công cụ đó tử tế hay không.") +
      khoi("Sổ bộ nguồn", NG.TOOL.length + " công cụ",
        '<div class="loc" id="locLop">' + lopNut + "</div>" +
        '<div class="loc" id="locTang">' + tangNut +
        '<span class="tim"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
        '<input id="timNguon" type="search" placeholder="Tìm công cụ, việc, câu hỏi…" autocomplete="off" aria-label="Tìm trong sổ bộ nguồn" value="' + esc(locTim) + '"></span></div>' +
        '<div class="luoi-nguon" id="luoiNguon"></div>');
  }

  function locVaVe() {
    var host = document.getElementById("luoiNguon");
    if (!host) return;
    var q = locTim.trim().toLowerCase();
    var ds = NG.TOOL.filter(function (t) {
      if (locLop !== "tat-ca" && t.lop !== locLop) return false;
      if (locTang !== "tat-ca" && String(t.tang) !== locTang) return false;
      if (!q) return true;
      return (t.ten + " " + t.viec + " " + t.hoi + " " + (t.luu || "")).toLowerCase().indexOf(q) !== -1;
    });
    if (!ds.length) {
      /* Trạng thái trống phải trả lời được "vì sao trống". Bộ lọc ở
         đây có BA trục (nhóm, tầng, chữ tìm) và hai trong ba nằm ở
         cụm nút phía trên, ngoài tầm mắt khi đã cuộn xuống — nên một
         dòng "không có gì khớp" trơ trọi bắt người đọc tự nhớ họ đã
         bấm những gì rồi tự đi gỡ từng cái. Liệt kê đúng các điều
         kiện đang bật, rồi cho MỘT nút thoát ra. */
      var dieu = [], l = null, j;
      if (locLop !== "tat-ca") {
        for (j = 0; j < NG.LOP.length; j++) if (NG.LOP[j].ma === locLop) l = NG.LOP[j];
        dieu.push("nhóm <b>" + esc(l ? l.ten : locLop) + "</b>");
      }
      if (locTang !== "tat-ca") dieu.push("tầng <b>" + esc(locTang) + "</b>");
      if (q) dieu.push("chữ <b>“" + esc(locTim.trim()) + "”</b>");
      host.innerHTML = dieu.length
        ? '<div class="trong trong-loc"><p><b>Không công cụ nào khớp.</b></p>' +
          '<p class="trong-dk">Đang lọc theo ' + dieu.join(" · ") + ".</p>" +
          '<button class="trong-xoa" type="button" id="xoaLoc">Xoá bộ lọc · xem lại cả ' +
          NG.TOOL.length + " công cụ</button></div>"
        : '<p class="trong">Sổ bộ nguồn chưa có công cụ nào.</p>';
      return;
    }
    var TIN = { cao: ["len", "bằng chứng mạnh"], vua: ["", "bằng chứng vừa"], "chua-ro": ["canh", "chưa rõ"] };
    host.innerHTML = ds.map(function (t) {
      var tin = TIN[t.tin] || ["", t.tin];
      return '<button class="tn" type="button" data-nguon="' + esc(t.ma) + '">' +
        '<div class="tn-dinh"><h3>' + esc(t.ten) + "</h3>" +
        '<span class="tang" data-t="' + t.tang + '">TẦNG ' + t.tang + "</span></div>" +
        '<p class="tn-viec">' + esc(t.viec) + "</p>" +
        '<p class="tn-hoi">' + esc(t.hoi) + "</p>" +
        '<div class="tn-chan">' +
        '<span class="the"' + (tin[0] ? ' data-k="' + tin[0] + '"' : "") + ">" + esc(tin[1]) + "</span>" +
        '<span class="the">' + (t.api === "co" ? "có API" : t.api === "mot-phan" ? "API một phần" : "không API") + "</span>" +
        '<span class="the">' + (t.tien === "free" ? "miễn phí" : t.tien === "freemium" ? "miễn phí có giới hạn" : "trả phí") + "</span>" +
        (t.luu ? '<span class="the" data-k="canh">có lưu ý</span>' : "") +
        "</div></button>";
    }).join("");
  }

  /* ═══════════════ HỒ SƠ ═══════════════ */

  var hoso = document.getElementById("hoso"),
    scrim = document.getElementById("scrim"),
    hosoTen = document.getElementById("hosoTen"),
    hosoTren = document.getElementById("hosoTren"),
    hosoBody = document.getElementById("hosoBody");

  function dongHoso() {
    hoso.dataset.open = "0";
    scrim.dataset.open = "0";
    hoso.setAttribute("aria-hidden", "true");
  }
  function moHoso(tren, ten, than) {
    hosoTren.textContent = tren;
    hosoTen.textContent = ten;
    hosoBody.innerHTML = than;
    hoso.dataset.open = "1";
    scrim.dataset.open = "1";
    hoso.setAttribute("aria-hidden", "false");
    hosoBody.scrollTop = 0;
  }

  function hosoChuoi(ten) {
    var c = null, i;
    for (i = 0; i < D.chuoi.length; i++) if (D.chuoi[i].ten === ten) c = D.chuoi[i];
    if (!c) return;
    var phan = D.tong.tvl ? (c.tvl / D.tong.tvl) * 100 : null;
    var nganh = D.luoi.filter(function (o) { return o.chuoi === ten; })
      .sort(function (a, b) { return b.tvl - a.tvl; });
    var tongN = nganh.reduce(function (n, o) { return n + o.tvl; }, 0);

    var than = '<div class="hs"><div class="hs-h">Vốn</div><div class="hs-vr">' +
      '<div class="hs-o"><span>Tài sản khoá</span><b>' + tien(c.tvl) + "</b><i>" +
      (phan == null ? "" : so(phan, 1) + "% toàn thị trường") + "</i></div>" +
      '<div class="hs-o"><span>Stablecoin</span><b>' + tien(c.stable) + "</b><i>" +
      (c.tyle == null ? "" : so(c.tyle, 1) + "× so với TVL") + "</i></div>" +
      '<div class="hs-o"><span>Khối lượng DEX 24h</span><b>' + tien(c.dex24h) + "</b></div>" +
      '<div class="hs-o"><span>Phí 24h</span><b>' + tien(c.phi24h) + "</b></div>" +
      "</div></div>" +
      '<div class="hs"><div class="hs-h">Đổi theo thời gian</div><div class="hs-vr">' +
      '<div class="hs-o"><span>24 giờ</span><b>' + chip(c.d1) + "</b></div>" +
      '<div class="hs-o"><span>7 ngày</span><b>' + chip(c.d7) + "</b></div>" +
      '<div class="hs-o"><span>30 ngày</span><b>' + chip(c.d30) + "</b></div>" +
      "</div></div>";

    if (c.nen && c.nen.length > 2) {
      than += '<div class="hs"><div class="hs-h">TVL 90 ngày</div>' +
        '<div style="height:96px;border:1px solid var(--line);border-radius:9px;padding:9px;background:var(--card)">' +
        nenSvg(c.nen, 500, 78).replace('class="nen"', 'class="nen" style="width:100%;height:78px"') +
        "</div></div>";
    }
    if (nganh.length) {
      than += '<div class="hs"><div class="hs-h">Vốn nằm ở ngành nào</div>' +
        nganh.map(function (o) {
          var p = tongN ? (o.tvl / tongN) * 100 : 0;
          return '<div class="tp-d" style="grid-template-columns:132px 1fr 62px">' +
            '<span class="tp-t">' + esc(o.nhom) + "</span>" +
            '<span class="tp-b"><i data-h="len" style="left:0;width:' + p.toFixed(1) + '%"></i></span>' +
            '<span class="tp-v">' + so(p, 0) + "%</span></div>";
        }).join("") +
        '<p class="hs-p" style="margin-top:9px;font-size:12px;color:var(--fg-3)">Tổng ' +
        tien(tongN) + " theo phía giao thức — lớn hơn TVL ở trên vì một đô đi qua nhiều giao thức được đếm nhiều lần.</p></div>";
    }
    moHoso("Hồ sơ chuỗi", ten, than);
  }

  function hosoNhom(ten) {
    var g = null, i;
    for (i = 0; i < D.nhom.length; i++) if (D.nhom[i].ten === ten) g = D.nhom[i];

    var chuoi = D.luoi.filter(function (o) { return o.nhom === ten; })
      .sort(function (a, b) { return b.tvl - a.tvl; });
    var tongC = chuoi.reduce(function (n, o) { return n + o.tvl; }, 0);

    /* "Khác" là RỔ GOM, không phải một ngành — nó là mọi nhóm ngoài
       tám nhóm lớn nhất, gộp lại cho bản đồ đỡ rối. Không có dòng
       nào của nó trong D.nhom, nên nếu chỉ `return` thì cú bấm vào
       nó trên bản đồ là một cú bấm chết: người dùng bấm, không có
       gì xảy ra, và không cách nào biết vì sao. */
    if (!g && !chuoi.length) return;

    var than = g
      ? '<div class="hs"><div class="hs-vr">' +
        '<div class="hs-o"><span>TVL nhóm</span><b>' + tien(g.tvl) + "</b></div>" +
        '<div class="hs-o"><span>Số giao thức</span><b>' + so(g.so, 0) + "</b></div>" +
        '<div class="hs-o"><span>24 giờ</span><b>' + chip(g.d1) + "</b></div>" +
        '<div class="hs-o"><span>7 ngày</span><b>' + chip(g.d7) + "</b></div>" +
        "</div></div>"
      : '<div class="hs"><p class="hs-luu"><b>Đây là rổ gom, không phải một ngành.</b>' +
        " Bản đồ dòng tiền chỉ tách riêng tám nhóm lớn nhất; mọi nhóm còn lại dồn vào đây" +
        " để các dải không mảnh tới mức không nhìn được. Muốn xem từng nhóm thì sang phòng" +
        " <b>Nhóm Ngành</b>.</p></div>" +
        '<div class="hs"><div class="hs-vr"><div class="hs-o"><span>Tổng trong rổ</span><b>' +
        tien(tongC) + "</b></div></div></div>";
    if (chuoi.length) {
      than += '<div class="hs"><div class="hs-h">Nằm trên chuỗi nào</div>' +
        chuoi.map(function (o) {
          var p = tongC ? (o.tvl / tongC) * 100 : 0;
          return '<div class="tp-d" style="grid-template-columns:132px 1fr 62px">' +
            '<span class="tp-t">' + esc(o.chuoi) + "</span>" +
            '<span class="tp-b"><i data-h="len" style="left:0;width:' + p.toFixed(1) + '%"></i></span>' +
            '<span class="tp-v">' + so(p, 0) + "%</span></div>";
        }).join("") + "</div>";
    }
    var top = (g ? D.giaoThuc.len.concat(D.giaoThuc.xuong) : [])
      .filter(function (p) { return p.nhom === ten; })
      .sort(function (a, b) { return b.tvl - a.tvl; }).slice(0, 8);
    if (top.length) {
      than += '<div class="hs"><div class="hs-h">Giao thức trong nhóm đang chuyển động</div>' +
        top.map(function (p) {
          return '<div class="ng"><span class="ng-t">' + esc(p.ten) + " · " + tien(p.tvl) +
            "</span>" + chip(p.d7) + "</div>";
        }).join("") + "</div>";
    }
    moHoso("Hồ sơ nhóm ngành", ten, than);
  }

  function hosoNguon(ma) {
    var t = null, i;
    for (i = 0; i < NG.TOOL.length; i++) if (NG.TOOL[i].ma === ma) t = NG.TOOL[i];
    if (!t) return;
    var lop = null;
    for (i = 0; i < NG.LOP.length; i++) if (NG.LOP[i].ma === t.lop) lop = NG.LOP[i];

    var RUI = { thap: ["len", "Thấp"], vua: ["canh", "Vừa"], cao: ["xuong", "Cao"] };
    var TIN = { cao: ["len", "Mạnh"], vua: ["", "Vừa"], "chua-ro": ["canh", "Chưa rõ"] };
    var TANG_Y = ["Không chạm ví.", "Dán địa chỉ ví công khai — vẫn không chạm quyền nào.",
      "Nối ví và ký đăng nhập — chữ ký, chưa chuyển tiền.",
      "Tiền thật rời ví: duyệt chi, hoán đổi, hoặc bắc cầu."];
    var rui = RUI[t.rui] || ["", t.rui], tin = TIN[t.tin] || ["", t.tin];

    var than = '<div class="hs"><p class="hs-p">' + esc(t.viec) + "</p></div>" +
      '<div class="hs"><div class="hs-h">Mở nó khi hỏi câu này</div>' +
      '<p class="hs-loi">' + esc(t.hoi) + "</p></div>" +
      '<div class="hs"><div class="hs-h">Quyền nó đòi ở ví bạn</div>' +
      '<div class="hs-o" style="border-left:3px solid var(--tien)">' +
      '<span>Tầng ' + t.tang + "</span><b>" + esc(TANG_Y[t.tang]) + "</b></div></div>" +
      '<div class="hs"><div class="hs-h">Xếp loại</div><div class="hs-vr">' +
      '<div class="hs-o"><span>Nhóm</span><b style="font-size:12.5px;font-family:inherit">' +
      esc(lop ? lop.ten : "—") + "</b></div>" +
      '<div class="hs-o"><span>Rủi ro nếu đi sai</span><b><span class="the"' +
      (rui[0] ? ' data-k="' + rui[0] + '"' : "") + ">" + esc(rui[1]) + "</span></b></div>" +
      '<div class="hs-o"><span>Bằng chứng độc lập</span><b><span class="the"' +
      (tin[0] ? ' data-k="' + tin[0] + '"' : "") + ">" + esc(tin[1]) + "</span></b></div>" +
      '<div class="hs-o"><span>Lấy dữ liệu tự động</span><b style="font-size:12.5px;font-family:inherit">' +
      (t.api === "co" ? "Có API" : t.api === "mot-phan" ? "API một phần" : "Không API") + "</b></div>" +
      "</div></div>";

    if (t.luu) than += '<div class="hs"><div class="hs-h">Lưu ý</div><p class="hs-luu">' + esc(t.luu) + "</p></div>";
    if (t.loi) than += '<div class="hs"><div class="hs-h">Liên quan tới kinh đô này</div><p class="hs-loi">' + esc(t.loi) + "</p></div>";

    than += '<div class="hs"><a class="hs-di" href="' + esc(t.url) + '" target="_blank" rel="noopener">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M18 13.5V19a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 19V8a1.5 1.5 0 0 1 1.5-1.5H11"/></svg>' +
      "Mở " + esc(t.ten) + "</a>" +
      '<p class="hs-p" style="margin-top:10px;font-size:11.8px;color:var(--fg-3)">Hộ Bộ không kiểm soát' +
      " trang này và không bảo đảm nội dung của nó. Kiểm lại tên miền trước khi nối ví bất cứ đâu.</p></div>";

    moHoso(lop ? lop.ten : "Nguồn dữ liệu", t.ten, than);
  }

  /* ═══════════════ SẮP XẾP BẢNG ═══════════════ */
  function ganSap(root) {
    var bangs = root.querySelectorAll("table.bang");
    Array.prototype.forEach.call(bangs, function (b) {
      var ths = b.querySelectorAll("th[data-sap]");
      Array.prototype.forEach.call(ths, function (th) {
        /* Nghe ở NÚT, nhưng `aria-sort` vẫn ghi lên <th> — ARIA đặt
           thuộc tính đó ở ô tiêu đề, không ở nút bên trong. */
        var nut = th.querySelector("button.sap") || th;
        nut.addEventListener("click", function () {
          var cot = Array.prototype.indexOf.call(th.parentNode.children, th);
          var xuong = th.getAttribute("aria-sort") !== "descending";
          Array.prototype.forEach.call(ths, function (x) { x.removeAttribute("aria-sort"); });
          th.setAttribute("aria-sort", xuong ? "descending" : "ascending");
          var tb = b.tBodies[0];
          var rows = Array.prototype.slice.call(tb.rows);
          rows.sort(function (r1, r2) {
            /* `data-v` là giá trị SỐ THẬT, không phải chữ hiển thị.
               Sắp theo chữ thì "9,8 tỷ $" đứng trên "41,2 tỷ $" vì
               '9' > '4' — một bảng xếp hạng sai mà trông rất bình
               thường. */
            var a = Number(r1.cells[cot].getAttribute("data-v"));
            var c = Number(r2.cells[cot].getAttribute("data-v"));
            if (!isFinite(a)) a = -Infinity;
            if (!isFinite(c)) c = -Infinity;
            return xuong ? c - a : a - c;
          });
          rows.forEach(function (r) { tb.appendChild(r); });
        });
      });
    });
  }

  /* ═══════════════ TUYẾN ═══════════════ */

  var IC = {
    tq: '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
    dt: '<path d="M4 6h6a4 4 0 0 1 4 4v4a4 4 0 0 0 4 4h2"/><path d="M4 18h6"/><path d="m17 5 3 3-3 3"/>',
    kb: '<ellipse cx="12" cy="6" rx="7.5" ry="2.8"/><path d="M4.5 6v12c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8V6"/><path d="M4.5 12c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8"/>',
    nh: '<rect x="3" y="12" width="4.5" height="9" rx="1"/><rect x="9.8" y="7" width="4.5" height="14" rx="1"/><rect x="16.5" y="3" width="4.5" height="18" rx="1"/>',
    od: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v10M9.4 9.6h5.2M9.4 14.4h5.2"/>',
    ls: '<path d="M3 17.5 9 11l4 4 7.5-8.5"/><path d="M15 6.5h5.5V12"/>',
    an: '<path d="M12 3 4.5 6v6c0 4.6 3.1 8 7.5 9 4.4-1 7.5-4.4 7.5-9V6z"/><path d="M9.5 12l1.8 1.8 3.4-3.6"/>',
    kn: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>'
  };

  var PHONG = [
    { ma: "tong-quan", ten: "Đại Sảnh", ic: IC.tq, ve: veTongQuan, dem: function () { return D.cheDo.diem + "/100"; } },
    { ma: "dong-tien", ten: "Dòng Tiền", ic: IC.dt, ve: veDongTien, dem: function () { return D.luoi.length + " dải"; } },
    { ma: "kho-bac", ten: "Kho Bạc", ic: IC.kb, ve: veKhoBac, dem: function () { return D.chuoi.length; } },
    { ma: "nhom-nganh", ten: "Nhóm Ngành", ic: IC.nh, ve: veNhom, dem: function () { return D.nhom.length; } },
    { ma: "tien-cho", ten: "Tiền Chờ", ic: IC.od, ve: veOnDinh, dem: function () { return D.stable.length; } },
    { ma: "loi-suat", ten: "Lợi Suất", ic: IC.ls, ve: veLoiSuat, dem: function () { return D.loiSuat.length; } },
    { ma: "an-ninh", ten: "An Ninh", ic: IC.an, ve: veAnNinh, dem: function () {
      var x = D.canhBao.filter(function (c) { return c.muc !== "g"; }).length;
      return x ? x + " ⚑" : "sạch";
    } },
    { ma: "kho-nguon", ten: "Kho Nguồn", ic: IC.kn, ve: veKhoNguon, dem: function () { return NG.TOOL.length; } }
  ];

  function svgIc(paths) {
    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' + paths + "</svg>";
  }

  function dungBen() {
    var host = document.getElementById("benMuc");
    if (!host) return;
    var lab = document.createElement("div");
    lab.className = "blab";
    lab.textContent = "Các phòng";
    host.appendChild(lab);
    PHONG.forEach(function (p) {
      var a = document.createElement("a");
      a.className = "bmuc";
      a.href = "#/" + p.ma;
      a.id = "muc-" + p.ma;
      a.innerHTML = '<span class="bic">' + svgIc(p.ic) + '</span><span class="bten">' + p.ten + "</span>" +
        (D ? '<span class="bn">' + p.dem() + "</span>" : "");
      host.appendChild(a);
    });
  }

  var than = document.getElementById("than"),
    tieu = document.getElementById("tieu"),
    ben = document.getElementById("ben");

  function ve() {
    var ma = (location.hash || "").replace(/^#\/?/, "") || "tong-quan";
    var p = null, i;
    for (i = 0; i < PHONG.length; i++) if (PHONG[i].ma === ma) p = PHONG[i];
    if (!p) p = PHONG[0];

    tieu.textContent = p.ten;
    document.title = "Hộ Bộ · " + p.ten;
    /* Dải giải nghĩa nối SAU nội dung phòng, một chỗ duy nhất cho cả tám
       phòng. Nhét vào từng hàm `ve*()` là tám chỗ phải nhớ, và phòng thứ
       chín thêm sau sẽ thiếu mà không có gì báo. */
    than.innerHTML = p.ve() + triThuc(p.ma);
    than.style.animation = "none";
    /* Ép trình duyệt tính lại bố cục rồi mới bật animation, không thì
       gán lại cùng một animation không kích hoạt lần nữa. */
    void than.offsetWidth;
    than.style.animation = "";

    PHONG.forEach(function (x) {
      var el = document.getElementById("muc-" + x.ma);
      if (el) {
        if (x.ma === p.ma) el.setAttribute("aria-current", "page");
        else el.removeAttribute("aria-current");
      }
    });

    ganSap(than);
    if (ma === "kho-nguon") locVaVe();

    /* Thanh thành phần mọc ra ở khung hình sau, để mắt thấy nó CHẠY
       tới giá trị chứ không phải đã nằm sẵn ở đó. */
    var bars = than.querySelectorAll(".tp-b i[data-rong]");
    if (bars.length) {
      requestAnimationFrame(function () {
        Array.prototype.forEach.call(bars, function (b) {
          b.style.width = b.getAttribute("data-rong") + "%";
        });
      });
    }

    if (window.innerWidth <= 940) ben.dataset.mo = "0";
    window.scrollTo(0, 0);
  }

  /* ═══════════════ GẮN ═══════════════ */

  function chay() {
    if (!D) {
      than.innerHTML = '<p class="giaithich"><b>Chưa có số liệu.</b> File ' +
        "<code>assets/js/v/dong-tien.js</code> chưa được sinh lần nào. " +
        "Chạy <code>node scripts/build-hobu.mjs</code> ở gốc repo, hoặc đợi lượt " +
        "GitHub Actions kế tiếp.</p>";
      return;
    }

    var ngay = document.getElementById("ngay");
    if (ngay) ngay.textContent = "cập nhật " + D.date;
    var song = document.getElementById("song");
    if (song) song.hidden = false;
    var giaTop = document.getElementById("giaTop");
    if (giaTop && (D.tong.btc || D.tong.eth)) {
      giaTop.innerHTML = "<span>BTC</span> <b>" + so(D.tong.btc, 0) + " $</b>" +
        "<span>ETH</span> <b>" + so(D.tong.eth, 0) + " $</b>";
    }

    /* Số liệu cũ thì nói thẳng ở đầu trang. Bot chạy 4 lượt/ngày,
       nên quá 1 ngày nghĩa là bốn lượt liên tiếp không ghi được gì —
       lúc đó mọi con số bên dưới vẫn hiện ra rất tự tin, và đó đúng
       là lý do phải có dòng này. */
    var gio = (Date.now() - new Date(D.generatedAt).getTime()) / 36e5;
    var cb = document.getElementById("canhBao");
    if (cb && isFinite(gio) && gio > 24) {
      cb.hidden = false;
      cb.innerHTML = "<b>Số liệu đã " + Math.floor(gio / 24) + " ngày chưa cập nhật.</b> " +
        "Đường ống chạy 4 lượt/ngày, nên quá một ngày nghĩa là bốn lượt liên tiếp không ghi được gì. " +
        "Mọi con số bên dưới vẫn đúng với thời điểm " + esc(D.date) + ", không đúng với hôm nay.";
    }

    var nga = (D.nguon || []).filter(function (n) { return !n.ok; });
    if (nga.length && cb && cb.hidden) {
      cb.hidden = false;
      cb.innerHTML = "<b>" + nga.length + " nguồn không lấy được ở lượt gần nhất:</b> " +
        esc(nga.map(function (n) { return n.nhan; }).join(", ")) +
        ". Phần liên quan sẽ trống chứ không được điền bằng số đoán.";
    }

    dungBen();
    window.addEventListener("hashchange", ve);
    ve();
  }

  /* mở/đóng thanh bên trên máy hẹp */
  var nut = document.getElementById("benMoNut");
  if (nut) nut.addEventListener("click", function () {
    ben.dataset.mo = ben.dataset.mo === "1" ? "0" : "1";
  });

  /* Uỷ quyền sự kiện ở cấp document: thân trang bị vẽ lại mỗi lần
     đổi phòng, nên gắn thẳng vào từng nút là gắn lại sau mỗi lần vẽ
     — và quên một chỗ thì nó chết im lặng. */
  document.addEventListener("click", function (e) {
    var el;

    el = e.target.closest ? e.target.closest("[data-nguon]") : null;
    if (el) { hosoNguon(el.getAttribute("data-nguon")); return; }

    el = e.target.closest ? e.target.closest("tr[data-mo]") : null;
    if (el) {
      var loai = el.getAttribute("data-mo"), ten = el.getAttribute("data-ten");
      if (loai === "chuoi") hosoChuoi(ten);
      else if (loai === "nhom") hosoNhom(ten);
      return;
    }

    /* Nút thoát của trạng thái trống: gỡ cả ba trục cùng lúc, và kéo
       aria-pressed lẫn ô tìm về đúng trạng thái đã gỡ — không thì
       lưới hiện đủ 47 công cụ trong khi cụm nút phía trên vẫn tô
       sáng một bộ lọc không còn tác dụng. */
    el = e.target.closest ? e.target.closest("#xoaLoc") : null;
    if (el) {
      locLop = "tat-ca"; locTang = "tat-ca"; locTim = "";
      var oTim = document.getElementById("timNguon");
      if (oTim) oTim.value = "";
      Array.prototype.forEach.call(document.querySelectorAll("#locLop button"), function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-lop") === "tat-ca"));
      });
      Array.prototype.forEach.call(document.querySelectorAll("#locTang button"), function (b) {
        b.setAttribute("aria-pressed", String(b.getAttribute("data-tang") === "tat-ca"));
      });
      locVaVe();
      return;
    }

    el = e.target.closest ? e.target.closest("#locLop button") : null;
    if (el) {
      locLop = el.getAttribute("data-lop");
      Array.prototype.forEach.call(document.querySelectorAll("#locLop button"), function (b) {
        b.setAttribute("aria-pressed", String(b === el));
      });
      locVaVe();
      return;
    }

    el = e.target.closest ? e.target.closest("#locTang button") : null;
    if (el) {
      locTang = el.getAttribute("data-tang");
      Array.prototype.forEach.call(document.querySelectorAll("#locTang button"), function (b) {
        b.setAttribute("aria-pressed", String(b === el));
      });
      locVaVe();
      return;
    }

    /* Bản đồ: rê hoặc bấm vào một nút thì tách riêng dòng của nó. */
    el = e.target.closest ? e.target.closest(".bd-o") : null;
    var bd = document.getElementById("bando");
    if (el && bd) {
      var c = el.getAttribute("data-c"), n = el.getAttribute("data-n");
      if (c) hosoChuoi(c); else if (n) hosoNhom(n);
      return;
    }
  });

  document.addEventListener("input", function (e) {
    if (e.target && e.target.id === "timNguon") { locTim = e.target.value; locVaVe(); }
  });

  /* Soi bản đồ khi rê chuột. Dùng mouseover ở cấp document vì SVG bị
     vẽ lại cùng thân trang. */
  document.addEventListener("mouseover", function (e) {
    var bd = document.getElementById("bando");
    if (!bd) return;
    var o = e.target.closest ? e.target.closest(".bd-o") : null;
    if (!o) return;
    var c = o.getAttribute("data-c"), n = o.getAttribute("data-n");
    bd.setAttribute("data-soi", "1");
    Array.prototype.forEach.call(bd.querySelectorAll(".bd-noi"), function (p) {
      var khop = c ? p.getAttribute("data-c") === c : p.getAttribute("data-n") === n;
      p.setAttribute("data-sang", khop ? "1" : "0");
    });
    Array.prototype.forEach.call(bd.querySelectorAll(".bd-nut"), function (g) {
      var khop = g === o;
      if (!khop) {
        var gc = g.getAttribute("data-c"), gn = g.getAttribute("data-n");
        khop = D.luoi.some(function (x) {
          if (c) return x.chuoi === c && (gn ? x.nhom === gn : false);
          return x.nhom === n && (gc ? x.chuoi === gc : false);
        });
      }
      g.setAttribute("data-sang", khop ? "1" : "0");
    });
  });
  document.addEventListener("mouseout", function (e) {
    var bd = document.getElementById("bando");
    if (!bd) return;
    if (e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest(".bd-o")) return;
    bd.removeAttribute("data-soi");
  });

  document.getElementById("hosoDong").addEventListener("click", dongHoso);
  scrim.addEventListener("click", dongHoso);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") dongHoso();
  });

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", chay);
  else chay();
})();
