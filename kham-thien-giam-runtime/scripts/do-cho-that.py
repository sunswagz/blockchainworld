"""CHỢ THẬT nằm ở đâu trên thang w — câu treo suốt phiên, nay trả lời được.

    python scripts/do-cho-that.py

`chay-demo.py --quet` dựng một dãy chợ pha giữa hai đầu mút:

    p_chợ = 0,5 + w·(p_mô_hình − 0,5)

w=0 chợ mù, w=1 chợ biết y hệt ta. Phiên giấy hoà vốn quanh w ≈ 1. Câu
còn lại là: **chợ THẬT nằm ở đâu trên thang ấy?**

Suốt phiên câu đó không trả lời được vì băng chưa từng có một dòng sổ
lệnh nào trong khung ăn thua — `_tim_khung` chỉ bám khung đang đặt cược.
Nay có: đường tới Polymarket chập chờn chứ không đứt hẳn, và trong 24
phút thông (14:54–15:18 UTC 29/08) runtime đã ghi được những dòng ấy.

Ít mẫu. Nên phép đo này KHÔNG chốt gì — nó ước lượng, khai rõ khoảng
tin, và nói thẳng là cần bao nhiêu nữa mới chốt được.

## Ba câu, theo thứ tự

1. **Sổ ấy có thật không**, hay chỉ là thang chờ? Đây là câu chặn: sổ
   không yết giá thì mọi câu sau vô nghĩa.
2. **Chợ định giá tốt tới đâu** — điểm kỹ năng so với tỉ lệ nền, và w
   ước lượng bằng hồi quy p_chợ theo p_mô_hình.
3. **Còn lợi thế ròng nào không** sau spread và phí.
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham.bang import NguonKhung, giai_doan_cua  # noqa: E402
from kham.chay_lai import dung_so  # noqa: E402
from kham.ket_qua import so_ket_qua  # noqa: E402


def main() -> int:
    dong = []
    for k in NguonKhung(None):
        for tt in (k.get("thiTruong") or []):
            if giai_doan_cua(tt) != "quan-sat":
                continue
            su = dung_so((tt.get("so") or {}).get("UP"), tt.get("ma") or "?", "UP")
            sd = dung_so((tt.get("so") or {}).get("DOWN"), tt.get("ma") or "?",
                         "DOWN")
            if su is None or sd is None:
                continue
            dong.append((tt, su, sd))

    print()
    print("=" * 76)
    print("  CHỢ THẬT NẰM Ở ĐÂU — sổ lệnh khung ăn thua, lần đầu có")
    print("=" * 76)
    print(f"  {len(dong):,} dòng khung ăn thua trong băng")
    if len(dong) < 30:
        print("  Quá ít để nói gì. Cần runtime chạy thêm những lúc mạng thông.\n")
        return 0

    # ── 1. sổ ấy có THẬT không ───────────────────────────────────────
    dungDuoc = [x for x in dong if x[1].dung_duoc or x[2].dung_duoc]
    thangCho = sum(1 for _tt, su, sd in dong
                   if su.trai_ca_bang or sd.trai_ca_bang)
    print()
    print(f"  1. SỔ CÓ THẬT KHÔNG")
    print(f"     dùng được   {len(dungDuoc):>5,} / {len(dong):,} "
          f"({len(dungDuoc)/len(dong):.0%})")
    print(f"     thang chờ   {thangCho:>5,}")
    if not dungDuoc:
        print()
        print("     KHÔNG dòng nào yết giá thật. Khung ăn thua chỉ có thang")
        print("     chờ — nghĩa là cửa ấy KHÔNG giao dịch được, và cả hướng")
        print("     'chuyển sang khung ăn thua' phải xem lại từ đầu.")
        print("=" * 76 + "\n")
        return 0

    sp, giua, sau = [], [], []
    for _tt, su, _sd in dungDuoc:
        b, a = su.best_bid, su.best_ask
        if b is None or a is None or a <= b:
            continue
        sp.append(a - b)
        giua.append((a + b) / 2.0)
        sau.append(sum(m.luong for m in su.ask[:3]))
    if sp:
        print(f"     spread trung vị {statistics.median(sp):.4f} · "
              f"giá giữa trung vị {statistics.median(giua):.3f} · "
              f"sâu 3 mức {statistics.median(sau):,.0f} cổ")

    # ── 2. chợ định giá tốt tới đâu ──────────────────────────────────
    cap = []
    for tt, su, _sd in dungDuoc:
        g = su.giua
        p = tt.get("pUp")
        that = so_ket_qua.lay(tt.get("slug") or "")
        if g is None or p is None or that is None:
            continue
        cap.append((float(g), float(p), 1 if that else 0))
    print()
    print(f"  2. CHỢ ĐỊNH GIÁ TỐT TỚI ĐÂU   ({len(cap):,} dòng có kết quả)")
    if len(cap) < 30:
        print("     chưa đủ dòng có kết quả để chấm. Khung mới đóng thì kết")
        print("     quả phải chờ — chạy lại `scripts/dung-ket-qua.py` sau.")
        print("=" * 76 + "\n")
        return 0

    n = len(cap)
    nen = sum(t for _g, _p, t in cap) / n
    bCho = sum((g - t) ** 2 for g, _p, t in cap) / n
    bMo = sum((p - t) ** 2 for _g, p, t in cap) / n
    bNen = sum((nen - t) ** 2 for _g, _p, t in cap) / n
    print(f"     tỉ lệ nền {nen:.1%}")
    print(f"     Brier chợ      {bCho:.5f}   kỹ năng "
          f"{(bNen-bCho)/max(1e-9,bNen):+.1%}")
    print(f"     Brier mô hình  {bMo:.5f}   kỹ năng "
          f"{(bNen-bMo)/max(1e-9,bNen):+.1%}")
    print(f"     Brier tỉ lệ nền{bNen:.5f}")

    # w bằng hồi quy qua gốc: (p_chợ − 0,5) ≈ w · (p_mô_hình − 0,5)
    tu = sum((g - 0.5) * (p - 0.5) for g, p, _t in cap)
    mau = sum((p - 0.5) ** 2 for _g, p, _t in cap)
    w = tu / mau if mau > 0 else float("nan")
    print()
    print(f"     w ước lượng = {w:.3f}   (chợ mù w=0 · chợ biết y hệt ta w=1)")
    print("     Phiên giấy hoà vốn quanh w ≈ 1, nên w dưới 1 rõ rệt thì CÓ")
    print("     chỗ; w quanh 1 hoặc trên thì KHÔNG.")

    # ── 3. lợi thế ròng ──────────────────────────────────────────────
    from kham.can_loi import can
    from kham.config import CONFIG
    nguong = float(CONFIG["canLoi"]["netEdgeToiThieu"])
    qua = tong = 0
    for tt, su, sd in dungDuoc:
        p = tt.get("pUp")
        if p is None:
            continue
        for ben, pp, so in (("UP", p, su), ("DOWN", 1.0 - p, sd)):
            if not so.dung_duoc:
                continue
            ch = can(tt.get("ma") or "?", ben, "do", pp,
                     float(tt.get("batDinh") or 0.02), so, 100.0)
            if ch is None:
                continue
            tong += 1
            if ch.netEdge >= nguong:
                qua += 1
    print()
    print(f"  3. LỢI THẾ RÒNG   {qua:,}/{tong:,} cơ hội qua sàng "
          f"(ngưỡng {nguong:g})")
    print()
    print(f"  {len(dong):,} dòng là RẤT ÍT — đây là ước lượng, không phải")
    print("  kết luận. Đường tới Polymarket chập chờn chứ không đứt hẳn, nên")
    print("  cứ để runtime chạy: mỗi lúc mạng thông là băng dày thêm, và")
    print("  phép đo này sắc thêm.")
    print("=" * 76 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
