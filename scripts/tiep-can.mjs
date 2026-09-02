/* ═══════════════════════════════════════════════════════
   TIẾP CẬN — vá bốn thước tiếp cận của một cung bằng máy.

       node scripts/tiep-can.mjs <cung>          sửa thật
       node scripts/tiep-can.mjs <cung> --thu    xem sẽ đổi gì, chưa ghi
       node scripts/tiep-can.mjs --tat-ca --thu  soi cả 12 cung một lượt

   Bốn thước, bốn cách hỏng khác nhau, nhưng cùng một tính chất:
   người dùng chuột trên màn hình sáng KHÔNG BAO GIỜ gặp chúng, nên
   chúng nằm im nhiều tháng mà không ai báo.

     nhan       SVG trang trí thiếu aria-hidden → trình đọc màn hình
                đọc ra một mớ toạ độ giữa câu
     tieu-diem  thiếu :focus-visible → đi bằng bàn phím thì không biết
                mình đang đứng ở đâu trên trang
     so-cot     thiếu tabular-nums → mỗi lượt cập nhật là cả bảng số
                nhảy ngang, và mắt đọc lướt theo cột bị gãy
     svg-co     svg chỉ có viewBox → CSS cũ kẹt trong cache là icon
                phình kín màn hình (đã xảy ra ở Cổng Thành)

   ── VÌ SAO LÀ MÁY ────────────────────────────────────────────
   Cùng lý do đã ghi ở đầu `thang.mjs`: repo có 2–4 phiên song song,
   luật là "chỉ sửa thư mục cung mình", và lúc viết file này bốn cung
   cần vá đều đang nằm trong worktree của phiên khác. Máy thì mỗi
   phiên chạy một lệnh cho cung của mình.

   ── PHÉP NHẬN DIỆN CHÉP TỪ BỘ ĐO, KHÔNG TỰ NGHĨ ─────────────
   `svgTran` dưới đây là bản chép nguyên logic của thước `nhan` trong
   scripts/tien-hoa.mjs, kể cả mẹo soi ~240 ký tự phía trước để bỏ
   qua svg đã nằm trong thẻ có aria-hidden. Nghĩ ra một phép nhận
   diện khác là sớm muộn máy vá một tập, bộ đo soi một tập khác, và
   không bên nào sai rõ ràng để mà sửa.
   ═══════════════════════════════════════════════════════ */

import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const THU = process.argv.includes("--thu");
const TAT_CA = process.argv.includes("--tat-ca");
const CUNG = process.argv.slice(2).find((a) => !a.startsWith("--"));

function moiCung() {
  return readdirSync(ROOT, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith(".") && d.name !== "node_modules")
    .map((d) => d.name)
    .filter((n) => existsSync(join(ROOT, n, "index.html")))
    .sort();
}

/* Bản chép của thước `nhan`: svg chưa có aria-hidden/role/aria-label,
   và thẻ cha gần nhất cũng không có. */
function svgTran(html) {
  const ra = [];
  for (const m of html.matchAll(/<svg([^>]*)>/g)) {
    if (/aria-hidden|role=|aria-label/.test(m[1])) continue;
    const truoc = html.slice(Math.max(0, m.index - 240), m.index);
    const cha = [...truoc.matchAll(/<(?:span|button|a|div)([^>]*)>/g)].pop();
    if (cha && /aria-hidden|aria-label/.test(cha[1])) continue;
    ra.push(m.index);
  }
  return ra;
}

/* Thước thứ TƯ: `svg-co` — svg chỉ có viewBox thì không có cỡ nội
   tại, và CSS cũ còn kẹt trong cache là icon phình kín màn hình. Đã
   xảy ra thật ở Cổng Thành.

   Cỡ lấy từ CHÍNH viewBox, không bịa: `viewBox="0 0 24 24"` cho
   width=24 height=24. Thuộc tính HTML thua CSS về độ ưu tiên, nên
   thêm nó KHÔNG đổi diện mạo lúc CSS còn chạy — nó chỉ là lưới đỡ
   cho đúng cái ngày CSS không tới nơi. */
