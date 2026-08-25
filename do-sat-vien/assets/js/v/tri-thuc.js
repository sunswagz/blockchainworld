/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.
   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:
       node knowledge-os/sinh.mjs do-sat-vien

   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,
   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).

   SINH TAY, PHẢI COMMIT — không workflow nào chạy lệnh này.
   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng
   CACHE_VERSION khi file này đổi. */
window.TRI_THUC = {"sinhLuc":"2026-08-25T17:11:47.923Z","goi":"knowledge-os","cung":"do-sat-vien","vai":"Rủi ro Layer 2","y":"Mỗi risk trả lời: ai có quyền đổi trạng thái cuối, người dùng đang tin ai?","phong":[{"ma":"tong-quan","ten":"Tổng quan Lớp 2","y":"Mỗi lớp hai là một cách trả lời câu mở rộng bằng cách hi sinh gì. Bảng này xếp các câu trả lời cạnh nhau để so được.","khaiNiem":["scaling_tradeoff","final_settlement","decentralization"]},{"ma":"rui-ro","ten":"Phân tích rủi ro","y":"Mỗi ô rủi ro trả lời đúng một câu: ai có quyền đổi trạng thái cuối, và người gửi tiền đang tin ai.","khaiNiem":["trusted_third_party","counterparty_risk","decentralization"]},{"ma":"kiem-chung","ten":"Hệ chứng minh","y":"Chứng minh là cách thay lòng tin bằng phép kiểm. Không có nó thì lớp hai chỉ là một cơ sở dữ liệu có người quản.","khaiNiem":["verification","consensus"]},{"ma":"du-lieu","ten":"Dữ liệu sẵn có","y":"Không đọc được dữ liệu thì không dựng lại được trạng thái, và không dựng lại được thì không tự rút tiền ra được.","khaiNiem":["verification","final_settlement"]},{"ma":"xep-thu-tu","ten":"Xếp thứ tự giao dịch","y":"Quyền xếp thứ tự là một quyền lực thật: nó quyết định giao dịch nào vào trước, và ai bị bỏ lại.","khaiNiem":["trusted_third_party","decentralization","final_settlement"]},{"ma":"hoat-dong","ten":"Hoạt động","y":"Số giao dịch và phí là tín hiệu về nhu cầu thật, tách khỏi câu chuyện tiếp thị.","khaiNiem":["network_effect","price_signal"]},{"ma":"do-song","ten":"Độ sống","y":"Mạng đứng im thì tiền vẫn ở đó nhưng không rút ra được. Độ sống là khoảng cách giữa sở hữu và dùng được.","khaiNiem":["final_settlement","counterparty_risk"]},{"ma":"luu-tru","ten":"Cửa thoát","y":"Cửa thoát là quyền rút về lớp nền khi người vận hành ngừng hợp tác. Không có nó thì chủ quyền chỉ là lời hứa.","khaiNiem":["individual_sovereignty","final_settlement"]},{"ma":"lt-tong-quan","ten":"Liên thông","y":"Chuyển giá trị giữa hai chuỗi là bài toán quyết toán liên miền — và mọi lời giải đều thêm một bên phải tin.","khaiNiem":["international_settlement","trusted_third_party","counterparty_risk"]},{"ma":"lt-khung-token","ten":"Khung token liên chuỗi","y":"Cùng một cái tên token trên hai chuỗi có thể là hai lời hứa khác nhau. Khung nào phát hành nó quyết định lời hứa đó ai giữ.","khaiNiem":["medium_of_exchange","counterparty_risk"]},{"ma":"lt-cau-y-dinh","ten":"Cầu ý định","y":"Người giải ứng vốn trước rồi đòi lại sau — đó là thanh khoản đổi lấy rủi ro, đúng phép đánh đổi của mọi trung gian.","khaiNiem":["salability","trusted_third_party","counterparty_risk"]},{"ma":"rieng-tu","ten":"Quyền riêng tư","y":"Kiểm được mà không phơi ra là bài toán khó nhất của sổ cái công khai.","khaiNiem":["individual_sovereignty","verification"]},{"ma":"zk","ten":"Bằng chứng không tiết lộ","y":"Kiểm rẻ hơn chạy lại là điều kiện để một người thường còn tự kiểm được — tức là để phi tập trung còn nghĩa.","khaiNiem":["verification","decentralization"]}],"khaiNiem":{"scaling_tradeoff":{"en":"Scaling trade-off","vi":"Đánh đổi mở rộng quy mô","loai":"architecture_tradeoff","nghia":"Tăng dữ liệu/thực thi trên lớp đồng thuận có thể tăng chi phí chạy nút và giảm mức phân tán.","goc":"sach","chuong":[10],"trang":[230]},"decentralization":{"en":"Decentralization","vi":"Phi tập trung","loai":"network_property","nghia":"Quyền xác minh/vận hành không tập trung vào một bên duy nhất.","goc":"sach","chuong":[8,10],"trang":[146,230]},"trusted_third_party":{"en":"Trusted third party","vi":"Bên thứ ba đáng tin cậy","loai":"architecture","nghia":"Trung gian mà hai bên phải tin để ghi sổ, xử lý hoặc quyết toán giao dịch.","goc":"sach","chuong":[8,10],"trang":[144,229,231]},"final_settlement":{"en":"Final settlement","vi":"Quyết toán cuối cùng","loai":"payment_function","nghia":"Trạng thái chuyển giá trị được xem là hoàn tất, không phụ thuộc chuỗi nghĩa vụ trung gian tiếp theo.","goc":"sach","chuong":[9],"trang":[182,183,187]},"counterparty_risk":{"en":"Counterparty risk","vi":"Rủi ro đối tác","loai":"risk","nghia":"Rủi ro bên còn lại hoặc trung gian không thực hiện nghĩa vụ.","goc":"sach","chuong":[9],"trang":[183,188]},"verification":{"en":"Verification","vi":"Xác minh","loai":"trust_model","nghia":"Thay việc tin một bên bằng quy tắc/bằng chứng mà nhiều nút có thể tự kiểm tra.","goc":"sach","chuong":[8],"trang":[146,147]},"consensus":{"en":"Consensus","vi":"Đồng thuận","loai":"network_mechanism","nghia":"Quy tắc để mạng thống nhất trạng thái hợp lệ mà không cần một sổ cái trung tâm.","goc":"sach","chuong":[8],"trang":[147]},"network_effect":{"en":"Network effect","vi":"Hiệu ứng mạng","loai":"network_property","nghia":"Lợi ích dùng một tiêu chuẩn trao đổi tăng khi số người cùng dùng tăng.","goc":"sach","chuong":[1],"trang":[16]},"price_signal":{"en":"Price signal","vi":"Tín hiệu giá","loai":"information","nghia":"Giá cô đọng thông tin phân tán về khan hiếm, nhu cầu và chi phí cơ hội.","goc":"sach","chuong":[6],"trang":[115,117,120]},"individual_sovereignty":{"en":"Individual sovereignty","vi":"Chủ quyền cá nhân","loai":"political_economy","nghia":"Khả năng cá nhân nắm/di chuyển giá trị mà không hoàn toàn phụ thuộc quyền cho phép của trung gian.","goc":"sach","chuong":[5,7,8,9],"trang":[83,135,142,187]},"international_settlement":{"en":"International settlement","vi":"Quyết toán quốc tế","loai":"payment_function","nghia":"Chuyển giá trị cuối cùng giữa các bên ở khu vực pháp lý khác nhau.","goc":"sach","chuong":[9],"trang":[182,183,188]},"medium_of_exchange":{"en":"Medium of exchange","vi":"Phương tiện trao đổi","loai":"money_function","nghia":"Tài sản được nhận chủ yếu để đổi lấy hàng hóa khác; chức năng cốt lõi của tiền.","goc":"sach","chuong":[1],"trang":[11]},"salability":{"en":"Salability","vi":"Tính thanh khoản/khả năng bán đổi","loai":"money_property","nghia":"Mức dễ trao đổi với tổn thất thấp, xét theo quy mô, không gian và thời gian.","goc":"sach","chuong":[1],"trang":[12,13]},"stablecoin_settlement":{"en":"Stablecoin settlement","vi":"Quyết toán bằng stablecoin","loai":"payment_function","nghia":"Khối lượng chuyển giá trị chạy bằng token neo đô la trên chuỗi công khai, thay vì bằng đồng tiền gốc của chuỗi.","goc":"repo","nguon":"ho-bo/assets/js/v/dong-tien.js · thai-boc-tu toa t04"},"rwa_tokenization":{"en":"RWA tokenization","vi":"Token hoá tài sản thế giới thật","loai":"asset_role","nghia":"Trái phiếu kho bạc, tín dụng tư nhân và hàng hoá được phát hành dạng token, mang lợi suất ngoài chuỗi vào trong chuỗi.","goc":"repo","nguon":"thai-boc-tu toa t09"},"rollup_settlement":{"en":"Rollup settlement","vi":"Quyết toán qua rollup","loai":"architecture","nghia":"Thực thi tách khỏi quyết toán: giao dịch chạy ở lớp hai rồi nén về lớp một, và quyền đổi trạng thái cuối nằm ở đâu là câu hỏi mở.","goc":"repo","nguon":"do-sat-vien (bảng rủi ro L2) · thai-boc-tu toa t02"},"mev_extraction":{"en":"MEV extraction","vi":"Rút giá trị theo thứ tự khối","loai":"network_mechanism","nghia":"Khoản thu được nhờ quyền xếp thứ tự giao dịch trong một khối; nó biến quyền dựng khối thành một tài sản có giá.","goc":"repo","nguon":"thai-boc-tu toa t02 (nhóm nguồn Block Builders · MEV)"},"perpetual_funding":{"en":"Perpetual funding rate","vi":"Phí funding hợp đồng vĩnh cửu","loai":"price","nghia":"Khoản trả định kỳ giữa hai phía long và short để kéo giá hợp đồng vĩnh cửu về giá giao ngay — lãi suất của một vị thế đòn bẩy, tính theo giờ.","goc":"repo","nguon":"thi-bac-ty-runtime/bac/ · thi-bac-ty/assets/js/v/cang-phi.js"},"ai_agent_execution":{"en":"AI agent execution","vi":"Tác tử AI ra quyết định","loai":"mechanism","nghia":"Model đọc dữ liệu thị trường rồi đề xuất hành động, còn quyền phủ quyết nằm ở một lớp luật tất định tách riêng.","goc":"repo","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết) · thai-boc-tu toa t12"}},"quanHe":[{"tu":"medium_of_exchange","loai":"requires","den":"salability","vi":"Phương tiện trao đổi phải dễ bán/đổi với tổn thất thấp.","goc":"sach","tin":"high","chuong":[1],"trang":[11,12]},{"tu":"trusted_third_party","loai":"creates","den":"counterparty_risk","vi":"Trung gian thêm điểm lỗi và nghĩa vụ phải tin.","goc":"sach","tin":"high","chuong":[8,9],"trang":[144,183]},{"tu":"verification","loai":"supports","den":"consensus","vi":"Các nút tự kiểm tra quy tắc trước khi chấp nhận trạng thái.","goc":"sach","tin":"high","chuong":[8],"trang":[146,147]},{"tu":"final_settlement","loai":"reduces","den":"counterparty_risk","vi":"Quyết toán cuối giảm chuỗi nghĩa vụ chờ trung gian.","goc":"sach","tin":"high","chuong":[9],"trang":[183]},{"tu":"scaling_tradeoff","loai":"affects","den":"decentralization","vi":"Lớp đồng thuận nặng hơn có thể làm chi phí giữ/xác minh bản sao tăng.","goc":"sach","tin":"high","chuong":[10],"trang":[230]}],"lop2026":[{"tu":"stablecoin_settlement","loai":"extends","den":"medium_of_exchange","vi":"Chức năng phương tiện trao đổi chạy trên chuỗi công khai nhưng đơn vị vẫn là đô la, không phải đồng tiền gốc của chuỗi.","goc":"repo","tin":"high","nguon":"ho-bo phòng tien-cho"},{"tu":"stablecoin_settlement","loai":"carries","den":"counterparty_risk","vi":"Token neo đô la là một lời hứa đổi lại; lời hứa đó có người phát hành, và người phát hành có thể vỡ.","goc":"repo","tin":"high","nguon":"ho-bo phòng tien-cho (cột lệch neo)"},{"tu":"rwa_tokenization","loai":"carries","den":"counterparty_risk","vi":"Token chỉ đáng giá bằng người giữ tài sản gốc ngoài chuỗi — đúng loại rủi ro mà quyết toán trên chuỗi không xoá được.","goc":"repo","tin":"high","nguon":"thai-boc-tu toa t09"},{"tu":"rollup_settlement","loai":"extends","den":"scaling_tradeoff","vi":"Đánh đổi mở rộng được dời sang một lớp riêng thay vì nới thông số lớp một.","goc":"repo","tin":"high","nguon":"do-sat-vien"},{"tu":"rollup_settlement","loai":"challenges","den":"final_settlement","vi":"Quyết toán cuối trở thành câu hỏi 'ai có quyền đổi trạng thái cuối, và trong bao lâu' chứ không còn là một mốc dứt khoát.","goc":"repo","tin":"medium","nguon":"do-sat-vien (bảng rủi ro L2)"},{"tu":"mev_extraction","loai":"challenges","den":"decentralization","vi":"Quyền xếp thứ tự có giá thì nó dồn về tay người trả giá cao nhất, và số người dựng khối co lại.","goc":"repo","tin":"medium","nguon":"thai-boc-tu toa t02"},{"tu":"mev_extraction","loai":"extends","den":"price_signal","vi":"Phí ưu tiên là một giá thật cho một thứ khan hiếm thật — vị trí trong khối.","goc":"repo","tin":"low","nguon":"thai-boc-tu toa t02"},{"tu":"perpetual_funding","loai":"carries","den":"counterparty_risk","vi":"Vị thế hai chân ở hai sàn là tin hai bên thứ ba cùng lúc; một cảng ốm thì phép tính đúng vẫn mất tiền.","goc":"repo","tin":"high","nguon":"thi-bac-ty phòng cang"},{"tu":"ai_agent_execution","loai":"challenges","den":"verification","vi":"Một đề xuất của model không kiểm lại được từng bước, nên quyền phủ quyết phải nằm ở lớp luật tất định tách riêng.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết)"}],"vaiVon":[{"ma":"settlement","ten":"Quyết toán","khaiNiem":["final_settlement","consensus","verification","counterparty_risk"],"heThong":["L1/L2 settlement","Cross-chain Capital Router"]},{"ma":"risk","ten":"Rủi ro","khaiNiem":["counterparty_risk","trusted_third_party","verification","decentralization"],"heThong":["Risk Engine","venue health","bridge risk","depeg detection"]},{"ma":"liquidity","ten":"Thanh khoản","khaiNiem":["salability","medium_of_exchange","price_signal"],"heThong":["DEX arbitrage","Automated LP","Stablecoin arbitrage"]}],"nguon":{"sach":{"ten":"Tiêu chuẩn Bitcoin (The Bitcoin Standard)","tacGia":"Saifedean Ammous","nam":2018,"canhBao":"Tác giả đứng rõ trong truyền thống Kinh tế học Áo và có lập trường Bitcoin-maximalist; phải tách author_claim khỏi dữ kiện."},"ranhGioi":"Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."}};

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
