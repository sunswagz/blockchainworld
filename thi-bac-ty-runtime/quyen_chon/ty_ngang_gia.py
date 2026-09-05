"""Ty NGANG GIÁ — vi phạm ngang giá call/put trên Deribit.

Engine thứ bảy, và nó là engine đầu tiên KHÔNG CẦN MÔ HÌNH nào.

Bốn ty phái sinh/tín dụng hiện có đều phải dự báo một thứ: funding sẽ giữ
nguyên, lãi suất sẽ giữ nguyên, basis sẽ hội tụ. Ngang giá thì không dự báo
gì cả — nó là một ĐẲNG THỨC phải đúng, nếu không thì có tiền để nhặt:

    C − P = (F − K) · e^(−rT)

Vế trái là hai quyền chọn cùng kỳ hạn cùng giá thực hiện; vế phải là hợp
đồng tương lai trừ giá thực hiện, chiết khấu về hiện tại. Không tham số
nào phải ước, không phân phối nào phải giả định. Đẳng thức lệch quá phí thì
edge có thật bất kể thị trường đi đâu.

## Đo thật ngày 27/08/2026, và con số nói hết

    lệch ngang giá ở giá GIỮA        −1,04 bps   (441 cặp BTC)
    bề rộng bid/ask hai chân        +62,00 bps
    lệch ở giá THỰC THI             −29,48 bps

Đọc ba dòng ấy theo thứ tự là hiểu cả engine:

**Ở giá giữa, ngang giá ĐÚNG.** −1 bps trên 441 cặp là nhiễu làm tròn, không
phải cơ hội. Hàng chục bàn tự doanh canh đẳng thức này liên tục, và họ canh
tốt.

**Chênh bid/ask là 62 bps.** Vào vị thế là mua ở ask và bán ở bid, nên ta
mất khoảng một nửa bề rộng ấy trên mỗi chân.

**Nên edge thực thi là −29 bps.** Không phải lỗi công thức — đó chính là
tiền trả cho việc vượt chênh giá. Ty này sẽ từ chối gần như mọi cặp, và đó
là **kết quả đúng**: một ty tìm được nhiều cơ hội ngang giá là một ty đang
tính sai chứ không phải một ty giỏi.

Bản đồ §21 nói đích đúng là **từ chối 95 trên 100**. Ty này từ chối 100
trên 100 — gần cái đích ấy nhất trong cả hệ tính tới lúc viết.

## HỆ SỐ CHIẾT KHẤU HIỆN KHÔNG LÀM GÌ, và phải nói ra

`e^(−rT)` nằm trong công thức vì công thức đúng phải có nó. Nhưng Deribit
trả `interest_rate = 0` cho **cả 1058 hợp đồng** đo được, nên hệ số ấy đang
bằng đúng 1,0 và không đổi con số nào.

Đây là đúng cái bẫy `bac/rui_ro.py` từng cắn — ba cửa khai ra mà `xet()`
không đọc tới — chỉ khác hình dạng: lần này là một thừa số trong công thức
luôn bằng 1. Người đọc thấy `e^(−rT)` thì tưởng đang được che khỏi rủi ro
lãi suất; thực tế là không, và sẽ không, cho tới ngày Deribit công bố một
lãi suất khác 0.

Nên mỗi cơ hội mang `chietKhauCoHieuLuc`, và selftest canh rằng con số ấy
nói đúng sự thật. Giữ công thức mà **khai là nó đang trơ** thì đúng cả hai
đường: đúng khi lãi suất về 0, và đúng khi nó khác 0.

## Hai chỗ khác dễ bịa ra edge

**Dùng giá GIỮA.** Giá giữa không mua được cũng không bán được. Bảng trên
cho thấy khoảng cách giữa hai cách tính là 28 bps — lớn hơn cả ngưỡng chấp
nhận của ty này.

**Quên phí bị CHẶN TRÊN.** Phí quyền chọn Deribit là
`min(0,03% × underlying, 12,5% × phí quyền)`. Với quyền chọn rẻ thì vế thứ
hai chặn, và tính theo vế thứ nhất là báo phí cao gấp nhiều lần rồi từ chối
những cơ hội có thật. Sai theo hướng an toàn vẫn là sai.
"""
from __future__ import annotations

import datetime as _dt
import math
import time
from dataclasses import dataclass, replace

