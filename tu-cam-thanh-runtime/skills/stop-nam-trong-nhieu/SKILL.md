# Kỹ năng: Stop nằm trong biên độ nhiễu

Một điểm vào tốt hơn không cứu được gì nếu stop vẫn nằm giữa đường đi của chính
lệnh thắng. Đây là chỗ bốn chiến lược khác hẳn nhau cùng chết.

## Chuyện đã xảy ra

Chiến lược cầm quyền thoát bằng stop ở **77% số lệnh**, kỳ vọng −0,666R ngoài
mẫu. Chẩn đoán ban đầu — của tôi — là "vào lệnh quá muộn, ở đỉnh chân sóng". Nên
dựng hai bộ luật mới với **điểm vào ngược nhau hoàn toàn**:

- **Chờ kéo lùi**: chỉ vào sau khi giá đã về EMA20, stop đặt sau swing thấp
- **Bung nén**: vào đúng lúc phá biên 20 nến, khi biến động và khối lượng cùng giãn

Cùng đoạn nến, cùng mốc chia 70/30, cùng chuỗi tín hiệu:

```
                  trong mẫu            NGOÀI MẪU         khớp trội  SL%
thuận xu hướng    89 lệnh −0,204R      44 lệnh −0,666R      0,462   77%
mua đáy biên      13 lệnh +0,034R       5 lệnh −1,231R      1,265  100%
chờ kéo lùi       76 lệnh −0,628R      29 lệnh −0,673R      0,045   72%
bung nén          25 lệnh −0,371R       8 lệnh −0,233R     −0,138   62%
```

Bốn điểm vào khác hẳn nhau, bốn kết quả cùng âm. **Khi mọi giả thuyết đều sai
theo cùng một kiểu, giả thuyết sai không phải là chúng — mà là thứ chúng dùng
chung.**

## Đo cái dùng chung

Với mỗi lệnh, đo giá đi xa nhất về phía mình trong 48 nến, rồi đo **giá đã lùi
ngược bao xa TRƯỚC lúc chạm mục tiêu 2,1R**:

```
                  chạm được 2,1R    lùi ngược trước đó    quét qua stop trước
thuận xu hướng     36% số lệnh       trung vị 0,86R            42%
chờ kéo lùi        46% số lệnh       trung vị 1,32R            67%
bung nén           48% số lệnh       trung vị 1,12R            56%
```

Đọc kỹ hai cột đầu của hàng «chờ kéo lùi»: nó có **điểm vào tốt hơn hẳn** —
46% số lệnh rốt cuộc chạm mục tiêu, so với 36% của chiến lược cũ. Nó vẫn thua
nhiều hơn.

Vì stop cấu trúc của nó **hẹp hơn**, nên cùng một biên độ nhiễu giá tính ra
thành 1,32R thay vì 0,86R. Vào đúng hơn nhưng bị quét nhiều hơn, và phần bị quét
ăn hết phần vào đúng.

> **R là tỉ số, không phải khoảng cách.** Thu hẹp mẫu số thì mọi thứ khác trong
> thị trường tự động nở ra — kể cả cái nhiễu đang chờ quét mình.

## Nới stop cũng không xong — và đó mới là câu trả lời

```
stopATR     ngoài mẫu       thắng    SL%    TP chạm
   1,5      −0,666R        20,5%    77%       5
   2,0      −0,689R        20,7%    72%       1
   2,5      −0,644R        21,4%    68%       1
   3,0      −0,480R        31,8%    59%       1
```

Nới stop giảm tỉ lệ bị quét đúng như dự đoán (77% → 59%) và nâng tỉ lệ thắng
(20,5% → 31,8%). Nhưng số lệnh chạm mục tiêu **sụp từ 5 xuống 1**: mục tiêu suy
ra từ RR ≥ 2,0 nên stop rộng gấp đôi đẩy mục tiêu ra xa gấp đôi.

Hệ đang bị kẹp giữa hai đầu:

```
stop phải ≥ ~2,5× hiện tại  để sống qua nhiễu
mục tiêu phải ≤ ~2,1R       để với tới trong 48 nến
RR tối thiểu 2,0            ⇒ hai điều kiện trên loại trừ nhau
```

Trên BTC khung 1h với cửa sổ giữ 48 nến, **RR 2,0 và một cái stop sống được
không cùng tồn tại.** Đó không phải một lỗi để sửa; đó là một sự thật về khung
thời gian này, và nó phải được biết trước khi viết chiến lược thứ năm.

## Cách dùng

Trước khi đổ lỗi cho điểm vào, đo ba con số này:

1. **Bao nhiêu % lệnh CÓ LÚC chạm mục tiêu?** Thấp thì mục tiêu quá xa — đừng
   sửa điểm vào.
2. **Trong số đó, bao nhiêu % bị quét qua stop trước?** Cao thì stop nằm trong
   nhiễu — vẫn đừng sửa điểm vào.
3. **Nới stop thì tỉ lệ chạm mục tiêu đổi thế nào?** Nếu nó sụp, thì RR tối
   thiểu chính là ràng buộc đang giết mình, không phải chiến lược.

Và luôn hỏi: nếu mọi biến thể đều sai theo cùng một kiểu, thì **cái chưa từng
được đem ra thử là cái nào?** Ở đây, sau bốn bộ luật, cái chưa từng đổi là khung
thời gian, cửa sổ giữ lệnh, và ngưỡng RR — chứ không phải điểm vào.

## Một bẫy đã suýt dính

Phép thử «nới stop» chỉ hợp lệ **sau khi** rủi ro mỗi lệnh đã cố định theo tiền
mua được. Trước đó, kích thước bị ghim bởi trần tiền mặt nên nới stop đồng nghĩa
với cược to hơn — và bảng sẽ báo "stop rộng hơn thì lỗ nặng hơn", một kết luận
đúng số nhưng trả lời nhầm câu hỏi. Xem [[kich-thuoc-vi-the]].
