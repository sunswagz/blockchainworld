/* ═══════════════════════════════════════════════════════
   KIỂM ẢNH — mọi ảnh được KHAI có thật sự nằm trên đĩa không.

       node scripts/kiem-anh.mjs      thoát 1 nếu có ảnh khai mà thiếu

   ── VÌ SAO ───────────────────────────────────────────────────
   Đây là lớp lỗi CLAUDE.md đã mô tả bằng văn xuôi từ lâu, kèm cả câu
   "sẽ nổ đúng lần L2BEAT thêm dự án mới", mà chưa có phép canh nào:

     `build-l2beat.mjs` và `build-congbo.mjs` TẢI ảnh về `assets/logos/`,
     rồi ghi `logos.js` trỏ tới chúng. Nếu `git add` của workflow không
     phủ thư mục ảnh, `logos.js` được commit còn ảnh thì không — trang
     hiện ô vỡ, và KHÔNG lỗi nào báo: không 404 trong log build, không
     phép kiểm nào đỏ, Actions xanh.

   Lời cảnh báo nằm trong văn xuôi thì chỉ cứu được người vừa đọc đúng
   đoạn ấy. Thành phép canh thì nó tự kêu.

   ── ĐỌC BẢNG BẰNG CÁCH NẠP, KHÔNG BẰNG REGEX ─────────────────
   Bản nháp bóc bảng bằng regex và báo 93/93 ảnh thiếu — toàn báo oan,
   vì nó ghép sai thư mục. `logos.js` là JS hợp lệ gán vào `window`,
   nên nạp thẳng bằng `new Function` là đọc đúng thứ trình duyệt đọc,
   không phải một bản phỏng đoán về nó.

   HAI bảng, HAI thư mục khác nhau — đó chính là chỗ regex trượt:

     DSV_LOGO_MAP → do-sat-vien/assets/logos/   (dùng chung)
     CB_LOGO_BU   → cong-bo/assets/logos/       (ảnh bù cho dự án đã ngừng)
   ═══════════════════════════════════════════════════════ */

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const thieu = [];
let tong = 0;

/* ── 1. đường dẫn cục bộ trong index.html ────────────────────
   Cổng Thành ở gốc cũng tính: nó là một webapp có ảnh riêng, và phép
   nhận diện "thư mục con có index.html" không bắt được chính thư mục
   gốc. */
function moiTrang() {
  const con = readdirSync(ROOT, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith(".") && d.name !== "node_modules")
    .map((d) => d.name)
    .filter((n) => existsSync(join(ROOT, n, "index.html")))
    .sort();
  return existsSync(join(ROOT, "index.html")) ? ["", ...con] : con;
}

for (const cung of moiTrang()) {
  const html = readFileSync(join(ROOT, cung, "index.html"), "utf8");
  const da = new Set();
  for (const m of html.matchAll(/(?:src|href)="([^"#?:]+)"/g)) {
    const d = m[1];
    /* Bỏ đường ra ngoài và đường dữ liệu — chỉ soi file trong repo. */
    if (/^(https?:|\/\/|data:|mailto:|#)/.test(d)) continue;
    da.add(d);
  }
  for (const d of da) {
    tong += 1;
    /* Đường bắt đầu bằng `/` tính từ gốc SITE, tức gốc repo. */
    const p = d.startsWith("/") ? join(ROOT, d) : join(ROOT, cung, d);
    if (!existsSync(p)) thieu.push(`${cung || "(cổng thành)"}/index.html → ${d}`);
  }
}

/* ── 2. bảng tra logo ────────────────────────────────────────
   Khai tường minh bảng nào trỏ vào thư mục nào. Đoán bằng tên bảng là
   sớm muộn đoán sai, và một phép kiểm đoán sai thì báo oan — mà cảnh
   báo báo oan đều đặn thì người ta bỏ qua luôn lần nó đúng. */
const BANG = [
  ["DSV_LOGO_MAP", "do-sat-vien/assets/logos"],
  ["CB_LOGO_BU", "cong-bo/assets/logos"],
];
const pLogo = join(ROOT, "cong-bo", "assets", "js", "logos.js");
if (existsSync(pLogo)) {
  const win = {};
  try {
    new Function("window", readFileSync(pLogo, "utf8"))(win);
  } catch (e) {
    thieu.push(`cong-bo/assets/js/logos.js không nạp được: ${String(e.message).slice(0, 90)}`);
  }
  for (const [ten, thu] of BANG) {
    const b = win[ten];
    if (!b) {
      /* Bảng biến mất là chuyện đáng biết: hoặc script sinh đã đổi tên,
         hoặc nó ngừng ghi bảng ấy. Cả hai đều nên có người ngó lại. */
      thieu.push(`logos.js không còn bảng \`${ten}\` — script sinh đã đổi?`);
      continue;
    }
    for (const f of Object.values(b)) {
      tong += 1;
      if (!existsSync(join(ROOT, thu, f))) thieu.push(`${ten} → ${thu}/${f}`);
    }
  }
}

if (!thieu.length) {
  console.log(`✓ Cả ${tong} ảnh/tệp được khai đều có trên đĩa.`);
  process.exit(0);
}
console.log(`✗ ${thieu.length}/${tong} đường khai mà KHÔNG có trên đĩa:\n`);
for (const d of thieu.slice(0, 25)) console.log("   " + d);
if (thieu.length > 25) console.log(`   … và ${thieu.length - 25} đường nữa`);
console.log("\n  Ảnh vỡ trên site không sinh ra lỗi nào: không 404 trong log build,");
console.log("  không phép kiểm nào đỏ, Actions vẫn xanh. Xem `ra` của node sinh ra");
console.log("  chúng trong scripts/node/ — `git add` có phủ thư mục ảnh không?");
process.exit(1);
