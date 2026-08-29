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

#: TÁM họ, theo đúng bảng phân loại lại mười ba thread. Một ty mới phải thuộc
#: một trong tám họ này, hoặc phải thêm họ ở ĐÂY trước — không tự khai họ lạ.
#:
#: `tien-doan` là họ thứ tám, thêm ngày 27/08/2026 cho adapter Khâm Thiên
#: Giám. Nó KHÔNG nhét vừa bảy họ cũ: thị trường tiên đoán không phải phái
#: sinh (không có tài sản cơ sở để phái sinh từ đó), không phải chênh lệch
#: (không có hai nơi để so), không phải tín dụng. Nhét bừa vào `chenh-lech`
#: cho khỏi phải sửa hợp đồng thì `_pheu_theo_ho()` gộp nó với chênh lệch
#: stablecoin, và cái phễu ấy nói dối về cả hai.
HO = (
    "phai-sinh",     # Perpetual · Basis · Options
    "tin-dung",      # Lending · Yield
    "chenh-lech",    # DEX · Stablecoin
    "thanh-khoan",   # LP · JIT MM · Uniswap v4
    "thanh-ly",      # Liquidation
    "mev",           # Search · Execution
    "cau-noi",       # Cross-chain router
    "tien-doan",     # Polymarket — kết toán NHỊ PHÂN, không có giá cơ sở
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


def xin_theo_suc_chua(vonSanUsd: float, sucChuaToiDaUsd: float | None,
                      phan: float = 0.5,
                      tranUsd: float = 25_000.0) -> float:
    """Cỡ vốn NÊN XIN, theo sức chứa của chính cơ hội ấy.

    ## Vì sao không xin một con số cứng

    Đo trên máy sống 29/08/2026, sau khi nâng vốn ảo lên một triệu: máy
    vẫn chỉ rót được **6.200 USD**, tỉ lệ dùng vốn 0,62%. Không phải vì
    hết tiền (còn 797.000 khả dụng), không phải vì trần vị thế (120 chỗ,
    mới dùng 14) — mà vì **mỗi ty xin cứng 500 USD**. Vốn không chạm được
    thị trường vì không ai xin nó.

    Xin cứng còn sai theo cả hai chiều: 500 USD vào một pool chứa nổi
    25.000 là bỏ phí, mà 500 USD vào một pool chứa 600 lại là quá tay.
    Sức chứa là con số duy nhất biết pool ấy nuốt được bao nhiêu.

    ## Vì sao chỉ một PHẦN sức chứa

    Xin trọn sức chứa nghĩa là **ta chính là sức chứa** — và lúc ấy con số
    ấy không còn đúng nữa, vì nó được tính cho một thị trường chưa có ta
    trong đó. Một nửa là chỗ đứng thận trọng.

    ## Sàn và trần

    SÀN là `vonSanUsd` — cỡ mà mọi con số bps của tờ trình được tính ở đó.
    Không bao giờ xin ít hơn sàn, vì dưới sàn thì phí cố định ăn hết.

    TRẦN chặn một sức chứa sai đơn vị biến thành một lời xin vô nghĩa —
    cùng lý do với `TRAN_USD` trong `bac/suc_chua.py`.

    `None` sức chứa → xin đúng sàn. Không biết pool nuốt được bao nhiêu
    thì xin nhỏ nhất, chứ không đoán.
    """
    san = max(0.0, float(vonSanUsd))
    # `<= 0` và `< 0` cho cùng kết quả: sức chứa đúng bằng 0 đi tiếp thì
    # `max(san, min(tran, 0)) == san`, y hệt nhánh này. Con đột biến ấy
    # TƯƠNG ĐƯƠNG — ghi lại để lượt quét sau khỏi đi tìm phép kiểm không
    # tồn tại. Cái đáng kiểm là «sức chứa 0 thì xin đúng SÀN», và phép
    # kiểm ấy đã có.
    if sucChuaToiDaUsd is None or sucChuaToiDaUsd <= 0:
        return san
    return max(san, min(float(tranUsd),
                        float(sucChuaToiDaUsd) * float(phan)))


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
    # ── vốn bị giữ bao lâu, và có rút ra được không ──────────────────────
    #
    # Hai trường này KHÔNG suy ra được từ `giuGio`, và lẫn chúng với nhau là
    # một cách để người phân bổ quyết định sai:
    #
    #   `giuGio`            DỰ ĐỊNH giữ bao lâu. Một vị thế funding giữ 8 giờ
    #                       nhưng thoát được bất cứ lúc nào.
    #   `khoaVonDenGio`    BUỘC phải giữ bao lâu. Một PT Pendle 90 ngày thì
    #                       không có cách nào ra sớm, dù thị trường đổi.
    #   `thanhKhoanThoatUsd` RA được bao nhiêu. Vào được $100.000 không có
    #                       nghĩa là ra được $100.000.
    #
    # `0.0` khác `None`: 0 là "rút được ngay, đã kiểm"; None là "chưa biết".
    # Coi None thành 0 là thưởng cho sự mù — đúng lỗi mà cả hợp đồng này
    # sinh ra để chặn.
    khoaVonDenGio: float | None = None
    thanhKhoanThoatUsd: float | None = None

    # ── dưới ngần này thì kinh tế của cơ hội không còn nghĩa ─────────────
    #
    # KHÔNG phải sàn chung `phanBo.toiThieuMotLanUsd`. Sàn chung nói "rót ít
    # hơn ngần này thì phí cố định của HỆ ăn hết". Trường này nói một chuyện
    # riêng của từng engine:
    #
    #   cho vay Ethereum  gas khứ hồi $12 → dưới ~$5.000 thì gas > 24 bps
    #   chênh stablecoin  edge vài bps    → dưới ~$500 thì phí taker ăn hết
    #   funding perp      cỡ lệnh tối thiểu của sàn
    #
    # $25 đủ cho cái thứ hai mà không đủ cho cái thứ nhất. Một sàn chung
    # không phân biệt được, nên nó hoặc quá lỏng cho engine đắt, hoặc quá
    # chặt cho engine rẻ.
    #
    # `None` = ty chưa khai. Rủi Ro Tổng coi đó là CHƯA ĐO, không phải là 0.
    vonToiThieuKinhTeUsd: float | None = None

    ruiRo: RuiRo = field(default_factory=RuiRo)
    tuoiDuLieuGiay: float | None = None
    tinCay: float | None = None         # [0,1] — không tự chấm được thì None

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
        if self.khoaVonDenGio is not None and self.khoaVonDenGio < 0:
            loi.append(f"khoá vốn {self.khoaVonDenGio} giờ — không âm được")
        if self.thanhKhoanThoatUsd is not None and self.thanhKhoanThoatUsd < 0:
            loi.append(f"thanh khoản thoát {self.thanhKhoanThoatUsd} — không âm được")
        if (self.vonToiThieuKinhTeUsd is not None
                and self.vonCanUsd < self.vonToiThieuKinhTeUsd - 1e-9):
            loi.append(
                f"xin {self.vonCanUsd} nhưng tự khai cần tối thiểu "
                f"{self.vonToiThieuKinhTeUsd} mới kinh tế — tờ trình tự mâu "
                f"thuẫn. Ty phải hoặc xin đủ, hoặc hạ ngưỡng nó khai; để "
                f"trung ương gỡ hộ là bắt trung ương biết chi phí của ngành")
        if self.vonToiThieuKinhTeUsd is not None and self.vonToiThieuKinhTeUsd <= 0:
            loi.append(f"vốn tối thiểu kinh tế {self.vonToiThieuKinhTeUsd} "
                       f"phải > 0 — khai 0 nghĩa là 'engine này kinh tế ở "
                       f"mọi cỡ vốn', và chưa engine nào như thế")

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

    @property
    def gio_von_bi_giu(self) -> float:
        """Vốn thực sự nằm ngoài tầm tay bao nhiêu giờ.

        Là chỗ lớn hơn giữa *định giữ* và *buộc phải giữ*. Một cơ hội định
        giữ 8 giờ mà khoá 90 ngày thì vốn bị giữ 90 ngày, không phải 8 giờ —
        và người phân bổ phải thấy con số 90 ngày ấy chứ không thấy con số 8.

        `khoaVonDenGio = None` (chưa biết) thì trả về `giuGio`, và chỗ phạt
        cho sự chưa-biết nằm ở `phan_bo.diem()` chứ không ở đây: hàm này chỉ
        báo cáo, không phán xét.
        """
        if self.khoaVonDenGio is None:
            return self.giuGio
        return max(self.giuGio, self.khoaVonDenGio)

    @property
    def raDuocKhong(self) -> bool | None:
        """Ra được hết phần vốn XIN không. `None` = chưa đo thanh khoản thoát."""
        if self.thanhKhoanThoatUsd is None:
            return None
        return self.thanhKhoanThoatUsd + 1e-9 >= self.vonCanUsd

    def tom_tat(self) -> dict:
        return {
            "ma": self.ma, "luc": self.luc,
            "chienLuoc": self.chienLuoc, "ho": self.ho,
            "taiSan": self.taiSan, "dinhGiaBang": self.dinhGiaBang,
            "cang": list(self.cang), "chuoi": list(self.chuoi),
            "chan": [c.tom_tat() for c in self.chan],
            "vonCanUsd": self.vonCanUsd,
            "sucChuaToiDaUsd": self.sucChuaToiDaUsd,
            "khoaVonDenGio": self.khoaVonDenGio,
            "vonToiThieuKinhTeUsd": self.vonToiThieuKinhTeUsd,
            "thanhKhoanThoatUsd": self.thanhKhoanThoatUsd,
            "gioVonBiGiu": self.gio_von_bi_giu,
            "raDuocKhong": self.raDuocKhong,
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
