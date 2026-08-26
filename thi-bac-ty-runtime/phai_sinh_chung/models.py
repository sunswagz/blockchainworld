"""Kiểu dữ liệu dùng chung của HỌ PHÁI SINH.

`BaoGia` ở đây chứ không ở trong một ty, vì ty Cơ Sở cũng đọc mark và
funding của đúng những sàn ấy. Để nó nằm trong `bac/` thì ty thứ hai phải
`import bac.models` — mà ty gọi ty là điều luật chung cấm.

`CoHoi` thì ở lại `bac/`: nó là ngôn ngữ NỘI BỘ của riêng ty chênh lệch
funding, và không ty nào khác cần hiểu `soMocLong` hay `intervalShortGio`.
"""
from __future__ import annotations

from __future__ import annotations
import datetime as dt
from dataclasses import dataclass, field


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
