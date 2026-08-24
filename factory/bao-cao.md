# Sức khoẻ xưởng — 24/08/2026 07:52 UTC · lượt 221

Xưởng khoẻ, trừ đúng một chỗ: 19/20 node có mặt trong sổ ghi `ok` ở lượt gần nhất, và không node nào trễ quá gấp đôi `nhip` của nó.

**Đáng lo — `tien-hoa-dqt`.** `chuoiLoi` là 5, `ket` là `loi`, và `lucOk` là `null`: node này **chưa `ok` lượt nào**. Bốn lượt còn trong nhật ký (20/08 19:10, 21/08 07:12, 22/08 13:14, 23/08 18:53) đều cùng một dòng `1 điểm yếu · haiku-4-5 · cổng chặn quyết định`, và `doi` luôn là `false` — không lượt nào ghi được gì. Ba node cùng khuôn `tien-hoa` (`ho-bo`, `thai-boc-tu`, `kham-thien-giam`) thì đều `ok`, phiếu đo 6/7.

**Không node nào trễ hạn.** Xa hạn nhất là `bao-cao`: 24,5 giờ trên `nhip` 24 — chưa tới ngưỡng gấp đôi. `dai-quan-trac` có ngã một lượt lúc 02:13 (`tq/scan.js` teo từ 10.571 xuống 3.843 byte, phép kiểm chặn lại) nhưng lượt 07:33 đã `ok` và `chuoiLoi` về 0, nên đó là một cú vấp đã tự đứng dậy chứ không phải bệnh.

**Chạy đều mà chưa từng đổi — `dong-dau`.** Nhịp 6 giờ, lượt nào cũng `ok`, nhưng `lucDoi` là `null` và mọi mục nhật ký của nó đều `doi: false`: chưa lượt nào sinh ra thay đổi. Sổ đăng ký ghi nó "tự bỏ qua nếu sha256 trùng bản trước", nên đây có thể đúng thiết kế — cũng có thể bản số liệu đằng sau đã đứng yên. (`hoang-thanh` có `lucDoi` từ 14/08, tức 10 ngày, nhưng `nhip` là 0 và `che` là `tay` nên không tính vào nhóm chạy đều.)

**Việc nên làm trước:** mở `tien-hoa-dqt`. Một node nhịp 24 giờ ngã 5 lượt liên tiếp và chưa `ok` lần nào thì không phải sự cố nhất thời — hoặc cổng đang trả lại mọi bản vá, hoặc phiếu đo Đài Quan Trắc mắc ở một điểm yếu model không vá nổi.
