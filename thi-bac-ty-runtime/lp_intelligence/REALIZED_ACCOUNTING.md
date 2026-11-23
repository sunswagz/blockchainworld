# Realized Accounting Module

This module records the Base Uniswap V3 NonfungiblePositionManager lifecycle.

- Event source: verified PositionManager logs for Transfer, IncreaseLiquidity, DecreaseLiquidity and Collect.
- Ownership: event stream is filtered to wallet ownership intervals; the scan must include the first incoming NFT transfer.
- Fee attribution: principal-first against DecreaseLiquidity receivables; Collect excess is classified as realized fees.
- Gas: wallet-signed transaction receipts, gasUsed × effectiveGasPrice + Base l1Fee, with equal allocation across distinct positions touched in one transaction.
- USD: only event-time price observations within the configured timestamp tolerance are accepted.
- Net PnL: only emitted when acquisition/capital basis, historical prices, current valuation and complete gas data are verified.

The module is read-only. It does not sign, approve, simulate, submit or execute transactions. See the runtime README for the runner command and limitations.
