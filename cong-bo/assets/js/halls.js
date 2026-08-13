/* ═══════════════════════════════════════════════════════
   Chuyển cung — mục "CÁC CUNG" trong thanh bên.

   Công Bộ có sidebar riêng nên lối sang cung khác nằm luôn trong
   đó, cùng kiểu với mục "Đồ nghề" ở trên. Cùng dữ liệu như ba cung
   kia, khác cách bày.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var HALLS = [
    {
      href: "../kinh-thanh/",
      name: "Kinh Thành",
      note: "9 quốc gia L1",
      icon: '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/>' +
            '<path d="M12 3.4c2.4 2.4 3.6 5.3 3.6 8.6s-1.2 6.2-3.6 8.6c-2.4-2.4-3.6-5.3-3.6-8.6S9.6 5.8 12 3.4Z"/>'
    },
    {
      href: "../dai-quan-trac/",
      name: "Đài Quan Trắc",
      note: "địa chính trị",
      icon: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.2"/>' +
            '<path d="M12 12l6-3.6"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/>'
    },
    {
      href: "../do-sat-vien/",
      name: "Đô Sát Viện",
      note: "bảng xét Layer 2",
      icon: '<path d="M3.5 20.5h17"/><path d="M4.5 16.8h7.2v3.7H4.5z"/>' +
            '<path d="M7 12.4h7.2v4.4H7z"/><path d="M9.5 8h7.2v4.4H9.5z"/>'
    }
  ];

  var GATE = {
    href: "../",
    name: "Cổng Thành",
    note: "cửa ngõ",
    icon: '<path d="M2.5 21h19"/><path d="M4 21V7.5h3.2M19.8 7.5H23V21"/>' +
          '<path d="M8.5 21v-8a3.5 3.5 0 0 1 7 0v8"/><path d="M7 7.5 12 3l5 4.5"/>'
  };

  function svg(paths) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" ' +
      'stroke-linecap="round" stroke-linejoin="round">' + paths + "</svg>";
  }

  function dong(h) {
    var a = document.createElement("a");
    a.className = "bmuc";
    a.href = h.href;
    a.title = h.name + " — " + h.note;
    a.innerHTML = '<span class="bic">' + svg(h.icon) + "</span><span>" + h.name + "</span>";
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
