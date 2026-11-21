# LP Intelligence OS — Roadmap

## Phase 0 — Foundation
- [x] Kiểm tra BlockchainWorld main, runtime Python, builder và cung Thị Bạc Ty.
- [x] Kiểm tra engine lp_amm hiện hữu và nhánh LP V3 cũ.
- [x] Chốt DEX LP only, public wallet read-only, không execution.
- [x] Tạo data contracts, metrics, SQLite schema/repository và read-only API.
- [ ] Review và merge foundation PR.

## Phase 1 — Data MVP
- [x] GeckoTerminal V2 public pool discovery adapter.
- [x] Uniswap V3/Base WETH/USDC candidate discovery.
- [x] Verify pool address and fee tier against official Uniswap V3 factory.
- [x] Read token0/token1, slot0, current tick and liquidity via JSON-RPC eth_call.
- [x] Archive provider payload with SHA-256 provenance and append pool snapshots.
- [x] Add one-shot collector CLI and offline fixtures.
- [ ] Run live collector with a configured Base RPC and review first verified snapshot.
- [ ] Cross-check TVL/volume and token prices with a second provider.
- [x] Implement Uniswap V3 feeGrowthInside and position accrued-fee math primitives.
- [ ] Integrate fee accounting with consistent-block RPC reads and NFT position discovery.
- [ ] Gate: do not rank stale data, missing provenance or unverified contracts.

## Phase 2 — Wallet Position Monitor
- [ ] Enter public EVM address; no connect/sign.
- [ ] Discover Uniswap V3 NFT positions; read pool, tickLower/tickUpper, liquidity, tokens owed.
- [ ] Reconcile position with pool state and block timestamp.
- [ ] Append position snapshots.
- [ ] Gate: reconcile at least three fixtures against OKX/Uniswap UI.

## Phase 3 — Risk & Alerts
- [ ] Fee APR windows 24h/7d/30d, incentives separate.
- [ ] Range status, distance-to-edge, uptime, fee coverage, IL/PnL with version-correct math.
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
- [ ] Orca/Raydium on Solana with a dedicated adapter.
- [ ] QuickSwap, SushiSwap, Momentum and other AMMs after verifying actual LP support in OKX Wallet.
- [ ] Portfolio-level exposure and capital sizing for 500–1,000 USD.

## Phase 6 — Learning loop
- [ ] Record reasons for opening/holding/closing and realized outcomes.
- [ ] Evaluate range/fee forecast errors.
- [ ] Historical replay/backtest without look-ahead.
- [ ] No automated execution; user remains the signer.

## Target cadence
- Pool metrics: 15–60 minutes subject to provider limits.
- Position state: hourly; faster only when justified by market volatility.
- Risk events: event-driven/polling where supported.
- AI: only on important alerts or explicit user request.
- Dashboard: latest snapshot with visible data age.

Initial capital of 500–1,000 USD is a sizing constraint. Include entry/exit gas, slippage and rebalance costs; avoid fragmenting capital across tiny positions.
