"""MARKET DATA ENGINE — nến OHLCV công khai, không cần API key của sàn.

Ba nguồn theo thứ tự: data-api.binance.vision → api.binance.com → nến tổng hợp.
Nguồn thứ ba KHÔNG phải để giao dịch. Nó để cả hệ thống vẫn chạy kín vòng khi
mạng chặn Binance — và trạng thái nguồn luôn hiện đỏ trên dashboard, không giấu.
Một bot đọc dữ liệu giả mà không ai biết thì tệ hơn một bot đứng im.
"""
from __future__ import annotations

import math
import random
import time
from typing import Any

import httpx

from .bus import bus
from .config import CONFIG

TF_MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}

_source: dict[str, Any] = {"name": "chưa kết nối", "live": False, "lastOk": None, "lastError": None}
_synth: dict[str, dict] = {}


def data_source() -> dict:
    return dict(_source)


def _parse(rows: list) -> list[dict]:
    # Binance: [openTime, o, h, l, c, v, closeTime, ...]
    # Nến cuối CHƯA ĐÓNG. Giữ lại nhưng đánh dấu: quyết định vào lệnh chỉ được
    # dựa trên nến đã đóng, còn giá hiện tại thì lấy từ nến đang chạy.
    n = len(rows)
    return [
        {
            "t": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]),
            "c": float(r[4]), "v": float(r[5]), "closeTime": int(r[6]), "closed": i < n - 1,
        }
        for i, r in enumerate(rows)
    ]


async def _fetch(client: httpx.AsyncClient, url: str, symbol: str, interval: str, limit: int) -> list[dict]:
    r = await client.get(url, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=12.0)
    r.raise_for_status()
    js = r.json()
    if not isinstance(js, list) or not js:
        raise ValueError("payload rỗng")
    return _parse(js)


def _synthetic(symbol: str, interval: str, limit: int) -> list[dict]:
    """Random walk có cụm biến động — đủ giống thật về HÌNH DẠNG để mọi tầng phía
    sau gặp đúng loại dữ liệu chúng phải xử lý."""
    step = TF_MS.get(interval, 3_600_000)
    key = f"{symbol}:{interval}"
    now = int(time.time() * 1000)
    st = _synth.get(key)
    if st is None:
        price, vol, out = 100_000.0, 0.004, []
        start = now - limit * step
        for i in range(limit):
            vol = max(0.0015, min(0.02, vol + (random.random() - 0.5) * 0.0008))
            drift = math.sin(i / 40) * 0.0009
            o = price
            c = o * (1 + drift + (random.random() - 0.5) * vol * 2)
            out.append({
                "t": start + i * step, "o": o, "h": max(o, c) * (1 + random.random() * vol),
                "l": min(o, c) * (1 - random.random() * vol), "c": c,
                "v": 100 + random.random() * 900, "closeTime": start + (i + 1) * step - 1, "closed": True,
            })
            price = c
        st = {"candles": out}
        _synth[key] = st

    while st["candles"][-1]["t"] + step < now:
        prev = st["candles"][-1]
        o = prev["c"]
        c = o * (1 + (random.random() - 0.5) * 0.008)
        t = prev["t"] + step
        st["candles"].append({
            "t": t, "o": o, "h": max(o, c) * 1.002, "l": min(o, c) * 0.998, "c": c,
            "v": 100 + random.random() * 900, "closeTime": t + step - 1, "closed": True,
        })
        if len(st["candles"]) > limit + 50:
            st["candles"].pop(0)

    out = [dict(x) for x in st["candles"][-limit:]]
    out[-1]["closed"] = False
    return out


async def get_candles(client: httpx.AsyncClient, symbol: str, interval: str, limit: int | None = None) -> list[dict]:
    """Không bao giờ ném lỗi — luôn trả về dữ liệu dùng được, kèm trạng thái nguồn."""
    limit = limit or CONFIG["data"]["candleLimit"]
    for url in CONFIG["data"]["sources"]:
        try:
            candles = await _fetch(client, url, symbol, interval, limit)
            host = httpx.URL(url).host
            if not _source["live"] or _source["name"] != host:
                _source.update(name=host, live=True, lastError=None)
                bus.log("data", "nguon-song", f"dữ liệu thật từ {host}")
            _source["lastOk"] = time.strftime("%H:%M:%S")
            return candles
        except Exception as e:  # noqa: BLE001 — nguồn nào hỏng cũng chỉ là lý do thử nguồn kế
            _source["lastError"] = f"{httpx.URL(url).host}: {type(e).__name__}: {e}"

    if _source["live"] or _source["name"] != "tổng hợp":
        _source.update(name="tổng hợp", live=False)
        bus.log("data", "nguon-tong-hop",
                f"không với tới sàn ({_source['lastError']}) — chuyển sang nến TỔNG HỢP, đừng tin kết quả")
    return _synthetic(symbol, interval, limit)


