"""Ty TIÊN ĐOÁN — cơ hội Polymarket, do Khâm Thiên Giám định giá.

Adapter mỏng. Nó KHÔNG định giá lại: `fairValue`, `netEdge`, `batDinhMoHinh`
đều do cỗ máy kia tính, và viết lại chúng ở đây là dựng cỗ máy thứ ba dưới
một cái tên khác. Việc của file này chỉ là **dịch** — từ ngôn ngữ của kham
sang `ToTrinh`, thứ tiếng chung mà Rủi Ro Tổng đọc được.

## Ba phép đổi đơn vị, và cả ba đều phải khai ra

Kham đo bằng **đô mỗi cổ** trên thang xác suất 0–1. Thị Bạc Ty đo bằng
**bps trên vốn**. Đổi qua lại là chỗ dễ nhân nhầm nhất trong cả file:

    netEdge = 0,05  và  vwap = 0,42
        → mỗi cổ tốn 0,42 đô, ăn 0,05 đô
        → 0,05 / 0,42 = 11,9%  = 1.190 bps

Chia cho `vwap` chứ không cho 1,0: vốn bỏ ra là GIÁ, không phải mệnh giá.
Chia cho 1,0 thì một cơ hội ở giá 0,10 bị báo thấp đi mười lần, và những cơ
hội rẻ nhất — đúng chỗ edge hay nằm — biến mất khỏi bảng xếp hạng.

## `giuGio` là nửa đời, và đó là PROXY

Vị thế Polymarket sống tới khi market kết toán, có thể vài giờ hoặc vài
tháng. Kham đo `nuaDoiMs` — nửa đời của chính cái edge ấy, tức là bao lâu
thì lợi thế mòn đi một nửa. Đó không phải thời gian giữ, nhưng nó là thứ
gần nhất đo được, và nó đúng chiều: edge mòn nhanh thì phải vào nhanh.

Khai `giu-gio-la-nua-doi-khong-phai-ky-han` trong `phiConThieu` để không ai
đọc `netMoiGioBps` của ty này như đọc của ty funding.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

MA_CHIEN_LUOC = "prediction.polymarket.v1"
HO = "tien-doan"

#: Cỗ máy kia có ví riêng và cỡ lệnh riêng. $50 là chỗ phí gas Polygon và
#: phần vụn không khớp còn nhỏ so với một edge tính bằng phần trăm.
_VON_TOI_THIEU = 50.0

URL = "http://127.0.0.1:5186/api/trang-thai"
HET_GIO_GIAY = 4.0

#: Thứ ty này KHÔNG trừ được, và ba khoản đầu là của chính cỗ máy kia.
PHI_CON_THIEU = (
    "gas-polygon-vao-ra",
    "truot-gia-ngoai-do-sau-da-do",
    "thue",
    "giu-gio-la-nua-doi-khong-phai-ky-han",
)
SUC_CHUA_CON_THIEU = ("do-sau-so-lenh-ngoai-muoi-hai-muc",)

CUA = ("netToiThieuBps", "batDinhToiDaMoHinh", "xacSuatKhopToiThieu",
       "sucChuaToiThieuUsd", "tuoiToiDaGiay")

CONFIG = {
    "url": URL,
    "ruiRo": {
        # Rộng hơn ngưỡng của chính kham (`netEdgeToiThieu`) là vô nghĩa —
        # cơ hội nào kham đã loại thì không tới đây. Ngưỡng này chặn thêm ở
        # tầng Thị Bạc Ty, nơi so ty này với BỐN ty khác.
        "netToiThieuBps": 200.0,
        # `batDinhMoHinh` là chính kham nói "tôi không chắc". Một cơ hội
        # 2.000 bps mà bất định 0,08 đô mỗi cổ trên giá 0,42 là edge nằm
        # trong sai số của chính mô hình.
        "batDinhToiDaMoHinh": 0.35,
        "xacSuatKhopToiThieu": 0.30,
        "sucChuaToiThieuUsd": 25.0,
        "tuoiToiDaGiay": 120.0,
    },
}

NHAN = {
    "net-duoi-nguong": "NET dưới ngưỡng",
    "bat-dinh-qua-lon": "bất định mô hình nuốt hết edge",
    "kho-khop": "xác suất khớp quá thấp",
    "suc-chua-qua-nho": "sức chứa quá nhỏ",
    "du-lieu-cu": "lát cắt cỗ máy kia quá cũ",
    "thieu-so": "thiếu giá hoặc thiếu sức chứa",
}


def net_bps(netEdge, vwap) -> float | None:
    """Đô mỗi cổ → bps trên vốn. `None` khi thiếu một trong hai.

    Vốn bỏ ra là GIÁ mỗi cổ, không phải mệnh giá $1.
    """
    if netEdge is None or vwap is None:
        return None
    try:
        v = float(vwap)
        if v <= 0.0 or v > 1.0:
            return None
        return float(netEdge) / v * 10_000.0
    except (TypeError, ValueError):
        return None


class DocKham:
    """Đọc lát cắt cỗ máy kia. KHÔNG import, KHÔNG đặt lệnh, chỉ đọc."""

    def __init__(self, url: str = URL) -> None:
        self.url = url
        self.docDuoc = False
        self.vi = ""
        self.lucMs = 0.0
        self.soLoi = 0

    def doc(self) -> dict:
        try:
            rq = urllib.request.Request(
                self.url, headers={"User-Agent": "thi-bac-ty/0.1 (read-only)"})
            with urllib.request.urlopen(rq, timeout=HET_GIO_GIAY) as r:
                d = json.load(r)
            self.docDuoc, self.vi = True, ""
            self.lucMs = time.time() * 1000.0
            return d if isinstance(d, dict) else {}
        except (urllib.error.URLError, OSError, ValueError) as e:
            self.docDuoc = False
            self.soLoi += 1
            self.vi = f"{type(e).__name__}: {str(e)[:90]}"
            return {}

    def tuoi_giay(self) -> float | None:
        if self.lucMs <= 0:
            return None
        return (time.time() * 1000.0 - self.lucMs) / 1000.0

    def tom_tat(self) -> dict:
        return {"url": self.url, "docDuoc": self.docDuoc, "vi": self.vi,
                "soLoi": self.soLoi, "tuoiGiay": self.tuoi_giay()}


class CongRuiRo:
    """Cổng ty. Mọi khoá khai trong `CUA` đều phải được `xet()` đọc tới —
    hợp đồng ấy do selftest canh, và ba cửa giả trong `bac/rui_ro.py` là
    lý do nó tồn tại."""

    def __init__(self, c: dict) -> None:
        self.c = dict(c)

    def xet(self, co: dict) -> tuple[bool, list]:
        ly: list = []
        net = co.get("_netBps")
        if net is None or co.get("sucChua") is None:
            ly.append(("thieu-so", "thiếu giá hoặc thiếu sức chứa — cỗ máy "
                                   "kia chưa đo xong, không phải bằng 0"))
            return False, ly
        if net < float(self.c["netToiThieuBps"]):
            ly.append(("net-duoi-nguong",
                       f"NET {net:.0f} bps < {self.c['netToiThieuBps']:.0f}"))
        bd = co.get("batDinh")
        if bd is not None and float(bd) > float(self.c["batDinhToiDaMoHinh"]):
            ly.append(("bat-dinh-qua-lon",
                       f"bất định mô hình {float(bd):.3f} > "
                       f"{self.c['batDinhToiDaMoHinh']:.2f} — chính cỗ máy "
                       f"định giá đang nói nó không chắc"))
        xs = co.get("xacSuatKhop")
        if xs is not None and float(xs) < float(self.c["xacSuatKhopToiThieu"]):
            ly.append(("kho-khop", f"xác suất khớp {float(xs):.2f} < "
                                   f"{self.c['xacSuatKhopToiThieu']:.2f}"))
        if float(co.get("sucChua") or 0.0) < float(self.c["sucChuaToiThieuUsd"]):
            ly.append(("suc-chua-qua-nho",
                       f"sức chứa ${float(co.get('sucChua') or 0):,.0f} < "
                       f"${self.c['sucChuaToiThieuUsd']:,.0f}"))
        t = co.get("_tuoiGiay")
        if t is not None and t > float(self.c["tuoiToiDaGiay"]):
            ly.append(("du-lieu-cu", f"lát cắt cũ {t:.0f}s > "
                                     f"{self.c['tuoiToiDaGiay']:.0f}s"))
        return (not ly), ly

    def tom_tat(self) -> dict:
        return {k: self.c[k] for k in CUA if k in self.c}


class TyTienDoan(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("thị trường tiên đoán Polymarket — định giá do Khâm Thiên Giám "
            "tính, ty này chỉ DỊCH sang tờ trình, không định giá lại")

    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, url: str | None = None) -> None:
        super().__init__()
        self.doc = DocKham(url or CONFIG["url"])
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.coHoi: list = []
        self.boQua = {"dangLam": 0, "khongDichDuoc": 0}

    def quet(self) -> list:
        d = self.doc.doc()
        self.boQua = {"dangLam": 0, "khongDichDuoc": 0}
        ra = []
        tuoi = self._tuoi_lat_cat(d)
        for c in (d.get("coHoi") or []):
            # RANH GIỚI ĐẾM: cỗ máy kia đã lấy thì `von_ngoai` đếm rồi.
            # Nộp tờ trình cho nó nữa là đếm cùng một vị thế hai lần.
            if c.get("dangLam"):
                self.boQua["dangLam"] += 1
                continue
            net = net_bps(c.get("net"), c.get("vwap"))
            if net is None:
                self.boQua["khongDichDuoc"] += 1
                continue
            co = dict(c)
            co["_netBps"] = net
            co["_grossBps"] = net_bps(c.get("gross"), c.get("vwap"))
            co["_phiBps"] = net_bps(c.get("phi"), c.get("vwap"))
            co["_tuoiGiay"] = tuoi
            qua, ly = self.cong.xet(co)
            co["_duyet"], co["_lyDoMa"] = qua, ly
            ra.append(co)
        ra.sort(key=lambda x: -(x.get("_netBps") or 0.0))
        self.coHoi = ra
        return list(ra)

    @staticmethod
    def _tuoi_lat_cat(d: dict) -> float | None:
        """Tuổi lát cắt theo đồng hồ của CHÍNH cỗ máy kia nếu nó công bố.

        Không có thì `None` — và `None` chảy vào cửa `tuoiToiDaGiay`, nơi
        nó KHÔNG chặn. Đó là lựa chọn có chủ ý và nó đáng ngờ: xem
        `phiConThieu` khai `tuoi-lat-cat-khong-doc-duoc`.
        """
        v = d.get("chayDuocGiay")
        return float(v) if isinstance(v, (int, float)) else None

    def xet(self, co):
        return bool(co.get("_duyet")), list(co.get("_lyDoMa") or ())

    def trinh(self, co) -> ToTrinh:
        return xuat_to_trinh(co)

    # ── kế toán: BIẾT cách, nhưng chưa đo được từ đây ────────────────────
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """Ty này khai `doDuoc=False` chứ KHÔNG trả `None`, và khác biệt
        ấy là cả nội dung của hàm.

        `None` nghĩa là *"ty chưa biết tự kế toán"* — một món nợ kỹ thuật.
        `doDuoc=False` nghĩa là *"biết cách, nhưng vòng này không đo
        được"* — một sự thật về thế giới. Ở đây là vế thứ hai, và trộn hai
        vế lại là biến một chuyện của đường mạng thành một chuyện của mã.

        Vì sao chưa đo được: thị trường tiên đoán kết toán một lần, ăn
        thua tại thời điểm ấy, và **con số kết toán nằm ở Polymarket**.
        Máy này không với tới được — đường mạng chặn `*.polymarket.com` ở
        tầng TLS (bắt tay TCP xong mới bị giết, 5/5 lần; Binance vẫn 200).
        Đó là *không làm được từ đây*, khác hẳn *chưa làm*.

        Và **không được lấy kết toán từ `nhap_so_ngoai`** để lấp chỗ này:
        sổ ngoài mang kết toán của những vị thế CỖ MÁY KIA đang giữ, còn
        đây là vị thế Thị Bạc Ty tự mở trên những cơ hội cỗ máy kia BỎ
        QUA (`dangLam=False` — xem ranh giới đếm ở `quet()`). Hai tập rời
        nhau; ghép chúng là gán kết quả của người khác cho mình.

        Ngày đường mạng mở lại, chỗ cần sửa là ở đây: đọc trạng thái kết
        toán của chính `conditionId` mà tờ trình đã ghi.
        """
        from thi_bac_ty.ke_toan import KetToanVong

        return KetToanVong(
            doDuoc=False,
            vi="tiên đoán Polymarket: kết toán nằm ở Polymarket, và đường "
               "mạng máy này CHẶN `*.polymarket.com` ở tầng TLS. Không đo "
               "được từ đây — khác hẳn thu bằng 0. Không lấy kết toán của "
               "cỗ máy kia để lấp: hai tập vị thế rời nhau.")

    def tom_tat(self) -> dict:
        return {"doc": self.doc.tom_tat(), "cua": self.cong.tom_tat(),
                "soCoHoi": len(self.coHoi), "boQua": dict(self.boQua),
                "loiNhac": ("Cơ hội cỗ máy kia ĐANG LÀM bị bỏ qua có chủ ý — "
                            "chúng đã được đếm là vốn ngoài trong Danh Mục. "
                            "Nộp tờ trình cho chúng nữa là đếm hai lần.")}


def _rui_ro(co: dict) -> RuiRo:
    """Sáu mặt, đúng sáu mặt `MAT_RUI_RO` khai — không bịa mặt thứ bảy.

    `batDinhMoHinh` của kham KHÔNG có mặt riêng để trú, và đó là một khoảng
    trống thật của hợp đồng: sáu mặt hiện có đo rủi ro của THẾ GIỚI, không
    đo rủi ro của việc CHÍNH TA nhìn sai thế giới.

    Thay vì thêm mặt thứ bảy cho một ty duy nhất — sáu mặt kia đã có mười
    lăm chỗ đọc, và mặt thứ bảy sẽ là `None` ở cả năm ty cũ — nó được cộng
    vào `thiTruong`: mô hình sai bao nhiêu thì giá đi ngược ta bấy nhiêu, và
    hệ quả không phân biệt được với một cú biến động thật.
    """
    bd = float(co.get("batDinh") or 0.0)
    return RuiRo(
        # kết toán NHỊ PHÂN: thắng đủ hoặc mất đủ, không có nửa chừng
        thiTruong=min(1.0, 0.30 + bd * 2.0),
        thanhKhoan=0.45,    # sổ lệnh mỏng, thoát sớm là chịu trượt
        giaoThuc=0.35,      # hợp đồng Polymarket trên Polygon
        cang=0.55,          # MỘT sàn duy nhất, và nó giữ tiền
        thucThi=0.35,       # cỗ máy kia tự đặt lệnh, ta chỉ nhìn
        cauNoi=0.0,         # không bắc cầu
    )


def _tin_cay(co: dict) -> float:
    """Bắt đầu 1,0 rồi TRỪ, cùng lối bốn ty kia."""
    d = 1.0
    bd = co.get("batDinh")
    if bd is None:
        d -= 0.35
    else:
        d -= min(0.40, float(bd) * 1.5)
    if co.get("sucChua") is None:
        d -= 0.30
    if co.get("_tuoiGiay") is None:
        # Không đo được tuổi lát cắt thì ta không biết mình đang nhìn bao
        # giờ. Cửa `tuoiToiDaGiay` không chặn được, nên độ tin phải trừ.
        d -= 0.20
    if not co.get("maker"):
        d -= 0.05
    return max(0.0, min(1.0, d))


def _ten_tai_san(co: dict) -> str:
    """`<market>:<UP|DOWN>` — hai token khác nhau, hai tên khác nhau."""
    ma = str(co.get("ma") or "?")
    ben = str(co.get("ben") or "?").upper()
    return f"{ma}:{ben}"


def xuat_to_trinh(co: dict) -> ToTrinh:
    von = max(_VON_TOI_THIEU, float(co.get("sucChua") or _VON_TOI_THIEU))
    von = min(von, 500.0)
    nuaDoiGio = (float(co["nuaDoiMs"]) / 3_600_000.0
                 if co.get("nuaDoiMs") else 24.0)
    thieu = PHI_CON_THIEU
    if co.get("_tuoiGiay") is None:
        thieu = thieu + ("tuoi-lat-cat-khong-doc-duoc",)
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=_ten_tai_san(co),
        # LUÔN là LONG, và đó không phải chỗ đơn giản hoá.
        #
        # Trên Polymarket ta MUA cổ phần của một kết quả; UP và DOWN là hai
        # token khác nhau, và mua DOWN không phải bán khống UP — nó là mua
        # dài một thứ khác. Nhét UP/DOWN vào `ben` là nói dối `_dau_van()`
        # của Trung Ương: nó gộp `LONG@polymarket` với `SHORT@polymarket`
        # thành hai vị thế đối nhau, trong khi thật ra chúng là hai vị thế
        # CÙNG chiều trên hai tài sản.
        #
        # Nên UP/DOWN thuộc về TÊN TÀI SẢN, và `_dau_van()` phân biệt được.
        chan=(Chan("LONG", "polymarket", _ten_tai_san(co), von,
                   "prediction", "Polygon"),),
        vonCanUsd=von,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=(float(co["sucChua"])
                         if co.get("sucChua") is not None else None),
        grossBps=(co.get("_grossBps") or 0.0),
        phiUocBps=(co.get("_phiBps") or 0.0),
        netUocBps=(co.get("_netBps") or 0.0),
        giuGio=max(0.25, nuaDoiGio),
        # Bán lại trước kết toán được, nên KHÔNG khoá theo hợp đồng — nhưng
        # bán lại là chịu trượt trên một sổ lệnh mỏng, và điều đó nằm ở
        # `thanhKhoanThoatUsd` chứ không ở đây.
        khoaVonDenGiay=0.0,
        thanhKhoanThoatUsd=(float(co["sucChua"])
                            if co.get("sucChua") is not None else None),
        ruiRo=_rui_ro(co),
        tuoiDuLieuGiay=(co.get("_tuoiGiay") if co.get("_tuoiGiay") is not None
                        else 0.0),
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False, phiConThieu=thieu,
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang="USDC",
        cang=("polymarket",), chuoi=("Polygon",),
        bangChung=(
            f"{_ten_tai_san(co)} · chiến thuật "
            f"{co.get('ct') or '?'}",
            f"fair {co.get('fair')} vs vwap {co.get('vwap')} → NET "
            f"{(co.get('_netBps') or 0):,.0f} bps trên vốn",
            f"bất định mô hình {co.get('batDinh')} đô mỗi cổ — do CHÍNH cỗ "
            f"máy định giá khai, không phải ta suy ra",
            "ĐỊNH GIÁ KHÔNG PHẢI CỦA TY NÀY. Khâm Thiên Giám tính; ty này "
            "chỉ dịch sang tờ trình để Rủi Ro Tổng nhìn thấy.",
            "Cơ hội cỗ máy kia ĐANG LÀM không đi qua đây — chúng đã là vốn "
            "ngoài trong Danh Mục, nộp lần nữa là đếm hai lần.",
        ))
