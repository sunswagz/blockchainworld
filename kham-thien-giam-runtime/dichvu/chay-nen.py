"""Chạy runtime ở chế độ nền — không cửa sổ, có nhật ký xoay vòng.

    pythonw dichvu/chay-nen.py

Khác `run.py` ở ba chỗ, và cả ba đều cần cho một tiến trình sống lâu ngày:

1. **Nhật ký xoay vòng.** Một runtime chạy nhịp 2 giây sẽ đẻ ra rất nhiều
   dòng. Không xoay thì sau vài tuần file log lớn hơn cả dữ liệu, và lúc
   cần đọc thì không mở nổi.

2. **Ghi PID.** Không có nó thì `dung.ps1` phải đoán tiến trình nào là của
   mình — và trên máy có nhiều Python thì đoán sai nghĩa là giết nhầm.

3. **Không mở trình duyệt.** `run.py` in ra địa chỉ buồng lái cho người
   đọc; ở chế độ nền thì không có ai đọc.

Chạy bằng `pythonw.exe` (không phải `python.exe`) để không có cửa sổ đen
nào bật lên. Hệ quả: mọi lỗi chỉ còn nằm trong nhật ký, nên nhật ký là thứ
duy nhất nói được vì sao nó chết.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

NHAT_KY = GOC / "data" / "nhat-ky"
NHAT_KY.mkdir(parents=True, exist_ok=True)
PID = GOC / "dichvu" / "pid.txt"


def _dat_nhat_ky() -> None:
    tay = logging.handlers.RotatingFileHandler(
        NHAT_KY / "runtime.log", maxBytes=8 * 1024 * 1024, backupCount=5,
        encoding="utf-8")
    tay.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s"))
    goc = logging.getLogger()
    goc.setLevel(logging.INFO)
    goc.addHandler(tay)

    # `httpx` ghi MỖI lời gọi ở mức INFO. Nhịp 2 giây × 2 market = hơn
    # 86.000 dòng mỗi ngày, và chúng nhấn chìm đúng những dòng đáng đọc:
    # vòng tiến hoá nhận hay trả lại, cầu dao ngắt, khung bị bỏ qua vì sao.
    #
    # Một nhật ký toàn tiếng ồn thì tương đương không có nhật ký — người ta
    # ngừng mở nó, và lần nó ghi thứ quan trọng cũng không ai đọc.
    for ten in ("httpx", "httpcore", "websockets", "uvicorn.access"):
        logging.getLogger(ten).setLevel(logging.WARNING)

    # stdout/stderr của tiến trình nền không đi đâu cả khi chạy bằng
    # pythonw. Chuyển chúng vào nhật ký, nếu không thì một traceback lúc
    # khởi động sẽ biến mất hoàn toàn và tiến trình chỉ đơn giản là không
    # lên — không dấu vết nào để lần.
    class _Ong:
        def __init__(self, muc):
            self.muc = muc
            self._dem = ""

        def write(self, s):
            self._dem += s
            while "\n" in self._dem:
                d, self._dem = self._dem.split("\n", 1)
                if d.strip():
                    logging.log(self.muc, d.rstrip())

        def flush(self):
            if self._dem.strip():
                logging.log(self.muc, self._dem.rstrip())
            self._dem = ""

        # uvicorn hỏi hai thứ này khi dựng cấu hình log của nó. Thiếu
        # `isatty` thì nó ném `ValueError: Unable to configure formatter
        # 'default'` — một câu không hề nhắc tới stdout, nên rất khó lần
        # ra rằng nguyên nhân là lớp chuyển hướng này.
        def isatty(self):
            return False

        def fileno(self):
            raise OSError("luồng này chỉ đi vào nhật ký, không có fd")

    sys.stdout = _Ong(logging.INFO)
    sys.stderr = _Ong(logging.ERROR)


def dang_chay() -> int | None:
    """PID của bản ĐANG chạy, hoặc None. Đọc `pid.txt` rồi KIỂM LẠI.

    `pid.txt` một mình không đủ: tiến trình bị `Stop-Process` thì khối
    `finally` không chạy, nên file ở lại trỏ vào một PID đã chết. Tin nó
    là từ chối khởi động mãi mãi.

    Nên kiểm cả hai vế — PID còn sống, VÀ nó đúng là bản này chứ không
    phải một tiến trình khác vô tình trùng số. Trên Windows số PID được
    dùng lại rất nhanh.
    """
    try:
        so = int(PID.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    if so == os.getpid():
        return None
    try:
        import psutil                                    # noqa: F401
    except ImportError:
        psutil = None
    if psutil is not None:
        try:
            tt = psutil.Process(so)
            if "chay-nen" in " ".join(tt.cmdline()):
                return so
        except Exception:                                # noqa: BLE001
            return None
        return None
    # Không có psutil thì hỏi hệ điều hành. Thà bỏ sót còn hơn chặn nhầm:
    # không chắc chắn thì cho chạy, vì chặn nhầm là runtime không lên.
    try:
        import subprocess
        r = subprocess.run(
            ["tasklist", "/FI", f"PID eq {so}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10)
        dong = (r.stdout or "").strip()
        return so if dong and "pythonw" in dong.lower() else None
    except Exception:                                    # noqa: BLE001
        return None


def main() -> int:
    _dat_nhat_ky()

    # ── MỘT bản, không hơn ────────────────────────────────────────────
    #
    # `pid.txt` đã có từ đầu nhưng chưa ai ĐỌC nó. Hệ quả đo được ngày
    # 30/08/2026: ba tiến trình `chay-nen.py` cùng sống, một từ 28/08.
    # Hai bản thừa nằm ở đúng một luồng, 2,4 MB, 0,2–0,6 giây CPU trong
    # hai ngày — chúng in xong biểu ngữ khởi động rồi treo, không phục
    # vụ gì, không giữ cổng, không ghi gì.
    #
    # Cái giá không phải là tài nguyên mà là NHẬT KÝ: mỗi lần bật thừa
    # để lại đúng ba dòng "chạy nền, PID x / chế độ / vòng tiến hoá" rồi
    # im. Đọc log thấy 55 lượt khởi động trong một ngày và không một
    # dòng lỗi nào — trông y hệt một cỗ máy đang sập rồi tự dậy liên
    # tục. Mất hơn một tiếng mới lần ra rằng nó không hề sập.
    #
    # Một chế độ hỏng mà TRÔNG như chế độ hỏng khác thì đắt hơn nhiều so
    # với chính nó.
    cu = dang_chay()
    if cu is not None:
        logging.warning("đã có một bản đang chạy (PID %d) — bản này thoát. "
                        "Muốn thay thì dừng bản kia trước.", cu)
        return 3

    PID.write_text(str(os.getpid()), encoding="utf-8")
    logging.info("=" * 70)
    logging.info("Khâm Thiên Giám — chạy nền, PID %d", os.getpid())

    try:
        import uvicorn
        from kham.config import CONFIG, che_hieu_luc
        logging.info("chế độ hiệu lực: %s · cổng %d",
                     che_hieu_luc(), CONFIG["port"])
        th = CONFIG.get("tienHoa") or {}
        logging.info("vòng tiến hoá: %s, mỗi ngày sau %02d:00 UTC",
                     "BẬT" if th.get("bat", True) else "tắt", th.get("gioUTC", 2))
        # `log_config=None`: đừng để uvicorn dựng lại logging. Ở đây đã
        # có handler xoay vòng riêng, và để nó cấu hình lại là mất luôn
        # phần xoay vòng — file log lớn dần tới lúc không mở nổi.
        uvicorn.run("kham.server:app", host="127.0.0.1",
                    port=CONFIG["port"], log_level="warning", log_config=None)
    except OSError as e:
        # Cổng bận là ca RIÊNG, và phải đọc ra được ngay từ dòng đầu.
        # Gộp nó vào "runtime chết" là giấu nguyên nhân duy nhất mà
        # người vận hành sửa được trong một câu lệnh.
        logging.error("KHÔNG chiếm được cổng %s: %s. Nhiều khả năng đã có "
                      "một bản khác đang nghe ở đó.", CONFIG.get("port"), e)
        return 2
    except Exception:                                   # noqa: BLE001
        logging.exception("runtime chết")
        return 1
    finally:
        try:
            PID.unlink(missing_ok=True)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
