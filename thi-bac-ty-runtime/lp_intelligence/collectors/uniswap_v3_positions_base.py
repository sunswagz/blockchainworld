"""Read-only Uniswap V3/Base NFT position and fee collector.

Discovers candidate token IDs from ERC-721 Transfer logs, then verifies current
ownership and position state. All contract reads are pinned to one block.
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
from ..fee_accounting import decode_position_fee_state, decode_tick_fee_state, encode_tick_call, position_unclaimed_fees_raw
from ..storage import SQLiteStore

CHAIN_ID = "8453"
FACTORY = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
POSITION_MANAGER = "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1"
SOURCE_URL = "https://basescan.org"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
OWNER_OF_SELECTOR = "0x6352211e"
POOL_SELECTORS = {
    "token0": "0x0dfe1681", "token1": "0xd21220a7", "slot0": "0x3850c7bd",
    "fee_growth_global0": "0xf3058399", "fee_growth_global1": "0x46141319",
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
        return bytes.fromhex(raw).rstrip(b"\\x00").decode("utf-8", errors="replace")
    if len(raw) < 128:
        raise ValueError("short ABI dynamic string")
    offset = int(raw[:64], 16) * 2
    if offset + 64 > len(raw):
        raise ValueError("invalid ABI string offset")
    length = int(raw[offset:offset + 64], 16)
    start, end = offset + 64, offset + 64 + length * 2
    if end > len(raw):
        raise ValueError("truncated ABI string")
    return bytes.fromhex(raw[start:end]).decode("utf-8", errors="replace")

def format_units(raw_amount: int, decimals: int) -> str:
    if raw_amount < 0 or not 0 <= decimals <= 255:
        raise ValueError("invalid token amount or decimals")
    return format(Decimal(raw_amount) / (Decimal(10) ** decimals), "f")

def _iso_from_block_timestamp(timestamp_hex: str) -> str:
    value = datetime.fromtimestamp(int(timestamp_hex, 16), tz=timezone.utc)
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")

def _call_address(rpc: JsonRpcClient, to: str, data: str, block_tag: str) -> str:
    return decode_address(rpc.eth_call(to, data, block_tag))

def _wallet_topic(wallet: str) -> str:
    return "0x" + _address_word(wallet)

def discover_wallet_token_ids(
    rpc: JsonRpcClient, wallet: str, *, from_block: int, to_block: int,
    chunk_size: int = 2000,
) -> list[int]:
    """Find all NFT IDs transferred into or out of wallet within the scan range."""
    if from_block < 0 or to_block < from_block:
        raise ValueError("invalid block scan range")
    if not 1 <= chunk_size <= 10000:
        raise ValueError("chunk_size must be between 1 and 10000")
    topic_wallet = _wallet_topic(wallet)
    token_ids: set[int] = set()
    cursor = from_block
    while cursor <= to_block:
        end = min(cursor + chunk_size - 1, to_block)
        incoming = rpc.get_logs(
            address=POSITION_MANAGER, from_block=cursor, to_block=end,
            topics=[TRANSFER_TOPIC, None, topic_wallet],
        )
        outgoing = rpc.get_logs(
            address=POSITION_MANAGER, from_block=cursor, to_block=end,
            topics=[TRANSFER_TOPIC, topic_wallet],
        )
        for log in [*incoming, *outgoing]:
            topics = log.get("topics", [])
            if len(topics) >= 4 and topics[0].lower() == TRANSFER_TOPIC:
                token_ids.add(int(topics[3], 16))
        cursor = end + 1
    return sorted(token_ids)

def collect_uniswap_v3_base_positions(
    wallet_address: str, *, from_block: int,
    rpc_url: str | None = None, store: SQLiteStore | None = None,
    rpc: JsonRpcClient | None = None, max_positions: int = 100,
    log_chunk_size: int = 2000,
) -> dict[str, Any]:
    wallet = "0x" + _address_word(wallet_address)[-40:]
    if max_positions < 1 or max_positions > 1000:
        raise ValueError("max_positions must be between 1 and 1000")
    owns_rpc = rpc is None
    rpc = rpc or JsonRpcClient(rpc_url or os.getenv("BASE_RPC_URL", "https://mainnet.base.org"))
    store = store or SQLiteStore()
    store.initialize()
    try:
        block_number = rpc.get_block_number()
        if from_block > block_number:
            raise ValueError("from_block is ahead of the latest block")
        block_tag = hex(block_number)
        block = rpc.get_block(block_number)
        block_hash = block["hash"].lower()
        observed_at = _iso_from_block_timestamp(block["timestamp"])
        fetched_at = utc_now()

        candidate_ids = discover_wallet_token_ids(
            rpc, wallet, from_block=from_block, to_block=block_number,
            chunk_size=log_chunk_size,
        )
        if len(candidate_ids) > max_positions * 10:
            raise RuntimeError(
                f"Scan found {len(candidate_ids)} candidate NFT IDs; exceeds safety bound "
                f"{max_positions * 10}. Narrow from_block or raise limits deliberately."
            )

        positions: list[dict[str, Any]] = []
        for token_id in candidate_ids:
            try:
                owner = _call_address(
                    rpc, POSITION_MANAGER, encode_uint_call(OWNER_OF_SELECTOR, token_id), block_tag,
                )
            except Exception:
                # A burned token or an ID no longer existing is not a current wallet position.
                continue
            if owner != wallet:
                continue
            position = decode_position_fee_state(rpc.eth_call(
                POSITION_MANAGER, encode_uint_call("0x99fbab88", token_id), block_tag,
            ))
            pool_address = decode_address(rpc.eth_call(
                FACTORY, factory_get_pool_calldata(position.token0, position.token1, position.fee),
                block_tag,
            ))
            if pool_address == ZERO_ADDRESS:
                raise RuntimeError(f"NFT {token_id} references a pool not found in official factory")

            token0 = _call_address(rpc, pool_address, POOL_SELECTORS["token0"], block_tag)
            token1 = _call_address(rpc, pool_address, POOL_SELECTORS["token1"], block_tag)
            pool_fee = decode_uint(rpc.eth_call(pool_address, POOL_SELECTORS["fee"], block_tag))
            if (token0, token1, pool_fee) != (position.token0, position.token1, position.fee):
                raise RuntimeError(f"NFT {token_id} does not reconcile with its factory pool identity")

            slot0 = rpc.eth_call(pool_address, POOL_SELECTORS["slot0"], block_tag)
            current_tick = decode_int24_word(slot0, 1)
            fee_global0 = decode_uint(rpc.eth_call(pool_address, POOL_SELECTORS["fee_growth_global0"], block_tag))
            fee_global1 = decode_uint(rpc.eth_call(pool_address, POOL_SELECTORS["fee_growth_global1"], block_tag))
            lower_tick = decode_tick_fee_state(rpc.eth_call(pool_address, encode_tick_call(position.tick_lower), block_tag))
            upper_tick = decode_tick_fee_state(rpc.eth_call(pool_address, encode_tick_call(position.tick_upper), block_tag))
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
                raise RuntimeError("ERC20 symbol is empty; refusing ambiguous fee amounts")

            pool_id = f"{CHAIN_ID}:uniswap-v3:{pool_address.lower()}"
            position_id = f"{CHAIN_ID}:uniswap-v3:nft:{token_id}"
            human0, human1 = format_units(owed0, decimals0), format_units(owed1, decimals1)
            raw_payload = {
                "chain_id": CHAIN_ID, "block_number": block_number, "block_hash": block_hash,
                "block_timestamp": observed_at, "scan_from_block": from_block,
                "wallet": wallet, "token_id": str(token_id), "owner_of": owner,
                "position": {
                    "token0": position.token0, "token1": position.token1, "fee": position.fee,
                    "tick_lower": position.tick_lower, "tick_upper": position.tick_upper,
                    "liquidity_raw": str(position.liquidity),
                    "fee_growth_inside0_last_x128": str(position.fee_growth_inside0_last_x128),
                    "fee_growth_inside1_last_x128": str(position.fee_growth_inside1_last_x128),
                    "tokens_owed0_stored_raw": str(position.tokens_owed0),
                    "tokens_owed1_stored_raw": str(position.tokens_owed1),
                },
                "pool": {
                    "address": pool_address, "token0": token0, "token1": token1,
                    "fee": pool_fee, "current_tick": current_tick,
                    "sqrt_price_x96": str(decode_uint(slot0, 0)),
                    "fee_growth_global0_x128": str(fee_global0),
                    "fee_growth_global1_x128": str(fee_global1),
                    "lower_fee_growth_outside0_x128": str(lower_tick.fee_growth_outside0_x128),
                    "lower_fee_growth_outside1_x128": str(lower_tick.fee_growth_outside1_x128),
                    "upper_fee_growth_outside0_x128": str(upper_tick.fee_growth_outside0_x128),
                    "upper_fee_growth_outside1_x128": str(upper_tick.fee_growth_outside1_x128),
                },
                "fees": {
                    "token0_raw": str(owed0), "token1_raw": str(owed1),
                    "token0_human": human0, "token1_human": human1,
                    "token0_symbol": symbol0, "token1_symbol": symbol1,
                    "token0_decimals": decimals0, "token1_decimals": decimals1,
                    "method": "feeGrowthInside Q128 + stored tokensOwed",
                },
                "data_status": "fresh",
            }
            raw_json = json.dumps(raw_payload, sort_keys=True, separators=(",", ":"))
            raw_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
            raw_id = store.add_provider_payload(
                source="base_rpc:uniswap_v3_nft", entity_id=position_id,
                fetched_at=fetched_at, payload_json=raw_json, payload_hash=raw_hash,
            )
            snapshot = PositionSnapshot(
                position_id=position_id, wallet_address=wallet, chain_id=CHAIN_ID,
                protocol="Uniswap", version="V3", pool_id=pool_id,
                observed_at=observed_at, fetched_at=fetched_at,
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
                "pool_address": pool_address, "token0_address": position.token0,
                "token1_address": position.token1, "token0_symbol": symbol0,
                "token1_symbol": symbol1, "token0_decimals": decimals0,
                "token1_decimals": decimals1, "tokens_owed0_raw": str(owed0),
                "tokens_owed1_raw": str(owed1), "tokens_owed0_human": human0,
                "tokens_owed1_human": human1, "current_tick": current_tick,
                "tick_lower": position.tick_lower, "tick_upper": position.tick_upper,
                "liquidity_raw": str(position.liquidity), "fee_tier": position.fee,
                "data_status": "fresh", "raw_ref": str(raw_id),
            })
            positions.append({
                "token_id": str(token_id), "position_id": position_id,
                "pool_address": pool_address, "token0": symbol0, "token1": symbol1,
                "fee_tier": position.fee, "tick_lower": position.tick_lower,
                "tick_upper": position.tick_upper, "current_tick": current_tick,
                "in_range": snapshot.in_range, "liquidity_raw": str(position.liquidity),
                "unclaimed_fee0": f"{human0} {symbol0}", "unclaimed_fee1": f"{human1} {symbol1}",
                "raw_ref": raw_id,
            })

        return {
            "status": "ok", "chain_id": CHAIN_ID, "wallet": wallet,
            "scan_from_block": from_block, "block_number": block_number,
            "block_hash": block_hash, "observed_at": observed_at,
            "candidate_token_ids": len(candidate_ids), "position_count": len(positions),
            "positions": positions, "fee_values_unit": "underlying token units; not USD",
            "data_status": "fresh",
        }
    finally:
        if owns_rpc:
            rpc.close()
