"""Offline self-test for LP Intelligence foundation.

Run from thi-bac-ty-runtime:
    python scripts/kiem-lp-intelligence.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.contracts import AlertEvent, Observation, PoolSnapshot, PositionSnapshot
from lp_intelligence.metrics import (
    concentrated_range_status, fee_coverage_ratio,
    impermanent_loss_v2, observed_fee_apr_pct,
)
from lp_intelligence.storage import SQLiteStore

NOW = "2026-11-22T00:00:00Z"
COUNT = 0


def check(label: str, condition: bool) -> None:
    global COUNT
    if not condition:
        raise AssertionError(label)
    COUNT += 1
    print("  ✓", label)


def main() -> int:
    check("V2 IL is zero at unchanged price", abs(impermanent_loss_v2(1.0)) < 1e-12)
    check("V2 IL is negative after 2x relative move", impermanent_loss_v2(2.0) < 0)
    check("V2 IL is symmetric for reciprocal price ratio",
          abs(impermanent_loss_v2(2.0) - impermanent_loss_v2(0.5)) < 1e-12)

    status, edge = concentrated_range_status(100.0, 90.0, 110.0)
    check("concentrated range reports in-range", status == "in_range" and edge is not None and edge > 0)
    status, edge = concentrated_range_status(80.0, 90.0, 110.0)
    check("concentrated range reports below-range", status == "below_range" and edge is not None and edge < 0)

    check("fee coverage is unknown if required input is missing",
          fee_coverage_ratio(12.0, None, 1.0) is None)
    check("fee coverage uses absolute IL plus gas",
          fee_coverage_ratio(12.0, 4.0, 2.0) == 2.0)

    apr, quality = observed_fee_apr_pct(1.0, 100.0, 24.0)
    check("short-window APR is labeled", apr is not None and quality == "short_window")
    check("unknown APR inputs remain unknown",
          observed_fee_apr_pct(None, 100.0, 24.0)[0] is None)

    obs = Observation("tvl", None, "USD", "fixture", "https://example.invalid",
                      NOW, NOW, status="missing", reason="fixture has no TVL")
    obs.validate()
    check("missing observation uses None, not zero", obs.value is None)

    rejected = False
    try:
        Observation("tvl", 0.0, "USD", "fixture", "https://example.invalid",
                    NOW, NOW, status="missing", reason="missing").validate()
    except ValueError:
        rejected = True
    check("missing observation cannot be encoded as zero", rejected)

    pool = PoolSnapshot(
        pool_id="base:uniswap-v3:eth-usdc:500", chain_id="8453", chain_name="Base",
        protocol="Uniswap", version="V3", pool_address="0x" + "1" * 40,
        token0_address="0x" + "2" * 40, token0_symbol="USDC",
        token1_address="0x" + "3" * 40, token1_symbol="WETH",
        observed_at=NOW, fetched_at=NOW, source="fixture",
        source_url="https://example.invalid/pool", tvl_usd=1_000_000.0,
        volume_24h_usd=250_000.0, fees_24h_usd=750.0, fee_tier_bps=5.0,
    )
    position = PositionSnapshot(
        position_id="fixture-position-1", wallet_address="0x" + "4" * 40,
        chain_id="8453", protocol="Uniswap", version="V3", pool_id=pool.pool_id,
        observed_at=NOW, fetched_at=NOW, source="fixture",
        source_url="https://example.invalid/position", tick_lower=-100,
        tick_upper=100, current_tick=0, principal_usd=500.0,
        unclaimed_fees_usd=0.75, in_range=True,
    )
    pool.validate()
    position.validate()
    check("pool and position contracts validate", True)

    with tempfile.TemporaryDirectory(prefix="lp-intelligence-") as tmp:
        store = SQLiteStore(Path(tmp) / "test.sqlite")
        store.initialize()
        store.add_pool_snapshot(pool)
        store.add_position_snapshot(position)
        store.add_alert(AlertEvent(
            "base:uniswap-v3:eth-usdc:500:range-warning", "warning",
            "Pool range warning", "Fixture warning", NOW,
            evidence=({"source": "fixture"},),
            recommended_checks=("Verify current tick",),
        ))
        check("SQLite persists latest pool", len(store.list_pools()) == 1)
        check("SQLite persists wallet position", len(store.list_positions()) == 1)
        check("SQLite persists alert evidence",
              store.list_alerts()[0]["evidence"][0]["source"] == "fixture")

    print(f"LP Intelligence self-test passed: {COUNT}/{COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
