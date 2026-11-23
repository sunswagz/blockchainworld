"""Offline fixtures for Uniswap V3 position valuation and HODL comparison."""
from __future__ import annotations
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lp_intelligence.performance import amounts_for_liquidity, compare_to_hodl, value_position
from lp_intelligence.storage import SQLiteStore


def main() -> int:
    checks = 0
    def check(label, condition):
        nonlocal checks
        if not condition:
            raise AssertionError(label)
        checks += 1
        print("  ✓", label)

    q96 = 1 << 96
    a0, a1 = amounts_for_liquidity(10**18, q96, -100, 100, 18, 18)
    check("in-range position contains both tokens", a0 > 0 and a1 > 0)
    below0, below1 = amounts_for_liquidity(10**18, q96, 100, 200, 18, 18)
    check("below-range position is token0 only", below0 > 0 and below1 == 0)
    above0, above1 = amounts_for_liquidity(10**18, q96, -200, -100, 18, 18)
    check("above-range position is token1 only", above0 == 0 and above1 > 0)

    value = value_position(
        liquidity_raw=10**18, sqrt_price_x96=q96, tick_lower=-100, tick_upper=100,
        decimals0=18, decimals1=18, fees0_raw=10**15, fees1_raw=2*10**15,
        price0_usd=Decimal("2000"), price1_usd=Decimal("1"),
    )
    check("principal and unclaimed fees are valued separately",
          Decimal(value["principal_usd"]) > 0 and Decimal(value["unclaimed_fees_usd"]) > 0)
    baseline = compare_to_hodl(
        current_principal_usd=Decimal("100"), current_fees_usd=Decimal("0"),
        current_price0_usd=Decimal("1"), current_price1_usd=Decimal("1"),
        initial_amount0=Decimal("60"), initial_amount1=Decimal("40"),
        initial_capital_usd=Decimal("100"),
    )
    check("HODL comparison is zero at unchanged prices",
          Decimal(baseline["il_vs_hodl_usd"]) == 0 and Decimal(baseline["pnl_before_claimed_fees_and_costs_usd"]) == 0)
    with tempfile.TemporaryDirectory() as tmp:
        store = SQLiteStore(Path(tmp) / "perf.sqlite")
        store.initialize()
        store.add_token_price_observation({
            "chain_id": "8453", "token_address": "0x" + "1"*40,
            "price_usd": 1.0, "observed_at": "2026-11-22T00:00:00Z",
            "fetched_at": "2026-11-22T00:00:01Z", "source": "fixture",
            "source_url": "https://example.invalid", "data_status": "fresh",
        })
        price = store.latest_token_price("8453", "0x" + "1"*40)
        check("token USD price observations persist with provenance", price is not None and price["source"] == "fixture")
    print(f"LP performance fixtures passed: {checks}/{checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
