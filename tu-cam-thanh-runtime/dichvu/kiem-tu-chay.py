"""Kiểm công tắc tự chạy và cờ dừng hẳn.

    python dichvu/kiem-tu-chay.py

Hai thứ được gác ở đây, và cả hai đều là chuyện "im lặng làm sai":

1. **Công tắc phải thật sự tạo/xoá lối tắt.** Nút bấm xong đổi màu mà file
   không đổi là thứ người dùng chỉ phát hiện ra sau vài lần khởi động máy —
   lúc đó họ đã tin là mình bật rồi.

2. **Không được bật khi runtime chạy từ worktree.** Lối tắt sẽ trỏ vào một thư
   mục sắp bị `git worktree remove` xoá, và khi đó nó hỏng mà không báo gì: lối
   tắt vẫn nằm trong Startup, vẫn chạy lúc đăng nhập, chỉ là chẳng có gì chạy.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

from trader import tu_chay  # noqa: E402

sai = 0


def ok(m: str) -> None:
    print(f"  OK   {m}")


def bao(m: str) -> None:
    global sai
    sai += 1
    print(f"  SAI  {m}")


print("\n[1] đọc được trạng thái")
tt = tu_chay.trang_thai()
for k in ("coThe", "bat", "heDieuHanh"):
    if k not in tt:
        bao(f"trạng thái thiếu trường {k}")
if "coThe" in tt and "bat" in tt:
    ok(f'coThe={tt["coThe"]} · bat={tt["bat"]} · {tt.get("viSao", "")}'.rstrip(" ·"))

if os.name != "nt":
    print("\n  —    không phải Windows, bỏ qua phần lối tắt")
elif not tt["coThe"]:
    print(f'\n  —    không bật được ở đây: {tt.get("viSao")}')
    print("       (đúng nếu đang chạy từ worktree — đó chính là điều cần chặn)")
else:
    lnk = Path(tt["duong"])
    ban_dau = lnk.exists()

    print("\n[2] bật thì phải TẠO RA lối tắt thật")
    r = tu_chay.dat(True)
    if r.get("ok") and lnk.exists() and r["bat"]:
        ok(f"đã tạo {lnk.name}")
    else:
        bao(f'bật xong mà file không có: ok={r.get("ok")} loi={r.get("loi")}')

    print("\n[3] lối tắt phải trỏ đúng chỗ")
    if lnk.exists():
        try:
            import subprocess

            ps = (f"$s=New-Object -ComObject WScript.Shell; $k=$s.CreateShortcut('{lnk}'); "
                  "Write-Output $k.TargetPath; Write-Output $k.Arguments; "
                  "Write-Output $k.WorkingDirectory")
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                                 capture_output=True, text=True).stdout.strip().splitlines()
            dich, tham, thu_muc = (out + ["", "", ""])[:3]
            if "pythonw" in dich.lower():
                ok(f"trỏ tới {Path(dich).name}")
            else:
                bao(f"trỏ tới {dich} — mong pythonw.exe (python.exe sẽ nháy cửa sổ đen)")
            ok("tham số: " + tham) if "chay-nen.py" in tham else bao(f"tham số lạ: {tham}")
            if Path(thu_muc) == GOC:
                ok("thư mục làm việc đúng")
            else:
                bao(f"thư mục làm việc {thu_muc} ≠ {GOC}")
        except Exception as e:  # noqa: BLE001
            bao(f"không đọc lại được lối tắt: {e}")

    print("\n[4] tắt thì phải XOÁ thật")
    r = tu_chay.dat(False)
    if r.get("ok") and not lnk.exists() and not r["bat"]:
        ok("đã xoá")
    else:
        bao(f'tắt xong mà file vẫn còn: ok={r.get("ok")} tồn tại={lnk.exists()}')

    print("\n[5] tắt hai lần liên tiếp không được nổ")
    try:
        tu_chay.dat(False)
        ok("tắt lần hai vẫn êm")
    except Exception as e:  # noqa: BLE001
        bao(f"tắt lần hai ném lỗi: {type(e).__name__}: {e}")

    # Trả lại đúng như lúc bắt đầu — phép kiểm không được đổi cấu hình của máy.
    if ban_dau:
        tu_chay.dat(True)
        print("       (đã khôi phục trạng thái ban đầu: BẬT)")


print("\n[6] cờ dừng hẳn")
co = tu_chay.CO_DUNG
da_co = co.exists()
tu_chay.xin_dung()
if co.exists():
    ok(f"xin_dung() tạo cờ {co.name}")
else:
    bao("xin_dung() không tạo được cờ — nút tắt hẳn sẽ vô dụng, giám sát dựng lại ngay")
if not da_co:
    co.unlink(missing_ok=True)

print("\n[7] bộ giám sát phải ĐỌC cờ đó")
# Hai file phải trỏ tới cùng một đường dẫn. Lệch nhau thì nút tắt hẳn im lặng
# mất tác dụng: buồng lái đặt cờ ở một chỗ, giám sát ngó một chỗ khác.
src = (GOC / "dichvu" / "chay-nen.py").read_text(encoding="utf-8")
if 'CO_DUNG = GOC / "dichvu" / "dung-lai"' in src and "CO_DUNG.exists()" in src:
    ok("chay-nen.py trỏ cùng đường dẫn và có kiểm cờ")
else:
    bao("chay-nen.py không kiểm cờ dừng, hoặc trỏ đường dẫn khác với tu_chay.py")

print("\n" + "=" * 58)
if sai:
    print(f"  {sai} phép kiểm hỏng.")
    sys.exit(1)
print("  CÔNG TẮC TỰ CHẠY ĐÚNG.")
print("=" * 58)
