/* ═══════════════════════════════════════════════════════
   Chuyển cung — cây "Cổng Thành" ở đầu thanh bên Đài Quan Trắc.

   Cổng Thành là nút gốc, bốn cung kia là nhánh con, thu gọn
   mở rộng được. Trạng thái nhớ trong localStorage nên đi
   sang cung khác vẫn giữ nguyên — mỗi cung là một lần tải
   trang riêng, không nhớ thì lần nào cũng bung ra lại.

   Chèn NGAY SAU .brand, tức là NGOÀI #navscroll: renderNav()
   xoá sạch #navscroll mỗi lần đổi trang, nên thứ chèn vào đó
   sẽ biến mất ngay lần bấm đầu tiên.

   Vì nằm ngoài #navscroll, khối này KHÔNG co được — nó chiếm
   chỗ cố định và ép #navscroll. Đó là lý do phần nhánh con
   phải có trần chiều cao (xem .halls-tree trong halls.css):
   bung hết cỡ trên màn thấp thì #navscroll còn 0px và phần
   điều hướng của app không cách nào với tới.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var KEY = "blockchainworld.halls.open";

  var HALLS = [
    {
      href: "../kinh-thanh/",
      name: "Kinh Thành",
      note: "bản đồ 9 quốc gia L1",
      icon: '<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/>' +
            '<path d="M12 3.4c2.4 2.4 3.6 5.3 3.6 8.6s-1.2 6.2-3.6 8.6c-2.4-2.4-3.6-5.3-3.6-8.6S9.6 5.8 12 3.4Z"/>'
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
    icon: '<path d="M2.5 21h19"/><path d="M4 21V7.5h3.2M19.8 7.5H23V21"/>' +
          '<path d="M8.5 21v-8a3.5 3.5 0 0 1 7 0v8"/><path d="M7 7.5 12 3l5 4.5"/>'
  };

  function svg(paths, w) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="' +
      (w || 1.7) + '" stroke-linecap="round" stroke-linejoin="round">' + paths + '</svg>';
  }

  /* Đọc/ghi trạng thái. localStorage có thể ném lỗi khi người dùng
     chặn cookie bên thứ ba hoặc duyệt ẩn danh — hỏng chỗ này không
     được phép làm mất luôn thanh điều hướng. */
  function isOpen() {
    try { return localStorage.getItem(KEY) !== "0"; } catch (e) { return true; }
  }
  function remember(open) {
    try { localStorage.setItem(KEY, open ? "1" : "0"); } catch (e) {}
  }

  function mount() {
    var brand = document.querySelector("#nav .brand");
    if (!brand || document.querySelector(".halls-nav")) return;

    var wrap = document.createElement("div");
    wrap.className = "halls-nav";

    // ── nút gốc: Cổng Thành ──────────────────────────────
    var head = document.createElement("div");
    head.className = "halls-head";
    head.innerHTML =
      '<button class="tw" type="button" aria-expanded="true" aria-controls="hallsTree" ' +
      'aria-label="Thu gọn danh sách cung">' +
      svg('<path d="M9 5l7 7-7 7"/>', 2.2) + '</button>' +
      '<span class="ic">' + svg(GATE.icon) + '</span>' +
      '<span class="lbl"><b>' + GATE.name + '</b><i>' + HALLS.length + ' cung khác</i></span>' +
      '<a class="go-gate" href="' + GATE.href + '" title="Mở ' + GATE.name + '">' +
      svg('<path d="M5 12h13M12 5l7 7-7 7"/>', 2) + '</a>';
    wrap.appendChild(head);

    // ── nhánh con: bốn cung ──────────────────────────────
    var tree = document.createElement("div");
    tree.className = "halls-tree scroll";
    tree.id = "hallsTree";

    HALLS.forEach(function (h) {
      var a = document.createElement("a");
      a.className = "hall-link";
      a.href = h.href;
      a.title = h.name + " — " + h.note;
      a.innerHTML =
        '<span class="ic">' + svg(h.icon) + '</span>' +
        '<span class="lbl"><b>' + h.name + '</b><i>' + h.note + '</i></span>' +
        '<span class="go">' + svg('<path d="M9 5l7 7-7 7"/>', 2) + '</span>';
      tree.appendChild(a);
    });
    wrap.appendChild(tree);

    // ── đóng mở ──────────────────────────────────────────
    var tw = head.querySelector(".tw");

    /* Bung tới chiều cao nội dung thật, nhưng không quá 42% màn hình.
       Chạm trần thì .halls-tree tự cuộn (nó có class .scroll). Nhờ vậy
       #navscroll luôn còn chỗ, kể cả màn thấp hay sau này thêm cung. */
    function cap() {
      return Math.max(120, Math.round(window.innerHeight * 0.42));
    }

    function apply(open, animate) {
      wrap.classList.toggle("closed", !open);
      tw.setAttribute("aria-expanded", open ? "true" : "false");
      tw.setAttribute("aria-label", (open ? "Thu gọn" : "Mở rộng") + " danh sách cung");
      tree.style.transition = animate ? "" : "none";
      tree.style.maxHeight = open ? Math.min(tree.scrollHeight, cap()) + "px" : "0px";
    }

    function toggle() {
      var open = wrap.classList.contains("closed");
      apply(open, true);
      remember(open);
    }

    // Bấm vào thân hàng cũng đóng mở; riêng mũi tên bên phải là
    // link thật đi sang Cổng Thành nên phải để nó yên.
    head.addEventListener("click", function (ev) {
      if (ev.target.closest(".go-gate")) return;
      toggle();
    });

    brand.parentNode.insertBefore(wrap, brand.nextSibling);

    apply(isOpen(), false);
    // Bật lại transition ở khung hình sau, để lần vẽ đầu không chạy
    // hoạt cảnh đóng mở trước mắt người dùng.
    requestAnimationFrame(function () { tree.style.transition = ""; });

    // Đổi cỡ cửa sổ làm trần chiều cao lệch (nhánh con có thể xuống
    // dòng), nên đo lại khi đang mở.
    window.addEventListener("resize", function () {
      if (!wrap.classList.contains("closed")) {
        tree.style.maxHeight = Math.min(tree.scrollHeight, cap()) + "px";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
