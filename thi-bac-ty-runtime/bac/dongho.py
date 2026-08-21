"""Đồng hồ kết toán — và lỗi tệ nhất của mọi funding scanner sơ sài.

## Funding KHÔNG chảy liên tục

Bản v0.1 mà runtime này thay thế tính thu nhập funding như thế này:

    thu = funding_moi_gio × số_giờ_giữ

Công thức ấy trông hiển nhiên và nó SAI, vì funding không phải lãi suất tích
luỹ từng giây. Nó là một khoản trả **tại một mốc**. Sàn kết toán 8 giờ trả
vào 00:00, 08:00, 16:00 UTC — không trả gì vào lúc 03:47.

Hệ quả, bằng số:

    Binance funding 0,01% / 8 giờ.  Vào lệnh 00:05, thoát 04:05 (giữ 4 giờ).
    Công thức cũ:  0,01% × (4/8) = 0,005%   ← nghe hợp lý
    Thực tế:       0,00%                    ← chưa qua mốc nào

Ngược lại, vào 07:55 và thoát 08:05 (giữ 10 PHÚT) thì thu trọn 0,01%. Cùng
một cặp sàn, cùng một mức funding, hai câu trả lời lệch nhau vô hạn lần — và
công thức cũ không phân biệt được hai trường hợp ấy.

Sai số này không hiện ra như một lỗi. Nó hiện ra như một bảng xếp hạng cơ hội
sai thứ tự, và một con số "Net APR" đủ đẹp để người ta xuống tiền.

## Vì sao vẫn cần chuẩn hoá theo giờ

Chuẩn hoá `rate / interval_hours` vẫn đúng và vẫn cần — nhưng cho một việc
KHÁC: **so hai sàn với nhau về dài hạn**. Nó trả lời "sàn nào trả nhiều hơn",
không trả lời "giữ 6 tiếng thì được bao nhiêu".

Nên module này giữ hai phép đo riêng, và không cho phép lẫn:

    moi_gio()      so sàn với nhau. Đơn vị: phần/giờ.
    thu_thuc()     thu được bao nhiêu trong CỬA SỔ giữ cụ thể, đếm theo mốc.

## Quy ước dấu — giống nhau ở cả bốn sàn

    funding > 0  →  LONG trả, SHORT nhận
    funding < 0  →  LONG nhận, SHORT trả

Nên với một cặp (long ở A, short ở B):

    thu = (số mốc B) × rate_B  −  (số mốc A) × rate_A

Công thức ấy đúng cho MỌI dấu, kể cả khi cả hai âm. Đừng viết lại nó thành
`abs(...)` hay tách nhánh theo dấu — mỗi lần có người làm thế là một lần
nhánh âm im lặng đảo dấu.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

GIO_MS = 3_600_000.0


def moi_gio(rate: float, interval_hours: float) -> float:
    """Chuẩn hoá funding về phần/giờ. Dùng để SO SÀNH sàn, không để tính thu.

    `interval_hours` phải là số dương thật. Rơi vào 0 thì phép chia ném ra
    `ZeroDivisionError` chứ không trả về `inf` — một `inf` lọt vào bảng xếp
    hạng sẽ đứng đầu mọi cơ hội mãi mãi, và trông y hệt một cơ hội tốt.
    """
    if not (interval_hours > 0):
        raise ValueError(f"interval_hours phải > 0, nhận {interval_hours!r}")
    return rate / interval_hours


def moi_ngay(rate: float, interval_hours: float) -> float:
    return moi_gio(rate, interval_hours) * 24.0


@dataclass(frozen=True)
class LichMoc:
    """Các mốc kết toán rơi vào cửa sổ giữ, và tổng phần trăm trả tại đó."""
    soMoc: int
    mocDauMs: int | None      # mốc đầu tiên rơi vào cửa sổ
    mocCuoiMs: int | None     # mốc cuối cùng rơi vào cửa sổ
    choMocDauGiay: float | None   # phải chờ bao lâu tới đồng xu đầu tiên
    uocLuong: bool            # True = phải suy ra mốc vì sàn không cho biết


def dem_moc(nowMs: float, giuGio: float, mocKeMs: int | None,
            intervalGio: float) -> LichMoc:
    """Đếm số mốc kết toán rơi vào `[now, now + giuGio]`.

    `mocKeMs` là mốc kết toán KẾ TIẾP do sàn công bố. Thiếu nó thì không có
    cách nào biết đồng hồ của sàn đang ở đâu trong chu kỳ, và ta buộc phải
    ước lượng — nhưng phải KHAI ra là đang ước lượng (`uocLuong=True`), chứ
    không được lặng lẽ trả về một con số trông như đo được.

    Mốc rơi ĐÚNG vào biên cuối cửa sổ vẫn được tính: thoát lệnh lúc 08:00:00
    thì khoản funding 08:00 đã ghi vào vị thế trước khi lệnh đóng khớp. Đây
    là lựa chọn LẠC QUAN duy nhất trong cả module, và nó nằm ở đây một mình
    để dễ tìm; muốn thận trọng thì đổi `<=` thành `<` ở đúng một dòng dưới.
    """
    if not (intervalGio > 0):
        raise ValueError(f"intervalGio phải > 0, nhận {intervalGio!r}")
    if giuGio < 0:
        raise ValueError(f"giuGio không được âm, nhận {giuGio!r}")

    buocMs = intervalGio * GIO_MS
    hetMs = nowMs + giuGio * GIO_MS
    uoc = mocKeMs is None

    if uoc:
        # Không biết đồng hồ sàn ở đâu → giả định mốc kế nằm giữa chu kỳ. Đó
        # là kỳ vọng của một lần vào lệnh ngẫu nhiên, không phải một con số
        # đo được. Cờ `uocLuong` đi kèm để tầng trên hạ điểm tin cậy.
        dau = nowMs + buocMs / 2.0
    else:
        dau = float(mocKeMs)
        # Sàn có thể trả về một mốc đã trôi qua (đồng hồ lệch, hoặc dữ liệu
        # cũ). Kéo nó về mốc kế tiếp còn ở phía trước thay vì đếm âm.
        if dau < nowMs:
            thieu = math.ceil((nowMs - dau) / buocMs)
            dau += thieu * buocMs

    if dau > hetMs:
        return LichMoc(0, None, None, (dau - nowMs) / 1000.0, uoc)

    so = int(math.floor((hetMs - dau) / buocMs)) + 1
    cuoi = dau + (so - 1) * buocMs
    return LichMoc(so, int(dau), int(cuoi), (dau - nowMs) / 1000.0, uoc)


def thu_thuc(nowMs: float, giuGio: float, rate: float,
             mocKeMs: int | None, intervalGio: float) -> tuple[float, LichMoc]:
    """Funding thực nhận trên MỘT chân, trong cửa sổ giữ.

    Trả về `(phần_thu, lịch_mốc)`. Dấu theo quy ước ở đầu file: đây là số mà
    một vị thế SHORT nhận được. Chân LONG lấy số âm của nó.
    """
    lich = dem_moc(nowMs, giuGio, mocKeMs, intervalGio)
    return lich.soMoc * rate, lich


def thu_cap(nowMs: float, giuGio: float,
            rateLong: float, mocLongMs: int | None, intervalLongGio: float,
            rateShort: float, mocShortMs: int | None, intervalShortGio: float
            ) -> dict:
    """Funding thực nhận của CẢ CẶP delta-neutral, trong cửa sổ giữ.

    Đây là con số Risk Engine phải dùng, chứ không phải `spread × số giờ`.
    """
    tShort, lichShort = thu_thuc(nowMs, giuGio, rateShort, mocShortMs, intervalShortGio)
    tLong, lichLong = thu_thuc(nowMs, giuGio, rateLong, mocLongMs, intervalLongGio)
    return {
        "thu": tShort - tLong,
        "thuShort": tShort,
        "traLong": tLong,
        "soMocShort": lichShort.soMoc,
        "soMocLong": lichLong.soMoc,
        "choMocDauGiay": _som_hon(lichShort.choMocDauGiay, lichLong.choMocDauGiay),
        "uocLuong": lichShort.uocLuong or lichLong.uocLuong,
    }


def _som_hon(a: float | None, b: float | None) -> float | None:
    if a is None:
        return b
    if b is None:
        return a
    return min(a, b)


def gio_giu_toi_thieu(nowMs: float, mocKeMs: int | None, intervalGio: float) -> float:
    """Phải giữ ít nhất bao nhiêu giờ mới chạm được MỘT mốc kết toán.

    Buồng lái cần con số này để nói thẳng "giữ dưới N giờ thì thu bằng 0"
    thay vì để người vận hành tự suy ra từ một bảng số.
    """
    lich = dem_moc(nowMs, 0.0, mocKeMs, intervalGio)
    return (lich.choMocDauGiay or 0.0) / 3600.0
