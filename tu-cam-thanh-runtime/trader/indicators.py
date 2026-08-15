"""Chỉ báo viết tay, Python thuần.

Mọi hàm trả về LIST CÙNG ĐỘ DÀI với đầu vào, dùng None cho phần chưa đủ dữ liệu.
Giữ căn chỉnh như vậy thì ghép chỉ báo với nến không bao giờ lệch chỉ số — đó là
lỗi âm thầm hay gặp nhất khi tự viết feature engine, và nó không báo gì cả:
chỉ số dịch một ô là bot đọc RSI của nến hôm qua mà tưởng là hôm nay.
"""
from __future__ import annotations

import math
import statistics
from typing import Iterable, Optional, Sequence

Candle = dict  # {t, o, h, l, c, v, closed}
Num = Optional[float]


def _defined(xs: Iterable[Num]) -> list[float]:
    return [x for x in xs if x is not None and not math.isnan(x)]


def last(xs: Sequence) -> Num:
    return xs[-1] if xs else None


def sma(vals: Sequence[float], p: int) -> list[Num]:
    out: list[Num] = [None] * len(vals)
    total = 0.0
    for i, v in enumerate(vals):
        total += v
        if i >= p:
            total -= vals[i - p]
        if i >= p - 1:
            out[i] = total / p
    return out


def ema(vals: Sequence[float], p: int) -> list[Num]:
    out: list[Num] = [None] * len(vals)
    if len(vals) < p:
        return out
    k = 2 / (p + 1)
    prev = sum(vals[:p]) / p
    out[p - 1] = prev
    for i in range(p, len(vals)):
        prev = vals[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def _wilder(vals: Sequence[float], p: int) -> list[Num]:
    out: list[Num] = [None] * len(vals)
    if len(vals) < p:
        return out
    prev = sum(vals[:p]) / p
    out[p - 1] = prev
    for i in range(p, len(vals)):
        prev = (prev * (p - 1) + vals[i]) / p
        out[i] = prev
    return out


def rsi(closes: Sequence[float], p: int = 14) -> list[Num]:
    out: list[Num] = [None] * len(closes)
    if len(closes) < p + 1:
        return out
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(0.0, d))
        losses.append(max(0.0, -d))
    ag, al = _wilder(gains, p), _wilder(losses, p)
    for i in range(len(ag)):
        if ag[i] is None:
            continue
        rs = math.inf if al[i] == 0 else ag[i] / al[i]
        out[i + 1] = 100 - 100 / (1 + rs)
    return out


