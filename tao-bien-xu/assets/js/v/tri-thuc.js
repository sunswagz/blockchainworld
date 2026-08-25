/* TỰ SINH bởi knowledge-os/sinh.mjs — đừng sửa tay.
   Nguồn: knowledge-os/data/. Sửa dữ liệu ở đó rồi sinh lại:
       node knowledge-os/sinh.mjs tao-bien-xu

   Mang CẢ dữ liệu lẫn phần vẽ — khuôn HTML chung cho mọi cung,
   viết một lần trong sinh.mjs. Cung gọi TRI_THUC.ve(maPhong).

   SINH TAY, PHẢI COMMIT — không workflow nào chạy lệnh này.
   Nằm ở assets/js/v/ nên đi nhánh MẠNG-TRƯỚC: KHÔNG cần nâng
   CACHE_VERSION khi file này đổi. */
window.TRI_THUC = {"sinhLuc":"2026-08-25T17:11:47.928Z","goi":"knowledge-os","cung":"tao-bien-xu","vai":"Công xưởng AI","y":"Knowledge OS cấp context chuẩn hóa; model suy luận trên dữ liệu có provenance.","phong":[{"ma":"van-hanh","ten":"Bảng vận hành","y":"Nhà máy tự nói mình chạy được bao nhiêu lượt là cách duy nhất để kiểm nó — một dây chuyền chết trong im lặng thì không lỗi nào báo.","khaiNiem":["verification","economic_calculation"]},{"ma":"so-do","ten":"Sơ đồ nhà máy","y":"Mười tám máy là tư liệu sản xuất của xưởng: chúng không tự tạo giá trị, chúng biến công sức thành thứ dùng lại được.","khaiNiem":["distributed_knowledge","capital_goods"]},{"ma":"to","ten":"Tổ thợ & kỹ năng","y":"Kỹ năng là tri thức đã đóng gói để dùng lại. Đó là chỗ năng suất tăng mà không cần thêm người.","khaiNiem":["distributed_knowledge","productivity"]},{"ma":"duyet","ten":"Bốn mức duyệt","y":"Mức duyệt là câu trả lời cho câu tin máy tới đâu. Bốn mức, vì tin hết và không tin gì đều là hai cách hỏng.","khaiNiem":["verification","trusted_third_party"]}],"khaiNiem":{"verification":{"en":"Verification","vi":"Xác minh","loai":"trust_model","nghia":"Thay việc tin một bên bằng quy tắc/bằng chứng mà nhiều nút có thể tự kiểm tra.","goc":"sach","chuong":[8],"trang":[146,147]},"distributed_knowledge":{"en":"Distributed knowledge","vi":"Tri thức phân tán","loai":"information","nghia":"Tri thức kinh tế nằm rải trong nhiều người/ngành và không thể tập trung hoàn toàn vào một nhà hoạch định.","goc":"sach","chuong":[6],"trang":[115,117]},"economic_calculation":{"en":"Economic calculation","vi":"Tính toán kinh tế","loai":"mechanism","nghia":"Dùng giá và đơn vị tính toán để so sánh chi phí, doanh thu, lợi nhuận và lựa chọn phương án.","goc":"sach","chuong":[1,6,7],"trang":[16,114,118,140]},"capital_goods":{"en":"Capital goods","vi":"Tư liệu sản xuất","loai":"capital_asset","nghia":"Công cụ/hàng hóa dùng để tạo hàng hóa tương lai thay vì tiêu dùng ngay.","goc":"sach","chuong":[1,5,6],"trang":[17,84,85,118]},"productivity":{"en":"Productivity","vi":"Năng suất","loai":"economic_outcome","nghia":"Giá trị/sản lượng tạo ra trên một đơn vị lao động; sách nối tăng năng suất với tích lũy vốn.","goc":"sach","chuong":[5],"trang":[85,88]},"trusted_third_party":{"en":"Trusted third party","vi":"Bên thứ ba đáng tin cậy","loai":"architecture","nghia":"Trung gian mà hai bên phải tin để ghi sổ, xử lý hoặc quyết toán giao dịch.","goc":"sach","chuong":[8,10],"trang":[144,229,231]},"ai_agent_execution":{"en":"AI agent execution","vi":"Tác tử AI ra quyết định","loai":"mechanism","nghia":"Model đọc dữ liệu thị trường rồi đề xuất hành động, còn quyền phủ quyết nằm ở một lớp luật tất định tách riêng.","goc":"repo","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết) · thai-boc-tu toa t12"}},"quanHe":[{"tu":"capital_goods","loai":"increase","den":"productivity","vi":"Ví dụ cần câu/thuyền minh họa công cụ làm tăng năng suất.","goc":"sach","tin":"high","chuong":[5],"trang":[85,86]}],"lop2026":[{"tu":"ai_agent_execution","loai":"extends","den":"distributed_knowledge","vi":"Model gom tín hiệu rải rác mà không ai đọc hết được, đúng bài toán tri thức phân tán.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime"},{"tu":"ai_agent_execution","loai":"challenges","den":"verification","vi":"Một đề xuất của model không kiểm lại được từng bước, nên quyền phủ quyết phải nằm ở lớp luật tất định tách riêng.","goc":"repo","tin":"medium","nguon":"tu-cam-thanh-runtime (Risk Engine phủ quyết)"}],"vaiVon":[{"ma":"price_discovery","ten":"Khám phá giá","khaiNiem":["distributed_knowledge","economic_calculation"],"heThong":["JIT Market Making","DEX market making","Prediction markets"]},{"ma":"risk","ten":"Rủi ro","khaiNiem":["trusted_third_party","verification"],"heThong":["Risk Engine","venue health","bridge risk","depeg detection"]}],"nguon":{"sach":{"ten":"Tiêu chuẩn Bitcoin (The Bitcoin Standard)","tacGia":"Saifedean Ammous","nam":2018,"canhBao":"Tác giả đứng rõ trong truyền thống Kinh tế học Áo và có lập trường Bitcoin-maximalist; phải tách author_claim khỏi dữ kiện."},"ranhGioi":"Nhãn `goc` trên mỗi mục: sach = tác giả mô tả · tacGia = lập trường riêng của tác giả · phanTich = SUNSWaGz suy ra · repo = đo được từ repo/runtime năm 2026. Ánh xạ khái niệm sang toa/phòng của cung là phân tích, sách không nói gì về repo này."}};

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
