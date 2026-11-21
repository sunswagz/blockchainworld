# LP Intelligence runtime

Read-only DEX LP monitoring and analysis package for BlockchainWorld / Thị Bạc Ty.

## Scope
- DEX liquidity pools only.
- Public wallet address monitoring only.
- No wallet connection, signing, approvals, transaction construction or execution.
- No lending/borrowing modules.
- SQLite storage and FastAPI read-only API.

## Foundation
- contracts.py: canonical data contracts and provenance validation.
- metrics.py: pure math helpers; V2 IL is not used as a substitute for V3/V4 range math.
- storage.py / schema.sql: append-only snapshots, provider payload archive, positions and alerts.
- api.py: read-only GET endpoints.
- providers/geckoterminal.py: GeckoTerminal V2 public pool discovery.
- evm.py: minimal JSON-RPC eth_call helpers; no signing methods.
- collectors/uniswap_v3_base.py: WETH/USDC candidate discovery and Uniswap V3 factory/pool verification.

## Run locally

From thi-bac-ty-runtime:

    python -m pip install -r requirements.txt
    LP_INTELLIGENCE_DB=./data/lp-intelligence.sqlite uvicorn lp_intelligence.api:app --host 127.0.0.1 --port 8787

## Collect one live snapshot

Set a Base RPC URL (the public Base RPC is the default; a dedicated provider is recommended for stable production use):

    export BASE_RPC_URL=https://mainnet.base.org
    export LP_INTELLIGENCE_DB=./data/lp-intelligence.sqlite
    python scripts/thu-thap-uniswap-v3-base.py

The collector:
1. Discovers WETH pools on GeckoTerminal.
2. Filters to the canonical Base WETH/USDC token pair.
3. Verifies each candidate against the official Uniswap V3 factory and fee tiers.
4. Reads token0/token1, slot0 and liquidity using eth_call.
5. Archives the provider payload and appends a pool snapshot.

GeckoTerminal's public API is rate-limited; do not run this command more frequently than the provider permits. Schedule it at 15–60 minute intervals after observing provider limits and successful runs.

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
- Fee income and APR remain null until validated fee accounting is available; no nominal estimate is mislabeled as realized fee income.
