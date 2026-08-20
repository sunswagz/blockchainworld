# Kỹ năng: Mẫu giá — hình học đọc được, và giá trị thật của nó

Mười ba mẫu biểu đồ kinh điển, mỗi mẫu một định nghĩa hình học chính xác — rồi
kết quả khi đem cả mười ba ra đo trên đúng cây nến bot này giao dịch.

Phần định nghĩa để **nhìn ra** mẫu. Phần số đo để biết nhìn ra rồi thì làm gì.

## Phần I — Nhận diện: mẫu là gì, xác nhận ở đâu

Một mẫu chỉ tính khi **đã phá mức xác nhận**. "Gần giống vai-đầu-vai" chưa phá
cổ áo không phải mẫu — nó là một hình thù, và đếm nó là tự chấm điểm cho cái
mình vừa vẽ ra.

### Nhóm ĐẢO CHIỀU

**Hai đỉnh** — hai đỉnh ngang nhau (lệch ≤1,5%), đáy giữa là **cổ áo**.
Xác nhận: đóng cửa **dưới** cổ áo. Stop trên đỉnh cao hơn.
Mục tiêu kinh điển: cổ áo − chiều cao mẫu.

**Hai đáy** — gương của trên. Xác nhận: đóng **trên** cổ áo.

**Vai–đầu–vai** — ba đỉnh, giữa cao nhất, hai vai lệch nhau ≤35% chiều cao đầu.
Cổ áo nối hai đáy. Xác nhận: đóng dưới cổ áo. Vai lệch quá thì đó là **ba đỉnh
bất kỳ**, không phải vai-đầu-vai — đừng gọi chung tên.

**Vai–đầu–vai ngược** — gương.

**Nến trùm** (outside bar) — nến trùm cả biên độ nến trước, thân ≥1,2×ATR, đóng
ở 30% trên (tăng) hoặc 30% dưới (giảm).

### Nhóm HỘI TỤ — phân biệt bằng DẤU của hai độ dốc

```
đỉnh ngang  + đáy lên     → TAM GIÁC TĂNG    phá lên
đỉnh xuống  + đáy ngang   → TAM GIÁC GIẢM    phá xuống
đỉnh xuống  + đáy lên     → TAM GIÁC CÂN     theo hướng phá
đỉnh lên    + đáy lên     → NÊM TĂNG         phá XUỐNG
đỉnh xuống  + đáy xuống   → NÊM GIẢM         phá LÊN
```

**Nêm là chỗ dễ đọc sai nhất.** Giá vẫn đang tạo đỉnh cao hơn mà mẫu lại báo
giảm. Lý do: bề rộng đang co — mỗi nhịp tăng yếu dần so với nhịp trước. Điều
kiện hội tụ ở đây là bề rộng cuối ≤60% bề rộng đầu; thiếu nó thì mọi đoạn xu
hướng đều thành "nêm".

### Nhóm TIẾP DIỄN

**Cờ** — một **cột** ≥3×ATR rồi đoạn nghỉ hẹp ≤1,5×ATR, phá tiếp theo hướng cột.
Không có cột thì đoạn hẹp đó chỉ là thị trường đang chán, không phải cờ.

**Cốc tay cầm** — hai vành ngang nhau, đáy sâu ≥2×ATR và nằm **gần giữa** cốc
(lệch tâm ≤30%), rồi tay cầm nông ≤50% chiều sâu cốc. Cốc mà đáy lệch hẳn về một
bên là chữ **V** — thứ khác hẳn.

**Nến trong** (inside bar) — biên độ nằm gọn trong nến mẹ. Không có hướng riêng;
nó chỉ nói **thị trường đang nén**.

## Phần II — Số đo: mỗi mẫu thật sự đáng bao nhiêu

4000 nến BTC 1h. Vào tại nến xác nhận, stop và mục tiêu do chính mẫu khai, giữ
tối đa 48 nến, trừ 15bps mỗi đầu. Hai lần cùng tên phải cách nhau ≥12 nến (không
gộp trùng thì một hình vai-đầu-vai đứng yên 10 nến sẽ được đếm 10 lần).

```
mẫu                   n   mục tiêu MẪU    RR   thắng  MFE giữa   1.0R    1.5R    2.0R
NẾN_TRÙM_GIẢM        52        +0.021  1.19   61.5%      1.34  +0.095  +0.077  +0.197
NẾN_TRÙM_TĂNG        49        -0.109  1.15   53.1%      0.74  -0.212  -0.191  -0.135
HAI_ĐỈNH            111        -0.171  0.49   49.5%      0.77  -0.247  -0.353  -0.477
HAI_ĐÁY             124        -0.230  0.47   44.4%      0.58  -0.289  -0.468  -0.495
VAI_ĐẦU_VAI_NGƯỢC    21        -0.268  1.25   38.1%      0.88  -0.208  -0.550  -0.588
VAI_ĐẦU_VAI          26        -0.332  1.49   42.3%      0.92  -0.206  -0.365  -0.554
CỐC_TAY_CẦM          19        -0.366  1.92   36.8%      0.65  -0.525  -0.518  -0.557
NẾN_TRONG_TĂNG      153        -0.383  2.36   33.3%      0.47  -0.426  -0.438  -0.487
NẾN_TRONG_GIẢM      160        -0.454  2.38   28.7%      0.30  -0.422  -0.417  -0.403
```

