# Báo cáo sức khoẻ xưởng — 26/08/2026 20:42 UTC (lượt 308)

Xưởng chạy được, nhưng có một chỗ hỏng kinh niên: 21/23 node trong sổ đang `ok`, hai node `loi`, và một trong hai đã ngã 8 lượt liên tiếp.

**Đáng lo — `chuoiLoi` ≥ 2**

- `tien-hoa-dqt` (nhịp 24h): `chuoiLoi` 8, `lucOk` và `lucDoi` đều **null** — node này **chưa từng có một lượt thành công nào** trong sổ. Lượt nào cũng cùng một chú thích: "1 điểm yếu · haiku-4-5 · cổng chặn quyết định". Nó vẫn chạy đúng nhịp; thứ hỏng là bản vá luôn bị cổng trả lại.

**Đáng theo dõi — mới ngã, chưa thành chuỗi**

- `dai-quan-trac` (nhịp 12h): `chuoiLoi` 1, ngã lúc 20:42 vì kiểm không qua — `scan.js` teo 5985→2701 byte, `tq/scan.js` teo 7896→2479 byte. Lượt liền trước (20:22) vẫn `ok`. Đúng kiểu lỗi này đã xảy ra một lần ngày 24/08 rồi tự khỏi ở lượt kế.

**Không node nào trễ quá gấp đôi nhịp.** Gần nhất là `bao-cao` (nhịp 24h, lần cuối 25/08 13:41 → trễ ~7 giờ), vẫn trong ngưỡng.

**Chạy đều nhưng nguồn phía sau đứng im**

- `dong-dau` (nhịp 6h): `ok` mọi lượt nhưng `lucDoi` là **null** — chưa lượt nào sinh ra thay đổi. Sổ đăng ký nói node này tự bỏ qua khi sha256 trùng bản trước, nên đây có thể là hành vi đúng chứ không phải hỏng.
- `ho-bo-tien-hoa`: `ok` lúc 20:28 nhưng `doi: false`, `lucDoi` vẫn là 25/08 13:30 — trượt một lượt không đổi gì.
- `hoang-thanh`: `luc` = `lucDoi` = 14/08 09:16, tức **12 ngày không đổi**. Nhịp của nó là 0 (chạy tay) nên không tính là trễ, nhưng bản ghi duy nhất trong sổ là mồi từ `generatedAt` sẵn có.

**Việc nên làm trước:** mở `tien-hoa-dqt` — 8 lượt liên tiếp bị cổng chặn, chưa từng qua, nghĩa là mỗi lượt đang đốt một lần gọi model mà không đổi lấy gì.
