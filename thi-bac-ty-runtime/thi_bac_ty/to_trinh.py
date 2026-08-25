"""TỜ TRÌNH — hợp đồng cơ hội, "đồng tiền ngôn ngữ" của Thị Bạc Ty.

Mọi ty nói với trung ương bằng **đúng một kiểu dữ liệu**: `ToTrinh`. Tên gọi
theo đúng việc nó làm — một ty phát hiện cơ hội thì **trình** lên, còn quyền
duyệt và chia vốn nằm ở trung ương.

Bản kế hoạch gọi kiểu này là `Opportunity`; ở đây đặt là `ToTrinh` vì cả repo
dùng tên tiếng Việt, và vì `CoHoi` đã có nghĩa khác:

    bac.models.CoHoi   thứ ty TỰ TÌM RA — nội bộ, đầy thuật ngữ funding
    ToTrinh            thứ ty TRÌNH LÊN — chung, mọi ty đều hiểu

Hai thứ khác nhau về mục đích. `CoHoi` có `soMocLong`, `intervalShortGio` —
những từ mà ty Tín Dụng hay ty Thanh Lý không hiểu và không cần hiểu.

## Ba luật của hợp đồng này

**1. KHÔNG BIẾT phải khác KHÔNG.** Mọi trường có thể chưa đo được đều nhận
`None`, không nhận `0`. Ty không đánh giá nổi rủi ro cầu nối thì ghi `None`;
ghi `0` là nói "đã đo, và bằng không" — rồi Rủi Ro Tổng cộng một đống số 0
lại và kết luận mọi thứ an toàn.

**2. Con số chưa đủ mô hình phải TỰ KHAI.** `moHinhPhiDuChua` và
`moHinhSucChuaDuChua` không phải trang trí. Khi trung ương xếp hạng:

    perp.funding_spread   18 bps   ← chặn trên, thiếu bốn khoản phí
    credit.lending_rate   11 bps   ← đã trừ đủ

kết luận "cái đầu tốt hơn" là kết luận SAI rút ra từ hai con số không cùng
đơn vị. Cỗ máy sẽ tự đánh lừa mình bằng số liệu của chính mình.

**3. Hợp đồng tự soát mình.** `kiem()` chạy được không cần mạng, không cần
trung ương. Một tờ trình sai khuôn phải chết **ở cửa ty**, không phải trôi
vào sổ đăng ký rồi làm hỏng thống kê ba tháng sau.

## Vì sao có `vonCanUsd` VÀ `sucChuaToiDaUsd`

Đây là hai câu hỏi khác nhau, và người phân bổ vốn cần cả hai:

    vonCanUsd         ty XIN bao nhiêu
    sucChuaToiDaUsd   rót thêm tới đâu thì chính cơ hội ấy tự giết mình

Thiếu cái thứ hai thì trung ương có $10.000 nhàn rỗi sẽ rót cả vào cơ hội
tốt nhất, và trượt giá ăn sạch biên trước khi vào xong lệnh. Sức chứa là
thuộc tính của THỊ TRƯỜNG, không phải của ty — nhưng chỉ ty mới đo được nó,
nên nó nằm trong tờ trình.
"""
from __future__ import annotations

import datetime as _dt
import re
import uuid
from dataclasses import dataclass, field

#: Khuôn mã chiến lược: `<họ>.<tên>.v<số>`. Ép khuôn ngay ở hợp đồng vì mã này
#: sẽ nằm trong mọi bản ghi lịch sử — sai khuôn một lần là lệch vĩnh viễn.
KHUON_CHIEN_LUOC = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+\.v\d+$")

#: Bảy họ, theo đúng bảng phân loại lại mười ba thread. Một ty mới phải thuộc
#: một trong bảy họ này, hoặc phải thêm họ ở ĐÂY trước — không tự khai họ lạ.
HO = (
    "phai-sinh",     # Perpetual · Basis · Options
    "tin-dung",      # Lending · Yield
    "chenh-lech",    # DEX · Stablecoin
    "thanh-khoan",   # LP · JIT MM · Uniswap v4
    "thanh-ly",      # Liquidation
    "mev",           # Search · Execution
    "cau-noi",       # Cross-chain router
)

#: Sáu mặt rủi ro mà Rủi Ro Tổng biết cộng lại. Ty nào không đo được mặt nào
#: thì để `None` — xem luật 1.
MAT_RUI_RO = ("thiTruong", "thanhKhoan", "giaoThuc", "cang", "thucThi", "cauNoi")

