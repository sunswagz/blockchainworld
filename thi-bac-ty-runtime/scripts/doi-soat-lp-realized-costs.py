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


def scan_token_events(rpc: JsonRpcClient, token_id: int, from_block: int,
                      to_block: int, chunk_size: int, wallet: str) -> list[dict]:
    token_topic = "0x" + format(token_id, "064x")
    logs = []
    cursor = from_block
    topics = list(EVENT_TOPICS)
    while cursor <= to_block:
        end = min(cursor + chunk_size - 1, to_block)
        for topic in topics:
            logs.extend(rpc.get_logs(
                address=POSITION_MANAGER, from_block=cursor, to_block=end,
                topics=[topic, token_topic] if topic != TRANSFER_TOPIC else [topic, None, None, token_topic],
            ))
        cursor = end + 1
    decoded = [decode_position_manager_event(item, wallet) for item in logs]
    return sorted(decoded, key=lambda x: (
        x["block_number"], x["transaction_index"], x["log_index"]
    ))


def owned_events(events: list[dict], wallet: str) -> tuple[list[dict], str]:
    """Filter events to wallet ownership intervals; report whether entry basis is knowable."""
    active = False
    saw_incoming = False
    basis_known = False
    selected = []
    for event in events:
        if event["event_type"] == "Transfer":
            sender = event.get("from_address")
            recipient = event.get("recipient")
            if sender == wallet:
                if active:
                    selected.append(event)
                active = False
            if recipient == wallet:
                selected.append(event)
                if not saw_incoming:
                    saw_incoming = True
                    basis_known = sender == ZERO_ADDRESS
                elif sender != ZERO_ADDRESS:
                    basis_known = False
                active = True
        elif active:
            selected.append(event)
    if not saw_incoming:
        return [], "incomplete_transfer_history"
    if active and basis_known:
        return selected, "minted_to_wallet"
    if active:
        return selected, "acquired_by_transfer_or_reacquired"
    return selected, "position_no_longer_held"


