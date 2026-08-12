/* ═══════════════════════════════════════════════════════
   Sinh assets/js/data/live.js từ các API công khai.

   Chạy tay:      npm run refresh
   Chạy tự động:  .github/workflows/refresh-data.yml (mỗi 6 giờ)

   Nguyên tắc:
   · Không phụ thuộc gói ngoài — chỉ fetch của Node 18+.
   · Hỏng một nguồn thì giữ số cũ của nguồn đó, không xoá trắng.
     (chạy trong cron không ai canh, nên thà cũ còn hơn mất)
   · Chỉ đụng vào 3 chỉ số đo được. `addr` và `dec` giữ nguyên
     số chụp trong strength.js — xem ghi chú cuối file.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT = join(ROOT, "assets", "js", "data", "live.js");
const BEGIN = "/* KT_LIVE_BEGIN */";
const END = "/* KT_LIVE_END */";

/* ── bảng tên: mỗi endpoint gọi cùng một chuỗi một kiểu ──
   Đây là chỗ dễ sai nhất. Ví dụ thật: /protocols gọi BNB Chain
   là "Binance", còn /v2/chains và stablecoinchains gọi là "BSC".
   Sai một tên là chỉ số rơi về 0 mà không báo lỗi gì.          */
const MAP = {
  eth:  { tvl: "Ethereum",  stab: "Ethereum",  proto: "Ethereum"  },
  bnb:  { tvl: "BSC",       stab: "BSC",       proto: "Binance"   },
  sol:  { tvl: "Solana",    stab: "Solana",    proto: "Solana"    },
  avax: { tvl: "Avalanche", stab: "Avalanche", proto: "Avalanche" },
  sui:  { tvl: "Sui",       stab: "Sui",       proto: "Sui"       },
  near: { tvl: "Near",      stab: "Near",      proto: "Near"      },
  ton:  { tvl: "TON",       stab: "TON",       proto: "TON"       }
};

/* Cosmos và Polkadot không tồn tại như một "chuỗi" trong API —
   chúng là liên minh. Cộng dồn các thành viên, đúng cách app
   đang làm cho TVL trong refreshTVL(). */
const AGG = {
  atom: ["Cosmos", "Provenance", "Cronos", "dYdX", "Sei", "THORChain", "Kava",
         "Osmosis", "Injective", "Neutron", "Terra", "Canto", "Secret", "MANTRA",
         "Babylon Genesis", "Noble", "Stride", "Archway"],
  dot:  ["Polkadot", "Hydration", "Bifrost", "Astar", "Moonriver", "Moonbeam",
         "Equilibrium", "Acala", "Interlay", "Polkadex"]
};

const IDS = [...Object.keys(MAP), ...Object.keys(AGG)];

/* ── tiện ích ─────────────────────────────────────────── */
const log = (...a) => console.log(...a);

async function getJSON(url, label) {
  const t0 = Date.now();
  const res = await fetch(url, { headers: { "user-agent": "kinh-thanh-databot" } });
  if (!res.ok) throw new Error(`${label}: HTTP ${res.status}`);
  const data = await res.json();
  log(`  ✓ ${label.padEnd(14)} ${String(Date.now() - t0).padStart(5)} ms`);
  return data;
}

/* norm() y hệt trong app.js — khoá thành phố phải trùng tuyệt đối,
   nếu không trình duyệt tra không ra. Giữ nguyên dấu cách. */
const normVi = (s) => String(s).toLowerCase().normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d");

/* Nạp thẳng file dữ liệu của app trong sandbox thay vì bóc bằng regex.
   Chúng là script thường gán vào window.KT_DATA, nên chỉ cần một window giả. */
async function loadAppData(rel, key) {
  const src = await readFile(join(ROOT, rel), "utf8");
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox, { timeout: 5000 });
  return sandbox.window.KT_DATA[key];
}

/* khớp tên không phân biệt hoa thường/dấu cách — API hay đổi vặt */
function indexBy(rows, nameKey, valueFn) {
  const m = new Map();
  for (const r of rows) {
    const n = r[nameKey];
    if (typeof n !== "string") continue;
    m.set(n.toLowerCase().replace(/[^a-z0-9]/g, ""), valueFn(r));
  }
  return m;
}
const look = (m, name) => m.get(String(name).toLowerCase().replace(/[^a-z0-9]/g, ""));

/* lấy giá trị cho 1 nước: hoặc tên thẳng, hoặc cộng dồn liên minh */
function pull(index, id, field, report) {
  if (AGG[id]) {
    let sum = 0, hit = 0;
    for (const member of AGG[id]) {
      const v = look(index, member);
      if (Number.isFinite(v)) { sum += v; hit++; }
    }
    report.push(`${id}.${field}: gộp ${hit}/${AGG[id].length} thành viên`);
    return hit ? sum : null;
  }
  const v = look(index, MAP[id][field]);
  if (!Number.isFinite(v)) report.push(`${id}.${field}: KHÔNG khớp tên "${MAP[id][field]}"`);
  return Number.isFinite(v) ? v : null;
}

