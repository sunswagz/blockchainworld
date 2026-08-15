"""Kiểm bộ giám sát — phần khó thấy nhất: nó có BỎ CUỘC đúng lúc không.

    python dichvu/kiem-giam-sat.py

Chạy `chay-nen.py` thật, chỉ rút ngắn hằng số thời gian, trên một thư mục giả
có `run.py` chết ngay lập tức. Cái đang được gác là: cấu hình sai làm tiến trình
chết trong một giây, và nếu không có nghỉ tăng dần + điểm bỏ cuộc thì bộ giám
sát sẽ dựng lại nó hàng nghìn lượt một phút — nện API sàn và làm nóng máy suốt
đêm mà không ai hay, vì nó không hề báo lỗi ở đâu cả.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

DICHVU = Path(__file__).resolve().parent
sai = 0


def ok(m: str) -> None:
    print(f"  OK   {m}")


def bao(m: str) -> None:
    global sai
    sai += 1
    print(f"  SAI  {m}")


def nap(goc: Path):
    """Nạp chay-nen.py rồi trỏ nó vào thư mục giả (tên file có gạch nối)."""
    spec = importlib.util.spec_from_file_location("chay_nen", DICHVU / "chay-nen.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # type: ignore[union-attr]
    m.GOC = goc
    m.NHAT_KY = goc / "data" / "nhat-ky"
    m.TRANG_THAI = goc / "dichvu" / "trang-thai.json"
    return m


def dung_gia(thu_muc: Path, than: str, cong: int) -> None:
    (thu_muc / "dichvu").mkdir(parents=True, exist_ok=True)
    (thu_muc / "config.json").write_text(json.dumps({"port": cong}), encoding="utf-8")
    (thu_muc / "run.py").write_text(than, encoding="utf-8")


print("\n[1] chết nhanh liên tục thì phải BỎ CUỘC, không quay tít")
tmp = Path(tempfile.mkdtemp(prefix="kiem-gs-"))
try:
    # run.py chết ngay — mô phỏng đúng cấu hình sai.
    dung_gia(tmp, "import sys\nprint('no ra ngay')\nsys.exit(3)\n", 5199)
    m = nap(tmp)
    m.NGHI = [0.2, 0.2, 0.2]           # rút ngắn để kiểm chạy trong vài giây
    m.TOI_DA_CHET_NHANH = 4
    m.CHET_NHANH_GIAY = 30

    t0 = time.time()
    ma = m.main()
    giay = time.time() - t0

    if ma == 1:
        ok(f"bỏ cuộc và trả mã lỗi 1 sau {giay:.1f}s")
    else:
        bao(f"trả mã {ma}, mong 1 — vòng lặp không tự dừng")

    if giay > 30:
        bao(f"chạy {giay:.0f}s, quá lâu — có vẻ không đếm số lần chết nhanh")
    else:
        ok(f"dừng nhanh ({giay:.1f}s), không quay vô hạn")

    log = (tmp / "data" / "nhat-ky" / "runtime.log").read_text(encoding="utf-8")
    if "DỪNG HẲN" in log:
        ok("nhật ký có ghi rõ lý do dừng hẳn")
    else:
        bao("dừng mà không ghi lý do vào nhật ký — người dùng sẽ không biết vì sao")

    so_luot = log.count("[giám sát] lượt ")
    if so_luot == m.TOI_DA_CHET_NHANH:
        ok(f"thử đúng {so_luot} lượt rồi thôi")
    else:
        bao(f"thử {so_luot} lượt, mong {m.TOI_DA_CHET_NHANH}")

    tt = json.loads((tmp / "dichvu" / "trang-thai.json").read_text(encoding="utf-8"))
    if tt.get("dungHan") and tt.get("lyDo"):
        ok(f'trạng thái ghi dungHan kèm lý do: "{tt["lyDo"]}"')
    else:
        bao("trạng thái không ghi dungHan — trang-thai.ps1 sẽ báo là vẫn ổn")
finally:
    shutil.rmtree(tmp, ignore_errors=True)


print("\n[2] sống được một lúc rồi mới chết thì KHÔNG tính là chết nhanh")
tmp = Path(tempfile.mkdtemp(prefix="kiem-gs-"))
try:
    dung_gia(tmp, "import sys, time\ntime.sleep(1.2)\nsys.exit(1)\n", 5198)
    m = nap(tmp)
    m.NGHI = [0.2, 0.2, 0.2]
    m.TOI_DA_CHET_NHANH = 3
    m.CHET_NHANH_GIAY = 1.0      # sống 1.2s > 1.0s ⇒ coi là lành

    import threading
    kq: list = []
    th = threading.Thread(target=lambda: kq.append(m.main()), daemon=True)
    th.start()
    th.join(timeout=9)

    log_f = tmp / "data" / "nhat-ky" / "runtime.log"
    log = log_f.read_text(encoding="utf-8") if log_f.exists() else ""
    if th.is_alive() and "DỪNG HẲN" not in log:
        ok("vẫn kiên trì khởi động lại — đúng, vì đây là trục trặc chứ không phải cấu hình sai")
    else:
        bao("đã bỏ cuộc, nhưng tiến trình sống đủ lâu nên không được tính là chết nhanh")
finally:
    shutil.rmtree(tmp, ignore_errors=True)


print("\n[3] cổng đã bận thì phải thoát, không dựng bản thứ hai")
tmp = Path(tempfile.mkdtemp(prefix="kiem-gs-"))
try:
    import socket

    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    s.listen(1)
    cong_ban = s.getsockname()[1]

    dung_gia(tmp, "import sys\nsys.exit(0)\n", cong_ban)
    m = nap(tmp)
    ma = m.main()
    s.close()

    if ma == 0:
        ok(f"thấy cổng {cong_ban} đã bận nên thoát êm")
    else:
        bao(f"trả mã {ma} — hai vòng lặp cùng đặt lệnh trên một tài khoản là hỏng nặng")
    log_f = tmp / "data" / "nhat-ky" / "runtime.log"
    if log_f.exists() and "đã bận" in log_f.read_text(encoding="utf-8"):
        ok("nhật ký nói rõ vì sao thoát")
    else:
        bao("thoát mà không ghi lý do")
finally:
    shutil.rmtree(tmp, ignore_errors=True)


print("\n" + "=" * 58)
if sai:
    print(f"  {sai} phép kiểm hỏng.")
    sys.exit(1)
print("  BỘ GIÁM SÁT KHÔNG QUAY TÍT.")
print("=" * 58)
