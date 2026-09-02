#!/usr/bin/env node
/* ═══════════════════════════════════════════════════════
   LỚP CSS KHÔNG AI DÙNG — cân nặng nằm trong SHELL.

       npm run lop-chet            soi Cổng Thành + 12 cung
       npm run lop-chet -- <cung>  soi một cung

   CSS thừa không báo lỗi. Nó chỉ nằm đó, tải về mỗi lượt, và lớn
   dần theo mỗi tính năng bị gỡ mà quên dọn kiểu. Đài Quan Trắc có
   1,7 KB như vậy: dải nhiệt `.heat`/`.hcell` CHƯA TỪNG xuất hiện ở
   JS hay HTML, khối `.pc-*` và `.tang-*` thì còn lại sau một lần
   đổi cấu trúc từ 15/08.

   ── VÌ SAO KHÓ, VÀ BA LẦN KÊU OAN ĐÃ GẶP ──────────────
   Lớp CSS không được "gọi" ở đâu cả — nó chỉ khớp hoặc không. Nên
   mọi phép dò đều là phỏng đoán, và phỏng đoán sai làm người ta xoá
   nhầm lớp đang chạy. Ba bản nháp đều kêu oan:

     1. ghi cứng danh sách tệp JS → thiếu một tệp, báo chết cả loạt
        lớp mà tệp ấy đang dùng
     2. hỏi "tên lớp có nằm trong mã không" (chuỗi con) → `.tang`
        được coi là sống vì chữ "tang" nằm trong một bản tin
     3. đòi tiền tố dài hơn 2 ký tự → bỏ sót `el('div','lv l'+n)` và
        `'trang-thai'+' c'+lvl`, báo tám lớp đang chạy là chết

   Nên bản này nới về phía AN TOÀN ở mọi chỗ còn ngờ: thà bỏ sót một
   lớp chết còn hơn xui người ta xoá một lớp đang dùng. Một bộ kiểm
   xoá nhầm một lần là mất niềm tin vĩnh viễn.
   ═══════════════════════════════════════════════════════ */
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CUNG = process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : null;
const XD = String.fromCharCode(10), C = String.fromCharCode(92);
const GOC = "";

/* Bỏ chú thích mà GIỮ số dòng — cùng lý do đã ghi ở de-im-lang.mjs. */
const catCss = (s) => s.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " "));

function moiCung() {
  const con = readdirSync(ROOT, { withFileTypes: true })
    /* Bỏ `dist` — nó là BẢN DỰNG, tức bản chép của chính site. Báo nó
       là báo lại y hệt phát hiện ở bản gốc, và người đọc phải tự đoán
       hai dòng ấy là một. `dist` cũng gitignore nên máy khác không có. */
    .filter((d) => d.isDirectory() && !d.name.startsWith(".") &&
      d.name !== "node_modules" && d.name !== "dist")
    .map((d) => d.name)
    .filter((n) => existsSync(join(ROOT, n, "index.html")))
    .sort();
  return existsSync(join(ROOT, "index.html")) ? [GOC, ...con] : con;
}

/* Tệp JS mà trang THẬT SỰ nạp: thẻ <script src> tĩnh, VÀ script chèn
   lúc chạy (`s.src='assets/js/pwa.js'`). Vòng tiến hoá đã đổi pwa.js
   sang lối nạp động để bớt cân vỏ; bản chỉ đọc thẻ tĩnh mất hẳn tệp
   ấy rồi báo `.sw-toast` là lớp chết — trong khi pwa.js dựng nó mỗi
   lần có bản mới. */
function tepTrang(goc, html) {
  const duong = [
    ...[...html.matchAll(/<script src="([^"]+)"/g)].map((m) => m[1]),
    ...[...html.matchAll(/[.]src *= *['"]([^'"]+[.]js)['"]/g)].map((m) => m[1]),
  ];
  return duong.filter((p, i, a) => a.indexOf(p) === i && existsSync(join(goc, p)))
    .map((p) => readFileSync(join(goc, p), "utf8"));
}

