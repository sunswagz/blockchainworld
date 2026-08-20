/* ═══════════════════════════════════════════════════════
   Chuyển cung — mục "CÁC CUNG" trong thanh bên.

   TỰ SINH bởi scripts/build-halls.mjs — đừng sửa tay.
   Sửa danh sách ở scripts/cung.mjs rồi chạy `npm run halls`.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var HALLS = [
    {
      href: "../kinh-thanh/",
      name: "Kinh Thành",
      note: "9 quốc gia L1",
      icon: '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/><path d="M12 3.4c2.4 2.4 3.6 5.3 3.6 8.6s-1.2 6.2-3.6 8.6c-2.4-2.4-3.6-5.3-3.6-8.6S9.6 5.8 12 3.4Z"/>'
    },
    {
      href: "../hoang-thanh/",
      name: "Hoàng Thành",
      note: "15 nền văn hoá",
      icon: '<path d="M3 21h18M5 21V10l7-5.5L19 10v11"/><path d="M9.5 21v-5.5h5V21"/>'
    },
    {
      href: "../tu-cam-thanh/",
      name: "Tử Cấm Thành",
      note: "lõi giao dịch",
      icon: '<path d="M2.5 21h19"/><path d="M4.5 21V9.5h15V21"/><path d="M3 9.5 12 4l9 5.5"/><path d="M10.2 21v-5a1.8 1.8 0 0 1 3.6 0v5"/><path d="M7 21v-3.2a1.2 1.2 0 0 1 2.4 0V21"/><path d="M14.6 21v-3.2a1.2 1.2 0 0 1 2.4 0V21"/>'
    },
    {
      href: "../cong-bo/",
      name: "Công Bộ",
      note: "bộ đồ nghề",
      icon: '<path d="M14.5 5.5a4 4 0 0 0 5 5l-9.5 9.5a2.1 2.1 0 0 1-3-3z"/><path d="M14.5 5.5 17 3l4 4-2.5 2.5"/>'
    },
    {
      href: "../ho-bo/",
      name: "Hộ Bộ",
      note: "dòng tiền blockchain",
      icon: '<ellipse cx="12" cy="6" rx="7.5" ry="2.8"/><path d="M4.5 6v4.4c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8V6"/><path d="M4.5 10.4v4.4c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8v-4.4"/><path d="M4.5 14.8v3.2c0 1.55 3.36 2.8 7.5 2.8s7.5-1.25 7.5-2.8v-3.2"/>'
    },
    {
      href: "../do-sat-vien/",
      name: "Đô Sát Viện",
      note: "bảng xét Layer 2",
      icon: '<path d="M3.5 20.5h17"/><path d="M4.5 16.8h7.2v3.7H4.5z"/><path d="M7 12.4h7.2v4.4H7z"/><path d="M9.5 8h7.2v4.4H9.5z"/>'
    },
    {
      href: "../dai-quan-trac/",
      name: "Đài Quan Trắc",
      note: "địa chính trị",
      icon: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.2"/><path d="M12 12l6-3.6"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/>'
    },
    {
      href: "../tang-thu-cac/",
      name: "Tàng Thư Các",
      note: "kho Claude Skills",
      icon: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>'
    },
    {
      href: "../kham-thien-giam/",
      name: "Khâm Thiên Giám",
      note: "đài chiêm thị trường",
      icon: '<circle cx="12" cy="12" r="8.6"/><path d="M12 3.4v17.2M3.4 12h17.2"/><circle cx="12" cy="12" r="3.1"/>'
    },
    {
      href: "../thai-boc-tu/",
      name: "Thái Bộc Tự",
      note: "đoàn tàu & khớp nối",
      icon: '<path d="M4 17V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10"/><path d="M2 20h20"/><path d="M8 5V3h8v2"/><circle cx="8" cy="17" r="1.4"/><circle cx="16" cy="17" r="1.4"/>'
    }
  ];

  var GATE = {
    href: "../",
    name: "Cổng Thành",
    note: "cửa ngõ",
    icon: '<path d="M2.5 21h19"/><path d="M4 21V7.5h3.2M19.8 7.5H23V21"/><path d="M8.5 21v-8a3.5 3.5 0 0 1 7 0v8"/><path d="M7 7.5 12 3l5 4.5"/>'
  };

  /* Nhớ đóng/mở. MẶC ĐỊNH LÀ ĐÓNG: thanh bên mỗi cung còn mục riêng
     của nó, danh sách cung bung sẵn thì đẩy phần đó xuống dưới màn.
     Nên chỉ mở khi người dùng đã tự mở — tức là khoá phải bằng "1",
     thiếu khoá là đóng.
     localStorage ném lỗi khi duyệt ẩn danh hoặc chặn cookie bên thứ
     ba; hỏng chỗ này không được phép làm mất luôn lối chuyển cung. */
  var KEY = "blockchainworld.cung.mo";
  function daMo() {
    try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; }
  }
  function nho(mo) {
    try { localStorage.setItem(KEY, mo ? "1" : "0"); } catch (e) {}
  }

  function svg(paths, px) {
    var s = px || 16;
    return '<svg width="' + s + '" height="' + s + '" viewBox="0 0 24 24" fill="none" ' +
      'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" ' +
      'stroke-linejoin="round">' + paths + "</svg>";
  }
  var MUI = '<path d="M9 5l7 7-7 7"/>';

  /* CSS đi kèm ngay trong file này, KHÔNG nằm ở halls.css của từng
     cung. Lý do: bảy cung đặt tên biến màu khác hẳn nhau (--ink-3 ở
     Tàng Thư Các, --dim ở Đài Quan Trắc…), nên một khối CSS dùng
     chung không thể gọi tên biến nào cả. Ở đây chỉ dùng currentColor,
     opacity và một màu xám trung tính — tự hợp với cả nền sáng lẫn
     nền tối. Phần màu sắc của từng hàng vẫn do .bmuc của cung lo. */
  var CSS =
    '.cung-hang{display:flex;align-items:center;gap:2px}' +
    '.cung-hang .cung-goc{flex:1;min-width:0;cursor:pointer}' +
    '.cung-mui{display:inline-flex;align-items:center;flex:0 0 auto;opacity:.5;' +
      'transition:transform .18s ease}' +
    '.cung-cay[data-mo="1"] .cung-mui{transform:rotate(90deg)}' +
    '.cung-dem{margin-left:auto;font-size:10.5px;opacity:.55;white-space:nowrap;' +
      'font-variant-numeric:tabular-nums}' +
    '.cung-vao{display:inline-flex;align-items:center;padding:6px;border-radius:6px;opacity:.4}' +
    '.cung-vao:hover{opacity:1;text-decoration:none}' +
    '.cung-nhanh{overflow:hidden;max-height:0;transition:max-height .22s ease}' +
    '.cung-vien{margin:2px 0 2px 16px;padding-left:7px;' +
      'border-left:1px solid rgba(128,128,128,.3)}' +
    '@media (prefers-reduced-motion:reduce){.cung-mui,.cung-nhanh{transition:none}}';

  function nhungCss() {
    if (document.getElementById("cungCss")) return;
    var st = document.createElement("style");
    st.id = "cungCss";
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  function dong(h) {
    var a = document.createElement("a");
    a.className = "bmuc";
    a.href = h.href;
    a.title = h.name + " — " + h.note;
    a.innerHTML = '<span class="bic">' + svg(h.icon) + '</span><span class="bten">' + h.name + "</span>";
    return a;
  }

  function mount() {
    var host = document.getElementById("cungNav");
    if (!host || host.firstChild) return;
    nhungCss();

    var lab = document.createElement("div");
    lab.className = "blab";
    lab.textContent = "Các cung";
    host.appendChild(lab);

    var cay = document.createElement("div");
    cay.className = "cung-cay";

    /* Nút bấm và link là HAI thẻ cạnh nhau, không lồng nhau: <a> nằm
       trong <button> là HTML không hợp lệ và trình duyệt sẽ tự tháo
       ra. Nút lo đóng/mở, mũi tên bên phải mới thật sự sang Cổng
       Thành. Dùng <button> thật nên có bàn phím và ARIA miễn phí. */
    var hang = document.createElement("div");
    hang.className = "cung-hang";
    hang.innerHTML =
      '<button class="bmuc cung-goc" type="button" aria-expanded="false" ' +
        'aria-controls="cungNhanh">' +
        '<span class="cung-mui">' + svg(MUI, 13) + "</span>" +
        '<span class="bic">' + svg(GATE.icon) + "</span>" +
        '<span class="bten">' + GATE.name + "</span>" +
        '<span class="cung-dem">' + HALLS.length + " cung</span>" +
      "</button>" +
      '<a class="cung-vao" href="' + GATE.href + '" title="Mở ' + GATE.name + '">' +
        svg('<path d="M5 12h13M12 5l7 7-7 7"/>', 15) + "</a>";
    cay.appendChild(hang);

    var nhanh = document.createElement("div");
    nhanh.className = "cung-nhanh";
    nhanh.id = "cungNhanh";
    var vien = document.createElement("div");
    vien.className = "cung-vien";
    HALLS.forEach(function (h) { vien.appendChild(dong(h)); });
    nhanh.appendChild(vien);
    cay.appendChild(nhanh);

    host.appendChild(cay);

    var nut = hang.querySelector(".cung-goc");

    function apply(mo, chay) {
      cay.setAttribute("data-mo", mo ? "1" : "0");
      nut.setAttribute("aria-expanded", mo ? "true" : "false");
      nut.title = (mo ? "Thu gọn" : "Mở rộng") + " danh sách cung";
      nhanh.style.transition = chay ? "" : "none";
      nhanh.style.maxHeight = mo ? nhanh.scrollHeight + "px" : "0px";
    }

    nut.addEventListener("click", function () {
      var mo = cay.getAttribute("data-mo") !== "1";
      apply(mo, true);
      nho(mo);
    });

    apply(daMo(), false);
    /* Bật lại hoạt cảnh ở khung hình sau, để lần vẽ đầu không chạy
       animation đóng/mở ngay trước mắt người dùng. */
    requestAnimationFrame(function () { nhanh.style.transition = ""; });

    /* Đổi cỡ cửa sổ có thể làm tên cung xuống dòng, khiến chiều cao
       thật khác lúc đo. Đo lại khi đang mở, không thì phần cuối bị
       cắt mất mà không có gì báo. */
    window.addEventListener("resize", function () {
      if (cay.getAttribute("data-mo") === "1") {
        nhanh.style.maxHeight = nhanh.scrollHeight + "px";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
