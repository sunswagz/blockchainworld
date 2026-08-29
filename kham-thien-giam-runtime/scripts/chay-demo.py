r"""DEMO — cả cỗ máy chạy, tiền ảo, dữ liệu thật, kế toán thật.

    python scripts/chay-demo.py                         # cả ba chợ, 3 ngày
    python scripts/chay-demo.py --von=50000 --ngay=7
    python scripts/chay-demo.py --cho=cong-bang

Chạy `PhienPhatLai` — đúng cỗ máy thật: định giá qua sổ đăng ký động cơ,
nắn theo sổ hiệu chỉnh, sáu ngón chiến thuật, cầu dao rủi ro với Kelly,
khớp giấy theo VWAP có phí, tồn kho, kết toán, sổ.

Khung ăn thua dựng từ nến Binance (`kham/cho_gia_dinh.py`): giá nền, σ,
strike và KẾT QUẢ đều thật; spread và độ sâu sổ lệnh đo từ 127.816 lát sổ
Polymarket đã ghi. Đúng một thứ giả định — mức giá chợ yết — và nó là
tham số có tên.

## Đọc kết quả theo đúng thứ tự

    1. `hoan-hao` phải LỖ. Chợ biết y hệt ta thì lợi thế bằng 0 và phí
       ăn phần còn lại. Nó LÃI nghĩa là có lỗi ở đâu đó, và mọi con số
       khác trong phiên này vô nghĩa cho tới khi tìm ra.
    2. `cong-bang` là CẬN TRÊN. Chợ thật đo được có kỹ năng +6,6% so với
       tỉ lệ nền, khó hơn hẳn một đồng xu. Thua ở đây thì khỏi bàn tiếp.
    3. `tho` đo phép nắn đáng bao nhiêu tiền — một KỊCH BẢN, không phải
       dự báo: chợ thật không mắc đúng lỗi của mô hình ta.

## Và câu hỏi sắc hơn cả ba: `--quet`

Ba cái chợ trên là hai đầu mút và một kịch bản. Câu thật sự cần trả lời
nằm ở GIỮA: **chợ phải giỏi tới đâu thì bot hết lãi?**

`--quet` chạy một dãy chợ pha giữa hai đầu mút:

    p_chợ = 0,5 + w · (p_đã_nắn − 0,5),     w từ 0 tới 1

w=0 là chợ mù, w=1 là chợ biết y hệt ta. Điểm hoà vốn w* là con số quyết
định cả cung này có tương lai hay không, vì nó biến câu hỏi mơ hồ "bot có
ăn được chợ không" thành một câu đo được: **chợ thật giỏi hơn hay kém
hơn w\*?**

KHÔNG dùng con số +6,6% đã đo để chọn w. Con số ấy đo chợ ở CUỐI CỬA ĐẶT
CƯỢC, nơi strike chưa tồn tại — trong khung ăn thua thì strike đã biết và
chợ gần như chắc chắn định giá tốt hơn hẳn. Lấy nó sang đây là rộng rãi
với chính mình một cách không có cơ sở.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402
from kham.cho_gia_dinh import PHUT, dung_khung  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.nan_lai import khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402
from kham.phat_lai import PhienPhatLai  # noqa: E402


CO = tham_so.doc({
    "cho": "chợ giả định: cong-bang | ...",
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "số ngày băng/nến lấy về",
    "quet": tham_so.BAT,
    "von": "vốn ảo ban đầu, USD",
}, ten='chay-demo.py')


VON = float(CO.lay("von", "10000"))
SO_NGAY = int(CO.lay("ngay", "3"))
MA = CO.lay("ma", "BTC_5M")
CHO = CO.lay("cho", "")
QUET = CO.co("quet")
BAC_QUET = (0.0, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0)
RIENG = GOC / "data" / "demo"

CAU_HOI = {
    "hoan-hao": "chợ biết y hệt ta → PHẢI LỖ, nếu lãi là có lỗi",
    "cong-bang": "chợ không biết gì → CẬN TRÊN, thắng mới là điều kiện cần",
    "tho": "chợ mắc đúng lỗi của mô hình thô → phép nắn đáng bao nhiêu",
}


def _tien(x: float) -> str:
    return f"{'-' if x < 0 else ''}${abs(x):,.2f}"


def nen_1p(cap: str, tuMs: float, soNen: int) -> dict:
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


def mot_cho(kieu: str, theoMoc: dict, pn) -> None:
    def p_tho(S, K, tau, sig):
        gc = dinh_gia(MA, S, K, tau, sig)
        return None if gc is None else gc.pUp

    def p_nan(S, K, tau, sig):
        p = p_tho(S, K, tau, sig)
        if p is None:
            return None
        return pn.nan(p) if pn.dung_duoc else p

    ham = {"cong-bang": None, "tho": p_tho, "hoan-hao": p_nan}[kieu]
    khung = dung_khung(theoMoc, MA, kieu, ham)

    p = PhienPhatLai(von=VON, thuMucSo=RIENG / kieu)
    kq = p.chay(khung)

    print()
    print("  " + "─" * 72)
    print(f"  CHỢ `{kieu}` — {CAU_HOI[kieu]}")
    print("  " + "─" * 72)
    print(f"    khung hình {kq.soKhungHinh:>8,} · cửa sổ {kq.soCuaSo:>6,} · "
          f"lệnh {kq.soLenh:>6,} · khớp {kq.soKhop:>6,}")
    print(f"    kết toán   {kq.soKetToan:>8,} · thắng {kq.soThang:>6,} / "
          f"thua {kq.soThua:<6,} ({kq.tiLeThang:.1%})")
    print(f"    vốn {_tien(kq.von0)} → {_tien(kq.von)}   "
          f"lãi lỗ {_tien(kq.tongLaiLo)}  ({kq.loiNhuanPct:+.2f}%)")
    print(f"    phí {_tien(kq.tongPhi)} · sụt vốn {kq.sutVonPct:.2f}% · "
          f"lỗ nặng nhất {_tien(kq.thuaLonNhat)}")
    if kq.ngatLucKhung:
        print(f"    ⚠ cầu dao ngắt ở khung {kq.ngatLucKhung:,} — {kq.ngatLyDo}")
    if kq.soKetToan:
        print(f"    lãi lỗ mỗi cửa sổ {_tien(kq.tongLaiLo/kq.soKetToan)}")
    if not kq.soKhop and kq.boQua:
        print("    KHÔNG khớp lệnh nào. Lý do hàng đầu:")
        for ly, n in sorted(kq.boQua.items(), key=lambda x: -x[1])[:3]:
            print(f"      {n:>8,} × {ly}")
    if not kq.soKhop and kq.lyDoTuChoi:
        for ly, n in sorted(kq.lyDoTuChoi.items(), key=lambda x: -x[1])[:3]:
            print(f"      {n:>8,} × rủi ro: {ly}")

    # Chốt an toàn của `hoan-hao`, in NGAY tại chỗ chứ không để người đọc
    # tự nhớ mà đối chiếu.
    if kieu == "hoan-hao" and kq.tongLaiLo > 0:
        print()
        print("    ⚠⚠ CHỢ BIẾT Y HỆT TA MÀ VẪN LÃI. Đây là dấu hiệu LỖI,")
        print("       không phải dấu hiệu giỏi. Mọi con số của các chợ khác")
        print("       trong phiên này KHÔNG dùng được cho tới khi tìm ra.")


def quet(theoMoc: dict, pn) -> None:
    """Chợ giỏi tới đâu thì bot hết lãi. Đây là con số quyết định."""
    def p_nan(S, K, tau, sig):
        gc = dinh_gia(MA, S, K, tau, sig)
        if gc is None:
            return None
        return pn.nan(gc.pUp) if pn.dung_duoc else gc.pUp

    print()
    print("  " + "=" * 72)
    print("  QUÉT — chợ phải giỏi tới đâu thì bot hết lãi")
    print("  " + "=" * 72)
    print("    p_chợ = 0,5 + w·(p_đã_nắn − 0,5).  w=0 chợ mù, w=1 chợ biết")
    print("    y hệt ta. Điểm hoà vốn w* biến câu hỏi 'bot có ăn được chợ")
    print("    không' thành một câu đo được.")
    print()
    print("       w      cửa sổ   khớp   kết toán  thắng     lãi lỗ      %vốn")
    truoc = None
    hoaVon = None
    for w in BAC_QUET:
        def pha(S, K, tau, sig, _w=w):
            p = p_nan(S, K, tau, sig)
            return None if p is None else 0.5 + _w * (p - 0.5)

        khung = dung_khung(theoMoc, MA, "pha", pha)
        ph = PhienPhatLai(von=VON, thuMucSo=RIENG / f"quet-{w:g}")
        kq = ph.chay(khung)
        print(f"    {w:>4.2f}   {kq.soCuaSo:>7,} {kq.soKhop:>7,} "
              f"{kq.soKetToan:>9,}  {kq.tiLeThang:>5.1%}  "
              f"{_tien(kq.tongLaiLo):>11}  {kq.loiNhuanPct:>+7.2f}%")
        if truoc is not None and truoc > 0 >= kq.tongLaiLo and hoaVon is None:
            hoaVon = w
        truoc = kq.tongLaiLo

    print()
    if hoaVon is None:
        print("    Không thấy điểm hoà vốn trong dãy đã quét.")
    else:
        print(f"    Hoà vốn quanh w ≈ {hoaVon:g}: chợ giỏi hơn mức đó thì bot LỖ.")
    print()
    print("    KHÔNG lấy con số +6,6% đã đo để chọn w. Nó đo chợ ở CUỐI CỬA")
    print("    ĐẶT CƯỢC, nơi strike chưa tồn tại; trong khung ăn thua thì")
    print("    strike đã biết và chợ gần như chắc chắn định giá tốt hơn hẳn.")
    print("    Muốn biết chợ thật nằm ở đâu trên thang này thì phải có SỔ")
    print("    LỆNH trong [T, T+300] — runtime đã sẵn sàng ghi, chỉ chờ đường.")


def main() -> int:
    cap = next((t.get("nen") for t in CONFIG["thiTruong"]
                if t.get("ma") == MA), None)
    if not cap:
        print(f"\n  Không có market `{MA}` trong config.\n")
        return 1

    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    soNen = SO_NGAY * 24 * 60 + 10
    print()
    print("=" * 76)
    print("  DEMO KHÂM THIÊN GIÁM — tiền ẢO, dữ liệu THẬT, kế toán THẬT")
    print("=" * 76)
    print(f"  {MA} ({cap}) · {SO_NGAY} ngày · vốn {_tien(VON)}")
    print(f"  lấy {soNen:,} nến 1 phút…", flush=True)
    theoMoc = nen_1p(cap, hetMs - soNen * PHUT, soNen)
    if len(theoMoc) < 400:
        print(f"  Chỉ lấy được {len(theoMoc)} nến. Không đủ.\n")
        return 1
    print(f"  đã lấy {len(theoMoc):,} nến")

    hc = HieuChinh()
    pn = khop(hc)
    print(f"  sổ hiệu chỉnh {hc.tong_mau:,} mẫu · phép nắn dùng được "
          f"{pn.dung_duoc}"
          + (f" · sai {pn.saiTruoc*100:.2f} → {pn.saiSau*100:.2f} điểm"
             if pn.dung_duoc else ""))

    # `hoan-hao` chạy TRƯỚC: nó là máy dò lỗi, và biết sớm thì đỡ đọc
    # nhầm hai con số kia.
    if QUET:
        quet(theoMoc, pn)
    else:
        for kieu in (["hoan-hao", "cong-bang", "tho"] if not CHO else [CHO]):
            mot_cho(kieu, theoMoc, pn)

    print()
    print("=" * 76)
    print("  Đọc theo thứ tự: `hoan-hao` phải LỖ (nếu lãi là có lỗi) →")
    print("  `cong-bang` là CẬN TRÊN, thắng nó mới là điều kiện CẦN →")
    print("  `tho` là một kịch bản, không phải dự báo.")
    print()
    print("  Chợ THẬT khó hơn `cong-bang`: đo được nó có kỹ năng +6,6% so")
    print("  với tỉ lệ nền. Và phiên này không có tác động thị trường,")
    print("  không trượt giá theo thời gian, không chọn lọc bất lợi.")
    print("=" * 76)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
