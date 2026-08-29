/* ═══════════════════════════════════════════════════════
   PHÂN TÍCH TIN — mỗi bài một lớp phán đoán, ĐÁNH DẤU LÀ PHÁN ĐOÁN.

   Ba bước, cùng đường với build-dong-tin.mjs của Đài Quan Trắc và
   tách ba bước vì cùng một lý do:

     1. --de-bai   chọn bài CHƯA phân tích → assets/data/tin-de-bai.json
     2. (Actions)  Claude Code Action đọc đề bài, viết
                   assets/data/tin-phan-tich.json — JSON THÔ
     3. (không cờ) đọc cả hai, KIỂM, dựng assets/js/v/tin-phan-tich.js

   ĐỪNG cho model ghi thẳng file .js. Đó là file trình duyệt nạp;
   một lỗi cú pháp của model thành một trang trắng cho người xem.

   ── RANH GIỚI PHẢI GIỮ, VÀ NÓ LÀ RANH GIỚI CỦA CẢ CUNG ─
   Cung này sống bằng một luật: thứ ĐO ĐƯỢC và thứ LUẬN RA không bao
   giờ trông giống nhau. Bài báo là DỮ LIỆU — tiêu đề, ảnh, link đều
   của toà soạn. Phân tích là PHÁN ĐOÁN của model.

   Nên hai thứ đó nằm ở HAI FILE khác nhau, hai biến khác nhau, và
   giao diện vẽ chúng bằng hai lối khác nhau. Trộn vào một file là
   xoá mất ranh giới ngay ở tầng dữ liệu, rồi không ai dựng lại được.

   ── VÌ SAO KHÔNG PHẢI LỜI KHUYÊN ĐẦU TƯ ────────────────
   Trường `theoDoi` cố ý KHÔNG phải "mua gì bán gì". Nó là "điều gì
   sắp tới sẽ cho biết cách đọc này đúng hay sai".

   Đây không phải né tránh. Một câu "mua ETH" không kiểm được và
   không ai chịu trách nhiệm; một câu "nếu dòng vào ETF âm hai phiên
   liên tiếp thì cách đọc này sai" thì kiểm được, và tuần sau nhìn
   lại biết ngay model đúng hay sai. Cùng tinh thần với `nguoc` —
   mọi phán đoán ở repo này đều phải nói ra điều gì bác bỏ được nó.

   ── VAN CHI PHÍ ───────────────────────────────────────
   Hai cái van, và cái thứ hai mới là chính:

   1. MOI_LUOT — tối đa bao nhiêu bài mỗi lượt.
   2. NHỚ KẾT QUẢ CŨ. Mỗi bài chỉ phân tích ĐÚNG MỘT LẦN trong đời.
      Không có van này thì 30 bài × 4 lượt/ngày = 120 lượt gọi model
      mỗi ngày cho cùng một nhúm bài không đổi. Bảng điều khiển
      Anthropic từng ghi 610K token cho ba lượt quét — xem mục "Repo
      này KHÔNG dùng ANTHROPIC_API_KEY nữa" trong CLAUDE.md. Nay trả
      bằng quota gói, nhưng quota vẫn là gói của người dùng.

   ── BẪY ĐÃ CẮN MỘT LẦN: DỮ LIỆU THỬ LỌT LÊN SITE ──────
   Thử bộ kiểm bằng cách tự viết JSON giả, chạy bước 3, rồi xoá
   `assets/data/`. Tưởng là sạch — KHÔNG. Bước 3 đã nhét mục hợp lệ
   trong đám giả đó vào BỘ NHỚ của tin-phan-tich.js, và bộ nhớ thì
   sống qua mọi lượt sau. Kết quả: một bài về lừa đảo qua điện thoại
   nằm trên site thật với mạch lan truyền "ETF hút vốn ròng".

   Xoá `assets/data/` KHÔNG xoá bộ nhớ. Muốn dọn thì ghi đè thẳng:

       node -e 'require("fs").writeFileSync(
         "thai-boc-tu/assets/js/v/tin-phan-tich.js",
         "window.THAIBOC_PT={\\"pt\\":{}};\\n")'

   Và tốt hơn: thử bộ kiểm trên một BẢN CHÉP, đừng thử trên file
   thật. Bộ kiểm bắt được JSON sai khuôn, nó không bắt được JSON
   đúng khuôn mà nội dung bịa — vì nó không đọc bài báo.

   ── HỎNG THÌ GIỮ BẢN CŨ ───────────────────────────────
   Không có JSON model thì bước 3 vẫn chạy: nó dựng lại file từ
   riêng bộ nhớ cũ. Bài mới chưa kịp phân tích thì hiện không có
   nhãn — đúng như vậy, chứ không bịa một nhãn cho đủ bộ.
   ═══════════════════════════════════════════════════════ */