def price_usd_at(store: SQLiteStore, token: str, observed_at: str,
                 max_skew_seconds: int) -> Decimal | None:
    item = store.token_price_near(CHAIN_ID, token, observed_at, max_skew_seconds)
    if not item:
        return None
    return Decimal(str(item["price_usd"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True)
    parser.add_argument("--from-block", type=int, required=True,
                        help="Must include the first NFT transfer into this wallet for complete attribution")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--max-price-skew-seconds", type=int, default=300)
    parser.add_argument("--rpc-url", default=None)
    args = parser.parse_args()
    wallet = args.wallet.lower()
    if not (wallet.startswith("0x") and len(wallet) == 42):
        raise ValueError("wallet must be a 20-byte EVM address")
    if args.from_block < 0 or not 1 <= args.chunk_size <= 5000:
        raise ValueError("invalid block range or chunk size")
    if args.max_price_skew_seconds < 0:
        raise ValueError("max price skew cannot be negative")

    store = SQLiteStore()
    store.initialize()
    fee_rows = store.list_position_fees(wallet, limit=500)
    if not fee_rows:
        raise RuntimeError("No position snapshots for this wallet; run the Base NFT position collector first")

    rpc = JsonRpcClient(args.rpc_url or __import__("os").getenv("BASE_RPC_URL", "https://mainnet.base.org"))
    try:
        latest_block = rpc.get_block_number()
        if args.from_block > latest_block:
            raise ValueError("--from-block is ahead of Base latest block")
        block_cache: dict[int, tuple[str, str]] = {}
        metadata = {row["position_id"]: row for row in fee_rows}
        per_position_events: dict[str, list[dict]] = {}
        tx_positions: dict[str, set[str]] = defaultdict(set)
        event_count = 0
        ownership_status = {}

        for row in fee_rows:
            token_id = int(row["token_id"])
            events = scan_token_events(rpc, token_id, args.from_block, latest_block,
                                       args.chunk_size, wallet)
            selected, basis_status = owned_events(events, wallet)
            position_id = row["position_id"]
            ownership_status[position_id] = basis_status
            if basis_status == "incomplete_transfer_history":
                raise RuntimeError(
                    f"Token {token_id}: no incoming Transfer found in scan range. "
                    "Choose an earlier --from-block; refusing to guess ownership or fees."
                )
            per_position_events[position_id] = selected
            for event in selected:
                event["position_id"] = position_id
                store.add_lp_position_event(event)
                event_count += 1
                tx_positions[event["tx_hash"]].add(position_id)

        # Transaction costs are recorded only when this wallet is the transaction sender.
        gas_by_position: dict[str, int] = defaultdict(int)
        cost_tx_count = 0
        for tx_hash, position_ids in tx_positions.items():
            tx = rpc.get_transaction(tx_hash)
            if tx.get("from", "").lower() != wallet:
                continue
            receipt = rpc.get_transaction_receipt(tx_hash)
            gas_used = int(receipt["gasUsed"], 16)
            effective_gas_price = int(receipt.get("effectiveGasPrice", tx.get("gasPrice", "0x0")), 16)
            l1_fee = int(receipt.get("l1Fee", "0x0"), 16)
            total_fee = gas_used * effective_gas_price + l1_fee
            block_number = int(receipt["blockNumber"], 16)
            timestamp, block_hash = iso_timestamp(rpc, block_number, block_cache)
            allocations = allocate_transaction_gas(total_fee, list(position_ids))
            for position_id, amount in allocations.items():
                gas_by_position[position_id] += amount
            store.add_lp_transaction_cost({
                "chain_id": CHAIN_ID, "tx_hash": tx_hash, "wallet_address": wallet,
                "tx_from": tx.get("from", "").lower(), "tx_to": (tx.get("to") or "").lower(),
                "block_number": block_number, "block_hash": block_hash,
                "block_timestamp": timestamp, "receipt_status": receipt.get("status", "unknown"),
                "gas_used": str(gas_used), "effective_gas_price_wei": str(effective_gas_price),
                "l1_fee_wei": str(l1_fee), "total_fee_wei": str(total_fee),
                "native_symbol": "ETH", "position_ids_json": json.dumps(sorted(position_ids)),
                "allocation_method": "equal split across distinct wallet-held positions touched in transaction",
                "data_status": "fresh" if "l1Fee" in receipt else "provisional_l1_fee_field_missing",
                "raw_receipt_json": json.dumps(receipt, sort_keys=True),
            })
            cost_tx_count += 1

        summaries = []
        for position_id, events in per_position_events.items():
            row = metadata[position_id]
            cash = attribute_position_cashflows(events)
            contributed_usd = Decimal(0)
            recovered_usd = Decimal(0)
            realized_fees_usd = Decimal(0)
            price_coverage = True
            principal_owed0 = principal_owed1 = 0
            for event in sorted(events, key=lambda x: (
                x["block_number"], x["transaction_index"], x["log_index"]
            )):
                kind = event["event_type"]
                if kind == "DecreaseLiquidity":
                    principal_owed0 += int(event["amount0_raw"])
                    principal_owed1 += int(event["amount1_raw"])
                elif kind == "IncreaseLiquidity":
                    p0 = price_usd_at(store, row["token0_address"], iso_timestamp(rpc, event["block_number"], block_cache)[0], args.max_price_skew_seconds)
                    p1 = price_usd_at(store, row["token1_address"], iso_timestamp(rpc, event["block_number"], block_cache)[0], args.max_price_skew_seconds)
                    if p0 is None or p1 is None:
                        price_coverage = False
                    else:
                        contributed_usd += (
                            Decimal(event["amount0_raw"]) / (Decimal(10) ** int(row["token0_decimals"])) * p0
                            + Decimal(event["amount1_raw"]) / (Decimal(10) ** int(row["token1_decimals"])) * p1
                        )
                elif kind == "Collect":
                    amount0, amount1 = int(event["amount0_raw"]), int(event["amount1_raw"])
                    principal0, principal1 = min(principal_owed0, amount0), min(principal_owed1, amount1)
                    principal_owed0 -= principal0
                    principal_owed1 -= principal1
                    fee0, fee1 = amount0 - principal0, amount1 - principal1
                    timestamp = iso_timestamp(rpc, event["block_number"], block_cache)[0]
                    p0 = price_usd_at(store, row["token0_address"], timestamp, args.max_price_skew_seconds)
                    p1 = price_usd_at(store, row["token1_address"], timestamp, args.max_price_skew_seconds)
                    if p0 is None or p1 is None:
                        price_coverage = False
                    else:
                        scale0, scale1 = Decimal(10) ** int(row["token0_decimals"]), Decimal(10) ** int(row["token1_decimals"])
                        realized_fees_usd += Decimal(fee0) / scale0 * p0 + Decimal(fee1) / scale1 * p1
                        recovered_usd += Decimal(principal0) / scale0 * p0 + Decimal(principal1) / scale1 * p1

            gas_wei = gas_by_position.get(position_id, 0)
            latest = store.list_position_performance(position_id=position_id, limit=1)
            current_value = Decimal(str(latest[0]["position_value_usd"])) if latest else None
            gas_price = price_usd_at(store, WETH_BASE, iso_timestamp(rpc, latest_block, block_cache)[0], args.max_price_skew_seconds)
            gas_usd = (Decimal(gas_wei) / Decimal(10**18) * gas_price) if gas_price is not None else None
            # Net PnL is only meaningful when acquisition basis, all event prices and current valuation exist.
            net_pnl = None
            status_parts = []
            if ownership_status[position_id] != "minted_to_wallet":
                status_parts.append("unknown_acquisition_basis")
            if not price_coverage:
                status_parts.append("missing_historical_token_prices")
            if current_value is None:
                status_parts.append("missing_current_position_valuation")
            if gas_wei and gas_usd is None:
                status_parts.append("missing_native_gas_price")
            if not status_parts and current_value is not None and gas_usd is not None:
                net_pnl = current_value + recovered_usd + realized_fees_usd - contributed_usd - gas_usd
                accounting_status = "provisional_net_pnl"
            else:
                accounting_status = "partial:" + ",".join(status_parts or ["incomplete"])
            snapshot = {
                "position_id": position_id, "wallet_address": wallet, "chain_id": CHAIN_ID,
                "block_number": latest_block, "block_hash": rpc.get_block(latest_block)["hash"].lower(),
                "observed_at": iso_timestamp(rpc, latest_block, block_cache)[0],
                "token0_address": row["token0_address"], "token1_address": row["token1_address"],
                "token0_symbol": row["token0_symbol"], "token1_symbol": row["token1_symbol"],
                "liquidity_contributed0_raw": cash["liquidity_contributed0_raw"],
                "liquidity_contributed1_raw": cash["liquidity_contributed1_raw"],
                "principal_owed0_raw": cash["principal_owed0_raw"],
                "principal_owed1_raw": cash["principal_owed1_raw"],
                "principal_recovered0_raw": cash["principal_recovered0_raw"],
                "principal_recovered1_raw": cash["principal_recovered1_raw"],
                "realized_fees0_raw": cash["realized_fees0_raw"],
                "realized_fees1_raw": cash["realized_fees1_raw"],
                "realized_fees_usd": float(realized_fees_usd) if price_coverage else None,
                "principal_recovered_usd": float(recovered_usd) if price_coverage else None,
                "gas_cost_native_wei": str(gas_wei),
                "gas_cost_usd": float(gas_usd) if gas_usd is not None else None,
                "net_pnl_usd": float(net_pnl) if net_pnl is not None else None,
                "accounting_status": accounting_status,
                "methodology_json": json.dumps({
                    "realized_fee_attribution": cash["attribution_method"],
                    "ownership": ownership_status[position_id],
                    "gas": "receipt gasUsed * effectiveGasPrice + Base receipt l1Fee; equally allocated across touched positions and valued at event-time ETH/WETH price",
                    "usd_prices": "nearest stored token price within configured event-time skew; missing prices remain unknown",
                    "net_pnl": "current position value + principal recovered + realized fees - liquidity contributions - attributed gas",
                    "limitations": ["NFT transfer acquisition price is unknown unless minted directly to wallet",
                                    "external swap/rebalance costs outside NPM lifecycle logs are not included",
                                    "token price history must be ingested near each event timestamp"],
                }, sort_keys=True),
            }
            store.add_lp_position_accounting_snapshot(snapshot)
            summaries.append({
                "position_id": position_id, "token_id": row["token_id"],
                "realized_fees0_raw": cash["realized_fees0_raw"],
                "realized_fees1_raw": cash["realized_fees1_raw"],
                "principal_recovered0_raw": cash["principal_recovered0_raw"],
                "principal_recovered1_raw": cash["principal_recovered1_raw"],
                "gas_cost_native_wei": str(gas_wei), "gas_cost_usd": snapshot["gas_cost_usd"],
                "net_pnl_usd": snapshot["net_pnl_usd"], "accounting_status": accounting_status,
            })

        print(json.dumps({
            "status": "ok", "wallet": wallet, "chain_id": CHAIN_ID,
            "from_block": args.from_block, "to_block": latest_block,
            "events_persisted": event_count, "wallet_paid_transactions": cost_tx_count,
            "positions": summaries,
        }, indent=2))
        return 0
    finally:
        rpc.close()


if __name__ == "__main__":
    raise SystemExit(main())
