/* Gộp một lô bản dịch (khoá theo TÊN skill) vào file dich/<kho>.json
   (khoá theo ID đầy đủ).

   Vì sao khoá theo tên rồi mới nối id: id là `kho/đường/dẫn/dài/dòng`,
   chép tay 60 cái là chắc chắn sai một cái, và sai thì im lặng —
   bản dịch không bao giờ hiện ra mà không có lỗi nào báo.

   Chạy: node scripts/dich-gop.mjs <kho> <lô.json>
*/
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const R = join(dirname(fileURLToPath(import.meta.url)), "..") + "/";
const DICH = R + "tang-thu-cac/assets/data/dich/";
const [kho, loFile] = process.argv.slice(2);
if (!kho || !loFile) { console.error("cần: <kho> <lô.json>"); process.exit(1); }

const TT = JSON.parse(
  readFileSync(R + "tang-thu-cac/assets/js/data.js", "utf8")
    .match(/window\.TT_DATA\s*=\s*([\s\S]*);\s*$/)[1]
);
const lo = JSON.parse(readFileSync(loFile, "utf8"));

/* Tra tên → id trong đúng kho này. Tên có thể trùng giữa các kho,
   nên PHẢI lọc theo kho trước — đây chính là lỗi từng làm hai skill
   mượn bản dịch của nhau. */
const cuaKho = (TT.skills || []).filter((s) => s.kho === kho);
const theoTen = new Map();
for (const s of cuaKho) {
  const ten = s.duong.split("/").pop();
  if (theoTen.has(ten)) theoTen.set(ten, null);   /* trùng tên trong cùng kho → bỏ, không đoán */
  else theoTen.set(ten, s.id);
}

const ten = kho.replace(/\//g, "__").replace(/[^A-Za-z0-9_.-]/g, "_") + ".json";
const p = join(DICH, ten);
let cu = {};
if (existsSync(p)) cu = JSON.parse(readFileSync(p, "utf8")).skills || {};

let them = 0; const lac = [], mo = [];
for (const [t, d] of Object.entries(lo)) {
  const id = theoTen.get(t);
  if (!id) { lac.push(t); continue; }
  if (!d.tom || !d.lam || !d.lam.length || !d.khi) { mo.push(t); continue; }
  cu[id] = d;                                     /* KHÔNG có may: 1 — viết tay */
  them++;
}

mkdirSync(DICH, { recursive: true });
writeFileSync(p, JSON.stringify({ kho, luc: new Date().toISOString(),
  nguon: "viết tay trong phiên, đọc mô tả gốc", skills: cu }), "utf8");

console.log(`${kho}: thêm ${them} · tổng ${Object.keys(cu).length}`);
if (lac.length) console.log("  ✗ không khớp tên: " + lac.join(", "));
if (mo.length) console.log("  ✗ thiếu trường: " + mo.join(", "));

/* Sinh lại chỉ mục NGAY, đừng để thành một bước phải nhớ.
   Quên bước này thì bản dịch nằm trên đĩa mà màn danh mục vẫn báo "còn
   nguyên bản gốc" — đúng lỗi đã xảy ra khi dịch xong 2.859 cái mà danh
   sách không hay biết. Máy làm hộ thì không quên được. */
const { execFileSync } = await import("node:child_process");
execFileSync(process.execPath, [join(R, "scripts", "build-dich-tom.mjs")], { stdio: "inherit" });
