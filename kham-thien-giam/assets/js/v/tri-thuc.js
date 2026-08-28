/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.
   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:
       node knowledge-os/sinh.mjs kham-thien-giam

   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,
   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).

   BOT GHI mỗi 24 giờ (node `tri-thuc`) — ĐỪNG SỬA TAY file này,
   sửa dữ liệu nguồn rồi sinh lại. Sửa thẳng vào đây thì đúng cho
   tới lượt bot kế tiếp, rồi biến mất không dấu vết.
   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng
   CACHE_VERSION khi file này đổi. */
window.TRI_THUC = {"sinhLuc":"2026-08-28T20:04:05.794Z","goi":"knowledge-os","cung":"kham-thien-giam","vai":"Thị trường dự đoán","y":"Giá xác suất là cơ chế tổng hợp thông tin phân tán.","phong":[{"ma":"dai-chiem","ten":"Đài Chiêm","y":"Tự tính ra giá trị đáng có rồi mới nhìn sang chợ — đó là dùng phép tính kinh tế để KIỂM tín hiệu giá, thay vì đọc giá như sự thật.","khaiNiem":["price_signal","distributed_knowledge","economic_calculation"]},{"ma":"so-lenh","ten":"Sổ Lệnh","y":"Giá không kèm khối lượng là một con số vô nghĩa. Sổ lệnh là chỗ tính thanh khoản hiện ra thành số đo được.","khaiNiem":["salability","price_signal"]},{"ma":"can-loi","ten":"Cân Lợi","y":"Lợi thế chỉ có thật sau khi trừ phí và trượt giá. Trước đó nó là một tương quan, và tương quan không phải lợi thế.","khaiNiem":["economic_calculation","price_signal"]},{"ma":"kho-doi","ten":"Kho Đối","y":"Hai chân phải khớp; một chân khớp mà chân kia trượt là biến phòng hộ thành đặt cược. Vấn đề bắt đầu SAU cú khớp thứ nhất.","khaiNiem":["counterparty_risk","trusted_third_party"]},{"ma":"quan-vi","ten":"Đài Quan Ví","y":"Ví công khai là tri thức nằm rải sẵn trên sổ cái. Đọc được không có nghĩa là suy ra được động cơ — nên chỗ này chỉ ghi, không đoán.","khaiNiem":["distributed_knowledge","verification"]},{"ma":"truong-thi","ten":"Trường Thi","y":"Nói 60% mà thực tế thắng 40% thì mô hình sai, dù mỗi lệnh trông vẫn hợp lý. Hiệu chuẩn là phép kiểm duy nhất trả lời được câu đó.","khaiNiem":["verification","economic_calculation"]}],"khaiNiem":{"price_signal":{"en":"Price signal","vi":"Tín hiệu giá","loai":"information","nghia":"Giá cô đọng thông tin phân tán về khan hiếm, nhu cầu và chi phí cơ hội.","goc":"sach","chuong":[6],"trang":[115,117,120]},"distributed_knowledge":{"en":"Distributed knowledge","vi":"Tri thức phân tán","loai":"information","nghia":"Tri thức kinh tế nằm rải trong nhiều người/ngành và không thể tập trung hoàn toàn vào một nhà hoạch định.","goc":"sach","chuong":[6],"trang":[115,117]},"economic_calculation":{"en":"Economic calculation","vi":"Tính toán kinh tế","loai":"mechanism","nghia":"Dùng giá và đơn vị tính toán để so sánh chi phí, doanh thu, lợi nhuận và lựa chọn phương án.","goc":"sach","chuong":[1,6,7],"trang":[16,114,118,140]},"network_effect":{"en":"Network effect","vi":"Hiệu ứng mạng","loai":"network_property","nghia":"Lợi ích dùng một tiêu chuẩn trao đổi tăng khi số người cùng dùng tăng.","goc":"sach","chuong":[1],"trang":[16]},"salability":{"en":"Salability","vi":"Tính thanh khoản/khả năng bán đổi","loai":"money_property","nghia":"Mức dễ trao đổi với tổn thất thấp, xét theo quy mô, không gian và thời gian.","goc":"sach","chuong":[1],"trang":[12,13]},"counterparty_risk":{"en":"Counterparty risk","vi":"Rủi ro đối tác","loai":"risk","nghia":"Rủi ro bên còn lại hoặc trung gian không thực hiện nghĩa vụ.","goc":"sach","chuong":[9],"trang":[183,188]},"trusted_third_party":{"en":"Trusted third party","vi":"Bên thứ ba đáng tin cậy","loai":"architecture","nghia":"Trung gian mà hai bên phải tin để ghi sổ, xử lý hoặc quyết toán giao dịch.","goc":"sach","chuong":[8,10],"trang":[144,229,231]},"verification":{"en":"Verification","vi":"Xác minh","loai":"trust_model","nghia":"Thay việc tin một bên bằng quy tắc/bằng chứng mà nhiều nút có thể tự kiểm tra.","goc":"sach","chuong":[8],"trang":[146,147]},"stablecoin_settlement":{"en":"Stablecoin settlement","vi":"Quyết toán bằng stablecoin","loai":"payment_function","nghia":"Khối lượng chuyển giá trị chạy bằng token neo đô la trên chuỗi công khai, thay vì bằng đồng tiền gốc của chuỗi.","goc":"repo","nguon":"ho-bo/assets/js/v/dong-tien.js · thai-boc-tu toa t04"},"rwa_tokenization":{"en":"RWA tokenization","vi":"Token hoá tài sản thế giới thật","loai":"asset_role","nghia":"Trái phiếu kho bạc, tín dụng tư nhân và hàng hoá được phát hành dạng token, mang lợi suất ngoài chuỗi vào trong chuỗi.","goc":"repo","nguon":"thai-boc-tu toa t09"},"mev_extraction":{"en":"MEV extraction","vi":"Rút giá trị theo thứ tự khối","loai":"network_mechanism","nghia":"Khoản thu được nhờ quyền xếp thứ tự giao dịch trong một khối; nó biến quyền dựng khối thành một tài sản có giá.","goc":"repo","nguon":"thai-boc-tu toa t02 (nhóm nguồn Block Builders · MEV)"},"perpetual_funding":{"en":"Perpetual funding rate","vi":"Phí funding hợp đồng vĩnh cửu","loai":"price","nghia":"Khoản trả định kỳ giữa hai phía long và short để kéo giá hợp đồng vĩnh cửu về giá giao ngay — lãi suất của một vị thế đòn bẩy, tính theo giờ.","goc":"repo","nguon":"thi-bac-ty-runtime/bac/ · thi-bac-ty/assets/js/v/cang-phi.js"},"ai_agent_execution":{"en":"AI agent execution","vi":"Tác tử AI ra quyết định","loai":"mechanism","nghia":"Model đọc dữ liệu thị trường rồi đề xuất hành động, còn quyền phủ quyết nằm ở một lớp luật tất định tách riêng.","goc":"repo","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết) · thai-boc-tu toa t12"}},"quanHe":[{"tu":"price_signal","loai":"carries","den":"distributed_knowledge","vi":"Giá cô đọng điều kiện và lựa chọn của nhiều người.","goc":"sach","tin":"high","chuong":[6],"trang":[115,117]},{"tu":"price_signal","loai":"enables","den":"economic_calculation","vi":"Giá cho phép phân bổ nguồn lực theo chi phí cơ hội.","goc":"sach","tin":"high","chuong":[6],"trang":[117,120]},{"tu":"trusted_third_party","loai":"creates","den":"counterparty_risk","vi":"Trung gian thêm điểm lỗi và nghĩa vụ phải tin.","goc":"sach","tin":"high","chuong":[8,9],"trang":[144,183]}],"lop2026":[{"tu":"stablecoin_settlement","loai":"carries","den":"counterparty_risk","vi":"Token neo đô la là một lời hứa đổi lại; lời hứa đó có người phát hành, và người phát hành có thể vỡ.","goc":"repo","tin":"high","nguon":"ho-bo phòng tien-cho (cột lệch neo)"},{"tu":"rwa_tokenization","loai":"carries","den":"counterparty_risk","vi":"Token chỉ đáng giá bằng người giữ tài sản gốc ngoài chuỗi — đúng loại rủi ro mà quyết toán trên chuỗi không xoá được.","goc":"repo","tin":"high","nguon":"thai-boc-tu toa t09"},{"tu":"mev_extraction","loai":"extends","den":"price_signal","vi":"Phí ưu tiên là một giá thật cho một thứ khan hiếm thật — vị trí trong khối.","goc":"repo","tin":"low","nguon":"thai-boc-tu toa t02"},{"tu":"perpetual_funding","loai":"carries","den":"counterparty_risk","vi":"Vị thế hai chân ở hai sàn là tin hai bên thứ ba cùng lúc; một cảng ốm thì phép tính đúng vẫn mất tiền.","goc":"repo","tin":"high","nguon":"thi-bac-ty phòng cang"},{"tu":"ai_agent_execution","loai":"extends","den":"distributed_knowledge","vi":"Model gom tín hiệu rải rác mà không ai đọc hết được, đúng bài toán tri thức phân tán.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime"},{"tu":"ai_agent_execution","loai":"challenges","den":"verification","vi":"Một đề xuất của model không kiểm lại được từng bước, nên quyền phủ quyết phải nằm ở lớp luật tất định tách riêng.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết)"}],"vaiVon":[{"ma":"liquidity","ten":"Thanh khoản","khaiNiem":["salability","price_signal","economic_calculation"],"heThong":["DEX arbitrage","Automated LP","Stablecoin arbitrage"]},{"ma":"price_discovery","ten":"Khám phá giá","khaiNiem":["price_signal","distributed_knowledge","economic_calculation"],"heThong":["JIT Market Making","DEX market making","Prediction markets"]},{"ma":"risk","ten":"Rủi ro","khaiNiem":["counterparty_risk","trusted_third_party","verification"],"heThong":["Risk Engine","venue health","bridge risk","depeg detection"]},{"ma":"settlement","ten":"Quyết toán","khaiNiem":["verification","counterparty_risk"],"heThong":["L1/L2 settlement","Cross-chain Capital Router"]}],"nguon":{"sach":{"ten":"Tiêu chuẩn Bitcoin (The Bitcoin Standard)","tacGia":"Saifedean Ammous","nam":2018,"canhBao":"Tác giả đứng rõ trong truyền thống Kinh tế học Áo và có lập trường Bitcoin-maximalist; phải tách author_claim khỏi dữ kiện."},"ranhGioi":"Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."}};

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