/* ── đọc lại bản trước để làm lưới an toàn ────────────── */
async function readPrevious() {
  if (!existsSync(OUT)) return null;
  try {
    const txt = await readFile(OUT, "utf8");
    const a = txt.indexOf(BEGIN), b = txt.indexOf(END);
    if (a < 0 || b < 0) return null;
    const body = txt.slice(a + BEGIN.length, b).trim().replace(/^var\s+LIVE\s*=\s*/, "").replace(/;$/, "");
    return JSON.parse(body);
  } catch {
    return null;
  }
}

/* ── chạy ─────────────────────────────────────────────── */
const prev = await readPrevious();
const report = [];
const failed = [];

log("Đang gọi các nguồn:");

let tvlIndex = null, stabIndex = null, protoIndex = null;

try {
  const rows = await getJSON("https://api.llama.fi/v2/chains", "TVL");
  tvlIndex = indexBy(rows, "name", (r) => r.tvl);
} catch (e) { failed.push(e.message); }

try {
  const rows = await getJSON("https://stablecoins.llama.fi/stablecoinchains", "stablecoin");
  stabIndex = indexBy(rows, "name", (r) => (r.totalCirculatingUSD || {}).peggedUSD);
} catch (e) { failed.push(e.message); }

try {
  const list = await getJSON("https://api.llama.fi/protocols", "giao thức");
  const count = {};
  for (const p of list) for (const c of p.chains || []) count[c] = (count[c] || 0) + 1;
  protoIndex = indexBy(Object.keys(count).map((n) => ({ name: n, n: count[n] })), "name", (r) => r.n);
} catch (e) { failed.push(e.message); }

/* ── L2BEAT: hồ sơ tự trị của từng "thành phố" ──────────
   Đây là nguồn duy nhất trả lời được câu hỏi trung tâm của app:
   thành phố này tự trị đến đâu, và ai đang thật sự cầm chìa khoá. */
let cities = (prev && prev.cities) || {};
try {
  const l2b = await getJSON("https://l2beat.com/api/scaling/summary", "L2BEAT");
  const projects = l2b.projects || {};

  // tra ngược: mọi cách gọi tên của L2BEAT → dự án
  const idx = new Map();
  const key = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, "");
  for (const p of Object.values(projects)) {
    for (const alias of [p.id, p.slug, p.name, String(p.name || "").replace(/ Chain$/i, "")]) {
      if (alias && !idx.has(key(alias))) idx.set(key(alias), p);
    }
  }

  // app gọi thành phố là gì? Lấy từ chính dữ liệu của app, không đoán.
  //
  // CHỈ lấy thành phố thuộc Ethereum. L2BEAT chỉ theo dõi lớp mở rộng của
  // Ethereum, nên quét cả 9 nước sẽ dính đụng độ tên có thật:
  //   · "basechain" của TON  → khớp nhầm "Base Chain" (L2 của Ethereum)
  //   · "phala" của Polkadot → khớp nhầm dự án cùng tên bên Ethereum
  // Gán Stage 1 và $11.6b cho basechain của TON là sai trắng trợn, nên
  // thà bỏ sót vài cái còn hơn hiện số bịa.
  const CHAINS_DATA = await loadAppData("assets/js/data/chains.js", "CHAINS");
  const CITIES_DATA = await loadAppData("assets/js/data/cities.js", "CITIES");
  const wanted = new Map(); // khoá norm() của app → tên hiển thị
  for (const C of CHAINS_DATA) {
    if (C.id !== "eth") continue;
    for (const T of C.tiers) {
      if (T.kind !== "l2") continue;
      for (const G of T.groups) for (const it of G.items) if (!it.more) wanted.set(normVi(it.n), it.n);
    }
  }
  for (const k of Object.keys(CITIES_DATA)) {
    if (CITIES_DATA[k].parent === "eth") wanted.set(normVi(k), CITIES_DATA[k].n || k);
  }

  const found = {};
  const missed = [];
  for (const [k, display] of wanted) {
    const p = idx.get(key(k));
    if (!p) { missed.push(display); continue; }
    found[k] = {
      name: p.name,
      slug: p.slug || p.id,
      stage: p.stage || null,
      category: p.category || null,
      hostChain: p.hostChain || null,
      providers: p.providers || [],
      tvs: p.tvs && p.tvs.breakdown ? Math.round(p.tvs.breakdown.total) : null,
      change7d: p.tvs && typeof p.tvs.change7d === "number" ? p.tvs.change7d : null,
      risks: (p.risks || []).map((r) => ({
        n: r.name, v: r.value, s: r.sentiment, d: r.description || ""
      }))
    };
  }
  cities = found;
  report.push(`L2BEAT: khớp ${Object.keys(found).length}/${wanted.size} thành phố`);
  if (missed.length) report.push("L2BEAT không có: " + missed.join(", "));
} catch (e) {
  failed.push(e.message);
  report.push("L2BEAT hỏng — giữ hồ sơ thành phố của bản trước");
}

