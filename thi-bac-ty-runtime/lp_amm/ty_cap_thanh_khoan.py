"""Ty CẤP THANH KHOẢN — phí AMM, và một khoản lỗ ta KHÔNG đo được.

Engine thứ chín, và nó là engine thành thật nhất trong chín: nó từ chối
**11.276 trên 17.163 pool** ngay ở cửa đầu tiên, vì với chúng ta không đo
được tổn thất vô thường và một con số lãi thiếu phần lỗ là con số nói dối.

## Tổn thất vô thường không đo được từ một ảnh chụp

IL phụ thuộc giá hai tài sản đi bao xa so với nhau **trong tương lai**. Đo
nó đòi một mô hình biến động, và runtime này không có — cũng không nên có,
vì mọi engine khác ở đây cố ý không dự báo gì.

Nên ty này không ước IL. Nó làm điều khác: **chỉ nhận những pool mà IL nhỏ
theo cấu tạo** — hai tài sản neo vào nhau (USDC-USDT, stETH-ETH). DefiLlama
gắn cờ `ilRisk` cho đúng chuyện đó, và ty này từ chối thẳng mọi pool
`ilRisk = "yes"`.

Từ chối 11.276 pool là mất phần lớn thị trường. Đó là cái giá của việc
không bịa một con số IL, và nó đáng trả: một bảng xếp hạng LP tính lãi mà
bỏ lỗ sẽ luôn xếp WETH-ALT lên đầu, đúng những pool ăn vốn nhanh nhất.

**Kể cả `ilRisk = "no"` thì IL cũng KHÔNG bằng 0.** Stablecoin mất neo là
IL thật và có thể rất lớn. `phiConThieu` khai `ton-that-vo-thuong-du-neo`
để không ai đọc NET ở đây như đọc NET của một khoản cho vay.

## Ba cửa dữ liệu, và cả ba đều bắt được thứ có thật

**TVL phi lý.** DefiLlama báo `aerodrome-slipstream WETH-SAND` có TVL
**$31,4 tỷ** — trong khi cả DeFi cộng lại mới cỡ 100–200 tỷ. Một pool
altcoin bằng một phần năm toàn ngành là dữ liệu hỏng, không phải cơ hội, và
nó sẽ đứng đầu mọi bảng xếp hạng dựa trên sức chứa.

**`apyBase` không khớp vòng quay.** Phí AMM sinh ra từ khối lượng:

    apyBase ≈ (khối lượng ngày / TVL) × mức phí × 365

Nên đảo ngược lại là suy được mức phí ngầm định. Ra ngoài khoảng
[0,5 bps; 100 bps] thì hoặc khối lượng sai, hoặc `apyBase` sai — và ta
không biết cái nào, nên từ chối cả cặp số.

Đây là phép kiểm CHÉO, không phải một cửa ngưỡng: nó so hai con số của
CÙNG một nguồn với nhau. Nguồn nói dối một cách nhất quán thì nó không bắt
được; nguồn hỏng một chỗ thì nó bắt.

**Vòng quay bằng 0.** Pool không có giao dịch thì không có phí, và
`apyBase` của nó là số của quá khứ.

## Thưởng KHÔNG vào NET

Cùng luật `tin_dung/`: `apyReward` là token phát thêm, bốc hơi khi chương
trình hết, và ta không có đường bán nó. Tính nó vào NET là để mọi bảng xếp
hạng bị chiếm bởi những pool đang mua thanh khoản bằng token của chính mình.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, replace

from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.nguon import Nguon, so_hoac_none
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

MA_CHIEN_LUOC = "amm.fee_farming.v1"
HO = "thanh-khoan"

#: Hai giao dịch (vào + ra), và vị thế LP không có đòn bẩy. $500 là chỗ gas
#: L2 còn nhỏ so với phí thu được trong một tuần.
_VON_TOI_THIEU = 500.0

API = "https://yields.llama.fi/pools"

PHI_CON_THIEU = (
    "ton-that-vo-thuong-du-neo",   # ilRisk="no" KHÔNG có nghĩa IL = 0
    "gia-token-thuong",
    "thue",
    "truot-gia-khi-vao-ra-vi-the",
)
SUC_CHUA_CON_THIEU = ("do-sau-that-cua-pool", "phan-tram-pool-ta-chiem")

CUA = ("apyToiThieuPhanTram", "tvlToiThieuUsd", "tvlToiDaUsd",
       "vongQuayToiThieu", "phiNgamToiThieuBps", "phiNgamToiDaBps",
       "netToiThieuBps", "doiHoiIlRiskNo", "doiHoiCapNeoThat")

CONFIG = {
    "quet": {
        "chuoi": ("Ethereum", "Arbitrum", "Base", "Polygon", "Optimism"),
        "hetGioHoiGiay": 45.0,
        "giuGio": 168.0,          # một tuần — đủ để gas amortise
    },
    "ruiRo": {
        "doiHoiIlRiskNo": True,
        # Cửa CHÍNH — tự đọc ký hiệu. Xem `NEO_DO_LA`.
        "doiHoiCapNeoThat": True,
        "apyToiThieuPhanTram": 2.0,
        "tvlToiThieuUsd": 1_000_000.0,
        # Trần dữ liệu hỏng, không phải trần ưa thích. Xem docstring.
        "tvlToiDaUsd": 5_000_000_000.0,
        "vongQuayToiThieu": 0.02,
        "phiNgamToiThieuBps": 0.5,
        "phiNgamToiDaBps": 100.0,
        "netToiThieuBps": 20.0,
    },
    "von": {"moiCoHoiUsd": 500.0},
    "sucChua": {"phanTvl": 0.002, "tranUsd": 25_000.0},
}

#: Tài sản NEO — hai token cùng nhóm thì tổn thất vô thường nhỏ theo cấu
#: tạo. Danh sách này là cửa CHÍNH; `ilRisk` của DefiLlama chỉ là cửa phụ.
#:
#: Vì sao không tin `ilRisk`: nó gắn `no` cho `uniswap-v3 RAIN-USDT` trên
#: Arbitrum, và RAIN là một altcoin. Pool ấy là pool DUY NHẤT qua được mọi
#: cửa khác — tức là nếu tin cờ ấy thì kết quả cuối cùng của cả engine là
#: một dương tính giả. Cờ của bên thứ ba là một LỜI KHAI, không phải một
#: phép đo.
#:
#: Danh sách hẹp là cố ý. Không nhận ra một cặp thì TỪ CHỐI nó và nói vì
#: sao — sai theo hướng bỏ lỡ thì mất cơ hội, sai theo hướng nhận bừa thì
#: mất vốn, và hai cái đó không cân nhau.
NEO_DO_LA = frozenset((
    "USDC", "USDT", "DAI", "USDS", "USDE", "SUSDE", "FRAX", "LUSD", "GHO",
    "CRVUSD", "PYUSD", "TUSD", "USDD", "FDUSD", "USDP", "BUSD", "SUSD",
    "USDC.E", "USDBC", "USDT0", "SDAI", "SUSDS",
))
NEO_ETH = frozenset((
    "ETH", "WETH", "STETH", "WSTETH", "RETH", "CBETH", "WEETH", "EZETH",
    "RSETH", "METH", "SFRXETH", "FRXETH", "OSETH",
))
NEO_BTC = frozenset((
    "BTC", "WBTC", "CBBTC", "TBTC", "LBTC", "SOLVBTC", "BTCB",
))
NHOM_NEO = (NEO_DO_LA, NEO_ETH, NEO_BTC)


def cap_neo_that(kyHieu: str) -> bool | None:
    """Hai vế có CÙNG một nhóm neo không.

    `None` = không đọc được ký hiệu thành hai vế. Đó khác hẳn `False`:
    `False` là "đọc được và chúng không neo nhau", `None` là "tôi không
    biết" — và cả hai đều dẫn tới từ chối, nhưng với hai lý do khác nhau.
    """
    ve = [x.strip().upper() for x in str(kyHieu).split("-") if x.strip()]
    if len(ve) != 2:
        return None
    return any(ve[0] in n and ve[1] in n for n in NHOM_NEO)


NHAN = {
    "co-rui-ro-il": "cặp không neo — tổn thất vô thường không đo được",
    "khong-doc-duoc-cap": "không đọc được ký hiệu thành hai vế neo",
    "apy-duoi-nguong": "phí gốc dưới ngưỡng",
    "tvl-qua-nho": "TVL quá nhỏ",
    "tvl-phi-ly": "TVL lớn tới mức không thể là thật",
    "vong-quay-qua-thap": "gần như không có giao dịch",
    "phi-ngam-vo-ly": "apyBase và khối lượng KHÔNG khớp nhau",
    "net-duoi-nguong": "NET dưới ngưỡng",
    "thieu-so": "nguồn không đủ số để cân",
}


@dataclass(frozen=True)
class Pool:
    ma: str
    duAn: str
    chuoi: str
    kyHieu: str
    tvlUsd: float | None
    khoiLuongNgayUsd: float | None
    apyGocPhanTram: float | None
    apyThuongPhanTram: float | None
    ilRisk: str
    phoi: str
    docLucMs: float

    def tuoi_giay(self, nowMs: float | None = None) -> float:
        now = nowMs if nowMs is not None else time.time() * 1000.0
        return (now - self.docLucMs) / 1000.0

    @property
    def vongQuay(self) -> float | None:
        """Khối lượng ngày chia TVL. `None` khi thiếu một trong hai."""
        if (self.khoiLuongNgayUsd is None or self.tvlUsd is None
                or self.tvlUsd <= 0):
            return None
        return self.khoiLuongNgayUsd / self.tvlUsd

    @property
    def phiNgamBps(self) -> float | None:
        """Mức phí SUY RA từ `apyBase` và vòng quay.

        `apyBase ≈ vòng quay × mức phí × 365`, nên đảo lại là suy được mức
        phí. Đây là phép kiểm CHÉO hai con số của cùng một nguồn — không
        bắt được nguồn nói dối nhất quán, nhưng bắt được nguồn hỏng một chỗ.
        """
        vq = self.vongQuay
        if vq is None or vq <= 0 or self.apyGocPhanTram is None:
            return None
        return (self.apyGocPhanTram / 100.0) / (vq * 365.0) * 10_000.0


@dataclass(frozen=True)
class CoHoiLp:
    pool: Pool
    vonXinUsd: float
    giuGio: float
    grossBps: float | None
    phiVaoRaUsd: float | None
    netBps: float | None
    sucChuaToiDaUsd: float | None
    hoaVonSauGio: float | None
    routerConThieu: tuple = ()
    duyet: bool = False
    lyDo: tuple = ()
    lyDoMa: tuple = ()

    @property
    def netMoiGioBps(self) -> float:
        return (self.netBps / self.giuGio
                if (self.netBps is not None and self.giuGio) else 0.0)

    def tom_tat(self) -> dict:
        p = self.pool
        return {"ma": p.ma, "duAn": p.duAn, "chuoi": p.chuoi,
                "kyHieu": p.kyHieu, "tvlUsd": p.tvlUsd,
                "khoiLuongNgayUsd": p.khoiLuongNgayUsd,
                "vongQuay": p.vongQuay, "phiNgamBps": p.phiNgamBps,
                "apyGocPhanTram": p.apyGocPhanTram,
                "apyThuongPhanTram": p.apyThuongPhanTram,
                "ilRisk": p.ilRisk, "grossBps": self.grossBps,
                "phiVaoRaUsd": self.phiVaoRaUsd, "netBps": self.netBps,
                "netMoiGioBps": self.netMoiGioBps,
                "hoaVonSauGio": self.hoaVonSauGio,
                "sucChuaToiDaUsd": self.sucChuaToiDaUsd,
                "routerConThieu": list(self.routerConThieu),
                "duyet": self.duyet, "lyDo": list(self.lyDo),
                "lyDoMa": [list(x) for x in self.lyDoMa]}


class CongRuiRo:
    def __init__(self, c: dict) -> None:
        self.c = dict(c)

    def xet(self, co: CoHoiLp) -> tuple[bool, list]:
        p, ly = co.pool, []
        if p.tvlUsd is None or p.apyGocPhanTram is None:
            ly.append(("thieu-so", "nguồn không đủ số để cân — thiếu, "
                                   "không phải bằng 0"))
            return False, ly

        # Cửa ĐẦU TIÊN: TỰ đọc ký hiệu, không tin cờ của bên thứ ba.
        neo = cap_neo_that(p.kyHieu)
        if neo is None:
            ly.append(("khong-doc-duoc-cap",
                       f"không đọc được {p.kyHieu!r} thành hai vế — «không "
                       f"biết» và «không neo» đều dẫn tới từ chối, nhưng "
                       f"phải nói khác nhau"))
        elif not neo:
            ly.append(("co-rui-ro-il",
                       f"{p.kyHieu} không phải cặp neo — tổn thất vô thường "
                       f"không đo được từ một ảnh chụp"))
        # Cửa PHỤ: cờ của nguồn. Giữ vì nó bắt được thứ danh sách chưa biết,
        # nhưng KHÔNG được đứng một mình — xem `NEO_DO_LA`.
        if self.c["doiHoiIlRiskNo"] and p.ilRisk != "no":
            ly.append(("co-rui-ro-il",
                       f"ilRisk = {p.ilRisk!r} — tổn thất vô thường không đo "
                       f"được từ một ảnh chụp, và một con số lãi thiếu phần "
                       f"lỗ là con số nói dối"))
        if p.apyGocPhanTram < float(self.c["apyToiThieuPhanTram"]):
            ly.append(("apy-duoi-nguong",
                       f"phí gốc {p.apyGocPhanTram:.2f}% < "
                       f"{self.c['apyToiThieuPhanTram']:.1f}%"))
        if p.tvlUsd < float(self.c["tvlToiThieuUsd"]):
            ly.append(("tvl-qua-nho", f"TVL ${p.tvlUsd:,.0f}"))
        if p.tvlUsd > float(self.c["tvlToiDaUsd"]):
            ly.append(("tvl-phi-ly",
                       f"TVL ${p.tvlUsd:,.0f} — cả DeFi cộng lại mới cỡ "
                       f"100–200 tỷ; đây là dữ liệu hỏng chứ không phải cơ "
                       f"hội, và nó sẽ đứng đầu mọi bảng xếp hạng"))
        vq = p.vongQuay
        if vq is None:
            ly.append(("thieu-so", "không có khối lượng — không suy ra được "
                                   "phí ngầm để đối chiếu"))
        elif vq < float(self.c["vongQuayToiThieu"]):
            ly.append(("vong-quay-qua-thap",
                       f"vòng quay {vq:.4f}x/ngày — không giao dịch thì "
                       f"không có phí, và `apyBase` là số của quá khứ"))
        pn = p.phiNgamBps
        if pn is not None and not (float(self.c["phiNgamToiThieuBps"]) <= pn
                                   <= float(self.c["phiNgamToiDaBps"])):
            ly.append(("phi-ngam-vo-ly",
                       f"mức phí suy ra {pn:.2f} bps ngoài khoảng "
                       f"[{self.c['phiNgamToiThieuBps']}, "
                       f"{self.c['phiNgamToiDaBps']}] — apyBase và khối "
                       f"lượng KHÔNG khớp, và ta không biết cái nào sai"))
        if co.netBps is None:
            ly.append(("thieu-so", "chưa đo được phí vào/ra"))
        elif co.netBps < float(self.c["netToiThieuBps"]):
            ly.append(("net-duoi-nguong", f"NET {co.netBps:.1f} bps"))
        return (not ly), ly

    def tom_tat(self) -> dict:
        return {k: self.c[k] for k in CUA if k in self.c}


class NguonPool(Nguon):
    """DefiLlama yields. CÔNG KHAI, không cần khoá — `tin_dung/` đã dùng."""

    ten = "defillama-pool-lp"

    def __init__(self) -> None:
        super().__init__()
        self.soTho = 0

    async def doc(self, client, chuoi=()) -> list:
        t0 = time.perf_counter()
        try:
            r = await client.get(API)
            r.raise_for_status()
            ds = (r.json() or {}).get("data") or []
        except Exception as e:                                # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
        self.soTho = len(ds)
        muon = {c.lower() for c in chuoi} if chuoi else None
        now = time.time() * 1000.0
        ra = []
        for x in ds:
            ch = str(x.get("chain") or "?")
            if muon is not None and ch.lower() not in muon:
                continue
            ra.append(Pool(
                ma=str(x.get("pool") or "?"), duAn=str(x.get("project") or "?"),
                chuoi=ch, kyHieu=str(x.get("symbol") or "?"),
                tvlUsd=so_hoac_none(x.get("tvlUsd")),
                khoiLuongNgayUsd=so_hoac_none(x.get("volumeUsd1d")),
                apyGocPhanTram=so_hoac_none(x.get("apyBase")),
                apyThuongPhanTram=so_hoac_none(x.get("apyReward")),
                ilRisk=str(x.get("ilRisk") or "?"),
                phoi=str(x.get("exposure") or "?"), docLucMs=now))
        self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        return ra

    def tom_tat(self) -> dict:
        return {**self.suc_khoe.tom_tat(), "soTho": self.soTho}


def mot_co_hoi(p: Pool, vonUsd: float, giuGio: float, sucChuaC: dict,
               phiVaoRaUsd: float | None) -> CoHoiLp:
    """Phí thu trong cửa sổ giữ, trừ chi phí vào+ra.

    `apyBase` là phí GỐC — thưởng KHÔNG cộng vào, cùng luật `tin_dung/`.
    """
    gross = (None if p.apyGocPhanTram is None else
             p.apyGocPhanTram * 100.0 * (giuGio / (365.0 * 24.0)))
    phiBps = (None if (phiVaoRaUsd is None or vonUsd <= 0)
              else phiVaoRaUsd / vonUsd * 10_000.0)
    net = (None if (gross is None or phiBps is None) else gross - phiBps)
    chua = (None if p.tvlUsd is None else
            min(p.tvlUsd * float(sucChuaC["phanTvl"]),
                float(sucChuaC["tranUsd"])))
    hoa = None
    if (p.apyGocPhanTram or 0) > 0 and phiVaoRaUsd is not None and vonUsd > 0:
        moiGio = vonUsd * (p.apyGocPhanTram / 100.0) / (365.0 * 24.0)
        hoa = phiVaoRaUsd / moiGio if moiGio > 0 else None
    return CoHoiLp(pool=p, vonXinUsd=vonUsd, giuGio=giuGio, grossBps=gross,
                   phiVaoRaUsd=phiVaoRaUsd, netBps=net,
                   sucChuaToiDaUsd=chua, hoaVonSauGio=hoa)


def tim_co_hoi(ds, vonUsd: float, giuGio: float, sucChuaC: dict, cong,
               phiVaoRa=None) -> list:
    ra = []
    for p in ds:
        co = mot_co_hoi(p, vonUsd, giuGio, sucChuaC,
                        phiVaoRa(p.chuoi) if phiVaoRa else None)
        qua, ly = cong.xet(co)
        ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                          lyDo=tuple(c for _, c in ly)))
    ra.sort(key=lambda c: -c.netMoiGioBps)
    return ra


def _chay(coro):
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures as _cf
    with _cf.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


class TyCapThanhKhoan(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("cấp thanh khoản AMM — CHỈ nhận cặp neo nhau, vì tổn thất vô "
            "thường không đo được từ một ảnh chụp")

    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, dinhTuyen=None, client_factory=None) -> None:
        super().__init__()
        self.dinhTuyen = dinhTuyen
        self.nguon = NguonPool()
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.pool: list = []
        self.coHoi: list = []
        self._cf = client_factory

    def quet(self) -> list:
        self.pool = _chay(self._doc())
        self.coHoi = tim_co_hoi(
            self.pool, float(CONFIG["von"]["moiCoHoiUsd"]),
            float(CONFIG["quet"]["giuGio"]), CONFIG["sucChua"], self.cong,
            self._phi_vao_ra)
        return list(self.coHoi)

    async def _doc(self):
        import httpx
        q = CONFIG["quet"]
        lam = self._cf or (lambda: httpx.AsyncClient(
            timeout=float(q["hetGioHoiGiay"]),
            headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}))
        async with lam() as c:
            return await self.nguon.doc(c, q["chuoi"])

    def _phi_vao_ra(self, chuoi: str) -> float | None:
        """Gas VÀO + RA vị thế. `None` khi thiếu Router — và `None` chảy lên
        thành «chưa đo được», không thành 0."""
        if self.dinhTuyen is None:
            return None
        try:
            g = self.dinhTuyen._gas_usd(str(chuoi).strip().lower(),
                                        "doi-tren-amm")
            return None if g is None else 2.0 * g
        except Exception:                                     # noqa: BLE001
            return None

    def xet(self, co):
        return bool(co.duyet), list(co.lyDoMa or ())

    def trinh(self, co) -> ToTrinh:
        return xuat_to_trinh(co)

    def tom_tat(self) -> dict:
        return {"nguon": self.nguon.tom_tat(), "cua": self.cong.tom_tat(),
                "soPool": len(self.pool), "soCoHoi": len(self.coHoi),
                "soQua": sum(1 for c in self.coHoi if c.duyet)}


def _rui_ro(co: CoHoiLp) -> RuiRo:
    return RuiRo(
        # Cặp neo nhau nên rủi ro giá thấp — nhưng KHÔNG bằng 0: stablecoin
        # mất neo là tổn thất vô thường thật và có thể rất lớn.
        thiTruong=0.35,
        thanhKhoan=0.30,
        giaoThuc=0.45,     # hợp đồng AMM giữ vốn suốt thời gian ở trong
        cang=0.10,
        thucThi=0.30,
        cauNoi=0.0,
    )


def _tin_cay(co: CoHoiLp) -> float:
    d = 1.0
    p = co.pool
    if p.vongQuay is None:
        d -= 0.30
    if p.phiNgamBps is None:
        d -= 0.20
    if co.phiVaoRaUsd is None:
        d -= 0.25
    if (p.apyThuongPhanTram or 0) > (p.apyGocPhanTram or 0):
        # Thưởng lớn hơn phí gốc nghĩa là pool đang MUA thanh khoản, và
        # `apyBase` của nó sẽ tụt đúng lúc chương trình hết.
        d -= 0.15
    if (p.tvlUsd or 0) < 5_000_000.0:
        d -= 0.10
    return max(0.0, min(1.0, d))


def xuat_to_trinh(co: CoHoiLp) -> ToTrinh:
    p = co.pool
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=p.kyHieu,
        chan=(Chan("CAP_THANH_KHOAN", p.duAn, p.kyHieu, co.vonXinUsd,
                   "lp", p.chuoi),),
        vonCanUsd=co.vonXinUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=co.sucChuaToiDaUsd,
        grossBps=(co.grossBps or 0.0),
        phiUocBps=((co.phiVaoRaUsd or 0.0) / max(co.vonXinUsd, 1.0) * 10_000.0),
        netUocBps=(co.netBps or 0.0),
        giuGio=co.giuGio,
        # Rút được bất cứ lúc nào — vị thế LP không có kỳ hạn.
        khoaVonDenGiay=0.0,
        thanhKhoanThoatUsd=co.sucChuaToiDaUsd,
        ruiRo=_rui_ro(co),
        tuoiDuLieuGiay=p.tuoi_giay(),
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False, phiConThieu=PHI_CON_THIEU,
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang="USD",
        cang=(p.duAn,), chuoi=(p.chuoi,),
        bangChung=(
            f"{p.duAn} · {p.chuoi} · {p.kyHieu} · ilRisk={p.ilRisk}",
            f"TVL ${(p.tvlUsd or 0):,.0f} · khoi luong/ngay "
            f"${(p.khoiLuongNgayUsd or 0):,.0f} · vong quay "
            f"{(p.vongQuay or 0):.3f}x",
            (f"muc phi SUY RA tu apyBase va khoi luong: "
             f"{p.phiNgamBps:.2f} bps — hai con so KHOP nhau"
             if p.phiNgamBps is not None else
             "khong suy duoc muc phi ngam — thieu khoi luong"),
            f"phi goc {(p.apyGocPhanTram or 0):.2f}%/nam · thuong "
            f"{(p.apyThuongPhanTram or 0):.2f}% KHONG tinh vao NET",
            (f"hoa von sau {co.hoaVonSauGio:,.0f} gio"
             if co.hoaVonSauGio is not None else "chua tinh duoc hoa von"),
            "TON THAT VO THUONG KHONG DUOC UOC. Ty nay chi nhan cap NEO "
            "nhau (ilRisk=no), va ke ca the thi IL cung KHONG bang 0 — "
            "stablecoin mat neo la IL that. Xem `ton-that-vo-thuong-du-neo`.",
        ))
