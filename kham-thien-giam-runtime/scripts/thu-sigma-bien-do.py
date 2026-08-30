"""σ ước từ BIÊN ĐỘ cao–thấp có tốt hơn σ ước từ giá đóng không?

    python scripts/thu-sigma-bien-do.py --ngay=20

## Vì sao hỏi

Bộ ước đang chạy (`DoBienDong`) lấy độ lệch chuẩn log-return giữa các
giá ĐÓNG của từng phút. Nó vứt đi biên độ trong phút: một phút giá chạy
lên 0,3% rồi về chỗ cũ được tính là "không biến động".

Parkinson (1980) dùng chính biên độ ấy:

    σ²_phút = (ln(H/L))² / (4 ln 2)

Với chuyển động Brown, ước lượng này có phương sai nhỏ hơn ước lượng
đóng-đến-đóng chừng **5 lần** — cùng số nến cho một con số ít nhiễu hơn
hẳn. Và σ là mẫu số của z, nên bớt nhiễu ở σ là bớt nhiễu ở MỌI dự báo.

Nó KHÔNG phải `dinhGia.heSoSigma` đã thử và bị bác: nút ấy nhân σ với
một hằng số (đo trên 20 ngày thì có ý nghĩa, đo lại trên 40 ngày thì
biến mất). Đây là một bộ ước KHÁC — cùng kỳ vọng, ít phương sai hơn.

## Ba biến thể đem so

    dong    đóng-đến-đóng, đúng bộ ước đang chạy (mốc so)
    bienDo  Parkinson thuần
    pha     trung bình hình học của hai cái trên — Parkinson giả định
            không có nhảy giá qua đêm và không có khe mở cửa; trộn lại
            là cách rẻ để giữ phần đúng của cả hai

## KẾT QUẢ 30/08/2026 — và vì sao CHƯA đổi bộ ước đang chạy

Hai quãng 20 ngày KHÔNG chồng lấn, bốn chợ, chấm ngoài mẫu trên tập
CHỐT, bootstrap chia khối theo KHUNG (1.441 khối mỗi quãng):

    quãng            bienDo                    pha
    gần đây   [-0,000618, +0,000303]   [-0,000485, -0,000026]  TỐT HƠN
    20–40 ngày[-0,000677, +0,000194]   [-0,000472, -0,000041]  TỐT HƠN

`bienDo` thuần: chứa 0 ở cả hai quãng. `pha` (trung bình hình học):
TỐT HƠN có ý nghĩa ở CẢ HAI, độ lớn gần hệt nhau, và cùng chiều trên cả
tập CHỌN lẫn CHỐT. Đây là bằng chứng mạnh hơn hẳn ca `dinhGia.heSoSigma`
— nút ấy có ý nghĩa trên 20 ngày rồi biến mất trên 40, còn chiều thì
ĐẢO trên tập CHỌN.

**Nhưng chưa đổi được, và lý do là một chỗ chặn thật.** Bộ ước SỐNG
(`DoBienDong` trong `vong.py`) chỉ nạp mồi MỘT LẦN từ nến 1 phút, sau
đó được nuôi bằng `bd.them(gia, now)` — GIÁ LẤY MẪU, mỗi phút một điểm.
Nó không có cao–thấp thật của phút ấy. Cao–thấp dựng từ mẫu 2 giây thì
HẸP HƠN cao–thấp thật, nên Parkinson tính trên mẫu sẽ ra một con số
khác hẳn con số đo được ở đây.

Đổi bộ ước mà không đổi NGUỒN NUÔI nó là vặn nút của cỗ máy A rồi lắp
vào cỗ máy B — đúng cái đã cắn một lần (`tu-nang-cap.py` vặn cửa sổ σ
trên lưới phút trong khi runtime chạy bộ ước mẫu thô, σ thật chỉ bằng
0,875 lần σ đã tuning).

Việc phải làm TRƯỚC, theo thứ tự:

  1. nuôi `DoBienDong` bằng nến 1 phút THẬT (`nguon.nen_gan_day`) mỗi
     phút, không phải bằng giá lấy mẫu — 4 lời gọi/phút, weight 8 trên
     hạn mức 1.200, không đáng kể;
  2. cho `DoBienDong` giữ được (đóng, cao, thấp) chứ không chỉ đóng;
  3. đo lại `dinhGia.bienDongCuaSoGiay` — ghi chú của nó tự đặt điều
     kiện "đo lại khi bộ ước σ đổi";
  4. rồi mới bật `pha`, và vẫn phải đo lại trên hai quãng không chồng
     lấn như ở đây.

Ghi con số ÂM này lại là để bước 1–4 có lý do, chứ không phải để ai đó
đọc thấy "tốt hơn" rồi đổi thẳng.

## Vì sao script này ĐƯỢC phép tự viết bộ ước

`selftest` có một luật: mọi `_sigma` riêng trong `scripts/` phải ra
ĐÚNG con số của bộ ước chung — vì một script kết luận về mô hình bằng
σ khác σ của mô hình thì nói về một cỗ máy không tồn tại.

Script này là NGOẠI LỆ cùng loại với `thu-uoc-sigma.py`: việc của nó
CHÍNH LÀ so các bộ ước với nhau. Nên nó khai tên khác (`_sigma_dong`,
`_sigma_bien_do`) và mốc so `dong` phải trùng khớp bộ ước chung tới
1e-15 — phép kiểm ấy nằm ngay trong script, chạy trước khi đo.
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

CO = tham_so.doc({
    "ngay": "số ngày nến lấy về",
    "ma": "mã thị trường, ví dụ BTC_5M",
    "lui": "lùi mốc KẾT THÚC lại bấy nhiêu ngày — để đo một quãng CŨ, "
           "không chồng lấn với quãng vừa đo",
}, ten='thu-sigma-bien-do.py')

from kham.ban_thu import nen_ohlc  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.hoc_offline import (cua_so_sigma, khoang_tin_theo_khoi,  # noqa: E402
                              quen_sigma, sigma_tai)
from kham.ket_qua import thi_truong_doi_chieu_duoc  # noqa: E402
from kham.nan_lai import khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402

PHUT = 60_000
SO_NGAY = float(CO.lay("ngay", "20"))
LUI = float(CO.lay("lui", "0"))
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
CHIA_HOC, CHIA_CHON = 0.50, 0.75


def _sigma_dong(oh: dict, T: int, soNen: int) -> float | None:
    """Đóng-đến-đóng — phải trùng KHỚP bộ ước chung."""
    gs = [oh.get(T - i * PHUT) for i in range(soNen + 1)]
    if any(g is None or g[3] <= 0 for g in gs):
        return None
    c = [g[3] for g in gs][::-1]
    r = [math.log(c[i + 1] / c[i]) for i in range(len(c) - 1)]
    sd = statistics.pstdev(r)
    return (sd / math.sqrt(60.0)) if sd > 0 else None


_K_PARK = 1.0 / (4.0 * math.log(2.0))


def _sigma_bien_do(oh: dict, T: int, soNen: int) -> float | None:
    """Parkinson: σ²/phút = (ln(H/L))² / (4 ln 2), lấy trung bình rồi quy giây."""
    v = []
    for i in range(soNen):
        g = oh.get(T - i * PHUT)
        if g is None or g[2] <= 0 or g[1] <= 0:   # cao=[1] thấp=[2]
            return None
        v.append(_K_PARK * math.log(g[1] / g[2]) ** 2)
    if not v:
        return None
    s = math.sqrt(sum(v) / len(v)) / math.sqrt(60.0)
    return s if s > 0 else None


def _sigma_pha(oh: dict, T: int, soNen: int) -> float | None:
    a, b = _sigma_dong(oh, T, soNen), _sigma_bien_do(oh, T, soNen)
    if a is None or b is None:
        return None
    return math.sqrt(a * b)


#: `pha` chứ không phải `tron`: `ban_thu.uoc_tron` nghĩa là bộ ước
#: ĐƯƠNG NHIỆM, và hai chữ giống nhau ở hai chỗ là một chỗ để đọc nhầm.
BO_UOC = {"dong": _sigma_dong, "bienDo": _sigma_bien_do,
          "pha": _sigma_pha}


def _cap(oh: dict, mocs: list, ma: str, soNen: int, ham) -> list:
    ra = []
    for T in mocs:
        K, het = oh.get(T), oh.get(T + 5 * PHUT)
        if K is None or het is None or abs(het[3] - K[3]) < 1e-12:
            continue
        sig = ham(oh, T, soNen)
        if sig is None:
            continue
        thang = het[3] > K[3]
        for tau in LAT_CAT:
            t = T + int((300.0 - tau) * 1000.0)
            S = oh.get(t)
            if S is None or S[3] <= 0:
                continue
            gc = dinh_gia(ma, float(S[3]), float(K[3]), tau, sig)
            if gc is not None:
                ra.append((gc.pUp, thang, T))
    return ra


def _cham(cap_hoc: list, cap_chot: list):
    hc = HieuChinh(duong=GOC / "data" / "_tam-sigma-bien-do.json")
    hc.o = {}
    for p, t, _ in cap_hoc:
        hc.them(p, t)
    pn = khop(hc)
    sai = [((pn.nan(p) if pn.dung_duoc else p) - (1.0 if t else 0.0)) ** 2
           for p, t, _ in cap_chot]
    return sum(sai) / max(1, len(sai)), sai


def main() -> int:
    soNen = max(2, int(round(cua_so_sigma() / 60.0)))
    tong = int(SO_NGAY * 24 * 60 + soNen + 20)
    # Lùi mốc kết thúc để đo một quãng KHÔNG CHỒNG LẤN. Hai lượt đo mà
    # quãng này bao trùm quãng kia thì không phải hai bằng chứng — phần
    # chung chiếm phần lớn cả hai.
    het = (int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
           - int(LUI * 24 * 60) * PHUT)

    print()
    print("=" * 78)
    print("  σ TỪ BIÊN ĐỘ CAO–THẤP so với σ TỪ GIÁ ĐÓNG")
    print("=" * 78)
    print(f"  {SO_NGAY:g} ngày · lùi {LUI:g} ngày · cửa sổ {soNen} nến"
          f" · lấy {tong:,} nến/cặp…",
          flush=True)

    oh: dict[str, dict] = {}
    for t in thi_truong_doi_chieu_duoc():
        g = nen_ohlc(str(t["nen"]), het - tong * PHUT, tong)
        if len(g) >= 1200:
            oh[str(t["ma"])] = g
    if not oh:
        print("  không cặp nào đủ nến.\n")
        return 1
    print(f"  {len(oh)} chợ · " + " · ".join(f"{m} {len(g):,}"
                                             for m, g in oh.items()))

    # CHỨNG trước khi đo: mốc so phải TRÙNG KHỚP bộ ước chung.
    ma0 = next(iter(oh))
    T0 = next(T for T in sorted(oh[ma0]) if T % 300_000 == 0
              and all((T - i * PHUT) in oh[ma0] for i in range(soNen + 1)))
    quen_sigma()
    chuan = sigma_tai({k: v[3] for k, v in oh[ma0].items()}, T0,
                      cua_so_sigma(), ma0)
    minh = _sigma_dong(oh[ma0], T0, soNen)
    ok = chuan is not None and minh is not None and abs(chuan - minh) < 1e-15
    print(f"  mốc so `dong` trùng bộ ước chung: {ok}  "
          f"({chuan!r} vs {minh!r})")
    if not ok:
        print("  DỪNG: mốc so không phải bộ ước đang chạy — mọi so sánh")
        print("  phía sau sẽ nói về một cỗ máy khác.\n")
        return 2

    mocs = sorted({T for g in oh.values() for T in g if T % 300_000 == 0})
    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)
    mHoc, mChon, mChot = mocs[:a], mocs[a:b], mocs[b:]
    print(f"  HỌC {len(mHoc):,} · CHỌN {len(mChon):,} · CHỐT {len(mChot):,}"
          f" mốc  (tách theo THỜI GIAN)")
    print()

    ket = {}
    for ten, ham in BO_UOC.items():
        hoc, chon, chot = ([], [], [])
        for ma, g in oh.items():
            hoc.extend(_cap(g, mHoc, ma, soNen, ham))
            chon.extend(_cap(g, mChon, ma, soNen, ham))
            chot.extend(_cap(g, mChot, ma, soNen, ham))
        if min(len(hoc), len(chon), len(chot)) < 500:
            print(f"    {ten:8} chưa đủ cặp ({len(hoc)}/{len(chon)}/{len(chot)})")
            continue
        bChon, _ = _cham(hoc, chon)
        bChot, saiChot = _cham(hoc, chot)
        ket[ten] = {"chon": bChon, "chot": bChot, "sai": saiChot,
                    "moc": [x[-1] for x in chot], "n": len(hoc)}
        print(f"    {ten:8} HỌC {len(hoc):>7,}  CHỌN {bChon:.5f}  "
              f"CHỐT {bChot:.5f}")

    if "dong" not in ket:
        print("\n  không chấm được mốc so.\n")
        return 1
    goc = ket["dong"]
    print()
    print("  khoảng tin 95% trên CHỐT, so với `dong` (âm = tốt hơn):")
    for ten, r in ket.items():
        if ten == "dong":
            continue
        n = min(len(r["sai"]), len(goc["sai"]))
        hieu = [r["sai"][i] - goc["sai"][i] for i in range(n)]
        thap, cao, soK = khoang_tin_theo_khoi(hieu, goc["moc"][:n])
        dau = ("TỐT HƠN" if cao < 0 else "TỆ HƠN" if thap > 0 else "chứa 0")
        print(f"    {ten:8} [{thap:+.6f}, {cao:+.6f}]  ({soK} khối) → {dau}")
    print()
    print("  Đọc kỹ: đây là bộ ước KHÁC, không phải một hệ số nhân. Trước")
    print("  khi đổi bộ ước đang chạy, đo LẠI trên cửa sổ thời gian gấp")
    print("  đôi — một trục đẹp trên 20 ngày đã từng biến mất trên 40.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
