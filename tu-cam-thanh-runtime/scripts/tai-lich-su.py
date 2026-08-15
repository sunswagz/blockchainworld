"""Tải nến lịch sử về đĩa, để chạy lại không phải gọi mạng mỗi lần.

    python scripts/tai-lich-su.py                 # 3000 nến 1h + 4h
    python scripts/tai-lich-su.py --so 6000

Binance trả tối đa 1000 nến một lượt, nên phải phân trang lùi theo `endTime`.
Không phân trang thì "3000 nến" lặng lẽ thành 1000 — và một backtest trên 1000
nến 1h chỉ là 6 tuần, quá ngắn để nói được gì về một chiến lược.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

from trader.config import CONFIG  # noqa: E402

KHO = GOC / "data" / "lich-su"
NGUON = ["https://data-api.binance.vision/api/v3/klines",
         "https://api.binance.com/api/v3/klines"]


def tai(client: httpx.Client, symbol: str, tf: str, so: int) -> list[dict]:
    ra: list[list] = []
    het = None
    while len(ra) < so:
        con = min(1000, so - len(ra))
        tham = {"symbol": symbol, "interval": tf, "limit": con}
        if het:
            tham["endTime"] = het
        lo = None
        for u in NGUON:
            try:
                r = client.get(u, params=tham, timeout=20)
                r.raise_for_status()
                lo = r.json()
                break
            except Exception as e:  # noqa: BLE001
                print(f"    {httpx.URL(u).host}: {type(e).__name__}")
        if not lo:
            break
        ra = lo + ra
        het = int(lo[0][0]) - 1
        print(f"    {tf}: {len(ra)}/{so} nến · tới {time.strftime('%Y-%m-%d', time.gmtime(int(lo[0][0]) / 1000))}")
        if len(lo) < con:
            break
        time.sleep(0.3)

    n = len(ra)
    return [{"t": int(x[0]), "o": float(x[1]), "h": float(x[2]), "l": float(x[3]),
             "c": float(x[4]), "v": float(x[5]), "closeTime": int(x[6]), "closed": i < n - 1}
            for i, x in enumerate(ra)]


def main() -> None:
    so = 3000
    if "--so" in sys.argv:
        so = int(sys.argv[sys.argv.index("--so") + 1])
    symbol = CONFIG["symbol"]
    tfs = [CONFIG["timeframes"]["primary"], CONFIG["timeframes"]["context"]]

    KHO.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True) as c:
        for tf in tfs:
            # Khung ngữ cảnh cần phủ CÙNG khoảng thời gian với khung chính, mà
            # mỗi nến của nó dài hơn — nên số nến ít hơn theo đúng tỉ lệ. Tải
            # bằng số nến cho cả hai là khung ngữ cảnh phủ dài gấp bốn lần một
            # cách vô ích, còn ngược lại thì thiếu ngay chỗ cần.
            n = so if tf == tfs[0] else max(400, so // 4 + 250)
            print(f"  {symbol} {tf} — cần {n} nến")
            nen = tai(c, symbol, tf, n)
            f = KHO / f"{symbol}-{tf}.json"
            f.write_text(json.dumps(nen), encoding="utf-8")
            d0 = time.strftime("%Y-%m-%d", time.gmtime(nen[0]["t"] / 1000))
            d1 = time.strftime("%Y-%m-%d", time.gmtime(nen[-1]["t"] / 1000))
            print(f"  → {f.name}: {len(nen)} nến, {d0} … {d1}\n")


if __name__ == "__main__":
    main()
