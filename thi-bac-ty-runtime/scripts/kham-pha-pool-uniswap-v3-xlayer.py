#!/usr/bin/env python3
"""Discover GeckoTerminal X Layer pools around WOKB and verify against Uniswap V3 Factory."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.evm import JsonRpcClient, decode_uint, verify_uniswap_v3_pool
from lp_intelligence.providers.geckoterminal import GeckoTerminalClient
from lp_intelligence.xlayer import CHAIN_ID, DEFAULT_RPC_URL, UNISWAP_V3

NETWORK = "x-layer"
TOKEN0 = "0x0dfe1681"
TOKEN1 = "0xd21220a7"
SLOT0 = "0x3850c7bd"
LIQUIDITY = "0x1a686502"


def address_from_result(result: str) -> str:
    if len(result) < 66:
        raise ValueError("Malformed ABI address")
    return "0x" + result[-40:].lower()


def discover(rpc: JsonRpcClient, gecko: GeckoTerminalClient) -> dict:
    wrapped = UNISWAP_V3["wrapped_native_token"]
    candidates, provider_payload = gecko.token_pools(NETWORK, wrapped)
    block = rpc.get_block_number()
    block_tag = hex(block)
    verified = []
    for candidate in candidates:
        try:
            token0 = address_from_result(rpc.eth_call(candidate.address, TOKEN0, block_tag))
            token1 = address_from_result(rpc.eth_call(candidate.address, TOKEN1, block_tag))
            fee = verify_uniswap_v3_pool(
                rpc, UNISWAP_V3["factory"], candidate.address, token0, token1,
                block_tag=block_tag,
            )
            if fee is None:
                continue
            slot0 = rpc.eth_call(candidate.address, SLOT0, block_tag)
            sqrt_price_x96 = decode_uint(slot0, 0)
            tick = decode_uint(slot0, 1)
            if tick >= 2**23:
                tick -= 2**24
            liquidity = decode_uint(rpc.eth_call(candidate.address, LIQUIDITY, block_tag))
            verified.append({
                "pool_address": candidate.address,
                "name": candidate.name,
                "dex_id_provider_label": candidate.dex_id,
                "token0": token0,
                "token1": token1,
                "fee_tier": fee,
                "sqrt_price_x96": str(sqrt_price_x96),
                "current_tick": tick,
                "liquidity_raw": str(liquidity),
                "tvl_usd_provider": candidate.reserve_in_usd,
                "volume_24h_usd_provider": candidate.volume_24h_usd,
                "source_url": candidate.source_url,
                "ranking_inputs": {
                    "tvl_usd": candidate.reserve_in_usd,
                    "volume_24h_usd": candidate.volume_24h_usd,
                },
            })
        except Exception as exc:
            # Candidate-level failures are retained, not silently interpreted as zero.
            verified.append({
                "pool_address": candidate.address,
                "name": candidate.name,
                "verification_status": "error",
                "error": str(exc),
            })
    verified.sort(
        key=lambda p: (
            p.get("tvl_usd_provider") or -1,
            p.get("volume_24h_usd_provider") or -1,
        ),
        reverse=True,
    )
    return {
        "snapshot_type": "xlayer_uniswap_v3_pool_discovery",
        "chain_id": CHAIN_ID,
        "block_number": block,
        "factory": UNISWAP_V3["factory"],
        "discovery_token": wrapped,
        "provider": "GeckoTerminal",
        "candidate_count": len(candidates),
        "verified_or_error_count": len(verified),
        "verified_pools": verified,
        "ranking_method": "descending provider TVL then 24h volume; not an investment recommendation",
        "limitations": [
            "Discovery is limited to pools returned for WOKB by GeckoTerminal; it is not a complete X Layer pool census.",
            "TVL and volume are provider metrics; pool identity, fee tier, tick and liquidity are checked on-chain.",
            "No APR is inferred from volume or fee tier.",
        ],
        "raw_provider_payload": provider_payload,
        "read_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rpc-url", default=DEFAULT_RPC_URL)
    parser.add_argument("--output")
    args = parser.parse_args()
    rpc, gecko = JsonRpcClient(args.rpc_url), GeckoTerminalClient()
    try:
        if int(rpc.call("eth_chainId", []), 16) != CHAIN_ID:
            raise RuntimeError("RPC is not X Layer mainnet (chain ID 196)")
        result = discover(rpc, gecko)
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(rendered + "\\n", encoding="utf-8")
        else:
            print(rendered)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        rpc.close()
        gecko.close()


if __name__ == "__main__":
    raise SystemExit(main())