from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.nguon import Nguon, so_hoac_none
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

MA_CHIEN_LUOC = "options.put_call_parity.v1"
HO = "phai-sinh"

#: Ba chân, mỗi chân một cỡ lệnh tối thiểu, và chân tương lai cần ký quỹ.
#: $300 là chỗ cỡ lệnh tối thiểu của Deribit (0,1 BTC quyền chọn) còn nhỏ
#: so với một edge tính bằng bps.
_VON_TOI_THIEU = 300.0

API = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"

PHI_CON_THIEU = (
    "phi-rut-tien",
    "ky-quy-thay-doi-theo-gia",   # chân tương lai bị gọi ký quỹ nếu giá chạy
    "thue",
    "chi-doc-DINH-so-khong-doc-do-sau",
    # Deribit trả interest_rate = 0 nên `e^(−rT)` đang trơ. Rủi ro lãi suất
    # vì thế CHƯA được trừ, dù công thức trông như đã trừ.
    "rui-ro-lai-suat-vi-san-tra-lai-suat-0",
)
SUC_CHUA_CON_THIEU = ("do-sau-ngoai-dinh-so",)

CUA = ("netToiThieuBps", "tuoiToiDaGiay", "oiToiThieu",
       "chenhGiaToiDaPhanTram", "conLaiGioToiThieu")

CONFIG = {
    "quet": {
        "tienTe": ("BTC", "ETH"),
        "hetGioHoiGiay": 20.0,
    },
    "ruiRo": {
        # Cao hơn hẳn ty funding (5 bps): ba chân, ba lần trượt giá, và một
        # sổ lệnh mỏng hơn perp nhiều bậc.
        "netToiThieuBps": 25.0,
        "tuoiToiDaGiay": 60.0,
        # Quyền chọn không ai giữ thì giá yết là giá của người tạo lập duy
        # nhất, và nó không phải giá thị trường.
        "oiToiThieu": 5.0,
        # Chênh bid/ask rộng quá thì "giá" chỉ là một khoảng, không phải một
        # con số — và edge tính trên một khoảng là edge tưởng tượng.
        "chenhGiaToiDaPhanTram": 40.0,
        # Sát đáo hạn thì thanh khoản bốc hơi và ba chân không đóng kịp.
        "conLaiGioToiThieu": 48.0,
    },
    # Deribit: min(0,03% × underlying, 12,5% × phí quyền) MỖI chân quyền
    # chọn; chân tương lai 0,05% taker.
    "phi": {
        "quyenChonPhanUnderlying": 0.0003,
        "quyenChonTranPhanPhiQuyen": 0.125,
        "tuongLaiTaker": 0.0005,
    },
    "von": {"moiCoHoiUsd": 300.0},
    "sucChua": {"phanOi": 0.02, "tranUsd": 20_000.0},
}

NHAN = {
    "net-duoi-nguong": "NET dưới ngưỡng",
    "du-lieu-cu": "dữ liệu quá cũ",
    "oi-qua-mong": "gần như không ai giữ hợp đồng này",
    "chenh-gia-qua-rong": "bid/ask rộng tới mức giá chỉ là một khoảng",
    "sap-dao-han": "quá sát đáo hạn",
    "thieu-so": "thiếu giá hoặc thiếu tham số chiết khấu",
}

THANG = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
         "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def doc_ky_han(ma: str) -> _dt.datetime | None:
    """`BTC-28AUG26-96000-C` → 28/08/2026 08:00 UTC.

    Deribit kết toán lúc 08:00 UTC. Lấy nửa đêm là lệch tám giờ, và tám giờ
    ấy đi thẳng vào hệ số chiết khấu của những kỳ hạn ngắn.
    """
    p = ma.split("-")
    if len(p) != 4:
        return None
    d = p[1]
    # `>= 6` chứ KHÔNG `>= 7`. Deribit KHÔNG đệm số 0 vào ngày: `BTC-5SEP26`
    # là tên thật, dài đúng 6 ký tự ở phần ngày. Cửa `< 7` cũ vứt SẠCH mọi
    # kỳ hạn rơi vào ngày 1–9 — chừng ba mươi phần trăm số ngày đáo hạn —
    # và vứt trong im lặng, vì `None` chảy vào một `continue` không đếm.
    #
    # Không ai thấy suốt nhiều tháng vì phép kiểm dựng kỳ hạn bằng «hôm nay
    # + 30 ngày»: hai mươi mốt ngày mỗi tháng nó cho ngày hai chữ số và
    # xanh, chín ngày còn lại nó đỏ. Nó đỏ đúng hôm 02/09/2026.
    if len(d) < 6:
        return None
    try:
        ngay = int(d[:-5])
        thang = THANG.get(d[-5:-2].upper())
        nam = 2000 + int(d[-2:])
        if thang is None:
            return None
        return _dt.datetime(nam, thang, ngay, 8, 0,
                            tzinfo=_dt.timezone.utc)
    except (ValueError, KeyError):
        return None


