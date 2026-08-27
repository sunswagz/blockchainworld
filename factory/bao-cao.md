# Sức khoẻ xưởng — 27/08/2026 22:51 UTC (lượt 340)

Xưởng cơ bản khoẻ: 19/20 node có ghi nhận đều báo `ok` ở lượt gần nhất, 17 trong số đó ghi được dữ liệu mới. Đúng một chỗ hỏng, và nó hỏng dai dẳng.

**Đáng lo**
- `tien-hoa-dqt` (Tiến hoá Đài Quan Trắc, nhịp 24h): `chuoiLoi` = 9, `ket` = `loi`, còn `lucOk` lẫn `lucDoi` đều `null` — node này **chưa từng có một lượt thành công nào** trong sổ. Chín lượt cùng một chú thích: "1 điểm yếu · haiku-4-5 · cổng chặn quyết định", tức bản vá model đề xuất bị cổng số học trả lại lần nào cũng như lần nào.
- Không node nào trễ quá gấp đôi `nhip`. Sát nhất là `bao-cao`: lượt gần nhất 26/08 20:43, cách 26 giờ so với nhịp 24h — trễ nhẹ, chưa tới ngưỡng.

**Chạy được nhưng dữ liệu không đổi**
- `dong-dau`: `ket` = `ok` mọi lượt nhưng `lucDoi` = `null`, chưa đổi lần nào. Sổ đăng ký ghi rõ node này "tự bỏ qua nếu sha256 trùng bản trước" — hành vi đã khai, không phải nguồn chết.
- `hoang-thanh`: `lucDoi` đứng ở 14/08, 13 ngày không đổi — nhưng `nhip` = 0, chế độ `tay`, nó chỉ đổi khi có người chạy tay.
- Ngoài hai cái đó, mọi node `ok` đều có `lucDoi` trùng `luc`: chạy lượt nào ghi được dữ liệu mới lượt đó, không có nguồn nào chết sau lưng.

**Việc nên làm trước**
Mở cổng chặn của `tien-hoa-dqt` xem vì sao 9 lượt liên tiếp đều bị trả lại — hoặc bản vá luôn hỏng, hoặc ngưỡng cổng đặt sai. Hiện mỗi 24 giờ tốn một lượt model mà chưa lần nào ghi được gì.
