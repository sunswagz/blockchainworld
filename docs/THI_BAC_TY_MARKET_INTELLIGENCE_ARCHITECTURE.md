# Kiến trúc Market Intelligence trong Thị Bạc Ty

**Trạng thái:** Foundation proposal v0.1  
**Phạm vi:** Tích hợp trực tiếp vào `thi-bac-ty-runtime`, không tạo runtime cạnh tranh.

## 1. Quyết định kiến trúc

Market Intelligence là lớp quan sát và diễn giải thị trường dùng chung, nằm trước Opportunity Engine. Nó cung cấp bối cảnh thị trường có nguồn gốc và độ mới rõ ràng; không tự cấp vốn, không tự đặt lệnh và không thay thế các ty chuyên môn.

Luồng mục tiêu:

```
PUBLIC DATA SOURCES
  ├─ Exchange market data (OHLCV, trades, order book, derivatives)
  ├─ Market aggregates (market cap, dominance, stablecoins)
  ├─ DeFi / on-chain metrics (TVL, flows, supply)
  └─ Macro / events
          │
          ▼
DATA INTAKE & PROVENANCE
  ├─ source adapter
  ├─ timestamp normalization (UTC)
  ├─ schema validation
  ├─ freshness / completeness checks
  └─ immutable raw snapshot
          │
          ▼
NORMALIZED MARKET CONTEXT
  ├─ BTC / ETH price structure
  ├─ TOTAL / TOTAL2 / TOTAL3
  ├─ BTC.D / ETH-BTC / USDT.D
  ├─ derivatives / liquidity
  └─ macro / ecosystem context
          │
          ▼
ANALYSIS & FORECAST
  ├─ technical features and market structure
  ├─ regime / cycle classification
  ├─ capital rotation
  ├─ bullish / base / bearish scenarios
  └─ forecast evaluation
          │
          ▼
THỊ BẠC TY CENTRAL
  ├─ attach market context to opportunity review
  ├─ Risk Engine remains authoritative
  ├─ Capital Allocator remains authoritative
  └─ Ledger records capital decisions
```

## 2. Ranh giới với các runtime hiện hữu

- `thi-bac-ty-runtime/thi_bac_ty/`: nơi sở hữu hợp đồng dữ liệu thị trường chuẩn và điểm nối vào Trung Ương.
- `thi-bac-ty-runtime/bac/`: giữ nguyên ty funding-spread đang hoạt động; không refactor trong foundation.
- `tu-cam-thanh-runtime/trader/`: đã có bộ chỉ báo kỹ thuật và các kỹ năng Market Structure / Regime Detection. Không sao chép mù quáng; tích hợp qua hợp đồng dữ liệu hoặc API có phiên bản.
- `kham-thien-giam-runtime/kham/`: runtime quan sát/nghiên cứu thị trường hiện hữu. Có thể cung cấp các bản quét đã chuẩn hóa qua adapter, không import chéo module runtime.
- `knowledge-os/`: giữ tri thức, định nghĩa và quan hệ; không trở thành nguồn dữ liệu thị trường realtime.

Không tạo import ngược từ Trung Ương sang `bac/`. Không tạo phụ thuộc Python trực tiếp giữa ba runtime. Trao đổi qua JSON/API có schema và phiên bản.

## 3. Các miền dữ liệu

### Market breadth
- BTCUSDT, ETHUSDT: giá và OHLCV.
- TOTAL, TOTAL2, TOTAL3: tổng vốn hóa và breadth.
- BTC.D, ETH/BTC, USDT.D: dominance và rotation.

### Derivatives & liquidity
- Funding rate, open interest, basis, liquidation aggregates.
- Order-book depth / spread khi nguồn có thể xác minh.
- Không suy ra thanh khoản thực từ OI đơn lẻ.

### On-chain / ecosystem
- Stablecoin supply, chain TVL, bridge flows, protocol metrics.
- Phân biệt số dư, dòng vào/ra, số liệu ước tính và dữ liệu đã xác nhận.

