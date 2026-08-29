"""Bộ ước σ nào tốt nhất? Chấm bằng kết quả thật, không tin sách.

    python scripts/thu-uoc-sigma.py --ngay=20

Bảng hiệu chỉnh và vòng tự nâng cấp đều chỉ về cùng một chỗ: **σ là
nguồn sai lớn nhất của mô hình**. Mô hình quá tự tin ở hai đuôi, và cửa
sổ ước σ vặn từ 300s lên 900s là thay đổi có ích nhất từng đo được.

Nhưng cả hai lần đó ta chỉ vặn CỬA SỔ. Bản thân bộ ước vẫn là loại thô
nhất có thể: độ lệch chuẩn của log-return giá ĐÓNG. Nó vứt đi ba phần tư
thông tin mỗi cây nến — cao, thấp, mở đều bị bỏ.

Bốn ứng viên, tất cả dùng đúng dữ liệu đã có:

    dong-dong    độ lệch chuẩn log-return giá đóng      (đang dùng)
    ewma         như trên nhưng trọng số suy giảm        nhạy hơn với đổi chế độ
    parkinson    từ (cao/thấp) — lý thuyết nói ~5× hiệu quả hơn
    garman-klass từ (cao, thấp, mở, đóng) — ~7×

Lý thuyết nói Parkinson và Garman–Klass hiệu quả hơn hẳn. Lý thuyết ấy
giả định khuếch tán liên tục, không nhảy, không khoảng trống — crypto 24/7
thì gần đúng hơn cổ phiếu, nhưng "gần đúng" không phải "đúng". Nên đo.

## Chấm y hệt vòng tự nâng cấp

Ba tập tách theo THỜI GIAN: HỌC khớp phép nắn, CHỌN xếp hạng, CHỐT chỉ
gật hay lắc. Bộ ước là một lựa chọn RỜI RẠC nên nó không có "một bước
nhỏ" để dò — càng phải có tập CHỐT, vì bốn ứng viên chọn trên một tập là
bốn cơ hội để tiếng ồn thắng.
"""
from __future__ import annotations

import math
import statistics
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.nan_lai import khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402

PHUT = 60_000.0
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
CHIA_HOC, CHIA_CHON = 0.50, 0.75
BIEN = 0.995


CO = tham_so.doc({
    "cuaso": "cửa sổ σ, giây",
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "số ngày băng/nến lấy về",
}, ten='thu-uoc-sigma.py')


SO_NGAY = int(CO.lay("ngay", "20"))
MA = CO.lay("ma", "BTC_5M")
CUA_SO = float(CO.lay("cuaso", "900"))


def nen_ohlc(cap: str, tuMs: float, soNen: int) -> dict:
    """{mốc đóng: (mở, cao, thấp, đóng)} — bốn giá, không chỉ giá đóng."""
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
                ra[int(n[0]) + int(PHUT)] = (float(n[1]), float(n[2]),
                                             float(n[3]), float(n[4]))
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


# ══════════════════════════════════════════════════════════════════════
#  BỐN BỘ ƯỚC — tất cả trả về σ MỖI GIÂY
# ══════════════════════════════════════════════════════════════════════

def _lay_nen(oh: dict, T: int, soNen: int):
    ns = [oh.get(T - i * int(PHUT)) for i in range(soNen)]
    if any(x is None or min(x) <= 0 for x in ns):
        return None
    return ns[::-1]


def uoc_dong_dong(oh, T, soNen):
    ns = _lay_nen(oh, T, soNen + 1)
    if ns is None or len(ns) < 3:
        return None
    c = [x[3] for x in ns]
    r = [math.log(c[i + 1] / c[i]) for i in range(len(c) - 1)]
    sd = statistics.pstdev(r)
    return (sd / math.sqrt(60.0)) if sd > 0 else None


def uoc_ewma(oh, T, soNen, lam: float = 0.94):
    ns = _lay_nen(oh, T, soNen + 1)
    if ns is None or len(ns) < 3:
        return None
    c = [x[3] for x in ns]
    r = [math.log(c[i + 1] / c[i]) for i in range(len(c) - 1)]
    v = r[0] ** 2
    for x in r[1:]:
        v = lam * v + (1.0 - lam) * x * x
    return (math.sqrt(v) / math.sqrt(60.0)) if v > 0 else None


def uoc_parkinson(oh, T, soNen):
    """σ² = mean[(ln(H/L))²] / (4·ln2). Dùng biên độ, không dùng giá đóng."""
    ns = _lay_nen(oh, T, soNen)
    if ns is None or len(ns) < 2:
        return None
    s = sum(math.log(h / l) ** 2 for _o, h, l, _c in ns) / len(ns)
    v = s / (4.0 * math.log(2.0))
    return (math.sqrt(v) / math.sqrt(60.0)) if v > 0 else None


def uoc_garman_klass(oh, T, soNen):
    """σ² = mean[0,5(ln(H/L))² − (2ln2−1)(ln(C/O))²]."""
    ns = _lay_nen(oh, T, soNen)
    if ns is None or len(ns) < 2:
        return None
    k = 2.0 * math.log(2.0) - 1.0
    s = sum(0.5 * math.log(h / l) ** 2 - k * math.log(c / o) ** 2
            for o, h, l, c in ns) / len(ns)
    # Garman–Klass CÓ THỂ ra âm trên mẫu nhỏ — nó là ước lượng không chệch
    # của phương sai, không phải một phương sai. Âm thì trả None chứ đừng
    # kẹp về 0: kẹp là lặng lẽ biến một phép đo hỏng thành một con số nhỏ.
    return (math.sqrt(s) / math.sqrt(60.0)) if s > 0 else None


