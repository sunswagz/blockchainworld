# Market Intelligence package

Gói này là lớp bối cảnh thị trường dùng chung của Trung Ương Thị Bạc Ty.

## Phạm vi v0.1
- Định nghĩa hợp đồng `MarketObservation`, `Scenario`, `Forecast`.
- Kiểm tra provenance, timestamp, trạng thái dữ liệu và xác suất.
- Không gọi mạng, không ghi database, không phát sinh giao dịch.

## Ranh giới
- Không import `bac/`.
- Không import trực tiếp từ `tu-cam-thanh-runtime` hoặc `kham-thien-giam-runtime`.
- Không thay thế `ToTrinh`, Risk Engine, Capital Allocator hoặc Ledger.
- Không có API key, private key hay quyền đặt lệnh.

Xem:
- [Kiến trúc](../../../docs/THI_BAC_TY_MARKET_INTELLIGENCE_ARCHITECTURE.md)
- [Đặc tả](../../../docs/THI_BAC_TY_MARKET_INTELLIGENCE_SPEC.md)
- [Roadmap](../../../docs/THI_BAC_TY_MARKET_INTELLIGENCE_ROADMAP.md)

## Kiểm tra offline
Từ thư mục `thi-bac-ty-runtime`:

```bash
python scripts/kiem-market-intelligence.py
```
