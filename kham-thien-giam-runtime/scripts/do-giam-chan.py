"""Quét cả trục `nanLai.heSoGiamChan` trên bốn chợ, có KHOẢNG TIN.

Vòng tự nâng cấp cho hai câu trả lời ngược nhau tuỳ mẫu:

    BTC, 10 ngày   → 0,7 giảm về 0,3   (nắn ÍT đi)
    bốn chợ, 20 ngày → 0,7 tăng lên 1,0 (nắn NHIỀU hơn, hết giảm chấn)

Một trong hai là nhiễu, hoặc cả hai. Điểm Brier trần trụi không phân
biệt được; khoảng tin thì có.

Dùng chính `cham` của `tu-nang-cap.py` — cùng thước mà cái cổng dùng,
không dựng lại bản sao.
"""
import importlib.util as iu
import sys
import time

sys.path.insert(0, ".")

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "ngay": "số ngày nến lấy về",
}, ten='do-giam-chan.py')
from kham.config import CONFIG
from kham.hoc_offline import khoang_tin_theo_khoi
from kham.ket_qua import thi_truong_doi_chieu_duoc

sp = iu.spec_from_file_location("_tnc", "scripts/tu-nang-cap.py")
m = iu.module_from_spec(sp)
sp.loader.exec_module(m)

NGAY = int(CO.lay("ngay", "20"))
PHUT = 60_000.0
het = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
soNen = NGAY * 24 * 60 + 20
chos = {}
for t in thi_truong_doi_chieu_duoc():
    chos[str(t["ma"])] = m.nen_1p(str(t["nen"]), het - soNen * PHUT, soNen)
mocs = sorted({T for tm in chos.values() for T in tm if T % 300_000 == 0})
a, b = int(len(mocs) * m.CHIA_HOC), int(len(mocs) * m.CHIA_CHON)
ba = (mocs[:a], mocs[a:b], mocs[b:])
cs0 = float(m.doc_tham_so("dinhGia.bienDongCuaSoGiay") or 300.0)
print()
print(f"  {len(chos)} chợ · {NGAY} ngày · HỌC {len(ba[0]):,} · "
      f"CHỌN {len(ba[1]):,} · CHỐT {len(ba[2]):,} khung")
print()

cu = (CONFIG.get("nanLai") or {}).get("heSoGiamChan")
ket = {}
try:
    for hs in (0.3, 0.5, 0.7, 0.85, 1.0):
        CONFIG.setdefault("nanLai", {})["heSoGiamChan"] = hs
        r = m.cham(chos, ba, cs0)
        ket[hs] = r
        print(f"    {hs:4.2f}   CHỌN {r['chon']:.5f}   CHỐT {r['chot']:.5f}"
              + ("   ← đương nhiệm" if abs(hs - 0.7) < 1e-9 else ""))
    print()
    goc = ket[0.7]
    for hs, r in ket.items():
        if abs(hs - 0.7) < 1e-9:
            continue
        n = min(len(r["_saiChot"]), len(goc["_saiChot"]))
        hieu = [r["_saiChot"][i] - goc["_saiChot"][i] for i in range(n)]
        thap, cao, soK = khoang_tin_theo_khoi(hieu, goc["_mocChot"][:n])
        dau = ("TỐT HƠN" if cao < 0 else "TỆ HƠN" if thap > 0 else "chứa 0")
        print(f"    {hs:4.2f} vs 0,70 trên CHỐT: [{thap:+.6f}, {cao:+.6f}]"
              f"  ({soK} khối) → {dau}")
finally:
    if cu is None:
        (CONFIG.get("nanLai") or {}).pop("heSoGiamChan", None)
    else:
        CONFIG["nanLai"]["heSoGiamChan"] = cu
print()
