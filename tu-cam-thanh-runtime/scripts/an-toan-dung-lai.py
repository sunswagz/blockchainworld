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

# LÀN nào. `--demo` hỏi về làn hai chiều ở cổng 5282; mặc định là làn chính.
# Hỏi nhầm làn thì câu trả lời vẫn đúng — về một bot khác.
LAN = "demo" if "--demo" in sys.argv else "chinh"
CONG = 5282 if LAN == "demo" else 5182


def _giam_sat() -> tuple[bool, str]:
    """Bộ giám sát của làn này còn sống không, và nó là ai.

    Câu hỏi này THIẾU trong bản đầu, và nó thiếu đúng vào ngày cần nhất. Ngày
    30/08 công cụ báo "AN TOÀN — 3 vị thế mở nhưng OCO đã ở SÀN", tôi giết tiến
    trình con để nạp mã mới, và KHÔNG CÓ AI dựng lại: bộ giám sát đã chết từ
    trước đó hai tiếng mà không gì lộ ra.

    "An toàn để dừng" gồm HAI vế: vị thế được sàn canh, VÀ có ai đó dựng lại.
    Bản đầu chỉ hỏi vế thứ nhất — và vế ấy đúng, nên câu trả lời sai mà không
    sai một chữ nào.
    """
    import sys as _s
    from pathlib import Path as _P

    _s.path.insert(0, str(_P(__file__).resolve().parent.parent))
    from trader import nghi_thuc as _NT

    ten = "trang-thai-demo.json" if LAN == "demo" else "trang-thai.json"
    f = _P(__file__).resolve().parent.parent / "dichvu" / ten
    try:
        tt = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, f"không đọc được {ten}"
    pid = tt.get("giamSatPid")
    if not pid:
        return False, f"{ten} không ghi giamSatPid"
    if not _NT._con_song(pid):
        return False, f"bộ giám sát pid {pid} ĐÃ CHẾT"
    return True, f"bộ giám sát pid {pid} còn sống"


def main() -> int:
    # Hỏi vế "có ai dựng lại không" TRƯỚC, vì nó không cần mạng và vì nó là vế
    # đã sót. Không chặn ở đây — chỉ nói ra; người gọi có thể đang cố tình dừng
    # hẳn. Nhưng nói ra thì không ai còn giết nhầm trong im lặng.
    _ok, _vs = _giam_sat()
    print(("  ⓘ " if _ok else "  ⚠ ") + _vs
          + ("" if _ok else " — giết tiến trình con bây giờ là KHÔNG AI DỰNG LẠI. "
                            "Bật lại bằng dichvu/bat.ps1" + (" -Demo" if LAN == "demo" else "")))
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

    # SÀN GIẤY không có OCO, và không cần có. Vị thế nằm trong `account.json`,
    # và `mark()` chấm lại chúng ngay vòng đầu sau khi dựng lại — stop không
    # nằm trong bộ nhớ tiến trình, nó nằm trên đĩa.
    #
    # Bản đầu áp luật OCO cho MỌI chế độ, nên làn demo bị báo "KHÔNG AN TOÀN —
    # 1/1 vị thế không có OCO" ngay lệnh SHORT đầu tiên của phép đo. Một ⚠ cho
    # thứ không gãy là cách nhanh nhất dạy người ta bỏ qua ⚠.
    if d.get("mode") == "paper":
        for p in vt:
            print(f"  {p.get('id')} {p.get('side')} {p.get('qty')} @ {p.get('entry')} · "
                  f"SL {p.get('stopLoss')}")
        print(f"AN TOÀN — {len(vt)} vị thế trên SÀN GIẤY. Không có OCO ở sàn nào "
              f"cả, và không cần: vị thế nằm trong account.json và được chấm lại "
              f"ngay vòng đầu sau khi dựng lại.")
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
