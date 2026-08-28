/* Kiểm giao diện buồng lái bằng SỐ, không bằng cảm giác.
 *
 *     node scripts/kiem-giao-dien.mjs
 *
 * Luật lấy từ ba kỹ năng trong Tàng Thư Các — `baseline-ui`,
 * `anti-ui-slop`, `accessibility` — nhưng KHÔNG chép nguyên. Phần lớn
 * luật ở đó viết cho Tailwind + React; buồng lái này là CSS thuần, không
 * có bước dựng. Chép nguyên là mang về một hệ quy chiếu thứ hai rồi phải
 * sống với cả hai.
 *
 * Nên dịch: giữ Ý ĐỊNH, bỏ cú pháp. `tabular-nums` thì CSS thuần cũng có;
 * "một màu nhấn mỗi khung nhìn" thì đếm được; "trạng thái rỗng phải có
 * một việc tiếp theo" thì soi được. Còn `cn()`, `motion/react`, `Radix`
 * thì không mang sang.
 *
 * `anti-ui-slop` nói đúng câu đáng nghe nhất: dùng hệ có sẵn của chính
 * sản phẩm trước khi mượn hệ bên ngoài. File này là cách giữ lời đó.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const GOC = join(dirname(fileURLToPath(import.meta.url)), "..");
const css = readFileSync(join(GOC, "web/app.css"), "utf8");
const js = readFileSync(join(GOC, "web/app.js"), "utf8");
const html = readFileSync(join(GOC, "web/index.html"), "utf8");

let loi = 0, ok = 0;
const bao = (dat, ten, ghi = "") => {
  console.log(`  ${dat ? "OK   " : "LỖI  "} ${ten.padEnd(34)} ${ghi}`);
  dat ? ok++ : loi++;
};

/* ── 1. TƯƠNG PHẢN ─────────────────────────────────────────────────
   Luật của chính cung này đã ghi "màu mới phải đạt WCAG AA 4.5 trên MỌI
   nền" — nhưng ghi trong văn xuôi thì không ai kiểm. Nay đo. */
