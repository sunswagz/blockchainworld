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
def load_skills() -> tuple[str, int]:
    """Nạp mọi SKILL.md. Trả (nội dung ghép, SỐ KỸ NĂNG).

    Trả về cả con số vì trước đây dashboard tự đếm bằng
    `len(skills.split("---"))` — mà `---` vừa là dấu ghép giữa các file vừa là
    đường kẻ ngang trong chính markdown, nên nó báo **11 kỹ năng trong khi trên
    đĩa có 5**. Không có gì đổ, chỉ là một con số sai nằm ngay cạnh những con số
    đúng, và không ai có lý do để nghi ngờ nó.

    Kho kỹ năng nằm ngoài code để sửa được mà không phải deploy lại — và để đọc
    git log của nó là thấy bot đã học thêm những gì.
    """
    parts: list[str] = []
    if SKILLS_DIR.exists():
        for d in sorted(SKILLS_DIR.iterdir()):
            # `skills/traders/` bị BỎ QUA có chủ ý. Đó là kho hồ sơ trader do
            # Đài quan sát sinh ra — hàng chục file, và nạp hết vào system
            # prompt thì vừa phình vừa đắt, mà tệ hơn là dìm bộ não trong dữ
            # liệu CHƯA QUA KIỂM CHỨNG. Chúng phải được truy hồi có chọn lọc,
            # đúng như bài học trong `recall()`.
            if d.name == "traders":
                continue
            f = d / "SKILL.md" if d.is_dir() else d
            if f.suffix == ".md" and f.exists():
                parts.append(f.read_text(encoding="utf-8").strip())
    return "\n\n---\n\n".join(parts), len(parts)


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
# Tham số của bộ luật. Tách ra thành hằng số CÓ TÊN vì phòng huấn luyện xoay
# đúng những số này để tìm bộ tốt hơn. Trước đây chúng nằm rải rác trong thân
# hàm dưới dạng số trần — mà một con số trần trong thân hàm thì không dò được,
# và cũng không ai biết nó đã từng được chọn theo căn cứ gì.
THAM_MAC_DINH: dict[str, Any] = {
    "stopAtr": 1.5,        # SL cách giá bao nhiêu lần ATR
    "demTp": 1.05,         # đệm trên mức RR tối thiểu — đừng nằm sát mép
    "boiTp2": 1.6,         # TP2 = TP1 × số này
    "tinCay": 0.6,         # độ tin cậy gán cho lệnh thuận xu hướng
    "adxToiThieu": 0.0,    # 0 = không lọc thêm, đã có ADX≥22 trong regime
    "cheDoVao": ["TREND_UP", "TREND_DOWN"],
    "chanXungDot": True,   # khung lớn ngược khung nhỏ thì đứng ngoài
    "chanBienDongCao": False,
}


def mock_thesis(state: dict, regime: dict, primary_tf: str,
                tham: dict | None = None) -> dict:
    """Suy luận bằng luật để vòng lặp chạy kín khi không có API key.

    Cố ý bảo thủ: chỉ vào lệnh thuận xu hướng rõ, còn lại NO_TRADE. Nó không phải
    "phiên bản rẻ của Claude" — nó là mức sàn để so sánh. Brain thật mà không
    thắng nổi cái này thì đó là thông tin đáng giá.

    `tham` để phòng huấn luyện dò tham số. Bỏ trống thì chạy đúng như mặc định,
    nên bản chạy thật và bản chạy lại dùng CHUNG một hàm này — nếu tách làm hai
    bản thì sớm muộn chúng lệch nhau, và backtest sẽ đo một chiến lược không
    phải chiến lược sắp chạy bằng tiền thật.
    """
    th = {**THAM_MAC_DINH, **(tham or {})}
    p = state["timeframes"][primary_tf]
    price = p["price"]
    atr = p["_raw"]["atr"] or price * 0.01
    prim = regime["primary"]
    conflict = th["chanXungDot"] and "MTF_CONFLICT" in regime["flags"]

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
    if conflict or prim not in th["cheDoVao"]:
        base["reason_codes"].append("MTF_CONFLICT" if conflict else "NO_CLEAR_TREND")
        return base
    if th["chanBienDongCao"] and "HIGH_VOLATILITY" in regime["flags"]:
        base["reason_codes"].append("BIEN_DONG_QUA_CAO")
        return base
    if th["adxToiThieu"] and (p.get("adx") or 0) < th["adxToiThieu"]:
        base["reason_codes"].append(f"ADX_DUOI_{th['adxToiThieu']}")
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
    sa = th["stopAtr"]
    drag = price * (r["feeBps"] + r["slippageBps"]) / 10_000
    stop_that = sa * atr + drag
    k1 = (r["minRR"] * stop_that + drag) / atr * th["demTp"]
    k2 = k1 * th["boiTp2"]

    long = prim == "TREND_UP"
    stop = price - sa * atr if long else price + sa * atr
    tp1 = price + k1 * atr if long else price - k1 * atr
    tp2 = price + k2 * atr if long else price - k2 * atr
    base.update({
        "action": "LONG" if long else "SHORT",
        "confidence": th["tinCay"],
        "entry_zone": [round(price * 0.999, 2), round(price * 1.001, 2)],
        "invalidation": round(stop, 2),
        "invalidation_logic": f"{sa}×ATR ngược hướng — mất vùng này là hết xu hướng ngắn hạn",
        "targets": [round(tp1, 2), round(tp2, 2)],
        "suggested_risk_pct": 0.5,
        "reason_codes": ["MOCK_BRAIN", "TREND_ALIGNED", "ADX_CONFIRMS"],
        "reasoning": f"[mock] Thuận {prim} với ADX {p.get('adx')}. SL {sa}×ATR, TP1 {k1:.1f}×ATR — "
                     f"bội số này suy từ ATR/giá hiện tại ({atr / price * 100:.3f}%) để RR còn "
                     f"≥{r['minRR']} sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
    })
    return base


