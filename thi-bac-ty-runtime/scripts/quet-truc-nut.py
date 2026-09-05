"""Quét CẢ TRỤC của một núm phân bổ trên tờ trình đã ghi.

    py scripts/quet-truc-nut.py
    py scripts/quet-truc-nut.py --nut=phanBo.toiDaSoViThe --luoi=30,60,120,180
    py scripts/quet-truc-nut.py --cua-so=2000,4000

Luật đọc nằm ở `thi_bac_ty/quet_truc.py` — file này chỉ là cái vỏ. Nó
KHÔNG đo lãi lỗ và không giả vờ đo được: cơ hội không được cấp vốn thì
không có kết cục. Xem `thi_bac_ty/chay_lai_he.py`.

Sổ đăng ký được SAO LƯU bằng API backup của sqlite trước khi đọc — mở
thẳng file đang được ghi vừa chạm khoá vừa có thể đọc phải trang rách.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

from thi_bac_ty.chay_lai_he import mot_luot, thu_hoach          # noqa: E402
from thi_bac_ty.quet_truc import (doi_chieu_hai_cua_so,          # noqa: E402
                                  quet_truc)
from thi_bac_ty.so_dang_ky import SoDangKy                       # noqa: E402
from thi_bac_ty.trung_uong import _dat_nut                       # noqa: E402

#: Ba núm, và cả ba đã được đo trên làn thật 05/09/2026. Lưới phải chạm
#: được HAI MÉP của `NUT_TRUNG_UONG` và phải chứa giá trị đang dùng.
MAC_DINH = {
    "phanBo.toiDaSoViThe": [3, 10, 30, 60, 90, 120, 150, 180, 240, 300],
    "ruiRoTong.tranMotCoHoi": [0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.35],
    "phanBo.toiThieuMotLanUsd": [25, 100, 500, 1000, 2500, 5000, 10000],
}


def _co(t: str, mac=None):
    for a in sys.argv[1:]:
        if a.startswith(t + "="):
            return a[len(t) + 1:]
    return mac


def _sao_luu(nguon: Path) -> Path:
    ra = Path(tempfile.mkdtemp(prefix="quet-truc-")) / "sdk.sqlite3"
    src = sqlite3.connect(f"file:{nguon}?mode=ro", uri=True, timeout=180)
    dst = sqlite3.connect(str(ra))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    return ra


def main() -> int:
    cong = _co("--cong", "5188")
    url = f"http://127.0.0.1:{cong}/api/trang-thai"
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            anh = json.load(r)["trungUong"]
    except Exception as e:                                # noqa: BLE001
        print(f"không đọc được {url}: {type(e).__name__}: {e}")
        print("cỗ máy phải đang chạy — tham số và vốn lấy từ nó.")
        return 2

    goc = anh["thamSo"]
    von = float(anh["danhMuc"]["vonBanDauUsd"])
    duong = Path(_co("--so-dang-ky",
                     str(GOC / "data" / "thi-bac-ty-so-dang-ky.sqlite3")))
    sdk = SoDangKy(_sao_luu(duong))

    nuts = ([_co("--nut")] if _co("--nut") else list(MAC_DINH))
    luoiTay = _co("--luoi")
    cuaSo = [int(x) for x in str(_co("--cua-so", "2000,4000")).split(",")]

    for nut in nuts:
        luoi = ([float(x) if "." in x else int(x)
                 for x in luoiTay.split(",")] if luoiTay
                else MAC_DINH.get(nut))
        if not luoi:
            print(f"không có lưới mặc định cho {nut} — dùng --luoi=")
            continue
        ket = []
        for n in cuaSo:
            tt, hong = thu_hoach(sdk, n=n)
            r = quet_truc(tt, goc, von, nut, luoi, mot_luot, _dat_nut)
            ket.append(r)
            print("")
            print(f"### {nut}  ·  cửa sổ {n} tờ trình ({len(tt)}, hỏng {hong})")
            if not r["hienTaiTrenLuoi"]:
                print(f"  ⚠ giá trị đang dùng {r['hienTai']} KHÔNG nằm trên "
                      f"lưới — mọi so sánh đang so với một điểm chưa đo")
            print("%12s%7s%12s%13s%14s%12s" % (
                "giá trị", "soCap", "rót USD", "NET bps/giờ",
                "TỔNG USD/giờ", "tỉ trọng ty"))
            for d in r["diem"]:
                net = d.get("netMoiGioBinhQuanBps")
                tt2 = d.get("tongUsdMoiGio")
                tr = d.get("tiTrongTy")
                dau = " ←" if d["giaTri"] == r["hienTai"] else ""
                print("%12s%7d%12s%13s%14s%12s%s" % (
                    d["giaTri"], d.get("soCap", 0),
                    f"{d.get('tongCapUsd', 0):,.0f}",
                    "-" if net is None else f"{net:.4f}",
                    "-" if tt2 is None else f"{tt2:.3f}",
                    "-" if tr is None else f"{tr:.1%}", dau))
            if r["batDong"]:
                print("  → TRỤC BẤT ĐỘNG: núm này không ràng buộc gì trong "
                      "chế độ hiện tại. Đừng đề xuất vặn nó.")
            # Quán quân theo TỔNG mà bị loại vì TẬP TRUNG phải hiện ra.
            # Tính rồi giấu thì người đọc thấy một người thắng khiêm tốn
            # và không biết vì sao kẻ cao điểm hơn không được gọi tên.
            tn = r.get("totNhat") or {}
            for bl in tn.get("quanQuanBiLoai", []):
                print("  ✗ %s có TỔNG cao hơn (%.3f) nhưng TẬP TRUNG hơn "
                      "chỗ đang đứng (ty %s · cảng %s) — cỗ máy này gọi thế "
                      "là `b-tot-hon-NHUNG-dam-hon`, và `cong_duyet` LOẠI."
                      % (bl["giaTri"], bl["tongUsdMoiGio"],
                         "-" if bl.get("tiTrongTy") is None
                         else f"{bl['tiTrongTy']:.1%}",
                         "-" if bl.get("tiTrongCang") is None
                         else f"{bl['tiTrongCang']:.1%}"))
            if tn.get("thieuMoc"):
                print("  ⚠ không có điểm ĐANG ĐỨNG trên lưới nên KHÔNG loại "
                      "được ai vì tập trung — người thắng ở đây mới chỉ "
                      "thắng theo TỔNG")

        if len(ket) >= 2:
            dc = doi_chieu_hai_cua_so(ket[0], ket[-1])
            print(f"  → hai cửa sổ: {dc['vi']}"
                  + ("" if dc["giaTri"] is None
                     else f" (giá trị {dc['giaTri']})"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