BO_UOC = {"dong-dong": uoc_dong_dong, "ewma": uoc_ewma,
          "parkinson": uoc_parkinson, "garman-klass": uoc_garman_klass}


def _brier(cap):
    return (sum((p - (1.0 if t else 0.0)) ** 2 for p, t, *_ in cap)
            / max(1, len(cap)))


def cap_du_doan(oh, mocs, ham, soNen):
    ra = []
    for T in mocs:
        n0, n5 = oh.get(T), oh.get(T + 5 * int(PHUT))
        if n0 is None or n5 is None:
            continue
        K, het = n0[3], n5[3]
        if abs(het - K) < 1e-12:
            continue
        sig = ham(oh, T, soNen)
        if sig is None:
            continue
        thang = het > K
        for tau in LAT_CAT:
            t = T + int((300.0 - tau) * 1000.0)
            if t % int(PHUT):
                continue
            n = oh.get(t)
            if n is None:
                continue
            gc = dinh_gia(MA, float(n[3]), float(K), tau, sig)
            if gc is not None:
                ra.append((gc.pUp, thang, T))
    return ra


def cham(oh, ba, ham, soNen):
    hoc, chon, chot = (cap_du_doan(oh, m, ham, soNen) for m in ba)
    if len(hoc) < 1500 or len(chon) < 500 or len(chot) < 500:
        return None
    hc = HieuChinh(duong=DATA_DIR / "_tam-sigma.json")
    hc.o = {}
    for p, t, *_ in hoc:
        hc.them(p, t)
    pn = khop(hc)

    def nan(cap):
        return [(pn.nan(p) if pn.dung_duoc else p, t) for p, t, *_ in cap]

    return {"n": len(chon), "chon": _brier(nan(chon)),
            "chot": _brier(nan(chot)),
            "saiChot": [(q - (1.0 if t else 0.0)) ** 2 for q, t in nan(chot)],
            "mocChot": [x[-1] for x in chot]}


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
    print("  BỘ ƯỚC σ NÀO TỐT NHẤT — chấm bằng kết quả thật")
    print("=" * 76)
    print(f"  {MA} ({cap}) · {SO_NGAY} ngày · cửa sổ {CUA_SO:g}s "
          f"({soNen} nến) · lấy {tong:,} nến…", flush=True)
    oh = nen_ohlc(cap, hetMs - tong * PHUT, tong)
    if len(oh) < 1200:
        print(f"  chỉ lấy được {len(oh)} nến. Không đủ.\n")
        return 1
    mocs = [T for T in sorted(oh) if T % 300_000 == 0]
    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)
    ba = (mocs[:a], mocs[a:b], mocs[b:])
    print(f"  {len(oh):,} nến · {len(mocs):,} khung · "
          f"HỌC {len(ba[0]):,} · CHỌN {len(ba[1]):,} · CHỐT {len(ba[2]):,}")
    print()
    print("    bộ ước           cặp CHỌN   Brier CHỌN   Brier CHỐT")

    kq = {}
    for ten, ham in BO_UOC.items():
        r = cham(oh, ba, ham, soNen)
        if r is None:
            print(f"    {ten:<16} — không đủ cặp")
            continue
        kq[ten] = r
        print(f"    {ten:<16} {r['n']:>8,}   {r['chon']:>10.5f}   "
              f"{r['chot']:>10.5f}", flush=True)

    if "dong-dong" not in kq or len(kq) < 2:
        print("\n  Không đủ để so.\n")
        return 1

    goc = kq["dong-dong"]
    xep = sorted(((t, r) for t, r in kq.items()), key=lambda x: x[1]["chon"])
    tot, rTot = xep[0]
    print()
    if tot == "dong-dong":
        print("  GIỮ NGUYÊN `dong-dong` — không bộ nào khá hơn ở tập CHỌN.")
        return 0
    print(f"  Quán quân tập CHỌN: `{tot}` "
          f"({rTot['chon']:.5f} so với {goc['chon']:.5f})")
    if rTot["chon"] >= goc["chon"] * BIEN:
        print(f"  TRẢ LẠI: chưa vượt biên {BIEN:g}× "
              f"(cần ≤ {goc['chon']*BIEN:.5f}).")
        return 0

    # Tập CHỐT chỉ gật hay lắc, kèm khoảng tin có cặp.
    # Lấy lại theo KHUNG — xem `khoang_tin_theo_khoi`.
    from kham.hoc_offline import khoang_tin_theo_khoi
    hieu = [x - y for x, y in zip(goc["saiChot"], rTot["saiChot"])]
    n_ = len(hieu)
    thap, cao, soK = khoang_tin_theo_khoi(hieu, goc.get("mocChot"))
    print(f"  CHỐT {goc['chot']:.5f} → {rTot['chot']:.5f} · chênh "
          f"{sum(hieu)/n_:+.6f} · khoảng tin 95% [{thap:+.6f}, {cao:+.6f}]")
    if rTot["chot"] >= goc["chot"]:
        print("  TRẢ LẠI: tập CHỐT không gật.")
    elif thap <= 0 <= cao:
        print("  ⚠ CHỐT gật nhưng khoảng tin CHỨA 0 — nằm trong tiếng ồn.")
        print("    Chưa đủ để đổi một bộ phận của mô hình.")
    else:
        print(f"  NHẬN VỀ MẶT ĐO ĐẠC: `{tot}` khá hơn `dong-dong` rõ rệt.")
        print("    Đây là đổi một BỘ PHẬN, không phải vặn một con số — nên")
        print("    nó cần một lời khai trong config và một đường mã, chứ")
        print("    không tự ghi đè ở đây.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
