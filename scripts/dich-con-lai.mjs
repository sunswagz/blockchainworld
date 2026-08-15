/* Còn bao nhiêu skill chưa dịch, và in mô tả để dịch tiếp.

   Chạy:
     node scripts/dich-con-lai.mjs              thống kê
     node scripts/dich-con-lai.mjs <kho> [n]    in n mô tả của một kho

   Xem scripts/dich-tiep.md để biết cách ghi kết quả và cách viết mục
   "Với hệ thống của bạn".
*/
import { readFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DICH = join(ROOT, "tang-thu-cac", "assets", "data", "dich");

const TT = JSON.parse(
  (await readFile(join(ROOT, "tang-thu-cac/assets/js/data.js"), "utf8"))
    .match(/window\.TT_DATA\s*=\s*([\s\S]*);\s*$/)[1]
);

/* Hai kho này dịch TAY đủ bốn mục trong glossary.js — không nằm trong
   phạm vi việc này. */
const TAY = new Set(["anthropics/skills", "anthropics/claude-plugins-official"]);

const xong = new Set();
let coBan = 0;
if (existsSync(DICH)) {
  for (const f of await readdir(DICH)) {
    if (!f.endsWith(".json")) continue;
    const j = JSON.parse(await readFile(join(DICH, f), "utf8"));
    for (const [id, s] of Object.entries(j.skills || {})) {
      xong.add(id);
      if (s.ban) coBan++;
    }
  }
}

const cd = (TT.skills || []).filter((s) => !TAY.has(s.kho));
const conLai = cd.filter((s) => !xong.has(s.id));

const [kho, soStr] = process.argv.slice(2);

if (!kho) {
  console.log(`đã dịch : ${xong.size} / ${cd.length}   (${coBan} có mục "với hệ thống")`);
  console.log(`còn lại : ${conLai.length}\n`);
  const dem = {};
  for (const s of conLai) dem[s.kho] = (dem[s.kho] || 0) + 1;
  for (const [k, n] of Object.entries(dem).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${String(n).padStart(4)}  ${k}`);
  }
  console.log("\nIn mô tả để dịch:  node scripts/dich-con-lai.mjs <kho> [số]");
  process.exit(0);
}

const lo = conLai.filter((s) => s.kho === kho).slice(0, Number(soStr) || 60);
if (!lo.length) { console.log(`${kho}: không còn gì để dịch.`); process.exit(0); }

console.log(`=== ${kho} · ${lo.length} skill ===`);
for (const s of lo) {
  /* Chỉ in TÊN, không in id: dich-gop.mjs tra ngược tên → id, nên
     người dịch không bao giờ phải chạm vào id. */
  console.log(s.duong.split("/").pop() + " | " + (s.moTa || "").replace(/\s+/g, " ").slice(0, 140));
}
