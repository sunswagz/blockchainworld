# Báo cáo sức khoẻ xưởng

Chưa có lượt báo cáo nào.

File này do node `bao-cao` (M18) ghi đè, một lượt mỗi ngày. Nội dung
thật sẽ thay chỗ mấy dòng này ngay lượt chạy đầu tiên.

Vì sao nó nằm sẵn trong repo dù chưa có nội dung: bước commit của
`refresh-data.yml` liệt kê TỪNG đường dẫn cho `git add`. Mà `git add`
gặp pathspec không khớp file nào thì không bỏ qua — nó chết với mã
128 và kéo cả lượt chạy đỏ theo, kể cả khi mọi node khác đã xong.
Lượt #10 và #11 ngày 15/08/2026 đỏ đúng vì lý do này.

Có file mồi thì đường dẫn luôn khớp, và danh sách `git add` vẫn khớp
được với `ra` của node trong `scripts/nha-may.mjs` — thứ mà
`npm run kiem` đối chiếu.
