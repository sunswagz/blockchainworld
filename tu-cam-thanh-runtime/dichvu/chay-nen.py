"""Bộ giám sát — giữ runtime sống, ghi log xoay vòng, không hiện cửa sổ nào.

Task Scheduler gọi file này bằng `pythonw.exe` (không console), rồi nó tự sinh
`run.py` làm tiến trình con và trông chừng.

Vì sao cần một tầng riêng thay vì để Task Scheduler tự khởi động lại:

1. **Task Scheduler chỉ coi là hỏng khi mã thoát khác 0.** Uvicorn chết vì cổng
   bận vẫn có thể thoát 0, và khi đó không có gì khởi động lại cả — dịch vụ chết
   im lặng, đúng kiểu hỏng tệ nhất.

2. **Phải có nghỉ tăng dần và có điểm bỏ cuộc.** Cấu hình sai làm tiến trình
   chết trong một giây; khởi động lại ngay lập tức là một vòng quay tít, ăn CPU
   và nện API sàn hàng nghìn lượt một phút. Ở đây: chết nhanh thì giãn dần
   5→10→30→60→300 giây, và chết nhanh 10 lần liên tiếp thì DỪNG HẲN kèm một
   dòng nói rõ vì sao. Một dịch vụ dừng và giải thích thì sửa được; một dịch vụ
   quay tít thì chỉ làm máy nóng.

3. **Log phải xoay vòng liên tục.** Chuyển hướng stdout thẳng ra file thì sau
   vài tuần chạy nó thành file vài GB. Ở đây stdout của con được đọc từng dòng
   rồi ghi qua `RotatingFileHandler`, nên nó xoay ngay cả khi tiến trình con
   chạy liên tục hàng tháng.
"""
from __future__ import annotations

import json
import logging
import logging.handlers
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent      # tu-cam-thanh-runtime/
NHAT_KY = GOC / "data" / "nhat-ky"
TRANG_THAI = GOC / "dichvu" / "trang-thai.json"
CO_DUNG = GOC / "dichvu" / "dung-lai"             # buồng lái xin dừng hẳn

CHET_NHANH_GIAY = 30          # sống ngắn hơn ngần này thì coi là chết nhanh
NGHI = [5, 10, 30, 60, 120, 300]
TOI_DA_CHET_NHANH = 10


def _log() -> logging.Logger:
    NHAT_KY.mkdir(parents=True, exist_ok=True)
    lg = logging.getLogger("tct")
    lg.setLevel(logging.INFO)
    h = logging.handlers.RotatingFileHandler(
        NHAT_KY / "runtime.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%d %H:%M:%S"))
    lg.addHandler(h)
    return lg


def _cong() -> int:
    try:
        return json.loads((GOC / "config.json").read_text(encoding="utf-8-sig"))["port"]
    except Exception:  # noqa: BLE001
        return 5182


def _dang_ban(cong: int) -> bool:
    with socket.socket() as s:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", cong)) == 0


