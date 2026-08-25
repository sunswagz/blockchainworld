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
    nguonTsMs: int | None = None  # dấu thời gian đi kèm báo giá
    nhanTsMs: int | None = None   # máy mình nhận lúc nào
    #: `nguonTsMs` có phải do SÀN đóng dấu không. False = adapter tự điền giờ
    #: máy vì sàn không gửi. Phân biệt được hai thứ này mới đo được lệch đồng
    #: hồ: lấy dấu mình tự điền đi đo đồng hồ của chính mình thì luôn ra 0.
    nguonTuSan: bool = False
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
        """Báo giá này già bao nhiêu giây. **Có thể ÂM** — xem dưới.

        Lấy `nguonTsMs` chứ không lấy `nhanTsMs`: một request thành công vẫn
        có thể trả về dữ liệu sàn đã cache từ lâu, và lúc đó `nhanTsMs` mới
        tinh nhưng nội dung thì cũ. Đo nhầm cái sau là tự cấp cho mình một
        cảm giác tươi mới không có thật.

        **KHÔNG kẹp về 0 nữa.** Bản đầu viết `max(0.0, …)`, và chính chỗ kẹp
        ấy giết cửa `tuoiToiDaGiay`: đồng hồ máy chậm 6,94 phút (đo thật
        21/08/2026) làm dấu thời gian sàn nằm ở tương lai, hiệu ra âm, kẹp về
        0 — "vừa mới tinh", mãi mãi, cho cả Binance lẫn OKX.

        Tuổi âm là một TÍN HIỆU, không phải một con số cần dọn: nó nói đồng
        hồ hai bên không khớp. Truyền `nowMs` từ `dong_ho.bay_gio_ms()` thì
        con số này về đúng; còn âm nghĩa là bù chưa đủ, và cổng rủi ro phải
        thấy điều đó.
        """
        if self.nguonTsMs is None:
            return None
        return (nowMs - self.nguonTsMs) / 1000.0

    def tom_tat(self, nowMs: float) -> dict:
        return {
            "san": self.san, "ma": self.ma,
            "rate": self.rate, "intervalGio": self.intervalGio,
            "moiGio": self.moiGio, "moiNgayBps": self.moiNgay * 10_000.0,
            "markPx": self.markPx, "mocKeMs": self.mocKeMs,
            "oiUsd": self.oiUsd, "tuoiGiay": self.tuoi_giay(nowMs),
            "nguonTuSan": self.nguonTuSan,
            "intervalSuyRa": self.intervalSuyRa, "ghiChu": self.ghiChu,
        }


#: Bốn khoản chi phí CHƯA có trong `netBps`, theo đúng thứ tự trong
#: `can_loi.py`. Một chỗ khai duy nhất — chép làm hai bản thì hai bản sẽ lệch,
#: và bản lệch sẽ là bản người ta đọc.
PHI_CON_THIEU = (
    "vay-coin",          # chi phí vay để short spot
    "chuyen-von",        # phí chuyển vốn giữa sàn
    "basis-luc-thoat",   # hai mark rời nhau lúc đóng vị thế
    "von-bi-khoa",       # vốn kẹt không làm được việc khác
)


@dataclass(frozen=True)
class CoHoi:
    """Một cặp LONG/SHORT đã trừ những chi phí ĐANG ĐO ĐƯỢC, đã qua cổng.

    **`netBps` là CHẶN TRÊN, không phải lợi nhuận.** Bản đầu của docstring
    này viết "đã tính đủ chi phí" trong khi `can_loi.py` ngay bên cạnh liệt kê
    bốn khoản chưa trừ — hai file trong cùng một gói nói ngược nhau, và người
    đọc `models.py` trước sẽ tin nhầm.

    Nên nay mỗi cơ hội mang theo `moHinhPhiDuChua` và `phiConThieu`: con số
    không tự nói được nó thiếu gì, nên nó phải mang theo lời khai.

    Chuyện này quan trọng hơn vẻ ngoài. Khi Thị Bạc Ty có chiến lược thứ hai,
    bảng xếp hạng sẽ đặt cạnh nhau:

        funding spread   18 bps   ← chặn trên, còn thiếu bốn khoản
        chiến lược khác  11 bps   ← đã trừ đủ

    và kết luận "funding tốt hơn" là kết luận SAI, rút ra từ hai con số không
    cùng đơn vị. Không có cờ này thì không cách nào biết mà tránh.

    `netBps` vẫn là con số đáng xếp hạng NHẤT trong các con số đang có.
    `grossBpsNgay` để lên bảng cho người đọc thấy chênh lệch thô, chưa trừ gì.
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

    #: Mô hình phí đã đủ chưa. **Luôn False ở bản này** — xem `PHI_CON_THIEU`.
    #: Không để mặc định True: một trường mặc định "đã đủ" mà quên đặt lại là
    #: đúng cách con số này bắt đầu nói dối.
    moHinhPhiDuChua: bool = False
    #: Những khoản chi phí CHƯA trừ. Rỗng chỉ khi `moHinhPhiDuChua` là True.
    phiConThieu: tuple[str, ...] = ()

    duyet: bool = False
    #: Câu đầy đủ cho người đọc — có mang con số, nên KHÔNG gộp được.
    lyDo: tuple[str, ...] = ()
    #: Mã lý do để GỘP. Xem `rui_ro.NHAN`. Hai trường này luôn cùng độ dài.
    lyDoMa: tuple[str, ...] = ()
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
            "moHinhPhiDuChua": self.moHinhPhiDuChua,
            "phiConThieu": list(self.phiConThieu),
            "duyet": self.duyet, "lyDo": list(self.lyDo),
            "lyDoMa": list(self.lyDoMa), "luc": self.luc,
        }
