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

## X Layer wallet bootstrap (read-only)

X Layer mainnet uses chain ID `196`, native gas token OKB, and the official public RPC `https://rpc.xlayer.tech`. The OKX Wallet display address `XKO...` is normalized to the corresponding EVM `0x...` address by the bootstrap script.

Official Uniswap v3 X Layer deployments (verify against the official deployment page before upgrades):
- Factory: `0x4B2ab38DBF28D31D467aA8993f6c2585981D6804`
- NonfungiblePositionManager: `0x315e413A11AB0df498eF83873012430ca36638Ae`
- WOKB: `0xe538905cf8410324e03A5A23C1c177a474D59b2b`

Run from `thi-bac-ty-runtime`:

    python scripts/khoi-tao-vi-xlayer.py --wallet XKO51f9d30f78239e53f14c1e248fd29e6966ce5287

Or save a baseline JSON snapshot:

    python scripts/khoi-tao-vi-xlayer.py --wallet 0x51f9d30f78239e53f14c1e248fd29e6966ce5287 --output ./data/xlayer-wallet-baseline.json

The script verifies chain ID, captures block number, native OKB balance and transaction count, and checks that the official Uniswap v3 Factory and Position Manager addresses contain contract code at the same block. It does not enumerate ERC-20 token balances or LP positions yet; those are separate collectors. A zero transaction count is not proof of inactivity on other networks.

No signing, approvals, transaction construction or transaction submission is performed.

## X Layer ERC-20 balance scanner (read-only)

The EVM JSON-RPC standard does not provide a method to enumerate every ERC-20 held by an address. Therefore this scanner queries only explicitly supplied token contracts; by default it checks WOKB. Do not interpret the result as a complete wallet token inventory.

    python scripts/quet-token-xlayer.py --wallet XKOYOUR40HEXADDRESS
    python scripts/quet-token-xlayer.py --wallet 0xYOUR40HEXADDRESS --token 0xTOKENCONTRACT --token 0xANOTHERTOKEN --output ./data/xlayer-token-balances.json

The scanner checks chain ID 196 and reads balanceOf, decimals and symbol at a single block tag. A provider/indexer with an authenticated wallet portfolio endpoint can be added later as a separate, provenance-labelled discovery adapter; RPC remains the verification source.

## X Layer Uniswap V3 pool discovery

    python scripts/kham-pha-pool-uniswap-v3-xlayer.py --output ./data/xlayer-uniswap-v3-pools.json

This discovers pools returned by GeckoTerminal for WOKB, then independently verifies each candidate against the official Uniswap V3 X Layer Factory and reads token0/token1, fee tier, current tick and liquidity at one block. Results are ranked by provider TVL then 24h volume; this is a sorting aid, not an investment score. It is not a complete census of all X Layer pools and does not infer APR from volume.

## Offline scanner fixtures

    python scripts/kiem-xlayer-scanners.py

The fixtures cover XKO/0x normalization, ABI address/symbol decoding and invalid-address rejection. Live RPC and UI reconciliation remain separate acceptance gates.

## X Layer Uniswap V3 position NFT scanner

For a newly created wallet with no LP history, take the baseline block from the wallet bootstrap output and use that as `--from-block` for subsequent scans:

    python scripts/khoi-tao-vi-xlayer.py --wallet XKOYOUR40HEXADDRESS --output ./data/xlayer-wallet-baseline.json
    # Read block.number from the baseline JSON, then:
    python scripts/quet-vi-the-uniswap-v3-xlayer.py --wallet XKOYOUR40HEXADDRESS --from-block BASELINE_BLOCK --output ./data/xlayer-uniswap-v3-positions.json

The scanner replays incoming/outgoing ERC-721 Transfer logs from the X Layer Uniswap V3 Position Manager, confirms current ownership with `ownerOf`, decodes the position tuple, verifies the pool through the official Factory, and reads current tick at one block. It reports range status and raw tokensOwed.

It does not yet calculate feeGrowthInside or USD PnL. Direct wallet ownership only is covered; staked/custodied NFTs need a separate adapter. A late `--from-block` may miss older positions. No transaction methods are called.


## Base Uniswap V3 rolling 24h swap activity

The Base collector now pins pool identity, token metadata, slot0 and liquidity reads to one snapshot block. It also finds the block near the rolling 24-hour boundary and scans the pool's Uniswap V3 `Swap` event logs in bounded chunks.

- Pool identity and fee tier: verified against the official Uniswap V3 Factory.
- Spot price, tick, liquidity and token decimals: read from Base RPC at the snapshot block.
- Provider TVL and 24h volume: retained as provider-sourced values.
- On-chain Swap activity: raw input-side token amounts, swap count, estimated volume and estimated fee amount.
- History: appended to `pool_activity_snapshots`, including block number/hash, block timestamp, scanned block range and source payload reference.
- API: `GET /api/v1/pool-activity?limit=100`.

