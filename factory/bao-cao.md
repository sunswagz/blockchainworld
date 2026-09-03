# Sức khoẻ xưởng — 03/09/2026 23:30 UTC · lượt 636

Xưởng chạy được nhưng có hai vết: 2 trên 31 node đang ngã, mọi node còn lại `ok` và không node nào trễ quá gấp đôi `nhip` của nó.

**Đáng lo** — `dong-dau`: chuỗi lỗi **5**, cớ `khoa-sai`, lượt `ok` cuối 02/09 11:37; nhịp 6 giờ nên nó đã ngã năm lượt liền, và mỗi lượt ngã là một bản số liệu không được đóng dấu.
`tien-hoa-xoay`: chuỗi lỗi **2**, cả hai lượt 03/09 (16:38 và 21:32) đều "cong-bo: ngã ở MODEL", cớ `chua-ro`. Phiếu đo 17/17 → 17/17 nên không tụt điểm nào; thứ mất là hai lượt tiến hoá của cong-bo.

**Chạy đều mà chưa đổi được gì** — `tri-thuc`: `ok` mọi lượt nhưng `lucDoi` là `null`, chưa lượt nào ghi được file nào. Nó sinh lát cắt cho 11 cung, nên đáng hỏi nguồn `knowledge-os/data/` phía sau có còn đổi không.
`hoang-thanh`: `ok`, nhưng `lucDoi` 14/08 — 20 ngày nội dung không đổi. `nhip: 0` (chạy tay) nên không tính là trễ.

**Cần kiểm** — bốn node vắng hẳn trong `state.json` (`kham-thien-giam`, `thi-bac-ty`, `tu-cam-thanh`, `giao-hang`) đều khai `nhip: 0`, tức chạy tay hoặc chạy theo commit; vắng là đúng hình dạng của chúng, không phải hỏng.

**Việc nên làm trước** — sửa khoá cho `dong-dau`. Đó là node duy nhất có chuỗi lỗi ≥ 5 kèm nguyên nhân đã có tên (`khoa-sai`), nên sửa được ngay mà không phải đoán.
