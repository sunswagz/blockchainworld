"""Đối soát sổ cục bộ với sàn testnet, và dọn nếu lệch.

    python scripts/doi-so.py          chỉ soát và in
    python scripts/doi-so.py --don    dọn: huỷ lệnh mồ côi, đóng sổ vị thế ma

Sổ cục bộ và sàn lệch nhau khi runtime chết giữa chừng — giữa lệnh MARKET và
lệnh OCO, hoặc sau khi OCO khớp mà tiến trình chưa kịp ghi. Sàn luôn đúng; sổ
cục bộ chỉ là bản chép.

Chạy cái này khi thấy `MAX_POSITIONS: đang giữ 1/1 vị thế` mà trên sàn không có
gì — đó là dấu hiệu kinh điển của một vị thế ma.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader.broker_testnet import TestnetBroker  # noqa: E402
from trader.config import CONFIG  # noqa: E402

DON = "--don" in sys.argv


def main() -> int:
    b = TestnetBroker(CONFIG["risk"], CONFIG["symbol"])
    if not b.ready:
        print(f"không nối được sàn: {b.last_error}")
        return 1

    sym = CONFIG["symbol"]
    gia = b.client.price(sym)
    treo = b.client.open_orders(sym)
    so = b.state["positions"]

    print(f"\nSÀN     : {len(treo)} lệnh treo")
    for o in treo:
        print(f"          {o['side']:<4} {o['type']:<18} KL {o['origQty']} "
              f"giá {o.get('price')} stop {o.get('stopPrice')} listId {o.get('orderListId')}")
    print(f"SỔ      : {len(so)} vị thế, {b.state.get('closedCount', 0)} lệnh đã đóng")
    for p in so:
        print(f"          {p['id']} {p['side']} {p['qty']} @ {p['entry']} OCO {p.get('ocoOrderListId')}")

    f = b.client.filters(sym)
    bal = b.client.balances()
    print(f"SỐ DƯ   : {f['quote']} {bal.get(f['quote'], {}).get('free', 0):,.2f} rảnh · "
          f"{f['base']} {bal.get(f['base'], {}).get('total', 0):.8f}")

    canh = b.doi_soat()
    print(f"\nLỆCH    : {len(canh)} chỗ")
    for c in canh:
        print(f"          ⚠ {c}")

    if not canh:
        print("\n  Sổ khớp sàn, không cần dọn.")
        return 0

    if not DON:
        print("\n  (chỉ soát — thêm --don để dọn)")
        return 0

    print("\nDỌN")
    ids = {o.get("orderListId") for o in treo}
    for p in list(so):
        oco = p.get("ocoOrderListId")
        if oco is None or oco not in ids:
            # Sàn không còn giữ lệnh nào cho vị thế này ⇒ nó đã kết thúc ở đâu đó.
            # Đóng sổ theo giá hiện tại và ghi rõ lý do, đừng đoán là chạm SL hay TP.
            b._settle(p, ly_do="DOI_SO_DONG_TAY")
            print(f"  đã đóng sổ vị thế ma {p['id']}")
    if treo and not b.state["positions"]:
        b.client.cancel_all(sym)
        print(f"  đã huỷ {len(treo)} lệnh mồ côi trên sàn")

    con = b.doi_soat()
    print(f"\n  còn lệch: {len(con)}")
    return 0 if not con else 1


if __name__ == "__main__":
    raise SystemExit(main())
