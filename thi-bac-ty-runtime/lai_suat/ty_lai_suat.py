"""TY LÃI SUẤT — Pendle PT. Lãi CỐ ĐỊNH, khoá tới ngày đáo hạn.

Cùng họ `tin-dung` với ty cho vay, nhưng cơ chế ngược nhau ở đúng chỗ đáng
kể nhất:

    tin_dung   lãi THẢ NỔI, rút được bất cứ lúc nào (còn thanh khoản)
    lai_suat   lãi CỐ ĐỊNH, khoá tới ngày đáo hạn

Đó là lý do ty này đáng dựng: nó là ty đầu tiên dùng `khoaVonDenGio` với
một con số THẬT khác 0. Trước nó, trường ấy tồn tại trong hợp đồng mà chưa
ai chứng minh nó có tác dụng.

## Hệ quả thấy ngay, và nó ĐÚNG

Một PT đáo hạn sau 57 ngày sẽ bị `rui_ro_tong.khoaVonToiDaGio` (mặc định
720 giờ = 30 ngày) **TỪ CHỐI**, dù lãi 8%/năm nghe rất ổn. Không phải vì
8% là xấu, mà vì khoá vốn 57 ngày là từ chối mọi cơ hội tốt hơn xuất hiện
trong 57 ngày ấy — và chi phí đó không nằm trong con số 8%.

Người vận hành thấy được đúng đánh đổi ấy và tự quyết có nới trần không.
Đó là việc của người, không phải của máy.

## PT chứ không phải LP

DefiLlama trả cả hai dạng cho mỗi thị trường Pendle:

    "For buying PT-sUSDe-22OCT2026"   ← lãi cố định, ta lấy
    "For LP | Maturity 22OCT2026"     ← có tổn thất tạm thời, ta BỎ

LP là chuyện của thread #8 (Automated LP) và nó có hệ toán khác hẳn. Lẫn
hai thứ vào nhau là bịa ra một con số không mô tả cái nào.

## Bán sớm được, nhưng ta KHÔNG BIẾT giá

PT bán lại được trên AMM của Pendle trước đáo hạn — nhưng ở giá nào thì
nguồn này không nói. Nên `thanhKhoanThoatUsd = None`: chưa đo được, chứ
không phải bằng 0 và cũng không phải bằng TVL.
"""
from __future__ import annotations

import asyncio
import datetime as _dt
import re
import time
from dataclasses import dataclass, field, replace

from chuoi_chung.thang import rui_ro_tvl
from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.nguon import Nguon, so_hoac_none
from thi_bac_ty.to_trinh import (Chan, RuiRo, ToTrinh,
                             xin_theo_suc_chua)

MA_CHIEN_LUOC = "yield.pendle_pt.v1"
HO = "tin-dung"
DUONG = "https://yields.llama.fi/pools"

CONFIG = {
    "quet": {
        "chuoi": ["Ethereum", "Arbitrum", "Base", "Optimism", "Mantle"],
        "hetGioHoiGiay": 30.0,
    },
    "ruiRo": {
        "tvlToiThieuUsd": 3_000_000.0,
        "apyToiThieuPhanTram": 3.0,
        "apyToiDaPhanTram": 60.0,
        # Còn dưới ngần này giờ tới đáo hạn thì phần lãi còn lại quá nhỏ so
        # với phí vào — và rủi ro thao tác không giảm theo.
        "conLaiToiThieuGio": 72.0,
        "tuoiToiDaGiay": 900.0,
    },
    # Xin ĐÚNG bằng ngưỡng kinh tế: mua PT là một lượt swap có trượt
    # giá, và vốn khoá tới đáo hạn — xin ít hơn là tự mâu thuẫn.
    #: `moiCoHoiUsd` là SÀN — cỡ dùng để tính mọi con số bps. Cỡ XIN thì
    #: theo SỨC CHỨA của chính thị trường ấy: xin cứng 1.000 vào một PT
    #: chứa nổi 50.000 là bỏ phí. Xem `to_trinh.xin_theo_suc_chua`.
    "von": {"moiCoHoiUsd": 1000.0, "phanSucChuaXin": 0.5,
            "tranMotLanUsd": 50_000.0},
    "sucChua": {"phanTvl": 0.01, "tranUsd": 50_000.0},
}

