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

TRADES = "trades.jsonl"      # EPISODIC MEMORY — từng giao dịch THẬT
LESSONS = "lessons.jsonl"    # SEMANTIC MEMORY — bài học từ lệnh thật
THESES = "theses.jsonl"      # mọi luận điểm, kể cả cái bị Risk Engine từ chối
COST = "cost.json"           # đồng hồ chi phí theo ngày UTC
ACCOUNT = "account.json"     # trạng thái tài khoản paper

# File RIÊNG cho bài học đúc từ chạy lại lịch sử. Cố ý không nhập vào
# `lessons.jsonl`: lệnh chạy lại khớp đúng giá đặt, không có nhảy giá qua stop,
# không khớp một phần — nên chúng đáng tin về CẤU TRÚC nhưng không đáng tin về
# ĐỘ LỚN. Trộn chung là mất khả năng phân biệt, đúng như 14 lệnh giả của
# selftest từng làm sai lệch sổ giao dịch mà không ai nhận ra.
LESSONS_CHAY_LAI = "lessons-chay-lai.jsonl"

# BẢN SOÁT LẠI của bài học thật — SINH LẠI ĐƯỢC từ `trades.jsonl`, nên được phép
# ghi đè (khác hẳn `lessons.jsonl`).
#
# Vì sao cần: bài học được đúc NGAY LÚC lệnh đóng, khi sổ mới có vài lệnh. Nhiều
# câu hỏi chỉ trả lời được khi nhìn cả sổ — "lệnh này cược lớn hơn mức thường bao
# nhiêu" là vô nghĩa khi chưa có "mức thường". Tám bài học đầu tiên vì thế ra
# đúng HAI câu cho tám lệnh khác nhau, trong đó có hai lệnh cược gấp 1,8–1,9× vẫn
# bị dán nhãn GOOD_TRADE.
#
# `lessons.jsonl` giữ nguyên — đó là bản ghi bộ não ĐÃ nghĩ gì lúc đó, và xoá nó
# là xoá bằng chứng. File này là lớp phủ: `recall()` ưu tiên bản soát lại khi có,
# và xoá file đi là quay về nguyên trạng.
LESSONS_SOAT_LAI = "lessons-soat-lai.jsonl"


def append(name: str, obj: dict) -> dict:
    with _lock:
        with (DATA_DIR / name).open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return obj


def write_all(name: str, rows: list[dict]) -> int:
    """Ghi ĐÈ cả file. Chỉ dùng cho kho sinh lại được từ dữ liệu gốc.

    Không bao giờ dùng cho `TRADES` hay `LESSONS` — đó là sổ append-only, ghi đè
    là xoá lịch sử không lấy lại được.
    """
    if name in (TRADES, LESSONS, THESES):
        raise ValueError(f"{name} là sổ append-only, không được ghi đè")
    with _lock:
        with (DATA_DIR / name).open("w", encoding="utf-8") as f:
            for o in rows:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
    return len(rows)


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
