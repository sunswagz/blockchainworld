"""claude-crypto-trader — AI Trader Runtime, mốc M0."""

__version__ = "0.1.0"

import sys as _sys

# Console Windows mặc định là cp1252 — nó không in nổi dấu tiếng Việt, và một
# `UnicodeEncodeError` giữa vòng lặp sẽ giết runtime vì một dòng LOG chứ không
# phải vì một lỗi giao dịch. `bus.log()` được gọi từ trong `get_candles`, nên
# một dòng nhật ký có chữ "ớ" làm đứt luôn đường lấy dữ liệu.
#
# Chỗ này là `__init__.py` chứ không phải `config.py`, và đó là chủ ý: mọi
# đường vào gói đều đi qua đây, kể cả `python -m trader.snapshot` hay một
# script kiểm chỉ import mỗi `trader.bus`.
#
# Không dùng biến môi trường PYTHONIOENCODING: nó phải được đặt TRƯỚC khi
# Python khởi động, tức là ngoài tầm với của chính file này.
#
# `kham/__init__.py` và `bac/__init__.py` đã có khối này từ trước, và chú
# thích ở đó ghi "Bài học từ Tử Cấm" — bài học rút ra TỪ runtime này rồi đem
# áp cho hai runtime sau, mà chính nơi sinh ra nó thì chưa ai quay lại vá.
# `scripts/selftest.py` vì thế chết giữa chừng ở `trader/bus.py`, trong khi
# chạy lại với PYTHONIOENCODING=utf-8 thì 100% đạt: mã vẫn đúng, chỉ đường ra
# chữ là sai.
for _luong in (_sys.stdout, _sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
