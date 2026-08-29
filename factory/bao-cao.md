# Sức khoẻ xưởng — 29/08/2026 03:47Z · lượt 376

**Xưởng đang khoẻ.** Cả 23 node có mặt trong sổ đều `ket: ok` và `chuoiLoi` bằng 0; 21 node vừa chạy gọn trong khoảng 03:11–03:47.

**Không node nào đáng lo theo hai phép đo.** Không có `chuoiLoi >= 2`, và không node nào trễ quá gấp đôi `nhip`. Sát nhất là `bao-cao` (nhịp 24 giờ, lượt trước 27/08 22:52 — khoảng 29 giờ), vẫn dưới một nhịp rưỡi. Đáng để mắt chứ chưa đáng lo: `tien-hoa-dqt` ngã năm lượt liền từ 23/08 tới 27/08 (cổng chặn trả lại), lượt 29/08 03:30 mới nhận được bản vá nên chuỗi vừa về 0.

**Chạy đều nhưng nguồn có thể đã đứng:** `hoang-thanh` báo ok lúc 28/08 15:37 mà `lucDoi` vẫn là 14/08 09:16 — mười lăm ngày không đổi nội dung. Node này `che: tay`, `nhip: 0`, nguồn nằm ngoài repo, nên "ok mà không đổi" ở đây chưa chắc là hỏng; chỉ là chỗ duy nhất trong sổ có khoảng cách đó. (`dong-dau` có `lucDoi: null` nhưng đúng thiết kế: bỏ qua khi sha256 trùng bản trước.)

**Một chỗ lệch giữa hai file:** `tri-thuc` và `tri-thuc-tien-hoa` khai `nhip: 24` trong sổ đăng ký nhưng KHÔNG có dòng nào trong `state.json` — không ở bảng `node`, không ở nhật ký `nk`. Bốn node vắng mặt còn lại (`kham-thien-giam`, `thi-bac-ty`, `tu-cam-thanh`, `giao-hang`) đều `nhip: 0` nên vắng là đúng.

**Việc nên làm trước:** truy xem `tri-thuc` và `tri-thuc-tien-hoa` có thật sự được gọi không — hai node khai nhịp 24 giờ mà chưa ghi được lượt nào vào sổ.
