# Báo cáo sức khoẻ xưởng — 21/08/2026 02:16 UTC (lượt 126)

**Tổng:** Xưởng về cơ bản khoẻ — 19/20 node có mặt trong sổ đang `ok` ở lượt gần nhất, và không node nào trễ quá gấp đôi nhịp. Đúng một chỗ đang ngã.

**Đáng lo**
- `tien-hoa-dqt` (Tiến hoá Đài Quan Trắc, nhịp 24h): `chuoiLoi` = 2 — ngã hai lượt liên tiếp (20/08 19:10 và 21/08 02:16), cùng một ghi chú "1 điểm yếu · haiku-4-5 · cổng chặn quyết định". Nặng hơn con số đó: `lucOk` = null, tức **node này chưa có lượt thành công nào** trong sổ, không có mốc "trước đây chạy được" để so.
- Trễ nhịp: không có. `bao-cao` (nhịp 24h, lượt cuối 20/08 02:08) vừa chớm quá hạn một chút, chưa tới ngưỡng đáng nói.

**Chạy đều nhưng `lucDoi` không nhúc nhích**
- `dong-dau` (nhịp 6h): mọi lượt trong nhật ký đều `ket: ok` nhưng `doi: false`, và `lucDoi` = null — chưa lần nào bản pin đổi kể từ khi sổ bắt đầu ghi.
- `thai-boc-tu-tin-pt` (20/08 19:17): `ok` và `doi: true`, nhưng ghi chú "nhận 0 · loại 0 · phủ 30/30 bài" — phủ hết bài mà không nhận được mục nào.
- `hoang-thanh`: `lucDoi` đứng ở 14/08 (7 ngày). Node này `nhip: 0`, chế "tay" nên vốn không tự chạy — dữ liệu cũ, không phải bot hỏng. Hai node tay khác trong sổ đăng ký (`tu-cam-thanh`, `kham-thien-giam`) chưa có dòng nào trong state.

**Việc nên làm trước:** xem lượt `tien-hoa-dqt` gần nhất — cổng chặn trả lại bản vá vì lý do gì. Đó là node duy nhất đang `loi`, đã ngã liên tiếp, và chưa từng thành công lần nào.
