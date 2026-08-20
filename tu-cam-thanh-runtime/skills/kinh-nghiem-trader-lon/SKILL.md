# Kỹ năng: Kinh nghiệm trader lớn — đối chiếu với số đo tại chỗ

Những câu nổi tiếng nhất trong nghề, mỗi câu kèm **thứ hệ thống này đã đo được
về chính nó**. Câu nào số đo xác nhận thì mạnh hơn hẳn một lời khuyên. Câu nào
số đo bẻ lại thì còn quý hơn.

Cột trái là **kinh nghiệm truyền lại** — không phải số đo, và phải đọc như vậy.
Cột phải là số đo tại chỗ, có cỡ mẫu.

---

## 1. "Cắt lỗ sớm, để lãi chạy" — Livermore, và gần như mọi người sau ông

**Đo được ở đây:** 77% lệnh chết ở stop, MFE trung vị 1,45R. Và khi tôi dựng một
chiến lược có stop HẸP HƠN (đặt sau cấu trúc thay vì 1,5×ATR), nó **tệ hơn** —
điểm vào tốt hơn (46% lệnh rốt cuộc chạm mục tiêu so với 36%) mà vẫn thua nhiều
hơn, vì cùng biên độ nhiễu tính trên stop hẹp thành 1,32R thay vì 0,86R.

**Chỗ câu này bị đọc sai:** "cắt lỗ sớm" không có nghĩa **stop hẹp**. Nó có
nghĩa **thoát ngay khi luận điểm hỏng**. Hai thứ khác nhau: điểm luận điểm hỏng
do CẤU TRÚC thị trường đặt, không do mình muốn mất ít. Đặt stop theo mức mình
chịu được là để thị trường quyết định hộ mình lúc nào sai.

---

## 2. "Không phải đúng hay sai, mà là kiếm bao nhiêu khi đúng, mất bao nhiêu khi sai" — Soros

**Đo được ở đây:** 8 lệnh thật, thắng 37,5%, tổng tiền **−$95,69**. Ba lệnh
thắng cược 37·45·58; hai lệnh thua cược 104·112. Kỳ vọng tính bằng R ra
**+0,282R** — dương — trong khi tài khoản đang lỗ.

Đây là câu của Soros hiện ra dưới dạng một con số. Đúng 37,5% số lần mà vẫn lỗ,
không phải vì tỉ lệ thắng thấp, mà vì **cược nhỏ lúc đúng và cược to lúc sai**.

---

## 3. "Kích thước vị thế quan trọng hơn điểm vào" — Kovner, Tharp, Vince

**Đo được ở đây:** đây là câu được xác nhận mạnh nhất trong cả hệ thống, và nó
được xác nhận theo cách khó chịu nhất — bằng một con lỗi.

Rủi ro mỗi lệnh tính trên vốn **79.772** trong khi chỉ **6.346** là tiền mua
được. Mục tiêu rủi ro 399 lớn hơn mọi thứ 6.346 đỡ nổi, nên trần tiền mặt chạm ở
MỌI lệnh, và khi nó chạm thì khối lượng bị ghim còn rủi ro trôi theo độ rộng
stop: **42 · 79 · 158** cho cùng một tín hiệu ở ba độ rộng stop khác nhau.

Điểm vào không đổi một chút nào. Kết quả đổi 3,75 lần.

---

## 4. "Chỉ vào lệnh có tỉ lệ 5:1" — Paul Tudor Jones

**Đo được ở đây:** trên BTC 1h, cửa sổ giữ 48 nến, **RR 2,0 đã là không với
tới**. Nới stop để sống qua nhiễu thì mục tiêu 2R bị đẩy ra xa gấp đôi và số lệnh
chạm đích sụp từ 5 xuống 1.

**Chỗ câu này bị đọc sai:** 5:1 là luật **CHỌN**, không phải luật **ĐẶT**. Jones
không đặt mục tiêu ở 5R rồi chờ; ông bỏ qua mọi thứ không tự nó cho 5:1. Ép mục
tiêu ra 5R trên một thị trường không đi xa đến thế thì chỉ tạo ra một chuỗi lệnh
hết hạn.

---

## 5. "Quyết định tốt ≠ kết quả tốt" — Mark Douglas

**Đo được ở đây:** trong 8 lệnh thật, hậu kiểm bắt được **1 lệnh
BAD_TRADE_GOOD_OUTCOME** — thắng nhưng cược lệch 0,5× mức thường.

Đây là loại nguy hiểm nhất, vì phần thưởng đến ngay và nó dạy đúng thứ không
được lặp lại. Một hệ thống chỉ học theo lãi/lỗ sẽ củng cố chính cái lệnh đó.

---

## 6. "Sống sót trước, lợi nhuận sau" — mẫu số chung của mọi Market Wizard

**Đo được ở đây:** **chuỗi thua dài nhất 8 lệnh liên tiếp** trong 44 lệnh chạy
lại. Đó mới là con số quyết định mức rủi ro mỗi lệnh — không phải kỳ vọng.

