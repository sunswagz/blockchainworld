# LP Intelligence OS — Roadmap

## Phase 0 — Foundation
- [x] Inspect BlockchainWorld runtime, builder and Thị Bạc Ty.
- [x] Preserve existing lp_amm engine; keep LP Intelligence isolated.
- [x] DEX LP only; public-wallet read-only; no execution.
- [x] Data contracts, metrics, SQLite and read-only API.
- [ ] Review and merge foundation PR.

## Phase 1 — Data MVP
- [x] GeckoTerminal V2 public pool discovery.
- [x] Uniswap V3/Base WETH/USDC candidate discovery and factory verification.
- [x] Read pool state using JSON-RPC eth_call.
- [x] Archive raw provider payload and append pool snapshots.
- [x] Implement Uniswap V3 feeGrowthInside and accrued-fee math.
- [x] Enumerate Base Uniswap V3 NFT positions for a public wallet.
- [x] Pin position, pool, tick, fee-growth and token metadata reads to one block.
- [x] Reconcile NFT owner, NPM tuple, factory pool, token pair and fee tier.
- [x] Persist raw and human-readable fee amounts in underlying token units.
- [ ] Run live wallet collector with a public address and compare at least three positions with Uniswap UI.
- [ ] Cross-check token prices/TVL/volume with a second provider.
- [ ] Gate: no USD fee/APR until price provenance and historical snapshots are validated.

## Phase 2 — Fee Performance & Position Monitor
- [ ] Store time-series fee observations at 24h/7d/30d boundaries.
- [ ] Reconcile collected fees vs unclaimed fees and prevent double counting.
- [ ] Calculate USD fee values using block-aligned price observations.
- [ ] Fee APR windows 24h/7d/30d; incentive APR separate.
- [ ] Position principal, IL/PnL and gas using V3-specific math.
- [ ] Gate: reconcile at least three live positions against UI.

## Phase 3 — Risk & Alerts
- [ ] Range status, distance-to-edge, uptime, fee coverage.
- [ ] Token/contract, depeg, exploit, pause, bridge and congestion checks.
- [ ] Telegram outbound-only; dedupe, severity, retry and delivery audit.
- [ ] Gate: simulated alerts; no spam when nothing material changes.

## Phase 4 — AI Analyst & Dashboard
- [ ] OpenAI Responses API with read-only function tools.
- [ ] Evidence-first Vietnamese reports; confirmed/estimate/unknown explicit.
- [ ] Dashboard inside Thị Bạc Ty; backend not hosted on GitHub Pages.
- [ ] Chat history and decision journal.
- [ ] Gate: every AI claim traces to evidence IDs; no transaction tools.

## Phase 5 — Multi-protocol expansion
- [ ] Uniswap V2/V4, PancakeSwap V2/V3.
- [ ] Orca/Raydium on Solana with dedicated adapters.
- [ ] Other AMMs only after verifying LP support in OKX Wallet.
- [ ] Capital sizing for initial 500–1,000 USD.

## Phase 6 — Learning loop
- [ ] Record reasons for opening/holding/closing and realized outcomes.
- [ ] Evaluate forecast errors and historical replay without look-ahead.
- [ ] No automated execution; user remains the signer.

## Target cadence
- Pool metrics: 15–60 minutes subject to provider limits.
- Position state: hourly; faster only when justified.
- Dashboard: latest snapshot with visible data age.
- AI: important alerts or explicit request only.
