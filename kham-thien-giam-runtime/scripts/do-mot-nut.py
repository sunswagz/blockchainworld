"""Quét CẢ TRỤC của MỘT nút, bốn chợ, có KHOẢNG TIN.

    python scripts/do-mot-nut.py --nut=nanLai.heSoGiamChan
    python scripts/do-mot-nut.py --nut=ruiRo.kellyPhan --ngay=20
    python scripts/do-mot-nut.py --nut=... --gia-tri=0.3,0.5,0.7

## Vì sao cần một công cụ RIÊNG bên cạnh `tu-nang-cap.py`

`tu-nang-cap.py` quét ~51 ứng viên rồi in ra quán quân. Quán quân của
một lượt quét là cực trị của 51 biến ngẫu nhiên: nó gần như luôn dương,
gần như luôn nhỏ, và **dấu của nó không đáng tin** khi mẫu hẹp. Cái
cổng biết thế (nó siết biên theo `log` số ứng viên), nhưng người đọc
bảng thì nhớ tên nút và nhớ chiều, rồi mang cái chiều ấy đi.

Đã cắn: nhiều lượt liền quán quân là `nanLai.heSoGiamChan 0,7 → 0,3`.
Quét cả trục có khoảng tin thì 0,3 không những là nhiễu — nó **TỆ HƠN
có ý nghĩa**, và chiều đúng ngược lại (0,85/1,00 tốt hơn).

Hai công cụ không mâu thuẫn. Chúng trả lời hai câu khác nhau:

    tu-nang-cap.py   "trong 51 nút, có nút nào đáng vặn không?"
    do-mot-nut.py    "nút NÀY nên đặt ở đâu?"

Câu sau kiểm ĐÚNG MỘT giả thuyết định trước, nên không phải trả giá
so-sánh-bội, nên nó nhìn thấy thứ cái cổng phải bỏ qua.

## Cách đọc bảng ra

Cột `CHỌN` và `CHỐT` là Brier — càng NHỎ càng tốt. Khoảng tin dựng trên
hiệu số sai lệch từng cặp của tập CHỐT so với trị đương nhiệm, bootstrap
chia khối theo **KHUNG**: bốn lát cắt τ của một khung chia chung một kết
quả, và bốn chợ tại cùng một mốc tương quan gần 1 — chúng không phải
bốn bằng chứng độc lập.

    cả khoảng < 0   TỐT HƠN có ý nghĩa
    cả khoảng > 0   TỆ HƠN có ý nghĩa
    chứa 0          không phân biệt được — ĐỪNG vặn theo nó

Hình dạng cả trục nói nhiều hơn thắng thua từng cặp: đơn điệu là thứ
khó giả, còn một đỉnh nhọn giữa trục thường là nhiễu.

## Nó KHÔNG nói gì

Không nói tiền. Thước ở đây là độ chuẩn của DỰ BÁO trên kết quả THẬT,
không có giá chợ trong đó. Một nút chỉnh dự báo chuẩn hơn vẫn có thể
không đổi một đồng lãi lỗ nào, vì còn phải qua sổ lệnh, phí, và trượt
giá. Câu tiền nằm ở `chay-phat-lai.py`.
"""
from __future__ import annotations

import importlib.util as iu
import sys
import time

sys.path.insert(0, ".")

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "nut": "đường nút, ví dụ nanLai.heSoGiamChan",
    "ngay": "số ngày nến lấy về",
    "gia-tri": "danh sách trị cần thử, cách nhau bởi dấu phẩy",
}, ten='do-mot-nut.py')

from kham.chan_doan import NUT_THEO_DUONG, doc_tham_so  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.hoc_offline import khoang_tin_theo_khoi  # noqa: E402
from kham.ket_qua import thi_truong_doi_chieu_duoc  # noqa: E402

PHUT = 60_000.0
NGAY = int(CO.lay("ngay", "20"))
DUONG = CO.lay("nut", "")


def _dat(duong: str, gt: float) -> None:
    """Đặt một trị vào CONFIG trong bộ nhớ, theo đường có dấu chấm."""
    k = duong.split(".")
    d = CONFIG
    for x in k[:-1]:
        d = d.setdefault(x, {})
    d[k[-1]] = gt


