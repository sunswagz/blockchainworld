/* ═══════════════════════════════════════════════════════
   DÒ KHO — lục Tàng Thư Các tìm kỹ năng CHƯA khai thác.

   Chạy:
     node scripts/do-kho.mjs quet          soi kho, ra đề xuất
     node scripts/do-kho.mjs so            xem sổ đã khai thác
     node scripts/do-kho.mjs ghi <tên>...  đánh dấu đã khai thác

   ── VÌ SAO CÓ FILE NÀY ────────────────────────────────
   `tien-hoa.mjs ky-nang` đã biết chọn kỹ năng — nhưng nó chỉ chọn
   theo THƯỚC ĐANG TRƯỢT. Nghĩa là nó chỉ tìm được thứ hợp với những
   phép canh ta ĐÃ CÓ, và không bao giờ tìm ra thứ đáng canh mà ta
   chưa nghĩ tới.

   Đó là trần thật của vòng tiến hoá: cung nào đạt hết thước thì
   model được bảo "tìm một chỗ không thước nào đo được" — lời dặn mơ
   hồ nhất trong cả prompt. Trần đó không phá được bằng cách sửa
   prompt; phải có nguồn ý tưởng MỚI chảy vào.

   Kho Tàng Thư Các là nguồn đó: 3.696 kỹ năng người khác viết ra từ
   kinh nghiệm của họ. File này biến nó thành một dòng chảy thay vì
   một đống nằm im.

   ── NÓ LÀM GÌ, VÀ CỐ Ý KHÔNG LÀM GÌ ───────────────────
   LÀM: soi kho theo sáu lĩnh vực, bỏ những cái đã khai thác, xếp
   hạng, tải SKILL.md của vài ứng viên đầu bảng, và ghi lại một đoạn
   TRÍCH kèm đường dẫn bản đầy đủ.

   KHÔNG LÀM: tự biến luật thành phép canh. Một câu tiếng Anh trong
   SKILL.md thành một biểu thức chính quy chấm điểm mười hai cung là
   bước cần phán đoán, và một phép canh sai thì tệ hơn không có —
   nó chặn mọi đề xuất đúng, hoặc tệ hơn, LUÔN ĐẠT mà không ai biết.
   Repo này vừa dính đúng chuyện đó: thước SVG đạt giả ở cả mười hai
   cung suốt nhiều tuần vì một ký tự backspace lọt vào regex.

   Nên file này dừng ở "đây là kỹ năng chưa ai dùng, đây là chỗ đọc,
   đây là đoạn trích đủ để quyết có đọc tiếp không". Người hoặc model
   đọc rồi mới viết phép canh.

   Ranh giới đó không phải sự thận trọng suông — xem khối "ĐÃ THỬ RÚT
   LUẬT BẰNG MÁY, VÀ ĐÃ BỎ" ở giữa file: tôi đã thử làm phần đọc hiểu
   bằng regex, đo được kết quả, và nó cho ra rác.

   ── SỔ ĐÃ KHAI THÁC LÀ ĐIỀU KIỆN ĐỂ NÓ TIẾN ───────────
   Không có sổ thì mỗi lượt lại đề xuất đúng những cái tuần trước đã
   dùng, và "vòng tự tiến hoá" thành một vòng đi tại chỗ. Sổ nằm ở
   `factory/kho-da-dung.json`, ghi cả tên kỹ năng lẫn thứ nó đã sinh
   ra — để sau này lần ngược được một phép canh về nguồn của nó.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const KHO = join(ROOT, "tang-thu-cac/assets/js/data.js");
const SO = join(ROOT, "factory/kho-da-dung.json");
const RA = join(ROOT, "factory/kho-de-xuat.json");
const LENH = process.argv[2];

/* Sáu lĩnh vực. Khớp theo TÊN kỹ năng chứ không theo mô tả: mô tả
   nào cũng nhắc "design" hay "test" ở đâu đó, nên khớp mô tả cho ra
   1.339/3.696 — tức là không lọc gì cả. */
