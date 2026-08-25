"""Cầu nối runtime → cung tĩnh.

Cung `thi-bac-ty/` là trang tĩnh trên GitHub Pages: không server, không vòng
lặp, không khoá API. Nó không thể tự hỏi Binance hay Hyperliquid bất cứ điều
gì — và đó là chủ ý, vì mọi thứ trong repo này theo luật "khoá không bao giờ
ra tới trình duyệt".

Nên runtime ghi một lát cắt trạng thái thành `assets/js/v/cang-phi.js`, và
trang tĩnh chỉ việc đọc. Cùng cơ chế Hoàng Thành, Tử Cấm Thành và Khâm Thiên
Giám đang dùng: nguồn nằm ngoài tầm với của Actions ⇒ sinh ở máy có nguồn ⇒
commit kết quả.

Chọn `assets/js/v/` không tuỳ tiện: đó là nhánh **mạng-trước** trong `sw.js`,
được miễn luật nâng `CACHE_VERSION`. Đặt nhầm sang nhánh cache-trước thì máy
đã cài app sẽ hiện lát cắt của hôm qua cho tới lần nâng version kế tiếp — một
bảng điều khiển nói dối, tệ hơn hẳn không có bảng nào.

    python -m bac.snapshot      quét một lượt, ghi, rồi thoát
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
from pathlib import Path

from .config import CONFIG, ROOT, che_hieu_luc
from .sach import sach

_TUONG_DOI = ("assets", "js", "v", "cang-phi.js")

HEADER = """/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime — ĐỪNG SỬA TAY.
   Lát cắt chênh lệch funding giữa các cảng, để trang tĩnh đọc được mà không
   cần server và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python run.py                 ghi mỗi vòng lặp
       python -m bac.snapshot        ghi một lần rồi thoát
*/
"""


def _cung_tinh() -> Path | None:
    """Thư mục cung tĩnh, hoặc None nếu không có.

    Kiểm bằng `index.html` chứ không chỉ kiểm thư mục tồn tại. Hàm ghi mà tự
    `mkdir` đường dẫn anh em thì chuyển runtime sang chỗ khác là nó lặng lẽ
    đẻ ra một thư mục rác rồi ghi vào đó, còn cung thật thì ngừng cập nhật.
    Không lỗi nào, chỉ có một trang web đứng yên.
    """
    tay = (CONFIG.get("cungTinh") or "").strip()
    if tay:
        p = Path(tay)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        return p if (p / "index.html").exists() else None
    anh_em = ROOT.parent / "thi-bac-ty"
    return anh_em if (anh_em / "index.html").exists() else None


def dung(runtime) -> dict:
    """Dựng object lát cắt.

    `date` và `tomTat` phải nằm NGAY ĐẦU object. Cổng Thành chỉ đọc 900 byte
    đầu file rồi huỷ dòng tải, nên đổi thứ tự khoá là thẻ ngoài cổng mất ngày
    cập nhật — và mất trong im lặng.
    """
    a = runtime.anh_chup()
    gio = dt.datetime.now(dt.timezone.utc)
    co_hoi = a.get("coHoi") or []
    duyet = [c for c in co_hoi if c.get("duyet")]

    return {
        "date": gio.strftime("%d/%m/%Y"),
        "tomTat": _tom_tat(a, co_hoi, duyet),
        "generatedAt": gio.isoformat(timespec="milliseconds").replace("+00:00", "Z"),

        "maChienLuoc": a.get("maChienLuoc"),
        "che": a.get("che"),
        "cheKhai": a.get("cheKhai"),
        "vong": a.get("vong"),
        "chayDuocGiay": a.get("chayDuocGiay"),
        "giuGio": a.get("giuGio"),
        "ma": a.get("ma") or [],

        "cang": a.get("cang") or [],
        "dongHo": a.get("dongHo") or {},
        "baoGia": a.get("baoGia") or [],
        "coHoi": co_hoi,
        "soDuyet": len(duyet),
        # `viSaoTuChoi` là số liệu đáng giá nhất khi bảng trống. Bỏ nó ra khỏi
        # lát cắt là dựng một trang hiện bảng rỗng, mọi đèn xanh, và không ai
        # biết vì sao không có cơ hội nào — chính kiểu hỏng im lặng mà cả repo
        # này tồn tại để chặn.
        "viSaoTuChoi": a.get("viSaoTuChoi") or {},
        "ruiRo": a.get("ruiRo") or {},
        # Trần vốn CHƯA có hiệu lực. Có trong lát cắt vì đó là sự thật về
        # cỗ máy, và người xem trang tĩnh có quyền biết ba con số ấy không
        # chặn gì — chứ không phải suy ra từ việc chúng vắng mặt.
        "von": a.get("von") or {},
        "phiSan": a.get("phiSan") or {},
        "doDai": a.get("doDai") or [],
        "so": a.get("so") or {},
        "loiVongCuoi": a.get("loiVongCuoi"),

        "loiNhac": (
            "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu "
            "sống. Trang này không gọi sàn nào và không đặt được lệnh nào."
        ),
    }


def _tom_tat(a: dict, coHoi: list, duyet: list) -> str:
    song = sum(1 for c in (a.get("cang") or []) if c.get("songSot"))
    tong = len(a.get("cang") or [])
    if not coHoi:
        return f"{song}/{tong} cảng · chưa cân được cặp nào"
    if not duyet:
        return f"{len(coHoi)} cặp đã cân · KHÔNG cặp nào qua cửa rủi ro"
    tot = max(duyet, key=lambda c: c.get("netBps") or 0.0)
    return (f"{len(duyet)}/{len(coHoi)} cặp qua cửa · tốt nhất {tot['ma']} "
            f"{tot['netBps']:+.1f} bps")


def ghi_lat_cat(runtime) -> Path | None:
    """Ghi lát cắt ra cung tĩnh. None nếu không tìm thấy cung."""
    cung = _cung_tinh()
    if cung is None:
        return None
    d = cung.joinpath(*_TUONG_DOI)
    d.parent.mkdir(parents=True, exist_ok=True)
    # `sach()` bắt buộc, không phải phòng xa: `inf`/`nan` làm `json.dumps` ném
    # giữa chừng, và vòng lặp chỉ ghi một dòng nhật ký rồi đi tiếp — cung tĩnh
    # đứng im ở lát cắt cũ mà không ai biết.
    noi_dung = HEADER + "window.CANG_PHI = " + json.dumps(
        sach(dung(runtime)), ensure_ascii=False, indent=2) + ";\n"
    d.write_text(noi_dung, encoding="utf-8")
    return d


def _main() -> None:
    from .vong import runtime
    asyncio.run(runtime.mot_vong())
    p = ghi_lat_cat(runtime)
    if p is None:
        print("Không tìm thấy cung tĩnh — bỏ qua việc ghi lát cắt.")
        print("Đặt `cungTinh` trong config.json nếu runtime đã chuyển ra khỏi repo.")
    else:
        print(f"Đã ghi {p}")
        print(f"chế độ: {che_hieu_luc()}")


if __name__ == "__main__":
    _main()