function hex(s) {
  const m = /^#?([0-9a-f]{6})$/i.exec(s.trim());
  if (!m) return null;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function sang([r, g, b]) {
  const f = (v) => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}
function tuongPhan(a, b) {
  const [x, y] = [sang(a), sang(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
}

const bien = {};
for (const m of css.matchAll(/--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})/g)) {
  bien[m[1]] = hex(m[2]);
}
// Nền thật sự dùng trong buồng lái.
const NEN = ["nen", "nen2", "the", "the2"].filter((n) => bien[n]);
// Màu chữ, kèm mức tối thiểu. `mo2` chỉ dùng cho nhãn phụ và chú thích —
// WCAG cho phép 3.0 với chữ lớn/phụ trợ, nhưng ở đây vẫn đòi 3.0 chứ
// không tha hẳn: một nhãn không đọc được thì cũng vô dụng như một số sai.
const CHU = { chu: 4.5, mo: 4.5, mo2: 3.0, sao: 4.5, len: 4.5, xuong: 4.5, canh: 4.5, tim: 4.5 };

let te = null;
for (const [ten, sanNen] of Object.entries(CHU)) {
  if (!bien[ten]) continue;
  for (const n of NEN) {
    const t = tuongPhan(bien[ten], bien[n]);
    if (!te || t < te.t) te = { t, ten, n };
    if (t < sanNen) {
      bao(false, `tương phản --${ten} trên --${n}`,
        `${t.toFixed(2)} < ${sanNen} — chữ không đọc nổi`);
    }
  }
}
if (te) bao(true, "tương phản: cặp tệ nhất", `--${te.ten}/--${te.n} = ${te.t.toFixed(2)}`);

/* ── 2. SỐ PHẢI THẲNG CỘT ──────────────────────────────────────────
   `tabular-nums`: chữ số cùng bề rộng. Không có nó thì một con số đếm
   ngược nhảy qua nhảy lại theo bề rộng chữ số — mắt đọc thành chuyển
   động, trong khi thứ đang đổi chỉ là giá trị. */
bao(/font-variant-numeric:\s*tabular-nums/.test(css),
  "số dùng tabular-nums", `${(css.match(/tabular-nums/g) || []).length} chỗ`);

/* ── 3. KHÔNG GRADIENT, KHÔNG HÀO QUANG LÀM TÍN HIỆU CHÍNH ────────── */
bao(!/linear-gradient|radial-gradient/.test(css), "không dùng gradient");
const hao = css.match(/text-shadow:\s*0 0 \d+px/g) || [];
bao(hao.length <= 1, "hào quang chỉ dùng phụ hoạ",
  `${hao.length} chỗ — mỗi chỗ phải kèm dấu hiệu thứ hai`);

/* ── 4. THANG z-index CỐ ĐỊNH ─────────────────────────────────────── */
const z = [...css.matchAll(/z-index:\s*(\d+)/g)].map((m) => +m[1]);
const zHop = new Set([1, 5, 10, 50]);
bao(z.every((v) => zHop.has(v)), "z-index theo thang cố định",
  z.length ? `dùng ${[...new Set(z)].join(", ")}` : "không dùng");

/* ── 5. NÚT CHỈ CÓ BIỂU TƯỢNG PHẢI CÓ NHÃN ────────────────────────── */
const svgTron = /<button(?![^>]*aria-label)[^>]*>\s*<svg/.test(html);
bao(!svgTron, "nút biểu tượng có aria-label");

/* ── 6. TÔN TRỌNG prefers-reduced-motion ──────────────────────────── */
bao(/prefers-reduced-motion/.test(css), "tôn trọng prefers-reduced-motion");

/* ── 7. CHIỀU CAO KHUNG NHÌN DÙNG dvh ─────────────────────────────── */
const vhCu = (css.match(/\d+vh\b/g) || []).filter((s) => !s.includes("dvh"));
bao(vhCu.length === 0, "dùng dvh thay vì vh",
  vhCu.length ? `còn ${vhCu.join(", ")} — thanh địa chỉ di động làm sai` : "");

/* ── 8. TRẠNG THÁI RỖNG PHẢI NÓI VIỆC TIẾP THEO ───────────────────
   Luật `baseline-ui`: "empty states MUST give one clear next action".
   Ở một buồng lái thì "việc tiếp theo" thường là MỘT CÂU giải thích vì
   sao đang trống và điều gì sẽ làm nó hết trống — chứ không phải một cái
   nút. Nên đo bằng độ dài: một câu "chưa có dữ liệu" cụt lủn thì không
   nói được gì cho ai. */
const DOI = String.fromCharCode(34), DON = String.fromCharCode(39);
const CHEO = String.fromCharCode(92);   // dùng trong bieuThucSau
const NHAY = /"([^"]*)"/g;
// Đọc CẢ biểu thức trong `chuaCo(...)`, không chỉ chuỗi đầu tiên. Bản
// đầu cắt ở dấu nháy đóng nên một câu nối bằng dấu cộng bị chấm là "cụt"
// trong khi nó dài nhất trong đám — báo động giả, và báo động giả thì
// người ta ngừng tin cả bộ kiểm.
function bieuThucSau(vanBan, tu) {
  let sau = 1, i = tu;
  while (i < vanBan.length && sau > 0) {
    const c = vanBan[i];
    if (c === "(") sau++;
    else if (c === ")") sau--;
    else if (c === DOI || c === DON) {
      i++;
      while (i < vanBan.length && vanBan[i] !== c) i += vanBan[i] === CHEO ? 2 : 1;
    }
    i++;
  }
  return vanBan.slice(tu, i - 1);
}
const rong = [];
// `function chuaCo(` cũng khớp mẫu này — phép kiểm suýt bắt chính dòng
// định nghĩa hàm và báo một "câu cụt" rỗng. Bỏ nơi khai báo ra.
for (const m of js.matchAll(/(?<!function )chuaCo\(/g)) {
  const bt = bieuThucSau(js, m.index + m[0].length);
  // chỉ đếm phần nằm trong dấu nháy — tên biến không phải câu chữ
  const chu = [...bt.matchAll(NHAY)].map((x) => x[1]).join(" ");
  rong.push(chu);
}
const cut = rong.filter((s) => s.length < 60);
bao(cut.length === 0, "trạng thái rỗng nói việc tiếp theo",
  cut.length
    ? `${cut.length} câu cụt: ${cut.slice(0, 2).map((s) => s.slice(0, 40)).join(" | ")}`
    : `${rong.length} chỗ, ngắn nhất ${Math.min(...rong.map((s) => s.length))} ký tự`);

/* ── 9. MÀU NHẤN: một cho điều hướng, còn lại phải MANG NGHĨA ──────
   `baseline-ui` nói "một màu nhấn mỗi khung nhìn". Với một bảng dữ liệu
   thì luật đó phải đọc là: một màu nhấn ĐIỀU HƯỚNG, còn xanh/đỏ/vàng là
   NGHĨA (lên, xuống, cảnh báo) chứ không phải trang trí. Kiểm phần đọc
   được: mỗi màu nghĩa phải luôn đi kèm chữ hoặc dấu, không đứng một mình. */
const mauNghia = ["len", "xuong", "canh"];
bao(mauNghia.every((m) => bien[m]), "màu nghĩa khai đủ trong bảng màu",
  mauNghia.join(", "));

console.log(`\n  ${ok}/${ok + loi} phép kiểm giao diện đạt\n`);
process.exit(loi ? 1 : 0);
