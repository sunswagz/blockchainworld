"""Cầu nối runtime → cung tĩnh.

Cung `tu-cam-thanh/` là một trang tĩnh trên GitHub Pages: không có server, không
có vòng lặp, không có khoá API. Nó không thể tự hỏi Binance hay Claude bất cứ
điều gì — và đó là chủ ý, vì mọi thứ trong repo này đều theo luật "khoá không
bao giờ ra tới trình duyệt".

Nên runtime ghi lại một lát cắt trạng thái thành `assets/js/v/phien.js`, và trang
tĩnh chỉ việc đọc. Cùng cơ chế Hoàng Thành đang dùng: nguồn nằm ngoài tầm với của
Actions ⇒ sinh ở máy có nguồn ⇒ commit kết quả.

Chọn `assets/js/v/` không phải tuỳ tiện: đó là nhánh **mạng-trước** trong `sw.js`,
được miễn luật nâng `CACHE_VERSION`. Đặt nhầm sang nhánh cache-trước thì máy đã
cài app sẽ hiện phiên giao dịch của hôm qua cho tới lần nâng version kế tiếp —
một bảng điều khiển nói dối, tệ hơn hẳn không có bảng nào. Đúng cái bẫy đã cắn
`logos.js` của Công Bộ.
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from .bus import bus
from .config import CONFIG, ROOT
from .journal import performance, recent_lessons, recent_trades

# Runtime mặc định nằm cạnh cung: <repo>/tu-cam-thanh-runtime/ và <repo>/tu-cam-thanh/.
# Nhưng runtime CHUYỂN ĐI ĐÂU CŨNG ĐƯỢC — nó không cần nằm trong repo. Khi đó
# đặt `cungTinh` trong config.json trỏ tới thư mục cung, hoặc để trống nếu không
# muốn ghi ảnh chụp nữa.
_TUONG_DOI = ("assets", "js", "v", "phien.js")


def _cung_tinh() -> Path | None:
    """Thư mục cung tĩnh, hoặc None nếu không có.

    Kiểm bằng `index.html` chứ không chỉ kiểm thư mục tồn tại. Trước đây hàm ghi
    tự `mkdir` đường dẫn anh em: chuyển runtime sang chỗ khác là nó lặng lẽ đẻ ra
    một thư mục `tu-cam-thanh/` rác ở cạnh chỗ mới rồi ghi vào đó, còn cung thật
    thì ngừng cập nhật. Không có lỗi nào, chỉ có một trang web đứng yên.
    """
    tay = (CONFIG.get("cungTinh") or "").strip()
    if tay:
        p = Path(tay)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        return p if (p / "index.html").exists() else None
    anh_em = ROOT.parent / "tu-cam-thanh"
    return anh_em if (anh_em / "index.html").exists() else None

HEADER = """/* SINH TỰ ĐỘNG bởi tu-cam-thanh-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái của runtime giao dịch, để trang tĩnh đọc được mà không
   cần server và không cần khoá API. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem README):
       python run.py            ghi mỗi vòng lặp
       python -m trader.snapshot   ghi một lần rồi thoát
*/
"""


def _trim_tf(tf: dict) -> dict:
    """Bỏ `_raw` — nó là số chưa làm tròn dành cho Risk Engine, trang không dùng."""
    return {k: v for k, v in tf.items() if k != "_raw"}


def build(runtime) -> dict:
    snap = runtime.snapshot()
    ms = snap.get("marketState") or {}
    acct = snap.get("account") or {}
    perf = performance()

    return {
        "generatedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "chayTu": snap.get("startedAt"),
        "vong": snap.get("ticks"),
        "tamDung": snap.get("paused"),
        # Sàn nào đang khớp lệnh là thứ người xem PHẢI thấy ngay. Một bảng số
        # liệu không nói rõ nó là tiền giả nội bộ hay lệnh thật trên testnet thì
        # con số nào cũng vô nghĩa.
        "san": snap.get("venue"),
        "cheDoSan": snap.get("mode"),
        "chiLong": snap.get("spotOnly"),
        "cap": snap.get("symbol"),
        "khung": snap.get("timeframes"),
        "gia": snap.get("price"),
        "nguon": snap.get("dataSource"),
        "cheDo": snap.get("regime"),
        "thiTruong": {tf: _trim_tf(f) for tf, f in (ms.get("timeframes") or {}).items()},
        "luanDiem": snap.get("thesis"),
        "phanQuyet": snap.get("decision"),
        "taiKhoan": {
            "vonBanDau": runtime.cfg["risk"]["startingEquity"],
            "von": acct.get("equityMarked"),
            "vonThucHien": acct.get("equity"),
            "dinhVon": acct.get("peakEquity"),
            "laiLoMo": acct.get("openPnl"),
            "laiLoHomNay": acct.get("todayPnl"),
            "drawdownPct": acct.get("drawdownPct"),
            "soLenhDaDong": acct.get("closedCount"),
            "viThe": acct.get("positions") or [],
        },
        "rui_ro": {
            "dungHan": snap.get("risk", {}).get("halted"),
            "ngatMach": snap.get("risk", {}).get("breakers") or [],
            "gioiHan": snap.get("risk", {}).get("limits"),
        },
        "boNao": {
            "cheDo": snap.get("brain", {}).get("mode"),
            "model": snap.get("brain", {}).get("model"),
            "homNay": snap.get("brain", {}).get("today"),
            "hanMucUsd": snap.get("brain", {}).get("budgetUsd"),
            "soKyNang": snap.get("brain", {}).get("skillsLoaded"),
        },
        "thongKe": perf,
        "giaoDich": recent_trades(20),
        "baiHoc": recent_lessons(10),
        "theGioi": _the_gioi(),
        "huanLuyen": _huan_luyen(),
    }


def _the_gioi() -> dict | None:
    """Lát cắt nguồn ngoài, đủ gọn để nằm trong một file trang tĩnh.

    Cố ý KHÔNG chép cả 186 bài tin vào đây: file này bị commit và tải về ở mỗi
    lượt mở cung, nên nó phải nhẹ. Giữ các con số cùng vài tiêu đề đầu mỗi chủ
    đề — đủ để thấy bot đang đọc gì, không biến trang thành một bản sao RSS.
    """
    from . import nguon

    k = nguon.kho()
    if not k.get("co"):
        return None
    ps, vm, tl, sk = k["phaiSinh"], k["viMo"], k["tamLy"], k.get("suKien") or {}
    return {
        "luc": k.get("luc"),
        "phaiSinh": {"fundingNamHoa": ps.get("fundingNamHoa"),
                     "openInterestUsd": ps.get("openInterestUsd"),
                     "oiDoi24hPct": ps.get("oiDoi24hPct"),
                     "topTrader": ps.get("topTrader"), "toanSan": ps.get("toanSan"),
                     "nguon": ps.get("nguon")},
        "viMo": {"muc": vm.get("muc"), "khauVi": vm.get("khauVi"), "nguon": vm.get("nguon")},
        "tamLy": {"gt": tl.get("gt"), "nhan": tl.get("nhan"), "chuoi": tl.get("chuoi")},
        "tin": [{"ma": c["ma"], "soBai": c["soBai"],
                 "bai": [{"tieuDe": b["tieuDe"], "nguon": b["nguon"], "url": b.get("url")}
                         for b in c["bai"][:2]]}
                for c in (sk.get("chuDe") or [])],
        "soFeed": sk.get("soFeed"), "soBai": sk.get("soBai"),
    }


def _huan_luyen() -> dict | None:
    """Kết quả phiên huấn luyện gần nhất — KHÔNG kèm danh sách lệnh.

    Đây là phần đáng công bố nhất của cả cung: nó cho thấy chiến lược đã được
    đem ra đo chứ không chỉ được mô tả. Nhưng chỉ đăng con số tổng và kết luận;
    hàng trăm dòng lệnh thuộc về buồng lái, không thuộc về một trang chỉ-đọc.
    """
    from . import phien_hoc

    p = phien_hoc.trang_thai()
    kq = p.get("ketQua")
    if not kq:
        return None
    ra: dict = {"viec": p.get("viec"), "xong": p.get("xong")}
    if kq.get("thongKe"):
        ra.update({"thongKe": kq["thongKe"], "theoRegime": kq.get("theoRegime"),
                   "dungSom": kq.get("dungSom"), "baiHoc": kq.get("baiHoc"),
                   "nguong": kq.get("nguong")})
    if kq.get("totNhat"):
        ra.update({"totNhat": kq["totNhat"], "ketLuan": kq.get("ketLuan"),
                   "soToHop": kq.get("soToHop"), "mocCat": kq.get("mocCat"),
                   "tongNen": kq.get("tongNen")})
    return ra


_da_nhac = False


def write(runtime) -> Path | None:
    """Ghi ảnh chụp sang cung tĩnh. Trả None nếu không tìm thấy cung.

    Không tìm thấy thì BỎ QUA chứ không tạo thư mục mới — và nhắc đúng một lần,
    vì vòng lặp gọi hàm này mỗi 20 giây.
    """
    global _da_nhac

    cung = _cung_tinh()
    if cung is None:
        if not _da_nhac:
            _da_nhac = True
            tay = CONFIG.get("cungTinh")
            bus.log("system", "khong-thay-cung",
                    f"không thấy cung tĩnh ({tay or ROOT.parent / 'tu-cam-thanh'}) — "
                    f"bỏ qua việc ghi ảnh chụp. Runtime vẫn giao dịch bình thường; "
                    f"chỉ là trang công khai không được cập nhật. Nếu đã chuyển "
                    f"runtime đi chỗ khác, đặt \"cungTinh\" trong config.json.")
        return None

    out = cung.joinpath(*_TUONG_DOI)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = build(runtime)
    body = json.dumps(data, ensure_ascii=False, indent=1, default=str)
    out.write_text(f"{HEADER}window.TU_CAM_THANH = {body};\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    # Ghi một lần từ trạng thái đã lưu trên đĩa, không cần chạy vòng lặp.
    import asyncio

    import httpx

    from .loop import runtime as rt

    async def _once() -> None:
        rt.brain = await __import__("trader.brain", fromlist=["get_brain"]).get_brain()
        async with httpx.AsyncClient() as c:
            await rt.tick(c)
        p = write(rt)
        if p:
            print(f"đã ghi {p}")
        else:
            print("KHÔNG thấy cung tĩnh — không ghi gì.\n"
                  f'  đã tìm: {CONFIG.get("cungTinh") or ROOT.parent / "tu-cam-thanh"}\n'
                  '  nếu runtime đã chuyển đi chỗ khác, đặt "cungTinh" trong config.json\n'
                  "  trỏ tới thư mục cung (thư mục có index.html).")

    asyncio.run(_once())
