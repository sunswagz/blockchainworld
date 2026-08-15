/* ═══════════════════════════════════════════════════════
   Dựng dai-quan-trac/assets/js/scan.js từ bản quét của Tạo Biện Xứ.

   File này KHÔNG CÒN GỌI API NÀO. Trước đây nó tự gọi
   api.anthropic.com bằng ANTHROPIC_API_KEY — và đó là thứ đã tốn
   ~170 USD/tháng rồi phải tắt lịch ngày 14/08/2026.

   ── VIỆC QUÉT GIỜ NẰM Ở ĐÂU ───────────────────────────────────
   Ở chính nhà máy. Bước "Quét chiến trường" trong refresh-data.yml
   chạy `anthropics/claude-code-action`, trả bằng QUOTA GÓI qua
   CLAUDE_CODE_OAUTH_TOKEN, không phải tiền token. Nó dùng WebSearch
   rồi ghi ra một file JSON thô.

   Nên script này còn đúng hai việc, và cả hai đều xác định:

     --de-bai   đọc THEATERS trong data.js của app, ghi đề bài ra
                assets/data/de-bai.json cho bước quét đọc.
     (mặc định) đọc assets/data/quet.json do bước quét ghi, KIỂM,
                rồi dựng scan.js.

   ── VÌ SAO TÁCH ĐÔI CHỨ KHÔNG ĐỂ MODEL GHI THẲNG scan.js ──────
   scan.js là file JS mà trình duyệt nạp. Để model viết thẳng JS là
   một lỗi cú pháp của nó thành một trang trắng cho người xem. Cho
   nó ghi JSON rồi ta dựng JS: hỏng thì hỏng ở chỗ đọc được, và
   khối kiểm bên dưới chặn được trước khi ghi đè bản cũ.

   Khoá vẫn không bao giờ đi xuống trình duyệt — nay còn mạnh hơn
   trước, vì đã không còn khoá API nào để mà lộ.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const APP = join(ROOT, "dai-quan-trac");
const OUT = join(APP, "assets", "js", "scan.js");
const DE_BAI = join(APP, "assets", "data", "de-bai.json");
const QUET = join(APP, "assets", "data", "quet.json");

const LVLS = ["n", "g", "y", "r"];

/* Lấy danh sách chiến trường từ chính dữ liệu của app. Không chép
   cứng sang đây: thêm một chiến trường vào data.js là lượt quét sau
   tự có, không phải sửa hai chỗ. */
async function docChienTruong() {
  const src = await readFile(join(APP, "assets", "js", "data.js"), "utf8");
  const hop = { window: {} };
  vm.createContext(hop);
  vm.runInContext(src, hop, { timeout: 5000 });
  const ds = (hop.window.DQT_DATA || {}).THEATERS;
  if (!Array.isArray(ds) || !ds.length)
    throw new Error("không đọc được THEATERS trong dai-quan-trac/assets/js/data.js");
  return ds;
}

/* ═══════════════ RA ĐỀ BÀI ═══════════════ */
if (process.argv.includes("--de-bai")) {
  const ds = await docChienTruong();
  await mkdir(dirname(DE_BAI), { recursive: true });
  await writeFile(DE_BAI, JSON.stringify({
    ghiChu: "SINH TỰ ĐỘNG từ dai-quan-trac/assets/js/data.js. Đừng sửa tay, đừng commit.",
    chien_truong: ds.map((t) => ({ id: t.id, ten: t.short, tim: t.query }))
  }, null, 2) + "\n", "utf8");
  console.log(`Đề bài: ${ds.length} chiến trường → ${DE_BAI.replace(ROOT, "")}`);
  process.exit(0);
}

/* ═══════════════ DỰNG KẾT QUẢ ═══════════════ */
if (!existsSync(QUET)) {
  console.error("Chưa có assets/data/quet.json — bước quét chưa chạy hoặc đã ngã.\n" +
    "Giữ nguyên bản quét cũ, không ghi đè.");
  process.exit(1);
}

const ds = await docChienTruong();
const hopLe = new Set(ds.map((t) => t.id));
const tenTheoMa = Object.fromEntries(ds.map((t) => [t.id, t.short]));

let tho;
try {
  tho = JSON.parse(await readFile(QUET, "utf8"));
} catch (e) {
  console.error(`quet.json không phải JSON đọc được: ${e.message}`);
  process.exit(1);
}

const now = new Date().toISOString();
const signals = [];
const levels = {};
const log = [];
let nhan = 0;

/* Kiểm từng chiến trường trước khi nhận. Model có thể bịa một id
   không có thật, trả mức ngoài bảng, hoặc trả ngày kiểu "tuần
   trước" — nhận bừa thì bảng hiện một chiến trường không tồn tại
   và không ai lần ra nó từ đâu ra. */
for (const c of Array.isArray(tho.chien_truong) ? tho.chien_truong : []) {
  const ten = tenTheoMa[c && c.id];
  if (!hopLe.has(c && c.id)) {
    log.push({ ok: false, t: String((c && c.id) || "?"), at: now,
      d: "bỏ — id chiến trường không có trong data.js" });
    continue;
  }
  const muc = LVLS.includes(c.muc) ? c.muc : null;
  const tin = (Array.isArray(c.tin_hieu) ? c.tin_hieu : []).filter(
    (s) => s && typeof s.tieu_de === "string" && s.tieu_de.trim()
  ).slice(0, 4);

  tin.forEach((s) => signals.push({
    th: c.id,
    tieu_de: String(s.tieu_de).trim(),
    ngay: /^\d{4}-\d{2}-\d{2}$/.test(s.ngay || "") ? s.ngay : null,
    nguon: s.nguon ? String(s.nguon).slice(0, 60) : null,
    tac_dong: s.tac_dong ? String(s.tac_dong).trim() : null,
    muc, at: now
  }));

  if (muc) levels[c.id] = muc;
  nhan++;
  log.push({ ok: true, t: ten, at: now,
    d: `${tin.length} tín hiệu · mức ${muc || "n"}` +
       (c.tom_tat ? " · " + String(c.tom_tat).trim() : "") });
}

/* Không nhận được chiến trường nào thì GIỮ BẢN CŨ. Bản quét hôm
   qua tuy cũ nhưng đúng; một bảng trống thì người xem đọc thành
   "thế giới không có tin gì", sai hẳn nghĩa. */
if (!nhan) {
  console.error("Không nhận được chiến trường nào từ quet.json — giữ nguyên bản cũ.");
  process.exit(1);
}

const scan = {
  generatedAt: now,
  date: `${String(new Date().getUTCDate()).padStart(2, "0")}/` +
        `${String(new Date().getUTCMonth() + 1).padStart(2, "0")}/` +
        `${new Date().getUTCFullYear()}`,
  model: typeof tho.model === "string" ? tho.model : "claude-code-action",
  signals, levels, log
};

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH — ĐỪNG SỬA TAY.
   Sinh bởi scripts/build-scan.mjs lúc ${now}
   Nguồn: bước "Quét chiến trường" của nhà máy (Claude Code Action
   + WebSearch), trả bằng quota gói. Không có khoá API nào.
   ═══════════════════════════════════════════════════════ */
window.DQT_SCAN = ${JSON.stringify(scan, null, 2)};
`;

await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, js, "utf8");

console.log(`✓ ${signals.length} tín hiệu · ${nhan}/${ds.length} chiến trường nhận được`);
console.log(`  đã ghi dai-quan-trac/assets/js/scan.js · ${(js.length / 1024).toFixed(1)} KB`);
