# LP Intelligence OS — Roadmap

## Phase 0 — Foundation
- [x] Kiểm tra BlockchainWorld main, runtime Python, builder và cung Thị Bạc Ty.
- [x] Kiểm tra engine lp_amm hiện hữu và nhánh LP V3 cũ.
- [x] Chốt DEX LP only, public wallet read-only, không execution.
- [x] Tạo data contracts, metrics, SQLite schema/repository và read-only API.
- [ ] Review và merge foundation PR.

## Phase 1 — Data MVP
- [ ] Adapter market registry từ OKX Onchain OS.
- [ ] Adapter pool discovery/metrics cho Uniswap V3 trên Base.
- [ ] Xác minh ETH/USDC bằng chain ID, factory, pool address, token addresses và fee tier.
- [ ] Thu thập price/tick/liquidity/volume/fees; lưu raw payload và provenance.
- [ ] Cross-check GeckoTerminal/DefiLlama; ghi nhận provider disagreement.
- [ ] Gate: không xếp hạng dữ liệu stale, thiếu provenance hoặc contract chưa xác minh.

## Phase 2 — Wallet Position Monitor
- [ ] Nhập public EVM address; không connect/sign.
- [ ] Tìm Uniswap V3 NFT positions; đọc pool, tickLower/tickUpper, liquidity, tokens owed.
- [ ] Đối chiếu với pool state và block timestamp.
- [ ] Lưu position snapshots append-only.
- [ ] Gate: so khớp thủ công với OKX/Uniswap cho ít nhất 3 fixture positions.

## Phase 3 — Risk & Alerts
- [ ] Fee APR theo cửa sổ 24h/7d/30d, tách incentive.
- [ ] Range status, distance-to-edge, uptime, fee coverage, IL/PnL theo đúng AMM version.
- [ ] Token/contract, depeg, exploit, pause, bridge và congestion checks.
- [ ] Telegram outbound-only; dedupe, severity, retry và delivery audit.
- [ ] Gate: test alert giả lập; không spam khi không có biến động quan trọng.

## Phase 4 — AI Analyst & Dashboard
- [ ] OpenAI Responses API với function tools read-only.
- [ ] Báo cáo tiếng Việt evidence-first; phân biệt confirmed/estimate/unknown.
- [ ] Dashboard trong cung Thị Bạc Ty; backend không nằm trên GitHub Pages.
- [ ] Chat history và decision journal.
- [ ] Gate: mọi kết luận truy ngược được về evidence IDs; không có tool giao dịch.

## Phase 5 — Multi-protocol expansion
- [ ] Uniswap V2/V4, PancakeSwap V2/V3.
- [ ] Orca/Raydium trên Solana với adapter riêng.
- [ ] QuickSwap, SushiSwap, Momentum và AMM khác sau khi xác minh LP thực tế trong OKX Wallet.
- [ ] Portfolio-level exposure và capital sizing cho 500–1.000 USD.

## Phase 6 — Learning loop
- [ ] Ghi lý do mở/giữ/đóng và kết quả thực tế.
- [ ] Đánh giá dự báo range/fee và sai số mô hình.
- [ ] Replay/backtest không look-ahead.
- [ ] Không bật execution tự động; mọi hành động vẫn do người dùng ký.

## Nhịp mục tiêu
- Pool metrics: 15–60 phút tùy provider/rate limits.
- Position state: mỗi giờ; nhanh hơn khi có biến động mạnh.
- Risk events: event-driven/polling nhanh khi nguồn hỗ trợ.
- AI: chỉ gọi khi có alert quan trọng hoặc người dùng yêu cầu.
- Dashboard: cập nhật snapshot mới nhất, hiển thị tuổi dữ liệu.

Vốn khởi điểm 500–1.000 USD là ràng buộc sizing. Tính gas vào/ra, slippage và chi phí tái cân bằng; tránh chia vốn quá nhỏ vào nhiều pool.
