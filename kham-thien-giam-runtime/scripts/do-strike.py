"""STRIKE đặt ở đâu? Chấm điểm chính chợ — có ĐỐI CHỨNG tỉ lệ nền.

    python scripts/do-strike.py
    TAU=150 N=800 python scripts/do-strike.py

Slug là `<coin>-updown-5m-T`. Runtime hiểu: cửa đặt cược [T−300, T], khung
quan sát [T, T+300], strike là giá lúc T−300. Ba giả thuyết:

    (A) UP thắng ⟺ giá(T+300) > giá(T−300)   ← runtime đang dùng
    (B) UP thắng ⟺ giá(T+300) > giá(T)       ← strike ở đầu khung quan sát
    (C) UP thắng ⟺ giá(T)     > giá(T−300)   ← slug đặt tên theo lúc KẾT THÚC

Lấy báo giá CUỐI CÙNG của cửa đặt cược làm dự đoán của chợ, rồi chấm
điểm chợ trên từng định nghĩa. Chợ có thể sai lẻ tẻ nhưng nó không sai
có hệ thống về chính cái nó đang bán.

## Đối chứng TỈ LỆ NỀN — bản đầu của phép đo này đã ngã ở đúng đây

Bản đầu so điểm Brier thô và kết luận (B) thắng: 0,2602 với 69,3% đúng
hướng, so với (A) 0,3632. Nhưng giá chợ trung vị là 0,328 và mẫu lấy là
300 slug ĐẦU BẢNG CHỮ CÁI — tức một khối thời gian liền nhau. Nếu quãng
ấy thị trường đi xuống thì UP thua chừng 69% số lần, và một cái chợ yết
thấp trông "chính xác 69%" mà không cần biết gì cả.

Nói cách khác: điểm Brier thô đo LẪN tỉ lệ nền với kỹ năng. Cùng đúng
một cái bẫy mà `do_tre.py` phải dựng phép đối chứng ngẫu nhiên để tránh.

Nên bản này:
  1. lấy mẫu NGẪU NHIÊN trải cả băng, không lấy một khối liền;
  2. khai tỉ lệ nền của từng định nghĩa;
  3. chấm bằng ĐIỂM KỸ NĂNG — Brier của chợ so với Brier của một kẻ chỉ
     biết yết đúng tỉ lệ nền. Dương là chợ biết thứ gì đó; âm là không.
  4. bootstrap CÓ CẶP trên chênh lệch, vì cùng một slug cho cả ba.
"""
from __future__ import annotations

import os
import random
import statistics
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402

from kham import tham_so  # noqa: E402

# Không cờ nào — nhưng vẫn phải TỪ CHỐI cờ lạ. Một cờ gõ sai bị
# nuốt im lặng thì phép đo chạy ở cấu hình khác cấu hình người ta
# yêu cầu, rồi in ra một báo cáo trông hoàn toàn hợp lệ.
tham_so.doc({}, ten='do-strike.py')
from kham.bang import NguonKhung  # noqa: E402
from kham.chay_lai import dung_so  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.ket_qua import moc_tu_slug  # noqa: E402
from kham.nguon import nguon  # noqa: E402

NEN = {t["ma"]: t.get("nen") for t in CONFIG["thiTruong"]}
TAU_TOI_DA = float(os.environ.get("TAU", "150"))
TOI_DA_SLUG = int(os.environ.get("N", "500"))
HAT = int(os.environ.get("HAT", "20260829"))


def brier(du, that) -> float:
    return sum((p - t) ** 2 for p, t in zip(du, that)) / max(1, len(du))


def ky_nang(du, that) -> tuple[float, float, float]:
    """(Brier chợ, Brier kẻ chỉ biết tỉ lệ nền, điểm kỹ năng)."""
    n = max(1, len(that))
    nen = sum(that) / n
    bCho = brier(du, that)
    bNen = brier([nen] * n, that)
    kn = 0.0 if bNen <= 0 else (bNen - bCho) / bNen
    return bCho, bNen, kn


