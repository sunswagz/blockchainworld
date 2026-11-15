# Đặc tả sản phẩm — Thị Bạc Ty Market Intelligence

**Phiên bản:** 0.1.0  
**Trạng thái:** Foundation / đề xuất để triển khai theo từng lát cắt  
**Mục tiêu:** Phân tích thị trường crypto và phát hiện bối cảnh/cơ hội đầu tư; không phải hệ thống tự động giao dịch.

## 1. Người dùng và đầu ra

Người dùng cần một bảng điều khiển trả lời:
1. Thị trường đang ở regime nào?
2. BTC, ETH và breadth thị trường đang mạnh/yếu ra sao?
3. Dòng vốn đang luân chuyển giữa BTC, ETH, altcoin, stablecoin và các hệ sinh thái nào?
4. Kịch bản 1D, 1W, 1M, 3M, 1Y là gì?
5. Điều kiện nào xác nhận hoặc vô hiệu hóa từng kịch bản?
6. Dự báo trước đây đúng/sai ở đâu và sai số bao nhiêu?

Đầu ra bắt buộc: market snapshot, data-quality report, technical summary, scenario forecast, risk notes, forecast evaluation.

## 2. Module sản phẩm

| ID | Module | Trách nhiệm |
|---|---|---|
| MI-01 | Market Data Intake | Thu thập, chuẩn hóa, lưu provenance |
| MI-02 | Market Breadth | BTC, ETH, TOTAL, TOTAL2, TOTAL3 |
| MI-03 | Dominance & Rotation | BTC.D, ETH/BTC, USDT.D, nhóm ngành |
| MI-04 | Technical Analysis | OHLCV, structure, EMA, RSI, MACD, ATR, volume |
| MI-05 | Derivatives | Funding, OI, basis, liquidation |
| MI-06 | On-chain & DeFi | Stablecoin, TVL, flow, ecosystem |
| MI-07 | Macro & Events | Rates, USD, liquidity, event calendar |
| MI-08 | Regime & Cycle | Accumulation, expansion, distribution, contraction |
| MI-09 | Forecast & Scenarios | Bull/base/bear theo horizon |
| MI-10 | Risk Context | Volatility, liquidity, correlation, invalidation |
| MI-11 | Forecast Journal | Lưu bất biến forecast và kết quả |
| MI-12 | Reporting & Alerts | Dashboard, daily/weekly/monthly report |

## 3. Danh mục nguồn dữ liệu dự kiến

| Nguồn | Dữ liệu | Vai trò / lưu ý |
|---|---|---|
| Binance public API | OHLCV, trades, order book, derivatives endpoints | Dữ liệu sàn; không đại diện toàn thị trường |
| CoinGecko | Giá, market cap, asset metadata | Aggregated market data; chú ý plan/rate limit |
| CoinMarketCap | Market cap, dominance, global metrics | Nguồn thay thế; API key/plan có thể cần |
| DefiLlama | TVL, stablecoins, yields, chains | DeFi ecosystem; định nghĩa từng metric phải được ghi rõ |
| TradingView | Charting / visual review | Không giả định có quyền API dữ liệu; đối chiếu qua biểu đồ hoặc nguồn được cấp phép |
| FRED / official macro sources | Macro series | Tần suất thấp, có độ trễ; ghi rõ release date |
| Glassnode / CryptoQuant | On-chain analytics | Giai đoạn sau; phụ thuộc gói API |

Không coi tất cả nguồn có sẵn miễn phí. Trước khi chọn nguồn chính thức phải thử coverage, rate limit, latency, revision policy, terms of use và chi phí.

## 4. Chuẩn hóa chỉ số và timeframe

### Symbols / indices
- BTCUSDT, ETHUSDT (exchange-specific).
- TOTAL, TOTAL2, TOTAL3 (aggregated market-cap series; không tự thay bằng tổng volume sàn).
- BTC.D, ETH/BTC, USDT.D.
- Sau MVP: SOL, BNB, XRP, stablecoin supply, chain TVL, sector indices.

### Timeframes
- Data candles: 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M (chỉ lấy những timeframe nguồn hỗ trợ).
- Forecast horizons: 1D, 1W, 1M, 3M, 1Y.
- Lưu cả event time và ingestion time.
- Mọi phép tính phải xử lý nến chưa đóng và khoảng trống dữ liệu.

## 5. Phương pháp phân tích

Không có chỉ báo đơn lẻ nào tạo ra tín hiệu giao dịch.

- Structure: swing highs/lows, HH/HL/LH/LL, BOS/CHoCH.
- Trend: EMA 20/50/100/200, slope và alignment.
- Momentum: RSI, MACD.
- Volatility: ATR, Bollinger bandwidth.
- Volume: volume profile/relative volume/OBV khi có dữ liệu phù hợp.
- Levels: support/resistance, Fibonacci retracement/extension; ghi rõ anchor points.
- Derivatives: funding/OI/liquidation; phân biệt crowding với directional flow.
- Rotation: BTC.D, ETH/BTC, TOTAL2/TOTAL3 và stablecoin dominance/supply.
- Macro: chỉ dùng series có ngày công bố và tần suất rõ.

Feature phải lưu version, tham số và input window để tái lập kết quả.

## 6. Forecast contract

Mỗi forecast gồm:
- forecast_id, model_version, created_at, as_of, valid_until.
- asset_or_index, horizon, timeframe_basis.
- regime, directional_bias.
- confidence (optional, calibrated only).
- probabilities (optional; chỉ công bố khi có mô hình hiệu chỉnh).
- bullish/base/bearish scenario.
- triggers, invalidation_conditions, target_zones (optional).
- evidence_ids, source_coverage, data_quality.
- status: draft / active / expired / invalidated / evaluated.

Không công bố xác suất chỉ dựa trên cảm giác. Nếu chưa có calibration, để null và dùng định tính. Không chỉnh sửa forecast cũ; tạo phiên bản mới và liên kết forecast superseded.

## 7. Kiểm định

- Walk-forward và out-of-sample; không random split time series.
- Tránh look-ahead bias, survivorship bias và revised-data leakage.
- Benchmark tối thiểu: buy-and-hold BTC, buy-and-hold ETH, cash/stablecoin.
- Đo directional accuracy, calibration/Brier score khi có probability, MAE/MAPE cho target định lượng, max adverse excursion và drawdown cho chiến lược.
- Báo cáo kết quả theo regime, asset, horizon và phí/slippage.
- Tách kết quả paper/research khỏi P&L thực.

## 8. MVP acceptance criteria

MVP chỉ được coi là đạt khi:
1. Có dữ liệu BTC/ETH OHLCV và TOTAL/TOTAL2/TOTAL3/dominance từ nguồn được ghi rõ.
2. Tất cả dữ liệu có observed_at, fetched_at, source, unit, freshness.
3. Tính được feature kỹ thuật cơ bản trên 1D/1W/1M.
4. Có forecast 1D/1W/1M/3M với kịch bản và invalidation.
5. Forecast được lưu và đánh giá sau horizon.
6. Tests offline chạy được.
7. Dashboard hiển thị stale/missing/provisional rõ ràng.
8. Không có quyền giao dịch hoặc tự phân bổ vốn.

## 9. Ngoài phạm vi MVP

- AI tự quyết định đầu tư hoặc cấp vốn.
- Auto trading / private keys / withdrawal.
- Mô hình dự đoán giá bằng deep learning trước khi có baseline và backtest.
- Tick-level full depth archive.
- Cam kết độ chính xác hoặc lợi nhuận.
