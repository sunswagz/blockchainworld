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

**135.000 nến khung 4h trên 15 chợ độc lập** (2022-07 → 2026-08). Vào tại nến
xác nhận, stop và mục tiêu do chính mẫu khai, giữ tối đa 48 nến, trừ 15bps mỗi
đầu. Hai lần cùng tên phải cách nhau ≥12 nến — không gộp trùng thì một hình
vai-đầu-vai đứng yên 10 nến sẽ được đếm 10 lần.

```
mẫu                        n  mục tiêu MẪU    RR   thắng    MFE    1.0R    1.5R    2.0R
NÊM_GIẢM                  60        +0.056  1.95   46.7%   0.91  -0.112  -0.217  -0.357
TAM_GIÁC_TĂNG            867        -0.021  1.48   43.7%   0.81  -0.113  -0.143  -0.191
TAM_GIÁC_GIẢM            810        -0.022  1.54   44.6%   0.86  -0.110  -0.209  -0.306
NÊM_TĂNG                  47        -0.034  1.82   40.4%   0.72  -0.245  -0.263  -0.177
VAI_ĐẦU_VAI              698        -0.038  1.16   46.0%   0.84  -0.151  -0.242  -0.330
HAI_ĐỈNH                2029        -0.040  0.53   55.9%   0.88  -0.093  -0.192  -0.311
NẾN_TRÙM_TĂNG           2025        -0.068  1.17   46.2%   0.89  -0.081  -0.091  -0.123
NẾN_TRÙM_GIẢM           2098        -0.069  1.19   45.8%   0.89  -0.081  -0.112  -0.139
NẾN_TRONG_GIẢM          5645        -0.082  2.46   35.6%   0.94  -0.080  -0.098  -0.137
CỐC_TAY_CẦM              237        -0.089  1.76   38.4%   0.73  -0.132  -0.084  +0.016
VAI_ĐẦU_VAI_NGƯỢC        678        -0.118  1.10   43.5%   0.77  -0.140  -0.216  -0.266
HAI_ĐÁY                 1970        -0.144  0.52   49.1%   0.74  -0.169  -0.237  -0.313
TAM_GIÁC_CÂN             707        -0.172  2.89   29.8%   0.83  -0.129  -0.260  -0.371
NẾN_TRONG_TĂNG          5126        -0.184  2.23   32.4%   0.79  -0.159  -0.187  -0.209
```

**13/14 mẫu có kỳ vọng ÂM sau phí**, ở mọi luật thoát. Cái duy nhất dương là
`NÊM_GIẢM` với n=60 — và nó ÂM ở cả ba luật thoát cố định, tức con số dương ấy
phụ thuộc hoàn toàn vào cách đặt đích riêng của mẫu.

### Bảng này vừa LẬT một kết luận của chính nó

Bản trước đo trên **4.000 nến BTC 1h** và kết luận: `NẾN_TRÙM_GIẢM` là "cái duy
nhất sống sót", +0,021R, và **càng kéo đích ra càng tốt** (+0,095 → +0,197).

Trên 40 lần dữ liệu, ở khung bot thật sự chạy, nó là **−0,069R qua 2.098 lần**,
và **càng kéo đích ra càng tệ** (−0,081 → −0,139). Dấu đổi, và hướng của xu
hướng cũng đổi.

Đó không phải lỗi của phép đo cũ — 52 lần xuất hiện là 52 lần. Nó là bài học về
việc **một kết luận rút từ 52 quan sát trên một chợ thì chưa phải kết luận**,
kể cả khi nó đã qua cắt trong/ngoài mẫu.

### Ba điều bảng này nói mà sách không nói

**1. Thắng nhiều vẫn lỗ — và đây là cách nó xảy ra.**
`HAI_ĐỈNH` thắng **55,9%** qua 2.029 lần. Vẫn lỗ −0,040R. Vì luật đặt mục tiêu
kinh điển của nó cho **RR chỉ 0,53** — đích gần hơn cả stop. Ở RR 0,53 phải
thắng **65%** mới hoà, và phí đẩy ngưỡng đó lên cao hơn nữa.

> Một mẫu có tỉ lệ thắng cao mà không kèm RR là một câu chưa nói hết.

**2. Đích xa hơn không cứu được — nên lỗi không nằm ở luật đặt mục tiêu.**
Cột 1.0R/1.5R/2.0R dùng đúng stop của mẫu nhưng đích cố định. Gần như mọi mẫu
càng kéo đích ra càng tệ. Nghĩa là sau khi phá mức xác nhận, giá **không có xu
hướng đi tiếp** — hình học ấy không đoán được gì.

Ngoại lệ duy nhất là `CỐC_TAY_CẦM` (−0,132 → +0,016 ở 2R). Một ngoại lệ trong
14 mẫu × 3 luật thoát = 42 ô là đúng thứ phép thử bội sinh ra khi chẳng có gì.

**3. MFE trung vị dưới 1R ở MỌI mẫu.**
Không mẫu nào có MFE trung vị chạm 1R. Một nửa số lần chúng xuất hiện, giá
không đi nổi 0,95R về phía mình trước khi kết thúc. Không luật thoát nào cứu
được một tín hiệu như thế.
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
