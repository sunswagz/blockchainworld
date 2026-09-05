# Báo cáo sức khoẻ xưởng — 05/09/2026 05:09 UTC (lượt 696)

**Tổng:** Xưởng chạy được nhưng có chuyện — 26/28 node ghi `ok` ở lượt gần nhất, hai node đang ngã, và một trong hai đã ngã 9 lượt liền.

**Đáng lo**
- `dong-dau` — `chuoiLoi` 9, `vi: "khoa-sai"`. Lượt chạy được cuối cùng là 02/09 11:37 UTC, tức đã hỏng liên tục ~65 giờ ở nhịp 6 giờ. Chín lượt cùng một lý do nghĩa là nó sẽ không tự khỏi.
- `thuoc-moi` — `chuoiLoi` 2, `vi: "chua-ro"`, và `lucOk` là `null`: node này **chưa từng có lượt nào chạy được**. Hai lượt ngã cách nhau 2 giờ (04/09 21:04 và 23:07) dù nhịp khai là 168 giờ.
- Không node nào trễ quá gấp đôi `nhip` của nó. Bốn node `kham-thien-giam`, `thi-bac-ty`, `tu-cam-thanh`, `giao-hang` không có dòng nào trong state.json — cả bốn khai `nhip: 0` nên không có lượt tự động để ghi sổ; CẦN KIỂM chứ chưa phải lỗi.

**Chạy được mà chưa đổi được gì**
- `tri-thuc` — ba lượt gần nhất (01/09, 02/09, 03/09) đều `ok` mà `doi` đều `false`, và `lucDoi` vẫn là `null`: chạy trọn nhưng chưa lần nào ghi ra thay đổi.
- `hoang-thanh` — `ket: "ok"` nhưng `lucDoi` đứng ở 14/08, tức 22 ngày, trong khi lượt chạy gần nhất là 28/08. Node khai `nhip: 0` (chạy tay), nên đây là hệ quả của việc chưa ai chạy lại, không phải nguồn dữ liệu chết.

**Việc nên làm trước:** kiểm và thay khoá cho `dong-dau` — nó hỏng đúng một cách suốt 9 lượt, và `vi: "khoa-sai"` đã chỉ thẳng chỗ hỏng.