def main() -> int:
    cuoi: dict[str, tuple[float, str]] = {}
    tauNhoNhat: dict[str, float] = {}
    for k in NguonKhung(None):
        for tt in (k.get("thiTruong") or []):
            slug, ma = tt.get("slug"), tt.get("ma")
            tau = tt.get("conLaiGiay")
            if not slug or not ma or not isinstance(tau, (int, float)):
                continue
            if tau > TAU_TOI_DA:
                continue
            if slug in tauNhoNhat and tauNhoNhat[slug] <= tau:
                continue
            so = dung_so((tt.get("so") or {}).get("UP"), ma, "UP")
            if so is None or not so.dung_duoc:
                continue
            g = so.giua
            if g is None:
                continue
            tauNhoNhat[slug] = float(tau)
            cuoi[slug] = (float(g), ma)

    print()
    print("=" * 74)
    print("  STRIKE ĐẶT Ở ĐÂU — chấm điểm chợ, có đối chứng tỉ lệ nền")
    print("=" * 74)
    print(f"  {len(cuoi):,} slug có báo giá trong {TAU_TOI_DA:.0f}s cuối cửa "
          "đặt cược.")
    if not cuoi:
        print("  Không đủ mẫu. Không kết luận gì.\n")
        return 0

    # Mẫu NGẪU NHIÊN trải cả băng. Lấy khối liền là mời tỉ lệ nền vào
    # đóng vai kỹ năng.
    rd = random.Random(HAT)
    dsach = sorted(cuoi.items())
    rd.shuffle(dsach)

    du: list[float] = []
    that = {"A": [], "B": [], "C": []}
    bo = 0
    for i, (slug, (g, ma)) in enumerate(dsach[:TOI_DA_SLUG], 1):
        cap = NEN.get(ma)
        T = moc_tu_slug(slug)
        if not cap or T is None:
            bo += 1
            continue
        truoc = nguon.gia_dong_khung(cap, T - 300_000.0)
        giua = nguon.gia_dong_khung(cap, T)
        sau = nguon.gia_dong_khung(cap, T + 300_000.0)
        if None in (truoc, giua, sau):
            bo += 1
            continue
        if (abs(sau - truoc) < 1e-9 or abs(sau - giua) < 1e-9
                or abs(giua - truoc) < 1e-9):
            bo += 1
            continue
        du.append(g)
        that["A"].append(1 if sau > truoc else 0)
        that["B"].append(1 if sau > giua else 0)
        that["C"].append(1 if giua > truoc else 0)
        if i % 100 == 0:
            print(f"    {i} slug…", flush=True)

    n = len(du)
    print(f"  chấm được {n:,} slug (bỏ {bo:,})")
    if n < 80:
        print("  Chưa đủ mẫu để tách các giả thuyết. ĐỪNG chốt.\n")
        return 0

    print()
    print(f"    giá chợ: trung vị {statistics.median(du):.3f} · "
          f"trung bình {sum(du)/n:.3f}")
    print()
    print("                             tỉ lệ nền   Brier chợ   Brier nền   "
          "ĐIỂM KỸ NĂNG")
    bang = []
    for ten, nhan in (("A", "giá(T+300)>giá(T−300)"),
                      ("B", "giá(T+300)>giá(T)    "),
                      ("C", "giá(T)    >giá(T−300)")):
        t = that[ten]
        bCho, bNen, kn = ky_nang(du, t)
        bang.append((ten, kn, bCho, t))
        print(f"    ({ten}) {nhan}   {sum(t)/n:>7.1%}   {bCho:>9.4f}   "
              f"{bNen:>9.4f}   {kn:>+9.1%}")
    print()
    print("    Điểm kỹ năng = 1 − Brier(chợ)/Brier(kẻ chỉ biết tỉ lệ nền).")
    print("    Dương: chợ biết thứ gì đó ngoài tỉ lệ nền. Âm: KHÔNG.")
    print()

    bang.sort(key=lambda x: -x[1])
    nhat, nhi = bang[0], bang[1]

    # Bootstrap CÓ CẶP trên chênh lệch Brier giữa quán quân và á quân.
    rd2 = random.Random(HAT + 1)
    hieu = [(p - t2) ** 2 - (p - t1) ** 2
            for p, t1, t2 in zip(du, nhat[3], nhi[3])]
    lan = sorted(sum(hieu[rd2.randrange(n)] for _ in range(n)) / n
                 for _ in range(4000))
    thap, cao = lan[int(0.025 * len(lan))], lan[int(0.975 * len(lan))]
    print(f"    Quán quân ({nhat[0]}) kỹ năng {nhat[1]:+.1%} · "
          f"á quân ({nhi[0]}) {nhi[1]:+.1%}")
    print(f"    chênh Brier, khoảng tin 95% có cặp: [{thap:+.4f}, {cao:+.4f}]")
    print()
    print("  ĐỌC KẾT LUẬN:")
    if nhat[1] <= 0.02:
        print(f"    KHÔNG giả thuyết nào có điểm kỹ năng đáng kể "
              f"(cao nhất {nhat[1]:+.1%}).")
        print("    Chợ không tiên đoán được định nghĩa nào tốt hơn một kẻ chỉ")
        print("    biết tỉ lệ nền — nên phép đo này KHÔNG chốt được strike.")
        print("    Đừng đem con số lãi nào của phiên phát lại ra dùng.")
    elif thap <= 0:
        print(f"    ({nhat[0]}) và ({nhi[0]}) không tách nhau đủ. ĐỪNG chốt.")
    elif nhat[0] == "A":
        print("    `giaMo` ĐÚNG và `ket_thuc_tu_slug` ĐÚNG.")
    elif nhat[0] == "B":
        print("    `giaMo` SAI: runtime lấy giá lúc T−300, chợ tính từ T.")
    else:
        print("    `giaMo` ĐÚNG nhưng `ket_thuc_tu_slug` SAI: khung ăn thua")
        print("    kết thúc ở T, không phải T+300.")
    print("=" * 74)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