const LINH_VUC = {
  "lập trình công cụ": /\b(cli|tooling|build|bundler|refactor|codegen|automation|devtool|scaffold)\b/i,
  "kiểm thử rà soát": /\b(test|testing|lint|audit|review|verify|qa|coverage|regression|debug)\b/i,
  "dữ liệu phân tích": /\b(data|analytics|sql|etl|dataset|dataviz|chart|query|metric)\b/i,
  "hạ tầng vận hành": /\b(infra|devops|ci|cd|deploy|docker|observability|monitor|sre|pipeline|perf)\b/i,
  "giao tiếp nội dung": /\b(writing|copy|docs|content|changelog|readme|guideline)\b/i,
  "nghiên cứu": /\b(research|literature|survey|analysis|investigat|explor)\b/i
};

/* ── LOẠI TRỪ: NGHĨA KHÁC CỦA CÙNG MỘT TỪ ──────────────────
   Lượt quét 29/08 mang về "analyzing-linux-audit-logs-for-intrusion"
   và "analyzing-office365-audit-logs-for-compromise" — hai kỹ năng
   điều tra xâm nhập, lọt vào "kiểm thử rà soát" chỉ vì tên có chữ
   "audit". Hai trên năm suất của lượt ấy là rác, và mỗi suất rác
   tốn một lượt WebFetch trong hạn 24 lượt của model.

   "audit" ở đây nghĩa là rà soát MÃ NGUỒN của mình, không phải đọc
   nhật ký hệ thống tìm kẻ đột nhập. Danh sách này hẹp có chủ ý: chỉ
   những từ mà một kỹ năng hợp với repo tĩnh này gần như chắc chắn
   không mang. Rộng tay hơn là bắt đầu loại nhầm thứ có ích, và một
   bộ lọc loại nhầm thì không ai còn tin cái nó giữ lại. */
const LOAI_TRU = /\b(intrusion|compromise|malware|forensic|phishing|threat-hunt|incident-response|siem)\b/i;

/* Bao nhiêu SKILL.md tải mỗi lượt. Đây là van chi phí duy nhất:
   mỗi cái là một lượt gọi raw.githubusercontent, và tải cả kho là
   3.696 lượt cho thứ phần lớn không dùng tới. */
const TAI_MOI_LUOT = 6;

function docKho() {
  if (!existsSync(KHO)) return null;
  const cu = global.window;
  global.window = {};
  try { eval(readFileSync(KHO, "utf8").replace(/^\/\*[\s\S]*?\*\/\s*/, "")); }
  catch { global.window = cu; return null; }
  const D = global.window.TT_DATA;
  global.window = cu;
  return D && Array.isArray(D.skills) ? D : null;
}

function docSo() {
  if (!existsSync(SO)) return { daDung: {} };
  try { return JSON.parse(readFileSync(SO, "utf8")); } catch { return { daDung: {} }; }
}

/* ═══════════ ghi sổ ═══════════ */
if (LENH === "ghi") {
  const ten = process.argv.slice(3).filter(Boolean);
  if (!ten.length) { console.error("Dùng: node scripts/do-kho.mjs ghi <tên kỹ năng>…"); process.exit(2); }
  const so = docSo();
  const luc = new Date().toISOString();
  for (const t of ten) so.daDung[t] = { luc, ghiChu: so.daDung[t] ? so.daDung[t].ghiChu : null };
  so.capNhat = luc;
  await mkdir(dirname(SO), { recursive: true });
  await writeFile(SO, JSON.stringify(so, null, 1) + "\n", "utf8");
  console.log("✓ ghi " + ten.length + " kỹ năng vào sổ · tổng " + Object.keys(so.daDung).length);
  process.exit(0);
}

if (LENH === "so") {
  const so = docSo();
  const k = Object.keys(so.daDung).sort();
  console.log("Đã khai thác " + k.length + " kỹ năng:");
  for (const t of k) console.log("  " + t.padEnd(34) + (so.daDung[t].luc || "").slice(0, 10));
  process.exit(0);
}

if (LENH !== "quet") {
  console.error("Lệnh lạ. Có: quet · so · ghi <tên>…");
  process.exit(2);
}

/* ═══════════ quét ═══════════ */
const D = docKho();
if (!D) { console.error("Không đọc được kho Tàng Thư Các."); process.exit(1); }
const so = docSo();
const daDung = new Set(Object.keys(so.daDung));

