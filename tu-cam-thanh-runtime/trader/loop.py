"""Vòng lặp điều phối — cỗ máy tuần hoàn của M0.

    THẾ GIỚI → MARKET DATA → FEATURES → MARKET STATE/REGIME
             → CLAUDE BRAIN (+ MEMORY + SKILLS) → TRADE THESIS
             → RISK ENGINE → chấp nhận/từ chối → EXECUTION
             → RESULT → JOURNAL → POST-MORTEM → LESSON → MEMORY ↺

Điểm cần nhớ khi đọc: brain KHÔNG được gọi mỗi vòng lặp. Vòng lặp chạy mỗi ~20
giây để theo dõi vị thế và cập nhật dashboard, nhưng brain chỉ được đánh thức khi
có nến mới đóng / regime đổi / người dùng bấm tay, và luôn phải qua cửa hạn mức
chi phí. Gọi model mỗi vòng lặp là cách hết tiền nhanh nhất mà không thu được gì —
giữa hai nến 1H thì trạng thái thị trường gần như không đổi.
"""
from __future__ import annotations

import asyncio
import datetime as _dt
import traceback

import httpx

from .brain import get_brain
from .broker import PaperBroker
from .bus import bus
from .config import CONFIG
from .data import get_market_data, data_source
from .features import build_market_state
from .journal import recall
from .regime import classify
from .risk import RiskEngine
from . import snapshot


