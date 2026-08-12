/* ═══════════════════════════════════════════════════════
   Đóng dấu mỗi bản số liệu lên IPFS, ghi lại lịch sử.

   Chạy: npm run snapshot     (cần PINATA_JWT)

   Vì sao đáng làm ngay, dù chưa neo lên chuỗi:

   Hôm nay bảng xếp hạng nói Ethereum 97 điểm. Ba tháng nữa,
   không gì chứng minh được hôm nay nó đúng là 97 — file live.js
   bị ghi đè mỗi 6 giờ, git history thì người có quyền đẩy vẫn
   sửa được.

   Pin mỗi bản thành một CID riêng thì con số đó bất biến: CID
   chính là hash của nội dung, đổi một chữ số là ra CID khác.
   Đây đã là tính chất "web3" thật, không tốn một đồng gas.

   Và khi nào muốn neo lên Base, thứ cần ghi lên chuỗi chỉ là
   cột `sha256` trong history.json — mỗi dòng 32 byte. Việc
   chuẩn bị đã xong sẵn từ bây giờ.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir, appendFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const LIVE = join(ROOT, "kinh-thanh", "assets", "js", "data", "live.js");
const HIST = join(ROOT, "kinh-thanh", "assets", "data", "history.json");
const BEGIN = "/* KT_LIVE_BEGIN */";
const END = "/* KT_LIVE_END */";

const JWT = process.env.PINATA_JWT;
if (!JWT) {
  console.error("Thiếu PINATA_JWT.");
  process.exit(1);
}
if (!existsSync(LIVE)) {
  console.error("Chưa có live.js — chạy `npm run refresh` trước.");
  process.exit(1);
}

/* ── lấy đúng khối dữ liệu trong live.js ───────────────── */
const txt = await readFile(LIVE, "utf8");
const a = txt.indexOf(BEGIN), b = txt.indexOf(END);
if (a < 0 || b < 0) {
  console.error("live.js không có mốc KT_LIVE_BEGIN/END — bản này sinh bởi script cũ?");
  process.exit(1);
}
const body = txt.slice(a + BEGIN.length, b).trim()
  .replace(/^var\s+LIVE\s*=\s*/, "").replace(/;$/, "");
const live = JSON.parse(body);

/* Chỉ đóng dấu phần SỐ, bỏ phần mô tả dài của L2BEAT.
   Muốn chứng minh "hôm đó Ethereum bao nhiêu TVL", không cần
   kèm theo vài chục KB văn bản tiếng Anh. */
const snapshot = {
  generatedAt: live.generatedAt,
  date: live.date,
  sources: live.sources,
  chains: live.chains,
  cities: Object.fromEntries(Object.entries(live.cities || {}).map(([k, v]) => [k, {
    stage: v.stage, tvs: v.tvs, category: v.category
  }]))
};

/* Chuẩn hoá bằng JSON.stringify không thụt lề, khoá theo đúng thứ tự
   chèn — cùng dữ liệu vào thì cùng byte ra, nên sha256 tái lập được. */
const canonical = JSON.stringify(snapshot);
const sha256 = createHash("sha256").update(canonical, "utf8").digest("hex");

console.log(`Bản số liệu ngày ${snapshot.date}`);
console.log(`  ${Object.keys(snapshot.chains).length} quốc gia · ${Object.keys(snapshot.cities).length} thành phố · ${canonical.length} byte`);
console.log(`  sha256  ${sha256}`);

/* ── đã đóng dấu bản này chưa? ─────────────────────────── */
let history = [];
if (existsSync(HIST)) {
  try { history = JSON.parse(await readFile(HIST, "utf8")); } catch { history = []; }
}
if (history.some((h) => h.sha256 === sha256)) {
  console.log("\nBản này đã đóng dấu rồi (sha256 trùng) — không pin lại.");
  process.exit(0);
}

/* ── pin lên Pinata ────────────────────────────────────── */
const res = await fetch("https://api.pinata.cloud/pinning/pinJSONToIPFS", {
  method: "POST",
  headers: { Authorization: "Bearer " + JWT, "content-type": "application/json" },
  body: JSON.stringify({
    pinataContent: snapshot,
    pinataMetadata: {
      name: `kinh-thanh-snapshot-${snapshot.date.split("/").reverse().join("-")}`,
      keyvalues: { app: "kinh-thanh", kind: "snapshot", date: snapshot.date, sha256 }
    },
    pinataOptions: { cidVersion: 1 }
  })
});

const raw = await res.text();
if (!res.ok) {
  console.error(`\nPinata trả về HTTP ${res.status}\n${raw.slice(0, 400)}`);
  process.exit(1);
}
const cid = JSON.parse(raw).IpfsHash;

/* ── ghi vào lịch sử ───────────────────────────────────── */
history.unshift({
  ts: snapshot.generatedAt,
  date: snapshot.date,
  cid,
  sha256,
  bytes: canonical.length,
  anchored: null // sẽ điền tx hash trên Base khi nào neo lên chuỗi
});
await mkdir(dirname(HIST), { recursive: true });
await writeFile(HIST, JSON.stringify(history, null, 2) + "\n", "utf8");

/* ── file nhỏ cho app đọc đồng bộ ──────────────────────
   Cùng lý do với live.js: app dựng bảng xếp hạng ngay khi tải
   xong, không kịp chờ fetch. Chỉ mang bản mới nhất + số đếm,
   toàn bộ lịch sử vẫn nằm ở history.json. */
const latest = history[0];
await writeFile(
  join(ROOT, "kinh-thanh", "assets", "js", "data", "provenance.js"),
  `/* TỰ SINH bởi scripts/pin-snapshot.mjs — đừng sửa tay. */\n` +
  `(function () {\n` +
  `"use strict";\n` +
  `var D = window.KT_DATA = window.KT_DATA || {};\n` +
  `D.PROV = ${JSON.stringify({
    cid: latest.cid, sha256: latest.sha256, date: latest.date,
    ts: latest.ts, bytes: latest.bytes, count: history.length,
    anchored: latest.anchored
  }, null, 2)};\n` +
  `})();\n`,
  "utf8"
);

console.log(`\n✓ CID  ${cid}`);
console.log(`  lịch sử: ${history.length} bản trong assets/data/history.json`);
console.log(`\n  Khi neo lên Base sau này, thứ cần ghi lên chuỗi là:`);
console.log(`    0x${sha256}   (32 byte)`);

if (process.env.GITHUB_OUTPUT) await appendFile(process.env.GITHUB_OUTPUT, `snapshot_cid=${cid}\n`);
