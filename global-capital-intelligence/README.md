# Global Capital Intelligence — Market Data Engine

## Data pipeline hiện tại
- **Crypto live board:** Binance Spot public REST snapshot mỗi 60 giây + WebSocket ticker stream cho các cặp đang theo dõi (tick cập nhật theo luồng sàn, thường khoảng 1 giây), không cần API key.
- **History:** Binance Spot Klines khi chọn một tài sản, các khung 1D / 7D / 30D.
- **Equities:** TradingView Symbol Info widget + link OPEN CHART. Data level phụ thuộc quyền dữ liệu từng sàn/TradingView.
- **Flow proxy:** Binance taker-buy quote volume trừ phần còn lại; không đồng nghĩa dòng vốn ròng toàn thị trường.
- **Breadth:** số cặp tăng/giảm trong universe có dữ liệu.
- **Relative strength:** bình quân hiệu suất 24h của các cặp crypto đang có dữ liệu.
- **GCI score:** thang 0–100 gồm Trend 25%, Momentum 25%, Volume tương đối 20%, Buyer pressure 15%, Liquidity 15%. Đây là bộ lọc quan sát kỹ thuật ngắn hạn, không phải dự báo/khuyến nghị.
- **Watchlist:** lưu local trên trình duyệt; CSV và copy symbols giữ nguyên.

## Nguồn và giới hạn
- Binance Spot public market endpoints: `/api/v3/ticker/24hr`, `/api/v3/klines`. Chỉ phản ánh thanh khoản/cặp trên Binance Spot; cặp không tồn tại hoặc đã delist sẽ không có dữ liệu.
- TradingView widgets không phải API giá cho phép tự lưu trữ. Widget có branding và dữ liệu theo quyền dữ liệu của từng exchange; nâng cấp TradingView account không làm dữ liệu nhúng thành realtime.
- Volume, buyer pressure và breadth là proxy giao dịch; không gọi là ETF flows, on-chain net flows hay institutional flows.
- Stock API riêng chưa bật. Twelve Data Basic công bố real-time US equities nhưng gắn giới hạn “internal non-display usage”; trước khi hiển thị dữ liệu cổ phiếu qua API riêng cần kiểm tra license/display rights phù hợp. Không đưa API key vào browser.
- Nếu muốn snapshot server-side, cần GitHub Actions/backend và provider key được thêm vào GitHub Secrets bởi chủ repository.

## Thực hành
- WebSocket crypto: chỉ subscribe các cặp trong universe; REST snapshot/flow metrics refresh 60 giây (throttled); lịch sử tải theo yêu cầu.
- Historical klines: tải khi người dùng chọn tài sản/khung thời gian.
- Cache service worker chỉ cache app shell, không cache phản hồi thị trường như thể đó là live.
- Không có dữ liệu: hiển thị trạng thái lỗi hoặc thiếu cặp, không tự điền giá giả.

## Roadmap tiếp
1. Xác minh mapping của từng symbol với exchange/provider ID.
2. Thêm provider cổ phiếu có quyền hiển thị phù hợp (có thể Twelve Data Grow trở lên tùy license/điều khoản).
3. Lưu snapshots OHLCV và trạng thái provider phía server.
4. Tách module ETF flows, on-chain flows và macro liquidity khi có nguồn xác minh.
5. Alert engine cho ngưỡng giá, biến động, volume anomaly và scoring.

## Kiểm thử
```bash
node scripts/check-gci.mjs
node --check global-capital-intelligence/assets/js/app.js
node scripts/build-dist.mjs
```
