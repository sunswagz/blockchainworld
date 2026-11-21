#!/usr/bin/env python3
"""Record USD valuation and HODL-relative performance for Base Uniswap V3 NFTs.

Supply explicit token USD price observations in a JSON file. The script refuses
missing/stale prices and never substitutes zero. Claimed fees and gas are not
fabricated; PnL is explicitly before those items.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lp_intelligence.contracts import parse_utc, utc_now
from lp_intelligence.performance import compare_to_hodl, value_position
from lp_intelligence.storage import SQLiteStore


def load_prices(store: SQLiteStore, path: str | None) -> None:
    if not path:
        return
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("prices JSON must be a list of token price observations")
    fetched_at = utc_now()
    for item in data:
        required = ("chain_id", "token_address", "price_usd", "observed_at", "source", "source_url")
        if any(key not in item for key in required):
            raise ValueError(f"each price item requires: {', '.join(required)}")
        parse_utc(item["observed_at"])
        if not str(item["source_url"]).startswith("https://"):
            raise ValueError("price source_url must use HTTPS")
        price = float(item["price_usd"])
        if price <= 0:
            raise ValueError("token USD price must be positive")
        store.add_token_price_observation({
            **item, "price_usd": price, "fetched_at": fetched_at,
            "data_status": item.get("data_status", "fresh"),
        })


def get_fresh_price(store: SQLiteStore, chain_id: str, address: str,
                    now: datetime, max_age_minutes: int) -> dict:
    item = store.latest_token_price(chain_id, address)
    if item is None:
        raise ValueError(f"Missing USD price observation for token {address}")
    age = now - parse_utc(item["observed_at"])
    if age < timedelta(minutes=-5) or age > timedelta(minutes=max_age_minutes):
        raise ValueError(f"Stale/future USD price for token {address}: age={age}")
    if item["data_status"] not in ("fresh", "provisional"):
        raise ValueError(f"Price observation status is not usable: {item['data_status']}")
    return item


def window_apr(history: list[dict], current: dict, hours: int) -> float | None:
    now = parse_utc(current["observed_at"])
    cutoff = now - timedelta(hours=hours)
    candidates = [x for x in history if parse_utc(x["observed_at"]) <= cutoff]
    if not candidates:
        return None
    previous = candidates[-1]
    elapsed = (now - parse_utc(previous["observed_at"])).total_seconds() / 3600
    if elapsed <= 0 or elapsed > hours + 6:
        return None
    fee_delta = Decimal(current["unclaimed_fees_usd"]) - Decimal(previous["unclaimed_fees_usd"])
    if fee_delta < 0:
        # A fee collection or other reset may have occurred; do not annualize a negative delta.
        return None
    capital = (Decimal(current["principal_usd"]) + Decimal(previous["principal_usd"])) / 2
    if capital <= 0:
        return None
    apr = fee_delta / capital * Decimal(8760) / Decimal(str(elapsed)) * Decimal(100)
    return float(apr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True)
    parser.add_argument("--prices-json", help="JSON list of explicit token USD price observations")
    parser.add_argument("--max-price-age-minutes", type=int, default=60)
    args = parser.parse_args()
    wallet = "0x" + args.wallet.strip().removeprefix("XKO").removeprefix("0x").lower()
    if len(wallet) != 42 or any(c not in "0123456789abcdef" for c in wallet[2:]):
        raise ValueError("Invalid EVM wallet address")
    if args.max_price_age_minutes < 1:
        raise ValueError("max price age must be positive")

    store = SQLiteStore()
    store.initialize()
    load_prices(store, args.prices_json)
    fee_rows = store.list_position_fees(wallet, limit=500)
    if not fee_rows:
        raise RuntimeError("No Base position fee snapshots found. Run the wallet monitor first.")

    now = datetime.now(timezone.utc)
    output = []
    for fee in fee_rows:
        raw = store.get_provider_payload(int(fee["raw_ref"])) if fee.get("raw_ref") else None
        if not raw:
            raise RuntimeError(f"Missing raw on-chain payload for {fee['position_id']}")
        payload = raw["payload"]
        sqrt_price_x96 = int(payload["pool"]["sqrt_price_x96"])
        pos = payload["position"]
        p0 = get_fresh_price(store, fee["chain_id"], fee["token0_address"], now, args.max_price_age_minutes)
        p1 = get_fresh_price(store, fee["chain_id"], fee["token1_address"], now, args.max_price_age_minutes)
        valued = value_position(
            liquidity_raw=int(fee["liquidity_raw"]), sqrt_price_x96=sqrt_price_x96,
            tick_lower=int(fee["tick_lower"]), tick_upper=int(fee["tick_upper"]),
            decimals0=int(fee["token0_decimals"]), decimals1=int(fee["token1_decimals"]),
            fees0_raw=int(fee["tokens_owed0_raw"]), fees1_raw=int(fee["tokens_owed1_raw"]),
            price0_usd=Decimal(str(p0["price_usd"])), price1_usd=Decimal(str(p1["price_usd"])),
        )
        history = list(reversed(store.list_position_performance(position_id=fee["position_id"], limit=5000)))
        initial = history[0] if history else None
        if initial:
            baseline_amount0, baseline_amount1 = Decimal(initial["amount0"]), Decimal(initial["amount1"])
            initial_capital = Decimal(initial["initial_capital_usd"] or initial["principal_usd"])
            comparison = compare_to_hodl(
                current_principal_usd=Decimal(valued["principal_usd"]),
                current_fees_usd=Decimal(valued["unclaimed_fees_usd"]),
                current_price0_usd=Decimal(str(p0["price_usd"])),
                current_price1_usd=Decimal(str(p1["price_usd"])),
                initial_amount0=baseline_amount0, initial_amount1=baseline_amount1,
                initial_capital_usd=initial_capital,
            )
        else:
            initial_capital = Decimal(valued["principal_usd"])
            comparison = compare_to_hodl(
                current_principal_usd=Decimal(valued["principal_usd"]),
                current_fees_usd=Decimal(valued["unclaimed_fees_usd"]),
                current_price0_usd=Decimal(str(p0["price_usd"])),
                current_price1_usd=Decimal(str(p1["price_usd"])),
                initial_amount0=Decimal(valued["amount0"]),
                initial_amount1=Decimal(valued["amount1"]),
                initial_capital_usd=initial_capital,
            )
        current = {
            "observed_at": fee["block_timestamp"], "principal_usd": valued["principal_usd"],
            "unclaimed_fees_usd": valued["unclaimed_fees_usd"],
        }
        apr24 = window_apr(history, current, 24)
        apr7 = window_apr(history, current, 24 * 7)
        apr30 = window_apr(history, current, 24 * 30)
        methodology = {
            "valuation": "Uniswap V3 liquidity amounts from sqrtPriceX96 and tick bounds",
            "hodl_baseline": "first saved performance snapshot after onboarding; not NFT mint",
            "il": "current LP principal minus mark-to-market value of initial token amounts",
            "fee_apr": "provisional change in unclaimed fee balance; null if no suitable prior point or fee balance fell",
            "price_sources": [p0["source"], p1["source"]],
            "price_observed_at": [p0["observed_at"], p1["observed_at"]],
            "claimed_fees": "not included; collect-event accounting not yet implemented",
            "gas_and_rebalance_costs": "not included; no verified cost ledger yet",
            "pnl": "before claimed fees, gas and rebalance costs",
        }
        record = {
            "position_id": fee["position_id"], "wallet_address": wallet,
            "chain_id": fee["chain_id"], "block_number": fee["block_number"],
            "block_hash": fee["block_hash"], "observed_at": fee["block_timestamp"],
            "fetched_at": utc_now(), "token0_address": fee["token0_address"],
            "token1_address": fee["token1_address"], "token0_symbol": fee["token0_symbol"],
            "token1_symbol": fee["token1_symbol"], **valued,
            "initial_capital_usd": str(initial_capital), **comparison,
            "fee_apr_24h_pct": apr24, "fee_apr_7d_pct": apr7,
            "fee_apr_30d_pct": apr30, "claimed_fees_usd": None,
            "gas_cost_usd": None, "rebalance_cost_usd": None,
            "data_status": "provisional", "methodology_json": json.dumps(methodology, sort_keys=True),
        }
        # Convert Decimal-derived string fields to SQLite numeric values where schema expects REAL.
        for key in ("price0_usd", "price1_usd", "principal_usd", "unclaimed_fees_usd",
                    "position_value_usd", "initial_capital_usd", "hodl_value_usd",
                    "il_vs_hodl_usd", "il_vs_hodl_pct", "fee_adjusted_vs_hodl_usd",
                    "pnl_before_claimed_fees_and_costs_usd"):
            record[key] = float(record[key])
        store.add_position_performance_snapshot(record)
        output.append(record)

    print(json.dumps({"wallet": wallet, "positions_valued": len(output),
                      "status": "provisional", "data": output}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
