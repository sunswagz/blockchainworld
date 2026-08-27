"""BẢNG ĐO TAY — phí rút CEX, thứ duy nhất ở đây không đọc được bằng máy.

Binance `/sapi/v1/capital/config/getall` và OKX `/api/v5/asset/currencies`
đều đòi khoá đã ký (thử ngày 27/08/2026: `-2014` và `50103`). Repo này
không có khoá sàn nào và cố ý không có — nên con số phải tới từ một người
ngồi đọc trang phí rồi gõ vào đây.

Số gõ tay thì có hai cách hỏng, và bảng này chặn cả hai:

1. **Không biết nó tới từ đâu.** Nên mỗi dòng mang `nguon` — đường dẫn
   trang đã đọc — và `ngayDo`.
2. **Nó cũ đi trong im lặng.** Sàn đổi phí rút mà không báo ai. Nên bảng
   có HẠN: quá `HAN_NGAY` thì `tra_cuu()` trả `None`, và `None` chảy lên
   thành "cả tuyến không đo được".

Trả `None` nghe như thua cuộc, nhưng nó đúng: một con số 90 ngày tuổi
trông giống hệt một con số đúng, và không gì trong nó nói rằng nó cũ.
Chuyện này đã cắn ở tầng khác của chính kho này — ghi chú "mỗi bản site
~440 KB" đúng hồi hai cung, sai gấp 50 lần sau khi tách thư mục, và phép
tính hạn mức dựa trên nó sai theo.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass

#: Bao lâu thì một số gõ tay hết đáng tin. 45 ngày là ước lượng, không phải
#: một hằng số của tự nhiên — sàn đổi phí rút vài lần một năm, và chọn quá
#: dài thì bảng nói dối, quá ngắn thì Router mù trong khi số vẫn còn đúng.
HAN_NGAY = 45.0


@dataclass(frozen=True)
class DongPhi:
    """Một dòng: rút tài sản A khỏi sàn S về chuỗi C tốn bao nhiêu."""
    san: str
    taiSan: str
    chuoi: str
    phiUsd: float
    giayCho: float
    nguon: str
    ngayDo: str          # ISO, ngày người đọc trang phí

    def tuoi_ngay(self, homNay: _dt.date | None = None) -> float:
        d = _dt.date.fromisoformat(self.ngayDo)
        return ((homNay or _dt.date.today()) - d).days

    def con_han(self, homNay: _dt.date | None = None) -> bool:
        return self.tuoi_ngay(homNay) <= HAN_NGAY


#: Đo ngày 27/08/2026 từ trang phí công khai của từng sàn. Cột `giayCho` là
#: thời gian rút TỚI KHI VÀO VÍ trong điều kiện bình thường — không phải
#: thời gian sàn hứa, mà là thời gian quan sát được, và nó phồng lên trong
#: lúc mạng tắc.
#:
#: Chỉ ghi những cặp thật sự dùng: ba sàn giao ngay của `san_chung/` và hai
#: stablecoin mà `on_dinh/` xoay. Thêm dòng thì thêm cả `nguon` và `ngayDo`
#: — dòng không có xuất xứ thì `kiem()` từ chối.
BANG: tuple[DongPhi, ...] = (
    DongPhi("binance", "USDT", "ethereum", 1.00, 900.0,
            "binance.com/en/fee/cryptoFee", "2026-08-27"),
    DongPhi("binance", "USDT", "arbitrum", 0.30, 300.0,
            "binance.com/en/fee/cryptoFee", "2026-08-27"),
    DongPhi("binance", "USDC", "ethereum", 1.00, 900.0,
            "binance.com/en/fee/cryptoFee", "2026-08-27"),
    DongPhi("binance", "USDC", "arbitrum", 0.30, 300.0,
            "binance.com/en/fee/cryptoFee", "2026-08-27"),
    DongPhi("okx", "USDT", "ethereum", 1.60, 900.0,
            "okx.com/fees", "2026-08-27"),
    DongPhi("okx", "USDT", "arbitrum", 0.10, 300.0,
            "okx.com/fees", "2026-08-27"),
    DongPhi("okx", "USDC", "ethereum", 1.60, 900.0,
            "okx.com/fees", "2026-08-27"),
    DongPhi("okx", "USDC", "arbitrum", 0.10, 300.0,
            "okx.com/fees", "2026-08-27"),
    DongPhi("bybit", "USDT", "ethereum", 2.00, 900.0,
            "bybit.com/en/help-center/article/Withdrawal-Fee", "2026-08-27"),
    DongPhi("bybit", "USDT", "arbitrum", 0.20, 300.0,
            "bybit.com/en/help-center/article/Withdrawal-Fee", "2026-08-27"),
    DongPhi("bybit", "USDC", "arbitrum", 0.20, 300.0,
            "bybit.com/en/help-center/article/Withdrawal-Fee", "2026-08-27"),
)


def tra_cuu(san: str, taiSan: str, chuoi: str,
            homNay: _dt.date | None = None) -> DongPhi | None:
    """Dòng phí, hoặc `None` khi không có HOẶC đã quá hạn.

    Gộp hai trường hợp vào cùng một `None` là cố ý: với bên gọi thì "chưa
    ai đo" và "đo lâu rồi, không còn tin được" dẫn tới cùng một hành động —
    khai ra là không đo được. Muốn biết là trường hợp nào thì gọi
    `chan_doan()`.
    """
    d = _tim(san, taiSan, chuoi)
    return d if (d is not None and d.con_han(homNay)) else None


def chan_doan(san: str, taiSan: str, chuoi: str,
              homNay: _dt.date | None = None) -> str:
    d = _tim(san, taiSan, chuoi)
    if d is None:
        return f"bảng chưa có dòng nào cho {san}/{taiSan}/{chuoi}"
    if not d.con_han(homNay):
        return (f"dòng {san}/{taiSan}/{chuoi} đo ngày {d.ngayDo}, đã "
                f"{d.tuoi_ngay(homNay):.0f} ngày > hạn {HAN_NGAY:.0f} — "
                f"đọc lại {d.nguon} rồi cập nhật `ngayDo`")
    return "còn hạn"


def _tim(san: str, taiSan: str, chuoi: str) -> DongPhi | None:
    for d in BANG:
        if (d.san == san.lower() and d.taiSan == taiSan.upper()
                and d.chuoi == chuoi.lower()):
            return d
    return None


def chuoi_cua_san(san: str, taiSan: str,
                  homNay: _dt.date | None = None) -> tuple[str, ...]:
    """Những chuỗi sàn này rút được tài sản này về, và dòng còn hạn.

    Dùng làm câu trả lời cho "sàn kia có nhận chuỗi này không". Một sàn rút
    được về chuỗi C thì cũng nạp được từ chuỗi C — chiều ngược lại luôn
    đúng, còn chiều rút mới là chiều bị giới hạn.

    Không có nghĩa là danh sách ĐẦY ĐỦ: bảng chỉ ghi những cặp thật sự
    dùng. Nên nó trả lời được "chắc chắn có", chứ không trả lời được "chắc
    chắn không" — và `dinh_tuyen` phải xử hai câu ấy khác nhau.
    """
    return tuple(sorted({d.chuoi for d in BANG
                         if d.san == san.lower()
                         and d.taiSan == taiSan.upper()
                         and d.con_han(homNay)}))

def kiem() -> list[str]:
    """Bảng có tự mâu thuẫn không. Chạy trong selftest, không cần mạng."""
    loi: list[str] = []
    thay: set[tuple[str, str, str]] = set()
    for d in BANG:
        k = (d.san, d.taiSan, d.chuoi)
        if k in thay:
            loi.append(f"dòng trùng: {k}")
        thay.add(k)
        if not d.nguon or not d.ngayDo:
            loi.append(f"{k} thiếu xuất xứ — số không có nguồn thì không "
                       f"kiểm lại được, và không kiểm lại được thì không "
                       f"sửa được khi sàn đổi phí")
        if d.phiUsd < 0 or d.giayCho <= 0:
            loi.append(f"{k} phí hoặc thời gian vô lý: {d.phiUsd}/{d.giayCho}")
        try:
            _dt.date.fromisoformat(d.ngayDo)
        except ValueError:
            loi.append(f"{k} ngày đo sai khuôn ISO: {d.ngayDo!r}")
    return loi


def tom_tat(homNay: _dt.date | None = None) -> dict:
    con = [d for d in BANG if d.con_han(homNay)]
    return {
        "soDong": len(BANG),
        "soConHan": len(con),
        "soQuaHan": len(BANG) - len(con),
        "hanNgay": HAN_NGAY,
        "tuoiLonNhatNgay": max((d.tuoi_ngay(homNay) for d in BANG), default=0),
        "loiNhac": ("Bảng này gõ tay vì sàn đòi khoá đã ký mới cho đọc phí "
                    "rút. Quá hạn thì Router trả None chứ không trả số cũ."),
    }
