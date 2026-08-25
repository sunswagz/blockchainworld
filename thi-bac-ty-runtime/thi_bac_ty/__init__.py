"""THỊ BẠC TY — Trung Ương.

Đây **không phải** một chiến lược. Đây là bộ máy trung tâm mà mọi ty phải đi
qua: hợp đồng cơ hội, sổ đăng ký, danh mục, rủi ro tổng, phân bổ vốn, sổ cái,
điều phối thực thi.

    THỊ BẠC TY
        │
        ├── TRUNG ƯƠNG  ← gói này
        │     Data · Risk · Capital · Ledger · Execution
        │
        └── CÁC TY      ← `bac/` hiện là ty đầu tiên đã hoạt động
              Phái sinh · Tín dụng · Chênh lệch · Thanh khoản ·
              Thanh lý · MEV · Cầu nối

## Luật chung, và nó là lý do gói này tồn tại

    KHÔNG ty nào được tự quản toàn bộ vốn của hệ thống.
    KHÔNG ty nào được tự dựng Rủi Ro Tổng riêng.
    KHÔNG ty nào được tự quyết danh mục.

    MỌI ty chỉ: phát hiện → đánh giá → xuất TỜ TRÌNH.

Không có luật này thì mười ba ty là mười ba đứa đều tưởng tiền trong ví là
của mình — và không đứa nào nhìn thấy tổng.

## Chiều phụ thuộc, một chiều

    bac/  (ty)  ──import──►  thi_bac_ty/  (trung ương)

Trung ương **không được** import ngược. Nó không biết funding spread là gì,
không biết `dongho.py` đếm mốc kết toán ra sao. Nó chỉ biết `ToTrinh`.

Ngày nào trung ương phải `import bac` để xử một trường hợp riêng, ngày ấy hợp
đồng đã hỏng: nghĩa là `ToTrinh` chưa nói đủ, và chỗ phải sửa là hợp đồng chứ
không phải thêm một nhánh `if` cho ty đó.

## Chưa refactor `bac/`, và đó là chủ ý

`bac/` đang chạy thật, có 159 phép kiểm, có băng ghi và vòng tiến hoá. Chuyển
cả nó sang kiến trúc mới trong một lượt là cách nhanh nhất để phá thứ đang
chạy. Nên:

    bac/  giữ nguyên  ──►  adapter  ──►  thi_bac_ty/

Lớp mới dựng XUNG QUANH, không dựng ĐÈ. Khi trung ương ổn định rồi mới từ từ
chuyển ruột.
"""

__version__ = "0.1.0"

import sys as _sys

# Console Windows mặc định cp1252 — không in nổi dấu tiếng Việt. Cùng lý do
# đã ghi ở `bac/__init__.py`; lặp lại ở đây vì gói này phải chạy được độc lập
# (phép kiểm có thể chỉ import `thi_bac_ty` mà không chạm `bac`).
for _luong in (_sys.stdout, _sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