def he_so_chiet_khau(laiSuat: float | None, conLaiNam: float) -> float | None:
    """`e^(−rT)`. `None` khi thiếu lãi suất — KHÔNG mặc định 1,0.

    Mặc định 1,0 là ngầm nói lãi suất bằng 0, và với kỳ hạn một năm ở lãi
    suất 5% thì đó là bỏ sót 5% giá trị — lớn gấp trăm lần cái edge ta đi
    tìm.
    """
    if laiSuat is None or conLaiNam < 0:
        return None
    return math.exp(-float(laiSuat) * conLaiNam)


def phi_mot_chan_quyen_chon(phiQuyen: float, underlying: float,
                            c: dict) -> float:
    """Phí MỘT chân quyền chọn, đã áp trần theo phí quyền.

    `min(0,03% × underlying, 12,5% × phí quyền)`. Quên vế thứ hai là báo phí
    cao gấp nhiều lần cho quyền chọn rẻ, rồi từ chối những cơ hội có thật —
    sai theo hướng an toàn vẫn là sai.
    """
    a = float(c["quyenChonPhanUnderlying"]) * underlying
    b = float(c["quyenChonTranPhanPhiQuyen"]) * max(phiQuyen, 0.0)
    return min(a, b)


@dataclass(frozen=True)
class CoHoiNgangGia:
    tienTe: str
    kyHan: str
    giaThucHien: float
    tuongLai: float
    conLaiGio: float
    heSoChietKhau: float
    #: Hệ số chiết khấu có THẬT SỰ đổi con số không, hay đang bằng 1,0.
    #: Deribit trả `interest_rate = 0` cho mọi hợp đồng ở thời điểm đo, nên
    #: hôm nay nó trơ — và một thừa số luôn bằng 1 mà không ai khai ra thì
    #: người đọc tưởng mình được che khỏi rủi ro lãi suất.
    chietKhauCoHieuLuc: bool
    #: Vế trái đo bằng giá THỰC THI, không phải giá giữa.
    veTraiUsd: float
    vePhaiUsd: float
    #: Dương = mua tổng hợp rẻ hơn tương lai; âm = ngược lại.
    lechUsd: float
    huong: str                   # "MUA_TONG_HOP" | "BAN_TONG_HOP"
    grossBps: float
    phiBps: float
    netBps: float
    oiToiThieu: float | None
    chenhGiaPhanTram: float | None
    sucChuaToiDaUsd: float | None
    vonXinUsd: float
    tuoiGiay: float
    duyet: bool = False
    lyDo: tuple = ()
    lyDoMa: tuple = ()

    @property
    def giuGio(self) -> float:
        """Giữ tới ĐÁO HẠN. Ngang giá chỉ đóng chắc chắn tại kết toán —
        đóng sớm là bán lại ba chân trên ba sổ lệnh mỏng."""
        return max(self.conLaiGio, 1.0)

    @property
    def netMoiGioBps(self) -> float:
        return self.netBps / self.giuGio if self.giuGio else 0.0

    def tom_tat(self) -> dict:
        return {"tienTe": self.tienTe, "kyHan": self.kyHan,
                "giaThucHien": self.giaThucHien, "tuongLai": self.tuongLai,
                "conLaiGio": self.conLaiGio,
                "heSoChietKhau": self.heSoChietKhau,
                "chietKhauCoHieuLuc": self.chietKhauCoHieuLuc,
                "veTraiUsd": self.veTraiUsd, "vePhaiUsd": self.vePhaiUsd,
                "lechUsd": self.lechUsd, "huong": self.huong,
                "grossBps": self.grossBps, "phiBps": self.phiBps,
                "netBps": self.netBps, "netMoiGioBps": self.netMoiGioBps,
                "oiToiThieu": self.oiToiThieu,
                "chenhGiaPhanTram": self.chenhGiaPhanTram,
                "sucChuaToiDaUsd": self.sucChuaToiDaUsd,
                "tuoiGiay": self.tuoiGiay, "duyet": self.duyet,
                "lyDo": list(self.lyDo),
                "lyDoMa": [list(x) for x in self.lyDoMa]}


