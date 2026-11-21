"""Pure mathematical helpers. No provider calls and no execution code."""
from __future__ import annotations

import math


def impermanent_loss_v2(price_ratio: float) -> float:
    """50/50 constant-product IL as a fraction vs HODL.

    ONLY applies to standard V2-style pools. Never use for V3/V4 positions.
    """
    if not math.isfinite(price_ratio) or price_ratio <= 0:
        raise ValueError("price_ratio must be finite and greater than zero")
    return (2.0 * math.sqrt(price_ratio) / (1.0 + price_ratio)) - 1.0


def concentrated_range_status(price: float, lower: float, upper: float) -> tuple[str, float | None]:
    """Return range status and distance to nearest edge in percent.

    Distance is positive inside range and negative outside.
    """
    if not all(math.isfinite(x) for x in (price, lower, upper)):
        raise ValueError("prices must be finite")
    if price <= 0 or lower <= 0 or upper <= lower:
        raise ValueError("require 0 < lower < upper and price > 0")
    if price < lower:
        return "below_range", -((lower - price) / price) * 100.0
    if price > upper:
        return "above_range", -((price - upper) / price) * 100.0
    distance = min((price - lower) / price, (upper - price) / price) * 100.0
    return "in_range", distance


def fee_coverage_ratio(
    realized_fees_usd: float | None,
    estimated_il_usd: float | None,
    gas_usd: float | None,
    rebalance_cost_usd: float | None = 0.0,
) -> float | None:
    """Fees divided by modeled loss/costs; None if a required input is unknown."""
    values = (realized_fees_usd, estimated_il_usd, gas_usd, rebalance_cost_usd)
    if any(v is None for v in values):
        return None
    if any(not math.isfinite(v) for v in values if v is not None):
        raise ValueError("inputs must be finite")
    denominator = abs(estimated_il_usd) + gas_usd + (rebalance_cost_usd or 0.0)
    if denominator <= 0:
        return None
    return realized_fees_usd / denominator


def observed_fee_apr_pct(
    fees_usd: float | None,
    average_capital_usd: float | None,
    elapsed_hours: float | None,
) -> tuple[float | None, str]:
    """Annualize observed fees and label short windows explicitly."""
    if fees_usd is None or average_capital_usd is None or elapsed_hours is None:
        return None, "missing_inputs"
    if not all(math.isfinite(v) for v in (fees_usd, average_capital_usd, elapsed_hours)):
        raise ValueError("inputs must be finite")
    if fees_usd < 0 or average_capital_usd <= 0 or elapsed_hours <= 0:
        raise ValueError("fees must be >= 0, capital and elapsed_hours > 0")
    apr = (fees_usd / average_capital_usd) * (8760.0 / elapsed_hours) * 100.0
    return apr, ("short_window" if elapsed_hours < 72.0 else "observed_window")
