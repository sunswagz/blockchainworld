"""GIẢ THUYẾT — khai trước khi đo, chốt sau khi đo, tra trước khi tốn công.

    python scripts/gia-thuyet.py                        liệt kê tất cả
    python scripts/gia-thuyet.py --tra "khung 4h"       cái này đã thử chưa?
    python scripts/gia-thuyet.py --khai <mã> --hoi "..." --doan "..." \\
        --do "..." --truong kyVongR --toan ">" --gia 0 --mau 20
    python scripts/gia-thuyet.py --chot <mã> --so '{"kyVongR":0.11,"mau":26}'

Ba lệnh, và thứ tự của chúng là cả điểm của công cụ. `--tra` chạy TRƯỚC khi dựng
một phép đo mới; `--khai` chạy TRƯỚC khi đo; `--chot` chạy SAU. Đảo thứ tự thì
sổ vẫn ghi được nhưng không còn ngăn được gì.

VÌ SAO KHÔNG CÓ `--sua`

Sửa một bản khai sau khi đã thấy số là toàn bộ thứ sổ này sinh ra để chặn. Cần
đổi dự đoán thì khai một mã MỚI và nói rõ trong `--hoi` là nó thay cho mã cũ —
để cả hai cùng nằm trong sổ, và người đọc sau thấy được là đã có một lần đổi ý.
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import so_gia_thuyet as G  # noqa: E402

MAU_PQ = {"XÁC_NHẬN": "✓", "BÁC_BỎ": "✗", "KHÔNG_KẾT_LUẬN": "?", None: "…"}


def _co(ten: str, mac_dinh=None):
    return sys.argv[sys.argv.index(ten) + 1] if ten in sys.argv else mac_dinh


def _in_mot(g: dict, day_du: bool = False) -> None:
    dau = MAU_PQ.get(g["phanQuyet"], "…")
    print(f"  {dau} {g['ma']:28} {g['phanQuyet'] or 'ĐANG MỞ':16} {g['luc'][:10]}")
    if day_du:
        print(textwrap.fill(f"hỏi:  {g['cauHoi']}", 88, initial_indent="      ",
                            subsequent_indent="            "))
        print(textwrap.fill(f"đoán: {g['duDoan']}", 88, initial_indent="      ",
                            subsequent_indent="            "))
        n = g["nguong"]
        print(f"      ngưỡng: {n['truong']} {n['toanTu']} {n['giaTri']} · mẫu ≥ {n['mauToiThieu']}")
        if g.get("moTa"):
            print(f"      đo được: {g['moTa']}")


def main() -> int:
    if "--khai" in sys.argv:
        ma = _co("--khai")
        nguong = {"truong": _co("--truong", "kyVongR"),
                  "toanTu": _co("--toan", ">"),
                  "giaTri": float(_co("--gia", 0)),
                  "mauToiThieu": int(_co("--mau", 20))}
        r = G.khai(ma, _co("--hoi", ""), _co("--doan", ""), _co("--do", ""), nguong)
        if not r["ok"]:
            print("KHÔNG KHAI ĐƯỢC:", r["viSao"])
            return 1
        print(f"đã khai «{ma}» lúc {r['banKhai']['luc']} · vân tay {r['banKhai']['dau']}")
        print("Bản khai này không sửa được nữa. Đo xong thì --chot.")
        return 0

    if "--chot" in sys.argv:
        ma = _co("--chot")
        try:
            so = json.loads(_co("--so", "{}"))
        except ValueError as e:
            print(f"--so phải là JSON: {e}")
            return 1
        r = G.chot(ma, so, _co("--ghi-chu", ""))
        if not r["ok"]:
            print("KHÔNG CHỐT ĐƯỢC:", r["viSao"])
            return 1
        print(f"«{ma}» → {r['phanQuyet']}  ({r['moTa']})")
        if r["phanQuyet"] == "BÁC_BỎ":
            print("Kết quả ÂM đã được cất. Đây là thứ đắt nhất vừa mua được — "
                  "lượt sau tra ra nó là tiết kiệm nguyên một phép đo.")
        return 0

    if "--tra" in sys.argv:
        t = _co("--tra", "")
        ds = G.tra(t)
        print(f"tra «{t}» → {len(ds)} giả thuyết\n")
        for g in ds:
            _in_mot(g, day_du=True)
            print()
        if not ds:
            print("  (chưa ai thử cái này — khai một giả thuyết trước khi đo)")
        return 0

    tt = G.tom_tat()
    print(f"{tt['tong']} giả thuyết · " +
          " · ".join(f"{k} {v}" for k, v in sorted(tt["theoPhanQuyet"].items())))
    if tt["dangMo"]:
        print(f"ĐANG MỞ (đã khai, chưa chốt): {', '.join(tt['dangMo'])}")
    print()
    for g in G.tra(""):
        _in_mot(g)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
