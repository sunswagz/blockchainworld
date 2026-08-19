/* ═══════════════════════════════════════════════════════
   DỰNG BẢN QUÉT cho Đài Quan Trắc.

   Chạy hai chế độ:
     --de-bai   đọc THEATERS trong data.js của TỪNG chủ thể, ghi đề
                bài ra assets/data/de-bai.json cho bước quét đọc.
     (mặc định) đọc assets/data/quet.json do bước quét ghi, KIỂM,
                rồi dựng scan.js cho từng chủ thể.

   ── VÌ SAO TÁCH ĐÔI CHỨ KHÔNG ĐỂ MODEL GHI THẲNG scan.js ──────
   scan.js là file JS mà trình duyệt nạp. Để model viết thẳng JS là
   một lỗi cú pháp của nó thành một trang trắng cho người xem. Cho
   nó ghi JSON rồi ta dựng JS: hỏng thì hỏng ở chỗ đọc được, và
   khối kiểm bên dưới chặn được trước khi ghi đè bản cũ.

   Khoá vẫn không bao giờ đi xuống trình duyệt — nay còn mạnh hơn
   trước, vì đã không còn khoá API nào để mà lộ.

   ── VÌ SAO ID PHẢI GHÉP "nuoc:chien_truong" ──────────────────
   Hai chủ thể CÓ chiến trường trùng id: `nga` vừa là Nga–Ukraina
   của Việt Nam vừa là Nga-đường-vòng của Trung Quốc. Nếu để id
   phẳng thì tín hiệu về nước này chảy sang bảng nước kia, và
   không ai lần ra vì cả hai đều "hợp lệ".

   Ghép tiền tố là cùng một cách app đã khoá state theo chủ thể
   (`state.gg['vn:nangluong']`). Một quy ước, dùng ở cả hai đầu.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { CHU_THE, docChuThe } from "./dqt-chuthe.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const APP = join(ROOT, "dai-quan-trac");
const QUET = join(APP, "assets", "data", "quet.json");
const DE_BAI = join(APP, "assets", "data", "de-bai.json");
const LVLS = ["n", "g", "y", "r"];

/* Lấy danh sách chiến trường từ chính dữ liệu của app. Không chép
   cứng sang đây: thêm một chiến trường vào data.js là lượt quét sau
   tự có, không phải sửa hai chỗ. */
async function docTatCa() {
  const ra = [];
  for (const ct of CHU_THE) {
    let d;
    try { d = await docChuThe(APP, ct); }
    catch (e) { console.error(`  ⚠ ${ct.ten}: ${e.message}`); continue; }
    const ds = d.THEATERS;
    if (!Array.isArray(ds) || !ds.length) {
      console.error(`  ⚠ ${ct.ten}: không có THEATERS`); continue;
    }
    ra.push({ ct, ds });
  }
  if (!ra.length) throw new Error("không đọc được chiến trường của chủ thể nào");
  return ra;
}

/* ═══════════════ RA ĐỀ BÀI ═══════════════ */
if (process.argv.includes("--de-bai")) {
  const nhom = await docTatCa();
  const muc = [];
  for (const { ct, ds } of nhom)
    for (const t of ds)
      muc.push({ id: `${ct.id}:${t.id}`, nuoc: ct.ten, ten: t.short,
                 tim: t.query, boi_canh: ct.boiCanh });

  await mkdir(dirname(DE_BAI), { recursive: true });
  await writeFile(DE_BAI, JSON.stringify({
    ghiChu: "SINH TỰ ĐỘNG từ data.js của từng chủ thể. Đừng sửa tay, đừng commit.",
    chien_truong: muc
  }, null, 2) + "\n", "utf8");

  console.log(`Đề bài: ${muc.length} chiến trường / ${nhom.length} chủ thể → ${DE_BAI.replace(ROOT, "")}`);
  for (const { ct, ds } of nhom) console.log(`  ${ct.ten}: ${ds.length}`);
  process.exit(0);
}

/* ═══════════════ DỰNG KẾT QUẢ ═══════════════ */
if (!existsSync(QUET)) {
  console.error("Chưa có assets/data/quet.json — bước quét chưa chạy hoặc đã ngã.\n" +
    "Giữ nguyên bản quét cũ, không ghi đè.");
  process.exit(1);
}

const nhom = await docTatCa();
const theoNuoc = Object.fromEntries(nhom.map(({ ct, ds }) => [ct.id, {
  ct, hopLe: new Set(ds.map((t) => t.id)),
  ten: Object.fromEntries(ds.map((t) => [t.id, t.short])),
  tong: ds.length, signals: [], levels: {}, log: [], nhan: 0
}]));

