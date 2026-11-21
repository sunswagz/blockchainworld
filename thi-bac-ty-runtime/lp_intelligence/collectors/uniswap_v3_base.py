"""Uniswap V3/Base pool discovery and on-chain verification."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from typing import Any

from ..contracts import PoolSnapshot, utc_now
from ..evm import JsonRpcClient, decode_int24_word, decode_uint, verify_uniswap_v3_pool
from ..providers.geckoterminal import GeckoTerminalClient, PoolCandidate
from ..storage import SQLiteStore
from ..swap_activity import collect_swap_activity

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
TOKEN_DECIMALS = "0x313ce567"


def _hex_address(result: str) -> str:
    if len(result) < 66:
        raise ValueError("short ABI address response")
    return "0x" + result[-40:].lower()


def _is_expected_pair(candidate: PoolCandidate) -> bool:
    return {candidate.base_token_address, candidate.quote_token_address} == {WETH.lower(), USDC.lower()}


def find_verified_candidate(candidates: list[PoolCandidate], rpc: JsonRpcClient,
                            block_tag: str = "latest") -> tuple[PoolCandidate, int]:
    matches = [item for item in candidates if _is_expected_pair(item)]
    matches.sort(key=lambda item: item.reserve_in_usd or -1.0, reverse=True)
    for candidate in matches:
        fee = verify_uniswap_v3_pool(rpc, FACTORY, candidate.address, WETH, USDC, block_tag=block_tag)
        if fee is not None:
            return candidate, fee
    raise RuntimeError("No GeckoTerminal WETH/USDC candidate was confirmed by the official Uniswap V3 Base factory")


def collect_uniswap_v3_base(*, rpc_url: str | None = None, store: SQLiteStore | None = None,
                            gecko: GeckoTerminalClient | None = None,
                            rpc: JsonRpcClient | None = None) -> dict[str, Any]:
    rpc_url = rpc_url or os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    owns_gecko, owns_rpc = gecko is None, rpc is None
    gecko = gecko or GeckoTerminalClient()
    rpc = rpc or JsonRpcClient(rpc_url)
    store = store or SQLiteStore()
    try:
        candidates, discovery_payload = gecko.token_pools(NETWORK, WETH)
        latest_block = rpc.get_block_number()
        block_data = rpc.get_block(latest_block)
        block_tag = hex(latest_block)
        block_timestamp = int(block_data["timestamp"], 16)
        candidate, fee_tier = find_verified_candidate(candidates, rpc, block_tag)

        token0 = _hex_address(rpc.eth_call(candidate.address, POOL_SELECTORS["token0"], block_tag))
        token1 = _hex_address(rpc.eth_call(candidate.address, POOL_SELECTORS["token1"], block_tag))
        if (token0, token1) != tuple(sorted((WETH.lower(), USDC.lower()))):
            raise RuntimeError("On-chain token0/token1 do not match expected WETH/USDC pair")

        slot0 = rpc.eth_call(candidate.address, POOL_SELECTORS["slot0"], block_tag)
        sqrt_price_x96 = decode_uint(slot0, 0)
        current_tick = decode_int24_word(slot0, 1)
        liquidity = decode_uint(rpc.eth_call(candidate.address, POOL_SELECTORS["liquidity"], block_tag))
        if sqrt_price_x96 <= 0 or liquidity <= 0:
            raise RuntimeError("Pool has zero price or liquidity; refusing to publish snapshot")

        token0_decimals = decode_uint(rpc.eth_call(token0, TOKEN_DECIMALS, block_tag))
        token1_decimals = decode_uint(rpc.eth_call(token1, TOKEN_DECIMALS, block_tag))
        token_prices = {
            (candidate.base_token_address or "").lower(): candidate.base_token_price_usd,
            (candidate.quote_token_address or "").lower(): candidate.quote_token_price_usd,
        }
        token0_price, token1_price = token_prices.get(token0), token_prices.get(token1)
        activity = None
        if token0_price is not None and token1_price is not None:
            activity = collect_swap_activity(
                rpc, pool_address=candidate.address, fee_tier=fee_tier,
                token0_usd=token0_price, token1_usd=token1_price,
                token0_decimals=token0_decimals, token1_decimals=token1_decimals,
                now_timestamp=block_timestamp, latest_block=latest_block,
            )

        spot_price = (sqrt_price_x96 / (2**96)) ** 2 * (10 ** (token0_decimals - token1_decimals))
        fetched_at = utc_now()
        pool_id = f"{CHAIN_ID}:uniswap-v3:{candidate.address.lower()}"
        raw_payload = {
            "discovery": discovery_payload,
            "candidate": asdict(candidate),
            "onchain": {
                "chain_id": CHAIN_ID, "factory": FACTORY, "fee_tier": fee_tier,
                "token0": token0, "token1": token1,
                "token0_decimals": token0_decimals, "token1_decimals": token1_decimals,
                "sqrt_price_x96": str(sqrt_price_x96), "current_tick": current_tick,
                "liquidity_raw": str(liquidity),
                "snapshot_block": {"number": latest_block, "hash": block_data["hash"],
                                   "timestamp": block_timestamp},
                "swap_activity_24h": activity,
            },
        }
        raw_json = json.dumps(raw_payload, sort_keys=True, separators=(",", ":"))
        raw_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        raw_id = store.add_provider_payload(source="geckoterminal+base_rpc", entity_id=pool_id,
                                            fetched_at=fetched_at, payload_json=raw_json,
                                            payload_hash=raw_hash)
        estimated_fees = activity["fees_usd_estimated"] if activity else None
        snapshot = PoolSnapshot(
            pool_id=pool_id, chain_id=CHAIN_ID, chain_name="Base",
            protocol="Uniswap", version="V3", pool_address=candidate.address,
            token0_address=token0, token0_symbol="WETH",
            token1_address=token1, token1_symbol="USDC",
            observed_at=fetched_at, fetched_at=fetched_at,
            source="geckoterminal+base_rpc", source_url=candidate.source_url,
            data_status="fresh", tvl_usd=candidate.reserve_in_usd,
            volume_24h_usd=candidate.volume_24h_usd, fees_24h_usd=None,
            fee_apr_pct=None, incentive_apr_pct=None, spot_price=spot_price,
            current_tick=current_tick, fee_tier_bps=fee_tier / 100.0, raw_ref=str(raw_id),
        )
        store.add_pool_snapshot(snapshot)
        if activity is not None:
            store.add_pool_activity_snapshot({
                "pool_id": pool_id, "block_number": latest_block,
                "block_hash": block_data["hash"], "block_timestamp": block_timestamp,
                **activity, "data_status": "estimated", "raw_ref": str(raw_id),
            })
        return {
            "status": "ok", "pool_id": pool_id, "pool_address": candidate.address,
            "fee_tier": fee_tier, "snapshot_block": latest_block,
            "current_tick": current_tick, "liquidity_raw": str(liquidity),
            "spot_price_token1_per_token0": spot_price,
            "tvl_usd_provider": candidate.reserve_in_usd,
            "volume_24h_usd_provider": candidate.volume_24h_usd,
            "swap_activity_24h": activity, "fees_24h_usd_estimated": estimated_fees,
            "fee_apr_pct": None, "raw_payload_id": raw_id, "data_status": "fresh",
        }
    finally:
        if owns_gecko:
            gecko.close()
        if owns_rpc:
            rpc.close()
