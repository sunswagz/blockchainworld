# Kỹ năng: Học từ trader thật — nghiên cứu, không sao chép

Đài quan sát theo dõi trader công khai trên Hyperliquid và OKX. Mục đích là
**giải phẫu cách họ giao dịch**, không phải đi theo họ. Không có nút "sao chép"
ở đâu trong hệ thống, và đó là chủ ý.

## Vì sao không sao chép

Một người có ROI +38% trong 90 ngày có thể chỉ là người vào đúng một sóng. Sao
chép họ ở chế độ thị trường khác là **mua lại đúng rủi ro đã trả cho họ** —
nhưng không có phần thưởng, vì sóng đó đã đi rồi.

Thêm nữa: họ có thể đang phòng hộ cho một vị thế mình không nhìn thấy, và họ
chịu được mức sụt giảm mà tài khoản này không chịu nổi.

## Cái đã đo được, và cái nó dạy

**Người thua giữ lệnh rất ngắn.** Nhóm đang lỗ giữ trung vị **9,5 giờ**, nhóm
đỉnh giữ **84,5 giờ**. Cùng lúc đó nhóm đang lỗ vào chủ động (taker) nhiều hơn
và bị thanh lý nhiều nhất.

> Vội vàng và trả giá để vào ngay là hai dấu hiệu đi cùng nhau, và chúng đi
> cùng với thua lỗ.

**Phong cách đọc ra được từ hành vi, không từ lời khai.** Ví dụ đã đo:

| trader | phong cách | kiểu cắt lỗ | bằng chứng |
|---|---|---|---|
| `0xbe2bfb44` | `SCALPER` | `TRAILING_STOP` | giữ ngắn, vào chủ động cao |
| `0x15baf1ce` | `TREND` | — | giữ 16,6h, vào chủ động chỉ 6% |

Hai tầng độc lập (phong cách và kiểu cắt lỗ) cùng chỉ về **một chân dung nhất
quán** — đó là dấu hiệu phép đo đang bắt đúng thứ có thật, chứ không phải hai
nhãn rời ghép lại.

## Chỉ học nhóm TOP là học sai

Lấy mẫu phải có cả **nhóm giữa**, **nhóm đang lỗ**, và **ví đã cháy**. Người
thua dạy được thứ người thắng không dạy được: họ chết vì cái gì.

Nếu hồ sơ người thua trông **giống hệt** hồ sơ người thắng ở mọi chỉ số ta đo,
điều đó nghĩa là **ta đang đo sai thứ** — và đó là phát hiện đáng giá hơn một
bảng xếp hạng đẹp.

## Trader ngừng hoạt động thì không dạy được gì

Một trader trong mẫu có 235 vòng nhưng chúng từ **891–984 ngày trước**, và một
coin trong đó đã ngừng niêm yết. Phân tích họ chỉ tốn hạn mức API để nhận về ô
trống. Lọc bằng khối lượng tháng > 0.

## Đồng thuận mạnh KHÔNG phải tín hiệu vào lệnh

Khi 70% người giỏi đã LONG, **phần lớn lực mua đã tiêu rồi**. Cộng thêm funding
cao và open interest cao thì cú quét ngược không phải rủi ro xa — nó là cách
thị trường lấy lại thanh khoản.

Ba cách đếm cùng một đồng thuận thường **không đồng ý với nhau**: theo đầu
người, theo vốn, theo chất lượng. Chỗ chúng lệch nhau chính là thông tin — số
đông nhỏ đang đối đầu với vài người lớn.

> **Luật:** đồng thuận là **bối cảnh**, không phải lệnh. Chỉ số đồng thuận nào
> không bao giờ nói được "đừng theo" thì chỉ là máy khuếch đại đám đông đội lốt
> phân tích.

## Mọi thứ rút ra ở đây vẫn phải qua cửa duyệt

Mẫu hành vi tìm được từ trader thật là **tương quan trong quá khứ**, chưa phải
nguyên nhân. Nó đi vào hệ thống với tư cách challenger và phải thắng bản đang
chạy trên dữ liệu ngoài mẫu — y như mọi ý tưởng khác.
