# Kỹ năng: Kích thước vị thế — chỗ lãi lỗ thật sự được quyết định

Bộ luật quyết định *vào hay không*. Kích thước quyết định *thắng thua bao nhiêu*.
Trong tám lệnh thật đầu tiên của hệ thống này, chính kích thước — chứ không phải
tín hiệu — biến một kỳ vọng dương thành một khoản lỗ.

## Chuyện đã xảy ra

```
rủi ro mỗi lệnh:  37 · 45 · 45 · 53 · 58 · 63 · 104 · 112
kết quả:          W    L    L    W    W    L     L     L

kỳ vọng  +0,282R        tổng tiền  −$95,69
```

Rủi ro chênh nhau **gấp ba** giữa lệnh nhỏ nhất và lớn nhất. Ba lệnh thắng rơi
vào nhóm đặt cược nhỏ, các lệnh thua rơi vào nhóm đặt cược lớn. R chuẩn hoá theo
rủi ro nên nó không nhìn thấy điều đó.

## Vì sao rủi ro trôi

Kích thước bị chặn bởi **tiền mua được**, không phải bởi rủi ro mục tiêu:

```
qty      = min(riskAmount / stopDist,  maxNotional / entry)
maxNotional ≤ availableQuote × 0,995
```

Khi trần tiền mặt bám vào, `qty` bị ghim và **rủi ro thực tế = qty × stopDist**
trôi theo khoảng cách stop. Stop rộng ⇒ cùng số lượng ⇒ mất nhiều hơn.

Tài khoản này có vốn $73.000 nhưng chỉ **$10.000 tiền mua được** (phần còn lại
là BTC đang giữ). Nên trần tiền mặt bám gần như mọi lệnh.

## Ba luật rút ra

**1. Khi bị ghim bởi trần tiền mặt, phải tính LẠI rủi ro và kiểm lại.**
Nếu rủi ro thực tế lệch quá xa mức mục tiêu, lệnh đó không còn là lệnh mình
định vào nữa.

**2. Rủi ro không đều thì R mất ý nghĩa so sánh.**
Đọc R và tiền cùng lúc. Lệch dấu nghĩa là rủi ro trôi, và khi đó **tiền mới đúng**.

**3. "Vốn" và "tiền mua được" là hai con số khác nhau.**
Tính kích thước trên vốn tổng khi đang giữ coin thì sàn sẽ từ chối lệnh vì thiếu
số dư — sau khi đã tốn một lượt gọi model. Sàn giấy không bao giờ chỉ ra chuyện
này vì nó chỉ giữ một con số.

## Chuỗi thua quyết định mức risk, không phải kỳ vọng

Phòng huấn luyện đo được **thua liền 12 lệnh** và sụt sâu nhất **10,1%** trên
cùng bộ luật. Con số đó — chứ không phải kỳ vọng — mới trả lời được câu "mức
risk này có ngồi yên nổi không".

Kỳ vọng nói cho biết đi đường dài có lời không. Chuỗi thua nói cho biết **có
sống tới đường dài không**.

## Chi phí không được phép cứu một lệnh sai hình học

Có lần Risk Engine duyệt một lệnh LONG với cắt lỗ nằm **trên** giá vào: hôm đó
ATR chỉ 0,094% giá còn phí+trượt là 0,15%, nên giá khớp vượt qua cả SL và phép
so "SL có dưới giá vào không" ra sai.

Hậu quả không dừng ở chỗ lọt: khoảng stop teo còn 5,66 nên RR tính ra **14,72**
và kích thước phình lên theo đúng tỉ lệ nghịch ấy.

> **Luật:** hình học của lệnh (SL/TP nằm phía nào) phải so với **giá tham
> chiếu**. Kế toán (mất bao nhiêu tiền, RR bao nhiêu) mới so với **giá khớp**.
> Trộn hai câu hỏi này lại là mở đường cho một lệnh vô nghĩa thành một lệnh rất to.
