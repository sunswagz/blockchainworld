# Báo cáo sức khoẻ xưởng — 16/08/2026 13:16Z (lượt 33)

**Xưởng đang khoẻ.** Cả 10 node có bản ghi đều `ket: ok`, `chuoiLoi = 0`, và không node nào trễ quá nhịp của nó.

**Không có node nào đáng lo.** Sáu node nhịp 6 giờ (kinh-thanh, do-sat-vien, cong-bo, ho-bo, tang-thu-cac, quan-trac-do) đều vừa chạy trong vòng 13 phút trước lúc chốt sổ, đều `doi: true`. `dai-quan-trac` nhịp 12 giờ, chạy cách 6,2 giờ. `bao-cao` nhịp 24 giờ, chạy cách 23 giờ — sắp đến hạn, chưa trễ. Lượt lỗi duy nhất còn trong nhật ký là `dai-quan-trac` ngày 15/08 13:14 (bộ kiểm chặn `scan.js` teo từ 10188 xuống 3886 byte); hai lượt sau đó đã ok và `doi: true`, nên đã tự hồi.

**Chạy đều nhưng dữ liệu không đổi:**

- `dong-dau` — chạy đủ mọi lượt, nhưng `lucDoi` là `null` và cả ba lượt trong nhật ký đều `doi: false`. Sổ đăng ký khai `ra: []`, nên node này **không thể** có `doi: true`; đây là đặc điểm cấu trúc, không phải nguồn chết. Đừng đọc thành báo động.
- `hoang-thanh` — `lucDoi` đứng ở 14/08 09:16, đã hơn 2 ngày. Nhưng nó là node `che: tay`, `nhip: 0`, và bản ghi duy nhất mang chú thích "mồi từ dấu generatedAt sẵn có trong file": nó chưa từng thật sự chạy qua xưởng, nên "lâu không đổi" ở đây nghĩa là lâu chưa ai chạy tay.
- `tu-cam-thanh` — có trong `registry.json` nhưng **không có bản ghi nào trong `state.json`**. Cũng là node `che: tay`, `nhip: 0`.

**Việc nên làm trước:** chạy tay hai node `che: tay` — `npm run hoangthanh` và `python -m trader.snapshot` — vì đó là hai chỗ duy nhất trong sổ đang đứng yên, và cả hai đứng yên vì không có lịch tự động chứ không vì hỏng.
