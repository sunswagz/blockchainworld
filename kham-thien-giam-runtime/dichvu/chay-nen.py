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


def main() -> int:
    _dat_nhat_ky()
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
