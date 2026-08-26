"""Hai kiểu dữ liệu của cả runtime: một BÁO GIÁ, một CƠ HỘI.

Cố ý ít kiểu. Mọi thứ khác là dict thuần đi thẳng ra JSON cho buồng lái — thêm
một lớp kiểu nữa chỉ tạo thêm chỗ để hai bản sao lệch nhau.
"""
from __future__ import annotations

#: `BaoGia` nay là của cả HỌ phái sinh — xem
#: `phai_sinh_chung/models.py`. Bí danh giữ ở đây vì `bac/`
#: đã gọi nó ở nhiều chỗ.
from phai_sinh_chung.models import BaoGia  # noqa: F401

import datetime as dt
from dataclasses import dataclass, field


def bay_gio() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")



#: Bốn khoản `can_loi.py` CHƯA trừ được. Của RIÊNG ty chênh lệch
#: funding, không phải của cả họ phái sinh — nên nó ở lại đây khi
#: `BaoGia` chuyển ra `phai_sinh_chung/`.
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
