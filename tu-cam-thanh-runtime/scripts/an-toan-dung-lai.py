"""CÓ AN TOÀN ĐỂ DỰNG LẠI RUNTIME KHÔNG — hỏi một câu, trả lời một câu.

    python scripts/an-toan-dung-lai.py       mã thoát 0 = an toàn, 1 = không

VÌ SAO CẦN MỘT SCRIPT CHO MỘT CÂU HỎI

Vì đã trả lời sai nó. Vị thế mở nằm ở `account.positions`, không phải ở
`positions` tại gốc `/api/state` — khoá gốc ấy KHÔNG tồn tại, nên
`d.get("positions")` trả None và đọc y hệt "không có vị thế nào". Hai lần dựng
lại runtime trong một buổi với niềm tin sai đó.

Lần ấy không mất gì: OCO đặt ở SÀN nên SL/TP sống độc lập với tiến trình. Nhưng
"không mất gì lần này" và "an toàn" là hai chuyện, và cái ngăn cách chúng là
`ocoError` — vị thế mở mà OCO đặt hỏng thì stop chỉ tồn tại trong bộ nhớ của
tiến trình sắp bị giết.

Nên câu trả lời có ba mức, không phải hai:

    không vị thế nào            → an toàn
    có vị thế, OCO ở sàn OK     → an toàn (sàn giữ stop hộ)
    có vị thế, ocoError khác No → KHÔNG an toàn, dừng lại
"""
from __future__ import annotations

import json
import sys
import urllib.request

CONG = 5182


def main() -> int:
    try:
        with urllib.request.urlopen(
                f"http://localhost:{CONG}/api/state", timeout=10) as r:
            d = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"KHÔNG HỎI ĐƯỢC runtime ({type(e).__name__}) — "
              f"nó có thể đã chết sẵn. Kiểm trước khi làm gì.")
        return 1

    vt = (d.get("account") or {}).get("positions") or []
    if not vt:
        print("AN TOÀN — không có vị thế nào đang mở.")
        return 0

    hong = [p for p in vt if p.get("ocoError") or not p.get("ocoOrderListId")]
    for p in vt:
        print(f"  {p.get('id')} {p.get('side')} {p.get('qty')} @ {p.get('entry')} · "
              f"SL {p.get('stopLoss')} · OCO {p.get('ocoOrderListId')} · "
              f"lỗi OCO: {p.get('ocoError')}")
    if hong:
        print(f"KHÔNG AN TOÀN — {len(hong)}/{len(vt)} vị thế không có OCO sống ở sàn. "
              f"Giết tiến trình là bỏ stop của chúng lại trong bộ nhớ.")
        return 1
    print(f"AN TOÀN — {len(vt)} vị thế mở nhưng OCO đã ở SÀN, "
          f"SL/TP sống độc lập với tiến trình.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