class CongRuiRo:
    def __init__(self, c: dict) -> None:
        self.c = dict(c)

    def xet(self, co: CoHoiNgangGia) -> tuple[bool, list]:
        ly: list = []
        if co.oiToiThieu is None or co.chenhGiaPhanTram is None:
            ly.append(("thieu-so", "sàn không công bố đủ số để cân — thiếu, "
                                   "không phải bằng 0"))
            return False, ly
        if co.netBps < float(self.c["netToiThieuBps"]):
            ly.append(("net-duoi-nguong",
                       f"NET {co.netBps:.1f} bps < "
                       f"{self.c['netToiThieuBps']:.0f}"))
        if co.oiToiThieu < float(self.c["oiToiThieu"]):
            ly.append(("oi-qua-mong",
                       f"OI {co.oiToiThieu:,.1f} < {self.c['oiToiThieu']:,.0f} "
                       f"— giá yết là giá của một người tạo lập, không phải "
                       f"giá thị trường"))
        if co.chenhGiaPhanTram > float(self.c["chenhGiaToiDaPhanTram"]):
            ly.append(("chenh-gia-qua-rong",
                       f"bid/ask rộng {co.chenhGiaPhanTram:.0f}% > "
                       f"{self.c['chenhGiaToiDaPhanTram']:.0f}%"))
        if co.conLaiGio < float(self.c["conLaiGioToiThieu"]):
            ly.append(("sap-dao-han",
                       f"còn {co.conLaiGio:.0f}h < "
                       f"{self.c['conLaiGioToiThieu']:.0f}h"))
        if co.tuoiGiay > float(self.c["tuoiToiDaGiay"]):
            ly.append(("du-lieu-cu", f"dữ liệu cũ {co.tuoiGiay:.0f}s"))
        return (not ly), ly

    def tom_tat(self) -> dict:
        return {k: self.c[k] for k in CUA if k in self.c}


def mot_co_hoi(tienTe: str, kyHan: str, K: float, call: dict, put: dict,
               vonXinUsd: float, phiC: dict, sucChuaC: dict,
               now: _dt.datetime | None = None) -> CoHoiNgangGia | None:
    """Một cặp call/put cùng kỳ hạn cùng giá thực hiện → một cơ hội.

    Giá quyền chọn Deribit yết theo TỶ LỆ underlying, nên nhân lại thành đô
    trước khi so với `F − K`. Quên nhân là so hai con số ở hai đơn vị, và
    kết quả trông như một edge khổng lồ.
    """
    F = so_hoac_none(call.get("underlying_price"))
    r = so_hoac_none(call.get("interest_rate"))
    cb, ca = so_hoac_none(call.get("bid_price")), so_hoac_none(call.get("ask_price"))
    pb, pa = so_hoac_none(put.get("bid_price")), so_hoac_none(put.get("ask_price"))
    if None in (F, cb, ca, pb, pa) or F <= 0 or K <= 0:
        return None

    het = doc_ky_han(f"{tienTe}-{kyHan}-{K:.0f}-C")
    if het is None:
        return None
    bay = now or _dt.datetime.now(_dt.timezone.utc)
    conGio = (het - bay).total_seconds() / 3600.0
    if conGio <= 0:
        return None
    df = he_so_chiet_khau(r, conGio / (365.0 * 24.0))
    if df is None:
        return None

    vePhai = (F - K) * df

    # Hai chiều, và mỗi chiều dùng đúng giá THỰC THI của chiều ấy.
    #   MUA tổng hợp: mua call ở ASK, bán put ở BID
    #   BÁN tổng hợp: bán call ở BID, mua put ở ASK
    muaUsd = (ca - pb) * F
    banUsd = (cb - pa) * F

    # Mua tổng hợp rẻ hơn tương lai → mua tổng hợp, bán tương lai.
    lechMua = vePhai - muaUsd
    # Bán tổng hợp đắt hơn tương lai → bán tổng hợp, mua tương lai.
    lechBan = banUsd - vePhai
    if lechMua >= lechBan:
        huong, veTrai, lech = "MUA_TONG_HOP", muaUsd, lechMua
        phiQuyen = (ca + pb) / 2.0 * F
    else:
        huong, veTrai, lech = "BAN_TONG_HOP", banUsd, lechBan
        phiQuyen = (cb + pa) / 2.0 * F

    phiUsd = (2.0 * phi_mot_chan_quyen_chon(phiQuyen, F, phiC)
              + float(phiC["tuongLaiTaker"]) * F)
    gross = lech / F * 10_000.0
    phiBps = phiUsd / F * 10_000.0

    oi = [so_hoac_none(call.get("open_interest")),
          so_hoac_none(put.get("open_interest"))]
    oiMin = None if None in oi else min(oi)
    chenh = _chenh_phan_tram(cb, ca, pb, pa)
    chua = (None if oiMin is None
            else min(oiMin * F * float(sucChuaC["phanOi"]),
                     float(sucChuaC["tranUsd"])))

    return CoHoiNgangGia(
        tienTe=tienTe, kyHan=kyHan, giaThucHien=K, tuongLai=F,
        conLaiGio=conGio, heSoChietKhau=df,
        chietKhauCoHieuLuc=(abs(df - 1.0) > 1e-9),
        veTraiUsd=veTrai, vePhaiUsd=vePhai, lechUsd=lech, huong=huong,
        grossBps=gross, phiBps=phiBps, netBps=gross - phiBps,
        oiToiThieu=oiMin, chenhGiaPhanTram=chenh,
        sucChuaToiDaUsd=chua, vonXinUsd=vonXinUsd, tuoiGiay=0.0)


