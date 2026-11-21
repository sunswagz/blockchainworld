"""Offline fixtures for unified wallet monitor persistence."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lp_intelligence.storage import SQLiteStore


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="wallet-monitor-") as tmp:
        store = SQLiteStore(Path(tmp) / "wallet.sqlite")
        store.initialize()
        wallet = "0x" + "1" * 40
        store.add_wallet_baseline({
            "wallet_address": wallet, "chain_id": "196", "chain_name": "X Layer",
            "baseline_block": 123, "baseline_hash": "0x" + "a" * 64,
            "baseline_timestamp": "2026-11-22T00:00:00Z",
            "scan_from_block": 123, "created_at": "2026-11-22T00:00:00Z",
        })
        baseline = store.get_wallet_baseline(wallet, "196")
        assert baseline and baseline["scan_from_block"] == 123
        store.add_xlayer_position_snapshot(wallet,
            {"number": 130, "hash": "0x" + "b" * 64, "timestamp": 1000},
            {"token_id": "7", "pool_address": "0x" + "2" * 40,
             "token0": "0x" + "3" * 40, "token1": "0x" + "4" * 40,
             "fee_tier": 500, "tick_lower": -100, "tick_upper": 100,
             "current_tick": 0, "liquidity_raw": "900",
             "tokens_owed0_raw": "11", "tokens_owed1_raw": "12",
             "range_status": "in_range", "verification": "owner_and_factory_confirmed"})
        positions = store.list_xlayer_positions(wallet)
        assert len(positions) == 1 and positions[0]["token_id"] == "7"
        result = {"chains": {"196": {"owned_positions": 1}}}
        store.add_wallet_monitor_run(wallet, "2026-11-22T00:00:00Z", "ok", result)
        runs = store.list_wallet_monitor_runs(wallet)
        assert runs[0]["result"]["chains"]["196"]["owned_positions"] == 1
    print("Unified wallet monitor persistence fixtures passed: 4/4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
