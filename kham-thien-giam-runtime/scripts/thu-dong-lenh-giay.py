"""Dòng lệnh ở nhịp GIÂY có thêm thông tin không? Câu `thu-dong-lenh.py` để lại.

    python scripts/thu-dong-lenh-giay.py --ngay=5
    python scripts/thu-dong-lenh-giay.py --ngay=5 --ma=ETH_5M

## Vì sao có script này

`do-tran-mo-hinh.py` chốt: mô hình đã vắt 98,9% thông tin nằm trong `p`,
và mọi phép nắn chỉ là biến đổi đơn điệu của `p` nên không phép nào vượt
được cái trần ấy. Muốn khá hơn thì phải thêm THÔNG TIN.

`thu-dong-lenh.py` thử nguồn thông tin rẻ nhất — mất cân bằng dòng lệnh
tính trên 5 nến 1 PHÚT — và trả lời KHÔNG: khoảng tin [-0,001469,
+0,000102] chứa 0. Nhưng nó để lại đúng một câu:

    "Muốn tìm alpha ở dòng lệnh thì phải xuống nhịp NHỎ HƠN NHIỀU so
     với 1 phút."

Lý do là thật chứ không phải cái cớ: một cửa sổ 5 phút thì 5 nến phút
gần nhất trải suốt cả khung, nên "áp lực mua bán" đo trên đó gần như đã
nằm trọn trong chính giá — mà giá thì `p` biết rồi. Áp lực CHƯA vào giá
là áp lực của mấy giây cuối.

Binance cho nến 1 GIÂY, kèm `takerBuyBaseVolume`. Đó là thứ này đo.

## Bốn ứng viên, và vì sao phải siết biên

Bốn cửa sổ: 5, 15, 30, 60 giây trước lúc quyết định. Quét bốn ứng viên
rồi lấy cái tốt nhất là bốn lần rút thăm, nên biên ở tập CHỌN siết theo
`hoc_offline.bien_theo_ung_vien` — cùng phép siết mà cổng tự nâng cấp
dùng. Tập CHỐT chỉ gật hay lắc.

## Ba chỗ dễ tự lừa, đã bịt

1. **Nhìn trộm tương lai.** Đặc trưng chỉ đọc nến có `openTime` trong
   `[t − W, t)` — nến mở lúc `t` đóng lúc `t+1`, nằm SAU lúc quyết
   định. Lệch một giây ở đây là đủ để mọi kết luận thành rác.
2. **Khối bootstrap.** Bốn lát τ của một khung chia chung MỘT kết quả,
   nên khối là MỐC KHUNG chứ không phải từng cặp.
3. **σ tự tính.** Dùng `hoc_offline.sigma_tai` — bộ ước chung. Một
   script kết luận về mô hình bằng σ khác σ của mô hình thì kết luận
   ấy nói về một cỗ máy không tồn tại.
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "số ngày nến 1 giây lấy về",
}, ten='thu-dong-lenh-giay.py')

from kham.config import CONFIG  # noqa: E402
from kham.ban_thu import _brier  # noqa: E402
from kham.dinh_gia import dinh_gia  # noqa: E402
from kham.hoc_offline import (bien_theo_ung_vien, khoang_tin_theo_khoi,  # noqa: E402
                              cua_so_sigma, quen_sigma, sigma_tai)

MA = CO.lay("ma", "BTC_5M")
SO_NGAY = float(CO.lay("ngay", "5"))
GIAY = 1000
PHUT = 60_000
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
CUA_SO = (5, 15, 30, 60)          # giây, bốn ứng viên
CHIA_HOC, CHIA_CHON = 0.50, 0.75
O_P, O_LECH = 10, 5


def nen_1s(cap: str, tuMs: int, denMs: int) -> dict:
    """{mốc giây ms: (đóng, khối lượng, khối lượng mua chủ động)}.

    Lấy theo lô 1000 nến. Một lô hỏng KHÔNG được giết cả lượt, nhưng
    cũng không được biến mất: đếm lại và khai ra, vì lỗ hổng dữ liệu
    làm đặc trưng cửa sổ ngắn trả None chứ không sai — và "ít mẫu hơn
    dự tính" là thứ phải nhìn thấy chứ không phải đoán.
    """
    ra: dict = {}
    hong = 0
    goc = CONFIG["nguon"]["binanceSpot"]
    t = int(tuMs)
    tong = max(1, (denMs - tuMs) // (1000 * GIAY))
    lo = 0
    while t < denMs:
        u = (f"{goc}/api/v3/klines?symbol={cap}&interval=1s"
             f"&startTime={t}&limit=1000")
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                d = json.load(r)
        except (urllib.error.URLError, OSError, ValueError):
            hong += 1
            t += 1000 * GIAY
            continue
        if not d:
            break
        for k in d:
            try:
                ra[int(k[0])] = (float(k[4]), float(k[5]), float(k[9]))
            except (TypeError, ValueError, IndexError):
                continue
        t = int(d[-1][0]) + GIAY
        lo += 1
        if lo % 60 == 0:
            print(f"    …{lo}/{tong} lô · {len(ra):,} giây", flush=True)
    if hong:
        print(f"    {hong} lô hỏng, bỏ qua")
    return ra


def luoi_phut(g1s: dict) -> dict:
    """{mốc phút ms: giá đóng phút} — dựng từ nến giây.

    Giá đóng của phút `m` là giá đóng của nến GIÂY mở lúc `m − 1s`.
    Lấy nhầm nến mở lúc `m` là lấy giá của phút SAU.
    """
    ra = {}
    for t, v in g1s.items():
        if t % PHUT == PHUT - GIAY:
            ra[t + GIAY] = v[0]
    return ra


def lech(g1s: dict, t: int, cuaSoGiay: int) -> float | None:
    """Mất cân bằng dòng lệnh trên `[t − cuaSo, t)`. KHÔNG chạm tới `t`.

    Nến mở lúc `t` đóng lúc `t + 1s`, tức nó chứa giao dịch xảy ra SAU
    lúc quyết định. Đọc nó là nhìn trộm tương lai, và nó sẽ cho một kết
    quả rất đẹp.
    """
    tong = mua = 0.0
    thieu = 0
    for i in range(1, cuaSoGiay + 1):
        n = g1s.get(t - i * GIAY)
        if n is None:
            thieu += 1
            continue
        tong += n[1]
        mua += n[2]
    if thieu > cuaSoGiay // 5 or tong <= 0:
        return None
    return (2.0 * mua - tong) / tong


def _o(v: float, canh: list) -> int:
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

    het = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    tu = het - int(SO_NGAY * 24 * 3600 * 1000) - 1200 * GIAY
    print()
    print("=" * 76)
    print("  DÒNG LỆNH NHỊP GIÂY CÓ THÊM THÔNG TIN NGOÀI `p` KHÔNG")
    print("=" * 76)
    print(f"  {MA} ({cap}) · {SO_NGAY:g} ngày · lấy nến 1 GIÂY…", flush=True)

    g = nen_1s(cap, tu, het)
    if len(g) < 20_000:
        print(f"  chỉ lấy được {len(g):,} giây. Không đủ.\n")
        return 1
    lp = luoi_phut(g)
    print(f"  {len(g):,} giây · {len(lp):,} mốc phút")

    cuaSoSig = cua_so_sigma()
    mocs = [T for T in sorted(lp) if T % 300_000 == 0]
    quen_sigma()

    def dung(ms: list) -> list:
        ra = []
        for T in ms:
            K, het5 = lp.get(T), lp.get(T + 5 * PHUT)
            if K is None or het5 is None or abs(het5 - K) < 1e-12:
                continue
            sig = sigma_tai(lp, T, cuaSoSig, MA)
            if sig is None:
                continue
            thang = het5 > K
            for tau in LAT_CAT:
                t = T + int((300.0 - tau) * 1000.0)
                S = lp.get(t)
                if S is None or S <= 0:
                    continue
                gc = dinh_gia(MA, float(S), float(K), tau, sig)
                if gc is None:
                    continue
                lcs = [lech(g, t, w) for w in CUA_SO]
                if any(x is None for x in lcs):
                    continue
                # (p, thắng, lệch…, mốc): hai ô đầu đúng thứ tự
                # mà `ban_thu._brier` đọc — một bản `_brier` duy
                # nhất cho cả cung, không giữ bản sao.
                ra.append((gc.pUp, thang, *lcs, T))
        return ra

    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)
    hoc, chon, chot = dung(mocs[:a]), dung(mocs[a:b]), dung(mocs[b:])
    if min(len(hoc), len(chon), len(chot)) < 500:
        print(f"  chưa đủ cặp: {len(hoc)}/{len(chon)}/{len(chot)}.\n")
        return 1
    print(f"  HỌC {len(hoc):,} · CHỌN {len(chon):,} · CHỐT {len(chot):,} cặp")
    print()
    for i, w in enumerate(CUA_SO):
        v = sorted(x[2 + i] for x in hoc)
        print(f"    lệch {w:>2}s: trung vị {statistics.median(v):+.4f} · "
              f"d1 {v[len(v)//10]:+.4f} · d9 {v[-len(v)//10]:+.4f}")

    ps = sorted(x[0] for x in hoc)
    canhP = [ps[int((i + 1) * len(ps) / O_P) - 1] for i in range(O_P - 1)]

    def bang(capHoc: list, chiSo: int | None, canhL: list) -> dict:
        b_: dict = {}
        for x in capHoc:
            k = (_o(x[0], canhP),
                 _o(x[chiSo], canhL) if chiSo is not None else 0)
            d = b_.setdefault(k, [0, 0])
            d[0] += 1 if x[1] else 0
            d[1] += 1
        return b_

    def ap(b_: dict, x, chiSo: int | None, canhL: list) -> float:
        k = (_o(x[0], canhP), _o(x[chiSo], canhL) if chiSo is not None else 0)
        d = b_.get(k)
        if not d or d[1] < 20:
            d = None
            for kk, dd in b_.items():          # lùi về ô `p` gộp mọi lệch
                if kk[0] == k[0]:
                    d = [(d[0] + dd[0]), (d[1] + dd[1])] if d else list(dd)
            if not d or d[1] == 0:
                return x[0]
        return d[0] / d[1]

    bGoc = bang(hoc, None, [])
    tran = {"chon": _brier([(ap(bGoc, x, None, []), x[1]) for x in chon]),
            "chot": _brier([(ap(bGoc, x, None, []), x[1]) for x in chot])}

    print()
    print(f"    {'bảng':<16}{'CHỌN':>10}{'CHỐT':>10}")
    print(f"    {'`p` một mình':<16}{tran['chon']:>10.5f}{tran['chot']:>10.5f}")

    bien = bien_theo_ung_vien(len(CUA_SO))
    ket = []
    for i, w in enumerate(CUA_SO):
        ls = sorted(x[2 + i] for x in hoc)
        canhL = [ls[int((j + 1) * len(ls) / O_LECH) - 1]
                 for j in range(O_LECH - 1)]
        b_ = bang(hoc, 2 + i, canhL)
        cc = _brier([(ap(b_, x, 2 + i, canhL), x[1]) for x in chon])
        ct = _brier([(ap(b_, x, 2 + i, canhL), x[1]) for x in chot])
        ket.append((w, cc, ct, canhL, b_, i))
        print(f"    {'`p` + lệch ' + str(w) + 's':<16}{cc:>10.5f}{ct:>10.5f}")

    tot = min(ket, key=lambda r: r[1])
    w, cc, ct, canhL, b_, i = tot
    can = tran["chon"] * bien
    print()
    print(f"  ứng viên khá nhất ở CHỌN: lệch {w}s "
          f"({cc:.5f}, cần ≤ {can:.5f}, biên {bien:.4f} sau "
          f"{len(CUA_SO)} ứng viên)")

    if cc > can:
        print()
        print("  TRẢ LẠI ở tập CHỌN: chưa vượt biên.")
        print("  Dòng lệnh nhịp giây cũng KHÔNG nói thêm gì ngoài `p`.")
        print("=" * 76)
        return 0

    hieu = [((ap(b_, x, 2 + i, canhL) - (1.0 if x[1] else 0.0)) ** 2
             - (ap(bGoc, x, None, []) - (1.0 if x[1] else 0.0)) ** 2)
            for x in chot]
    thap, cao, soK = khoang_tin_theo_khoi(hieu, [x[-1] for x in chot])
    print(f"  CHỐT: {tran['chot']:.5f} → {ct:.5f}")
    print(f"  khoảng tin 95% theo KHUNG: [{thap:+.6f}, {cao:+.6f}]  "
          f"({soK} khung)")
    print()
    if cao < 0:
        print(f"  NHẬN: lệch dòng lệnh {w}s có thêm thông tin thật.")
    else:
        print("  KHÔNG đủ bằng chứng ở tập CHỐT: khoảng tin chứa 0.")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
