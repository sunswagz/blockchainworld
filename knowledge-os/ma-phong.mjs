/* ═══════════════════════════════════════════════════════
   BẢNG MÃ PHÒNG — một chỗ duy nhất, hai bộ đo cùng đọc.

   `kiem.mjs` cần nó để bắt ánh xạ trỏ vào mã không tồn tại.
   `do.mjs` cần nó để đếm phủ phòng. Chép làm hai bản là tạo bản
   sao thứ hai của cùng một sự thật, và bản thứ hai luôn là bản
   lệch — luật đã ghi trong CLAUDE.md, ở đây chỉ áp vào chỗ mới.

   Mã phòng đọc THẲNG từ mã nguồn cung, không bao giờ chép sang đây.
   Thêm cung mới thì thêm MỘT dòng vào DOC_PHONG.
   ═══════════════════════════════════════════════════════ */

import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

/* Ba cung khai mục bằng cùng một khuôn: một khối `muc: {` hoặc
   `VI.muc = {` trong glossary.js, khoá là mã phòng. Một khuôn thì
   khai một lần. */
export const KHOI_MUC = /(?:VI\.)?muc\s*[:=]\s*\{([\s\S]*?)\n {2}\}/;
const KHOA_MUC = /^\s{4}"([a-z0-9-]+)":\s*\{/gm;

export const DOC_PHONG = {
  /* Sổ 18 toa viết tay. */
  "thai-boc-tu": ["thai-boc-tu/assets/js/toa.js", /ma:\s*"(t\d\d)"/g],
  /* Mảng PHONG dựng thanh bên. */
  "ho-bo": ["ho-bo/assets/js/app.js", /ma:\s*"([a-z-]+)"/g, /var PHONG = \[([\s\S]*?)\n {2}\];/],
  /* Cung một trang: mỗi ô là một <section class="o">. */
  "thi-bac-ty": ["thi-bac-ty/index.html", /<section class="o[^"]*" id="([a-z-]+)"/g],
  /* Cung một trang: mỗi mục là một <section class="muc">. */
  "tu-cam-thanh": ["tu-cam-thanh/index.html", /<section class="muc" id="([a-z-]+)"/g],
  /* Sổ phòng viết tay, tách khỏi app.js. */
  "kham-thien-giam": ["kham-thien-giam/assets/js/phong.js", /ma:\s*"([a-z-]+)"/g],
  /* Khoá của VI.muc trong glossary — cùng bảng mà app.js dùng để định tuyến. */
  "cong-bo": ["cong-bo/assets/js/glossary.js", KHOA_MUC, KHOI_MUC],
  "do-sat-vien": ["do-sat-vien/assets/js/glossary.js", KHOA_MUC, KHOI_MUC],
  /* Mảng MUC_BEN: mỗi dòng một tuyến "#/xxx". */
  "tao-bien-xu": ["tao-bien-xu/assets/js/app.js", /\["#\/([a-z-]+)"/g, /var MUC_BEN = \[([\s\S]*?)\n {2}\];/],
  /* Thanh bên dựng theo dữ liệu, nhưng mã CỐ ĐỊNH thì viết thẳng
     trong ROUTES dạng `id:'xxx'`. Chỉ đọc mã cố định — mã sinh từ
     dữ liệu (`th/…`, `soi/…`, `cht/…`) đổi theo lượt bot, ánh xạ
     vào đó là ánh xạ sẽ lặng lẽ trỏ trượt. */
  "dai-quan-trac": ["dai-quan-trac/assets/js/app.js", /\{id:'([a-z]+)'/g, /ROUTES = \[([\s\S]*?)\n {2}\];/],
  "tang-thu-cac": ["tang-thu-cac/assets/js/glossary.js", KHOA_MUC, KHOI_MUC],
  "hoang-thanh": ["hoang-thanh/assets/js/app.js", /\{ hash: "#\/([a-z-]+)"/g]
};

/* Mã phòng đọc THẲNG từ mã nguồn cung, không bao giờ chép sang đây.
   Trả `null` nghĩa là "không đọc được", KHÁC hẳn "không có phòng
   nào" — và phép kiểm dưới phân biệt hai chuyện đó. */
export async function docMaPhong(REPO, ten) {
  const khai = DOC_PHONG[ten];
  if (!khai) return null;
  const [duong, mau, cat] = khai;
  if (!existsSync(join(REPO, duong))) return null;
  let t = await readFile(join(REPO, duong), "utf8");
  if (cat) {
    const m = t.match(cat);
    if (!m) return null;
    t = m[1];
  }
  const ds = [...t.matchAll(mau)].map((m) => m[1]);
  return ds.length ? new Set(ds) : null;
}
