"""Thị Bạc Ty — ty coi việc buôn bán giữa các cảng.

Thị Bạc Ty là sở quan trông coi tàu buôn nước ngoài: xét hàng, thu thuế, và
đối chiếu giá **giữa các cảng** với nhau. Runtime này làm đúng việc ấy trên
hợp đồng vĩnh cửu (perpetual futures): cùng một tài sản, cùng một lúc, mỗi
sàn trả một mức **funding** khác nhau — và chênh lệch ấy là thứ có thể thu
được mà không cần đoán giá đi lên hay đi xuống.

    LONG nơi funding thấp   ·   SHORT nơi funding cao   ·   DELTA ≈ 0

Đọc README.md trước khi sửa. Bốn điều không được quên:

  1. Không đưa runtime này vào bất kỳ GitHub Actions nào.
  2. **Funding trả theo MỐC, không chảy liên tục.** Giữ 4 giờ trên một sàn
     kết toán 8 giờ có thể thu được ĐÚNG BẰNG KHÔNG. Xem `dongho.py`.
  3. NET EDGE sau phí, trượt giá và lệch mark mới là alpha. Funding thô
     thì không.
  4. Cửa đặt lệnh thật đóng cứng, và mở nó cần ba việc ở ba nơi khác nhau.
"""

__version__ = "0.1.0"

import sys as _sys

# Console Windows mặc định là cp1252 — nó không in nổi dấu tiếng Việt, và một
# `UnicodeEncodeError` giữa vòng lặp sẽ giết runtime vì một dòng LOG chứ không
# phải vì một lỗi giao dịch.
#
# Chỗ này là `__init__.py` chứ không phải `config.py`, và đó là chủ ý: mọi
# đường vào gói đều đi qua đây, kể cả `python -m bac.snapshot` hay một script
# kiểm chỉ import mỗi `bac.dongho`.
for _luong in (_sys.stdout, _sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
