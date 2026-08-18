# Sức khoẻ xưởng — 18/08/2026 19:00 UTC (lượt 68)

Xưởng đang khoẻ: cả 10 node có ghi trong sổ đều `ket: ok`, `chuoiLoi = 0`,
không node nào trễ quá nhịp của nó.

**Không có node đáng lo.** Lượt `loi` gần nhất là `dai-quan-trac` ngày
15/08 (scan.js teo còn 3886 byte, bộ kiểm chặn lại) — đã chạy lại tốt 4
lượt kể từ đó, gần nhất 19:00 hôm nay.

**Chạy đều nhưng chưa lượt nào ghi đổi:**

- `dong-dau` — chạy đủ nhịp 6 giờ, lượt gần nhất 13:20 hôm nay, nhưng
  `lucDoi` vẫn là `null` và mọi lượt trong nhật ký đều `doi: false`. Sổ
  đăng ký ghi nó "tự bỏ qua nếu sha256 trùng bản trước", nên không rõ đây
  là bỏ qua đúng thiết kế hay là chưa bao giờ pin được lượt nào.
- `hoang-thanh` — `lucDoi` đứng ở 14/08 09:16, đã 4 ngày. Node này `nhip: 0`,
  `che: tay` nên không tính là trễ; nó chỉ đổi khi có người chạy
  `npm run hoangthanh`.
- `tu-cam-thanh` có trong sổ đăng ký nhưng **không có mục nào trong
  state.json** — chưa lượt nào được ghi nhận.

**Việc nên làm trước:** xem `dong-dau` đã pin được lượt nào chưa — đó là
node duy nhất chạy đều mà chưa từng ghi `doi: true`.
