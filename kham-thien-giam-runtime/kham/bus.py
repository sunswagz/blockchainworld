"""Sổ sự kiện trong bộ nhớ — buồng lái đọc, không ai ghi ra đĩa từ đây.

Cố ý có trần: một vòng lặp 2 giây chạy qua đêm sinh ra hàng chục nghìn dòng,
và một danh sách không trần sẽ ăn hết RAM rồi giết runtime vì lý do không liên
quan gì tới giao dịch.

## Và cố ý GỘP dòng lặp — cái trần thôi thì chưa đủ

Một điều kiện dai (mất đường tới chợ) kêu lại mỗi vòng. Đo thật: 78 trong
80 dòng buồng lái là ĐÚNG NĂM câu lặp đi lặp lại, tất cả nói một chuyện.
Cái trần khi ấy không bảo vệ được gì — nó chỉ quyết định dòng nào bị đẩy
ra, và dòng bị đẩy ra luôn là dòng HIẾM, tức là dòng đáng đọc nhất.

Chuyện này đã trả giá: `KeyError: 'gamma'` giết mọi vòng lặp suốt mấy
tiếng trong khi buồng lái vẫn xanh, vì tiếng kêu của nó chìm mất.

Nên: cùng `(loai, muc)` thì không thêm dòng mới. Dòng cũ được nhấc khỏi
chỗ cũ, tăng `soLan`, rồi đặt lại ở CUỐI với `stt` mới. Điều kiện dai
chiếm đúng một dòng và tự khai nó kêu bao nhiêu lần; dòng hiếm không bao
giờ bị một dòng lắm mồm đẩy ra nữa.
"""
from __future__ import annotations

import datetime as _dt
import threading
from collections import deque


def bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class Bus:
    #: Gộp một dòng lặp nếu bản cũ còn nằm trong ngần này dòng cuối.
    _GOP_TRONG = 60

    def __init__(self, tran: int = 600) -> None:
        self._d: deque = deque(maxlen=tran)
        self._khoa = threading.Lock()
        self._dem = 0

    def ghi(self, muc: str, loai: str = "tin", **kw) -> dict:
        with self._khoa:
            self._dem += 1
            e = {"stt": self._dem, "luc": bay_gio(), "loai": loai,
                 "muc": muc, **kw}
            cu = self._cu(loai, muc)
            if cu is not None:
                # Giữ lần ĐẦU tiên: biết điều kiện này bắt đầu từ lúc nào
                # quan trọng hơn biết nó vừa kêu lại lúc nãy.
                e["soLan"] = int(cu.get("soLan") or 1) + 1
                e["tuLuc"] = cu.get("tuLuc") or cu.get("luc")
                self._d.remove(cu)
            self._d.append(e)
        return e

    def _cu(self, loai: str, muc: str) -> dict | None:
        """Dòng gần nhất cùng `(loai, muc)`, hoặc None.

        Chỉ dò `_GOP_TRONG` dòng cuối. Dò cả đệm thì một câu kêu lại sau
        nửa tiếng vẫn bị gộp vào dòng cũ, và người đọc mất mất cái tin
        "nó ĐÃ IM rồi lại kêu" — tin ấy thường là tin đáng giá nhất.
        """
        n = 0
        for e in reversed(self._d):
            if e.get("loai") == loai and e.get("muc") == muc:
                return e
            n += 1
            if n >= self._GOP_TRONG:
                return None
        return None

    def gan_day(self, n: int = 120) -> list[dict]:
        with self._khoa:
            return list(self._d)[-n:]

    def tong(self) -> int:
        return self._dem


bus = Bus()
