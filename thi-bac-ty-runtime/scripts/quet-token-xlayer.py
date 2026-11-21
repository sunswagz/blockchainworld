#!/usr/bin/env python3
"""Read-only ERC-20 balance scanner for explicitly supplied X Layer token contracts.

It does not claim to enumerate every token held by a wallet: EVM JSON-RPC has no
standard wallet-token enumeration method. Supply --token repeatedly or a JSON
file containing token contract addresses.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.evm import JsonRpcClient, decode_uint
from lp_intelligence.xlayer import CHAIN_ID, DEFAULT_RPC_URL, UNISWAP_V3

BALANCE_OF = "0x70a08231"
DECIMALS = "0x313ce567"
SYMBOL = "0x95d89b41"


def address_word(address: str) -> str:
    raw = address.lower().removeprefix("0x")
    if len(raw) != 40 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError(f"Invalid EVM address: {address}")
    return raw.rjust(64, "0")


def decode_string(result: str) -> str:
    raw = result.removeprefix("0x")
    if len(raw) == 64:
        try:
            return bytes.fromhex(raw).rstrip(b"\\x00").decode("utf-8")
        except UnicodeDecodeError:
            pass
    try:
        offset = int(raw[:64], 16) * 2
        length = int(raw[offset:offset + 64], 16)
        return bytes.fromhex(raw[offset + 64:offset + 64 + length * 2]).decode("utf-8")
    except (ValueError, UnicodeDecodeError, IndexError):
        return "UNKNOWN"


def scan(rpc: JsonRpcClient, wallet: str, token: str, block_tag: str) -> dict:
    balance_data = BALANCE_OF + address_word(wallet)
    raw_balance = decode_uint(rpc.eth_call(token, balance_data, block_tag))
    try:
        decimals = decode_uint(rpc.eth_call(token, DECIMALS, block_tag))
        if decimals > 255:
            raise ValueError("invalid decimals")
    except Exception:
        decimals = None
    try:
        symbol = decode_string(rpc.eth_call(token, SYMBOL, block_tag))
    except Exception:
        symbol = "UNKNOWN"
    human = None if decimals is None else str(Decimal(raw_balance) / (Decimal(10) ** decimals))
    return {
        "token_address": token.lower(),
        "symbol": symbol,
        "decimals": decimals,
        "balance_raw": str(raw_balance),
        "balance": human,
        "data_status": "fresh" if decimals is not None else "partial",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True)
    parser.add_argument("--token", action="append", default=[], help="ERC-20 contract; repeatable")
    parser.add_argument("--token-file", help="JSON array of ERC-20 contract addresses")
    parser.add_argument("--rpc-url", default=DEFAULT_RPC_URL)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        wallet = "0x" + address_word(args.wallet)[-40:]
        tokens = list(args.token)
        if args.token_file:
            tokens.extend(json.loads(Path(args.token_file).read_text(encoding="utf-8")))
        if not tokens:
            tokens = [UNISWAP_V3["wrapped_native_token"]]
        tokens = list(dict.fromkeys("0x" + address_word(t)[-40:] for t in tokens))
        rpc = JsonRpcClient(args.rpc_url)
        try:
            chain_id = int(rpc.call("eth_chainId", []), 16)
            if chain_id != CHAIN_ID:
                raise RuntimeError(f"Wrong chain ID: {chain_id}; expected {CHAIN_ID}")
            block = rpc.get_block_number()
            block_tag = hex(block)
            result = {
                "snapshot_type": "xlayer_erc20_balances",
                "chain_id": chain_id,
                "block_number": block,
                "wallet": wallet,
                "tokens": [scan(rpc, wallet, token, block_tag) for token in tokens],
                "enumeration_note": "Only explicitly supplied token contracts were queried; this is not a complete wallet token inventory.",
                "read_only": True,
            }
        finally:
            rpc.close()
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
