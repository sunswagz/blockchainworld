"""HTTP + SSE — dashboard quan sát và khung chat.

Web app là client thuần: nó không tính toán gì, chỉ hiển thị những gì runtime
phát ra qua bus. Nhờ vậy đóng trình duyệt không ảnh hưởng gì tới giao dịch, và
mở hai tab cũng không nhân đôi thứ gì.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from .brain import get_brain
from .bus import bus
from .config import CONFIG, WEB_DIR
from .journal import performance, recent_lessons, recent_theses, recent_trades
from .loop import runtime
from . import nguon, phien_hoc, tu_chay

app = FastAPI(title="Claude Trader — M0", docs_url=None, redoc_url=None)


@app.on_event("startup")
async def _startup() -> None:
    app.state.loop_task = asyncio.create_task(runtime.run())
    # Nguồn ngoài chạy ở LUỒNG RIÊNG, không nằm trong vòng giao dịch. Một lượt
    # gom mất ~5 giây trong khi nhịp tick là 20 giây; để chung thì một hôm
    # Yahoo chậm là vòng giao dịch trễ theo, và sự cố mạng của người khác hoá
    # thành sự cố của mình.
    nguon.bat_dau(CONFIG["symbol"], nhip=CONFIG.get("nhipNguonNgoai", 900))


@app.on_event("shutdown")
async def _shutdown() -> None:
    task = getattr(app.state, "loop_task", None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


# ── Trang tĩnh ────────────────────────────────────────────────────────────
@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/app.js")
async def appjs() -> FileResponse:
    return FileResponse(WEB_DIR / "app.js", media_type="application/javascript")


@app.get("/app.css")
async def appcss() -> FileResponse:
    return FileResponse(WEB_DIR / "app.css", media_type="text/css")


@app.get("/chart.js")
async def chartjs() -> FileResponse:
    return FileResponse(WEB_DIR / "chart.js", media_type="application/javascript")


# ── API đọc ───────────────────────────────────────────────────────────────
@app.get("/api/state")
async def state() -> JSONResponse:
    return JSONResponse(runtime.snapshot())


@app.get("/api/journal")
async def journal() -> JSONResponse:
    return JSONResponse({
        "trades": recent_trades(40),
        "lessons": recent_lessons(30),
        "theses": recent_theses(30),
        "performance": performance(),
    })


@app.get("/api/candles")
async def candles(limit: int = 160) -> JSONResponse:
    """Nến thô cho biểu đồ, kèm EMA và các mức mà bộ não đang nhìn.

    Trả cả `overlay` (SL/TP/vùng vào của luận điểm hiện tại, S/R) vì một biểu đồ
    nến trần không nói được điều đáng nói nhất: bot đang nhìn CHỖ NÀO trên đó.
    """
    m = runtime.last_market
    if not m:
        return JSONResponse({"ready": False, "timeframes": {}})

    out = {}
    for tf, c in m["timeframes"].items():
        out[tf] = [
            {"t": x["t"], "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"],
             "v": x["v"], "closed": x["closed"]}
            for x in c[-limit:]
        ]

    st = runtime.state or {}
    pri = runtime.primary
    f = (st.get("timeframes") or {}).get(pri, {})
    th = runtime.last_thesis or {}
    pos = runtime.broker.snapshot(m["price"]).get("positions") or []

    return JSONResponse({
        "ready": True,
        "symbol": m["symbol"],
        "price": m["price"],
        "primary": pri,
        "timeframes": out,
        "overlay": {
            "ema20": f.get("ema20"), "ema50": f.get("ema50"), "ema200": f.get("ema200"),
            "support": [z["price"] for z in (f.get("support") or [])],
            "resistance": [z["price"] for z in (f.get("resistance") or [])],
            "entryZone": th.get("entry_zone"),
            "stopLoss": th.get("invalidation"),
            "targets": th.get("targets") or [],
            "action": th.get("action"),
            "positions": [{"entry": p["entry"], "stopLoss": p["stopLoss"],
                           "targets": p.get("targets") or [], "side": p["side"]} for p in pos],
        },
    })


@app.get("/api/events")
async def events(since: int = 0) -> JSONResponse:
    return JSONResponse({"events": bus.since(since)})


@app.get("/api/stream")
async def stream(request: Request) -> StreamingResponse:
    """SSE: sự kiện thời gian thực + nhịp trạng thái mỗi 3 giây."""
    q = bus.subscribe()

    async def gen():
        try:
            for ev in bus.since(max(0, (bus.ring[-1]["seq"] if bus.ring else 0) - 60)):
                yield f"event: bus\ndata: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n"
            last_state = 0.0
            while True:
                if await request.is_disconnected():
                    break
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=1.0)
                    yield f"event: bus\ndata: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n"
                except asyncio.TimeoutError:
                    pass
                now = asyncio.get_event_loop().time()
                if now - last_state > 3.0:
                    last_state = now
                    snap = json.dumps(runtime.snapshot(), ensure_ascii=False, default=str)
                    yield f"event: state\ndata: {snap}\n\n"
        finally:
            bus.unsubscribe(q)

    return StreamingResponse(gen(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no",
    })


# ── API ghi ───────────────────────────────────────────────────────────────
@app.post("/api/control")
async def control(request: Request) -> JSONResponse:
    body = await request.json()
    return JSONResponse(runtime.control(body.get("action", "")))


@app.post("/api/chat")
async def chat(request: Request) -> StreamingResponse:
    body = await request.json()
    messages = body.get("messages") or []
    brain = await get_brain()

    snap = runtime.snapshot()
    context = {
        "symbol": snap["symbol"],
        "price": snap["price"],
        "dataSource": snap["dataSource"],
        "regime": snap["regime"],
        "marketState": snap["marketState"],
        "latestThesis": snap["thesis"],
        "latestRiskDecision": snap["decision"],
        "account": {k: snap["account"].get(k) for k in
                    ("equity", "equityMarked", "openPnl", "todayPnl", "drawdownPct", "positions", "closedCount")},
        "riskLimits": snap["risk"]["limits"],
        "riskBreakers": snap["risk"]["breakers"],
        "performance": performance(),
        "recentLessons": recent_lessons(8),
    }

    async def gen():
        async for chunk in brain.chat(messages, context):
            yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
        yield "data: {\"done\":true}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache", "X-Accel-Buffering": "no",
    })


@app.get("/api/skills")
async def skills() -> JSONResponse:
    """Kho kỹ năng — đọc thẳng từ đĩa, không cache.

    Kỹ năng nằm ngoài code để sửa được mà không phải deploy lại. Hiện chúng ra
    đây để thấy bộ não đang được dạy đúng những gì mình nghĩ mình đã dạy — chứ
    không phải một con số "11 kỹ năng" không ai kiểm được.
    """
    from .config import SKILLS_DIR

    out = []
    if SKILLS_DIR.exists():
        for d in sorted(SKILLS_DIR.iterdir()):
            f = d / "SKILL.md" if d.is_dir() else d
            if f.suffix != ".md" or not f.exists():
                continue
            txt = f.read_text(encoding="utf-8")
            dong = [l for l in txt.splitlines() if l.strip()]
            tieu = next((l.lstrip("# ").strip() for l in dong if l.startswith("#")), f.stem)
            mo = next((l.strip() for l in dong if not l.startswith("#")), "")
            out.append({
                "ma": d.name if d.is_dir() else f.stem,
                "tieuDe": tieu,
                "moTa": mo[:220],
                "soDong": len(txt.splitlines()),
                "soKyTu": len(txt),
            })
    return JSONResponse({"skills": out, "tong": len(out)})


@app.get("/api/hoc")
async def hoc_trang_thai() -> JSONResponse:
    """Trạng thái phòng huấn luyện + kết quả lượt gần nhất."""
    return JSONResponse({**phien_hoc.trang_thai(), "sanSang": phien_hoc.san_sang()})


@app.post("/api/hoc")
async def hoc_chay(req: Request) -> JSONResponse:
    """Khởi động một phiên huấn luyện. Trả về ngay, tiến độ xem ở GET.

    Không chờ ở đây: lượt đọc lịch sử đầu tiên mất khoảng sáu phút, quá lâu cho
    một request HTTP. Trả ngay rồi để giao diện hỏi tiến độ.
    """
    body = await req.json()
    viec = body.get("viec", "chay-lai")
    if viec not in ("chay-lai", "quet"):
        return JSONResponse({"ok": False, "vi_sao": f"việc lạ: {viec}"}, status_code=400)
    return JSONResponse(phien_hoc.bat_dau(viec, body))


@app.get("/api/the-gioi")
async def the_gioi() -> JSONResponse:
    """Nguồn dữ liệu ngoài: phái sinh, vĩ mô, tâm lý, tin tức.

    Đọc thẳng kho mà luồng nền đã đặt sẵn — không chạm mạng trong request này,
    nên mở dashboard không bao giờ phải chờ Yahoo.
    """
    return JSONResponse(nguon.kho())


@app.get("/api/tu-chay")
async def tu_chay_xem() -> JSONResponse:
    """Tự chạy lúc đăng nhập đang bật hay tắt."""
    return JSONResponse(tu_chay.trang_thai())


@app.post("/api/tu-chay")
async def tu_chay_dat(req: Request) -> JSONResponse:
    """Bật/tắt tự chạy lúc đăng nhập.

    Để trong app chứ không chỉ để trong script cài đặt, vì đây là quyết định
    theo TỪNG MÁY: máy nhiều người dùng chung thì tắt, máy riêng hoặc VPS thì
    bật. Bắt người ta mở terminal để đổi một lựa chọn như vậy là bắt sai chỗ.
    """
    body = await req.json()
    return JSONResponse(tu_chay.dat(bool(body.get("bat"))))


@app.post("/api/dung-han")
async def dung_han() -> JSONResponse:
    """Dừng hẳn runtime — đặt cờ rồi tự thoát.

    Đặt cờ TRƯỚC khi thoát: bộ giám sát thấy tiến trình con chết thì mặc định
    dựng lại (đó là việc của nó), nên không có cờ thì nút này chỉ làm runtime
    nhấp nháy rồi quay lại.

    Thoát bằng một luồng riêng sau một nhịp ngắn, để phản hồi HTTP kịp đi ra.
    Thoát ngay trong handler thì trình duyệt nhận lỗi kết nối và người dùng
    không biết là đã dừng thành công hay chưa.
    """
    import threading

    tu_chay.xin_dung()

    def _thoat() -> None:
        time.sleep(0.6)
        os._exit(0)

    threading.Thread(target=_thoat, daemon=True).start()
    return JSONResponse({"ok": True, "noi": "đang dừng — bộ giám sát sẽ không dựng lại"})


@app.get("/api/config")
async def cfg() -> JSONResponse:
    return JSONResponse(CONFIG)
