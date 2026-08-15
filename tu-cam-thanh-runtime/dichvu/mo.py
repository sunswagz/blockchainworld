"""Mở buồng lái. Chưa chạy thì bật lên rồi chờ, xong mới mở trình duyệt.

Lối tắt ngoài desktop trỏ vào đây qua `pythonw.exe` nên không có cửa sổ nào
nháy lên. Mở thẳng URL thì nhanh hơn, nhưng lúc dịch vụ chưa kịp dậy — vừa khởi
động máy, hoặc vừa bị dừng — người bấm sẽ gặp trang "không kết nối được" và
không biết phải làm gì tiếp. Bấm một lối tắt thì phải ra buồng lái, chấm hết.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent


def cong() -> int:
    try:
        return json.loads((GOC / "config.json").read_text(encoding="utf-8-sig"))["port"]
    except Exception:  # noqa: BLE001
        return 5182


def song(c: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.8)
        return s.connect_ex(("127.0.0.1", c)) == 0


def main() -> int:
    c = cong()
    if not song(c):
        # Gọi thẳng bộ giám sát, không qua Task Scheduler: dịch vụ lịch tác vụ
        # của Windows có thể đang tắt (đúng trường hợp máy này), và khi đó mọi
        # đường qua nó đều hỏng với thông báo nghe như lỗi cú pháp.
        # `sys.executable` chính là pythonw.exe đang chạy file này, nên chắc
        # chắn cùng một bản Python với lối tắt khởi động.
        subprocess.Popen([sys.executable, "dichvu/chay-nen.py"], cwd=str(GOC),
                         creationflags=subprocess.CREATE_NO_WINDOW)
        # Runtime mất ~12 giây để nạp nến và mở cổng. Chờ tới 45 giây rồi vẫn
        # mở trình duyệt: thà để người dùng thấy trang lỗi thật còn hơn lối tắt
        # bấm vào không có phản ứng gì.
        for _ in range(45):
            if song(c):
                break
            time.sleep(1)
    webbrowser.open(f"http://localhost:{c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
