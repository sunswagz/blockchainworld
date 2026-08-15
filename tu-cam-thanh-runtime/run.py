"""Điểm khởi động.

    python run.py                     # brain auto (có khoá thì dùng Claude)
    python run.py --brain=mock        # không gọi API, không tốn tiền
    python run.py --symbol=ETHUSDT --port=5231
"""
from __future__ import annotations

import uvicorn

from trader.config import CONFIG, brain_mode


def main() -> None:
    port = CONFIG["port"]
    mode = brain_mode()
    print("=" * 74)
    print("  CLAUDE TRADER — M0")
    print(f"  cặp {CONFIG['symbol']} · khung {CONFIG['timeframes']['primary']}+{CONFIG['timeframes']['context']}"
          f" · vòng {CONFIG['loopSeconds']}s")
    print(f"  brain: {mode.upper()}" + ("" if mode == "claude" else "  (không gọi API — đặt ANTHROPIC_API_KEY để bật)"))
    print(f"  rủi ro tối đa mỗi lệnh: {CONFIG['risk']['maxRiskPerTradePct']}%"
          f" · trần lỗ ngày {CONFIG['risk']['maxDailyLossPct']}%"
          f" · kill switch drawdown {CONFIG['risk']['maxDrawdownPct']}%")
    print(f"  hạn mức model: ${CONFIG['brain']['dailyBudgetUsd']}/ngày, {CONFIG['brain']['maxCallsPerDay']} lượt")
    print(f"\n  dashboard →  http://localhost:{port}\n")
    print("  TIỀN GIẢ. Sàn giấy. Đừng nối vào tài khoản thật ở mốc này.")
    print("=" * 74)
    uvicorn.run("trader.server:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