Important accounting distinction: the on-chain Swap-derived USD volume/fees are estimates using the event input deltas, pool fee tier, on-chain token decimals and GeckoTerminal token USD prices. They are kept in a separate activity table and are not written into the canonical `fees_24h_usd` pool metric. They are not yet a block-by-block oracle valuation or the LP's realized fee earnings. Fee APR remains null until the position-level accounting and capital denominator are reconciled.

Run offline checks:

    python scripts/kiem-lp-collector-fixtures.py
    python scripts/kiem-lp-swap-activity.py


## Unified multi-chain Wallet & Position Monitor

The unified monitor coordinates the Base and X Layer NFT scanners for one public EVM wallet and stores per-chain scan baselines plus monitor-run history.

First run for a newly created/unused wallet:

    python scripts/theo-doi-vi-lp.py --wallet XKO51f9d30f78239e53f14c1e248fd29e6966ce5287

Or use the normalized EVM address:

    python scripts/theo-doi-vi-lp.py --wallet 0x51f9d30f78239e53f14c1e248fd29e6966ce5287

The monitor verifies chain IDs 196 and 8453, records the latest block/hash/timestamp as a per-chain baseline if none exists, then scans NFT Transfer logs from that baseline onward. On later runs it reuses the original baseline so positions that were created after onboarding can still be rediscovered. Existing baselines are never silently reset.

Optional chain selection:

    python scripts/theo-doi-vi-lp.py --wallet XKO... --chains xlayer
    python scripts/theo-doi-vi-lp.py --wallet 0x... --chains base

The X Layer scanner persists latest position snapshots in `xlayer_position_snapshots`; the Base collector persists position and fee snapshots in the existing position tables. Every monitor invocation is archived in `wallet_monitor_runs`. Baselines are stored in `wallet_chain_baselines`.

Read-only APIs:
- `GET /api/v1/wallet-monitor/{wallet}` — per-chain baselines and monitor-run history.
- `GET /api/v1/wallet-monitor/{wallet}/xlayer-positions` — latest X Layer NFT position snapshots.
- `GET /api/v1/positions?wallet=0x...` — latest Base position snapshots.
- `GET /api/v1/position-fees?wallet=0x...` — latest Base unclaimed-fee snapshots.

Important: the first baseline is appropriate only because this wallet was stated to be newly created and unused. It does not backfill historical NFT transfers before the baseline. If monitoring a previously used wallet, seed an earlier baseline/scan start block before relying on the inventory. ERC-20 enumeration, staked/custodied NFT discovery, X Layer feeGrowthInside math and USD valuation remain separate follow-up work.

The monitor uses public RPC reads only. It never requests a wallet connection, seed phrase, private key, signature, approval, or transaction.


## Fee Performance Engine — Uniswap V3/Base

The performance engine values the current principal held by each Base V3 NFT using its liquidity, tick bounds and the pool's `sqrtPriceX96`. It separately values unclaimed fees from the existing Q128 fee-growth collector. It does not apply the V2 impermanent-loss formula to concentrated-liquidity positions.

### Record token USD prices

Create a JSON file containing fresh, sourced price observations for both tokens in every position:

    [
      {
        "chain_id": "8453",
        "token_address": "0xTOKEN_ADDRESS",
        "price_usd": 2000.0,
        "observed_at": "2026-11-22T12:00:00Z",
        "source": "your-price-provider",
        "source_url": "https://provider.example/price"
      }
    ]

Each token requires its own record. The source and timestamp are retained; prices older than 60 minutes are rejected by default. Do not use a stablecoin peg as a substitute for a price observation unless it is explicitly sourced and recorded.

### Run valuation

First run the wallet monitor so the latest Base NFT fee snapshots and raw payloads include `sqrtPriceX96`. Then:

    python scripts/tinh-hieu-suat-lp.py \
      --wallet 0xYOUR_PUBLIC_WALLET \
      --prices-json ./prices.json

The first saved performance snapshot establishes the HODL comparison baseline. This is the first monitored valuation, not the NFT mint/deposit date. Later snapshots compare the current LP principal and fee balance against holding those initial token amounts.

### Metrics and limitations

- Principal USD: V3 token amounts derived from liquidity, current sqrt price and tick bounds.
- Unclaimed fees USD: feeGrowthInside Q128 + stored tokensOwed, valued using the same token price observations.
- IL vs HODL: current LP principal minus mark-to-market value of the baseline token amounts.
- Fee-adjusted vs HODL: current principal + current unclaimed fees - HODL benchmark.
- PnL: current principal + unclaimed fees - initial monitored capital.
- 24h/7d/30d fee APR: provisional annualization of the change in unclaimed fee balance against average principal, only when a suitable prior snapshot exists and the fee balance did not fall. It is null if data is insufficient or a fee collection/reset may have occurred.