PHI_CON_THIEU = ("gas-vao-ra", "truot-gia-tren-amm-pendle",
                 "chuyen-von-giua-chuoi", "thue")

#: Hai khoản Router trả lời được. `truot-gia-tren-amm-pendle` thì KHÔNG —
#: nó đòi đường cong AMM của chính Pendle, thứ không nguồn công khai nào
#: cho, và nó ở lại khai báo dù Router có đo được mọi thứ khác.
ROUTER_GO_DUOC = ("gas-vao-ra", "chuyen-von-giua-chuoi")


def _phi_con_thieu(daDo: bool, routerConThieu: tuple = ()) -> tuple:
    """Khai báo thiếu của MỘT cơ hội — cùng lối `on_dinh` và `tin_dung`."""
    if not daDo:
        return PHI_CON_THIEU
    return (tuple(x for x in PHI_CON_THIEU if x not in ROUTER_GO_DUOC)
            + tuple(f"router:{x}" for x in routerConThieu))


#: Tài sản DÙNG ĐỂ BẮC CẦU. Không phải token PT.
#:
#: Bản nháp đầu bắc cầu chính `t.taiSan` — `SKAITO`, `STRCX`, `SUSD3` — và
#: Router trả `None` cho tất cả, đúng như nó phải làm: không cầu nào chuyển
#: một token PT của Pendle. Nhưng cái sai nằm ở MÔ HÌNH, không ở Router:
#: vào một vị thế PT là mang **stablecoin** sang chuỗi ấy rồi mới swap trên
#: AMM Pendle. Token PT sinh ra TẠI CHỖ và chết tại chỗ.
#:
#: Nó lộ ra vì Router im lặng đúng chỗ đáng im — nếu nó chịu bịa một con số
#: cho `SKAITO` thì lỗi mô hình này đã trôi qua mà không ai thấy.
TAI_SAN_BAC_CAU = "USDC"


def phi_vao_ra(chuoi: str, taiSan: str, vonUsd: float,
               dinhTuyen=None) -> tuple:
    """(usd, giây, thứ-chưa-tính) để vào vị thế trên chuỗi này rồi ra.

    Hai khoản, và cả hai nhân đôi vì vốn phải quay về:

        gas swap trên AMM Pendle   ×2  (vào rồi ra)
        bắc cầu USDC TỪ NHÀ        ×2  (sang rồi về)

    `taiSan` nhận vào chỉ để ghi nhật ký — thứ thật sự đi qua cầu là
    `TAI_SAN_BAC_CAU`, xem ghi chú ở trên.

    Chuỗi không có trong bản đồ Router — `Mantle` chẳng hạn — thì trả `None`
    và cơ hội giữ nguyên khai báo. Đó không phải thất bại: Pendle có mặt
    trên nhiều chuỗi hơn số chuỗi ta bắc cầu tới được, và giả vờ ngược lại
    là bịa một tuyến không tồn tại.
    """
    if dinhTuyen is None:
        return None, None, ()
    try:
        from chuyen_von.diem import Diem
        from chuyen_von.dinh_tuyen import NHA
        c = str(chuoi).strip().lower()
        gas = dinhTuyen._gas_usd(c, "doi-tren-amm")
        if gas is None:
            return None, None, ()
        if c == NHA:
            return 2.0 * gas, 0.0, ("gas-limit-uoc-luong",)
        _, t = dinhTuyen.phi_bps(Diem("chuoi", NHA), Diem("chuoi", c),
                                 TAI_SAN_BAC_CAU, vonUsd)
        if t.phiUsd is None:
            return None, None, ()
        return (2.0 * gas + 2.0 * t.phiUsd, 2.0 * (t.giayCho or 0.0),
                tuple(t.khongDoDuoc))
    except Exception as e:                                    # noqa: BLE001
        return None, None, (f"router-no:{type(e).__name__}",)
