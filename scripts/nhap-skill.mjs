/* ═══════════════════════════════════════════════════════
   M11 · KHO DỤNG CỤ — nhập skill từ Tàng Thư Các vào repo.

   Tàng Thư Các quét 3.656 skill từ 66 kho, xếp hạng, dịch tóm tắt —
   rồi để đó. Không có `.claude/skills/` nên KHÔNG phiên nào, kể cả
   bot, gọi được một cái nào. Nó là catalogue chứ chưa là kho dụng cụ.

   File này nối chỗ đứt đó: chọn skill đầu bảng theo nhóm, tải về
   `.claude/skills/`, ghi sổ xuất xứ. Từ đó mọi phiên Claude trong
   repo — người lẫn bot — dùng được.

   ── BỐN CHỐT AN TOÀN, VÌ ĐÂY LÀ MÃ CỦA NGƯỜI LẠ ──────────────
   Skill không phải dữ liệu để đọc. Nó là CHỈ DẪN mà model sẽ làm
   theo. Tải bừa về là mở cửa cho người lạ viết lệnh vào phiên của
   mình. Nên:

     1. CHỈ `SKILL.md`. Không tải script, không tải file kèm. Chỉ dẫn
        thì đọc được và soát được; script thì không.
     2. Sàn sao + chỉ kho đã nằm trong catalogue. Không nhận đường
        dẫn tuỳ ý.
     3. Trần mỗi kho. Không có nó thì một kho 241K sao (affaan-m/ECC)
        chiếm sạch kệ, và ta được 12 bản sao của cùng một giọng.
     4. Sổ xuất xứ `factory/skills.json`: lấy từ đâu, lúc nào, sha256
        bao nhiêu. Đổi nội dung là thấy ngay ở diff.

   Mỗi file nhập về đội thêm một khối đầu ghi rõ nó là hàng ngoài.
   ═══════════════════════════════════════════════════════ */

import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const NGUON = join(ROOT, "tang-thu-cac", "assets", "js", "data.js");
const KE = join(ROOT, ".claude", "skills");
const SO = join(ROOT, "factory", "skills.json");

/* Nhóm nào đáng có trên kệ. Xưởng này cần cải thiện giao diện và
   chất lượng, nên bốn nhóm này — không phải cả chín. */
const NHOM_CAN = ["giao-dien", "kiem-thu", "tai-lieu", "lap-trinh"];
const SAN_SAO = 500;
const TRAN_MOI_KHO = 2;
const TRAN_TONG = 12;

function docCatalogue() {
  const hop = { window: {} };
  vm.createContext(hop);
  vm.runInContext(readFileSync(NGUON, "utf8"), hop, { timeout: 8000 });
  const d = hop.window.TT_DATA;
  if (!d || !Array.isArray(d.skills)) throw new Error("không đọc được TT_DATA.skills");
  return d;
}

/* Chọn: chính chủ trước, rồi sao giảm dần, và không kho nào được
   quá TRAN_MOI_KHO suất. */
function chon(d) {
  const nhanhTheoKho = Object.fromEntries((d.kho || []).map((k) => [k.id, k.nhanh || "main"]));
  const ung = d.skills
    .filter((k) => NHOM_CAN.includes(k.nhom) && (k.sao || 0) >= SAN_SAO && k.kho && k.duong)
    .sort((a, b) => (b.chinhChu ? 1 : 0) - (a.chinhChu ? 1 : 0) || (b.sao || 0) - (a.sao || 0));

  const dem = {};
  const lay = [];
  for (const k of ung) {
    if (lay.length >= TRAN_TONG) break;
    if ((dem[k.kho] || 0) >= TRAN_MOI_KHO) continue;
    dem[k.kho] = (dem[k.kho] || 0) + 1;
    lay.push({ ...k, nhanh: nhanhTheoKho[k.kho] || "main" });
  }
  return lay;
}

/* Tên thư mục = tên skill. Trùng tên giữa hai kho thì thêm tên chủ —
   catalogue đã có sẵn cờ `trungTen` cho đúng chuyện này. */
function tenKe(k, dsan) {
  const tho = String(k.ten || "").toLowerCase().replace(/[^a-z0-9-]/g, "-").replace(/-+/g, "-");
  const trung = dsan.filter((x) => x !== k && String(x.ten).toLowerCase() === String(k.ten).toLowerCase());
  return trung.length ? `${k.kho.split("/")[0].toLowerCase()}-${tho}` : tho;
}

