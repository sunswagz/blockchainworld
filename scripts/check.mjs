/* Kiểm cú pháp mọi file JS được trình duyệt nạp, ở cả Cổng Thành
   lẫn từng cung. Chạy: npm run check

   Quét theo thư mục thay vì liệt kê tay, để thêm file mới không
   phải nhớ cập nhật danh sách — đúng loại việc mà con người quên. */

import { readdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(execFile);
const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");

const AREAS = ["assets", "kinh-thanh", "dai-quan-trac", "scripts"];
const LOOSE = ["sw.js", "server.js", "kinh-thanh/sw.js", "dai-quan-trac/sw.js"];

async function walk(dir, out = []) {
  for (const name of await readdir(dir)) {
    const p = join(dir, name);
    const s = await stat(p);
    if (s.isDirectory()) await walk(p, out);
    else if (/\.m?js$/.test(name)) out.push(p);
  }
  return out;
}

const files = [];
for (const a of AREAS) {
  const p = join(ROOT, a);
  if (existsSync(p)) files.push(...(await walk(p)));
}
for (const f of LOOSE) {
  const p = join(ROOT, f);
  if (existsSync(p)) files.push(p);
}

let bad = 0;
for (const f of files) {
  try {
    await run(process.execPath, ["--check", f]);
  } catch (e) {
    bad++;
    console.error(`✗ ${relative(ROOT, f)}\n${(e.stderr || "").trim().split("\n").slice(0, 3).join("\n")}`);
  }
}

if (bad) {
  console.error(`\n${bad}/${files.length} file lỗi cú pháp.`);
  process.exit(1);
}
console.log(`✓ ${files.length} file JS đều hợp lệ`);
