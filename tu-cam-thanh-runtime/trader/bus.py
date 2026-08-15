"""Bus sự kiện — thứ làm cho hệ thống QUAN SÁT ĐƯỢC.

Mỗi mắt xích trong sơ đồ dữ liệu phát một sự kiện có `stage`; web app chỉ việc
nghe và tô sáng đúng ô trong sơ đồ. Không tầng nào gọi thẳng vào UI.
"""
from __future__ import annotations

import asyncio
import datetime as _dt
import itertools
from typing import Any

RING = 800

STAGES = (
    "data",      # MARKET DATA ENGINE
    "features",  # FEATURE FACTORY
    "regime",    # MARKET STATE / REGIME
    "brain",     # CLAUDE BRAIN
    "risk",      # RISK ENGINE
    "exec",      # EXECUTION
    "journal",   # TRADE JOURNAL
    "memory",    # POST-MORTEM / LESSON MEMORY
    "system",    # vòng lặp, lỗi, điều khiển
)


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


class Bus:
    def __init__(self) -> None:
        self._seq = itertools.count(1)
        self.ring: list[dict[str, Any]] = []
        self._queues: set[asyncio.Queue] = set()

    def emit(self, stage: str, type: str, msg: str = "", **payload: Any) -> dict:
        ev = {"seq": next(self._seq), "ts": _now(), "stage": stage, "type": type, "msg": msg, **payload}
        self.ring.append(ev)
        if len(self.ring) > RING:
            del self.ring[: len(self.ring) - RING]
        for q in list(self._queues):
            try:
                q.put_nowait(ev)
            except asyncio.QueueFull:
                # Client chậm không được kéo tụt vòng lặp giao dịch.
                pass
        return ev

    def log(self, stage: str, type: str, msg: str = "", **payload: Any) -> dict:
        print(f"[{_now()[11:19]}] {stage:<8} {type:<20} {msg}", flush=True)
        return self.emit(stage, type, msg, **payload)

    def since(self, seq: int = 0) -> list[dict]:
        return [e for e in self.ring if e["seq"] > seq]

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=500)
        self._queues.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._queues.discard(q)


bus = Bus()
