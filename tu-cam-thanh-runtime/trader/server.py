"""HTTP + SSE — dashboard quan sát và khung chat.

Web app là client thuần: nó không tính toán gì, chỉ hiển thị những gì runtime
phát ra qua bus. Nhờ vậy đóng trình duyệt không ảnh hưởng gì tới giao dịch, và
mở hai tab cũng không nhân đôi thứ gì.
"""
from __future__ import annotations

import asyncio
import contextlib
import json

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from .brain import get_brain
from .bus import bus
from .config import CONFIG, WEB_DIR
from .journal import performance, recent_lessons, recent_theses, recent_trades
from .loop import runtime

app = FastAPI(title="Claude Trader — M0", docs_url=None, redoc_url=None)


@app.on_event("startup")
async def _startup() -> None:
    app.state.loop_task = asyncio.create_task(runtime.run())


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


@app.get("/api/config")
async def cfg() -> JSONResponse:
    return JSONResponse(CONFIG)
