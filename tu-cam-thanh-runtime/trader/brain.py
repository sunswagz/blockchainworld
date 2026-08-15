"""CLAUDE BRAIN — tầng suy luận.

Ba điều file này cố tình làm khác một "bot hỏi AI mua hay bán":

1. **Không dự đoán giá.** Đầu ra là kịch bản kèm xác suất + một hành động, trong
   đó NO_TRADE là một quyết định hợp lệ và được khen như mọi quyết định khác.
2. **Đầu ra có schema.** Structured outputs ép JSON đúng khuôn, nên Risk Engine
   ở dưới đọc được bằng máy chứ không phải parse văn xuôi.
3. **Có đồng hồ tiền.** Mỗi lượt gọi được đo token và quy ra USD; quá hạn mức
   ngày là brain tự tắt, vòng lặp vẫn chạy tiếp ở chế độ NO_TRADE.

Điều thứ ba không phải chi tiết kỹ thuật. Một đường ống gọi model theo lịch mà
không có trần chi phí thì chuyện duy nhất chưa xảy ra là hoá đơn chưa về.
"""
from __future__ import annotations

import asyncio
import datetime as _dt
import json
from typing import Any, AsyncIterator

from .bus import bus
from .config import CONFIG, SKILLS_DIR, brain_mode
from . import store
from .regime import REGIMES

# ── Giá niêm yết, USD trên 1 triệu token ──────────────────────────────────
PRICES = {
    "claude-opus-5":    {"in": 5.00, "out": 25.00},
    "claude-opus-4-8":  {"in": 5.00, "out": 25.00},
    "claude-fable-5":   {"in": 10.00, "out": 50.00},
    "claude-sonnet-5":  {"in": 3.00, "out": 15.00},
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
}
DEFAULT_PRICE = {"in": 5.00, "out": 25.00}


def _utc_day() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


# ── Schema đầu ra ─────────────────────────────────────────────────────────
_SCENARIO = {
    "type": "object", "additionalProperties": False,
    "required": ["name", "probability", "description"],
    "properties": {
        "name": {"type": "string"},
        "probability": {"type": "number"},
        "description": {"type": "string"},
    },
}

THESIS_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": [
        "regime_read", "market_summary", "scenarios", "action", "confidence",
        "entry_zone", "invalidation", "invalidation_logic", "targets",
        "suggested_risk_pct", "strategy", "reason_codes", "reasoning", "event_risk",
    ],
    "properties": {
        "regime_read": {"type": "string", "enum": REGIMES},
        "market_summary": {"type": "string"},
        "scenarios": {"type": "array", "items": _SCENARIO},
        "action": {"type": "string", "enum": ["LONG", "SHORT", "NO_TRADE"]},
        "confidence": {"type": "number"},
        "entry_zone": {"anyOf": [{"type": "array", "items": {"type": "number"}}, {"type": "null"}]},
        "invalidation": {"anyOf": [{"type": "number"}, {"type": "null"}]},
        "invalidation_logic": {"type": "string"},
        "targets": {"type": "array", "items": {"type": "number"}},
        "suggested_risk_pct": {"type": "number"},
        "strategy": {"type": "string"},
        "reason_codes": {"type": "array", "items": {"type": "string"}},
        "reasoning": {"type": "string"},
        "event_risk": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "UNKNOWN"]},
    },
}

POSTMORTEM_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": [
        "regime_appropriate", "entry_valid", "size_valid", "stop_placement_valid",
        "thesis_was_wrong", "classification", "lesson", "change_strategy", "confidence_in_lesson",
    ],
    "properties": {
        "regime_appropriate": {"type": "boolean"},
        "entry_valid": {"type": "boolean"},
        "size_valid": {"type": "boolean"},
        "stop_placement_valid": {"type": "boolean"},
        "thesis_was_wrong": {"type": "boolean"},
        "classification": {"type": "string", "enum": [
            "GOOD_TRADE_GOOD_OUTCOME", "GOOD_TRADE_BAD_OUTCOME",
            "BAD_TRADE_GOOD_OUTCOME", "BAD_TRADE_BAD_OUTCOME",
        ]},
        "lesson": {"type": "string"},
        "change_strategy": {"type": "boolean"},
        "confidence_in_lesson": {"type": "number"},
    },
}


