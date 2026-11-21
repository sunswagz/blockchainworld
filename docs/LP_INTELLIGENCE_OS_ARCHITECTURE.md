# LP Intelligence OS — Kiến trúc kỹ thuật

Phiên bản 0.1.0 · Foundation proposal · DEX liquidity pools only.

## 1. Mục tiêu

LP Intelligence OS là lớp quan sát, phân tích và quản trị vị thế LP cá nhân tích hợp với Thị Bạc Ty / BlockchainWorld. Vốn khởi điểm dự kiến 500–1.000 USD. Hệ thống phải phân biệt phí swap thực nhận, incentive, IL, gas, slippage và chi phí tái cân bằng; không xếp APR ngắn hạn thành cơ hội chỉ vì con số cao.

Câu hỏi sản phẩm:
1. Pool nào có thanh khoản, volume và phí swap thực tế đáng theo dõi?
2. APR nào đến từ phí, APR nào đến từ incentive?
3. Giá hiện tại đang ở đâu so với range và khi nào vị thế ngừng thu phí?
4. Phí có bù IL, gas và chi phí tái cân bằng không?
5. Có sự kiện depeg, exploit, pause, bridge hoặc chain congestion không?
6. Số liệu nào là on-chain confirmed, provider estimate hay unknown?

## 2. Ranh giới với BlockchainWorld hiện hữu

- thi-bac-ty-runtime/lp_amm là engine AMM đã có trên main, thiên về cặp tài sản cùng nhóm neo và bộ lọc rủi ro thận trọng. Giữ nguyên, không thay thế.
- thi-bac-ty-runtime/thi_bac_ty là Trung Ương và hợp đồng ToTrinh. LP Intelligence giai đoạn đầu chỉ quan sát/đề xuất, chưa gửi quyết định cấp vốn vào Capital Allocator.
- thi-bac-ty là cung tĩnh read-only. Đây là nơi hiển thị snapshot đã xuất; không chứa secrets và không làm backend.
- scripts/build-dist.mjs loại runtime Python khỏi dist. Không thêm runtime vào HALLS hoặc GitHub Pages.
- PR #2 Market Intelligence foundation là PR riêng; không tự động merge hoặc sửa đổi trong LP PR.

### Nghiên cứu LP V3 cũ

Nhánh claude/liquidity-pool-system-h3jvq8 có ý tưởng range uptime, fee coverage, PnL so HODL và đọc vị thế theo địa chỉ. Tuy nhiên nhánh này diverged khỏi main (19 commits ahead, 317 behind tại thời điểm kiểm tra) và phần LP V3 tập trung tokenized equities/USDG trên X Layer. Không merge/cherry-pick nguyên nhánh. Chỉ tái sử dụng khái niệm đã kiểm chứng sau khi viết test cho Ethereum/Base.

## 3. Kiến trúc logic

    OKX public wallet address ───────┐
                                     │ read-only
    DEX / chain data providers ──────┼──> Collectors + protocol adapters
                                     │             │
    Macro / market data ─────────────┘             ▼
                                          Normalize + provenance
                                                   │
                                                   ▼
                                          SQLite / PostgreSQL
                                                   │
                            ┌──────────────────────┼─────────────────┐
                            ▼                      ▼                 ▼
                       Pool Scanner          Position Monitor    Risk Engine
                            └──────────────────────┼─────────────────┘
                                                   ▼
                                            Alert Event Engine
                                                   │
                                      ┌────────────┴────────────┐
                                      ▼                         ▼
                                Telegram Bot                AI Analyst
                                                            OpenAI API
                                      └────────────┬────────────┘
                                                   ▼
                                           Read-only Dashboard
                                           BlockchainWorld / Thị Bạc Ty
                                                   │
                                                   ▼
                                       User reviews and signs in OKX

## 4. Data adapters và nguồn

Mỗi adapter phải khai báo provider, chain_id, protocol, version, observed_at, fetched_at, data_status và source_url. Thiếu số phải là null, không phải 0.

- OKX Onchain OS Market API: supported-chain registry và token top-liquidity để phát hiện/đối chiếu pool. Endpoint top-liquidity trả top 5 pool của một token, không phải danh mục toàn bộ pool.
- Uniswap subgraph / GraphQL: pool, swaps, volume, TVL, fee tier, position entities và dữ liệu giờ/ngày. Đây là indexer, không thay thế xác minh on-chain.
- RPC/EVM logs: xác minh chain, factory, pool contract, token addresses, tick/range, NFT position và fee accounting.
- GeckoTerminal / DefiLlama: cross-check thanh khoản, volume, TVL và yields; APR annualized từ cửa sổ ngắn chỉ là tín hiệu rủi ro.
- Orca/Raydium: adapter Solana riêng; không áp dụng giả định EVM.
- Macro: Fed, USD, yields, ETF flows và lịch sự kiện; chỉ làm bối cảnh rủi ro.