import { writeFile, mkdir } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CUNG = "thai-boc-tu";
const TIN = join(ROOT, CUNG, "assets/js/v/tin-tuc.js");
const SO = join(ROOT, CUNG, "assets/js/v/tin-phan-tich.js");
const DE = join(ROOT, CUNG, "assets/data/tin-de-bai.json");
const THO = join(ROOT, CUNG, "assets/data/tin-phan-tich.json");

/* 12 → 24 (29/08). Sổ nhà máy ghi "nhận 12 · phủ 14/30 bài": mười sáu
   bài trên bảng tin KHÔNG có phân tích nào, và đó đúng là thứ người
   dùng đòi ("mỗi bài viết đều có AI phân tích").

   Vì sao nâng con số này chứ không nâng nhịp node: van chi phí THẬT
   là bộ nhớ ngay dưới — mỗi bài chỉ phân tích đúng một lần trong
   đời, nên tổng lượt gọi model bằng SỐ BÀI KHÁC NHAU từng xuất hiện,
   không phụ thuộc MOI_LUOT. Con số này chỉ quyết BAO LÂU thì phủ
   hết. Nâng nhịp 12 → 6 giờ thì cũng phủ nhanh bằng, nhưng thêm hai
   lượt chạy mỗi ngày và đẩy đệm ngân sách lượt xuống 2,95× — dưới
   ngưỡng 3× mà `npm run kiem` đòi.

   24 bài/lượt × 2 lượt/ngày = 48, so với bảng tin 30 bài làm mới 4
   lượt/ngày. Đo trước khi nâng: cả nhóm ba bước chạy 125 giây với 12
   bài, van của bước model là 8 phút — còn thừa nhiều. Nếu sổ vẫn ghi
   "phủ dưới 30/30" sau vài ngày thì nguồn tin đang đẻ hơn 48 bài
   mới mỗi ngày, và lúc đó mới đáng nâng tiếp. */
const MOI_LUOT = 24;
/* Giữ bao nhiêu phân tích cũ. Bài rơi khỏi bảng tin vẫn giữ một thời
   gian: nguồn hay đưa lại cùng một link, và phân tích lại là trả tiền
   hai lần cho cùng một bài. */
const TRAN_NHO = 150;

const MUC = ["cao", "vua", "thap"];

function docBien(p, ten) {
  if (!existsSync(p)) return null;
  const cu = global.window; global.window = {};
  try { eval(readFileSync(p, "utf8").replace(/^\/\*[\s\S]*?\*\/\s*/, "")); }
  catch { global.window = cu; return null; }
  const v = global.window[ten]; global.window = cu; return v || null;
}

const khoa = (link) => String(link || "").split("?")[0].replace(/\/$/, "").toLowerCase();

const tin = docBien(TIN, "THAIBOC_TIN");
if (!tin || !Array.isArray(tin.bai)) {
  console.error("Chưa có tin-tuc.js hoặc file hỏng. Chạy build-tintuc.mjs trước.");
  process.exit(1);
}
const cu = docBien(SO, "THAIBOC_PT");
const nho = {};
if (cu && cu.pt) for (const k in cu.pt) nho[k] = cu.pt[k];

/* ═══════════════ BƯỚC 1 · RA ĐỀ ═══════════════ */
if (process.argv.includes("--de-bai")) {
  const chua = tin.bai.filter((b) => !nho[khoa(b.link)]).slice(0, MOI_LUOT);

  /* Danh sách toa hợp lệ, lấy từ chính sổ toa — để model chọn trong
     đó chứ không tự nghĩ ra mã. Bịa mã thì bước 3 loại mục đó. */
  const toa = docBien(join(ROOT, CUNG, "assets/js/toa.js"), "THAIBOC_TOA");
  const dsToa = ((toa && toa.TOA) || []).map((t) => ({ ma: t.ma, ten: t.ten, lat: t.lat }));

  const de = {
    ghiChu: "SINH TỰ ĐỘNG bởi scripts/build-tin-phantich.mjs. Đừng sửa tay, đừng commit.",
    sinhLuc: new Date().toISOString(),
    daNho: Object.keys(nho).length,
    toaHopLe: dsToa,
    bai: chua.map((b) => ({
      link: b.link, tieuDe: b.tieuDe, nguon: b.nguon,
      ngay: b.ngay, tom: b.tom, toaDoan: b.toa
    }))
  };
  await mkdir(dirname(DE), { recursive: true });
  await writeFile(DE, JSON.stringify(de, null, 2) + "\n", "utf8");
  console.log("✓ Ra đề: " + chua.length + "/" + tin.bai.length +
    " bài chưa phân tích (đã nhớ " + Object.keys(nho).length + ")");
  process.exit(0);
}