def _chenh_phan_tram(cb, ca, pb, pa) -> float | None:
    """Chênh bid/ask RỘNG NHẤT trong hai chân, theo % của giá giữa."""
    ra = []
    for b, a in ((cb, ca), (pb, pa)):
        giua = (b + a) / 2.0
        if giua <= 0:
            return None
        ra.append((a - b) / giua * 100.0)
    return max(ra)


class NguonDeribit(Nguon):
    """Đỉnh sổ toàn bộ chuỗi quyền chọn. CÔNG KHAI, không cần khoá."""

    ten = "deribit-quyen-chon"

    def __init__(self) -> None:
        super().__init__()
        self.theoTienTe: dict = {}

    async def doc(self, client, tienTe=("BTC", "ETH")) -> list[dict]:
        t0 = time.perf_counter()
        ra: list[dict] = []
        for tt in tienTe:
            try:
                r = await client.get(API, params={"currency": tt,
                                                  "kind": "option"})
                r.raise_for_status()
                ds = (r.json() or {}).get("result") or []
                for x in ds:
                    x["_tienTe"] = tt
                ra.extend(ds)
                self.theoTienTe[tt] = f"ok · {len(ds)}"
            except Exception as e:                            # noqa: BLE001
                self.theoTienTe[tt] = f"{type(e).__name__}"
        if ra:
            self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        else:
            self.suc_khoe.ghi_loi(RuntimeError("không tiền tệ nào trả lời"))
        return ra

    def tom_tat(self) -> dict:
        return {**self.suc_khoe.tom_tat(), "theoTienTe": dict(self.theoTienTe)}


def ghep_cap(ds: list[dict]) -> dict:
    """Gom theo `(tiền tệ, kỳ hạn, giá thực hiện)`, mỗi khoá một cặp C/P.

    Thiếu một vế thì BỎ, không đoán vế kia. Ngang giá là đẳng thức ba chân;
    hai chân không nói được gì.
    """
    cap: dict = {}
    for x in ds:
        p = str(x.get("instrument_name") or "").split("-")
        if len(p) != 4 or p[3] not in ("C", "P"):
            continue
        K = so_hoac_none(p[2])
        if K is None:
            continue
        cap.setdefault((x.get("_tienTe") or p[0], p[1], K), {})[p[3]] = x
    return {k: v for k, v in cap.items() if "C" in v and "P" in v}