SUC_CHUA_CON_THIEU = ("do-sau-amm-pendle",)

#: Một nguồn duy nhất cho cả khai báo của ty lẫn
#: từng tờ trình nó xuất ra.
_VON_TOI_THIEU = 1000.0

NHAN = {
    "tvl-qua-nho": "TVL quá nhỏ",
    "apy-duoi-nguong": "lãi cố định dưới ngưỡng",
    "apy-cao-bat-thuong": "lãi cao bất thường — dấu hiệu xấu",
    "sap-dao-han": "quá gần đáo hạn, phần lãi còn lại không bù nổi phí vào",
    "da-dao-han": "đã quá hạn",
    "khong-doc-duoc-dao-han": "không đọc được ngày đáo hạn",
    "du-lieu-cu": "dữ liệu quá cũ",
}

CUA = ("tvlToiThieuUsd", "apyToiThieuPhanTram", "apyToiDaPhanTram",
       "conLaiToiThieuGio", "tuoiToiDaGiay")

#: `PT-sUSDe-22OCT2026` · `For LP | Maturity 15OCT2026`
_THANG = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
          "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
_NGAY = re.compile(r"(\d{1,2})([A-Z]{3})(\d{4})")


def doc_dao_han(meta: str | None) -> _dt.datetime | None:
    """`...22OCT2026` → ngày đáo hạn UTC. `None` nếu không đọc được.

    `None` phải chảy tới tận cổng ty và bị TỪ CHỐI ở đó. Đoán một ngày đáo
    hạn là đoán đúng con số quyết định vốn bị khoá bao lâu.
    """
    m = _NGAY.search((meta or "").upper())
    if not m:
        return None
    ng, th, na = int(m.group(1)), _THANG.get(m.group(2)), int(m.group(3))
    if not th:
        return None
    try:
        return _dt.datetime(na, th, ng, tzinfo=_dt.timezone.utc)
    except ValueError:
        return None


def la_pt(meta: str | None) -> bool:
    """Đúng dạng PT chứ không phải LP. Xem docstring đầu file."""
    s = (meta or "").upper()
    return "PT-" in s and "LP" not in s


@dataclass(frozen=True)
class ThiTruongPT:
    ma: str
    chuoi: str
    taiSan: str
    meta: str
    apyPhanTram: float
    tvlUsd: float
    tvlGiaoThucUsd: float | None
    daoHan: _dt.datetime | None
    docLucMs: float = field(default_factory=lambda: time.time() * 1000.0)

    @property
    def conLaiGio(self) -> float | None:
        if self.daoHan is None:
            return None
        return (self.daoHan - _dt.datetime.now(_dt.timezone.utc)).total_seconds() / 3600.0

    def tuoi_giay(self) -> float:
        return (time.time() * 1000.0 - self.docLucMs) / 1000.0

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "chuoi": self.chuoi, "taiSan": self.taiSan,
                "meta": self.meta, "apyPhanTram": self.apyPhanTram,
                "tvlUsd": self.tvlUsd, "tvlGiaoThucUsd": self.tvlGiaoThucUsd,
                "daoHan": self.daoHan.isoformat() if self.daoHan else None,
                "conLaiGio": self.conLaiGio, "tuoiGiay": self.tuoi_giay()}


@dataclass(frozen=True)
class CoHoiPT:
    tt: ThiTruongPT
    vonXinUsd: float
    giuGio: float
    grossBps: float
    netBps: float
    sucChuaToiDaUsd: float | None
    #: Phí vào+ra do Router đo. `None` = chưa đo được, và `netBps` KHÔNG
    #: gồm nó — cơ hội giữ nguyên khai báo `gas-vao-ra`.
    phiVaoRaUsd: float | None = None
    giayCauNoi: float | None = None
    routerConThieu: tuple = ()
    duyet: bool = False
    lyDo: tuple = ()
    lyDoMa: tuple = ()

    @property
    def netMoiGioBps(self) -> float:
        return self.netBps / self.giuGio if self.giuGio else 0.0

    def tom_tat(self) -> dict:
        return {**self.tt.tom_tat(), "vonXinUsd": self.vonXinUsd,
                "giuGio": self.giuGio, "grossBps": self.grossBps,
                "netBps": self.netBps, "netMoiGioBps": self.netMoiGioBps,
                "sucChuaToiDaUsd": self.sucChuaToiDaUsd, "duyet": self.duyet,
                "lyDo": list(self.lyDo),
                "lyDoMa": [list(x) for x in self.lyDoMa]}


