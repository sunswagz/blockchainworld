#!/usr/bin/env python3
"""Discover directly wallet-owned Uniswap V3 X Layer position NFTs using Transfer logs.

This is read-only. Use --from-block equal to the baseline block for a newly created
wallet, or an earlier block if the wallet may already have received a position NFT.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.evm import JsonRpcClient, decode_uint, factory_get_pool_calldata
from lp_intelligence.xlayer import CHAIN_ID, DEFAULT_RPC_URL, UNISWAP_V3

TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
OWNER_OF = "0x6352211e"
POSITIONS = "0x99fbab88"
SLOT0 = "0x3850c7bd"


def topic_address(address: str) -> str:
    raw = address.lower().removeprefix("0x")
    if len(raw) != 40:
        raise ValueError("invalid wallet address")
    return "0x" + raw.rjust(64, "0")


def signed24(value: int) -> int:
    value &= (1 << 24) - 1
    return value - (1 << 24) if value & (1 << 23) else value


def word_address(value: int) -> str:
    return "0x" + format(value & ((1 << 160) - 1), "040x")


def collect(rpc: JsonRpcClient, wallet: str, from_block: int, chunk_size: int = 2000) -> dict:
    latest = rpc.get_block_number()
    if from_block < 0 or from_block > latest:
        raise ValueError("from-block must be between zero and the latest block")
    npm = UNISWAP_V3["nonfungible_position_manager"]
    factory = UNISWAP_V3["factory"]
    wallet_topic = topic_address(wallet)
    incoming = rpc.get_logs(address=npm, from_block=from_block, to_block=latest,
                            topics=[TRANSFER_TOPIC, None, wallet_topic])
    outgoing = rpc.get_logs(address=npm, from_block=from_block, to_block=latest,
                            topics=[TRANSFER_TOPIC, wallet_topic, None])
    token_ids = set()
    for log in incoming + outgoing:
        topics = log.get("topics") or []
        if len(topics) >= 4:
            token_ids.add(int(topics[3], 16))
    block_tag = hex(latest)
    positions = []
    for token_id in sorted(token_ids):
        owner_result = rpc.eth_call(npm, OWNER_OF + format(token_id, "064x"), block_tag)
        owner = word_address(decode_uint(owner_result))
        if owner.lower() != wallet.lower():
            continue
        raw = rpc.eth_call(npm, POSITIONS + format(token_id, "064x"), block_tag)
        values = [decode_uint(raw, i) for i in range(12)]
        token0, token1 = word_address(values[2]), word_address(values[3])
        fee = values[4]
        tick_lower, tick_upper = signed24(values[5]), signed24(values[6])
        pool_data = rpc.eth_call(factory, factory_get_pool_calldata(token0, token1, fee), block_tag)
        pool = word_address(decode_uint(pool_data))
        if int(pool, 16) == 0:
            positions.append({"token_id": str(token_id), "owner": owner, "verification": "factory_pool_missing"})
            continue
        slot0 = rpc.eth_call(pool, SLOT0, block_tag)
        current_tick = signed24(decode_uint(slot0, 1))
        positions.append({
            "token_id": str(token_id),
            "owner": owner,
            "pool_address": pool,
            "token0": token0,
            "token1": token1,
            "fee_tier": fee,
            "tick_lower": tick_lower,
            "tick_upper": tick_upper,
            "liquidity_raw": str(values[7]),
            "tokens_owed0_raw": str(values[10]),
            "tokens_owed1_raw": str(values[11]),
            "current_tick": current_tick,
            "range_status": "in_range" if tick_lower <= current_tick < tick_upper else ("below_range" if current_tick < tick_lower else "above_range"),
            "verification": "owner_and_factory_confirmed",
        })
    block = rpc.get_block(latest)
    return {
        "snapshot_type": "xlayer_uniswap_v3_wallet_positions",
        "chain_id": CHAIN_ID,
        "wallet": wallet,
        "from_block": from_block,
        "to_block": latest,
        "block_hash": block["hash"],
        "block_timestamp": int(block["timestamp"], 16),
        "candidate_transfer_count": len(token_ids),
        "owned_position_count": len(positions),
        "positions": positions,
        "limitations": [
            "Only directly wallet-owned Uniswap V3 NFTs are reported; NFTs custodied or staked in another contract need a separate adapter.",
            "Transfer logs are scanned only from --from-block onward; a too-late start block can miss older still-owned NFTs.",
            "This scanner does not yet calculate feeGrowthInside or USD valuation.",
        ],
        "read_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True)
    parser.add_argument("--from-block", required=True, type=int)\n    parser.add_argument("--chunk-size", type=int, default=2000)
    parser.add_argument("--rpc-url", default=DEFAULT_RPC_URL)
    parser.add_argument("--output")
    args = parser.parse_args()
    rpc = JsonRpcClient(args.rpc_url)
    try:
        if int(rpc.call("eth_chainId", []), 16) != CHAIN_ID:
            raise RuntimeError("RPC is not X Layer mainnet (chain ID 196)")
        wallet = "0x" + topic_address(args.wallet)[-40:]
        result = collect(rpc, wallet, args.from_block, args.chunk_size)
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        rpc.close()


if __name__ == "__main__":
    raise SystemExit(main())
