"""Khớp đường nắn trên NHIỀU coin hơn bốn coin đang theo — có tốt hơn không?

    python scripts/thu-nan-them-coin.py --ngay=20
    python scripts/thu-nan-them-coin.py --ngay=20 --them=BNBUSDT,DOGEUSDT

## Câu hỏi

`dinh_gia` áp MỘT sổ hiệu chỉnh cho cả bốn chợ, và
`do-nan-chung-hay-rieng.py` đã đo ngoài mẫu rằng một đường CHUNG là đúng
(1,590c so với bốn đường riêng 1,640c). Câu tiếp theo chưa ai hỏi:
đường chung ấy nên khớp trên MẤY coin?

Bảng nắn là một hàm của `p` — nó nói "mô hình bảo 0,70 thì thực tế ra
bao nhiêu". Nếu quan hệ ấy là tính chất của MÔ HÌNH (khuếch tán
log-chuẩn với σ ước từ nến phút) chứ không của riêng BTC, thì mọi coin
có cùng cấu trúc đều là mẫu hợp lệ, và thêm coin là thêm mẫu MIỄN PHÍ:
Binance cho không, không cần Polymarket niêm yết chúng.

Nếu ngược lại — mỗi coin lệch một kiểu — thì thêm coin là pha loãng, và
đường nắn áp cho BTC/ETH/SOL/XRP sẽ tệ đi.

## Chấm thế nào

Chỉ chấm trên BỐN CHỢ ĐANG THEO, vì đó là nơi đường nắn được dùng. Coin
thêm vào chỉ tham gia phần KHỚP.

    HỌC   50% mốc đầu   khớp bảng (có/không có coin thêm)
    CHỐT  25% mốc cuối  chấm, trên bốn chợ đang theo

Thước là Brier sau nắn. Khoảng tin bootstrap chia khối theo KHUNG — bốn
lát τ của một khung chia chung MỘT kết quả.

Tập CHỌN cố tình KHÔNG dùng: đây là một giả thuyết ĐỊNH TRƯỚC với đúng
hai nhánh, không phải một cuộc quét nhiều ứng viên.

## Chỗ dễ tự lừa

Thêm coin làm bảng DÀY hơn, và một bảng dày hơn gần như luôn cho Brier
trong mẫu tốt hơn. Nên mọi con số ở đây là NGOÀI MẪU, và mốc thời gian
của tập chốt nằm sau toàn bộ tập học.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "ngay": "số ngày nến lấy về",
    "them": "danh sách cặp Binance thêm vào phần KHỚP, cách nhau dấu phẩy",
}, ten='thu-nan-them-coin.py')

from kham.dinh_gia import HieuChinh  # noqa: E402
from kham.hoc_offline import (cap_du_doan, cua_so_sigma,  # noqa: E402
                              khoang_tin_theo_khoi, nen_1p, quen_sigma)
from kham.ket_qua import thi_truong_doi_chieu_duoc  # noqa: E402
from kham.nan_lai import khop  # noqa: E402

PHUT = 60_000.0
SO_NGAY = float(CO.lay("ngay", "20"))
THEM = [x.strip().upper() for x in (CO.lay("them") or
        "BNBUSDT,DOGEUSDT,ADAUSDT,AVAXUSDT").split(",") if x.strip()]
CHIA_HOC = 0.50


def _cap(theoMoc: dict, mocs: list, ma: str, cuaSo: float) -> list:
    quen_sigma()
    return cap_du_doan(theoMoc, mocs, ma, cuaSo, keoMoc=True)


def _brier_nan(pn, cap) -> float:
    return sum(((pn.nan(p) if pn.dung_duoc else p)
                - (1.0 if t else 0.0)) ** 2 for p, t, *_ in cap) / max(1, len(cap))


def _sai_tung_cap(pn, cap) -> list[float]:
    return [((pn.nan(p) if pn.dung_duoc else p) - (1.0 if t else 0.0)) ** 2
            for p, t, *_ in cap]


def main() -> int:
    cuaSo = cua_so_sigma()
    soNen = int(SO_NGAY * 24 * 60 + cuaSo / 60.0 + 20)
    het = int(time.time() * 1000.0 // PHUT * PHUT) - int(PHUT)

    theo = [(str(t["ma"]), str(t["nen"])) for t in thi_truong_doi_chieu_duoc()]
    print()
    print("=" * 78)
    print("  KHỚP ĐƯỜNG NẮN TRÊN NHIỀU COIN HƠN — CÓ TỐT HƠN KHÔNG")
    print("=" * 78)
    print(f"  chấm trên : {', '.join(m for m, _ in theo)}")
    print(f"  thêm vào  : {', '.join(THEM)}")
    print(f"  {SO_NGAY:g} ngày · lấy {soNen:,} nến mỗi cặp…", flush=True)

    luoi: dict[str, dict] = {}
    for ma, cap in theo:
        luoi[ma] = nen_1p(cap, het - soNen * PHUT, soNen)
    for cap in THEM:
        g = nen_1p(cap, het - soNen * PHUT, soNen)
        if len(g) < 1200:
            print(f"    {cap}: chỉ {len(g)} nến — bỏ")
            continue
        luoi["+" + cap] = g

    thieu = [m for m, g in luoi.items() if len(g) < 1200]
    if thieu:
        print(f"  thiếu nến: {thieu}")
    print(f"  {len(luoi)} lưới · " + " · ".join(
        f"{m} {len(g):,}" for m, g in luoi.items()))

    mocs = sorted({T for m, _ in theo for T in luoi[m] if T % 300_000 == 0})
    cat = int(len(mocs) * CHIA_HOC)
    mHoc, mChot = mocs[:cat], mocs[int(len(mocs) * 0.75):]
    print(f"  HỌC {len(mHoc):,} mốc · CHỐT {len(mChot):,} mốc "
          f"(tách theo THỜI GIAN)")
    if len(mHoc) < 500 or len(mChot) < 250:
        print("  chưa đủ mốc.\n")
        return 1

    # cặp để CHẤM: chỉ bốn chợ đang theo, chỉ tập CHỐT
    chot = []
    for ma, _ in theo:
        chot.extend(_cap(luoi[ma], mChot, ma, cuaSo))
    if len(chot) < 500:
        print(f"  chỉ dựng được {len(chot)} cặp chốt.\n")
        return 1
    print(f"  {len(chot):,} cặp chấm trên tập CHỐT")
    print()

    def _khop_tren(dsMa: list[str]):
        hc = HieuChinh(duong=GOC / "data" / "_tam-them-coin.json")
        hc.o = {}
        n = 0
        for ma in dsMa:
            g = luoi.get(ma)
            if not g or len(g) < 1200:
                continue
            ms = [T for T in mHoc if T in g] if not ma.startswith("+") else \
                 [T for T in sorted(g) if T % 300_000 == 0 and T <= mHoc[-1]]
            for p, t, *_ in _cap(g, ms, ma.lstrip("+"), cuaSo):
                hc.them(p, t)
                n += 1
        return khop(hc), n

    maTheo = [m for m, _ in theo]
    pnGoc, nGoc = _khop_tren(maTheo)
    pnMoi, nMoi = _khop_tren(maTheo + [m for m in luoi if m.startswith("+")])

    bGoc, bMoi = _brier_nan(pnGoc, chot), _brier_nan(pnMoi, chot)
    print(f"    {'khớp trên':<28}{'mẫu':>10}{'Brier CHỐT':>14}")
    print(f"    {'bốn chợ đang theo':<28}{nGoc:>10,}{bGoc:>14.5f}")
    print(f"    {'+ ' + str(len(THEM)) + ' coin nữa':<28}{nMoi:>10,}{bMoi:>14.5f}")
    print()

    a, b = _sai_tung_cap(pnGoc, chot), _sai_tung_cap(pnMoi, chot)
    hieu = [b[i] - a[i] for i in range(len(a))]
    thap, cao, soK = khoang_tin_theo_khoi(hieu, [x[-1] for x in chot])
    print(f"  khoảng tin 95% (thêm coin − chỉ bốn chợ), theo KHUNG:")
    print(f"    [{thap:+.6f}, {cao:+.6f}]  ({soK} khối)")
    print()
    if cao < 0:
        print("  THÊM COIN TỐT HƠN có ý nghĩa — đường nắn là tính chất của")
        print("  MÔ HÌNH, không của riêng bốn coin ấy, nên thêm mẫu là thêm")
        print("  bằng chứng. Cân nhắc mở rộng phần KHỚP của sổ hiệu chỉnh.")
    elif thap > 0:
        print("  THÊM COIN TỆ HƠN có ý nghĩa — mỗi coin lệch một kiểu, nên")
        print("  thêm vào là pha loãng. Giữ nguyên bốn chợ.")
    else:
        print("  KHÔNG đủ bằng chứng: khoảng tin chứa 0. Giữ nguyên bốn chợ")
        print("  là kết quả hợp lệ, và nó rẻ hơn — ít lời gọi mạng hơn mỗi")
        print("  vòng ngày.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
