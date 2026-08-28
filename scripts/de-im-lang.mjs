/* ═══════════════════════════════════════════════════════
   ĐÈ IM LẶNG — tìm chỗ một luật CSS bị luật sau ghi đè mà
   không ai biết.

       node scripts/de-im-lang.mjs             soi cả 12 cung
       node scripts/de-im-lang.mjs <cung>      soi một cung

   Thoát 1 khi còn chỗ đè, nên cắm được vào bộ kiểm.

   ── CHUYỆN ĐÃ XẢY RA ─────────────────────────────────────────
   Đài Quan Trắc khai `.tt-n` hai lần trong app.css với giá trị chọi
   nhau, vì hai tính năng khác hẳn nhau cùng chọn tiền tố `tt-`:
   `tt` = trạng thái của cung ấy, và `tt` = tri thức, widget mà
   knowledge-os sinh cho MƯỜI MỘT cung. Cùng độ đặc hiệu thì cái nằm
   dưới thắng, nên số cấp độ — chữ to nhất trên dải trạng thái — bị
   vẽ 10,5px thay vì 27px, ở mọi trang, mọi chủ thể, không lỗi nào báo.

   Tìm ra nó là do may. Cái sinh ra nó thì không may chút nào: mỗi lần
   knowledge-os thêm một lớp `tt-` là mười một cung cùng nhận, nên lớp
   lỗi này mở rộng theo số cung chứ không đứng yên. Nên nó phải thành
   phép canh, đừng để lần sau lại trông vào may.

   ── PHÉP NHẬN DIỆN, VÀ HAI BẪY ĐÃ GỠ ─────────────────────────
   Báo khi: CÙNG ngữ cảnh (@media/@supports), CÙNG selector, CÙNG
   thuộc tính, KHÁC giá trị, ở HAI khối khác nhau.

   Bẫy 1 — khai hai lần trong CÙNG một khối là lối dự phòng CỐ Ý:

       #app{height:100vh; height:100dvh}
       .om-ten{display:block; display:-webkit-box}

   Trình duyệt cũ lấy dòng đầu, trình duyệt mới lấy dòng sau — đó là
   cách duy nhất viết dự phòng trong CSS. Nên trong mỗi khối chỉ lấy
   GIÁ TRỊ CUỐI, đúng thứ trình duyệt dùng. Không có luật trừ này thì
   hai chỗ đúng đắn bị gọi là lỗi, và cảnh báo báo nhầm thì người ta
   bỏ qua cảnh báo.

   Bẫy 2 — bỏ chú thích phải GIỮ số dòng. Thay khối chú thích nhiều
   dòng bằng một dấu cách là mọi số dòng in ra sau đó đều sai, và một
   bộ kiểm chỉ sai chỗ là bộ kiểm khiến người ta đi tìm nhầm nơi.

   ── KHÔNG TỰ SỬA, VÀ ĐÓ LÀ CHỦ Ý ─────────────────────────────
   Máy này chỉ báo. Chọn giá trị nào thắng là quyết định thiết kế —
   `.drawer` rộng 470px hay 400px thì chỉ người dựng cung ấy biết.
   Thứ máy nói chắc chắn là: hôm nay một trong hai đang chết, và
   người viết nó không hay.
   ═══════════════════════════════════════════════════════ */

import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CUNG = process.argv.slice(2).find((a) => !a.startsWith("--"));

/* Cùng phép nhận diện "cung" với kiem-quy-trinh.mjs, thang.mjs và
   tiep-can.mjs: thư mục có index.html NGAY tại gốc nó. */
/* Cổng Thành ở GỐC repo cũng là một webapp có CSS riêng, nhưng nó
   không lọt qua phép nhận diện "thư mục con có index.html" — nó CHÍNH
   LÀ thư mục gốc. Bản đầu bỏ sót nó, và sót im lặng: lệnh in "✓ không
   chỗ nào" trong khi có một tệp chưa hề được đọc.

   Ký hiệu bằng chuỗi rỗng và in ra là "(cổng thành)". */
const GOC = "";

function moiCung() {
  const con = readdirSync(ROOT, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith(".") && d.name !== "node_modules")
    .map((d) => d.name)
    .filter((n) => existsSync(join(ROOT, n, "index.html")))
    .sort();
  return existsSync(join(ROOT, "index.html")) ? [GOC, ...con] : con;
}

/* Tách CSS thành từng khối luật, mang theo ngăn xếp @media đang mở và
   số dòng thật. Không dùng regex một phát: `@media{...}` lồng khối nên
   phải đếm ngoặc, còn regex `[^{}]+\{[^{}]*\}` thì đọc @media thành
   một luật có selector là cả câu điều kiện. */
