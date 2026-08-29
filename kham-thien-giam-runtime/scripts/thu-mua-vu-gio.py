r"""σ có MÙA VỤ trong ngày không? Hướng thứ bảy, sau khi sáu hướng đã đóng.

    python scripts/thu-mua-vu-gio.py --ngay=20

Tài liệu đã chốt: "Dữ liệu giá Binance đã cạn" — sáu hướng thử, sáu lần
không. Nhưng cả sáu đều vặn CÁCH ĐO σ (cửa sổ, bộ ước, nắn theo τ) hoặc
mượn tin từ mã khác (BTC dẫn ETH/SOL/XRP). Không hướng nào hỏi câu này:

    **σ đo từ 900 giây vừa qua có thiên vị theo GIỜ TRONG NGÀY không?**

Có lý do để ngờ là có. Biến động crypto có mùa vụ trong ngày rất rõ —
phiên Mỹ mở, phiên Á mở, quãng chết cuối tuần. Một bộ ước nhìn lại 900
giây thì luôn CHẬM một nhịp so với mùa vụ ấy: ngay trước giờ sôi động nó
đọc σ của quãng lặng, và ngược lại.

Đây là THÔNG TIN MỚI thật, không phải một cách vặn khác của cùng một số:
giờ trong ngày không nằm trong 900 giây nến vừa qua.

## Ứng viên

    trơn        σ như đang dùng                          (đương nhiệm)
    mua-vu-4    σ × hệ số riêng cho từng khối 6 giờ UTC
    mua-vu-8    σ × hệ số riêng cho từng khối 3 giờ UTC

Bốn khối chứ không phải 24 giờ riêng: 24 tham số trên chừng 4.000 khung
là 170 khung mỗi tham số — thừa chỗ cho tiếng ồn mặc áo quy luật. Khối 6
giờ giữ bậc tự do ở mức 4, và `mua-vu-8` có mặt để xem chia mịn hơn thì
khá lên hay tệ đi. Nếu mịn hơn mà TỆ đi thì chính điều đó là bằng chứng
đang khớp quá, và nó đáng giá ngang một kết quả dương.

Hệ số học TRÊN TẬP HỌC và chỉ trên tập ấy. Kẹp vào [0,70; 1,40] — một hệ
số ngoài dải đó không phải mùa vụ, nó là vài khung dị thường.

## Chấm y hệt vòng tự nâng cấp

Ba tập tách theo THỜI GIAN: HỌC khớp phép nắn VÀ hệ số mùa vụ, CHỌN xếp
hạng, CHỐT chỉ gật hay lắc. Khoảng tin lấy lại THEO KHUNG.

Bẫy riêng của phép thử này: mùa vụ theo giờ mà học trên quãng NGẮN thì hệ
số mỗi khối chỉ dựa vào vài ngày. Để `--ngay` nhỏ là tự chuốc một kết quả
đẹp mà rỗng — mặc định 20 ngày.
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
}, ten='thu-mua-vu-gio.py')


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




KHOI = {"mua-vu-4": 4, "mua-vu-8": 8}


def _khoi(T: int, soKhoi: int) -> int:
    """Mốc T rơi vào khối giờ nào. Giờ UTC, chia đều."""
    gio = (T // 3_600_000) % 24
    return int(gio * soKhoi // 24)


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


def he_so_mua_vu(oh, mocsHoc, soNen, soKhoi):
    """Học hệ số từng khối giờ TRÊN TẬP HỌC.

    Hệ số = độ lớn log-return THẬT của 5 phút tới, chia cho độ lớn mà σ
    đang dự báo. Lớn hơn 1 nghĩa là bộ ước đang DƯỚI ước ở khối giờ ấy.

    Dùng TRUNG VỊ của tỉ số, không phải tỉ số của trung bình: một khung
    nhảy giá làm hỏng trung bình, mà mùa vụ là chuyện của phần ĐÔNG các
    khung chứ không phải của cái đuôi. Chia cho 0,6745 vì trung vị của
    |N(0,1)| là 0,6745 — chuẩn hoá để hệ số 1,0 nghĩa là 'bộ ước đang
    đúng', chứ không phải một con số không tên.
    """
    theoKhoi: dict = {}
    for T in mocsHoc:
        n0, n5 = oh.get(T), oh.get(T + 5 * int(PHUT))
        if n0 is None or n5 is None:
            continue
        sig = uoc_tron(oh, T, soNen)
        if not sig:
            continue
        try:
            that = abs(math.log(n5[3] / n0[3]))
        except (ValueError, ZeroDivisionError):
            continue
        duBao = sig * math.sqrt(300.0)
        if duBao <= 0:
            continue
        theoKhoi.setdefault(_khoi(T, soKhoi), []).append(that / duBao)
    hs = {}
    for k, ds in theoKhoi.items():
        if len(ds) < 40:
            continue
        m = statistics.median(ds) / 0.6745
        hs[k] = min(1.40, max(0.70, m))
    return hs


def uoc_theo_mua_vu(hs, soKhoi):
    """Bộ ước σ đã nhân hệ số mùa vụ của khối giờ tương ứng."""
    def ham(oh, T, soNen):
        s = uoc_tron(oh, T, soNen)
        if s is None:
            return None
        return s * hs.get(_khoi(T, soKhoi), 1.0)
    return ham

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
    print("  σ CÓ MÙA VỤ TRONG NGÀY KHÔNG — hướng thứ bảy")
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
    ketQua["trơn"] = cham(oh, ba, uoc_tron, soNen)
    for ten, soKhoi in KHOI.items():
        hs = he_so_mua_vu(oh, ba[0], soNen, soKhoi)
        if len(hs) < soKhoi:
            print("  " + ten + ": chỉ học được " + str(len(hs)) + "/"
                  + str(soKhoi) + " khối — bỏ qua.")
            continue
        print("  " + ten + ": hệ số theo khối = "
              + " · ".join(str(k) + ":" + format(hs[k], ".3f")
                            for k in sorted(hs)))
        ketQua[ten] = cham(oh, ba, uoc_theo_mua_vu(hs, soKhoi), soNen)

    ketQua = {k: v for k, v in ketQua.items() if v}
    if "trơn" not in ketQua:
        print("  chưa đủ cặp.")
        return 1

    print()
    print("    ứng viên        cặp CHỌN   Brier CHỌN   Brier CHỐT")
    for ten, r in ketQua.items():
        print("    " + ten.ljust(14)
              + format(r["n"], ",").rjust(9)
              + format(r["chon"], ".5f").rjust(13)
              + format(r["chot"], ".5f").rjust(13))

    goc = ketQua["trơn"]
    ung = {k: v for k, v in ketQua.items() if k != "trơn"}
    if not ung:
        print(N + "  Không ứng viên nào chạy được." + N)
        return 0
    tot = min(ung, key=lambda k: ung[k]["chon"])
    r = ung[tot]
    # Biên siết theo SỐ ỨNG VIÊN — dùng chung hàm với vòng tự nâng
    # cấp, không chép lại công thức. Hai bản sao của một phép
    # hiệu chỉnh đa so sánh thì sớm muộn lệch nhau.
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
