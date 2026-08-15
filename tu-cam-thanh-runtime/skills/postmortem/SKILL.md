# Kỹ năng: Hậu kiểm giao dịch

Kỹ năng quan trọng nhất trong kho, vì nó quyết định bot **học ra cái gì**.

## Nguyên tắc trung tâm: quyết định ≠ kết quả

Thị trường có tính ngẫu nhiên. Một quyết định tốt vẫn thua, một quyết định tồi
vẫn thắng. Học theo tiền lãi/lỗ thay vì theo chất lượng quyết định thì cuối cùng
sẽ học ra cờ bạc — và nó sẽ học rất nhanh, vì phần thưởng đến ngay.

|  | Kết quả tốt | Kết quả xấu |
|---|---|---|
| **Quyết định tốt** | `GOOD_TRADE_GOOD_OUTCOME` — giữ nguyên | `GOOD_TRADE_BAD_OUTCOME` — **giữ nguyên** |
| **Quyết định tồi** | `BAD_TRADE_GOOD_OUTCOME` — **cảnh báo, đừng lặp lại** | `BAD_TRADE_BAD_OUTCOME` — sửa |

Hai ô in đậm là hai ô hay bị đọc sai nhất, và cũng là hai ô mang gần như toàn bộ
giá trị của việc hậu kiểm.

## Bảy câu hỏi, trả lời độc lập

1. Chế độ thị trường lúc vào lệnh là gì?
2. Chiến lược có hợp chế độ đó không?
3. Điểm vào có đúng theo setup không, hay đã đuổi giá?
4. Kích thước vị thế có đúng luật không?
5. Có bỏ qua mâu thuẫn giữa các khung / rủi ro sự kiện nào không?
6. Stop đặt ở chỗ cấu trúc, hay ở một con số tuỳ tiện?
7. **Luận điểm có sai không, hay chỉ là một lần thua trong biên độ thống kê
   bình thường?**

Câu 7 quyết định `thesis_was_wrong`. Dính stop ở đúng chỗ đã định, vì đúng lý do
đã lường trước, là **luận điểm đúng và kết quả xấu** — không phải luận điểm sai.

## `change_strategy` — cửa hẹp

Chỉ đặt `true` khi có **mẫu lặp lại qua nhiều lệnh**, ví dụ: "bốn lệnh gần nhất
trong `RANGE` đều bị quét trước khi chạy đúng hướng". Một lệnh không bao giờ đủ.

Đổi chiến lược sau mỗi lệnh thua là đường cong sát thủ: hệ thống đuổi theo nhiễu,
mọi thay đổi đều được biện minh bằng lệnh gần nhất, và không phiên bản nào sống
đủ lâu để biết nó tốt hay xấu.

## Viết bài học cho lần sau đọc

Bài học sẽ được đưa lại vào prompt khi gặp regime tương tự. Viết sao cho **có
thể hành động được** và **kiểm chứng được**:

- Tệ: "cần cẩn thận hơn"
- Tệ: "lẽ ra nên chờ xác nhận"
- Được: "Trong `RANGE` + `LOW_VOLATILITY`, phá biên không kèm volume > 1.4× đã
  quay đầu 3/4 lần. Chờ nến đóng ngoài biên trước khi vào."

Nếu bài học không nói được **lần sau làm khác đi ở chỗ nào**, thì đó không phải
bài học, chỉ là cảm xúc sau một lệnh thua.
