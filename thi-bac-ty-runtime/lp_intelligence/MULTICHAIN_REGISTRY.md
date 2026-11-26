# Multi-chain DEX Registry Foundation

This registry is a control plane for LP discovery, not a claim that every listed
network or DEX can already be scanned. The chain catalogue is a versioned
snapshot of OKX's published Supported Networks documentation. Refresh it from
the official source during maintenance; wallet support, API support and DEX
data support are separate capabilities.

## Status semantics

- `registry_only`: chain is listed, but no LP scanner is enabled.
- `adapter_available`: a project adapter exists; it still requires live RPC
  and independent wallet/UI reconciliation before production acceptance.
- DEX `discovery_required`: protocol family is known, deployment addresses
  and ABI have not been verified for that chain.
- DEX `partial`: some discovery exists, but position/accounting coverage is
  incomplete.

## Current truthful coverage

- Base: existing Uniswap V3 pool, NFT position, fee/performance and accounting
  collectors.
- X Layer: existing Uniswap V3 pool and position discovery; realized fee/PnL
  parity with Base is incomplete.
- EVM V2, other EVM V3, stable-swap, Solana AMM/CLMM and Sui AMM/CLMM are
  registered as protocol families only. No contract address is inferred.
- Bitcoin, TON and TRON appear in the chain catalogue but are not EVM chains;
  the EVM JSON-RPC collectors must never be pointed at them.

## Adapter contract

Every protocol adapter must expose pool discovery and wallet-position
discovery. It is read-only by design. There is no signing, approval, swap,
liquidity add/remove, transaction construction or broadcasting method.

Normalized records must preserve:
- chain key and protocol key;
- source/provider and source URL or RPC block provenance;
- block number/hash/timestamp where available;
- raw token amounts and decimals;
- explicit nulls and coverage status for unavailable metrics.

## Run offline validation

```bash
cd thi-bac-ty-runtime
python scripts/kiem-multichain-registry.py
```

This stage does not claim complete DEX enumeration. Full coverage requires
verified protocol deployment registries, provider/indexer discovery, chain-
specific adapters, historical event backfill and live reconciliation.
