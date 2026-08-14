/* ═══════════════════════════════════════════════════════
   Sinh `assets/js/halls.js` cho MỌI cung từ scripts/cung.mjs.

   Chạy: npm run halls

   Mỗi cung cần một danh sách lối sang các cung khác. Danh sách đó
   là cùng một sự thật chép ra N bản, và thêm một cung là sửa tay
   N−1 file — việc lặp lại thuần tuý, tức là việc máy nên làm.

   File sinh ra vẫn là file thường, commit như mọi file khác: mỗi
   cung phải tự chứa đủ để chạy offline, không nạp chung từ gốc.
   Chỉ khác là không sửa tay nữa.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CUNG, CONG_THANH } from "./cung.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

/* Icon chứa nháy KÉP (thuộc tính SVG) nên phải bọc bằng nháy ĐƠN và
   để nguyên bên trong. Đừng dùng JSON.stringify rồi đổi nháy: nó đổi
   luôn cả nháy của thuộc tính, ra `cx='12'` và file hỏng cú pháp.
   Vòng kiểm bên dưới chặn trường hợp icon lỡ có nháy đơn. */
function nhay(s) { return "'" + s + "'"; }

function khoiMuc(c, thut) {
  const t = " ".repeat(thut);
  return t + "{\n" +
    t + '  href: "../' + c.ma + '/",\n' +
    t + '  name: "' + c.ten + '",\n' +
    t + '  note: "' + c.note + '",\n' +
    t + "  icon: " + nhay(c.icon) + "\n" +
    t + "}";
}

/* icon là chuỗi có dấu nháy kép bên trong (thuộc tính SVG), nên bọc
   bằng nháy đơn. JSON.stringify rồi đổi nháy là cách gọn nhất mà vẫn
   escape đúng — nhưng phải chắc trong icon không có nháy đơn. */
for (const c of [...CUNG, CONG_THANH]) {
  if (c.icon.indexOf("'") !== -1) {
    console.error("✗ icon của " + (c.ma || "cổng thành") + " có dấu nháy đơn — đổi sang nháy kép");
    process.exit(1);
  }
}

function dungFile(cung) {
  const khac = CUNG.filter((c) => c.ma !== cung.ma);
  return `/* ═══════════════════════════════════════════════════════
   Chuyển cung — mục "CÁC CUNG" trong thanh bên.

   TỰ SINH bởi scripts/build-halls.mjs — đừng sửa tay.
   Sửa danh sách ở scripts/cung.mjs rồi chạy \`npm run halls\`.
   ═══════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var HALLS = [
${khac.map((c) => khoiMuc(c, 4)).join(",\n")}
  ];

  var GATE = {
    href: "../",
    name: "${CONG_THANH.ten}",
    note: "${CONG_THANH.note}",
    icon: ${nhay(CONG_THANH.icon)}
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
`;
}

let ghi = 0, giu = 0;
for (const c of CUNG) {
  const p = join(ROOT, c.ma, "assets", "js", "halls.js");
  if (!existsSync(join(ROOT, c.ma, "index.html"))) {
    console.error("✗ " + c.ma + " có trong sổ nhưng không có thư mục — sửa scripts/cung.mjs");
    process.exitCode = 1;
    continue;
  }
  const moi = dungFile(c);
  const cu = existsSync(p) ? await readFile(p, "utf8") : "";
  if (cu === moi) { giu++; continue; }
  await writeFile(p, moi, "utf8");
  console.log("  ✓ " + c.ma + "/assets/js/halls.js");
  ghi++;
}

console.log("\n" + CUNG.length + " cung · ghi lại " + ghi + " · giữ nguyên " + giu);
if (ghi) console.log("Nhớ `npm run nang` — halls.js nằm trong SHELL của mọi cung vừa đổi.");
