# Báo cáo sức khoẻ xưởng — 25/08/2026 13:40 UTC (lượt 261)

Xưởng cơ bản khoẻ: 21/22 node trong sổ có lượt gần nhất `ok`, đường số liệu 6 giờ (kinh-thanh, do-sat-vien, cong-bo, ho-bo, thai-boc-tu, tang-thu-cac, quan-trac-do) đều vừa chạy trong vòng 30 phút và đều ghi được dữ liệu mới — chỉ có đúng một node đang ngã dai dẳng.

**Đáng lo — `tien-hoa-dqt` (Tiến hoá Đài Quan Trắc), `chuoiLoi` = 6.** Lượt gần nhất 24/08 19:02, `ket: "loi"`, chú thích lặp y nguyên qua cả sáu lượt: "1 điểm yếu · haiku-4-5 · cổng chặn quyết định". Nặng hơn con số 6: `lucOk` và `lucDoi` đều `null` — node này **chưa từng có một lượt thành công nào**, chưa từng ghi được byte nào vào `dai-quan-trac/assets/{css/app.css,js/app.js}`. Trong nhật ký nó ngã đều từ 20/08 19:10 trở đi, không lượt nào khác kiểu.

**Không có node nào trễ quá gấp đôi `nhip`.** Gần nhất là `bao-cao` (nhịp 24 giờ, chạy lần cuối 24/08 07:53 — trễ khoảng 30 giờ) và `tien-hoa-dqt` (nhịp 24, trễ ~18,6 giờ, chưa tới hạn). Ba node `che: "tay"` — `hoang-thanh`, `kham-thien-giam`, `thi-bac-ty`, `tu-cam-thanh` — khai `nhip: 0` nên không tính là trễ.

**Chạy được mà nguồn có thể đã chết:** không có. Mọi node có `nhip > 0` và `ket: "ok"` đều có `lucDoi` trùng đúng `luc` của lượt gần nhất, nghĩa là lượt nào cũng ghi ra dữ liệu khác bản trước.

Hai chỗ `doi: false` không phải dấu hiệu nguồn chết:
- `dong-dau` — `ra` rỗng, bản chất là pin IPFS bỏ qua khi sha256 trùng, nên `lucDoi: null` là đúng thiết kế.
- `hoang-thanh` — `lucDoi` 14/08 09:16, đứng yên 11 ngày, nhưng đó là node chạy tay (`nhip: 0`, `npm run hoangthanh`), sổ ghi rõ chú thích "mồi từ dấu generatedAt sẵn có trong file".

## Việc nên làm trước

Mở phiếu đo bảy thước của `tien-hoa-dqt` và xem "1 điểm yếu" đó là thước nào: node đã sáu lượt liên tiếp gọi model rồi bị chính cổng chặn của mình trả lại, chưa lần nào qua — nên vấn đề nằm ở cổng hoặc ở đề bài, không phải ở một lượt xui.
