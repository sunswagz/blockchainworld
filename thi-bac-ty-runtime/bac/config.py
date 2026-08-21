"""Cấu hình, đường dẫn, và BA CỬA của chế độ chạy.

Một chỗ duy nhất đọc `config.json` và `.env`, để không phiên nào phải đoán giá
trị đang có hiệu lực là gì.

## Ba cửa, ba nơi khác nhau về bản chất

Một lệnh THẬT chỉ rời khỏi máy khi cả ba cùng mở:

    1. `config.json` → `che: "that"`
    2. `config.json` → `datLenh.toiXacNhanDaDocRuiRo: true`
    3. `.env`        → khoá API của ít nhất một sàn

Ba nơi khác nhau là chủ ý. Một dòng cấu hình duy nhất ngăn giữa mô phỏng và
tiền thật là quá mỏng: sửa nhầm một ký tự, hoặc `git checkout` một file, là
tiền thật bắt đầu chạy mà không ai kịp nhận ra.

Thiếu bất kỳ cửa nào thì **rơi về sổ giấy**, và `ly_do_khong_that()` in ra
đúng cửa nào đang đóng — không rơi trong im lặng.

Riêng bản v0.1 còn thêm một khoá cứng nữa: lớp đặt lệnh CHƯA TỒN TẠI. Ba cửa
mở hết thì runtime vẫn từ chối chạy và nói thẳng còn thiếu gì. Xem `README.md`
mục "Lộ trình" — cửa thứ tư mở ở V0.6, sau khi có máy trạng thái hai chân và
đối soát vị thế.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `TBT_DATA_DIR` tách sổ sách của phép kiểm khỏi sổ sách thật. Không có nó thì
# mọi phép kiểm chạm tới sổ đều ghi vào sổ THẬT, và bảng điều khiển khoe những
# giao dịch chưa từng xảy ra — bài học đã phải trả giá ở tu-cam-thanh-runtime.
DATA_DIR = Path(os.environ.get("TBT_DATA_DIR") or (ROOT / "data"))
WEB_DIR = ROOT / "web"

MAC_DINH = {
    "port": 5188,
    "nhipGiay": 30,
    "che": "quan-sat",
    "cungTinh": "",
    "quet": {
        "ma": ["BTC", "ETH", "SOL", "XRP", "DOGE"],
        "giuGio": 8.0,
        "hetGioHoiGiay": 10.0,
    },
    "san": {
        "hyperliquid": {"bat": True, "phiTakerBps": 4.5, "truotGiaBps": 2.0},
        "binance": {"bat": True, "phiTakerBps": 5.0, "truotGiaBps": 2.0},
        "okx": {"bat": True, "phiTakerBps": 5.0, "truotGiaBps": 2.0},
        "bybit": {"bat": True, "phiTakerBps": 5.5, "truotGiaBps": 2.0},
    },
    "ruiRo": {
        "grossToiThieuBpsNgay": 3.0,
        "netToiThieuBps": 0.5,
        "lechMarkToiDaBps": 40.0,
        "doiHoiHaiMark": True,
        "tuoiToiDaGiay": 90.0,
        "nhanUocLuongMoc": False,
        "doiHoiItNhatMotMoc": True,
        "lechDongHoToiDaGiay": 10.0,
        "vonMoiCoHoiUsd": 100.0,
        "vonToiDaUsd": 300.0,
        "donBayToiDa": 1.0,
    },
    "datLenh": {
        "toiXacNhanDaDocRuiRo": False,
    },
    "so": {
        "giuNgay": 30,
    },
}

CHE_HOP_LE = ("quan-sat", "giay", "that")


def _gop(mac_dinh: dict, tren: dict) -> dict:
    """Gộp sâu, và cấu hình người dùng KHÔNG được xoá khoá mặc định.

    Gộp nông thì đặt `"ruiRo": {"netToiThieuBps": 2}` sẽ vứt sạch sáu cửa còn
    lại về không tồn tại, và cổng rủi ro rơi về giá trị rỗng — tức là mở toang
    trong khi người sửa tưởng mình vừa siết chặt.
    """
    ra = dict(mac_dinh)
    for k, v in (tren or {}).items():
        ra[k] = _gop(ra[k], v) if isinstance(v, dict) and isinstance(ra.get(k), dict) else v
    return ra


def _doc_dotenv() -> None:
    """Đọc `.env` bằng tay — không phụ thuộc thư viện, không đè biến đã có.

    `utf-8-sig` chứ không phải `utf-8`: Notepad trên Windows lưu kèm BOM, và
    khi đó tên biến ĐẦU TIÊN thành "﻿BINANCE_API_KEY". Không lỗi nào
    báo — biến đó coi như không tồn tại, và người dùng ngồi nhìn một runtime
    bảo "thiếu khoá" trong khi khoá nằm sờ sờ trong file.
    """
    p = ROOT / ".env"
    if not p.exists():
        return
    for tho in p.read_text(encoding="utf-8-sig").splitlines():
        d = tho.strip()
        if not d or d.startswith("#") or "=" not in d:
            continue
        k, v = d.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _nap() -> dict:
    _doc_dotenv()
    p = ROOT / "config.json"
    tren = {}
    if p.exists():
        tren = json.loads(p.read_text(encoding="utf-8-sig"))
    c = _gop(MAC_DINH, tren)
    if c["che"] not in CHE_HOP_LE:
        raise ValueError(f"che={c['che']!r} không hợp lệ, phải là một trong {CHE_HOP_LE}")
    return c


CONFIG = _nap()
DATA_DIR.mkdir(parents=True, exist_ok=True)

#: Tên biến môi trường của từng sàn. Chỉ để BIẾT có khoá hay không — không
#: chỗ nào trong runtime đọc giá trị của chúng ở bản v0.1.
KHOA_SAN = {
    "binance": ("BINANCE_API_KEY", "BINANCE_API_SECRET"),
    "okx": ("OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"),
    "bybit": ("BYBIT_API_KEY", "BYBIT_API_SECRET"),
    "hyperliquid": ("HYPERLIQUID_PRIVATE_KEY",),
}


def san_co_khoa() -> dict[str, bool]:
    return {s: all(os.environ.get(k) for k in ks) for s, ks in KHOA_SAN.items()}


def ly_do_khong_that() -> list[str]:
    """Những cửa đang ĐÓNG, viết bằng câu người đọc hiểu ngay."""
    ra = []
    if CONFIG.get("che") != "that":
        ra.append('config.json → che vẫn là "%s", chưa phải "that"' % CONFIG.get("che"))
    if not (CONFIG.get("datLenh") or {}).get("toiXacNhanDaDocRuiRo"):
        ra.append("config.json → datLenh.toiXacNhanDaDocRuiRo chưa bật")
    if not any(san_co_khoa().values()):
        ra.append(".env → chưa sàn nào có đủ khoá API")
    # Cửa thứ tư: lớp đặt lệnh chưa tồn tại. Nó KHÔNG mở được bằng cấu hình,
    # và đó là chủ ý — xem README mục "Lộ trình".
    ra.append("lớp đặt lệnh chưa được viết (V0.6) — chưa có máy trạng thái "
              "hai chân, chưa có đối soát vị thế, chưa có kill switch")
    return ra


def che_hieu_luc() -> str:
    """Chế độ THẬT SỰ đang chạy, sau khi xét đủ mọi cửa.

    Khác `CONFIG["che"]` — đó chỉ là điều người dùng KHAI. Buồng lái phải hiện
    con số này, không hiện bản khai, nếu không nó sẽ nói "THẬT" trong khi mọi
    lệnh đang đi vào sổ giấy.
    """
    khai = CONFIG.get("che", "quan-sat")
    if khai != "that":
        return khai
    return "giay"       # còn cửa đóng thì rơi về sổ giấy, không bao giờ "that"
