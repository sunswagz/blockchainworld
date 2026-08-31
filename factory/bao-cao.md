# Sức khoẻ xưởng — 31/08/2026 14:36 UTC · lượt 493

**Xưởng đang khoẻ.** Mọi node có mặt trong sổ đều `ket: ok`, `chuoiLoi` = 0 ở tất cả, và không node nào trễ quá gấp đôi `nhip` của nó.

**Đáng lo: không có.** Đáng ghi mà chưa thành bệnh: `dai-quan-trac` ngã đúng một lượt 30/08 21:24 (`scan.js` teo còn 3805 byte, bản cũ 8871) — cổng chặn giữ bản cũ, lượt 23:37 đã ok lại. Cùng lỗi ấy từng nổ 26/08. Hai lần cách nhau bốn ngày, chưa thành chuỗi.

**Chạy được mà đầu ra đứng yên:**
- `hoang-thanh` — lượt 28/08 báo ok nhưng `lucDoi` vẫn là 14/08: 17 ngày không đổi một byte. Node chạy tay (`nhip` 0), nguồn nằm ngoài repo.
- `tri-thuc` — `lucDoi` = null, tức chưa lượt nào ghi ra thay đổi, dù lượt gần nhất (30/08 06:09) ok. Sổ đăng ký nói nó cố ý bỏ qua cung nào nội dung không đổi, nên chưa kết luận được đây là hỏng hay là đúng thiết kế.
- `dong-dau` cũng `lucDoi` = null nhưng `ra` rỗng — không tính.

**Việc nên làm trước:** chạy `npm run hoangthanh` rồi xem `hoang-thanh/assets/js/data.js` có đổi không. Đổi thì 17 ngày kia chỉ là do lâu không ai chạy tay; không đổi thì nguồn ngoài repo đã đứng, và cung đang phục vụ số liệu từ 14/08 mà không dấu hiệu nào báo.
