"""CONNECTOR GIAO NGAY — đỉnh sổ lệnh ba sàn, dùng chung cho MỌI ty.

Đây là lớp `CONNECTORS` mà bản đồ §27 gọi là Data World, và nó ra đời đúng
lúc có người dùng THỨ HAI chứ không phải dựng sẵn từ đầu:

    on_dinh/   chênh lệch stablecoin — cần bid/ask của USDC/USDT
    co_so/     cash-and-carry        — cần giá giao ngay của BTC/ETH

Cùng ba sàn, cùng ba hình dạng JSON, hai ty khác HỌ. Để mỗi ty tự viết một
adapter là đúng cái §27 cảnh báo: bốn engine, bốn adapter Binance khác nhau,
và ngày sàn đổi khuôn thì phải sửa bốn chỗ.

Nằm ở `san_chung/` chứ không ở `phai_sinh_chung/`: đỉnh sổ giao ngay không
thuộc riêng họ phái sinh. Adapter funding perp thì có — chúng đọc chu kỳ kết
toán và mốc, hai thứ chỉ phái sinh mới có — nên chúng ở lại
`phai_sinh_chung/san/`.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

from thi_bac_ty.nguon import Nguon, so_hoac_none


@dataclass(frozen=True)
class DinhSo:
    """Đỉnh sổ lệnh của một cặp trên một sàn."""
    san: str
    cap: str
    mua: float          # bid — giá ta BÁN được
    ban: float          # ask — giá ta MUA được
    muaLuong: float | None
    banLuong: float | None
    docLucMs: float = field(default_factory=lambda: time.time() * 1000.0)

    @property
    def giua(self) -> float:
        return (self.mua + self.ban) / 2.0

    @property
    def lechNeoBps(self) -> float:
        """Lệch khỏi neo 1,00 — thước phân biệt sai giá với DEPEG."""
        return abs(self.giua - 1.0) * 10_000.0

    def tuoi_giay(self, nowMs: float | None = None) -> float:
        now = nowMs if nowMs is not None else time.time() * 1000.0
        return (now - self.docLucMs) / 1000.0

    def tom_tat(self) -> dict:
        return {"san": self.san, "cap": self.cap, "mua": self.mua,
                "ban": self.ban, "muaLuong": self.muaLuong,
                "banLuong": self.banLuong, "giua": self.giua,
                "lechNeoBps": self.lechNeoBps, "tuoiGiay": self.tuoi_giay()}


def _ky_hieu(cap: str, san: str) -> str:
    a, b = cap.split("/")
    return f"{a}-{b}" if san == "okx" else f"{a}{b}"


class SanGiaoNgay(Nguon):
    """Ba sàn, mỗi sàn một hình dạng JSON. Lỗi một sàn KHÔNG giết cả lượt."""

    ten = "giao-ngay"

    def __init__(self) -> None:
        super().__init__()
        self.theoSan = {}

    async def doc(self, client, cap=("USDC/USDT",), san=("binance", "okx", "bybit")):
        t0 = time.perf_counter()
        viec = [(s, c) for s in san for c in cap]
        ra = await asyncio.gather(
            *(_mot(client, s, c) for s, c in viec), return_exceptions=True)
        tot, loi = [], []
        for (s, c), x in zip(viec, ra):
            if isinstance(x, BaseException) or x is None:
                loi.append(f"{s}:{c}")
                self.theoSan[s] = f"{type(x).__name__}" if isinstance(
                    x, BaseException) else "trống"
            else:
                tot.append(x)
                self.theoSan[s] = "ok"
        if tot:
            self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        else:
            self.suc_khoe.ghi_loi(RuntimeError("không sàn nào trả lời: "
                                               + ", ".join(loi)))
        return tot

    def tom_tat(self) -> dict:
        return {**self.suc_khoe.tom_tat(), "theoSan": dict(self.theoSan)}


async def _mot(client, san: str, cap: str) -> DinhSo | None:
    k = _ky_hieu(cap, san)
    if san == "binance":
        r = await client.get(
            "https://api.binance.com/api/v3/ticker/bookTicker", params={"symbol": k})
        r.raise_for_status()
        d = r.json()
        return _dung(san, cap, d.get("bidPrice"), d.get("askPrice"),
                     d.get("bidQty"), d.get("askQty"))
    if san == "okx":
        r = await client.get("https://www.okx.com/api/v5/market/ticker",
                             params={"instId": k})
        r.raise_for_status()
        d = (r.json().get("data") or [{}])[0]
        return _dung(san, cap, d.get("bidPx"), d.get("askPx"),
                     d.get("bidSz"), d.get("askSz"))
    if san == "bybit":
        r = await client.get("https://api.bybit.com/v5/market/tickers",
                             params={"category": "spot", "symbol": k})
        r.raise_for_status()
        d = ((r.json().get("result") or {}).get("list") or [{}])[0]
        return _dung(san, cap, d.get("bid1Price"), d.get("ask1Price"),
                     d.get("bid1Size"), d.get("ask1Size"))
    return None


def _dung(san, cap, mua, ban, ml, bl) -> DinhSo | None:
    m, b = so_hoac_none(mua), so_hoac_none(ban)
    # Giá ≤ 0 hoặc bid > ask là sổ lệnh hỏng, không phải cơ hội ngược đời.
    if m is None or b is None or m <= 0 or b <= 0 or m > b:
        return None
    return DinhSo(san, cap, m, b, so_hoac_none(ml), so_hoac_none(bl))
