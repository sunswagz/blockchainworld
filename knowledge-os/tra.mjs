/* ═══════════════════════════════════════════════════════
   Tra cứu Knowledge OS ở dòng lệnh.

       node knowledge-os/tra.mjs khai-niem price_signal
       node knowledge-os/tra.mjs tim "lãi suất"
       node knowledge-os/tra.mjs cung thi-bac-ty
       node knowledge-os/tra.mjs vai-von time_price
       node knowledge-os/tra.mjs 2026

   Đây là công cụ ĐỌC, không ghi gì. Nó để trả lời một câu hỏi hay
   gặp khi đang sửa một cung: "khái niệm này đang nối vào đâu, và
   dòng nào là của sách, dòng nào là mình suy ra?"

   Mọi thứ in ra đều kèm nhãn nguồn. Không có chế độ nào in ra một
   câu mà không nói câu đó đến từ đâu — đó là cả điểm của gói này.
   ═══════════════════════════════════════════════════════ */

import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const GOI = dirname(fileURLToPath(import.meta.url));
const json = async (p) => JSON.parse(await readFile(join(GOI, p), "utf8"));

const C = await json("data/concepts/core.json");
const R = await json("data/relations/core.json");
const B = await json("data/bridges/repo.json");
const K = await json("data/bridges/capital-os.json");
const C26 = await json("data/2026/concepts.json");
const R26 = await json("data/2026/relations.json");

const BANG = new Map([...C, ...C26].map((x) => [x.id, x]));
const MOI = [...R, ...R26];

const NHAN = {
  source: "sách", author_claim: "tác giả", analysis: "phân tích", repo: "repo", web: "web",
  book: "sách"
};
const nhan = (x) => `[${NHAN[x] || x}]`;

function viTri(x) {
  if (x.source_chapters?.length) return `ch.${x.source_chapters.join(",")} tr.${(x.source_pages || []).join(",")}`;
  if (x.chapters?.length) return `ch.${x.chapters.join(",")} tr.${(x.pages || []).join(",")}`;
  return x.source_ref || "";
}

function inKhaiNiem(id) {
  const x = BANG.get(id);
  if (!x) return loi(`Không có khái niệm "${id}".`);
  console.log(`${x.label_vi} · ${x.label_en}  ${nhan(x.stance)}  ${viTri(x)}`);
  console.log(`  loại: ${x.kind}`);
  console.log(`  ${x.definition_vi}\n`);

  const noi = MOI.filter((r) => r.from === id || r.to === id);
  if (!noi.length) { console.log("  (chưa nối vào đâu)"); return; }
  console.log(`  ${noi.length} quan hệ:`);
  for (const r of noi) {
    const kia = r.from === id ? r.to : r.from;
    const mui = r.from === id ? "→" : "←";
    const t = BANG.get(kia);
    console.log(`    ${mui} ${(t ? t.label_vi : kia).padEnd(28)} ${r.relation.padEnd(18)} ` +
      `${nhan(r.source_type)} ${r.confidence}`);
    console.log(`       ${r.reason_vi}`);
  }
}

function inTim(q) {
  const t = (q || "").toLowerCase();
  if (!t) return loi("Thiếu từ khoá.");
  const ra = [...C, ...C26].filter((x) =>
    x.id.includes(t) ||
    (x.label_en || "").toLowerCase().includes(t) ||
    x.label_vi.toLowerCase().includes(t) ||
    x.definition_vi.toLowerCase().includes(t));
  if (!ra.length) return console.log(`Không có gì khớp "${q}".`);
  console.log(`${ra.length} khái niệm khớp "${q}":\n`);
  for (const x of ra) console.log(`  ${x.id.padEnd(26)} ${x.label_vi.padEnd(30)} ${nhan(x.stance)}`);
}

function inCung(ten) {
  const h = B.hall_mappings.find((x) => x.hall === ten);
  if (!h) return loi(`Cung "${ten}" chưa có cầu nối.\n  Đang có: ` +
    B.hall_mappings.map((x) => x.hall).join(", "));
  console.log(`${h.hall} — ${h.role_vi}   [phân tích]`);
  console.log(`  ${h.example_vi}\n`);
  console.log("  khái niệm mức cung:");
  for (const i of h.concepts) {
    const x = BANG.get(i);
    console.log(`    ${i.padEnd(26)} ${(x ? x.label_vi : "?").padEnd(30)} ${x ? nhan(x.stance) : ""}`);
  }
  if (!h.rooms?.length) return console.log("\n  (chưa ánh xạ phòng nào)");
  console.log(`\n  ${h.rooms.length} phòng đã ánh xạ:`);
  for (const p of h.rooms) {
    console.log(`\n    ${p.id} · ${p.name_vi}`);
    console.log(`      ${p.note_vi}`);
    console.log(`      → ${p.concepts.join(", ")}`);
  }
}

function inVaiVon(ma) {
  const r = K.roles.find((x) => x.id === ma);
  if (!r) return loi(`Không có vai vốn "${ma}".\n  Đang có: ` + K.roles.map((x) => x.id).join(", "));
  console.log(`${r.id} · ${r.label_vi}   [phân tích]\n`);
  for (const i of r.concepts) {
    const x = BANG.get(i);
    console.log(`  ${i.padEnd(26)} ${(x ? x.label_vi : "?").padEnd(30)} ${x ? nhan(x.stance) : ""}`);
  }
  if (r.systems?.length) console.log(`\n  hệ thống: ${r.systems.join(" · ")}`);
}

function in2026() {
  console.log(`Lớp 2026 — ${C26.length} khái niệm, ${R26.length} quan hệ.`);
  console.log("Không dòng nào ở đây là lời của sách; sách viết năm 2018.\n");
  for (const x of C26) {
    console.log(`  ${x.label_vi} · ${x.label_en}  ${nhan(x.stance)}`);
    console.log(`    ${x.definition_vi}`);
    console.log(`    nguồn: ${x.source_ref}`);
    for (const r of R26.filter((y) => y.from === x.id)) {
      const t = BANG.get(r.to);
      console.log(`      ${r.relation.padEnd(11)} ${(t ? t.label_vi : r.to).padEnd(28)} ${r.confidence}`);
    }
    console.log();
  }
}

function loi(m) {
  console.error(m);
  process.exitCode = 1;
}

const [lenh, tham] = process.argv.slice(2);
if (lenh === "khai-niem") inKhaiNiem(tham);
else if (lenh === "tim") inTim(tham);
else if (lenh === "cung") inCung(tham);
else if (lenh === "vai-von") inVaiVon(tham);
else if (lenh === "2026") in2026();
else {
  console.error("node knowledge-os/tra.mjs khai-niem <id> | tim <từ> | cung <tên> | vai-von <id> | 2026");
  process.exit(2);
}