# ── Bộ luật thứ hai: đi ngang ─────────────────────────────────────────────
THAM_BIEN: dict[str, Any] = {
    "viTriMua": 0.25,      # chỉ mua khi giá nằm dưới 25% chiều cao dải Bollinger
    "rsiToiDa": 45.0,      # và RSI còn ở nửa dưới
    "adxToiDa": 20.0,      # ADX phải THẤP — cao nghĩa là đang có xu hướng, không phải biên
    "stopAtr": 1.2,
    "demTp": 1.05,
    "tinCay": 0.55,
    "chanXungDot": False,  # khung lớn nghiêng chiều nào không quyết định gì trong biên
}


def mock_range_thesis(state: dict, regime: dict, primary_tf: str,
                      tham: dict | None = None) -> dict:
    """Mua ở ĐÁY BIÊN khi thị trường đi ngang. Bộ luật thứ hai, chỉ LONG.

    Vì sao cần: bot hiện chỉ vào lệnh được ở TREND_UP. TREND_DOWN sinh luận điểm
    SHORT rồi bị Risk Engine chặn vì sàn spot không short được, còn RANGE thì bộ
    luật xu hướng từ chối thẳng. Đo tại đây: 38 luận điểm liên tiếp đều NO_TRADE,
    100% trong chế độ RANGE. Bot đứng ngoài gần như toàn bộ thời gian — không
    phải vì thận trọng, mà vì không có công cụ cho trạng thái thị trường phổ
    biến nhất.

    Đây là bộ luật NGƯỢC HƯỚNG, và nó nguy hiểm theo một kiểu riêng: trong biên
    thì mua đáy là đúng, nhưng khi biên vỡ thì mua đáy là bắt dao rơi. Ba hàng
    rào chặn đúng chuyện đó — ADX phải thấp (còn là biên), không mua khi vừa
    thủng đáy biên (`BREAKOUT_DOWN`), và stop nằm dưới đáy biên chứ không phải
    dưới giá vào.

    **Chưa được chạy thật.** Nó vào hệ thống với tư cách CHALLENGER và phải
    thắng bản đang chạy trên dữ liệu ngoài mẫu mới được lên — xem `chien_luoc.py`.
    """
    th = {**THAM_BIEN, **(tham or {})}
    p = state["timeframes"][primary_tf]
    price = p["price"]
    atr = p["_raw"]["atr"] or price * 0.01

    base = {
        "regime_read": regime["primary"],
        "market_summary": f"[biên] {regime['primary']}, ADX {p.get('adx')}, "
                          f"RSI {p.get('rsi14')}, vị trí dải {p.get('bbPosition')}",
        "scenarios": [
            {"name": "bật lại trong biên", "probability": 0.45, "description": "chạm đáy biên rồi hồi"},
            {"name": "đi ngang tiếp", "probability": 0.35, "description": "không đi đâu cả"},
            {"name": "thủng biên", "probability": 0.20, "description": "mất đáy — đây là kịch bản giết chiến lược này"},
        ],
        "action": "NO_TRADE", "confidence": 0.4,
        "entry_zone": None, "invalidation": None,
        "invalidation_logic": "không vào lệnh nên không có điểm vô hiệu hoá",
        "targets": [], "suggested_risk_pct": 0.0,
        "strategy": "MOCK_RANGE_V1",
        "reason_codes": ["MOCK_BRAIN", "CHIEN_LUOC_BIEN"],
        "reasoning": "Bộ luật biên: chỉ mua ở đáy biên khi thị trường thật sự đi ngang.",
        "event_risk": "UNKNOWN",
    }

    if regime["primary"] != "RANGE":
        base["reason_codes"].append("KHONG_PHAI_BIEN")
        return base
    # Vừa thủng đáy biên thì đây không còn là biên nữa. Không có chốt này thì
    # chiến lược sẽ mua đúng vào lúc tệ nhất, và mua thêm ở mỗi nến rơi.
    if "BREAKOUT_DOWN" in regime["flags"]:
        base["reason_codes"].append("DANG_THUNG_BIEN")
        return base
    adx = p.get("adx")
    if adx is None or adx > th["adxToiDa"]:
        base["reason_codes"].append(f"ADX_{adx}_QUA_CAO_KHONG_CON_LA_BIEN")
        return base
    bb = p.get("bbPosition")
    rsi = p.get("rsi14")
    if bb is None or bb > th["viTriMua"]:
        base["reason_codes"].append("CHUA_VE_DAY_BIEN")
        return base
    if rsi is None or rsi > th["rsiToiDa"]:
        base["reason_codes"].append("RSI_CHUA_DU_THAP")
        return base
    day = p.get("range20Low")
    if day is None or day >= price:
        base["reason_codes"].append("KHONG_DOC_DUOC_DAY_BIEN")
        return base

    # SL dưới ĐÁY BIÊN, không phải dưới giá vào: điểm vô hiệu hoá của luận điểm
    # này là "biên bị mất", và đó là một mức giá cụ thể trên biểu đồ chứ không
    # phải một bội số ATR tuỳ ý.
    r = CONFIG["risk"]
    stop = min(day - 0.25 * atr, price - th["stopAtr"] * atr)
    drag = price * (r["feeBps"] + r["slippageBps"]) / 10_000
    stop_that = (price - stop) + drag
    tp1 = price + (r["minRR"] * stop_that + drag) * th["demTp"]
    tp2 = price + (tp1 - price) * 1.6

    # Mục tiêu không được vượt đỉnh biên — trong biên thì đỉnh biên là nơi người
    # bán đứng chờ, đặt TP qua đó là tự hứa một thứ chính chiến lược không tin.
    dinh = p.get("range20High")
    if dinh and tp1 > dinh:
        base["reason_codes"].append("MUC_TIEU_VUOT_DINH_BIEN")
        return base

    base.update({
        "action": "LONG", "confidence": th["tinCay"],
        "entry_zone": [round(price * 0.999, 2), round(price * 1.001, 2)],
        "invalidation": round(stop, 2),
        "invalidation_logic": f"dưới đáy biên 20 nến ({day:.2f}) — mất mức này là hết biên",
        "targets": [round(tp1, 2), round(tp2, 2)],
        "suggested_risk_pct": 0.5,
        "reason_codes": ["MOCK_BRAIN", "CHIEN_LUOC_BIEN", "O_DAY_BIEN", "ADX_THAP"],
        "reasoning": f"[biên] Giá ở {bb:.2f} chiều cao dải, RSI {rsi}, ADX {adx} — "
                     f"đi ngang thật. Mua đáy biên, SL dưới {day:.2f}, "
                     f"TP dưới đỉnh biên {dinh}.",
    })
    return base


