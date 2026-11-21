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
- metrics.py: pure math helpers; V2 IL is not a substitute for V3/V4 range math.
- fee_accounting.py: integer-only Uniswap V3 feeGrowthInside and position fee accrual math.
- storage.py / schema.sql: append-only snapshots, provider payload archive, positions and alerts.
- api.py: read-only GET endpoints.
- providers/geckoterminal.py: GeckoTerminal V2 public pool discovery.
- evm.py: minimal JSON-RPC eth_call helpers; no signing methods.
- collectors/uniswap_v3_base.py: WETH/USDC discovery and official factory/pool verification.

## Run locally
From thi-bac-ty-runtime:
    python -m pip install -r requirements.txt
    LP_INTELLIGENCE_DB=./data/lp-intelligence.sqlite uvicorn lp_intelligence.api:app --host 127.0.0.1 --port 8787

## Collect one live snapshot
    export BASE_RPC_URL=https://mainnet.base.org
    export LP_INTELLIGENCE_DB=./data/lp-intelligence.sqlite
    python scripts/thu-thap-uniswap-v3-base.py

The collector discovers WETH pools through GeckoTerminal, filters canonical Base WETH/USDC, verifies the candidate with the official Uniswap V3 factory, reads token0/token1/slot0/liquidity via eth_call, then archives provider payload and appends a pool snapshot.

## Uniswap V3 fee accounting primitives
fee_accounting.py implements integer-only protocol math:
- Decode pool.ticks(int24) feeGrowthOutside values.
- Decode NonfungiblePositionManager.positions(tokenId) checkpoints and tokensOwed.
- Compute feeGrowthInside from lower/upper tick state and current tick.
- Compute unclaimed token amounts using Q128 fixed-point arithmetic and uint256 wraparound.

These are deterministic offline-tested primitives, not yet a live position collector. Integration must fetch feeGrowthGlobal0X128/1X128, both boundary tick states, the NFT position tuple, token decimals and a consistent block tag, then reconcile results against the official Uniswap position view. Do not convert raw token amounts to USD or publish APR until price/decimal provenance and time-window accounting are available.

## Self-tests
    python scripts/kiem-lp-intelligence.py
    python scripts/kiem-lp-collector-fixtures.py
    python scripts/kiem-lp-fee-accounting.py

## API
- GET /health
- GET /api/v1/pools?limit=100
- GET /api/v1/positions?wallet=0x...
- GET /api/v1/alerts?limit=100

All endpoints are read-only. Missing values remain null, and all observations retain provenance. Fee income and APR remain null until validated fee accounting is available.