**8/9 mẫu đủ cỡ mẫu có kỳ vọng ÂM sau phí**, ở mọi luật thoát.

### Ba điều bảng này nói mà sách không nói

**1. Thắng nhiều vẫn lỗ — và đây là cách nó xảy ra.**
`HAI_ĐỈNH` **chạm đích 69,4%** số lần. Vẫn lỗ −0,171R. Vì luật đặt mục tiêu kinh
điển của nó cho **RR chỉ 0,49** — đích gần hơn cả stop. Ở RR 0,49 phải thắng
**67%** mới hoà, và phí đẩy ngưỡng đó lên cao hơn nữa.

> Một mẫu có tỉ lệ thắng cao mà không kèm RR là một câu chưa nói hết.

**2. Đích xa hơn không cứu được — nên lỗi không nằm ở luật đặt mục tiêu.**
Cột 1.0R/1.5R/2.0R dùng đúng stop của mẫu nhưng đích cố định. `HAI_ĐỈNH` càng
kéo đích ra càng tệ: −0,247 → −0,353 → −0,477. Nghĩa là sau khi phá cổ áo, giá
**không có xu hướng đi tiếp**. Hình học ấy không đoán được gì trên khung này.

Đối chiếu: `NẾN_TRÙM_GIẢM` càng kéo đích ra càng **tốt** hơn (+0,095 → +0,197).
Đó mới là dấu hiệu của một tín hiệu có hướng thật.

**3. MFE trung vị dưới 1R ở gần như mọi mẫu.**
Một nửa số lần `NẾN_TRONG_GIẢM` xuất hiện, giá **không đi nổi 0,3R** về phía mình
trước khi kết thúc. Không luật thoát nào cứu được một tín hiệu như thế.

### Cái duy nhất sống sót — và vì sao vẫn chưa được tin

`NẾN_TRÙM_GIẢM` dương ở cả bốn luật thoát. Nhưng **12 mẫu × 4 luật = 48 tổ hợp
đo một lượt**; tìm ra một cái dương nhẹ là đúng thứ phép thử bội sinh ra khi
chẳng có gì cả. Nên chia đôi dữ liệu:

```
                     trong mẫu (70%)          ngoài mẫu (30%)
NẾN_TRÙM_GIẢM   n=31  mẫu −0,075  1R +0,011   n=21  mẫu +0,162  1R +0,219
```

Dương ở **cả hai nửa** dưới mục tiêu cố định — hiếm, và đáng ghi lại. Nhưng
+0,011R trong mẫu là gần bằng không, và n=21 ngoài mẫu là sát ngưỡng. **Chưa đủ
để giao dịch.** Mọi mẫu còn lại âm ở cả hai nửa.

## Phần III — Phép đo này KHÔNG chứng minh điều gì

Nó đo mẫu giá làm **tín hiệu vào lệnh đứng một mình**, với stop và đích máy móc.
Nó **không** đo mẫu giá làm bối cảnh — kết hợp với chế độ thị trường, với vùng
giá đã nhiều lần được tôn trọng, với khối lượng, với khung lớn. Người giao dịch
giỏi hiếm khi dùng mẫu theo kiểu đứng một mình, và bảng trên không nói gì về
cách dùng đó.

Kết luận đúng: **mẫu giá ở đây là ngôn ngữ mô tả, không phải nút bấm.** Biết đọc
"đây là nêm tăng đang co" là biết mô tả trạng thái. Từ mô tả tới quyết định còn
một bước nữa, và bước đó phải có số đo riêng.

## Cách dùng

Khi thấy một mẫu, hỏi bốn câu — theo đúng thứ tự:

1. **Đã xác nhận chưa?** Chưa phá mức xác nhận thì chưa có gì để bàn.
2. **RR của nó là bao nhiêu?** Dưới 1 thì tỉ lệ thắng phải trên 67% mới hoà, và
   không mẫu nào ở đây đạt.
3. **Trên thị trường NÀY, khung NÀY, nó đã đo được bao nhiêu?** Bảng ở trên. Nếu
   mẫu không có trong bảng thì nó chưa từng được đo — đừng mượn số của sách.
4. **Có mẫu nào ngược hướng cùng xác nhận không?** Hai mẫu ngược hướng không
   triệt tiêu thành "trung tính" — nó nghĩa là hình học đang mâu thuẫn, và đó là
   lúc đứng ngoài chứ không phải lúc lấy trung bình.

Xem thêm [[stop-nam-trong-nhieu]] — cùng một sự thật nhìn từ phía khác: trên
khung 1h này, phần lớn thứ trông như tín hiệu đều bị nhiễu ăn hết trước khi kịp
thành tiền.
