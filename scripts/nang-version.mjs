/* ═══════════════════════════════════════════════════════
   Nâng CACHE_VERSION ở mọi sw.js đang tụt lại phía sau.

   Chạy: npm run nang        (xem trước: npm run nang -- --thu)

   `npm run kiem` đã biết CHỖ NÀO cần nâng — nó so commit cuối của
   sw.js với commit cuối từng file trong SHELL. Nhưng biết rồi vẫn
   phải mở N file sửa tay, và với một hoàng thành nhiều bộ nhiều ban
   thì "sửa tay N chỗ" luôn kết thúc bằng sót một chỗ.

   Sót thì hỏng im lặng: máy đã cài app cứ dùng bản cũ, không 404,
   không lỗi mạng, chỉ có giao diện vỡ ở đúng cung bị sót.

   File được sw.js phục vụ MẠNG-TRƯỚC thì bỏ qua — nó lấy bản mới
   mỗi lần, cache chỉ là lưới đỡ lúc mất mạng. Cùng luật với `kiem`,
   nếu không thì bot cập nhật số liệu 4 lượt/ngày sẽ bắt nâng version
   4 lượt/ngày.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { docMangTruoc, laMangTruoc } from "./mang-truoc.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const THU = process.argv.includes("--thu");

function commitCuoi(p) {
  try {
    return Number(execFileSync("git", ["log", "-1", "--format=%ct", "--", p],
      { cwd: ROOT, encoding: "utf8" }).trim()) || 0;
  } catch { return 0; }
}

/* Đang sửa dở cũng phải tính.

   `npm run kiem` soi trạng thái ĐÃ COMMIT — đúng vai của nó, vì nó
   trả lời "thứ đã đẩy đi có nhất quán không". Nhưng công cụ này thì
   chạy TRƯỚC khi commit, nên nếu chỉ nhìn commit thì nó luôn nói
   "không có gì cần nâng" ngay sau khi bạn vừa sửa xong — vô dụng
   đúng lúc cần nhất.

   Nên: file nào đang đổi trong cây làm việc thì coi như mới nhất. */
const dangSua = new Set();
try {
  const t = execFileSync("git", ["status", "--porcelain"],
    { cwd: ROOT, encoding: "utf8" });
  for (const d of t.split("\n")) {
    const p = d.slice(3).trim().replace(/^"|"$/g, "");
    if (p) dangSua.add(p.replace(/\\/g, "/"));
  }
} catch {}

/* Thư mục nào có index.html thì là cung; cộng thêm gốc repo. */
const BO_QUA = new Set(["assets", "scripts", "dist", "node_modules", ".git", ".github", ".claude"]);
const noi = ["."];
for (const ten of await readdir(ROOT)) {
  if (BO_QUA.has(ten) || ten.startsWith(".")) continue;
  if (existsSync(join(ROOT, ten, "index.html"))) noi.push(ten);
}

let nang = 0, yen = 0;
for (const c of noi) {
  const swP = c === "." ? "sw.js" : `${c}/sw.js`;
  if (!existsSync(join(ROOT, swP))) continue;

  const sw = await readFile(join(ROOT, swP), "utf8");
  const m = /CACHE_VERSION = "v(\d+)"/.exec(sw);
  if (!m) continue;

  const tSw = commitCuoi(swP);
  if (!tSw) { console.log("  · " + swP + " — chưa commit lần nào, bỏ qua"); continue; }

  /* sw.js đang sửa dở thì hỏi thêm MỘT câu nữa: con số đã đổi chưa?
     Đừng chỉ hỏi "file có đổi không".

     Bản đầu bỏ qua mọi sw.js đang sửa dở, với lý do "đang sửa nghĩa
     là đã tự nâng rồi". Lý do đó sai ngay lần dùng thật đầu tiên:
     thêm một nhánh mạng-trước vào tao-bien-xu/sw.js là SỬA sw.js mà
     KHÔNG đụng CACHE_VERSION — và công cụ im lặng báo "không chỗ nào
     cần nâng" trong khi app.js với app.css trong SHELL vừa đổi hết.

     Đó đúng là kiểu hỏng công cụ này sinh ra để chặn, và nó tự dính.
     Nên: so con số với bản đã commit. Khác → đã nâng, để yên.
     Giống → cứ soi SHELL như mọi sw.js khác. */
  if (dangSua.has(swP)) {
    let cuHon = null;
    try {
      const t = execFileSync("git", ["show", "HEAD:" + swP],
        { cwd: ROOT, encoding: "utf8" });
      const mc = /CACHE_VERSION = "v(\d+)"/.exec(t);
      cuHon = mc ? mc[1] : null;
    } catch {}
    if (cuHon !== null && cuHon !== m[1]) { yen++; continue; }
  }

  /* Nhận diện mạng-trước dùng chung với `npm run kiem` — xem
     scripts/mang-truoc.mjs. Trước đây cùng một regex bị chép ở hai
     file, và khi một cung khai bằng dạng khác thì cả hai cùng đoán
     sai theo cùng một kiểu.

     Không đọc được khai báo thì KHÔNG nâng bừa. Nâng version của một
     cung mà mình không hiểu chỉ đẩy một bản cache mới xuống máy người
     dùng chứ chẳng sửa gì, lại xoá luôn dấu hiệu để lần sau không ai
     lần ra. `npm run kiem` mới là chỗ nói ra chuyện đó. */
  const { duong: mangTruoc, docDuoc } = docMangTruoc(sw);
  const shell = [...sw.matchAll(/^\s*"\.\/([^"]+)"/gm)].map((x) => x[1]);
  if (!docDuoc) {
    console.log("  · " + swP + " — không đọc được khai báo mạng-trước, bỏ qua " +
      "(chạy `npm run kiem` để xem chi tiết)");
    continue;
  }

  const tre = [];
  for (const f of shell) {
    if (laMangTruoc(mangTruoc, f)) continue;
    const p = c === "." ? f : `${c}/${f}`;
    if (!existsSync(join(ROOT, p))) continue;
    if (dangSua.has(p) || commitCuoi(p) > tSw) tre.push(f);
  }

  if (!tre.length) { yen++; continue; }

  const cu = Number(m[1]), moi = cu + 1;
  const ten = (c === "." ? "gốc" : c).padEnd(15);
  console.log("  " + (THU ? "sẽ nâng" : "✓ nâng") + " " + ten + "v" + cu + " → v" + moi +
    "   (" + tre.length + " file mới hơn: " + tre.slice(0, 3).join(", ") +
    (tre.length > 3 ? "…" : "") + ")");
  if (!THU) {
    await writeFile(join(ROOT, swP),
      sw.replace(/CACHE_VERSION = "v\d+"/, 'CACHE_VERSION = "v' + moi + '"'), "utf8");
  }
  nang++;
}

console.log("\n" + (nang ? nang + " sw.js " + (THU ? "cần nâng" : "đã nâng") : "Không chỗ nào cần nâng") +
  " · " + yen + " chỗ vốn đã kịp.");
if (nang && !THU) {
  console.log("Commit chúng cùng lần sửa, đừng để riêng — người dùng cần cả hai mới thấy bản mới.");
}
