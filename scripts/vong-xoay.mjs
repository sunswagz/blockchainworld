/* ═══════════════════════════════════════════════════════
   VÒNG XOAY — bảy cung dùng chung MỘT node tiến hoá.

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

export const VONG_XOAY = [
  "cong-bo", "do-sat-vien", "hoang-thanh", "kinh-thanh",
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