/* ═══════════════ BƯỚC 3 · KIỂM VÀ DỰNG ═══════════════ */
const hopLeToa = new Set(
  (((docBien(join(ROOT, CUNG, "assets/js/toa.js"), "THAIBOC_TOA") || {}).TOA) || [])
    .map((t) => t.ma));
const trongTin = new Set(tin.bai.map((b) => khoa(b.link)));

let nhan = 0, loai = 0;
const viLoai = [];

if (existsSync(THO)) {
  let j = null;
  try { j = JSON.parse(readFileSync(THO, "utf8")); }
  catch (e) { console.error("JSON model hỏng: " + e.message); }
  const ds = j && Array.isArray(j.bai) ? j.bai : [];

  for (const x of ds) {
    const k = khoa(x && x.link);
    /* Loại chứ KHÔNG sửa hộ. Sửa hộ là dạy đường ống chấp nhận rác,
       và lần sau rác sẽ nhiều hơn. */
    const vi = (() => {
      if (!k) return "thiếu link";
      if (!trongTin.has(k)) return "link không có trong bảng tin";
      if (!MUC.includes(x.muc)) return "mức lạ: " + x.muc;
      if (x.toa != null && !hopLeToa.has(x.toa)) return "mã toa bịa: " + x.toa;
      if (!Array.isArray(x.mach) || x.mach.length < 2 || x.mach.length > 4)
        return "mạch phải có 2–4 bước";
      if (x.mach.some((m) => typeof m !== "string" || !m.trim() || m.length > 90))
        return "bước mạch rỗng hoặc quá dài";
      if (typeof x.theoDoi !== "string" || x.theoDoi.trim().length < 10)
        return "thiếu điều cần theo dõi";
      if (typeof x.nguoc !== "string" || x.nguoc.trim().length < 10)
        return "thiếu điều bác bỏ được";
      return null;
    })();
    if (vi) { loai++; if (viLoai.length < 6) viLoai.push((x && x.link ? x.link.slice(-40) : "?") + " — " + vi); continue; }

    nho[k] = {
      muc: x.muc,
      toa: x.toa == null ? null : x.toa,
      mach: x.mach.map((m) => m.trim().slice(0, 90)),
      theoDoi: x.theoDoi.trim().slice(0, 220),
      nguoc: x.nguoc.trim().slice(0, 220),
      luc: new Date().toISOString()
    };
    nhan++;
  }
}

/* Dọn bộ nhớ: giữ bài còn trong bảng tin trước, rồi tới bài mới nhất. */
const khoaCon = Object.keys(nho)
  .sort((a, b) => {
    const ta = trongTin.has(a) ? 1 : 0, tb = trongTin.has(b) ? 1 : 0;
    if (ta !== tb) return tb - ta;
    return (nho[b].luc || "") < (nho[a].luc || "") ? -1 : 1;
  })
  .slice(0, TRAN_NHO);
const pt = {};
for (const k of khoaCon) pt[k] = nho[k];

const phu = tin.bai.filter((b) => pt[khoa(b.link)]).length;
const demMuc = { cao: 0, vua: 0, thap: 0 };
for (const b of tin.bai) {
  const a = pt[khoa(b.link)];
  if (a && demMuc[a.muc] != null) demMuc[a.muc]++;
}

const now = new Date();
const data = {
  generatedAt: now.toISOString(),
  date: now.toISOString().slice(0, 10).split("-").reverse().join("/"),
  tomTat: phu + "/" + tin.bai.length + " bài có phân tích",
  tong: { daNho: Object.keys(pt).length, phuBaiHienTai: phu, tongBai: tin.bai.length, demMuc },
  pt
};

await mkdir(dirname(SO), { recursive: true });
await writeFile(SO,
  "/* TỰ SINH — đừng sửa tay. Nguồn: scripts/build-tin-phantich.mjs\n" +
  "   Sinh lúc " + data.generatedAt + " */\n" +
  "window.THAIBOC_PT = " + JSON.stringify(data) + ";\n", "utf8");

console.log("✓ Ghi " + SO.replace(ROOT, ".") +
  "  (" + (JSON.stringify(data).length / 1024).toFixed(1) + " KB)");
console.log("  nhận " + nhan + " · loại " + loai + " · phủ " + phu + "/" + tin.bai.length + " bài");
for (const v of viLoai) console.log("    ✗ " + v);
