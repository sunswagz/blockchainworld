"""Cấu hình + đường dẫn + chế độ brain.

Một chỗ duy nhất đọc config.json và .env, để không phiên nào phải đoán
giá trị đang có hiệu lực là gì.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `TCT_DATA_DIR` tách sổ sách của phép kiểm khỏi sổ sách thật.
#
# Không có nó, `selftest.py` ghi thẳng vào `data/trades.jsonl` — và nó CỐ TÌNH
# dựng những lệnh thắng để kiểm phần kế toán. Đo tại đây: 14 trong 17 lệnh của
# sổ là hàng giả của selftest, toàn TAKE_PROFIT, cùng một giá vào. Bảng điều
# khiển vì thế khoe "thắng 82,4% · kỳ vọng +1,135R" trong khi bot chưa từng tự
# vào một lệnh nào. Con số đẹp nhất hệ thống lại là con số bịa — đúng thứ mà

DATA_DIR = Path(os.environ.get("TCT_DATA_DIR") or (ROOT / "data"))
SKILLS_DIR = ROOT / "skills"
WEB_DIR = ROOT / "web"


def _load_dotenv() -> None:
    """Đọc .env bằng tay — không phụ thuộc thư viện, không ghi đè biến đã có.

    `utf-8-sig` chứ không phải `utf-8`: Notepad trên Windows lưu kèm BOM, và khi
    đó tên biến ĐẦU TIÊN thành "﻿ANTHROPIC_API_KEY". Không có lỗi nào báo —
    chỉ là biến đó coi như không tồn tại, và người dùng ngồi nhìn một runtime
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


def _chong_tran_cli() -> None:
    """Khi bộ não chạy qua CLI, chồng `brain.cli` lên `brain`.

    Chồng ở MỘT chỗ, ngay sau khi đọc config, thay vì rải điều kiện
    `if mode == "cli"` khắp `loop.py`, đồng hồ chi phí và `brain.py`. Mọi tầng
    phía sau chỉ đọc `CONFIG["brain"]` như cũ và tự nhiên thấy đúng trần.

    Rải điều kiện là cách chắc chắn để một tầng nào đó bị bỏ sót — và tầng bị
    bỏ sót ở đây là tầng tiêu quota của người dùng.
    """
    if brain_mode() != "cli":
        return
    rieng = {k: v for k, v in (CONFIG["brain"].get("cli") or {}).items()
             if not k.startswith("_")}
    CONFIG["brain"].update(rieng)

# Cờ dòng lệnh thắng config: python run.py --brain=mock --port=5231 --symbol=ETHUSDT
for _arg in sys.argv[1:]:
    if not _arg.startswith("--") or "=" not in _arg:
        continue
    _k, _v = _arg[2:].split("=", 1)
    if _k == "brain":
        os.environ["BRAIN"] = _v
    elif _k == "port":
        CONFIG["port"] = int(_v)
    elif _k == "symbol":
        CONFIG["symbol"] = _v
    elif _k == "model":
        CONFIG["brain"]["model"] = _v
    elif _k == "loop":
        CONFIG["loopSeconds"] = int(_v)
    elif _k == "mode":
        CONFIG["mode"] = _v

# Cho phép đổi sàn bằng biến môi trường, để chạy thử một lượt mà không sửa file
# đã commit: `MODE=paper python run.py`. Cờ dòng lệnh vẫn thắng biến môi trường.
if os.environ.get("MODE") and not any(a.startswith("--mode=") for a in sys.argv[1:]):
    CONFIG["mode"] = os.environ["MODE"]

if CONFIG.get("mode") not in ("paper", "testnet"):
    raise SystemExit(f"mode không hợp lệ: {CONFIG.get('mode')!r} — chỉ có 'paper' hoặc 'testnet'")

DATA_DIR.mkdir(parents=True, exist_ok=True)



def brain_mode() -> str:
    """Ba đường tới một bộ não, xếp theo thứ tự ưu tiên khi để `auto`:

        claude   SDK + ANTHROPIC_API_KEY — tính TIỀN theo từng lượt gọi
        cli      claude.exe đã đăng nhập — tính QUOTA GÓI, không đồng nào
        mock     luật thuần, không gọi gì

    'auto' cố ý rơi về mock khi không có đường nào: hệ thống phải chạy kín vòng
    được mà không tốn gì, nếu không thì không ai dám để nó chạy lâu.

    Vì sao `claude` đứng trước `cli` dù `cli` rẻ hơn: ai đã cắm khoá API vào
    `.env` là đã chọn trả tiền để có độ trễ thấp và ràng buộc schema ở tầng API.
    Lặng lẽ chuyển họ sang CLI chậm hơn là quyết định hộ người dùng.
    """
    want = (os.environ.get("BRAIN") or "auto").lower()
    if want in ("mock", "claude", "cli"):
        if want != "cli":
            return want
        from . import cli_claude
        return "cli" if cli_claude.co_the() else "mock"

    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude"
    try:
        from . import cli_claude
        if cli_claude.co_the():
            return "cli"
    except Exception:  # noqa: BLE001 — thiếu module thì coi như không có đường này
        pass
    return "mock"


# Chồng trần CLI ở CUỐI file: nó cần cả `CONFIG` (đã đọc), cờ dòng lệnh (đã áp)
# và `brain_mode()` (định nghĩa phía trên). Đặt sớm hơn một dòng nào là hỏng một
# trong ba thứ đó — và đã hỏng thật một lần vì gọi trước khi hàm tồn tại.
_chong_tran_cli()
