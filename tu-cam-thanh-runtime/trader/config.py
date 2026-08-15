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
DATA_DIR = ROOT / "data"
SKILLS_DIR = ROOT / "skills"
WEB_DIR = ROOT / "web"


def _load_dotenv() -> None:
    """Đọc .env bằng tay — không phụ thuộc thư viện, không ghi đè biến đã có."""
    p = ROOT / ".env"
    if not p.exists():
        return
    for raw in p.read_text(encoding="utf-8").splitlines():
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

DATA_DIR.mkdir(parents=True, exist_ok=True)


def brain_mode() -> str:
    """auto = có khoá thì dùng Claude; claude = bắt buộc; mock = không bao giờ gọi API.

    'auto' cố ý rơi về mock khi thiếu khoá: hệ thống phải chạy kín vòng được
    mà không tốn đồng nào, nếu không thì không ai dám để nó chạy lâu.
    """
    want = (os.environ.get("BRAIN") or "auto").lower()
    if want == "mock":
        return "mock"
    if want == "claude":
        return "claude"
    return "claude" if os.environ.get("ANTHROPIC_API_KEY") else "mock"
