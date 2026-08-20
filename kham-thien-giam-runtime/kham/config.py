"""Cấu hình + đường dẫn + ba cửa của chế độ chạy.

Một chỗ duy nhất đọc `config.json` và `.env`, để không phiên nào phải đoán
giá trị đang có hiệu lực là gì.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `KTG_DATA_DIR` tách sổ sách của phép kiểm khỏi sổ sách thật — cùng bài học
# đã phải trả giá ở tu-cam-thanh-runtime: selftest ở đó dựng những lệnh thắng
# để kiểm phần kế toán, rồi 14/17 lệnh trong sổ thật là hàng giả và bảng điều
# khiển khoe "thắng 82,4%" trong khi bot chưa tự vào lệnh nào. Con số đẹp nhất
# hệ thống lại là con số bịa.
DATA_DIR = Path(os.environ.get("KTG_DATA_DIR") or (ROOT / "data"))
WEB_DIR = ROOT / "web"


def _load_dotenv() -> None:
    """Đọc .env bằng tay — không phụ thuộc thư viện, không ghi đè biến đã có.

    `utf-8-sig` chứ không phải `utf-8`: Notepad trên Windows lưu kèm BOM, và
    khi đó tên biến ĐẦU TIÊN thành "﻿ANTHROPIC_API_KEY". Không lỗi nào
    báo — biến đó coi như không tồn tại, và người dùng ngồi nhìn một runtime
    bảo "thiếu khoá" trong khi khoá nằm sờ sờ trong file.
    """
    p = ROOT / ".env"
    if not p.exists():
        return
    for raw in p.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        if not os.environ.get(k):
            os.environ[k] = v


_load_dotenv()

CONFIG: dict = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))

# Cờ dòng lệnh thắng config: python run.py --che=quan-sat --port=5286
for _arg in sys.argv[1:]:
    if not _arg.startswith("--") or "=" not in _arg:
        continue
    _k, _v = _arg[2:].split("=", 1)
    if _k == "port":
        CONFIG["port"] = int(_v)
    elif _k == "che":
        CONFIG["che"] = _v
    elif _k == "vong":
        CONFIG["loopSeconds"] = float(_v)

if os.environ.get("CHE") and not any(a.startswith("--che=") for a in sys.argv[1:]):
    CONFIG["che"] = os.environ["CHE"]

CHE_HOP_LE = ("quan-sat", "giay", "that")
if CONFIG.get("che") not in CHE_HOP_LE:
    raise SystemExit(
        f"che không hợp lệ: {CONFIG.get('che')!r} — chỉ có {', '.join(CHE_HOP_LE)}"
    )

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════
#  BA CỬA CỦA LỆNH THẬT
#
#  Một lệnh thật chỉ rời khỏi máy này khi CẢ BA cùng mở. Vì sao ba chứ không
#  phải một cờ: một dòng cấu hình duy nhất ngăn giữa mô phỏng và tiền thật là
#  quá mỏng — sửa nhầm một ký tự, hoặc `git checkout` một file, là tiền thật
#  bắt đầu chạy mà không ai kịp nhận ra.
#
#  Ba cửa nằm ở ba nơi khác nhau về BẢN CHẤT, nên không thao tác đơn lẻ nào
#  mở được cả ba:
#    · config.json  — file đã commit, diff nhìn thấy được khi review
#    · config.json  — một xác nhận riêng, tách khỏi cờ chính, buộc đọc mục rủi ro
#    · .env         — khoá ví, KHÔNG BAO GIỜ ở trong repo
#
#  Thiếu bất kỳ cửa nào thì rơi về sổ giấy. Và không rơi trong im lặng —
#  `ly_do_khong_that()` nói rõ cửa nào đang đóng.
# ══════════════════════════════════════════════════════════════════════════

def _co_khoa_vi() -> bool:
    return bool((os.environ.get("POLYMARKET_PRIVATE_KEY") or "").strip())


def ly_do_khong_that() -> list[str]:
    """Danh sách cửa đang đóng. Rỗng = đủ điều kiện đặt lệnh thật."""
    dl = CONFIG.get("datLenh") or {}
    thieu: list[str] = []
    if CONFIG.get("che") != "that":
        thieu.append("che ≠ 'that' (đang: %r)" % CONFIG.get("che"))
    if not dl.get("choPhepLenhThat"):
        thieu.append("datLenh.choPhepLenhThat = false")
    if not dl.get("toiXacNhanDaDocRuiRo"):
        thieu.append("datLenh.toiXacNhanDaDocRuiRo = false")
    if not _co_khoa_vi():
        thieu.append("thiếu POLYMARKET_PRIVATE_KEY trong .env")
    return thieu


def dat_lenh_that() -> bool:
    """True chỉ khi cả ba cửa cùng mở."""
    return not ly_do_khong_that()


def che_hieu_luc() -> str:
    """Chế độ THỰC SỰ đang chạy, sau khi đã soi ba cửa.

    Khai `che: "that"` mà thiếu khoá ví thì chế độ hiệu lực là `giay`, không
    phải `that`. Hàm này tồn tại để bảng điều khiển và nhật ký nói đúng thứ
    đang xảy ra chứ không nói lại thứ file cấu hình mong muốn.
    """
    if CONFIG.get("che") == "quan-sat":
        return "quan-sat"
    return "that" if dat_lenh_that() else "giay"


def nao_cham_bat() -> bool:
    """Vòng não chậm (Claude) có khoá để chạy không."""
    return bool((os.environ.get("ANTHROPIC_API_KEY") or "").strip())
