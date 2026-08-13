/* ═══════════════════════════════════════════════════════
   Sinh do-sat-vien/assets/js/data.js từ L2BEAT.

   Chạy tay:      npm run l2beat
   Chạy tự động:  .github/workflows/refresh-data.yml

   Khác với build-live.mjs (chỉ lấy 14 thành phố thuộc Ethereum
   để gắn huy hiệu lên thẻ Kinh Thành), ở đây lấy TOÀN BỘ 107 dự
   án — vì Đô Sát Viện là bảng xét đầy đủ, không phải chú thích
   thêm cho bản đồ.

   Không có phép khớp tên nào ở đây, nên cũng không có nguy cơ
   khớp nhầm như vụ "basechain" của TON dính vào Base.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir, readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "do-sat-vien", "assets", "js", "data.js");
const SRC = "https://l2beat.com/api/scaling/summary";

const log = (...a) => console.log(...a);

/* giữ bản cũ nếu nguồn hỏng — script chạy trong cron không ai canh */
async function previous() {
  if (!existsSync(OUT)) return null;
  try {
    const t = await readFile(OUT, "utf8");
    const m = t.match(/window\.DSV_DATA = ([\s\S]*);\s*$/);
    return m ? JSON.parse(m[1]) : null;
  } catch { return null; }
}

let raw;
try {
  const t0 = Date.now();
  const res = await fetch(SRC, { headers: { "user-agent": "do-sat-vien-databot" } });
  if (!res.ok) throw new Error("HTTP " + res.status);
  raw = await res.json();
  log(`✓ L2BEAT ${Date.now() - t0} ms`);
} catch (e) {
  const prev = await previous();
  console.error("Không gọi được L2BEAT — " + e.message);
  if (prev) { console.error("Giữ nguyên bản cũ ngày " + prev.date + ", không ghi đè."); process.exit(0); }
  process.exit(1);
}

const list = Object.values(raw.projects || {});
if (!list.length) { console.error("Nguồn trả về 0 dự án — không ghi đè."); process.exit(1); }

/* Cắt gọn: giữ đúng thứ bảng cần. Mô tả rủi ro tiếng Anh của
   L2BEAT giữ lại làm tooltip đối chiếu — bản dịch nằm ở app. */
const projects = list.map((p) => ({
  id: p.id,
  slug: p.slug || p.id,
  ten: p.name,
  loai: p.type,                         // layer2 | layer3
  dang: p.category,                     // Optimistic Rollup | ZK Rollup | …
  thang: p.stage,                       // Stage 0 | 1 | 2 | Not applicable
  me: p.hostChain,                      // chuỗi mẹ
  stack: (p.providers || [])[0] || null,
  tvs: p.tvs?.breakdown?.total ?? null,
  d7: typeof p.tvs?.change7d === "number" ? p.tvs.change7d : null,
  chiaTvs: p.tvs?.breakdown ? {
    native: p.tvs.breakdown.native ?? 0,
    canonical: p.tvs.breakdown.canonical ?? 0,
    external: p.tvs.breakdown.external ?? 0
  } : null,
  ruiRo: (p.risks || []).map((r) => ({ n: r.name, v: r.value, s: r.sentiment, d: r.description || "" })),
  xemXet: !!p.isUnderReview,
  luuTru: !!p.isArchived
})).sort((a, b) => (b.tvs || 0) - (a.tvs || 0));

const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
const out = {
  generatedAt: now.toISOString(),
  date: `${pad(now.getUTCDate())}/${pad(now.getUTCMonth() + 1)}/${now.getUTCFullYear()}`,
  nguon: "l2beat.com/api/scaling/summary",
  tongTvs: projects.reduce((s, p) => s + (p.tvs || 0), 0),
  projects
};

/* ── thống kê in ra để thấy ngay khi nguồn đổi hình ── */
const đếm = (f) => projects.reduce((m, p) => { const k = f(p) ?? "—"; m[k] = (m[k] || 0) + 1; return m; }, {});
const show = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}=${v}`).join("  ");

log(`  ${projects.length} dự án · tổng $${(out.tongTvs / 1e9).toFixed(2)}b`);
log("  loại  :", show(đếm((p) => p.loai)));
log("  thang :", show(đếm((p) => p.thang)));
log("  dạng  :", show(đếm((p) => p.dang)));
log("  stack :", show(đếm((p) => p.stack)));

const chuaDich = new Set();
for (const p of projects) for (const r of p.ruiRo) chuaDich.add(r.n + " → " + r.v);
log(`  ${chuaDich.size} cặp (chiều rủi ro → giá trị) khác nhau`);

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-l2beat.mjs — ĐỪNG SỬA TAY.
   Nguồn: ${out.nguon}
   Lấy lúc: ${out.generatedAt}
   ${projects.length} dự án · tổng tài sản $${(out.tongTvs / 1e9).toFixed(2)}b
   ═══════════════════════════════════════════════════════ */
window.DSV_DATA = ${JSON.stringify(out, null, 1)};
`;

await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, js, "utf8");
log(`\n✓ đã ghi do-sat-vien/assets/js/data.js · ${(js.length / 1024).toFixed(0)} KB`);
