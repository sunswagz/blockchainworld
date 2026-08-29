"""Đài Quan Ví — quan sát bot khác, và một giới hạn phải nói thẳng.

Giữ đúng tinh thần `giai_phau.py` của Tử Cấm Thành: **quan sát được gì thì
nói cái đó**. Không suy ra động cơ, không gán chiến lược cho ai, không sao
chép lệnh.

## Giới hạn không vượt qua được, và vì sao phải ghi nó ở đây

Nghiên cứu về Polymarket chỉ ra: vì đặt và huỷ lệnh diễn ra OFF-CHAIN, dữ
liệu blockchain của một ví KHÔNG đủ để dựng lại toàn bộ vòng đời báo giá của
nó. Ta thấy được các lần KHỚP, không thấy được các lần YẾT rồi HUỶ.

Hệ quả rất cụ thể: có thể nói "ví này khớp cả hai chiều trong 93% số market
nó tham gia". KHÔNG thể nói "ví này là market maker" — vì phần lớn hoạt động
của một market maker nằm ở những lệnh chưa bao giờ khớp.

Nên mọi nhãn ở đây đều kèm `bangChung` là thứ ĐO ĐƯỢC, và mọi nhãn đều mang
`doTinCay`. Nhãn nào không có bằng chứng đo được thì không tồn tại.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

from .config import CONFIG
from .bus import bus
from .nguon import nguon

_VI = CONFIG["vi"]


@dataclass
class HoSoVi:
    ten: str
    soLenh: int = 0
    soMarket: int = 0
    caHaiChieu: int = 0             # market mà ví khớp cả UP lẫn DOWN
    tongTienUsd: float = 0.0
    giaVaoTrungBinh: float = 0.0
    canKetQua: int = 0              # số lần vào ở giá trên 90c
    khungNgan: int = 0              # số lần vào market 5m/15m
    quanSatLuc: str = ""
    nhan: list[dict] = field(default_factory=list)

    @property
    def tiLeCaHaiChieu(self) -> float:
        return self.caHaiChieu / self.soMarket if self.soMarket else 0.0

    @property
    def tiLeCanKetQua(self) -> float:
        return self.canKetQua / self.soLenh if self.soLenh else 0.0


# Mỗi nhãn khai rõ: đo bằng gì, và nói được tới đâu.
LUAT_NHAN = [
    {
        "ma": "hai-chieu",
        "ten": "Khớp hai chiều",
        "dieuKien": lambda h: h.soMarket >= 8 and h.tiLeCaHaiChieu >= 0.6,
        "doTinCay": "cao",
        "noiDuoc": "Ví này thường giữ cả UP lẫn DOWN trong cùng một market.",
        "khongNoiDuoc": "KHÔNG suy ra được đây là arbitrage hay market making — "
                        "phần yết-rồi-huỷ nằm off-chain, không đọc được.",
    },
    {
        "ma": "can-ket-qua",
        "ten": "Săn cận kết quả",
        "dieuKien": lambda h: h.soLenh >= 20 and h.tiLeCanKetQua >= 0.35,
        "doTinCay": "cao",
        "noiDuoc": "Phần lớn lệnh vào ở giá trên 90c, tức là sát lúc kết quả rõ.",
        "khongNoiDuoc": "KHÔNG suy ra được lãi hay lỗ — ngón này lãi đều rồi "
                        "mất lớn một lần, và một lát cắt không thấy được lần đó.",
    },
    {
        "ma": "khung-ngan",
        "ten": "Chuyên khung ngắn",
        "dieuKien": lambda h: h.soLenh >= 20 and h.khungNgan / max(1, h.soLenh) >= 0.7,
        "doTinCay": "cao",
        "noiDuoc": "Hoạt động gần như chỉ ở market 5 và 15 phút.",
        "khongNoiDuoc": "KHÔNG suy ra được có dùng bot hay không — tần suất cao "
                        "là gợi ý mạnh, không phải bằng chứng.",
    },
    {
        "ma": "tan-suat-cao",
        "ten": "Tần suất cao",
        "dieuKien": lambda h: h.soLenh >= 500,
        "doTinCay": "trung bình",
        "noiDuoc": "Số lệnh quan sát được trong cửa sổ này rất lớn.",
        "khongNoiDuoc": "Cửa sổ quan sát có giới hạn của API, nên đây là SÀN "
                        "DƯỚI của hoạt động thật, không phải tổng.",
    },
]


class DaiQuanVi:
    def __init__(self) -> None:
        self.hoSo: dict[str, HoSoVi] = {}
        self.nga: dict[str, str] = {}
        self._lanCuoiMs = 0.0

    def den_luot(self) -> bool:
        cach = float(_VI["phutGiuaHaiLuot"]) * 60_000.0
        return (time.time() * 1000.0 - self._lanCuoiMs) >= cach

    def quet(self, danhSach: list[str] | None = None) -> dict[str, HoSoVi]:
        """Quét các ví theo dõi. Chỉ ĐỌC, không sao chép lệnh của ai.

        Một ví hỏng KHÔNG được giết cả lượt quét — nhưng cũng không được
        biến mất không dấu vết. Bản trước là `except Exception: continue`
        trần: một `KeyError` trong `_mot_vi` làm MỌI ví trượt im lặng, và
        buồng lái hiện "chưa quét ví nào" — không phân biệt được với
        "chưa tới lượt". Đúng hình dạng lỗi đã giấu `KeyError: 'gamma'`
        suốt mấy tiếng trong khi buồng lái vẫn xanh.

        Nên: vẫn đi tiếp, nhưng GHI LẠI, và `tom_tat` khai ra.
        """
        self._lanCuoiMs = time.time() * 1000.0
        self.nga = {}
        for ten in (danhSach or _VI["theoDoi"]):
            try:
                self.hoSo[ten] = self._mot_vi(ten)
            except Exception as e:                  # noqa: BLE001
                self.nga[ten] = f"{type(e).__name__}: {e}"[:160]
                continue
        if self.nga:
            bus.ghi(f"quét ví: {len(self.nga)}/{len(danhSach or _VI['theoDoi'])}"
                    f" ví ngã — {'; '.join(list(self.nga)[:3])}", loai="canh")
        return self.hoSo

    def _mot_vi(self, ten: str) -> HoSoVi:
        h = HoSoVi(ten=ten, quanSatLuc=time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                     time.gmtime()))
        hd = nguon.hoat_dong_vi(ten, gioiHan=500) or []
        theo_market: dict[str, set] = defaultdict(set)
        tong_tien = 0.0
        tong_gia = 0.0
        dem_gia = 0

        for a in hd:
            if (a.get("type") or "").upper() not in ("TRADE", "BUY", "SELL", ""):
                continue
            h.soLenh += 1
            mid = str(a.get("conditionId") or a.get("market") or "")
            ben = (a.get("outcome") or "").upper()
            if mid and ben:
                theo_market[mid].add(ben)
            try:
                gia = float(a.get("price"))
                sl = float(a.get("size") or 0)
            except (TypeError, ValueError):
                continue
            tong_tien += gia * sl
            tong_gia += gia
            dem_gia += 1
            if gia >= 0.90:
                h.canKetQua += 1
            tieu_de = (a.get("title") or a.get("slug") or "").lower()
            if "5m" in tieu_de or "15m" in tieu_de or "up or down" in tieu_de:
                h.khungNgan += 1

        h.soMarket = len(theo_market)
        h.caHaiChieu = sum(1 for s in theo_market.values() if len(s) >= 2)
        h.tongTienUsd = tong_tien
        h.giaVaoTrungBinh = tong_gia / dem_gia if dem_gia else 0.0
        h.nhan = self._gan_nhan(h)
        return h

    @staticmethod
    def _gan_nhan(h: HoSoVi) -> list[dict]:
        ra = []
        for l in LUAT_NHAN:
            try:
                if l["dieuKien"](h):
                    ra.append({k: v for k, v in l.items() if k != "dieuKien"})
            except Exception:                       # noqa: BLE001
                continue
        return ra

    def tom_tat(self) -> dict:
        return {
            "soVi": len(self.hoSo),
            # Ví nào ngã và vì sao. Không có trường này thì một lượt quét
            # hỏng sạch trông y hệt một lượt quét chưa tới lượt.
            "nga": dict(self.nga),
            "quetLucMs": self._lanCuoiMs,
            "gioiHan": "Đặt/huỷ lệnh diễn ra off-chain, nên chỉ thấy được các "
                       "lần KHỚP. Không dựng lại được vòng đời báo giá, và vì "
                       "vậy không kết luận được ai là market maker.",
            "vi": [
                {
                    "ten": h.ten, "soLenh": h.soLenh, "soMarket": h.soMarket,
                    "tiLeCaHaiChieu": h.tiLeCaHaiChieu,
                    "tiLeCanKetQua": h.tiLeCanKetQua,
                    "giaVaoTrungBinh": h.giaVaoTrungBinh,
                    "tongTienUsd": h.tongTienUsd,
                    "nhan": h.nhan, "quanSatLuc": h.quanSatLuc,
                }
                for h in self.hoSo.values()
            ],
        }


dai_quan_vi = DaiQuanVi()
