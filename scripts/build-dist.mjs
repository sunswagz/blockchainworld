/* ═══════════════════════════════════════════════════════
   Gom app thành dist/ để đưa lên IPFS.

   Chạy: npm run dist

   dist/ chỉ chứa thứ trình duyệt cần. Không có scripts/,
   .github/, README, server.js — những thứ đó là đồ nghề,
   đưa lên IPFS chỉ tổ nặng và lộ cấu hình.

   Kèm ba lớp kiểm tra chạy TRƯỚC khi ghi, vì một khi đã pin
   lên IPFS thì CID sai không rút lại được.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir, rm, readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, relative, extname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIST = join(ROOT, "dist");

/* thứ đi lên IPFS — không có gì khác */
const INCLUDE = ["index.html", "manifest.webmanifest", "sw.js", "assets"];

const TEXT = new Set([".html", ".css", ".js", ".mjs", ".json", ".webmanifest", ".svg", ".md"]);

const log = (...a) => console.log(...a);
const fail = (msg) => { console.error("\n✗ " + msg); process.exitCode = 1; };

/* ── liệt kê file ─────────────────────────────────────── */
async function walk(dir, out = []) {
  for (const name of await readdir(dir)) {
    const p = join(dir, name);
    const s = await stat(p);
    if (s.isDirectory()) await walk(p, out);
    else out.push(p);
  }
  return out;
}

async function collect() {
  const files = [];
  for (const item of INCLUDE) {
    const p = join(ROOT, item);
    if (!existsSync(p)) { fail(`thiếu ${item}`); continue; }
    const s = await stat(p);
    if (s.isDirectory()) files.push(...(await walk(p)));
    else files.push(p);
  }
  return files;
}

const files = await collect();
if (process.exitCode) process.exit(1);

/* ── kiểm tra 1: không được có đường dẫn tuyệt đối ──────
   Gateway IPFS hay phục vụ app dưới /ipfs/<CID>/. Một cái
   src="/assets/..." sẽ trỏ ra gốc gateway và 404 sạch. */
const ABS = [
  /\b(?:src|href)\s*=\s*"\/(?!\/)/,
  /url\(\s*\/(?!\/)/,
  /"(?:start_url|scope)"\s*:\s*"\//,
  /serviceWorker\.register\(\s*["']\//
];
let absHits = 0;
for (const f of files) {
  if (!TEXT.has(extname(f))) continue;
  const txt = await readFile(f, "utf8");
  txt.split(/\r?\n/).forEach((line, i) => {
    for (const re of ABS) {
      if (re.test(line)) {
        absHits++;
        fail(`đường dẫn tuyệt đối ${relative(ROOT, f)}:${i + 1}\n    ${line.trim().slice(0, 100)}`);
      }
    }
  });
}

/* ── kiểm tra 2: danh sách SHELL của sw.js phải khớp thật ──
   Dễ trôi nhất: thêm file mới mà quên khai vào SHELL, thế là
   app mất file đó khi offline mà không ai biết. */
const swTxt = await readFile(join(ROOT, "sw.js"), "utf8");
const shell = [...swTxt.matchAll(/^\s*"(\.\/[^"]+)"/gm)].map((m) => m[1]);
const present = new Set(files.map((f) => "./" + relative(ROOT, f).replace(/\\/g, "/")));
for (const s of shell) {
  if (s === "./") continue;
  if (!present.has(s)) fail(`sw.js khai "${s}" nhưng không có file đó`);
}
const shellSet = new Set(shell);
// sw.js không tự cache chính nó — trình duyệt quản lý riêng vòng đời của nó
const notCached = [...present].filter((p) => !shellSet.has(p) && p !== "./sw.js" && !/\.(png|ico)$/.test(p));
if (notCached.length) {
  log("  ⚠ có trong dist nhưng sw.js không cache: " + notCached.join(", "));
}

/* ── kiểm tra 3: số liệu còn tươi không ────────────────── */
const livePath = join(ROOT, "assets", "js", "data", "live.js");
if (existsSync(livePath)) {
  const m = (await readFile(livePath, "utf8")).match(/"generatedAt":\s*"([^"]+)"/);
  if (m) {
    const days = (Date.now() - new Date(m[1]).getTime()) / 864e5;
    log(`  số liệu sinh cách đây ${days.toFixed(1)} ngày` + (days > 2 ? "  ⚠ nên chạy npm run refresh trước" : ""));
  }
}

if (process.exitCode) {
  console.error("\nCó lỗi — KHÔNG ghi dist/. Sửa xong hãy chạy lại.");
  process.exit(1);
}

/* ── ghi dist ─────────────────────────────────────────── */
await rm(DIST, { recursive: true, force: true });
let bytes = 0;
for (const f of files) {
  const rel = relative(ROOT, f);
  const dest = join(DIST, rel);
  await mkdir(dirname(dest), { recursive: true });
  const buf = await readFile(f);
  await writeFile(dest, buf);
  bytes += buf.length;
}

log(`\n✓ dist/ · ${files.length} file · ${(bytes / 1024).toFixed(0)} KB`);
log("  đã kiểm: đường dẫn tương đối, danh sách cache của sw.js, độ tươi số liệu");
log("  bước sau: npm run pin  (cần PINATA_JWT)");
