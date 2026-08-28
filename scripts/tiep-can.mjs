/* ═══════════════════════════════════════════════════════
   TIẾP CẬN — vá ba thước tiếp cận của một cung bằng máy.

       node scripts/tiep-can.mjs <cung>          sửa thật
       node scripts/tiep-can.mjs <cung> --thu    xem sẽ đổi gì, chưa ghi
       node scripts/tiep-can.mjs --tat-ca --thu  soi cả 12 cung một lượt

   Ba thước, ba cách hỏng khác nhau, nhưng cùng một tính chất: người
   dùng chuột trên màn hình sáng KHÔNG BAO GIỜ gặp chúng, nên chúng
   nằm im nhiều tháng mà không ai báo.

     nhan       SVG trang trí thiếu aria-hidden → trình đọc màn hình
                đọc ra một mớ toạ độ giữa câu
     tieu-diem  thiếu :focus-visible → đi bằng bàn phím thì không biết
                mình đang đứng ở đâu trên trang
     so-cot     thiếu tabular-nums → mỗi lượt cập nhật là cả bảng số
                nhảy ngang, và mắt đọc lướt theo cột bị gãy

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
  const coTieuDiem = /:focus-visible/.test(cssTat);
  const thieuSo = demThieuSo(cssTat);
  const nhan = mauNhan(app) || mauNhan(cssTat);

  return { cung, pHtml, pApp, html, app, svg, coTieuDiem, thieuSo, nhan };
}

function vaHtml(k) {
  let h = k.html;
  /* Sửa từ CUỐI về ĐẦU: chèn từ đầu thì mọi vị trí sau đó lệch đi. */
  for (const i of k.svg.slice().reverse()) h = h.slice(0, i + 4) + ' aria-hidden="true"' + h.slice(i + 4);
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
  if (!k.coTieuDiem) viec.push("thiếu :focus-visible");
  if (k.thieuSo > 0) viec.push(`${k.thieuSo} mặt số thiếu tabular-nums`);
  if (!viec.length) { console.log(`· ${cung.padEnd(16)} đã đủ cả ba`); return; }

  const { t, loi } = vaCss(k);
  console.log(`${THU ? "·" : "✓"} ${cung.padEnd(16)} ${viec.join(" · ")}` +
    (!k.coTieuDiem && k.nhan ? ` · vòng tiêu điểm dùng var(${k.nhan})` : "") +
    (loi ? `\n     ✗ ${loi}` : ""));
  if (THU || loi) return;

  if (k.svg.length) writeFileSync(k.pHtml, vaHtml(k));
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
