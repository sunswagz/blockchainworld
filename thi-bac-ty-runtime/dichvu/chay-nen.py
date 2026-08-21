"""Chạy runtime ở chế độ nền — không cửa sổ, có nhật ký xoay vòng.

    pythonw dichvu/chay-nen.py

Khác `run.py` ở ba chỗ, và cả ba đều cần cho một tiến trình sống lâu ngày:

1. **Nhật ký xoay vòng.** Nhịp 30 giây × 4 cảng × 5 mã đẻ ra rất nhiều dòng.
   Không xoay thì sau vài tuần file log lớn hơn cả băng, và lúc cần đọc thì
   không mở nổi.

2. **Ghi PID.** Không có nó thì `dung.ps1` phải đoán tiến trình nào là của
   mình — và trên máy có ba runtime Python cùng chạy thì đoán sai nghĩa là
   giết nhầm cung khác.

3. **Không in ra buồng lái.** `run.py` in địa chỉ cho người đọc; ở chế độ
   nền thì không có ai đọc.

Chạy bằng `pythonw.exe` (không phải `python.exe`) để không có cửa sổ đen nào
bật lên. Hệ quả: **mọi lỗi chỉ còn nằm trong nhật ký**, nên nhật ký là thứ
duy nhất nói được vì sao nó chết.

## Vì sao cung này cần chạy nền hơn hai cung kia

Thị Bạc Ty không giao dịch — nó **học**. Và tầng học chỉ chạy được khi có
băng: `chay_lai.py` cần đủ khung để nhìn TỚI TRƯỚC qua cả cửa sổ giữ, còn
`tien_hoa.py` đòi ≥30 cơ hội hậu kiểm được ở cả hai bên trước khi dám nhận
một thay đổi.

Với nhịp 30 giây và cửa sổ giữ 8 giờ, một phiên chạy tay vài chục phút
**không sinh ra một mẫu hậu kiểm nào** — băng chưa phủ hết cửa sổ, nên mọi
cơ hội đều rơi vào nhánh "không đo được". Bảng sẽ xanh, sổ tiến hoá sẽ ghi
"chưa đủ mẫu", và không có gì sai cả; chỉ là chưa có gì để học.
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


def _nhat_ky() -> None:
    thu_muc = DATA_DIR / "nhat-ky"
    thu_muc.mkdir(parents=True, exist_ok=True)
    tay = logging.handlers.RotatingFileHandler(
        thu_muc / "runtime.log", maxBytes=5_000_000, backupCount=5,
        encoding="utf-8")
    tay.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s %(message)s"))
    goc = logging.getLogger()
    goc.setLevel(logging.INFO)
    goc.addHandler(tay)


def main() -> int:
    _nhat_ky()
    log = logging.getLogger("chay-nen")

    # Ghi PID TRƯỚC khi khởi động uvicorn: nếu uvicorn chết ngay vì cổng bận
    # thì vẫn còn dấu vết ai đã thử chạy.
    try:
        PID.write_text(str(os.getpid()), encoding="utf-8")
    except OSError as e:
        log.warning("không ghi được pid.txt: %s", e)

    port = CONFIG["port"]
    log.info("Thị Bạc Ty chạy nền · cổng %s · chế độ %s · nhịp %ss",
             port, che_hieu_luc(), CONFIG["nhipGiay"])
    log.info("băng ghi: %s · giữ %s ngày",
             "BẬT" if (CONFIG.get("bang") or {}).get("ghi", True) else "TẮT",
             (CONFIG.get("bang") or {}).get("ngayGiuLai", 30))

    try:
        import uvicorn
        uvicorn.run("bac.server:app", host="127.0.0.1", port=port,
                    log_level="warning")
    except Exception:                                   # noqa: BLE001
        log.exception("runtime chết")
        return 1
    finally:
        try:
            PID.unlink(missing_ok=True)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
