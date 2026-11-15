# Roadmap — Market Intelligence

## Nguyên tắc triển khai

Mỗi giai đoạn phải tạo ra một lát cắt chạy được, có test và có tiêu chí nghiệm thu. Không dựng 12 module rỗng cùng lúc. Không thay đổi đường đi của vốn khi chưa có bằng chứng.

## Phase 0 — Foundation (nhánh hiện tại)
- [x] Kiểm tra repository, runtime và các nguyên tắc Thị Bạc Ty hiện hữu.
- [x] Chốt kiến trúc: tích hợp trong `thi-bac-ty-runtime/thi_bac_ty/market_intelligence`.
- [x] Định nghĩa hợp đồng observation / forecast.
- [x] Viết đặc tả sản phẩm, nguồn dữ liệu, freshness, risk boundary.
- [ ] Merge sau khi review.

## Phase 1 — Market Snapshot (MVP dữ liệu)
- Adapter Binance public klines cho BTCUSDT/ETHUSDT.
- Adapter market-cap provider cho TOTAL family và dominance.
- Canonical schema + raw provenance + freshness.
- Local SQLite/PostgreSQL repository abstraction.
- Tests fixture/offline; không phụ thuộc API live để pass CI.

**Gate:** dữ liệu đồng bộ, không trùng nến, timestamp UTC đúng, phát hiện gap/stale; không ghi 0 cho missing.

## Phase 2 — Technical & Breadth
- Tích hợp feature technical theo module dùng chung có kiểm soát.
- Multi-timeframe 1D/1W/1M.
- Market structure, levels, momentum, volatility, breadth.
- Snapshot JSON versioned.

**Gate:** so khớp thủ công trên bộ fixture đã chọn; nến chưa đóng được đánh dấu provisional.

## Phase 3 — Scenario & Forecast Journal
- Bull/base/bear scenario engine theo 1D/1W/1M/3M/1Y.
- Trigger và invalidation bắt buộc.
- Lưu forecast append-only.
- Đánh giá forecast khi horizon hết hạn.

**Gate:** không ghi confidence/probability nếu chưa calibration; backtest walk-forward.

## Phase 4 — Dashboard & Alerting
- Dashboard read-only tích hợp vào buồng lái Thị Bạc Ty.
- Daily / weekly / monthly reports.
- Cảnh báo thay đổi regime, breadth, dominance và cấu trúc.
- Nguồn lỗi/stale được hiển thị rõ.

**Gate:** dashboard không chứa secret; endpoint điều khiển chỉ localhost.

## Phase 5 — Capital OS Context Bridge
- Adapter MarketContext sang Opportunity review.
- Đưa context vào báo cáo ToTrinh hoặc màn hình trung ương mà không phá schema hiện hữu.
- Risk Engine vẫn là quyền quyết định trần rủi ro.
- Replay và review mọi thay đổi tham số.

**Gate:** shadow mode, đối chiếu quyết định có/không có MarketContext; không cấp vốn tự động.

## Hạ tầng balanced đề xuất

- Local dev: Python runtime hiện có + SQLite fixtures.
- Continuous ingestion: một worker/container riêng (ví dụ VPS nhỏ hoặc managed container).
- Database: PostgreSQL managed khi cần lưu lịch sử tập trung; bắt đầu SQLite/local nếu chưa cần multi-user.
- Scheduler: cron/managed scheduler cho batch; WebSocket cho stream khi cần.
- Dashboard: giao diện read-only của runtime hiện hữu; static GitHub Pages chỉ hiển thị snapshot đã xuất.
- AI analysis: ChatGPT Project để phân tích cùng người dùng; API model riêng chỉ khi cần pipeline tự động, ngân sách API tách biệt.

Không dùng GitHub Actions làm worker streaming liên tục. Cron workflow có thể chạy batch và deploy snapshot, nhưng không phải daemon 24/7.

## Rủi ro cần kiểm soát
- Rate limit / thay đổi schema / gián đoạn nguồn.
- Sai lệch giữa các provider market cap.
- Dữ liệu sửa lại hoặc bị thiếu.
- Look-ahead bias và nến chưa đóng.
- AI hallucination và xác suất chưa calibration.
- Overfitting và thay đổi regime.
- Secrets lộ qua static site / logs.
