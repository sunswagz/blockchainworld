"""TY PHÁI SINH — cắm `bac/` vào khuôn `thi_bac_ty.Ty`.

File này **không** chứa logic mới. Nó là chỗ nối, và nó cố tình mỏng: mọi
việc đo đạc vẫn nằm trong `can_loi.py`, `rui_ro.py`, `xuat_to_trinh.py`. Nếu
một ngày file này dày lên thì đó là dấu hiệu logic đang trôi ra khỏi ty và
vào chỗ nối — sửa chỗ đó, đừng để nó ở đây.

## `quet()` KHÔNG gọi mạng

`Runtime.mot_vong()` đã hỏi bốn sàn và đã dựng `self.coHoi` xong. Nếu `quet()`
gọi mạng lần nữa thì mỗi vòng hỏi hai lượt, và tệ hơn: hai lượt ấy chụp hai
thời điểm khác nhau, nên báo giá dùng để tính lại không phải báo giá đã ghi
vào băng. Đúng lỗi ghép-hai-thời-điểm mà `dong_ho.py` sinh ra để chặn.

Nên `quet()` ở đây chỉ **đọc lại** lượt quét vừa xong.

## `quet()` trả về CẢ cơ hội bị loại, có chủ ý

Trả về mỗi cơ hội đã qua cổng thì `soCoHoi` bằng `soQuaCongTy`, và tỉ lệ sống
sót qua cổng ty vĩnh viễn là 100% — một con số luôn đẹp là một con số không
nói gì. Cái phễu chỉ có nghĩa khi mẫu số là số cơ hội THẬT SỰ nhìn thấy.
"""
from __future__ import annotations

from thi_bac_ty.khuon_ty import Ty

from .config import CONFIG, MA_CHIEN_LUOC
from .xuat_to_trinh import HO, xuat_to_trinh


class TyPerp(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("chênh lệch funding perp giữa Hyperliquid · Binance · OKX · "
            "Bybit; delta-neutral hai chân, thu tại MỐC KẾT TOÁN")

    def __init__(self, runtime) -> None:
        super().__init__()
        self._rt = runtime

    # ── ba việc, và chỉ ba ────────────────────────────────────────────────
    def quet(self) -> list:
        """Đọc lại lượt quét vừa xong. Xem docstring đầu file."""
        return list(self._rt.coHoi)

    def xet(self, co) -> tuple[bool, list[tuple[str, str]]]:
        """Cổng ty đã chạy trong `tim_co_hoi()`; ở đây chỉ đọc kết quả.

        Chạy lại `cong.xet()` ở đây sẽ cho cùng một câu trả lời trên cùng dữ
        liệu, nhưng nó tạo ra hai chỗ cùng quyết một chuyện — và hai chỗ ấy
        sẽ lệch nhau đúng vào ngày ai đó sửa một chỗ.
        """
        return bool(co.duyet), list(co.lyDoMa or ())

    def trinh(self, co):
        """Dịch sang `ToTrinh`. `oiUsd` tra từ CHÍNH lượt quét này."""
        oi = {(b.ma, b.san): b.oiUsd for b in self._rt.baoGia}
        xin = float((CONFIG.get("von") or {}).get("moiCoHoiUsd", 100.0))
        return xuat_to_trinh(
            co, vonXinUsd=xin,
            oiLongUsd=oi.get((co.ma, co.sanLong)),
            oiShortUsd=oi.get((co.ma, co.sanShort)))
