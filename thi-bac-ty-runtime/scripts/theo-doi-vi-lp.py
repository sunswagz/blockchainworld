#!/usr/bin/env python3
"""Unified read-only LP wallet monitor for Base and X Layer.

For a newly created/unused wallet, first run establishes a per-chain block baseline.
Subsequent runs replay Transfer logs from that baseline to find currently owned NFTs.
No signing, approvals, transaction construction or transaction submission.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.contracts import utc_now
from lp_intelligence.evm import JsonRpcClient
from lp_intelligence.storage import SQLiteStore
from lp_intelligence.xlayer import CHAIN_ID as XLAYER_CHAIN_ID, DEFAULT_RPC_URL as XLAYER_RPC, CHAIN_NAME as XLAYER_NAME

BASE_CHAIN_ID = 8453
BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")


def load_xlayer_position_scanner():
    path = Path(__file__).with_name("quet-vi-the-uniswap-v3-xlayer.py")
    spec = importlib.util.spec_from_file_location("xlayer_position_scanner", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def get_or_create_baseline(store: SQLiteStore, wallet: str, chain_id: int,
                           chain_name: str, rpc: JsonRpcClient) -> dict:
    existing = store.get_wallet_baseline(wallet, str(chain_id))
    if existing:
        return existing
    latest = rpc.get_block_number()
    block = rpc.get_block(latest)
    baseline = {
        "wallet_address": wallet.lower(), "chain_id": str(chain_id),
        "chain_name": chain_name, "baseline_block": latest,
        "baseline_hash": block["hash"].lower(),
        "baseline_timestamp": datetime.fromtimestamp(
            int(block["timestamp"], 16), tz=timezone.utc
        ).isoformat().replace("+00:00", "Z"),
        "scan_from_block": latest, "created_at": utc_now(),
    }
    store.add_wallet_baseline(baseline)
    return store.get_wallet_baseline(wallet, str(chain_id))


def run(wallet: str, *, include_base: bool, include_xlayer: bool,
        store: SQLiteStore, base_rpc_url: str, xlayer_rpc_url: str) -> dict:
    results = {"wallet": wallet.lower(), "observed_at": utc_now(), "chains": {},
               "safety": {"read_only": True, "signed": False, "approvals": False,
                          "transactions_sent": False}}
    if include_xlayer:
        rpc = JsonRpcClient(xlayer_rpc_url)
        try:
            chain_id = int(rpc.call("eth_chainId", []), 16)
            if chain_id != XLAYER_CHAIN_ID:
                raise RuntimeError(f"X Layer RPC returned chain ID {chain_id}")
            baseline = get_or_create_baseline(store, wallet, XLAYER_CHAIN_ID, XLAYER_NAME, rpc)
            scanner = load_xlayer_position_scanner()
            snapshot = scanner.collect(rpc, wallet, int(baseline["scan_from_block"]))
            block = {"number": snapshot["to_block"], "hash": snapshot["block_hash"],
                     "timestamp": snapshot["block_timestamp"]}
            for position in snapshot["positions"]:
                store.add_xlayer_position_snapshot(wallet, block, position)
            results["chains"]["196"] = {
                "chain_name": XLAYER_NAME, "baseline_block": baseline["baseline_block"],
                "scan_from_block": baseline["scan_from_block"],
                "latest_block": snapshot["to_block"],
                "candidate_nfts": snapshot["candidate_transfer_count"],
                "owned_positions": snapshot["owned_position_count"],
                "positions": snapshot["positions"],
                "limitations": snapshot["limitations"],
            }
        finally:
            rpc.close()
    if include_base:
        rpc = JsonRpcClient(base_rpc_url)
        try:
            chain_id = int(rpc.call("eth_chainId", []), 16)
            if chain_id != BASE_CHAIN_ID:
                raise RuntimeError(f"Base RPC returned chain ID {chain_id}")
            baseline = get_or_create_baseline(store, wallet, BASE_CHAIN_ID, "Base", rpc)
        finally:
            rpc.close()
        from lp_intelligence.collectors.uniswap_v3_positions_base import collect_uniswap_v3_base_positions
        snapshot = collect_uniswap_v3_base_positions(
            wallet, from_block=int(baseline["scan_from_block"]),
            rpc_url=base_rpc_url, store=store,
        )
        results["chains"]["8453"] = {
            "chain_name": "Base", "baseline_block": baseline["baseline_block"],
            "scan_from_block": baseline["scan_from_block"],
            "latest_block": snapshot["block_number"],
            "candidate_nfts": snapshot["candidate_token_ids"],
            "owned_positions": snapshot["position_count"],
            "positions": snapshot["positions"],
            "fee_values_unit": snapshot["fee_values_unit"],
            "limitations": [
                "Fee values are underlying token units, not USD.",
                "Directly wallet-owned NFTs only; staked/custodied NFTs require another adapter.",
            ],
        }
    results["status"] = "ok"
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True, help="Public EVM address or OKX XKO-prefixed address")
    parser.add_argument("--chains", default="xlayer,base", help="Comma-separated subset: xlayer,base")
    parser.add_argument("--xlayer-rpc", default=XLAYER_RPC)
    parser.add_argument("--base-rpc", default=BASE_RPC)
    args = parser.parse_args()
    try:
        wallet = "0x" + args.wallet.strip().removeprefix("XKO").removeprefix("0x").lower()
        if len(wallet) != 42 or any(c not in "0123456789abcdef" for c in wallet[2:]):
            raise ValueError("Invalid public wallet address")
        chains = {x.strip().lower() for x in args.chains.split(",") if x.strip()}
        if not chains or not chains <= {"xlayer", "base"}:
            raise ValueError("--chains must contain xlayer and/or base")
        store = SQLiteStore()
        store.initialize()
        result = run(wallet, include_base="base" in chains, include_xlayer="xlayer" in chains,
                     store=store, base_rpc_url=args.base_rpc, xlayer_rpc_url=args.xlayer_rpc)
        store.add_wallet_monitor_run(wallet, result["observed_at"], "ok", result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
