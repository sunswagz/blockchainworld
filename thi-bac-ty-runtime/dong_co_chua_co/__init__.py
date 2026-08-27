"""SỔ ĐĂNG KÝ ENGINE CHƯA CÓ — và điều kiện để chúng thôi bị chặn.

README từng khai sáu engine "bị chặn vì hạ tầng" bằng văn xuôi. Văn xuôi có
đúng một cách hỏng, và nó hỏng im lặng: **thế giới đổi mà câu văn không
đổi**. Router ra đời ngày 27/08/2026 và gỡ mất một điều kiện chặn của hai
engine trong sáu — nhưng đoạn văn kia vẫn nói y như cũ, và sẽ còn nói y như
cũ cho tới khi có người nhớ ra.

Nên file này làm với engine đúng thứ `hien_phap.py` làm với luật: mỗi
engine mang theo **điều kiện chặn của chính nó, viết dưới dạng hàm canh**.
Chạy một lượt thì biết cái nào còn chặn, cái nào đã mở, và mở nhờ cái gì.

## Ba trạng thái, và phân biệt chúng mới là điểm của cả file

    CHAN        thiếu hạ tầng tới mức không QUÉT được
    QUET_DUOC   quét được, nhưng KHÔNG thực thi được
    SAN_SANG    mọi điều kiện đã đủ — dựng được ngay

`QUET_DUOC` là trạng thái đáng giá nhất và cũng dễ bị bỏ sót nhất. Một
engine quét được mà chưa thực thi được vẫn **có ích ngay**: nó đo được cơ
hội có thật hay không trước khi ai bỏ công dựng lớp thực thi. Cả runtime
này đang chạy `moPhong=True` — không ty nào trong sáu ty hiện có thực thi
gì cả — nên "chưa thực thi được" không phải lý do để không dựng.

Cái phân biệt `QUET_DUOC` với `CHAN` là **dữ liệu công khai không cần
khoá**. Không có dữ liệu thì scanner chỉ là một cái vỏ luôn trả rỗng, và
một cái vỏ như thế tệ hơn không có: nó làm phễu có thêm một dòng vĩnh viễn
bằng không, và người đọc tưởng đã phủ engine ấy.

## Vì sao nó KHÔNG phải một ty, và không nằm trong `thi_bac_ty/`

Nó không quét cơ hội, không xin vốn, không có `quet()`. Và nó nói về những
ty CHƯA tồn tại — mà Trung Ương thì không được biết ty nào tồn tại, huống
hồ ty nào sắp tồn tại.
"""
