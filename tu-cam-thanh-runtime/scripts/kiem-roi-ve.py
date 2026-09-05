"""Kiểm đường RƠI VỀ PAPER khi khai testnet mà không nối được.

    python scripts/kiem-roi-ve.py

Đây là phép kiểm về một hành vi AN TOÀN, không phải về tính năng: khai
`mode: testnet` mà thiếu khoá thì runtime phải chạy tiếp bằng sàn giấy **và nói
to là nó đang làm vậy**. Rơi về im lặng là kiểu hỏng tệ nhất trong cả hệ thống —
mọi con số trên dashboard vẫn đẹp, chỉ là chúng không tương ứng với lệnh nào có
thật trên sàn, và không có gì báo.

Không sửa config.json: nó tạm đổi CONFIG trong bộ nhớ rồi dựng lại Runtime.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# KHÔNG BAO GIỜ chạm sổ thật. GHI ĐÈ, không `setdefault`: một dòng
# `export TCT_DATA_DIR=` trong shell là đủ để setdefault không làm gì, và
# chuyện đó đã sập BA lần ở repo này — lần nặng nhất là bộ kiểm cửa duyệt đưa
# một champion GIẢ lên ngôi trong sổ chiến lược thật.
import os
from _tam_tu_don import tam_moi

os.environ["TCT_DATA_DIR"] = tam_moi("tct-kiem-")

from trader import bus as bus_mod  # noqa: E402
from trader.config import CONFIG  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("  OK   " if cond else "  SAI  ") + label)
    if not cond:
        FAILS.append(label)


def main() -> int:
    import os

    # Giả lập "khai testnet nhưng không có khoá"
    CONFIG["mode"] = "testnet"
    for k in ("BINANCE_TESTNET_KEY", "BINANCE_TESTNET_SECRET"):
        os.environ.pop(k, None)

    from trader.loop import Runtime

    print("\n[1] KHAI testnet, KHÔNG có khoá")
    truoc = len(bus_mod.bus.ring)
    rt = Runtime()
    su_kien = bus_mod.bus.ring[truoc:]

    check(rt.mode == "paper", f"đã rơi về sàn giấy (mode = {rt.mode})")
    check(getattr(rt.broker, "kind", "paper") == "paper", "broker đang là PaperBroker")
    check(rt.risk.spot_only is False, "spot_only tắt lại theo — sàn giấy short được")

    tieng_on = [e for e in su_kien if e["type"] in ("roi-ve-paper", "testnet-thieu-khoa")]
    check(len(tieng_on) >= 2,
          f"có {len(tieng_on)} sự kiện cảnh báo — rơi về KHÔNG được im lặng")
    for e in tieng_on:
        print(f"       [{e['stage']}] {e['type']}: {e['msg'][:100]}")

    print("\n[2] KHAI paper — không đụng gì tới mạng sàn")
    CONFIG["mode"] = "paper"
    rt2 = Runtime()
    check(rt2.mode == "paper" and getattr(rt2.broker, "kind", "paper") == "paper",
          "chạy thẳng sàn giấy, không thử nối testnet")

    print("\n[3] SPOT KHÔNG SHORT ĐƯỢC")
    from trader.risk import RiskEngine

    r = RiskEngine(CONFIG["risk"], spot_only=True)
    d = r.evaluate({"action": "SHORT", "confidence": 0.9, "invalidation": 100,
                    "targets": [80], "entry_zone": None, "suggested_risk_pct": 0.5},
                   {"price": 90, "symbol": "BTCUSDT"},
                   {"equity": 10000, "positions": [], "peakEquity": 10000}, 1.0)
    check(not d["approved"] and any("SPOT_KHONG_SHORT" in x for x in d["rejections"]),
          f"luận điểm SHORT bị chặn: {d['rejections']}")

    r2 = RiskEngine(CONFIG["risk"], spot_only=False)
    d2 = r2.evaluate({"action": "SHORT", "confidence": 0.9, "invalidation": 100,
                      "targets": [80], "entry_zone": None, "suggested_risk_pct": 0.5},
                     {"price": 90, "symbol": "BTCUSDT"},
                     {"equity": 10000, "positions": [], "peakEquity": 10000}, 1.0)
    check(not any("SPOT_KHONG_SHORT" in x for x in d2["rejections"]),
          "sàn giấy KHÔNG chặn SHORT (luật chỉ áp cho spot)")

    print("\n" + "=" * 62)
    if FAILS:
        print(f"  {len(FAILS)} PHÉP KIỂM SAI:")
        for x in FAILS:
            print("   - " + x)
        return 1
    print("  ĐƯỜNG RƠI VỀ AN TOÀN VÀ ỒN ÀO ĐÚNG MỨC.")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
