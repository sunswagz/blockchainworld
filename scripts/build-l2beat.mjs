/* ═══════════════════════════════════════════════════════
   Sinh do-sat-vien/assets/js/data.js từ L2BEAT.

   Chạy tay:      npm run l2beat
   Chạy tự động:  .github/workflows/refresh-data.yml

   ── HAI NGUỒN, VÀ VÌ SAO PHẢI CẢ HAI ──────────────────

   1. API  /api/scaling/summary
        · tvs.breakdown (gốc bản địa / cầu chính thức / cầu ngoài)
        · tvs.change7d
        · chart — chuỗi thời gian để vẽ biểu đồ
      Đây là giao diện công khai, ổn định. NHƯNG nó KHÔNG có
      logo, không có tab, không có hệ chứng minh, không có UOPS.

   2. HTML /scaling/summary → window.__SSR_DATA__
        · icon (logo), tab (rollups/validium/khác)
        · proofSystem {type, name, challengeProtocol}
        · activity.pastDayUops
        · stage.missing — còn thiếu gì để lên thang sau
        · description, stacks, dataAvailability
      Đây là dữ liệu nội bộ của trang, KHÔNG phải API cam kết.
      L2BEAT đổi cấu trúc trang là chỗ này gãy.

   Nên nguồn 1 là BẮT BUỘC, nguồn 2 là LÀM GIÀU THÊM. Nguồn 2
   hỏng thì giữ nguyên phần làm giàu của bản trước và kêu to
   trong log, chứ không xoá trắng và không làm hỏng cả lần chạy.

   Khác với build-live.mjs (chỉ lấy 14 thành phố thuộc Ethereum
   để gắn huy hiệu lên thẻ Kinh Thành), ở đây lấy TOÀN BỘ dự án.
   Không có phép khớp tên nào, nên cũng không có nguy cơ khớp
   nhầm như vụ "basechain" của TON dính vào Base.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir, readFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "do-sat-vien", "assets", "js", "data.js");
const LOGOS = join(ROOT, "do-sat-vien", "assets", "logos");

const HOST = "https://l2beat.com";
const API = HOST + "/api/scaling/summary";
const PAGE = HOST + "/scaling/summary";
const UA = "do-sat-vien-databot";

const log = (...a) => console.log(...a);
const warn = (...a) => console.error("  ⚠", ...a);

/* L2BEAT nấp sau Cloudflare và chặn khi gọi dồn (error code: 1015).
   Cron 4 lần/ngày thì không sao, nhưng chạy tay liên tiếp thì dính. */
const nghi = (ms) => new Promise((r) => setTimeout(r, ms));

async function lay(url, kieu) {
  for (let lan = 1; lan <= 3; lan++) {
    try {
      const res = await fetch(url, { headers: { "user-agent": UA } });
      const txt = await res.text();
      if (!res.ok) throw new Error("HTTP " + res.status);
      if (/^error code: \d+/.test(txt)) throw new Error(txt.trim().slice(0, 40));
      return kieu === "json" ? JSON.parse(txt) : txt;
    } catch (e) {
      if (lan === 3) throw e;
      warn(`${url} lỗi (${e.message}) — thử lại lần ${lan + 1} sau ${lan * 5}s`);
      await nghi(lan * 5000);
    }
  }
}

/* giữ bản cũ nếu nguồn hỏng — script chạy trong cron, không ai canh */
async function truoc() {
  if (!existsSync(OUT)) return null;
  try {
    const t = await readFile(OUT, "utf8");
    const m = t.match(/window\.DSV_DATA = ([\s\S]*);\s*$/);
    return m ? JSON.parse(m[1]) : null;
  } catch { return null; }
}

const cu = await truoc();

/* ── nguồn 1: API (bắt buộc) ───────────────────────────── */
let raw;
try {
  const t0 = Date.now();
  raw = await lay(API, "json");
  log(`✓ API  ${Date.now() - t0} ms`);
} catch (e) {
  console.error("Không gọi được API L2BEAT — " + e.message);
  if (cu) { console.error("Giữ nguyên bản cũ ngày " + cu.date + ", không ghi đè."); process.exit(0); }
  process.exit(1);
}