if (failed.length) log("\n  ⚠ nguồn hỏng: " + failed.join(" · "));
if (!tvlIndex && !stabIndex && !protoIndex) {
  console.error("\nHỏng cả ba nguồn số — không ghi gì, giữ nguyên file cũ.");
  process.exit(1);
}

const chains = {};
for (const id of IDS) {
  const before = (prev && prev.chains && prev.chains[id]) || {};
  const row = {};
  const put = (field, index) => {
    const v = index ? pull(index, id, field, report) : null;
    if (Number.isFinite(v) && v > 0) row[field] = Math.round(v);
    else if (Number.isFinite(before[field])) row[field] = before[field]; // giữ số cũ
  };
  put("tvl", tvlIndex);
  put("stab", stabIndex);
  put("proto", protoIndex);
  chains[id] = row;
}

const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
const live = {
  generatedAt: now.toISOString(),
  date: `${pad(now.getUTCDate())}/${pad(now.getUTCMonth() + 1)}/${now.getUTCFullYear()}`,
  sources: {
    tvl: "api.llama.fi/v2/chains",
    stab: "stablecoins.llama.fi/stablecoinchains",
    proto: "api.llama.fi/protocols (đếm giao thức theo chuỗi)",
    cities: "l2beat.com/api/scaling/summary (stage, rủi ro, TVS)"
  },
  frozen: {
    addr: "Địa chỉ hoạt động 24h — chưa có nguồn miễn phí nào phủ cả 9 nước. Giữ số chụp trong strength.js.",
    dec: "Phi tập trung — là đánh giá, không phải số đo. Không tự động hoá được."
  },
  chains,
  cities
};

/* ── so sánh với bản trước ────────────────────────────── */
log("\nThay đổi so với bản trước:");
const fmt = (v) => (v == null ? "—" : v >= 1e9 ? "$" + (v / 1e9).toFixed(2) + "b"
  : v >= 1e6 ? "$" + (v / 1e6).toFixed(1) + "m" : String(v));
for (const id of IDS) {
  const a = (prev && prev.chains && prev.chains[id]) || {};
  const b = chains[id];
  const bits = ["tvl", "stab", "proto"].map((k) => {
    if (a[k] === b[k]) return null;
    return `${k} ${fmt(a[k])} → ${fmt(b[k])}`;
  }).filter(Boolean);
  log(`  ${id.padEnd(5)} ${bits.length ? bits.join("  ·  ") : "không đổi"}`);
}
if (report.length) log("\nGhi chú khớp tên:\n  " + report.join("\n  "));

/* ── ghi file ─────────────────────────────────────────── */
const js = `/* ═══════════════════════════════════════════════════════
   TỰ SINH — ĐỪNG SỬA TAY.
   Sinh bởi scripts/build-live.mjs lúc ${live.generatedAt}
   Sửa tay sẽ bị ghi đè ở lần cập nhật tự động kế tiếp.

   File này đè số đo lên bản chụp trong strength.js.
   Xoá file này đi thì app quay về dùng số chụp — vẫn chạy bình thường.
   ═══════════════════════════════════════════════════════ */
(function () {
"use strict";

${BEGIN}
var LIVE = ${JSON.stringify(live, null, 2)};
${END}

var D = window.KT_DATA = window.KT_DATA || {};

/* chỉ đè khi có số thật — hỏng nguồn thì giữ nguyên số chụp.
   Guard chỉ bao phần này: hồ sơ thành phố bên dưới không phụ
   thuộc vào strength.js nên vẫn phải gán dù chưa có STRENGTH. */
if (D.STRENGTH) {
  Object.keys(LIVE.chains).forEach(function (id) {
    var row = LIVE.chains[id], target = D.STRENGTH[id];
    if (!target) return;
    ["tvl", "stab", "proto"].forEach(function (k) {
      var v = row[k];
      if (typeof v === "number" && isFinite(v) && v > 0) target[k] = v;
    });
  });
}

/* app hiển thị "số chụp ngày ..." ở bảng xếp hạng — cho đúng ngày thật */
D.SNAP_DATE = LIVE.date;
D.LIVE = LIVE;

/* hồ sơ L2BEAT cho từng thành phố — l2beat.js đọc từ đây */
D.L2BEAT = LIVE.cities;
})();
`;

await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, js, "utf8");
log(`\nĐã ghi ${OUT.replace(ROOT + "\\", "").replace(ROOT + "/", "")} · ${(js.length / 1024).toFixed(1)} KB · ngày ${live.date}`);
log(`  ${Object.keys(chains).length} quốc gia · ${Object.keys(cities).length} thành phố có hồ sơ L2BEAT`);
