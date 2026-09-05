"""Kiểm tầng nguồn dữ liệu ngoài — phân loại tin và sức khoẻ từng nguồn.

    python scripts/kiem-nguon.py            # đủ, có chạm mạng
    python scripts/kiem-nguon.py --offline  # chỉ kiểm phân loại, không chạm mạng

Phần `--offline` là phần quan trọng nhất và nên chạy mỗi lần sửa `CHU_DE`. Xếp
tin sai không làm chương trình đổ; nó chỉ lặng lẽ đặt tin vào nhóm sai, và
người đọc bảng tin không có cách nào biết. Hai lỗi có thật đã bắt được ở đây:

  · "SEC Charges **Boiler** Room Operator" rơi vào nhóm vĩ mô vì "oil" nằm
    trong "b-oil-er" — hồi còn so khớp bằng chuỗi con.
  · Nhóm "quy định crypto" nuốt trọn mọi án lừa đảo thường của SEC, vì chỉ xét
    từ pháp lý mà không đòi thêm ngữ cảnh crypto.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# KHÔNG BAO GIỜ chạm sổ thật. GHI ĐÈ, không `setdefault`: một dòng
# `export TCT_DATA_DIR=` trong shell là đủ để setdefault không làm gì, và
# chuyện đó đã sập BA lần ở repo này — lần nặng nhất là bộ kiểm cửa duyệt đưa
# một champion GIẢ lên ngôi trong sổ chiến lược thật.
import os
from _tam_tu_don import tam_moi

os.environ["TCT_DATA_DIR"] = tam_moi("tct-kiem-")

from trader import nguon  # noqa: E402

sai = 0


def kiem(tieu_de: str, mong: set[str], vi_sao: str = "") -> None:
    """`mong` là TẬP chủ đề đúng. Tập rỗng nghĩa là không được xếp vào đâu cả."""
    global sai
    kq = nguon._xep_chu_de(tieu_de)
    duoc = {ma for ma, _ in kq}
    if duoc == mong:
        print(f"  OK   {tieu_de[:62]}")
        return
    sai += 1
    print(f"  SAI  {tieu_de[:62]}")
    print(f"       mong {sorted(mong) or '(không nhóm nào)'} · ra {sorted(duoc) or '(không nhóm nào)'}")
    if kq:
        print(f"       khớp: {kq}")
    if vi_sao:
        print(f"       {vi_sao}")


print("\n[1] bẫy chuỗi con — từ khoá phải khớp theo RANH GIỚI TỪ")
kiem("SEC Charges Boiler Room Operator and Three Entities", set(),
     '"oil" nằm trong "b-oil-er" — không được tính là tin dầu')
kiem("Company reports strong retail sales in Detroit", set(),
     '"oil" không nằm trong "Detroit"; "gdp" không nằm đâu cả')
kiem("Oil prices climb as OPEC holds output steady", {"VI_MO"})

print("\n[2] nhóm quy định phải đòi CẢ pháp lý LẪN crypto")
kiem("SEC Charges Toms River Trio in Alleged $47 Million Scheme", set(),
     "án lừa đảo thường — không dính tài sản số")
kiem("Federal Reserve Board issues enforcement action with former employee", set(),
     "án phạt ngân hàng — không dính tài sản số")
kiem("SEC approves spot Bitcoin ETF applications from BlackRock", {"QUY_DINH", "ETF"},
     "vừa là tin pháp lý vừa là tin ETF — nằm ở cả hai nhóm là đúng")
kiem("New crypto regulation clears Senate committee", {"QUY_DINH"})

print("\n[3] nhóm Fed = CHÍNH SÁCH, không phải 'mọi thứ Fed nói'")
kiem("Federal Reserve issues FOMC statement", {"FED"})
kiem("Minutes of the Federal Open Market Committee, June 16-17, 2026", {"FED"})
kiem("Minutes of the Board's discount rate meetings on June 8", {"FED"})
kiem("Fed cuts rates by 25 basis points", {"FED"})
kiem("Powell signals patience on interest rates", {"FED"})
kiem("Federal Reserve Board announces new leadership for task force", set(),
     "bổ nhiệm nhân sự — không phải tin chính sách")

print("\n[4] lạm phát và vĩ mô")
kiem("Latest Consumer Price Index Offers A Look At Inflation", {"LAM_PHAT"})
kiem("Jobless claims fall to a three-month low", {"LAM_PHAT"})
kiem("Treasury yield curve steepens after tariff announcement", {"VI_MO"})

print("\n[5] tin không thuộc nhóm nào thì phải nằm ngoài, không được ép vào")
kiem("China's Z.AI Ships GLM-5.3, Calling It Top Open-Weight Coding Model", set())
kiem("Uber partners with Pony.ai for 2,000 robotaxis in Europe", set())
kiem("Meta Patents Cameras That Recognize Faces", set())

if "--offline" not in sys.argv:
    import time

    print("\n[6] chạm mạng — từng nguồn một")
    t = time.time()
    d = nguon.tat_ca()
    print(f"       gom hết trong {time.time() - t:.1f}s")
    for ten, goi in d.items():
        if goi.get("co"):
            print(f"  OK   {ten}")
        else:
            sai += 1
            print(f"  SAI  {ten} không lấy được · {goi.get('loi')}")

    ps = d["phaiSinh"]
    for truong in ("funding", "openInterestUsd", "topTrader", "toanSan", "taker"):
        if ps.get(truong) is None:
            sai += 1
            print(f"  SAI  phái sinh thiếu {truong}")
        else:
            print(f"  OK   phái sinh có {truong}")

    sk = d["suKien"]
    print(f"       feed sống {sk['soFeed']}/{sk['tongFeed']} · {sk['soBai']} bài")
    if sk["soFeed"] < 5:
        sai += 1
        print(f"  SAI  quá ít feed sống — {sk['loi']}")

    # Một chủ đề rỗng KHÔNG phải lỗi (hôm nay có thể không có tin dầu). Nhưng
    # rỗng HẾT thì là hỏng phân loại chứ không phải hôm nay trời yên.
    co_tin = sum(1 for c in sk["chuDe"] if c["soBai"])
    if co_tin == 0 and sk["soBai"]:
        sai += 1
        print(f"  SAI  {sk['soBai']} bài mà không bài nào vào nhóm nào")
    else:
        print(f"  OK   {co_tin}/{len(sk['chuDe'])} nhóm có tin")

print("\n" + "=" * 60)
if sai:
    print(f"  {sai} phép kiểm hỏng.")
    sys.exit(1)
print("  TẦNG NGUỒN NGOÀI SẠCH.")
print("=" * 60)
