/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.
   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:
       node knowledge-os/sinh.mjs tang-thu-cac

   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,
   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).

   BOT GHI mỗi 24 giờ (node `tri-thuc`) — ĐỪNG SỬA TAY file này,
   sửa dữ liệu nguồn rồi sinh lại. Sửa thẳng vào đây thì đúng cho
   tới lượt bot kế tiếp, rồi biến mất không dấu vết.
   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng
   CACHE_VERSION khi file này đổi. */
window.TRI_THUC = {"sinhLuc":"2026-09-05T05:13:51.908Z","goi":"knowledge-os","cung":"tang-thu-cac","vai":"Kho kỹ năng","y":"Skill là năng lực thực thi; Knowledge OS là tri thức miền.","phong":[{"ma":"tong-quan","ten":"Lưới nhóm việc","y":"Kỹ năng xếp theo VIỆC chứ không theo tên tác giả. Đó là cách gom tri thức nằm rải thành thứ tra được.","khaiNiem":["distributed_knowledge"]},{"ma":"danh-muc","ten":"Danh mục skill","y":"Mỗi hồ sơ skill nói rõ nó đến từ đâu và làm gì. Không có dòng nguồn thì một skill là một hộp đen mình phải tin.","khaiNiem":["distributed_knowledge","verification"]},{"ma":"xep-hang","ten":"Xếp hạng kho","y":"Số sao đo mức được dùng lại, không đo chất lượng. Hai thứ đó tương quan nhưng không bằng nhau, và trộn chúng là đọc sai bảng.","khaiNiem":["network_effect","verification"]},{"ma":"xu-huong","ten":"Xu hướng","y":"Sao tăng nhanh là hiệu ứng mạng đang chạy. GitHub không cho biết số sao quá khứ, nên cung tự ghi mốc rồi lấy hiệu — tự dựng lấy đường kiểm khi nguồn không cấp.","khaiNiem":["network_effect","verification"]},{"ma":"lich-su","ten":"Lịch sử cập nhật","y":"Chỉ ghi lần CÓ thay đổi thật. Nhật ký ghi cả lần không đổi thì thành rác, và rác che mất đúng dòng đáng xem.","khaiNiem":["verification"]}],"khaiNiem":{"distributed_knowledge":{"en":"Distributed knowledge","vi":"Tri thức phân tán","loai":"information","nghia":"Tri thức kinh tế nằm rải trong nhiều người/ngành và không thể tập trung hoàn toàn vào một nhà hoạch định.","goc":"sach","chuong":[6],"trang":[115,117]},"verification":{"en":"Verification","vi":"Xác minh","loai":"trust_model","nghia":"Thay việc tin một bên bằng quy tắc/bằng chứng mà nhiều nút có thể tự kiểm tra.","goc":"sach","chuong":[8],"trang":[146,147]},"network_effect":{"en":"Network effect","vi":"Hiệu ứng mạng","loai":"network_property","nghia":"Lợi ích dùng một tiêu chuẩn trao đổi tăng khi số người cùng dùng tăng.","goc":"sach","chuong":[1],"trang":[16]},"ai_agent_execution":{"en":"AI agent execution","vi":"Tác tử AI ra quyết định","loai":"mechanism","nghia":"Model đọc dữ liệu thị trường rồi đề xuất hành động, còn quyền phủ quyết nằm ở một lớp luật tất định tách riêng.","goc":"repo","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết) · thai-boc-tu toa t12"},"stablecoin_settlement":{"en":"Stablecoin settlement","vi":"Quyết toán bằng stablecoin","loai":"payment_function","nghia":"Khối lượng chuyển giá trị chạy bằng token neo đô la trên chuỗi công khai, thay vì bằng đồng tiền gốc của chuỗi.","goc":"repo","nguon":"ho-bo/assets/js/v/dong-tien.js · thai-boc-tu toa t04"}},"quanHe":[],"lop2026":[{"tu":"ai_agent_execution","loai":"extends","den":"distributed_knowledge","vi":"Model gom tín hiệu rải rác mà không ai đọc hết được, đúng bài toán tri thức phân tán.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime"},{"tu":"ai_agent_execution","loai":"challenges","den":"verification","vi":"Một đề xuất của model không kiểm lại được từng bước, nên quyền phủ quyết phải nằm ở lớp luật tất định tách riêng.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết)"},{"tu":"stablecoin_settlement","loai":"supports","den":"network_effect","vi":"Sách 2018 dùng hiệu ứng mạng để giải thích vì sao tiền HỘI TỤ về một chuẩn: càng nhiều người nhận thì càng đáng nhận, nên thị trường dồn về một thứ chứ không chia đều. Tám năm sau, chỗ kiểm được luận điểm ấy rõ nhất không phải giá coin mà là số dư stablecoin nằm ở đâu — vì stablecoin là thứ trên chuỗi được dùng để TRẢ NHAU nhiều nhất, và nó chạy được trên mọi chuỗi như nhau. Bảng Kinh Thành ngày 05/09/2026, cộng chín chuỗi nó theo dõi: stablecoin lưu hành 180,9 tỉ đô, riêng Ethereum giữ 147,3 tỉ — 81,4%. Tài sản khoá cũng vậy: 62,5 tỉ tổng, Ethereum 49,3 tỉ — 78,8%. Đến đây thì chỉ mới là 'chuỗi lớn thì lớn'. Chỗ đáng đọc nằm ở cột thứ ba trong CÙNG một bảng: đếm giao thức thì Ethereum chỉ có 1.855 trên 5.046, tức 36,8% — gần hai phần ba số phần mềm chạy ở NƠI KHÁC. Nhà phát triển đã toả ra, tiền thì không. Đó là bằng chứng mạnh cho hiệu ứng mạng hơn hẳn con số 81% đứng một mình, vì nó loại được lời giải thích cạnh tranh: nếu vốn dồn về một chỗ chỉ vì chỗ ấy có sẵn công cụ, thì 563 giao thức của Avalanche đã phải kéo về nhiều hơn 485 triệu đô. Cái kéo vốn về không phải mã nguồn — mã nguồn rẻ và chép được — mà là chỗ NGƯỜI KHÁC đang để tiền. Một quan sát ngược chiều đáng ghi vì nó tinh chỉnh chứ không bác: TON giữ 766 triệu đô stablecoin trên 50,8 triệu đô tài sản khoá, tỉ lệ 15 lần, trong khi Ethereum chỉ 3,0 lần. Nghĩa là hiệu ứng mạng của chức năng TRẢ TIỀN bám theo số người dùng sẵn có và đi trước, còn thị trường vốn tới sau — hai chức năng của sách hội tụ ở hai nơi khác nhau và theo hai nhịp khác nhau. Đây là supports chứ không phải extends: cơ chế sách mô tả đang chạy đúng như mô tả. Thứ sách không nói được, và cũng không thể trách, là hiệu ứng mạng ấy hoá ra bám vào ĐƠN VỊ ĐO (đô la) và NƠI QUYẾT TOÁN, chứ không bám vào độ cứng của đồng tiền — xem quan hệ usd_numeraire → unit_of_account. Giới hạn phải nói rõ: chín chuỗi này là tập Kinh Thành chọn theo dõi chứ không phải toàn thị trường, cả ba cột đều lấy từ một nguồn duy nhất là DefiLlama, và số dư nằm trên một chuỗi không đo được nó luân chuyển bao nhiêu vòng.","goc":"repo","tin":"high","nguon":"kinh-thanh/assets/js/data/live.js (khối chains: tvl · stab · proto) · ho-bo/assets/js/v/dong-tien.js"}],"vaiVon":[],"nguon":{"sach":{"ten":"Tiêu chuẩn Bitcoin (The Bitcoin Standard)","tacGia":"Saifedean Ammous","nam":2018,"canhBao":"Tác giả đứng rõ trong truyền thống Kinh tế học Áo và có lập trường Bitcoin-maximalist; phải tách author_claim khỏi dữ kiện."},"ranhGioi":"Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."}};

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
