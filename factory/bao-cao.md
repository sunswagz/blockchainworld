# Sức khoẻ xưởng — 23/08/2026 07:19 UTC (lượt 189)

Xưởng về cơ bản khoẻ: 21/22 node ở `ok`, chỉ đúng một node đang ngã, và nó ngã dai.

**Đáng lo — `tien-hoa-dqt` (Tiến hoá Đài Quan Trắc, nhịp 24h).** `ket: loi`,
`chuoiLoi: 4`, và `lucOk: null` — trong cả sổ này nó **chưa từng có lượt nào ok**.
Bốn lượt ngã liên tiếp (20/08 19:10, 21/08 02:16, 21/08 07:12, 22/08 13:14) đều
cùng một chú thích: `1 điểm yếu · haiku-4-5 · cổng chặn quyết định`. Tức là node
vẫn chạy, model vẫn đề xuất, nhưng cổng chặn trả lại bản vá mỗi lần — cùng một
điểm yếu, không lượt nào qua. `doi: false` cả bốn lượt, nên không có gì được ghi ra.

**Trễ nhịp:** không có. Mọi node `nhip > 0` đều chạy trong vòng một nhịp; `bao-cao`
là sát nhất (24,2h / nhịp 24h), chưa tới ngưỡng gấp đôi.

**Chạy đều mà nguồn có thể đã chết:** không có. Mọi node đến hạn đều có `lucDoi`
trùng `luc` của lượt gần nhất, nghĩa là lượt nào cũng ghi ra được dữ liệu mới.
Riêng `dong-dau` có `lucDoi: null` nhưng `ra` rỗng — không có đường ra để đổi.
Bốn node `nhip: 0` (`hoang-thanh`, `kham-thien-giam`, `thi-bac-ty`, `tu-cam-thanh`)
chạy tay nên không tính trễ; `hoang-thanh` đứng ở 14/08, ba node kia chưa có lượt nào trong sổ.

**Việc nên làm trước:** xem `tien-hoa-dqt` — cổng chặn đang trả lại bản vá bốn lượt
liên tiếp trên cùng một điểm yếu, nên lượt thứ năm nhiều khả năng cũng vậy.