BEN = ("LONG", "SHORT", "CHO_VAY", "DI_VAY", "CAP_THANH_KHOAN")


def bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class Chan:
    """Một chân của vị thế. Điều Phối Thực Thi sau này đọc đúng kiểu này.

    Tách chân ra khỏi tờ trình là điều kiện để có delta-neutral thật: một cơ
    hội hai chân mà chỉ khớp một chân thì không phải "lãi ít hơn", nó là một
    vị thế MỘT CHIỀU — loại rủi ro hoàn toàn khác với thứ ty vừa trình lên.
    """
    ben: str
    cang: str
    taiSan: str
    vonUsd: float | None = None
    loai: str = "perp"          # perp · spot · lending · lp · option …
    chuoi: str | None = None    # None với sàn tập trung

    def tom_tat(self) -> dict:
        return {"ben": self.ben, "cang": self.cang, "taiSan": self.taiSan,
                "vonUsd": self.vonUsd, "loai": self.loai, "chuoi": self.chuoi}


@dataclass(frozen=True)
class RuiRo:
    """Sáu mặt rủi ro, thang [0, 1]. `None` = CHƯA ĐO ĐƯỢC, không phải 0."""
    thiTruong: float | None = None
    thanhKhoan: float | None = None
    giaoThuc: float | None = None
    cang: float | None = None
    thucThi: float | None = None
    cauNoi: float | None = None

    def chua_do(self) -> tuple[str, ...]:
        return tuple(m for m in MAT_RUI_RO if getattr(self, m) is None)

    def cao_nhat(self) -> float | None:
        """Mặt rủi ro nặng nhất trong những mặt ĐÃ đo.

        Lấy max chứ không lấy trung bình: rủi ro không bù trừ cho nhau. Một
        cơ hội an toàn năm mặt và chết ở mặt thứ sáu vẫn là một cơ hội chết,
        còn trung bình sẽ làm nó trông êm.
        """
        co = [getattr(self, m) for m in MAT_RUI_RO if getattr(self, m) is not None]
        return max(co) if co else None

    def tom_tat(self) -> dict:
        return {**{m: getattr(self, m) for m in MAT_RUI_RO},
                "chuaDo": list(self.chua_do()), "caoNhat": self.cao_nhat()}


