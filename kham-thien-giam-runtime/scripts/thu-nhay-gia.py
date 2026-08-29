r"""σ CHỐNG NHẢY GIÁ có tốt hơn không? Hướng thứ chín.

    python scripts/thu-nhay-gia.py --ngay=20

Tám hướng đã đóng. Trước khi thêm hướng thứ chín, đọc lại luật đã ghi ở
CLAUDE.md: **trần mô hình đóng sẵn mọi ý tưởng chỉ đổi cách biến `z`
thành xác suất** — Student-t, nắn kiểu khác, kẹp, làm trơn, tất cả đều
đơn điệu trong `p` nên vô ích. Chỉ thứ làm `z` KHÁC ĐI mới còn cửa, và
`z` chỉ phụ thuộc `S, K, τ, σ`.

Đây là một ứng viên đúng loại ấy: đổi σ.

## Vì sao KHÔNG trùng với hướng "bộ ước σ" đã đóng

Hướng ấy so bốn bộ ước — close-close, ewma, Parkinson, Garman–Klass. Cả
bốn đo cùng một thứ (biến động thực hiện) và chỉ khác nhau ở HIỆU QUẢ
thống kê: dùng bao nhiêu phần thông tin của mỗi cây nến.

Bipower và medRV hỏi một câu khác hẳn: **bỏ phần NHẢY GIÁ ra khỏi σ**.
Biến động thực hiện = phần khuếch tán + phần nhảy. Mô hình `Φ(z)` giả
định khuếch tán liên tục, nên phần nhảy trong σ là tạp chất — nó thổi σ
lên và làm mô hình rụt rè quá ở đúng những cửa sổ vừa có cú nhảy.

Nếu đúng thế thì bỏ nhảy ra phải khá hơn. Nếu không khá hơn thì ta biết
thêm một điều đáng giá: với khung 5 phút, phần nhảy KHÔNG phải tạp chất
— nó là dự báo thật cho 5 phút tới.

## Ứng viên

    dong-dong    độ lệch chuẩn log-return giá đóng     (đương nhiệm)
    bipower      sqrt(π/2 · trung bình |r_i|·|r_{i-1}|)
    med-rv       trung vị trượt ba nhịp, chống nhảy mạnh hơn bipower
    pha-nua      nửa phương sai thực hiện + nửa bipower

`pha-nua` có mặt vì hai đầu cực đoan hiếm khi là câu trả lời: nếu bỏ hết
nhảy là quá tay còn giữ hết là chưa đủ, cái pha sẽ thắng cả hai — và đó
là một kết quả khác hẳn với "cả hai đều thua".

## Chấm y hệt vòng tự nâng cấp

Ba tập tách theo THỜI GIAN, khoảng tin lấy lại THEO KHUNG, biên siết
theo số ứng viên.
"""
from __future__ import annotations

import math
import statistics
import sys
import time
from pathlib import Path

N = chr(10)
GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.hoc_offline import (BIEN_CHOT, bien_theo_ung_vien,  # noqa: E402
                              khoang_tin_theo_khoi)
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
}, ten='thu-nhay-gia.py')


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





def uoc_tron(oh, T, soNen):
    """σ đương nhiệm: độ lệch chuẩn log-return giá đóng trên lưới phút."""
    c = _lay_nen(oh, T, soNen)
    if c is None:
        return None
    r = [math.log(c[i + 1][3] / c[i][3]) for i in range(len(c) - 1)
         if c[i][3] > 0 and c[i + 1][3] > 0]
    if len(r) < 5:
        return None
    s = statistics.pstdev(r) / math.sqrt(60.0)
    return s if s > 0 else None




def _loi(oh, T, soNen):
    """Dãy log-return trong cửa sổ σ, hoặc None."""
    c = _lay_nen(oh, T, soNen)
    if c is None:
        return None
    r = [math.log(c[i + 1][3] / c[i][3]) for i in range(len(c) - 1)
         if c[i][3] > 0 and c[i + 1][3] > 0]
    return r if len(r) >= 5 else None


def uoc_bipower(oh, T, soNen):
    """σ bipower: bỏ phần nhảy giá.

    BV = (π/2) · trung bình(|r_i|·|r_{i-1}|). Tích của HAI độ lớn liền
    nhau: một cú nhảy đơn lẻ chỉ làm to đúng một thừa số, nên ảnh hưởng
    của nó bị nén — trong khi phương sai thực hiện bình phương nó lên.
    """
    r = _loi(oh, T, soNen)
    if r is None or len(r) < 6:
        return None
    tich = [abs(r[i]) * abs(r[i - 1]) for i in range(1, len(r))]
    bv = (math.pi / 2.0) * (sum(tich) / len(tich))
    s = math.sqrt(max(0.0, bv)) / math.sqrt(60.0)
    return s if s > 0 else None


