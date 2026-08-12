/* ═══════════════════════════════════════════════════════
   Quét 5 chiến trường bằng Claude + web_search, ghi kết quả
   ra dai-quan-trac/assets/js/scan.js.

   Chạy tay:      npm run scan          (cần ANTHROPIC_API_KEY)
   Chạy tự động:  .github/workflows/scan-observatory.yml

   VÌ SAO CHẠY Ở ĐÂY CHỨ KHÔNG PHẢI TRONG TRÌNH DUYỆT

   Bản gốc dai-quan-trac.html gọi thẳng api.anthropic.com từ
   trình duyệt — và không gửi kèm khoá nào, nên lời gọi đó chưa
   bao giờ thành công.

   Thêm khoá vào đó cũng không sửa được: trang chạy trên GitHub
   Pages công khai, nên khoá nhúng trong mã là khoá đã lộ. Ai mở
   DevTools cũng lấy được và tiêu tiền của chủ tài khoản. (Anthropic
   có header anthropic-dangerous-direct-browser-access cho phép gọi
   từ trình duyệt — chữ "dangerous" nằm trong tên header là có lý do,
   và nó dành cho trang chỉ chạy cục bộ, không phải trang công khai.)

   Nên khoá ở lại phía máy chủ, trong GitHub Secrets. Trình duyệt
   chỉ đọc file kết quả tĩnh.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const APP = join(ROOT, "dai-quan-trac");
const OUT = join(APP, "assets", "js", "scan.js");

const KEY = process.env.ANTHROPIC_API_KEY;
if (!KEY) {
  console.error("Thiếu ANTHROPIC_API_KEY.\n" +
    "  · Cục bộ: $env:ANTHROPIC_API_KEY=\"sk-ant-...\"; npm run scan\n" +
    "  · CI:     Settings → Secrets and variables → Actions → New repository secret");
  process.exit(1);
}

/* ── lấy danh sách chiến trường từ chính dữ liệu của app ──
   Không chép cứng sang đây: thêm một chiến trường vào data.js
   là lần quét sau tự có, không phải sửa hai chỗ. */
async function loadTheaters() {
  const src = await readFile(join(APP, "assets", "js", "data.js"), "utf8");
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox, { timeout: 5000 });
  return sandbox.window.DQT_DATA.THEATERS;
}

const MODEL = "claude-opus-5";
const LVLS = ["n", "g", "y", "r"];

function prompt(t) {
  return `Dùng web_search để tìm diễn biến MỚI NHẤT trong 7 ngày gần đây về: ${t.query}.
Bối cảnh: đây là bảng quan trắc đánh giá tác động tới kinh tế Việt Nam.
Trả về DUY NHẤT một JSON object, không markdown, không lời dẫn, không giải thích:
{"muc":"g|y|r","tom_tat":"1 câu tiếng Việt","tin_hieu":[{"tieu_de":"câu tiếng Việt mô tả sự kiện có thật","ngay":"YYYY-MM-DD","nguon":"tên hãng tin","tac_dong":"1 câu: sự kiện này truyền tới kinh tế Việt Nam qua đường nào"}]}
muc: g nếu bình thường, y nếu có căng thẳng đáng chú ý, r nếu gián đoạn nghiêm trọng.
Tối đa 4 tín hiệu, chỉ dùng sự kiện thật tìm được. Nếu không tìm được gì thì trả "tin_hieu":[].`;
}

async function scanOne(t) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 4000,
      // web_search_20260209 có lọc động — chạy trên Opus 4.6 trở lên.
      // Bản gốc dùng web_search_20250305 (biến thể cũ).
      tools: [{ type: "web_search_20260209", name: "web_search" }],
      messages: [{ role: "user", content: prompt(t) }]
    })
  });

  const raw = await res.text();
  if (!res.ok) throw new Error(`HTTP ${res.status} — ${raw.slice(0, 200)}`);
  const data = JSON.parse(raw);

  // Lời từ chối trả về HTTP 200 — phải xem stop_reason trước khi đọc content
  if (data.stop_reason === "refusal") {
    throw new Error("mô hình từ chối" +
      (data.stop_details?.category ? ` (${data.stop_details.category})` : ""));
  }

  const txt = (data.content || []).filter(b => b.type === "text").map(b => b.text).join("\n");
  const m = txt.replace(/```json|```/g, "").match(/\{[\s\S]*\}/);
  if (!m) throw new Error("không đọc được JSON trong phản hồi");
  return { j: JSON.parse(m[0]), usage: data.usage || {} };
}

/* ── chạy ─────────────────────────────────────────────── */
const THEATERS = await loadTheaters();
console.log(`Quét ${THEATERS.length} chiến trường bằng ${MODEL}\n`);

const signals = [];
const levels = {};
const log = [];
const now = new Date().toISOString();
let failed = 0, inTok = 0, outTok = 0;

for (const t of THEATERS) {
  const t0 = Date.now();
  try {
    const { j, usage } = await scanOne(t);
    const list = Array.isArray(j.tin_hieu) ? j.tin_hieu : [];
    list.forEach(s => {
      if (!s.tieu_de) return;
      signals.push({
        th: t.id, tieu_de: s.tieu_de, ngay: s.ngay, nguon: s.nguon,
        tac_dong: s.tac_dong, muc: j.muc, at: now
      });
    });
    if (LVLS.includes(j.muc)) levels[t.id] = j.muc;
    log.push({ ok: true, t: t.short, at: now,
      d: `${list.length} tín hiệu · mức ${j.muc || 'n'}${j.tom_tat ? ' · ' + j.tom_tat : ''}` });
    inTok += usage.input_tokens || 0;
    outTok += usage.output_tokens || 0;
    console.log(`  ✓ ${t.short.padEnd(18)} ${list.length} tín hiệu · mức ${j.muc || '?'} · ${Date.now() - t0} ms`);
  } catch (e) {
    failed++;
    log.push({ ok: false, t: t.short, at: now, d: `Quét lỗi — ${e.message}` });
    console.log(`  ✗ ${t.short.padEnd(18)} ${e.message}`);
  }
}

if (failed === THEATERS.length) {
  console.error("\nHỏng cả 5 chiến trường — giữ nguyên bản quét cũ, không ghi đè.");
  process.exit(1);
}

const scan = {
  generatedAt: now,
  date: `${String(new Date().getUTCDate()).padStart(2, "0")}/${String(new Date().getUTCMonth() + 1).padStart(2, "0")}/${new Date().getUTCFullYear()}`,
  model: MODEL,
  signals, levels, log
};

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH — ĐỪNG SỬA TAY.
   Sinh bởi scripts/build-scan.mjs lúc ${now}
   Nguồn: ${MODEL} + web_search. Khoá API ở lại phía máy chủ.
   ═══════════════════════════════════════════════════════ */
window.DQT_SCAN = ${JSON.stringify(scan, null, 2)};
`;

await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, js, "utf8");

console.log(`\n✓ ${signals.length} tín hiệu · ${Object.keys(levels).length}/${THEATERS.length} chiến trường có mức`);
console.log(`  token: ${inTok} vào · ${outTok} ra`);
console.log(`  đã ghi dai-quan-trac/assets/js/scan.js · ${(js.length / 1024).toFixed(1)} KB`);
