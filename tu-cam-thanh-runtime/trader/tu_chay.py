"""Công tắc TỰ CHẠY LÚC ĐĂNG NHẬP, bật/tắt được từ trong buồng lái.

Mặc định **TẮT**, và đó là mặc định đúng chứ không phải mặc định lười: một cỗ
máy đặt lệnh tự khởi động trên một máy nhiều người dùng chung là thứ không ai
xin phép. Ai muốn nó tự chạy thì tự bật, trên đúng cái máy của mình.

Mỗi nền tảng một kiểu tự chạy, nên ở đây khai báo thẳng cái nào làm được:

    Windows   lối tắt .lnk trong thư mục Startup — không cần quyền quản trị
    Linux     systemd user unit — chưa dựng, `coThe=False` và nói rõ vì sao
    macOS     launchd plist — chưa dựng

Trả `coThe=False` kèm lời giải thích vẫn tốt hơn là giấu cái nút đi: người dùng
trên VPS cần biết vì sao nút không bấm được, chứ không phải tự hỏi nó đâu mất.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from .bus import bus
from .config import ROOT

_LAN_LNK = (os.environ.get("TCT_LAN") or "chinh").strip() or "chinh"
TEN_LNK = ("Tu Cam Thanh - runtime.lnk" if _LAN_LNK == "chinh"
           else f"Tu Cam Thanh - {_LAN_LNK}.lnk")   # ASCII: COM WScript.Shell không tạo
                                          # nổi file tên có dấu (ép về ANSI rồi
                                          # ném FileNotFoundException)
# Cờ báo bộ giám sát: đừng dựng lại. Tên mang HẬU TỐ LÀN đúng như
# `dichvu/chay-nen.py` đặt — nút "dừng hẳn" ở buồng lái làn demo mà ghi vào cờ
# của làn chính thì nó dừng nhầm bot đang giữ vị thế thật, và buồng lái vừa bấm
# thì vẫn chạy tiếp. Làn chính giữ nguyên tên cũ.
_LAN = (os.environ.get("TCT_LAN") or "chinh").strip() or "chinh"
CO_DUNG = ROOT / "dichvu" / ("dung-lai" if _LAN == "chinh" else f"dung-lai-{_LAN}")


def _startup() -> Path | None:
    if os.name != "nt":
        return None
    d = os.environ.get("APPDATA")
    if not d:
        return None
    return Path(d) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / TEN_LNK


def _pythonw() -> Path:
    """pythonw.exe cùng bản với tiến trình đang chạy (không cửa sổ)."""
    p = Path(sys.executable)
    w = p.with_name("pythonw.exe")
    return w if w.exists() else p


def _trong_worktree() -> bool:
    # Worktree là thứ tạm. Bật tự chạy trỏ vào đó thì `git worktree remove` một
    # cái là hỏng ÂM THẦM: lối tắt vẫn còn, chỉ là không còn gì để chạy.
    return "\\.claude\\worktrees\\" in str(ROOT) or "/.claude/worktrees/" in str(ROOT)


def trang_thai() -> dict:
    lnk = _startup()
    if os.name != "nt":
        return {"coThe": False, "bat": False, "heDieuHanh": os.name,
                "viSao": "Tự chạy trên Linux/macOS cần systemd user unit hoặc launchd — "
                         "chưa dựng. Trên VPS thì đó mới là cách đúng, không phải thư mục Startup."}
    if _trong_worktree():
        return {"coThe": False, "bat": False, "heDieuHanh": "nt",
                "goc": str(ROOT),
                "viSao": "Runtime đang chạy từ một git worktree — thư mục tạm sẽ bị xoá khi "
                         "xong việc, và lối tắt sẽ trỏ vào hư không mà không báo gì. "
                         "Cài từ cây chính rồi bật ở đó."}
    if lnk is None:
        return {"coThe": False, "bat": False, "heDieuHanh": "nt",
                "viSao": "không tìm được thư mục Startup (thiếu biến môi trường APPDATA)"}
    return {"coThe": True, "bat": lnk.exists(), "heDieuHanh": "nt",
            "duong": str(lnk), "goc": str(ROOT), "python": str(_pythonw())}


def dat(bat: bool) -> dict:
    """Bật/tắt tự chạy. Trả về trạng thái sau khi đổi."""
    tt = trang_thai()
    if not tt["coThe"]:
        return {**tt, "ok": False}

    lnk = Path(tt["duong"])
    if not bat:
        if lnk.exists():
            lnk.unlink()
        bus.emit("system", "tu-chay-tat", "đã TẮT tự chạy lúc đăng nhập")
        return {**trang_thai(), "ok": True}

    # Tạo .lnk qua PowerShell. Python thuần không dựng được .lnk mà không thêm
    # gói ngoài, còn PowerShell thì có sẵn ở mọi bản Windows.
    ps = (
        "$s = New-Object -ComObject WScript.Shell; "
        f"$k = $s.CreateShortcut('{lnk}'); "
        f"$k.TargetPath = '{_pythonw()}'; "
        # Lối tắt của LÀN nào thì gọi đúng làn ấy. .lnk không đặt được biến
        # môi trường, nên cờ dòng lệnh là đường duy nhất.
        "$k.Arguments = 'dichvu\\chay-nen.py"
        + ("" if _LAN_LNK == "chinh" else f" --lan {_LAN_LNK}")
        + "'; "
        f"$k.WorkingDirectory = '{ROOT}'; "
        "$k.WindowStyle = 7; "
        "$k.Description = 'Runtime giao dich Tu Cam Thanh'; "
        "$k.Save()"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if r.returncode != 0 or not lnk.exists():
        loi = (r.stderr or r.stdout or "không rõ").strip()[:300]
        bus.log("system", "tu-chay-loi", f"bật tự chạy hỏng: {loi}")
        return {**trang_thai(), "ok": False, "loi": loi}

    bus.emit("system", "tu-chay-bat", "đã BẬT tự chạy lúc đăng nhập")
    return {**trang_thai(), "ok": True}


def xin_dung() -> None:
    """Đặt cờ để bộ giám sát ĐỪNG dựng lại runtime sau khi nó thoát.

    Không có cờ này thì nút "dừng hẳn" trong buồng lái vô dụng: tiến trình chết,
    bộ giám sát làm đúng việc của nó và dựng lại ngay sau vài giây, và người
    dùng thấy như nút không có tác dụng.
    """
    CO_DUNG.parent.mkdir(parents=True, exist_ok=True)
    CO_DUNG.write_text("dung", encoding="utf-8")
    bus.emit("system", "xin-dung", "đã xin dừng hẳn — bộ giám sát sẽ không dựng lại")
