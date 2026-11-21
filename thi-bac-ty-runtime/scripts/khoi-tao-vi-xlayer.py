#!/usr/bin/env python3
"""Read-only X Layer wallet bootstrap snapshot.

Accepts OKX's XKO-prefixed display form or a standard 0x EVM address.
Performs only public JSON-RPC reads; no signing, approvals, or transactions.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

from lp_intelligence.xlayer import (
    CHAIN_ID,
    CHAIN_NAME,
    DEFAULT_RPC_URL,
    EXPLORER_BASE_URL,
    NATIVE_SYMBOL,
    UNISWAP_V3,
)

ADDRESS_RE = re.compile(r"^(?:XKO)?([0-9a-fA-F]{40})$")


def normalize_address(value: str) -> str:
    match = ADDRESS_RE.fullmatch(value.strip())
    if not match:
        raise ValueError("Expected 40 hex characters, optionally prefixed with XKO or 0x")
    return "0x" + match.group(1).lower()


def rpc_call(url: str, method: str, params: list) -> object:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = json.loads(response.read().decode())
    if body.get("error"):
        raise RuntimeError(f"RPC {method} failed: {body['error']}")
    return body["result"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True, help="Public XKO... or 0x... wallet address")
    parser.add_argument("--rpc-url", default=os.getenv("XLAYER_RPC_URL", DEFAULT_RPC_URL))
    parser.add_argument("--output", help="Optional JSON output path; stdout if omitted")
    args = parser.parse_args()

    try:
        wallet = normalize_address(args.wallet)
        chain_id = int(rpc_call(args.rpc_url, "eth_chainId", []), 16)
        if chain_id != CHAIN_ID:
            raise RuntimeError(f"Wrong network: expected chain ID {CHAIN_ID}, received {chain_id}")

        block_hex = rpc_call(args.rpc_url, "eth_blockNumber", [])
        block_number = int(block_hex, 16)
        balance_wei = int(rpc_call(args.rpc_url, "eth_getBalance", [wallet, block_hex]), 16)
        nonce = int(rpc_call(args.rpc_url, "eth_getTransactionCount", [wallet, block_hex]), 16)

        contracts = {}
        for name, address in (
            ("uniswap_v3_factory", UNISWAP_V3["factory"]),
            ("uniswap_v3_position_manager", UNISWAP_V3["nonfungible_position_manager"]),
        ):
            code = rpc_call(args.rpc_url, "eth_getCode", [address, block_hex])
            contracts[name] = {"address": address, "has_code": code not in ("0x", "0x0")}

        result = {
            "schema_version": "1.0",
            "snapshot_type": "xlayer_wallet_bootstrap",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "chain": {"name": CHAIN_NAME, "chain_id": chain_id, "rpc_url": args.rpc_url},
            "block": {"number": block_number, "tag": block_hex},
            "wallet": {
                "address": wallet,
                "okb_balance_wei": str(balance_wei),
                "okb_balance": str(balance_wei / 10**18),
                "transaction_count": nonce,
                "explorer_url": f"{EXPLORER_BASE_URL}/address/{wallet}",
            },
            "protocol_contracts": contracts,
            "limitations": [
                "This is a starting baseline, not a complete token or LP position inventory.",
                "A zero transaction count does not prove the address has never been used on another chain.",
                "ERC-20 balances and Uniswap NFT positions require separate read-only collectors.",
            ],
            "safety": {
                "read_only": True,
                "signed": False,
                "approvals": False,
                "transactions_sent": False,
            },
        }
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as handle:
                handle.write(rendered + "\n")
        else:
            print(rendered)
        return 0
    except (ValueError, RuntimeError, urllib.error.URLError, TimeoutError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
