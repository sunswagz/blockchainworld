# Sức khoẻ xưởng — chốt 20/08/2026 02:07 UTC (lượt 94)

Xưởng đang khoẻ: cả 12 node có ghi lượt đều `ket: ok`, `chuoiLoi` bằng 0 ở mọi node, lỗi gần nhất trong nhật ký là 15/08 (`dai-quan-trac`, kiểm chặn vì `scan.js` teo còn 3886 byte so với 10188 byte bản cũ) và lượt sau đã qua.

**Đáng lo: không có.** Không node nào `chuoiLoi >= 2`, cũng không node nào trễ quá gấp đôi `nhip`. Sát ngưỡng nhất là `bao-cao` — nhịp 24 giờ, lượt cuối 18/08 19:01, tức 31 giờ tính tới dấu chốt trên, khoảng 1,3× nhịp. Chưa tới mức phải xem.

**Chạy đều mà dữ liệu có thể đã đứng:**
- `dong-dau` — 11 lượt trong nhật ký đều `doi: false`, `lucDoi` vẫn là `null`, tức chưa lần nào ghi nhận thay đổi. Nhưng sổ đăng ký khai `ra: []` cho node này, nên có thể `doi` không bao giờ true được về mặt cấu trúc; hai file này không đủ để kết luận nguồn phía sau đã chết.
- Mười node còn lại đều có `lucDoi` trùng đúng `luc` của lượt gần nhất — dữ liệu đổi thật ở lượt cuối, không phải chạy suông.

**Hai node `che: tay` đang đứng im:** `hoang-thanh` chỉ có đúng một dấu 14/08 09:16 kèm chú thích "mồi từ dấu generatedAt sẵn có trong file" — chưa từng có lượt chạy thật, đã 6 ngày. `tu-cam-thanh` có trong sổ đăng ký nhưng **không có mục nào** trong `state.json`.

**Việc nên làm trước:** chạy tay `npm run hoangthanh` rồi commit, để node có dấu cũ nhất trong sổ đổi từ một dấu mồi thành một lượt thật.
