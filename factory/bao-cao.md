# Sức khoẻ xưởng — 01/09/2026 19:03 UTC · lượt 539

**Xưởng đang khoẻ.** 27 node có dòng trong sổ đều `ket: ok`, `chuoiLoi` của tất cả bằng 0.

**Không có node nào đáng lo.** Không cái nào `chuoiLoi >= 2`, không cái nào trễ quá gấp đôi `nhip`. Bốn node khai `nhip: 0` (`hoang-thanh`, `kham-thien-giam`, `thi-bac-ty`, `tu-cam-thanh`, và `giao-hang` chạy theo) nên không tính trễ. Đáng theo dõi chứ chưa đáng báo động: `tien-hoa-xoay` ngã hai lượt liên tiếp — 31/08 21:04 (tang-thu-cac) và 01/09 00:43 (thi-bac-ty), cùng ghi "ngã ở MODEL" — rồi tự đứng dậy lúc 09:10, nên chuỗi đã về 0.

**Chạy được mà số không đổi:**

- `hoang-thanh` — `lucDoi` đứng ở 14/08, mười tám ngày. Lượt tay gần nhất 28/08 chạy xong với `doi: false`. Đáng ngờ nhất trong sổ.
- `tri-thuc` — `lucDoi` là `null`: chưa lượt nào ghi ra thay đổi, dù `tri-thuc-tien-hoa` đã sửa dữ liệu nguồn ở cả lượt 30/08 lẫn 31/08. CẦN KIỂM.
- `tien-hoa-dqt` — `lucDoi` đứng từ 30/08 05:46, nhưng sổ tự khai lý do: "0 điểm yếu". Phiếu đầy thì không gọi model, nên đây không phải hỏng.

**Việc nên làm trước:** chạy `npm run hoangthanh` ở máy có nguồn, rồi xem `lucDoi` có nhích khỏi 14/08 không. Nhích thì node vẫn sống và chỉ là lâu ngày không chạy tay; không nhích thì nguồn ngoài repo đã đứng, và đó là việc phải sửa ở nguồn chứ không ở xưởng.