def tim_co_hoi(ds: list[dict], vonXinUsd: float, phiC: dict, sucChuaC: dict,
               cong, now=None, boDem: dict | None = None) -> list:
    """Cặp nào KHÔNG dựng nổi một cơ hội thì ĐẾM ra, đừng `continue` suông.

    Bản trước bỏ qua im lặng, và cái im lặng ấy giấu một con bọ thật suốt
    nhiều tháng: `doc_ky_han` từ chối mọi kỳ hạn ngày 1–9 (Deribit không
    đệm số 0), nên chừng ba mươi phần trăm số ngày đáo hạn biến mất khỏi
    danh sách cơ hội. Không lỗi nào ném, không dòng nào kêu — chỉ là ty
    này thấy ít cơ hội hơn thật, và "ít cơ hội" trông y hệt "chợ hôm nay
    không có gì".

    `boDem` là một dict tuỳ chọn; truyền vào thì nó nhận `soCapBoQua` và
    `capBoQua` (tối đa tám mã, đủ để lần ra khuôn chung mà không phình
    ảnh chụp).
    """
    ra = []
    bo = []
    for (tt, kyHan, K), v in ghep_cap(ds).items():
        co = mot_co_hoi(tt, kyHan, K, v["C"], v["P"], vonXinUsd, phiC,
                        sucChuaC, now)
        if co is None:
            bo.append(f"{tt}-{kyHan}-{K:.0f}")
            continue
        qua, ly = cong.xet(co)
        ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                          lyDo=tuple(c for _, c in ly)))
    if boDem is not None:
        boDem["soCapBoQua"] = len(bo)
        boDem["capBoQua"] = sorted(bo)[:8]
    ra.sort(key=lambda c: -c.netMoiGioBps)
    return ra


def _chay(coro):
    """Chạy một coroutine kể cả khi đã có vòng lặp đang chạy."""
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures as _cf
    with _cf.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


class TyNgangGia(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("vi phạm ngang giá call/put trên Deribit — KHÔNG mô hình nào, "
            "chỉ một đẳng thức phải đúng")

    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, client_factory=None) -> None:
        super().__init__()
        self.nguon = NguonDeribit()
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.coHoi: list = []
        self._boDem: dict = {}
        self._cf = client_factory

    def quet(self) -> list:
        ds = _chay(self._doc())
        self._boDem = {}
        self.coHoi = tim_co_hoi(ds, float(CONFIG["von"]["moiCoHoiUsd"]),
                                CONFIG["phi"], CONFIG["sucChua"], self.cong,
                                boDem=self._boDem)
        return list(self.coHoi)

    async def _doc(self):
        import httpx
        q = CONFIG["quet"]
        lam = self._cf or (lambda: httpx.AsyncClient(
            timeout=float(q["hetGioHoiGiay"]),
            headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}))
        async with lam() as c:
            return await self.nguon.doc(c, q["tienTe"])

    def xet(self, co):
        return bool(co.duyet), list(co.lyDoMa or ())

    # ── kế toán: ngang giá ĐÓNG CHẮC CHẮN tại đáo hạn, không trước ───────
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """Ngang giá khoá một khoản chênh và giữ tới KẾT TOÁN.

        Không có dòng tiền lúc giữ — ba chân nằm im, và cái đổi chỉ là giá
        của chúng. Nên `thuUsd` là **0 ĐO ĐƯỢC** suốt thời gian giữ, cùng
        lối với ty chênh stablecoin.

        Khác ở chỗ ĐÓNG, và khác vì một lý do đã ghi sẵn trong
        `CoHoiNgangGia.giuGio`: *"đóng sớm là bán lại ba chân trên ba sổ
        lệnh mỏng"*. Nên ty này **không** đóng khi chênh hội tụ — nó giữ
        tới đáo hạn, lúc ấy quan hệ ngang giá đúng theo định nghĩa và
        khoản chênh đã khoá thành hiện thực.

        Ngày đáo hạn tới thì trả về đúng khoản đã khoá LÚC MỞ, đọc từ tờ
        trình. Không đọc `lechUsd` của lượt quét mới: chênh hôm nay là
        chênh cho người vào hôm nay, còn vị thế này đã chốt giá của mình
        rồi — cùng luật với Pendle PT.
        """
        from thi_bac_ty.ke_toan import KetToanVong

        tien = toTrinh.get("taiSan")
        c = next((x for x in self.coHoi if x.tienTe == tien), None)
        con = c.conLaiGio if c is not None else None
        von = sum(abs(float(getattr(x, "vonUsd", 0.0) or 0.0))
                  for x in viThe)
        vi = (f"ngang giá {tien}: giữ tới đáo hạn"
              + (f", còn {con:.1f}h" if con is not None else
                 " (lượt quét gần nhất KHÔNG có hợp đồng nào của mã này)")
              + ". Không dòng tiền lúc giữ — ba chân nằm im, chỉ giá đổi")

        if con is None or con > 0.0:
            return KetToanVong(thuUsd=0.0, vi=vi)

        try:
            net = float(toTrinh["netUocBps"])
        except (KeyError, TypeError, ValueError):
            return KetToanVong(
                doDuoc=False,
                vi="tờ trình thiếu `netUocBps` nên không dựng lại được "
                   "khoản đã khoá lúc mở — không đoán")
        return KetToanVong(
            thuUsd=von * net / 10_000.0, dongLai=True,
            lyDoDong=f"đã tới đáo hạn — ngang giá đóng tại kết toán, khoản "
                     f"chênh {net:+.2f} bps khoá lúc mở nay thành hiện thực",
            vi=vi)

    def trinh(self, co):
        return xuat_to_trinh(co)

    def tom_tat(self) -> dict:
        # `soCapBoQua` là cặp call/put ghép được nhưng KHÔNG dựng nổi một
        # cơ hội. Nó phải lên ảnh chụp: một con số 0 ở đây nói "mọi cặp
        # đều đọc được", còn một con số lớn nói "có cả một họ mã đang
        # rơi khỏi bảng" — hai câu ấy trước nay trông giống hệt nhau.
        return {"nguon": self.nguon.tom_tat(), "cua": self.cong.tom_tat(),
                "soCoHoi": len(self.coHoi),
                "soQua": sum(1 for c in self.coHoi if c.duyet),
                "soCapBoQua": self._boDem.get("soCapBoQua"),
                "capBoQua": self._boDem.get("capBoQua"),
                "phanBoNet": _phan_bo_net(self.coHoi,
                                          float(self.cong.c["netToiThieuBps"]))}


