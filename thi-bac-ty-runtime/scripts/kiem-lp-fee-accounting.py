"""Offline fixtures for Uniswap V3 fee-growth accounting."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lp_intelligence.fee_accounting import (
    Q128, UINT256_MASK, PositionFeeState, TickFeeState, accrued_fee_raw,
    decode_position_fee_state, decode_tick_fee_state, encode_position_call,
    encode_tick_call, fee_growth_inside_x128, position_unclaimed_fees_raw,
)
def word(value: int) -> str:
    return format(value, "064x")
def main() -> int:
    checks = 0
    def check(label: str, condition: bool) -> None:
        nonlocal checks
        if not condition: raise AssertionError(label)
        checks += 1
        print("  ✓", label)
    inside = fee_growth_inside_x128(100, -100, 100, 0, 20, 30)
    check("feeGrowthInside subtracts both outside accumulators", inside == 50)
    below = fee_growth_inside_x128(100, -100, 100, -101, 20, 30)
    check("feeGrowthInside handles tick below range with uint256 underflow", below == (100 - 80 - 30) % (1 << 256))
    above = fee_growth_inside_x128(100, -100, 100, 100, 20, 30)
    check("feeGrowthInside handles upper boundary", above == 10)
    wrapped = fee_growth_inside_x128(5, -10, 10, 0, UINT256_MASK - 2, 1)
    check("feeGrowthInside uses uint256 wraparound",
          wrapped == ((5 - (UINT256_MASK - 2) - 1) & UINT256_MASK))
    check("accrued fees include stored tokensOwed",
          accrued_fee_raw(2 * Q128, 7, 2, 11) == 21)
    position = PositionFeeState(
        token0="0x" + "1" * 40, token1="0x" + "2" * 40, fee=500,
        tick_lower=-10, tick_upper=10, liquidity=Q128,
        fee_growth_inside0_last_x128=0, fee_growth_inside1_last_x128=0,
        tokens_owed0=3, tokens_owed1=4)
    owed0, owed1 = position_unclaimed_fees_raw(
        position, 0, 2 * Q128, 5 * Q128, TickFeeState(0, 0), TickFeeState(0, 0))
    check("position accounting returns raw token0/token1 amounts",
          owed0 == 2 * Q128 + 3 and owed1 == 5 * Q128 + 4)
    decoded_tick = decode_tick_fee_state("0x" + "".join(word(v) for v in (1,2,3,4,5,6,7,1)))
    check("tick decoder reads feeGrowthOutside words 2 and 3", decoded_tick == TickFeeState(3,4))
    pos_values = (0, 0, int("1"*40,16), int("2"*40,16), 500,
                  (1<<24)-10, 10, 12345, 100, 200, 7, 8)
    decoded_pos = decode_position_fee_state("0x" + "".join(word(v) for v in pos_values))
    check("position decoder reads NFT ticks, liquidity and owed amounts",
          decoded_pos.tick_lower == -10 and decoded_pos.tick_upper == 10
          and decoded_pos.liquidity == 12345 and decoded_pos.tokens_owed1 == 8)
    check("ticks(int24) calldata encodes signed negative tick",
          encode_tick_call(-10).startswith("0xf30dba93")
          and encode_tick_call(-10)[-64:] == word((1<<256)-10))
    check("positions(uint256) calldata uses expected selector",
          encode_position_call(42) == "0x99fbab88" + word(42))
    rejected = False
    try: fee_growth_inside_x128(1, 10, 10, 0, 0, 0)
    except ValueError: rejected = True
    check("invalid tick range is rejected", rejected)
    print(f"LP fee accounting fixtures passed: {checks}/{checks}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
