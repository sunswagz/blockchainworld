"""TỰ NÂNG CẤP — lặp cho tới khi không nút nào còn cải thiện được nữa.

    python scripts/tu-nang-cap.py --thu          # xem sẽ vặn gì
    python scripts/tu-nang-cap.py                # vặn thật
    python scripts/tu-nang-cap.py --ngay=14 --vong=8

Mỗi VÒNG: quét MỌI nút mô hình, chấm từng ứng viên bằng độ chuẩn của dự
báo trên kết quả thật, chọn nút cho cải thiện LỚN NHẤT, xác nhận, vặn,
rồi lặp lại. Dừng khi không nút nào vượt nổi biên.

Đây là hạ xuống dốc theo toạ độ (coordinate descent) — thô, nhưng đúng
hình dạng bài toán: bốn nút, mỗi nút một dải hẹp có trần cứng, và hàm
mục tiêu đắt nhưng chạy được.

## Chỗ nguy hiểm nhất, và cái chốt cho nó

Lặp N vòng trên CÙNG một tập kiểm thì tập ấy thôi còn là ngoài mẫu: mỗi
vòng ta lại dùng nó để CHỌN, nên tới vòng thứ N nó đã bị nhìn N lần và
con số trên nó thành lạc quan có hệ thống. Đây là cái bẫy giết phần lớn
những vòng tự tối ưu, và nó không lộ ra ở đâu — mọi con số vẫn đẹp dần.

Nên chia BA tập, tách theo thời gian:

    HỌC     50%   khớp phép nắn
    CHỌN    25%   quét nút, chọn quán quân        ← bị nhìn nhiều lần
    CHỐT    25%   xác nhận quán quân               ← chỉ nhìn MỘT lần mỗi vòng,
                                                     và chỉ để GẬT hay LẮC

Tập CHỐT không bao giờ được dùng để chọn giữa các ứng viên — nó chỉ trả
lời một câu hỏi nhị phân về ứng viên đã chọn. Một lần dùng cho một câu
hỏi nhị phân thì rò rỉ ít hơn hẳn một lần dùng để xếp hạng 60 ứng viên.

## Và một chốt nữa: SO SÁNH BỘI

Quét 4 nút × chừng 15 mức là 60 phép so. Trong 60 phép so trên tiếng ồn
thuần tuý, cái tốt nhất luôn trông khá hơn đáng kể. Nên biên vượt ở tập
CHỌN được siết theo số ứng viên đã thử, và tập CHỐT phải gật độc lập.
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
from kham.chan_doan import NUT_THEO_DUONG, doc_tham_so  # noqa: E402
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.ket_qua import (  # noqa: E402
    thi_truong_doi_chieu_duoc)
from kham.nan_lai import khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402
from kham.tien_hoa import _dat_tham_so, ghi_config  # noqa: E402

PHUT = 60_000.0
LAT_CAT = (240.0, 180.0, 120.0, 60.0)

#: Nút mà bàn thử Brier nhìn thấy. NHẬP từ `kham.hoc_offline` —
#: ba bản sao của cùng một danh sách là ba chỗ để chúng lệch nhau,
#: và ở đây lệch nghĩa là hai công cụ vặn hai bộ nút khác nhau.
from kham.hoc_offline import NUT_MO_HINH  # noqa: E402,F401

CHIA_HOC, CHIA_CHON = 0.50, 0.75
BIEN_CHON = 0.995          # siết thêm theo số ứng viên, xem `_bien`
BIEN_CHOT = 0.999          # tập CHỐT chỉ cần gật, không cần vượt xa


CO = tham_so.doc({
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "số ngày băng/nến lấy về",
    "thu": tham_so.BAT,
    "vong": "số vòng tối đa",
    "gop": tham_so.BAT,
}, ten='tu-nang-cap.py')


THU = CO.co("thu")
SO_NGAY = int(CO.lay("ngay", "10"))
TOI_DA_VONG = int(CO.lay("vong", "6"))
MA = CO.lay("ma", "BTC_5M")
GOP = CO.co("gop")
SO = DATA_DIR / "tu-nang-cap.jsonl"


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
from kham.hoc_offline import quen_sigma  # noqa: E402
from kham.hoc_offline import sigma_tai as _sigma_chung  # noqa: E402


def sigma_tai(theoMoc, T, cuaSoGiay):
    """σ mỗi giây tại mốc T. Gọi thẳng bộ ước chung."""
    return _sigma_chung(theoMoc, int(T), float(cuaSoGiay))
def cap_du_doan(chos: dict, mocs: list, cuaSoGiay: float,
                keoMoc: bool = False) -> list:
    """(p, thắng[, mốc khung]) theo THỨ TỰ THỜI GIAN, gộp mọi chợ.

    `chos` là `{mã: {mốc ms: giá}}`. Một chợ chỉ là trường hợp riêng
    `{MA: theoMoc}` — MỘT đường mã cho cả hai, vì hai đường thì sớm
    muộn lệch nhau và chỗ lệch sẽ nằm trong phép chấm.

    `keoMoc` để bootstrap gộp được theo KHUNG: bốn lát cắt của một
    khung chia chung MỘT kết quả, nên chúng không phải bốn quan sát
    độc lập.

    ## Mốc kéo theo là mốc THỜI GIAN, không phải (chợ, thời gian)

    Bốn coin tương quan gần 1 — `kho_doi` có sẵn ma trận nói thế, và
    cả cổng 7b dựng lên vì chuyện đó. Nên BTC, ETH, SOL, XRP tại cùng
    một mốc KHÔNG phải bốn bằng chứng độc lập; chúng gần như là một
    quan sát nhìn từ bốn phía.

    Kéo theo `T` trần trụi khiến bootstrap gom cả bốn chợ vào MỘT khối,
    và khoảng tin thu được trung thực. Kéo theo `(ma, T)` thì mẫu trông
    to gấp bốn, khoảng tin hẹp lại quãng một nửa, và cổng CHỐT sẽ gật
    cho tiếng ồn. Gộp chợ là để có thêm THÔNG TIN, không phải để có
    thêm CON SỐ.
    """
    ra = []
    for T in mocs:
        for ma, theoMoc in chos.items():
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
                gc = dinh_gia(ma, float(S), float(K), tau, sig)
                if gc is not None:
                    ra.append((gc.pUp, thang, T) if keoMoc
                              else (gc.pUp, thang))
    return ra


def _brier(cap) -> float:
    return sum((p - (1.0 if t else 0.0)) ** 2 for p, t, *_ in cap) / max(1, len(cap))


def cham(chos: dict, ba: tuple, cuaSoGiay: float) -> dict | None:
    """Khớp nắn trên HỌC, chấm trên CHỌN và CHỐT. Ba tập tách theo thời gian."""
    hoc, chon = (cap_du_doan(chos, m, cuaSoGiay) for m in ba[:2])
    chot = cap_du_doan(chos, ba[2], cuaSoGiay, keoMoc=True)
    if len(hoc) < 1500 or len(chon) < 500 or len(chot) < 500:
        return None
    hc = HieuChinh(duong=DATA_DIR / "_tam-tu-nang.json")
    hc.o = {}
    for p, t in hoc:
        hc.them(p, t)
    pn = khop(hc)

    def nan(cap):
        return [(pn.nan(p) if pn.dung_duoc else p, t) for p, t, *_ in cap]

    return {"nHoc": len(hoc), "nChon": len(chon), "nChot": len(chot),
            "chon": _brier(nan(chon)), "chot": _brier(nan(chot)),
            "chonTho": _brier(chon), "chotTho": _brier(chot),
            # Giữ lại dãy sai số TỪNG CẶP của tập CHỐT để còn dựng được
            # khoảng tin có cặp. Không có nó thì "khá hơn 0,00001" và
            # "khá hơn 0,01" đọc y hệt nhau.
            "_saiChot": [(q - (1.0 if t else 0.0)) ** 2 for q, t in nan(chot)],
            "_mocChot": [x[-1] for x in chot]}


def _bien(soUngVien: int) -> float:
    """Biên vượt SIẾT theo số ứng viên đã thử.

    Quét 60 ứng viên trên tiếng ồn thuần tuý thì cái tốt nhất vẫn trông
    khá hơn đáng kể — đó là so sánh bội, không phải khám phá. Siết biên
    theo `log` số ứng viên là một cách thô nhưng đúng hướng để trả lại
    phần lợi thế mà chính việc quét nhiều đã tặng không.
    """
    return 1.0 - (1.0 - BIEN_CHON) / max(1.0, math.log(max(2, soUngVien)))


def mot_vong(chos: dict, ba: tuple, vong: int) -> dict | None:
    hienTai = {d: float(doc_tham_so(d) or 0.0) for d in NUT_MO_HINH}
    cs0 = hienTai["dinhGia.bienDongCuaSoGiay"]
    goc = cham(chos, ba, cs0)
    if goc is None:
        print("    chưa đủ cặp để chấm.")
        return None

    print(f"    đương nhiệm: Brier CHỌN {goc['chon']:.5f} · "
          f"CHỐT {goc['chot']:.5f}")
    ungVien = []
    for duong in NUT_MO_HINH:
        n = NUT_THEO_DUONG.get(duong)
        if n is None:
            continue
        v = float(n.thap)
        while v <= n.cao + 1e-9:
            if abs(v - hienTai[duong]) > 1e-12:
                ungVien.append((duong, round(v, 6)))
            v += n.buoc

    tot = None
    for duong, v in ungVien:
        if duong == "dinhGia.bienDongCuaSoGiay":
            r = cham(chos, ba, v)
        else:
            cu = _dat_tham_so(duong, v)
            try:
                r = cham(chos, ba, cs0)
            finally:
                _dat_tham_so(duong, cu)
        if r is None:
            continue
        if tot is None or r["chon"] < tot[2]["chon"]:
            tot = (duong, v, r)

    if tot is None:
        print("    không ứng viên nào chấm được.")
        return None

    duong, v, r = tot
    bien = _bien(len(ungVien))
    print(f"    quán quân: {duong} {hienTai[duong]:g} → {v:g}")
    print(f"      CHỌN {goc['chon']:.5f} → {r['chon']:.5f}  "
          f"(cần ≤ {goc['chon']*bien:.5f}, biên {bien:.4f} sau "
          f"{len(ungVien)} ứng viên)")
    if r["chon"] >= goc["chon"] * bien:
        print("      TRẢ LẠI: chưa vượt biên ở tập CHỌN.")
        # NÓI LUÔN tập CHỐT nói gì, dù ứng viên đã bị loại.
        #
        # Bản trước chỉ in CHỐT khi ứng viên ĐƯỢC NHẬN. Nên ca thường gặp
        # nhất — suýt qua ở CHỌN — không bao giờ lộ ra CHỐT nghĩ sao, và
        # người đọc thấy cùng một nút suýt thắng nhiều lượt liền thì rất
        # dễ kết luận "nó gần đúng rồi, nới biên đi".
        #
        # Đo trên `nanLai.heSoGiamChan`, nút liên tục là quán quân:
        #
        #     hệ số   CHỌN      CHỐT
        #      0,30   0.15578   0.15861
        #      0,50   0.15586   0.15857
        #      0,70   0.15601   0.15861   ← đương nhiệm
        #      1,00   0.15638   0.15879
        #
        # CHỌN cải thiện ĐƠN ĐIỆU, CHỐT PHẲNG LÌ, mọi khoảng tin chứa 0.
        # Đó là dấu vân tay của khớp quá trên tập xếp hạng — và là lý do
        # tồn tại của tập CHỐT. Chuỗi "suýt thắng" KHÔNG phải bằng chứng
        # tích luỹ; nó là cùng một tiếng ồn nhìn từ nhiều lượt.
        dau = "khá hơn" if r["chot"] < goc["chot"] else "TỆ HƠN"
        print(f"      (CHỐT {goc['chot']:.5f} → {r['chot']:.5f} — {dau}. "
              "In ra ngay cả khi đã loại:")
        print("       một nút suýt thắng nhiều lượt liền mà CHỐT không đi")
        print("       cùng chiều thì đó là tiếng ồn, không phải bằng chứng)")
        return {"nhan": None, "duong": duong, "den": v, "goc": goc, "moi": r,
                "soUngVien": len(ungVien), "bien": bien, "lyDo": "thua ở CHỌN"}

    # Tập CHỐT chỉ trả lời GẬT hay LẮC về đúng ứng viên này. Không dùng
    # nó để xếp hạng — dùng để xếp hạng là biến nó thành tập chọn thứ hai.
    print(f"      CHỐT {goc['chot']:.5f} → {r['chot']:.5f}  "
          f"(cần ≤ {goc['chot']*BIEN_CHOT:.5f})")
    if r["chot"] >= goc["chot"] * BIEN_CHOT:
        print("      TRẢ LẠI: tập CHỐT không gật. Đây đúng là chỗ cái bẫy")
        print("               so-sánh-bội hay lộ ra.")
        return {"nhan": None, "duong": duong, "den": v, "goc": goc, "moi": r,
                "soUngVien": len(ungVien), "bien": bien, "lyDo": "CHỐT lắc"}

    # ĐỘ MỎNG CỦA BẰNG CHỨNG, in ngay tại chỗ.
    #
    # Ngưỡng đặt trước và không được nới sau khi thấy kết quả. Nhưng một
    # ứng viên qua ngưỡng bằng 0,00001 và một ứng viên qua bằng 0,01 thì
    # đọc y hệt nhau nếu chỉ in chữ "NHẬN" — mà chúng là hai chuyện khác
    # hẳn. Khoảng tin có cặp trên tập CHỐT nói ra chỗ khác nhau ấy.
    from kham.hoc_offline import khoang_tin_theo_khoi
    a, b2 = goc.get("_saiChot") or [], r.get("_saiChot") or []
    if a and b2 and len(a) == len(b2):
        hieu = [x - y for x, y in zip(a, b2)]     # dương = ứng viên khá hơn
        n_ = len(hieu)
        # Lấy lại theo KHUNG, không theo cặp: bốn lát cắt của một khung
        # chia chung một kết quả, nên bootstrap theo cặp là giả vờ có
        # gấp bốn số quan sát thực. Đo được: khoảng tin HẸP ĐI 2,18 lần,
        # tức cổng dễ nhận một thay đổi chỉ là tiếng ồn.
        thap, cao, soK = khoang_tin_theo_khoi(hieu, goc.get("_mocChot"))
        print(f"      chênh Brier CHỐT {sum(hieu)/n_:+.6f} · "
              f"khoảng tin 95% [{thap:+.6f}, {cao:+.6f}] ({soK} khung)")
        if thap <= 0 <= cao:
            print("      ⚠ khoảng tin CHỨA 0: qua ngưỡng nhưng nằm trong")
            print("        tiếng ồn. Nhận theo đúng luật đã đặt trước, nhưng")
            print("        đừng đọc đây là một cải thiện chắc chắn.")

    print(f"      NHẬN.")
    return {"nhan": {"nut": duong, "tu": hienTai[duong], "den": v},
            "duong": duong, "den": v, "goc": goc, "moi": r,
            "soUngVien": len(ungVien), "bien": bien, "lyDo": "cả hai gật"}


def _cho_can_lay() -> list:
    """(mã, cặp nến) sẽ chấm. `--gop` thì lấy mọi chợ LÊN/XUỐNG đang theo."""
    if GOP:
        return [(str(t.get("ma")), str(t.get("nen")))
                for t in thi_truong_doi_chieu_duoc()]
    c = next((t.get("nen") for t in CONFIG["thiTruong"]
              if t.get("ma") == MA), None)
    return [(MA, str(c))] if c else []


def main() -> int:
    dsCho = _cho_can_lay()
    if not dsCho:
        print(chr(10) + "  Không có market `" + MA + "`." + chr(10))
        return 1

    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    soNen = SO_NGAY * 24 * 60 + 20
    print()
    print("=" * 78)
    print("  TỰ NÂNG CẤP — lặp tới khi không nút nào cải thiện được nữa")
    print("=" * 78)
    print("  " + ", ".join(m for m, _ in dsCho) + " · " + str(SO_NGAY)
          + " ngày · tối đa " + str(TOI_DA_VONG) + " vòng")
    print("  lấy " + format(soNen, ",") + " nến mỗi chợ…", flush=True)
    chos: dict = {}
    for maX, capX in dsCho:
        tm = nen_1p(capX, hetMs - soNen * PHUT, soNen)
        if len(tm) < 1200:
            print("    " + maX + ": chỉ lấy được " + str(len(tm))
                  + " nến — BỎ QUA")
            continue
        chos[maX] = tm
    if not chos:
        print("  không chợ nào đủ nến. Dừng." + chr(10))
        return 1

    # Lưới mốc lấy HỢP của mọi chợ: một chợ thiếu nến ở mốc T thì
    # `cap_du_doan` tự bỏ qua chợ ấy ở mốc ấy, chứ không được làm cả
    # mốc biến mất với ba chợ còn lại.
    mocs = sorted({T for tm in chos.values() for T in tm
                   if T % 300_000 == 0})
    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)
    ba = (mocs[:a], mocs[a:b], mocs[b:])
    print("  " + str(len(chos)) + " chợ · "
          + " · ".join(m + " " + format(len(tm), ",") + " nến"
                       for m, tm in chos.items()))
    print(f"  HỌC {len(ba[0]):,} khung · CHỌN {len(ba[1]):,} · CHỐT {len(ba[2]):,}"
          "   (tách theo THỜI GIAN)")

    daNhan = []
    for vong in range(1, TOI_DA_VONG + 1):
        print()
        print(f"  ── VÒNG {vong} " + "─" * 58)
        kq = mot_vong(chos, ba, vong)
        if kq is None or not kq.get("nhan"):
            print("    dừng: không nút nào còn cải thiện được.")
            break
        nhan = kq["nhan"]
        daNhan.append(nhan)
        if THU:
            _dat_tham_so(nhan["nut"], nhan["den"])   # chỉ trong bộ nhớ
        else:
            ghi_config(nhan["nut"], nhan["den"])
        ban = {"luc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "vong": vong,
               "ma": ("+".join(chos) if GOP else MA),
               "soNgay": SO_NGAY,
               "nguonMau": "binance-that", "thu": THU, **kq}
        if not THU:
            SO.parent.mkdir(parents=True, exist_ok=True)
            with SO.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ban, ensure_ascii=False) + "\n")

    print()
    print("=" * 78)
    if not daNhan:
        print("  KHÔNG vặn gì. Cấu hình hiện tại đã là tốt nhất trong dải cho")
        print("  phép, theo phép đo này. Đứng yên là một kết quả hợp lệ.")
    else:
        print(f"  ĐÃ VẶN {len(daNhan)} nút:")
        for x in daNhan:
            print(f"    {x['nut']}: {x['tu']:g} → {x['den']:g}")
        if THU:
            print("  (--thu: chỉ trong bộ nhớ, KHÔNG ghi config)")
    print()
    print("  Đo bằng độ chuẩn của DỰ BÁO trên kết quả THẬT — không giá chợ,")
    print("  không giả định. Nó KHÔNG nói bot kiếm được bao nhiêu.")
    print("=" * 78)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
