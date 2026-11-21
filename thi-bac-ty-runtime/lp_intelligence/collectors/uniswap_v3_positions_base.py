"""Read-only Uniswap V3/Base NFT position and fee collector.

All contract reads are pinned to one block tag. No signing or transaction methods.
"""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from ..contracts import PositionSnapshot, utc_now
from ..evm import JsonRpcClient, decode_int24_word, decode_uint, factory_get_pool_calldata
from ..fee_accounting import (
    PositionFeeState, decode_position_fee_state, decode_tick_fee_state,
    encode_tick_call, position_unclaimed_fees_raw,
)
from ..storage import SQLiteStore

CHAIN_ID = "8453"
FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
POSITION_MANAGER = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
SOURCE_URL = "https://basescan.org"
NPM_SELECTORS = {
    "balance_of": "0x70a08231",
    "token_of_owner_by_index": "0x2f745c59",
    "owner_of": "0x6352211e",
}
POOL_SELECTORS = {
    "token0": "0x0dfe1681",
    "token1": "0xd21220a7",
    "slot0": "0x3850c7bd",
    "fee_growth_global0": "0xf3058399",
    "fee_growth_global1": "0x46141319",
    "fee": "0xddca3f43",
}
ERC20_SELECTORS = {"decimals": "0x313ce567", "symbol": "0x95d89b41"}
ZERO_ADDRESS = "0x" + "0" * 40


def _word(value: int) -> str:
    if not 0 <= value < 2**256:
        raise ValueError("ABI value must fit uint256")
    return format(value, "064x")


def _address_word(address: str) -> str:
    raw = address.lower().removeprefix("0x")
    if len(raw) != 40 or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError("invalid EVM address")
    return raw.rjust(64, "0")


def encode_address_uint_call(selector: str, address: str, index: int) -> str:
    return selector + _address_word(address) + _word(index)


def encode_uint_call(selector: str, value: int) -> str:
    return selector + _word(value)


def decode_address(result: str) -> str:
    raw = result.removeprefix("0x")
    if len(raw) < 64:
        raise ValueError("short ABI address response")
    return "0x" + raw[-40:].lower()


def decode_abi_string(result: str) -> str:
    raw = result.removeprefix("0x")
    if len(raw) == 64:
        # Some ERC20 contracts expose bytes32 symbols.
        return bytes.fromhex(raw).rstrip(b"\\x00").decode("utf-8", errors="replace")
    if len(raw) < 128:
        raise ValueError("short ABI dynamic string")
    offset = int(raw[:64], 16) * 2
    if offset + 64 > len(raw):
        raise ValueError("invalid ABI string offset")
    length = int(raw[offset:offset + 64], 16)
    start = offset + 64
    end = start + length * 2
    if end > len(raw):
        raise ValueError("truncated ABI string")
    return bytes.fromhex(raw[start:end]).decode("utf-8", errors="replace")


def format_units(raw_amount: int, decimals: int) -> str:
    if raw_amount < 0 or not 0 <= decimals <= 255:
        raise ValueError("invalid token amount or decimals")
    value = Decimal(raw_amount) / (Decimal(10) ** decimals)
    return format(value, "f")


def _iso_from_block_timestamp(timestamp_hex: str) -> str:
    value = datetime.fromtimestamp(int(timestamp_hex, 16), tz=timezone.utc)
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def _call_address(rpc: JsonRpcClient, to: str, selector: str, block_tag: str) -> str:
    return decode_address(rpc.eth_call(to, selector, block_tag))