def _truc(nut) -> list[float]:
    """Trị cần thử: khai tay, hoặc cả trục theo dải và bước của nút."""
    tay = CO.lay("gia-tri", "")
    if tay:
        return [float(x) for x in tay.split(",") if x.strip()]
    ra = []
    v = float(nut.thap)
    while v <= float(nut.cao) + 1e-9:
        ra.append(round(v, 6))
        v += float(nut.buoc)
    # Trục quá dày thì mỗi lượt chấm là một lượt quét băng — giữ ~9 mốc,
    # đủ thấy HÌNH DẠNG mà không phải chờ nửa tiếng.
    if len(ra) > 9:
        b = max(1, len(ra) // 9)
        ra = ra[::b]
        if abs(ra[-1] - float(nut.cao)) > 1e-9:
            ra.append(round(float(nut.cao), 6))
    return ra


def main() -> int:
    nut = NUT_THEO_DUONG.get(DUONG)
    if nut is None:
        print()
        print("  Không có nút `" + str(DUONG) + "`. Các nút có thật:")
        for d in sorted(NUT_THEO_DUONG):
            print("    " + d)
        print()
        return 1

    # Nạp `tu-nang-cap.py` để dùng CHÍNH phép chấm của nó, không dựng
    # bản sao. Nhưng lúc nạp, nó chạy `tham_so.doc` trên `sys.argv` thật
    # và thoát vì thấy cờ `--nut` lạ. Che argv trong đúng lúc nạp.
    sp = iu.spec_from_file_location("_tnc", "scripts/tu-nang-cap.py")
    m = iu.module_from_spec(sp)
    cuArgv = sys.argv
    sys.argv = ["tu-nang-cap.py"]
    try:
        sp.loader.exec_module(m)
    finally:
        sys.argv = cuArgv

    # TỪ CHỐI nút không chạm `pUp`.
    #
    # Thước ở đây là Brier — độ chuẩn của DỰ BÁO. Nút cỡ lệnh, nút trần
    # vốn, nút ngưỡng vào lệnh đều không đổi một con số dự báo nào, nên
    # quét chúng bằng thước này cho ra một đường PHẲNG. Đường phẳng ấy
    # không nói "nút không quan trọng"; nó nói "hỏi sai thước". Mà đường
    # phẳng thì trông y hệt một kết luận, nên nó nguy hiểm hơn một lỗi.
    #
    # `NUT_MO_HINH` là danh sách nút đi vào `pUp`, do chính
    # `tu-nang-cap.py` khai. Đọc từ đó chứ không chép lại.
    if DUONG not in m.NUT_MO_HINH:
        print()
        if DUONG == "dinhGia.sanNenGiay":
            # Ca riêng, vì lý do KHÁC HẲN: nút này CÓ đi vào `pUp`.
            # Nói nhầm là "không đi vào pUp" thì lần sau ai đó sẽ gỡ nó
            # khỏi mã vì tưởng nó vô dụng.
            print("  `dinhGia.sanNenGiay` CÓ đi vào `pUp` — nhưng bàn thử")
            print("  này không bao giờ chạm tới nó. `tau = max(san,")
            print("  tau_that)`, mà lát cắt nhỏ nhất ở đây là "
                  + format(min(m.LAT_CAT), "g") + " giây còn mép")
            print("  trên của nút là 15 giây, nên `max` luôn trả `tau_that`.")
            print("  Đo được: quét cả trục 1→15 cho Brier GIỐNG HỆT tới 5")
            print("  chữ số, khoảng tin [0,000000, 0,000000].")
            print()
            print("  Nó vẫn đo được bằng LÃI LỖ trên băng — băng có khung ở")
            print("  mọi τ, kể cả sát 0. Xem vòng tiến hoá ngày.")
            print()
            return 1
        print("  `" + DUONG + "` KHÔNG đi vào `pUp`, nên thước Brier ở")
        print("  đây không đo được nó — nó sẽ cho một đường PHẲNG, và")
        print("  đường phẳng trông y hệt một kết luận.")
        print()
        print("  Nút đo được bằng thước này:")
        for d in m.NUT_MO_HINH:
            print("    " + d)
        print()
        print("  Nút cỡ lệnh / trần vốn / ngưỡng vào lệnh phải đo bằng")
        print("  TIỀN: `scripts/chay-phat-lai.py`, hoặc vòng tiến hoá ngày")
        print("  vốn chấm bằng lãi lỗ trên băng.")
        print()
        return 1

    het = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    soNen = NGAY * 24 * 60 + 20
    print()
    print("=" * 78)
    print("  QUÉT CẢ TRỤC — " + DUONG)
    print("=" * 78)
    print("  " + str(nut.y))
    print("  dải [" + format(nut.thap, "g") + ", " + format(nut.cao, "g")
          + "] · bước " + format(nut.buoc, "g"))
    print("  lấy " + format(soNen, ",") + " nến mỗi chợ…", flush=True)

    chos = {}
    for t in thi_truong_doi_chieu_duoc():
        tm = m.nen_1p(str(t["nen"]), het - soNen * PHUT, soNen)
        if len(tm) >= 1200:
            chos[str(t["ma"])] = tm
    if not chos:
        print("  không chợ nào đủ nến. Dừng." + chr(10))
        return 1
    mocs = sorted({T for tm in chos.values() for T in tm
                   if T % 300_000 == 0})
    a, b = int(len(mocs) * m.CHIA_HOC), int(len(mocs) * m.CHIA_CHON)
    ba = (mocs[:a], mocs[a:b], mocs[b:])
    print("  " + str(len(chos)) + " chợ · HỌC " + format(len(ba[0]), ",")
          + " · CHỌN " + format(len(ba[1]), ",")
          + " · CHỐT " + format(len(ba[2]), ",") + " khung")
    print()

    cu = doc_tham_so(DUONG)
    try:
        cu = float(cu)
    except (TypeError, ValueError):
        cu = None
    truc = _truc(nut)
    if cu is not None and not any(abs(x - cu) < 1e-9 for x in truc):
        truc = sorted(truc + [cu])

    # `bienDongCuaSoGiay` là tham số của chính phép chấm, không phải một
    # trị đọc từ CONFIG lúc chấm — nên khi quét CHÍNH nó thì phải truyền
    # trị đang thử vào `cham`, chứ đặt vào CONFIG thì không có tác dụng.
    laCuaSo = DUONG == "dinhGia.bienDongCuaSoGiay"
    cs0 = float(doc_tham_so("dinhGia.bienDongCuaSoGiay") or 300.0)

    ket: dict[float, dict] = {}
    for v in truc:
        if laCuaSo:
            r = m.cham(chos, ba, v)
        else:
            _dat(DUONG, v)
            r = m.cham(chos, ba, cs0)
        if r is None:
            print("    " + format(v, ">8g") + "   chưa đủ cặp")
            continue
        ket[v] = r
        nhan = ("   ← đương nhiệm"
                if cu is not None and abs(v - cu) < 1e-9 else "")
        print("    " + format(v, ">8g") + "   CHỌN " + format(r["chon"], ".5f")
              + "   CHỐT " + format(r["chot"], ".5f") + nhan, flush=True)
    if cu is not None:
        _dat(DUONG, cu)

    goc = ket.get(cu) if cu is not None else None
    if goc is None:
        print(chr(10) + "  Không chấm được trị đương nhiệm — "
              "không dựng được khoảng tin." + chr(10))
        return 1

    print()
    print("  khoảng tin trên tập CHỐT, so với đương nhiệm "
          + format(cu, "g") + ":")
    tot = []
    for v, r in ket.items():
        if abs(v - cu) < 1e-9:
            continue
        n = min(len(r["_saiChot"]), len(goc["_saiChot"]))
        hieu = [r["_saiChot"][i] - goc["_saiChot"][i] for i in range(n)]
        thap, cao, soK = khoang_tin_theo_khoi(hieu, goc["_mocChot"][:n])
        if cao < 0:
            dau = "TỐT HƠN"
            tot.append((v, cao))
        elif thap > 0:
            dau = "TỆ HƠN"
        else:
            dau = "chứa 0"
        print("    " + format(v, ">8g") + "   ["
              + format(thap, "+.6f") + ", " + format(cao, "+.6f")
              + "]  (" + str(soK) + " khối) → " + dau)

    # Trục PHẲNG TUYỆT ĐỐI: thước không nhìn thấy nút, chứ không phải
    # "không trị nào tốt hơn". Hai câu ấy khác hẳn nhau, và câu thứ hai
    # trông y hệt một kết luận.
    if len({round(r["chot"], 9) for r in ket.values()}) == 1 and len(ket) > 1:
        print()
        print("  ⚠ TRỤC PHẲNG TUYỆT ĐỐI — thước này KHÔNG NHÌN THẤY nút.")
        print("    Mọi trị cho cùng một điểm tới chữ số cuối. Đây không")
        print("    phải 'không trị nào tốt hơn'; đây là 'hỏi sai thước'.")
        print("    Thường vì nút chỉ có tác dụng ở vùng bàn thử không lấy")
        print("    mẫu — lát cắt τ nhỏ nhất ở đây là "
              + format(min(m.LAT_CAT), "g") + " giây.")
        print()
        return 1

    # Nút giữ vùng τ→0 thì bàn thử chỉ nhìn được RÌA NGOÀI của vùng ấy.
    if DUONG == "dinhGia.matPhangCanKetQua":
        print()
        print("  ⚠ VÙNG MÙ: nút này giữ vùng τ→0, mà lát cắt nhỏ nhất ở")
        print("    đây là " + format(min(m.LAT_CAT), "g") + " giây. Tỉ lệ bị"
              " kẹp đo được: 1,39% ở τ=240s ·")
        print("    7,05% ở 180s · 17,50% ở 120s · 36,94% ở 60s — tăng vọt")
        print("    khi τ nhỏ. Ở τ lớn phép kẹp gần như chỉ tốn điểm, nên")
        print("    bảng dưới sẽ ĐƠN ĐIỆU khuyên hạ. Đó là hạ lớp bảo vệ")
        print("    đúng chỗ cái thước không nhìn được. Xem")
        print("    `//vungMuCuaBanThuBrier` trong config.json.")

    print()
    if tot:
        tot.sort(key=lambda x: x[1])
        print("  CÓ trị tốt hơn có ý nghĩa: "
              + ", ".join(format(v, "g") for v, _ in tot))
        print("  Đọc HÌNH DẠNG cả trục trước khi vặn: đơn điệu là thứ khó")
        print("  giả, một đỉnh nhọn giữa trục thường là nhiễu.")
    else:
        print("  Không trị nào tốt hơn có ý nghĩa. Giữ nguyên là kết quả")
        print("  hợp lệ, và nó đáng tin hơn một lần vặn theo khoảng chứa 0.")
    print()
    print("  Thước ở đây là độ CHUẨN của dự báo, không phải TIỀN.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
