/* Dịch loạt mục KHUÔN MẪU của kho ComposioHQ/awesome-claude-skills.

   Kho này có ~380 skill dùng chung đúng một câu mô tả:
     "Automate <Tên> tasks via Rube MCP (Composio). Always search tools first
      for current schemas."
   Chỉ đổi tên dịch vụ. Dịch tay từng cái là chép lại cùng một câu 380 lần,
   nên bản dịch của câu khuôn đó viết một lần ở đây rồi áp cho mọi mục khớp.

   KHÔNG phải dịch máy: câu tiếng Việt dưới đây do người viết, script chỉ
   thay tên dịch vụ. Mục nào KHÔNG khớp khuôn thì script bỏ qua và in ra để
   dịch tay — xem scripts/dich-tiep.md.

   Chạy:
     node scripts/dich-composio.mjs --thu   xem trước, không ghi
     node scripts/dich-composio.mjs         ghi vào dich/
*/
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const KHO = "ComposioHQ/awesome-claude-skills";
const TEP = join(ROOT, "tang-thu-cac/assets/data/dich/ComposioHQ__awesome-claude-skills.json");

/* Khuôn mô tả gốc. Bắt cả bản có lẫn không có câu "Always search tools…". */
const KHUON = /^Automate (.+?) tasks via Rube MCP \(Composio\)\.(?:\s*Always search tools first for current schemas\.)?\s*$/;

const TT = JSON.parse(
  (await readFile(join(ROOT, "tang-thu-cac/assets/js/data.js"), "utf8"))
    .match(/window\.TT_DATA\s*=\s*([\s\S]*);\s*$/)[1]
);

const cu = existsSync(TEP) ? JSON.parse(await readFile(TEP, "utf8")) : { kho: KHO, skills: {} };
const thu = process.argv.includes("--thu");

let them = 0;
const boQua = [];

for (const s of TT.skills || []) {
  if (s.kho !== KHO) continue;
  if (cu.skills[s.id]) continue;
  const m = KHUON.exec((s.moTa || "").trim());
  if (!m) { boQua.push(s.duong.split("/").pop() + " | " + (s.moTa || "").slice(0, 110)); continue; }
  const ten = m[1];
  cu.skills[s.id] = {
    tom: `Tự động hoá các thao tác ${ten} qua Rube MCP của Composio.`,
    lam: [
      `Gọi thao tác ${ten} từ agent`,
      "Tra danh sách công cụ trước để lấy lược đồ hiện hành",
    ],
    khi: `Bạn dùng ${ten} và muốn agent thao tác hộ.`,
  };
  them++;
}

if (!thu) {
  await mkdir(dirname(TEP), { recursive: true });
  await writeFile(TEP, JSON.stringify(cu, null, 2) + "\n");
}

console.log(`${KHO}: ${thu ? "sẽ thêm" : "thêm"} ${them} · tổng ${Object.keys(cu.skills).length}`);
if (boQua.length) {
  console.log(`\nKhông khớp khuôn — ${boQua.length} mục, dịch tay:`);
  for (const d of boQua) console.log("  " + d);
}