Ở 0,5%/lệnh, chuỗi 8 lệnh mất 4% vốn: sống được. Ở 5%/lệnh, mất 34%: cần lãi 51%
để về bờ. Cùng một chiến lược, cùng một chuỗi thua — khác nhau ở một con số
không liên quan gì tới chất lượng tín hiệu.

---

## 7. "Đi theo xu hướng" — Dennis, Seykota, Turtles

**Đo được ở đây:** chiến lược thuận xu hướng của hệ này có kỳ vọng **−0,666R
qua 44 lệnh** ngoài mẫu, và chế độ TREND_UP|none lỗ đều **−0,422R qua 36 lệnh**.

**Chỗ khác biệt quan trọng:** Turtles giao dịch **khung ngày trở lên**, trên
**rổ nhiều thị trường**, với **cửa sổ giữ hàng tháng**. Bot này chạy 1h, một
coin, giữ tối đa 48 nến. Cùng tên gọi "thuận xu hướng" nhưng khác nhau về mọi
chiều. Mượn kết quả của họ để tin vào hệ này là mượn nhầm.

---

## 8. "Đám đông thường sai ở điểm cực" — kinh nghiệm nghịch chiều

**Đo được ở đây:** trên 111 vị thế BTC của nhóm trader đang quan sát,
**96,4% ĐẦU NGƯỜI đang long nhưng chỉ 37,3% VỐN đang long.**

Đám đông và tiền lớn đứng hai phía. Nhưng đây là **bối cảnh**, không phải lệnh:
nó nói chỗ đông người ở đâu, không nói ai đúng. Số đo này chưa từng được kiểm
xem nó có dự báo được gì không — chưa đo thì chưa được dùng để bấm nút.

---

## 9. "Mẫu giá hoạt động" — sách kỹ thuật, gần như toàn bộ

**Đo được ở đây:** 9 mẫu kinh điển đủ cỡ mẫu trên 4000 nến 1h, dùng đúng điểm
vào/stop/mục tiêu mà chính mẫu khai: **8/9 kỳ vọng âm sau phí**. Kéo mục tiêu ra
xa hơn cũng không cứu. Chi tiết ở [[mau-gia]].

Đây là chỗ số đo **bẻ lại** kinh nghiệm truyền lại rõ nhất — và cũng là chỗ phải
cẩn thận nhất khi kết luận: phép đo ấy đo mẫu giá làm **tín hiệu đứng một mình**,
không đo mẫu giá làm bối cảnh kết hợp với chế độ, vùng giá và khối lượng. Người
giỏi hiếm khi dùng mẫu theo kiểu đứng một mình.

---

## 10. "Giữ nhật ký giao dịch" — không ai phản đối, gần như không ai làm đủ

**Đo được ở đây:** hệ này có nhật ký từ đầu, và trong 14.751 vòng nó đúc ra 8
bài học — **chỉ 2 câu khác nhau**, 0 lần đòi đổi chiến lược. Một cuốn nhật ký
luôn kết luận "ổn" thì im lặng y hệt như không có nhật ký.

Nhật ký chỉ có giá trị khi nó **so được lệnh này với cả sổ**. "Lệnh này cược lớn
hơn mức thường bao nhiêu" là câu hỏi không trả lời được ở lệnh thứ nhất, và phải
soát lại về sau. Xem [[tri-nho-soat-lai]].

---

## Bốn thứ mọi người trong danh sách này đều làm, và đo được ở đây

**1. Họ biết mình sai ở đâu TRƯỚC khi vào.**
Không có điểm vô hiệu hoá thì không có lệnh. Risk Engine ở đây chặn thẳng
`THIẾU_SL` — không phải vì thận trọng, mà vì không có nó thì không tính được
kích thước, và không tính được kích thước thì mọi con số R về sau vô nghĩa.

**2. Họ cược đều.**
Hệ số biến thiên rủi ro của 8 lệnh đầu ở đây là **0,406** — quá cao để R có
nghĩa. Cược đều không phải kỷ luật đạo đức; nó là điều kiện để phép đo hoạt động.

**3. Họ tách phép đo khỏi hy vọng.**
Backtest ngoài mẫu, cửa duyệt là hàm thuần, phát hiện mang theo cỡ mẫu. Hệ này
có cả ba, và cả ba đều sinh ra từ một lần bị chính con số của mình lừa.

**4. Họ đứng ngoài phần lớn thời gian.**
NO_TRADE là một quyết định. Ở đây nó là câu trả lời đúng trong hầu hết các vòng,
và cầu dao chế độ còn chủ động chặn thêm chế độ đã đo là lỗ đều.

## Cách dùng

Gặp một câu khuyên trong nghề, hỏi ba câu:

1. **Nó nói về thị trường nào, khung nào, cỡ mẫu bao nhiêu?** Turtles trên khung
   ngày và bot này trên 1h không cùng một bài toán.
2. **Hệ này đã đo được gì về chính nó chưa?** Có thì đọc số. Chưa thì nó là giả
   thuyết, và giả thuyết thì đem đi đo chứ không đem đi tin.
3. **Nếu tin nó thì làm gì KHÁC đi?** Không trả lời được thì đó là một câu hay,
   không phải một luật.
