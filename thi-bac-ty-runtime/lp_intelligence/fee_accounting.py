"""Uniswap V3 fee-growth accounting primitives.

All calculations are integer-only and mirror the protocol's uint256 wraparound.
This module does not fetch data, sign transactions, or submit transactions.
"""
from __future__ import annotations
from dataclasses import dataclass

Q128 = 1 << 128
UINT256_MOD = 1 << 256
UINT256_MASK = UINT256_MOD - 1
TICKS_SELECTOR = "0xf30dba93"
POSITIONS_SELECTOR = "0x99fbab88"

def _word(value: int) -> str:
    if not 0 <= value < UINT256_MOD:
        raise ValueError("ABI uint256 value out of range")
    return format(value, "064x")

def encode_tick_call(tick: int) -> str:
    if not -(1 << 23) <= tick < (1 << 23):
        raise ValueError("tick does not fit int24")
    return TICKS_SELECTOR + _word(tick % UINT256_MOD)

def encode_position_call(token_id: int) -> str:
    if not 0 <= token_id < UINT256_MOD:
        raise ValueError("token_id must fit uint256")
    return POSITIONS_SELECTOR + _word(token_id)

def _words(data: str, expected: int) -> list[int]:
    raw = data.removeprefix("0x")
    if len(raw) < expected * 64:
        raise ValueError(f"ABI response requires at least {expected} words")
    return [int(raw[i * 64:(i + 1) * 64], 16) for i in range(expected)]

def _as_int24(value: int) -> int:
    value &= (1 << 24) - 1
    return value - (1 << 24) if value & (1 << 23) else value

@dataclass(frozen=True)
class TickFeeState:
    fee_growth_outside0_x128: int
    fee_growth_outside1_x128: int

@dataclass(frozen=True)
class PositionFeeState:
    token0: str
    token1: str
    fee: int
    tick_lower: int
    tick_upper: int
    liquidity: int
    fee_growth_inside0_last_x128: int
    fee_growth_inside1_last_x128: int
    tokens_owed0: int
    tokens_owed1: int

def decode_tick_fee_state(data: str) -> TickFeeState:
    """Decode feeGrowthOutside fields (words 2 and 3) from pool.ticks()."""
    values = _words(data, 8)
    return TickFeeState(values[2], values[3])

def decode_position_fee_state(data: str) -> PositionFeeState:
    """Decode the canonical 12-word NonfungiblePositionManager.positions() tuple."""
    values = _words(data, 12)
    return PositionFeeState(
        token0="0x" + format(values[2], "040x")[-40:],
        token1="0x" + format(values[3], "040x")[-40:],
        fee=values[4],
        tick_lower=_as_int24(values[5]),
        tick_upper=_as_int24(values[6]),
        liquidity=values[7],
        fee_growth_inside0_last_x128=values[8],
        fee_growth_inside1_last_x128=values[9],
        tokens_owed0=values[10],
        tokens_owed1=values[11],
    )

def fee_growth_inside_x128(
    fee_growth_global_x128: int, tick_lower: int, tick_upper: int,
    current_tick: int, lower_fee_growth_outside_x128: int,
    upper_fee_growth_outside_x128: int,
) -> int:
    """Compute feeGrowthInside using uint256 modular arithmetic."""
    values = (fee_growth_global_x128, lower_fee_growth_outside_x128, upper_fee_growth_outside_x128)
    if any(not 0 <= value < UINT256_MOD for value in values):
        raise ValueError("fee growth values must fit uint256")
    if tick_lower >= tick_upper:
        raise ValueError("tick_lower must be less than tick_upper")
    if current_tick >= tick_lower:
        fee_growth_below = lower_fee_growth_outside_x128
    else:
        fee_growth_below = (fee_growth_global_x128 - lower_fee_growth_outside_x128) & UINT256_MASK
    if current_tick < tick_upper:
        fee_growth_above = upper_fee_growth_outside_x128
    else:
        fee_growth_above = (fee_growth_global_x128 - upper_fee_growth_outside_x128) & UINT256_MASK
    return (fee_growth_global_x128 - fee_growth_below - fee_growth_above) & UINT256_MASK

def accrued_fee_raw(
    liquidity: int, fee_growth_inside_now_x128: int,
    fee_growth_inside_last_x128: int, tokens_owed_last: int = 0,
) -> int:
    """Return unclaimed token amount in raw units, including stored tokensOwed."""
    if liquidity < 0 or tokens_owed_last < 0:
        raise ValueError("liquidity and tokens_owed_last cannot be negative")
    if not 0 <= fee_growth_inside_now_x128 < UINT256_MOD:
        raise ValueError("current fee growth must fit uint256")
    if not 0 <= fee_growth_inside_last_x128 < UINT256_MOD:
        raise ValueError("last fee growth must fit uint256")
    delta = (fee_growth_inside_now_x128 - fee_growth_inside_last_x128) & UINT256_MASK
    return tokens_owed_last + (liquidity * delta // Q128)

def position_unclaimed_fees_raw(
    position: PositionFeeState, current_tick: int,
    fee_growth_global0_x128: int, fee_growth_global1_x128: int,
    lower_tick_state: TickFeeState, upper_tick_state: TickFeeState,
) -> tuple[int, int]:
    """Calculate token0/token1 fees currently owed to one V3 NFT position."""
    inside0 = fee_growth_inside_x128(
        fee_growth_global0_x128, position.tick_lower, position.tick_upper,
        current_tick, lower_tick_state.fee_growth_outside0_x128,
        upper_tick_state.fee_growth_outside0_x128)
    inside1 = fee_growth_inside_x128(
        fee_growth_global1_x128, position.tick_lower, position.tick_upper,
        current_tick, lower_tick_state.fee_growth_outside1_x128,
        upper_tick_state.fee_growth_outside1_x128)
    owed0 = accrued_fee_raw(position.liquidity, inside0, position.fee_growth_inside0_last_x128, position.tokens_owed0)
    owed1 = accrued_fee_raw(position.liquidity, inside1, position.fee_growth_inside1_last_x128, position.tokens_owed1)
    return owed0, owed1
