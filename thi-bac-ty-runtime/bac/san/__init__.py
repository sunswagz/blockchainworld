"""Bốn cảng perp — thân hàm ở `phai_sinh_chung/san/`.

Chuyển ra khi ty Cơ Sở tới: nó đọc mark và funding của ĐÚNG những sàn ấy.
Để mỗi ty tự hỏi một lượt là hai ảnh chụp ở hai thời điểm rồi đem so như thể
cùng lúc — đúng lỗi mà `dong_ho.py` sinh ra để chặn, chỉ khác là lần này
giữa hai TY chứ không giữa hai cảng.
"""
from phai_sinh_chung.san import TAT_CA  # noqa: F401
from phai_sinh_chung.san.base import (  # noqa: F401
    Cang, SucKhoe, bay_gio_ms, moc_tron_gio_ke, nguyen_hoac_none,
    so_hoac_none)