const list = Object.values(raw.projects || {});
if (!list.length) { console.error("Nguồn trả về 0 dự án — không ghi đè."); process.exit(1); }

/* ── nguồn 2: SSR (làm giàu, hỏng thì bỏ qua) ──────────── */
let ssr = null;
try {
  await nghi(1500);                       // đừng gọi dồn vào Cloudflare
  const html = await lay(PAGE, "text");
  const dau = html.indexOf("window.__SSR_DATA__=");
  if (dau === -1) throw new Error("không thấy window.__SSR_DATA__");
  const i = dau + "window.__SSR_DATA__=".length;
  const cuoi = html.indexOf("</script>", i);
  const d = JSON.parse(html.slice(i, cuoi).trim().replace(/;$/, ""));
  const e = d?.props?.entries;
  if (!e || typeof e !== "object") throw new Error("props.entries không đúng hình");
  ssr = {};
  for (const [tab, muc] of Object.entries(e)) {
    if (!Array.isArray(muc)) continue;
    for (const p of muc) if (p && p.id) ssr[p.id] = { ...p, tab };
  }
  log(`✓ SSR  ${Object.keys(ssr).length} dự án · tab: ` +
    Object.entries(e).map(([k, v]) => `${k}=${v.length}`).join(" "));
} catch (e) {
  ssr = null;
  warn("Không đọc được SSR (" + e.message + ").");
  warn("Logo / tab / hệ chứng minh / UOPS sẽ lấy lại từ bản trước.");
}

/* bản đồ làm giàu của lần chạy trước, để vá khi SSR hỏng */
const vaCu = {};
if (cu) for (const p of cu.projects || []) vaCu[p.id] = p;

/* ── gộp ───────────────────────────────────────────────── */
const TAB_VI = { rollups: "rollup", validiumsAndOptimiums: "validium", others: "khac" };

let tuSSR = 0, tuCu = 0, khong = 0;

