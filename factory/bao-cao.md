# Báo cáo sức khoẻ xưởng

Chốt sổ 15/08/2026 13:11 UTC (lượt #6): xưởng về cơ bản khoẻ — mọi node
có mặt trong sổ đều `ket: ok`, `chuoiLoi` = 0 — nhưng có một node im.

**Đáng lo — `dai-quan-trac` (bản quét, nhịp 12 giờ).** Dấu cuối là
13/08 08:53, tức ~52 giờ trước lúc chốt sổ, hơn **4 lần** nhịp của nó.
Nó không đỏ, và đó mới là chỗ khó thấy: `chuThich` ghi "mồi từ dấu
generatedAt sẵn có trong file", nghĩa là sổ chưa ghi nhận **lượt chạy
thật nào** của node này — nó im chứ không ngã.

**Không ghi nhận trong sổ: `bao-cao` (M18, nhịp 24 giờ).** Có trong
`registry.json` nhưng không có mục nào trong `state.json`.

**Chạy đều mà dữ liệu đứng im: không có.** Năm node nhịp 6 giờ đều chạy
trong khoảng 13:01–13:11 hôm nay với `doi: true` và `lucDoi` đúng bằng
lượt đó. `dong-dau` có `doi: false`, `lucDoi: null` — đúng thiết kế đã
ghi trong sổ đăng ký (bỏ qua khi sha256 trùng bản trước). `hoang-thanh`
và `tu-cam-thanh` là `che: tay`, `nhip: 0`, không tính trễ.

**Làm trước:** tìm xem vì sao `dai-quan-trac` chưa có lượt chạy thật nào.