### Macro / events
- USD, rates, liquidity proxies và lịch sự kiện.
- Mỗi chỉ số phải khai báo tần suất, độ trễ và nguồn.

## 4. Multi-timeframe

Khung chuẩn: 1h, 4h, 1D, 1W, 1M, 3M.  
Các kỳ dự báo chuẩn: 1D, 1W, 1M, 3M, 1Y.

Quy tắc:
- Chỉ dùng nến đã đóng cho tín hiệu xác nhận, trừ khi đánh dấu rõ provisional.
- Dự báo ngắn hạn không được ghi đè xu hướng khung lớn.
- Nến tháng/tuần chưa đóng phải có trạng thái provisional.
- Không trộn timezone; lưu UTC, hiển thị theo Asia/Ho_Chi_Minh.
- Không dùng dữ liệu tương lai khi backtest (look-ahead bias).

## 5. Cơ chế độ tin cậy dữ liệu

Mọi observation phải có source, observed_at, fetched_at, unit và trạng thái.  
`None` có nghĩa là chưa biết/không có dữ liệu; không thay bằng 0.

Trạng thái tối thiểu:
- `fresh`: còn trong ngưỡng tuổi dữ liệu.
- `stale`: đã quá ngưỡng tuổi.
- `missing`: không có dữ liệu.
- `invalid`: sai schema hoặc không hợp lệ.
- `provisional`: dữ liệu chưa chốt (ví dụ nến đang chạy).

Một chỉ số stale/missing không được hiển thị như dữ liệu realtime. Mỗi báo cáo phải nêu thời điểm dữ liệu và độ phủ.

## 6. Hợp đồng với Capital OS

Market Intelligence xuất `MarketContext` và `Forecast` có phiên bản. Nó không xuất lệnh giao dịch và không được tự cấp vốn.

Trong giai đoạn đầu:
1. Context chỉ hỗ trợ người phân tích và Opportunity Engine.
2. Các ty tiếp tục xuất `ToTrinh` theo hợp đồng hiện tại.
3. Risk Engine và Capital Allocator giữ quyền quyết định vốn.
4. Mọi đề xuất thay đổi tham số phải qua replay, review và versioning hiện hữu.
5. Không bật execution tự động từ tín hiệu phân tích.

Chỉ sau khi có dữ liệu lịch sử đủ tốt, kiểm định ngoài mẫu và phê duyệt mới xem xét cho phép MarketContext tác động định lượng đến risk ceilings.

## 7. Cập nhật và vận hành

Mục tiêu vận hành (không phải cam kết SLA):
- 1m–5m: giá/market microstructure từ stream hoặc polling phù hợp.
- 15m: cập nhật feature ngắn hạn.
- 1h: tổng hợp regime, derivatives và cảnh báo.
- 1D: snapshot đóng nến ngày và forecast log.
- 1W / 1M: đánh giá chu kỳ khi nến đã đóng.

GitHub Actions không phải hạ tầng streaming 24/7. Dùng workflow cho batch/research/deploy; dùng worker riêng và database managed cho ingestion liên tục. Dashboard GitHub Pages chỉ là read-only presentation; không chứa API secret.

## 8. Bảo mật và an toàn

- Public market data only ở giai đoạn đầu.
- Không lưu API key giao dịch, private key hoặc seed phrase.
- Không cấp quyền đặt lệnh cho collector hoặc analyst.
- Secrets chỉ đặt trong secret manager của môi trường triển khai.
- API dashboard chỉ đọc; endpoint điều khiển runtime hiện hữu giữ localhost.
- Tách ingestion, analysis, capital decision và execution thành các quyền riêng.

## 9. Tiêu chí hoàn thành foundation

- Hợp đồng observation/forecast có kiểm tra.
- Tài liệu kiến trúc, nguồn dữ liệu, freshness và risk boundary.
- Unit tests offline, không gọi mạng.
- Branch riêng và pull request draft; chưa merge vào main.
