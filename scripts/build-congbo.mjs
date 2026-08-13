/* ═══════════════════════════════════════════════════════
   Sinh dữ liệu cho Công Bộ từ hạ tầng công cụ của L2BEAT.

   Chạy tay:      npm run congbo
   Chạy tự động:  .github/workflows/refresh-data.yml

   ── BA CÔNG CỤ, HAI CẦN DỮ LIỆU ───────────────────────

   1. Nhật ký đổi thay  ← um-prod.l2beat.com/discovery/changes
        Nhật ký thay đổi cấu hình hợp đồng on-chain của các dự án.
        Mỗi mục là một diff dạng markdown. ~2,1 MB thô.

   2. Kính lúp hồ sơ    ← fe-stag.l2beat.com/api/discolupe
        198 dự án × 13 hạng mục hồ sơ: hạng mục nào đã dựng, hạng
        mục nào còn bỏ trống.

   3. Giải mã lời gọi   ← KHÔNG cần dữ liệu build
        Chạy hẳn trong trình duyệt (assets/js/decoder.js). API
        tools-api.l2beat.com/api/decode của chính L2BEAT hiện trả
        500, nên tự viết còn chắc hơn là gọi sang.

   ── CẢNH BÁO VỀ NGUỒN ─────────────────────────────────
   `fe-stag` là host STAGING của L2BEAT, không phải bản chính thức.
   Nó có thể đổi hoặc tắt bất cứ lúc nào, và không ai nợ mình lời
   báo trước. Nên cũng như build-l2beat.mjs: hỏng thì giữ bản cũ,
   in cảnh báo, app hiện dải nhắc — chứ không xoá trắng.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir, readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIR = join(ROOT, "cong-bo", "assets", "js");
const UA = "cong-bo-databot";

/* Diff dài nhất trong một lần chạy là 436 KB — một hợp đồng bị
   dựng lại toàn bộ. Đưa nguyên vào thì riêng nó chiếm 1/5 file.
   Cắt ở 6 KB và ghi rõ đã cắt; ai cần đủ thì có liên kết sang
   L2BEAT ở cuối mỗi mục. */
const CAP_DIFF = 6144;

const log = (...a) => console.log(...a);
const warn = (...a) => console.error("  ⚠", ...a);
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

async function docCu() {
  const f = join(DIR, "data.js");
  if (!existsSync(f)) return null;
  try {
    const t = await readFile(f, "utf8");
    const m = t.match(/window\.CB_DATA\s*=\s*([\s\S]*);\s*$/);
    return m ? JSON.parse(m[1]) : null;
  } catch { return null; }
}
const cu = await docCu();

/* ── 1. nhật ký đổi thay ───────────────────────────── */
/* Bóc phần hữu ích ra khỏi diff: tên hợp đồng, địa chỉ, chuỗi,
   và số dòng thêm/bớt. Nhờ vậy bảng đọc được mà không cần vẽ
   cả diff ra ngay. */
function boc(msg) {
  const m = msg.match(/contract\s+([A-Za-z0-9_ ]+?)\s*\(([a-z0-9]+):(0x[0-9a-fA-F]{40})\)/);
  let them = 0, bot = 0;
  for (const d of msg.split("\n")) {
    if (/^\s*\+(?!\+\+)/.test(d)) them++;
    else if (/^\s*-(?!--)/.test(d)) bot++;
  }
  return {
    hopDong: m ? m[1].trim() : null,
    chuoi: m ? m[2] : null,
    diaChi: m ? m[3] : null,
    them, bot
  };
}

let nhatKy = null;
try {
  const t0 = Date.now();
  const raw = await lay("https://um-prod.l2beat.com/discovery/changes", "json");
  if (!Array.isArray(raw) || !raw.length) throw new Error("không phải mảng, hoặc rỗng");
  let catBot = 0;
  nhatKy = raw.map((x) => {
    const b = boc(x.message || "");
    let d = x.message || "";
    const dai = d.length;
    if (dai > CAP_DIFF) { d = d.slice(0, CAP_DIFF); catBot++; }
    return {
      duAn: x.projectId,
      luc: x.timestamp,
      diff: d,
      daiGoc: dai > CAP_DIFF ? dai : null,
      ...b
    };
  }).sort((a, b) => b.luc - a.luc);
  log(`✓ nhật ký  ${Date.now() - t0} ms · ${nhatKy.length} thay đổi · ${catBot} diff bị cắt`);
} catch (e) {
  warn("Không lấy được nhật ký đổi thay — " + e.message);
  nhatKy = cu?.nhatKy || null;
  if (nhatKy) warn("Giữ nguyên bản trước (" + nhatKy.length + " mục).");
}

