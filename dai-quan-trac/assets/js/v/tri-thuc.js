/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.
   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:
       node knowledge-os/sinh.mjs dai-quan-trac

   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,
   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).

   SINH TAY, PHẢI COMMIT — không workflow nào chạy lệnh này.
   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng
   CACHE_VERSION khi file này đổi. */
window.TRI_THUC = {"sinhLuc":"2026-08-25T17:11:47.926Z","goi":"knowledge-os","cung":"dai-quan-trac","vai":"Địa chính trị, tiền tệ và dòng vốn","y":"Phân loại tin theo chuỗi cung tiền → lãi suất → tỷ giá → dòng vốn → tài sản.","phong":[{"ma":"flow","ten":"Dòng chảy","y":"Vốn chảy đi đâu là câu trả lời gộp cho mọi chính sách tiền tệ. Chặn dòng chảy là chính sách; đo dòng chảy là đọc kết quả của chính sách.","khaiNiem":["capital_mobility","capital_controls","price_signal"]},{"ma":"chain","ten":"Mạch truyền dẫn","y":"Cung tiền → lãi suất → tỷ giá → dòng vốn → tài sản. Mỗi mắt xích là một chỗ tín hiệu có thể bị bẻ, và bẻ ở đâu thì méo lan từ đó về sau.","khaiNiem":["central_bank","interest_rate","fiat_money","capital_mobility"]},{"ma":"gauges","ten":"Bảng cảnh báo sớm","y":"Đồng hồ đo áp lực lên đồng tiền. Chúng đọc được vì giá vẫn còn nói thật ở đâu đó — mất chỗ ấy là mất luôn cảnh báo.","khaiNiem":["price_signal","monetary_debasement"]},{"ma":"levels","ten":"Cấp độ áp lực","y":"Từ áp lực tới khủng hoảng là một thang, không phải một công tắc. Sách kể thang này ở thế kỷ 20; các nấc vẫn nhận ra được.","khaiNiem":["currency_war","monetary_nationalism","capital_controls"]},{"ma":"banco","ten":"Bàn cờ Mỹ–Trung","y":"Hai hệ thanh toán cạnh tranh nhau là cạnh tranh tiền tệ ở quy mô nhà nước — chuyện sách kể bằng vàng và bảng Anh.","khaiNiem":["monetary_competition","currency_war","international_settlement"]}],"khaiNiem":{"fiat_money":{"en":"Fiat money","vi":"Tiền pháp định","loai":"monetary_regime","nghia":"Tiền do nhà nước phát hành và điều hành bằng luật/chính sách, có thể không còn quy đổi sang hàng hóa nền.","goc":"sach","chuong":[4],"trang":[50,51]},"central_bank":{"en":"Central bank","vi":"Ngân hàng trung ương","loai":"institution","nghia":"Cơ quan điều hành tiền tệ/lãi suất; tác giả phê phán khả năng can thiệp cung tiền và giá vốn.","goc":"sach","chuong":[4,5,6],"trang":[50,90,121]},"monetary_nationalism":{"en":"Monetary nationalism","vi":"Chủ nghĩa tiền tệ quốc gia","loai":"monetary_regime","nghia":"Mỗi quốc gia điều hành đồng tiền riêng và tỷ giá trở thành biến chính sách.","goc":"sach","chuong":[4,7],"trang":[56,61,135]},"currency_war":{"en":"Currency war","vi":"Chiến tranh tiền tệ","loai":"macro","nghia":"Cạnh tranh phá giá/tỷ giá giữa quốc gia để đạt mục tiêu thương mại; đây là cách diễn giải của tác giả.","goc":"tacGia","chuong":[7],"trang":[139,140]},"capital_controls":{"en":"Capital controls","vi":"Kiểm soát dòng vốn","loai":"policy","nghia":"Hạn chế khả năng chuyển/giữ giá trị giữa tài sản, ngân hàng hoặc biên giới.","goc":"sach","chuong":[4,7],"trang":[75,136]},"capital_mobility":{"en":"Capital mobility","vi":"Khả năng luân chuyển vốn","loai":"market_property","nghia":"Mức vốn có thể di chuyển qua biên giới/tài sản; liên quan bộ ba bất khả thi.","goc":"sach","chuong":[7],"trang":[136,137]},"monetary_debasement":{"en":"Monetary debasement","vi":"Pha loãng tiền tệ","loai":"mechanism","nghia":"Giảm sức mua đơn vị tiền do tăng nguồn cung hoặc giảm chất lượng tài sản bảo chứng.","goc":"sach","chuong":[3,4,5],"trang":[28,68,89]},"price_signal":{"en":"Price signal","vi":"Tín hiệu giá","loai":"information","nghia":"Giá cô đọng thông tin phân tán về khan hiếm, nhu cầu và chi phí cơ hội.","goc":"sach","chuong":[6],"trang":[115,117,120]},"interest_rate":{"en":"Interest rate","vi":"Lãi suất","loai":"price","nghia":"Giá của vốn vay; trong sách nó nối tiết kiệm, nhu cầu vay và ưu tiên thời gian.","goc":"sach","chuong":[5,6],"trang":[90,121]},"monetary_competition":{"en":"Monetary competition","vi":"Cạnh tranh tiền tệ","loai":"mechanism","nghia":"Các phương tiện tiền tệ cạnh tranh về độ cứng, tính thanh khoản, mức chấp nhận và công nghệ.","goc":"sach","chuong":[1,2,3],"trang":[14,15,24]},"international_settlement":{"en":"International settlement","vi":"Quyết toán quốc tế","loai":"payment_function","nghia":"Chuyển giá trị cuối cùng giữa các bên ở khu vực pháp lý khác nhau.","goc":"sach","chuong":[9],"trang":[182,183,188]},"onchain_credit_market":{"en":"On-chain credit market","vi":"Thị trường tín dụng trên chuỗi","loai":"market","nghia":"Cho vay có thế chấp vượt mức chạy bằng hợp đồng, lãi suất do cung cầu trong pool quyết định chứ không do một ngân hàng đặt.","goc":"repo","nguon":"ho-bo phòng loi-suat · thai-boc-tu toa t06"},"mev_extraction":{"en":"MEV extraction","vi":"Rút giá trị theo thứ tự khối","loai":"network_mechanism","nghia":"Khoản thu được nhờ quyền xếp thứ tự giao dịch trong một khối; nó biến quyền dựng khối thành một tài sản có giá.","goc":"repo","nguon":"thai-boc-tu toa t02 (nhóm nguồn Block Builders · MEV)"},"perpetual_funding":{"en":"Perpetual funding rate","vi":"Phí funding hợp đồng vĩnh cửu","loai":"price","nghia":"Khoản trả định kỳ giữa hai phía long và short để kéo giá hợp đồng vĩnh cửu về giá giao ngay — lãi suất của một vị thế đòn bẩy, tính theo giờ.","goc":"repo","nguon":"thi-bac-ty-runtime/bac/ · thi-bac-ty/assets/js/v/cang-phi.js"}},"quanHe":[{"tu":"fiat_money","loai":"managed_by","den":"central_bank","vi":"Ngân hàng trung ương là cơ quan chính sách tiền tệ chủ chốt.","goc":"sach","tin":"high","chuong":[4,6],"trang":[50,121]},{"tu":"central_bank","loai":"influences","den":"interest_rate","vi":"Tác giả tập trung vào khả năng ngân hàng trung ương tác động giá vốn.","goc":"sach","tin":"high","chuong":[5,6],"trang":[90,121]},{"tu":"monetary_nationalism","loai":"creates","den":"currency_war","vi":"Tác giả liên hệ tiền tệ quốc gia và cạnh tranh phá giá.","goc":"sach","tin":"medium","chuong":[7],"trang":[139,140]},{"tu":"capital_controls","loai":"reduces","den":"capital_mobility","vi":"Kiểm soát dòng vốn hạn chế dịch chuyển vốn xuyên biên giới.","goc":"sach","tin":"high","chuong":[7],"trang":[136,137]}],"lop2026":[{"tu":"onchain_credit_market","loai":"supports","den":"interest_rate","vi":"Lãi suất pool là giá của thời gian được niêm yết công khai và cập nhật liên tục.","goc":"repo","tin":"high","nguon":"ho-bo phòng loi-suat"},{"tu":"mev_extraction","loai":"extends","den":"price_signal","vi":"Phí ưu tiên là một giá thật cho một thứ khan hiếm thật — vị trí trong khối.","goc":"repo","tin":"low","nguon":"thai-boc-tu toa t02"},{"tu":"perpetual_funding","loai":"extends","den":"interest_rate","vi":"Funding là lãi suất của một vị thế đòn bẩy, kết toán theo mốc chứ không chảy liên tục.","goc":"repo","tin":"high","nguon":"thi-bac-ty phòng co-hoi · thi-bac-ty-runtime/bac/"}],"vaiVon":[],"nguon":{"sach":{"ten":"Tiêu chuẩn Bitcoin (The Bitcoin Standard)","tacGia":"Saifedean Ammous","nam":2018,"canhBao":"Tác giả đứng rõ trong truyền thống Kinh tế học Áo và có lập trường Bitcoin-maximalist; phải tách author_claim khỏi dữ kiện."},"ranhGioi":"Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."}};

