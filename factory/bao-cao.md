# Báo cáo sức khoẻ xưởng — 17/08/2026 19:02Z (lượt 51)

**Xưởng đang khoẻ.** Cả 10 node có bản ghi đều `ket: ok` và `chuoiLoi = 0`; không node nào ngã lượt nào trong nhật ký kể từ 15/08.

**Không có node nào đáng lo.** Không có `chuoiLoi >= 2`, và không node nào trễ quá gấp đôi nhịp. Sáu node nhịp 6 giờ (kinh-thanh, do-sat-vien, cong-bo, ho-bo, tang-thu-cac, quan-trac-do) chạy lúc 13:10–13:17, tức cách 5,8 giờ — chưa tới hạn. `kinh-thanh` còn chạy thêm lượt 19:00 và `dai-quan-trac` (nhịp 12) chạy 19:02, cả hai `doi: true`. Chỉ `bao-cao` (nhịp 24) là vừa quá hạn: lượt gần nhất 16/08 18:49, cách 24,2 giờ — quá nhịp 0,2 giờ, còn xa mức đáng lo.

Lượt lỗi duy nhất còn trong nhật ký vẫn là `dai-quan-trac` ngày 15/08 13:14 (bộ kiểm chặn `scan.js` teo từ 10188 xuống 3886 byte). Bốn lượt sau đó đều ok và `doi: true`, nên đã hồi hẳn.

**Chạy đều nhưng dữ liệu không đổi:**

- `dong-dau` — chạy đủ mọi lượt, `lucDoi` vẫn `null`, mọi lượt `doi: false`. Sổ đăng ký khai `ra: []`, nên node này **không thể** có `doi: true`; đó là đặc điểm cấu trúc, không phải nguồn chết. Đừng đọc thành báo động.
- `hoang-thanh` — `lucDoi` đứng ở 14/08 09:16, đã 3,4 ngày. Nhưng nó `che: tay`, `nhip: 0`, và bản ghi duy nhất mang chú thích "mồi từ dấu generatedAt sẵn có trong file": nó chưa từng thật sự chạy qua xưởng.
- `tu-cam-thanh` — có trong `registry.json` nhưng **không có bản ghi nào trong `state.json`**. Cũng `che: tay`, `nhip: 0`.

Ngoài ba dòng trên, mọi node đều có `lucDoi` trùng đúng lượt chạy gần nhất — không chỗ nào chạy suông mà nguồn đứng yên.

**Việc nên làm trước:** chạy tay `cd tu-cam-thanh-runtime && python -m trader.snapshot`. Đó là node duy nhất trong sổ đăng ký chưa từng có một lượt nào trong `state.json`, tức chỗ sổ và thực tế lệch nhau xa nhất — `hoang-thanh` ít ra còn một mốc thời gian để so.