/* ── 2. kính lúp hồ sơ ─────────────────────────────── */
/* 13 cờ "đã dựng hạng mục này chưa" của mỗi dự án. Đổi sang mảng
   tên hạng mục để app khỏi phải biết trước danh sách khoá. */
const HANG_MUC = [
  ["areContractsDiscoveryDriven", "hopDong"],
  ["arePermissionsDiscoveryDriven", "quyenHan"],
  ["costsConfigured", "chiPhi"],
  ["livenessConfigured", "doSong"],
  ["milestonesConfigured", "cotMoc"],
  ["operatorConfigured", "benVanHanh"],
  ["withdrawalsConfigured", "rutTien"],
  ["otherConsiderationsConfigured", "luuYKhac"],
  ["stateDerivationConfigured", "dungTrangThai"],
  ["stateValidationConfigured", "kiemChung"],
  ["upgradesAndGovernanceConfigured", "nangCap"]
];

let kinhLup = null;
try {
  await nghi(1200);
  const raw = await lay("https://fe-stag.l2beat.com/api/discolupe", "json");
  const ds = raw?.data?.projects;
  if (!Array.isArray(ds) || !ds.length) throw new Error("thiếu data.projects");
  kinhLup = ds.map((p) => {
    const co = [], thieu = [];
    for (const [khoa, ten] of HANG_MUC) (p[khoa] ? co : thieu).push(ten);
    return {
      id: p.id,
      ten: p.display?.name || p.id,
      slug: p.display?.slug || p.id,
      dang: p.display?.category || null,
      stacks: p.display?.stacks || [],
      loai: p.type || null,
      tvs: typeof p.tvs === "number" ? p.tvs : null,
      luuTru: !!p.isArchived,
      xemXet: !!p.isUnderReview,
      co, thieu
    };
  }).sort((a, b) => (b.tvs || 0) - (a.tvs || 0));
  log(`✓ kính lúp  ${kinhLup.length} dự án · ${HANG_MUC.length} hạng mục`);
} catch (e) {
  warn("Không lấy được kính lúp hồ sơ — " + e.message);
  warn("(fe-stag là host staging của L2BEAT, tắt lúc nào không báo)");
  kinhLup = cu?.kinhLup || null;
  if (kinhLup) warn("Giữ nguyên bản trước (" + kinhLup.length + " dự án).");
}

if (!nhatKy && !kinhLup) {
  console.error("Cả hai nguồn đều hỏng và không có bản cũ — không ghi đè.");
  process.exit(1);
}

/* ── đóng gói ──────────────────────────────────────── */
const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
/* Toàn bộ diff gộp vào data.js là ~930 KB — không thể bắt người mở
   trang tải hết chỉ để xem bảng kính lúp. Tách làm hai:
     data.js       meta + kính lúp + tóm tắt từng thay đổi (nhẹ)
     v/nhat-ky.js  nguyên văn diff, chèn <script> khi mở màn đó */
const tomTat = (nhatKy || []).map((x) => ({
  duAn: x.duAn, luc: x.luc, hopDong: x.hopDong, chuoi: x.chuoi,
  diaChi: x.diaChi, them: x.them, bot: x.bot, daiGoc: x.daiGoc
}));

const out = {
  generatedAt: now.toISOString(),
  date: `${pad(now.getUTCDate())}/${pad(now.getUTCMonth() + 1)}/${now.getUTCFullYear()}`,
  nguon: "l2beat.com — um-prod/discovery/changes + fe-stag/api/discolupe",
  coNhatKy: !!nhatKy,
  coKinhLup: !!kinhLup,
  hangMuc: HANG_MUC.map((h) => h[1]),
  nhatKy: tomTat,
  kinhLup: kinhLup || []
};

