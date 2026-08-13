/* ═══════════════════════════════════════════════════════
   Thanh bên dạng thư mục.

   "Quốc gia · Layer 1" thành một mục chính gập được — mặc định
   thu gọn, bấm mới mở. Ngang hàng với nó là các cung khác
   (Đài Quan Trắc, Đô Sát Viện) và lối về Cổng Thành.

   Thêm cung mới sau này = thêm một dòng vào HALLS.

   KHÔNG tạo phần tử mới cho #cCount, #openRank, #countryList —
   chỉ DI CHUYỂN đúng những phần tử đang có vào trong mục. app.js
   giữ tham chiếu tới chúng ngay từ lúc nạp (countryList được lưu
   vào biến ở dòng 166), nên thay thế bằng phần tử khác là hỏng
   toàn bộ danh sách quốc gia.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var KEY = "kt.nav.countries";

  var HALLS = [
    {
      href: "../dai-quan-trac/",
      name: "Đài Quan Trắc",
      note: "dòng chảy địa chính trị",
      icon: '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.2"/>' +
            '<path d="M12 12l6-3.6"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/>'
    },
    {
      href: "../do-sat-vien/",
      name: "Đô Sát Viện",
      note: "bảng xét L2 · thang tự trị",
      icon: '<path d="M3.5 20.5h17"/><path d="M4.5 16.8h7.2v3.7H4.5z"/>' +
            '<path d="M7 12.4h7.2v4.4H7z"/><path d="M9.5 8h7.2v4.4H9.5z"/>'
    },
    {
      href: "../cong-bo/",
      name: "Công Bộ",
      note: "bộ đồ nghề · giải mã",
      icon: '<path d="M14.5 5.5a4 4 0 0 0 5 5l-9.5 9.5a2.1 2.1 0 0 1-3-3z"/>' +
            '<path d="M14.5 5.5 17 3l4 4-2.5 2.5"/>'
    },
    {
      href: "../tang-thu-cac/",
      name: "Tàng Thư Các",
      note: "kho tra cứu Claude Skills",
      icon: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H10v16H5.5A1.5 1.5 0 0 1 4 18.5z"/>' +
            '<path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H14v16h4.5a1.5 1.5 0 0 0 1.5-1.5z"/>'
    }
  ];

  var GATE = {
    href: "../",
    name: "Cổng Thành",
    note: "cửa ngõ · các cung khác",
    icon: '<path d="M2.5 21h19"/><path d="M4 21V7.5h3.2M19.8 7.5H23V21"/>' +
          '<path d="M8.5 21v-8a3.5 3.5 0 0 1 7 0v8"/><path d="M7 7.5 12 3l5 4.5"/>'
  };

  function svg(paths, w) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="' +
      (w || 1.7) + '" stroke-linecap="round" stroke-linejoin="round">' + paths + '</svg>';
  }

  function el(tag, cls) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    return e;
  }

  function hallRow(h, extra) {
    var a = el("a", "nav-hall" + (extra ? " " + extra : ""));
    a.href = h.href;
    a.title = h.name + " — " + h.note;
    a.innerHTML =
      '<span class="chev-space"></span>' +
      '<span class="ic">' + svg(h.icon) + '</span>' +
      '<span class="lbl"><b>' + h.name + '</b><i>' + h.note + '</i></span>' +
      '<span class="go">' + svg('<path d="M9 5l7 7-7 7"/>', 2) + '</span>';
    return a;
  }

  function mount() {
    var scroll = document.querySelector(".nav-scroll");
    if (!scroll || scroll.querySelector(".nav-group")) return;

    var label = scroll.querySelector(".nav-label");
    var count = document.getElementById("cCount");
    var rank = document.getElementById("openRank");
    var list = document.getElementById("countryList");
    if (!label || !count || !rank || !list) return;

    /* ── mục chính gập được ── */
    var group = el("div", "nav-group");

    var head = el("button", "nav-group-head");
    head.type = "button";
    head.setAttribute("aria-expanded", "false");

    var chev = el("span", "chev");
    chev.innerHTML = svg('<path d="M9 5l7 7-7 7"/>', 2.2);
    var title = el("span", "t");
    title.textContent = "Quốc gia · Layer 1";

    head.appendChild(chev);
    head.appendChild(title);
    head.appendChild(count);            // di chuyển, không tạo mới
    group.appendChild(head);

    var body = el("div", "nav-group-body");
    body.appendChild(rank);             // di chuyển
    body.appendChild(list);             // di chuyển
    group.appendChild(body);

    scroll.insertBefore(group, label);
    label.remove();

    /* mặc định thu gọn; nhớ lựa chọn của người dùng */
    var open = false;
    try { open = localStorage.getItem(KEY) === "1"; } catch (e) {}
    group.dataset.open = open ? "1" : "0";
    head.setAttribute("aria-expanded", String(open));

    head.addEventListener("click", function () {
      var next = group.dataset.open !== "1";
      group.dataset.open = next ? "1" : "0";
      head.setAttribute("aria-expanded", String(next));
      try { localStorage.setItem(KEY, next ? "1" : "0"); } catch (e) {}
    });

    /* ── các cung ngang hàng ── */
    var after = group;
    HALLS.forEach(function (h) {
      var row = hallRow(h);
      after.parentNode.insertBefore(row, after.nextSibling);
      after = row;
    });
    var gate = hallRow(GATE, "to-gate");
    after.parentNode.insertBefore(gate, after.nextSibling);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
