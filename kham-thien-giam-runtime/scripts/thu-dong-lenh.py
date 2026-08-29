"""DÒNG LỆNH có thêm thông tin không? Hướng duy nhất còn lại, và Binance cho không.

    python scripts/thu-dong-lenh.py --ngay=20

`do-tran-mo-hinh.py` chốt: mô hình đã vắt 98,9% thông tin nằm trong `p`,
và mọi phép nắn đều là biến đổi đơn điệu của `p` nên không phép nào vượt
được cái trần ấy. Kết luận: muốn khá hơn thì phải thêm THÔNG TIN, không
phải thêm tham số.

Ba nguồn thông tin đã nêu — sổ lệnh, dòng lệnh, độ trễ liên sàn — tưởng
như đều nằm sau cánh cửa Polymarket đang đóng. Nhưng KHÔNG: nến Binance
đã kèm sẵn một thứ mà mô hình chưa hề dùng.

    n[5]  khối lượng cả nến
    n[9]  khối lượng phía NGƯỜI MUA CHỦ ĐỘNG (taker buy)

    lệch dòng lệnh = (2·mua_chủ_động − tổng) / tổng    ∈ [−1, +1]

Đây là mất cân bằng dòng lệnh, thước cổ điển nhất của áp lực mua/bán
ngắn hạn. Nó KHÔNG nằm trong `p` — `p` chỉ biết giá và σ.

## Phép thử phải trả lời đúng một câu

Không phải "lệch dòng lệnh có tương quan với kết quả không" — gần như
thứ gì cũng có tương quan chút ít. Câu đúng là:

    **Nó có thêm thông tin NGOÀI thứ `p` đã biết không?**

Nên chấm ứng viên hai chiều `(p, lệch)` so với TRẦN của `p` một mình.
Vượt được trần ấy trên dữ liệu CHƯA THẤY thì đó là thông tin mới thật;
không vượt thì nó chỉ đang nói lại điều `p` đã nói.

Ba tập tách theo THỜI GIAN, y hệt mọi phép thử khác ở cung này.
"""
from __future__ import annotations

import math
import random
import statistics
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.dinh_gia import dinh_gia  # noqa: E402
from kham.nguon import nguon  # noqa: E402

PHUT = 60_000.0
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
CHIA_HOC, CHIA_CHON = 0.50, 0.75
O_P, O_LECH = 8, 3          # 8 ô cho p × 3 ô cho lệch dòng lệnh


CO = tham_so.doc({
    "cuaso": "cửa sổ σ, giây",
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "số ngày băng/nến lấy về",
}, ten='thu-dong-lenh.py')


SO_NGAY = int(CO.lay("ngay", "20"))
MA = CO.lay("ma", "BTC_5M")
CUA_SO = float(CO.lay("cuaso", "900"))


