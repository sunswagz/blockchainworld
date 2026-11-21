# LP Intelligence runtime

Read-only DEX LP monitoring and analysis package for BlockchainWorld / Thị Bạc Ty.

## Scope
- DEX liquidity pools only.
- Public wallet address monitoring only.
- No wallet connection, signing, approvals, transaction construction or execution.
- No lending/borrowing modules.
- SQLite storage and FastAPI read-only API.

## Uniswap V3/Base pool collector
GeckoTerminal discovers candidate WETH/USDC pools. The official Uniswap V3 Factory verifies pool address and fee tier. JSON-RPC eth_call reads pool state and raw provider payloads are archived with SHA-256 provenance.

## Uniswap V3/Base NFT position collector
The collector discovers candidate NFT IDs through ERC-721 Transfer logs (incoming and outgoing) from the Uniswap V3 NonfungiblePositionManager, then confirms current ownership with ownerOf. The standard Position Manager is not assumed to expose ERC721Enumerable methods.

Official Base contracts:
- Uniswap V3 Factory: `0x33128a8fC17869897dcE68Ed026d694621f6FDfD`
- NonfungiblePositionManager: `0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1`

Run from thi-bac-ty-runtime:

    python -m pip install -r requirements.txt
    export BASE_RPC_URL=https://mainnet.base.org
    export LP_INTELLIGENCE_DB=./data/lp-intelligence.sqlite
    python scripts/thu-thap-uniswap-v3-positions-base.py --wallet 0xYOUR_PUBLIC_ADDRESS --from-block 1000000

Set `--from-block` to a block no later than the earliest time the wallet could have received one of its current position NFTs. If this is set too late, older still-owned NFTs may be missed. The collector scans logs in chunks (default 2,000 blocks); adjust `--log-chunk-size` only if your RPC provider supports larger ranges.

The collector:
1. Captures latest block number/hash/timestamp.
2. Scans incoming and outgoing ERC-721 Transfer logs from the supplied start block through the captured block.
3. Confirms each candidate token's current owner with ownerOf at the captured block.
4. Reads the position tuple and resolves its pool through the official factory.
5. Verifies pool token0/token1/fee against the NFT tuple.
6. Reads slot0, feeGrowthGlobal, boundary tick states and ERC20 decimals/symbols at the same block tag.
7. Calculates unclaimed token amounts with feeGrowthInside Q128 math plus stored tokensOwed.
8. Archives evidence and appends position and fee snapshots with block number/hash.

Fee amounts are denominated in underlying tokens, not USD. USD valuation and APR remain null until independently sourced prices and time-window snapshots are reconciled.

## Reconciliation limits
This stage reconciles event-derived token candidates, current NFT ownership, NFT tuple, factory mapping, pool identity, fee tier and same-block fee-growth inputs. It does not call collect(0), simulate a transaction, or submit anything. The fee result follows Uniswap V3's published fee-growth method; an independent UI comparison against at least three real positions remains a manual acceptance gate.

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