def collect_uniswap_v3_base_positions(
    wallet_address: str,
    *,
    rpc_url: str | None = None,
    store: SQLiteStore | None = None,
    rpc: JsonRpcClient | None = None,
    max_positions: int = 100,
) -> dict[str, Any]:
    """Discover the wallet's current V3 NFT positions and calculate unclaimed fees."""
    wallet = "0x" + _address_word(wallet_address)[-40:]
    if max_positions < 1 or max_positions > 1000:
        raise ValueError("max_positions must be between 1 and 1000")
    owns_rpc = rpc is None
    rpc = rpc or JsonRpcClient(rpc_url or os.getenv("BASE_RPC_URL", "https://mainnet.base.org"))
    store = store or SQLiteStore()
    try:
        block_number = rpc.get_block_number()
        block_tag = hex(block_number)
        block = rpc.get_block(block_number)
        block_hash = block["hash"].lower()
        observed_at = _iso_from_block_timestamp(block["timestamp"])
        fetched_at = utc_now()

        balance = decode_uint(rpc.eth_call(
            POSITION_MANAGER,
            NPM_SELECTORS["balance_of"] + _address_word(wallet),
            block_tag,
        ))
        if balance > max_positions:
            raise RuntimeError(
                f"Wallet has {balance} V3 NFTs, above configured safety limit {max_positions}; "
                "increase max_positions explicitly if this is expected"
            )

        positions: list[dict[str, Any]] = []
        for index in range(balance):
            token_id = decode_uint(rpc.eth_call(
                POSITION_MANAGER,
                encode_address_uint_call(NPM_SELECTORS["token_of_owner_by_index"], wallet, index),
                block_tag,
            ))
            owner = _call_address(
                rpc, POSITION_MANAGER,
                encode_uint_call(NPM_SELECTORS["owner_of"], token_id), block_tag,
            )
            if owner != wallet:
                raise RuntimeError(f"NFT {token_id} ownerOf does not match wallet at block {block_number}")

            position = decode_position_fee_state(rpc.eth_call(
                POSITION_MANAGER, encode_uint_call("0x99fbab88", token_id), block_tag,
            ))
            pool_result = rpc.eth_call(
                FACTORY,
                factory_get_pool_calldata(position.token0, position.token1, position.fee),
                block_tag,
            )
            pool_address = decode_address(pool_result)
            if pool_address == ZERO_ADDRESS:
                raise RuntimeError(f"NFT {token_id} references a pair/fee not found in official factory")

            token0 = _call_address(rpc, pool_address, POOL_SELECTORS["token0"], block_tag)
            token1 = _call_address(rpc, pool_address, POOL_SELECTORS["token1"], block_tag)
            pool_fee = decode_uint(rpc.eth_call(pool_address, POOL_SELECTORS["fee"], block_tag))
            if (token0, token1, pool_fee) != (position.token0, position.token1, position.fee):
                raise RuntimeError(f"NFT {token_id} does not reconcile with its factory pool identity")

            slot0 = rpc.eth_call(pool_address, POOL_SELECTORS["slot0"], block_tag)
            current_tick = decode_int24_word(slot0, 1)
            fee_global0 = decode_uint(rpc.eth_call(
                pool_address, POOL_SELECTORS["fee_growth_global0"], block_tag,
            ))
            fee_global1 = decode_uint(rpc.eth_call(
                pool_address, POOL_SELECTORS["fee_growth_global1"], block_tag,
            ))
            lower_tick = decode_tick_fee_state(rpc.eth_call(
                pool_address, encode_tick_call(position.tick_lower), block_tag,
            ))
            upper_tick = decode_tick_fee_state(rpc.eth_call(
                pool_address, encode_tick_call(position.tick_upper), block_tag,
            ))
            owed0, owed1 = position_unclaimed_fees_raw(
                position, current_tick, fee_global0, fee_global1, lower_tick, upper_tick,
            )

            decimals0 = decode_uint(rpc.eth_call(position.token0, ERC20_SELECTORS["decimals"], block_tag))
            decimals1 = decode_uint(rpc.eth_call(position.token1, ERC20_SELECTORS["decimals"], block_tag))
            if decimals0 > 255 or decimals1 > 255:
                raise RuntimeError("ERC20 decimals response is outside uint8 range")
            symbol0 = decode_abi_string(rpc.eth_call(position.token0, ERC20_SELECTORS["symbol"], block_tag))
            symbol1 = decode_abi_string(rpc.eth_call(position.token1, ERC20_SELECTORS["symbol"], block_tag))
            if not symbol0 or not symbol1:
                raise RuntimeError("ERC20 symbol is empty; refusing to publish ambiguous token amounts")

            pool_id = f"{CHAIN_ID}:uniswap-v3:{pool_address.lower()}"
            position_id = f"{CHAIN_ID}:uniswap-v3:nft:{token_id}"
            raw_payload = {
                "chain_id": CHAIN_ID,
                "block_number": block_number,
                "block_hash": block_hash,
                "block_timestamp": observed_at,
                "wallet": wallet,
                "token_id": str(token_id),
                "owner_of": owner,
                "position": {
                    "token0": position.token0, "token1": position.token1,
                    "fee": position.fee, "tick_lower": position.tick_lower,
                    "tick_upper": position.tick_upper, "liquidity_raw": str(position.liquidity),
                    "fee_growth_inside0_last_x128": str(position.fee_growth_inside0_last_x128),
                    "fee_growth_inside1_last_x128": str(position.fee_growth_inside1_last_x128),
                    "tokens_owed0_stored_raw": str(position.tokens_owed0),
                    "tokens_owed1_stored_raw": str(position.tokens_owed1),
                },
                "pool": {
                    "address": pool_address, "token0": token0, "token1": token1,
                    "fee": pool_fee, "current_tick": current_tick,
                    "fee_growth_global0_x128": str(fee_global0),
                    "fee_growth_global1_x128": str(fee_global1),
                    "lower_fee_growth_outside0_x128": str(lower_tick.fee_growth_outside0_x128),
                    "lower_fee_growth_outside1_x128": str(lower_tick.fee_growth_outside1_x128),
                    "upper_fee_growth_outside0_x128": str(upper_tick.fee_growth_outside0_x128),
                    "upper_fee_growth_outside1_x128": str(upper_tick.fee_growth_outside1_x128),
                },
                "fees": {
                    "token0_raw": str(owed0), "token1_raw": str(owed1),
                    "token0_human": format_units(owed0, decimals0),
                    "token1_human": format_units(owed1, decimals1),
                    "token0_symbol": symbol0, "token1_symbol": symbol1,
                    "token0_decimals": decimals0, "token1_decimals": decimals1,
                    "method": "feeGrowthInside Q128 + stored tokensOwed",
                },
                "data_status": "fresh",
            }
            raw_json = json.dumps(raw_payload, sort_keys=True, separators=(",", ":"))
            raw_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
            raw_id = store.add_provider_payload(
                source="base_rpc:uniswap_v3_nft",
                entity_id=position_id,
                fetched_at=fetched_at,
                payload_json=raw_json,
                payload_hash=raw_hash,
            )
            snapshot = PositionSnapshot(
                position_id=position_id, wallet_address=wallet,
                chain_id=CHAIN_ID, protocol="Uniswap", version="V3",
                pool_id=pool_id, observed_at=observed_at, fetched_at=fetched_at,
                source="base_rpc:uniswap_v3_nft",
                source_url=f"{SOURCE_URL}/token/{POSITION_MANAGER}?a={token_id}",
                data_status="fresh", liquidity_raw=str(position.liquidity),
                tick_lower=position.tick_lower, tick_upper=position.tick_upper,
                current_tick=current_tick,
                in_range=(position.tick_lower <= current_tick < position.tick_upper),
                raw_ref=str(raw_id),
            )
            store.add_position_snapshot(snapshot)
            store.add_position_fee_snapshot({
                "position_id": position_id, "token_id": str(token_id),
                "wallet_address": wallet, "block_number": block_number,
                "block_hash": block_hash, "block_timestamp": observed_at,
                "pool_address": pool_address,
                "token0_address": position.token0, "token1_address": position.token1,
                "token0_symbol": symbol0, "token1_symbol": symbol1,
                "token0_decimals": decimals0, "token1_decimals": decimals1,
                "tokens_owed0_raw": str(owed0), "tokens_owed1_raw": str(owed1),
                "tokens_owed0_human": format_units(owed0, decimals0),
                "tokens_owed1_human": format_units(owed1, decimals1),
                "current_tick": current_tick, "tick_lower": position.tick_lower,
                "tick_upper": position.tick_upper, "liquidity_raw": str(position.liquidity),
                "fee_tier": position.fee, "data_status": "fresh",
                "raw_ref": str(raw_id),
            })
            positions.append({
                "token_id": str(token_id), "position_id": position_id,
                "pool_address": pool_address, "token0": symbol0, "token1": symbol1,
                "fee_tier": position.fee, "tick_lower": position.tick_lower,
                "tick_upper": position.tick_upper, "current_tick": current_tick,
                "in_range": snapshot.in_range, "liquidity_raw": str(position.liquidity),
                "unclaimed_fee0": f"{format_units(owed0, decimals0)} {symbol0}",
                "unclaimed_fee1": f"{format_units(owed1, decimals1)} {symbol1}",
                "raw_ref": raw_id,
            })

        return {
            "status": "ok", "chain_id": CHAIN_ID, "wallet": wallet,
            "block_number": block_number, "block_hash": block_hash,
            "observed_at": observed_at, "position_count": len(positions),
            "positions": positions, "fee_values_unit": "token units; not USD",
            "data_status": "fresh",
        }
    finally:
        if owns_rpc:
            rpc.close()
