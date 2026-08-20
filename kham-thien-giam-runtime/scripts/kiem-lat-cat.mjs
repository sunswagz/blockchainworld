/* Kiểm hợp đồng trường: mọi khoá mà cung tĩnh ĐỌC đều phải có trong lát cắt.
 *
 *     node scripts/kiem-lat-cat.mjs
 *
 * Đây là chỗ hỏng dễ nhất và im lặng nhất của một trang số liệu: đổi tên một
 * khoá ở `snapshot.py`, `app.js` đọc ra `undefined`, và giao diện hiện "—"
 * hoặc "NaN" ở đúng ô mà người xem tin nhất. Không lỗi nào trong console,
 * không phép kiểm nào đỏ.
 *
 * Cùng lối với `tu-cam-thanh-runtime/scripts/kiem-giao-dien.mjs`, khác một
 * điểm: bên kia hỏi API đang chạy, bên này đọc FILE ĐÃ COMMIT. Vì lát cắt là
 * thứ thật sự lên site — runtime có thể đúng mà file commit vẫn cũ.
 *
 * Danh sách dưới đây phải sửa cùng lúc với `app.js`. Thấy nó lệch thì đó
 * chính là thứ phép kiểm này sinh ra để bắt.
 */

import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const GOC = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const LAT_CAT = join(GOC, "kham-thien-giam", "assets", "js", "v", "dai-chiem.js");

/* Khoá app.js đọc. `?` = được phép null, nhưng KHOÁ PHẢI TỒN TẠI.
   Phân biệt đó quan trọng: một khoá null là "chưa đo được", còn một khoá
   thiếu hẳn là "ai đó vừa đổi tên mà quên bên kia". */
const CAN = [
  // Cổng Thành đọc 900 byte đầu — hai khoá này PHẢI đứng đầu object
  "date", "tomTat",
  "generatedAt",

  "che", "cheKhai", "vong", "chayDuocGiay", "loiNhac",

  "thiTruong",
  "risk.von", "risk.vonBanDau", "risk.ngatKhanCap", "risk.lyDoNgat?",
  "risk.sutVonPct", "risk.loNgayUsd",

  "kho.soThiTruong", "kho.viThe", "kho.phoiNhiemGop",
  "kho.tongChuaPhongHoUsd", "kho.tongLoKhoaUsd",

  "hieuChinh.tongMau", "hieuChinh.duDeDungKelly", "hieuChinh.bang",
  "hieuChinh.saiSoTB?",

  "thongKe",
  "lenh.tongLenh", "lenh.daKhop", "lenh.duong", "lenh.cuaDangDong",
  "chienThuat", "vi", "nguon", "bang.soKhung", "bang.bat",
  "coHoi", "boQua",
];

/* Cổng Thành (assets/js/portal.js) chỉ đọc 900 BYTE ĐẦU rồi huỷ dòng tải.
   Nên `date` và `tomTat` phải nằm trong ngần ấy byte, không thì thẻ ngoài
   cổng mất ngày cập nhật — và mất im lặng. Đúng bẫy đã ghi cho Hộ Bộ và
   Thái Bộc Tự trong chính portal.js. */
const BYTE_CONG_THANH = 900;

let loi = 0;
const bao = (m) => { console.error("  ✗ " + m); loi++; };
const ok = (m) => console.log("  ✓ " + m);

if (!existsSync(LAT_CAT)) {
  console.error(`Chưa có lát cắt ở ${LAT_CAT}`);
  console.error("Sinh bằng: cd kham-thien-giam-runtime && python -m kham.snapshot");
  process.exit(1);
}

const tho = readFileSync(LAT_CAT, "utf8");

/* ── 1. hai khoá Cổng Thành cần phải nằm trong 900 byte đầu ────────── */
const dau = tho.slice(0, BYTE_CONG_THANH);
for (const k of ["date", "tomTat"]) {
  if (new RegExp(`"${k}"\\s*:`).test(dau)) ok(`"${k}" nằm trong ${BYTE_CONG_THANH} byte đầu`);
  else bao(`"${k}" KHÔNG nằm trong ${BYTE_CONG_THANH} byte đầu — thẻ Cổng Thành sẽ mất nó`);
}