def _phan_bo_net(coHoi, nguongBps: float) -> dict:
    """NET và GROSS nằm ở đâu so với ngưỡng — không chỉ đếm bao nhiêu trượt.

    Một bảng lý do chỉ nói «net dưới ngưỡng: 2.989» đọc như «sát mà chưa
    đủ». Đo làn thật 05/09/2026 thì không: net trung vị **−39,7 bps** trên
    ngưỡng **+25** — cách nhau 65 bps, tức không phải chuyện vặn ngưỡng.
    Và GROSS (trước phí) cũng âm ở CẢ 747 cơ hội, cao nhất −4,35 bps.
    
    Gross âm toàn bộ KHÔNG phải lỗi dấu: `muaUsd` dùng ask-call/bid-put,
    `banUsd` dùng bid-call/ask-put, nên khi ngang giá đúng ở giá giữa thì
    `banUsd < vePhai < muaUsd` và cả hai chiều đều âm. Đó là spread ăn
    hết, và nó là câu trả lời ĐÚNG — chỉ là trước nay không ai đọc được
    nó từ một con số đếm.

    Trả `None` cho mọi vị trí khi chưa có mẫu: 0 ở đây đọc thành «ngang
    giá đúng khít», một câu dữ liệu không hề nói.
    """
    # Phép đo này nay là MỘT chỗ dùng chung: `thi_bac_ty.khoang_nguong`.
    # Ba ty hỏi cùng một câu «khối bị loại nằm sát ngưỡng hay xa hẳn», và
    # ba bản chép là ba chỗ sẽ lệch.
    from thi_bac_ty.khoang_nguong import vi_tri as _vitri

    net = [c.netBps for c in coHoi if c.netBps is not None]
    return {
        "nguongBps": nguongBps,
        "net": _vitri(net),
        "gross": _vitri([c.grossBps for c in coHoi
                         if c.grossBps is not None]),
        "phi": _vitri([c.phiBps for c in coHoi if c.phiBps is not None]),
        # Khoảng cách từ cơ hội TỐT NHẤT tới ngưỡng. Đây mới là con số nói
        # «vặn ngưỡng có mở được gì không».
        "cachNguongBps": (round(nguongBps - max(net), 2) if net else None),
        "soDatNguong": sum(1 for x in net if x >= nguongBps),
    }


