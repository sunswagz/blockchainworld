"""Mô hình định giá được ở CỬA NÀO? Chỉ cần Binance.

    python scripts/do-cua-nao.py

`do-strike.py` chốt được: UP thắng ⟺ giá(T+300) > giá(T). Strike là giá
lúc T. Hệ quả kéo theo là một câu hỏi về kiến trúc, và nó lớn hơn hẳn
chuyện một tham số sai.

    cửa runtime đang làm việc:  [T−300, T]   `giai_doan == DAT_CUOC`
    khung ăn thua thật sự    :  [T,   T+300]

Trong cửa runtime làm việc, strike CHƯA TỒN TẠI: nó là giá lúc T, mà T
còn ở phía trước. Công thức của cung này là

    z = [ln(S/K) − σ²τ/2] / (σ√τ),   P = Φ(z)

và nó chỉ có nghĩa khi K đã biết. Với K chưa xảy ra, số gia từ T tới
T+300 độc lập với mọi thứ quan sát được lúc t < T, nên giá trị thật là
**đúng 0,5**, bất kể giá đang ở đâu.

Nói thẳng: **bot đang giao dịch đúng cái cửa mà mô hình chứng minh được
là không đoán nổi, và tắt máy đúng lúc cửa đoán được bắt đầu.**

## Phép đo

Không cần sổ lệnh, không cần Polymarket — chỉ nến 1 phút Binance.

Với mỗi mốc T lấy ngẫu nhiên, chấm mô hình ở HAI vị trí:

    TRƯỚC  t = T − 60s   K = giá(T−300)  τ = 60s     ← cách runtime làm
    TRONG  t = T + 240s  K = giá(T)      τ = 60s     ← cửa ăn thua thật

rồi so P mô hình với kết quả thật (B) bằng ĐIỂM KỸ NĂNG so với tỉ lệ nền.
Cùng một mô hình, cùng một τ, cùng một tỉ lệ nền — khác đúng chỗ đứng.
"""
from __future__ import annotations

import math
import os
import random
import statistics
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham.bang import NguonKhung  # noqa: E402
from kham.ket_qua import moc_tu_slug  # noqa: E402
from kham.nguon import nguon  # noqa: E402

TOI_DA = int(os.environ.get("N", "300"))
HAT = int(os.environ.get("HAT", "20260829"))
TAU_GIAY = 60.0


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def p_up(S: float, K: float, tau: float, sig: float) -> float:
    """Đúng công thức `dinh_gia` dùng. `sig` là sigma mỗi GIÂY."""
    if S <= 0 or K <= 0 or tau <= 0 or sig <= 0:
        return 0.5
    v = sig * math.sqrt(tau)
    z = (math.log(S / K) - 0.5 * v * v) / v
    return max(1e-6, min(1 - 1e-6, _phi(z)))


def brier(du, that) -> float:
    return sum((p - t) ** 2 for p, t in zip(du, that)) / max(1, len(du))


def ky_nang(du, that) -> tuple[float, float, float]:
    n = max(1, len(that))
    nen = sum(that) / n
    bC, bN = brier(du, that), brier([nen] * n, that)
    return bC, bN, (0.0 if bN <= 0 else (bN - bC) / bN)


