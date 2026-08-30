"""DỌN VIỆC MỒ CÔI — tiến trình con của một nghi thức đã chết, còn ghi vào kho.

    python dichvu/don-viec-mo-coi.py          xem trước, KHÔNG giết gì
    python dichvu/don-viec-mo-coi.py --giet   giết thật

CHUYỆN ĐÃ XẢY RA, và vì sao cần một công cụ chứ không phải một lệnh gõ tay

Ngày 30/08 có hai nghi thức chạy chồng (khoá liên tiến trình sinh ra để chặn
chuyện đó). Tôi dọn bằng PowerShell, khớp theo MẪU DÒNG LỆNH:

    Get-CimInstance Win32_Process | Where CommandLine -like '*do-huong*' | Stop-Process

Nó giết đúng việc mồ côi — và giết luôn việc «đo hướng» của nghi thức ĐANG chạy
hợp lệ ở làn chính. Nghi thức ấy về sau báo `ma=4294967295` và `do-huong.json`
đứng im một ngày. Không lỗi nào chỉ ra rằng chính tôi đã giết nó.

Mẫu dòng lệnh không phân biệt được hai làn, cũng không phân biệt được việc hợp
lệ với việc mồ côi. Khoá `nghi-thuc-khoa.json` thì có: nó ghi PID của việc con
ĐANG được một nghi thức sống trông coi.

LUẬT: chỉ giết tiến trình KHÔNG được khoá nào nhận. Mọi thứ khác để yên.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

GIET = "--giet" in sys.argv
NL = chr(10)

# Việc của nghi thức, nhận ra bằng tên script. Chỉ những cái này mới nằm trong
# tầm dọn — không đụng `run.py`, không đụng bộ giám sát.
VIEC = ("do-mau-gia.py", "do-khung.py", "dau-chien-luoc.py", "bo-pha.py",
        "soat-lai-bai-hoc.py", "do-huong.py", "lo-luyen.py", "ban-giao.py")


def _so_cua_moi_lan() -> list[Path]:
    """Thư mục sổ của MỌI làn — mỗi làn giữ khoá riêng."""
    ra = [GOC / "data"]
    ra += [p for p in GOC.glob("data-*") if p.is_dir() and p.name != "data"]
    return ra


def _pid_hop_le() -> set[int]:
    """PID việc con mà một khoá CÒN HIỆU LỰC đang nhận."""
    from trader import nghi_thuc as NT      # noqa: PLC0415

    ra: set[int] = set()
    for so in _so_cua_moi_lan():
        f = so / "nghi-thuc-khoa.json"
        try:
            k = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        # Khoá của một chủ đã chết thì không bảo vệ được ai — nhưng việc con của
        # nó thì vẫn có thể đang chạy và vẫn đang ghi kho. Đó CHÍNH LÀ mồ côi.
        if NT._con_song(k.get("pid")) and k.get("conPid"):
            ra.add(int(k["conPid"]))
    return ra


def _dang_chay() -> list[tuple[int, str]]:
    if sys.platform != "win32":
        return []
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
         "ForEach-Object { $_.ProcessId.ToString() + '|' + $_.CommandLine }"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    ra = []
    for dong in (r.stdout or "").splitlines():
        if "|" not in dong:
            continue
        pid, _, cmd = dong.partition("|")
        try:
            ra.append((int(pid.strip()), cmd))
        except ValueError:
            continue
    return ra


def main() -> int:
    hop_le = _pid_hop_le()
    toi = os.getpid()
    mo_coi = [(p, c) for p, c in _dang_chay()
              if p not in hop_le and p != toi and any(v in c for v in VIEC)]

    print(f"{NL}  khoá đang nhận việc con: {sorted(hop_le) or 'không có'}")
    if not mo_coi:
        print("  không có việc mồ côi nào." + NL)
        return 0

    print(f"  {len(mo_coi)} việc MỒ CÔI (không khoá nào nhận):")
    for p, c in mo_coi:
        ten = next((v for v in VIEC if v in c), "?")
        print(f"    pid {p:>6}  {ten}")
    if not GIET:
        print(f"{NL}  (xem trước — thêm --giet để giết){NL}")
        return 0

    for p, _ in mo_coi:
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"Stop-Process -Id {p} -Force -ErrorAction SilentlyContinue"],
                       capture_output=True)
        print(f"    đã giết pid {p}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