def macd(closes: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    ef, es = ema(closes, fast), ema(closes, slow)
    line: list[Num] = [
        (ef[i] - es[i]) if (ef[i] is not None and es[i] is not None) else None for i in range(len(closes))
    ]
    d = _defined(line)
    sig_tail = ema(d, signal)
    offset = len(line) - len(d)
    sig: list[Num] = [None] * len(closes)
    for i, v in enumerate(sig_tail):
        if v is not None:
            sig[i + offset] = v
    hist: list[Num] = [
        (line[i] - sig[i]) if (line[i] is not None and sig[i] is not None) else None for i in range(len(closes))
    ]
    return {"line": line, "signal": sig, "hist": hist}


def true_ranges(c: Sequence[Candle]) -> list[Num]:
    tr: list[Num] = [None] * len(c)
    for i in range(1, len(c)):
        tr[i] = max(
            c[i]["h"] - c[i]["l"],
            abs(c[i]["h"] - c[i - 1]["c"]),
            abs(c[i]["l"] - c[i - 1]["c"]),
        )
    return tr


def atr(c: Sequence[Candle], p: int = 14) -> list[Num]:
    tr = [x for x in true_ranges(c)[1:]]
    return [None] + _wilder(tr, p)


def adx(c: Sequence[Candle], p: int = 14) -> dict:
    n = len(c)
    empty = lambda: [None] * n  # noqa: E731
    if n < p * 2 + 2:
        return {"adx": empty(), "plusDI": empty(), "minusDI": empty()}

    plus_dm, minus_dm, tr = [], [], []
    for i in range(1, n):
        up = c[i]["h"] - c[i - 1]["h"]
        dn = c[i - 1]["l"] - c[i]["l"]
        plus_dm.append(up if (up > dn and up > 0) else 0.0)
        minus_dm.append(dn if (dn > up and dn > 0) else 0.0)
        tr.append(max(c[i]["h"] - c[i]["l"], abs(c[i]["h"] - c[i - 1]["c"]), abs(c[i]["l"] - c[i - 1]["c"])))

    atr_s, p_s, m_s = _wilder(tr, p), _wilder(plus_dm, p), _wilder(minus_dm, p)
    p_di, m_di = empty(), empty()
    dx: list[Num] = []
    for i in range(len(atr_s)):
        if atr_s[i] is None or atr_s[i] == 0:
            dx.append(None)
            continue
        pd = (p_s[i] / atr_s[i]) * 100
        md = (m_s[i] / atr_s[i]) * 100
        p_di[i + 1] = pd
        m_di[i + 1] = md
        s = pd + md
        dx.append(0.0 if s == 0 else abs(pd - md) / s * 100)

    d = _defined(dx)
    tail = _wilder(d, p)
    off = len(dx) - len(d)
    adx_arr = empty()
    for i, v in enumerate(tail):
        if v is not None:
            adx_arr[i + off + 1] = v
    return {"adx": adx_arr, "plusDI": p_di, "minusDI": m_di}


def bbands(closes: Sequence[float], p: int = 20, k: float = 2.0) -> dict:
    mid = sma(closes, p)
    upper: list[Num] = [None] * len(closes)
    lower: list[Num] = [None] * len(closes)
    width: list[Num] = [None] * len(closes)
    for i in range(p - 1, len(closes)):
        win = closes[i - p + 1 : i + 1]
        m = mid[i]
        sd = statistics.pstdev(win)
        upper[i] = m + k * sd
        lower[i] = m - k * sd
        width[i] = None if m == 0 else (upper[i] - lower[i]) / m * 100
    return {"mid": mid, "upper": upper, "lower": lower, "width": width}


def swings(c: Sequence[Candle], lr: int = 2) -> dict:
    """Đỉnh/đáy swing xác nhận bằng `lr` nến hai bên."""
    highs, lows = [], []
    for i in range(lr, len(c) - lr):
        is_h = is_l = True
        for j in range(i - lr, i + lr + 1):
            if j == i:
                continue
            if c[j]["h"] >= c[i]["h"]:
                is_h = False
            if c[j]["l"] <= c[i]["l"]:
                is_l = False
        if is_h:
            highs.append({"i": i, "t": c[i]["t"], "price": c[i]["h"]})
        if is_l:
            lows.append({"i": i, "t": c[i]["t"], "price": c[i]["l"]})
    return {"highs": highs, "lows": lows}


def market_structure(c: Sequence[Candle], lr: int = 2) -> dict:
    """HH+HL = uptrend, LH+LL = downtrend, lệch nhau = đang chuyển."""
    s = swings(c, lr)
    h, l = s["highs"][-2:], s["lows"][-2:]
    tail = {"swingHighs": s["highs"][-4:], "swingLows": s["lows"][-4:]}
    if len(h) < 2 or len(l) < 2:
        return {"label": "UNCLEAR", "higherHigh": None, "higherLow": None, **tail}
    hh = h[1]["price"] > h[0]["price"]
    hl = l[1]["price"] > l[0]["price"]
    label = "UPTREND" if (hh and hl) else "DOWNTREND" if (not hh and not hl) else "TRANSITION"
    return {"label": label, "higherHigh": hh, "higherLow": hl, **tail}


def support_resistance(c: Sequence[Candle], price: float, tol_pct: float = 0.35) -> dict:
    """Gom swing gần nhau thành vùng, rồi tách theo phía so với giá hiện tại."""
    s = swings(c, 2)
    pool = sorted(x["price"] for x in (s["highs"][-12:] + s["lows"][-12:]))
    zones: list[dict] = []
    for lvl in pool:
        hit = next((z for z in zones if abs(z["price"] - lvl) / lvl * 100 < tol_pct), None)
        if hit:
            hit["touches"] += 1
            hit["price"] = (hit["price"] * (hit["touches"] - 1) + lvl) / hit["touches"]
        else:
            zones.append({"price": lvl, "touches": 1})
    support = sorted([z for z in zones if z["price"] < price], key=lambda z: -z["price"])[:3]
    resistance = sorted([z for z in zones if z["price"] > price], key=lambda z: z["price"])[:3]
    return {"support": support, "resistance": resistance}


def volatility_state(atr_arr: Sequence[Num], closes: Sequence[float]) -> dict:
    """ATR hiện tại so với trung vị 100 nến — biến động phải TƯƠNG ĐỐI mới có nghĩa."""
    a, c = last(atr_arr), last(closes)
    if a is None or not c:
        return {"atr": None, "atrPct": None, "ratio": None, "label": "UNKNOWN"}
    atr_pct = a / c * 100
    hist = [
        atr_arr[i] / closes[i] * 100
        for i in range(max(0, len(atr_arr) - 100), len(atr_arr))
        if atr_arr[i] is not None and closes[i]
    ]
    med = statistics.median(hist) if hist else None
    ratio = (atr_pct / med) if med else None
    label = "NORMAL"
    if ratio is not None and ratio > 1.5:
        label = "HIGH"
    elif ratio is not None and ratio < 0.65:
        label = "LOW"
    return {"atr": a, "atrPct": atr_pct, "ratio": ratio, "label": label}
