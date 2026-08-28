/* ═══════════════════════════════════════════════════════
   THỬ CỔNG — bắn bốn bản vá giả vào cổng chặn tri thức và
   xem nó nhận/trả đúng không.

       node knowledge-os/thu-cong.mjs        thoát 1 nếu có kịch bản sai

   ── VÌ SAO CÓ FILE NÀY ───────────────────────────────────────
   Cổng chặn là thứ duy nhất đứng giữa model và dữ liệu tri thức. Nó
   sai theo hướng chặt thì lượt tiến hoá nào cũng bị trả lại và không
   ai biết vì sao; sai theo hướng lỏng thì dữ liệu hỏng đi thẳng vào
   `main` với một dòng "✓ qua cả ba phép".

   Không thử được bằng cách nhìn: cổng có ba lớp, mỗi lớp gọi một tiến
   trình con, và lớp thứ hai so với một phiếu chụp TRƯỚC khi sửa. Cách
   duy nhất biết nó còn đúng là bắn vào nó những bản vá đã biết trước
   đáp án.

   Bản đầu của bộ thử này chỉ sống trong thư mục tạm của một phiên, và
   đúng phiên ấy phát hiện cổng nhận nhầm một bản vá trùng id ở lớp
   2026. Bộ thử nằm ngoài repo thì lần sau không ai chạy lại được.

   ── LUÔN TRẢ ĐĨA VỀ NGUYÊN TRẠNG ─────────────────────────────
   Mỗi kịch bản chép ba tệp model được sửa ra chỗ tạm, sửa bản trên
   đĩa, chạy cổng, rồi chép trả. `finally` chứ không phải cuối hàm:
   cổng gọi process.exit trong tiến trình con nên ném lỗi là chuyện
   bình thường, mà ném xong không trả tệp là bỏ lại một repo bẩn.
   ═══════════════════════════════════════════════════════ */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const GOI = dirname(fileURLToPath(import.meta.url));
const SUA = [
  "data/bridges/repo.json",
  "data/2026/concepts.json",
  "data/2026/relations.json",
  "data/concepts/core.json",     /* lớp sách — kịch bản 3 cố tình chạm vào */
];
const GOC_JSON = join(GOI, "data", "phieu-thu-cong.json");

function chay(args) {
  try {
    return { ma: 0, ra: execFileSync(process.execPath, [join(GOI, "do.mjs"), ...args],
      { encoding: "utf8", stdio: "pipe" }) };
  } catch (e) {
    return { ma: e.status ?? 1, ra: String(e.stdout || "") + String(e.stderr || "") };
  }
}

function doc(p) { return readFileSync(join(GOI, p), "utf8"); }
const ds = (x) => (Array.isArray(x) ? x : x.concepts || x.relations || x.items || []);

/* Chụp phiếu gốc một lần, dùng chung cho cả bốn kịch bản — đúng như
   workflow làm: `--ghi` ở bước ra đề, `--so` ở bước cổng. */
chay(["--ghi", GOC_JSON]);

const KICH_BAN = [
  {
    ten: "bản vá THẬT: thêm một phán quyết 2026 hợp lệ",
    mong: 0,
    sua() {
      const p = "data/2026/relations.json";
      const j = JSON.parse(doc(p));
      const a = ds(j);
      a.push({
        from: "stablecoin_settlement", relation: "extends", to: "salability",
        reason_vi: "Bản thử — không giữ lại.",
        source_type: "repo", source_ref: "ho-bo/assets/js/v/dong-tien.js",
        confidence: "medium",
      });
      writeFileSync(join(GOI, p), JSON.stringify(j, null, 2) + "\n");
    },
  },
  {
    ten: "TỤT: xoá bớt quan hệ 2026 đang có",
    mong: 1,
    sua() {
      const p = "data/2026/relations.json";
      const j = JSON.parse(doc(p));
      ds(j).splice(0, 6);
      writeFileSync(join(GOI, p), JSON.stringify(j, null, 2) + "\n");
    },
  },
  {
    ten: "NGOÀI PHẠM VI: chạm vào lớp sách",
    mong: 1,
    sua() {
      const p = "data/concepts/core.json";
      const j = JSON.parse(doc(p));
      ds(j).push({
        id: "khai_niem_bia", label_en: "Made up", label_vi: "Bịa",
        kind: "foundation", definition_vi: "Bản thử.",
        source_chapters: [3], source_pages: [91], stance: "source",
      });
      writeFileSync(join(GOI, p), JSON.stringify(j, null, 2) + "\n");
    },
  },
  {
    ten: "DỮ LIỆU HỎNG: trùng id ngay trong lớp 2026",
    mong: 1,
    sua() {
      const p = "data/2026/concepts.json";
      const j = JSON.parse(doc(p));
      const a = ds(j);
      a.push(JSON.parse(JSON.stringify(a[0])));
      writeFileSync(join(GOI, p), JSON.stringify(j, null, 2) + "\n");
    },
  },
];

let hong = 0;
for (const kb of KICH_BAN) {
  const luu = SUA.map((p) => [p, doc(p)]);
  let kq;
  try {
    kb.sua();
    kq = chay(["cong", "--so", GOC_JSON]);
  } finally {
    for (const [p, t] of luu) writeFileSync(join(GOI, p), t);
  }
  const dung = kq.ma === kb.mong;
  if (!dung) hong++;
  console.log(`${dung ? "✓" : "✗"} ${kb.ten}`);
  console.log(`     mong thoát ${kb.mong}, thật ${kq.ma}` +
    (dung ? "" : `\n     ${kq.ra.split("\n").filter((x) => x.trim()).slice(-3).join("\n     ")}`));
}

/* Cổng vừa chạy `sinh.mjs` thật ở kịch bản được NHẬN, nên lát cắt trên
   đĩa có thể đã dựng lại từ dữ liệu giả. Dựng lại lần cuối từ dữ liệu
   ĐÃ TRẢ để không bỏ lại một repo bẩn. */
try { execFileSync(process.execPath, [join(GOI, "sinh.mjs")], { stdio: "pipe" }); } catch { }
if (existsSync(GOC_JSON)) { try { (await import("node:fs")).unlinkSync(GOC_JSON); } catch { } }

console.log(hong ? `\n✗ ${hong}/${KICH_BAN.length} kịch bản SAI.` : `\n✓ Cả ${KICH_BAN.length} kịch bản đúng.`);
process.exit(hong ? 1 : 0);
