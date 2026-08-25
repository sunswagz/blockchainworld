# HANDOFF CHO CLAUDE CODE

## Mục tiêu
Đưa Knowledge OS vào `sunswagz/blockchainworld` như lớp tri thức nền dùng chung. **Không dựng thêm một cung đọc The Bitcoin Standard.**

## Trước khi sửa
1. Đọc toàn bộ `CLAUDE.md` hiện tại của repo.
2. Audit repo hiện tại, không tin cứng snapshot trong gói nếu repo đã đổi.
3. Làm đúng worktree/branch và ranh giới file của repo.
4. `factory/registry.json` đang là file bot sinh: không sửa tay.

## Kiến trúc đề xuất
- Đặt gói lõi ở nguồn, ví dụ `knowledge-os/` (không deploy nguyên khối).
- Viết generator (bộ sinh) theo phong cách repo để tạo context nhỏ cho từng cung, ví dụ `thi-bac-ty/assets/js/v/knowledge.js`.
- V1 ưu tiên `thai-boc-tu`, `ho-bo`, `thi-bac-ty`, sau đó `cong-bo`, `do-sat-vien`, `kham-thien-giam`.
- Không thay công thức tài chính hiện có chỉ để khớp sách; Knowledge OS chỉ giải nghĩa và nối bối cảnh.

## V1 cần xong
- `thai-boc-tu`: t01↔consensus/final_settlement; t04↔medium_of_exchange/unit_of_account; t05↔salability/price_signal; t06↔capital_market/interest_rate.
- `thi-bac-ty`: funding ↔ interest_rate + capital_market + price_signal.
- `ho-bo`: stablecoin ↔ medium_of_exchange + unit_of_account + counterparty_risk; yield ↔ interest_rate + risk.
- Validator concept/relation/hall mapping.
- Chạy toàn bộ kiểm tra repo hiện có.

## Lớp 2018→2026
Không sửa dữ liệu book để “cập nhật sách”. Tạo lớp `data/2026/` riêng cho stablecoin, DeFi, RWA, rollup, MEV, perpetual DEX, AI agents. Quan hệ mới phải mang loại `supports/challenges/extends` và nguồn web/repo riêng.
