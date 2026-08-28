/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.
   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:
       node knowledge-os/sinh.mjs ho-bo

   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,
   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).

   SINH TAY, PHẢI COMMIT — không workflow nào chạy lệnh này.
   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng
   CACHE_VERSION khi file này đổi. */
window.TRI_THUC = {"sinhLuc":"2026-08-28T15:12:13.456Z","goi":"knowledge-os","cung":"ho-bo","vai":"Dòng tiền, stablecoin, lợi suất và vốn","y":"Lợi suất không chỉ là %, mà là giá vốn + rủi ro + nhu cầu thanh khoản.","phong":[{"ma":"tien-cho","ten":"Tiền Chờ","y":"Stablecoin làm được việc của tiền chỉ chừng nào lời hứa đổi lại còn đứng — nên cột lệch neo đọc chiều giảm là đọc rủi ro đối tác.","khaiNiem":["medium_of_exchange","unit_of_account","counterparty_risk"]},{"ma":"loi-suat","ten":"Lợi Suất","y":"Một con số % là ba thứ cộng lại: giá của thời gian, phần bù rủi ro, và nhu cầu thanh khoản trước mắt. Xếp hạng theo % thô là xếp hạng theo rủi ro.","khaiNiem":["interest_rate","capital_market","savings","counterparty_risk"]},{"ma":"dong-tien","ten":"Dòng Tiền","y":"Vốn chảy đi đâu là một tín hiệu giá ở mức tổng: nó nói thị trường đang định giá công việc nào cao hơn.","khaiNiem":["price_signal","capital_market","salability"]},{"ma":"kho-bac","ten":"Kho Bạc","y":"TVL theo chuỗi đo lượng giá trị chịu nằm lại dưới quyền quyết toán của chuỗi đó.","khaiNiem":["store_of_value","network_effect","final_settlement"]},{"ma":"nhom-nganh","ten":"Nhóm Ngành","y":"Chia theo ngành là cách đọc vốn đang làm công việc kinh tế nào, thay vì đọc tên dự án.","khaiNiem":["economic_calculation","capital_market"]},{"ma":"an-ninh","ten":"An Ninh","y":"Mỗi vụ mất tiền là một lần bên thứ ba đáng tin hoá ra không đáng tin — và số tiền mất là giá của lần tin đó.","khaiNiem":["counterparty_risk","trusted_third_party","verification"]},{"ma":"tong-quan","ten":"Đại Sảnh","y":"Chế độ rủi ro là một phép tính gộp trên nhiều tín hiệu giá. Nó tóm tắt, nên nó cũng che — mỗi thành phần đều mở ra xem lại được ở phòng riêng.","khaiNiem":["economic_calculation","price_signal","capital_market"]},{"ma":"kho-nguon","ten":"Kho Nguồn","y":"Không ai đọc hết thị trường một mình. Kho công cụ này là cách gom tri thức nằm rải, và mỗi công cụ là một đường tự kiểm lại thay vì tin lời người khác.","khaiNiem":["distributed_knowledge","verification"]}],"khaiNiem":{"medium_of_exchange":{"en":"Medium of exchange","vi":"Phương tiện trao đổi","loai":"money_function","nghia":"Tài sản được nhận chủ yếu để đổi lấy hàng hóa khác; chức năng cốt lõi của tiền.","goc":"sach","chuong":[1],"trang":[11]},"unit_of_account":{"en":"Unit of account","vi":"Đơn vị tính toán","loai":"money_function","nghia":"Thước đo chung để biểu thị giá, lời/lỗ và thực hiện tính toán kinh tế.","goc":"sach","chuong":[1,6],"trang":[16,114]},"capital_market":{"en":"Capital market","vi":"Thị trường vốn","loai":"market","nghia":"Nơi vốn tiết kiệm được cho vay/phân bổ cho các quá trình sản xuất và đầu tư.","goc":"sach","chuong":[6],"trang":[121,123]},"interest_rate":{"en":"Interest rate","vi":"Lãi suất","loai":"price","nghia":"Giá của vốn vay; trong sách nó nối tiết kiệm, nhu cầu vay và ưu tiên thời gian.","goc":"sach","chuong":[5,6],"trang":[90,121]},"savings":{"en":"Savings","vi":"Tiết kiệm","loai":"capital_process","nghia":"Phần tiêu dùng hiện tại được trì hoãn để dành nguồn lực cho tương lai.","goc":"sach","chuong":[5,6],"trang":[85,89,121,123]},"price_signal":{"en":"Price signal","vi":"Tín hiệu giá","loai":"information","nghia":"Giá cô đọng thông tin phân tán về khan hiếm, nhu cầu và chi phí cơ hội.","goc":"sach","chuong":[6],"trang":[115,117,120]},"counterparty_risk":{"en":"Counterparty risk","vi":"Rủi ro đối tác","loai":"risk","nghia":"Rủi ro bên còn lại hoặc trung gian không thực hiện nghĩa vụ.","goc":"sach","chuong":[9],"trang":[183,188]},"salability":{"en":"Salability","vi":"Tính thanh khoản/khả năng bán đổi","loai":"money_property","nghia":"Mức dễ trao đổi với tổn thất thấp, xét theo quy mô, không gian và thời gian.","goc":"sach","chuong":[1],"trang":[12,13]},"store_of_value":{"en":"Store of value","vi":"Kho lưu trữ giá trị","loai":"money_function","nghia":"Khả năng giữ sức mua qua thời gian.","goc":"sach","chuong":[1,9],"trang":[12,13,182]},"network_effect":{"en":"Network effect","vi":"Hiệu ứng mạng","loai":"network_property","nghia":"Lợi ích dùng một tiêu chuẩn trao đổi tăng khi số người cùng dùng tăng.","goc":"sach","chuong":[1],"trang":[16]},"final_settlement":{"en":"Final settlement","vi":"Quyết toán cuối cùng","loai":"payment_function","nghia":"Trạng thái chuyển giá trị được xem là hoàn tất, không phụ thuộc chuỗi nghĩa vụ trung gian tiếp theo.","goc":"sach","chuong":[9],"trang":[182,183,187]},"economic_calculation":{"en":"Economic calculation","vi":"Tính toán kinh tế","loai":"mechanism","nghia":"Dùng giá và đơn vị tính toán để so sánh chi phí, doanh thu, lợi nhuận và lựa chọn phương án.","goc":"sach","chuong":[1,6,7],"trang":[16,114,118,140]},"trusted_third_party":{"en":"Trusted third party","vi":"Bên thứ ba đáng tin cậy","loai":"architecture","nghia":"Trung gian mà hai bên phải tin để ghi sổ, xử lý hoặc quyết toán giao dịch.","goc":"sach","chuong":[8,10],"trang":[144,229,231]},"verification":{"en":"Verification","vi":"Xác minh","loai":"trust_model","nghia":"Thay việc tin một bên bằng quy tắc/bằng chứng mà nhiều nút có thể tự kiểm tra.","goc":"sach","chuong":[8],"trang":[146,147]},"distributed_knowledge":{"en":"Distributed knowledge","vi":"Tri thức phân tán","loai":"information","nghia":"Tri thức kinh tế nằm rải trong nhiều người/ngành và không thể tập trung hoàn toàn vào một nhà hoạch định.","goc":"sach","chuong":[6],"trang":[115,117]},"stablecoin_settlement":{"en":"Stablecoin settlement","vi":"Quyết toán bằng stablecoin","loai":"payment_function","nghia":"Khối lượng chuyển giá trị chạy bằng token neo đô la trên chuỗi công khai, thay vì bằng đồng tiền gốc của chuỗi.","goc":"repo","nguon":"ho-bo/assets/js/v/dong-tien.js · thai-boc-tu toa t04"},"onchain_credit_market":{"en":"On-chain credit market","vi":"Thị trường tín dụng trên chuỗi","loai":"market","nghia":"Cho vay có thế chấp vượt mức chạy bằng hợp đồng, lãi suất do cung cầu trong pool quyết định chứ không do một ngân hàng đặt.","goc":"repo","nguon":"ho-bo phòng loi-suat · thai-boc-tu toa t06"},"rwa_tokenization":{"en":"RWA tokenization","vi":"Token hoá tài sản thế giới thật","loai":"asset_role","nghia":"Trái phiếu kho bạc, tín dụng tư nhân và hàng hoá được phát hành dạng token, mang lợi suất ngoài chuỗi vào trong chuỗi.","goc":"repo","nguon":"thai-boc-tu toa t09"},"rollup_settlement":{"en":"Rollup settlement","vi":"Quyết toán qua rollup","loai":"architecture","nghia":"Thực thi tách khỏi quyết toán: giao dịch chạy ở lớp hai rồi nén về lớp một, và quyền đổi trạng thái cuối nằm ở đâu là câu hỏi mở.","goc":"repo","nguon":"do-sat-vien (bảng rủi ro L2) · thai-boc-tu toa t02"},"mev_extraction":{"en":"MEV extraction","vi":"Rút giá trị theo thứ tự khối","loai":"network_mechanism","nghia":"Khoản thu được nhờ quyền xếp thứ tự giao dịch trong một khối; nó biến quyền dựng khối thành một tài sản có giá.","goc":"repo","nguon":"thai-boc-tu toa t02 (nhóm nguồn Block Builders · MEV)"},"perpetual_funding":{"en":"Perpetual funding rate","vi":"Phí funding hợp đồng vĩnh cửu","loai":"price","nghia":"Khoản trả định kỳ giữa hai phía long và short để kéo giá hợp đồng vĩnh cửu về giá giao ngay — lãi suất của một vị thế đòn bẩy, tính theo giờ.","goc":"repo","nguon":"thi-bac-ty-runtime/bac/ · thi-bac-ty/assets/js/v/cang-phi.js"},"ai_agent_execution":{"en":"AI agent execution","vi":"Tác tử AI ra quyết định","loai":"mechanism","nghia":"Model đọc dữ liệu thị trường rồi đề xuất hành động, còn quyền phủ quyết nằm ở một lớp luật tất định tách riêng.","goc":"repo","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết) · thai-boc-tu toa t12"}},"quanHe":[{"tu":"medium_of_exchange","loai":"requires","den":"salability","vi":"Phương tiện trao đổi phải dễ bán/đổi với tổn thất thấp.","goc":"sach","tin":"high","chuong":[1],"trang":[11,12]},{"tu":"salability","loai":"includes","den":"store_of_value","vi":"Thanh khoản theo thời gian trở thành khả năng lưu trữ giá trị.","goc":"sach","tin":"high","chuong":[1],"trang":[12,13]},{"tu":"salability","loai":"supports","den":"unit_of_account","vi":"Mức chấp nhận rộng giúp giá cùng biểu thị trong một đơn vị.","goc":"sach","tin":"high","chuong":[1],"trang":[16]},{"tu":"unit_of_account","loai":"enables","den":"economic_calculation","vi":"Đơn vị chung cho phép so sánh chi phí và lợi nhuận.","goc":"sach","tin":"high","chuong":[1,6],"trang":[16,114]},{"tu":"price_signal","loai":"carries","den":"distributed_knowledge","vi":"Giá cô đọng điều kiện và lựa chọn của nhiều người.","goc":"sach","tin":"high","chuong":[6],"trang":[115,117]},{"tu":"price_signal","loai":"enables","den":"economic_calculation","vi":"Giá cho phép phân bổ nguồn lực theo chi phí cơ hội.","goc":"sach","tin":"high","chuong":[6],"trang":[117,120]},{"tu":"interest_rate","loai":"prices","den":"capital_market","vi":"Lãi suất được mô tả là giá của vốn vay.","goc":"sach","tin":"high","chuong":[6],"trang":[121]},{"tu":"trusted_third_party","loai":"creates","den":"counterparty_risk","vi":"Trung gian thêm điểm lỗi và nghĩa vụ phải tin.","goc":"sach","tin":"high","chuong":[8,9],"trang":[144,183]},{"tu":"final_settlement","loai":"reduces","den":"counterparty_risk","vi":"Quyết toán cuối giảm chuỗi nghĩa vụ chờ trung gian.","goc":"sach","tin":"high","chuong":[9],"trang":[183]}],"lop2026":[{"tu":"stablecoin_settlement","loai":"extends","den":"medium_of_exchange","vi":"Chức năng phương tiện trao đổi chạy trên chuỗi công khai nhưng đơn vị vẫn là đô la, không phải đồng tiền gốc của chuỗi.","goc":"repo","tin":"high","nguon":"ho-bo phòng tien-cho"},{"tu":"stablecoin_settlement","loai":"carries","den":"counterparty_risk","vi":"Token neo đô la là một lời hứa đổi lại; lời hứa đó có người phát hành, và người phát hành có thể vỡ.","goc":"repo","tin":"high","nguon":"ho-bo phòng tien-cho (cột lệch neo)"},{"tu":"onchain_credit_market","loai":"extends","den":"capital_market","vi":"Tiết kiệm gặp nhu cầu vay qua hợp đồng thay vì qua trung gian, nhưng vẫn là cùng một việc kinh tế.","goc":"repo","tin":"high","nguon":"ho-bo phòng loi-suat"},{"tu":"onchain_credit_market","loai":"supports","den":"interest_rate","vi":"Lãi suất pool là giá của thời gian được niêm yết công khai và cập nhật liên tục.","goc":"repo","tin":"high","nguon":"ho-bo phòng loi-suat"},{"tu":"rwa_tokenization","loai":"extends","den":"capital_market","vi":"Lợi suất sinh ngoài chuỗi được đưa vào trong chuỗi, nối hai thị trường vốn vốn tách rời.","goc":"repo","tin":"medium","nguon":"thai-boc-tu toa t09"},{"tu":"rwa_tokenization","loai":"carries","den":"counterparty_risk","vi":"Token chỉ đáng giá bằng người giữ tài sản gốc ngoài chuỗi — đúng loại rủi ro mà quyết toán trên chuỗi không xoá được.","goc":"repo","tin":"high","nguon":"thai-boc-tu toa t09"},{"tu":"rollup_settlement","loai":"challenges","den":"final_settlement","vi":"Quyết toán cuối trở thành câu hỏi 'ai có quyền đổi trạng thái cuối, và trong bao lâu' chứ không còn là một mốc dứt khoát.","goc":"repo","tin":"medium","nguon":"do-sat-vien (bảng rủi ro L2)"},{"tu":"mev_extraction","loai":"extends","den":"price_signal","vi":"Phí ưu tiên là một giá thật cho một thứ khan hiếm thật — vị trí trong khối.","goc":"repo","tin":"low","nguon":"thai-boc-tu toa t02"},{"tu":"perpetual_funding","loai":"extends","den":"interest_rate","vi":"Funding là lãi suất của một vị thế đòn bẩy, kết toán theo mốc chứ không chảy liên tục.","goc":"repo","tin":"high","nguon":"thi-bac-ty phòng co-hoi · thi-bac-ty-runtime/bac/"},{"tu":"perpetual_funding","loai":"carries","den":"counterparty_risk","vi":"Vị thế hai chân ở hai sàn là tin hai bên thứ ba cùng lúc; một cảng ốm thì phép tính đúng vẫn mất tiền.","goc":"repo","tin":"high","nguon":"thi-bac-ty phòng cang"},{"tu":"ai_agent_execution","loai":"extends","den":"distributed_knowledge","vi":"Model gom tín hiệu rải rác mà không ai đọc hết được, đúng bài toán tri thức phân tán.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime"},{"tu":"ai_agent_execution","loai":"challenges","den":"verification","vi":"Một đề xuất của model không kiểm lại được từng bước, nên quyền phủ quyết phải nằm ở lớp luật tất định tách riêng.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết)"}],"vaiVon":[{"ma":"liquidity","ten":"Thanh khoản","khaiNiem":["salability","medium_of_exchange","price_signal","economic_calculation"],"heThong":["DEX arbitrage","Automated LP","Stablecoin arbitrage"]},{"ma":"credit","ten":"Tín dụng","khaiNiem":["capital_market","interest_rate","savings","counterparty_risk"],"heThong":["Lending Rate Arbitrage","Liquidation Hunter"]},{"ma":"time_price","ten":"Giá của thời gian/vốn","khaiNiem":["interest_rate","capital_market","economic_calculation"],"heThong":["Basis / Cash-and-Carry","Funding arbitrage","Yield Trading"]},{"ma":"price_discovery","ten":"Khám phá giá","khaiNiem":["price_signal","distributed_knowledge","economic_calculation"],"heThong":["JIT Market Making","DEX market making","Prediction markets"]},{"ma":"settlement","ten":"Quyết toán","khaiNiem":["final_settlement","verification","counterparty_risk"],"heThong":["L1/L2 settlement","Cross-chain Capital Router"]},{"ma":"risk","ten":"Rủi ro","khaiNiem":["counterparty_risk","trusted_third_party","verification"],"heThong":["Risk Engine","venue health","bridge risk","depeg detection"]},{"ma":"reserve","ten":"Dự trữ","khaiNiem":["store_of_value","counterparty_risk"],"heThong":["BTC strategic reserve","stablecoin operating reserve"]}],"nguon":{"sach":{"ten":"Tiêu chuẩn Bitcoin (The Bitcoin Standard)","tacGia":"Saifedean Ammous","nam":2018,"canhBao":"Tác giả đứng rõ trong truyền thống Kinh tế học Áo và có lập trường Bitcoin-maximalist; phải tách author_claim khỏi dữ kiện."},"ranhGioi":"Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."}};

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
