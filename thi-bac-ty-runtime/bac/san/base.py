"""Khuôn chung cho một cảng, và sổ sức khoẻ của nó."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod

from ..models import BaoGia

GIO_MS = 3_600_000


class SucKhoe:
    """Cảng này có đang sống không — và đừng để nó chết trong im lặng.

    Một cảng hỏng mà bảng vẫn hiện đủ ba cảng còn lại thì người xem đọc thành
    "thị trường không có chênh lệch", trong khi sự thật là "mình đang mù một
    mắt". Nên mọi lượt hỏi đều để lại dấu ở đây, và buồng lái hiện nó cạnh
    từng cảng chứ không gộp vào một dòng chung.
    """

    def __init__(self, ten: str) -> None:
        self.ten = ten
        self.tongLuot = 0
        self.soLoi = 0
        self.loiCuoi: str | None = None
        self.lanCuoiOkMs: float = 0.0
        self.treTrungBinhMs: float | None = None

    def ghi_ok(self, treMs: float) -> None:
        self.tongLuot += 1
        self.lanCuoiOkMs = time.time() * 1000.0
        self.treTrungBinhMs = (treMs if self.treTrungBinhMs is None
                               else self.treTrungBinhMs * 0.7 + treMs * 0.3)

    def ghi_loi(self, e: BaseException) -> None:
        self.tongLuot += 1
        self.soLoi += 1
        self.loiCuoi = f"{type(e).__name__}: {e}"

    def tuoi_giay(self) -> float | None:
        if self.lanCuoiOkMs <= 0:
            return None
        return (time.time() * 1000.0 - self.lanCuoiOkMs) / 1000.0

    def tom_tat(self) -> dict:
        return {
            "ten": self.ten, "tongLuot": self.tongLuot, "soLoi": self.soLoi,
            "loiCuoi": self.loiCuoi, "tuoiGiay": self.tuoi_giay(),
            "treTrungBinhMs": self.treTrungBinhMs,
            "songSot": self.lanCuoiOkMs > 0,
        }


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


def moc_tron_gio_ke(nowMs: float | None = None) -> int:
    """Mốc tròn giờ kế tiếp, epoch ms. Dùng cho cảng kết toán theo giờ."""
    now = nowMs if nowMs is not None else time.time() * 1000.0
    return int((int(now) // GIO_MS + 1) * GIO_MS)


def so_hoac_none(v):
    if v in (None, "", "null"):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f and abs(f) != float("inf") else None      # loại NaN/inf


def nguyen_hoac_none(v):
    f = so_hoac_none(v)
    return None if f is None else int(f)