const CHO_PHEP = /^[a-zA-Z0-9._\/-]+$/;

async function tai(k) {
  if (!CHO_PHEP.test(k.kho) || !CHO_PHEP.test(k.duong) || k.duong.includes(".."))
    throw new Error("đường dẫn có ký tự lạ — bỏ");
  const url = `https://raw.githubusercontent.com/${k.kho}/${k.nhanh}/${k.duong}/SKILL.md`;
  const res = await fetch(url, { headers: { "user-agent": "blockchainworld-nha-may" } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const noi = await res.text();
  if (!noi.trim()) throw new Error("SKILL.md rỗng");
  if (noi.length > 200_000) throw new Error(`quá to (${noi.length} byte)`);
  return { noi, url };
}

const d = docCatalogue();
const ds = chon(d);
console.log(`Kệ dụng cụ: chọn ${ds.length} skill từ ${new Set(ds.map((x) => x.kho)).size} kho` +
            ` (nhóm ${NHOM_CAN.join("/")}, sàn ${SAN_SAO} sao, trần ${TRAN_MOI_KHO}/kho)\n`);

let soCu = { generatedAt: null, skill: [] };
if (existsSync(SO)) { try { soCu = JSON.parse(await readFile(SO, "utf8")); } catch {} }
const shaCu = Object.fromEntries((soCu.skill || []).map((s) => [s.id, s.sha]));

const so = [];
let moi = 0, doi = 0, giu = 0, hong = 0;

for (const k of ds) {
  const ten = tenKe(k, ds);
  let t;
  try { t = await tai(k); }
  catch (e) { hong++; console.log(`  ✗ ${String(k.ten).padEnd(28)} ${e.message}`); continue; }

  const sha = createHash("sha256").update(t.noi).digest("hex").slice(0, 16);
  const dau =
    `<!-- ═══ HÀNG NGOÀI — nhập tự động, ĐỪNG SỬA TAY ═══\n` +
    `     Kho    : ${k.kho} (${k.sao.toLocaleString("vi-VN")} sao)\n` +
    `     Đường  : ${k.duong}\n` +
    `     Giấy phép: ${k.giayPhep || "không khai"}\n` +
    `     Nguồn  : ${t.url}\n` +
    `     sha256 : ${sha} · nhập ${new Date().toISOString()}\n` +
    `     Sinh bởi scripts/nhap-skill.mjs. Sổ: factory/skills.json\n` +
    `     Đây là chỉ dẫn do người ngoài viết — đọc trước khi tin. ═══ -->\n\n`;

  const duongKe = join(KE, ten, "SKILL.md");
  await mkdir(dirname(duongKe), { recursive: true });
  await writeFile(duongKe, dau + t.noi, "utf8");

  if (!shaCu[k.id]) { moi++; console.log(`  + ${ten.padEnd(28)} ${k.kho}`); }
  else if (shaCu[k.id] !== sha) { doi++; console.log(`  ~ ${ten.padEnd(28)} đổi nội dung`); }
  else giu++;

  so.push({ id: k.id, ten, kho: k.kho, duong: k.duong, nhom: k.nhom,
            sao: k.sao, giayPhep: k.giayPhep || null, nhanh: k.nhanh,
            sha, luc: new Date().toISOString() });
}

if (!so.length) {
  console.error("\nKhông nhập được skill nào — giữ nguyên kệ cũ.");
  process.exit(1);
}

await mkdir(dirname(SO), { recursive: true });
await writeFile(SO, JSON.stringify({
  generatedAt: new Date().toISOString(),
  ghiChu: "SINH TỰ ĐỘNG bởi scripts/nhap-skill.mjs — sổ xuất xứ của .claude/skills/.",
  luat: { nhom: NHOM_CAN, sanSao: SAN_SAO, tranMoiKho: TRAN_MOI_KHO, tranTong: TRAN_TONG },
  skill: so
}, null, 2) + "\n", "utf8");

console.log(`\n✓ kệ có ${so.length} skill · ${moi} mới · ${doi} đổi · ${giu} giữ nguyên` +
            (hong ? ` · ${hong} hỏng` : ""));