class NguonPendle(Nguon):
    ten = "defillama-pendle"

    def __init__(self) -> None:
        super().__init__()
        self.soBoViLp = 0
        self.soBoViKhongDocDuocHan = 0

    async def doc(self, client, chuoi=()) -> list[ThiTruongPT]:
        t0 = time.perf_counter()
        try:
            r = await client.get(DUONG)
            r.raise_for_status()
            d = r.json()
        except Exception as e:                            # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
        self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        ds = d.get("data", d) if isinstance(d, dict) else d
        if not isinstance(ds, list):
            return []

        tvl_gt = 0.0
        for x in ds:
            if "pendle" in (x.get("project") or "").lower():
                tvl_gt += so_hoac_none(x.get("tvlUsd")) or 0.0

        muon = {c.lower() for c in chuoi} if chuoi else None
        ra, bo_lp, bo_han = [], 0, 0
        for x in ds:
            if "pendle" not in (x.get("project") or "").lower():
                continue
            if muon is not None and (x.get("chain") or "").lower() not in muon:
                continue
            meta = x.get("poolMeta") or ""
            if not la_pt(meta):
                bo_lp += 1
                continue
            apy = so_hoac_none(x.get("apyBase"))
            if apy is None:
                continue
            han = doc_dao_han(meta)
            if han is None:
                bo_han += 1
            ra.append(ThiTruongPT(
                ma=str(x.get("pool")), chuoi=str(x.get("chain") or "?"),
                taiSan=str(x.get("symbol") or "?"), meta=str(meta),
                apyPhanTram=apy,
                tvlUsd=so_hoac_none(x.get("tvlUsd")) or 0.0,
                tvlGiaoThucUsd=tvl_gt or None, daoHan=han))
        self.soBoViLp = bo_lp
        self.soBoViKhongDocDuocHan = bo_han
        return ra

    def tom_tat(self) -> dict:
        return {**self.suc_khoe.tom_tat(), "soBoViLp": self.soBoViLp,
                "soBoViKhongDocDuocHan": self.soBoViKhongDocDuocHan}


class CongRuiRo:
    def __init__(self, c: dict) -> None:
        self.c = dict(c)

    def xet(self, co: CoHoiPT) -> tuple[bool, list[tuple[str, str]]]:
        t = co.tt
        ly = []
        if t.daoHan is None:
            ly.append(("khong-doc-duoc-dao-han",
                       f"không đọc được ngày đáo hạn từ {t.meta!r} — đoán một "
                       f"ngày đáo hạn là đoán đúng con số quyết định vốn bị "
                       f"khoá bao lâu"))
        else:
            con = t.conLaiGio or 0.0
            if con <= 0:
                ly.append(("da-dao-han", f"đã quá hạn {abs(con):.0f} giờ"))
            elif con < float(self.c["conLaiToiThieuGio"]):
                ly.append(("sap-dao-han",
                           f"còn {con:.0f} giờ < {self.c['conLaiToiThieuGio']:.0f}"
                           f" — phần lãi còn lại quá nhỏ so với phí vào, mà "
                           f"rủi ro thao tác không giảm theo"))

        if t.tvlUsd < float(self.c["tvlToiThieuUsd"]):
            ly.append(("tvl-qua-nho",
                       f"TVL ${t.tvlUsd / 1e6:.1f}M < "
                       f"${self.c['tvlToiThieuUsd'] / 1e6:.1f}M"))
        if t.apyPhanTram < float(self.c["apyToiThieuPhanTram"]):
            ly.append(("apy-duoi-nguong",
                       f"lãi cố định {t.apyPhanTram:.2f}% < "
                       f"{self.c['apyToiThieuPhanTram']:.2f}%"))
        if t.apyPhanTram > float(self.c["apyToiDaPhanTram"]):
            ly.append(("apy-cao-bat-thuong",
                       f"lãi cố định {t.apyPhanTram:.1f}% > "
                       f"{self.c['apyToiDaPhanTram']:.0f}% — lãi cố định cao "
                       f"bất thường là thị trường đang trả để ai đó gánh một "
                       f"rủi ro, không phải một món hời"))
        if t.tuoi_giay() > float(self.c["tuoiToiDaGiay"]):
            ly.append(("du-lieu-cu", f"dữ liệu {t.tuoi_giay():.0f}s quá cũ"))
        return (not ly), ly

    def tom_tat(self) -> dict:
        return {k: self.c[k] for k in CUA if k in self.c}


