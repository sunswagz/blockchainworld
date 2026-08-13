/* ═══════════════════════════════════════════════════════
   Gom Cổng Thành + các cung thành dist/.

   Chạy: npm run dist

   dist/ chỉ chứa thứ trình duyệt cần. Không có scripts/,
   .github/, README, server.js.

   Kèm các lớp kiểm tra chạy TRƯỚC khi ghi, vì một khi đã pin
   lên IPFS thì CID sai không rút lại được — và vì một cung
   khai thiếu file trong sw.js sẽ hỏng offline mà không báo.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir, rm, readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join, relative, extname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIST = join(ROOT, "dist");

/* Cổng Thành ở gốc; mỗi cung là một thư mục có index.html riêng.
   Thêm cung mới = thêm thư mục + một dòng ở đây. */
const GATE = ["index.html", "manifest.webmanifest", "sw.js", "assets"];
const HALLS = ["kinh-thanh", "dai-quan-trac", "do-sat-vien"];

const TEXT = new Set([".html", ".css", ".js", ".mjs", ".json", ".webmanifest", ".svg", ".md"]);

const log = (...a) => console.log(...a);
const fail = (msg) => { console.error("  ✗ " + msg); process.exitCode = 1; };

async function walk(dir, out = []) {
  for (const name of await readdir(dir)) {
    const p = join(dir, name);
    const s = await stat(p);
    if (s.isDirectory()) await walk(p, out);
    else out.push(p);
  }
  return out;
}

async function collect(items, base = ROOT) {
  const files = [];
  for (const item of items) {
    const p = join(base, item);
    if (!existsSync(p)) { fail(`thiếu ${relative(ROOT, p)}`); continue; }
    const s = await stat(p);
    if (s.isDirectory()) files.push(...(await walk(p)));
    else files.push(p);
  }
  return files;
}

const gateFiles = await collect(GATE);
const hallFiles = {};
for (const h of HALLS) {
  if (!existsSync(join(ROOT, h))) { fail(`thiếu cung ${h}/`); continue; }
  hallFiles[h] = await walk(join(ROOT, h));
}
if (process.exitCode) process.exit(1);

const allFiles = [...gateFiles, ...Object.values(hallFiles).flat()];

/* ── kiểm tra 1: không có đường dẫn tuyệt đối ───────────
   Gateway IPFS hay phục vụ dưới /ipfs/<CID>/. Một cái
   src="/assets/..." sẽ trỏ ra gốc gateway và 404 sạch. */
const ABS = [
  /\b(?:src|href)\s*=\s*"\/(?!\/)/,
  /url\(\s*\/(?!\/)/,
  /"(?:start_url|scope)"\s*:\s*"\//,
  /serviceWorker\.register\(\s*["']\//
];
for (const f of allFiles) {
  if (!TEXT.has(extname(f))) continue;
  const txt = await readFile(f, "utf8");
  txt.split(/\r?\n/).forEach((line, i) => {
    for (const re of ABS) {
      if (re.test(line)) {
        fail(`đường dẫn tuyệt đối ${relative(ROOT, f)}:${i + 1}\n      ${line.trim().slice(0, 90)}`);
      }
    }
  });
}

/* ── kiểm tra 2: SHELL của mỗi sw.js phải khớp thật ─────
   Mỗi cung có sw.js riêng; đường dẫn trong SHELL là tương
   đối với thư mục của chính cung đó. */
async function checkShell(swPath, baseDir, files) {
  const swTxt = await readFile(swPath, "utf8");
  const shell = [...swTxt.matchAll(/^\s*"(\.\/[^"]+)"/gm)].map((m) => m[1]);
  const present = new Set(
    files.map((f) => "./" + relative(baseDir, f).replace(/\\/g, "/"))
  );
  for (const s of shell) {
    if (s === "./") continue;
    if (!present.has(s)) fail(`${relative(ROOT, swPath)} khai "${s}" nhưng không có file đó`);
  }
  const shellSet = new Set(shell);
  const missed = [...present].filter(
    (p) => !shellSet.has(p) && p !== "./sw.js" && !/\.(png|ico)$/.test(p)
  );
  if (missed.length) {
    log(`  ⚠ ${relative(ROOT, baseDir) || "gốc"}: có trong dist nhưng sw.js không cache — ${missed.join(", ")}`);
  }
}

await checkShell(join(ROOT, "sw.js"), ROOT, gateFiles);
for (const h of HALLS) {
  await checkShell(join(ROOT, h, "sw.js"), join(ROOT, h), hallFiles[h]);
}

/* ── kiểm tra 3: độ tươi của dữ liệu tự sinh ───────────── */
async function freshness(label, path, key) {
  if (!existsSync(path)) return;
  const m = (await readFile(path, "utf8")).match(new RegExp(`"${key}":\\s*"([^"]+)"`));
  if (!m) { log(`  · ${label}: chưa chạy lần nào`); return; }
  const days = (Date.now() - new Date(m[1]).getTime()) / 864e5;
  log(`  · ${label}: sinh cách đây ${days.toFixed(1)} ngày` + (days > 2 ? "  ⚠" : ""));
}
await freshness("số liệu Kinh Thành", join(ROOT, "kinh-thanh/assets/js/data/live.js"), "generatedAt");
await freshness("bản quét Quan Trắc", join(ROOT, "dai-quan-trac/assets/js/scan.js"), "generatedAt");
await freshness("bảng xét Đô Sát Viện", join(ROOT, "do-sat-vien/assets/js/data.js"), "generatedAt");

if (process.exitCode) {
  console.error("\nCó lỗi — KHÔNG ghi dist/. Sửa xong hãy chạy lại.");
  process.exit(1);
}

/* ── ghi dist ─────────────────────────────────────────── */
await rm(DIST, { recursive: true, force: true });
let bytes = 0;
for (const f of allFiles) {
  const dest = join(DIST, relative(ROOT, f));
  await mkdir(dirname(dest), { recursive: true });
  const buf = await readFile(f);
  await writeFile(dest, buf);
  bytes += buf.length;
}

log(`\n✓ dist/ · ${allFiles.length} file · ${(bytes / 1024).toFixed(0)} KB`);
log(`  Cổng Thành ${gateFiles.length} file` +
  HALLS.map((h) => ` · ${h} ${hallFiles[h].length}`).join(""));
log("  bước sau: npm run pin  (cần PINATA_JWT)");