function svgThieuCo(html) {
  const ra = [];
  for (const m of html.matchAll(/<svg\b([^>]*)>/g)) {
    if (/(^|\s)width=/.test(m[1])) continue;
    const vb = m[1].match(/viewBox="\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)/);
    if (!vb) continue;          /* không có viewBox thì không suy ra được */
    ra.push({ vi: m.index + 4, w: vb[1], h: vb[2] });
  }
  return ra;
}

/* Đếm mặt số còn THIẾU tabular-nums — bản chép của thước `so-cot`,
   kể cả nhánh di truyền.

   Chép chứ không rút gọn, vì bản rút gọn đã báo nhầm thật: bản đầu
   chỉ hỏi "có khai ở gốc không", nên nó đòi vá SÁU cung đang khai
   theo từng khối và đang ĐẠT thước. Máy vá thứ không hỏng là máy sinh
   ra diff rỗng, và diff rỗng thì người duyệt thôi đọc diff. */
function demThieuSo(css) {
  const cssMa = css.replace(/\/\*[\s\S]*?\*\//g, "");
  if (/(?:^|\})\s*(?:body|html|:root)[^{}]*\{[^{}]*tabular-nums/.test(cssMa)) return 0;

  const khoi = [...cssMa.matchAll(/([^{}]+)\{([^{}]*)\}/g)]
    .map((m) => ({ sel: m[1].trim().replace(/\s+/g, " "), than: m[2] }));
  const LA_SO = (k) => /font-family:\s*var\(--mono\)/.test(k.than) ||
    /(^|[\s,>+~])(table|td|th)(?![-\w])/.test(k.sel) ||
    /[.#](bang|cot|o-so)(?![-\w])/.test(k.sel);
  const gocSel = (s) => s.trim().split(/[\s>+~]+/)[0].replace(/:{1,2}[\w-]+(\([^)]*\))?/g, "");
  const daPhu = new Set();
  for (const k of khoi)
    if (/tabular-nums/.test(k.than))
      for (const s of k.sel.split(",")) daPhu.add(gocSel(s));
  return khoi.filter(LA_SO).filter((k) =>
    !/tabular-nums/.test(k.than) &&
    !k.sel.split(",").every((s) => daPhu.has(gocSel(s)))).length;
}

/* Màu nhấn của cung, để vẽ vòng tiêu điểm. Lấy biến ĐANG dùng làm màu
   chữ của thẻ `a` — đó là màu cung tự chọn để nói "chỗ này bấm được",
   nên vòng tiêu điểm dùng chung màu ấy là nhất quán chứ không phải
   bịa thêm một màu thứ hai. Không tìm được thì thử vài tên quen. */
function mauNhan(css) {
  const a = css.match(/(?:^|\})\s*a\s*\{[^{}]*color:\s*var\((--[\w-]+)\)/);
  if (a) return a[1];
  for (const t of ["--acc", "--acc-2", "--tau", "--tien", "--lam", "--vang", "--son", "--purple", "--info"]) {
    if (new RegExp(`\\${t}\\s*:\\s*#`).test(css)) return t;
  }
  return null;
}

function doCung(cung) {
  const pHtml = join(ROOT, cung, "index.html");
  const thuCss = join(ROOT, cung, "assets", "css");
  const fsCss = existsSync(thuCss)
    ? readdirSync(thuCss).filter((f) => f.endsWith(".css")).map((f) => join(thuCss, f)) : [];
  const pApp = fsCss.find((p) => p.endsWith("app.css")) || fsCss[0];
  if (!existsSync(pHtml) || !pApp) return { cung, bo: "thiếu index.html hoặc CSS" };

  const html = readFileSync(pHtml, "utf8");
  const cssTat = fsCss.map((p) => readFileSync(p, "utf8")).join("\n");
  const app = readFileSync(pApp, "utf8");

  const svg = svgTran(html);
  const svgCo = svgThieuCo(html);
  const coTieuDiem = /:focus-visible/.test(cssTat);
  const thieuSo = demThieuSo(cssTat);
  const nhan = mauNhan(app) || mauNhan(cssTat);

  return { cung, pHtml, pApp, html, app, svg, svgCo, coTieuDiem, thieuSo, nhan };
}

function vaHtml(k) {
  let h = k.html;
  /* Trộn HAI nguồn vị trí rồi mới sắp giảm dần và chèn từ CUỐI về
     ĐẦU. Chèn từ đầu thì mọi vị trí sau đó lệch đi; và vì có hai
     nguồn, chạy hai vòng riêng cũng lệch — vòng sau không biết vòng
     trước đã đẩy chuỗi ra bao nhiêu. */
  const chen = [
    ...k.svg.map((i) => ({ vi: i + 4, chuoi: ' aria-hidden="true"' })),
    ...k.svgCo.map((x) => ({ vi: x.vi, chuoi: ` width="${x.w}" height="${x.h}"` })),
  ].sort((p, q) => q.vi - p.vi);
  for (const c of chen) h = h.slice(0, c.vi) + c.chuoi + h.slice(c.vi);
  return h;
}

function vaCss(k) {
  let t = k.app;
  const m = t.match(/(^|\n)body\s*\{[^}]*\}/);
  if (!m) return { t, loi: "không thấy khối body{} để móc vào" };

  if (k.thieuSo > 0) {
    /* Khai ở body vì `font-variant-numeric` DI TRUYỀN — một dòng phủ
       cả trang, khỏi phải nhớ khai lại ở từng khối, và bộ đo có nhánh
       nhận đúng chuyện đó. */
    const cu = m[0];
    const moi = cu.replace(/\}$/,
      ";\n  /* Số liệu phải ĐỨNG CỘT. Chữ số tỉ lệ thì mỗi lượt cập nhật là\n" +
      "     cả bảng nhảy ngang và mắt đọc lướt theo cột bị gãy. Khai ở\n" +
      "     body vì font-variant-numeric DI TRUYỀN. */\n" +
      "  font-variant-numeric:tabular-nums}");
    t = t.replace(cu, moi);
  }

  if (!k.coTieuDiem) {
    if (!k.nhan) return { t, loi: "không tìm được biến màu nhấn cho vòng tiêu điểm" };
    const mm = t.match(/(^|\n)body\s*\{[^}]*\}/);
    const i = mm.index + mm[0].length;
    t = t.slice(0, i) +
      "\n/* Tiêu điểm bàn phím phải THẤY ĐƯỢC. Trình duyệt có vòng mặc định\n" +
      "   nhưng nó chìm trên nền của cung này, nên người đi bằng bàn phím\n" +
      "   không biết mình đang đứng ở đâu. Dùng chính màu nhấn của cung,\n" +
      "   không bịa thêm một màu thứ hai. */\n" +
      `:focus-visible{outline:2.5px solid var(${k.nhan});outline-offset:2px;border-radius:5px}\n` +
      t.slice(i);
  }
  return { t, loi: null };
}

