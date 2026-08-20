# Kỹ năng: Đo được phải đổi được hành vi

Một hệ thống đo rất giỏi mà không đổi hành vi thì không phải hệ thống học. Nó là
một cái đồng hồ đắt tiền.

## Chuyện đã xảy ra

14.751 vòng. Ba cỗ máy đo chạy tốt và đo ra những điều rất đáng biết:

```
phòng huấn luyện   TREND_UP|none lỗ đều −0,422R qua 36 lệnh chạy lại
                   chiến lược cầm quyền kỳ vọng −0,666R qua 44 lệnh
                   34/44 lệnh thoát bằng stop, chỉ 5 lệnh chạm mục tiêu
đài quan sát       96,4% ĐẦU NGƯỜI long nhưng chỉ 37,3% VỐN long
sổ thật            rủi ro không đều, kỳ vọng lệch dấu với tiền
```

Không con số nào trong đó tới được chỗ ra quyết định. Chúng nằm trong
`trader-ho-so.json`, trong `lessons-chay-lai.jsonl`, trên bảng — rồi ở đó. Mỗi
lượt bộ máy lại bắt đầu từ số không, trong khi cách đó hai thư mục là câu trả lời.

Đo mà không nhớ được thì không phải học. Đó là quan trắc.

## Ống dẫn có bốn khúc, thiếu khúc nào cũng đứt

```
ĐO  →  CHƯNG THÀNH CÂU  →  ĐƯA VÀO CHỖ QUYẾT ĐỊNH  →  ĐỔI HÀNH VI
```

Hệ này trước đó có khúc 1, và tưởng là đã đủ. Khúc 2 và 3 dựng xong thì bộ não
mới ĐỌC được; chỉ tới khúc 4 nó mới thật sự đổi việc mình làm.

Kiểm nhanh một hệ bất kỳ: chỉ vào một con số nó vừa đo được, rồi hỏi **"nếu con
số này đổi dấu thì hệ làm gì khác đi?"** Không trả lời được thì khúc 4 chưa có.

## Năm luật của khúc chưng cất

**1. Cỡ mẫu nằm TRONG câu.**
"Chế độ này lỗ" là tin đồn. "Chế độ này lỗ đều −0,422R qua 36 lệnh chạy lại" là
một phát hiện. Để cỡ mẫu ở một trường bên cạnh thì nó sẽ bị bỏ qua khi đọc.

**2. Từ chối phải đếm được.**
Cửa lọc bỏ đi thứ thiếu mẫu — nhưng bỏ im lặng thì "không có phát hiện nào" trông
giống hệt "chưa đo lần nào". Trả về danh sách đã bỏ kèm lý do từng cái.

**3. Chưng lại là ghi đè sạch, không cộng dồn.**
Phát hiện là ảnh chụp số liệu lúc này, không phải sự kiện đã xảy ra. Cộng dồn thì
câu cũ về một chế độ nay đã khác nằm cạnh câu mới, và cả hai cùng trông có căn cứ.

**4. Cắt bớt thì cắt theo BẰNG CHỨNG.**
Prompt có hạn nên phải cắt. Bản đầu ở đây cắt theo thứ tự các nguồn chạy xong,
nên "thời gian giữ đo trên 2 hồ sơ" lọt vào còn "chuỗi thua 8 lệnh liên tiếp qua
44 lệnh" bị cắt. Xếp theo độ tin rồi tới cỡ mẫu trước khi cắt.

**5. Câu phải tự khai nguồn, vì mỗi nguồn đúng về một thứ khác nhau.**
Lệnh chạy lại đúng về **cấu trúc** (chế độ nào hợp) và đẹp quá mức về **độ lớn**
(không nhảy giá qua stop). Lệnh thật ít nhưng đúng về độ lớn. Trader ngoài là
**bối cảnh**, không phải lệnh. Trộn chung là mất khả năng cân.

## Cửa lọc chặn nhầm thứ đáng giá nhất

Cửa chưng cất ở đây từng gác trên trường `tham` (bộ tham số) của chiến lược cầm
quyền. Chiến lược hiện tại là chiến lược luật, `tham` rỗng — nên cửa vứt đi phát
hiện quan trọng nhất trong cả hệ:

> chiến lược đang chạy có kỳ vọng **−0,666R** qua 44 lệnh chạy lại

Không báo lỗi. Không dòng log nào. Chỉ là một câu không bao giờ xuất hiện.

Bài học: **gác cửa trên thứ mình thật sự cần, không gác trên thứ thường đi kèm
nó.** Và mỗi khi viết một cửa lọc, thử ngay một lượt với dữ liệu thật rồi đếm cái
đi qua — cửa chặn nhầm thứ đáng giá nhất còn tệ hơn không có cửa.

## Khúc 4: đổi hành vi — hai cái bẫy chết người

**Bẫy nhìn trước.** Phát hiện đúc TỪ chạy lại mà quay lại chặn chính vòng chạy
lại thì lần chạy sau ra kết quả đẹp hơn trong khi không có gì thật sự tốt lên.
Cầu dao ở đây vì thế chỉ mắc vào đường CHẠY THẬT; vòng chạy lại đi đường khác
và không bao giờ chạm tới nó. Kiểm bằng cách đọc đường nhập: nếu mã chạy lại
không nhập mô-đun chứa cầu dao, bẫy đóng.

**Bẫy tự bịt mắt.** Chặn cả một chế độ là quyết định lớn, và **chế độ bị chặn thì
không bao giờ thu thêm dữ liệu để cãi lại.** Nên ngưỡng phải cao hơn ngưỡng phát
hiện nhiều lần (ở đây: ≥30 lệnh và ≤−0,25R, gấp ba ngưỡng thường), và phải có
phép kiểm cho **cửa ngược lại** — chế độ lỗ nông dù đủ mẫu vẫn KHÔNG được chặn.
Thiếu phép kiểm đó, ngưỡng sẽ trôi dần cho tới khi mọi chế độ đều bị khai tử.

Và luôn **giữ nguyên luận điểm gốc trong sổ** khi chặn. Xoá đi thì cầu dao thành
vô hình, không ai đánh giá được nó chặn đúng hay chặn oan.

## Cách dùng

Đứng trước một phát hiện, hỏi bốn câu:

1. **Cỡ mẫu bao nhiêu, từ nguồn nào?** 44 lệnh mô phỏng, 8 lệnh thật và 2 hồ sơ
   người ngoài là ba loại bằng chứng khác hẳn nhau.
2. **Nó nói về cấu trúc hay về độ lớn?** Chạy lại nói được cái đầu, không nói
   được cái sau.
3. **Nếu tin nó thì mình làm gì KHÁC đi?** Không trả lời được thì đó là một quan
   sát, không phải một phát hiện.
4. **Có phát hiện nào đang mâu thuẫn với nó không?** Chạy lại nói một đằng và sổ
   thật nói một nẻo là chuyện bình thường — khi đó sổ thật thắng về độ lớn, chạy
   lại thắng về cấu trúc.