async def get_market_data(client: httpx.AsyncClient, symbol: str | None = None) -> dict:
    symbol = symbol or CONFIG["symbol"]
    primary = CONFIG["timeframes"]["primary"]
    context = CONFIG["timeframes"]["context"]
    p = await get_candles(client, symbol, primary)
    ctx = await get_candles(client, symbol, context)
    price = p[-1]["c"]
    bus.emit("data", "candles",
             f"{symbol} {primary}={len(p)} nến · {context}={len(ctx)} nến · giá {price:,.2f}",
             price=price, source=_source["name"], live=_source["live"])
    return {
        "symbol": symbol,
        "price": price,
        "timeframes": {primary: p, context: ctx},
        "source": data_source(),
        "lastClosedCandleTime": p[-2]["t"] if len(p) > 1 else p[-1]["t"],
    }


# ── NẾN QUÁ CŨ ────────────────────────────────────────────────────────────────
#
# MKRUSDT ngừng cập nhật 15/09/2025 (đổi tên sang SKY). File của nó vẫn đủ 1500
# nến, vẫn đọc được, vẫn qua mọi phép đếm — và đóng góp vào bảng gộp một cửa sổ
# "ngoài mẫu" kết thúc từ một năm trước. Không gì đỏ lên.
#
# Luật ấy đã được viết BA LẦN, chép tay, ở `dau-chien-luoc.py`, `lo-luyen.py`,
# `do-huong.py` — và THIẾU HẲN ở `do-khung.py` với `do-mau-gia.py`. Một luật
# nằm ở ba bản sao thì nó không phải luật, nó là ba thói quen trùng nhau.
#
# ĐẾM THEO NẾN, KHÔNG THEO NGÀY
#
# Ngưỡng 30 ngày phẳng đúng cho 1d và quá lỏng cho mọi khung dưới nó: 30 ngày
# trên 5m là 8.640 nến thiếu, mà phép kiểm vẫn xanh. Nên ngưỡng đếm bằng NẾN
# rồi mới quy ra ngày, có chặn trên chặn dưới:
#
#     1d → 60 ngày, ép về trần 30   (đúng bằng luật cũ, không đổi hành vi)
#     4h → 10 ngày
#     5m → 0,2 ngày, ép về sàn 3    (mạng chập vài giờ không được tính là chết)
QUA_CU_NEN = 60
QUA_CU_SAN_NGAY = 3.0
QUA_CU_TRAN_NGAY = 30.0


def tuoi_nen(ds: list[dict], bay_gio_ms: float | None = None) -> float | None:
    """Số NGÀY kể từ nến cuối. `None` khi không có nến nào đọc được mốc thời gian."""
    moc = [x.get("t") or 0 for x in (ds or []) if x.get("t")]
    if not moc:
        return None
    if bay_gio_ms is None:
        bay_gio_ms = time.time() * 1000
    return (bay_gio_ms - max(moc)) / 86_400_000


def han_cu_ngay(tf: str) -> float:
    """Ngưỡng «quá cũ» của một khung, tính bằng ngày."""
    ms = TF_MS.get(tf) or TF_MS["1d"]
    return min(QUA_CU_TRAN_NGAY,
               max(QUA_CU_SAN_NGAY, QUA_CU_NEN * ms / 86_400_000))


def qua_cu(ds: list[dict], tf: str, bay_gio_ms: float | None = None) -> float | None:
    """Trả TUỔI (ngày) nếu chợ đã chết, `None` nếu còn dùng được.

    Trả về tuổi chứ không phải `True`: chỗ gọi luôn cần in ra con số, và một hàm
    trả bool thì chỗ gọi lại đi tính tuổi lần nữa — tức lại có hai bản sao.
    """
    t = tuoi_nen(ds, bay_gio_ms)
    if t is None:
        return None
    return t if t > han_cu_ngay(tf) else None
