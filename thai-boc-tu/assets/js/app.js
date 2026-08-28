/* ═══════════════════════════════════════════════════════
   THÁI BỘC TỰ — giao diện.

   Sáu phòng, một tuyến hash, không khung nào ngoài trình duyệt.

   ── BA LUẬT CHẠY XUYÊN FILE ───────────────────────────

   1. KHÔNG BỊA SỐ. Thiếu dữ liệu thì vẽ "—", không vẽ 0. Ô trống
      nói "chưa đo được"; số 0 nói "đo được và bằng không". Ở cung
      này luật đó nặng hơn mọi cung khác, vì năm toa (DePIN, AI,
      danh tính, game, meme) KHÔNG đo được bằng TVL — vẽ 0 cho
      chúng là nói "năm toa này rỗng", một câu sai hẳn.

   2. ĐO ĐƯỢC và LUẬN RA không bao giờ trông giống nhau. Thứ tự bị
      đốt và thang tiến hoá là LUẬN — chúng luôn mang nhãn "luận"
      và không bao giờ nằm chung một bảng với con số đo được.

   3. MỌI CON SỐ TRUY NGƯỢC ĐƯỢC. Mỗi toa mở ra là thấy đúng những
      category DefiLlama đã cộng vào nó. Không đồng ý với cách xếp
      thì vẫn thấy được thành phần mà tự xếp lại.

   ── HAI NGUỒN, KHỚP BẰNG MÃ TOA ───────────────────────
   `window.THAIBOC`     — bot sinh 4 lượt/ngày (số)
   `window.THAIBOC_TOA` — viết tay (chữ)

   Chúng khớp nhau bằng mã `t01`…`t18`. Lệch mã là hỏng thật, nên
   `dungTau()` báo thẳng ra màn hình chứ không lặng lẽ bỏ qua toa
   đó — một toa biến mất khỏi bảng mà không ai biết còn tệ hơn một
   dòng báo lỗi xấu xí.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var D = window.THAIBOC || null;
  var S = window.THAIBOC_TOA || { TOA: [], THANG: [], THIEU: [], CUNG: {} };
  /* Lớp tri thức nền — `knowledge-os/sinh.mjs` ghi ra assets/js/v/tri-thuc.js,
     mang cả dữ liệu lẫn hàm vẽ. Nó KHÔNG đụng con số nào: TVL, tập trung,
     thứ tự bị đốt đều tính y như cũ. Việc duy nhất của nó là trả lời "toa
     này giải bài toán kinh tế gốc nào", và mỗi câu đến từ đâu.

     Nó đứng cùng bậc nhận thức với `songSot` — LUẬN chứ không phải số đo —
     nên trong hồ sơ nó cũng đeo huy hiệu LUẬN. Thiếu file thì hồ sơ vẫn
     đủ, chỉ không có khối giải nghĩa. */
  var TT = window.TRI_THUC || null;
  /* Nguồn thứ ba, sinh riêng và có thể vắng: GitHub có thể chạm hạn
     mức trong khi DefiLlama vẫn chạy. Vắng thì đúng một phòng báo
     thiếu, các phòng khác không biết gì cả. */
  var CT = window.THAIBOC_CT || null;
  /* Nguồn thứ tư: tin từ sáu toà soạn/blog bên ngoài. Cũng có thể
     vắng độc lập với ba nguồn kia. */
  var TIN = window.THAIBOC_TIN || null;
  /* Lớp phán đoán của model cho từng bài tin. Tách hẳn khỏi TIN —
     bài báo là dữ liệu, phân tích là phán đoán, và ranh giới đó
     phải có từ tầng file chứ không chỉ ở giao diện. */
  var PT = window.THAIBOC_PT || null;

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

  /* Tiền theo bậc tiếng Việt — cùng thang với Hộ Bộ, để hai cung
     đọc số giống nhau. */
  function tien(n) {
    if (n == null || !isFinite(n)) return "—";
    var a = Math.abs(n);
    if (a >= 1e12) return so(n / 1e12, 2) + " ngh.tỷ $";
    if (a >= 1e9) return so(n / 1e9, a >= 1e11 ? 0 : 1) + " tỷ $";
    if (a >= 1e6) return so(n / 1e6, a >= 1e8 ? 0 : 1) + " tr $";
    if (a >= 1e3) return so(n / 1e3, 0) + " ng $";
    return so(n, 0) + " $";
  }

  function pt(x, d) {
    if (x == null || !isFinite(x)) return "—";
    return so(x * 100, d == null ? 1 : d) + "%";
  }

  /* Tên thước đo, hiện ngay dưới mỗi con số. Không có dòng này thì
     78 tỷ của toa nền và 307 tỷ của toa tiền ổn định trông như
     cùng một phép đo, mà chúng là hai thước khác hẳn nhau. */
  var TEN_THUOC = {
    "tvl-giao-thuc": "TVL giao thức",
    "tvl-chuoi": "TVL toàn chuỗi",
    "luu-hanh": "lượng lưu hành",
    "khong-do-duoc": "TVL không đo được toa này"
  };

  /* `n` là chữ thường và LUÔN được escape — nó nhận số đếm từ dữ
     liệu. Nhãn HTML (ví dụ huy hiệu "LUẬN") đi qua `nhan`, tham số
     riêng, chứ không nhét vào `n`: nhét vào đó thì esc() biến thẻ
     thành chữ và huy hiệu hiện ra dưới dạng `&lt;span…`. Đã dính
     đúng lỗi đó một lần, và nó dính ở chính hai phòng cần huy hiệu
     nhất — hai phòng bày phần LUẬN. */
  /* `than` đi qua .khoi-than chứ KHÔNG nhả thẳng vào .khoi. Lớp đó đã
     có sẵn trong app.css và Hộ Bộ vẫn dùng, nhưng cung này chưa từng
     gọi tới — nên tiêu đề và phần luận thụt vào 17px còn nội dung thì
     dán sát viền thẻ, và mọi thẻ con có viền riêng (.dot, .sk, .tin,
     .cua, .ct) chạm đúng vào viền ngoài. Hai đường kẻ chồng nhau đọc
     ra như lỗi dựng chứ không như một dải tràn viền cố ý. */
  /* Hàng tiêu đề mang BA thứ khác hẳn nhau, và `n` trước đây gánh hai
     trong ba: vừa là SỐ ĐẾM ("10 bậc", "9/14 còn động"), vừa là LỜI
     MỜI BẤM ("bấm một toa để mở hồ sơ"). Cả hai in ra cùng một ô chữ
     máy xám nhạt canh phải, nên một câu sai khiến đọc ra như một con
     số — và nó lại là chữ mờ nhất khối, nằm xa danh sách nhất. Thứ
     duy nhất nói rằng ba danh sách kia bấm được thì không ai thấy.
     Nay `bam` là tham số riêng: chữ thường, chip, đứng ngay sau tên
     khối. `n` giữ nguyên vai DỮ LIỆU. */
  function khoi(tieu, n, than, y, nhan, bam) {
    return '<section class="khoi"><div class="khoi-dinh"><h2>' + esc(tieu) + "</h2>" +
      (nhan || "") +
      (bam ? '<span class="bam">' + esc(bam) + "</span>" : "") +
      (n ? '<span class="n">' + esc(n) + "</span>" : "") + "</div>" +
      (y ? '<div class="khoi-y">' + y + "</div>" : "") +
      '<div class="khoi-than">' + than + "</div></section>";
  }

  var HUY_LUAN = '<span class="luan">LUẬN</span>';

  /* Dùng đúng bộ lớp .nhan/.to/.duoi của khối "ô số" dùng chung —
     đừng đặt lớp mới cho cùng một thứ, hai cung cạnh nhau mà ô số
     lệch nhau vài pixel là thấy ngay. */
  function oSo(ten, gt, y) {
    return '<div class="o-so"><div class="nhan">' + esc(ten) + "</div>" +
      '<div class="to">' + gt + "</div>" +
      (y ? '<div class="duoi">' + y + "</div>" : "") +
      "</div>";
  }

  /* ═══════════════ CHỖ RỖNG PHẢI TỰ NÓI VÌ SAO ═══════════════
     Luật 1 của cung — "thiếu dữ liệu thì vẽ gạch, không vẽ 0" — mới
     canh được từng Ô. Nó không canh được cả một DANH SÁCH rỗng, mà
     chín danh sách ở đây đều dựng bằng `.map().join("")`: nguồn hụt
     một lượt là ra đúng một cái <div> không có con nào.

     Chỗ rỗng ấy tệ hơn số 0 chứ không nhẹ hơn. Số 0 nói sai một câu;
     chỗ trống không nói câu nào, nên người đọc tự điền — và ba câu
     họ có thể điền ("trang hỏng", "bằng không", "chưa đo được") thì
     chỉ một câu đúng. Không lỗi nào báo, và thước "ô trống" cũng
     không đếm được: nó đếm dấu "—", mà ở đây không có lấy một dấu.

     Nên mỗi chỗ rỗng mang một câu RIÊNG, nói đúng nguồn nào hụt và
     trống ấy nghĩa là gì. Một câu chung ("Không có dữ liệu") thì lại
     về đúng chỗ trống câm, chỉ tốn thêm một dòng chữ. */
  function hoacTrong(html, vi, tot) {
    if (html) return html;
    return '<p class="trong"' + (tot ? ' data-tot="1"' : "") + ">" + vi + "</p>";
  }

  function bang(cot, hang, vi) {
    var th = cot.map(function (c) {
      return "<th" + (c.rong ? ' style="width:' + c.rong + '"' : "") + ">" + esc(c.t) + "</th>";
    }).join("");
    /* Bảng rỗng giữ nguyên <thead>: cột nào lẽ ra có mặt vẫn đọc
       được, nên người xem biết mình đang thiếu CÁI GÌ. */
    var than = hang || '<tr><td class="trong" colspan="' + cot.length + '">' +
      (vi || "Không dòng nào ở lượt dữ liệu này.") + "</td></tr>";
    return '<div class="cuon"><table class="bang"><thead><tr>' + th +
      "</tr></thead><tbody>" + than + "</tbody></table></div>";
  }

  /* Ghép số (bot) với chữ (viết tay). Lệch mã thì trả về danh sách
     lệch để phòng nào cũng báo được, thay vì âm thầm thiếu toa. */
  function ghep() {
    var soTheoMa = {};
    (D ? D.toa : []).forEach(function (t) { soTheoMa[t.ma] = t; });
    var ra = [], thieuSo = [], thuaSo = {};
    for (var k in soTheoMa) thuaSo[k] = true;
    S.TOA.forEach(function (c) {
      var s = soTheoMa[c.ma];
      if (!s) { thieuSo.push(c.ma); return; }
      delete thuaSo[c.ma];
      ra.push({ c: c, s: s });
    });
    return { toa: ra, thieuSo: thieuSo, thuaSo: Object.keys(thuaSo) };
  }

  var G = null;

  function canhLech() {
    if (!G || (!G.thieuSo.length && !G.thuaSo.length)) return "";
    var m = [];
    if (G.thieuSo.length) m.push("có chữ mà thiếu số: " + G.thieuSo.join(", "));
    if (G.thuaSo.length) m.push("có số mà thiếu chữ: " + G.thuaSo.join(", "));
    return '<p class="canhbao" style="display:block"><b>Sổ toa lệch số liệu.</b> ' +
      esc(m.join(" · ")) + ". Sửa <code>assets/js/toa.js</code> hoặc " +
      "<code>scripts/build-thaiboc.mjs</code> cho hai bên khớp mã toa.</p>";
  }

  /* ═══════════════ PHÒNG · ĐOÀN TÀU ═══════════════ */

  /* Hạng trụ lại chia ba vùng. Khai ở đây chứ không ở phòng Thứ Tự
     vì giờ CẢ HAI chỗ dùng: dải tàu tô mép theo nó, phòng Thứ Tự xếp
     hàng theo nó. Một chỗ khai, hai chỗ đọc. */
  function vungCua(h) { return h >= 13 ? "som" : h >= 7 ? "giua" : "muon"; }

  function theToa(t) {
    var s = t.s, c = t.c;
    var doDuoc = s.thuoc !== "khong-do-duoc" && s.tvl != null;
    var tt = s.tapTrung;
    return '<button class="toa" type="button" data-toa="' + esc(c.ma) + '"' +
      ' data-vung="' + vungCua(c.songSot) + '">' +
      '<div class="toa-so">TOA ' + esc(c.so) + "</div>" +
      '<div class="toa-ten">' + esc(c.ten) + "</div>" +
      '<div class="toa-gt" data-do="' + (doDuoc ? "1" : "0") + '">' +
        (doDuoc ? tien(s.tvl) : "—") + "</div>" +
      '<div class="toa-th">' + esc(TEN_THUOC[s.thuoc]) + "</div>" +
      (tt != null
        ? '<div class="toa-tt"><i data-rong="' + (tt * 100).toFixed(1) + '"></i></div>' +
          '<div class="toa-tt-n">' + so(s.soGiaoThuc, 0) + " giao thức · " +
            esc(s.tapTrungTen || "lớn nhất") + " giữ " + pt(tt, 0) + "</div>"
        : '<div class="toa-tt-n" style="margin-top:9px">' + so(s.soGiaoThuc, 0) + " giao thức</div>") +
      "</button>";
  }

  function veDoanTau() {
    var dl = D.duongLui, tc = D.traiChuoi;
    var soDo = G.toa.filter(function (t) { return t.s.thuoc !== "khong-do-duoc"; }).length;

    var oS = '<div class="luoi-so">' +
      oSo("Giao thức đang xếp toa", '<b>' + so(D.tong.soGiaoThuc, 0) + "</b>",
        D.tong.soCategory + " nhóm nguồn → 18 toa") +
      oSo("Vốn treo trên một khớp nối", "<b>" + pt(dl.tyLe, 1) + "</b>",
        dl.motN + " giao thức không khai nguồn giá dự phòng") +
      oSo("Chỉ đứng trên một chuỗi", "<b>" + so(tc.motN, 0) + "</b>",
        "giữ " + tien(tc.motTvl) + " — chuỗi đó ngã là ngã theo") +
      oSo("Toa đo được bằng số", "<b>" + soDo + "/18</b>",
        "năm toa còn lại TVL không đo nổi") +
      "</div>";

    var tau = '<div class="tau">' + hoacTrong(G.toa.map(theToa).join(""),
      "<b>Không toa nào ghép được.</b> Sổ toa <code>assets/js/toa.js</code> và " +
      "số liệu <code>assets/js/v/doan-tau.js</code> không khớp nhau ở mã toa nào. " +
      "Dòng báo lệch ở đầu phòng nói rõ mã nào thừa, mã nào thiếu.") + "</div>";

    var duY = "";
    if (D.du && D.du.cat.length) {
      duY = khoi("Phần chưa xếp toa", D.du.cat.length + " nhóm",
        '<p class="giaithich">Còn <b>' + D.du.soGiaoThuc + " giao thức</b> giữ <b>" +
        tien(D.du.tvl) + "</b> không thuộc toa nào trong thang 18 toa: " +
        '<span class="hs-ng" style="display:inline-flex;margin-left:2px">' +
        D.du.cat.map(function (c) { return "<span>" + esc(c) + "</span>"; }).join("") +
        "</span></p>",
        "Bày ra chứ không nhét bừa vào toa gần nhất. Một thang 18 toa không " +
        "ôm hết hơn trăm nhóm nguồn, và ép cho vừa thì bảng đẹp hơn rồi sai đi " +
        "mà không ai biết. Phần dư ở đây rất nhỏ so với tổng, nhưng nó phải " +
        "nhìn thấy được thì mới kiểm được.");
    }

    return canhLech() +
      khoi("Đoàn tàu đang chở gì", null, oS,
        "Bốn con số này là toàn bộ luận điểm của cung: cái đáng lo không phải " +
        "toa nào to, mà là <b>bao nhiêu thứ đang treo trên một khớp nối duy nhất</b>.") +
      khoi("Mười tám toa", G.toa.length + " toa", tau,
        "Mỗi toa một thước đo, và thước nào cũng ghi ngay dưới con số. " +
        "Toa nền đo bằng TVL toàn chuỗi, tiền ổn định đo bằng lượng lưu hành, " +
        "còn DePIN, AI, danh tính, game và meme thì <b>TVL không đo được</b> — " +
        "chẳng ai khoá vốn vào một meme coin để nó chạy. Chúng hiện “—”, " +
        "không hiện 0.", null, "bấm một toa để mở hồ sơ") +
      veTinTuc() +
      duY;
  }

  /* ═══════════════ TIN TỨC ═══════════════
     Khối này nằm trong phòng Đoàn Tàu chứ không đứng riêng, và đó
     là chủ ý: mỗi bài mang nhãn TOA, nên nó đọc tiếp ngay bên dưới
     bảng 18 toa thay vì thành một trang tin rời rạc. Một tin về
     Tether nằm cạnh con số 308 tỷ lưu hành của toa 04.

     Ảnh TRỎ THẲNG sang CDN của toà soạn — không tải về repo, xem
     lý do ở đầu scripts/build-tintuc.mjs. Ba thuộc tính bắt buộc,
     đừng bỏ cái nào:
       referrerpolicy="no-referrer"  không gửi kèm đường dẫn trang này
       loading="lazy"                ảnh dưới màn hình chưa tải
       onerror=...hidden             ảnh 404 thì ẩn hẳn khung

     Thiếu onerror thì một ảnh hỏng để lại cái icon vỡ, xấu hơn hẳn
     một thẻ không có ảnh — và tin tức thì link chết là chuyện thường. */

  function theTin(b) {
    var tenToa = null;
    if (b.toa) S.TOA.forEach(function (t) { if (t.ma === b.toa) tenToa = t; });
    var ng = b.ngay ? ngayVn(b.ngay) : null;
    var d = b.ngay ? soNgay(b.ngay) : null;
    var tuoi = d == null ? (ng || "")
      : d <= 0 ? "hôm nay" : d === 1 ? "hôm qua" : d + " ngày trước";

    return '<article class="tin">' +
      (b.anh
        ? '<a class="tin-anh" href="' + esc(b.link) + '" target="_blank" rel="noopener noreferrer">' +
          '<img src="' + esc(b.anh) + '" alt="" loading="lazy" decoding="async" ' +
          'referrerpolicy="no-referrer" ' +
          'onerror="this.parentNode.hidden=true"></a>'
        : "") +
      '<div class="tin-than">' +
        '<div class="tin-d"><span class="tin-ng">' + esc(b.nguon) + "</span>" +
          '<span class="tin-t2">' + esc(tuoi) + "</span></div>" +
        '<a class="tin-t" href="' + esc(b.link) + '" target="_blank" rel="noopener noreferrer">' +
          esc(b.tieuDe) + "</a>" +
        (b.tom ? '<p class="tin-tom">' + esc(b.tom.slice(0, 150)) + "…</p>" : "") +
        '<div class="tin-m">' +
          (tenToa
            ? '<button class="tin-toa" type="button" data-toa="' + esc(tenToa.ma) + '">toa ' +
              esc(tenToa.so) + " · " + esc(tenToa.ten) + "</button>"
            : '<span class="tin-toa" data-trong="1">chưa xếp toa</span>') +
        "</div>" +
        vePhanTich(b) +
      "</div></article>";
  }

  /* ═══════════════ LỚP PHÁN ĐOÁN AI ═══════════════
     Đây là chỗ luật xương sống của cung bị thử nặng nhất: bài báo là
     DỮ LIỆU, phân tích là PHÁN ĐOÁN, và hai thứ đó không được trông
     giống nhau.

     Nên khối này KHÁC hẳn phần trên về mọi mặt nhìn được: nền riêng,
     viền trái riêng, nhãn "PHÁN ĐOÁN AI" đứng đầu. Người lướt nhanh
     vẫn phải thấy ngay đâu là câu toà soạn viết, đâu là câu máy đoán.

     `theoDoi` cố ý KHÔNG phải "mua gì bán gì". Nó là điều sắp tới sẽ
     cho biết cách đọc này đúng hay sai — kiểm được, và tuần sau nhìn
     lại biết ngay model đúng hay sai. Một câu "mua ETH" thì không ai
     kiểm và không ai chịu trách nhiệm. */

  var TEN_MUC = {
    cao: { ten: "ẢNH HƯỞNG CAO", v: "som" },
    vua: { ten: "ẢNH HƯỞNG VỪA", v: "giua" },
    thap: { ten: "ẢNH HƯỞNG THẤP", v: "muon" }
  };

  function khoaTin(link) {
    return String(link || "").split("?")[0].replace(/\/$/, "").toLowerCase();
  }

  function vePhanTich(b) {
    if (!PT || !PT.pt) return "";
    var a = PT.pt[khoaTin(b.link)];
    if (!a) return "";
    var m = TEN_MUC[a.muc] || { ten: "?", v: "giua" };

    return '<div class="pt" data-v="' + m.v + '">' +
      '<div class="pt-d"><span class="pt-nhan">PHÁN ĐOÁN AI</span>' +
        '<span class="dot-nhan" data-v="' + m.v + '">' + m.ten + "</span></div>" +
      '<div class="pt-mach">' + a.mach.map(function (x, i) {
        return (i ? '<i aria-hidden="true">↓</i>' : "") + "<span>" + esc(x) + "</span>";
      }).join("") + "</div>" +
      '<p class="pt-d1"><b>Theo dõi:</b> ' + esc(a.theoDoi) + "</p>" +
      '<p class="pt-d2"><b>Sai nếu:</b> ' + esc(a.nguoc) + "</p>" +
      "</div>";
  }

  function veTinTuc() {
    if (!TIN || !TIN.bai || !TIN.bai.length) {
      return khoi("Tin tức", null,
        '<p class="giaithich"><b>Chưa có bản tin nào.</b> File ' +
        "<code>assets/js/v/tin-tuc.js</code> chưa được sinh, hoặc lượt gần nhất " +
        "không nguồn nào trả bài. Chạy <code>node scripts/build-tintuc.mjs</code> " +
        "ở gốc repo, hoặc đợi lượt GitHub Actions kế tiếp.</p>", null);
    }

    var nga = (TIN.nguon || []).filter(function (n) { return !n.ok; });
    var ok = (TIN.nguon || []).filter(function (n) { return n.ok; });
    var gio = Math.floor((Date.now() - new Date(TIN.generatedAt).getTime()) / 36e5);

    var dsNguon = '<p class="tin-nguon">Đọc từ ' + ok.length + "/" +
      (TIN.nguon || []).length + " nguồn: " +
      ok.map(function (n) { return "<b>" + esc(n.nhan) + "</b>"; }).join(" · ") +
      (nga.length
        ? '. <span style="color:var(--canh)">Không lấy được: ' +
          esc(nga.map(function (n) { return n.nhan; }).join(", ")) + ".</span>"
        : ".") +
      " Lấy cách đây " + gio + " giờ.</p>";

    return khoi("Thế giới bên ngoài đang nói gì",
      TIN.tong.soBai + " bài · " + TIN.tong.soXepToa + " xếp được toa",
      dsNguon + '<div class="tin-l">' + TIN.bai.map(theTin).join("") + "</div>",
      "Tiêu đề và ảnh <b>lấy thẳng từ bài gốc</b>; bấm vào là sang đúng trang của " +
      "toà soạn đó, cung này không chép lại nội dung của ai. Ảnh nằm trên máy chủ " +
      "của họ chứ không tải về đây — nên mở trang này là trình duyệt bạn có gọi " +
      "sang CDN của mấy toà soạn ấy. " +
      "<b>Nhãn toa là phần cung này thêm vào</b>: khớp từ khoá trên tiêu đề và tóm " +
      "tắt, bấm vào để mở hồ sơ toa đó. Khớp từ khoá thì sai được, nên bài nào " +
      "không chắc sẽ để “chưa xếp toa” thay vì đoán bừa — gắn nhãn sai còn tệ hơn " +
      "không gắn, vì người đọc sẽ tin cái nhãn.");
  }

  /* ═══════════════ PHÒNG · KHỚP NỐI ═══════════════ */

  function theSk(o, max) {
    var lui = o.tvl - o.tvlRieng;
    var wR = max > 0 ? (o.tvlRieng / max) * 100 : 0;
    var wL = max > 0 ? (lui / max) * 100 : 0;
    /* <button>, không phải <div>. Mở hồ sơ là việc của một NÚT, và
       hai danh sách kia (.toa, .dot) đã là nút từ đầu — chỉ danh sách
       này bị bỏ lại. Hậu quả im lặng: cả phòng Khớp Nối chuột mới
       bấm được, bàn phím không tab tới được ô nào, và vì không thẻ
       nào nhận được focus nên viền :focus-visible cũng chưa bao giờ
       hiện ở đây.

       Ruột phải là nội dung DÒNG cho hợp lệ trong <button>: <div>
       và <p> đổi sang <span>, còn hình thức giữ nguyên bằng
       display:flex/block đã khai trong app.css. */
    return '<button class="sk" type="button" data-oracle="' + esc(o.ten) + '">' +
      '<span class="sk-d"><span class="sk-t">' + esc(o.ten) + "</span>" +
      '<span class="sk-v">' + tien(o.tvl) + " · " + o.soGiaoThuc + " giao thức</span></span>" +
      '<span class="sk-b">' +
        '<i data-p="rieng" data-rong="' + wR.toFixed(2) + '"></i>' +
        '<i data-p="lui" data-rong="' + wL.toFixed(2) + '"></i>' +
      "</span>" +
      '<span class="sk-y"><b>' + tien(o.tvlRieng) + "</b> (" + o.soRieng +
      " giao thức) khai <b>đúng mình nó</b> và không nguồn nào khác — mất khớp này " +
      "là mất giá, không có đường lui. Phần còn lại (" + tien(lui) +
      ") có khai thêm ít nhất một nguồn.</span></button>";
  }

  function veKhopNoi() {
    var dl = D.duongLui;
    var max = D.oracle.length ? D.oracle[0].tvl : 0;

    var dan = '<div class="luoi-so">' +
      oSo("Không có đường lui", "<b>" + tien(dl.motTvl) + "</b>",
        dl.motN + " giao thức khai đúng một nguồn giá") +
      oSo("Còn đường lui", "<b>" + tien(dl.nhieuTvl) + "</b>",
        dl.nhieuN + " giao thức khai từ hai nguồn trở lên") +
      oSo("Tỷ lệ vốn treo một khớp", "<b>" + pt(dl.tyLe, 1) + "</b>",
        "trong tổng số vốn có khai nguồn giá") +
      "</div>";

    var ct = '<div class="chu-thich">' +
      '<span><i style="background:var(--xuong)"></i> vốn treo trên đúng khớp này</span>' +
      '<span><i style="background:var(--len)"></i> vốn còn nguồn dự phòng khác</span>' +
      "</div>";

    var ds = D.oracle.map(function (o) { return theSk(o, max); }).join("");
    /* Chú thích màu đi CÙNG danh sách, không đứng riêng: một bảng chú
       thích cho hai dải màu không tồn tại thì đọc như hai dải đã bị
       mất, chứ không như "chưa có gì để tô màu". */
    var dsKhoi = hoacTrong(ds && ct + ds,
      "<b>Không khớp nối nào để bày.</b> Lượt này không giao thức nào khai " +
      "nguồn giá, nên không có gì để xếp hạng. Trống ở đây nghĩa là <i>thiếu " +
      "khai báo</i>, không phải không ai dùng oracle — và con số “không có " +
      "đường lui” ở khối trên vốn đã là sàn dưới, nên nó cũng đang đọc trên " +
      "cùng chỗ hụt này.");

    var chuoi = bang(
      [{ t: "Chuỗi", rong: "34%" }, { t: "Giao thức đứng trên" }, { t: "TVL của chuỗi" }],
      D.khopChuoi.map(function (c) {
        return "<tr><td><b>" + esc(c.ten) + "</b></td><td class=\"mono\">" +
          so(c.soGiaoThuc, 0) + "</td><td class=\"mono\">" +
          (c.tvl == null ? "—" : tien(c.tvl)) + "</td></tr>";
      }).join(""),
      "Lượt này không giao thức nào khai mình đứng trên chuỗi nào, " +
      "nên chưa đếm được chuỗi nào."
    );

    var tc = D.traiChuoi;
    var traiY = '<p class="giaithich">Trong số giao thức có khai chuỗi: <b>' +
      so(tc.motN, 0) + "</b> chỉ đứng trên <b>một chuỗi duy nhất</b> và giữ " +
      tien(tc.motTvl) + "; <b>" + so(tc.nhieuN, 0) + "</b> đứng trên nhiều chuỗi và giữ " +
      tien(tc.nhieuTvl) + ". Số đông là nhóm thứ nhất, nhưng phần lớn tiền nằm ở nhóm " +
      "thứ hai — nghĩa là vốn lớn đã tự trải ra, còn cái đuôi dài thì chưa.</p>";

    return khoi("Bao nhiêu vốn treo trên một khớp nối", null, dan,
      "Đây là con số cung này tồn tại để nói. Một giao thức khai đúng một nguồn " +
      "giá là một giao thức không có đường lui: nguồn đó sai hoặc chết thì tài sản " +
      "thế chấp bị định giá sai, và cái sai đó chạy thẳng vào thanh lý.") +
      /* Cùng lối nhắc với khối "Mười tám toa": danh sách nào bấm được
         thì nói ngay ở hàng tiêu đề. Ba danh sách cùng mở hồ sơ mà
         chỉ một cái nói ra điều đó thì hai cái kia đọc như bảng chết. */
      khoi("Vốn hoá không phải tầm quan trọng hệ thống",
        D.oracle.length + " khớp",
        dsKhoi,
        "Một dự án oracle có thể có vốn hoá khiêm tốn mà vẫn là chỗ hàng chục tỷ " +
        "đô đang dựa vào. Bảng vốn hoá không bao giờ nói ra điều đó, vì nó đo " +
        "<b>giá của token</b> chứ không đo <b>lượng vốn phụ thuộc</b>. Bảng dưới " +
        "đo cái thứ hai — tự tính từ khai báo của từng giao thức, không lấy từ " +
        "bảng tổng nào.", null, "bấm một khớp để mở hồ sơ") +
      khoi("Đứng trên chuỗi nào", D.khopChuoi.length + " chuỗi đông nhất", traiY + chuoi,
        "Chuỗi cũng là một khớp nối: giao thức chỉ đứng trên một chuỗi thì chuỗi " +
        "đó ngã là nó ngã theo, không cần ai tấn công trực tiếp vào nó.");
  }

  /* ═══════════════ PHÒNG · THỨ TỰ BỊ ĐỐT ═══════════════ */

  var TEN_VUNG = { som: "BỎ SỚM", giua: "GIỮA", muon: "TRỤ LẠI" };

  function veThuTu() {
    var ds = G.toa.slice().sort(function (a, b) { return b.c.songSot - a.c.songSot; });
    var hang = ds.map(function (t) {
      var v = vungCua(t.c.songSot);
      var doDuoc = t.s.thuoc !== "khong-do-duoc" && t.s.tvl != null;
      return '<button class="dot" type="button" data-vung="' + v + '" data-toa="' + esc(t.c.ma) + '">' +
        '<span class="dot-h">' + t.c.songSot + "</span>" +
        '<span class="dot-t">' + esc(t.c.ten) +
          '<span class="dot-nhan" data-v="' + v + '">' + TEN_VUNG[v] + "</span>" +
          "<i>toa " + esc(t.c.so) + " · " + esc(t.c.lat) + "</i></span>" +
        '<span class="dot-s">' + (doDuoc ? tien(t.s.tvl) : "không đo được") + "</span>" +
        "</button>";
    }).join("");

    return khoi("Đoàn tàu tự tháo mình ra theo thứ tự nào", null,
      '<div class="dot-l">' + hoacTrong(hang,
        "<b>Chưa xếp được thứ tự nào.</b> Thứ tự này đọc từ hạng trụ lại của " +
        "từng toa trong <code>assets/js/toa.js</code>, và lượt này không toa nào " +
        "ghép được với số liệu. Trống ở đây là <i>chưa ghép được</i>, không phải " +
        "đoàn tàu không có thứ tự.") + "</div>",
      "Đọc từ trên xuống là đọc đúng thứ tự bị bỏ khi nhiên liệu cạn: trên cùng " +
      "bỏ trước nhất, dưới cùng trụ lại lâu nhất. <b>Đây là suy luận theo thứ tự " +
      "phụ thuộc, không phải số đo và không phải dự báo giá.</b> Cách đọc một " +
      "hạng: “bỏ toa này thì phần còn lại có chạy tiếp được không?” Bỏ meme thì " +
      "kết sổ vẫn chạy, khối vẫn được tạo, tài sản vẫn chuyển. Bỏ kết sổ thì " +
      /* Danh sách THỨ BA mở hồ sơ, và là cái duy nhất chưa từng nói ra
         điều đó — chú thích ở phòng Khớp Nối đã ghi đúng bệnh này rồi
         sửa cho hai danh sách kia mà bỏ sót chính nó. */
      "không còn gì cả.", HUY_LUAN, "bấm một toa để mở hồ sơ") +
      khoi("Một điều đáng chú ý trong bảng trên", null,
        '<p class="giaithich">Năm toa mà TVL <b>không đo nổi</b> — DePIN, AI, danh tính, ' +
        "game, meme — nằm gần hết ở nửa trên của bảng, tức nửa bị bỏ trước. Đó " +
        "không phải trùng hợp, và cũng không phải bằng chứng chúng vô giá trị. " +
        "Nó là cùng một sự thật nhìn từ hai phía: <b>chưa có vốn khoá nào phụ " +
        "thuộc vào chúng để chạy</b>, nên vừa không có gì để TVL đo, vừa không " +
        "có gì gãy theo nếu chúng biến mất.</p>", null);
  }

  /* ═══════════════ PHÒNG · CỬA NỐI ═══════════════ */

  var IC_DI = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" ' +
    'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12.5 6l6 6-6 6"/></svg>';

  /* Đếm CUNG phân biệt, không đếm cửa: năm cửa Hộ Bộ chỉ là năm
     phòng của cùng một cung. */
  function demCung() {
    var t = {};
    G.toa.forEach(function (x) {
      (x.c.cung || []).forEach(function (k) {
        if (S.CUNG[k]) t[S.CUNG[k].goc || k] = 1;
      });
    });
    return Object.keys(t).length;
  }

  function veCuaNoi() {
    /* Gom theo cung đích: mỗi cung một thẻ, kèm đúng những toa trỏ
       sang nó. Ngược lại (mỗi toa một thẻ) thì Hộ Bộ hiện năm lần
       và bảng thành danh sách trùng lặp. */
    var theo = {};
    G.toa.forEach(function (t) {
      (t.c.cung || []).forEach(function (k) {
        if (!S.CUNG[k]) return;
        theo[k] = theo[k] || { k: k, toa: [] };
        theo[k].toa.push(t.c);
      });
    });
    var ds = Object.keys(theo).map(function (k) { return theo[k]; })
      .sort(function (a, b) { return b.toa.length - a.toa.length; });

    var the = ds.map(function (x) {
      var c = S.CUNG[x.k];
      return '<a class="cua" href="' + esc(c.duong) + '">' +
        '<div class="cua-t">' + esc(c.ten) + IC_DI + "</div>" +
        '<p class="cua-y">Đọc tiếp từ ' + (x.toa.length > 1 ? x.toa.length + " toa" : "toa " + esc(x.toa[0].so)) +
        " của đoàn tàu.</p>" +
        '<div class="cua-toa">' + x.toa.map(function (t) {
          return "<span>toa " + esc(t.so) + " · " + esc(t.ten) + "</span>";
        }).join("") + "</div></a>";
    }).join("");

    return khoi("Toa nào đọc tiếp ở cung nào",
      demCung() + " cung · " + ds.length + " cửa",
      '<div class="cua-l">' + hoacTrong(the,
        "<b>Chưa toa nào mở cửa sang cung khác.</b> Cửa nối khai tay trong " +
        "<code>assets/js/toa.js</code>, ở trường <code>cung</code> của từng toa. " +
        "Trống ở đây là <i>sổ toa chưa khai</i>, không phải các cung kia biến mất — " +
        "vẫn sang được bằng Cổng Thành ở khối dưới.") + "</div>",
      "Cung này chỉ vẽ <b>quan hệ giữa các toa</b>. Chi tiết bên trong từng toa " +
      "đã nằm ở cung khác rồi, nên thay vì chép lại, mỗi toa có một cửa mở thẳng " +
      "sang đó: nền tảng sang Kinh Thành, mở rộng sang Đô Sát Viện, tiền ổn định " +
      "và thanh khoản sang Hộ Bộ.") +
      khoi("Cổng Thành", null,
        '<p class="giaithich">Về <a href="../">trang chủ Cổng Thành</a> để thấy toàn bộ ' +
        "các cung.</p>", null);
  }

  /* ═══════════════ PHÒNG · THANG TIẾN HOÁ ═══════════════ */

  /* Luật 1 của cung, ở đúng chỗ dễ trượt nhất — và đã trượt thật.
     `g.muc ? g.muc + "%" : "—"` gộp HAI câu khác hẳn nhau làm một:
     0 là một đánh giá có thật ("bậc này gần như chưa có gì chạy
     được"), còn "—" nghĩa là chưa ai luận tới. Sổ toa ghi muc:0 cho
     bậc 9 và bậc 10, nên trang đang vẽ dấu gạch ở đúng hai bậc mà
     tài liệu nguồn đã nói rõ nhất — nói "không biết" thay cho một
     câu người viết sổ đã dám viết ra.

     Hai phòng cùng đọc S.THANG nên chỉ có MỘT hàm; để hai bản chép
     là bảo đảm ngày nào đó chúng lệch nhau. */
  function mucLuan(m) {
    return (m == null || !isFinite(m)) ? "—" : so(m, 0) + "%";
  }
  function coMuc(m) { return m != null && isFinite(m); }

  function veThang() {
    var tg = S.THANG.map(function (g) {
      /* Không có `muc` thì KHÔNG vẽ thanh: một máng rỗng đọc y hệt
         0%, tức là lại bịa ra con số vừa mới cẩn thận không bịa.
         Và nó chặn luôn `width:undefined%` rò ra HTML. */
      return '<div class="tg"><div class="tg-s">' + esc(g.so) + "</div><div>" +
        '<div class="tg-t">' + esc(g.ten) +
        '<span class="tg-p">' + mucLuan(g.muc) + " luận</span></div>" +
        (coMuc(g.muc) ? '<div class="tg-b"><i data-rong="' + g.muc + '"></i></div>' : "") +
        '<p class="tg-y">' + esc(g.y) + "</p></div></div>";
    }).join("");

    /* Danh sách nút thắt là phần LUẬN, nhưng huy hiệu tình trạng thì
       ĐO ĐƯỢC — lấy từ phòng Công Trường. Một nút thắt kèm câu "chưa
       ai xây" đọc khác hẳn cùng nút thắt đó đứng trơ một mình. */
    var th = S.THIEU.map(function (x) {
      var n = null;
      if (CT) (CT.nut || []).forEach(function (y) { if (y.ma === x.ma) n = y; });
      var v = !n ? "som" : n.soDangXay > 0 ? "muon" : "giua";
      var nhan = !CT ? "" : !n ? "CHƯA AI XÂY"
        : n.soDangXay > 0 ? n.soDangXay + "/" + n.soKho + " ĐANG XÂY"
        : n.soKho + " KHO, ĐỨNG IM";
      return '<div class="thieu"><div class="thieu-t">' + esc(x.ten) +
        (nhan ? '<span class="dot-nhan" data-v="' + v + '">' + esc(nhan) + "</span>" : "") +
        "</div><p class=\"thieu-y\">" + esc(x.y) + "</p></div>";
    }).join("");

    return khoi("Đoàn tàu đã đi được bao xa", null, tg,
      "<b>Không một con số nào trong khối này là số đo.</b> Đây là đánh giá kiến " +
      "trúc: phần nào của viễn cảnh đã có bản chạy được, phần nào còn là giả " +
      "thuyết. Một thanh phần trăm trông y hệt một phép đo, nên phải nói thẳng " +
      "rằng nó không phải — không có API nào chấm được “kinh tế tác tử đã xong " +
      "25%”.", HUY_LUAN) +
      khoi("Những khớp nối còn thiếu", S.THIEU.length + " chỗ",
        '<div class="thieu-l">' + hoacTrong(th,
          "<b>Sổ toa chưa khai nút thắt nào.</b> Danh sách này viết tay ở " +
          "<code>THIEU</code> trong <code>assets/js/toa.js</code>. Trống nghĩa là " +
          "<i>chưa ai viết ra</i>, không phải đã hết chỗ thiếu — chưa có API nào " +
          "chấm được câu đó, nên không có nguồn nào điền hộ.") + "</div>",
        "Câu hỏi lớn của blockchain đã không còn là nhanh hơn hay rẻ hơn — đó là " +
        "câu hỏi của khoảng 2017–2022. Những chỗ dưới đây là thứ chặn đoàn tàu " +
        "tự chạy, và không chỗ nào giải được bằng thêm thông lượng. " +
        (CT
          ? "Huy hiệu bên phải mỗi nút là phần <b>đo được</b>, hỏi thẳng GitHub: " +
            "nút đó có kho mã nào đang bị đụng vào không. Xem chi tiết ở " +
            '<a href="#/cong-truong">Công Trường</a>.'
          : ""));
  }

  /* ═══════════════ PHÒNG · CÔNG TRƯỜNG ═══════════════
     Phòng này trả lời câu "thế giới đang làm tới đâu" bằng thứ ĐO
     ĐƯỢC, đặt cạnh thang tiến hoá vốn chỉ là LUẬN.

     Hai nguồn ghép lại ở đây, và cố ý không gộp ở khâu sinh dữ liệu:
       THAIBOC     — tiền (DefiLlama)
       THAIBOC_CT  — người đang làm (GitHub)

     Bậc 1–3 có dấu hiệu bằng TIỀN vì chúng đã thành hạ tầng thật.
     Bậc 4 trở lên chưa có tiền để đo, chỉ còn đo được bằng CÔNG
     TRƯỜNG: có kho mã nào đang được đụng vào không. Và mấy bậc cuối
     thì đến công trường cũng không có — đó là câu trả lời, không
     phải chỗ dữ liệu bị thiếu. */

  var TRANG_KHO = {
    "dang-xay": { ten: "ĐANG XÂY", v: "muon" },
    "cham": { ten: "CHẬM", v: "giua" },
    "nguoi": { ten: "NGUỘI", v: "som" },
    "khong-hoi-duoc": { ten: "KHÔNG HỎI ĐƯỢC", v: "som" },
    "khong-ro": { ten: "KHÔNG RÕ", v: "giua" }
  };

  function ngayVn(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    if (isNaN(d.getTime())) return "—";
    var p = function (n) { return String(n).padStart(2, "0"); };
    return p(d.getUTCDate()) + "/" + p(d.getUTCMonth() + 1) + "/" + d.getUTCFullYear();
  }

  function soNgay(iso) {
    if (!iso) return null;
    var t = new Date(iso).getTime();
    return isFinite(t) ? Math.floor((Date.now() - t) / 86400000) : null;
  }

  /* Dấu hiệu bằng TIỀN cho ba bậc đầu. Lấy thẳng từ bảng đoàn tàu
     nên không có con số nào ở đây là mới — đây chỉ là cùng số liệu
     đó nhìn theo trục "đã đi tới đâu" thay vì trục "toa nào to". */
  function toaTheoMa(ma) {
    var r = null;
    (D.toa || []).forEach(function (t) { if (t.ma === ma) r = t; });
    return r;
  }
  function cong() {
    var s = 0, co = false;
    for (var i = 0; i < arguments.length; i++) {
      var t = toaTheoMa(arguments[i]);
      if (t && t.thuoc !== "khong-do-duoc" && t.tvl != null) { s += t.tvl; co = true; }
    }
    return co ? s : null;
  }
  var DO_TIEN = {
    "1": function () {
      return [["TVL toàn chuỗi", tien(D.tong.tvlChuoi)],
              ["Stablecoin lưu hành", tien(D.tong.luuHanhStable)]];
    },
    "2": function () {
      return [["Chợ · tín dụng · phái sinh", tien(cong("t05", "t06", "t07"))],
              ["Đặt cọc & tái đặt cọc", tien(cong("t08"))]];
    },
    "3": function () {
      var t9 = toaTheoMa("t09"), t11 = toaTheoMa("t11");
      return [["Tài sản thế giới thật", t9 ? tien(t9.tvl) : "—"],
              ["Giao thức DePIN", t11 ? so(t11.soGiaoThuc, 0) + " cái · TVL không đo được" : "—"]];
    }
  };

  /* Nút thắt của một bậc, kèm tình trạng công trường lấy từ CT. */
  function nutCuaBac(bac) {
    return (S.THIEU || []).filter(function (x) { return x.giaiDoan === bac; })
      .map(function (x) {
        var n = null;
        if (CT) (CT.nut || []).forEach(function (y) { if (y.ma === x.ma) n = y; });
        return { t: x, n: n };
      });
  }

  function veCongTruong() {
    if (!CT) {
      return khoi("Chưa có số liệu công trường", null,
        '<p class="giaithich"><b>File <code>assets/js/v/cong-truong.js</code> chưa được sinh lần nào.</b> ' +
        "Chạy <code>node scripts/build-congtruong.mjs</code> ở gốc repo, hoặc đợi lượt " +
        "GitHub Actions kế tiếp. Phần đoàn tàu và khớp nối vẫn chạy bình thường — " +
        "hai nguồn tách nhau đúng để một bên ngã không kéo bên kia.</p>", null);
    }

    /* HAI con số, không phải một — và gộp chúng lại là nói quá.

       Bản đầu chỉ có một ô "bậc cao nhất còn dấu hiệu" = 7, vì bậc 7
       có kho toà án phi tập trung còn commit. Nhưng "một kho 81 sao
       đang chạy" và "78 tỷ đô đang nằm trên đó" là hai loại bằng
       chứng khác hẳn nhau, và trộn lại thì bảng nói rằng thế giới
       đã đi tới bậc 7 — sai hẳn.

       Nên tách: bậc cuối còn đo được bằng TIỀN là chỗ đã thành hạ
       tầng thật; bậc xa nhất có CÔNG TRƯỜNG động là chỗ mới có người
       đang xây. Khoảng cách giữa hai số đó chính là phần việc còn
       lại. */
    var bacTien = 0, bacXay = 0, i;
    for (i = 1; i <= 10; i++) {
      if (DO_TIEN[String(i)]) bacTien = i;
      var coXay = nutCuaBac(i).some(function (x) { return x.n && x.n.soDangXay > 0; });
      if (coXay) bacXay = i;
    }

    var trong = (S.THIEU || []).filter(function (x) {
      var co = false;
      (CT.nut || []).forEach(function (y) { if (y.ma === x.ma) co = true; });
      return !co;
    });

    var gio = Math.floor((Date.now() - new Date(CT.generatedAt).getTime()) / 36e5);

    var dan = '<div class="luoi-so">' +
      oSo("Hạ tầng thật tới bậc", "<b>" + bacTien + "/10</b>",
        "bậc cuối còn đo được bằng tiền đang nằm trên đó") +
      oSo("Có người đang xây tới bậc", "<b>" + bacXay + "/10</b>",
        "xa nhất còn kho mã có commit trong 30 ngày") +
      oSo("Nút chưa ai xây", "<b>" + trong.length + "/" + (S.THIEU || []).length + "</b>",
        "không tìm được kho mã nào đang làm việc đó") +
      oSo("Hỏi GitHub cách đây", "<b>" + gio + " giờ</b>",
        "bot chạy 4 lượt/ngày · không phải realtime") +
      "</div>" +
      /* Khoảng cách với lưới ô số ngay trên do `.khoi-than>.giaithich`
         lo, không vá bằng style dòng: chỗ này là chỗ DUY NHẤT một
         đoạn giải thích đứng sau nội dung khác trong cùng một khối,
         nên một con số vá tay ở đây là một con số không ai đối chiếu
         được với chỗ nào. */
      '<p class="giaithich">Khoảng cách giữa <b>bậc ' + bacTien +
      "</b> và <b>bậc " + bacXay + "</b> là phần việc đang dở: có người xây, chưa có " +
      "vốn nào đứng lên trên. Và đọc con số thứ hai cho đúng — <b>“có công trường” " +
      "không có nghĩa là “đã tới”</b>. Bậc " + bacXay + " còn động vì một kho toà án " +
      "phi tập trung vẫn có commit, chứ không phải vì nhà nước nào đã thành giao thức.</p>";

    /* ── từng bậc ── */
    var bac = (S.THANG || []).map(function (g) {
      var n = Number(g.so);
      var ds = nutCuaBac(n);
      var tien2 = DO_TIEN[g.so] ? DO_TIEN[g.so]() : null;

      var dh = "";
      if (tien2) {
        dh += '<div class="bac-do">' + tien2.map(function (p) {
          return '<span class="bac-o"><i>' + esc(p[0]) + "</i><b>" + esc(p[1]) + "</b></span>";
        }).join("") + "</div>";
      }
      if (ds.length) {
        dh += '<div class="bac-nut">' + ds.map(function (x) {
          var st = !x.n ? "trong" : x.n.soDangXay > 0 ? "xay" : "dung";
          var nhan = !x.n ? "chưa ai xây"
            : x.n.soDangXay > 0 ? x.n.soDangXay + "/" + x.n.soKho + " công trường động"
            : x.n.soKho + " kho, không cái nào động";
          return '<span class="bac-n" data-st="' + st + '">' + esc(x.t.ten) +
            "<i>" + nhan + "</i></span>";
        }).join("") + "</div>";
      }
      if (!dh) {
        dh = '<p class="bac-khong">Không có dấu hiệu nào đo được ở bậc này — ' +
          "chưa có tiền để đếm, cũng chưa có kho mã nào để trỏ tới.</p>";
      }

      var moc = n === bacTien ? "MÉP TIỀN" : n === bacXay ? "MÉP CÔNG TRƯỜNG" : "";
      return '<div class="bac"' + (moc ? ' data-day="1"' : "") + ">" +
        '<div class="bac-s">' + esc(g.so) + "</div><div>" +
        '<div class="bac-t">' + esc(g.ten) +
          (moc ? '<span class="bac-here" data-m="' + (n === bacTien ? "tien" : "xay") +
                 '">' + moc + "</span>" : "") +
          '<span class="bac-luan">' + mucLuan(g.muc) + " luận</span></div>" +
        dh + "</div></div>";
    }).join("");

    /* ── công trường ── */
    var ds = (CT.kho || []).slice().sort(function (a, b) {
      var x = (a.commit && a.commit.ngay) || a.day || "";
      var y = (b.commit && b.commit.ngay) || b.day || "";
      return y < x ? -1 : 1;
    });
    var ten = {};
    (S.THIEU || []).forEach(function (x) { ten[x.ma] = x.ten; });

    var ctHang = ds.map(function (k) {
      var tt = TRANG_KHO[k.trangThai] || { ten: "?", v: "giua" };
      var ng = (k.commit && k.commit.ngay) || k.day;
      var d = soNgay(ng);
      return '<div class="ct" data-v="' + tt.v + '">' +
        '<div class="ct-d"><a class="ct-t" href="https://github.com/' +
          esc(k.chu) + "/" + esc(k.ten) + '" target="_blank" rel="noopener">' +
          esc(k.chu) + "/<b>" + esc(k.ten) + "</b></a>" +
        '<span class="dot-nhan" data-v="' + tt.v + '">' + tt.ten + "</span></div>" +
        '<p class="ct-y">' + esc(k.y) + "</p>" +
        (k.commit && k.commit.thongDiep
          ? '<p class="ct-c"><span>lần cuối ' + esc(ngayVn(ng)) +
            (d != null ? " · " + d + " ngày trước" : "") + "</span>" +
            esc(k.commit.thongDiep) + "</p>"
          : '<p class="ct-c"><span>lần cuối ' + esc(ngayVn(ng)) + "</span></p>") +
        '<div class="ct-m"><span>nút: ' + esc(ten[k.nut] || k.nut) + "</span>" +
          (k.sao != null ? "<span>" + so(k.sao, 0) + " ★</span>" : "") +
          (k.ngonNgu ? "<span>" + esc(k.ngonNgu) + "</span>" : "") +
          (k.viecMo != null ? "<span>" + so(k.viecMo, 0) + " việc mở</span>" : "") +
        "</div></div>";
    }).join("");

    /* ── đề xuất ── */
    var dx = (CT.deXuat || []).map(function (x) {
      return '<div class="dx"><span class="dx-n">' + esc(ngayVn(x.ngay)) + "</span>" +
        '<span class="dx-k" data-k="' + esc(x.kho) + '">' + esc(x.kho) + "</span>" +
        '<span class="dx-t">' + esc(x.tieuDe) + "</span></div>";
    }).join("");

    /* ── nút trống ── */
    var tr = trong.map(function (x) {
      return '<div class="thieu" data-trong="1"><div class="thieu-t">' + esc(x.ten) +
        '<span class="dot-nhan" data-v="som">CHƯA AI XÂY</span></div>' +
        '<p class="thieu-y">' + esc(x.y) + "</p></div>";
    }).join("");

    return khoi("Thế giới đang xây tới đâu", null, dan,
      "Bốn con số này đọc từ <b>hai nguồn khác nhau</b>: tiền lấy từ DefiLlama, " +
      "còn “ai đang làm” lấy từ GitHub — số sao, ngày commit cuối và dòng commit " +
      "mới nhất của từng kho mã. <b>Không phải realtime.</b> Trang này là trang " +
      "tĩnh; gọi API lúc bạn mở thì mỗi người xem đốt hạn mức của chính họ. Bot " +
      "hỏi 4 lượt/ngày, và ô thứ tư luôn nói bản này cũ bao nhiêu giờ.") +

      khoi("Từng bậc đang có dấu hiệu gì", "10 bậc",
        '<div class="bac-l">' + bac + "</div>",
        "Cột phần trăm là <b>LUẬN</b> lấy từ tài liệu nguồn — giữ nguyên, không " +
        "đo được. Thứ bên dưới mỗi bậc mới là <b>ĐO ĐƯỢC</b>: ba bậc đầu đo bằng " +
        "tiền vì chúng đã thành hạ tầng thật; từ bậc 4 trở lên chưa có tiền để " +
        "đếm nên chỉ còn đo bằng công trường. Bậc nào không có cả hai thì nói " +
        "thẳng là không có, chứ không điền bằng số đoán.") +

      khoi("Công trường đang mở", CT.tong.soDangXay + "/" + CT.tong.soKho + " còn động",
        hoacTrong(ctHang,
          "<b>Lượt gần nhất không kho mã nào lấy được.</b> GitHub có thể chạm hạn " +
          "mức trong khi DefiLlama vẫn trả lời, nên phần tiền ở trên vẫn đúng. " +
          "Nhưng hai ô “có người đang xây tới bậc” và “nút chưa ai xây” thì " +
          "<i>đang đọc trên chính bảng rỗng này</i> — đừng đọc chúng như một kết luận."),
        "Mỗi kho là một chỗ nút thắt đó đang thật sự được xây. <b>Ngày commit " +
        "cuối là thước ở đây</b>, không phải số sao: một kho 2.000 sao mà tám " +
        "tháng không ai đụng vào thì nút đó đang nguội, còn một kho 81 sao có " +
        "commit hôm nay thì đang chạy. Bấm tên kho để sang thẳng GitHub.") +

      khoi("Kỹ sư vừa đề xuất gì", CT.deXuat.length + " dòng",
        '<div class="dx-l">' + hoacTrong(dx,
          "<b>Lượt gần nhất không đọc được dòng nào.</b> Hai kho " +
          "<code>ethereum/ERCs</code> và <code>ethereum/EIPs</code> không trả về " +
          "lịch sử thư mục chuẩn. Trống là <i>không hỏi được</i>, không phải " +
          "khoảng này không ai đề xuất gì.") + "</div>",
        "Đọc thẳng từ lịch sử thư mục chuẩn của <code>ethereum/ERCs</code> và " +
        "<code>ethereum/EIPs</code>. Đây là chỗ một chuẩn mới xuất hiện và một " +
        "chuẩn cũ đổi trạng thái — “Add ERC…” là vừa có đề xuất mới, “Move to " +
        "last call” là sắp chốt.") +

      /* Chỗ rỗng DUY NHẤT trong cung mang tin tốt: rỗng ở đây nghĩa là
         mọi nút thắt đều đã có kho mã trỏ tới. Nếu tô cùng khuôn xám
         với tám chỗ rỗng do thiếu dữ liệu thì một kết quả lành bị đọc
         thành một đường ống hỏng. Nhưng chỉ tốt khi sổ toa CÓ khai nút
         thắt — sổ trống thì rỗng ở đây chẳng nói lên điều gì cả. */
      khoi("Nút thắt chưa ai xây", trong.length + " nút",
        '<div class="thieu-l">' + hoacTrong(tr,
          (S.THIEU || []).length
            ? "<b>Không nút thắt nào bị bỏ trắng.</b> Cả " + (S.THIEU || []).length +
              " nút đều có ít nhất một kho mã trỏ tới. Đây là ô trống duy nhất " +
              "trong cung <i>mang tin tốt</i> — không phải chỗ dữ liệu bị hụt."
            : "<b>Sổ toa chưa khai nút thắt nào.</b> Không có danh sách nào để " +
              "đối chiếu với công trường, nên rỗng ở đây <i>chưa nói được điều " +
              "gì</i> — sửa <code>THIEU</code> trong <code>assets/js/toa.js</code>.",
          (S.THIEU || []).length > 0) + "</div>",
        "Đây là phát hiện chính của cả phòng, và nó lộ ra <b>vì bảng để trống chứ " +
        "không đi tìm cho đủ</b>: mọi nút CÓ công trường đều là nút kỹ thuật. " +
        "Mấy nút còn lại — pháp lý khớp với on-chain, thực thi ở thế giới vật " +
        "lý, ai được đặt hàm mục tiêu, cỗ máy tự thấy mình sắp mất kiểm soát — " +
        "không có kho mã nào để trỏ tới, vì chúng không phải bài toán giải được " +
        "bằng một kho mã.");
  }

  /* ═══════════════ NGĂN HỒ SƠ ═══════════════ */

  var hoso = document.getElementById("hoso"),
    scrim = document.getElementById("scrim"),
    hosoTen = document.getElementById("hosoTen"),
    hosoTren = document.getElementById("hosoTren"),
    hosoBody = document.getElementById("hosoBody");

  /* Nhớ chỗ vừa bấm để TRẢ TIÊU ĐIỂM khi đóng ngăn.
     Không có nó thì người dùng bàn phím đóng ngăn xong bị ném về đầu
     trang và phải Tab lại từ đầu qua 18 toa — mở một toa là mất chỗ
     đang đứng. Lấy từ checklist skill frontend-a11y: "modals restore
     focus on close". */
  var oCu = null;

  function dongHoso() {
    hoso.dataset.open = "0";
    scrim.dataset.open = "0";
    hoso.setAttribute("aria-hidden", "true");
    if (oCu && oCu.focus) { try { oCu.focus(); } catch (e) {} }
    oCu = null;
  }
  function moHoso(tren, ten, than) {
    oCu = document.activeElement;
    hosoTren.textContent = tren;
    hosoTen.textContent = ten;
    hosoBody.innerHTML = than;
    hoso.dataset.open = "1";
    scrim.dataset.open = "1";
    hoso.setAttribute("aria-hidden", "false");
    hosoBody.scrollTop = 0;
  }

  function dong(dt, dd) {
    return "<dt>" + esc(dt) + "</dt><dd>" + dd + "</dd>";
  }

  function hosoToa(ma) {
    var t = null;
    G.toa.forEach(function (x) { if (x.c.ma === ma) t = x; });
    if (!t) return;
    var c = t.c, s = t.s;
    var doDuoc = s.thuoc !== "khong-do-duoc" && s.tvl != null;

    var h = "";
    h += '<p style="margin:0 0 14px;color:var(--fg-2);font-size:13px">' + esc(c.lat) + "</p>";

    h += '<dl class="hs-d">' +
      dong("Thước đo", esc(TEN_THUOC[s.thuoc])) +
      dong("Giá trị", '<b class="mono">' + (doDuoc ? tien(s.tvl) : "— không đo được bằng thước này") + "</b>") +
      dong("Giao thức", '<span class="mono">' + so(s.soGiaoThuc, 0) + "</span>") +
      (s.tapTrung != null
        ? dong("Tập trung", '<span class="mono">' + pt(s.tapTrung, 0) + "</span> nằm ở " +
            esc(s.tapTrungTen || "cái lớn nhất") + " — tính trên cùng thước với con số trên")
        : "") +
      dong("Hạng trụ lại", '<span class="mono">' + c.songSot + "/18</span> " +
        '<span class="luan" style="margin-left:2px">LUẬN</span>') +
      "</dl>";

    h += '<h3 style="font-size:13px;margin:16px 0 6px">Trách nhiệm</h3>' +
      '<p style="margin:0;font-size:12.5px;line-height:1.65">' + esc(c.lam) + "</p>";

    h += '<dl class="hs-d" style="margin-top:12px">' +
      dong("Cần gì để sống", esc(c.vao)) +
      dong("Cung cấp gì", esc(c.ra)) +
      dong("Dựa vào", esc(c.dua.join(" · "))) +
      dong("Ai gãy theo", esc(c.nuoi.join(" · "))) +
      "</dl>";

    h += '<h3 style="font-size:13px;margin:16px 0 6px">Vì sao xếp ở hạng này</h3>' +
      '<p style="margin:0;font-size:12.5px;line-height:1.65;color:var(--fg-2)">' + esc(c.y) + "</p>";

    /* Lớp tri thức nền: khuôn HTML sinh ra từ knowledge-os/sinh.mjs, một
       nguồn cho mọi cung. Toa chưa ánh xạ thì trả "" chứ không vẽ khung rỗng. */
    h += (TT && TT.ve ? TT.ve(ma) : "");

    h += '<h3 style="font-size:13px;margin:16px 0 6px">Vài cái tên tiêu biểu</h3>' +
      '<div class="hs-ng">' + c.nguoi.map(function (n) {
        return "<span>" + esc(n) + "</span>";
      }).join("") + "</div>" +
      '<p style="margin:6px 0 0;font-size:11.5px;color:var(--fg-3);line-height:1.55">' +
      "Danh sách gợi ý, không phải danh sách đầy đủ và không phải khuyến nghị. " +
      "Một tài sản có thể mang trách nhiệm ở nhiều toa cùng lúc.</p>";

    /* Cột và tiêu đề đi theo THƯỚC của toa: toa nền xếp theo chuỗi,
       toa tiền ổn định xếp theo từng stablecoin. Cột "đứng trên mấy
       chuỗi" chỉ có nghĩa với giao thức, nên hai toa kia không có. */
    if (s.top && s.top.length) {
      var nhan = s.topNhan || "Giao thức";
      var coChuoi = nhan === "Giao thức";
      h += '<h3 style="font-size:13px;margin:16px 0 6px">Lớn nhất trong toa</h3>' +
        bang(coChuoi ? [{ t: nhan }, { t: "TVL" }, { t: "Chuỗi" }]
                     : [{ t: nhan }, { t: "Giá trị" }],
          s.top.map(function (p) {
            return "<tr><td>" + esc(p.ten) + '</td><td class="mono">' + tien(p.tvl) +
              (coChuoi ? '</td><td class="mono">' + (p.chuoi == null ? "—" : p.chuoi) : "") +
              "</td></tr>";
          }).join(""));
    }

    if (s.catGoc && s.catGoc.length) {
      h += '<h3 style="font-size:13px;margin:16px 0 6px">Cộng từ những nhóm nguồn nào</h3>' +
        '<div class="hs-ng">' + s.catGoc.map(function (x) {
          return "<span>" + esc(x) + "</span>";
        }).join("") + "</div>" +
        '<p style="margin:6px 0 0;font-size:11.5px;color:var(--fg-3);line-height:1.55">' +
        "Đây là cách truy ngược con số ở trên. Không đồng ý với cách xếp thì vẫn " +
        "thấy được thành phần mà tự xếp lại.</p>";
    }

    var cua = (c.cung || []).filter(function (k) { return S.CUNG[k]; });
    if (cua.length) {
      h += '<h3 style="font-size:13px;margin:16px 0 6px">Đọc tiếp ở cung khác</h3>' +
        '<div class="cua-l">' + cua.map(function (k) {
          return '<a class="cua" href="' + esc(S.CUNG[k].duong) + '">' +
            '<div class="cua-t">' + esc(S.CUNG[k].ten) + IC_DI + "</div></a>";
        }).join("") + "</div>";
    }

    moHoso("Toa " + c.so, c.ten, h);
  }

  function hosoOracle(ten) {
    var o = null;
    D.oracle.forEach(function (x) { if (x.ten === ten) o = x; });
    if (!o) return;
    var lui = o.tvl - o.tvlRieng;
    var h = '<dl class="hs-d">' +
      dong("Vốn đang dựa vào", '<b class="mono">' + tien(o.tvl) + "</b>") +
      dong("Số giao thức", '<span class="mono">' + so(o.soGiaoThuc, 0) + "</span>") +
      dong("Không có đường lui", '<span class="mono">' + tien(o.tvlRieng) + "</span> · " +
        o.soRieng + " giao thức") +
      dong("Còn nguồn khác", '<span class="mono">' + tien(lui) + "</span>") +
      "</dl>" +
      '<p style="margin:0 0 14px;font-size:12.5px;line-height:1.65;color:var(--fg-2)">' +
      "“Không có đường lui” nghĩa là giao thức đó khai đúng một nguồn giá và không " +
      "khai nguồn nào khác. Không phải mọi giao thức đều khai đầy đủ, nên con số " +
      "này là <b>sàn dưới</b> chứ không phải con số chính xác — thực tế có thể cao hơn.</p>";

    if (o.top && o.top.length) {
      h += '<h3 style="font-size:13px;margin:0 0 6px">Giao thức lớn nhất đang dựa vào</h3>' +
        bang([{ t: "Giao thức" }, { t: "TVL" }, { t: "Đường lui" }],
          o.top.map(function (p) {
            return "<tr><td>" + esc(p.ten) + '</td><td class="mono">' + tien(p.tvl) +
              "</td><td>" + (p.rieng
                ? '<span style="color:var(--xuong)">không có</span>'
                : '<span style="color:var(--len)">có nguồn khác</span>') + "</td></tr>";
          }).join(""));
    }
    moHoso("Khớp nối", o.ten, h);
  }

  /* ═══════════════ CÁC PHÒNG ═══════════════ */

  var IC = {
    tau: '<path d="M4 17V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10"/><path d="M2 20h20"/><path d="M8 5V3h8v2"/><circle cx="8" cy="17" r="1.4"/><circle cx="16" cy="17" r="1.4"/>',
    sk: '<path d="M9 12a3 3 0 0 1 3-3h1a3.5 3.5 0 1 0 0-7h-1"/><path d="M15 12a3 3 0 0 1-3 3h-1a3.5 3.5 0 1 0 0 7h1"/>',
    dot: '<path d="M12 3c1.5 3.5 4.5 5 4.5 9a4.5 4.5 0 0 1-9 0c0-4 3-5.5 4.5-9Z"/>',
    cua: '<path d="M14 3h5a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-5"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/>',
    tg: '<path d="M4 20h4V10H4zM10 20h4V4h-4zM16 20h4v-7h-4z"/>',
    ct: '<path d="M2 21h20"/><path d="M4 21V10l7-4 7 4v11"/><path d="M9 21v-6h4v6"/><path d="M11 6V3l6 2.2"/>'
  };

  var PHONG = [
    { ma: "doan-tau", ten: "Đoàn Tàu", ic: IC.tau, ve: veDoanTau,
      dem: function () { return G.toa.length + " toa"; } },
    { ma: "khop-noi", ten: "Khớp Nối", ic: IC.sk, ve: veKhopNoi,
      dem: function () { return pt(D.duongLui.tyLe, 0); } },
    { ma: "thu-tu", ten: "Thứ Tự Bị Đốt", ic: IC.dot, ve: veThuTu,
      dem: function () { return "luận"; } },
    { ma: "cua-noi", ten: "Cửa Nối", ic: IC.cua, ve: veCuaNoi,
      dem: function () { return demCung() + " cung"; } },
    { ma: "cong-truong", ten: "Công Trường", ic: IC.ct, ve: veCongTruong,
      dem: function () {
        return CT ? CT.tong.soDangXay + "/" + CT.tong.soKho : "—";
      } },
    { ma: "thang", ten: "Thang Tiến Hoá", ic: IC.tg, ve: veThang,
      dem: function () { return "luận"; } }
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
        '<span class="bn">' + p.dem() + "</span>";
      host.appendChild(a);
    });
  }

  var loa = document.getElementById("loa"),
    than = document.getElementById("than"),
    tieu = document.getElementById("tieu"),
    ben = document.getElementById("ben");

  function ve() {
    var ma = (location.hash || "").replace(/^#\/?/, "") || "doan-tau";
    var p = null, i;
    for (i = 0; i < PHONG.length; i++) if (PHONG[i].ma === ma) p = PHONG[i];
    if (!p) p = PHONG[0];

    tieu.textContent = p.ten;
    document.title = "Thái Bộc Tự · " + p.ten;
    /* Đổi phòng là thay TOÀN BỘ thân trang mà địa chỉ chỉ đổi phần
       sau dấu thăng — trình đọc màn hình không có gì báo cho người
       dùng biết vừa có chuyện gì. Một dòng thông báo lịch sự là đủ;
       aria-live trên cả #than thì mỗi lần vẽ lại đọc hết vài nghìn
       chữ, tệ hơn hẳn không có. */
    if (loa) loa.textContent = "Đã mở phòng " + p.ten + ".";
    than.innerHTML = p.ve();
    than.style.animation = "none";
    void than.offsetWidth;
    than.style.animation = "";

    PHONG.forEach(function (x) {
      var el = document.getElementById("muc-" + x.ma);
      if (el) {
        if (x.ma === p.ma) el.setAttribute("aria-current", "page");
        else el.removeAttribute("aria-current");
      }
    });

    /* Thanh mọc ra ở khung hình sau, để mắt thấy nó CHẠY tới giá
       trị chứ không phải đã nằm sẵn ở đó. */
    var bars = than.querySelectorAll("i[data-rong]");
    if (bars.length) {
      requestAnimationFrame(function () {
        Array.prototype.forEach.call(bars, function (b) {
          /* scaleX chứ không phải width. Đặt width ở đây thì trình
             duyệt tính lại bố cục mỗi khung hình của mọi thanh cùng
             lúc — với 18 toa cộng 14 khớp nối là hàng chục lần dựng
             lại lưới. Luật lấy từ skill motion-foundations. */
          b.style.transform = "scaleX(" +
            (Math.max(0, Math.min(100, parseFloat(b.getAttribute("data-rong")) || 0)) / 100) + ")";
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
        "<code>assets/js/v/doan-tau.js</code> chưa được sinh lần nào. " +
        "Chạy <code>node scripts/build-thaiboc.mjs</code> ở gốc repo, hoặc đợi " +
        "lượt GitHub Actions kế tiếp.</p>";
      return;
    }
    G = ghep();

    var ngay = document.getElementById("ngay");
    if (ngay) ngay.textContent = "cập nhật " + D.date;
    var song = document.getElementById("song");
    if (song) song.hidden = false;
    var giaTop = document.getElementById("giaTop");
    if (giaTop) {
      giaTop.innerHTML = "<span>giao thức</span> <b>" + so(D.tong.soGiaoThuc, 0) + "</b>" +
        "<span>chuỗi</span> <b>" + so(D.tong.soChuoi, 0) + "</b>";
    }

    /* Số liệu cũ thì nói thẳng ở đầu trang. Bot chạy 4 lượt/ngày,
       nên quá 1 ngày nghĩa là bốn lượt liên tiếp không ghi được gì —
       lúc đó mọi con số bên dưới vẫn hiện ra rất tự tin. */
    var gio = (Date.now() - new Date(D.generatedAt).getTime()) / 36e5;
    var cb = document.getElementById("canhBao");
    if (cb && isFinite(gio) && gio > 24) {
      cb.hidden = false;
      cb.innerHTML = "<b>Số liệu đã " + Math.floor(gio / 24) + " ngày chưa cập nhật.</b> " +
        "Đường ống chạy 4 lượt/ngày, nên quá một ngày nghĩa là bốn lượt liên tiếp " +
        "không ghi được gì. Mọi con số bên dưới vẫn đúng với thời điểm " +
        esc(D.date) + ", không đúng với hôm nay.";
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

  var nut = document.getElementById("benMoNut");
  if (nut) nut.addEventListener("click", function () {
    ben.dataset.mo = ben.dataset.mo === "1" ? "0" : "1";
  });

  /* Uỷ quyền sự kiện ở cấp document: thân trang bị vẽ lại mỗi lần
     đổi phòng, nên gắn thẳng vào từng nút là gắn lại sau mỗi lần vẽ
     — và quên một chỗ thì nó chết im lặng. */
  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    var el = e.target.closest("[data-toa]");
    if (el) { hosoToa(el.getAttribute("data-toa")); return; }
    el = e.target.closest("[data-oracle]");
    if (el) { hosoOracle(el.getAttribute("data-oracle")); return; }
  });

  document.getElementById("hosoDong").addEventListener("click", dongHoso);
  scrim.addEventListener("click", dongHoso);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") dongHoso();
  });

  chay();
})();
