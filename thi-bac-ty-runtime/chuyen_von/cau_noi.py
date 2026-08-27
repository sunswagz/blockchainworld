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

#: Địa chỉ token trên từng chuỗi. Chỉ khai những cặp các ty thật sự dùng.
TOKEN = {
    ("USDC", "ethereum"): "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    ("USDC", "arbitrum"): "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    ("USDC", "base"): "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    ("USDC", "polygon"): "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
    ("USDT", "ethereum"): "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    ("USDT", "arbitrum"): "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    ("USDT", "polygon"): "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
}

DECIMALS = {"USDC": 6, "USDT": 6}

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

        ts, td = TOKEN.get((taiSan, tuChuoi)), TOKEN.get((taiSan, denChuoi))
        ci, cj = CHAIN_ID.get(tuChuoi), CHAIN_ID.get(denChuoi)
        dec = DECIMALS.get(taiSan)
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
