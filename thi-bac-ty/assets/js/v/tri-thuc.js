/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.
   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:
       node knowledge-os/sinh.mjs thi-bac-ty

   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,
   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).

   BOT GHI mỗi 24 giờ (node `tri-thuc`) — ĐỪNG SỬA TAY file này,
   sửa dữ liệu nguồn rồi sinh lại. Sửa thẳng vào đây thì đúng cho
   tới lượt bot kế tiếp, rồi biến mất không dấu vết.
   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng
   CACHE_VERSION khi file này đổi. */
window.TRI_THUC = {"sinhLuc":"2026-08-31T14:40:42.270Z","goi":"knowledge-os","cung":"thi-bac-ty","vai":"Funding/basis giữa các sàn perpetual","y":"Funding được diễn giải như giá cân bằng vị thế/đòn bẩy và tín hiệu nơi vốn được trả tiền.","phong":[{"ma":"trung-uong","ten":"Chín ty dưới một Thị Bạc Ty","y":"Chín ty là chín cách vốn kiếm ra tiền, nhưng vốn thì chỉ có một túi — nên chỗ này không đo từng ty, nó đo VIỆC PHÂN VỐN giữa chín ty. Một ty lãi cao mà nuốt hết thanh khoản là làm nghèo tám ty còn lại, và chỉ một phép tính chung mới thấy được điều đó.","khaiNiem":["capital_market","economic_calculation","counterparty_risk","salability"]},{"ma":"co-hoi","ten":"Cơ hội","y":"Funding là lãi suất của một vị thế đòn bẩy, tính theo giờ. Bảng này là thị trường vốn ngắn hạn nhất trong nghề, và NET là giá sau khi trừ phí.","khaiNiem":["interest_rate","capital_market","price_signal"]},{"ma":"vi-sao","ten":"Vì sao bị chặn","y":"Một cơ hội bị chặn vì phép tính không ra, chứ không vì thiếu can đảm. Nói rõ chặn ở đâu là giữ cho phép tính còn kiểm được.","khaiNiem":["economic_calculation","counterparty_risk"]},{"ma":"bao-gia","ten":"Báo giá bốn cảng","y":"Bốn cảng báo bốn giá cho cùng một rủi ro. Chênh lệch đó chính là tín hiệu, và nó chỉ đọc được sau khi chuẩn hoá chu kỳ.","khaiNiem":["price_signal","salability"]},{"ma":"cang","ten":"Sức khoẻ cảng","y":"Giữ vị thế hai chân ở hai sàn là tin hai bên thứ ba cùng lúc. Cảng ốm thì edge tính đúng vẫn mất tiền.","khaiNiem":["counterparty_risk","trusted_third_party"]},{"ma":"hoc","ten":"Hai phép tính","y":"Ưu tiên thời gian nói vì sao có lãi suất; chuẩn hoá và đếm mốc là cách đo nó cho đúng ở đây.","khaiNiem":["time_preference","interest_rate","economic_calculation"]}],"khaiNiem":{"interest_rate":{"en":"Interest rate","vi":"Lãi suất","loai":"price","nghia":"Giá của vốn vay; trong sách nó nối tiết kiệm, nhu cầu vay và ưu tiên thời gian.","goc":"sach","chuong":[5,6],"trang":[90,121]},"capital_market":{"en":"Capital market","vi":"Thị trường vốn","loai":"market","nghia":"Nơi vốn tiết kiệm được cho vay/phân bổ cho các quá trình sản xuất và đầu tư.","goc":"sach","chuong":[6],"trang":[121,123]},"price_signal":{"en":"Price signal","vi":"Tín hiệu giá","loai":"information","nghia":"Giá cô đọng thông tin phân tán về khan hiếm, nhu cầu và chi phí cơ hội.","goc":"sach","chuong":[6],"trang":[115,117,120]},"time_preference":{"en":"Time preference","vi":"Ưu tiên thời gian","loai":"behavior","nghia":"Mức một người coi trọng lợi ích hiện tại so với tương lai; ưu tiên thấp hơn cho phép trì hoãn tiêu dùng và tích lũy vốn.","goc":"sach","chuong":[1,5,6],"trang":[15,83,84,121]},"counterparty_risk":{"en":"Counterparty risk","vi":"Rủi ro đối tác","loai":"risk","nghia":"Rủi ro bên còn lại hoặc trung gian không thực hiện nghĩa vụ.","goc":"sach","chuong":[9],"trang":[183,188]},"economic_calculation":{"en":"Economic calculation","vi":"Tính toán kinh tế","loai":"mechanism","nghia":"Dùng giá và đơn vị tính toán để so sánh chi phí, doanh thu, lợi nhuận và lựa chọn phương án.","goc":"sach","chuong":[1,6,7],"trang":[16,114,118,140]},"salability":{"en":"Salability","vi":"Tính thanh khoản/khả năng bán đổi","loai":"money_property","nghia":"Mức dễ trao đổi với tổn thất thấp, xét theo quy mô, không gian và thời gian.","goc":"sach","chuong":[1],"trang":[12,13]},"trusted_third_party":{"en":"Trusted third party","vi":"Bên thứ ba đáng tin cậy","loai":"architecture","nghia":"Trung gian mà hai bên phải tin để ghi sổ, xử lý hoặc quyết toán giao dịch.","goc":"sach","chuong":[8,10],"trang":[144,229,231]},"stablecoin_settlement":{"en":"Stablecoin settlement","vi":"Quyết toán bằng stablecoin","loai":"payment_function","nghia":"Khối lượng chuyển giá trị chạy bằng token neo đô la trên chuỗi công khai, thay vì bằng đồng tiền gốc của chuỗi.","goc":"repo","nguon":"ho-bo/assets/js/v/dong-tien.js · thai-boc-tu toa t04"},"onchain_credit_market":{"en":"On-chain credit market","vi":"Thị trường tín dụng trên chuỗi","loai":"market","nghia":"Cho vay có thế chấp vượt mức chạy bằng hợp đồng, lãi suất do cung cầu trong pool quyết định chứ không do một ngân hàng đặt.","goc":"repo","nguon":"ho-bo phòng loi-suat · thai-boc-tu toa t06"},"rwa_tokenization":{"en":"RWA tokenization","vi":"Token hoá tài sản thế giới thật","loai":"asset_role","nghia":"Trái phiếu kho bạc, tín dụng tư nhân và hàng hoá được phát hành dạng token, mang lợi suất ngoài chuỗi vào trong chuỗi.","goc":"repo","nguon":"thai-boc-tu toa t09"},"mev_extraction":{"en":"MEV extraction","vi":"Rút giá trị theo thứ tự khối","loai":"network_mechanism","nghia":"Khoản thu được nhờ quyền xếp thứ tự giao dịch trong một khối; nó biến quyền dựng khối thành một tài sản có giá.","goc":"repo","nguon":"thai-boc-tu toa t02 (nhóm nguồn Block Builders · MEV)"},"perpetual_funding":{"en":"Perpetual funding rate","vi":"Phí funding hợp đồng vĩnh cửu","loai":"price","nghia":"Khoản trả định kỳ giữa hai phía long và short để kéo giá hợp đồng vĩnh cửu về giá giao ngay — lãi suất của một vị thế đòn bẩy, tính theo giờ.","goc":"repo","nguon":"thi-bac-ty-runtime/bac/ · thi-bac-ty/assets/js/v/cang-phi.js"},"venue_fragmented_depth":{"en":"Venue-fragmented depth","vi":"Độ sâu phân mảnh theo cảng","loai":"market_structure","nghia":"Cùng một tài sản có độ sâu khác nhau ở từng cảng và từng cỡ vốn, nên câu «rót vào bao nhiêu mà không đội giá» chỉ trả lời được cho một cặp (cảng, cỡ) chứ không trả lời được cho chính tài sản đó.","goc":"repo","nguon":"thi-bac-ty-runtime/bac/suc_chua.py · thi-bac-ty phòng bao-gia"},"rollup_settlement":{"en":"Rollup settlement","vi":"Quyết toán qua rollup","loai":"architecture","nghia":"Thực thi tách khỏi quyết toán: giao dịch chạy ở lớp hai rồi nén về lớp một, và quyền đổi trạng thái cuối nằm ở đâu là câu hỏi mở.","goc":"repo","nguon":"do-sat-vien (bảng rủi ro L2) · thai-boc-tu toa t02"}},"quanHe":[{"tu":"price_signal","loai":"enables","den":"economic_calculation","vi":"Giá cho phép phân bổ nguồn lực theo chi phí cơ hội.","goc":"sach","tin":"high","chuong":[6],"trang":[117,120]},{"tu":"interest_rate","loai":"prices","den":"capital_market","vi":"Lãi suất được mô tả là giá của vốn vay.","goc":"sach","tin":"high","chuong":[6],"trang":[121]},{"tu":"trusted_third_party","loai":"creates","den":"counterparty_risk","vi":"Trung gian thêm điểm lỗi và nghĩa vụ phải tin.","goc":"sach","tin":"high","chuong":[8,9],"trang":[144,183]}],"lop2026":[{"tu":"stablecoin_settlement","loai":"carries","den":"counterparty_risk","vi":"Token neo đô la là một lời hứa đổi lại; lời hứa đó có người phát hành, và người phát hành có thể vỡ.","goc":"repo","tin":"high","nguon":"ho-bo phòng tien-cho (cột lệch neo)"},{"tu":"onchain_credit_market","loai":"extends","den":"capital_market","vi":"Tiết kiệm gặp nhu cầu vay qua hợp đồng thay vì qua trung gian, nhưng vẫn là cùng một việc kinh tế.","goc":"repo","tin":"high","nguon":"ho-bo phòng loi-suat"},{"tu":"onchain_credit_market","loai":"supports","den":"interest_rate","vi":"Lãi suất pool là giá của thời gian được niêm yết công khai và cập nhật liên tục.","goc":"repo","tin":"high","nguon":"ho-bo phòng loi-suat"},{"tu":"rwa_tokenization","loai":"extends","den":"capital_market","vi":"Lợi suất sinh ngoài chuỗi được đưa vào trong chuỗi, nối hai thị trường vốn vốn tách rời.","goc":"repo","tin":"medium","nguon":"thai-boc-tu toa t09"},{"tu":"rwa_tokenization","loai":"carries","den":"counterparty_risk","vi":"Token chỉ đáng giá bằng người giữ tài sản gốc ngoài chuỗi — đúng loại rủi ro mà quyết toán trên chuỗi không xoá được.","goc":"repo","tin":"high","nguon":"thai-boc-tu toa t09"},{"tu":"mev_extraction","loai":"extends","den":"price_signal","vi":"Phí ưu tiên là một giá thật cho một thứ khan hiếm thật — vị trí trong khối.","goc":"repo","tin":"low","nguon":"thai-boc-tu toa t02"},{"tu":"perpetual_funding","loai":"extends","den":"interest_rate","vi":"Funding là lãi suất của một vị thế đòn bẩy, kết toán theo mốc chứ không chảy liên tục.","goc":"repo","tin":"high","nguon":"thi-bac-ty phòng co-hoi · thi-bac-ty-runtime/bac/"},{"tu":"perpetual_funding","loai":"supports","den":"time_preference","vi":"Sẵn lòng trả để giữ vị thế thêm một chu kỳ là ưu tiên thời gian hiện ra thành một con số đo được.","goc":"repo","tin":"medium","nguon":"thi-bac-ty phòng hoc"},{"tu":"perpetual_funding","loai":"carries","den":"counterparty_risk","vi":"Vị thế hai chân ở hai sàn là tin hai bên thứ ba cùng lúc; một cảng ốm thì phép tính đúng vẫn mất tiền.","goc":"repo","tin":"high","nguon":"thi-bac-ty phòng cang"},{"tu":"venue_fragmented_depth","loai":"extends","den":"salability","vi":"Sách 2018 xếp tính thanh khoản thành ba trục — quy mô, không gian, thời gian — và coi nó là thuộc tính của chính đồng tiền. Từ đó tới nay chỗ trao đổi vỡ thành hàng chục cảng, và khi phải biến trục QUY MÔ thành một con số để rót vốn thì nó thôi là thuộc tính của tài sản: bốn cảng báo bốn giá cho cùng một rủi ro, vị thế hai chân bị chân MỎNG hơn chặn (`min` chứ không phải trung bình), và độ sâu thật thì không cảng nào công bố — `suc_chua.py` phải lấy 0,05% open interest làm thay và khai `do-sau-so-lenh` là thiếu ở MỌI lần ước lượng, không ngoại lệ. Đây là extends chứ không phải challenges: trục quy mô của sách vẫn đúng, nhưng 2026 cho thấy nó chỉ có nghĩa khi đi kèm một cảng và một cỡ vốn, và trong ba trục thì đúng nó là trục chưa đo được bằng dữ liệu công khai.","goc":"repo","tin":"high","nguon":"thi-bac-ty-runtime/bac/suc_chua.py · thi-bac-ty phòng trung-uong"},{"tu":"rollup_settlement","loai":"challenges","den":"trusted_third_party","vi":"Sách 2018 coi bên thứ ba đáng tin là ĐÚNG thứ chuỗi khối xoá đi: không còn ai đứng giữa ghi sổ thì cũng không còn ai phải tin. Từ đó tới nay thực thi phần lớn dời sang rollup, và bảng rủi ro mà Đô Sát Viên chép về cho thấy bên phải tin không biến mất — nó đổi hình thành quyền NÂNG CẤP HỢP ĐỒNG. Ô «cửa thoát» của Base ghi `None` và xếp hạng xấu, kèm nguyên văn lý do: hợp đồng nâng cấp được tức thì nên người dùng không có cửa sổ nào để rút ra trước một lần nâng cấp mình không muốn, và mỗi lần nâng cấp chỉ cần hai bên ký — Base Coordinator Multisig và Base Security Council. Đây là challenges chứ không phải carries: sách không dừng ở chỗ nói bên thứ ba là một rủi ro, sách nói công nghệ đã GIẢI QUYẾT nó; ô ấy nói ở lớp hai thì chưa. Phần tiến bộ thật của 2026 hẹp hơn lời sách nhiều: lòng tin ấy nay ĐO ĐƯỢC thành một ô có xếp hạng trong bảng, thay vì nằm trong điều khoản dịch vụ không ai đọc.","goc":"repo","tin":"high","nguon":"do-sat-vien/assets/js/v/rui-ro.js (cột cuaThoat, mục base) · do-sat-vien phòng rui-ro"}],"vaiVon":[{"ma":"time_price","ten":"Giá của thời gian/vốn","khaiNiem":["time_preference","interest_rate","capital_market","economic_calculation"],"heThong":["Basis / Cash-and-Carry","Funding arbitrage","Yield Trading"]},{"ma":"liquidity","ten":"Thanh khoản","khaiNiem":["salability","price_signal","economic_calculation"],"heThong":["DEX arbitrage","Automated LP","Stablecoin arbitrage"]},{"ma":"credit","ten":"Tín dụng","khaiNiem":["capital_market","interest_rate","counterparty_risk"],"heThong":["Lending Rate Arbitrage","Liquidation Hunter"]},{"ma":"price_discovery","ten":"Khám phá giá","khaiNiem":["price_signal","economic_calculation"],"heThong":["JIT Market Making","DEX market making","Prediction markets"]},{"ma":"risk","ten":"Rủi ro","khaiNiem":["counterparty_risk","trusted_third_party"],"heThong":["Risk Engine","venue health","bridge risk","depeg detection"]}],"nguon":{"sach":{"ten":"Tiêu chuẩn Bitcoin (The Bitcoin Standard)","tacGia":"Saifedean Ammous","nam":2018,"canhBao":"Tác giả đứng rõ trong truyền thống Kinh tế học Áo và có lập trường Bitcoin-maximalist; phải tách author_claim khỏi dữ kiện."},"ranhGioi":"Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."}};

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
