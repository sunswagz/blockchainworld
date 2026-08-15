# Kỹ năng: Đọc chỉ báo kỹ thuật

Chỉ báo là **đo lường**, không phải tín hiệu. `RSI < 30` không phải lệnh mua; nó
là một dữ kiện, và ý nghĩa của nó phụ thuộc hoàn toàn vào chế độ thị trường.

## Từng chỉ báo nói gì

**EMA 20/50/200** — cấu trúc xu hướng theo tầng thời gian.
`BULLISH_ALIGNED` (20>50>200) là xu hướng tăng đã trưởng thành. `MIXED` nghĩa là
đang giằng co — và giằng co là lý do để chờ, không phải để đoán bên thắng.

**RSI(14)** — động lượng, **không phải** chỉ báo quá mua/quá bán.
- Trong `RANGE`: 70/30 là biên có ý nghĩa.
- Trong `TREND_UP`: RSI có thể ở trên 70 hàng tuần. Bán vì "quá mua" trong xu
  hướng tăng là cách thua tiền phổ biến nhất mà vẫn thấy mình có lý.
- Thứ đáng giá nhất là **phân kỳ**: giá tạo đỉnh cao hơn còn RSI thì không.
- `rsiSlope` cho biết động lượng đang mạnh lên hay yếu đi — quan trọng hơn mức tuyệt đối.

**MACD histogram** — gia tốc. Histogram co lại nghĩa là xu hướng đang mất đà,
**trước** khi giá quay đầu. `macdHistSlope` đổi dấu là cảnh báo sớm, không phải
tín hiệu vào lệnh.

**ADX** — độ mạnh xu hướng, **không có hướng**. ADX 40 chỉ nói "đang có xu hướng
mạnh", không nói tăng hay giảm; hướng đọc ở `plusDI` vs `minusDI`.
- < 18: không có xu hướng. Chiến lược thuận xu hướng sẽ bị cắt liên tục.
- 18–22: vùng lưng chừng, đừng ép nhãn.
- \> 22: có xu hướng. \> 40: xu hướng mạnh, nhưng cũng thường là gần cuối.

**ATR** — biến động, đầu vào cho việc đặt stop và tính size. Đọc `atrRatioVsMedian`
chứ đừng đọc số tuyệt đối.

**Bollinger Bands** — `bbWidthPct` co lại là biến động nén, thường đi trước một
cú giãn nở. **Nó không nói hướng.** `bbPosition` gần 1 = sát biên trên.

**Volume** — `volumeRatio` so với trung bình 20 nến. Volume xác nhận phá vỡ; phá
vỡ không có volume nên coi là đáng ngờ cho tới khi có bằng chứng ngược lại.

## Cách hợp nhất

1. Xác định chế độ thị trường trước.
2. Chỉ đọc các chỉ báo có nghĩa trong chế độ đó.
3. Tìm **hợp lưu**: nhiều thứ độc lập cùng chỉ một hướng.
4. Tìm **mâu thuẫn** to bằng cách tìm hợp lưu. Mâu thuẫn giữa các khung thời
   gian là lý do đủ mạnh để NO_TRADE.

## Cái bẫy

Đừng liệt kê chỉ báo rồi cộng điểm. Bảy chỉ báo phái sinh từ cùng một chuỗi giá
không phải bảy bằng chứng độc lập — chúng gần như luôn đồng ý với nhau, và cảm
giác "mọi thứ đều xác nhận" chính là lúc nên nghi ngờ nhất.
