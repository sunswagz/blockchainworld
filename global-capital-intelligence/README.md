# Global Capital Intelligence

Module quan sát tài sản nằm trong Blockchain World.

## MVP hiện tại
- Asset registry nhập từ `Văn bản đã dán (1)(1).txt`.
- Tìm kiếm, lọc theo loại tài sản và nhóm ngành.
- Link mở biểu đồ TradingView cho từng mã.
- PWA shell cache để mở lại trang khi offline.
- Không hiển thị giá giả: dữ liệu giá được đánh dấu chưa kết nối nguồn.

## Registry
- 74 stock rows + 57 crypto rows + 20 market indicators trong tài liệu nguồn.
- Các mã trùng được gộp thành một tài sản và giữ nhiều nhóm phân loại.
- Mã, sàn và cặp giao dịch chưa được xác minh trực tiếp; xem `status` trong assets.json.
- Hedera được chuẩn hóa từ lỗi gõ `HBA RUSDT` thành `BINANCE:HBARUSDT`, theo ghi chú ngay trong tài liệu.

## Chạy và kiểm tra
```bash
node scripts/check-gci.mjs
```

## Lộ trình dữ liệu Balanced
1. Xác minh danh tính/sàn/cặp của từng tài sản.
2. Crypto: adapter CoinGecko với cache server-side/GitHub Actions, tôn trọng quota.
3. Stocks: adapter nhà cung cấp có license phù hợp; API key chỉ lưu trong GitHub Secrets.
4. Lưu snapshot và thời điểm cập nhật; không đưa API key vào client bundle.

Trang không phải khuyến nghị đầu tư.