const projects = list.map((p) => {
  const s = ssr && ssr[p.id];
  const c = vaCu[p.id];
  if (s) tuSSR++; else if (c && c.tab) tuCu++; else khong++;

  /* chỉ lấy phần làm giàu từ SSR; SỐ thì luôn từ API */
  const them = s ? {
    tab: TAB_VI[s.tab] || "khac",
    logo: s.icon ? s.icon.replace(/^.*\/static\/icons\//, "") : null,
    moTa: s.description || null,
    heCM: s.proofSystem ? {
      loai: s.proofSystem.type || null,
      ten: s.proofSystem.name || null,
      giaoThuc: s.proofSystem.challengeProtocol || null
    } : null,
    uops: s.activity && typeof s.activity.pastDayUops === "number"
      ? { sl: s.activity.pastDayUops, doi: s.activity.change ?? null, ky: s.activity.changePeriod || null }
      : null,
    thieu: s.stage && s.stage.missing ? {
      thangSau: s.stage.missing.nextStage || null,
      dieuKien: Array.isArray(s.stage.missing.requirements) ? s.stage.missing.requirements : []
    } : null,
    stacks: Array.isArray(s.stacks) ? s.stacks : [],
    baoDong: !!(s.statuses && s.statuses.ongoingAnomaly)
  } : (c ? {
    tab: c.tab || "khac", logo: c.logo ?? null, moTa: c.moTa ?? null,
    heCM: c.heCM ?? null, uops: c.uops ?? null, thieu: c.thieu ?? null,
    stacks: c.stacks || [], baoDong: !!c.baoDong
  } : {
    tab: "khac", logo: null, moTa: null, heCM: null, uops: null,
    thieu: null, stacks: [], baoDong: false
  });

  return {
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
    luuTru: !!p.isArchived,
    ...them
  };
}).sort((a, b) => (b.tvs || 0) - (a.tvs || 0));

log(`  làm giàu: ${tuSSR} từ SSR · ${tuCu} vá từ bản cũ · ${khong} không có`);
if (khong && ssr) warn(`${khong} dự án mới chưa có trong SSR — sẽ rơi vào tab "khác" cho tới lần chạy sau.`);

/* ── biểu đồ theo thời gian ────────────────────────────── */
let bieuDo = null;
if (raw.chart && Array.isArray(raw.chart.data) && raw.chart.data.length) {
  bieuDo = { cot: raw.chart.types || [], diem: raw.chart.data };
  log(`  biểu đồ : ${bieuDo.diem.length} điểm · cột [${bieuDo.cot.join(", ")}]`);
} else {
  warn("API không trả chart — giữ biểu đồ của bản trước.");
  bieuDo = cu?.bieuDo || null;
}

/* ── tải logo về repo ──────────────────────────────────── */
/* URL của L2BEAT có hash nội dung (base.4840b6b2.png) nên đổi tên
   file là đổi ảnh. Đã có file trùng tên thì bỏ qua, không tải lại. */
await mkdir(LOGOS, { recursive: true });
const daCo = new Set(existsSync(LOGOS) ? await readdir(LOGOS) : []);
let taiVe = 0, boQua = 0, hong = 0;

for (const p of projects) {
  if (!p.logo) continue;
  if (daCo.has(p.logo)) { boQua++; continue; }
  try {
    const res = await fetch(HOST + "/static/icons/" + p.logo, { headers: { "user-agent": UA } });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const buf = Buffer.from(await res.arrayBuffer());
    if (buf.length < 100) throw new Error("file quá nhỏ, " + buf.length + " byte");
    await writeFile(join(LOGOS, p.logo), buf);
    taiVe++;
    await nghi(120);                      // đừng dồn vào Cloudflare
  } catch (e) {
    warn(`logo ${p.ten} (${p.logo}): ${e.message}`);
    p.logo = null;
    hong++;
  }
}
log(`  logo    : ${taiVe} tải mới · ${boQua} đã có · ${hong} hỏng`);

/* ── đóng gói ──────────────────────────────────────────── */
const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
const out = {
  generatedAt: now.toISOString(),
  date: `${pad(now.getUTCDate())}/${pad(now.getUTCMonth() + 1)}/${now.getUTCFullYear()}`,
  nguon: "l2beat.com — API scaling/summary + dữ liệu trang scaling/summary",
  coSSR: !!ssr,
  tongTvs: projects.reduce((s, p) => s + (p.tvs || 0), 0),
  demTab: projects.reduce((m, p) => { m[p.tab] = (m[p.tab] || 0) + 1; return m; }, {}),
  bieuDo,
  projects
};

/* ── thống kê in ra để thấy ngay khi nguồn đổi hình ── */
const dem = (f) => projects.reduce((m, p) => { const k = f(p) ?? "—"; m[k] = (m[k] || 0) + 1; return m; }, {});
const show = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}=${v}`).join("  ");

log(`\n  ${projects.length} dự án · tổng $${(out.tongTvs / 1e9).toFixed(2)}b`);
log("  tab   :", show(out.demTab));
log("  thang :", show(dem((p) => p.thang)));
log("  hệ CM :", show(dem((p) => p.heCM?.loai)));
log("  UOPS  :", projects.filter((p) => p.uops).length + "/" + projects.length);

const cap = new Set();
for (const p of projects) for (const r of p.ruiRo) cap.add(r.n + " → " + r.v);
log(`  ${cap.size} cặp (chiều rủi ro → giá trị) khác nhau`);

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-l2beat.mjs — ĐỪNG SỬA TAY.
   Nguồn: ${out.nguon}
   Lấy lúc: ${out.generatedAt}
   ${projects.length} dự án · tổng tài sản $${(out.tongTvs / 1e9).toFixed(2)}b
   Làm giàu từ SSR: ${out.coSSR ? "có" : "KHÔNG — logo/tab/hệ CM lấy từ bản trước"}
   ═══════════════════════════════════════════════════════ */
window.DSV_DATA = ${JSON.stringify(out, null, 1)};
`;

await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, js, "utf8");
log(`\n✓ đã ghi do-sat-vien/assets/js/data.js · ${(js.length / 1024).toFixed(0)} KB`);
