# Báo cáo sức khoẻ xưởng — 15/08/2026 14:17 UTC (lượt 16)

Xưởng đang khoẻ: cả 9 node có ghi nhận trong `state.json` đều `ket: ok`, không node nào `chuoiLoi` >= 1.

**Không có node đáng lo.** Không node nào trễ quá gấp đôi `nhip`: bảy node nhịp 6h và 12h đều chạy trong khoảng 14:02–14:17, `bao-cao` (nhịp 24h) chạy 13:12. `hoang-thanh` và `tu-cam-thanh` khai `nhip: 0` (chạy tay) nên không tính trễ.

Một vết cũ, đã tự khỏi: `dai-quan-trac` ngã lúc 13:14 — "kiểm không qua: `scan.js` teo đột ngột 3886 byte, bản cũ 10188 byte". Lượt 14:17 đã `ok` và `doi: true`, chuỗi lỗi về 0.

**Chạy đều nhưng đầu ra không đổi:** `dong-dau` — hai lượt gần nhất (13:11 và 14:16) đều `ok` mà `doi: false`, và `lucDoi` vẫn là `null`, tức chưa lượt nào ghi được thay đổi. Sổ đăng ký ghi nó tự bỏ qua khi sha256 trùng bản trước, nên `lucDoi: null` sau 16 lượt nghĩa là chưa từng đóng dấu được bản nào.

Ngoài ra `tu-cam-thanh` có trong `registry.json` nhưng không có mục nào trong `state.json` — chưa từng được ghi nhận một lượt chạy.

**Việc nên làm trước:** soi `dong-dau` — xác minh nó thật sự pin được bản số liệu, hay chỉ đang bỏ qua im lặng mỗi lượt.
