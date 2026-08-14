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
import { NGUON, NGAY_TOI_DA, tuoi } from "./tuoi-du-lieu.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DIST = join(ROOT, "dist");

/* Cổng Thành ở gốc; mỗi cung là một thư mục có index.html riêng.
   Thêm cung mới = thêm thư mục + một dòng ở đây. */
const GATE = ["index.html", "manifest.webmanifest", "sw.js", "assets"];
const HALLS = ["kinh-thanh", "dai-quan-trac", "do-sat-vien", "cong-bo", "tang-thu-cac", "hoang-thanh"];

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
  /* Bỏ qua ảnh và các file NẠP THEO YÊU CẦU. Đô Sát Viện có 21 file
     trong assets/js/v/ (~620 KB) mà mỗi lần xem chỉ dùng một; nạp
     sẵn hết vào SHELL là gấp ba dung lượng cài để lấy về thứ phần
     lớn người dùng không mở. Chúng rơi vào nhánh cache-trước-cập-
     nhật-nền ở cuối sw.js, xem tới đâu lưu tới đó. */
  const shellSet = new Set(shell);
  const missed = [...present].filter(
    (p) => !shellSet.has(p) && p !== "./sw.js" &&
      !/\.(png|ico)$/.test(p) && !/\/assets\/js\/v\//.test(p)
  );
  if (missed.length) {
    log(`  ⚠ ${relative(ROOT, baseDir) || "gốc"}: có trong dist nhưng sw.js không cache — ${missed.join(", ")}`);
  }
}

await checkShell(join(ROOT, "sw.js"), ROOT, gateFiles);
for (const h of HALLS) {
  await checkShell(join(ROOT, h, "sw.js"), join(ROOT, h), hallFiles[h]);
}

/* ── kiểm tra 3: độ tươi của dữ liệu tự sinh ─────────────
   Danh sách nguồn và ngưỡng nằm ở scripts/tuoi-du-lieu.mjs, dùng
   chung với `npm run kiem`. Trước đây mỗi bên một bản chép: ngưỡng
   ở đây là 2 ngày, còn cả repo thì không có bên nào khác canh cả.
   Hoàng Thành sinh bằng TAY (`npm run hoangthanh`, nguồn ngoài repo)
   nên cũ là bình thường — cờ botSinh đánh dấu chuyện đó. */
for (const n of NGUON) {
  const t = await tuoi(ROOT, n.duong);
  if (!t.co) { log(`  · ${n.nhan}: chưa chạy lần nào`); continue; }
  log(`  · ${n.nhan}: sinh cách đây ${t.ngay.toFixed(1)} ngày`
    + (n.botSinh && t.ngay > NGAY_TOI_DA ? "  ⚠" : "")
    + (n.botSinh ? "" : "  (sinh tay, cũ là bình thường)"));
}

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
