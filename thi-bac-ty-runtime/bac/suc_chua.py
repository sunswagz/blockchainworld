"""Sức chứa — rót thêm tới đâu thì chính cơ hội tự giết mình.

Hợp đồng `ToTrinh` đòi `sucChuaToiDaUsd`, và đây là chỗ ty Phái Sinh trả lời.

## Bản này ước lượng THÔ, và nói thẳng là thô

Sức chứa thật đo bằng **độ sâu sổ lệnh**: rót $X vào thì VWAP trượt bao nhiêu
bps, và trượt tới đâu thì ăn hết biên. Runtime hiện **không hỏi sổ lệnh của
cảng nào** — mọi adapter chỉ lấy funding, mark và (một phần) open interest.

Nên ở đây dùng open interest làm thay, với một hệ số nhỏ. Đó là một phép ĐOÁN
có căn cứ yếu:

    OI nói thị trường ĐANG giữ bao nhiêu vị thế
    sổ lệnh nói ta VÀO ĐƯỢC bao nhiêu mà không đội giá

Hai câu hỏi khác nhau. Một thị trường OI lớn mà sổ lệnh mỏng vẫn đội giá ngay,
và OI không hề biết điều đó.

## Vì sao vẫn làm bản thô thay vì đợi sổ lệnh

Vì `None` cũng là một câu trả lời tệ. Người phân bổ vốn gặp `sucChuaToiDaUsd
= None` thì không sizing được gì cả, và mọi tờ trình của ty này thành vô dụng
với trung ương — trong khi ta vẫn biết chắc một điều: **không phải vô hạn**.

Nên trả về một con số, kèm `moHinhSucChuaDuChua = False` và danh sách thiếu
gì. Trung ương biết đây là số thô thì nó tự hạ trọng số; nó không bao giờ
được phép tưởng đây là số đo.

Đúng khuôn `moHinhPhiDuChua` đã dùng cho phí — cùng một luật: **con số không
tự nói được nó thiếu gì, nên nó phải mang theo lời khai.**

## Vì sao lấy MIN của hai chân

Vị thế delta-neutral phải vào được CẢ HAI chân. Chân nào mỏng hơn thì chân ấy
quyết. Lấy trung bình là dựng ra một sức chứa không chân nào chịu nổi, và cái
chân mỏng sẽ trượt giá đúng lúc ta rót theo con số trung bình ấy.
"""
from __future__ import annotations

#: Phần open interest coi là vào được mà không đội giá đáng kể.
#:
#: **Con số này là quy ước, không phải phép đo.** 0,05% của OI: với BTC trên
#: Hyperliquid (~2,9 tỉ OI) ra ~1,4 triệu USD — nghe hợp lý, và đó chính là
#: vấn đề: "nghe hợp lý" không phải bằng chứng. Giữ nhỏ vì sai về phía thận
#: trọng thì mất cơ hội, sai về phía rộng thì mất tiền.
PHAN_OI = 0.0005

#: Trần tuyệt đối, bất kể OI to tới đâu. Chặn trường hợp một cảng báo OI sai
#: đơn vị (đã thấy sàn trả OI bằng số COIN thay vì USD) biến sức chứa thành
#: một con số vô nghĩa mà trung ương lại tin.
TRAN_USD = 250_000.0

#: Dưới ngần này thì coi như không đáng vào — phí cố định và công sức vận
#: hành ăn hết phần lãi của một vị thế quá nhỏ.
SAN_USD = 25.0

THIEU = ("do-sau-so-lenh", "oi-thieu-o-mot-so-cang")


def uoc_luong(oiLongUsd: float | None, oiShortUsd: float | None) -> tuple[float | None, tuple[str, ...]]:
    """Trả `(sức chứa USD, những thứ còn thiếu)`. `None` khi không đoán nổi.

    Thiếu OI ở **cả hai** chân thì trả `None` — không có gì để suy. Thiếu một
    chân thì dùng chân còn lại, và ghi rõ là đang suy từ một phía.
    """
    co = [x for x in (oiLongUsd, oiShortUsd) if x is not None and x > 0]
    if not co:
        return None, THIEU + ("khong-cang-nao-bao-oi",)

    # MIN, không phải trung bình — xem docstring đầu file.
    nen = min(co)
    suc = min(nen * PHAN_OI, TRAN_USD)
    if suc < SAN_USD:
        return None, THIEU + ("suc-chua-duoi-san",)

    thieu = THIEU
    if len(co) == 1:
        thieu = thieu + ("chi-mot-cang-bao-oi",)
    return suc, thieu
