r"""TRỌNG SỐ của phần nhảy giá trong σ. Hướng thứ mười.

    python scripts/thu-trong-so-nhay.py --ngay=20

Hướng thứ chín đo σ chống nhảy giá và trả về một kết luận CÓ CHIỀU: càng
bỏ phần nhảy càng tệ, khoảng tin hẳn bên dương. Phần nhảy không phải tạp
chất — nó là dự báo thật cho 5 phút tới.

Một kết luận có chiều thì chỉ luôn sang phép thử kế tiếp, và phép thử ấy
là câu hỏi ngược lại: **nếu bỏ nhảy làm tệ đi, thì KHUẾCH ĐẠI nó có làm
tốt lên không?**

Cả hai câu nằm trên MỘT trục, nên đo bằng một tham số:

    σ² = RV + λ·(RV − BV)

`RV − BV` là phần nhảy (phương sai thực hiện trừ bipower). Khi đó:

    λ = −1   bỏ sạch phần nhảy         ← chính là bipower, hướng thứ chín
    λ =  0   giữ nguyên                ← ĐƯƠNG NHIỆM
    λ = +1   nhân đôi phần nhảy

Lẽ ra hướng thứ chín nên viết thẳng theo trục này ngay từ đầu — dò một
tham số liên tục nói được nhiều hơn hẳn so sánh vài bộ ước rời rạc, vì
nó cho thấy CHIỀU và cả chỗ tối ưu, chứ không chỉ "ai thắng ai".

Nếu λ tối ưu rơi vào quãng dương thì đó là một hướng NHẬN đầu tiên sau
chín lần không. Nếu nó rơi đúng 0 thì ta biết đương nhiệm đã ở chỗ tối
ưu trên trục này — cũng là một kết luận chặt, không phải một con số
không.

## Chấm y hệt vòng tự nâng cấp

Ba tập tách theo THỜI GIAN, khoảng tin lấy lại THEO KHUNG, biên siết
theo số ứng viên. λ = 0 nằm TRONG lưới làm đối chứng.
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
from kham.ban_thu import (_brier, _lay_nen, cap_du_doan,  # noqa: E402
                          cham as _cham_chung, nen_ohlc, uoc_tron)
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
}, ten='thu-trong-so-nhay.py')


SO_NGAY = int(CO.lay("ngay", "20"))
MA = CO.lay("ma", "BTC_5M")
CUA_SO = float(CO.lay("cuaso", "900"))


# ══════════════════════════════════════════════════════════════════════
#  BỐN BỘ ƯỚC — tất cả trả về σ MỖI GIÂY
# ══════════════════════════════════════════════════════════════════════


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


#: Trọng số phần nhảy. λ = 0 là ĐƯƠNG NHIỆM, cố ý nằm trong lưới.
#: Âm = bớt nhảy (λ = −1 chính là bipower), dương = khuếch đại.
LAM = (-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0)


def _rv_bv(oh, T, soNen):
    """Trả (phương sai thực hiện, bipower) trên cùng cửa sổ, hoặc None."""
    r = _loi(oh, T, soNen)
    if r is None or len(r) < 6:
        return None
    rv = sum(x * x for x in r) / len(r)
    tich = [abs(r[i]) * abs(r[i - 1]) for i in range(1, len(r))]
    bv = (math.pi / 2.0) * (sum(tich) / len(tich))
    return rv, bv


def uoc_trong_so(lam):
    """σ với phần nhảy nhân trọng số: σ² = RV + λ·(RV − BV).

    Kẹp sàn ở 0,25·RV: một cửa sổ mà BV vượt hẳn RV (chuyện xảy ra khi
    mẫu ít) với λ âm mạnh có thể đẩy phương sai xuống âm hoặc gần 0, và
    σ gần 0 làm mô hình tự tin tuyệt đối — đúng chỗ đắt nhất để sai.
    """
    def ham(oh, T, soNen):
        d = _rv_bv(oh, T, soNen)
        if d is None:
            return None
        rv, bv = d
        v = rv + lam * (rv - bv)
        v = max(v, 0.25 * rv)
        if v <= 0:
            return None
        s = math.sqrt(v) / math.sqrt(60.0)
        return s if s > 0 else None
    return ham


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
    print("  TRỌNG SỐ PHẦN NHẢY GIÁ TRONG σ — hướng thứ mười")
    print("=" * 76)
    print("  σ² = RV + λ·(RV − BV)   ·   λ=−1 là bipower, λ=0 là đương nhiệm")
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
    for lam in LAM:
        ten = "λ " + format(lam, "+.2f")
        ketQua[ten] = _cham_chung(oh, ba, uoc_trong_so(lam), soNen)
    ketQua = {k: v for k, v in ketQua.items() if v}
    goc_ten = "λ +0.00"
    if goc_ten not in ketQua:
        print("  chưa đủ cặp.")
        return 1

    print()
    print("    λ            cặp CHỌN   Brier CHỌN   Brier CHỐT")
    for ten, r in ketQua.items():
        nhan = ten + ("  ← đương nhiệm" if ten == goc_ten else "")
        print("    " + nhan.ljust(26)
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
