"""Người canh gác — dựng runtime dậy khi nó chết, và GHI LẠI mỗi lần.

    pythonw dichvu/canh-gac.py

## Vì sao cần, đo được chứ không phỏng đoán

`chay-nen.py` gọi thẳng `uvicorn.run()`. Không có vòng nào bọc ngoài,
nên tiến trình chết là hết — không ai dựng lại.

Đo ngày 02/09/2026: runtime khởi động lần cuối 30/08 lúc 19:04, còn ghi
dữ liệu tới 23:44 cùng ngày, rồi **chết và nằm im BA NGÀY**. Máy không
hề khởi động lại (chạy liên tục 129 giờ), nên nó không mất theo máy —
nó tự chết. Nhật ký không có một dòng lỗi nào: dòng cuối là biểu ngữ
khởi động.

Ba ngày ấy mất những gì:

    · không vòng tiến hoá ngày nào (02:00 UTC × 3)
    · không dựng lại sổ hiệu chỉnh
    · không ghi thêm một khung băng nào
    · buồng lái tắt, trang tĩnh đứng ở lát cắt cũ

Và không có gì báo. Một cỗ máy chết im lặng thì không phân biệt được
với một cỗ máy đang chạy mà chợ vắng.

## Nó KHÔNG chữa nguyên nhân, và đừng giả vờ là có

Người canh gác dựng lại, không sửa. Nhưng nó biến một cái chết IM LẶNG
thành một dòng ghi có giờ, có số lần — tức biến "không biết gì" thành
"biết nó chết lúc mấy giờ, bao lâu một lần". Đó là điều kiện để lần sau
tìm ra nguyên nhân.

## Ba chỗ dễ làm sai, đã tránh

1. **Đừng hỏi `pid.txt`.** File ấy ở lại sau khi tiến trình bị giết
   (`finally` không chạy), nên nó nói "đang chạy" về một PID đã chết.
   Hỏi CỔNG: cổng trả lời thì runtime sống, dứt khoát.
2. **Đừng dựng lại ngay tức khắc mãi.** Nếu nó chết vì một lỗi khởi
   động thì vòng dựng-chết-dựng quay tít và nhật ký thành rác. Lùi dần
   tới trần, và trần đủ ngắn để một cái chết thật vẫn được vá trong
   vài phút.
3. **Người canh gác cũng phải MỘT bản.** Hai người canh cùng dựng thì
   bản thứ hai của runtime thoát mã 3 (khoá một-bản của `chay-nen.py`)
   — vô hại nhưng làm nhật ký khó đọc. Khoá bằng chính cổng canh gác.
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
import urllib.error
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

NHAT_KY = GOC / "data" / "nhat-ky"
NHAT_KY.mkdir(parents=True, exist_ok=True)

#: Cổng canh gác GIỮ CHỖ — không phục vụ gì, chỉ để hai người canh
#: không cùng chạy. Rẻ hơn một file khoá và tự dọn khi tiến trình chết.
CONG_CANH = 5187

NHIP_GIAY = 20.0            # bao lâu hỏi một lần
CHO_LEN_GIAY = 90.0         # cho runtime bao lâu để lên sau khi dựng
NGHI_DAU = 10.0             # lùi lần đầu
NGHI_TOI_DA = 300.0         # trần lùi — 5 phút, đủ ngắn để không mất cả đêm


def _dat_nhat_ky() -> None:
    tay = logging.handlers.RotatingFileHandler(
        NHAT_KY / "canh-gac.log", maxBytes=2 * 1024 * 1024, backupCount=3,
        encoding="utf-8")
    tay.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s"))
    g = logging.getLogger()
    g.setLevel(logging.INFO)
    g.addHandler(tay)


def _cong_runtime() -> int:
    """Đọc cổng từ config. Đóng cứng ở đây là hai nguồn sự thật."""
    try:
        from kham.config import CONFIG
        return int(CONFIG["port"])
    except Exception:                                   # noqa: BLE001
        return 5186


def _con_song(cong: int) -> bool:
    """Runtime có trả lời không. Hỏi CỔNG, không hỏi `pid.txt`.

    `pid.txt` ở lại sau khi tiến trình bị giết, nên nó nói "đang chạy"
    về một PID đã chết — đúng cái làm người canh gác ngủ quên.
    """
    try:
        with urllib.request.urlopen(
                f"http://127.0.0.1:{cong}/api/trang-thai", timeout=8) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False


def _giu_cho() -> socket.socket | None:
    """Giữ cổng canh gác. None nghĩa là đã có người canh khác."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", CONG_CANH))
        s.listen(1)
        return s
    except OSError:
        s.close()
        return None


def _dung_day() -> subprocess.Popen | None:
    """Bật `chay-nen.py`. Dùng pythonw để không hiện cửa sổ."""
    py = Path(sys.executable)
    pyw = py.with_name("pythonw.exe")
    exe = str(pyw if pyw.exists() else py)
    try:
        return subprocess.Popen(
            [exe, str(GOC / "dichvu" / "chay-nen.py")],
            cwd=str(GOC),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except OSError as e:
        logging.error("không bật nổi chay-nen.py: %s: %s",
                      type(e).__name__, e)
        return None


def main() -> int:
    _dat_nhat_ky()
    cho = _giu_cho()
    if cho is None:
        logging.warning("đã có một người canh gác đang chạy (cổng %d) — "
                        "bản này thoát.", CONG_CANH)
        return 3

    cong = _cong_runtime()
    logging.info("=" * 70)
    logging.info("Người canh gác — PID %d · canh cổng %d · nhịp %.0fs",
                 os.getpid(), cong, NHIP_GIAY)

    soLanDung = 0
    nghi = NGHI_DAU
    lanSongCuoi = time.time()

    while True:
        if _con_song(cong):
            if nghi != NGHI_DAU:
                logging.info("runtime đã sống lại — đặt lại nhịp lùi")
            nghi = NGHI_DAU
            lanSongCuoi = time.time()
            time.sleep(NHIP_GIAY)
            continue

        chet_bao_lau = time.time() - lanSongCuoi
        soLanDung += 1
        logging.warning("runtime KHÔNG trả lời (đã im %.0f giây) — "
                        "dựng lại lần thứ %d", chet_bao_lau, soLanDung)

        p = _dung_day()
        if p is None:
            time.sleep(nghi)
            nghi = min(NGHI_TOI_DA, nghi * 2)
            continue

        # Chờ nó lên. Không chờ đủ thì lượt sau tưởng nó chết tiếp và
        # dựng chồng lên — khoá một-bản của `chay-nen.py` sẽ chặn, nhưng
        # nhật ký thành một chuỗi "thoát mã 3" không ai đọc nổi.
        het = time.time() + CHO_LEN_GIAY
        while time.time() < het:
            time.sleep(5.0)
            if _con_song(cong):
                break

        if _con_song(cong):
            logging.info("runtime lên lại sau %.0f giây",
                         CHO_LEN_GIAY - (het - time.time()))
            nghi = NGHI_DAU
            lanSongCuoi = time.time()
        else:
            logging.error("dựng rồi mà runtime vẫn không trả lời — "
                          "nghỉ %.0f giây rồi thử lại", nghi)
            time.sleep(nghi)
            nghi = min(NGHI_TOI_DA, nghi * 2)


if __name__ == "__main__":
    raise SystemExit(main())
