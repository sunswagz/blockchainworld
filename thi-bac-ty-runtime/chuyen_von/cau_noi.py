"""CẦU NỐI — báo giá dời tài sản giữa hai chuỗi, từ LI.FI, không cần khoá.

LI.FI gộp hàng chục cầu nối rồi trả về tuyến rẻ nhất kèm đủ ba con số ta
cần: số tiền NHẬN ĐƯỢC, gas phải trả, và thời gian ước tính.

## Đọc `estimate` cho đúng, và chỗ dễ đọc sai

Một báo giá thật (USDC, Ethereum → Arbitrum, $1.000, ngày 27/08/2026):

    fromAmount     1000000000        (1.000 USDC)
    toAmountMin     997500000        (997,5 USDC)
    fromAmountUSD      998.81
    toAmountUSD        997.65
    gasCosts[0]          0.0869 USD
    executionDuration    7 giây

Lấy hiệu hai cột **USD** ra 1,16 — nhưng phí thật là 2,50 USDC. Lệch vì
hai cột USD quy đổi ở hai giá token khác nhau. Nên phí đọc từ hiệu hai cột
**số lượng token**, chỗ không có tỷ giá nào chen vào:

    phí = (fromAmount − toAmountMin) / 10^decimals

Và dùng `toAmountMin` chứ không `toAmount`: `toAmountMin` là sàn có bảo
đảm sau trượt giá. Lấy `toAmount` là ghi vào sổ trường hợp tốt nhất rồi
gọi nó là dự báo.

Gas thì CỘNG THÊM chứ không nằm trong hiệu ấy — nó trả bằng token gốc của
chuỗi, không trừ vào số tài sản chuyển.

## Vì sao không tự chọn cầu

Chọn cầu là một quyết định vận hành có rủi ro (cầu bị hack, cầu kẹt thanh
khoản), và ta chưa có gì để đánh giá nó. LI.FI đã chọn; ta ghi lại tên
công cụ nó chọn vào `nguon` để về sau còn truy được, và khai
`rui-ro-cau-noi` là thứ KHÔNG đo được — vì đúng là ta không đo được.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from thi_bac_ty.nguon import Nguon, so_hoac_none

from .gas import CHAIN_ID

API = "https://li.quest/v1/quote"

#: Địa chỉ token trên từng chuỗi, ĐÃ ĐỐI CHIẾU với `li.quest/v1/tokens`
#: ngày 27/08/2026. Cùng kỷ luật với `bang_do.py`: số gõ tay phải mang xuất
#: xứ, vì không có xuất xứ thì không kiểm lại được.
#:
#: Hai chuyện lộ ra ở lần đối chiếu đầu tiên, và cả hai đều sắp lọt:
#:
#: 1. Ethereum có HAI token cùng ký hiệu USDC — một cái 6 thập phân
#:    (`0xA0b8…`, thật) và một cái 18 thập phân ở địa chỉ khác. Nên
#:    `decimals` phải theo TỪNG (tài sản, chuỗi), không theo tài sản: chia
#:    sai một luỹ thừa mười hai bậc thì "phí 2,5" thành "phí 2.500.000".
#:
#: 2. Địa chỉ tôi gõ cho "USDT trên Arbitrum" thật ra là **USDT0** — bản
#:    LayerZero OFT, một token KHÁC. LI.FI không phân giải nổi ký hiệu
#:    "USDT" trên Arbitrum (404). Nên nó được ghi đúng tên nó, và
#:    `kyHieuTy` nói rõ ty hỏi "USDT" thì nhận cái này.
#:
#: Thêm dòng thì đối chiếu lại bằng:
#:     curl -s "https://li.quest/v1/token?chain=<id>&token=<địa chỉ>"
@dataclass(frozen=True)
class DongToken:
    diaChi: str
    thapPhan: int
    kyHieuThat: str      # ký hiệu LI.FI trả về cho địa chỉ ấy
    ngayDoi: str = "2026-08-27"


TOKEN_BANG: dict = {
    ("USDC", "ethereum"): DongToken(
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6, "USDC"),
    ("USDC", "arbitrum"): DongToken(
        "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", 6, "USDC"),
    ("USDC", "base"): DongToken(
        "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 6, "USDC"),
    ("USDC", "polygon"): DongToken(
        "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", 6, "USDC"),
    ("USDT", "ethereum"): DongToken(
        "0xdAC17F958D2ee523a2206206994597C13D831ec7", 6, "USDT"),
    # KHÔNG phải USDT gốc — xem ghi chú 2 ở trên.
    ("USDT", "arbitrum"): DongToken(
        "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6, "USDT0"),
    ("USDT", "base"): DongToken(
        "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2", 6, "USDT"),
    ("USDT", "polygon"): DongToken(
        "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6, "USDT"),
    ("DAI", "ethereum"): DongToken(
        "0x6B175474E89094C44Da98b954EedeAC495271d0F", 18, "DAI"),
    ("DAI", "arbitrum"): DongToken(
        "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1", 18, "DAI"),
    ("DAI", "base"): DongToken(
        "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb", 18, "DAI"),
    ("DAI", "polygon"): DongToken(
        "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", 18, "DAI"),
}

#: Bí danh cho mã cũ và cho phép kiểm — chỉ địa chỉ, không kèm thập phân.
TOKEN = {k: v.diaChi for k, v in TOKEN_BANG.items()}


def kiem_token() -> list[str]:
    """Bảng token có tự mâu thuẫn không. Không cần mạng."""
    loi = []
    for (ts, ch), d in TOKEN_BANG.items():
        if not (d.diaChi.startswith("0x") and len(d.diaChi) == 42):
            loi.append(f"{ts}/{ch}: địa chỉ sai khuôn {d.diaChi!r}")
        if d.thapPhan not in (6, 8, 18):
            loi.append(f"{ts}/{ch}: thập phân lạ {d.thapPhan}")
        if d.kyHieuThat != ts:
            # Không phải lỗi — nhưng phải CỐ Ý, nên nó chỉ được im lặng khi
            # có ghi chú. Ở đây kiểm rằng ta biết mình đang lệch.
            if (ts, ch) != ("USDT", "arbitrum"):
                loi.append(f"{ts}/{ch}: ký hiệu thật là {d.kyHieuThat}, "
                           f"chưa ai ghi chú vì sao chấp nhận")
    thay = {}
    for (ts, ch), d in TOKEN_BANG.items():
        k = (ch, d.diaChi.lower())
        if k in thay:
            loi.append(f"{ch}: hai tài sản cùng địa chỉ {thay[k]} và {ts}")
        thay[k] = ts
    return loi


#: Địa chỉ hình nộm. LI.FI đòi `fromAddress` để dựng calldata, nhưng ta chỉ
#: đọc `estimate` và không bao giờ ký gì — không có lớp đặt lệnh nào tồn
#: tại trong runtime này.
DIA_CHI_HINH_NON = "0x0000000000000000000000000000000000000001"


@dataclass(frozen=True)
class BaoGiaCau:
    taiSan: str
    tuChuoi: str
    denChuoi: str
    vonUsd: float
    phiTaiSan: float | None      # đơn vị TÀI SẢN, chưa gồm gas
    gasUsd: float | None
    giayCho: float | None
    congCu: str
    docLucMs: float
    loi: str = ""

    @property
    def doDuoc(self) -> bool:
        return (self.phiTaiSan is not None and self.gasUsd is not None
                and self.giayCho is not None)

    @property
    def tongUsd(self) -> float | None:
        """Stablecoin nên 1 đơn vị ~ 1 đô. Sai số ấy nhỏ hơn nhiều so với
        sai số của chính `gasLimit` ước lượng, và nó không đổi dấu kết
        luận."""
        if not self.doDuoc:
            return None
        return self.phiTaiSan + self.gasUsd                     # type: ignore

    def tom_tat(self) -> dict:
        return {"taiSan": self.taiSan, "tu": self.tuChuoi,
                "den": self.denChuoi, "vonUsd": self.vonUsd,
                "phiTaiSan": self.phiTaiSan, "gasUsd": self.gasUsd,
                "giayCho": self.giayCho, "tongUsd": self.tongUsd,
                "congCu": self.congCu, "loi": self.loi}


class NguonCauNoi(Nguon):
    """Hỏi LI.FI một báo giá. Không cache: phí cầu đổi theo thanh khoản,
    và một báo giá cũ mười phút là một con số trông đúng mà đã sai."""

    ten = "cau-noi-lifi"

    def __init__(self) -> None:
        super().__init__()
        self.ganDay: list[BaoGiaCau] = []

    async def doc(self, client, taiSan: str, tuChuoi: str, denChuoi: str,
                  vonUsd: float) -> BaoGiaCau:
        t0 = time.perf_counter()
        bg = await self._mot(client, taiSan, tuChuoi, denChuoi, vonUsd)
        self.ganDay = ([bg] + self.ganDay)[:20]
        if bg.doDuoc:
            self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        else:
            self.suc_khoe.ghi_loi(RuntimeError(bg.loi or "không đo được"))
        return bg

    async def _mot(self, client, taiSan, tuChuoi, denChuoi,
                   vonUsd) -> BaoGiaCau:
        now = time.time() * 1000.0

        def hong(vi: str) -> BaoGiaCau:
            return BaoGiaCau(taiSan, tuChuoi, denChuoi, vonUsd,
                             None, None, None, "?", now, vi)

        a = TOKEN_BANG.get((taiSan, tuChuoi))
        b = TOKEN_BANG.get((taiSan, denChuoi))
        ci, cj = CHAIN_ID.get(tuChuoi), CHAIN_ID.get(denChuoi)
        # Thập phân của ĐẦU GỬI, vì `fromAmount` và `toAmountMin` LI.FI trả
        # về đều tính theo token nguồn.
        ts, td = (a.diaChi if a else None), (b.diaChi if b else None)
        dec = a.thapPhan if a else None
        if None in (ts, td, ci, cj, dec):
            return hong(f"chưa khai địa chỉ/chainId cho "
                        f"{taiSan} {tuChuoi}->{denChuoi}")
        if vonUsd <= 0:
            return hong(f"vốn phải dương, nhận {vonUsd}")

        r = await client.get(API, params={
            "fromChain": ci, "toChain": cj, "fromToken": ts, "toToken": td,
            "fromAmount": str(int(round(vonUsd * 10 ** dec))),
            "fromAddress": DIA_CHI_HINH_NON})
        if r.status_code >= 400:
            return hong(f"LI.FI {r.status_code}: {r.text[:120]}")
        d = r.json() or {}
        e = d.get("estimate") or {}

        vao = so_hoac_none(e.get("fromAmount"))
        ra = so_hoac_none(e.get("toAmountMin"))
        if vao is None or ra is None or vao <= 0:
            return hong(f"thiếu fromAmount/toAmountMin: {str(e)[:100]}")
        phi = (vao - ra) / 10 ** dec
        # Cầu trả về NHIỀU hơn số gửi là báo giá hỏng, không phải lãi.
        if phi < 0:
            return hong(f"toAmountMin > fromAmount ({ra} > {vao})")

        gas = 0.0
        for g in e.get("gasCosts") or []:
            v = so_hoac_none(g.get("amountUSD"))
            if v is None:
                gas = None
                break
            gas += v

        giay = so_hoac_none(e.get("executionDuration"))
        return BaoGiaCau(taiSan, tuChuoi, denChuoi, vonUsd, phi, gas, giay,
                         str(d.get("tool") or "?"), now,
                         "" if gas is not None and giay is not None
                         else "thiếu gasCosts hoặc executionDuration")

    def tom_tat(self) -> dict:
        return {**self.suc_khoe.tom_tat(),
                "ganDay": [b.tom_tat() for b in self.ganDay[:5]]}
