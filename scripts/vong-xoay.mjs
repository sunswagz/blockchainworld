import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

/* ═══════════════════════════════════════════════════════
   VÒNG XOAY — tám cung dùng chung MỘT node tiến hoá.

   Năm cung có vòng tiến hoá riêng, chạy mỗi ngày. Bảy cung trong
   danh sách này không có gì cả; chúng chỉ tiến khi có người ngồi
   vào sửa.

   ── VÌ SAO XOAY, KHÔNG PHẢI THÊM BẢY NODE ────────────────────
   Đã tính bằng số đo thật rồi bỏ: mỗi vòng tiến hoá tốn 86–263 giây
   model (đo trên năm vòng đang chạy). Bảy vòng nữa là thêm ~21 phút
   mỗi lượt, đẩy lượt xấu nhất từ 33 lên ~54 phút. Trần job 130 nên
   không nổ, nhưng đệm tụt từ 4× xuống 2,4× — dưới ngưỡng 3× mà phép
   canh ngân sách trong `npm run kiem` đòi.

   Xoay thì chi phí bằng MỘT vòng (~3 phút/lượt) thay vì bảy. Đổi
   lại mỗi cung chỉ được sửa mỗi tuần một bước. Chậm hơn bảy lần so
   với cung có vòng riêng — nhưng bảy cung này đang ở nhịp KHÔNG BAO
   GIỜ, nên so sánh đúng là "một tuần một bước" với "không bao giờ".

   ── VÌ SAO Ở FILE RIÊNG ──────────────────────────────────────
   Danh sách này ban đầu nằm trong scripts/tien-hoa.mjs. Nhưng
   `npm run kiem` phải đọc được nó để canh, mà import tien-hoa.mjs
   là chạy luôn phần thân của nó — file ấy gọi `thoat("Thiếu lệnh")`
   ngay ở đầu khi không có tham số, và nó giết cả bộ kiểm. Tách ra
   một module chỉ có dữ liệu thì cả hai bên đọc chung một nguồn mà
   không ai kéo theo tác dụng phụ của ai.

   ── LUẬT ─────────────────────────────────────────────────────
   THÊM cung vào đây khi nó chưa có vòng riêng.
   GỠ cung ra khi nó được cấp vòng riêng.

   Quên gỡ là mỗi tuần có một ngày cung ấy bị HAI model sửa trong
   cùng một lượt, không biết nhau: model thứ hai chấm phiếu gốc SAU
   khi model thứ nhất đã sửa, nên chốt "không được xấu đi" so với
   một mốc đã dịch. Hai bản vá chồng lên nhau và cổng chặn vẫn xanh.
   `npm run kiem` canh đúng chuyện đó.
   ═══════════════════════════════════════════════════════ */

/* `cong-thanh` KHÔNG phải một thư mục — nó là trang gốc repo, và
   `scripts/tien-hoa.mjs` nhận đúng tên ấy làm bí danh cho gốc. Trước
   02/09 nó nằm ngoài mọi vòng: mười hai cung tiến mỗi ngày hoặc mỗi
   tuần, còn trang ĐẦU TIÊN người ta thấy thì chỉ tiến khi có người
   ngồi vào sửa — lần gần nhất trước đó là 29/08.

   Ai sửa danh sách này thì nhớ: phép kiểm "có index.html không" ở
   `kiem-quy-trinh.mjs` phải biết về bí danh, không thì nó báo oan. */
export const VONG_XOAY = [
  "cong-bo", "cong-thanh", "do-sat-vien", "hoang-thanh", "kinh-thanh",
  "tang-thu-cac", "thi-bac-ty", "tu-cam-thanh",
];

/* Chọn theo NGÀY chứ không theo con đếm trong sổ: không cần trạng
   thái, không cần thêm file phải commit, và hai lượt cùng ngày (cron
   tám mốc) rơi vào CÙNG một cung nên không cung nào bị sửa hai lần
   trong ngày — lượt thứ hai thấy node chưa tới nhịp 24 giờ và bỏ
   qua. Một con đếm thì lượt thứ hai sẽ nhảy sang cung kế tiếp. */
export function cungHomNay(luc = Date.now()) {
  return VONG_XOAY[Math.floor(luc / 86400000) % VONG_XOAY.length];
}

