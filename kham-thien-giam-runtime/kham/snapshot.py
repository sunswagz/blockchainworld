"""Cầu nối runtime → cung tĩnh.

Cung `kham-thien-giam/` là trang tĩnh trên GitHub Pages: không server, không
vòng lặp, không khoá API. Nó không thể tự hỏi Polymarket hay Binance bất cứ
điều gì — và đó là chủ ý, vì mọi thứ trong repo này theo luật "khoá không bao
giờ ra tới trình duyệt".

Nên runtime ghi một lát cắt trạng thái thành `assets/js/v/dai-chiem.js`, và
trang tĩnh chỉ việc đọc. Cùng cơ chế Hoàng Thành và Tử Cấm Thành đang dùng:
nguồn nằm ngoài tầm với của Actions ⇒ sinh ở máy có nguồn ⇒ commit kết quả.

Chọn `assets/js/v/` không tuỳ tiện: đó là nhánh **mạng-trước** trong `sw.js`,
được miễn luật nâng `CACHE_VERSION`. Đặt nhầm sang nhánh cache-trước thì máy
đã cài app sẽ hiện lát cắt của hôm qua cho tới lần nâng version kế tiếp — một
bảng điều khiển nói dối, tệ hơn hẳn không có bảng nào. Đúng cái bẫy đã cắn
`logos.js` của Công Bộ.

    python -m kham.snapshot      ghi một lần rồi thoát

## Vòng lặp nền KHÔNG tự ghi file này, và tiêu đề từng nói ngược

Tiêu đề của `dai-chiem.js` hứa `python run.py — ghi mỗi vòng lặp` từ đầu.
Câu ấy chép từ Tử Cấm Thành, nơi nó đúng thật (`trader/loop.py` gọi
`snapshot.write` sau MỌI vòng). Ở đây không lời gọi nào tồn tại:
`ghi_lat_cat` chỉ có hai chỗ gọi — nút trong buồng lái và
`python -m kham.snapshot`.

Hậu quả im lặng: cung tĩnh chỉ đổi khi có người nhớ bấm nút, nên trang
công khai đứng ở lát cắt cũ trong khi tiêu đề của chính nó nói nó tươi mỗi
vòng. Đo ngày 28/08/2026: `dai-chiem.js` đã tám ngày tuổi.

**Cách chữa đúng là sửa LỜI HỨA, không thêm lời gọi vào vòng lặp.** Thị
Bạc Ty đã thử chiều kia trước và phải lùi lại: trang công khai đọc bản ĐÃ
COMMIT, nên ghi ra đĩa 30 giây một lần không đẩy được byte nào lên site —
đổi lại chỉ được một file được git theo dõi luôn bẩn, và
`git merge --ff-only` ở cây chính hỏng ngay lần đầu có commit chạm tới nó.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .config import CONFIG, ROOT, che_hieu_luc
from .sach import sach

_TUONG_DOI = ("assets", "js", "v", "dai-chiem.js")

HEADER = """/* SINH TỰ ĐỘNG bởi kham-thien-giam-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái Đài Chiêm, để trang tĩnh đọc được mà không cần server
   và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python -m kham.snapshot       ghi một lần rồi thoát
       nút "Ghi lát cắt" ở buồng lái localhost:5186

   Vòng lặp nền KHÔNG tự ghi file này. Trang công khai đọc bản ĐÃ COMMIT,
   nên ghi mỗi vòng cũng không làm site tươi hơn một giây nào — nó chỉ để
   lại một file được theo dõi luôn bẩn. SINH RỒI PHẢI COMMIT thì site mới
   đổi.
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
    anh_em = ROOT.parent / "kham-thien-giam"
    return anh_em if (anh_em / "index.html").exists() else None


def dung(runtime) -> dict:
    """Dựng object lát cắt.

    `date` và `tomTat` phải nằm NGAY ĐẦU object. Cổng Thành chỉ đọc 900 byte
    đầu file rồi huỷ dòng tải, nên đổi thứ tự khoá là thẻ ngoài cổng mất ngày
    cập nhật — và mất im lặng. Đúng bẫy đã ghi trong `portal.js` cho Hộ Bộ và
    Thái Bộc Tự.
    """
    a = runtime.anh_chup()
    gio = dt.datetime.now(dt.timezone.utc)
    tk = a.get("thongKe") or {}
    kho = a.get("kho") or {}

    co_hoi = a.get("coHoi") or []
    dang_lam = [c for c in co_hoi if c.get("dangLam")]

    return {
        "date": gio.strftime("%d/%m/%Y"),
        "tomTat": _tom_tat(a, co_hoi, dang_lam),
        "generatedAt": gio.isoformat(timespec="milliseconds").replace("+00:00", "Z"),

        "che": a.get("che"),
        "cheKhai": a.get("cheKhai"),
        "vong": a.get("vong"),
        "chayDuocGiay": a.get("chayDuocGiay"),

        "thiTruong": a.get("thiTruong") or [],
        # `boQua` là lý do từng market bị bỏ qua lượt này. Bỏ sót nó ra khỏi
        # lát cắt là đúng kiểu hỏng mà cả cung này giảng về: trang tĩnh hiện
        # một bảng trống, mọi đèn xanh, và không ai biết vì sao không có số.
        # `scripts/kiem-lat-cat.mjs` bắt được đúng chỗ này lúc dựng.
        "boQua": a.get("boQua") or {},
        "coHoi": co_hoi,
        "kho": kho,
        "risk": a.get("risk") or {},
        "lenh": {k: v for k, v in (a.get("lenh") or {}).items() if k != "ganDay"},
        "hieuChinh": a.get("hieuChinh") or {},
        "thongKe": tk,
        "chienThuat": a.get("chienThuat") or [],
        "vi": a.get("vi") or {},
        "nguon": a.get("nguon") or {},
        "dongSong": a.get("dongSong") or {},
        "ketToan": a.get("ketToan") or {},
        "doThi": a.get("doThi") or {},
        "voDich": a.get("voDich") or {},
        "tienHoa": a.get("tienHoa") or {},
        "quyetChan": a.get("quyetChan") or {},
        "bang": a.get("bang") or {},
        # SỐ KẾT QUẢ — sự thật nền mà mọi điểm số của cung này đứng lên.
        #
        # Thiếu nó, trang tĩnh nói về một máy dự báo mà không nói máy ấy
        # đã được chấm trên bao nhiêu kết quả THẬT. Và nó mang sẵn
        # `soTheoSan` với `soTuTinh`: 100% `tu-tinh` nghĩa là chưa một
        # dòng nào được SÀN xác nhận — điều phải đọc được từ ngoài, chứ
        # không nằm trong một ghi chú nội bộ.
        "soKetQua": a.get("soKetQua") or {},

        # Nói thẳng cho người xem trang tĩnh biết họ đang nhìn gì.
        "loiNhac": (
            "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu "
            "sống. Trang này không gọi API nào và không đặt được lệnh nào."
        ),
    }


def _tom_tat(a: dict, coHoi: list, dangLam: list) -> str:
    che = a.get("che")
    if che == "quan-sat":
        return f"{len(coHoi)} cơ hội đã cân · chế độ quan sát"
    tk = a.get("thongKe") or {}
    if tk.get("chuaCo") or not tk.get("n"):
        return f"{len(dangLam)}/{len(coHoi)} cơ hội qua sàng · chưa có market nào kết toán"
    return (f"{tk['n']} market đã kết toán · kỳ vọng {tk['kyVong']:+.4f}$/lệnh")


def ghi_lat_cat(runtime) -> Path | None:
    """Ghi lát cắt ra cung tĩnh. None nếu không tìm thấy cung."""
    cung = _cung_tinh()
    if cung is None:
        return None
    d = cung.joinpath(*_TUONG_DOI)
    d.parent.mkdir(parents=True, exist_ok=True)
    # `sach()` bắt buộc, không phải phòng xa: `inf` và `nan` làm `json.dumps`
    # ném giữa chừng, và vòng lặp chỉ ghi một dòng nhật ký rồi đi tiếp — cung
    # tĩnh đứng im ở lát cắt cũ mà không ai biết. Đã nổ thật một lần ở
    # `/api/trang-thai` với `tuoi_ms()` của nguồn chưa gọi lần nào.
    noi_dung = HEADER + "window.DAI_CHIEM = " + json.dumps(
        sach(dung(runtime)), ensure_ascii=False, indent=2) + ";\n"
    d.write_text(noi_dung, encoding="utf-8")
    return d


def _main() -> None:
    from .vong import runtime
    runtime._mot_vong()
    p = ghi_lat_cat(runtime)
    if p is None:
        print("Không tìm thấy cung tĩnh — bỏ qua việc ghi lát cắt.")
        print("Đặt `cungTinh` trong config.json nếu runtime đã chuyển ra khỏi repo.")
    else:
        print(f"Đã ghi {p}")
        print(f"chế độ: {che_hieu_luc()}")


if __name__ == "__main__":
    _main()