function tach(css) {
  /* GIỮ SỐ DÒNG — xem "bẫy 2" ở đầu file. */
  const ma = css.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " "));
  const ra = [];
  const nganh = [];
  let i = 0, dau = 0;
  while (i < ma.length) {
    const c = ma[i];
    if (c === "{") {
      const tho = ma.slice(dau, i);
      const dinh = tho.trim();
      /* Đếm tới KÝ TỰ ĐẦU của selector, không tới chỗ khối trước đóng:
         giữa hai khối có dòng trắng và chú thích, nên dau trỏ vào một
         khoảng trắng và số dòng in ra lệch vài dòng lên trên. Bộ kiểm
         chỉ sai chỗ thì người ta đi tìm nhầm nơi rồi thôi tin nó. */
      const lech = tho.length - tho.trimStart().length;
      if (dinh.startsWith("@")) {
        nganh.push(dinh.replace(/\s+/g, " "));
        i++; dau = i; continue;
      }
      let j = i + 1, sau = 1;
      while (j < ma.length && sau) { if (ma[j] === "{") sau++; else if (ma[j] === "}") sau--; j++; }
      ra.push({
        nganh: nganh.join(" ▸ "),
        sel: dinh.replace(/\s+/g, " "),
        than: ma.slice(i + 1, j - 1),
        dong: ma.slice(0, dau + lech).split("\n").length,
      });
      i = j; dau = j; continue;
    }
    if (c === "}") { nganh.pop(); i++; dau = i; continue; }
    i++;
  }
  return ra;
}

function soi(duong) {
  const luat = tach(readFileSync(duong, "utf8"));
  const bang = new Map();
  for (const l of luat) {
    /* Chỉ giữ giá trị CUỐI của mỗi thuộc tính trong khối — xem "bẫy 1". */
    const cuoi = new Map();
    for (const m of l.than.matchAll(/([-\w]+)\s*:\s*([^;]+)/g)) {
      const tp = m[1].toLowerCase();
      if (tp.startsWith("--")) continue;   /* biến: khai lại là chuyện thường */
      cuoi.set(tp, m[2].trim().replace(/\s+/g, " ").replace(/!important$/, "").trim());
    }
    /* Khoá theo CẢ danh sách selector, không theo từng selector tách ra.
       Lý do là một lối viết đúng đắn rất phổ biến:

           .bnhom,.bnhom2{color:var(--ink-3)}   nền chung
           .bnhom2       {color:var(--ink-2)}   rồi biệt hoá một cái

       Tách danh sách ra thì đây thành "cùng .bnhom2, khác giá trị" và
       bị gọi là lỗi — trong khi tác giả cố ý viết đúng như vậy. Khoá
       theo cả danh sách thì hai luật trên là hai selector khác nhau,
       còn `.tt-n{}` … `.tt-n{}` — thứ đã cắn thật — vẫn trùng khoá. */
    for (const [tp, gt] of cuoi) {
      const k = `${l.nganh}\u0000${l.sel}\u0000${tp}`;
      if (!bang.has(k)) bang.set(k, []);
      bang.get(k).push({ gt, dong: l.dong });
    }
  }
  const de = [];
  for (const [k, v] of bang) {
    if (v.length < 2) continue;
    if (new Set(v.map((x) => x.gt)).size < 2) continue;
    const [nganh, sel, tp] = k.split("\u0000");
    de.push({ nganh, sel, tp, v });
  }
  return de;
}

let tong = 0;
for (const c of CUNG ? [CUNG] : moiCung()) {
  const ten = c || "(cổng thành)";
  const thu = join(ROOT, c, "assets", "css");
  if (!existsSync(thu)) continue;
  for (const f of readdirSync(thu).filter((x) => x.endsWith(".css")).sort()) {
    const de = soi(join(thu, f));
    if (!de.length) continue;
    tong += de.length;
    console.log(`\n${ten}${c ? "/" : " "}assets/css/${f} — ${de.length} chỗ đè`);
    for (const d of de) {
      console.log(`   ${d.sel} · ${d.tp}${d.nganh ? `   [${d.nganh}]` : ""}`);
      console.log(`      ${d.v.map((x) => `dòng ${x.dong}: ${x.gt}`).join("   →   ")}` +
        `   ⟵ chỉ giá trị cuối có tác dụng`);
    }
  }
}

if (!tong) { console.log("✓ Không chỗ đè im lặng nào."); process.exit(0); }
console.log(`\n✗ ${tong} chỗ đè im lặng.`);
console.log("  Mỗi chỗ là một luật đang chết mà người viết không hay. Xoá luật chết,");
console.log("  hoặc gộp hai khối lại — máy không tự chọn hộ, xem đầu file để biết vì sao.");
process.exit(1);