function chay(cung) {
  const k = doCung(cung);
  if (k.bo) { console.log(`· ${cung.padEnd(16)} ${k.bo}`); return; }

  const viec = [];
  if (k.svg.length) viec.push(`${k.svg.length} svg thiếu aria-hidden`);
  if (k.svgCo.length) viec.push(`${k.svgCo.length} svg thiếu cỡ nội tại`);
  if (!k.coTieuDiem) viec.push("thiếu :focus-visible");
  if (k.thieuSo > 0) viec.push(`${k.thieuSo} mặt số thiếu tabular-nums`);
  if (!viec.length) { console.log(`· ${cung.padEnd(16)} đã đủ cả ba`); return; }

  const { t, loi } = vaCss(k);
  console.log(`${THU ? "·" : "✓"} ${cung.padEnd(16)} ${viec.join(" · ")}` +
    (!k.coTieuDiem && k.nhan ? ` · vòng tiêu điểm dùng var(${k.nhan})` : "") +
    (loi ? `\n     ✗ ${loi}` : ""));
  if (THU || loi) return;

  if (k.svg.length || k.svgCo.length) writeFileSync(k.pHtml, vaHtml(k));
  if (t !== k.app) writeFileSync(k.pApp, t);
}

if (TAT_CA) {
  if (!THU) {
    console.error("`--tat-ca` chỉ đi cùng `--thu`. Sửa thật thì gọi từng cung một —");
    console.error("cung nào có worktree phiên khác đang giữ thì để phiên đó chạy.");
    process.exit(2);
  }
  for (const c of moiCung()) chay(c);
  process.exit(0);
}

if (!CUNG) { console.error("Thiếu tên cung. `node scripts/tiep-can.mjs <cung> [--thu]`"); process.exit(2); }
if (!existsSync(join(ROOT, CUNG, "index.html"))) {
  console.error(`"${CUNG}" không phải một cung (không có index.html ở gốc thư mục).`);
  process.exit(2);
}
chay(CUNG);
if (!THU) console.log(`\nChạy lại phiếu đo: node scripts/tien-hoa.mjs do ${CUNG}`);
