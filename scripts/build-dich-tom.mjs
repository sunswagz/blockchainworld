/* Sinh CHỈ MỤC bản dịch cho màn danh sách.

   Vì sao cần: bản dịch đầy đủ nằm trong tang-thu-cac/assets/data/dich/,
   mỗi kho một tệp, nạp LƯỜI khi mở hồ sơ một skill. Cách đó đúng cho
   hồ sơ nhưng danh sách thì không dùng được: muốn biết skill nào đã có
   bản dịch, muốn hiện câu công dụng tiếng Việt ngay ngoài danh sách, và
   muốn bộ đếm "đã dịch / còn nguyên bản gốc" nói đúng — thì phải biết
   TẤT CẢ ngay từ đầu, không thể đợi người bấm vào từng cái.

   Tệp này gom đúng phần nhẹ nhất: id → câu "nó là gì". Bỏ lam/khi/ban
   (những mục dài) vì danh sách không hiện chúng; ai muốn đọc đủ thì mở
   hồ sơ, lúc đó tệp kho mới được nạp.

   Chạy:  node scripts/build-dich-tom.mjs
*/
import { readFile, readdir, writeFile } from "node:fs/promises";
import { existsSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DICH = join(ROOT, "tang-thu-cac", "assets", "data", "dich");
const RA = join(ROOT, "tang-thu-cac", "assets", "data", "dich-tom.json");

const TT = JSON.parse(
  (await readFile(join(ROOT, "tang-thu-cac/assets/js/data.js"), "utf8"))
    .match(/window\.TT_DATA\s*=\s*([\s\S]*);\s*$/)[1]
);
const hop = new Set((TT.skills || []).map((s) => s.id));

const tom = {};
const coBan = [];
let la = 0;

if (existsSync(DICH)) {
  for (const f of (await readdir(DICH)).sort()) {
    if (!f.endsWith(".json")) continue;
    const j = JSON.parse(await readFile(join(DICH, f), "utf8"));
    for (const [id, s] of Object.entries(j.skills || {})) {
      /* Id lạ = bản dịch trỏ vào skill không còn trong danh mục (kho gỡ
         skill, hoặc đổi đường dẫn). Bỏ qua chứ đừng ghi vào chỉ mục:
         ghi vào thì bộ đếm phồng lên mà không skill nào dùng tới. */
      if (!hop.has(id)) { la++; continue; }
      if (!s.tom) continue;
      tom[id] = s.tom;
      if (s.ban) coBan.push(id);
    }
  }
}

await writeFile(RA, JSON.stringify({ tom, coBan }) + "\n");

const kb = (statSync(RA).size / 1024).toFixed(0);
console.log(`dich-tom.json: ${Object.keys(tom).length} skill · ${coBan.length} có mục "với hệ thống" · ${kb} KB` +
  (la ? ` · bỏ ${la} id lạ` : ""));