def uoc_med_rv(oh, T, soNen):
    """medRV: trung vị trượt ba nhịp. Chống nhảy mạnh hơn bipower.

    Một cú nhảy làm hỏng đúng MỘT trong ba phần tử của mỗi bộ ba mà nó
    rơi vào, và trung vị bỏ qua nó. Hệ số π/(6−4√3+π) là chuẩn hoá để
    ước lượng không thiên vị dưới giả định khuếch tán.
    """
    r = _loi(oh, T, soNen)
    if r is None or len(r) < 7:
        return None
    he = math.pi / (6.0 - 4.0 * math.sqrt(3.0) + math.pi)
    bo = [sorted((abs(r[i - 1]), abs(r[i]), abs(r[i + 1])))[1] ** 2
          for i in range(1, len(r) - 1)]
    mv = he * (len(r) / max(1, len(r) - 2)) * (sum(bo) / len(bo))
    s = math.sqrt(max(0.0, mv)) / math.sqrt(60.0)
    return s if s > 0 else None


def uoc_pha_nua(oh, T, soNen):
    """Nửa phương sai thực hiện + nửa bipower.

    Hai đầu cực đoan hiếm khi là câu trả lời. Nếu bỏ hết nhảy là quá
    tay còn giữ hết là chưa đủ thì cái pha sẽ thắng cả hai — và đó là
    một kết quả khác hẳn với 'cả hai đều thua'.
    """
    a = uoc_tron(oh, T, soNen)
    b = uoc_bipower(oh, T, soNen)
    if a is None or b is None:
        return None
    v = 0.5 * a * a + 0.5 * b * b
    s = math.sqrt(max(0.0, v))
    return s if s > 0 else None


UNG_VIEN = {
    "dong-dong": uoc_tron,
    "bipower": uoc_bipower,
    "med-rv": uoc_med_rv,
    "pha-nua": uoc_pha_nua,
}

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
        print(N + "  Không có market `" + MA + "`." + N)
        return 1
    soNen = max(2, int(round(CUA_SO / 60.0)))
    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    tong = SO_NGAY * 24 * 60 + soNen + 20

    print()
    print("=" * 76)
    print("  σ CHỐNG NHẢY GIÁ CÓ TỐT HƠN KHÔNG — hướng thứ chín")
    print("=" * 76)
    print("  " + MA + " (" + cap + ") · " + str(SO_NGAY) + " ngày · cửa sổ "
          + format(CUA_SO, "g") + "s (" + str(soNen) + " nến) · lấy "
          + format(tong, ",") + " nến…", flush=True)

    oh = nen_ohlc(cap, hetMs - tong * PHUT, tong)
    if len(oh) < 2000:
        print("  chỉ lấy được " + str(len(oh)) + " nến. Không đủ." + N)
        return 1

    mocs = sorted(t for t in oh if t % (5 * int(PHUT)) == 0)
    n = len(mocs)
    a, b = int(n * 0.5), int(n * 0.75)
    ba = (mocs[:a], mocs[a:b], mocs[b:])
    print("  " + format(len(oh), ",") + " nến · " + format(n, ",")
          + " khung · HỌC " + format(len(ba[0]), ",")
          + " · CHỌN " + format(len(ba[1]), ",")
          + " · CHỐT " + format(len(ba[2]), ","))

    ketQua = {}
    for ten, ham in UNG_VIEN.items():
        ketQua[ten] = cham(oh, ba, ham, soNen)
    ketQua = {k: v for k, v in ketQua.items() if v}
    goc_ten = "dong-dong"
    if goc_ten not in ketQua:
        print("  chưa đủ cặp.")
        return 1

    print()
    print("    ứng viên        cặp CHỌN   Brier CHỌN   Brier CHỐT")
    for ten, r in ketQua.items():
        nhan = ten + ("  ← đương nhiệm" if ten == goc_ten else "")
        print("    " + nhan.ljust(28)
              + format(r["n"], ",").rjust(9)
              + format(r["chon"], ".5f").rjust(13)
              + format(r["chot"], ".5f").rjust(13))

    goc = ketQua[goc_ten]
    ung = {k: v for k, v in ketQua.items() if k != goc_ten}
    if not ung:
        print(N + "  Không ứng viên nào chạy được." + N)
        return 0
    tot = min(ung, key=lambda k: ung[k]["chon"])
    r = ung[tot]
    bien = bien_theo_ung_vien(len(ung))
    can = goc["chon"] * bien

    print()
    print("  Quán quân tập CHỌN: `" + tot + "` ("
          + format(r["chon"], ".5f") + " so với "
          + format(goc["chon"], ".5f") + ")")
    if r["chon"] > can:
        print("  TRẢ LẠI: chưa vượt biên " + format(bien, ".4f")
              + "× (cần ≤ " + format(can, ".5f") + ").")
    elif r["chot"] > goc["chot"] * BIEN_CHOT:
        print("  TRẢ LẠI: tập CHỐT không gật (" + format(r["chot"], ".5f")
              + " so với " + format(goc["chot"], ".5f") + ").")
    else:
        print("  NHẬN: vượt biên ở CHỌN và tập CHỐT gật.")

    hieu = [x - y for x, y in zip(r["saiChot"], goc["saiChot"])]
    thap, cao, soK = khoang_tin_theo_khoi(hieu, goc.get("mocChot"))
    print("  Khoảng tin 95% cho chênh Brier CHỐT (theo " + str(soK)
          + " KHUNG): [" + format(thap, "+.6f") + ", "
          + format(cao, "+.6f") + "]")
    if thap <= 0 <= cao:
        print("  → khoảng tin CHỨA 0. Chưa đủ bằng chứng, đừng đổi gì.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
