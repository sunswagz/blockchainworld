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

## Lỗi nằm ở MẪU SỐ, không nằm ở công thức

Công thức `rủi ro = vốn × %` không sai. Cái sai là chọn "vốn" nào.

Lấy 0,5% của **79.772** ra mục tiêu rủi ro **399** — lớn hơn mọi thứ **6.346**
tiền mặt có thể đỡ. Trần tiền mặt vì thế chạm ở *mọi* lệnh, và khi nó chạm thì
`qty` bị ghim còn `rủi ro = qty × stopDist` trôi theo độ rộng stop. Mục tiêu rủi
ro không điều khiển gì cả; **độ rộng stop điều khiển tất cả.**

Đo trên cùng một tín hiệu, ba độ rộng stop, tài khoản 79.772 vốn / 6.346 tiền mặt:

```
                     rủi ro     khối lượng
mẫu số = vốn giấy    42 · 79 · 158   0,09103 · 0,09103 · 0,09103   ← ngược đời
mẫu số = tiền mặt    32 · 32 ·  32   0,06868 · 0,03664 · 0,01833   ← đúng
```

Hàng trên là hình dạng của một cái thước hỏng: **khối lượng đứng im, rủi ro trôi
3,75 lần.** Hàng dưới là điều đáng lẽ phải xảy ra — rủi ro là thứ mình CHỌN,
khối lượng là thứ suy ra.

Đổi một mẫu số, `riskCv` từ 0,406 về 0, và R so sánh được trở lại. Trần tiền mặt
lui về đúng vai lưới an toàn: ở mức 0,5% nó chỉ chạm khi stop hẹp dưới 0,5% giá,
mà sàn stop tối thiểu 0,3×ATR đã chặn trước rồi.

Bài học chung: khi một con số trôi mà công thức trông đúng, **soát mẫu số trước
khi soát công thức.**

## Ba luật rút ra

**1. Rủi ro là thứ CHỌN, khối lượng là thứ SUY RA — không được đổi vai.**
Nếu cùng một mức rủi ro mục tiêu mà hai lệnh ra hai con số rủi ro khác nhau, thì
có một cái trần nào đó đang thay mình quyết định, và mục tiêu rủi ro chỉ còn là
trang trí. Kiểm bằng một phép thử ba dòng: cùng tín hiệu, ba độ rộng stop khác
nhau — rủi ro phải bằng nhau, khối lượng phải khác nhau.

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
