"""FEATURE FACTORY — biến nến thô thành một bảng số CÓ TÊN.

Ranh giới quan trọng: file này không kết luận gì cả, nó chỉ ĐO. Việc gán nhãn
("đang uptrend") nằm ở regime.py, việc suy luận nằm ở brain.py. Trộn ba tầng đó
vào nhau là cách chắc chắn nhất để sau này không ai lần lại được vì sao bot vào lệnh.
"""
from __future__ import annotations

from typing import Optional, Sequence

from . import indicators as ind
from . import mau_gia
from .indicators import last


def _r(v: Optional[float], n: int = 2) -> Optional[float]:
    return None if v is None else round(v, n)


def _rg(v: Optional[float], cs: int = 8) -> Optional[float]:
    """Làm tròn GIÁ theo CHỮ SỐ CÓ NGHĨA, không theo chữ số thập phân.

    `_r(v, 2)` đúng cho BTC (77.584,67) và phá huỷ mọi thứ dưới một đô:

        LINKUSDT  12,34        → 12,34        đúng
        VETUSDT    0,00679     → 0,01         sai 47%
        GALAUSDT   0,00182     → 0,0          CHIA CHO KHÔNG
        SHIBUSDT   0,00000517  → 0,0          CHIA CHO KHÔNG

    Bot chỉ chạy BTCUSDT nên chuyện này chưa từng lộ ra. Nó lộ đúng lúc mở
    bảng đo sang 48 chợ: `mock_thesis` chia `atr / price` và nổ ZeroDivision ở
    GALAUSDT. Cái nổ là phần MAY — với VET thì không nổ, chỉ là mọi con số dẫn
    xuất (khoảng cách tới hỗ trợ, ATR%, điểm vào, stop, mục tiêu) sai 47% mà
    bảng vẫn xanh.

    Tám chữ số có nghĩa: BTC 77.584,67 giữ nguyên tới xu (6 chữ số là mất phần
    xu), SHIB giữ tới 1e-13. Rộng hơn mức cần, và rộng ở đây không tốn gì.
    """
    if v is None or v == 0:
        return v
    import math

    return round(v, -int(math.floor(math.log10(abs(v)))) + (cs - 1))

def _slope(arr: Sequence[Optional[float]], n: int) -> Optional[float]:
    d = [x for x in arr if x is not None]
    if len(d) < n + 1:
        return None
    return (d[-1] - d[-1 - n]) / n


def _stack(a, b, c) -> str:
    if None in (a, b, c):
        return "UNKNOWN"
    if a > b > c:
        return "BULLISH_ALIGNED"
    if a < b < c:
        return "BEARISH_ALIGNED"
    return "MIXED"


def features_for(candles: list[dict]) -> dict:
    closes = [c["c"] for c in candles]
    vols = [c["v"] for c in candles]
    price = closes[-1]

    ema20, ema50, ema200 = ind.ema(closes, 20), ind.ema(closes, 50), ind.ema(closes, 200)
    rsi14 = ind.rsi(closes, 14)
    m = ind.macd(closes)
    atr14 = ind.atr(candles, 14)
    adx_all = ind.adx(candles, 14)
    bb = ind.bbands(closes, 20, 2)
    vol = ind.volatility_state(atr14, closes)
    struct = ind.market_structure(candles, 2)
    sr = ind.support_resistance(candles, price)

    vol_sma = ind.sma(vols, 20)
    vol_ratio = (vols[-1] / last(vol_sma)) if last(vol_sma) else None

    up, lo = last(bb["upper"]), last(bb["lower"])
    bb_pos = ((price - lo) / (up - lo)) if (up is not None and lo is not None and up != lo) else None

    window = candles[-21:-1] if len(candles) > 21 else candles[:-1]
    hi20 = max(c["h"] for c in window)
    lo20 = min(c["l"] for c in window)

    return {
        "price": _rg(price),
        "ema20": _rg(last(ema20)), "ema50": _rg(last(ema50)),
        "ema200": _rg(last(ema200)),
        "emaStack": _stack(last(ema20), last(ema50), last(ema200)),
        "rsi14": _r(last(rsi14), 1), "rsiSlope": _r(_slope(rsi14, 3), 2),
        "macdHist": _r(last(m["hist"])), "macdHistSlope": _r(_slope(m["hist"], 3), 3),
        "atr": _rg(last(atr14)), "atrPct": _r(vol["atrPct"], 3),
        "atrRatioVsMedian": _r(vol["ratio"], 2), "volatility": vol["label"],
        "adx": _r(last(adx_all["adx"]), 1),
        "plusDI": _r(last(adx_all["plusDI"]), 1), "minusDI": _r(last(adx_all["minusDI"]), 1),
        "bbWidthPct": _rg(last(bb["width"])), "bbPosition": _r(bb_pos, 2),
        "volumeRatio": _r(vol_ratio, 2),
        "structure": struct["label"],
        "swingHighs": [_rg(s["price"]) for s in struct["swingHighs"]],
        "swingLows": [_rg(s["price"]) for s in struct["swingLows"]],
        "support": [{"price": _rg(z["price"]), "touches": z["touches"]}
                    for z in sr["support"]],
        "resistance": [{"price": _rg(z["price"]), "touches": z["touches"]}
                       for z in sr["resistance"]],
        # MẪU GIÁ đã xác nhận tại nến này. Đưa vào feature chứ không để chiến
        # lược tự gọi, vì (a) nó là thứ ĐO ĐƯỢC từ thị trường, đúng chỗ của
        # features.py, và (b) mọi bộ luật rồi mọi bản chạy lại đều nhìn cùng
        # một danh sách — nếu mỗi nơi tự nhận diện thì sớm muộn hai nơi lệch
        # nhau, và backtest sẽ đo một thứ khác với bản chạy thật.
        "mauGia": mau_gia.tom_tat(mau_gia.nhan_dien(candles)),
        "range20High": _rg(hi20), "range20Low": _rg(lo20),
        "distToRange20HighPct": _r((hi20 - price) / price * 100, 2),
        "distToRange20LowPct": _r((price - lo20) / price * 100, 2),
        # _raw giữ số chưa làm tròn cho Risk Engine — làm tròn rồi tính size là
        # tự thêm sai số vào đúng chỗ không được phép có sai số.
        "_raw": {"atr": last(atr14), "adx": last(adx_all["adx"]), "ema20": last(ema20),
                 "ema50": last(ema50), "ema200": last(ema200)},
    }


def build_market_state(market: dict) -> dict:
    """Gộp feature của mọi khung thành một MARKET STATE duy nhất."""
    tfs = {tf: features_for(c) for tf, c in market["timeframes"].items()}
    return {
        "symbol": market["symbol"],
        "price": market["price"],
        "source": market["source"],
        "timeframes": tfs,
    }
