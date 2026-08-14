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
      href: "../tao-bien-xu/",
      name: "Tạo Biện Xứ",
      note: "công xưởng AI",
      icon: '<path d="M3 21h18M5 21V11l4-3v13M13 21V6l6-3v18"/><path d="M8 15h.01M16 12h.01"/>'
    },
    {
      href: "../cong-bo/",
      name: "Công Bộ",
      note: "bộ đồ nghề",
      icon: '<path d="M14.5 5.5a4 4 0 0 0 5 5l-9.5 9.5a2.1 2.1 0 0 1-3-3z"/><path d="M14.5 5.5 17 3l4 4-2.5 2.5"/>'
    },
    {
      href: "../do-sat-vien/",
      name: "Đô Sát Viện",
      note: "bảng xét Layer 2",
      icon: '<path d="M3.5 20.5h17"/><path d="M4.5 16.8h7.2v3.7H4.5z"/><path d="M7 12.4h7.2v4.4H7z"/><path d="M9.5 8h7.2v4.4H9.5z"/>'
    },
    {
      href: "../tang-thu-cac/",
      name: "Tàng Thư Các",
      note: "kho Claude Skills",
      icon: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/><path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>'
    }
  ];

  var GATE = {
    href: "../",
    name: "Cổng Thành",
    note: "cửa ngõ",
    icon: '<path d="M2.5 21h19"/><path d="M4 21V7.5h3.2M19.8 7.5H23V21"/><path d="M8.5 21v-8a3.5 3.5 0 0 1 7 0v8"/><path d="M7 7.5 12 3l5 4.5"/>'
  };

  function svg(paths) {
    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' + paths + "</svg>";
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

    var lab = document.createElement("div");
    lab.className = "blab";
    lab.textContent = "Các cung";
    host.appendChild(lab);

    HALLS.forEach(function (h) { host.appendChild(dong(h)); });
    host.appendChild(dong(GATE));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
