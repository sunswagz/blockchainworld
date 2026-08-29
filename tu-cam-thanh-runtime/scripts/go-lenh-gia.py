"""GỠ LỆNH GIẢ khỏi sổ giao dịch — nhận diện bằng CHỮ KÝ, không bằng danh sách.

    python scripts/go-lenh-gia.py           xem trước
    python scripts/go-lenh-gia.py --go      gỡ thật

CHUYỆN ĐÃ XẢY RA

`scripts/selftest.py` dùng `os.environ.setdefault("TCT_DATA_DIR", ...)`. Hễ môi
trường ĐÃ có biến đó — một dòng `export` trong shell là đủ — phép kiểm chạy
thẳng vào SỔ THẬT. Nó ghi 3 lệnh giả vào sổ giao dịch, đè kho chạy lại 86 → 40
bản, đè kho phát hiện 28 → 2. Xảy ra ít nhất hai lần, cách nhau một ngày.

Đây là lần THỨ HAI trong đời hệ này: lần trước là 14 lệnh giả của selftest trộn
vào thống kê, và cách chữa khi ấy sinh ra chính biến `TCT_DATA_DIR`.

CHỮ KÝ, KHÔNG PHẢI DANH SÁCH

Chọn tay ba cái id là chữa đúng lần này và vô dụng lần sau. Lệnh do sàn giấy của
phép kiểm sinh ra có dấu vết không thể nhầm:

    openedAt == closedAt        mở và đóng trong cùng một khoảnh khắc
    không có entryOrderId       lệnh thật luôn có mã lệnh của sàn
    không có ocoOrderListId     vị thế thật luôn có OCO bảo vệ

Cả BA điều kiện phải cùng đúng. Một lệnh thật đóng nhanh vẫn có mã sàn; một lệnh
sàn-giấy hợp lệ (chế độ paper) vẫn có hai mốc thời gian khác nhau.

KHÔNG XOÁ — CHUYỂN SANG KHO CÁCH LY

`trades.jsonl` là sổ append-only. Ghi đè nó là xoá lịch sử. Nên lệnh giả được
chuyển sang `trades-nhiem.jsonl` kèm lý do, và sổ chính được ghi lại KHÔNG có
chúng — có mất mát, nhưng mất mát ấy nằm trong một file đọc được chứ không biến
mất. Cách này đã dùng một lần cho `*-thu-nghiem.jsonl`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import store  # noqa: E402
from trader.config import DATA_DIR  # noqa: E402

NL = chr(10)

GO = "--go" in sys.argv


def la_gia(t: dict) -> bool:
    """Ba điều kiện phải CÙNG đúng."""
    return (
        bool(t.get("openedAt"))
        and t.get("openedAt") == t.get("closedAt")
        and not t.get("entryOrderId")
        and not t.get("ocoOrderListId")
    )


def _don_so_gia_thuyet() -> int:
    """Gỡ giả thuyết do phép kiểm ghi nhầm. Trả về số bản ghi đã gỡ.

    Selftest mục [15] khai `gt-thu` và `gt-be`. Chúng lọt vào sổ THẬT cùng đợt
    với ba lệnh giả, và sổ giả thuyết là append-only nên không có đường xoá bình
    thường — đúng như thiết kế: không ai được lặng lẽ sửa lại dự đoán cũ.

    Nên gỡ ở đây phải ĐỂ LẠI DẤU. Bản ghi bị gỡ đi vào kho cách ly, và một bản
    ghi mới được ĐẶT VÀO SỔ nói rõ đã gỡ cái gì, vì sao. Sổ vẫn append-only về
    tinh thần: lịch sử không mất, nó chỉ được chú thích thêm.
    """
    ma_cua = lambda xs: [str(x.get("ma", "")) for x in xs]
    ds = store.read_all(store.GIA_THUYET)
    la_thu = lambda x: str(x.get("ma", "")).startswith("gt-")
    rac = [x for x in ds if la_thu(x)]
    if not rac:
        return 0
    if not GO:
        print(f"{NL}sổ giả thuyết: {len(rac)} bản ghi của phép kiểm "
              f"({sorted(set(ma_cua(rac)))})")
        return len(rac)

    kho = DATA_DIR / "gia-thuyet-nhiem.jsonl"
    with kho.open("a", encoding="utf-8") as f:
        for x in rac:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    con = [x for x in ds if not la_thu(x)]
    with (DATA_DIR / store.GIA_THUYET).open("w", encoding="utf-8") as f:
        for x in con:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    store.append(store.GIA_THUYET, {
        "loai": "ghi-chu", "ma": "_don-rac-selftest",
        "luc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
        "daGo": sorted({x["ma"] for x in rac}),
        "viSao": ("phép kiểm ghi nhầm vào sổ thật khi TCT_DATA_DIR bị kế thừa "
                  "từ môi trường; đã chuyển sang gia-thuyet-nhiem.jsonl"),
    })
    return len(rac)


def main() -> int:
    ds = store.read_all(store.TRADES)
    gia = [t for t in ds if la_gia(t)]
    that = [t for t in ds if not la_gia(t)]

    print(f"{len(ds)} lệnh trong sổ · {len(gia)} khớp chữ ký LỆNH GIẢ\n")
    for t in gia:
        print(f"  {t.get('id', '?')[:14]}  {t.get('openedAt')}  "
              f"vào {t.get('entry')} ra {t.get('exit')}  pnl {t.get('pnl')}  "
              f"{t.get('exitReason')}")
    if not gia:
        print("  (sổ lệnh sạch)")
        _don_so_gia_thuyet()
        return 0

    tong = sum(t.get("pnl") or 0 for t in gia)
    print(f"\nChúng đang cộng {tong:+.2f} vào tổng lãi/lỗ và {len(gia)} vào số lệnh.")

    if not GO:
        print("\n(xem trước — thêm --go để gỡ)")
        return 0

    kho = DATA_DIR / "trades-nhiem.jsonl"
    with kho.open("a", encoding="utf-8") as f:
        for t in gia:
            f.write(json.dumps({**t, "_viSaoCachLy": (
                "khớp chữ ký lệnh giả: mở và đóng cùng khoảnh khắc, không mã lệnh "
                "sàn, không OCO. Do selftest ghi nhầm vào sổ thật khi TCT_DATA_DIR "
                "bị kế thừa từ môi trường.")}, ensure_ascii=False) + "\n")

    # Ghi thẳng, không qua `store.write_all` — hàm đó cố ý từ chối TRADES, và
    # việc phải đi vòng qua nó chính là chỗ dừng lại tự hỏi có nên làm không.
    with (DATA_DIR / store.TRADES).open("w", encoding="utf-8") as f:
        for t in that:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    print(f"\nđã chuyển {len(gia)} lệnh sang {kho.name}; sổ chính còn {len(that)} lệnh.")
    n_gt = _don_so_gia_thuyet()
    if n_gt:
        print(f"sổ giả thuyết: gỡ {n_gt} bản ghi của phép kiểm, có để lại ghi chú.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
