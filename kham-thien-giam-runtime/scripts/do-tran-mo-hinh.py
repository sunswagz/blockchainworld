"""CÒN BAO NHIÊU CHỖ ĐỂ CẢI THIỆN? Đo trần, rồi mới quyết có nên vặn tiếp.

    python scripts/do-tran-mo-hinh.py --ngay=20

Vòng tự nâng cấp đã hết việc: ba lượt độc lập, cả ba đứng yên. Bộ ước σ
đổi kiểu chỉ được 0,13%, dưới xa biên. Câu đúng để hỏi lúc này không phải
"vặn gì tiếp" mà là **"còn gì để vặn không"**.

## Ba mốc, và khoảng cách giữa chúng là toàn bộ câu trả lời

    SÀN     đoán bừa theo tỉ lệ nền          — không dùng thông tin nào
    NAY     mô hình hiện tại                  — chỗ ta đang đứng
    TRẦN    phép biến đổi ĐƠN ĐIỆU tốt nhất   — khớp NGAY TRÊN tập chấm

`TRẦN` cố tình khớp trong mẫu trên chính tập đang chấm. Nó KHÔNG phải
một mô hình dùng được — nó là thứ tốt nhất mà bất kỳ phép nắn nào cũng
không thể vượt, vì mọi phép nắn đều là một biến đổi đơn điệu của `p`.
Gian lận có chủ đích, để lấy một CẬN.

Đọc:

    NAY gần SÀN   → mô hình gần như vô dụng, sửa mô hình là đúng việc
    NAY gần TRẦN  → đã vắt kiệt thông tin trong `p`. Vặn thêm là phí công;
                    muốn khá hơn phải thêm THÔNG TIN MỚI, không phải
                    thêm tham số.

## Và một câu hỏi thứ hai: τ có đáng tách không

Bảng hiệu chỉnh gộp cả bốn lát cắt τ = 240/180/120/60 vào một bảng. Nếu
mô hình lệch KHÁC NHAU ở các τ khác nhau thì gộp là làm mờ. Đo riêng
từng τ sẽ thấy ngay.
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
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.nan_lai import _pava, khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402

PHUT = 60_000.0
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
CHIA = 0.6


def _tham(ten, mac_dinh):
    for a in sys.argv[1:]:
        if a.startswith(f"--{ten}="):
            return a.split("=", 1)[1]
    return mac_dinh


SO_NGAY = int(_tham("ngay", "20"))
MA = _tham("ma", "BTC_5M")
CUA_SO = float(_tham("cuaso", "900"))


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
    gs = gs[::-1]
    r = [math.log(gs[i + 1] / gs[i]) for i in range(len(gs) - 1)]
    sd = statistics.pstdev(r)
    return (sd / math.sqrt(60.0)) if sd > 0 else None


def _brier(cap):
    return sum((p - (1.0 if t else 0.0)) ** 2 for p, t in cap) / max(1, len(cap))


def tran_don_dieu(cap, soO: int = 40) -> float:
    """Brier của phép biến đổi ĐƠN ĐIỆU tốt nhất, khớp NGAY TRÊN `cap`.

    Khớp trong mẫu là CỐ Ý: đây là một CẬN của thông tin nằm trong `p`,
    không phải một mô hình đem dùng. Mọi phép nắn đều là biến đổi đơn
    điệu của `p`, nên không phép nắn nào vượt được con số này.

    ## Bản đầu SAI, và nó sai theo hướng vô lý

    Nó gọi `_pava(x, y, w)` rồi ánh xạ `yn[min(i, len(yn)-1)]` cho ô thứ
    `i`. Nhưng PAVA GỘP các ô vi phạm, nên `yn` NGẮN hơn số ô — ánh xạ
    theo chỉ số là gán giá trị của ô này cho ô khác. Kết quả: "trần"
    0,17191 trong khi mô hình đạt 0,15779, tức một cái trần THẤP HƠN thứ
    nó chặn. Vô lý, và may là vô lý lộ liễu.

    Nay tự chạy PAVA có theo dõi KHỐI: mỗi khối giữ (số thắng, số điểm),
    gộp thì cộng cả hai, nên tổng số điểm luôn khớp và việc gán trở lại
    không còn chỗ trượt.
    """
    xep = sorted(cap, key=lambda x: x[0])
    n = len(xep)
    if n < 40:
        return _brier(cap)
    soO = max(4, min(soO, n // 10))
    canh = [int(round(i * n / soO)) for i in range(soO + 1)]

    khoi = []
    for i in range(soO):
        lo, hi = canh[i], canh[i + 1]
        if hi <= lo:
            continue
        khoi.append([sum(1 for _p, t in xep[lo:hi] if t), hi - lo])
    if len(khoi) < 3:
        return _brier(cap)

    i = 0
    while i < len(khoi) - 1:
        a, b = khoi[i], khoi[i + 1]
        if a[0] / a[1] <= b[0] / b[1] + 1e-12:
            i += 1
            continue
        khoi[i] = [a[0] + b[0], a[1] + b[1]]
        del khoi[i + 1]
        i = max(0, i - 1)

    ra, k = [], 0
    for tong, dem in khoi:
        q = tong / dem
        for _ in range(dem):
            ra.append((q, xep[k][1]))
            k += 1
    assert k == n, f"gán trượt {k} != {n}"
    return _brier(ra)


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
    print("  CÒN BAO NHIÊU CHỖ ĐỂ CẢI THIỆN — đo TRẦN trước khi vặn tiếp")
    print("=" * 76)
    print(f"  {MA} ({cap}) · {SO_NGAY} ngày · cửa sổ σ {CUA_SO:g}s · "
          f"lấy {tong:,} nến…", flush=True)
    oh = nen(cap, hetMs - tong * PHUT, tong)
    if len(oh) < 1200:
        print(f"  chỉ lấy được {len(oh)} nến.\n")
        return 1

    mocs = [T for T in sorted(oh) if T % 300_000 == 0]
    cat = int(len(mocs) * CHIA)
    hocM, chamM = mocs[:cat], mocs[cat:]

    def dung(ms):
        ra = []
        for T in ms:
            K, het = oh.get(T), oh.get(T + 5 * int(PHUT))
            if K is None or het is None or abs(het - K) < 1e-12:
                continue
            sig = _sigma(oh, T, soNen)
            if sig is None:
                continue
            thang = het > K
            for tau in LAT_CAT:
                t = T + int((300.0 - tau) * 1000.0)
                if t % int(PHUT):
                    continue
                S = oh.get(t)
                if S is None or S <= 0:
                    continue
                gc = dinh_gia(MA, float(S), float(K), tau, sig)
                if gc is not None:
                    ra.append((gc.pUp, thang, tau))
        return ra

    hoc, cham = dung(hocM), dung(chamM)
    if len(cham) < 2000:
        print("  chưa đủ cặp.\n")
        return 1
    print(f"  {len(oh):,} nến · HỌC {len(hoc):,} cặp · CHẤM {len(cham):,} cặp")

    c2 = [(p, t) for p, t, _ in cham]
    nen_ti = sum(1 for _p, t in c2 if t) / len(c2)
    san = _brier([(nen_ti, t) for _p, t in c2])

    hc = HieuChinh(duong=DATA_DIR / "_tam-tran.json")
    hc.o = {}
    for p, t, _ in hoc:
        hc.them(p, t)
    pn = khop(hc)
    nay_tho = _brier(c2)
    nay_nan = _brier([(pn.nan(p) if pn.dung_duoc else p, t) for p, t in c2])
    tran = tran_don_dieu(c2)

    print()
    print(f"    SÀN   đoán bừa tỉ lệ nền ({nen_ti:.1%})      {san:.5f}")
    print(f"    NAY   mô hình thô                       {nay_tho:.5f}")
    print(f"    NAY   sau phép nắn (khớp ngoài mẫu)     {nay_nan:.5f}")
    print(f"    TRẦN  biến đổi đơn điệu tốt nhất        {tran:.5f}"
          "   (khớp TRONG mẫu, cố ý)")
    if tran > min(nay_tho, nay_nan) + 1e-9:
        print()
        print("  ⚠⚠ TRẦN CAO HƠN MÔ HÌNH. Một cái trần thấp hơn thứ nó chặn")
        print("     là vô nghĩa — phép tính trần đang hỏng, và mọi con số")
        print("     dưới đây không dùng được cho tới khi sửa.")
        return 1
    print()
    dat = san - nay_nan
    con = nay_nan - tran
    print(f"    đã lấy được {dat:.5f} trên tổng {san - tran:.5f} khoảng cách"
          f" SÀN→TRẦN  =  {dat/max(1e-9, san-tran):.1%}")
    print(f"    còn lại    {con:.5f}  ({con/max(1e-9, san-tran):.1%})")
    print()
    if con < 0.002:
        print("  ĐỌC: NAY gần như chạm TRẦN. Mọi phép nắn, mọi cách vặn tham")
        print("  số của `p` đều nằm dưới cái trần ấy — nên vặn thêm là phí")
        print("  công. Muốn khá hơn phải thêm THÔNG TIN MỚI vào `p`, không")
        print("  phải thêm tham số: sổ lệnh, dòng lệnh, độ trễ liên sàn.")
    else:
        print("  ĐỌC: còn khoảng trống đáng kể giữa NAY và TRẦN — một phép")
        print("  nắn tốt hơn hoặc nhiều mẫu hơn vẫn còn ăn được.")

    print()
    print("  TÁCH THEO τ — bảng hiệu chỉnh gộp cả bốn lát cắt vào một; nếu")
    print("  mô hình lệch khác nhau ở các τ thì gộp là làm mờ.")
    print("      τ      cặp    Brier thô   Brier nắn      TRẦN")
    for tau in LAT_CAT:
        ct = [(p, t) for p, t, x in cham if x == tau]
        if len(ct) < 300:
            continue
        print(f"    {tau:>4.0f}s {len(ct):>7,}   {_brier(ct):>9.5f}   "
              f"{_brier([(pn.nan(p) if pn.dung_duoc else p, t) for p, t in ct]):>9.5f}"
              f"   {tran_don_dieu(ct):>9.5f}")
    print("=" * 76)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
