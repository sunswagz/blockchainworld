"""Lưu trữ append-only bằng JSONL + vài file JSON trạng thái.

Chọn thứ đơn giản nhất chạy được ở M0: không phải cài gì, đọc được bằng mắt,
grep được. Đổi sang SQLite/Postgres sau này chỉ phải thay đúng file này.
"""
from __future__ import annotations

import json
import threading
from typing import Any

from .config import DATA_DIR

_lock = threading.Lock()

TRADES = "trades.jsonl"      # EPISODIC MEMORY — từng giao dịch
LESSONS = "lessons.jsonl"    # SEMANTIC MEMORY — bài học đã hậu kiểm
THESES = "theses.jsonl"      # mọi luận điểm, kể cả cái bị Risk Engine từ chối
COST = "cost.json"           # đồng hồ chi phí theo ngày UTC
ACCOUNT = "account.json"     # trạng thái tài khoản paper


def append(name: str, obj: dict) -> dict:
    with _lock:
        with (DATA_DIR / name).open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return obj


def read_all(name: str) -> list[dict]:
    p = DATA_DIR / name
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def write_json(name: str, obj: Any) -> Any:
    with _lock:
        (DATA_DIR / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return obj


def read_json(name: str, fallback: Any = None) -> Any:
    p = DATA_DIR / name
    if not p.exists():
        return fallback
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback
