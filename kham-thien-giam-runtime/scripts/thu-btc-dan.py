"""BTC có DẪN các đồng khác không? Nguồn thông tin cuối lấy được từ Binance.

    python scripts/thu-btc-dan.py --ma=ETH_5M --ngay=20

`do-tran-mo-hinh.py` chốt: mô hình đã vắt 98,9% thông tin nằm trong `p`;
muốn khá hơn phải thêm THÔNG TIN. `thu-dong-lenh.py` thử dòng lệnh nhịp
1 phút và nó LÀM TỆ ĐI. Còn một nguồn nữa, và nó không cần chợ:

    **BTC đã đi đâu trong chính cửa sổ này?**

Giả thuyết: trong một khung 5 phút của ETH, nếu BTC đã nhích lên rõ mà
ETH chưa theo kịp, thì ETH có xu hướng đuổi theo — nên P(ETH lên) cao
hơn giá của chính ETH hàm ý. Đây là thông tin KHÔNG nằm trong `p`: `p`
chỉ biết giá ETH và σ của ETH.

Đặc trưng, đo tại đúng thời điểm quyết định `t` trong khung [T, T+300]:

    lệch dẫn = (log-return BTC từ T tới t) − (log-return ĐỒNG NÀY từ T tới t)
               rồi chuẩn hoá theo σ của chính khung ấy

Dương lớn = BTC đã chạy mà đồng này chưa theo. Nếu có hiệu ứng dẫn thì ô
ấy phải thắng nhiều hơn mức `p` nói.

## Vẫn đúng một câu hỏi

Không phải "BTC có tương quan với ETH không" — hiển nhiên có, và `p` đã
gói phần đó qua chính giá ETH. Câu đúng: **lệch dẫn có nói thêm gì ngoài
thứ `p` đã biết không.** Nên chấm bảng hai chiều so với bảng `p` một
mình, ba tập tách theo THỜI GIAN, khoảng tin có cặp trên tập CHỐT.
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
from kham.ban_thu import _brier  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.dinh_gia import dinh_gia  # noqa: E402
from kham.nguon import nguon  # noqa: E402

PHUT = 60_000.0
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
CHIA_HOC, CHIA_CHON = 0.50, 0.75
O_P, O_DAN = 8, 3


CO = tham_so.doc({
    "cuaso": "cửa sổ σ, giây",
    "dan": "dan",
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "số ngày băng/nến lấy về",
}, ten='thu-btc-dan.py')


SO_NGAY = int(CO.lay("ngay", "20"))
MA = CO.lay("ma", "ETH_5M")
CUA_SO = float(CO.lay("cuaso", "900"))
DAN = CO.lay("dan", "BTCUSDT")


def nen(cap, tuMs, soNen) -> dict:
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
                ra[int(n[0]) + int(PHUT)] = float(n[4])
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


def _sigma(oh, T, soNen):
    gs = [oh.get(T - i * int(PHUT)) for i in range(soNen + 1)]
    if any(g is None or g <= 0 for g in gs):
        return None
    c = gs[::-1]
    r = [math.log(c[i + 1] / c[i]) for i in range(len(c) - 1)]
    sd = statistics.pstdev(r)
    return (sd / math.sqrt(60.0)) if sd > 0 else None


def _brier1(q, t):
    return (q - (1.0 if t else 0.0)) ** 2


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
    if cap == DAN:
        print(f"\n  `{MA}` chính là đồng dẫn. Chọn market khác.\n")
        return 1
    soNen = max(2, int(round(CUA_SO / 60.0)))
    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    tong = SO_NGAY * 24 * 60 + soNen + 20
    print()
    print("=" * 76)
    print(f"  {DAN} CÓ DẪN {cap} KHÔNG — thông tin ngoài `p`")
    print("=" * 76)
    print(f"  {MA} · {SO_NGAY} ngày · lấy {tong:,} nến × 2…", flush=True)
    oh = nen(cap, hetMs - tong * PHUT, tong)
    ob = nen(DAN, hetMs - tong * PHUT, tong)
    if len(oh) < 1200 or len(ob) < 1200:
        print(f"  chỉ lấy được {len(oh)} / {len(ob)} nến.\n")
        return 1

    mocs = [T for T in sorted(oh) if T % 300_000 == 0]
    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)

    def dung(ms):
        ra = []
        for T in ms:
            K, het = oh.get(T), oh.get(T + 5 * int(PHUT))
            Kb = ob.get(T)
            if None in (K, het, Kb) or abs(het - K) < 1e-12:
                continue
            sig = _sigma(oh, T, soNen)
            if sig is None or sig <= 0:
                continue
            thang = het > K
            for tau in LAT_CAT:
                t = T + int((300.0 - tau) * 1000.0)
                if t % int(PHUT):
                    continue
                S, Sb = oh.get(t), ob.get(t)
                if S is None or Sb is None or S <= 0 or Sb <= 0:
                    continue
                troi = 300.0 - tau
                if troi <= 0:
                    continue
                # Lệch dẫn, chuẩn hoá theo σ của chính khung và quãng đã trôi.
                lech = ((math.log(Sb / Kb) - math.log(S / K))
                        / (sig * math.sqrt(troi)))
                gc = dinh_gia(MA, float(S), float(K), tau, sig)
                if gc is not None:
                    ra.append((gc.pUp, lech, thang, T))
        return ra

    hoc, chon, chot = dung(mocs[:a]), dung(mocs[a:b]), dung(mocs[b:])
    if min(len(hoc), len(chon), len(chot)) < 1000:
        print("  chưa đủ cặp.\n")
        return 1
    print(f"  HỌC {len(hoc):,} · CHỌN {len(chon):,} · CHỐT {len(chot):,} cặp")
    ds = sorted(x[1] for x in hoc)
    print(f"  lệch dẫn: trung vị {statistics.median(ds):+.4f} · "
          f"d1 {ds[len(ds)//10]:+.4f} · d9 {ds[-len(ds)//10]:+.4f}")

    ps = sorted(x[0] for x in hoc)
    canhP = [ps[int((i + 1) * len(ps) / O_P) - 1] for i in range(O_P - 1)]
    canhD = [ds[int((i + 1) * len(ds) / O_DAN) - 1] for i in range(O_DAN - 1)]

    def khop(cap_, dungDan):
        b_: dict = {}
        for p, lc, t, *_ in cap_:
            k = (_o(p, canhP), _o(lc, canhD) if dungDan else 0)
            d = b_.setdefault(k, [0, 0])
            d[0] += 1 if t else 0
            d[1] += 1
        return b_

    def cham(cap_, b_, dungDan):
        ra = []
        for p, lc, t, *_ in cap_:
            k = (_o(p, canhP), _o(lc, canhD) if dungDan else 0)
            d = b_.get(k)
            if d is None or d[1] < 30:
                d = b_.get((k[0], 0)) or d
            ra.append(((d[0] / d[1]) if d and d[1] else p, t))
        return ra

    bP, bPD = khop(hoc, False), khop(hoc, True)
    print()
    print("    bảng            CHỌN       CHỐT")
    kq = {}
    for ten, b_, dd in (("`p` một mình", bP, False),
                        (f"`p` + lệch dẫn", bPD, True)):
        kq[ten] = (_brier(cham(chon, b_, dd)), _brier(cham(chot, b_, dd)),
                   cham(chot, b_, dd))
        print(f"    {ten:<16} {kq[ten][0]:.5f}    {kq[ten][1]:.5f}")

    g = kq["`p` một mình"]
    r = kq["`p` + lệch dẫn"]
    hieu = [_brier1(*x) - _brier1(*y) for x, y in zip(g[2], r[2])]
    n = len(hieu)
    # Lấy lại theo KHUNG, không theo cặp: bốn lát cắt của một khung
    # chia chung MỘT kết quả. Bootstrap theo cặp cho khoảng tin hẹp hơn
    # 2,18 lần — và trên một kết luận biên, đó là khác biệt giữa "nằm
    # hẳn một bên" với "chứa 0".
    from kham.hoc_offline import khoang_tin_theo_khoi
    mocChot = [x[-1] for x in chot]
    thap, cao, soK = khoang_tin_theo_khoi(hieu, mocChot)
    print()
    print(f"    chênh CHỌN {g[0]-r[0]:+.6f} · CHỐT {g[1]-r[1]:+.6f}")
    print(f"    khoảng tin 95% theo KHUNG trên CHỐT: "
          f"[{thap:+.6f}, {cao:+.6f}]  ({soK} khung)")
    print()
    if thap > 0:
        print(f"  {DAN} CÓ DẪN — và nó nói thứ `p` không nói. Đây là thông")
        print("  tin mới thật, và là hướng đúng: đưa vào `dinh_gia` như tín")
        print("  hiệu phụ CÓ TRẦN dịch chuyển, đúng chỗ `TinMoi` chừa sẵn.")
    elif cao < 0:
        print(f"  {DAN} làm TỆ ĐI. Đừng đưa vào.")
    else:
        print("  KHÔNG đủ bằng chứng: khoảng tin chứa 0. Giá của chính đồng")
        print("  này đã gói phần lớn chuyện BTC làm gì — đúng như một chợ")
        print("  hiệu quả phải thế.")
    print("=" * 76 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
