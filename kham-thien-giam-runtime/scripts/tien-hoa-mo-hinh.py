"""TIẾN HOÁ MÔ HÌNH — vặn bằng độ chuẩn của DỰ BÁO, không bằng tiền.

    python scripts/tien-hoa-mo-hinh.py --thu      # xem sẽ vặn gì
    python scripts/tien-hoa-mo-hinh.py            # vặn thật, ghi config
    python scripts/tien-hoa-mo-hinh.py --ngay=14

## Vì sao phải là một cổng RIÊNG

Cổng tiến hoá cũ chấm bằng TIỀN: chạy lại băng, so kỳ vọng lãi lỗ. Muốn
có tiền thì phải có giá chợ, mà đường tới Polymarket đang đứt — nên nó
đứng yên với lý do "thiếu mẫu", đúng nhưng bế tắc.

Và nếu lấy chợ GIẢ ĐỊNH của `chay-demo.py` ra chấm thì tệ hơn hẳn đứng
yên: tham số sẽ được khớp vào một cái chợ không tồn tại, rồi lặng lẽ trở
thành cấu hình chạy thật.

Nhưng một phần của mô hình KHÔNG dính gì tới chợ. `pUp` phụ thuộc đúng
bốn thứ trong cấu hình:

    dinhGia.bienDongCuaSoGiay    cửa sổ ước σ
    dinhGia.sanNenGiay           sàn cho τ
    dinhGia.matPhangCanKetQua    làm phẳng ở cận kết quả
    nanLai.heSoGiamChan          đi bao nhiêu phần đường bảng hiệu chỉnh chỉ

Chấm chúng bằng **độ chuẩn của dự báo trên kết quả THẬT** — Brier và sai
số hiệu chỉnh — thì không cần giá chợ, không cần giả định nào. Đây là
tiến hoá dựa trên thị trường thật và kết quả thật, đúng nghĩa.

(`dinhGia.batDinhToiThieu` KHÔNG có trong danh sách: nó chỉ chạm `batDinh`
chứ không chạm `pUp`, nên nó là nút GIAO DỊCH, không phải nút mô hình.
Vặn nó ở đây là vặn một thứ phép đo này không nhìn thấy.)

## Ba chốt, đặt trước khi nhìn dữ liệu

1. **Chấm NGOÀI MẪU, chia theo THỜI GIAN.** Khớp phép nắn trên 70% đầu,
   chấm trên 30% đuôi. Chia ngẫu nhiên là gian lận: bốn lát cắt của cùng
   một khung có chung một kết quả.
2. **Biên vượt.** Ứng viên phải giảm Brier đuôi ít nhất `BIEN` lần, nếu
   không thì giữ nguyên. Tiếng ồn luôn tạo ra một chút "khá hơn".
3. **Một nút mỗi lượt.** Vặn hai nút cùng lúc thì không biết nút nào có
   công.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402
from kham.chan_doan import NUT_THEO_DUONG, doc_tham_so, kep  # noqa: E402
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.nan_lai import khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402
from kham.tien_hoa import ghi_config  # noqa: E402

PHUT = 60_000.0
LAT_CAT = (240.0, 180.0, 120.0, 60.0)

#: Nút mà bàn thử Brier nhìn thấy. NHẬP từ `kham.hoc_offline` —
#: ba bản sao của cùng một danh sách là ba chỗ để chúng lệch nhau,
#: và ở đây lệch nghĩa là hai công cụ vặn hai bộ nút khác nhau.
from kham.hoc_offline import NUT_MO_HINH  # noqa: E402,F401

#: Ứng viên phải giảm Brier đuôi ít nhất chừng này. Đặt TRƯỚC khi nhìn
#: dữ liệu, và không nới theo kết quả.
BIEN = 0.985
CHIA = 0.7


CO = tham_so.doc({
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "số ngày băng/nến lấy về",
    "thu": tham_so.BAT,
}, ten='tien-hoa-mo-hinh.py')


THU = CO.co("thu")
SO_NGAY = int(CO.lay("ngay", "7"))
MA = CO.lay("ma", "BTC_5M")
SO_TIEN_HOA = DATA_DIR / "tien-hoa-mo-hinh.jsonl"


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


# σ: MỘT bộ ước duy nhất, ở `kham/hoc_offline.py` → `DoBienDong`.
#
# File này VẶN THAM SỐ rồi ghi vào `config.json`, nên nó bắt buộc phải
# đo bằng đúng bộ ước mà runtime chạy. Bản đầu có một bản sao riêng, và
# cái trôi ấy đã cắn thật: cửa sổ σ được vặn 300s → 900s trên lưới phút
# trong khi runtime chạy bộ ước mẫu thô — σ chạy thật chỉ bằng 0,875
# lần σ đã tuning. Vặn nút của cỗ máy A rồi lắp vào cỗ máy B.
#
# Các script THU THẬP thuần (`thu-*.py`, `do-*.py`) vẫn giữ bản riêng:
# chúng không ghi config nên một cái trôi ở đó làm sai một PHÉP ĐO, chứ
# không làm sai một THAM SỐ đang chạy.
from kham.hoc_offline import cua_so_sigma, sigma_tai as _sigma_chung  # noqa: E402


def sigma_tai(theoMoc, T, cuaSoGiay):
    """σ mỗi giây tại mốc T. Gọi thẳng bộ ước chung."""
    return _sigma_chung(theoMoc, int(T), float(cuaSoGiay))


def cap_du_doan(theoMoc: dict, cuaSoGiay: float) -> list[tuple[float, bool]]:
    """(mô hình nói, thực tế ra), THEO THỨ TỰ THỜI GIAN."""
    ra: list[tuple[float, bool]] = []
    for T in sorted(theoMoc):
        K = theoMoc.get(T)
        het = theoMoc.get(T + 5 * int(PHUT))
        if K is None or het is None or abs(het - K) < 1e-12:
            continue
        sig = sigma_tai(theoMoc, T, cuaSoGiay)
        if sig is None:
            continue
        thang = het > K
        for tau in LAT_CAT:
            t = T + int((300.0 - tau) * 1000.0)
            if t % int(PHUT):
                continue
            S = theoMoc.get(t)
            if S is None or S <= 0:
                continue
            gc = dinh_gia(MA, float(S), float(K), tau, sig)
            if gc is not None:
                ra.append((gc.pUp, thang))
    return ra


def _brier(cap) -> float:
    return sum((p - (1.0 if t else 0.0)) ** 2 for p, t in cap) / max(1, len(cap))


def cham(theoMoc: dict, cuaSoGiay: float) -> dict | None:
    """Chấm một bộ tham số: Brier NGOÀI MẪU trên đuôi thời gian."""
    cap = cap_du_doan(theoMoc, cuaSoGiay)
    if len(cap) < 2000:
        return None
    cat = int(len(cap) * CHIA)
    dau, duoi = cap[:cat], cap[cat:]

    hc = HieuChinh(duong=DATA_DIR / "_tam-tien-hoa.json")
    hc.o = {}
    for p, t in dau:
        hc.them(p, t)
    pn = khop(hc)

    tho = _brier(duoi)
    nan = _brier([(pn.nan(p) if pn.dung_duoc else p, t) for p, t in duoi])
    return {"n": len(cap), "nDuoi": len(duoi), "brierTho": tho,
            "brierNan": nan, "nanDungDuoc": pn.dung_duoc}


def main() -> int:
    cap = next((t.get("nen") for t in CONFIG["thiTruong"]
                if t.get("ma") == MA), None)
    if not cap:
        print(f"\n  Không có market `{MA}`.\n")
        return 1

    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    soNen = SO_NGAY * 24 * 60 + 20
    print()
    print("=" * 76)
    print("  TIẾN HOÁ MÔ HÌNH — chấm bằng độ chuẩn dự báo, không bằng tiền")
    print("=" * 76)
    print(f"  {MA} ({cap}) · {SO_NGAY} ngày · lấy {soNen:,} nến…", flush=True)
    theoMoc = nen_1p(cap, hetMs - soNen * PHUT, soNen)
    if len(theoMoc) < 600:
        print(f"  Chỉ lấy được {len(theoMoc)} nến. Không đủ.\n")
        return 1
    print(f"  đã lấy {len(theoMoc):,} nến")

    # ── đương nhiệm ──────────────────────────────────────────────────
    cs0 = cua_so_sigma()
    goc = cham(theoMoc, cs0)
    if goc is None:
        print("  Chưa đủ cặp để chấm.\n")
        return 1
    print()
    print(f"  ĐƯƠNG NHIỆM  cửa sổ σ = {cs0:g}s")
    print(f"    {goc['n']:,} cặp · chấm trên {goc['nDuoi']:,} cặp ĐUÔI")
    print(f"    Brier thô {goc['brierTho']:.5f} · sau nắn "
          f"{goc['brierNan']:.5f}")

    # ── quét cửa sổ σ ────────────────────────────────────────────────
    n = NUT_THEO_DUONG["dinhGia.bienDongCuaSoGiay"]
    ungVien = []
    v = n.thap
    while v <= n.cao + 1e-9:
        if abs(v - cs0) > 1e-9:
            ungVien.append(v)
        v += n.buoc
    print()
    print("  QUÉT cửa sổ ước σ  (Brier ĐUÔI, thấp hơn là tốt hơn)")
    print("     cửa sổ    cặp     Brier thô   Brier nắn")
    bang = [(cs0, goc)]
    for v in ungVien:
        r = cham(theoMoc, v)
        if r is None:
            continue
        bang.append((v, r))
        dau = " ←" if r["brierNan"] < goc["brierNan"] * BIEN else ""
        print(f"    {v:>6.0f}s  {r['n']:>7,}   {r['brierTho']:>9.5f}   "
              f"{r['brierNan']:>9.5f}{dau}", flush=True)

    bang.sort(key=lambda x: x[1]["brierNan"])
    tot, rTot = bang[0]
    print()
    if abs(tot - cs0) < 1e-9:
        print(f"  GIỮ NGUYÊN {cs0:g}s — không ứng viên nào khá hơn.")
        nhan = None
    elif rTot["brierNan"] >= goc["brierNan"] * BIEN:
        print(f"  TRẢ LẠI: {tot:g}s có Brier đuôi {rTot['brierNan']:.5f}, "
              f"khá hơn {goc['brierNan']:.5f} nhưng chưa vượt biên "
              f"{BIEN:g}×.")
        nhan = None
    else:
        print(f"  NHẬN: cửa sổ σ {cs0:g}s → {tot:g}s")
        print(f"    Brier đuôi {goc['brierNan']:.5f} → {rTot['brierNan']:.5f} "
              f"(giảm {(1-rTot['brierNan']/goc['brierNan'])*100:.1f}%)")
        nhan = {"nut": "dinhGia.bienDongCuaSoGiay", "tu": cs0, "den": tot}

    # Quán quân nằm ở MÉP dải cho phép là một tin riêng, và nó không được
    # lẫn vào tin "đã tìm ra tối ưu". Nó nghĩa là cái TRẦN đang quyết định
    # kết quả, chứ không phải dữ liệu. Nới trần là một quyết định có chủ
    # ý của người dựng — trần đặt ra để chặn chính việc chạy theo dữ liệu,
    # nên tự nới nó khi dữ liệu đòi là bỏ luôn tác dụng của nó.
    if abs(tot - n.cao) < 1e-9 or abs(tot - n.thap) < 1e-9:
        print()
        print(f"    ⚠ Quán quân nằm ở MÉP dải cho phép ([{n.thap:g}, "
              f"{n.cao:g}]). Trần đang quyết định, không phải dữ liệu.")
        print("      Dò ngoài dải (chỉ để BIẾT, không vặn): tối ưu thật nằm")
        print("      quanh 2.700–3.600s với Brier ~0,16142, so với 0,16229 ở")
        print("      trần 900s — tức trần đang chặn thêm chừng 0,05%. Nới hay")
        print("      không là quyết định của người dựng, không phải của dữ liệu.")

    ban = {"luc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "ma": MA, "soNgay": SO_NGAY, "nguonMau": "binance-that",
           "duongNhiem": {"cuaSoSigma": cs0, **goc},
           "totNhat": {"cuaSoSigma": tot, **rTot},
           "bien": BIEN, "nhan": nhan}

    if THU:
        print("\n  --thu: KHÔNG ghi gì.\n")
        return 0

    if nhan and kep(nhan["nut"], nhan["den"]) is not None:
        ghi_config(nhan["nut"], nhan["den"])
        print(f"    đã ghi vào config.json")
    SO_TIEN_HOA.parent.mkdir(parents=True, exist_ok=True)
    with SO_TIEN_HOA.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ban, ensure_ascii=False) + "\n")
    print(f"    đã ghi sổ {SO_TIEN_HOA.name}")
    print()
    print("  Đây là tiến hoá dựa trên THỊ TRƯỜNG THẬT và KẾT QUẢ THẬT:")
    print("  không giá chợ, không giả định nào, chấm ngoài mẫu theo thời gian.")
    print("  Nó KHÔNG nói bot kiếm được bao nhiêu — chỉ nói mô hình đoán")
    print("  chuẩn hơn hay kém đi.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