Claimed fees, gas and rebalance costs are intentionally null/not included until dedicated Collect-event and transaction-cost ledgers are implemented. Consequently PnL is explicitly before claimed fees, gas and rebalance costs. No historical performance is backfilled before the first valuation snapshot.

Read-only history API:

    GET /api/v1/position-performance?wallet=0x...

The engine rejects missing/stale price observations; it never silently converts missing prices to zero. Output status is `provisional` until claimed-fee and cost accounting are available.


Performance engine validation note: CI includes V3 amount math, range-boundary cases, fee valuation, HODL comparison and token-price provenance fixtures. Run the collector again after upgrading so its raw payload contains sqrtPriceX96, then provide fresh price observations before running the performance script.


Current-price convenience option: the runner can query GeckoTerminal V2 for each position token and archive the returned USD price with its provider URL and fetch timestamp:

    python scripts/tinh-hieu-suat-lp.py \
      --wallet 0xYOUR_PUBLIC_WALLET \
      --fetch-gecko-prices

Use `--prices-json` instead when you have a preferred price source; explicit JSON observations are recorded with their provenance. GeckoTerminal-derived valuations are marked provisional and are not historical block-aligned oracle prices.


## Realized Fee & Cost Accounting — Base Uniswap V3

The lifecycle ledger reads the official NonfungiblePositionManager events `Transfer`, `IncreaseLiquidity`, `DecreaseLiquidity` and `Collect`, then reads transaction receipts for wallet-paid gas. The event definitions follow the [official Uniswap V3 NonfungiblePositionManager interface](https://github.com/Uniswap/v3-periphery/blob/main/contracts/interfaces/INonfungiblePositionManager.sol).

### Run order

1. Run the Base NFT position collector so the database has the wallet's current NFT positions and token metadata.
2. Prepare timestamped historical price observations for token0/token1 and Base WETH. Pass them using `--prices-json`; each event must have a price observation within the configured event-time tolerance (default 5 minutes). Price points must be genuinely observed near the event time, not today’s price relabeled with a historical timestamp.
3. Run the read-only lifecycle scanner:

       python scripts/doi-soat-lp-realized-costs.py \
         --wallet 0xYOUR_PUBLIC_WALLET \
         --from-block FIRST_WALLET_NFT_TRANSFER_BLOCK \
         --prices-json ./historical-prices.json

The scan range must include the first transfer of each NFT into the wallet. If no incoming transfer is found, the scanner refuses to infer ownership. The script only reads logs, transactions, receipts and blocks; it never signs or sends transactions.

### Attribution rules

- `IncreaseLiquidity`: records token amounts contributed while the wallet owns the NFT.
- `DecreaseLiquidity`: records principal amounts receivable after liquidity removal.
- `Collect`: records amounts paid out. Because the event does not label each unit as principal or fee, the ledger uses a documented conservative **principal-first** rule: outstanding DecreaseLiquidity amounts are attributed to recovered principal first; any excess Collect amount is classified as realized fees.
- `Transfer`: delimits periods when the wallet owns the NFT. Events before acquisition and after transfer-out are not counted as wallet cashflows.
- Gas: receipt `gasUsed × effectiveGasPrice + l1Fee` where Base supplies `l1Fee`. The transaction's cost is split evenly across distinct wallet-held positions touched by that transaction. Missing L1 fee or historical ETH/WETH price prevents a complete USD net PnL.

### Net PnL and limitations

The formula is:

    current position value
    + principal recovered
    + realized fees
    - liquidity contributions
    - attributed gas costs

Net PnL is populated only when the NFT was minted directly to the wallet, every IncreaseLiquidity contribution transaction was sent by that wallet, the current position valuation is at least as recent as the latest fee snapshot, and event-time prices exist for every cashflow and gas transaction. If the NFT was acquired by transfer, acquisition cost is unknown and net PnL remains null. The first transfer must be included in the scan range.

External swap transactions and rebalancing outside the PositionManager event lifecycle are not yet attributed. Gas allocation across multiple positions in one transaction is an equal split and is labeled as such. This is a conservative accounting estimate, not an audited tax ledger.

Read-only endpoint:

    GET /api/v1/position-accounting?wallet=0x...

The endpoint returns raw token cashflows, gas and net PnL status. Missing historical prices, incomplete ownership history, missing Base L1 fee or unknown acquisition basis remain explicit rather than being replaced with zero.
