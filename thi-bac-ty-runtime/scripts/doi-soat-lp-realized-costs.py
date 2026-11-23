#!/usr/bin/env python3
"""Read-only Base Uniswap V3 lifecycle scanner and realized-fee/cost ledger.

Run the position collector first. This scanner reads NFT Transfer,
IncreaseLiquidity, DecreaseLiquidity and Collect logs plus transaction receipts.
It never signs, submits, simulates or executes transactions.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.accounting import (
    EVENT_TOPICS, TRANSFER_TOPIC, decode_position_manager_event,
    attribute_position_cashflows, allocate_transaction_gas,
)
from lp_intelligence.collectors.uniswap_v3_positions_base import (
    POSITION_MANAGER, format_units,
)
from lp_intelligence.evm import JsonRpcClient
from lp_intelligence.storage import SQLiteStore

CHAIN_ID = "8453"
WETH_BASE = "0x4200000000000000000000000000000000000006"
ZERO_ADDRESS = "0x" + "0" * 40


def iso_timestamp(rpc: JsonRpcClient, block_number: int, cache: dict[int, tuple[str, str]]) -> tuple[str, str]:
    if block_number not in cache:
        block = rpc.get_block(block_number)
        stamp = datetime.fromtimestamp(int(block["timestamp"], 16), tz=timezone.utc)
        cache[block_number] = (
            stamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
            block["hash"].lower(),
        )
    return cache[block_number]


def scan_positions_events(rpc: JsonRpcClient, token_ids: list[int], from_block: int,
                          to_block: int, chunk_size: int, wallet: str) -> dict[int, list[dict]]:
    """Fetch manager lifecycle logs in batches using JSON-RPC topic OR filters."""
    out = {token_id: [] for token_id in token_ids}
    cursor = from_block
    token_groups = [token_ids[i:i + 50] for i in range(0, len(token_ids), 50)]
    while cursor <= to_block:
        end = min(cursor + chunk_size - 1, to_block)
        for group in token_groups:
            token_topics = ["0x" + format(token_id, "064x") for token_id in group]
            for topic in EVENT_TOPICS:
                query_topics = (
                    [topic, None, None, token_topics]
                    if topic == TRANSFER_TOPIC else [topic, token_topics]
                )
                logs = rpc.get_logs(
                    address=POSITION_MANAGER, from_block=cursor, to_block=end,
                    topics=query_topics,
                )
                for raw in logs:
                    decoded = decode_position_manager_event(raw, wallet)
                    out[int(decoded["token_id"])].append(decoded)
        cursor = end + 1
    for token_id in out:
        out[token_id].sort(key=lambda x: (
            x["block_number"], x["transaction_index"], x["log_index"]
        ))
    return out

