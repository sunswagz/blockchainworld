"""Làm sạch số trước khi ra JSON.

`inf` và `nan` KHÔNG hợp lệ trong JSON, và Python thì sinh ra chúng rất dễ:
một phép chia cho 0 đã canh, một `float("inf")` dùng làm "cũ vô hạn", một
phương sai âm do sai số dấu phẩy động.

Chuyện đã xảy ra ngay lúc dựng: `TrangThaiNguon.tuoi_ms()` trả `inf` cho
nguồn chưa gọi lần nào — hoàn toàn đúng về mặt ngữ nghĩa để so sánh trong
`rui_ro.py`, và hoàn toàn không gửi đi được. Buồng lái nhận HTTP 500 và một
trang trắng, không phải một thông báo lỗi.

Chỗ nguy hơn: cùng lỗi ấy khi GHI LÁT CẮT sẽ làm `json.dumps` ném giữa chừng,
và runtime đang chạy vòng lặp sẽ chỉ ghi vào nhật ký rồi đi tiếp — cung tĩnh
đứng im ở lát cắt cũ mà không ai biết. Nên làm sạch ở một chỗ dùng chung cho
CẢ hai đường ra, thay vì vá đúng chỗ vừa nổ.

Quy ước: không biểu diễn được thì thành `None`, không thành 0. `None` hiện lên
giao diện là "—"; 0 hiện lên là một con số, và đó là nói dối.
"""
from __future__ import annotations

import math


def sach(x):
    """Trả về bản sao đã bỏ mọi `inf`/`nan`, đệ quy qua dict/list/tuple."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: sach(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [sach(v) for v in x]
    return x