(function () {
  "use strict";
  var T = window.TRI_THUC;
  if (!T) return;

  var TEN = { sach: "sách", tacGia: "tác giả", phanTich: "phân tích", repo: "repo", web: "web" };
  var GIAI = {
    sach: "Tác giả mô tả — tra lại được bằng chương/trang",
    tacGia: "Lập trường riêng của tác giả, không phải sự thật đo được",
    phanTich: "SUNSWaGz suy ra — sách không nói gì về chuyện này",
    repo: "Đo được từ repo/runtime này, năm 2026",
    web: "Nguồn ngoài"
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function chip(g) {
    return '<i class="tt-g" data-g="' + esc(g) + '" title="' + esc(GIAI[g] || "") + '">' +
      esc(TEN[g] || g) + "</i>";
  }
  function viTri(k) {
    if (!k.chuong || !k.chuong.length) return k.nguon || "";
    return "ch." + k.chuong.join(",") + (k.trang && k.trang.length ? " tr." + k.trang.join(",") : "");
  }
  function timPhong(ma) {
    var ds = T.phong || [], i;
    for (i = 0; i < ds.length; i++) if (ds[i].ma === ma) return ds[i];
    return null;
  }

  /* Trả về chuỗi HTML cho một phòng, hoặc "" nếu phòng chưa ánh xạ.
     Chưa ánh xạ thì KHÔNG vẽ khung rỗng: một khung có tiêu đề mà
     không có nội dung đọc ra là "chỗ này hỏng", chứ không phải
     "chỗ này chưa làm". */
  function ve(ma) {
    var p = timPhong(ma);
    if (!p) return "";

    var the = "", i, k, vt;
    for (i = 0; i < p.khaiNiem.length; i++) {
      k = T.khaiNiem[p.khaiNiem[i]];
      if (!k) continue;
      vt = viTri(k);
      the += '<div class="tt-k"><div class="tt-kd"><b>' + esc(k.vi) + "</b>" + chip(k.goc) +
        (vt ? '<span class="tt-vt">' + esc(vt) + "</span>" : "") + "</div><p>" + esc(k.nghia) + "</p></div>";
    }

    /* Lớp 2018→2026 vẽ RIÊNG dưới một tiêu đề riêng. Trộn nó vào
       lưới trên là đúng cái nhầm mà cả lớp này dựng ra để chặn. */
    var noi = "", ds = T.lop2026 || [], r, tu, den;
    for (i = 0; i < ds.length; i++) {
      r = ds[i];
      if (p.khaiNiem.indexOf(r.den) === -1) continue;
      tu = T.khaiNiem[r.tu]; den = T.khaiNiem[r.den];
      noi += "<p><b>" + esc(tu ? tu.vi : r.tu) + "</b>" + chip(r.goc) +
        '<span class="tt-loai">' + esc(r.loai) + "</span><b>" + esc(den ? den.vi : r.den) + "</b>" +
        '<span class="tt-tin">tin ' + esc(r.tin) + "</span>" +
        '<span class="tt-vi">' + esc(r.vi) + "</span></p>";
    }

    return '<section class="tt"><h3 class="tt-d">Vấn đề kinh tế gốc' +
      '<span class="tt-n">' + p.khaiNiem.length + " khái niệm</span></h3>" +
      '<p class="tt-y">' + esc(p.y) + "</p>" +
      (the ? '<div class="tt-luoi">' + the + "</div>" : "") +
      (noi ? '<div class="tt-26"><h4>2018 → 2026</h4>' + noi + "</div>" : "") +
      '<p class="tt-chan">Nền: «' + esc(T.nguon.sach.ten) + "» (" + esc(T.nguon.sach.tacGia) + ", " +
      esc(T.nguon.sach.nam) + "). Ánh xạ khái niệm sang phòng là <b>phân tích</b> của SUNSWaGz — " +
      "sách không nói gì về repo này. Sinh từ <code>knowledge-os/</code>.</p></section>";
  }

  /* Nối vào CUỐI thẻ chứa nội dung phòng. Dùng cho cung vẽ lại cả
     thân theo tuyến (`than.innerHTML = ...`).

     appendChild chứ KHÔNG `host.innerHTML += ...`: cộng chuỗi là
     phân tích lại toàn bộ cây con, và mọi listener đã gắn vào thẻ
     con bên trong đều rụng — hỏng im lặng, không lỗi nào báo, chỉ
     là bấm vào không ăn nữa. */
  function them(host, ma) {
    var s = ve(ma);
    if (!s || !host) return false;
    /* Gỡ khối cũ trước khi nối khối mới. Cung nào vẽ lại CÙNG một
       tuyến hai lần — điều hướng sâu, mở ngăn kéo, bấm lại đúng mục
       đang đứng — sẽ gọi lại chỗ này, và hai khối chồng nhau trông
       hệt như một trang dài chứ không giống lỗi. */
    var cu = host.querySelector ? host.querySelector(".tt-hop") : null;
    if (cu && cu.remove) cu.remove();
    var w = document.createElement("div");
    w.className = "tt-hop";
    w.innerHTML = s;
    host.appendChild(w);
    return true;
  }

  /* Chèn vào ngay sau <h2> của một thẻ đã có sẵn trong index.html.
     Dùng cho cung dựng trang tĩnh chứ không vẽ lại theo tuyến. */
  function gan(ma, muc) {
    var s = ve(ma);
    if (!s || !muc) return false;
    var w = document.createElement("div");
    w.className = "tt-hop";
    w.innerHTML = s;
    var h = muc.querySelector ? muc.querySelector("h2") : null;
    muc.insertBefore(w, h && h.nextSibling ? h.nextSibling : null);
    return true;
  }

  /* Một dòng nói lát cắt tri thức đến từ đâu, để nối vào chân trang.
     Gọi SAU khi cung đã vẽ xong chân trang của nó: phần lớn cung GÁN
     textContent cho thẻ đó, nên nối trước là bị xoá sạch mà không có
     lỗi nào báo. */
  function chan() {
    return " Lớp giải nghĩa: knowledge-os, nền là «" + T.nguon.sach.ten + "» (" +
      T.nguon.sach.tacGia + ", " + T.nguon.sach.nam +
      "). Nhãn nguồn trên từng dòng: sách · tác giả · phân tích · repo.";
  }

  T.ve = ve;
  T.them = them;
  T.gan = gan;
  T.chan = chan;
  T.co = function (ma) { return !!timPhong(ma); };
})();
