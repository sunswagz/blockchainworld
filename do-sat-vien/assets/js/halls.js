/* ═══════════════════════════════════════════════════════
   Chuyển cung — dải ngang ngay dưới thanh đầu trang.

   Đô Sát Viện không có thanh bên như hai cung kia, nên ở đây
   dùng dải ngang thay vì mục "Các cung" trong nav. Cùng dữ
   liệu, khác cách bày.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var HALLS = [
    {
      href: "../kinh-thanh/",
      name: "Kinh Thành",
      note: "bản đồ 9 quốc gia L1",
      icon: '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/>' +
            '<path d="M12 3.4c2.4 2.4 3.6 5.3 3.6 8.6s-1.2 6.2-3.6 8.6c-2.4-2.4-3.6-5.3-3.6-8.6S9.6 5.8 12 3.4Z"/>'
    },
    {
      href: "../dai-quan-trac/",
      name: "Đài Quan Trắc",
      note: "địa chính trị · kịch bản",
      icon: '<path d="M12 3.5v4"/><path d="M5.5 20.5 12 7.5l6.5 13"/>' +
            '<path d="M8.2 15.5h7.6"/><path d="M3 20.5h18"/>'
    }
  ];

  var GATE = {
    href: "../",
    name: "Cổng Thành",
    icon: '<path d="M2.5 21h19"/><path d="M4 21V7.5h3.2M19.8 7.5H23V21"/>' +
          '<path d="M8.5 21v-8a3.5 3.5 0 0 1 7 0v8"/><path d="M7 7.5 12 3l5 4.5"/>'
  };

  function svg(paths) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" ' +
      'stroke-linecap="round" stroke-linejoin="round">' + paths + '</svg>';
  }

  function mount() {
    var host = document.getElementById("cungStrip");
    if (!host || host.firstChild) return;

    var strip = document.createElement("nav");
    strip.className = "cung-strip";
    strip.setAttribute("aria-label", "Chuyển cung");

    var g = document.createElement("a");
    g.className = "cung to-gate";
    g.href = GATE.href;
    g.innerHTML = '<span class="ic">' + svg(GATE.icon) + '</span>' +
      '<span class="lbl"><b>' + GATE.name + '</b></span>';
    strip.appendChild(g);

    var here = document.createElement("span");
    here.className = "cung dang-o";
    here.innerHTML = '<span class="ic">' +
      svg('<path d="M3.5 20.5h17"/><path d="M6 20.5V9.5M18 20.5V9.5M10 20.5v-6h4v6"/>' +
          '<path d="M4 9.5 12 3.5l8 6"/>') + '</span>' +
      '<span class="lbl"><b>Đô Sát Viện</b><i>đang ở đây</i></span>';
    strip.appendChild(here);

    HALLS.forEach(function (h) {
      var a = document.createElement("a");
      a.className = "cung";
      a.href = h.href;
      a.title = h.name + " — " + h.note;
      a.innerHTML =
        '<span class="ic">' + svg(h.icon) + '</span>' +
        '<span class="lbl"><b>' + h.name + '</b><i>' + h.note + '</i></span>';
      strip.appendChild(a);
    });

    host.appendChild(strip);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
