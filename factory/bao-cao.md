# Báo cáo sức khoẻ xưởng — 22/08/2026 07:04 UTC (lượt 158)

**Tổng:** Xưởng khoẻ — 19/20 node có mặt trong sổ đang `ok` ở lượt gần nhất, không node nào trễ quá gấp đôi nhịp. Vẫn đúng một chỗ đang ngã, và là chỗ cũ.

**Đáng lo**
- `tien-hoa-dqt` (Tiến hoá Đài Quan Trắc, nhịp 24h): `chuoiLoi` = 3 — ngã ba lượt liên tiếp (20/08 19:10, 21/08 02:16, 21/08 07:12), cùng một ghi chú "1 điểm yếu · haiku-4-5 · cổng chặn quyết định". `lucOk` = null: **node này chưa có lượt thành công nào** trong sổ. Chuỗi tăng từ 2 lên 3 kể từ báo cáo trước, tức lượt kế tiếp không sửa được gì.
- Trễ nhịp: không có. Node xa hạn nhất là `bao-cao` (nhịp 24h, lượt cuối 21/08 02:17 → ~28,8 giờ) và `tien-hoa-dqt` (~23,9 giờ) — cả hai còn xa ngưỡng gấp đôi.

**Chạy đều nhưng `lucDoi` không nhúc nhích**
- `dong-dau` (nhịp 6h): mọi lượt trong nhật ký đều `ket: ok` nhưng `doi: false`, `lucDoi` = null — chưa lần nào đổi kể từ khi sổ ghi. Sổ đăng ký khai `ra: []` và "tự bỏ qua nếu sha256 trùng bản trước", nên đây có thể là hành vi đúng chứ chưa hẳn là hỏng.
- `hoang-thanh`: `lucDoi` vẫn đứng ở 14/08 (8 ngày). `nhip: 0`, chế "tay" — dữ liệu cũ vì không ai chạy tay, không phải bot hỏng.
- Ba node tay khác trong sổ đăng ký (`tu-cam-thanh`, `kham-thien-giam`, `thi-bac-ty`) và `giao-hang` chưa có dòng nào trong state; cả bốn đều `nhip: 0` nên không tính là trễ.
- Đã tự khỏi: `thai-boc-tu-tin-pt` từ "nhận 0 · phủ 30/30" (20/08) sang "nhận 12 · loại 0 · phủ 13/30" (22/08 02:13).

**Việc nên làm trước:** mở lượt `tien-hoa-dqt` 21/08 07:12 xem cổng chặn trả lại bản vá vì lý do gì. Đó là node duy nhất đang `loi`, đã ngã ba lượt liên tiếp, và chưa từng thành công lần nào — mỗi lượt tiếp theo là một lần gọi model chắc chắn bị trả lại.
