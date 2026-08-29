r"""KHỐI LƯỢNG có báo trước biến động không? Hướng thứ tám.

    python scripts/thu-khoi-luong.py --ngay=20

Bảy hướng đã đóng. Sáu hướng đầu chỉ vặn cách đo σ từ GIÁ; hướng thứ bảy
(mùa vụ theo giờ) là hướng đầu tiên thêm tin ngoài giá, và nó đóng lại
với hệ số 0,87–1,06 — bộ ước vốn đã không thiên vị theo giờ.

Còn một thứ nữa nằm sẵn trong chính cây nến Binance mà chưa ai dùng:
**khối lượng**. Mô hình hiện tại vứt nó đi hoàn toàn.

Lý do để ngờ nó có ích rất cụ thể: quan hệ khối-lượng–biến-động là một
trong những điều bền nhất trong tài chính thực nghiệm. Mười lăm phút vừa
qua giao dịch gấp ba mức thường ngày thì mười lăm phút tới hiếm khi lặng.
Bộ ước σ hiện tại chỉ thấy giá đã đi bao xa, không thấy nó đi qua bao
nhiêu tay.

Chú ý phân biệt với hướng đã đóng "dòng lệnh nhịp 1 phút (taker buy)":
cái đó đo HƯỚNG (mua nhiều hơn hay bán nhiều hơn), cái này đo ĐỘ LỚN.
Hai câu hỏi khác nhau, và câu thứ hai dễ hơn hẳn — độ lớn không đòi ai
phải đoán đúng chiều.

## Ứng viên

    beta 0.00   σ như đang dùng — ĐƯƠNG NHIỆM, cũng là phép đối chứng
    beta 0.10   σ × (V/V_thường)^0.10
    beta 0.20   ...
    beta 0.30
    beta 0.50

MỘT tham số duy nhất, dò trên lưới năm điểm. `beta 0.00` nằm trong lưới
cố ý: nếu tiếng ồn đủ để một beta khác thắng nó, ta thấy ngay bằng chính
khoảng cách giữa chúng.

`V_thường` là TRUNG VỊ khối lượng cửa sổ, học TRÊN TẬP HỌC. Trung vị chứ
không phải trung bình: khối lượng có đuôi rất dày, một cú xả làm trung
bình vô nghĩa. Hệ số kẹp [0,60; 1,70].

## Chấm y hệt vòng tự nâng cấp

Ba tập tách theo THỜI GIAN, khoảng tin lấy lại THEO KHUNG, biên siết theo
số ứng viên bằng `hoc_offline.bien_theo_ung_vien`.
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
}, ten='thu-khoi-luong.py')


SO_NGAY = int(CO.lay("ngay", "20"))
MA = CO.lay("ma", "BTC_5M")
CUA_SO = float(CO.lay("cuaso", "900"))


# ══════════════════════════════════════════════════════════════════════
#  BỐN BỘ ƯỚC — tất cả trả về σ MỖI GIÂY
# ══════════════════════════════════════════════════════════════════════


#: Lưới beta. 0.0 là ĐƯƠNG NHIỆM, cố ý nằm trong lưới làm đối chứng.
BETA = (0.0, 0.10, 0.20, 0.30, 0.50)


def nen_ohlcv(cap: str, tuMs: float, soNen: int) -> dict:
    """{mốc đóng: (mở, cao, thấp, đóng, KHỐI LƯỢNG)}.

    `nen_ohlc` của mấy phép thử trước vứt cột khối lượng đi. Đây là
    lý do phải có bản riêng — và cũng là lý do phép thử này có nghĩa:
    cột ấy nằm sẵn trong mọi lời gọi kline suốt từ đầu mà chưa ai đọc.
    """
    moc = int(tuMs // PHUT * PHUT)
    ra: dict = {}
    con = soNen
    while con > 0:
        lo = min(1000, con)
        d = nguon._lay("binance-kline",
                       CONFIG['nguon']['binanceSpot'] + '/api/v3/klines',
                       {"symbol": cap, "interval": "1m",
                        "startTime": moc, "limit": lo})
        if not isinstance(d, list) or not d:
            break
        for n in d:
            try:
                ra[int(n[0]) + int(PHUT)] = (float(n[1]), float(n[2]),
                                             float(n[3]), float(n[4]),
                                             float(n[5]))
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


def khoi_luong_cua_so(oh, T, soNen):
    """Tổng khối lượng trong đúng cửa sổ mà σ đang nhìn."""
    c = _lay_nen(oh, T, soNen)
    if c is None:
        return None
    try:
        return sum(x[4] for x in c)
    except (IndexError, TypeError):
        return None


def khoi_luong_thuong(oh, mocsHoc, soNen):
    """TRUNG VỊ khối lượng cửa sổ, học trên tập HỌC.

    Trung vị chứ không phải trung bình: khối lượng có đuôi rất dày, một
    cú xả làm trung bình vô nghĩa và kéo mọi hệ số về dưới 1.
    """
    ds = []
    for T in mocsHoc:
        v = khoi_luong_cua_so(oh, T, soNen)
        if v and v > 0:
            ds.append(v)
    return statistics.median(ds) if len(ds) >= 100 else None


def uoc_theo_khoi_luong(vThuong, beta):
    """σ nhân (V/V_thường)^beta. beta = 0 trả về đúng bộ ước đương nhiệm."""
    def ham(oh, T, soNen):
        s = uoc_tron(oh, T, soNen)
        if s is None:
            return None
        if beta == 0.0:
            return s
        v = khoi_luong_cua_so(oh, T, soNen)
        if not v or v <= 0 or not vThuong:
            return s
        he = (v / vThuong) ** beta
        return s * min(1.70, max(0.60, he))
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
    print("  KHỐI LƯỢNG CÓ BÁO TRƯỚC BIẾN ĐỘNG KHÔNG — hướng thứ tám")
    print("=" * 76)
    print("  " + MA + " (" + cap + ") · " + str(SO_NGAY) + " ngày · cửa sổ "
          + format(CUA_SO, "g") + "s (" + str(soNen) + " nến) · lấy "
          + format(tong, ",") + " nến…", flush=True)

    oh = nen_ohlcv(cap, hetMs - tong * PHUT, tong)
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

    vThuong = khoi_luong_thuong(oh, ba[0], soNen)
    if not vThuong:
        print("  không học được khối lượng thường. Dừng." + N)
        return 1
    print("  khối lượng thường (trung vị tập HỌC): "
          + format(vThuong, ",.1f"))

    ketQua = {}
    for beta in BETA:
        ten = "beta " + format(beta, ".2f")
        ketQua[ten] = _cham_chung(oh, ba, uoc_theo_khoi_luong(vThuong, beta),
                           soNen)
    ketQua = {k: v for k, v in ketQua.items() if v}
    goc_ten = "beta 0.00"
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
