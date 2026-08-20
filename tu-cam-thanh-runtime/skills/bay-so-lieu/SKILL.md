# Kỹ năng: Những con số tự nói dối

Mọi con số dưới đây đều **đo được trong chính hệ thống này**, không phải ví dụ
sách vở. Mỗi cái từng hiện lên bảng điều khiển và trông hoàn toàn hợp lý.

Điểm chung của chúng: không cái nào làm chương trình đổ. Chúng chỉ lặng lẽ nói
sai, nằm cạnh những con số đúng, và không cho ai lý do để nghi ngờ.

## 1. Kỳ vọng R dương mà tiền âm

```
kỳ vọng   +0,282R          tổng tiền   −$95,69      8 lệnh
rủi ro mỗi lệnh:  37 · 45 · 45 · 53 · 58 · 63 · 104 · 112
                  └── ba lệnh THẮNG ──┘   └─ lệnh THUA ─┘
```

**R chỉ so sánh được khi rủi ro mỗi lệnh gần như nhau.** Ở đây hai lệnh thua
cuối đặt cược gấp 2,5 lần lệnh thắng đầu, nên R chuẩn hoá đi mất đúng cái làm
nên khoản lỗ.

Nguyên nhân gốc: kích thước bị chặn bởi **tiền mua được**, không phải bởi rủi ro
mục tiêu — nên rủi ro thực tế trôi theo khoảng cách stop. Stop rộng ⇒ cùng số
lượng ⇒ rủi ro lớn hơn.

> **Luật:** đọc kỳ vọng R và tổng tiền **cùng lúc**. Hai cái lệch dấu nghĩa là
> rủi ro mỗi lệnh không đều, và khi đó **con số tiền mới đúng**.

## 2. Tỉ lệ thắng cao mà kiếm ít nhất

Đo trên trader thật ở Hyperliquid, ba nhóm lấy mẫu có chủ ý:

| nhóm | thắng | ROI | giữ lệnh |
|---|---|---|---|
| đỉnh | 52,3% | **+1963%** | 84,5h |
| giữa | **85,7%** | +22% | 82,6h |
| đang lỗ | 18,2% | −100% | 9,5h |

Nhóm **thắng nhiều nhất kiếm ít nhất** — họ cắt lãi non. Chốt lãi sớm đẩy tỉ lệ
thắng lên rất nhanh và ăn mòn kỳ vọng cũng nhanh không kém.

> **Luật:** tỉ lệ thắng không bao giờ là mục tiêu. Nó chỉ có nghĩa khi đọc kèm
> R trung bình thắng / R trung bình thua.

## 3. Bộ tham số đẹp nhất là bộ khớp nhiễu giỏi nhất

```
dò 72 tổ hợp → bộ tốt nhất TRONG mẫu  +0,085R
               chính bộ đó NGOÀI mẫu  −0,645R
               khớp trội               0,730R
```

Dò càng nhiều tổ hợp thì con số đứng đầu càng cao — **kể cả khi chiến lược hoàn
toàn vô dụng**, vì đó là cực trị của nhiễu. Bảng xếp hạng trong mẫu luôn đẹp.

> **Luật:** chỉ con số ngoài mẫu mới đáng tin. "Khớp trội" là khoảng cách giữa
> cái mình tưởng và cái có thật.

## 4. PnL cao ≠ giỏi, và ROI cao cũng vậy

Dòng đầu leaderboard Hyperliquid hôm đo: tài khoản **$61,9 triệu**, tuần lãi
**$1,99 triệu** — mà allTime **lỗ $397 nghìn**.

Rồi khi xếp theo ROI thay vì PnL, nhóm đỉnh ra ROI trung bình **4.170.644%**.
Không ai giao dịch được như vậy: đó là tài khoản khởi điểm gần $0 rồi nạp tiền,
mẫu số bé nên ROI vô nghĩa.

> **Luật:** xếp hạng theo PnL là xếp theo vốn lớn cộng may. Xếp theo ROI là xếp
> theo ai bắt đầu với ít vốn nhất. Cả hai đều không đo kỹ năng.

## 5. Số đúng về định nghĩa mà sai về nghĩa

Có lúc bảng hiện `độ phủ = 100%` trong khi số vòng tra được chế độ là **0**. Lý
do: đo "phủ **coin**" rồi đặt tên là "phủ **chế độ**". Không sai một phép tính
nào, và nó che mất hai lỗi thật nằm dưới.

> **Luật:** tên của một chỉ số phải là thứ nó đo. Khi hai chỉ số liên quan lệch
> nhau bất thường, cái đang nói dối thường là cái có tên đẹp hơn.

## 6. Ô trống vì lỗi, không phải vì không có dữ liệu

Một mẻ hồ sơ trader ghi `soVong: 0` cho 9/11 người. Chạy tươi thì ra 7 và 15
vòng. Sự thật: lỗi `429 Too Many Requests` bị khối `except` nuốt và biến thành
số 0. Suýt nữa thì đi sửa một hàm đang chạy đúng.

> **Luật:** một ô trống phải nói rõ nó trống vì **chưa có dữ liệu** hay vì
> **đã hỏng**. Ghi cả thông điệp lỗi, không chỉ tên lớp lỗi.
