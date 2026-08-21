"""Chạy runtime ở chế độ nền — không cửa sổ, có nhật ký xoay vòng.

    pythonw dichvu/chay-nen.py
    powershell -ExecutionPolicy Bypass -File dichvu\\bat.ps1

Khác `run.py` ở bốn chỗ, và cả bốn đều cần cho một tiến trình sống lâu ngày.

**1. Nhật ký xoay vòng.** Nhịp 30 giây × 4 cảng × 5 mã đẻ ra rất nhiều dòng.
Không xoay thì sau vài tuần file log lớn hơn cả băng, và lúc cần đọc thì
không mở nổi.

**2. Ghi PID.** Không có nó thì `dung.ps1` phải đoán tiến trình nào là của
mình — và trên máy có BA runtime Python cùng chạy thì đoán sai nghĩa là giết
nhầm cung khác.

**3. Chuyển `stdout`/`stderr` vào nhật ký.** `pythonw` không có luồng ra:
`sys.stdout` là `None`. Không chuyển hướng thì một traceback lúc khởi động
biến mất hoàn toàn và tiến trình chỉ đơn giản là **không lên** — không dấu
vết nào để lần.

**4. `log_config=None` cho uvicorn.** Để nó tự dựng lại logging là mất luôn
phần xoay vòng ở trên; file log lớn dần tới lúc không mở nổi.

## Cái bẫy `isatty` — đã cắn thật ngay lượt chạy đầu

Bản đầu của file này không có mục 3, và uvicorn chết ngay lúc dựng cấu hình
log của nó:

    AttributeError: 'NoneType' object has no attribute 'isatty'
    ValueError: Unable to configure formatter 'default'

Câu lỗi cuối **không hề nhắc tới stdout**, nên rất khó lần ra. Và vì chạy
bằng `pythonw`, nó cũng không hiện ra màn hình — chỉ có nhật ký nói được.
Đúng bẫy đã ghi sẵn ở `kham-thien-giam-runtime/dichvu/chay-nen.py`.

Nên lớp `_Ong` bên dưới phải có CẢ `isatty()` lẫn `fileno()`: uvicorn hỏi cả
hai khi dựng formatter.

## Vì sao cung này cần chạy nền hơn hai cung kia

Thị Bạc Ty không giao dịch — nó **học**. Tầng học chỉ chạy được khi có băng:
`chay_lai.py` cần đủ khung để nhìn TỚI TRƯỚC qua cả cửa sổ giữ, còn
`tien_hoa.py` đòi ≥30 cơ hội hậu kiểm được ở cả hai bên trước khi dám nhận
một thay đổi.

Với nhịp 30 giây và cửa sổ giữ 8 giờ, một phiên chạy tay vài chục phút
**không sinh ra một mẫu hậu kiểm nào** — băng chưa phủ hết cửa sổ, nên mọi
cơ hội rơi vào nhánh "không đo được". Bảng sẽ xanh, sổ tiến hoá ghi "chưa đủ
mẫu", và không có gì sai cả; chỉ là chưa có gì để học.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import bac  # noqa: F401,E402  — lớp ép UTF-8 cho console Windows

from bac.config import CONFIG, DATA_DIR, che_hieu_luc  # noqa: E402

PID = Path(__file__).resolve().parent / "pid.txt"


def _dat_nhat_ky() -> None:
    thu_muc = DATA_DIR / "nhat-ky"
    thu_muc.mkdir(parents=True, exist_ok=True)
    tay = logging.handlers.RotatingFileHandler(
        thu_muc / "runtime.log", maxBytes=8 * 1024 * 1024, backupCount=5,
        encoding="utf-8")
    tay.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s"))
    goc = logging.getLogger()
    goc.setLevel(logging.INFO)
    goc.addHandler(tay)

    # `httpx` ghi MỖI lời gọi ở mức INFO. Nhịp 30 giây × 4 cảng là hơn 11.000
    # dòng mỗi ngày, và chúng nhấn chìm đúng những dòng đáng đọc: cảng nào
    # chết, đồng hồ lệch bao nhiêu, vòng tiến hoá nhận hay trả lại.
    #
    # Một nhật ký toàn tiếng ồn thì tương đương không có nhật ký.
    for ten in ("httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(ten).setLevel(logging.WARNING)

    class _Ong:
        """Ống dẫn `stdout`/`stderr` vào nhật ký. Xem docstring đầu file."""

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

        # uvicorn hỏi CẢ HAI thứ này khi dựng cấu hình log. Thiếu `isatty`
        # thì nó ném `ValueError: Unable to configure formatter 'default'` —
        # một câu không hề nhắc tới stdout, nên rất khó lần ra.
        def isatty(self):
            return False

        def fileno(self):
            raise OSError("luồng này chỉ đi vào nhật ký, không có fd")

    sys.stdout = _Ong(logging.INFO)
    sys.stderr = _Ong(logging.ERROR)


def main() -> int:
    _dat_nhat_ky()

    # Ghi PID TRƯỚC khi khởi động uvicorn: nếu uvicorn chết ngay vì cổng bận
    # thì vẫn còn dấu vết ai đã thử chạy.
    try:
        PID.write_text(str(os.getpid()), encoding="utf-8")
    except OSError as e:
        logging.warning("không ghi được pid.txt: %s", e)

    port = CONFIG["port"]
    b = CONFIG.get("bang") or {}
    logging.info("Thị Bạc Ty chạy nền · cổng %s · chế độ %s · nhịp %ss",
                 port, che_hieu_luc(), CONFIG["nhipGiay"])
    logging.info("băng ghi: %s · giữ %s ngày · cửa sổ giữ %sh",
                 "BẬT" if b.get("ghi", True) else "TẮT",
                 b.get("ngayGiuLai", 30), CONFIG["quet"]["giuGio"])

    try:
        import uvicorn
        # `log_config=None`: đừng để uvicorn dựng lại logging. Ở đây đã có
        # handler xoay vòng riêng, và để nó cấu hình lại là mất luôn phần
        # xoay vòng — file log lớn dần tới lúc không mở nổi.
        uvicorn.run("bac.server:app", host="127.0.0.1", port=port,
                    log_level="warning", log_config=None)
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
