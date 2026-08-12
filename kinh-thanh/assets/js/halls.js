/* ═══════════════════════════════════════════════════════
   Chuyển cung — mục "CÁC CUNG" ở đầu thanh bên.

   Để đi thẳng từ Kinh Thành sang Đài Quan Trắc mà không phải
   quay ra Cổng Thành. Tự chèn vào DOM, không cần móc nào trong
   app.js — bỏ file này đi thì thanh bên về như cũ.

   Chèn vào ĐẦU .nav-scroll chứ không phải vào #countryList hay
   #secList: hai chỗ đó bị app.js xoá sạch mỗi lần đổi quốc gia,
   nên thứ chèn vào sẽ biến mất ngay lần bấm đầu tiên.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var HALLS = [
    {
      href: "../dai-quan-trac/",
      name: "Đài Quan Trắc",
      note: "dòng chảy địa chính trị",
      icon: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.2"/>' +
            '<path d="M12 12l6-3.6"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/>'
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
    var scroll = document.querySelector(".nav-scroll");
    if (!scroll || document.querySelector(".halls-nav")) return;

    var wrap = document.createElement("div");
    wrap.className = "halls-nav";

    var label = document.createElement("div");
    label.className = "nav-label";
    label.textContent = "Các cung";
    wrap.appendChild(label);

    HALLS.forEach(function (h) {
      var a = document.createElement("a");
      a.className = "hall-link";
      a.href = h.href;
      a.title = h.name + " — " + h.note;
      a.innerHTML =
        '<span class="mono">' + svg(h.icon) + '</span>' +
        '<span class="lbl"><b>' + h.name + '</b><i>' + h.note + '</i></span>' +
        '<span class="go"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></span>';
      wrap.appendChild(a);
    });

    var g = document.createElement("a");
    g.className = "hall-link to-gate";
    g.href = GATE.href;
    g.title = GATE.name;
    g.innerHTML = '<span class="mono">' + svg(GATE.icon) + '</span>' +
      '<span class="lbl"><b>' + GATE.name + '</b></span>';
    wrap.appendChild(g);

    scroll.insertBefore(wrap, scroll.firstChild);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
