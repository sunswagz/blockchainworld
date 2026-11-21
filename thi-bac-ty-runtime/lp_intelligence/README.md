# LP Intelligence runtime

Read-only DEX LP monitoring and analysis package for BlockchainWorld / Thị Bạc Ty.

## Scope
- DEX liquidity pools only.
- Public wallet address monitoring only.
- No wallet connection, signing, approvals, transaction construction or execution.
- No lending/borrowing modules.
- SQLite storage and FastAPI read-only API.

## Foundation files
- contracts.py: canonical data contracts and validation.
- metrics.py: pure math helpers; V2 IL is not used as a substitute for V3/V4 range math.
- storage.py: append-only SQLite snapshots, positions and alerts.
- api.py: read-only GET endpoints.
- schema.sql: database schema.

## Run locally

From thi-bac-ty-runtime:

    python -m pip install -r requirements.txt
    LP_INTELLIGENCE_DB=./data/lp-intelligence.sqlite uvicorn lp_intelligence.api:app --host 127.0.0.1 --port 8787

OpenAPI docs are available at /docs on the local service.

## Self-test

    python scripts/kiem-lp-intelligence.py

The self-test uses temporary SQLite storage and deterministic fixtures. It does not call external APIs or sign transactions.

## API
- GET /health
- GET /api/v1/pools?limit=100
- GET /api/v1/positions?wallet=0x...
- GET /api/v1/alerts?limit=100

All endpoints are read-only. No endpoint can send a transaction.

## Data semantics
- Timestamps are ISO-8601 UTC.
- Missing values remain null; never coerce unknown to zero.
- Every observation records source, observed_at, fetched_at and data_status.
- Provider estimates and on-chain confirmed values remain distinguishable.
