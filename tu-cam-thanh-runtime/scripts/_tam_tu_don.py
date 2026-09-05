"""Thư mục tạm TỰ DỌN lúc tiến trình thoát — một chỗ cho mọi bộ kiểm.

    os.environ["TCT_DATA_DIR"] = tam_moi("tct-kiem-")

VÌ SAO CẦN

Sáu script `kiem-*.py` đều ép `TCT_DATA_DIR` sang một thư mục tạm trước khi
import `trader` — đúng, và bắt buộc (xem `selftest [40]`: gọi `setdefault` thì
một dòng `export TCT_DATA_DIR=` trong shell là đủ để phép kiểm ghi thẳng vào sổ
thật, đã xảy ra ba lần). Nhưng không script nào DỌN thư mục ấy.

Vòng tiến hoá chạy các bộ kiểm liên tục, nên số thư mục bỏ lại trong `%TEMP%`
tăng khoảng 22.000 mỗi ngày. Ngày 04/09/2026 đếm được 130.837 thư mục rác chiếm
7,54 GB và ổ C: đầy 100% — đến mức `node` không khởi động nổi và mọi hook
PreToolUse ngã theo.

ĐẶT Ở ĐÂY, KHÔNG PHẢI TRONG `trader/`

Lời gọi phải chạy TRƯỚC `from trader import ...` (đó là cả điểm của nó), nên
helper không thể nằm trong gói `trader`. `scripts/` là thư mục của chính script
đang chạy nên luôn ở đầu `sys.path`.
"""
from __future__ import annotations

import atexit
import shutil
import tempfile

_DA_TAO: list[str] = []


def tam_moi(prefix: str) -> str:
    """Dựng thư mục tạm và ghi sổ để `atexit` xoá lúc thoát."""
    d = tempfile.mkdtemp(prefix=prefix)
    _DA_TAO.append(d)
    return d


@atexit.register
def _don() -> None:
    for d in _DA_TAO:
        shutil.rmtree(d, ignore_errors=True)
