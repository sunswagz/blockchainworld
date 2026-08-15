# Kỹ năng: Cấu trúc thị trường & vùng giá

## Đọc cấu trúc

Cấu trúc được định nghĩa bằng **đỉnh và đáy swing**, không bằng chỉ báo.

- `UPTREND` — đỉnh cao hơn (HH) **và** đáy cao hơn (HL)
- `DOWNTREND` — đỉnh thấp hơn (LH) **và** đáy thấp hơn (LL)
- `TRANSITION` — một trong hai vế đổi, vế kia chưa. Đây là vùng nguy hiểm nhất:
  trông như tiếp diễn ngay trước khi đảo chiều, và trông như đảo chiều ngay
  trước khi tiếp diễn.
- `UNCLEAR` — chưa đủ swing để kết luận. Không tự bịa cấu trúc cho đủ.

Một swing chỉ được tính khi có ít nhất 2 nến hai bên xác nhận. Đỉnh "đang hình
thành" chưa phải đỉnh.

## Hỗ trợ / kháng cự

Vùng trong dữ liệu được gom từ swing lịch sử, kèm `touches` = số lần chạm.

- Nhiều lần chạm = vùng được nhiều người nhìn thấy = phản ứng mạnh hơn, **nhưng
  cũng dễ bị phá hơn** khi có đủ lệnh dừng chất phía sau. Đừng đọc `touches` cao
  là "chắc chắn giữ".
- Vùng đã bị phá thường đổi vai: kháng cự cũ thành hỗ trợ mới.
- **Đừng đặt stop ngay tại vùng.** Đặt phía bên kia vùng, cộng thêm đệm theo
  ATR. Stop đặt đúng con số tròn mà ai cũng thấy là stop được thiết kế để bị quét.

## Quét thanh khoản (liquidity sweep)

Mẫu hình lặp lại nhiều nhất trong crypto: giá đâm thủng một đáy rõ ràng, lấy sạch
stop, rồi lấy lại vùng đó ngay trong 1–2 nến. Dấu hiệu:

1. Thủng một đáy/đỉnh swing dễ thấy
2. Volume tăng vọt lúc thủng
3. **Đóng nến trở lại phía trong** vùng vừa thủng

Vế 3 là vế quyết định. Thiếu nó thì đó là phá vỡ thật, không phải quét. Đừng gọi
tên mẫu hình khi mới có vế 1 và 2 — lúc đó hai kịch bản vẫn còn nguyên xác suất.

## Điều không được làm

Đừng vẽ cấu trúc để hợp với kết luận đã có sẵn trong đầu. Nếu phải bỏ qua một
swing để câu chuyện gọn hơn, thì câu chuyện đó sai, không phải swing đó thừa.