let tho;
try {
  tho = JSON.parse(await readFile(QUET, "utf8"));
} catch (e) {
  console.error(`quet.json không phải JSON đọc được: ${e.message}`);
  process.exit(1);
}

const now = new Date().toISOString();

/* Kiểm từng chiến trường trước khi nhận. Model có thể bịa một id
   không có thật, quên tiền tố nước, trả mức ngoài bảng, hoặc trả
   ngày kiểu "tuần trước" — nhận bừa thì bảng hiện một chiến trường
   không tồn tại và không ai lần ra nó từ đâu ra. */
for (const c of Array.isArray(tho.chien_truong) ? tho.chien_truong : []) {
  const raw = String((c && c.id) || "");
  const [nuoc, ma] = raw.includes(":") ? raw.split(":") : [null, raw];
  const b = nuoc && theoNuoc[nuoc];

  if (!b) {
    /* Không có tiền tố thì KHÔNG đoán hộ. `nga` thuộc cả hai nước;
       đoán sai là đổ tín hiệu vào bảng sai nước. */
    const bat = Object.values(theoNuoc).find((x) => x.hopLe.has(raw));
    (bat || Object.values(theoNuoc)[0]).log.push({
      ok: false, t: raw || "?", at: now,
      d: 'bỏ — id thiếu tiền tố nước (phải dạng "vn:hormuz")'
    });
    continue;
  }
  if (!b.hopLe.has(ma)) {
    b.log.push({ ok: false, t: ma || "?", at: now,
      d: "bỏ — id chiến trường không có trong data.js của " + b.ct.ten });
    continue;
  }

  const muc = LVLS.includes(c.muc) ? c.muc : null;
  const tin = (Array.isArray(c.tin_hieu) ? c.tin_hieu : []).filter(
    (s) => s && typeof s.tieu_de === "string" && s.tieu_de.trim()
  ).slice(0, 4);

  tin.forEach((s) => b.signals.push({
    th: ma,
    tieu_de: String(s.tieu_de).trim(),
    ngay: /^\d{4}-\d{2}-\d{2}$/.test(s.ngay || "") ? s.ngay : null,
    nguon: s.nguon ? String(s.nguon).slice(0, 60) : null,
    tac_dong: s.tac_dong ? String(s.tac_dong).trim() : null,
    muc, at: now
  }));

  if (muc) b.levels[ma] = muc;
  b.nhan++;
  b.log.push({ ok: true, t: b.ten[ma], at: now,
    d: `${tin.length} tín hiệu · mức ${muc || "n"}` +
       (c.tom_tat ? " · " + String(c.tom_tat).trim() : "") });
}

/* Không nhận được chiến trường nào thì GIỮ BẢN CŨ. Bản quét hôm
   qua tuy cũ nhưng đúng; một bảng trống thì người xem đọc thành
   "thế giới không có tin gì", sai hẳn nghĩa.

   Xét RIÊNG từng nước: model hết giờ giữa chừng thì nước quét
   trước vẫn phải được ghi, không kéo nhau cùng ngã. */
const ngay = `${String(new Date().getUTCDate()).padStart(2, "0")}/` +
             `${String(new Date().getUTCMonth() + 1).padStart(2, "0")}/` +
             `${new Date().getUTCFullYear()}`;
let daGhi = 0;

for (const b of Object.values(theoNuoc)) {
  if (!b.nhan) {
    console.error(`✗ ${b.ct.ten}: không nhận được chiến trường nào — giữ nguyên bản cũ.`);
    continue;
  }
  const scan = {
    generatedAt: now, date: ngay,
    model: typeof tho.model === "string" ? tho.model : "claude-code-action",
    signals: b.signals, levels: b.levels, log: b.log
  };
  const OUT = join(APP, ...b.ct.scanRa);
  const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH — ĐỪNG SỬA TAY.
   Sinh bởi scripts/build-scan.mjs lúc ${now}
   Chủ thể: ${b.ct.ten}
   Nguồn: bước "Quét chiến trường" của nhà máy (Claude Code Action
   + WebSearch), trả bằng quota gói. Không có khoá API nào.
   ═══════════════════════════════════════════════════════ */
window.${b.ct.scanBien} = ${JSON.stringify(scan, null, 2)};
`;
  await mkdir(dirname(OUT), { recursive: true });
  await writeFile(OUT, js, "utf8");
  daGhi++;
  console.log(`✓ ${b.ct.ten}: ${b.signals.length} tín hiệu · ${b.nhan}/${b.tong} chiến trường` +
              ` → ${b.ct.scanRa.join("/")} · ${(js.length / 1024).toFixed(1)} KB`);
}

if (!daGhi) {
  console.error("Không chủ thể nào nhận được kết quả — giữ nguyên toàn bộ bản cũ.");
  process.exit(1);
}
