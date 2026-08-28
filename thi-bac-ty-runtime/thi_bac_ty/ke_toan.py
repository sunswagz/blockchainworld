"""KẾ TOÁN THEO THỜI GIAN — nửa còn thiếu của cỗ máy.

Trước file này, vòng đời một vị thế dừng ở nửa đầu:

    mở vị thế  →  (không có gì xảy ra nữa, mãi mãi)

Đo được trên máy đang chạy ngày 28/08/2026, và cả ba đều là **đo**, không
phải nhận định:

- `FUNDING`, `PHI`, `TRUOT_GIA` có trong bảng `LOAI` của Sổ Cái mà **không
  dòng mã nào ghi chúng**;
- `DanhMuc.ghi_dong_tien()` — hàm dịch tiền mặt — **không có chỗ nào gọi**;
- `DanhMuc.dong()` gọi ở ĐÚNG MỘT chỗ: đóng gấp khi chân B không khớp.
  Không có đóng theo `giuGio`, không có đóng theo mục tiêu.

Hệ quả: `navUsd` theo cấu tạo là `vốn gốc + tiền mặt`, nên đường NAV phẳng
vì nó là **hằng số theo định nghĩa**. "Lãi 0%" không phải "hoà vốn" — nó là
"chưa bao giờ tính". Và bốn thứ đứng trên đường NAV — sụt vốn, cầu dao
`sut-von`, `hieu_nang`, vòng tiến hoá — đều đang đo một hằng số.

## Luật một: THU phải ĐO ĐƯỢC, không được suy từ dự đoán

Cách dễ nhất, và sai nhất: tờ trình đã khai `netUocBps` và `giuGio`, nên
cộng dồn `netUocBps × (đã giữ / giuGio)` là ra ngay một đường lãi đẹp.
Nhưng đó là **trả lại chính con số máy đã đoán** — cỗ máy sẽ luôn "kiếm
được" đúng bằng thứ nó dự đoán, và đường NAV thành một bản sao của kỳ vọng
chứ không phải của thị trường. `bac/chay_lai.py` đã ghi thẳng luật này:
`thuBps` là DỰ ĐOÁN, `thuThucBps` là ĐO ĐƯỢC, và khoảng cách giữa hai con
số ấy mới là thứ đáng học.

Nên kế toán KHÔNG nằm ở Trung Ương. Trung Ương không biết funding trả theo
mốc hay lãi cho vay cộng liên tục; nó hỏi ty, và ty trả lời bằng dữ liệu
ty vừa quét được trong chính vòng này.

## Luật hai: ty chưa biết kế toán thì phải KHAI, không được ngầm bằng 0

`Ty.ke_toan()` trả `None` mặc định. Trung Ương ĐẾM số vị thế không có kế
toán và bày ra — vì "vị thế này thu 0" và "không ai biết vị thế này thu
bao nhiêu" là hai câu khác hẳn, mà cộng vào NAV thì cả hai đều ra cùng một
con số. Đây là điều `none-khac-khong` trong hiến pháp, áp vào chỗ mới.

## Luật ba: PHÍ thu TRƯỚC, thu nhập cộng SAU

Phí vào lệnh ghi ngay lúc mở, lấy từ `phiUocBps` của chính tờ trình — con
số ty đã dùng để tính `netUocBps`, nên dùng lại nó là nhất quán. Hệ quả cố
ý: một vị thế mở rồi đóng ngay lập tức hiện ra một khoản LỖ đúng bằng phí.
Đó là sự thật, và nó phải xuất hiện trước lãi chứ không phải sau — cỗ máy
nào cũng dễ trông có lãi khi phí được hoãn lại tới cuối.
"""
from __future__ import annotations

from dataclasses import dataclass, field

#: Một năm, tính bằng giây. Lãi cho vay công bố theo năm nên mọi phép quy
#: đổi thời gian đi qua đây — chép 365*24*3600 rải rác là cách chắc chắn
#: để hai chỗ dùng hai con số khác nhau.
NAM_GIAY = 365.0 * 24.0 * 3600.0


@dataclass
class KetToanVong:
    """Một vòng kế toán cho MỘT vị thế, do ty trả lời."""
    #: Dòng tiền thu được trong vòng này. Âm được — funding có thể chảy
    #: ngược, và một cỗ máy chỉ biết cộng là một cỗ máy nói dối một nửa.
    thuUsd: float = 0.0
    #: Phí phát sinh TRONG vòng (không gồm phí vào lệnh — cái đó Trung
    #: Ương thu lúc mở).
    phiUsd: float = 0.0
    #: Câu người đọc hiểu. Bắt buộc khi `thuUsd != 0` — một dòng tiền
    #: không lý do là một con số câm, đúng luật của Sổ Cái.
    vi: str = ""
    #: Ty muốn đóng NGAY, không đợi hết `giuGio`. Dùng khi điều kiện đã
    #: hỏng: chênh lệch đảo dấu, pool cạn, lãi về âm.
    dongLai: bool = False
    lyDoDong: str = ""
    #: `False` = ty biết mình KHÔNG đo được vòng này (mất nguồn, dữ liệu
    #: quá cũ). Khác hẳn `thuUsd = 0`.
    doDuoc: bool = True

    def tom_tat(self) -> dict:
        return {"thuUsd": self.thuUsd, "phiUsd": self.phiUsd, "vi": self.vi,
                "dongLai": self.dongLai, "lyDoDong": self.lyDoDong,
                "doDuoc": self.doDuoc}


