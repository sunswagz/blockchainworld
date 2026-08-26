"""Thang rủi ro dùng chung cho các ty ĐỌC CHUỖI.

Đây là **hạ tầng dùng chung của một họ**, không phải một ty và cũng không
phải Trung Ương:

    thi_bac_ty/     TRUNG ƯƠNG — không biết ty nào tồn tại, không biết
                    "TVL" hay "dùng vốn" là gì
    chuoi_chung/    hạ tầng cho ty đọc chuỗi — biết TVL, biết dùng vốn,
                    KHÔNG biết chiến lược nào
    tin_dung/       ty
    lai_suat/       ty

Trước file này, `tin_dung` có hai thang ấy trong `ty_vay.py`. Khi ty thứ
hai đọc chuỗi xuất hiện, hai lựa chọn đều sai: chép sang (hai bản sao sẽ
lệch nhau đúng vào ngày ai đó hiệu chỉnh một bản), hoặc để ty mới import
ty cũ (ty gọi thẳng ty khác — điều luật chung cấm).

Chỗ thứ ba mới đúng, và bản đồ đã vẽ sẵn nó: **SHARED INFRASTRUCTURE**.

Cả hai thang dưới đây đều đã SAI một lần, và cách chúng sai đáng nhớ hơn
cách chúng đúng.
"""
from __future__ import annotations

import math


def rui_ro_tvl(tvlUsd: float | None) -> float | None:
    """TVL → rủi ro giao thức, thang [0,15 · 0,85], MỖI BẬC MƯỜI LẦN.

    Bản đầu dùng `sqrt(50M / TVL)` chặn trên bằng 1, và nó **bão hoà**: mọi
    giao thức dưới $50M đều ra đúng 1,00. Vì `rui_ro_tong.diem()` lấy MAX
    trong sáu mặt, một mặt bằng 1,00 loại thẳng cả cơ hội — nên cửa TVL vô
    tình biến thành "chỉ nhận giao thức trên $50M", một luật không ai khai
    và không đọc được ở đâu.

        $5M → 0,70   $50M → 0,45   $500M → 0,20   ≥$5B → 0,15

    Không mặt nào chạm 1,00: "chưa được kiểm chứng bằng thời gian" không
    phải là "chắc chắn hỏng".

    Vẫn là PROXY THÔ. TVL lớn nghĩa là đã sống lâu và bị soi nhiều, KHÔNG
    có nghĩa là đã được kiểm toán. Đừng đọc con số này như một kết luận.

    **Truyền TVL của GIAO THỨC, không của pool.** Một lỗi trong Aave v3 ảnh
    hưởng mọi thị trường Aave v3, dù thị trường ấy có $11M hay $2B.
    """
    if not tvlUsd or tvlUsd <= 0:
        return None
    return max(0.15, min(0.85, 0.70 - 0.25 * math.log10(tvlUsd / 5_000_000.0)))


def rui_ro_su_dung(u: float | None) -> float | None:
    """Dùng vốn → rủi ro thanh khoản. LỒI, không tuyến tính.

    Bản đầu lấy thẳng `rủi ro = dùng vốn`, và nó gọi sức khoẻ là bệnh: dùng
    vốn 80% ở một thị trường cho vay là BÌNH THƯỜNG và LÀNH MẠNH — nó chính
    là thứ sinh ra lãi. Chấm 0,80 khiến `rui_ro_tong` (lấy MAX) loại sạch
    mọi thị trường đang hoạt động, và chỉ nhận thị trường không ai vay —
    tức là thị trường không trả lãi.

        ≤50% → 0,02   70% → 0,16   80% → 0,36   90% → 0,64   100% → 0,95

    Đây là rủi ro TỈ LỆ. Rủi ro CỠ — "rút $200 ra có được không" — nằm ở
    `ToTrinh.thanhKhoanThoatUsd`, và nó CẮT TRẦN chứ không chấm điểm. Hai
    câu khác nhau, hai chỗ khác nhau.
    """
    if u is None:
        return None
    if u <= 0.5:
        return 0.02
    return max(0.02, min(0.95, ((u - 0.5) / 0.5) ** 2))


def thang(gt: float | None, tran: float) -> float | None:
    """Đưa một số về thang [0,1] theo trần. `None` vào thì `None` ra."""
    if gt is None:
        return None
    return max(0.0, min(1.0, gt / tran)) if tran > 0 else None
