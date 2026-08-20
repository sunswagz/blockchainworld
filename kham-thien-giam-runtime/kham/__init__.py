"""Khâm Thiên Giám — đài chiêm nghiệm thị trường tiên đoán.

Đài thiên văn nhà Nguyễn tính ra bầu trời ĐÁNG LẼ phải thế nào, rồi đem so
với điều người đời đang tin. Runtime này làm đúng việc ấy trên Polymarket:
tính `fair value` của một outcome, đem so với giá chợ, và chỉ động thủ khi
khoảng cách còn sống sót sau phí, trượt giá và sức chứa của sổ lệnh.

Đọc README.md trước khi sửa. Ba điều không được quên:

  1. Không đưa runtime này vào bất kỳ GitHub Actions nào.
  2. `net edge` mới là alpha. `signal`, `latency`, `accuracy` thì không.
  3. Risk Engine ở `rui_ro.py` là Python thuần và có quyền phủ quyết.
"""

__version__ = "0.1.0"

import sys as _sys

# Console Windows mặc định là cp1252 — nó không in nổi dấu tiếng Việt, và một
# `UnicodeEncodeError` giữa vòng lặp sẽ giết runtime vì một dòng LOG chứ không
# phải vì một lỗi giao dịch.
#
# Chỗ này là `__init__.py` chứ không phải `config.py`, và đó là chủ ý: mọi
# đường vào gói đều đi qua đây, kể cả `python -m kham.snapshot` hay một script
# kiểm chỉ import mỗi `kham.dongho`. Đặt ở `config.py` thì module nào không
# import config sẽ không được bảo vệ — đã vấp đúng một lần lúc dựng.
#
# Không dùng biến môi trường PYTHONIOENCODING: nó phải được đặt TRƯỚC khi
# Python khởi động, tức là ngoài tầm với của chính file này.
for _luong in (_sys.stdout, _sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