def nen_day_du(cap, tuMs, soNen) -> dict:
    """{mốc đóng: (đóng, khối lượng, mua chủ động)}."""
    moc = int(tuMs // PHUT * PHUT)
    ra: dict = {}
    con = soNen
    while con > 0:
        lo = min(1000, con)
        d = nguon._lay("binance-kline",
                       f"{CONFIG['nguon']['binanceSpot']}/api/v3/klines",
                       {"symbol": cap, "interval": "1m",
                        "startTime": moc, "limit": lo})
        if not isinstance(d, list) or not d:
            break
        for n in d:
            try:
                ra[int(n[0]) + int(PHUT)] = (float(n[4]), float(n[5]),
                                             float(n[9]))
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


def _sigma(oh, T, soNen):
    gs = [oh.get(T - i * int(PHUT)) for i in range(soNen + 1)]
    if any(g is None or g[0] <= 0 for g in gs):
        return None
    c = [g[0] for g in gs][::-1]
    r = [math.log(c[i + 1] / c[i]) for i in range(len(c) - 1)]
    sd = statistics.pstdev(r)
    return (sd / math.sqrt(60.0)) if sd > 0 else None


def _lech(oh, t, soNen: int = 5):
    """Lệch dòng lệnh trên `soNen` nến gần nhất tính tới `t`."""
    tong = mua = 0.0
    for i in range(soNen):
        n = oh.get(t - i * int(PHUT))
        if n is None:
            return None
        tong += n[1]
        mua += n[2]
    if tong <= 0:
        return None
    return (2.0 * mua - tong) / tong


def _brier1(q, t):
    return (q - (1.0 if t else 0.0)) ** 2


def _brier(cap):
    return sum(_brier1(q, t) for q, t in cap) / max(1, len(cap))


def _o(v, canh):
    for i, c in enumerate(canh):
        if v <= c:
            return i
    return len(canh)


def main() -> int:
    cap = next((t.get("nen") for t in CONFIG["thiTruong"]
                if t.get("ma") == MA), None)
    if not cap:
        print(f"\n  Không có market `{MA}`.\n")
        return 1
    soNen = max(2, int(round(CUA_SO / 60.0)))
    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    tong = SO_NGAY * 24 * 60 + soNen + 20
    print()
    print("=" * 76)
    print("  DÒNG LỆNH CÓ THÊM THÔNG TIN NGOÀI `p` KHÔNG")
    print("=" * 76)
    print(f"  {MA} ({cap}) · {SO_NGAY} ngày · lấy {tong:,} nến…", flush=True)
    oh = nen_day_du(cap, hetMs - tong * PHUT, tong)
    if len(oh) < 1200:
        print(f"  chỉ lấy được {len(oh)} nến.\n")
        return 1

    mocs = [T for T in sorted(oh) if T % 300_000 == 0]
    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)

    def dung(ms):
        ra = []
        for T in ms:
            n0, n5 = oh.get(T), oh.get(T + 5 * int(PHUT))
            if n0 is None or n5 is None or abs(n5[0] - n0[0]) < 1e-12:
                continue
            sig = _sigma(oh, T, soNen)
            if sig is None:
                continue
            thang = n5[0] > n0[0]
            for tau in LAT_CAT:
                t = T + int((300.0 - tau) * 1000.0)
                if t % int(PHUT):
                    continue
                n = oh.get(t)
                if n is None or n[0] <= 0:
                    continue
                lc = _lech(oh, t)
                if lc is None:
                    continue
                gc = dinh_gia(MA, float(n[0]), float(n0[0]), tau, sig)
                if gc is not None:
                    ra.append((gc.pUp, lc, thang, T))
        return ra

    hoc, chon, chot = dung(mocs[:a]), dung(mocs[a:b]), dung(mocs[b:])
    if min(len(hoc), len(chon), len(chot)) < 1000:
        print("  chưa đủ cặp.\n")
        return 1
    print(f"  HỌC {len(hoc):,} · CHỌN {len(chon):,} · CHỐT {len(chot):,} cặp")

    lcs = sorted(x[1] for x in hoc)
    print(f"  lệch dòng lệnh: trung vị {statistics.median(lcs):+.4f} · "
          f"d1 {lcs[len(lcs)//10]:+.4f} · d9 {lcs[-len(lcs)//10]:+.4f}")

    # Ô của `p` theo THỨ HẠNG trên tập HỌC; ô của `lệch` cũng vậy.
    ps = sorted(x[0] for x in hoc)
    canhP = [ps[int((i + 1) * len(ps) / O_P) - 1] for i in range(O_P - 1)]
    canhL = [lcs[int((i + 1) * len(lcs) / O_LECH) - 1] for i in range(O_LECH - 1)]

    def khop(cap_, dungLech: bool):
        b_: dict = {}
        for p, lc, t, *_ in cap_:
            k = (_o(p, canhP), _o(lc, canhL) if dungLech else 0)
            d = b_.setdefault(k, [0, 0])
            d[0] += 1 if t else 0
            d[1] += 1
        return b_

    def cham(cap_, b_, dungLech: bool):
        ra = []
        for p, lc, t, *_ in cap_:
            k = (_o(p, canhP), _o(lc, canhL) if dungLech else 0)
            d = b_.get(k)
            if d is None or d[1] < 30:
                # Ô thưa thì LÙI VỀ `p` một mình, đừng đoán bằng vài mẫu.
                d = b_.get((k[0], 0)) or b_.get(k)
            ra.append(((d[0] / d[1]) if d and d[1] else p, t))
        return ra

    bP = khop(hoc, False)
    bPL = khop(hoc, True)

    print()
    print("    bảng            CHỌN       CHỐT")
    kq = {}
    for ten, b_, dl in (("`p` một mình", bP, False),
                        ("`p` + dòng lệnh", bPL, True)):
        c1 = _brier(cham(chon, b_, dl))
        c2 = _brier(cham(chot, b_, dl))
        kq[ten] = (c1, c2, cham(chot, b_, dl))
        print(f"    {ten:<16} {c1:.5f}    {c2:.5f}")

    g, r = kq["`p` một mình"], kq["`p` + dòng lệnh"]
    print()
    print(f"    chênh CHỌN {g[0]-r[0]:+.6f} · CHỐT {g[1]-r[1]:+.6f}")

    gs = [_brier1(q, t) for q, t in g[2]]
    rs = [_brier1(q, t) for q, t in r[2]]
    hieu = [x - y for x, y in zip(gs, rs)]
    n = len(hieu)
    # Lấy lại theo KHUNG, không theo cặp: bốn lát cắt của một khung
    # chia chung MỘT kết quả. Bootstrap theo cặp cho khoảng tin hẹp hơn
    # 2,18 lần — và trên một kết luận biên, đó là khác biệt giữa "nằm
    # hẳn một bên" với "chứa 0".
    from kham.hoc_offline import khoang_tin_theo_khoi
    mocChot = [x[-1] for x in chot]
    thap, cao, soK = khoang_tin_theo_khoi(hieu, mocChot)
    print(f"    khoảng tin 95% theo KHUNG trên CHỐT: "
          f"[{thap:+.6f}, {cao:+.6f}]  ({soK} khung)")
    print()
    if thap > 0:
        print("  DÒNG LỆNH CÓ THÔNG TIN MỚI. Đây là hướng đúng để đi tiếp:")
        print("  nó vượt được cái trần của `p` một mình, tức là nó nói thứ")
        print("  `p` không nói. Bước sau: đưa nó vào `dinh_gia` như một tín")
        print("  hiệu phụ có TRẦN dịch chuyển, đúng chỗ `TinMoi` đã chừa sẵn.")
    elif cao < 0:
        print("  DÒNG LỆNH LÀM TỆ ĐI. Đừng đưa vào.")
    else:
        print("  KHÔNG đủ bằng chứng: khoảng tin chứa 0. Dòng lệnh ở nhịp")
        print("  1 phút không nói thêm gì ngoài thứ `p` đã biết — hợp lý,")
        print("  vì giá đã gói phần lớn thông tin ấy rồi. Muốn tìm alpha ở")
        print("  dòng lệnh thì phải xuống nhịp NHỎ HƠN NHIỀU so với 1 phút.")
    print("=" * 76 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
