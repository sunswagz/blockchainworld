"""Decode Uniswap V3 Swap logs and estimate rolling 24h volume and fees."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

SWAP_TOPIC = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
FEE_DENOMINATOR = 1_000_000


def _signed256(word: str) -> int:
    value = int(word, 16)
    return value - (1 << 256) if value & (1 << 255) else value


def decode_swap_log(log: dict[str, Any]) -> tuple[int, int]:
    data = log.get("data", "").removeprefix("0x")
    if len(data) < 64 * 5:
        raise ValueError("Swap log data must contain five ABI words")
    return _signed256(data[:64]), _signed256(data[64:128])


def find_block_at_or_before_timestamp(rpc: Any, target_timestamp: int, latest_block: int) -> int:
    low, high, answer = 0, latest_block, 0
    while low <= high:
        mid = (low + high) // 2
        timestamp = int(rpc.get_block(mid)["timestamp"], 16)
        if timestamp <= target_timestamp:
            answer, low = mid, mid + 1
        else:
            high = mid - 1
    return answer


def collect_swap_activity(
    rpc: Any,
    *,
    pool_address: str,
    fee_tier: int,
    token0_usd: float,
    token1_usd: float,
    token0_decimals: int,
    token1_decimals: int,
    now_timestamp: int,
    latest_block: int,
    chunk_size: int = 2000,
) -> dict[str, Any]:
    if not 0 <= fee_tier < FEE_DENOMINATOR:
        raise ValueError("fee_tier must be in millionths")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not 0 <= token0_decimals <= 255 or not 0 <= token1_decimals <= 255:
        raise ValueError("token decimals must be between 0 and 255")
    if token0_usd < 0 or token1_usd < 0:
        raise ValueError("token USD prices cannot be negative")

    from_block = find_block_at_or_before_timestamp(rpc, now_timestamp - 86400, latest_block)
    logs: list[dict[str, Any]] = []
    cursor = from_block
    while cursor <= latest_block:
        end = min(cursor + chunk_size - 1, latest_block)
        logs.extend(rpc.get_logs(
            address=pool_address, from_block=cursor, to_block=end, topics=[SWAP_TOPIC]
        ))
        cursor = end + 1

    volume_usd = Decimal(0)
    fees_usd = Decimal(0)
    volume_token0 = Decimal(0)
    volume_token1 = Decimal(0)
    fee_token0 = Decimal(0)
    fee_token1 = Decimal(0)
    scale0, scale1 = Decimal(10) ** token0_decimals, Decimal(10) ** token1_decimals

    for log in logs:
        amount0, amount1 = decode_swap_log(log)
        if amount0 > 0:
            gross = Decimal(amount0)
            fee = gross * Decimal(fee_tier) / Decimal(FEE_DENOMINATOR)
            volume_token0 += gross
            fee_token0 += fee
            volume_usd += gross / scale0 * Decimal(str(token0_usd))
            fees_usd += fee / scale0 * Decimal(str(token0_usd))
        elif amount1 > 0:
            gross = Decimal(amount1)
            fee = gross * Decimal(fee_tier) / Decimal(FEE_DENOMINATOR)
            volume_token1 += gross
            fee_token1 += fee
            volume_usd += gross / scale1 * Decimal(str(token1_usd))
            fees_usd += fee / scale1 * Decimal(str(token1_usd))
        else:
            raise ValueError("Swap log has no positive input amount")

    return {
        "window": "rolling_24h",
        "from_block": from_block,
        "to_block": latest_block,
        "swap_count": len(logs),
        "volume_usd_estimated": float(volume_usd),
        "fees_usd_estimated": float(fees_usd),
        "fee_token0_raw_estimated": str(fee_token0),
        "fee_token1_raw_estimated": str(fee_token1),
        "volume_token0_raw": str(volume_token0),
        "volume_token1_raw": str(volume_token1),
        "method": "on-chain Swap event input deltas × fee tier; normalized by token decimals and priced using provider token USD prices",
        "limitations": [
            "Fees are estimates from event deltas and fee tier, not a protocol accounting statement.",
            "USD conversion uses provider token prices, not block-by-block oracle prices.",
            "The 24h window begins at the last block at or before the target timestamp.",
        ],
    }