def _rui_ro(co) -> RuiRo:
    """Ngang giá KHOÁ được kết quả — nên rủi ro thị trường thấp, nhưng ba
    chân trên một sàn duy nhất thì rủi ro cảng và thực thi cao."""
    return RuiRo(
        # Đã khoá: mọi đường giá đều cho cùng một kết quả tại kết toán.
        thiTruong=0.10,
        thanhKhoan=0.55,   # sổ quyền chọn mỏng hơn perp nhiều bậc
        giaoThuc=0.20,
        cang=0.50,         # MỘT sàn giữ cả ba chân
        thucThi=0.55,      # ba chân phải khớp gần như cùng lúc
        cauNoi=0.0,
    )


def _tin_cay(co) -> float:
    d = 1.0
    if co.oiToiThieu is None:
        d -= 0.35
    elif co.oiToiThieu < 50.0:
        d -= 0.15
    if co.chenhGiaPhanTram is None:
        d -= 0.25
    elif co.chenhGiaPhanTram > 15.0:
        d -= 0.15
    # Kỳ hạn càng xa, hệ số chiết khấu càng nhạy với lãi suất sàn công bố —
    # và lãi suất ấy là con số của Deribit, không phải của thị trường.
    if co.conLaiGio > 24.0 * 180.0:
        d -= 0.15
    return max(0.0, min(1.0, d))


def xuat_to_trinh(co) -> ToTrinh:
    v = co.vonXinUsd / 3.0
    if co.huong == "MUA_TONG_HOP":
        chan = (Chan("LONG", "deribit", f"{co.tienTe}-{co.kyHan}-C", v, "option"),
                Chan("SHORT", "deribit", f"{co.tienTe}-{co.kyHan}-P", v, "option"),
                Chan("SHORT", "deribit", f"{co.tienTe}-{co.kyHan}-F", v, "perp"))
    else:
        chan = (Chan("SHORT", "deribit", f"{co.tienTe}-{co.kyHan}-C", v, "option"),
                Chan("LONG", "deribit", f"{co.tienTe}-{co.kyHan}-P", v, "option"),
                Chan("LONG", "deribit", f"{co.tienTe}-{co.kyHan}-F", v, "perp"))
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=co.tienTe,
        chan=chan,
        vonCanUsd=co.vonXinUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=co.sucChuaToiDaUsd,
        grossBps=co.grossBps, phiUocBps=co.phiBps, netUocBps=co.netBps,
        giuGio=co.giuGio,
        # Đóng sớm được, nhưng là bán lại BA chân trên ba sổ mỏng. Ngang giá
        # chỉ đóng CHẮC CHẮN tại kết toán, nên khoá vốn = thời gian còn lại.
        khoaVonDenGio=co.conLaiGio * 3600.0,
        thanhKhoanThoatUsd=co.sucChuaToiDaUsd,
        ruiRo=_rui_ro(co),
        tuoiDuLieuGiay=co.tuoiGiay,
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False, phiConThieu=PHI_CON_THIEU,
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang="USD",
        cang=("deribit",),
        bangChung=(
            f"{co.tienTe} {co.kyHan} K={co.giaThucHien:,.0f} · {co.huong}",
            f"C-P (gia THUC THI) = ${co.veTraiUsd:,.2f} · (F-K)e^(-rT) = "
            f"${co.vePhaiUsd:,.2f} -> lech ${co.lechUsd:,.2f}",
            (f"he so chiet khau {co.heSoChietKhau:.6f} tren "
             f"{co.conLaiGio:,.0f} gio"
             if co.chietKhauCoHieuLuc else
             f"he so chiet khau = 1,0 — san dang tra interest_rate = 0, nen "
             f"thua so nay HIEN KHONG doi con so nao. Giu trong cong thuc vi "
             f"cong thuc dung phai co no; khai ra vi mot thua so luon bang 1 "
             f"ma khong ai noi thi nguoi doc tuong minh duoc che"),
            f"gross {co.grossBps:.1f} - phi {co.phiBps:.1f} = NET "
            f"{co.netBps:.1f} bps (2 chan quyen chon co TRAN phi + 1 chan "
            f"tuong lai taker)",
            "KHONG mo hinh nao: khong uoc bien dong, khong gia dinh phan "
            "phoi. Dang thuc lech qua phi thi edge co that bat ke gia di dau.",
        ))
