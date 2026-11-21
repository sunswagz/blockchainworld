# LP Intelligence runtime

Read-only DEX LP monitoring and analysis package for BlockchainWorld / Thị Bạc Ty.

## Scope
- DEX liquidity pools only.
- Public wallet address monitoring only.
- No wallet connection, signing, approvals, transaction construction or execution.
- No lending/borrowing modules.
- SQLite storage and FastAPI read-only API.

## Uniswap V3/Base pool collector
- GeckoTerminal discovers candidate WETH/USDC pools.
- Official Uniswap V3 Factory confirms pool address and fee tier.
- JSON-RPC eth_call reads token0/token1, slot0 and liquidity.
- Provider payloads are archived with SHA-256 provenance.

## Uniswap V3/Base NFT position collector
The collector enumerates the current NFT positions held by a public wallet through the Base NonfungiblePositionManager. It does not connect to the wallet or request a signature.

Official Base contracts:
- Uniswap V3 Factory: `0x33128a8fC17869897dcE68Ed026d694621f6FDfD`
- NonfungiblePositionManager: `0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1`

Run from thi-bac-ty-runtime:

    python -m pip install -r requirements.txt
    export BASE_RPC_URL=https://mainnet.base.org
    export LP_INTELLIGENCE_DB=./data/lp-intelligence.sqlite
    python scripts/thu-thap-uniswap-v3-positions-base.py --wallet 0xYOUR_PUBLIC_ADDRESS

The collector:
1. Reads the current block number and pins all subsequent eth_call reads to that block.
2. Enumerates the wallet's NFTs using balanceOf and tokenOfOwnerByIndex.
3. Cross-checks each token with ownerOf and reads its position tuple.
4. Resolves the pool through the official factory and checks token0/token1/fee against the pool.
5. Reads slot0, feeGrowthGlobal, both boundary tick states and token decimals/symbols at the same block.
6. Calculates unclaimed token amounts using feeGrowthInside Q128 math plus stored tokensOwed.
7. Archives the evidence and appends position and fee snapshots with block number/hash.

Fee results are denominated in the two underlying tokens, not USD. USD valuation and APR remain null until independently sourced prices and time-window snapshots are reconciled.

## Reconciliation limits
This stage reconciles wallet ownership, NFT tuple, factory mapping, pool identity, fee tier and same-block fee-growth inputs. It does not execute collect(0), simulate a transaction, or submit anything. The computed unclaimed amount follows Uniswap V3's published fee-growth method; an independent UI comparison against at least three real positions remains a manual acceptance gate.

## Uniswap V3 fee accounting primitives
`fee_accounting.py` implements integer-only feeGrowthInside and accrued-fee math, with uint256 wraparound. `position_fee_snapshots` stores raw/human token units, decimals, block hash and provenance.

## Self-tests

    python scripts/kiem-lp-intelligence.py
    python scripts/kiem-lp-collector-fixtures.py
    python scripts/kiem-lp-fee-accounting.py
    python scripts/kiem-lp-position-collector-fixtures.py

## API
- GET /health
- GET /api/v1/pools?limit=100
- GET /api/v1/positions?wallet=0x...
- GET /api/v1/alerts?limit=100

All endpoints are read-only. Missing values remain null. No transaction method exists.