@dataclass
class SoViThe:
    """Sổ theo dõi MỘT vị thế đang mở, giữ trong bộ nhớ Trung Ương.

    Không nằm trong `DanhMuc` vì Danh Mục trả lời "đang phơi nhiễm bao
    nhiêu", còn sổ này trả lời "vị thế này đã sống bao lâu và đã cộng dồn
    được gì" — hai câu hỏi khác nhau, và nhét chung là bắt Danh Mục biết
    chuyện thời gian.
    """
    ma: str
    chienLuoc: str
    toTrinh: dict
    vonUsd: float
    moLucGiay: float
    keToanLucGiay: float
    thuCongDonUsd: float = 0.0
    phiCongDonUsd: float = 0.0
    soVongKeToan: int = 0
    soVongKhongDoDuoc: int = 0
    #: `None` = ty của vị thế này chưa cài `ke_toan()`. Không phải 0.
    coKeToan: bool | None = None

    @property
    def giuGio(self) -> float:
        try:
            return float(self.toTrinh.get("giuGio") or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def daGiuGio(self, nowGiay: float) -> float:
        return max(0.0, (nowGiay - self.moLucGiay) / 3600.0)

    def tom_tat(self, nowGiay: float) -> dict:
        return {
            "ma": self.ma, "chienLuoc": self.chienLuoc, "vonUsd": self.vonUsd,
            "daGiuGio": round(self.daGiuGio(nowGiay), 3),
            "giuGio": self.giuGio,
            "thuCongDonUsd": self.thuCongDonUsd,
            "phiCongDonUsd": self.phiCongDonUsd,
            "laiLoUsd": self.thuCongDonUsd - self.phiCongDonUsd,
            "soVongKeToan": self.soVongKeToan,
            "soVongKhongDoDuoc": self.soVongKhongDoDuoc,
            "coKeToan": self.coKeToan,
        }


@dataclass
class LatCatKeToan:
    """Kết quả một lượt kế toán toàn danh mục. Buồng lái đọc chỗ này."""
    soViThe: int = 0
    soKeToanDuoc: int = 0
    #: Vị thế mà TY CỦA NÓ chưa cài `ke_toan()`. Đây là con số phải bày
    #: ra: chúng nằm trong NAV nhưng không ai cộng lãi lỗ cho chúng.
    soKhongCoKeToan: int = 0
    #: Ty có kế toán nhưng vòng này khai KHÔNG đo được.
    soVongMu: int = 0
    #: Vốn nằm trong những vị thế KHÔNG được kế toán. Con số này quan
    #: trọng hơn số đếm: một vị thế 5 USD không ai cộng lãi thì kệ, còn
    #: 5.000 USD thì NAV đang sai một khoản chưa biết bao nhiêu.
    vonKhongDuocKeToanUsd: float = 0.0
    thuUsd: float = 0.0
    phiUsd: float = 0.0
    daDong: list = field(default_factory=list)
    loi: list = field(default_factory=list)

    def tom_tat(self) -> dict:
        return {
            "soViThe": self.soViThe,
            "soKeToanDuoc": self.soKeToanDuoc,
            "soKhongCoKeToan": self.soKhongCoKeToan,
            "soVongMu": self.soVongMu,
            "vonKhongDuocKeToanUsd": self.vonKhongDuocKeToanUsd,
            "thuUsd": self.thuUsd,
            "phiUsd": self.phiUsd,
            "rongUsd": self.thuUsd - self.phiUsd,
            "daDong": list(self.daDong),
            "loi": list(self.loi),
            "vi": _vi(self),
        }


def _vi(l: LatCatKeToan) -> str:
    if not l.soViThe:
        return ("Không vị thế nào đang mở, nên không có gì để kế toán. Đây "
                "là rỗng ĐO ĐƯỢC.")
    c = [f"{l.soViThe} vị thế: thu {l.thuUsd:+.4f} USD, phí {l.phiUsd:.4f}."]
    if l.soKhongCoKeToan:
        c.append(f"{l.soKhongCoKeToan} vị thế KHÔNG có kế toán "
                 f"({l.vonKhongDuocKeToanUsd:.0f} USD) — ty của chúng chưa "
                 f"cài `ke_toan()`, "
                 f"nên lãi lỗ của phần vốn ấy KHÔNG được biết, không phải "
                 f"bằng 0.")
    if l.soVongMu:
        c.append(f"{l.soVongMu} vị thế có kế toán nhưng vòng này ty khai "
                 f"không đo được.")
    if l.daDong:
        c.append(f"Đóng {len(l.daDong)} vị thế.")
    return " ".join(c)


def phi_vao_usd(toTrinh: dict, vonUsd: float) -> float:
    """Phí vào lệnh, lấy từ `phiUocBps` của chính tờ trình.

    Dùng lại đúng con số ty đã dùng để tính `netUocBps`: nếu Trung Ương
    tự bịa một mô hình phí khác thì `netUocBps` trên tờ trình và lãi lỗ
    trên sổ cái sẽ nói hai chuyện, và không ai biết tin cái nào.

    `phiUocBps` thiếu thì trả `0.0` chứ KHÔNG đoán — nhưng người gọi phải
    biết là nó thiếu, nên xem `phi_vao_thieu()`.
    """
    try:
        bps = float(toTrinh.get("phiUocBps"))
    except (TypeError, ValueError):
        return 0.0
    return abs(vonUsd) * bps / 10_000.0


def phi_vao_thieu(toTrinh: dict) -> bool:
    """Tờ trình có khai phí không. Thiếu thì vị thế vào sổ mà KHÔNG mất
    phí — trông có lãi hơn sự thật, nên phải đếm ra."""
    try:
        float(toTrinh.get("phiUocBps"))
    except (TypeError, ValueError):
        return True
    return False
