/* ═══════════════════════════════════════════════════════
   Chuyển cung — mục "CÁC CUNG" ở đầu thanh bên Đài Quan Trắc.

   Chèn NGAY SAU .brand, tức là NGOÀI #navscroll: renderNav()
   xoá sạch #navscroll mỗi lần đổi trang, nên thứ chèn vào đó
   sẽ biến mất ngay lần bấm đầu tiên.
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
    var brand = document.querySelector("#nav .brand");
    if (!brand || document.querySelector(".halls-nav")) return;

    var wrap = document.createElement("div");
    wrap.className = "halls-nav";

    var label = document.createElement("div");
    label.className = "navlab";
    label.textContent = "Các cung";
    wrap.appendChild(label);

    HALLS.forEach(function (h) {
      var a = document.createElement("a");
      a.className = "hall-link";
      a.href = h.href;
      a.title = h.name + " — " + h.note;
      a.innerHTML =
        '<span class="ic">' + svg(h.icon) + '</span>' +
        '<span class="lbl"><b>' + h.name + '</b><i>' + h.note + '</i></span>' +
        '<span class="go"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></span>';
      wrap.appendChild(a);
    });

    var g = document.createElement("a");
    g.className = "hall-link to-gate";
    g.href = GATE.href;
    g.title = GATE.name;
    g.innerHTML = '<span class="ic">' + svg(GATE.icon) + '</span>' +
      '<span class="lbl"><b>' + GATE.name + '</b></span>';
    wrap.appendChild(g);

    brand.parentNode.insertBefore(wrap, brand.nextSibling);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
