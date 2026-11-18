# Global Capital Intelligence

Module nghiên cứu vốn nằm trong Blockchain World.

## Phạm vi hiện tại
- Registry: 149 tài sản duy nhất gồm 73 stocks, 56 crypto assets và 20 market indicators, được nhập từ tài liệu nguồn.
- Tìm kiếm theo mã, tên, vai trò và nhóm ngành; lọc theo lớp tài sản/ngành.
- Watchlist cá nhân: thêm/bỏ tài sản, lưu bằng localStorage trên trình duyệt hiện tại.
- Sao chép toàn bộ mã trong bộ lọc hiện tại theo định dạng một mã mỗi dòng để đưa sang TradingView.
- Xuất danh sách đang lọc thành CSV (UTF-8 BOM, hỗ trợ Excel).
- Mở chart TradingView theo mã.
- PWA shell cache; registry có thể đọc lại sau khi đã được cache.
- Không tạo giá giả. Giao diện phân biệt registry với dữ liệu thị trường.

## Data integrity
- Mã/sàn/cặp giao dịch và trạng thái niêm yết vẫn cần xác minh.
- Hedera được chuẩn hóa theo ghi chú trong tài liệu nguồn.
- Các công ty tư nhân không được tự gán mã niêm yết.
- Watchlist lưu cục bộ, chưa đồng bộ giữa các thiết bị.
- Giá realtime, OHLCV, lịch sử, tín hiệu, scoring và cảnh báo chưa được kết nối.

## Kiến trúc dữ liệu đề xuất cho giai đoạn tiếp theo
1. **Instrument master**: chuẩn hóa tài sản theo provider ID, exchange, quote currency, contract address và chain; giữ nguyên symbol nguồn để truy vết.
2. **Crypto adapter**: provider có API terms rõ ràng; cache server-side và tôn trọng rate limit.
3. **Equity adapter**: nhà cung cấp dữ liệu cổ phiếu có quyền sử dụng phù hợp; API key chỉ lưu trong GitHub Secrets hoặc backend, không đưa vào browser bundle.
4. **Snapshot store**: lưu giá, timestamp, nguồn, độ trễ và trạng thái kiểm tra chất lượng.
5. **Signal layer**: heatmap, relative strength, volume anomaly, capital flow và scoring chỉ được bật khi có dữ liệu đủ chuẩn.
6. **Alert layer**: ngưỡng và lịch cập nhật tách khỏi UI; không coi giá cũ là giá hiện tại.

## Kiểm tra
```bash
node scripts/check-gci.mjs
node scripts/build-dist.mjs
```

Đây là công cụ nghiên cứu, không phải khuyến nghị đầu tư.
