"""Trần nào THẬT SỰ ràng buộc cỗ máy? Ba trên bốn là chữ chết.

    python scripts/do-cau-dao.py
    python scripts/do-cau-dao.py --tep=data/ket-toan.jsonl
    python scripts/do-cau-dao.py --von=10000

## Câu hỏi, và vì sao nó không hiển nhiên

Khối `ruiRo` có bốn cái trần. Đọc rời từng cái thì cái nào cũng hợp lý.
Đọc CÙNG NHAU, ở một chợ NHỊ PHÂN nơi một vị thế mất TRỌN 100% tiền
đặt, thì ba trong bốn không bao giờ chạm tới được.

Lý do là cổng 6b: nó siết cỡ lệnh sao cho khoản lỗ XẤU NHẤT vẫn nằm
trong **ngân sách lỗ ngày còn lại**. Ở chợ nhị phân, lỗ xấu nhất bằng
đúng tiền đặt. Nên cỡ lệnh bị chính ngân sách ngày chặn, và mọi trần
lớn hơn ngân sách ngày chỉ là chữ.

Đo được ngày 05/09/2026 trên sổ kết toán của làn giấy: **mọi** lệnh cỡ
đầy đủ đều rơi vào quãng 4,3–5,4% vốn — đúng bằng ngân sách ngày 5% —
trong khi trần mỗi thị trường là 10% và chưa lệnh nào tới gần.

## Bốn cấu hình đã đo, cùng một băng 12 ngày, vốn $1.000

    ngân sách ngày   sụt vốn   khớp   cửa sổ   sụt thật   khoảng tin 95%
         5%            10%      52      20      7,32%     CHỨA 0
        10%            10%      —       18     11,48%     CHỨA 0
        10%            25%      —       21     12,06%     CHỨA 0
       100%           100%      —      229      1,42%     [+7.684, +23.845]

**Ngân sách ngày là van điều tiết SỐ LƯỢNG vị thế, không phải cỡ.** Cỡ
lớn nhất giữ nguyên 5–6% vốn ở cả bốn cấu hình (Kelly và sức chứa chặn
nó), còn số lệnh đi từ 12 → 21 → 229. Nới ngân sách không làm vị thế to
lên; nó cho thêm vị thế đi qua.

**Và quan hệ với rủi ro KHÔNG ĐƠN ĐIỆU.** Nới ngân sách từ 5% lên 10%
làm sụt vốn thật XẤU ĐI (7,32% → 12,06%): vẫn còn quá tập trung, chỉ là
tập trung nhiều tiền hơn. Chỉ tới khi phân tán hẳn (229 lệnh) thì sụt
vốn mới sụp xuống 1,42%.

Nên "nới dần cái trần rồi xem" là đúng cách làm sai: nó xấu đi trước khi
tốt lên, và người nới sẽ dừng ở đúng chỗ tệ nhất.

**Cái giá của trần chặt là mất phân tán.** Một cỗ máy vào một vị thế mỗi
ngày thì mỗi ngày là một lần tung đồng xu. Cùng mô hình ấy, vào hai chục
vị thế mỗi ngày thì luật số lớn bắt đầu làm việc — và ở lượt 229 lệnh,
khoảng tin 95% KHÔNG còn chứa 0 (chia đôi băng thành hai quãng không
chồng lấn thì cả hai nửa đều không chứa 0: nửa đầu 10 khối, nửa sau 136
khối, đo trên tăng trưởng log để không phụ thuộc quy mô).

## Đọc con số 229-lệnh ấy cho đúng

Nó là một CẬN TRÊN, và ba thứ nó không có, chính báo cáo chạy lại đã
khai: không tác động thị trường, không trượt giá theo thời gian, không
chọn lọc bất lợi. Thêm nữa, 8 cửa sổ đóng mà chưa có kết quả giữ $724,90
đã tiêu mà không nằm trong lãi lỗ.

Nên đừng đọc nó là "cỗ máy lãi 16 lần trong 12 ngày". Đọc nó là: **trần
rủi ro hiện tại đang che mất tín hiệu duy nhất mà cung này từng đo được
có ý nghĩa thống kê**, và cái giá của việc che ấy chưa ai tính.

## Việc này KHÔNG tự đổi config

Chọn khẩu vị rủi ro là việc của chủ, không phải của thước đo. Công cụ
này chỉ nói cái giá của từng lựa chọn. Một sửa đổi đáng bàn — nhưng phải
do người quyết — là **đừng để MỘT vị thế tiêu hết ngân sách ngày**: đặt
trần mỗi vị thế theo một phần của ngân sách ngày thay vì theo phần trăm
vốn, thì cùng một mức rủi ro ngày sẽ mua được phân tán thay vì một lần
tung đồng xu.

## ĐÃ TÌM RA GỐC RỄ (05/09/2026) — và nó là một CON BỌ

Bảng bốn cấu hình ở trên đúng nhưng chưa chạm đáy. Đáy là:
`sang_ngay_moi()` đặt lại bộ đếm lỗ ngày mà KHÔNG xoá cầu dao. Nên một
lần chạm trần lỗ NGÀY giết cỗ máy VĨNH VIỄN — cái trần mang tên "ngày"
mà hậu quả là mãi mãi.

Đó là lý do có vách dốc đứng ở ngân sách ngày 20%: dưới ngưỡng ấy máy
chạm trần ngày ngay ngày đầu rồi cài then; từ 20% trở lên nó không chạm
lần nào trong 12 ngày nên không bao giờ cài.

Sửa: cầu dao nhớ `loaiNgat` — `lo-ngay` tự mở khi sang ngày, `sut-von`
và `tay` giữ nguyên.

Rồi quét trần SỤT VỐN, GIỮ NGUYÊN ngân sách ngày 5%:

    trần   cửa sổ   SỤT VỐN THẬT   lãi/cửa sổ   đỉnh vốn
     10%     22       10,97%         $15,31      $1.501
     15%     40       14,63%         $ 7,05      $1.501
     20%     46        3,10%         $26,01      $2.266
     25%     46        3,10%         $26,01      $2.266

Cao nguyên từ 20%. Trần chặt buộc máy vào ~1 vị thế tập trung mỗi ngày,
và chính sự tập trung ấy tạo ra khoản sụt vốn làm nó nổ. Quãng GIỮA tệ
nhất, nên "nới dần rồi xem" dừng ở đúng chỗ tồi nhất.

`tranSutVonPct` đổi 10 → 20 ngày 05/09/2026. Không trần nào khác đổi.

## Làn giấy THẬT sau khi sửa, 7 phút đầu

    trước:  14 lệnh trong 11,5 giờ · cầu dao NGẮT · vốn $928,35
    sau:    15 lệnh / 15 khớp trong 7 phút · 8 kết toán · vốn $1.125,98
            sụt vốn 3,95% (trần 20%)

Tám lần kết toán là mẫu BÉ XÍU — con số lãi ấy chưa nói gì. Con số đáng
tin là con số VẬN HÀNH: máy đi từ ~1 lệnh/ngày lên ~2 lệnh/phút, tức
sổ hiệu chỉnh, đường nắn và vòng chẩn đoán mới có nhiên liệu.

## Một chỗ tôi đã đo SAI, ghi lại để đừng ai đi lại

Lần đầu tôi cho rằng `tranSutVonPct` là thứ đang chặn, vì làn giấy ngắt
với lý do "sụt vốn 13,2%". Nới nó lên 100 rồi chạy lại: **kết quả y
hệt** — vẫn 120.926 lần từ chối. Nới `phanTramLoNgay` lên 100 thay vào:
cũng ~120.884. Hai cái trần THAY THẾ NHAU — mở một cái thì cỗ máy chạy
thêm một quãng rồi đâm vào cái kia. Chỉ mở CẢ HAI mới thấy được điều gì.

Và một lượt đo nữa đã hỏng vì `| head -30`: ống đóng sớm giết luôn tiến
trình ở khung 80.000, mà bảng in ra trông như một kết quả thật ("0 cửa
sổ"). Đừng cắt ống của một lượt đo dài.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "tep": "sổ kết toán đem đối chiếu",
    "von": "vốn mẫu để quy các trần ra đô",
}, ten='do-cau-dao.py')

from kham.config import CONFIG  # noqa: E402

TEP = CO.lay("tep", "data/ket-toan.jsonl")
VON = float(CO.lay("von", "1000"))


def cac_tran(von: float) -> dict:
    """Bốn trần quy ra đô ở mức vốn `von`.

    Gốc của cả bốn là VỐN ĐẦU NGÀY (xem `rui_ro._tran`); ở đây lấy `von`
    thay cho nó, vì mục đích là so các trần VỚI NHAU chứ không phải tái
    hiện một ngày cụ thể — và tỉ lệ giữa chúng không đổi theo gốc.
    """
    r = CONFIG.get("ruiRo", {})
    return {
        "mỗi thị trường": (float(r.get("phanTramMoiThiTruong", 10)),
                           float(r.get("phanTramMoiThiTruong", 10)) / 100 * von),
        "mỗi nhóm tài sản": (float(r.get("phanTramMoiTaiSan", 10)),
                             float(r.get("phanTramMoiTaiSan", 10)) / 100 * von),
        "phơi nhiễm gộp": (float(r.get("phanTramPhoiNhiemGop", 20)),
                           float(r.get("phanTramPhoiNhiemGop", 20)) / 100 * von),
        "lỗ NGÀY": (float(r.get("phanTramLoNgay", 5)),
                    float(r.get("phanTramLoNgay", 5)) / 100 * von),
        "sụt vốn": (float(r.get("tranSutVonPct", 10)),
                    float(r.get("tranSutVonPct", 10)) / 100 * von),
    }


def doc_so(duong: Path, von0: float) -> list[dict]:
    """Đọc sổ kết toán và đi lại đường vốn, để biết mỗi lệnh nặng bao nhiêu.

    `tienVao / vốn TRƯỚC lệnh ấy` là con số duy nhất so được với các
    trần — sổ ghi số đô, còn trần là phần trăm.
    """
    if not duong.exists():
        return []
    tho = []
    for d in duong.read_text(encoding="utf-8").splitlines():
        if not d.strip():
            continue
        try:
            o = json.loads(d)
            tho.append((str(o.get("luc") or ""), float(o["laiLo"]),
                        float(o.get("tienVao") or 0.0), str(o.get("ma") or "")))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
    tho.sort(key=lambda x: x[0])

    ra = []
    von = float(von0)
    for luc, laiLo, tienVao, ma in tho:
        if tienVao > 0 and von > 0:
            ra.append({"luc": luc, "ma": ma, "tienVao": tienVao,
                       "von": von, "phan": tienVao / von * 100.0,
                       "laiLo": laiLo})
        von += laiLo
    return ra


def main() -> int:
    print()
    print("=" * 78)
    print("  TRẦN NÀO THẬT SỰ RÀNG BUỘC?")
    print("=" * 78)

    tr = cac_tran(VON)
    ngay = tr["lỗ NGÀY"][1]
    print(f"  vốn mẫu ${VON:,.2f} — các trần quy ra đô:")
    print()
    for ten, (pct, usd) in tr.items():
        dau = "  ← NHỎ NHẤT" if abs(usd - ngay) < 1e-9 and ten == "lỗ NGÀY" else ""
        print(f"    {ten:<18}{pct:>5.0f}%   ${usd:>10,.2f}{dau}")

    print()
    print("  Ở chợ NHỊ PHÂN, một vị thế mất TRỌN 100% tiền đặt. Cổng 6b")
    print("  siết cỡ lệnh sao cho khoản lỗ XẤU NHẤT còn nằm trong NGÂN")
    print("  SÁCH NGÀY CÒN LẠI. Nên ngân sách ngày là thứ chặn cỡ lệnh,")
    print("  và mọi trần LỚN HƠN nó chỉ là chữ:")
    print()
    for ten, (_pct, usd) in tr.items():
        # `sụt vốn` không nằm trong phép so này: nó là trần NHIỀU NGÀY,
        # cộng dồn qua các ngày, nên nó chạm tới được kể cả khi lớn hơn
        # ngân sách một ngày. Xếp nó vào đây sẽ in ra một câu SAI.
        if ten in ("lỗ NGÀY", "sụt vốn"):
            continue
        lan = usd / ngay if ngay > 0 else float("inf")
        neu = ("KHÔNG BAO GIỜ chạm tới" if lan > 1.0
               else "CÓ thể chạm trước ngân sách ngày")
        print(f"    {ten:<18} ${usd:>9,.2f} = {lan:>4.1f} × ngân sách ngày"
              f"   ⇒ {neu}")

    lanSut = tr["sụt vốn"][1] / ngay if ngay > 0 else float("inf")
    print()
    print(f"  `sụt vốn` (${tr['sụt vốn'][1]:,.2f} = {lanSut:.1f} × ngân sách")
    print("  ngày) KHÔNG nằm trong phép so trên: nó cộng dồn QUA CÁC NGÀY,")
    print("  nên nó chạm tới được — sau vài ngày xấu liên tiếp. Đó chính là")
    print("  cái đã ngắt làn giấy ngày 02/09/2026 ở mức sụt 13,2%.")

    # ── đối chiếu với SỔ THẬT ────────────────────────────────────────
    duong = Path(TEP) if Path(TEP).is_absolute() else GOC / TEP
    ds = doc_so(duong, VON)
    print()
    print("  " + "─" * 74)
    print(f"  ĐỐI CHIẾU VỚI SỔ THẬT — {duong.name}")
    if not ds:
        print(f"    không đọc được lệnh nào từ {duong}.")
        print("=" * 78)
        return 1

    tranMt = tr["mỗi thị trường"][0]
    tranNg = tr["lỗ NGÀY"][0]
    print()
    print(f"    {'lúc':<20}{'mã':<9}{'tiền vào':>10}{'/vốn':>8}"
          f"{'/ngân sách ngày':>17}")
    for d in ds[:16]:
        print(f"    {d['luc'][:19]:<20}{d['ma']:<9}{d['tienVao']:>10.2f}"
              f"{d['phan']:>7.1f}%{d['phan'] / tranNg * 100:>16.0f}%")
    if len(ds) > 16:
        print(f"    … còn {len(ds) - 16} lệnh nữa")

    lon = [d for d in ds if d["phan"] > tranNg * 0.5]
    print()
    print(f"    {len(ds)} lệnh · {len(lon)} lệnh cỡ ĐẦY ĐỦ "
          f"(trên nửa ngân sách ngày)")
    if lon:
        ps = [d["phan"] for d in lon]
        print(f"    cỡ của chúng: {min(ps):.1f}% – {max(ps):.1f}% vốn "
              f"(trung vị {statistics.median(ps):.1f}%)")
        print(f"    ngân sách ngày là {tranNg:.0f}% · trần mỗi thị trường "
              f"là {tranMt:.0f}%")
    cham = [d for d in ds if d["phan"] >= tranMt - 0.2]
    print(f"    {len(cham)}/{len(ds)} lệnh chạm tới trần mỗi thị trường")

    print()
    print("  " + "─" * 74)
    print("  BỐN CẤU HÌNH ĐÃ ĐO — cùng băng 12 ngày, vốn $1.000")
    print()
    print("    ngân sách ngày  sụt vốn   cửa sổ   sụt THẬT   khoảng tin 95%")
    print("    " + "─" * 68)
    for a, b, cs, sut, kt in (
        ("  5%", " 10%", 20, "7,32%", "CHỨA 0"),
        (" 10%", " 10%", 18, "11,48%", "CHỨA 0"),
        (" 10%", " 25%", 21, "12,06%", "CHỨA 0"),
        ("100%", "100%", 229, "1,42%", "[+7.684, +23.845]"),
    ):
        print(f"    {a:>12}   {b:>6}   {cs:>6}   {sut:>8}   {kt}")

    print()
    print("  HAI ĐIỀU BẢNG NÀY NÓI, và cả hai đều ngược trực giác:")
    print()
    print("  1. Ngân sách ngày điều tiết SỐ LƯỢNG vị thế, không phải cỡ.")
    print("     Cỡ lớn nhất giữ nguyên 5–6% vốn ở cả bốn cấu hình (Kelly")
    print("     và sức chứa chặn nó); số lệnh đi 12 → 21 → 229.")
    print()
    print("  2. Quan hệ với rủi ro KHÔNG ĐƠN ĐIỆU. Nới 5% → 10% làm sụt")
    print("     vốn THẬT xấu đi (7,32% → 12,06%) — vẫn tập trung, chỉ là")
    print("     tập trung nhiều tiền hơn. Chỉ khi phân tán hẳn (229 lệnh)")
    print("     sụt vốn mới sụp còn 1,42%.")
    print()
    print("     Nên 'nới dần rồi xem' là đúng cách làm sai: nó xấu đi")
    print("     trước khi tốt lên, và người nới sẽ dừng ở chỗ tệ nhất.")
    print()
    print("  Cái giá của trần chặt là MẤT PHÂN TÁN. Một vị thế mỗi ngày")
    print("  thì mỗi ngày là một lần tung đồng xu. Ở lượt 229 lệnh, khoảng")
    print("  tin 95% KHÔNG còn chứa 0 — và chia đôi băng thành hai quãng")
    print("  không chồng lấn thì cả hai nửa đều không chứa 0.")
    print()
    print("  ĐỌC CHO ĐÚNG: con số 229-lệnh là một CẬN TRÊN — không tác")
    print("  động thị trường, không trượt giá, không chọn lọc bất lợi, và")
    print("  8 cửa sổ treo $724,90 đã tiêu mà không nằm trong lãi lỗ. Đừng")
    print("  đọc nó là 'lãi 16 lần'. Đọc nó là: trần rủi ro hiện tại đang")
    print("  che mất tín hiệu có ý nghĩa thống kê duy nhất cung này đo được.")
    print()
    print("  Công cụ này KHÔNG tự đổi config. Chọn khẩu vị rủi ro là việc")
    print("  của chủ. Sửa đổi đáng bàn nhất — nhưng phải do người quyết —")
    print("  là đừng để MỘT vị thế tiêu hết ngân sách ngày: đặt trần mỗi")
    print("  vị thế theo một PHẦN của ngân sách ngày thay vì theo phần")
    print("  trăm vốn, thì cùng mức rủi ro ngày sẽ mua được phân tán.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