@dataclass(frozen=True)
class ToTrinh:
    """Một cơ hội, viết bằng ngôn ngữ mọi ty đều hiểu."""

    # ── ai trình, về cái gì ──────────────────────────────────────────────
    chienLuoc: str                      # "perpetual.funding_spread.v1"
    ho: str                             # một trong HO
    taiSan: str                         # "BTC"
    chan: tuple[Chan, ...]

    # ── vốn ──────────────────────────────────────────────────────────────
    vonCanUsd: float                    # ty XIN bao nhiêu
    sucChuaToiDaUsd: float | None       # None = chưa đo được sức chứa

    # ── lợi ──────────────────────────────────────────────────────────────
    grossBps: float
    phiUocBps: float
    netUocBps: float
    giuGio: float

    # ── rủi ro và độ tin ─────────────────────────────────────────────────
    ruiRo: RuiRo = field(default_factory=RuiRo)
    tuoiDuLieuGiay: float | None = None
    tinCay: float | None = None         # [0,1] — None = không tự chấm được

    # ── lời khai về mô hình. Mặc định là CHƯA ĐỦ, có chủ ý ───────────────
    moHinhPhiDuChua: bool = False
    phiConThieu: tuple[str, ...] = ()
    moHinhSucChuaDuChua: bool = False
    sucChuaConThieu: tuple[str, ...] = ()

    # ── truy nguyên ──────────────────────────────────────────────────────
    dinhGiaBang: str = "USDT"
    cang: tuple[str, ...] = ()
    chuoi: tuple[str, ...] = ()
    bangChung: tuple[str, ...] = ()
    ma: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    luc: str = field(default_factory=bay_gio)

    # ── soát ─────────────────────────────────────────────────────────────
    def kiem(self) -> list[str]:
        """Trả về danh sách chỗ SAI KHUÔN. Rỗng là hợp lệ.

        Không ném: một tờ trình sai khuôn là chuyện của ty gửi, và trung ương
        cần **đếm** được có bao nhiêu tờ sai chứ không phải chết theo tờ đầu
        tiên. Ty nào gửi sai thì hiện tên nó trong thống kê.
        """
        loi = []
        if not KHUON_CHIEN_LUOC.match(self.chienLuoc or ""):
            loi.append(f"mã chiến lược {self.chienLuoc!r} sai khuôn "
                       f"<họ>.<tên>.v<số>")
        if self.ho not in HO:
            loi.append(f"họ {self.ho!r} không có trong {HO}")
        if not self.taiSan:
            loi.append("thiếu tài sản")
        if not self.chan:
            loi.append("không có chân nào — một cơ hội phải nói rõ nó vào đâu")
        for i, c in enumerate(self.chan):
            if c.ben not in BEN:
                loi.append(f"chân {i}: bên {c.ben!r} không hợp lệ")
            if not c.cang:
                loi.append(f"chân {i}: thiếu cảng")
        if not (self.vonCanUsd > 0):
            loi.append(f"vốn xin phải > 0, đang là {self.vonCanUsd}")
        if self.sucChuaToiDaUsd is not None and self.sucChuaToiDaUsd < self.vonCanUsd:
            loi.append(f"xin {self.vonCanUsd} nhưng sức chứa chỉ "
                       f"{self.sucChuaToiDaUsd} — xin nhiều hơn chỗ chứa")
        if not (self.giuGio > 0):
            loi.append(f"cửa sổ giữ phải > 0, đang là {self.giuGio}")

        # Luật 2: chưa đủ mô hình thì phải nói THIẾU GÌ. Một cờ `False` mà
        # danh sách rỗng là khai nửa vời — người đọc biết nó thiếu mà không
        # biết thiếu gì, nên không cân được với tờ trình của ty khác.
        if not self.moHinhPhiDuChua and not self.phiConThieu:
            loi.append("moHinhPhiDuChua=False mà không kê khoản nào còn thiếu")
        if self.moHinhPhiDuChua and self.phiConThieu:
            loi.append("moHinhPhiDuChua=True mà vẫn kê khoản thiếu")
        if not self.moHinhSucChuaDuChua and not self.sucChuaConThieu:
            loi.append("moHinhSucChuaDuChua=False mà không kê thiếu gì")

        for m in MAT_RUI_RO:
            v = getattr(self.ruiRo, m)
            if v is not None and not (0.0 <= v <= 1.0):
                loi.append(f"rủi ro {m}={v} ngoài thang [0,1]")
        if self.tinCay is not None and not (0.0 <= self.tinCay <= 1.0):
            loi.append(f"tinCay={self.tinCay} ngoài thang [0,1]")
        return loi

    @property
    def hop_le(self) -> bool:
        return not self.kiem()

    @property
    def net_moi_gio_bps(self) -> float:
        """NET quy về mỗi giờ giữ vốn — thước SO SÁNH giữa các ty.

        Không so `netUocBps` trần được: một cơ hội 20 bps giữ 24 giờ thua một
        cơ hội 6 bps giữ 2 giờ, vì vốn quay được mười hai lượt. Đây là chỗ
        `giuGio` thôi làm một con số trang trí.

        Vẫn CHƯA phải thước cuối cùng: nó chưa xét sức chứa (rót được bao
        nhiêu) và chưa xét rủi ro. Người phân bổ vốn phải nhìn cả ba.
        """
        return self.netUocBps / self.giuGio if self.giuGio else 0.0

    def tom_tat(self) -> dict:
        return {
            "ma": self.ma, "luc": self.luc,
            "chienLuoc": self.chienLuoc, "ho": self.ho,
            "taiSan": self.taiSan, "dinhGiaBang": self.dinhGiaBang,
            "cang": list(self.cang), "chuoi": list(self.chuoi),
            "chan": [c.tom_tat() for c in self.chan],
            "vonCanUsd": self.vonCanUsd,
            "sucChuaToiDaUsd": self.sucChuaToiDaUsd,
            "grossBps": self.grossBps, "phiUocBps": self.phiUocBps,
            "netUocBps": self.netUocBps, "netMoiGioBps": self.net_moi_gio_bps,
            "giuGio": self.giuGio,
            "ruiRo": self.ruiRo.tom_tat(),
            "tuoiDuLieuGiay": self.tuoiDuLieuGiay, "tinCay": self.tinCay,
            "moHinhPhiDuChua": self.moHinhPhiDuChua,
            "phiConThieu": list(self.phiConThieu),
            "moHinhSucChuaDuChua": self.moHinhSucChuaDuChua,
            "sucChuaConThieu": list(self.sucChuaConThieu),
            "bangChung": list(self.bangChung),
            "hopLe": self.hop_le, "loiKhuon": self.kiem(),
        }