/* ── ĐỪNG ĐỀ XUẤT LẠI THỨ VỪA ĐỀ XUẤT TUẦN TRƯỚC ──────────
   Xếp hạng ở dưới là TẤT ĐỊNH: cùng một kho, cùng một phép chấm thì
   ra cùng một top. Nên nếu chỉ loại "đã khai thác", lượt quét tuần
   sau đề xuất lại đúng năm cái tuần này — và vòng lặp thành một cái
   máy lặp lại chính nó. Lỗ này là của tôi, thấy ra khi lượt quét đầu
   chạy thật trên runner.

   Ghi danh sách "vừa đề xuất" vào CHÍNH file đề xuất, không mở sổ
   khai thác. Hai lý do:
   — "Đã đưa tới model" KHÔNG phải "đã dùng". Sổ khai thác là thứ
     quyết định lượt sau bỏ qua cái gì VĨNH VIỄN; nhét vào đó một
     thứ model có thể đã đọc lướt rồi bỏ là làm sổ ấy nói dối.
   — File đề xuất đã được khai ở `ra` của node và đã nằm trong lệnh
     git add. Thêm một file phải commit là thêm một chỗ hỏng, và
     thêm một mục phải khai trong CLAUDE.md.

   Cửa sổ 56 ngày rồi cho quay lại: chúng chưa từng bị khai thác,
   chỉ là chưa tới lượt. Kho có 769 ứng viên nên không lo cạn. */
const CUA_SO_NGAY = 56;
let ganDay = [];
try {
  const cu = JSON.parse(readFileSync(RA, "utf8"));
  const moc = Date.now() - CUA_SO_NGAY * 86400000;
  ganDay = [
    ...(cu.deXuat || []).map((x) => ({ ten: x.ten, luc: cu.luc })),
    ...(cu.ganDay || []),
  ].filter((x) => x && x.ten && Date.parse(x.luc) > moc);
  /* Bỏ trùng, giữ lần gần nhất. */
  const m = new Map();
  for (const x of ganDay) if (!m.has(x.ten) || m.get(x.ten).luc < x.luc) m.set(x.ten, x);
  ganDay = [...m.values()];
} catch { /* chưa có file đề xuất nào — lượt đầu, không loại gì */ }
const vuaDeXuat = new Set(ganDay.map((x) => x.ten));

/* Chấm ứng viên. Ba tín hiệu, và không cái nào là số sao của kho —
   sao là của cả repo nên xếp theo nó thì đầu bảng toàn một kho. */
