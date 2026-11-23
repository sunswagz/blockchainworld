"""Uniswap V3 NonfungiblePositionManager event decoding and cash-flow attribution.

Collect reports tokens paid out, not whether each token unit was fee or withdrawn
principal. We therefore use a transparent principal-first attribution: prior
DecreaseLiquidity amounts are treated as principal receivable and consumed first
by subsequent Collect events; any remainder is attributed to realized fees.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Any

COLLECT_TOPIC = "0x40d0efd1a53d60ecbf40971b9daf7dc90178c3aadc7aab1765632738fa8b8f01"
INCREASE_LIQUIDITY_TOPIC = "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f"
DECREASE_LIQUIDITY_TOPIC = "0x26f6a048ee9138f2c0ce266f322cb99228e8d619ae2bff30c67f8dcf9d2377b4"

EVENT_TOPICS = {
    COLLECT_TOPIC: "Collect",
    INCREASE_LIQUIDITY_TOPIC: "IncreaseLiquidity",
    DECREASE_LIQUIDITY_TOPIC: "DecreaseLiquidity",
}


def _word(data: str, index: int) -> int:
    raw = data.removeprefix("0x")
    start = index * 64
    word = raw[start:start + 64]
    if len(word) != 64:
        raise ValueError("event data has a missing ABI word")
    return int(word, 16)


def _address_word(data: str, index: int) -> str:
    raw = data.removeprefix("0x")
    start = index * 64
    word = raw[start:start + 64]
    if len(word) != 64:
        raise ValueError("event data has a missing ABI address")
    return "0x" + word[-40:].lower()


def decode_position_manager_event(log: dict[str, Any], wallet: str) -> dict[str, Any]:
    topics = log.get("topics") or []
    if len(topics) < 2:
        raise ValueError("position manager event is missing indexed tokenId")
    topic0 = topics[0].lower()
    event_type = EVENT_TOPICS.get(topic0)
    if event_type is None:
        raise ValueError("unsupported position manager event")
    token_id = int(topics[1], 16)
    data = log.get("data", "0x")
    item: dict[str, Any] = {
        "chain_id": "8453",
        "manager_address": log.get("address", "").lower(),
        "token_id": str(token_id),
        "tx_hash": log["transactionHash"].lower(),
        "block_number": int(log["blockNumber"], 16),
        "transaction_index": int(log.get("transactionIndex", "0x0"), 16),
        "log_index": int(log["logIndex"], 16),
        "block_hash": log.get("blockHash", "").lower(),
        "event_type": event_type,
        "wallet_address": wallet.lower(),
        "recipient": None,
        "amount0_raw": "0",
        "amount1_raw": "0",
        "liquidity_raw": "0",
        "raw_log_json": __import__("json").dumps(log, sort_keys=True),
    }
    if event_type == "Collect":
        item.update({
            "recipient": _address_word(data, 0),
            "amount0_raw": str(_word(data, 1)),
            "amount1_raw": str(_word(data, 2)),
        })
    elif event_type == "DecreaseLiquidity":
        item.update({
            "liquidity_raw": str(_word(data, 0)),
            "amount0_raw": str(_word(data, 1)),
            "amount1_raw": str(_word(data, 2)),
        })
    else:
        item.update({
            "liquidity_raw": str(_word(data, 0)),
            "amount0_raw": str(_word(data, 1)),
            "amount1_raw": str(_word(data, 2)),
        })
    return item


def attribute_position_cashflows(events: list[dict[str, Any]]) -> dict[str, str]:
    """Return cumulative principal and realized fee token units using principal-first attribution."""
    principal_owed0 = 0
    principal_owed1 = 0
    principal_recovered0 = 0
    principal_recovered1 = 0
    realized_fees0 = 0
    realized_fees1 = 0
    contributed0 = 0
    contributed1 = 0
    collect_count = 0

    ordered = sorted(events, key=lambda x: (
        int(x["block_number"]), int(x.get("transaction_index", 0)), int(x["log_index"])
    ))
    for event in ordered:
        kind = event["event_type"]
        amount0 = int(event.get("amount0_raw", "0"))
        amount1 = int(event.get("amount1_raw", "0"))
        if kind == "IncreaseLiquidity":
            contributed0 += amount0
            contributed1 += amount1
        elif kind == "DecreaseLiquidity":
            principal_owed0 += amount0
            principal_owed1 += amount1
        elif kind == "Collect":
            collect_count += 1
            principal_part0 = min(principal_owed0, amount0)
            principal_part1 = min(principal_owed1, amount1)
            principal_owed0 -= principal_part0
            principal_owed1 -= principal_part1
            principal_recovered0 += principal_part0
            principal_recovered1 += principal_part1
            realized_fees0 += amount0 - principal_part0
            realized_fees1 += amount1 - principal_part1

    return {
        "principal_owed0_raw": str(principal_owed0),
        "principal_owed1_raw": str(principal_owed1),
        "principal_recovered0_raw": str(principal_recovered0),
        "principal_recovered1_raw": str(principal_recovered1),
        "realized_fees0_raw": str(realized_fees0),
        "realized_fees1_raw": str(realized_fees1),
        "liquidity_contributed0_raw": str(contributed0),
        "liquidity_contributed1_raw": str(contributed1),
        "collect_event_count": str(collect_count),
        "attribution_method": "principal-first; DecreaseLiquidity amounts are principal receivable; Collect excess is realized fee",
    }


def allocate_transaction_gas(total_fee_wei: int, position_ids: list[str]) -> dict[str, int]:
    """Split one wallet-paid transaction cost evenly across distinct touched positions."""
    if total_fee_wei < 0:
        raise ValueError("gas fee cannot be negative")
    unique = sorted(set(position_ids))
    if not unique:
        return {}
    quotient, remainder = divmod(total_fee_wei, len(unique))
    return {position_id: quotient + (1 if index < remainder else 0)
            for index, position_id in enumerate(unique)}
