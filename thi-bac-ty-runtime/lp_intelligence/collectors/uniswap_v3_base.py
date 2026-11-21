"""Uniswap V3/Base pool discovery and on-chain verification.

GeckoTerminal discovers candidate pools. The official Uniswap V3 factory and
pool contracts verify identity and live state before a snapshot is persisted.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from typing import Any

from ..contracts import PoolSnapshot, utc_now
from ..evm import JsonRpcClient, decode_int24_word, decode_uint, verify_uniswap_v3_pool
from ..providers.geckoterminal import GeckoTerminalClient, PoolCandidate
from ..storage import SQLiteStore\nfrom ..swap_activity import collect_swap_activity

CHAIN_ID = "8453"
NETWORK = "base"
FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
WETH = "0x4200000000000000000000000000000000000006"
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
POOL_SELECTORS = {
    "token0": "0x0dfe1681",
    "token1": "0xd21220a7",
    "slot0": "0x3850c7bd",
    "liquidity": "0x1a686502",
}


def _hex_address(result: str) -> str:
    if len(result) < 66:
        raise ValueError("short ABI address response")
    return "0x" + result[-40:].lower()


def _is_expected_pair(candidate: PoolCandidate) -> bool:
    addresses = {candidate.base_token_address, candidate.quote_token_address}
    return addresses == {WETH.lower(), USDC.lower()}


def find_verified_candidate(
    candidates: list[PoolCandidate], rpc: JsonRpcClient
) -> tuple[PoolCandidate, int]:
    matches = [item for item in candidates if _is_expected_pair(item)]
    matches.sort(key=lambda item: item.reserve_in_usd or -1.0, reverse=True)
    for candidate in matches:
        fee_tier = verify_uniswap_v3_pool(rpc, FACTORY, candidate.address, WETH, USDC)
        if fee_tier is not None:
            return candidate, fee_tier
    raise RuntimeError(
        "No GeckoTerminal WETH/USDC candidate was confirmed by the official Uniswap V3 Base factory"
    )


def collect_uniswap_v3_base(
    *,
    rpc_url: str | None = None,
    store: SQLiteStore | None = None,
    gecko: GeckoTerminalClient | None = None,
    rpc: JsonRpcClient | None = None,
) -> dict[str, Any]:
    rpc_url = rpc_url or os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    owns_gecko = gecko is None
    owns_rpc = rpc is None
    gecko = gecko or GeckoTerminalClient()
    rpc = rpc or JsonRpcClient(rpc_url)
    store = store or SQLiteStore()

    try:
        candidates, discovery_payload = gecko.token_pools(NETWORK, WETH)
        candidate, fee_tier = find_verified_candidate(candidates, rpc)

        pool_token0 = _hex_address(rpc.eth_call(candidate.address, POOL_SELECTORS["token0"]))
        pool_token1 = _hex_address(rpc.eth_call(candidate.address, POOL_SELECTORS["token1"]))
        if (pool_token0, pool_token1) != tuple(sorted((WETH.lower(), USDC.lower()))):
            raise RuntimeError("On-chain token0/token1 do not match the expected WETH/USDC pair")

        slot0 = rpc.eth_call(candidate.address, POOL_SELECTORS["slot0"], block_tag)
        sqrt_price_x96 = decode_uint(slot0, 0)
        current_tick = decode_int24_word(slot0, 1)
        liquidity = decode_uint(rpc.eth_call(candidate.address, POOL_SELECTORS["liquidity"], block_tag))
        if sqrt_price_x96 <= 0 or liquidity <= 0:
            raise RuntimeError("Pool has zero price or liquidity; refusing to publish snapshot")

        # Base WETH (18 decimals) sorts before USDC (6 decimals).
        price_usdc_per_weth = (sqrt_price_x96 / (2**96)) ** 2 * (10**12)
        fetched_at = utc_now()\n        token_prices = {\n            candidate.base_token_address.lower(): candidate.base_token_price_usd,\n            candidate.quote_token_address.lower(): candidate.quote_token_price_usd,\n        }\n        token0_price = token_prices.get(pool_token0)\n        token1_price = token_prices.get(pool_token1)\n        swap_activity = None\n        if token0_price is not None and token1_price is not None:\n            swap_activity = collect_swap_activity(\n                rpc, pool_address=candidate.address, fee_tier=fee_tier,\n                token0_usd=token0_price, token1_usd=token1_price,\n                now_timestamp=block_timestamp, latest_block=latest_block,\n            )
        pool_id = f"{CHAIN_ID}:uniswap-v3:{candidate.address.lower()}"
        raw_payload = {
            "discovery": discovery_payload,
            "candidate": asdict(candidate),
            "onchain": {
                "chain_id": CHAIN_ID,
                "factory": FACTORY,
                "fee_tier": fee_tier,
                "token0": pool_token0,
                "token1": pool_token1,
                "sqrt_price_x96": str(sqrt_price_x96),
                "current_tick": current_tick,
                "liquidity_raw": str(liquidity),\n                "snapshot_block": {"number": latest_block, "hash": latest_block_data["hash"], "timestamp": block_timestamp},\n                "swap_activity_24h": swap_activity,
            },
        }
        raw_json = json.dumps(raw_payload, sort_keys=True, separators=(",", ":"))
        raw_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        raw_id = store.add_provider_payload(
            source="geckoterminal+base_rpc",
            entity_id=pool_id,
            fetched_at=fetched_at,
            payload_json=raw_json,
            payload_hash=raw_hash,
        )
        snapshot = PoolSnapshot(
            pool_id=pool_id,
            chain_id=CHAIN_ID,
            chain_name="Base",
            protocol="Uniswap",
            version="V3",
            pool_address=candidate.address,
            token0_address=pool_token0,
            token0_symbol="WETH",
            token1_address=pool_token1,
            token1_symbol="USDC",
            observed_at=fetched_at,
            fetched_at=fetched_at,
            source="geckoterminal+base_rpc",
            source_url=candidate.source_url,
            data_status="fresh",
            tvl_usd=candidate.reserve_in_usd,
            volume_24h_usd=candidate.volume_24h_usd,
            # Fee and APR are intentionally unknown until fee-growth accounting
            # is implemented; volume * fee tier is not realized fee income.
            fees_24h_usd=(swap_activity["fees_usd_estimated"] if swap_activity else None),
            fee_apr_pct=None,
            incentive_apr_pct=None,
            spot_price=price_usdc_per_weth,
            current_tick=current_tick,
            fee_tier_bps=fee_tier / 100.0,
            raw_ref=str(raw_id),
        )
        store.add_pool_snapshot(snapshot)\n        if swap_activity is not None:\n            store.add_pool_activity_snapshot({\n                "pool_id": pool_id, "block_number": latest_block,\n                "block_hash": latest_block_data["hash"], "block_timestamp": block_timestamp,\n                **swap_activity, "data_status": "estimated", "raw_ref": str(raw_id),\n            })
        return {
            "status": "ok",
            "pool_id": pool_id,
            "pool_address": candidate.address,
            "fee_tier": fee_tier,
            "current_tick": current_tick,
            "liquidity_raw": str(liquidity),
            "spot_price_usdc_per_weth": price_usdc_per_weth,
            "tvl_usd": candidate.reserve_in_usd,
            "volume_24h_usd": candidate.volume_24h_usd,
            "fees_24h_usd": None,
            "fee_apr_pct": None,
            "raw_payload_id": raw_id,
            "data_status": "fresh",
        }
    finally:
        if owns_gecko:
            gecko.close()
        if owns_rpc:
            rpc.close()
