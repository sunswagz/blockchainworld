"""Hai kiểu dữ liệu của cả runtime: một BÁO GIÁ, một CƠ HỘI.

Cố ý ít kiểu. Mọi thứ khác là dict thuần đi thẳng ra JSON cho buồng lái — thêm
một lớp kiểu nữa chỉ tạo thêm chỗ để hai bản sao lệch nhau.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field


def bay_gio() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class BaoGia:
    """Funding của MỘT tài sản trên MỘT sàn, tại một thời điểm.

    `rate` là mức trả cho ĐÚNG MỘT chu kỳ kết toán của sàn ấy — không phải mỗi
    giờ, không phải mỗi ngày. Bốn sàn có bốn chu kỳ khác nhau và chu kỳ còn
    đổi được giữa chừng (OKX chuyển 8h→4h→2h→1h tuỳ điều kiện thị trường), nên
    `rate` mà không kèm `intervalGio` là một con số vô nghĩa.

    Đây chính là chỗ một scanner sơ sài sập: nó so 0,08%/8h với 0,015%/1h rồi
    kết luận sàn đầu trả cao hơn, trong khi sự thật ngược lại (0,010%/giờ so
    với 0,015%/giờ).
    """
    san: str
    ma: str                       # BTC, ETH, SOL…
    rate: float                   # phần trả cho MỘT chu kỳ, vd 0.0001 = 0,01%
    intervalGio: float            # độ dài chu kỳ, tính bằng giờ
    markPx: float | None          # GIÁ MARK, không phải giá khớp cuối
    mocKeMs: int | None           # mốc kết toán kế tiếp, epoch ms
    oiUsd: float | None = None
    nguonTsMs: int | None = None  # sàn đóng dấu lúc nào
    nhanTsMs: int | None = None   # máy mình nhận lúc nào
    intervalSuyRa: bool = False   # True = phải suy chu kỳ, sàn không nói thẳng
    ghiChu: str = ""

    @property
    def moiGio(self) -> float:
        from .dongho import moi_gio
        return moi_gio(self.rate, self.intervalGio)

    @property
    def moiNgay(self) -> float:
        return self.moiGio * 24.0

    def tuoi_giay(self, nowMs: float) -> float | None:
        """Báo giá này già bao nhiêu giây, theo dấu thời gian của SÀN.

        Lấy `nguonTsMs` chứ không lấy `nhanTsMs`: một request thành công vẫn
        có thể trả về dữ liệu sàn đã cache từ lâu, và lúc đó `nhanTsMs` mới
        tinh nhưng nội dung thì cũ. Đo nhầm cái sau là tự cấp cho mình một
        cảm giác tươi mới không có thật.
        """
        if self.nguonTsMs is None:
            return None
        return max(0.0, (nowMs - self.nguonTsMs) / 1000.0)

    def tom_tat(self, nowMs: float) -> dict:
        return {
            "san": self.san, "ma": self.ma,
            "rate": self.rate, "intervalGio": self.intervalGio,
            "moiGio": self.moiGio, "moiNgayBps": self.moiNgay * 10_000.0,
            "markPx": self.markPx, "mocKeMs": self.mocKeMs,
            "oiUsd": self.oiUsd, "tuoiGiay": self.tuoi_giay(nowMs),
            "intervalSuyRa": self.intervalSuyRa, "ghiChu": self.ghiChu,
        }


@dataclass(frozen=True)
class CoHoi:
    """Một cặp LONG/SHORT đã tính đủ chi phí, đã qua cổng rủi ro.

    `netBps` là con số DUY NHẤT đáng dùng để xếp hạng. `grossBpsNgay` để lên
    bảng cho người đọc thấy chênh lệch thô, nhưng nó chưa trừ gì cả.
    """
    ma: str
    sanLong: str
    sanShort: str
    rateLong: float
    rateShort: float
    intervalLongGio: float
    intervalShortGio: float

    grossBpsNgay: float           # chênh lệch chuẩn hoá, bps/ngày — để SO SÁNH
    giuGio: float                 # cửa sổ giữ đang giả định
    soMocLong: int                # số mốc kết toán thực rơi vào cửa sổ
    soMocShort: int
    thuBps: float                 # funding thực thu trong cửa sổ, bps
    phiBps: float                 # phí + trượt giá, cả vào lẫn ra, hai chân
    netBps: float                 # thuBps − phiBps  ← thứ duy nhất là alpha
    netAprPct: float | None       # ngoại suy, có thể là None khi vô nghĩa

    lechMarkBps: float | None
    choMocDauGiay: float | None
    tuoiXauNhatGiay: float | None
    uocLuongMoc: bool

    duyet: bool
    lyDo: tuple[str, ...] = ()
    luc: str = field(default_factory=bay_gio)

    def tom_tat(self) -> dict:
        return {
            "ma": self.ma, "sanLong": self.sanLong, "sanShort": self.sanShort,
            "rateLong": self.rateLong, "rateShort": self.rateShort,
            "intervalLongGio": self.intervalLongGio,
            "intervalShortGio": self.intervalShortGio,
            "grossBpsNgay": self.grossBpsNgay, "giuGio": self.giuGio,
            "soMocLong": self.soMocLong, "soMocShort": self.soMocShort,
            "thuBps": self.thuBps, "phiBps": self.phiBps, "netBps": self.netBps,
            "netAprPct": self.netAprPct, "lechMarkBps": self.lechMarkBps,
            "choMocDauGiay": self.choMocDauGiay,
            "tuoiXauNhatGiay": self.tuoiXauNhatGiay,
            "uocLuongMoc": self.uocLuongMoc,
            "duyet": self.duyet, "lyDo": list(self.lyDo), "luc": self.luc,
        }
