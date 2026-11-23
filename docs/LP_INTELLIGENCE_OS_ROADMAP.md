# LP Intelligence OS — Roadmap

## Phase 0 — Foundation
- [x] Inspect BlockchainWorld runtime, builder and Thị Bạc Ty.
- [x] Preserve existing lp_amm engine; keep LP Intelligence isolated.
- [x] DEX LP only; public-wallet read-only; no execution.
- [x] Data contracts, metrics, SQLite and read-only API.
- [ ] Review and merge foundation PR.

## Phase 1 — Data MVP
- [x] GeckoTerminal V2 pool discovery and official factory verification.
- [x] Read pool state and archive raw provider payloads.
- [x] Implement Uniswap V3 feeGrowthInside and accrued-fee math.
- [x] Discover Base V3 NFT candidates from incoming/outgoing Transfer logs.
- [x] Verify current ownerOf and reconcile NPM tuple with factory pool identity.
- [x] Pin position, pool, tick, fee-growth and token metadata reads to one block.
- [x] Persist raw/human fee amounts in underlying token units with block hash.
- [ ] Run live collector for the configured public wallet and compare any detected positions with Uniswap UI.
- [ ] Cross-check prices/TVL/volume with a second provider.
- [ ] Gate: no USD fee/APR until price provenance and historical snapshots are validated.

## Phase 2 — Fee Performance & Position Monitor
- [x] Unified Base + X Layer wallet monitor orchestration.
- [x] Per-chain block baselines persisted without resetting on subsequent runs.
- [x] Persist X Layer NFT position snapshots and monitor-run history.
- [x] Read-only wallet monitor API endpoints.
- [ ] Execute live scan for configured public wallet; compare RPC results with explorer/UI.
- [x] Store append-only position fee and performance snapshots; window comparisons become available as history accrues.
- [x] Add Base V3 Collect/DecreaseLiquidity event ledger with principal-first attribution to prevent principal payouts being mislabeled as fees.\n- [ ] Reconcile historical fee claims against unclaimed balances with block-level state replay.
- [x] Calculate provisional USD fee values from timestamped provider price observations (not block-aligned oracle prices).
- [x] Provisional 24h/7d/30d APR from unclaimed-fee balance deltas; null when history is insufficient or balance falls. Incentives remain separate.
- [x] V3 principal, IL vs first-observed HODL baseline and provisional PnL before claimed fees/costs.\n- [x] Store Base V3 lifecycle events and wallet-paid transaction receipts; include L2 gas plus receipt L1 fee when supplied.\n- [x] Calculate conditional net PnL when mint-to-wallet basis, event-time token prices, current valuation and complete gas data exist.\n- [ ] Attribute external swaps/rebalances and all gas costs; reconcile net PnL for transferred-in positions.
- [ ] Gate: reconcile live positions against UI; no live wallet scan has been run from CI.

## Phase 3 — Risk & Alerts
- [ ] Range status, distance-to-edge, uptime, fee coverage.
- [ ] Token/contract, depeg, exploit, pause, bridge and congestion checks.
- [ ] Telegram outbound-only; dedupe, severity, retry and delivery audit.

## Phase 4 — AI Analyst & Dashboard
- [ ] OpenAI Responses API with read-only function tools.
- [ ] Evidence-first Vietnamese reports; confirmed/estimate/unknown explicit.
- [ ] Dashboard inside Thị Bạc Ty; backend not hosted on GitHub Pages.
- [ ] Chat history and decision journal.

## Phase 5 — Multi-protocol expansion
- [ ] Uniswap V2/V4, PancakeSwap V2/V3.
- [ ] Orca/Raydium on Solana with dedicated adapters.
- [ ] Other AMMs only after verifying LP support in OKX Wallet.
- [ ] Capital sizing for initial 500–1,000 USD.

## Phase 6 — Learning loop
- [ ] Record reasons for opening/holding/closing and realized outcomes.
- [ ] Evaluate forecast errors and historical replay without look-ahead.
- [ ] No automated execution; user remains the signer.


### Phase 2 implementation note

The initial Fee Performance Engine is implemented for Base Uniswap V3 NFTs. It stores sourced price observations, calculates current principal and unclaimed-fee USD values, compares LP principal against a first-monitored HODL baseline, and exposes performance history. APR is provisional and requires accumulated observations. Claimed fees, gas and rebalance costs remain unknown rather than being imputed. GeckoTerminal current prices are not block-aligned oracle prices; this is not yet a fully realized net-return ledger.


### Realized Fee & Cost Accounting implementation note

Base Uniswap V3 lifecycle logs are persisted idempotently by chain/transaction/log index. Ownership Transfer logs delimit the wallet's ownership periods. Collect amounts are attributed principal-first against DecreaseLiquidity amounts; this avoids treating the whole Collect payout as fees, but remains an explicit accounting convention rather than an on-chain fee/principal split. Wallet-signed transaction receipts record gasUsed × effectiveGasPrice plus Base l1Fee when available. Multi-position transaction gas is split equally among distinct positions touched.

Net PnL is intentionally null unless the NFT was minted directly to the wallet, the scan covers the initial transfer, historical prices are available near every event, current valuation is fresh relative to the latest fee snapshot, and the receipt includes the L1 fee component. External swaps/rebalances and transfer-acquisition cost remain outside the ledger. The implementation is Base V3 only; it is not yet a complete cross-chain audited cost basis.