def _ghi_trang_thai(**kw) -> None:
    TRANG_THAI.parent.mkdir(parents=True, exist_ok=True)
    TRANG_THAI.write_text(json.dumps(kw, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> int:
    lg = _log()
    cong = _cong()

    # Một bản một lúc. Cổng đã bận nghĩa là đã có runtime chạy — dựng thêm bản
    # nữa thì hai vòng lặp cùng đặt lệnh trên một tài khoản.
    if _dang_ban(cong):
        lg.info(f"[giám sát] cổng {cong} đã bận — đã có bản đang chạy, thoát")
        return 0

    py = Path(sys.executable)
    # pythonw.exe không có console; tiến trình con cần python.exe để stdout chảy
    # được vào pipe. Cùng thư mục nên chỉ đổi tên file.
    py_con = py.with_name("python.exe") if py.name.lower() == "pythonw.exe" else py

    moi = os.environ.copy()
    # Không có hai dòng này thì tiếng Việt trong log thành ký tự vỡ trên Windows
    # — console mặc định là cp1252, và log là thứ người ta chỉ đọc lúc đang hỏng.
    moi["PYTHONUTF8"] = "1"
    moi["PYTHONIOENCODING"] = "utf-8"

    # Cờ dừng còn sót từ lượt trước phải xoá trước khi chạy, nếu không lượt này
    # vừa lên đã tự tắt — và trông y hệt như runtime chết ngay khi khởi động.
    CO_DUNG.unlink(missing_ok=True)

    lg.info("=" * 62)
    lg.info(f"[giám sát] bắt đầu · {GOC} · cổng {cong} · pid {os.getpid()}")

    chet_nhanh = 0
    lan = 0
    while True:
        lan += 1
        t0 = time.time()
        try:
            con = subprocess.Popen(
                [str(py_con), "run.py"], cwd=str(GOC), env=moi,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as e:  # noqa: BLE001
            lg.info(f"[giám sát] không sinh được tiến trình con: {e}")
            return 1

        _ghi_trang_thai(giamSatPid=os.getpid(), conPid=con.pid, cong=cong,
                        batDau=time.time(), lanChay=lan, goc=str(GOC))
        lg.info(f"[giám sát] lượt {lan}: runtime pid {con.pid}")

        # Đọc từng dòng cho tới khi pipe đóng = tiến trình con thoát. Nhờ đi qua
        # đây, log xoay vòng liên tục thay vì chỉ xoay lúc khởi động lại.
        try:
            for dong in con.stdout:  # type: ignore[union-attr]
                d = dong.rstrip()
                if d:
                    lg.info(d)
        except Exception as e:  # noqa: BLE001
            lg.info(f"[giám sát] lỗi khi đọc log con: {e}")

        ma = con.wait()
        song = time.time() - t0
        lg.info(f"[giám sát] runtime thoát mã {ma} sau {song:.0f}s")

        # Buồng lái xin dừng hẳn: nghỉ, đừng dựng lại. Không kiểm cờ này thì nút
        # "dừng hẳn" thành vô dụng — tiến trình chết, bộ giám sát làm đúng việc
        # của nó và dựng lại sau vài giây, người dùng tưởng nút hỏng.
        if CO_DUNG.exists():
            CO_DUNG.unlink(missing_ok=True)
            lg.info("[giám sát] buồng lái xin dừng hẳn — nghỉ, không dựng lại")
            _ghi_trang_thai(giamSatPid=None, conPid=None, cong=cong,
                            dungTheoYeuCau=True, luc=time.time(), goc=str(GOC))
            return 0

        if song >= CHET_NHANH_GIAY:
            chet_nhanh = 0            # sống được một lúc = coi như lành
        else:
            chet_nhanh += 1

        if chet_nhanh >= TOI_DA_CHET_NHANH:
            lg.info(f"[giám sát] DỪNG HẲN — chết nhanh {chet_nhanh} lần liên tiếp. "
                    f"Đây gần như luôn là lỗi cấu hình chứ không phải trục trặc "
                    f"tạm thời: xem mấy dòng ngay trên đây, sửa, rồi chạy "
                    f"dichvu\\bat.ps1. Cứ khởi động lại tiếp chỉ nện API sàn "
                    f"và làm nóng máy.")
            _ghi_trang_thai(giamSatPid=os.getpid(), conPid=None, cong=cong,
                            dungHan=True, lyDo=f"chết nhanh {chet_nhanh} lần liên tiếp",
                            luc=time.time(), goc=str(GOC))
            return 1

        nghi = NGHI[min(chet_nhanh, len(NGHI) - 1)] if chet_nhanh else 3
        lg.info(f"[giám sát] khởi động lại sau {nghi}s"
                + (f" (chết nhanh {chet_nhanh}/{TOI_DA_CHET_NHANH})" if chet_nhanh else ""))
        time.sleep(nghi)


if __name__ == "__main__":
    sys.exit(main())