const ungVien = [];
const thayTen = new Set();
for (const s of D.skills) {
  const ten = s.ten || "";
  if (!ten || daDung.has(ten) || thayTen.has(ten) || vuaDeXuat.has(ten)) continue;
  if (LOAI_TRU.test(ten)) continue;
  const lv = Object.keys(LINH_VUC).filter((k) => LINH_VUC[k].test(ten));
  if (!lv.length) continue;
  const mo = String(s.moTa || "");
  let diem = lv.length * 2;
  /* Mô tả có câu mệnh lệnh thì dễ thành phép canh hơn hẳn. */
  if (/\b(MUST|NEVER|ALWAYS|REQUIRED)\b/.test(mo)) diem += 4;
  if (/\b(check|verify|validate|enforce|rule|guideline|standard)\b/i.test(mo)) diem += 2;
  if (mo.length > 160) diem += 1;
  /* Kho chính chủ Anthropic ưu tiên nhẹ — không phải vì hay hơn, mà
     vì giấy phép rõ ràng và ít khả năng biến mất. */
  if (/^anthropics\//.test(s.kho || "")) diem += 2;
  thayTen.add(ten);
  ungVien.push({ ten, kho: s.kho, duong: s.duong, lv, diem, mo: mo.slice(0, 180) });
}
ungVien.sort((a, b) => b.diem - a.diem || a.ten.localeCompare(b.ten));

/* ═══════════ tải và rút luật ═══════════ */
async function taiSkill(u) {
  for (const br of ["main", "master"]) {
    try {
      const r = await fetch(`https://raw.githubusercontent.com/${u.kho}/${br}/${u.duong}/SKILL.md`,
        { signal: AbortSignal.timeout(30000) });
      if (r.ok) return await r.text();
    } catch { /* thử nhánh sau */ }
  }
  return null;
}

/* ĐÃ THỬ RÚT LUẬT BẰNG MÁY, VÀ ĐÃ BỎ. Ghi lại để đừng ai làm lại.

   Bản đầu lọc "dòng có MUST/NEVER + đủ dài". Kết quả đo thật trên
   năm SKILL.md: sáu câu, trong đó năm câu là rác —

     <blocking_issues>Issues that MUST be fixed before publish…   (mảnh XML)
     1. Git History (ALWAYS search):                              (tiêu đề mục)

   Siết thêm bốn lớp lọc (bỏ thẻ đánh dấu, bỏ tiêu đề, bỏ dòng bảng,
   đòi đủ tám chữ) thì còn ĐÚNG MỘT câu, và câu đó nói về tmux —
   không dùng được ở đây.

   Lý do sâu hơn cả bộ lọc: SKILL.md không viết luật thành từng
   dòng. Giá trị của chúng nằm trong văn xuôi có bối cảnh — "vì sao"
   quan trọng ngang "cái gì", mà cái "vì sao" thì không cắt thành
   dòng được. Chính năm kỹ năng giao diện dùng hôm qua cũng vậy: thứ
   đáng giá là một đoạn giải thích, không phải một câu mệnh lệnh.

   Nên đổi vai cho đúng sức từng bên:
     máy   → tìm, bỏ trùng, xếp hạng, tải về  (làm tốt, rẻ, xác định)
     model → đọc hiểu, chọn cái hợp cung này  (việc cần phán đoán)

   Hàm này giờ chỉ cắt một ĐOẠN TRÍCH đủ để model quyết có đọc tiếp
   hay không, kèm đường dẫn bản đầy đủ. */
function trichDan(md) {
  const than = md
    .replace(/^---[\s\S]*?---\s*/, "")        // bỏ khối frontmatter
    .split("\n")
    .filter((l) => !/^[-*>#\s]*$/.test(l))    // bỏ dòng trống và gạch trang trí
    .join(" ")
    .replace(/\s+/g, " ")
    .trim();
  return than.slice(0, 900);
}

const chon = ungVien.slice(0, TAI_MOI_LUOT);
const deXuat = [];
for (const u of chon) {
  const md = await taiSkill(u);
  if (!md) { console.log("  ✗ " + u.ten + " — không tải được"); continue; }
  deXuat.push({
    ...u,
    byte: md.length,
    doc: "https://github.com/" + u.kho + "/blob/main/" + u.duong + "/SKILL.md",
    trich: trichDan(md)
  });
  console.log("  ✓ " + u.ten.padEnd(32) + String(md.length).padStart(6) + " byte · " + u.lv.join(", "));
}

const now = new Date();
const data = {
  ghiChu: "SINH TỰ ĐỘNG bởi scripts/do-kho.mjs quet. Đây là ĐỀ XUẤT, không phải phép canh.",
  luc: now.toISOString(),
  khoQuetLuc: D.date || null,
  tongSkill: D.skills.length,
  daDung: daDung.size,
  ungVien: ungVien.length,
  /* Ai vừa được đề xuất, để lượt sau không đề xuất lại. Xem khối
     "ĐỪNG ĐỀ XUẤT LẠI" ở đầu file: đây KHÔNG phải sổ khai thác. */
  ganDay: [...ganDay, ...deXuat.map((x) => ({ ten: x.ten, luc: now.toISOString() }))],
  theoLinhVuc: Object.fromEntries(Object.keys(LINH_VUC).map((k) =>
    [k, ungVien.filter((u) => u.lv.includes(k)).length])),
  deXuat
};
await mkdir(dirname(RA), { recursive: true });
await writeFile(RA, JSON.stringify(data, null, 1) + "\n", "utf8");

console.log("\n✓ " + RA.replace(ROOT, ".") +
  "  ·  " + ungVien.length + " ứng viên chưa khai thác / " + D.skills.length + " kỹ năng");
console.log("  đã khai thác: " + daDung.size + " · tải lượt này: " + deXuat.length);
for (const [k, v] of Object.entries(data.theoLinhVuc)) console.log("    " + k.padEnd(20) + v);