# ── Đồng hồ chi phí ───────────────────────────────────────────────────────
class CostMeter:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.state = store.read_json(store.COST) or {}

    def _day(self) -> dict:
        d = _utc_day()
        self.state.setdefault(d, {"usd": 0.0, "calls": 0, "inputTokens": 0,
                                  "outputTokens": 0, "cacheReadTokens": 0, "cacheWriteTokens": 0})
        return self.state[d]

    def record(self, model: str, usage: Any) -> float:
        p = PRICES.get(model, DEFAULT_PRICE)
        i = getattr(usage, "input_tokens", 0) or 0
        o = getattr(usage, "output_tokens", 0) or 0
        cw = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cr = getattr(usage, "cache_read_input_tokens", 0) or 0
        usd = (i * p["in"] + cw * p["in"] * 1.25 + cr * p["in"] * 0.1 + o * p["out"]) / 1_000_000
        d = self._day()
        d["usd"] = round(d["usd"] + usd, 6)
        d["calls"] += 1
        d["inputTokens"] += i
        d["outputTokens"] += o
        d["cacheReadTokens"] += cr
        d["cacheWriteTokens"] += cw
        store.write_json(store.COST, self.state)
        return usd

    def today(self) -> dict:
        return dict(self._day())

    def blocked(self) -> str | None:
        d = self._day()
        if d["usd"] >= self.cfg["dailyBudgetUsd"]:
            return f"đã tiêu ${d['usd']:.2f} ≥ hạn mức ${self.cfg['dailyBudgetUsd']}/ngày"
        if d["calls"] >= self.cfg["maxCallsPerDay"]:
            return f"đã gọi {d['calls']} lượt ≥ trần {self.cfg['maxCallsPerDay']}/ngày"
        return None


# ── Kỹ năng (skills) ──────────────────────────────────────────────────────
def load_skills() -> str:
    """Nạp mọi SKILL.md. Kho kỹ năng nằm ngoài code để sửa được mà không phải
    deploy lại — và để đọc git log của nó là thấy bot đã học thêm những gì."""
    parts: list[str] = []
    if SKILLS_DIR.exists():
        for d in sorted(SKILLS_DIR.iterdir()):
            f = d / "SKILL.md" if d.is_dir() else d
            if f.suffix == ".md" and f.exists():
                parts.append(f.read_text(encoding="utf-8").strip())
    return "\n\n---\n\n".join(parts)


SYSTEM_RULES = """Bạn là tầng suy luận của một AI Trading Runtime. Bạn KHÔNG cầm chìa khoá két.

Bạn được phép: đọc trạng thái thị trường, phân loại chế độ thị trường, dựng kịch bản
kèm xác suất, đề xuất hành động, đề xuất điểm vô hiệu hoá và mục tiêu, giải thích.

Bạn KHÔNG được phép và cũng không có cách nào để: bỏ stop loss, tăng size, tăng đòn bẩy,
gấp thếp, hay vượt giới hạn rủi ro. Bên dưới bạn là một Risk Engine viết bằng Python
thuần; nó tính lại size từ đầu và có quyền từ chối. `confidence` cao không mua được
thêm rủi ro — nó chỉ dùng để loại bỏ, không dùng để nới.

Cách làm việc bắt buộc:

1. TRẢ LỜI "THỊ TRƯỜNG ĐANG LÀ GÌ" TRƯỚC. Không nhảy sang mua/bán khi chưa phân loại
   được chế độ thị trường. Bạn được phép nói regime do bộ phân loại đưa vào là sai.
2. SUY LUẬN THEO XÁC SUẤT, không dự đoán một mức giá. Luôn đưa ít nhất 2 kịch bản
   và tổng xác suất xấp xỉ 1.0.
3. NO_TRADE LÀ QUYẾT ĐỊNH ĐÚNG khi risk/reward không đủ, khi các khung thời gian
   mâu thuẫn, hoặc khi bạn không đọc được thị trường. Nhiệm vụ của bạn không phải
   là giao dịch liên tục. Phần lớn thời gian, không có setup nào đáng vào.
4. STOP LOSS ĐẶT Ở CHỖ LUẬN ĐIỂM SAI, không phải ở một tỉ lệ phần trăm máy móc.
   Hỏi: "giá tới đâu thì tôi biết mình đã đọc sai?" — đó mới là điểm vô hiệu hoá.
   Trường `invalidation_logic` phải nói rõ cấu trúc nào bị phá.
5. MỤC TIÊU ĐẦU TIÊN QUYẾT ĐỊNH RR. Đừng đặt TP1 xa để RR đẹp trên giấy; Risk Engine
   tính RR trên TP1 và sẽ từ chối nếu dưới ngưỡng.
6. DÙNG BÀI HỌC ĐƯỢC ĐƯA VÀO. Nếu có bài học liên quan tới regime hiện tại, nói rõ
   bạn áp dụng hay bỏ qua và vì sao.

Khi vào lệnh: `suggested_risk_pct` là đề xuất, sẽ bị cắt trần. `targets` xếp từ gần
tới xa. `reason_codes` là các nhãn ngắn dạng SNAKE_CASE để thống kê sau này."""


