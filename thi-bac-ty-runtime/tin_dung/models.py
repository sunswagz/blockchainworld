"""Kiểu dữ liệu NỘI BỘ của ty tín dụng.

Đây là ngôn ngữ riêng của ty — `suDung`, `apyThuong`, `thanhKhoanRanhUsd`.
Trung Ương không hiểu và không cần hiểu; nó chỉ đọc `ToTrinh`.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

NAM_GIO = 365.0 * 24.0


@dataclass(frozen=True)
class ThiTruongVay:
    """Một thị trường cho vay, tại một thời điểm."""
    ma: str                      # id pool của nguồn
    giaoThuc: str                # aave-v3, compound-v3, morpho-blue…
    chuoi: str                   # Ethereum, Base…
    taiSan: str                  # USDC…
    apyGocPhanTram: float        # lãi THẬT từ người vay
    apyThuongPhanTram: float     # token thưởng — sẽ bốc hơi, KHÔNG tính vào net
    tvlUsd: float                # của RIÊNG pool này
    #: TVL của CẢ GIAO THỨC, cộng mọi pool. Rủi ro hợp đồng là thuộc tính
    #: của giao thức, không của pool: một lỗi trong Aave v3 ảnh hưởng mọi
    #: thị trường Aave v3, dù thị trường ấy có $11M hay $2B.
    #:
    #: Bản đầu suy rủi ro giao thức từ TVL pool, và Aave-trên-Polygon bị
    #: chấm 0,61 — ngang một giao thức mới toanh — chỉ vì cái pool ấy nhỏ.
    tvlGiaoThucUsd: float | None = None
    tongCungUsd: float | None = None   # tổng đã gửi vào
    tongVayUsd: float | None = None    # tổng đã vay ra
    docLucMs: float = field(default_factory=lambda: time.time() * 1000.0)

    # ── suy ra ────────────────────────────────────────────────────────────
    @property
    def thanhKhoanRanhUsd(self) -> float | None:
        """Cung − vay. Đây là số tiền THẬT SỰ rút ra được ngay bây giờ.

        `None` khi thiếu một trong hai vế — và None ở đây phải chảy tới tận
        `ToTrinh.thanhKhoanThoatUsd`, chứ không được thay bằng 0 hay bằng
        TVL. Không biết rút được bao nhiêu là một trạng thái, không phải
        một con số.
        """
        if self.tongCungUsd is None or self.tongVayUsd is None:
            return None
        return max(0.0, self.tongCungUsd - self.tongVayUsd)

    @property
    def suDung(self) -> float | None:
        """Tỉ lệ dùng vốn. 1,0 = đã cho vay hết, không ai rút ra được."""
        if not self.tongCungUsd:
            return None
        return max(0.0, min(1.0, (self.tongVayUsd or 0.0) / self.tongCungUsd))

    @property
    def tyLeThuong(self) -> float:
        """Phần lãi đến từ token thưởng. Cao = đang MUA thanh khoản."""
        tong = abs(self.apyGocPhanTram) + abs(self.apyThuongPhanTram)
        return (abs(self.apyThuongPhanTram) / tong) if tong > 0 else 0.0

    def tuoi_giay(self, nowMs: float | None = None) -> float:
        now = nowMs if nowMs is not None else time.time() * 1000.0
        return (now - self.docLucMs) / 1000.0

    def bps_trong(self, gio: float) -> float:
        """Lãi GỐC quy ra bps trong `gio` giờ.

        Cộng gộp bỏ qua có chủ ý: ở 30 ngày và vài phần trăm một năm, chênh
        lệch giữa cộng gộp và tuyến tính nhỏ hơn sai số của chính con số APY
        mà nguồn công bố. Làm phức tạp thêm một phép tính đã kém chính xác
        hơn đầu vào của nó là tự tạo ra một con số trông chính xác hơn nó là.
        """
        return self.apyGocPhanTram * 100.0 * (gio / NAM_GIO)

    def tom_tat(self, nowMs: float | None = None) -> dict:
        return {
            "ma": self.ma, "giaoThuc": self.giaoThuc, "chuoi": self.chuoi,
            "taiSan": self.taiSan,
            "apyGocPhanTram": self.apyGocPhanTram,
            "apyThuongPhanTram": self.apyThuongPhanTram,
            "tyLeThuong": self.tyLeThuong,
            "tvlUsd": self.tvlUsd,
            "tvlGiaoThucUsd": self.tvlGiaoThucUsd,
            "tongCungUsd": self.tongCungUsd,
            "tongVayUsd": self.tongVayUsd,
            "thanhKhoanRanhUsd": self.thanhKhoanRanhUsd,
            "suDung": self.suDung,
            "tuoiGiay": self.tuoi_giay(nowMs),
        }


@dataclass(frozen=True)
class CoHoiVay:
    """Một cơ hội gửi vốn, sau khi đã trừ phí và soi cửa."""
    thiTruong: ThiTruongVay
    vonXinUsd: float
    giuGio: float
    grossBps: float
    phiBps: float
    netBps: float
    sucChuaToiDaUsd: float | None
    thanhKhoanThoatUsd: float | None
    hoaVonSauGio: float | None      # giữ bao lâu thì gas hoà
    duyet: bool = False
    lyDo: tuple = ()                # câu cho người đọc
    lyDoMa: tuple = ()              # (mã, câu) — mã để gộp thống kê

    @property
    def netMoiGioBps(self) -> float:
        return self.netBps / self.giuGio if self.giuGio else 0.0

    def tom_tat(self) -> dict:
        return {
            **self.thiTruong.tom_tat(),
            "vonXinUsd": self.vonXinUsd, "giuGio": self.giuGio,
            "grossBps": self.grossBps, "phiBps": self.phiBps,
            "netBps": self.netBps, "netMoiGioBps": self.netMoiGioBps,
            "sucChuaToiDaUsd": self.sucChuaToiDaUsd,
            "thanhKhoanThoatUsd": self.thanhKhoanThoatUsd,
            "hoaVonSauGio": self.hoaVonSauGio,
            "duyet": self.duyet, "lyDo": list(self.lyDo),
            "lyDoMa": [list(x) for x in self.lyDoMa],
        }
