"""Ty VÒNG ĐỔI — đổi A sang B rồi đổi ngược, xem còn lại bao nhiêu.

Engine thứ tám. Nó trả lời một câu hỏi rất hẹp và rất kiểm chứng được:

    bỏ 1.000 USDC vào, đổi sang USDT, đổi ngược lại — còn bao nhiêu?

Còn HƠN 1.000 sau khi trừ gas thì có chênh lệch thật. Không mô hình, không
dự báo, và không cần biết pool nào ở đâu.

## Vì sao hỏi một bộ định tuyến thay vì tự so hai AMM

Cách hiển nhiên là đọc giá ở Uniswap và ở Curve rồi trừ. Nó sai theo hai
đường: hai giá ấy không kèm phí và trượt giá của CỠ LỆNH ta định vào, và
nó bỏ sót mọi tuyến nhiều chặng mà một bộ định tuyến sẽ tìm ra.

LI.FI **luôn chọn tuyến tốt nhất nó biết**. Nên nếu vòng khứ hồi qua tuyến
TỐT NHẤT vẫn lỗ, thì không có chênh lệch nào để mà nhặt — kết luận mạnh hơn
hẳn so hai pool. Và nếu nó lãi, đó là lãi ĐÃ TÍNH phí lẫn trượt giá ở đúng
cỡ lệnh ấy.

## HAI con số, và cổng dùng con số BI QUAN

LI.FI trả cả `toAmount` (kỳ vọng) lẫn `toAmountMin` (sàn có bảo đảm sau
dung sai trượt giá). Đo ngày 27/08 thì hai con số cách nhau **10 bps mỗi
lượt đổi**, và truyền tham số `slippage` không làm nó hẹp lại.

Cổng dùng `toAmountMin`. Một cơ hội chênh lệch chỉ đáng vào khi nó còn lãi
ở mức TỆ NHẤT được bảo đảm — nếu nó chỉ lãi ở mức kỳ vọng thì ta đang cược
vào việc trượt giá không xảy ra, và đó là dự báo chứ không phải chênh lệch.

`kyVongBps` vẫn được ghi lại để người đọc thấy khoảng cách. Giấu nó đi thì
không ai biết ngưỡng đang bị dung sai trượt giá nuốt mất bao nhiêu.

## Đo thật 27/08/2026 — và kết luận là KHÔNG có gì

    chuỗi     vòng                 bảo đảm   kỳ vọng   gas
    arbitrum  USDC→USDT→USDC       −68,1     −58,2     $0,035
    arbitrum  USDC→DAI →USDC       −68,9     −59,0     $0,035
    polygon   USDC→USDT→USDC       −70,6     −60,7     $0,060
    ethereum  USDC→USDT→USDC       −70,6     −60,7     $0,289
    polygon   USDC→DAI →USDC       −70,9     −60,9     $0,060
    base      USDC→DAI →USDC       −71,2     −61,3     $0,010

Khoảng 30 bps mỗi lượt đổi ở mức kỳ vọng, và gas gần như không đáng kể trên
L2 — phí AMM mới là thứ ăn hết. Stablecoin trên AMM là chỗ cạnh tranh nhất
của cả DeFi; tìm thấy chênh lệch ở đó thường có nghĩa là mình tính sai chứ
không phải mình nhanh hơn.

Lượt thứ hai được hỏi bằng **số ra ĐÃ BẢO ĐẢM** của lượt thứ nhất, không
phải số kỳ vọng. Nối kỳ vọng vào kỳ vọng là cộng dồn hai lần may mắn.

## Cái ty này KHÔNG đo được, và nó lớn

Hai lượt đổi là HAI giao dịch, không phải một. Giá đổi giữa chúng, và bất
kỳ ai đọc được giao dịch thứ nhất đều biết giao dịch thứ hai sắp tới. Một
vòng đổi có lãi trên giấy là một vòng đổi mời người khác chen vào giữa.

Đó chính là điều kiện `do-tre-thap` mà `dong_co_chua_co` khai cho engine
này, và nó KHÔNG được gỡ bởi việc ty này tồn tại. Ty quét được; thực thi
thì vẫn chặn.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, replace

from thi_bac_ty.khuon_ty import Ty
from thi_bac_ty.nguon import so_hoac_none
from thi_bac_ty.to_trinh import Chan, RuiRo, ToTrinh

MA_CHIEN_LUOC = "dex.round_trip.v1"
HO = "chenh-lech"

#: Hai lượt đổi, hai lần gas, và gas là khoản CỐ ĐỊNH. $500 là chỗ vài xu
#: gas trên L2 còn nhỏ so với một edge tính bằng bps.
_VON_TOI_THIEU = 500.0

PHI_CON_THIEU = (
    "chen-giua-hai-giao-dich",     # xem docstring — khoản LỚN NHẤT
    "truot-gia-ngoai-dung-sai",
    "thue",
    "phi-duyet-erc20-lan-dau",
)
SUC_CHUA_CON_THIEU = ("do-sau-pool-that",)

CUA = ("netToiThieuBps", "tuoiToiDaGiay", "khoangCachToiDaBps")

CONFIG = {
    "quet": {
        # Chỉ những cặp CÓ THẬT trong bảng token đã đối chiếu, và chỉ chuỗi
        # có RPC gas. Thêm cặp thì thêm ở `chuyen_von/cau_noi.py` trước.
        "cap": (("arbitrum", "USDC", "USDT"), ("arbitrum", "USDC", "DAI"),
                ("base", "USDC", "DAI"), ("polygon", "USDC", "USDT"),
                ("polygon", "USDC", "DAI"), ("ethereum", "USDC", "USDT")),
        "vonUsd": 1000.0,
        "hetGioHoiGiay": 30.0,
    },
    "ruiRo": {
        # Cao vì khoản KHÔNG đo được (chen giữa hai giao dịch) lớn và không
        # nằm trong con số nào. Ngưỡng thấp ở đây là mời một cơ hội mà phần
        # lãi của nó thuộc về người chen vào.
        "netToiThieuBps": 30.0,
        "tuoiToiDaGiay": 45.0,
        # Kỳ vọng cách xa mức bảo đảm quá thì "lãi" chỉ tồn tại nếu trượt
        # giá không xảy ra — và đó là dự báo, không phải chênh lệch.
        "khoangCachToiDaBps": 60.0,
    },
    "von": {"moiCoHoiUsd": 1000.0},
    "sucChua": {"tranUsd": 5_000.0},
}

NHAN = {
    "net-duoi-nguong": "vòng đổi lỗ hoặc lãi chưa đủ",
    "du-lieu-cu": "báo giá quá cũ",
    "khoang-cach-qua-lon": "kỳ vọng cách mức bảo đảm quá xa",
    "thieu-so": "một trong hai lượt đổi không báo giá được",
}


@dataclass(frozen=True)
class CoHoiVongDoi:
    chuoi: str
    tuTaiSan: str
    quaTaiSan: str
    vaoUsd: float
    #: Ra được bao nhiêu ở mức SÀN CÓ BẢO ĐẢM. `None` = một lượt hỏng.
    raBaoDamUsd: float | None
    #: Ra được bao nhiêu ở mức KỲ VỌNG — chỉ để đọc, cổng không dùng.
    raKyVongUsd: float | None
    gasUsd: float | None
    congCu: tuple
    tuoiGiay: float
    duyet: bool = False
    lyDo: tuple = ()
    lyDoMa: tuple = ()

    @property
    def giuGio(self) -> float:
        """Hai giao dịch nối nhau, xong trong vài giây. Nhưng `giuGio` là
        mẫu số của `netMoiGioBps`, và đặt nó quá nhỏ thì ty này áp đảo mọi
        ty khác trên bảng xếp hạng chỉ vì nó nhanh. Một phần tư giờ là thời
        gian THẬT từ lúc quyết tới lúc vốn quay về dùng được."""
        return 0.25

    @property
    def netBps(self) -> float | None:
        if self.raBaoDamUsd is None or self.gasUsd is None or self.vaoUsd <= 0:
            return None
        return (self.raBaoDamUsd - self.vaoUsd - self.gasUsd) / self.vaoUsd * 10_000.0

    @property
    def kyVongBps(self) -> float | None:
        if self.raKyVongUsd is None or self.gasUsd is None or self.vaoUsd <= 0:
            return None
        return (self.raKyVongUsd - self.vaoUsd - self.gasUsd) / self.vaoUsd * 10_000.0

    @property
    def khoangCachBps(self) -> float | None:
        """Kỳ vọng hơn mức bảo đảm bao nhiêu — tức dung sai trượt giá đang
        nuốt mất bao nhiêu."""
        a, b = self.kyVongBps, self.netBps
        return None if (a is None or b is None) else a - b

    @property
    def netMoiGioBps(self) -> float:
        n = self.netBps
        return 0.0 if n is None else n / self.giuGio

    def tom_tat(self) -> dict:
        return {"chuoi": self.chuoi, "tu": self.tuTaiSan, "qua": self.quaTaiSan,
                "vaoUsd": self.vaoUsd, "raBaoDamUsd": self.raBaoDamUsd,
                "raKyVongUsd": self.raKyVongUsd, "gasUsd": self.gasUsd,
                "netBps": self.netBps, "kyVongBps": self.kyVongBps,
                "khoangCachBps": self.khoangCachBps,
                "netMoiGioBps": self.netMoiGioBps, "congCu": list(self.congCu),
                "tuoiGiay": self.tuoiGiay, "duyet": self.duyet,
                "lyDo": list(self.lyDo),
                "lyDoMa": [list(x) for x in self.lyDoMa]}


class CongRuiRo:
    def __init__(self, c: dict) -> None:
        self.c = dict(c)

    def xet(self, co: CoHoiVongDoi) -> tuple[bool, list]:
        ly: list = []
        net = co.netBps
        if net is None:
            ly.append(("thieu-so", "một trong hai lượt đổi không báo giá "
                                   "được — thiếu, không phải bằng 0"))
            return False, ly
        if net < float(self.c["netToiThieuBps"]):
            ly.append(("net-duoi-nguong",
                       f"NET {net:.1f} bps < {self.c['netToiThieuBps']:.0f} "
                       f"— và ngưỡng cao vì khoản chen-giữa-hai-giao-dịch "
                       f"KHÔNG nằm trong con số này"))
        kc = co.khoangCachBps
        if kc is not None and kc > float(self.c["khoangCachToiDaBps"]):
            ly.append(("khoang-cach-qua-lon",
                       f"kỳ vọng hơn mức bảo đảm {kc:.0f} bps > "
                       f"{self.c['khoangCachToiDaBps']:.0f} — «lãi» chỉ tồn "
                       f"tại nếu trượt giá không xảy ra"))
        if co.tuoiGiay > float(self.c["tuoiToiDaGiay"]):
            ly.append(("du-lieu-cu", f"báo giá cũ {co.tuoiGiay:.0f}s"))
        return (not ly), ly

    def tom_tat(self) -> dict:
        return {k: self.c[k] for k in CUA if k in self.c}


def mot_co_hoi(chuoi: str, a: str, b: str, vaoUsd: float,
               di: dict | None, ve: dict | None,
               gasMotLuotUsd: float | None) -> CoHoiVongDoi:
    """Hai báo giá một chiều → một vòng khứ hồi.

    `di` và `ve` là dict `{"kyVong": …, "baoDam": …, "congCu": …}` tính bằng
    ĐƠN VỊ TÀI SẢN. Stablecoin nên 1 đơn vị ≈ 1 đô; sai số ấy nhỏ hơn nhiều
    so với ngưỡng 30 bps và không đổi dấu kết luận.

    Thiếu một chiều thì cả vòng `None` — cùng luật `TuyenDuong.phiUsd`: một
    chặng mù thì cả tuyến mù.
    """
    if di is None or ve is None:
        return CoHoiVongDoi(chuoi, a, b, vaoUsd, None, None,
                            None, (), 0.0)
    gas = None if gasMotLuotUsd is None else 2.0 * gasMotLuotUsd
    return CoHoiVongDoi(
        chuoi=chuoi, tuTaiSan=a, quaTaiSan=b, vaoUsd=vaoUsd,
        raBaoDamUsd=ve.get("baoDam"), raKyVongUsd=ve.get("kyVong"),
        gasUsd=gas,
        congCu=(str(di.get("congCu") or "?"), str(ve.get("congCu") or "?")),
        tuoiGiay=max(float(di.get("tuoiGiay") or 0.0),
                     float(ve.get("tuoiGiay") or 0.0)))


def _rui_ro(co: CoHoiVongDoi) -> RuiRo:
    return RuiRo(
        # Vốn ở dạng stablecoin cả vòng; rủi ro giá thấp nhưng không bằng 0
        # vì hai lượt đổi không nguyên tử.
        thiTruong=0.25,
        thanhKhoan=0.30,
        giaoThuc=0.40,     # đi qua router và nhiều pool ta không kiểm được
        cang=0.15,         # không sàn nào giữ tiền
        # Cao nhất trong sáu mặt: hai giao dịch rời nhau, và ai đọc được
        # giao dịch đầu đều biết giao dịch sau sắp tới.
        thucThi=0.75,
        cauNoi=0.0,
    )


def _tin_cay(co: CoHoiVongDoi) -> float:
    d = 1.0
    if co.raBaoDamUsd is None:
        d -= 0.50
    kc = co.khoangCachBps
    if kc is None:
        d -= 0.20
    elif kc > 30.0:
        d -= 0.15
    if co.gasUsd is None:
        d -= 0.25
    return max(0.0, min(1.0, d))


def xuat_to_trinh(co: CoHoiVongDoi) -> ToTrinh:
    net = co.netBps
    ky = co.kyVongBps
    return ToTrinh(
        chienLuoc=MA_CHIEN_LUOC, ho=HO, taiSan=co.tuTaiSan,
        chan=(Chan("LONG", "dex-router", co.quaTaiSan, co.vaoUsd, "spot",
                   co.chuoi),
              Chan("SHORT", "dex-router", co.quaTaiSan, co.vaoUsd, "spot",
                   co.chuoi)),
        vonCanUsd=co.vaoUsd,
        vonToiThieuKinhTeUsd=_VON_TOI_THIEU,
        sucChuaToiDaUsd=float(CONFIG["sucChua"]["tranUsd"]),
        grossBps=(0.0 if net is None else net + (co.gasUsd or 0.0)
                  / max(co.vaoUsd, 1.0) * 10_000.0),
        phiUocBps=((co.gasUsd or 0.0) / max(co.vaoUsd, 1.0) * 10_000.0),
        netUocBps=(net or 0.0),
        giuGio=co.giuGio,
        # Không khoá: hai giao dịch xong là vốn về. Nhưng nếu lượt thứ hai
        # hỏng thì vốn KẸT ở tài sản trung gian — và đó là rủi ro thực thi,
        # đã nằm ở `ruiRo.thucThi = 0,75`.
        khoaVonDenGiay=0.0,
        thanhKhoanThoatUsd=float(CONFIG["sucChua"]["tranUsd"]),
        ruiRo=_rui_ro(co),
        tuoiDuLieuGiay=co.tuoiGiay,
        tinCay=_tin_cay(co),
        moHinhPhiDuChua=False, phiConThieu=PHI_CON_THIEU,
        moHinhSucChuaDuChua=False, sucChuaConThieu=SUC_CHUA_CON_THIEU,
        dinhGiaBang=co.tuTaiSan,
        cang=("dex-router",), chuoi=(co.chuoi,),
        bangChung=(
            f"{co.chuoi}: {co.vaoUsd:,.0f} {co.tuTaiSan} -> {co.quaTaiSan} "
            f"-> {co.tuTaiSan} qua {'/'.join(co.congCu)}",
            (f"muc BAO DAM {net:+.1f} bps · ky vong {ky:+.1f} bps · dung sai "
             f"truot gia nuot {(co.khoangCachBps or 0):.0f} bps"
             if net is not None and ky is not None else
             "mot trong hai luot doi KHONG bao gia duoc"),
            "Cong dung muc BAO DAM: mot co hoi chenh lech chi dang vao khi "
            "no con lai o muc TE NHAT duoc bao dam. Chi lai o muc ky vong "
            "la cuoc vao viec truot gia khong xay ra.",
            "KHOAN LON NHAT KHONG DO DUOC: hai luot doi la HAI giao dich. "
            "Gia doi giua chung, va ai doc duoc giao dich dau deu biet giao "
            "dich sau sap toi. Xem `chen-giua-hai-giao-dich`.",
        ))


class NguonDoi:
    """Hỏi LI.FI một lượt đổi CÙNG chuỗi. Chỉ đọc, không ký gì.

    Dùng lại `TOKEN_BANG` của `chuyen_von/` chứ không giữ bảng địa chỉ thứ
    hai — hai bảng địa chỉ token là hai bảng sẽ lệch nhau, và lệch địa chỉ
    token nghĩa là báo giá cho một tài sản khác.
    """

    API = "https://li.quest/v1/quote"
    DIA_CHI_HINH_NON = "0x0000000000000000000000000000000000000001"
    ten = "dex-doi-lifi"

    def __init__(self) -> None:
        self.soLoi = 0
        self.loiCuoi = ""
        self.soLuot = 0

    async def doi(self, client, chuoi: str, a: str, b: str,
                  luong: float) -> dict | None:
        from chuyen_von.cau_noi import TOKEN_BANG
        from chuyen_von.gas import CHAIN_ID
        ta, tb = TOKEN_BANG.get((a, chuoi)), TOKEN_BANG.get((b, chuoi))
        cid = CHAIN_ID.get(chuoi)
        if ta is None or tb is None or cid is None or luong <= 0:
            self.soLoi += 1
            self.loiCuoi = f"chưa khai {a}/{b} trên {chuoi}"
            return None
        self.soLuot += 1
        try:
            r = await client.get(self.API, params={
                "fromChain": cid, "toChain": cid,
                "fromToken": ta.diaChi, "toToken": tb.diaChi,
                "fromAmount": str(int(round(luong * 10 ** ta.thapPhan))),
                "fromAddress": self.DIA_CHI_HINH_NON})
            if r.status_code >= 400:
                self.soLoi += 1
                self.loiCuoi = f"LI.FI {r.status_code}"
                return None
            d = r.json() or {}
            e = d.get("estimate") or {}
            ky = so_hoac_none(e.get("toAmount"))
            sn = so_hoac_none(e.get("toAmountMin"))
            if ky is None or sn is None:
                self.soLoi += 1
                self.loiCuoi = "thiếu toAmount/toAmountMin"
                return None
            return {"kyVong": ky / 10 ** tb.thapPhan,
                    "baoDam": sn / 10 ** tb.thapPhan,
                    "congCu": d.get("tool"), "tuoiGiay": 0.0}
        except Exception as e:                                # noqa: BLE001
            self.soLoi += 1
            self.loiCuoi = f"{type(e).__name__}: {str(e)[:60]}"
            return None

    def tom_tat(self) -> dict:
        return {"ten": self.ten, "soLuot": self.soLuot, "soLoi": self.soLoi,
                "loiCuoi": self.loiCuoi}


class TyVongDoi(Ty):
    ma = MA_CHIEN_LUOC
    ho = HO
    moTa = ("vòng đổi khứ hồi A->B->A trên cùng một chuỗi — hỏi bộ định "
            "tuyến TỐT NHẤT, nên lỗ ở đây nghĩa là không có chênh lệch nào")

    vonToiThieuKinhTeUsd = _VON_TOI_THIEU

    def __init__(self, dinhTuyen=None, client_factory=None) -> None:
        super().__init__()
        self.dinhTuyen = dinhTuyen
        self.nguon = NguonDoi()
        self.cong = CongRuiRo(CONFIG["ruiRo"])
        self.coHoi: list = []
        self._cf = client_factory

    def quet(self) -> list:
        self.coHoi = _chay(self._quet())
        return list(self.coHoi)

    async def _quet(self) -> list:
        import httpx
        q = CONFIG["quet"]
        lam = self._cf or (lambda: httpx.AsyncClient(
            timeout=float(q["hetGioHoiGiay"]),
            headers={"User-Agent": "thi-bac-ty/0.1 (+public data only)"}))
        von = float(q["vonUsd"])
        ra = []
        async with lam() as c:
            for chuoi, a, b in q["cap"]:
                di = await self.nguon.doi(c, chuoi, a, b, von)
                ve = (None if di is None else
                      await self.nguon.doi(c, chuoi, b, a, di["baoDam"]))
                co = mot_co_hoi(chuoi, a, b, von, di, ve,
                                self._gas(chuoi))
                qua, ly = self.cong.xet(co)
                ra.append(replace(co, duyet=qua, lyDoMa=tuple(ly),
                                  lyDo=tuple(x for _, x in ly)))
        ra.sort(key=lambda c: -(c.netBps if c.netBps is not None else -1e9))
        return ra

    def _gas(self, chuoi: str) -> float | None:
        """Gas MỘT lượt đổi. Thiếu Router thì `None`, và `None` chảy lên
        thành «không đo được» chứ không thành 0."""
        if self.dinhTuyen is None:
            return None
        try:
            return self.dinhTuyen._gas_usd(chuoi, "doi-tren-amm")
        except Exception:                                     # noqa: BLE001
            return None

    def xet(self, co):
        return bool(co.duyet), list(co.lyDoMa or ())

    # ── kế toán: vòng đổi XONG TRONG VÀI GIÂY, lãi lỗ ở lúc thoát ────────
    def ke_toan(self, viThe, toTrinh, tuGiay, denGiay):
        """Vòng đổi A→B→A không giữ gì lâu, nên nó không cộng dồn gì cả.

        Nếu ty này KHÔNG có kế toán thì mọi vị thế của nó là **lỗ chắc
        chắn trên sổ**: phí vào lệnh bị trừ lúc mở, `giuGio` 0,25 giờ trôi
        qua, vị thế đóng với `thuUsd` chưa bao giờ được đặt. Cỗ máy khi ấy
        ghi lại đúng phần chi phí và bỏ mất toàn bộ phần thu — một cách
        chắc chắn để một chiến lược có lãi hiện ra như một chiến lược lỗ.

        Đo lại vòng đổi bằng lượt quét MỚI NHẤT: cùng chuỗi, cùng cặp
        tài sản. Dùng `raBaoDamUsd` — mức sàn CÓ BẢO ĐẢM — chứ không dùng
        `raKyVongUsd`: kỳ vọng là con số trước trượt giá, và ghi nó vào sổ
        như tiền đã nhận là tự thưởng cho mình phần dung sai. Chính cổng
        của ty này cũng quyết định bằng mức bảo đảm.

        Trả về kèm `dongLai=True` ngay lượt kế toán đầu tiên: vốn quay về
        sau vài giây, giữ tiếp không sinh thêm gì, và `giuGio` 0,25 giờ
        chỉ là mẫu số cho `netMoiGioBps` chứ không phải thời gian nắm giữ
        thật (xem `CoHoiVongDoi.giuGio`).
        """
        from thi_bac_ty.ke_toan import KetToanVong

        chuoi = (toTrinh.get("chuoi") or [None])[0]
        tu = toTrinh.get("taiSan")
        qua = next((c.taiSan for c in viThe), None)
        c = next((x for x in self.coHoi
                  if x.chuoi == chuoi and x.tuTaiSan == tu
                  and x.quaTaiSan == qua), None)
        if c is None:
            return KetToanVong(
                doDuoc=False,
                vi=f"KHÔNG thấy vòng đổi {tu}→{qua} trên {chuoi} trong lượt "
                   f"quét gần nhất — tuyến biến mất khác hẳn tuyến hoà vốn")
        if c.raBaoDamUsd is None or c.gasUsd is None:
            return KetToanVong(
                doDuoc=False,
                vi=f"lượt báo giá {tu}→{qua} hỏng một chặng — không đo được "
                   f"mức ra CÓ BẢO ĐẢM")

        von = sum(abs(float(getattr(x, "vonUsd", 0.0) or 0.0)) for x in viThe)
        # `netBps` của cơ hội tính trên `vaoUsd` của NÓ; quy về vốn thật
        # đã cấp cho vị thế này.
        net = c.netBps
        thu = von * float(net) / 10_000.0
        return KetToanVong(
            thuUsd=thu, dongLai=True,
            lyDoDong=f"vòng đổi xong — vốn quay về sau vài giây, giữ tiếp "
                     f"không sinh thêm gì",
            vi=(f"vòng đổi {tu}→{qua}→{tu} trên {chuoi}: NET {net:+.2f} bps "
                f"ở mức CÓ BẢO ĐẢM trên {von:.2f} USD"
                + (f" (kỳ vọng {c.kyVongBps:+.2f} bps — chênh "
                   f"{c.khoangCachBps:.2f} bps là dung sai trượt giá)"
                   if c.kyVongBps is not None else "")))

    def trinh(self, co) -> ToTrinh:
        return xuat_to_trinh(co)

    def tom_tat(self) -> dict:
        return {"nguon": self.nguon.tom_tat(), "cua": self.cong.tom_tat(),
                "soCoHoi": len(self.coHoi),
                "soQua": sum(1 for c in self.coHoi if c.duyet)}


def _chay(coro):
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures as _cf
    with _cf.ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()
