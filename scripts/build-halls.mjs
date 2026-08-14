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