const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH bởi scripts/build-congbo.mjs — ĐỪNG SỬA TAY.
   Nguồn: ${out.nguon}
   Lấy lúc: ${out.generatedAt}
   ${out.nhatKy.length} thay đổi · ${out.kinhLup.length} dự án trong kính lúp
   Nguyên văn diff nằm ở v/nhat-ky.js, nạp theo yêu cầu.
   ═══════════════════════════════════════════════════════ */
window.CB_DATA = ${JSON.stringify(out)};
`;
await mkdir(join(DIR, "v"), { recursive: true });
await writeFile(join(DIR, "data.js"), js, "utf8");

const diffs = `/* TỰ SINH bởi scripts/build-congbo.mjs — ĐỪNG SỬA TAY.
   Nguyên văn diff của ${(nhatKy || []).length} thay đổi. Nạp theo yêu cầu. */
window.CB_DIFF = ${JSON.stringify((nhatKy || []).map((x) => x.diff))};
`;
await writeFile(join(DIR, "v", "nhat-ky.js"), diffs, "utf8");
log(`  tách   : data.js ${(js.length / 1024).toFixed(0)} KB + v/nhat-ky.js ${(diffs.length / 1024).toFixed(0)} KB`);

/* ── bảng tra logo, dùng chung với Đô Sát Viện ─────── */
/* 200 file logo đã nằm ở do-sat-vien/assets/logos/. Chép sang đây
   là nhân đôi 1 MB trong repo mà chẳng được gì; chỉ cần bảng tra
   id → tên file, còn ảnh thì trỏ sang thư mục kia. */
try {
  const f = join(ROOT, "do-sat-vien", "assets", "js", "data.js");
  const t = await readFile(f, "utf8");
  const dsv = JSON.parse(t.match(/window\.DSV_DATA = ([\s\S]*);\s*$/)[1]);
  const map = {};
  for (const p of dsv.duAn || []) if (p.logo) map[p.id] = p.logo;
  await writeFile(join(DIR, "logos.js"),
    "/* TỰ SINH bởi scripts/build-congbo.mjs — bảng tra id → tên file logo.\n" +
    "   Ảnh nằm ở do-sat-vien/assets/logos/, cung này chỉ trỏ sang. */\n" +
    "window.DSV_LOGO_MAP = " + JSON.stringify(map) + ";\n", "utf8");
  log(`  logo    : bảng tra ${Object.keys(map).length} dự án (ảnh dùng chung với Đô Sát Viện)`);
} catch (e) {
  warn("Không dựng được bảng tra logo (" + e.message + ") — bảng sẽ hiện chữ cái đầu.");
  const f2 = join(DIR, "logos.js");
  if (!existsSync(f2)) await writeFile(f2, "window.DSV_LOGO_MAP = {};\n", "utf8");
}

/* ── thống kê ──────────────────────────────────────── */
if (nhatKy) {
  const duAn = new Set(nhatKy.map((x) => x.duAn));
  const t = nhatKy.map((x) => x.luc).sort((a, b) => a - b);
  log(`  nhật ký : ${duAn.size} dự án · ${new Date(t[0] * 1000).toISOString().slice(0, 10)} → ${new Date(t[t.length - 1] * 1000).toISOString().slice(0, 10)}`);
}
if (kinhLup) {
  const day = kinhLup.filter((p) => !p.thieu.length).length;
  log(`  kính lúp: ${day}/${kinhLup.length} dự án hồ sơ đủ cả ${HANG_MUC.length} hạng mục`);
  const hay = {};
  kinhLup.forEach((p) => p.thieu.forEach((h) => { hay[h] = (hay[h] || 0) + 1; }));
  log("  thiếu nhiều nhất:", Object.entries(hay).sort((a, b) => b[1] - a[1]).slice(0, 4)
    .map(([k, v]) => `${k}=${v}`).join("  "));
}
log(`\n✓ đã ghi cong-bo/assets/js/data.js · ${(js.length / 1024).toFixed(0)} KB`);
