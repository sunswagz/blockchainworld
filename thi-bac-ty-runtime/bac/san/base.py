"""Khuôn chung cho một cảng, và sổ sức khoẻ của nó."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod

from thi_bac_ty.nguon import (SucKhoeNguon, nguyen_hoac_none,   # noqa: F401
                             so_hoac_none)

from ..dong_ho import dong_ho
from ..models import BaoGia

GIO_MS = 3_600_000


#: Sổ sức khoẻ của một cảng. Thân hàm nằm ở `thi_bac_ty/nguon.py` — cùng
#: một kỷ luật cho MỌI nguồn, không phải một bản sao cho mỗi ty.
#:
#: Giữ tên cũ `SucKhoe` ở đây vì `bac/` đã gọi nó ở sáu chỗ, và đổi tên chỉ
#: để cho đẹp là một lần sửa rủi ro không đổi lấy gì.
SucKhoe = SucKhoeNguon


class Cang(ABC):
    """Một cảng. Chỉ đọc dữ liệu CÔNG KHAI — không khoá, không ký, không lệnh."""

    ten: str = "?"

    def __init__(self) -> None:
        self.suc_khoe = SucKhoe(self.ten)

    @abstractmethod
    async def _hoi(self, client, ma: list[str]) -> list[BaoGia]:
        raise NotImplementedError

    async def bao_gia(self, client, ma: list[str]) -> list[BaoGia]:
        """Hỏi cảng, và KHÔNG BAO GIỜ ném ra ngoài.

        Ba cảng sống mà một cảng chết thì vẫn còn ba cặp để ghép. Để lỗi ném
        lên trên là biến một sự cố của một cảng thành mất trắng cả lượt quét.
        """
        t0 = time.perf_counter()
        try:
            ra = await self._hoi(client, ma)
        except Exception as e:                      # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
        self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        return ra


def bay_gio_ms() -> float:
    """Giờ SÀN đã bù lệch. **Mọi adapter phải dùng hàm này, không dùng
    `time.time()`.**

    Sàn không đóng dấu thời gian thì adapter tự điền — nhưng phải điền vào
    ĐÚNG MIỀN đồng hồ mà tầng trên đem ra so, nếu không nó tự làm mình thành
    dữ liệu cũ.

    Đã cắn thật ngay lúc dựng: sau khi bù lệch, `now` của vòng lặp chuyển
    sang giờ sàn (+397s), còn Hyperliquid và Bybit vẫn đóng dấu bằng giờ máy
    — nên cả hai bị vứt với lý do "cũ hơn 90s", mỗi lượt quét đúng 10 báo
    giá. Bảng vẫn xanh, chỉ có hai trong bốn cảng lặng lẽ biến mất.
    """
    return dong_ho.bay_gio_ms()


def moc_tron_gio_ke(nowMs: float | None = None) -> int:
    """Mốc tròn giờ kế tiếp, epoch ms. Dùng cho cảng kết toán theo giờ."""
    now = nowMs if nowMs is not None else bay_gio_ms()
    return int((int(now) // GIO_MS + 1) * GIO_MS)