/* ── BA FILE MODEL ĐƯỢC SỬA, VÀ FILE THỨ TƯ ĐI KÈM ─────────
   Mười hai cung theo đúng một khuôn: `<cung>/index.html`,
   `<cung>/assets/css/app.css`, `<cung>/assets/js/app.js`. Cổng Thành
   thì KHÔNG — mã của nó ở gốc repo và mang tên khác: `portal.css`,
   `portal.js`. Khuôn `${c}/assets/css/app.css` áp cho nó cho ra bốn
   đường không tồn tại.

   Vì sao chỗ này đáng có một hàm riêng thay vì bốn dòng chuỗi rải ra:
   `duong-ra` CHỈ in đường có thật trên đĩa, nên bốn đường sai không
   sinh lỗi nào — chúng lặng lẽ biến mất khỏi lệnh `git add`, và Cổng
   Thành thành cung mà model sửa mỗi tám ngày rồi bị vứt, sổ vẫn ghi
   "ok". Đó đúng là lỗi `ra: []` đã cắn một lần ở chính node xoay này,
   chỉ khác là lần này nó chỉ cắn MỘT cung nên còn khó thấy hơn.

   Nên tên file nằm ở đây, cạnh danh sách xoay, và cả `scripts/node/
   xuong.mjs` lẫn đề bài của workflow đều hỏi hàm này. Thêm một cung
   đặt tên file khác thì sửa đúng một chỗ.

   MỘT chỗ duy nhất biết Cổng Thành là ngoại lệ, và đó là `thuMuc`.
   Ba hàm dưới dựng trên nó; thêm hàm thứ tư thì cũng dựng trên nó,
   đừng viết lại phép so `=== "cong-thanh"` lần nữa. */
export const thuMuc = (cung) => (cung === "cong-thanh" ? "" : cung + "/");

export function fileSua(cung) {
  const d = thuMuc(cung);
  const ten = cung === "cong-thanh" ? "portal" : "app";
  return [`${d}index.html`, `${d}assets/css/${ten}.css`, `${d}assets/js/${ten}.js`];
}

/* Đề bài của lượt — `tien-hoa.mjs de-bai` ghi ra đây, model đọc nó
   rồi ghi lại `daLam` vào chính nó. Gitignore phải phủ được đường
   này, xem mục tương ứng trong .gitignore. */
export const fileDeBai = (cung) => `${thuMuc(cung)}assets/data/de-bai-tien-hoa.json`;

/* ── MƯỜI BA TRANG ĐƯỢC CHẤM ───────────────────────────────
   Khác với biến `cung` trong `kiem-quy-trinh.mjs`, và khác CÓ CHỦ Ý:
   ở đó `cung` nghĩa là "thư mục cung", dùng để soi `<cung>/sw.js`,
   `<cung>/assets/js/halls.js`… — những thứ Cổng Thành không có theo
   cùng khuôn. Ở đây câu hỏi khác: "trang nào bị thước chấm". Trả lời
   là mười hai cung CỘNG trang gốc.

   Hai khái niệm gần nhau nhưng không trùng, nên chúng là hai hàm chứ
   không phải một hàm dùng chung — gộp lại là mỗi lần sửa phải nhớ nó
   đang trả lời câu nào.

   Nhập `node:fs` ở đây KHÔNG phá luật "module chỉ có dữ liệu" mà file
   này sinh ra để giữ: luật ấy cấm CHẠY gì lúc nhập, không cấm nhập
   thư viện. `kiem-quy-trinh.mjs` vẫn import file này an toàn. */
export function dsTrang(root) {
  const bo = new Set(["node_modules", "dist"]);
  const ds = readdirSync(root, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith(".") && !bo.has(d.name))
    .map((d) => d.name)
    .filter((n) => existsSync(join(root, n, "index.html")))
    .sort();
  if (existsSync(join(root, "index.html"))) ds.push("cong-thanh");
  return ds;
}

/* Thêm `sw.js`: model không được sửa nó, nhưng `nang-version.mjs` chạy
   ngay sau cổng chặn và nâng CACHE_VERSION. Không commit nó thì người
   đã cài app ghép HTML mới với CSS cũ — kiểu hỏng khó lần ra nhất
   trong repo, theo đúng chữ của CLAUDE.md. */
export function fileRa(cung) {
  return [...fileSua(cung), `${thuMuc(cung)}sw.js`];
}
