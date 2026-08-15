# Kỹ năng: Nhận diện chế độ thị trường (Market Regime)

Câu hỏi đầu tiên luôn là **"thị trường đang là gì?"**, không phải "mua hay bán?".
Không có chiến lược nào tốt cho mọi thị trường; chọn sai chế độ thì mọi thứ phía
sau đều sai theo, kể cả khi từng chỉ báo đều đọc đúng.

## Các chế độ

| Chế độ | Dấu hiệu | Kiểu chiến lược hợp |
|---|---|---|
| `TREND_UP` | ADX ≥ 22, EMA20>50>200, HH+HL | pullback thuận xu hướng |
| `TREND_DOWN` | ADX ≥ 22, EMA20<50<200, LH+LL | pullback thuận xu hướng |
| `RANGE` | ADX < 18, giá quanh giữa dải Bollinger | hồi quy về trung bình ở biên |
| `BREAKOUT` | vượt biên 20 nến **kèm** volume > 1.4× | đi theo phá vỡ, SL dưới biên cũ |
| `HIGH_VOLATILITY` | ATR > 1.5× trung vị 100 nến | giảm size, nới SL, hoặc đứng ngoài |
| `LOW_VOLATILITY` | ATR < 0.65× trung vị, dải co | chuẩn bị cho giãn nở, chưa vào |
| `UNKNOWN` | tín hiệu mâu thuẫn | NO_TRADE |

## Quy tắc

**Breakout không có volume thì không phải breakout.** Đó gần như luôn là quét
thanh khoản: giá vượt biên để lấy stop rồi quay lại. Vế volume không phải trang
trí, nó là thứ phân biệt hai tình huống trông y hệt nhau trên biểu đồ giá.

**Khung lớn mâu thuẫn khung nhỏ là lý do chính đáng để đứng ngoài.** Cờ
`MTF_CONFLICT` xuất hiện khi 4H và 1H xếp EMA ngược nhau. Vào lệnh lúc đó là
đánh cược rằng khung nhỏ thắng khung lớn — thỉnh thoảng đúng, nhưng phải trả giá
bằng RR yêu cầu cao hơn hẳn, không phải bằng sự tự tin.

**Chuyển chế độ nguy hiểm hơn bản thân chế độ.** `RANGE → BREAKOUT` và
`TREND → RANGE` là hai chỗ mọi chiến lược đều lỗ nhiều nhất. Ở vài nến đầu sau
khi regime đổi, hạ tự tin xuống chứ đừng tăng.

**Biến động phải TƯƠNG ĐỐI.** ATR 500 USD không nói lên gì; ATR gấp 2 lần trung
vị 100 nến gần nhất mới là thông tin. Biến động cao không có nghĩa là không giao
dịch — nó có nghĩa là stop phải rộng hơn, và vì stop rộng hơn nên size phải nhỏ
đi đúng theo tỉ lệ đó.

Bộ phân loại đưa vào prompt chạy bằng luật cứng. Nó cố ý thô. Bạn được phép nói
nó đọc sai — hãy ghi rõ trong `regime_read` và giải thích trong `reasoning`.
