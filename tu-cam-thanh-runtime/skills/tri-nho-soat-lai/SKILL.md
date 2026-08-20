# Kỹ năng: Trí nhớ phải soát lại được

Bài học viết **ngay lúc sự việc xảy ra** và bài học viết **khi đã có cả cuốn sổ**
không phải một thứ. Cái đầu là thứ duy nhất viết được lúc đó; cái sau mới là thứ
đáng đưa vào đầu.

## Chuyện đã xảy ra

Bộ máy này chạy 14.751 vòng, đóng 8 lệnh, đúc ra 8 bài học. Đếm lại:

```
8 bài học  →  2 CÂU KHÁC NHAU
              0 lần đòi đổi chiến lược
              8/8 đều là "quyết định tốt"
```

Trí nhớ ngữ nghĩa khi đó không phải trí nhớ. Nó là một cái máy dán nhãn — và một
cái máy dán nhãn luôn báo "ổn" thì im lặng y hệt như không có gì.

Chạy hậu kiểm lại trên đúng 8 lệnh đó, lần này cho nó nhìn CẢ SỔ:

```
2 câu → 5 câu khác nhau
0     → 3 bài đòi đổi chiến lược
3 lệnh đổi nhãn: 2× BAD_TRADE_BAD_OUTCOME, 1× BAD_TRADE_GOOD_OUTCOME
```

Cùng dữ liệu, cùng luật. Chỉ khác **lúc nào thì hỏi**.

## Vì sao lúc đó không thể trả lời

Mọi câu hỏi có chữ "hơn bình thường" đều là câu hỏi so sánh, và so sánh cần một
tập nền:

> "Lệnh này cược lớn hơn mức thường bao nhiêu?"

Ở lệnh thứ nhất, "mức thường" chưa tồn tại. Ở lệnh thứ tám, nó tồn tại rồi —
nhưng bài học của lệnh thứ nhất đã đóng băng từ lâu.

Đó là lý do **hai lệnh cược gấp 1,8× và 1,9×** vẫn được dán nhãn quyết định tốt.
Không phải luật sai. Luật chưa có gì để đo.

Nhận ra dạng này: hỏi *lúc nào* thì tri thức cần cho phán quyết mới đủ. Nếu câu
trả lời là "muộn hơn lúc phán quyết", thì phán quyết đó phải soát lại được.

## Bốn cái bẫy khi làm lớp soát lại

**1. Đừng ghi đè bản gốc.**
`lessons.jsonl` là bản ghi bộ não ĐÃ nghĩ gì lúc đó — chính là bằng chứng cho chỗ
hỏng này. Xoá nó đi là xoá thứ chứng minh mình từng sai. Lớp soát lại nằm ở file
riêng, phần đọc ưu tiên nó; xoá file đi là quay về nguyên trạng.

**2. Đừng để nó thành bài học MỚI.**
Giữ nguyên mốc thời gian gốc. Đổi sang hôm nay là 8 bài học biến thành 16, kho
trí nhớ trông như dày lên gấp đôi trong khi không có một quan sát nào mới. Cùng
họ với "phủ 100%" đo sai đơn vị.

**3. Bảng và bộ não phải đọc CÙNG một bản.**
Lỡ tay để bảng đọc bản gốc còn bộ não đọc bản soát lại, thì hai bên nói hai
chuyện khác nhau về cùng một lệnh, và người xem không có cách nào biết bên nào
đang nói thật.

**4. Ngưỡng phải đo trên tập cố định.**
Luật "có lặp lại không" ở đây suýt chết vì đếm số lệnh lệch bằng *trung bình các
lệnh khác* — mẫu số đổi theo từng lệnh đang xét, nên cùng một cuốn sổ ra 2 chỗ
lệch thay vì 3, và luật không bao giờ nổ. Đếm bằng trung bình CẢ SỔ thì ra đúng
3/8 và luật nổ.

Bẫy 4 nguy nhất, vì nó không báo lỗi. Nó chỉ im lặng không bao giờ kích hoạt —
và "chưa từng thấy vấn đề" đọc giống hệt "không có vấn đề".

## Đổi chiến lược phải mua bằng một CHUỖI

Bài học đòi đổi chiến lược luôn được kéo vào prompt, kể cả khi lạc chế độ. Nên nó
phải đắt, nếu không mỗi lệnh thua lại đòi đổi một lần và kho trí nhớ thành tiếng ồn.

Ba nguyên nhân đủ tư cách — điểm chung: chúng là **tật của quy trình**, chỉ nhìn
thấy khi đếm trên cả sổ, không nhìn thấy trên một lệnh:

- kích thước lệch quá 1,6× ở **≥3 lệnh** → thước đo kích thước hỏng, sửa ở đó,
  đừng sửa tín hiệu vào lệnh
- **≥3 lệnh** dính stop trong ≤2 nến → stop nằm trong vùng nhiễu, nới stop và
  giảm khối lượng, đừng đổi tín hiệu
- một chế độ đã lỗ qua **≥5 lệnh** với ≥60% thua → ngừng vào lệnh ở chế độ đó,
  đừng chỉnh tham số

Và luôn kiểm **cửa ngược lại**: một cuốn sổ cược đều mà vẫn có lệnh thua thì phải
đòi đổi chiến lược **0 lần**. Thiếu phép kiểm đó, luật sẽ nới dần ra cho tới khi
mọi thứ đều "cần đổi chiến lược".

## Cách dùng

Khi đọc một bài học, hỏi ba câu:

1. **Bài này có cờ đã-soát-lại không?** Nếu không, mọi nhận xét so sánh trong đó
   được viết bởi một người chưa nhìn thấy phần còn lại của sổ.
2. **Kết luận này cần bao nhiêu lệnh mới đứng vững?** Một lệnh thua nói lên rất
   ít. Ba lệnh cùng một tật nói lên rất nhiều.
3. **Nếu nó nói "đổi chiến lược" — cớ lặp lại nằm ở đâu?** Không chỉ ra được thì
   đó là phản ứng với một kết quả, không phải một bài học.
