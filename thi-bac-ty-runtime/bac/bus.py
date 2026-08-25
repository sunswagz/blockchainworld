"""Sổ sự kiện trong bộ nhớ — buồng lái đọc, không ai ghi ra đĩa từ đây.

**Đây KHÔNG phải "opportunity bus".** Tên `bus` dễ gây hiểu nhầm: nó chỉ là
một `deque` có trần, giữ dòng nhật ký cho buồng lái đọc. Không ai đăng ký
nhận, không có chiến lược nào nối vào, và không cơ hội nào đi qua đây.

Chỗ nối các chiến lược lại với nhau — khi Thị Bạc Ty có chiến lược thứ hai —
là một thứ khác hẳn và chưa tồn tại. Đừng nối nó vào file này chỉ vì trùng
tên; lúc ấy hãy đổi tên file này thành `nhat_ky_su_kien.py` cho khỏi lẫn.

Cố ý có trần: một vòng lặp 2 giây chạy qua đêm sinh ra hàng chục nghìn dòng,
và một danh sách không trần sẽ ăn hết RAM rồi giết runtime vì lý do không liên
quan gì tới giao dịch.
"""
from __future__ import annotations

import datetime as _dt
import threading
from collections import deque


def bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class Bus:
    def __init__(self, tran: int = 600) -> None:
        self._d: deque = deque(maxlen=tran)
        self._khoa = threading.Lock()
        self._dem = 0

    def ghi(self, muc: str, loai: str = "tin", **kw) -> dict:
        with self._khoa:
            self._dem += 1
            e = {"stt": self._dem, "luc": bay_gio(), "loai": loai, "muc": muc, **kw}
            self._d.append(e)
        return e

    def gan_day(self, n: int = 120) -> list[dict]:
        with self._khoa:
            return list(self._d)[-n:]

    def tong(self) -> int:
        return self._dem


bus = Bus()
