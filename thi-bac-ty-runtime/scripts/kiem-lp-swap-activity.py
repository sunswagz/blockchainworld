"""Offline fixtures for Uniswap V3 Swap event activity accounting."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.swap_activity import SWAP_TOPIC, collect_swap_activity, decode_swap_log


def word(value: int) -> str:
    return format(value % (1 << 256), "064x")


class FakeRpc:
    def __init__(self, logs):
        self.logs = logs

    def get_block(self, number):
        return {"timestamp": hex(100000 + number * 2)}

    def get_logs(self, *, address, from_block, to_block, topics):
        assert topics == [SWAP_TOPIC]
        return self.logs


def main() -> int:
    # 1 WETH enters the pool; 2,000 USDC leaves. 0.05% fee = 0.0005 WETH = $1.
    log = {"data": "0x" + word(10**18) + word(-2_000 * 10**6) + word(1) + word(2) + word(3)}
    assert decode_swap_log(log) == (10**18, -2_000 * 10**6)
    result = collect_swap_activity(
        FakeRpc([log]), pool_address="0x" + "a" * 40, fee_tier=500,
        token0_usd=2000.0, token1_usd=1.0, token0_decimals=18, token1_decimals=6,
        now_timestamp=200000, latest_block=10, chunk_size=5,
    )
    assert result["swap_count"] == 1
    assert abs(result["volume_usd_estimated"] - 2000.0) < 1e-9
    assert abs(result["fees_usd_estimated"] - 1.0) < 1e-9
    assert result["fee_token0_raw_estimated"] == "500000000000000"
    print("LP swap activity fixtures passed: 5/5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