def _fmt_state(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


# ── Bộ não giả lập, không tốn tiền ────────────────────────────────────────
def mock_thesis(state: dict, regime: dict, primary_tf: str) -> dict:
    """Suy luận bằng luật để vòng lặp chạy kín khi không có API key.

    Cố ý bảo thủ: chỉ vào lệnh thuận xu hướng rõ, còn lại NO_TRADE. Nó không phải
    "phiên bản rẻ của Claude" — nó là mức sàn để so sánh. Brain thật mà không
    thắng nổi cái này thì đó là thông tin đáng giá.
    """
    p = state["timeframes"][primary_tf]
    price = p["price"]
    atr = p["_raw"]["atr"] or price * 0.01
    prim = regime["primary"]
    conflict = "MTF_CONFLICT" in regime["flags"]

    base = {
        "regime_read": prim,
        "market_summary": f"[mock] {prim}, ADX {p.get('adx')}, RSI {p.get('rsi14')}, EMA {p.get('emaStack')}",
        "scenarios": [
            {"name": "tiếp diễn", "probability": 0.4, "description": "giữ hướng hiện tại"},
            {"name": "quét thanh khoản rồi hồi", "probability": 0.35, "description": "thủng biên rồi lấy lại"},
            {"name": "đảo chiều", "probability": 0.25, "description": "mất cấu trúc"},
        ],
        "action": "NO_TRADE",
        "confidence": 0.4,
        "entry_zone": None, "invalidation": None,
        "invalidation_logic": "không vào lệnh nên không có điểm vô hiệu hoá",
        "targets": [], "suggested_risk_pct": 0.0,
        "strategy": "MOCK_RULES_V1",
        "reason_codes": ["MOCK_BRAIN"],
        "reasoning": "Bộ não giả lập: chỉ vào lệnh khi xu hướng rõ và các khung không mâu thuẫn.",
        "event_risk": "UNKNOWN",
    }
    if conflict or prim not in ("TREND_UP", "TREND_DOWN"):
        base["reason_codes"].append("MTF_CONFLICT" if conflict else "NO_CLEAR_TREND")
        return base

    # SL 1.5×ATR; TP1 SUY RA chứ không ghi cứng.
    #
    # Risk Engine thẩm định RR trên giá khớp dự kiến, mà chi phí (phí + trượt) tính
    # theo % GIÁ còn stop tính theo ATR. Nên bội số ATR cần cho TP1 phụ thuộc tỉ lệ
    # ATR/giá: biến động càng thấp, cùng 15bps ấy càng ăn nhiều RR. Ghi cứng "5×ATR"
    # thì hôm nay qua cửa, hôm sau ATR% tụt là bị chặn mà không đổi dòng code nào.
    #
    #     (k·ATR − drag) / (1.5·ATR + drag) ≥ minRR
    #   ⇒ k ≥ [ minRR·(1.5·ATR + drag) + drag ] / ATR
    r = CONFIG["risk"]
    drag = price * (r["feeBps"] + r["slippageBps"]) / 10_000
    stop_that = 1.5 * atr + drag
    k1 = (r["minRR"] * stop_that + drag) / atr * 1.05   # +5% đệm, đừng nằm sát mép
    k2 = k1 * 1.6

    long = prim == "TREND_UP"
    stop = price - 1.5 * atr if long else price + 1.5 * atr
    tp1 = price + k1 * atr if long else price - k1 * atr
    tp2 = price + k2 * atr if long else price - k2 * atr
    base.update({
        "action": "LONG" if long else "SHORT",
        "confidence": 0.6,
        "entry_zone": [round(price * 0.999, 2), round(price * 1.001, 2)],
        "invalidation": round(stop, 2),
        "invalidation_logic": "1.5×ATR ngược hướng — mất vùng này là hết xu hướng ngắn hạn",
        "targets": [round(tp1, 2), round(tp2, 2)],
        "suggested_risk_pct": 0.5,
        "reason_codes": ["MOCK_BRAIN", "TREND_ALIGNED", "ADX_CONFIRMS"],
        "reasoning": f"[mock] Thuận {prim} với ADX {p.get('adx')}. SL 1.5×ATR, TP1 {k1:.1f}×ATR — "
                     f"bội số này suy từ ATR/giá hiện tại ({atr / price * 100:.3f}%) để RR còn "
                     f"≥{r['minRR']} sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
    })
    return base


def mock_postmortem(trade: dict) -> dict:
    win = (trade.get("pnl") or 0) > 0
    normal_loss = trade.get("exitReason") == "STOP_LOSS"
    return {
        "regime_appropriate": True, "entry_valid": True, "size_valid": True,
        "stop_placement_valid": True,
        "thesis_was_wrong": bool(normal_loss and not win),
        "classification": "GOOD_TRADE_GOOD_OUTCOME" if win else "GOOD_TRADE_BAD_OUTCOME",
        "lesson": ("[mock] Lệnh chạy tới mục tiêu; setup và cách thoát giữ nguyên."
                   if win else
                   "[mock] Dính stop trong biên độ thống kê bình thường. Một lệnh thua "
                   "không đồng nghĩa một quyết định sai — chưa đủ cớ để đổi chiến lược."),
        "change_strategy": False,
        "confidence_in_lesson": 0.3,
    }


# ── Bộ não thật ───────────────────────────────────────────────────────────
class Brain:
    def __init__(self) -> None:
        self.cfg = CONFIG["brain"]
        self.mode = brain_mode()
        self.cost = CostMeter(self.cfg)
        self.skills = load_skills()
        self.client = None
        self.last_error: str | None = None
        if self.mode == "claude":
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic()
            except Exception as e:  # noqa: BLE001
                self.mode = "mock"
                self.last_error = f"không khởi tạo được SDK: {e}"
                bus.log("brain", "sdk-loi", self.last_error)
        bus.log("brain", "che-do", f"brain = {self.mode.upper()}"
                + ("" if self.mode == "claude" else " (không gọi API, không tốn tiền)"))

    # System prompt là phần ỔN ĐỊNH của mọi lượt gọi, nên nó được cache. Đặt
    # dữ liệu biến thiên (giá, feature) vào message chứ không vào đây — nhét
    # timestamp vào system prompt là tự huỷ cache mà không có gì báo.
    def _system(self) -> list[dict]:
        text = SYSTEM_RULES + ("\n\n# KHO KỸ NĂNG\n\n" + self.skills if self.skills else "")
        return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]

    def status(self) -> dict:
        return {
            "mode": self.mode,
            "model": self.cfg["model"],
            "today": self.cost.today(),
            "budgetUsd": self.cfg["dailyBudgetUsd"],
            "maxCalls": self.cfg["maxCallsPerDay"],
            "blocked": self.cost.blocked(),
            "lastError": self.last_error,
            "skillsLoaded": len(self.skills.split("---")) if self.skills else 0,
        }

    async def _structured(self, *, user: str, schema: dict, effort: str, label: str) -> dict | None:
        """Một lượt gọi có schema. Trả về None nếu bị chặn/lỗi/từ chối."""
        blocked = self.cost.blocked()
        if blocked:
            bus.log("brain", "het-han-muc", f"bỏ qua {label}: {blocked}")
            return None
        try:
            resp = await self.client.messages.create(
                model=self.cfg["model"],
                max_tokens=self.cfg.get("maxTokens", 16000),
                system=self._system(),
                thinking={"type": "adaptive"},
                output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
                messages=[{"role": "user", "content": user}],
            )
        except Exception as e:  # noqa: BLE001
            self.last_error = f"{type(e).__name__}: {e}"
            bus.log("brain", "loi-api", f"{label}: {self.last_error}")
            return None

        usd = self.cost.record(self.cfg["model"], resp.usage)

        # Kiểm stop_reason TRƯỚC khi đọc content — khi bị từ chối, content rỗng
        # và mọi code đọc content[0] sẽ nổ ở đúng lúc tệ nhất.
        if resp.stop_reason == "refusal":
            cat = getattr(getattr(resp, "stop_details", None), "category", None)
            self.last_error = f"model từ chối (category={cat})"
            bus.log("brain", "tu-choi", f"{label}: {self.last_error}")
            return None

        text = next((b.text for b in resp.content if b.type == "text"), None)
        if not text:
            bus.log("brain", "rong", f"{label}: không có khối text trong phản hồi")
            return None
        try:
            out = json.loads(text)
        except json.JSONDecodeError as e:
            bus.log("brain", "json-hong", f"{label}: {e}")
            return None

        bus.emit("brain", "chi-phi", f"{label}: ${usd:.4f} · vào {resp.usage.input_tokens} tok · "
                                     f"ra {resp.usage.output_tokens} tok · "
                                     f"cache đọc {getattr(resp.usage, 'cache_read_input_tokens', 0)}",
                 usd=usd, label=label)
        return out

    async def thesis(self, state: dict, regime: dict, memory: dict, account: dict, primary_tf: str) -> dict:
        payload = {
            "market_state": state,
            "regime_from_classifier": regime,
            "account": {
                "equity": account["equity"], "openPositions": len(account["positions"]),
                "todayPnl": account.get("todayPnl"), "drawdownPct": account.get("drawdownPct"),
            },
            "memory": memory,
            "hard_limits": {
                "max_risk_per_trade_pct": CONFIG["risk"]["maxRiskPerTradePct"],
                "min_rr": CONFIG["risk"]["minRR"],
                "min_confidence": CONFIG["risk"]["minConfidence"],
                "stop_must_be_between_atr": [CONFIG["risk"]["minStopAtr"], CONFIG["risk"]["maxStopAtr"]],
            },
        }
        user = ("Đây là trạng thái thị trường hiện tại. Phân loại chế độ thị trường trước, "
                "rồi mới quyết định. NO_TRADE là câu trả lời hợp lệ và thường là câu trả lời đúng.\n\n"
                + _fmt_state(payload))

        if self.mode != "claude" or not self.client:
            out = mock_thesis(state, regime, primary_tf)
        else:
            out = await self._structured(user=user, schema=THESIS_SCHEMA,
                                         effort=self.cfg.get("effort", "high"), label="thesis")
            if out is None:
                out = mock_thesis(state, regime, primary_tf)
                out["reason_codes"].append("FALLBACK_SAU_LOI_BRAIN")

        out["symbol"] = state["symbol"]
        out["source"] = "claude" if (self.mode == "claude" and "FALLBACK_SAU_LOI_BRAIN" not in out.get("reason_codes", [])) else "mock"
        out["regimeFromClassifier"] = regime["primary"]
        out["at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        store.append(store.THESES, out)
        bus.emit("brain", "luan-diem",
                 f"{out['action']} · tin cậy {out['confidence']:.2f} · đọc regime {out['regime_read']} · {out['strategy']}",
                 thesis=out)
        return out

    async def postmortem(self, trade: dict, regime_now: dict) -> dict:
        if self.mode != "claude" or not self.client:
            out = mock_postmortem(trade)
        else:
            user = (
                "Hậu kiểm giao dịch đã đóng dưới đây. Trả lời từng câu hỏi một cách độc lập.\n\n"
                "Điều quan trọng nhất: PHÂN BIỆT QUYẾT ĐỊNH VỚI KẾT QUẢ. Một lệnh thua theo "
                "đúng quy trình vẫn là quyết định tốt (GOOD_TRADE_BAD_OUTCOME) và KHÔNG được "
                "đổi chiến lược vì nó. Một lệnh thắng do vi phạm setup là quyết định tồi "
                "(BAD_TRADE_GOOD_OUTCOME) và phải ghi rõ là không được lặp lại. Học theo tiền "
                "lãi/lỗ thay vì theo chất lượng quyết định thì cuối cùng sẽ học ra cờ bạc.\n\n"
                "Chỉ đặt change_strategy = true khi có cớ lặp lại, không phải vì một lệnh.\n\n"
                + _fmt_state({"trade": trade, "regime_now": regime_now})
            )
            out = await self._structured(user=user, schema=POSTMORTEM_SCHEMA,
                                         effort=self.cfg.get("postmortemEffort", "medium"),
                                         label="postmortem")
            if out is None:
                out = mock_postmortem(trade)

        lesson = {
            "at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "tradeId": trade["id"], "symbol": trade.get("symbol"),
            "regime": trade.get("regimeAtEntry"), "regimeKey": trade.get("regimeKey"),
            "side": trade["side"], "pnl": trade.get("pnl"), "rMultiple": trade.get("rMultiple"),
            "exitReason": trade.get("exitReason"), "strategy": trade.get("strategy"),
            **out,
        }
        store.append(store.LESSONS, lesson)
        bus.log("memory", "bai-hoc",
                f"{out['classification']} · đổi chiến lược: {'CÓ' if out['change_strategy'] else 'KHÔNG'} · {out['lesson'][:110]}",
                lesson=lesson)
        return lesson

    async def chat(self, messages: list[dict], context: dict) -> AsyncIterator[str]:
        """Hỏi đáp với bộ não, có toàn bộ trạng thái hiện tại làm ngữ cảnh."""
        if self.mode != "claude" or not self.client:
            yield ("Brain đang ở chế độ **mock** nên không có mô hình để trả lời.\n\n"
                   "Đặt `ANTHROPIC_API_KEY` trong `.env` rồi khởi động lại là chat hoạt động. "
                   "Mọi tầng khác — dữ liệu, chỉ báo, regime, risk engine, sàn giấy, nhật ký — "
                   "vẫn đang chạy thật và bạn xem được ở các panel bên phải.")
            return
        blocked = self.cost.blocked()
        if blocked:
            yield f"Hết hạn mức chi phí hôm nay ({blocked}). Sửa `brain.dailyBudgetUsd` trong `config.json` nếu muốn nới."
            return

        sys_blocks = self._system()
        sys_blocks.append({
            "type": "text",
            "text": ("\n\n# NGỮ CẢNH VẬN HÀNH\n\nBạn đang trả lời người vận hành runtime này qua "
                     "dashboard. Trạng thái hiện tại kèm dưới đây. Trả lời ngắn, thẳng vào việc, "
                     "bằng tiếng Việt. Được phép nói thẳng khi số liệu chưa đủ để kết luận.\n\n"
                     + _fmt_state(context)),
        })
        try:
            async with self.client.messages.stream(
                model=self.cfg["model"],
                max_tokens=self.cfg.get("maxTokens", 16000),
                system=sys_blocks,
                thinking={"type": "adaptive"},
                output_config={"effort": "medium"},
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                final = await stream.get_final_message()
            usd = self.cost.record(self.cfg["model"], final.usage)
            bus.emit("brain", "chi-phi", f"chat: ${usd:.4f}", usd=usd, label="chat")
        except Exception as e:  # noqa: BLE001
            self.last_error = f"{type(e).__name__}: {e}"
            bus.log("brain", "loi-chat", self.last_error)
            yield f"\n\n_(lỗi gọi API: {self.last_error})_"


_brain: Brain | None = None
_lock = asyncio.Lock()


async def get_brain() -> Brain:
    global _brain
    async with _lock:
        if _brain is None:
            _brain = Brain()
    return _brain
