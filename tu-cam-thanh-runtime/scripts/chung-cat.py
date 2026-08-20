"""CHƯNG CẤT — đúc lại toàn bộ phát hiện từ mọi kho đo.

    python scripts/chung-cat.py           chưng và in ra
    python scripts/chung-cat.py --im      chưng, chỉ in một dòng tổng kết

Vòng lặp tự gọi hàm này định kỳ; script chỉ để chạy tay sau khi phòng huấn luyện
hoặc đài quan sát vừa chạy xong và muốn thấy ngay kết quả.

Đọc kỹ phần "ĐÃ BỎ": mỗi dòng ở đó là một điều bộ máy CHƯA đủ mẫu để nói. Danh
sách rỗng không có nghĩa mọi thứ đều tốt — nó có nghĩa không nguồn nào bị từ
chối, và đó là hai chuyện khác nhau.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trader import chung_cat, store  # noqa: E402

IM = "--im" in sys.argv


def main() -> int:
    kq = chung_cat.chung_cat()

    if not IM:
        theo: dict[str, list] = {}
        for p in store.read_all(store.PHAT_HIEN):
            theo.setdefault(p["nguon"], []).append(p)

        for nguon in ("chien-luoc", "chay-lai", "so-that", "dai-quan-sat"):
            ds = theo.get(nguon)
            if not ds:
                continue
            print(f"\n── {nguon} " + "─" * (68 - len(nguon)))
            for p in sorted(ds, key=lambda x: -(x.get("mau") or 0)):
                dau = f"[{p['doTin']}·mẫu {p['mau']}]"
                print(f"  {dau}")
                print(textwrap.fill(p["cau"], 76, initial_indent="   ",
                                    subsequent_indent="   "))

        if kq["daBo"]:
            print("\n── ĐÃ BỎ (chưa đủ mẫu để nói) " + "─" * 41)
            for b in kq["daBo"]:
                print(f"  {b['ma']:34} {b['viSao']}")

        # Cầu dao là phần DUY NHẤT đổi hành vi, nên nó phải hiện riêng.
        print("\n── CẦU DAO CHẾ ĐỘ " + "─" * 53)
        ngat = [p for p in store.read_all(store.PHAT_HIEN)
                if p.get("cheDo") and chung_cat.cau_dao(p["cheDo"], None)]
        if ngat:
            for p in ngat:
                print(f"  NGẮT  {p['cheDo']} — kỳ vọng {p['so'].get('kyVongR')}R "
                      f"qua {p['mau']} lệnh chạy lại")
            print(f"  (ngưỡng: ≤{chung_cat.CAU_DAO_KY_VONG}R và ≥{chung_cat.CAU_DAO_MAU} lệnh; "
                  f"chỉ áp ở đường chạy thật, không áp cho vòng chạy lại)")
        else:
            print("  không chế độ nào bị ngắt")

    print(f"\n{kq['soPhatHien']} phát hiện · bỏ {kq['soDaBo']} · "
          + " · ".join(f"{k} {v}" for k, v in sorted(kq["theoNguon"].items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