def mot_co_hoi(t: ThiTruongPT, von: float, sucChuaC: dict,
               dinhTuyen=None) -> CoHoiPT:
    """Giữ tới ĐÁO HẠN, không phải một cửa sổ ta tự chọn.

    PT trả lãi cố định tới ngày đáo hạn; giữ ngắn hơn thì phải bán trên AMM
    ở một giá ta không biết. Nên `giuGio` ở đây là thời gian còn lại, và nó
    bằng đúng `khoaVonDenGio` — hai con số trùng nhau, và đó là sự thật của
    công cụ này chứ không phải một sự trùng lặp cần gỡ.
    """
    con = t.conLaiGio if (t.conLaiGio or 0) > 0 else 1.0
    gross = t.apyPhanTram * 100.0 * (con / (365.0 * 24.0))
    phiUsd, giay, rct = phi_vao_ra(t.chuoi, t.taiSan, von, dinhTuyen)
    # Trượt giá AMM vẫn CHƯA trừ được dù có Router — nó đòi đường cong AMM
    # của chính Pendle. Khai ở `phiConThieu`, không giả vờ bằng 0.
    phiBps = (phiUsd / von * 10_000.0) if (phiUsd is not None and von > 0) else 0.0
    return CoHoiPT(
        tt=t, vonXinUsd=von, giuGio=con, grossBps=gross,
        netBps=gross - phiBps,
        sucChuaToiDaUsd=min(t.tvlUsd * float(sucChuaC["phanTvl"]),
                            float(sucChuaC["tranUsd"])) if t.tvlUsd else None,
        phiVaoRaUsd=phiUsd, giayCauNoi=giay, routerConThieu=rct)