/* ── 2. tách object và soi từng khoá ───────────────────────────────── */
const i = tho.indexOf("window.DAI_CHIEM");
if (i < 0) {
  bao("không thấy `window.DAI_CHIEM` — sai định dạng file");
  process.exit(1);
}
const j = tho.indexOf("=", i);
const json = tho.slice(j + 1).trim().replace(/;\s*$/, "");

let d;
try {
  d = JSON.parse(json);
} catch (e) {
  bao(`không parse được JSON: ${e.message}`);
  process.exit(1);
}

const doc = (o, duong) => duong.split(".").reduce(
  (x, k) => (x == null ? undefined : x[k]), o);

for (const raw of CAN) {
  const chon = raw.endsWith("?");
  const duong = chon ? raw.slice(0, -1) : raw;
  const v = doc(d, duong);
  if (v === undefined) bao(`thiếu khoá \`${duong}\``);
  else if (v === null && !chon) bao(`\`${duong}\` là null nhưng không khai \`?\``);
}
if (!loi) ok(`${CAN.length} khoá app.js đọc đều có mặt`);

/* ── 3. inf/nan không được lọt ra — chúng làm JSON.parse của trình
       duyệt ném, và trang trắng hoàn toàn ────────────────────────── */
if (/\b(Infinity|-Infinity|NaN)\b/.test(json)) {
  bao("có Infinity hoặc NaN trong lát cắt — `kham/sach.py` không chạy?");
} else {
  ok("không có Infinity/NaN");
}

/* ── 4. lát cắt không được mang khoá nào ───────────────────────────────
   Soi GIÁ TRỊ, không soi văn xuôi. Bản đầu của phép kiểm này quét cả chuỗi
   `PRIVATE_KEY` và lập tức báo đỏ vì lát cắt có đúng câu:

       "thiếu POLYMARKET_PRIVATE_KEY trong .env"

   — một LÝ DO giải thích vì sao cửa lệnh thật đang đóng, tức là đúng thứ
   phải hiện lên. Một phép kiểm báo nhầm ở đúng chỗ hệ thống làm đúng thì
   người ta sẽ tắt nó, và tắt rồi thì lần nó báo thật cũng mất theo.

   Nên soi hình dạng của BÍ MẬT thật:
     · 64 ký tự hex liền nhau  → hình dạng private key
     · khoá tên nhạy cảm mà có giá trị chuỗi dài → secret bị lọt */
const KHOA_64 = /(?:^|[^a-fA-F0-9])(?:0x)?[a-fA-F0-9]{64}(?:[^a-fA-F0-9]|$)/;
const TEN_NHAY = /"[^"]*(?:privateKey|apiSecret|passphrase|secret|token|apiKey)[^"]*"\s*:\s*"([^"]{12,})"/i;

const m64 = KHOA_64.test(json);
const mTen = TEN_NHAY.exec(json);
if (m64) bao("có chuỗi 64 ký tự hex — hình dạng của một private key");
else if (mTen) bao(`khoá nhạy cảm có giá trị: ${mTen[0].slice(0, 60)}…`);
else ok("không có bí mật nào lọt vào lát cắt");

/* ── 5. lát cắt phải nhẹ — nó nằm trong nhánh mạng-trước ───────────── */
const kb = Buffer.byteLength(tho, "utf8") / 1024;
if (kb > 250) bao(`lát cắt ${kb.toFixed(0)} KB — quá nặng cho một file tải mỗi lần mở trang`);
else ok(`lát cắt ${kb.toFixed(1)} KB`);

console.log();
if (loi) {
  console.error(`${loi} chỗ hỏng.`);
  process.exit(1);
}
console.log("Lát cắt khớp với những gì cung tĩnh đọc.");
