"""Nắn RIÊNG theo τ có đáng không? Câu hỏi cuối còn lại về mô hình.

    python scripts/thu-nan-theo-tau.py --ngay=20

`do-tran-mo-hinh.py` chốt: mô hình đã vắt 98,9% thông tin nằm trong `p`.
Nhưng bảng trần tách theo τ lộ ra một chỗ chưa vét:

    τ      Brier nắn    TRẦN riêng τ    khoảng cách
    240s     0.21422        0.21180        0.00242
    180s     0.18106        0.17873        0.00233
    120s     0.14098        0.13920        0.00178
     60s     0.09469        0.09288        0.00181

Trần GỘP là 0,15669; trung bình bốn trần RIÊNG là 0,15565 — thấp hơn
0,00104. Nghĩa là một phép nắn tách theo τ với tay được xuống dưới cái
trần mà phép nắn gộp không bao giờ chạm tới.

Lý do dễ hiểu: `HieuChinh` gộp cả bốn lát cắt vào MỘT bảng mười ô, nên
một `p = 0,7` ở τ=240 và một `p = 0,7` ở τ=60 bị coi là cùng một thứ.
Chúng không cùng một thứ: cái sau còn 60 giây để sai, cái trước còn 240.

## Nhưng đây là chỗ dễ tự lừa nhất

Tách bốn bảng là chia mẫu làm bốn, mỗi ô còn một phần tư số mẫu. Bảng
thưa thì PAVA bám tiếng ồn, và cái "khá hơn" đo trong mẫu sẽ bốc hơi
ngoài mẫu. Nên chấm y hệt vòng tự nâng cấp: ba tập tách theo THỜI GIAN,
tập CHỐT chỉ gật hay lắc, kèm khoảng tin có cặp.

Nếu nó không qua nổi thì câu trả lời là KHÔNG, và câu trả lời đó cũng
đáng giá: nó đóng lại câu hỏi cuối cùng còn mở về mô hình.
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
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.nan_lai import khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402

PHUT = 60_000.0
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
CHIA_HOC, CHIA_CHON = 0.50, 0.75
BIEN = 0.995


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


def _brier1(q, t):
    return (q - (1.0 if t else 0.0)) ** 2


def _brier(cap):
    return sum(_brier1(q, t) for q, t in cap) / max(1, len(cap))


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
    print("  NẮN RIÊNG THEO τ CÓ ĐÁNG KHÔNG")
    print("=" * 76)
    print(f"  {MA} ({cap}) · {SO_NGAY} ngày · cửa sổ σ {CUA_SO:g}s · "
          f"lấy {tong:,} nến…", flush=True)
    oh = nen(cap, hetMs - tong * PHUT, tong)
    if len(oh) < 1200:
        print(f"  chỉ lấy được {len(oh)} nến.\n")
        return 1

    mocs = [T for T in sorted(oh) if T % 300_000 == 0]
    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)
    ba = (mocs[:a], mocs[a:b], mocs[b:])

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

    hoc, chon, chot = (dung(m) for m in ba)
    if min(len(hoc), len(chon), len(chot)) < 1000:
        print("  chưa đủ cặp.\n")
        return 1
    print(f"  HỌC {len(hoc):,} · CHỌN {len(chon):,} · CHỐT {len(chot):,} cặp")

    def bang(cap_, duong):
        hc = HieuChinh(duong=duong)
        hc.o = {}
        for p, t in cap_:
            hc.them(p, t)
        return khop(hc)

    gop = bang([(p, t) for p, t, _ in hoc], DATA_DIR / "_tau-gop.json")
    rieng = {tau: bang([(p, t) for p, t, x in hoc if x == tau],
                       DATA_DIR / f"_tau-{int(tau)}.json")
             for tau in LAT_CAT}

    print()
    print("    bảng nắn         dùng được   mẫu")
    print(f"    gộp              {str(gop.dung_duoc):<9}   {gop.tongMau:,}")
    for tau in LAT_CAT:
        p_ = rieng[tau]
        print(f"    riêng τ={tau:.0f}s     {str(p_.dung_duoc):<9}   "
              f"{p_.tongMau:,}")

    def cham(cap_, kieu):
        ra = []
        for p, t, tau in cap_:
            pn = gop if kieu == "gop" else rieng[tau]
            ra.append((pn.nan(p) if pn.dung_duoc else p, t))
        return ra

    for ten, tap in (("CHỌN", chon), ("CHỐT", chot)):
        g, r = _brier(cham(tap, "gop")), _brier(cham(tap, "rieng"))
        print(f"    {ten}: gộp {g:.5f} · riêng {r:.5f} · chênh {g-r:+.6f}")

    gChon = _brier(cham(chon, "gop"))
    rChon = _brier(cham(chon, "rieng"))
    print()
    if rChon >= gChon * BIEN:
        print(f"  TRẢ LẠI ở tập CHỌN: cần ≤ {gChon*BIEN:.5f}, được "
              f"{rChon:.5f}.")
        print()
        print("  ĐỌC: tách bốn bảng là chia mẫu làm bốn; phần thông tin thêm")
        print("  được không bù nổi phần bảng thưa đi. Câu hỏi cuối còn mở về")
        print("  mô hình nay đã đóng — KHÔNG tách.")
        print("=" * 76 + "\n")
        return 0

    gs = [_brier1(q, t) for q, t in cham(chot, "gop")]
    rs = [_brier1(q, t) for q, t in cham(chot, "rieng")]
    hieu = [x - y for x, y in zip(gs, rs)]
    n = len(hieu)
    rd = random.Random(20260829)
    lan = sorted(sum(hieu[rd.randrange(n)] for _ in range(n)) / n
                 for _ in range(2000))
    thap, cao = lan[int(0.025 * len(lan))], lan[int(0.975 * len(lan))]
    print(f"  CHỐT: chênh {sum(hieu)/n:+.6f} · khoảng tin 95% "
          f"[{thap:+.6f}, {cao:+.6f}]")
    if thap > 0:
        print("  NHẬN VỀ MẶT ĐO ĐẠC: nắn riêng theo τ khá hơn rõ rệt.")
        print("    Đây là đổi CẤU TRÚC sổ hiệu chỉnh, không phải vặn một số —")
        print("    nên nó cần một đường mã và một lời khai, không tự ghi đè.")
    else:
        print("  ⚠ khoảng tin CHỨA 0: qua tập CHỌN nhưng nằm trong tiếng ồn.")
        print("    Không đủ để đổi cấu trúc sổ hiệu chỉnh.")
    print("=" * 76 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