class TyLaiSuat(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("lãi cố định Pendle PT — khoá vốn tới ngày đáo hạn, "
            "không rút sớm mà không bán lỗ trên AMM")

    #: Cao hơn ty cho vay, và có lý do: mua PT là một lượt swap trên AMM
    #: Pendle, nên ngoài gas còn có TRƯỢT GIÁ — mà trượt giá thì cỡ vốn nhỏ
    #: không cứu được, chỉ làm phần vụn thành lớn hơn.
    #:
    #: Thêm nữa vốn KHOÁ tới đáo hạn: bỏ $200 vào một chỗ khoá ba tháng là
    #: tiêu một slot vị thế trong ba tháng cho một khoản lãi vài đô.
    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, client_factory=None, dinhTuyen=None) -> None:
        super().__init__()
        self.dinhTuyen = dinhTuyen
        self.nguon = NguonPendle()
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.thiTruong: list = []
        self.coHoi: list = []
        self._cf = client_factory

    def quet(self) -> list:
        self.thiTruong = _chay(self._doc())
        von = float(CONFIG["von"]["moiCoHoiUsd"])
        ra = []
        for t in self.thiTruong:
            co = mot_co_hoi(t, von, CONFIG["sucChua"],
                            self.dinhTuyen)
            qua, ly = self.cong.xet(co)
            ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                              lyDo=tuple(c for _, c in ly)))
        ra.sort(key=lambda c: -c.netMoiGioBps)
        self.coHoi = ra
        return list(ra)

    async def _doc(self):
        import httpx
        lam = self._cf or (lambda: httpx.AsyncClient(
            timeout=float(CONFIG["quet"]["hetGioHoiGiay"]),
            headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}))
        async with lam() as c:
            return await self.nguon.doc(c, CONFIG["quet"]["chuoi"])

    def xet(self, co):
        return bool(co.duyet), list(co.lyDoMa or ())

    def trinh(self, co) -> ToTrinh:
        return xuat_to_trinh(co)

    # ── kế toán: lãi CỐ ĐỊNH, cộng đều tới ngày đáo hạn ──────────────────
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """PT khoá lãi tới đáo hạn, nên đây là ty duy nhất mà rate KHÔNG
        đổi giữa chừng: mua xong là biết trước sẽ nhận bao nhiêu.

        Hệ quả cho kế toán, và nó ngược với ba ty kia: rate lấy từ **tờ
        trình lúc mở**, không lấy từ lượt quét mới nhất. `apyPhanTram` hôm
        nay là lãi ngụ ý cho người mua HÔM NAY — vị thế đã mở thì không
        hưởng con số ấy. Dùng số mới là âm thầm đánh giá lại một hợp đồng
        đã khoá, và đường NAV sẽ nhấp nhô theo một thứ không chạm tới ta.

        Vẫn phải tra lượt quét gần nhất, nhưng chỉ để trả lời MỘT câu:
        thị trường ấy còn tồn tại không. Biến mất là `doDuoc=False`.

        Quá ngày đáo hạn thì ĐÒI ĐÓNG: sau đáo hạn PT không sinh thêm gì,
        giữ tiếp là giam vốn không lãi.
        """
        import datetime as _d

        from thi_bac_ty.ke_toan import NAM_GIAY, KetToanVong

        dt = max(0.0, float(denGiay) - float(tuGiay))
        if dt <= 0.0:
            return KetToanVong(vi="chưa qua giây nào kể từ lần kế toán trước")

        chuoi = (toTrinh.get("chuoi") or [None])[0]
        taiSan = toTrinh.get("taiSan")
        t = next((x for x in self.thiTruong
                  if x.chuoi == chuoi and x.taiSan == taiSan), None)
        if t is None:
            return KetToanVong(
                doDuoc=False,
                vi=f"KHÔNG thấy thị trường PT {taiSan} trên {chuoi} trong "
                   f"lượt quét gần nhất — biến mất khác hẳn trả 0%")

        # Lãi ĐÃ KHOÁ lúc mở, đọc từ tờ trình. Xem docstring.
        try:
            apy = float(toTrinh["grossBps"]) / 100.0 * (
                365.0 * 24.0 / float(toTrinh["giuGio"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return KetToanVong(
                doDuoc=False,
                vi="tờ trình thiếu `grossBps`/`giuGio` nên không dựng lại "
                   "được lãi đã khoá — không đoán")

        von = sum(abs(float(getattr(c, "vonUsd", 0.0) or 0.0)) for c in viThe)
        thu = von * (apy / 100.0) * dt / NAM_GIAY
        con = t.conLaiGio
        vi = (f"PT {taiSan} trên {chuoi}: lãi ĐÃ KHOÁ {apy:.2f}%/năm × "
              f"{dt / 3600:.4f}h trên {von:.2f} USD"
              + (f" · còn {con:.1f}h tới đáo hạn" if con is not None else ""))
        if con is not None and con <= 0.0:
            return KetToanVong(
                thuUsd=thu, dongLai=True,
                lyDoDong=f"đã qua ngày đáo hạn ({t.daoHan}) — PT không sinh "
                         f"thêm gì, giữ tiếp là giam vốn không lãi",
                vi=vi)
        return KetToanVong(thuUsd=thu, vi=vi)


def _chay(coro):
    """Xem `tin_dung/ty_vay._chay` — cùng lý do, cùng cái giá."""
    import concurrent.futures
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


def _tin_cay(co: CoHoiPT) -> float:
    """Bắt đầu 1,0 rồi TRỪ — cùng lối bốn ty kia.

    Trừ 0,25 khi chưa đo được phí vào+ra: `netBps` đang thiếu một khoản chỉ
    có thể làm nó tệ đi, và không trừ ở đây là để một cơ hội CHƯA ĐO xếp
    trên một cơ hội ĐÃ ĐO — thưởng cho sự thiếu hiểu biết.
    """
    d = 1.0
    if co.tt.daoHan is None:
        d -= 0.25
    if co.tt.tvlUsd is None or not co.tt.tvlUsd:
        d -= 0.20
    if co.phiVaoRaUsd is None:
        d -= 0.25
    return max(0.0, min(1.0, d))


def _xin(co) -> float:
    """Cỡ XIN theo sức chứa. Sàn là `vonXinUsd` — cỡ đã tính mọi bps."""
    v = CONFIG.get("von") or {}
    return xin_theo_suc_chua(
        co.vonXinUsd, getattr(co, "sucChuaToiDaUsd", None),
        float(v.get("phanSucChuaXin") or 0.5),
        float(v.get("tranMotLanUsd") or 50_000.0))


def xuat_to_trinh(co: CoHoiPT) -> ToTrinh:
    t = co.tt
    gt = rui_ro_tvl(t.tvlGiaoThucUsd or t.tvlUsd)
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=t.taiSan,
        chan=(Chan("CHO_VAY", "pendle", t.taiSan, _xin(co), "yield",
                   t.chuoi),),
        # XIN theo SỨC CHỨA — xem `thi_bac_ty.to_trinh.xin_theo_suc_chua`.
        # Các con số bps vẫn tính ở cỡ sàn, nên chúng là cận dưới.
        vonCanUsd=_xin(co), sucChuaToiDaUsd=co.sucChuaToiDaUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        grossBps=co.grossBps, phiUocBps=0.0, netUocBps=co.netBps,
        giuGio=co.giuGio,
        # ĐÂY là ty đầu tiên khai một con số khoá vốn THẬT khác 0.
        khoaVonDenGio=(t.conLaiGio if (t.conLaiGio or 0) > 0 else None),
        # Bán lại được trên AMM Pendle, nhưng ở giá nào thì nguồn không nói.
        # `None` = chưa đo, không phải 0 và cũng không phải TVL.
        thanhKhoanThoatUsd=None,
        ruiRo=RuiRo(
            thiTruong=0.15,          # PT bám tài sản gốc, phần lớn là stable
            thanhKhoan=0.45,         # chỉ ra được qua AMM, và ta không đo được
            giaoThuc=gt, cang=gt,
            thucThi=0.15, cauNoi=0.0),
        tuoiDuLieuGiay=t.tuoi_giay(),
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False,
        phiConThieu=_phi_con_thieu(co.phiVaoRaUsd is not None,
                                   co.routerConThieu),
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang=t.taiSan, cang=("pendle",), chuoi=(t.chuoi,),
        bangChung=(
            f"Pendle PT trên {t.chuoi} · {t.meta}",
            f"lãi CỐ ĐỊNH {t.apyPhanTram:.2f}%/năm tới đáo hạn",
            (f"đáo hạn {t.daoHan.date().isoformat()}, còn "
             f"{(t.conLaiGio or 0) / 24:.0f} ngày — vốn KHOÁ hết ngần ấy"
             if t.daoHan else "KHÔNG đọc được ngày đáo hạn"),
            f"TVL ${t.tvlUsd / 1e6:.1f}M",
            (f"phí vào+ra ${co.phiVaoRaUsd:,.2f} đã TRỪ (Router đo) — "
             f"trượt giá AMM Pendle thì chưa, xem phiConThieu"
             if co.phiVaoRaUsd is not None else
             "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"),
        ))
