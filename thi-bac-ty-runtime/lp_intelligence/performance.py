"""Uniswap V3 position valuation and performance math.

HODL comparison starts at the first recorded valuation snapshot, not NFT mint.
USD outputs require explicit token price observations. This module does not
invent prices, claimed fees, gas costs or historical data.
"""
from __future__ import annotations

from decimal import Decimal, getcontext
from typing import Any

getcontext().prec = 50
Q96 = Decimal(2) ** 96


def amounts_for_liquidity(
    liquidity_raw: int, sqrt_price_x96: int, tick_lower: int, tick_upper: int,
    decimals0: int, decimals1: int,
) -> tuple[Decimal, Decimal]:
    if liquidity_raw < 0 or sqrt_price_x96 <= 0:
        raise ValueError("liquidity must be >= 0 and sqrt price must be > 0")
    if tick_lower >= tick_upper or not (0 <= decimals0 <= 255 and 0 <= decimals1 <= 255):
        raise ValueError("invalid ticks or token decimals")
    sqrt_p = Decimal(sqrt_price_x96) / Q96
    base = Decimal("1.0001")\n    sqrt_a = base ** (Decimal(tick_lower) / 2)\n    sqrt_b = base ** (Decimal(tick_upper) / 2)
    liquidity = Decimal(liquidity_raw)
    if sqrt_p <= sqrt_a:
        amount0 = liquidity * (sqrt_b - sqrt_a) / (sqrt_a * sqrt_b)
        amount1 = Decimal(0)
    elif sqrt_p < sqrt_b:
        amount0 = liquidity * (sqrt_b - sqrt_p) / (sqrt_p * sqrt_b)
        amount1 = liquidity * (sqrt_p - sqrt_a)
    else:
        amount0 = Decimal(0)
        amount1 = liquidity * (sqrt_b - sqrt_a)
    return amount0 / (Decimal(10) ** decimals0), amount1 / (Decimal(10) ** decimals1)


def value_position(
    *, liquidity_raw: int, sqrt_price_x96: int, tick_lower: int, tick_upper: int,
    decimals0: int, decimals1: int, fees0_raw: int, fees1_raw: int,
    price0_usd: Decimal, price1_usd: Decimal,
) -> dict[str, Any]:
    if price0_usd <= 0 or price1_usd <= 0:
        raise ValueError("token prices must be positive")
    amount0, amount1 = amounts_for_liquidity(
        liquidity_raw, sqrt_price_x96, tick_lower, tick_upper, decimals0, decimals1
    )
    fees0 = Decimal(fees0_raw) / (Decimal(10) ** decimals0)
    fees1 = Decimal(fees1_raw) / (Decimal(10) ** decimals1)
    principal = amount0 * price0_usd + amount1 * price1_usd
    fees = fees0 * price0_usd + fees1 * price1_usd
    return {
        "amount0": str(amount0), "amount1": str(amount1),
        "fees0": str(fees0), "fees1": str(fees1),
        "principal_usd": str(principal), "unclaimed_fees_usd": str(fees),
        "position_value_usd": str(principal + fees),
        "price0_usd": str(price0_usd), "price1_usd": str(price1_usd),
    }


def compare_to_hodl(
    *, current_principal_usd: Decimal, current_fees_usd: Decimal,
    current_price0_usd: Decimal, current_price1_usd: Decimal,
    initial_amount0: Decimal, initial_amount1: Decimal,
    initial_capital_usd: Decimal,
) -> dict[str, str]:
    hodl_value = initial_amount0 * current_price0_usd + initial_amount1 * current_price1_usd
    il_usd = current_principal_usd - hodl_value
    fee_adjusted_vs_hodl = current_principal_usd + current_fees_usd - hodl_value
    pnl_before_claimed_fees_and_costs = current_principal_usd + current_fees_usd - initial_capital_usd
    return {
        "hodl_value_usd": str(hodl_value),
        "il_vs_hodl_usd": str(il_usd),
        "il_vs_hodl_pct": str((il_usd / hodl_value * 100) if hodl_value else Decimal(0)),
        "fee_adjusted_vs_hodl_usd": str(fee_adjusted_vs_hodl),
        "pnl_before_claimed_fees_and_costs_usd": str(pnl_before_claimed_fees_and_costs),
    }
