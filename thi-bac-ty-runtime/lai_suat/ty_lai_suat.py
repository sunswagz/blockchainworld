"""TY LÃI SUẤT — Pendle PT. Lãi CỐ ĐỊNH, khoá tới ngày đáo hạn.

Cùng họ `tin-dung` với ty cho vay, nhưng cơ chế ngược nhau ở đúng chỗ đáng
kể nhất:

    tin_dung   lãi THẢ NỔI, rút được bất cứ lúc nào (còn thanh khoản)
    lai_suat   lãi CỐ ĐỊNH, khoá tới ngày đáo hạn

Đó là lý do ty này đáng dựng: nó là ty đầu tiên dùng `khoaVonDenGiay` với
một con số THẬT khác 0. Trước nó, trường ấy tồn tại trong hợp đồng mà chưa
ai chứng minh nó có tác dụng.

## Hệ quả thấy ngay, và nó ĐÚNG

Một PT đáo hạn sau 57 ngày sẽ bị `rui_ro_tong.khoaVonToiDaGiay` (mặc định
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
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

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
    "von": {"moiCoHoiUsd": 200.0},
    "sucChua": {"phanTvl": 0.01, "tranUsd": 50_000.0},
}

PHI_CON_THIEU = ("gas-vao-ra", "truot-gia-tren-amm-pendle",
                 "chuyen-von-giua-chuoi", "thue")
SUC_CHUA_CON_THIEU = ("do-sau-amm-pendle",)

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


def mot_co_hoi(t: ThiTruongPT, von: float, sucChuaC: dict) -> CoHoiPT:
    """Giữ tới ĐÁO HẠN, không phải một cửa sổ ta tự chọn.

    PT trả lãi cố định tới ngày đáo hạn; giữ ngắn hơn thì phải bán trên AMM
    ở một giá ta không biết. Nên `giuGio` ở đây là thời gian còn lại, và nó
    bằng đúng `khoaVonDenGiay` — hai con số trùng nhau, và đó là sự thật của
    công cụ này chứ không phải một sự trùng lặp cần gỡ.
    """
    con = t.conLaiGio if (t.conLaiGio or 0) > 0 else 1.0
    gross = t.apyPhanTram * 100.0 * (con / (365.0 * 24.0))
    return CoHoiPT(
        tt=t, vonXinUsd=von, giuGio=con, grossBps=gross,
        # Gas và trượt giá AMM chưa trừ được — khai ở `phiConThieu`, KHÔNG
        # giả vờ bằng 0 trong con số NET.
        netBps=gross,
        sucChuaToiDaUsd=min(t.tvlUsd * float(sucChuaC["phanTvl"]),
                            float(sucChuaC["tranUsd"])) if t.tvlUsd else None)


class TyLaiSuat(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("lãi cố định Pendle PT — khoá vốn tới ngày đáo hạn, "
            "không rút sớm mà không bán lỗ trên AMM")

    def __init__(self, client_factory=None) -> None:
        super().__init__()
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
            co = mot_co_hoi(t, von, CONFIG["sucChua"])
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


def _chay(coro):
    """Xem `tin_dung/ty_vay._chay` — cùng lý do, cùng cái giá."""
    import concurrent.futures
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


def xuat_to_trinh(co: CoHoiPT) -> ToTrinh:
    t = co.tt
    gt = rui_ro_tvl(t.tvlGiaoThucUsd or t.tvlUsd)
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=t.taiSan,
        chan=(Chan("CHO_VAY", "pendle", t.taiSan, co.vonXinUsd, "yield",
                   t.chuoi),),
        vonCanUsd=co.vonXinUsd, sucChuaToiDaUsd=co.sucChuaToiDaUsd,
        grossBps=co.grossBps, phiUocBps=0.0, netUocBps=co.netBps,
        giuGio=co.giuGio,
        # ĐÂY là ty đầu tiên khai một con số khoá vốn THẬT khác 0.
        khoaVonDenGiay=(t.conLaiGio if (t.conLaiGio or 0) > 0 else None),
        # Bán lại được trên AMM Pendle, nhưng ở giá nào thì nguồn không nói.
        # `None` = chưa đo, không phải 0 và cũng không phải TVL.
        thanhKhoanThoatUsd=None,
        ruiRo=RuiRo(
            thiTruong=0.15,          # PT bám tài sản gốc, phần lớn là stable
            thanhKhoan=0.45,         # chỉ ra được qua AMM, và ta không đo được
            giaoThuc=gt, cang=gt,
            thucThi=0.15, cauNoi=0.0),
        tuoiDuLieuGiay=t.tuoi_giay(),
        tinCay=(0.75 if t.daoHan is not None else 0.30),
        moHinhPhiDuChua=False, phiConThieu=PHI_CON_THIEU,
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang=t.taiSan, cang=("pendle",), chuoi=(t.chuoi,),
        bangChung=(
            f"Pendle PT trên {t.chuoi} · {t.meta}",
            f"lãi CỐ ĐỊNH {t.apyPhanTram:.2f}%/năm tới đáo hạn",
            (f"đáo hạn {t.daoHan.date().isoformat()}, còn "
             f"{(t.conLaiGio or 0) / 24:.0f} ngày — vốn KHOÁ hết ngần ấy"
             if t.daoHan else "KHÔNG đọc được ngày đáo hạn"),
            f"TVL ${t.tvlUsd / 1e6:.1f}M",
            "gas và trượt giá AMM CHƯA trừ — xem phiConThieu",
        ))
