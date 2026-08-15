"""Thử NGUYÊN đường ống vào lệnh trên testnet, một lần, rồi đóng lại.

    python scripts/thu-mot-lenh.py --that

Khác `kiem-testnet.py`: chỗ kia chỉ mua-bán trần để kiểm chữ ký và bộ lọc. Chỗ
này đi qua ĐÚNG các tầng mà runtime thật đi qua — dữ liệu → feature → regime →
Risk Engine → TestnetBroker → OCO trên sổ sàn → đóng — nên nó bắt được những
chỗ chỉ hỏng khi ghép lại.

Cỡ lệnh: Risk Engine tính ra cỡ THẬT, nhưng script gửi đi một cỡ nhỏ (~$40) để
không chiếm hết số dư testnet cho một phép thử. Cả hai số đều in ra, đừng nhầm.

Không có cờ `--that` thì chỉ tính rồi in, KHÔNG gửi lệnh nào.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

from trader.broker_testnet import TestnetBroker  # noqa: E402
from trader.config import CONFIG  # noqa: E402
from trader.data import get_market_data  # noqa: E402
from trader.features import build_market_state  # noqa: E402
from trader.regime import classify  # noqa: E402
from trader.risk import RiskEngine  # noqa: E402

THAT = "--that" in sys.argv
NOTIONAL_THU = 40.0   # USD — đủ trên minNotional $5, đủ nhỏ để không chiếm số dư


async def main() -> int:
    pri = CONFIG["timeframes"]["primary"]
    ctx = CONFIG["timeframes"]["context"]

    print("\n[1] DỮ LIỆU + FEATURE + REGIME")
    async with httpx.AsyncClient() as c:
        m = await get_market_data(c)
    st = build_market_state(m)
    rg = classify(st, pri, ctx)
    f = st["timeframes"][pri]
    atr = f["_raw"]["atr"]
    price = st["price"]
    print(f"    giá {price:,.2f} · ATR {atr:.2f} ({atr / price * 100:.3f}%) · regime {rg['primary']}/{rg['quality']}")

    print("\n[2] SÀN")
    broker = TestnetBroker(CONFIG["risk"], CONFIG["symbol"])
    if not broker.ready:
        print(f"    KHÔNG nối được: {broker.last_error}")
        return 1
    acct = broker.snapshot(price)
    print(f"    vốn ${acct['equity']:,.2f} · mua được ${acct['availableQuote']:,.2f} · "
          f"vị thế mở {len(acct['positions'])}")
    for c_ in broker.doi_soat():
        print(f"    ⚠ {c_}")

    print("\n[3] LUẬN ĐIỂM (dựng tay, không gọi model)")
    r = CONFIG["risk"]
    drag = price * (r["feeBps"] + r["slippageBps"]) / 10_000
    stop_that = 1.5 * atr + drag
    k1 = (r["minRR"] * stop_that + drag) / atr * 1.05
    thesis = {
        "action": "LONG", "confidence": 0.75,
        "entry_zone": [price * 0.999, price * 1.001],
        "invalidation": round(price - 1.5 * atr, 2),
        "targets": [round(price + k1 * atr, 2)],
        "suggested_risk_pct": r["maxRiskPerTradePct"],
        "strategy": "THU_MOT_LENH", "reason_codes": ["THU_TAY"],
        "reasoning": "Lệnh thử đường ống, không phải tín hiệu.",
        "symbol": CONFIG["symbol"],
    }
    print(f"    LONG · SL {thesis['invalidation']:,.2f} (1.5×ATR) · TP {thesis['targets'][0]:,.2f} ({k1:.2f}×ATR)")

    print("\n[4] RISK ENGINE")
    risk = RiskEngine(CONFIG["risk"], spot_only=True)
    d = risk.evaluate(thesis, st, acct, atr)
    if not d["approved"]:
        print(f"    CHẶN: {d['rejections']}")
        return 1
    p = d["position"]
    print(f"    CHO QUA · RR {p['rr']} · rủi ro ${p['riskAmount']} ({p['riskPct']}%)")
    print(f"    cỡ thật: {p['qty']:.6f} BTC = ${p['notional']:,.2f}"
          + ("  (đã cắt theo tiền mua được)" if p["notionalCapped"] else ""))

    p_thu = dict(p)
    p_thu["qty"] = NOTIONAL_THU / p["entry"]
    p_thu["notional"] = NOTIONAL_THU
    p_thu["riskAmount"] = round(abs(p["entry"] - p["stopLoss"]) * p_thu["qty"], 2)
    print(f"    cỡ GỬI ĐI: {p_thu['qty']:.6f} BTC = ${NOTIONAL_THU:.2f} (thu nhỏ cho phép thử)")

    if not THAT:
        print("\n    (chưa gửi lệnh nào — thêm --that để gửi thật)")
        return 0

    print("\n[5] VÀO LỆNH THẬT + OCO")
    t = broker.open(p_thu, thesis, rg)
    if not t:
        print("    KHÔNG vào được — xem log ở trên")
        return 1
    print(f"    vào {t['qty']:.6f} @ {t['entry']:,.2f} · OCO listId {t['ocoOrderListId']}")
    if t.get("ocoError"):
        print(f"    ⚠ OCO lỗi: {t['ocoError']}")

    treo = broker.client.open_orders(CONFIG["symbol"])
    print(f"\n[6] LỆNH TREO TRÊN SÀN: {len(treo)}")
    for o in treo:
        print(f"    {o['side']:<4} {o['type']:<18} KL {o['origQty']} "
              f"giá {o.get('price')} stop {o.get('stopPrice')}")
    if len(treo) != 2:
        print("    ⚠ OCO đúng ra phải để lại 2 lệnh (chốt lãi + cắt lỗ)")

    print("\n[7] ĐÓNG LẠI (huỷ OCO + bán MARKET)")
    done = broker.close(t, price, "THU_XONG")
    print(f"    đóng @ {done['exit']:,.2f} · PnL ${done['pnl']:+,.2f} ({done['rMultiple']:+}R)")

    con = broker.client.open_orders(CONFIG["symbol"])
    print(f"    lệnh treo còn lại: {len(con)} (phải là 0)")
    sau = broker.snapshot(price)
    print(f"    vốn sau: ${sau['equity']:,.2f} · vị thế mở {len(sau['positions'])}")

    print("\n" + "=" * 62)
    print("  ĐI HẾT ĐƯỜNG ỐNG: regime → risk → MARKET → OCO → đóng → nhật ký")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
