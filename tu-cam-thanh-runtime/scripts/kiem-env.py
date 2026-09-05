"""Soát file .env trước khi chạy — KHÔNG in khoá ra màn hình.

    python scripts/kiem-env.py

Chỉ in độ dài và 4 ký tự đầu, đủ để bạn nhận ra mình dán nhầm chỗ mà không làm
lộ khoá lên terminal, lên log, hay lên ảnh chụp màn hình gửi cho ai đó.

Bắt đúng những lỗi hay gặp khi dán tay, tất cả đều im lặng nếu không soát:
BOM do Notepad, dấu nháy thừa, khoảng trắng thừa, dán nhầm key ↔ secret, dán
thiếu ký tự, và dán cả chữ "your_key_here" của file mẫu.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# KHÔNG BAO GIỜ chạm sổ thật. GHI ĐÈ, không `setdefault`: một dòng
# `export TCT_DATA_DIR=` trong shell là đủ để setdefault không làm gì, và
# chuyện đó đã sập BA lần ở repo này — lần nặng nhất là bộ kiểm cửa duyệt đưa
# một champion GIẢ lên ngôi trong sổ chiến lược thật.
import os
from _tam_tu_don import tam_moi

os.environ["TCT_DATA_DIR"] = tam_moi("tct-kiem-")

FAILS: list[str] = []
WARNS: list[str] = []


def bad(m: str) -> None:
    print("  SAI  " + m)
    FAILS.append(m)


def warn(m: str) -> None:
    print("  ?    " + m)
    WARNS.append(m)


def ok(m: str) -> None:
    print("  OK   " + m)


def che(v: str) -> str:
    """Che khoá: chỉ lộ 4 ký tự đầu."""
    return f"{v[:4]}…({len(v)} ký tự)" if len(v) > 8 else f"({len(v)} ký tự)"


def main() -> int:
    p = ROOT / ".env"
    print(f"\nsoát {p}")
    if not p.exists():
        bad(".env chưa tồn tại — chạy: cp .env.example .env")
        return 1

    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        warn("file có BOM (Notepad hay thêm). Runtime đọc utf-8-sig nên vẫn chạy, "
             "nhưng nên lưu lại bằng VS Code với encoding UTF-8 thường.")
    else:
        ok("không có BOM")

    kv: dict[str, str] = {}
    for i, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k != k.strip():
            warn(f"dòng {i}: tên biến có khoảng trắng thừa quanh '{k}'")
        kv[k.strip()] = v

    print()
    for ten in ("BINANCE_TESTNET_KEY", "BINANCE_TESTNET_SECRET"):
        if ten not in kv:
            bad(f"{ten}: không có dòng nào")
            continue
        thô = kv[ten]
        v = thô.strip()
        if v != thô:
            warn(f"{ten}: có khoảng trắng thừa (runtime tự cắt, nhưng nên dọn)")
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            warn(f"{ten}: bọc trong dấu nháy (runtime tự bỏ, nhưng không cần)")
            v = v[1:-1]
        if not v:
            bad(f"{ten}: còn rỗng — chưa dán khoá vào")
            continue
        if v.lower() in ("your_key_here", "xxx", "changeme", "todo"):
            bad(f"{ten}: vẫn là chữ mẫu '{v}'")
            continue
        if not v.isalnum():
            warn(f"{ten}: có ký tự lạ — khoá Binance chỉ gồm chữ và số. "
                 f"Chép hụt hoặc dính xuống dòng?")
        if len(v) < 40:
            bad(f"{ten}: chỉ {len(v)} ký tự — khoá Binance dài 64. Chép thiếu.")
            continue
        ok(f"{ten} = {che(v)}")
        kv[ten] = v

    k = kv.get("BINANCE_TESTNET_KEY", "").strip()
    s = kv.get("BINANCE_TESTNET_SECRET", "").strip()
    if k and s:
        if k == s:
            bad("KEY và SECRET giống hệt nhau — dán cùng một chuỗi vào cả hai chỗ")
        else:
            ok("KEY và SECRET khác nhau")

    # config.json có khai testnet không
    import json
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8-sig"))
    mode = cfg.get("mode")
    if mode == "testnet":
        ok('config.json: "mode": "testnet"')
    else:
        warn(f'config.json: "mode": "{mode}" — muốn dùng sàn thật thì đổi thành "testnet"')

    print("\n" + "=" * 60)
    if FAILS:
        print(f"  {len(FAILS)} chỗ PHẢI sửa:")
        for x in FAILS:
            print("   - " + x)
        print("\n  Sửa xong chạy lại, rồi tới: python scripts/kiem-testnet.py")
        return 1
    if WARNS:
        print(f"  {len(WARNS)} chỗ nên dọn, nhưng chạy được.")
    print("  .env ỔN. Bước tiếp: python scripts/kiem-testnet.py")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