def main() -> int:
    # Mốc T và mã nền lấy từ chính băng, để đo trên đúng quãng chợ ấy.
    moc: dict[int, str] = {}
    cap_theo_ma = {t["ma"]: t.get("nen") for t in kham.config.CONFIG["thiTruong"]}
    for k in NguonKhung(None):
        for tt in (k.get("thiTruong") or []):
            T = moc_tu_slug(tt.get("slug") or "")
            cap = cap_theo_ma.get(tt.get("ma"))
            if T is not None and cap:
                moc[int(T)] = cap

    ds = sorted(moc.items())
    random.Random(HAT).shuffle(ds)
    print()
    print("=" * 74)
    print("  MÔ HÌNH ĐỊNH GIÁ ĐƯỢC Ở CỬA NÀO — chỉ cần Binance")
    print("=" * 74)
    print(f"  {len(ds):,} mốc khung trong băng; lấy ngẫu nhiên {TOI_DA}.")

    duTruoc: list[float] = []
    duTrong: list[float] = []
    that: list[int] = []
    bo = 0
    for i, (T, cap) in enumerate(ds[:TOI_DA], 1):
        g = {}
        for ten, ms in (("t_300", T - 300_000.0), ("T", float(T)),
                        ("t60", T + 240_000.0), ("het", T + 300_000.0),
                        ("truoc60", T - 60_000.0)):
            g[ten] = nguon.gia_dong_khung(cap, ms)
        if None in g.values() or abs(g["het"] - g["T"]) < 1e-9:
            bo += 1
            continue
        # σ đo từ chính quãng ấy: 5 chênh lệch log của nến 1 phút.
        nen = [nguon.gia_dong_khung(cap, T - 300_000.0 + j * 60_000.0)
               for j in range(6)]
        if any(x is None or x <= 0 for x in nen):
            bo += 1
            continue
        r = [math.log(nen[j + 1] / nen[j]) for j in range(5)]
        sd = statistics.pstdev(r)
        sig = (sd / math.sqrt(60.0)) if sd > 0 else 0.0
        if sig <= 0:
            bo += 1
            continue

        # TRƯỚC: đứng ở T−60, strike = giá(T−300), τ = 60s  (cách runtime làm)
        duTruoc.append(p_up(g["truoc60"], g["t_300"], TAU_GIAY, sig))
        # TRONG: đứng ở T+240, strike = giá(T), τ = 60s     (cửa ăn thua thật)
        duTrong.append(p_up(g["t60"], g["T"], TAU_GIAY, sig))
        that.append(1 if g["het"] > g["T"] else 0)
        if i % 50 == 0:
            print(f"    {i} mốc…", flush=True)

    n = len(that)
    print(f"  chấm được {n:,} mốc (bỏ {bo:,})")
    if n < 60:
        print("  Chưa đủ mẫu. ĐỪNG chốt.\n")
        return 0

    print()
    print(f"    tỉ lệ nền UP thắng: {sum(that)/n:.1%}")
    print()
    print("                                   Brier    Brier nền   ĐIỂM KỸ NĂNG")
    for ten, du in (("TRƯỚC  t=T−60,  K=giá(T−300)", duTruoc),
                    ("TRONG  t=T+240, K=giá(T)    ", duTrong)):
        bC, bN, kn = ky_nang(du, that)
        print(f"    {ten}   {bC:.4f}     {bN:.4f}     {kn:>+9.1%}")
    print()
    _, _, knTruoc = ky_nang(duTruoc, that)
    _, _, knTrong = ky_nang(duTrong, that)

    rd = random.Random(HAT + 7)
    hieu = [(a - t) ** 2 - (b - t) ** 2
            for a, b, t in zip(duTruoc, duTrong, that)]
    lan = sorted(sum(hieu[rd.randrange(n)] for _ in range(n)) / n
                 for _ in range(4000))
    thap, cao = lan[int(0.025 * len(lan))], lan[int(0.975 * len(lan))]
    print(f"    chênh Brier (TRƯỚC − TRONG), khoảng tin 95% có cặp: "
          f"[{thap:+.4f}, {cao:+.4f}]")
    print()
    print("  ĐỌC KẾT LUẬN:")
    if thap > 0 and knTrong > 0.02:
        print("    Cùng một mô hình, cùng τ, cùng tỉ lệ nền — nhưng nó chỉ")
        print("    đoán được khi đứng TRONG khung ăn thua. Đứng ở cửa đặt")
        print("    cược thì nó tệ hơn cả một kẻ chỉ biết tỉ lệ nền.")
        print()
        print("    Runtime chỉ hành động khi `giai_doan == DAT_CUOC`, tức là")
        print("    ĐÚNG cái cửa mô hình không làm việc được, và tắt máy đúng")
        print("    lúc cửa đoán được bắt đầu. Đây không phải một tham số sai;")
        print("    đây là bot đang nhắm sai cửa.")
    elif knTrong <= 0.02:
        print("    Mô hình KHÔNG có kỹ năng đáng kể ở cửa nào cả. Vấn đề")
        print("    không nằm ở chỗ đứng — nó nằm ở chính mô hình.")
    else:
        print("    Hai chỗ đứng không tách nhau đủ. ĐỪNG chốt.")
    print("=" * 74)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