### Protocol adapter registry

Mỗi adapter khai báo các capability riêng: pool_discovery, pool_metrics, position_discovery, position_accounting, range_math, fee_accounting, incentive_accounting.

Không bật capability chỉ vì giao thức xuất hiện trong danh sách DEX swap routes của OKX. Hỗ trợ swap/route không đồng nghĩa OKX Wallet hỗ trợ tạo, tăng, giảm hoặc thu phí LP trên giao thức đó.

Ưu tiên triển khai:
1. Uniswap V3 trên Base — pool ETH/USDC.
2. Uniswap V3 trên Ethereum.
3. Uniswap V2 và PancakeSwap V3 sau khi adapter được kiểm chứng.
4. Orca, Raydium, QuickSwap, SushiSwap, Momentum và AMM khác sau khi xác minh chain, contract/program và khả năng LP thực tế.

## 5. Position monitor

Địa chỉ ví công khai được nhập thủ công; không cần connect wallet hoặc ký message. EVM Uniswap V3 positions được nhận diện từ NFT Position Manager và đối chiếu pool/tick. Solana positions dùng owner/program-account discovery riêng.

## 6. Risk engine

Bắt buộc tách:
- Observed: fee collected, feeGrowth, swap volume, TVL, spot price, liquidity, gas paid.
- Estimated: fee APR theo cửa sổ quan sát, slippage dự kiến, xác suất rời range.
- Unknown: thuế token chưa xác minh, fee chưa đọc được, bridge exposure chưa kiểm tra.

Chỉ báo:
- Fee APR và incentive APR tách riêng.
- Fee coverage = realized/estimated fees ÷ (IL + gas + rebalance cost), cùng kỳ và cùng đơn vị.
- PnL tuyệt đối và alpha so HODL tách riêng.
- Range status, distance-to-edge, time-in-range / uptime.
- Data freshness, source agreement và completeness.
- Depeg, token legitimacy, contract admin/upgrade, exploit/pause, bridge và congestion.

Không dùng công thức IL V2 50/50 để đánh giá concentrated liquidity V3/V4. V3/V4 cần range-specific math và fee-growth accounting.

## 7. AI Analyst

AI chỉ được gọi công cụ đọc: get_pool_snapshot, get_pool_history, get_position_snapshot, get_position_history, get_risk_events, get_macro_context, simulate_lp_scenario.

AI không có tool ký giao dịch, approve token, gửi transaction, chuyển tài sản hoặc thay đổi cấu hình ví. Mọi báo cáo phải kèm evidence IDs, nguồn, thời điểm và độ chắc chắn. Không được bịa dữ liệu thiếu.

## 8. Alert engine

Kiểm tra mỗi giờ; chỉ gửi khi vượt ngưỡng quan trọng hoặc có sự kiện khẩn cấp. Không gửi thông báo “không có gì mới” mỗi giờ. Exploit, depeg nghiêm trọng, protocol pause, bridge incident hoặc điều kiện rút tiền bị ảnh hưởng có thể phát ngay.

Alert gồm severity, dedupe_key, first_seen_at, last_seen_at, evidence, impact, recommended_checks và delivery status.

## 9. Dashboard và triển khai

- Static UI: cung tĩnh hiện hữu trong thi-bac-ty.
- API: FastAPI trong thi-bac-ty-runtime, deploy thành container/VPS riêng.
- Database: SQLite local MVP; PostgreSQL khi chạy server liên tục.
- Scheduler: worker/cron riêng; GitHub Actions chỉ dùng CI, batch snapshot và deploy, không làm daemon 24/7.
- Secrets: environment/secret manager ở backend.
- Static GitHub Pages chỉ nhận JSON snapshot đã xuất; không chứa OpenAI key, Telegram token, RPC secret hoặc database URL.

## 10. Bảo mật

1. Chỉ public address; không ký message.
2. Không yêu cầu seed phrase/private key.
3. Không có transaction-building/execution endpoint trong MVP.
4. API dashboard chỉ GET; CORS allowlist và rate limit ở backend.
5. Secrets không commit, không log, không đưa vào static assets.
6. Provider data là untrusted input.
7. Người dùng luôn tự xem và ký giao dịch trong OKX.

## 11. Tiêu chí MVP

- Canonical schema và provenance.
- SQLite append-only snapshots/positions/alerts.
- API read-only.
- Phép tính offline có kiểm thử.
- Adapter Uniswap V3/Base sau khi xác minh nguồn dữ liệu và contract.
- Monitor public wallet address, không cần connect wallet.
- Telegram alert và AI analysis sau khi cấu hình secrets ở server.
- Không có khả năng ký hoặc gửi giao dịch.