class Runtime:
    def __init__(self) -> None:
        self.cfg = CONFIG
        self.primary = CONFIG["timeframes"]["primary"]
        self.context = CONFIG["timeframes"]["context"]
        self.broker = PaperBroker(CONFIG["risk"])
        self.risk = RiskEngine(CONFIG["risk"])
        self.brain = None

        self.state: dict | None = None
        self.regime: dict | None = None
        self.last_thesis: dict | None = None
        self.last_decision: dict | None = None

        self.paused = False
        self.force_analyze = False
        self.last_thesis_at: _dt.datetime | None = None
        self.last_candle_seen: int | None = None
        self.last_regime_key: str | None = None
        self.ticks = 0
        self.started_at = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")

    # ── Điều khiển từ dashboard ───────────────────────────────────────────
    def control(self, action: str) -> dict:
        if action == "pause":
            self.paused = True
            bus.log("system", "tam-dung", "vòng lặp tạm dừng — vị thế đang mở vẫn được theo dõi")
        elif action == "resume":
            self.paused = False
            bus.log("system", "chay-lai", "vòng lặp chạy lại")
        elif action == "analyze":
            self.force_analyze = True
            bus.log("system", "phan-tich-tay", "yêu cầu brain phân tích ngay ở vòng kế tiếp")
        elif action == "kill":
            self.risk.halted_reason = "kill switch bấm tay"
            bus.log("system", "kill-switch", "KILL SWITCH — không mở lệnh mới cho tới khi khởi động lại")
        elif action == "unkill":
            self.risk.halted_reason = None
            bus.log("system", "kill-switch-off", "gỡ kill switch")
        elif action == "reset":
            self.broker.reset()
            self.risk.halted_reason = None
        else:
            return {"ok": False, "error": f"hành động không rõ: {action}"}
        return {"ok": True, "action": action}

    # ── Quyết định CÓ gọi brain hay không ─────────────────────────────────
    def _should_call_brain(self, market: dict) -> tuple[bool, str]:
        if self.paused:
            return False, "đang tạm dừng"
        if self.force_analyze:
            return True, "người dùng bấm phân tích"

        blockers = self.risk.circuit_breakers(self.broker.snapshot(market["price"]))
        if blockers:
            return False, blockers[0]

        now = _dt.datetime.now(_dt.timezone.utc)
        if self.last_thesis_at:
            waited = (now - self.last_thesis_at).total_seconds()
            if waited < self.cfg["brain"]["minSecondsBetweenTheses"]:
                return False, f"mới phân tích {int(waited)}s trước"

        new_candle = market["lastClosedCandleTime"] != self.last_candle_seen
        regime_changed = self.regime and self.regime["key"] != self.last_regime_key

        if self.cfg["brain"]["requireNewCandle"] and not new_candle and not regime_changed:
            return False, f"chưa có nến {self.primary} mới đóng"
        if self.regime and self.regime["quality"] == "LOW" and not regime_changed:
            return False, f"regime chất lượng thấp ({self.regime['primary']}) — không đáng gọi"
        return True, "nến mới đóng" if new_candle else "regime đổi"

    # ── Một vòng ──────────────────────────────────────────────────────────
    async def tick(self, client: httpx.AsyncClient) -> None:
        self.ticks += 1

        market = await get_market_data(client)
        self.state = build_market_state(market)
        bus.emit("features", "tinh-xong",
                 f"{len(self.state['timeframes'])} khung · RSI {self.state['timeframes'][self.primary].get('rsi14')} · "
                 f"ADX {self.state['timeframes'][self.primary].get('adx')} · ATR% {self.state['timeframes'][self.primary].get('atrPct')}")

        prev_key = self.regime["key"] if self.regime else None
        self.regime = classify(self.state, self.primary, self.context)
        if self.regime["key"] != prev_key:
            bus.log("regime", "doi-regime",
                    f"{prev_key or '—'} → {self.regime['key']} ({self.regime['quality']}) · " + "; ".join(self.regime["reasons"][:2]),
                    regime=self.regime)
        else:
            bus.emit("regime", "giu-nguyen", f"{self.regime['primary']} · chất lượng {self.regime['quality']}", regime=self.regime)

        # Vị thế đang mở được kiểm TRƯỚC khi nghĩ tới lệnh mới. Thoát lệnh không
        # bao giờ được xếp sau việc vào lệnh.
        closed = self.broker.mark(market["price"])
        for t in closed:
            bus.emit("journal", "ghi-so", f"đã ghi giao dịch {t['id']} vào nhật ký", trade=t)
            try:
                lesson = await self.brain.postmortem(t, self.regime)
                bus.emit("memory", "luu-tri-nho", f"bài học lưu cho regime {t.get('regimeAtEntry')}", lesson=lesson)
            except Exception as e:  # noqa: BLE001 — hậu kiểm hỏng không được làm chết vòng lặp
                bus.log("memory", "hau-kiem-loi", f"{type(e).__name__}: {e}")

        ok, why = self._should_call_brain(market)
        if not ok:
            bus.emit("brain", "bo-qua", f"không gọi brain: {why}")
            return

        self.force_analyze = False
        self.last_thesis_at = _dt.datetime.now(_dt.timezone.utc)
        self.last_candle_seen = market["lastClosedCandleTime"]
        self.last_regime_key = self.regime["key"]

        account = self.broker.snapshot(market["price"])
        memory = recall(self.regime["key"], self.regime["primary"])
        bus.emit("memory", "truy-hoi",
                 f"{len(memory['lessonsForThisRegime'])} bài học liên quan · "
                 f"lịch sử regime này: {memory['performanceThisRegime'].get('count', 0)} lệnh")

        bus.emit("brain", "dang-nghi", f"gọi brain ({why})…")
        thesis = await self.brain.thesis(self.state, self.regime, memory, account, self.primary)
        self.last_thesis = thesis

        atr = self.state["timeframes"][self.primary]["_raw"]["atr"]
        decision = self.risk.evaluate(thesis, self.state, account, atr)
        self.last_decision = decision

        if decision["approved"]:
            bus.log("risk", "chap-nhan",
                    f"cho qua · RR {decision['rr']:.2f} · risk ${decision['position']['riskAmount']} "
                    f"({decision['position']['riskPct']}%) · {decision['note']}",
                    decision=decision)
            self.broker.open(decision["position"], thesis, self.regime)
        elif thesis["action"] == "NO_TRADE":
            bus.emit("risk", "khong-vao-lenh", "brain chọn NO_TRADE — đây là một quyết định, không phải bỏ lỡ",
                     decision=decision)
        else:
            bus.log("risk", "tu-choi",
                    f"CHẶN {thesis['action']}: " + " | ".join(decision["rejections"]),
                    decision=decision)

    async def run(self) -> None:
        self.brain = await get_brain()
        bus.log("system", "khoi-dong",
                f"{self.cfg['symbol']} · {self.primary}+{self.context} · vòng {self.cfg['loopSeconds']}s · "
                f"vốn ${self.cfg['risk']['startingEquity']:,} · brain {self.brain.mode}")
        async with httpx.AsyncClient(headers={"accept": "application/json"}) as client:
            while True:
                try:
                    await self.tick(client)
                except Exception as e:  # noqa: BLE001 — một vòng hỏng không được giết runtime
                    bus.log("system", "loi-vong-lap", f"{type(e).__name__}: {e}")
                    traceback.print_exc()

                # Ghi lát cắt cho cung tĩnh sau MỌI vòng, kể cả vòng hỏng và vòng
                # thoát sớm. Đặt ở đây chứ không trong tick() vì tick() có nhiều
                # nhánh `return` — đặt trong đó là chắc chắn sót một nhánh, và
                # nhánh bị sót thì trang tĩnh đứng im mà không có gì báo.
                try:
                    snapshot.write(self)
                except Exception as e:  # noqa: BLE001
                    bus.log("system", "snapshot-loi", f"{type(e).__name__}: {e}")

                await asyncio.sleep(self.cfg["loopSeconds"])

    # ── Ảnh chụp cho dashboard ────────────────────────────────────────────
    def snapshot(self) -> dict:
        price = self.state["price"] if self.state else None
        acct = self.broker.snapshot(price)
        return {
            "startedAt": self.started_at,
            "ticks": self.ticks,
            "paused": self.paused,
            "symbol": self.cfg["symbol"],
            "timeframes": {"primary": self.primary, "context": self.context},
            "price": price,
            "dataSource": data_source(),
            "marketState": self.state,
            "regime": self.regime,
            "thesis": self.last_thesis,
            "decision": self.last_decision,
            "account": acct,
            "risk": {
                "halted": self.risk.halted_reason,
                "breakers": self.risk.circuit_breakers(acct),
                "limits": self.cfg["risk"],
            },
            "brain": self.brain.status() if self.brain else {"mode": "chưa khởi động"},
            "nextThesisIn": self._next_in(),
        }

    def _next_in(self) -> int | None:
        if not self.last_thesis_at:
            return 0
        elapsed = (_dt.datetime.now(_dt.timezone.utc) - self.last_thesis_at).total_seconds()
        return max(0, int(self.cfg["brain"]["minSecondsBetweenTheses"] - elapsed))


runtime = Runtime()
