/* Dò ứng viên thước — chạy MỘT LẦN để chọn, không phải thước.

   Vì sao có file này: thêm thước theo cảm hứng thì dễ ra hai loại
   thước vô dụng — cái mà MỌI cung đã đạt (không mở dư địa nào), và
   cái mà mọi cung đều trượt vì nó đo sai thứ. Nên đo trước, chọn sau.

   Ứng viên lấy từ kệ kỹ năng đã nhập: design-system (màu phải qua
   token), anti-ui-slop (z-index bịa, !important), accessibility
   (prefers-reduced-motion, color-scheme), baseline-ui (bề rộng dòng
   chữ, line-height không đơn vị).

   Chạy: node scripts/do-ung-vien.mjs
*/

import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { dsTrang, thuMuc } from "./vong-xoay.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

/* Mười ba trang: mười hai cung CỘNG Cổng Thành. Bản đầu tự đếm
   thư mục nên bỏ sót trang gốc — mà đây là chỗ CHỌN xem thước nào
   đáng thêm, nên sót một trang là chọn trên mẫu thiếu. Cùng nguồn với
   phieu-toan-thanh.mjs và thuoc-moi.mjs. */
const CUNG = dsTrang(ROOT);

/* Cắt chú thích trước khi dò chuỗi thô — cùng lý do đã ghi trong
   tien-hoa.mjs: một chú thích giải thích `!important` bị đếm thành
   một `!important` thật. */
const boChuThich = (s) => s.replace(/\/\*[\s\S]*?\*\//g, " ");

function docCss(cung) {
  /* thuMuc() chứ không phải `cung + "/"`: Cổng Thành ở GỐC repo nên
     đường của nó là "assets/css", không phải "cong-thanh/assets/css".
     Đổi mỗi danh sách CUNG mà quên chỗ này thì bảng vẫn ra 12 dòng —
     trang gốc bị `if (!cssGoc) continue` bỏ qua trong im lặng, và
     nhìn ngoài thì y như chưa sửa gì. Đã dính đúng thế một lần. */
  const d = join(ROOT, thuMuc(cung), "assets", "css");
  if (!existsSync(d)) return "";
  return readdirSync(d)
    .filter((f) => f.endsWith(".css"))
    .sort()
    .map((f) => readFileSync(join(d, f), "utf8"))
    .join("\n");
}

/* Thân các khối :root — màu khai ở đây là token, hợp lệ. */
function thanRoot(css) {
  return [...css.matchAll(/:root[^{]*\{([\s\S]*?)\}/g)]
    .map((m) => m[1])
    .join("\n");
}

const SO = [];
for (const c of CUNG) {
  const cssGoc = docCss(c);
  if (!cssGoc) continue;
  const css = boChuThich(cssGoc);
  const root = boChuThich(thanRoot(cssGoc));
  const ngoaiRoot = css.split(/:root[^{]*\{[\s\S]*?\}/).join(" ");
  const fHtml = join(ROOT, thuMuc(c), "index.html");
  const html = existsSync(fHtml) ? readFileSync(fHtml, "utf8") : "";

  const mau = (s) =>
    [...s.matchAll(/#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(/g)].length;

  SO.push({
    cung: c,
    /* accessibility: người bật "giảm chuyển động" trong hệ điều hành */
    giamChuyenDong: /@media[^{]*prefers-reduced-motion/.test(css) ? 1 : 0,
    /* accessibility: báo cho trình duyệt biết trang có mấy tông */
    tongMau: /color-scheme\s*:/.test(css) ? 1 : 0,
    /* design-system: màu phải đi qua token, không rải thẳng */
    mauNgoaiToken: mau(ngoaiRoot),
    mauTrongRoot: mau(root),
    /* anti-ui-slop */
    important: [...css.matchAll(/!important/g)].length,
    zBia: [...css.matchAll(/z-index\s*:\s*(-?\d+)/g)]
      .map((m) => Number(m[1]))
      .filter((n) => Math.abs(n) > 10).length,
    /* baseline-ui: dòng chữ quá dài thì mắt lạc hàng */
    beRongDong: /max-width\s*:\s*[\d.]+(ch|rem|em)/.test(css) ? 1 : 0,
    lineHeightPx: [...css.matchAll(/line-height\s*:\s*[\d.]+px/g)].length,
    /* html */
    metaMau: /name="theme-color"/.test(html) ? 1 : 0,
  });
}

const COT = [
  ["giamChuyenDong", "giảm-ch.động", (v) => (v ? "có" : "KHÔNG")],
  ["tongMau", "color-scheme", (v) => (v ? "có" : "KHÔNG")],
  ["mauNgoaiToken", "màu ngoài token", (v) => String(v)],
  ["important", "!important", (v) => String(v)],
  ["zBia", "z-index bịa", (v) => String(v)],
  ["beRongDong", "bề rộng dòng", (v) => (v ? "có" : "KHÔNG")],
  ["lineHeightPx", "line-height px", (v) => String(v)],
];

console.log("Dò ứng viên thước trên " + SO.length + " cung\n");
const w = 17;
console.log(
  "  " + "cung".padEnd(w) + COT.map(([, t]) => t.padStart(16)).join(""),
);
for (const s of SO) {
  console.log(
    "  " +
      s.cung.padEnd(w) +
      COT.map(([k, , f]) => f(s[k]).padStart(16)).join(""),
  );
}

console.log("\n  Ứng viên nào ĐÁNG thành thước (phải có cung trượt):");
for (const [k, ten] of COT) {
  const truot = SO.filter((s) =>
    k === "giamChuyenDong" || k === "tongMau" || k === "beRongDong"
      ? !s[k]
      : s[k] > 0,
  ).length;
  const nhan =
    truot === 0
      ? "BỎ — mọi cung đã đạt, không mở dư địa nào"
      : truot === SO.length
        ? "CÂN NHẮC — mọi cung đều trượt, kiểm xem có đo đúng không"
        : "NHẬN — phân biệt được " + truot + "/" + SO.length + " cung trượt";
  console.log("    " + ten.padEnd(18) + nhan);
}