function soi(c) {
  const goc = join(ROOT, c);
  const ih = join(goc, "index.html");
  if (!existsSync(ih)) return null;
  const html = readFileSync(ih, "utf8");
  const js = tepTrang(goc, html).join(XD);

  const thuCss = join(goc, "assets", "css");
  const tepCss = existsSync(thuCss)
    ? readdirSync(thuCss).filter((x) => x.endsWith(".css")).sort()
    : [];
  if (!tepCss.length) return null;
  const css = tepCss.map((f) => catCss(readFileSync(join(thuCss, f), "utf8"))).join(XD);

  /* TOKEN lớp có thật: mọi chuỗi trong JS tách theo khoảng trắng, và
     mọi class= của HTML. `el('div','a b')` và `classList.add('x')`
     đều là chuỗi, nên một phép là đủ cho cả hai. */
  /* GỠ DẤU THOÁT TRƯỚC KHI RÚT CHUỖI. Cộng Bố viết HTML trong chuỗi
     nháy kép — `"<tr><td class=\\"ts-i\\">"` — nên bộ rút chuỗi đứt ngay ở
     dấu thoát đầu tiên, `ts-i` không bao giờ thành token, và một lớp
     đang chạy bị báo là chết. Gỡ thoát một lượt rồi rút là hết. */
  const jsPhang = js.split(C + '"').join('"').split(C + "'").join("'");
  const token = new Set();
  const nem = (s) => s.split(/[\s"'`]+/).forEach((t) => {
    if (/^[a-z][a-z0-9-]*$/.test(t)) token.add(t);
  });
  for (const m of jsPhang.matchAll(/'([^'\n]*)'|"([^"\n]*)"/g)) nem(m[1] !== undefined ? m[1] : m[2]);
  for (const m of html.matchAll(/class="([^"]*)"/g)) nem(m[1]);
  for (const m of jsPhang.matchAll(/class="([^"]*)"/g)) nem(m[1]);

  /* Tiền tố ghép động: chữ CUỐI của một chuỗi đứng ngay TRƯỚC dấu +.
     Một chữ cái vẫn là một tiền tố — câu phải hỏi là nó có đứng
     trước dấu + hay không, chứ không phải nó dài mấy. */
  const tienTo = new Set();
  for (const m of jsPhang.matchAll(/['"][^'"\n]*?([a-z][a-z0-9-]*)['"]\s*\+/g)) tienTo.add(m[1]);

  const lop = new Set();
  for (const m of css.matchAll(/\.([a-z][a-z0-9-]{1,})(?=[\s,.:{>+~[])/g)) lop.add(m[1]);

  const song = (l) => {
    if (token.has(l)) return true;
    for (const t of tienTo) if (t !== l && l.startsWith(t)) return true;
    for (const t of token) if (t.length > 2 && l.endsWith(t)) return true;
    return false;
  };
  return { lop: lop.size, chet: [...lop].filter((l) => !song(l)).sort(), tepCss: tepCss.length };
}

let tong = 0, doDuoc = 0;
for (const c of CUNG ? [CUNG] : moiCung()) {
  const r = soi(c);
  if (!r) continue;
  doDuoc++;
  const ten = c || "(cổng thành)";
  if (!r.chet.length) continue;
  tong += r.chet.length;
  console.log(`${XD}${ten} — ${r.chet.length} lớp không token nào chạm tới (trên ${r.lop} lớp khai)`);
  console.log("   " + r.chet.join(" "));
}

if (!tong) { console.log(`✓ ${doDuoc} cung · không lớp CSS nào chết.`); process.exit(0); }
console.log(`${XD}✗ ${tong} lớp nghi chết trên ${doDuoc} cung.`);
console.log("  Kiểm bằng tay trước khi xoá — phép dò này là PHỎNG ĐOÁN, xem đầu file.");
process.exit(1);
