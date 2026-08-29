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
class SoVonGio:
    """VỐN-GIỜ: mẫu số đúng cho câu «tiền đang làm việc lãi bao nhiêu».

    ## Vì sao NAV không trả lời được câu ấy

    Máy demo có 100.000 USD vốn ảo mà chỉ rót được 6.000 — trần vị thế
    chặn phần còn lại. NAV nhích 0,04 USD một vòng, quy ra năm là ~0,4%,
    và con số ấy nói rằng chiến lược gần như vô dụng.

    Nó không vô dụng. 6.000 USD ấy đang chạy ở khoảng 7–8%/năm; 94.000
    còn lại nằm im. Hai câu hoàn toàn khác nhau:

        trên VỐN TỔNG       cỗ máy đang làm ăn ra sao
        trên VỐN ĐANG DÙNG  chiến lược đang làm ăn ra sao

    Gộp chúng làm một thì hoặc ta chê oan chiến lược, hoặc ta khoe một
    tỉ suất mà phần lớn vốn không hề hưởng. Đúng bài học «ba thước trả
    lời ba câu khác nhau» của `danh_muc.py`, đặt lên tầng lợi suất.

    ## Vì sao cộng VỐN-GIỜ chứ không lấy vốn hiện tại

    Vốn đang rót thay đổi từng vòng: mở thêm, đóng bớt, cầu dao ngắt.
    Chia thu nhập của cả tuần cho con số của phút này là chia cho một
    mẫu số chưa từng đúng suốt tuần ấy. Vốn-giờ là mẫu số duy nhất khớp
    với tử số — đúng thứ người cho vay gọi là APR.
    """
    vonGioUsd: float = 0.0       # Σ (vốn đang mở × số giờ nó mở)
    thuRongUsd: float = 0.0      # Σ (thu − phí trong kỳ)
    tuGiay: float = 0.0          # bắt đầu cộng từ lúc nào
    denGiay: float = 0.0         # cộng tới lúc nào
    #: Cùng hai con số ấy, TÁCH THEO TY.
    #:
    #: Tổng gộp trả lời «tiền đang làm việc lãi bao nhiêu» cho cả túi. Nó
    #: KHÔNG trả lời được «ty nào đang làm ra tiền», mà đó mới là câu vòng
    #: tiến hoá cần — và trước lượt này câu ấy chỉ có một nguồn: bảng
    #: hứa-vs-thực, thứ đòi **20 lần ĐÓNG** mỗi ty mới nói được gì. Đóng
    #: thì hiếm; cộng dồn lãi thì mỗi vòng ba mươi giây một lần.
    #:
    #: Nên tách ở đây là đổi một tín hiệu thưa lấy một tín hiệu dày, trên
    #: cùng một phép đo đã có sẵn mẫu số đúng.
    theoTy: dict = field(default_factory=dict)

    def nhip(self, denGiay: float) -> None:
        """Đẩy mốc cuối, kể cả vòng KHÔNG có vị thế nào.

        Vòng rỗng vẫn là một vòng đã sống: nó nằm trong cửa sổ đo, và bỏ nó
        đi là làm mẫu số nhỏ lại đúng bằng những quãng cỗ máy không rót
        được đồng nào — tức là khoe một mức «vốn dùng bình quân» cao hơn
        thật, đúng phần đáng lo nhất.
        """
        self.denGiay = max(self.denGiay, float(denGiay))

    def _o(self, ty: str | None) -> dict:
        return self.theoTy.setdefault(
            ty or "?", {"vonGioUsd": 0.0, "thuRongUsd": 0.0})

    def cong_thu(self, ty: str | None, thuRongUsd: float) -> None:
        """Thu ròng của MỘT ty. Tổng gộp vẫn cộng ở chỗ gọi, không cộng
        hai lần ở đây — một con số cộng hai đường là một con số sẽ lệch."""
        self._o(ty)["thuRongUsd"] += float(thuRongUsd)

    def cong(self, vonUsd: float, tuGiay: float, denGiay: float,
             ty: str | None = None) -> None:
        self.nhip(denGiay)
        dt = max(0.0, denGiay - tuGiay)
        if dt <= 0.0 or vonUsd <= 0.0:
            return
        if ty is not None:
            self._o(ty)["vonGioUsd"] += vonUsd * (dt / 3600.0)
        self.vonGioUsd += vonUsd * dt / 3600.0

    def loi_suat_nam(self) -> float | None:
        """Lợi suất năm trên vốn ĐANG DÙNG, hoặc `None` khi chưa đo nổi.

        `None` chứ không phải 0: chưa có vốn-giờ nào nghĩa là chưa có gì
        để chia, khác hẳn "đã chạy và huề vốn".
        """
        if self.vonGioUsd <= 0.0:
            return None
        return self.thuRongUsd / self.vonGioUsd * (365.0 * 24.0) * 100.0

    def tom_tat(self) -> dict:
        gio = max(0.0, self.denGiay - self.tuGiay) / 3600.0
        apr = self.loi_suat_nam()
        # HAI con số `None` vì HAI lý do khác nhau, và trộn chúng là mất
        # đúng cái phân biệt đang cần: `loiSuatNamPhanTram` thiếu vì chưa có vốn
        # nào làm việc; `vonBinhQuanUsd` thiếu vì cửa sổ đo dài 0 giây.
        return {
            "vonGioUsd": self.vonGioUsd, "thuRongUsd": self.thuRongUsd,
            "soGio": gio,
            "vonBinhQuanUsd": (self.vonGioUsd / gio) if gio > 0 else None,
            "loiSuatNamPhanTram": apr,
            # TÁCH THEO TY — câu «ty nào đang làm ra tiền», trả lời được
            # mỗi vòng thay vì đợi 20 lần đóng. `None` khi ty ấy chưa có
            # vốn-giờ nào: chưa có mẫu số thì không có tỉ suất, không
            # phải tỉ suất bằng 0.
            "theoTy": {
                k: {**v,
                    "loiSuatNamPhanTram": (
                        v["thuRongUsd"] / v["vonGioUsd"] * (365.0 * 24.0)
                        * 100.0 if v["vonGioUsd"] > 0 else None)}
                for k, v in sorted(self.theoTy.items())},
            "vi": ("chưa có vốn-giờ nào — chưa đồng nào làm việc, nên chưa "
                   "có mẫu số để chia" if apr is None else
                   f"vốn đang dùng bình quân "
                   f"{self.vonGioUsd / gio:,.0f} USD suốt {gio:.1f} giờ, thu "
                   f"ròng {self.thuRongUsd:+.4f} USD → {apr:+.2f}%/năm TRÊN "
                   f"PHẦN VỐN ẤY. Đây KHÔNG phải lợi suất của cả gia sản."
                   if gio > 0 else
                   f"{self.vonGioUsd:,.2f} vốn-giờ, thu ròng "
                   f"{self.thuRongUsd:+.4f} USD → {apr:+.2f}%/năm trên phần "
                   f"vốn ấy; cửa sổ đo còn quá ngắn để nói vốn bình quân"),
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
    #: Vòng kế toán nào thu VƯỢT XA mức mà chính tờ trình của nó hứa.
    #:
    #: Trung Ương nhận `thuUsd` từ ty và ghi thẳng vào Sổ Cái, không hỏi
    #: lại. Đó là đúng phân tầng — ty biết việc của ty — nhưng nó để hở
    #: đúng một lớp lỗi: một ty quên chia cho 8.760 (giờ trong năm) sẽ in
    #: ra tiền, NAV phồng lên, và `lechTien` VẪN KHỚP vì sổ ghi đúng con
    #: số bịa ấy. Không phép kiểm nào của cây mã này bắt được chuyện đó.
    #:
    #: Trần dựng từ chính lời hứa của tờ trình (`netUocBps`, `giuGio`)
    #: nhân một biên RỘNG: funding đảo chiều, phí AMM bùng lên — thu cao
    #: hơn hứa vài lần là chuyện thật. Nhân 8.760 lần thì không.
    soThuVuotTran: int = 0
    thuVuotTran: list = field(default_factory=list)
    daDong: list = field(default_factory=list)
    loi: list = field(default_factory=list)

    def tom_tat(self) -> dict:
        return {
            "soViThe": self.soViThe,
            "soKeToanDuoc": self.soKeToanDuoc,
            "soKhongCoKeToan": self.soKhongCoKeToan,
            "soThuVuotTran": self.soThuVuotTran,
            "thuVuotTran": list(self.thuVuotTran)[:5],
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
