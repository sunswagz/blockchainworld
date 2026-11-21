"""Read-only FastAPI surface for LP Intelligence."""
from __future__ import annotations

import os
from fastapi import FastAPI, Query
from .storage import SQLiteStore

app = FastAPI(
    title="LP Intelligence API",
    version="0.1.0",
    description="Read-only DEX LP monitoring. No wallet signing or transaction endpoints.",
)
store = SQLiteStore(os.getenv("LP_INTELLIGENCE_DB", "data/lp-intelligence.sqlite"))


@app.on_event("startup")
def initialize() -> None:
    store.initialize()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "lp-intelligence", "version": "0.1.0"}


@app.get("/api/v1/pools")
def pools(limit: int = Query(default=100, ge=1, le=500)) -> dict:
    data = store.list_pools(limit=limit)
    return {"data": data, "count": len(data)}


@app.get("/api/v1/positions")
def positions(
    wallet: str | None = Query(default=None, min_length=4, max_length=128),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    data = store.list_positions(wallet=wallet, limit=limit)
    return {"data": data, "count": len(data)}


@app.get("/api/v1/position-fees")
def position_fees(
    wallet: str | None = Query(default=None, min_length=4, max_length=128),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    data = store.list_position_fees(wallet=wallet, limit=limit)
    return {"data": data, "count": len(data), "fee_unit": "underlying token units; not USD"}


@app.get("/api/v1/alerts")
def alerts(limit: int = Query(default=100, ge=1, le=500)) -> dict:
    data = store.list_alerts(limit=limit)
    return {"data": data, "count": len(data)}


@app.get("/api/v1/pool-activity")
def pool_activity(
    pool_id: str | None = Query(default=None, min_length=3, max_length=256),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    data = store.list_pool_activity(pool_id=pool_id, limit=limit)
    return {"data": data, "count": len(data), "usd_values_are_estimates": True}


@app.get("/api/v1/wallet-monitor/{wallet}")
def wallet_monitor_runs(
    wallet: str,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    runs = store.list_wallet_monitor_runs(wallet, limit=limit)
    baselines = store.list_wallet_baselines(wallet)
    return {"wallet": wallet, "baselines": baselines, "runs": runs, "count": len(runs)}


@app.get("/api/v1/wallet-monitor/{wallet}/xlayer-positions")
def wallet_xlayer_positions(
    wallet: str,
    limit: int = Query(default=100, ge=1, le=500),
) -> dict:
    data = store.list_xlayer_positions(wallet, limit=limit)
    return {"wallet": wallet, "data": data, "count": len(data), "fee_unit": "raw underlying token units"}