# Sổ đăng ký bộ luật. Phòng huấn luyện và Risk Engine gọi qua đây thay vì gọi
# thẳng, để thêm một chiến lược không phải sửa chỗ nào khác.
BO_LUAT = {
    "MOCK_RULES_V1": (mock_thesis, THAM_MAC_DINH),
    "MOCK_RANGE_V1": (mock_range_thesis, THAM_BIEN),
}


def suy_luan(ma: str, state: dict, regime: dict, primary_tf: str,
             tham: dict | None = None) -> dict:
    ham, _ = BO_LUAT.get(ma, BO_LUAT["MOCK_RULES_V1"])
    return ham(state, regime, primary_tf, tham)


def mock_postmortem(trade: dict, so: list[dict] | None = None) -> dict:
    """Hậu kiểm bằng luật — có SO VỚI SỔ, không chỉ nhìn một lệnh.

    Bản đầu chỉ có hai câu cho mọi lệnh và luôn kết luận GOOD_TRADE. Đo được sau
    8 lệnh thật: 8 bài học nhưng chỉ **2 câu khác nhau**, 0 lần đòi đổi chiến
    lược, và mọi lệnh đều "quyết định tốt". Trí nhớ ngữ nghĩa khi đó không phải
    trí nhớ — nó là một cái máy dán nhãn.

    Giữ nguyên nguyên tắc trung tâm (quyết định ≠ kết quả), nhưng thêm những thứ
    MỘT LỆNH ĐƠN LẺ KHÔNG NÓI ĐƯỢC mà cả sổ thì nói được:

      · rủi ro lệnh này lệch bao nhiêu so với các lệnh khác — chính chỗ đã biến
        kỳ vọng +0,282R thành khoản lỗ −$95,69
      · dính stop quá nhanh: vào sai thời điểm, không phải luận điểm sai
      · thoát vì hết hạn giữ: mục tiêu đặt ngoài tầm với của biến động
    """
    pnl = trade.get("pnl") or 0
    win = pnl > 0
    ly_do = trade.get("exitReason")
    rui_ro = trade.get("riskAmount") or 0
    giu = trade.get("barsHeld") or trade.get("soNenGiu")

    hop_che_do = vao_dung = size_dung = stop_dung = True
    doi_cl = False
    tin = 0.3
    y: list[str] = []

    # — Rủi ro có ĐỀU so với các lệnh khác không —
    # R chỉ so sánh được khi rủi ro mỗi lệnh gần bằng nhau. Lệch nhiều nghĩa là
    # chính kích thước, chứ không phải tín hiệu, đang quyết định lãi lỗ.
    khac = [t.get("riskAmount") or 0 for t in (so or [])
            if t.get("id") != trade.get("id") and (t.get("riskAmount") or 0) > 0]
    if rui_ro and len(khac) >= 3:
        tb = sum(khac) / len(khac)
        if tb > 0:
            lech = rui_ro / tb
            if lech >= 1.6 or lech <= 0.625:
                size_dung = False
                tin = 0.5
                y.append(f"rủi ro {rui_ro:.0f} lệch {lech:.1f}× so với trung bình sổ "
                         f"({tb:.0f}) — R của lệnh này không so được với các lệnh khác")
                if lech >= 1.6 and not win:
                    y.append("và đây là một lệnh THUA đặt cược lớn — đúng dạng làm "
                             "kỳ vọng R dương trong khi tiền âm")

    # — Dính stop quá nhanh = vào sai lúc, không phải luận điểm sai —
    if ly_do == "STOP_LOSS" and isinstance(giu, (int, float)) and giu <= 2:
        vao_dung = False
        tin = max(tin, 0.45)
        y.append(f"dính stop chỉ sau {giu} nến — vào quá sớm hoặc stop nằm trong "
                 f"vùng nhiễu, chứ không phải luận điểm sai")

    # — Hết hạn giữ = mục tiêu ngoài tầm với —
    if ly_do in ("HET_HAN", "TIMEOUT"):
        tin = max(tin, 0.4)
        y.append("thoát vì hết hạn giữ, không chạm SL lẫn TP — mục tiêu đặt xa hơn "
                 "thứ biến động cho phép trong khoảng thời gian đó")

    # — Phân loại: quyết định ≠ kết quả, luôn luôn —
    # Đặt SAU khối "có lặp lại không" vì khối đó có thể hạ `hop_che_do`.
    quyet_dinh_tot = vao_dung and size_dung and stop_dung and hop_che_do
    if quyet_dinh_tot:
        pl = "GOOD_TRADE_GOOD_OUTCOME" if win else "GOOD_TRADE_BAD_OUTCOME"
    else:
        pl = "BAD_TRADE_GOOD_OUTCOME" if win else "BAD_TRADE_BAD_OUTCOME"

    if pl == "BAD_TRADE_GOOD_OUTCOME":
        y.append("THẮNG nhưng quy trình sai — đây là loại lệnh nguy hiểm nhất, vì "
                 "phần thưởng đến ngay và dạy đúng thứ không được lặp lại")

    # — CÓ LẶP LẠI KHÔNG: chỗ duy nhất được phép đòi đổi chiến lược —
    #
    # `change_strategy` là bài học đắt nhất trong kho: `journal._chon()` luôn kéo
    # nó vào prompt kể cả khi lạc chế độ. Vì thế nó phải mua bằng MỘT CHUỖI lệnh
    # sai, không phải một lệnh xui — nếu không, mỗi lệnh thua lại đòi đổi chiến
    # lược một lần và kho bài học biến thành tiếng ồn.
    #
    # Ba nguyên nhân dưới đây có chung một tính chất: chúng là tật của QUY TRÌNH
    # chứ không phải của một lệnh, nên chỉ nhìn thấy được khi đếm trên cả sổ.
    dong = [t for t in (so or []) if t.get("status") == "CLOSED" and t.get("pnl") is not None]

    if not size_dung and len(khac) >= 3:
        # Đếm bằng trung bình CẢ SỔ, không bằng "trung bình các lệnh khác".
        # Trung bình-trừ-mình đổi theo từng lệnh, nên cùng một cuốn sổ lại ra số
        # lệnh lệch khác nhau tuỳ đang xét lệnh nào — ở 8 lệnh đầu nó đếm ra 2
        # thay vì 3 và luật lặp lại không bao giờ nổ.
        moi_rr = [t["riskAmount"] for t in dong if (t.get("riskAmount") or 0) > 0]
        tb_ca_so = sum(moi_rr) / len(moi_rr)
        lech_nhieu = sum(1 for x in moi_rr if not (0.625 < x / tb_ca_so < 1.6))
        if lech_nhieu >= 3:
            doi_cl = True
            tin = max(tin, 0.7)
            y.append(f"KHÔNG PHẢI LỆNH NÀY XUI: {lech_nhieu}/{len(dong)} lệnh trong sổ "
                     f"cược lệch quá 1,6× so với mức thường. Rủi ro đang bị quyết định "
                     f"bởi khoảng cách stop và trần tiền mua được, không bởi mức rủi ro "
                     f"đã chọn — đó là tật của cách tính kích thước, sửa ở đó chứ không "
                     f"sửa ở tín hiệu vào lệnh")

    if not vao_dung:
        stop_som = sum(1 for t in dong if t.get("exitReason") == "STOP_LOSS"
                       and isinstance(t.get("barsHeld") or t.get("soNenGiu"), (int, float))
                       and (t.get("barsHeld") or t.get("soNenGiu")) <= 2)
        if stop_som >= 3:
            doi_cl = True
            tin = max(tin, 0.65)
            y.append(f"KHÔNG PHẢI LỆNH NÀY XUI: {stop_som} lệnh đã dính stop trong ≤2 nến. "
                     f"Stop đang nằm trong vùng nhiễu chứ không nằm sau cấu trúc — nới stop "
                     f"và giảm kích thước tương ứng, đừng đổi tín hiệu")

    # — Chế độ này có lỗ ĐỀU không —
    # Thua trong một chế độ không nói lên gì; thua ĐỀU qua nhiều lệnh trong CÙNG
    # chế độ là chiến lược không hợp chế độ đó. Cần đủ mẫu, nếu không 2 lệnh xui
    # cũng đủ khai tử một chế độ.
    ma = trade.get("regimeKey") or trade.get("regimeAtEntry")
    if ma and not win:
        cung = [t for t in dong if (t.get("regimeKey") or t.get("regimeAtEntry")) == ma]
        if len(cung) >= 5:
            tien = sum(t["pnl"] for t in cung)
            thua = sum(1 for t in cung if t["pnl"] <= 0)
            if tien < 0 and thua / len(cung) >= 0.6:
                doi_cl = True
                tin = max(tin, 0.6)
                hop_che_do = False
                y.append(f"KHÔNG PHẢI LỆNH NÀY XUI: chế độ {ma} đã lỗ {tien:+.0f} qua "
                         f"{len(cung)} lệnh ({thua} thua) — chiến lược này không ăn được "
                         f"trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số")

    if not y:
        y.append("chạy tới mục tiêu, setup và cách thoát giữ nguyên" if win else
                 "dính stop trong biên độ bình thường — một lệnh thua không đồng "
                 "nghĩa một quyết định sai")

    return {
        "regime_appropriate": hop_che_do, "entry_valid": vao_dung,
        "size_valid": size_dung, "stop_placement_valid": stop_dung,
        "thesis_was_wrong": bool(ly_do == "STOP_LOSS" and not win and vao_dung),
        "classification": pl,
        "lesson": "[luật] " + ". ".join(x[0].upper() + x[1:] for x in y) + ".",
        "change_strategy": doi_cl,
        "confidence_in_lesson": tin,
    }


# ── Bộ não thật ───────────────────────────────────────────────────────────
class Brain:
    def __init__(self) -> None:
        self.cfg = CONFIG["brain"]
        self.mode = brain_mode()
        self.cost = CostMeter(self.cfg)
        self.skills, self.so_ky_nang = load_skills()
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
            "skillsLoaded": self.so_ky_nang,
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
            out = mock_postmortem(trade, store.read_all(store.TRADES))
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
                out = mock_postmortem(trade, store.read_all(store.TRADES))

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
