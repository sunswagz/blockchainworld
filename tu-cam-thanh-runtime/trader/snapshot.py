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

from .config import ROOT
from .journal import performance, recent_lessons, recent_trades

# runtime nằm ở <repo>/tu-cam-thanh-runtime/, cung nằm ở <repo>/tu-cam-thanh/
OUT = ROOT.parent / "tu-cam-thanh" / "assets" / "js" / "v" / "phien.js"

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
    }


def write(runtime) -> Path:
    data = build(runtime)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, indent=1, default=str)
    OUT.write_text(f"{HEADER}window.TU_CAM_THANH = {body};\n", encoding="utf-8")
    return OUT


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
        print(f"đã ghi {p}")

    asyncio.run(_once())
