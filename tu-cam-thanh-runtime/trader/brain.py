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
        # MÃ, không phải câu văn. Đường SDK có `output_config` ép kiểu ở tầng
        # API; đường CLI thì lược đồ chỉ là một câu trong lời nhắc, nên model đã
        # nhét nguyên đoạn 300 chữ lý lẽ vào đây ở lượt chạy thật đầu tiên.
        "strategy": {"type": "string", "maxLength": 40,
                     "description": "MÃ ngắn viết HOA và gạch dưới, ví dụ MOCK_RULES_V1 hay CLI_TREND_V1. KHÔNG phải câu văn — lý lẽ thuộc về `reasoning`."},
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

    # Phần trần dành RIÊNG cho luận điểm. Hậu kiểm và luận điểm dùng chung một
    # trần, nên một ngày nhiều lệnh đóng có thể tiêu hết 8 lượt vào hậu kiểm và
    # bộ não không còn lượt nào để NGHĨ trước khi vào lệnh tiếp theo.
    #
    # Hậu kiểm trễ một ngày vẫn còn nguyên giá trị — lệnh đã đóng rồi. Luận
    # điểm trễ thì mất hẳn cơ hội. Nên khi đã tiêu quá nửa trần, hậu kiểm nhường
    # chỗ và rơi về `mock_postmortem`; luận điểm vẫn được gọi tới lượt cuối.
    PHAN_CHO_HAU_KIEM = 0.5

    def blocked(self, loai: str = "") -> str | None:
        d = self._day()
        if d["usd"] >= self.cfg["dailyBudgetUsd"]:
            return f"đã tiêu ${d['usd']:.2f} ≥ hạn mức ${self.cfg['dailyBudgetUsd']}/ngày"
        tran = self.cfg["maxCallsPerDay"]
        if d["calls"] >= tran:
            return f"đã gọi {d['calls']} lượt ≥ trần {tran}/ngày"
        if loai == "postmortem" and d["calls"] >= tran * self.PHAN_CHO_HAU_KIEM:
            return (f"đã gọi {d['calls']}/{tran} lượt — phần còn lại để dành cho luận "
                    f"điểm; hậu kiểm dùng luật thuần, đọc lại sau cũng được")
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
# ── Bộ luật thứ ba: chờ kéo lùi ───────────────────────────────────────────
THAM_KEO_LUI: dict[str, Any] = {
    "keoLuiToiDa": 0.8,    # giá phải về trong ngần này ATR quanh EMA20
    "keoLuiSau": 1.2,      # nhưng không được thủng quá sâu qua bên kia EMA20
    "rsiSan": 40.0,        # RSI đã nguội…
    "rsiTran": 62.0,       # …nhưng chưa gãy
    "demStop": 0.35,       # stop lùi thêm ngần này ATR sau mốc cấu trúc
    "demTp": 1.05,
    "boiTp2": 1.6,
    "tinCay": 0.6,
    "cheDoVao": ["TREND_UP", "TREND_DOWN"],
    "chanXungDot": True,
}


def _moc_cau_truc(p: dict, price: float, long: bool) -> float | None:
    """Mốc gần nhất mà thị trường ĐÃ từng tôn trọng, nằm bên kia giá.

    Ưu tiên swing gần nhất; không có thì lấy biên 20 nến. Trả None khi cả hai
    đều không đọc được — khi đó bộ luật phải đứng ngoài chứ không được bịa ra
    một con số, vì đúng chỗ này là chỗ chiến lược đang chạy làm sai.
    """
    if long:
        ds = [x for x in (p.get("swingLows") or []) if x is not None and x < price]
        moc = max(ds) if ds else p.get("range20Low")
    else:
        ds = [x for x in (p.get("swingHighs") or []) if x is not None and x > price]
        moc = min(ds) if ds else p.get("range20High")
    return moc if isinstance(moc, (int, float)) and moc > 0 else None


def _tp_tu_stop(price: float, stop: float, long: bool, r: dict,
                dem_tp: float, boi_tp2: float) -> tuple[float, float]:
    """Mục tiêu SUY RA từ khoảng cách stop THẬT, không từ bội số ATR ghi cứng.

    Bộ luật cấu trúc không có "1,5×ATR" để dựa vào — stop nằm ở đâu là do thị
    trường quyết định. Nên mục tiêu phải tính ngược từ chính khoảng cách đó, sau
    khi đã trừ phí và trượt giá ở CẢ HAI đầu:

        RR khi khớp = (khoảng TP − drag) / (khoảng SL + drag) ≥ minRR
    """
    drag = price * (r["feeBps"] + r["slippageBps"]) / 10_000
    stop_that = abs(price - stop) + drag
    xa = (r["minRR"] * stop_that + drag) * dem_tp
    if long:
        return price + xa, price + xa * boi_tp2
    return price - xa, price - xa * boi_tp2


def mock_keo_lui_thesis(state: dict, regime: dict, primary_tf: str,
                        tham: dict | None = None) -> dict:
    """Chỉ vào lệnh SAU khi giá đã kéo lùi về EMA20, và đặt stop sau CẤU TRÚC.

    Vì sao có bộ luật này — nó không phải một ý hay, nó là câu trả lời cho một
    số đo. Chiến lược đang cầm quyền thoát bằng stop ở **34/44 lệnh (77%)** và
    chỉ 5 lệnh chạm mục tiêu; kỳ vọng −0,666R qua 44 lệnh chạy lại.

    Chẩn đoán: nó vào lệnh khi ADX ≥ 22, tức là khi nhịp tăng ĐÃ chạy được một
    đoạn — giá đang ở đỉnh của một chân sóng. Stop 1,5×ATR đặt từ chỗ đó rơi vào
    giữa vùng giá mà một cú kéo lùi bình thường cũng quét tới. Không phải stop
    quá hẹp; là stop đặt ở chỗ chưa từng có ai bảo vệ.

    Hai chỗ khác chiến lược cũ, và chỉ hai chỗ đó — để nếu nó hơn thì biết là
    hơn nhờ cái gì:

      1. **Chờ kéo lùi.** Chỉ vào khi giá đã về trong 0,8×ATR quanh EMA20 và RSI
         đã nguội về 40–62. Cùng bối cảnh xu hướng, khác thời điểm bấm nút.
      2. **Stop sau cấu trúc.** Đặt dưới swing thấp gần nhất (hoặc đáy 20 nến),
         lùi thêm một khoảng đệm — một mốc thị trường ĐÃ từng tôn trọng, thay vì
         một khoảng cách máy móc tính từ giá hiện tại.

    Mục tiêu vẫn suy ra từ chi phí như bộ luật cũ, nên phần đó không phải là
    biến. Khác biệt duy nhất là ĐIỂM VÀO và CHỖ ĐẶT STOP.
    """
    th = {**THAM_KEO_LUI, **(tham or {})}
    p = state["timeframes"][primary_tf]
    price = p["price"]
    atr = p["_raw"]["atr"] or price * 0.01
    ema20 = p["_raw"].get("ema20") or p.get("ema20")
    rsi = p.get("rsi14")
    prim = regime["primary"]
    r = CONFIG["risk"]

    base = {
        "regime_read": prim,
        "market_summary": f"[kéo lùi] {prim}, RSI {rsi}, giá cách EMA20 "
                          f"{((price - ema20) / atr):.2f}×ATR" if ema20 else f"[kéo lùi] {prim}",
        "scenarios": [
            {"name": "kéo lùi rồi đi tiếp", "probability": 0.45, "description": "nhịp nghỉ trong xu hướng"},
            {"name": "kéo lùi thành đảo chiều", "probability": 0.35, "description": "mất mốc cấu trúc"},
            {"name": "đi tiếp không chờ", "probability": 0.20, "description": "lỡ nhịp, đứng ngoài"},
        ],
        "action": "NO_TRADE",
        "confidence": 0.4,
        "entry_zone": None, "invalidation": None,
        "invalidation_logic": "không vào lệnh nên không có điểm vô hiệu hoá",
        "targets": [], "suggested_risk_pct": 0.0,
        "strategy": "MOCK_KEO_LUI_V1",
        "reason_codes": ["KEO_LUI"],
        "reasoning": "Chờ giá kéo lùi về EMA20 rồi mới vào, stop đặt sau mốc cấu trúc.",
        "event_risk": "UNKNOWN",
    }

    if th["chanXungDot"] and "MTF_CONFLICT" in regime["flags"]:
        base["reason_codes"].append("MTF_CONFLICT")
        return base
    if prim not in th["cheDoVao"]:
        base["reason_codes"].append("NO_CLEAR_TREND")
        return base
    if ema20 is None or rsi is None:
        base["reason_codes"].append("KHONG_DOC_DUOC_EMA20_HOAC_RSI")
        return base

    long = prim == "TREND_UP"
    # Khoảng cách tới EMA20, tính theo ATR và có DẤU theo hướng xu hướng:
    # dương = giá còn ở phía "đã chạy", âm = đã thủng qua bên kia.
    lech = (price - ema20) / atr if long else (ema20 - price) / atr

    if lech > th["keoLuiToiDa"]:
        base["reason_codes"].append(f"CHUA_KEO_LUI_{lech:.2f}xATR")
        base["reasoning"] = (f"Giá còn cách EMA20 {lech:.2f}×ATR — vẫn ở đỉnh chân sóng. "
                             f"Vào đây là đặt stop vào chỗ chưa ai bảo vệ, đúng lỗi đã làm "
                             f"77% lệnh của chiến lược cũ chết ở stop.")
        return base
    if lech < -th["keoLuiSau"]:
        base["reason_codes"].append(f"THUNG_QUA_SAU_{lech:.2f}xATR")
        return base

    if long and not (th["rsiSan"] <= rsi <= th["rsiTran"]):
        base["reason_codes"].append(f"RSI_{rsi}_NGOAI_KHOANG")
        return base
    if not long and not ((100 - th["rsiTran"]) <= rsi <= (100 - th["rsiSan"])):
        base["reason_codes"].append(f"RSI_{rsi}_NGOAI_KHOANG")
        return base

    moc = _moc_cau_truc(p, price, long)
    if moc is None:
        base["reason_codes"].append("KHONG_DOC_DUOC_MOC_CAU_TRUC")
        return base

    stop = moc - th["demStop"] * atr if long else moc + th["demStop"] * atr
    # Kẹp vào dải stop mà Risk Engine chấp nhận. Không kẹp thì mốc cấu trúc quá
    # gần sẽ bị chặn ở cửa sau, còn quá xa thì kích thước vị thế teo lại — cả
    # hai đều là "đã tốn một lượt suy luận rồi mới biết".
    xa = abs(price - stop) / atr
    if xa < r["minStopAtr"]:
        stop = price - r["minStopAtr"] * atr if long else price + r["minStopAtr"] * atr
    elif xa > r["maxStopAtr"]:
        base["reason_codes"].append(f"MOC_CAU_TRUC_QUA_XA_{xa:.2f}xATR")
        base["reasoning"] = (f"Mốc cấu trúc gần nhất cách {xa:.2f}×ATR, vượt trần "
                             f"{r['maxStopAtr']}×ATR. Kéo stop lại gần cho vừa trần là bỏ "
                             f"mất chính lý do dùng stop cấu trúc — thà đứng ngoài.")
        return base

    tp1, tp2 = _tp_tu_stop(price, stop, long, r, th["demTp"], th["boiTp2"])
    base.update({
        "action": "LONG" if long else "SHORT",
        "confidence": th["tinCay"],
        "entry_zone": [round(price * 0.999, 2), round(price * 1.001, 2)],
        "invalidation": round(stop, 2),
        "invalidation_logic": (f"dưới mốc cấu trúc {moc:.2f} một khoảng đệm "
                               f"{th['demStop']}×ATR — mất mốc này là cú kéo lùi đã thành "
                               f"đảo chiều" if long else
                               f"trên mốc cấu trúc {moc:.2f} một khoảng đệm {th['demStop']}×ATR"),
        "targets": [round(tp1, 2), round(tp2, 2)],
        "suggested_risk_pct": 0.5,
        "reason_codes": ["KEO_LUI", "DA_KEO_LUI_VE_EMA20", "STOP_SAU_CAU_TRUC"],
        "reasoning": (f"Giá đã kéo lùi về {lech:+.2f}×ATR quanh EMA20, RSI {rsi} đã nguội "
                      f"mà chưa gãy. Stop {abs(price - stop) / atr:.2f}×ATR đặt sau mốc "
                      f"{moc:.2f} — một mức thị trường đã từng tôn trọng, không phải một "
                      f"khoảng cách máy móc tính từ giá hiện tại."),
    })
    return base


# ── Bộ luật thứ tư: bung nén ──────────────────────────────────────────────
THAM_BUNG_NEN: dict[str, Any] = {
    "bungToiThieu": 1.3,   # ATR phải đang GIÃN so với trung vị của chính nó
    "bungToiDa": 3.0,      # nhưng đã nổ quá rồi thì phần dễ ăn nhất đã qua
    "khoiLuongToiThieu": 1.2,   # khối lượng phải xác nhận
    "chamBienPct": 0.15,   # coi là chạm biên khi cách biên 20 nến dưới ngần này %
    "demStop": 0.3,
    "demTp": 1.05,
    "boiTp2": 1.6,
    "tinCay": 0.6,
    "cheDoVao": ["TREND_UP", "TREND_DOWN", "BREAKOUT"],
    "chanXungDot": False,  # phá biên là sự kiện của chính khung đó
}


def mock_bung_nen_thesis(state: dict, regime: dict, primary_tf: str,
                         tham: dict | None = None) -> dict:
    """Vào khi giá phá biên 20 nến CÙNG LÚC biến động và khối lượng đang giãn.

    Chiến lược cầm quyền không có một điều kiện nào về biến động lẫn khối lượng
    — nó chỉ đọc ADX, một thước đo xu hướng CHẬM. Bộ luật này thay thước đó bằng
    hai thước nhanh: `atrRatioVsMedian` (biến động đang giãn hay đang co) và
    `volumeRatio` (có tiền vào theo không).

    Đối chứng có chủ ý với bộ luật «chờ kéo lùi»: một bên chờ giá nguội rồi mới
    vào, một bên vào đúng lúc giá bung. Hai giả thuyết ngược nhau về cùng một
    khuyết tật, đo trên cùng một đoạn dữ liệu — nếu cả hai cùng thua champion
    thì vấn đề không nằm ở thời điểm vào lệnh, và đó cũng là một câu trả lời.

    Có một cửa mà bộ luật này KHÔNG được phép mở: nếu ATR đã giãn quá `bungToiDa`
    thì đứng ngoài. Vào sau khi đã nổ là mua ở chỗ stop phải đặt rất xa, và
    khoảng cách stop chính là thứ quyết định kích thước vị thế.
    """
    th = {**THAM_BUNG_NEN, **(tham or {})}
    p = state["timeframes"][primary_tf]
    price = p["price"]
    atr = p["_raw"]["atr"] or price * 0.01
    prim = regime["primary"]
    r = CONFIG["risk"]
    ty_atr = p.get("atrRatioVsMedian")
    ty_kl = p.get("volumeRatio")
    tren = p.get("range20High")
    duoi = p.get("range20Low")

    base = {
        "regime_read": prim,
        "market_summary": f"[bung nén] {prim}, ATR/trung vị {ty_atr}, khối lượng ×{ty_kl}",
        "scenarios": [
            {"name": "phá biên đi tiếp", "probability": 0.42, "description": "nén rồi bung, có khối lượng"},
            {"name": "phá giả rồi thu về", "probability": 0.38, "description": "quét thanh khoản ngoài biên"},
            {"name": "đi ngang tiếp", "probability": 0.20, "description": "chưa đủ lực"},
        ],
        "action": "NO_TRADE",
        "confidence": 0.4,
        "entry_zone": None, "invalidation": None,
        "invalidation_logic": "không vào lệnh nên không có điểm vô hiệu hoá",
        "targets": [], "suggested_risk_pct": 0.0,
        "strategy": "MOCK_BUNG_NEN_V1",
        "reason_codes": ["BUNG_NEN"],
        "reasoning": "Chỉ vào khi giá phá biên 20 nến cùng lúc biến động và khối lượng giãn.",
        "event_risk": "UNKNOWN",
    }

    if prim not in th["cheDoVao"]:
        base["reason_codes"].append("CHE_DO_KHONG_HOP")
        return base
    if th["chanXungDot"] and "MTF_CONFLICT" in regime["flags"]:
        base["reason_codes"].append("MTF_CONFLICT")
        return base
    if ty_atr is None or ty_kl is None or tren is None or duoi is None:
        base["reason_codes"].append("KHONG_DOC_DUOC_BIEN_DONG_HOAC_BIEN_GIA")
        return base

    if ty_atr < th["bungToiThieu"]:
        base["reason_codes"].append(f"CHUA_BUNG_{ty_atr}")
        return base
    if ty_atr > th["bungToiDa"]:
        base["reason_codes"].append(f"DA_NO_QUA_{ty_atr}")
        base["reasoning"] = (f"ATR đã gấp {ty_atr}× trung vị — phần dễ ăn nhất của cú bung "
                             f"đã qua, và stop bây giờ phải đặt rất xa. Khoảng cách stop là "
                             f"thứ quyết định kích thước vị thế, nên vào muộn ở đây không "
                             f"chỉ là ăn ít hơn mà là cược lệch hẳn so với các lệnh khác.")
        return base
    if ty_kl < th["khoiLuongToiThieu"]:
        base["reason_codes"].append(f"KHOI_LUONG_KHONG_XAC_NHAN_{ty_kl}")
        return base

    gan_tren = (tren - price) / price * 100 <= th["chamBienPct"]
    gan_duoi = (price - duoi) / price * 100 <= th["chamBienPct"]
    if gan_tren and prim != "TREND_DOWN":
        long, moc = True, tren
    elif gan_duoi and prim != "TREND_UP":
        long, moc = False, duoi
    else:
        base["reason_codes"].append("CHUA_CHAM_BIEN_20_NEN")
        return base

    # Stop nằm bên KIA mốc vừa phá — mốc đó vừa đổi vai từ kháng cự thành hỗ trợ
    # (hoặc ngược lại). Đây là chỗ luận điểm sai chứ không phải một khoảng cách.
    stop = moc - th["demStop"] * atr if long else moc + th["demStop"] * atr
    xa = abs(price - stop) / atr
    if xa < r["minStopAtr"]:
        stop = price - r["minStopAtr"] * atr if long else price + r["minStopAtr"] * atr
        xa = r["minStopAtr"]
    elif xa > r["maxStopAtr"]:
        base["reason_codes"].append(f"MOC_PHA_QUA_XA_{xa:.2f}xATR")
        return base

    tp1, tp2 = _tp_tu_stop(price, stop, long, r, th["demTp"], th["boiTp2"])
    base.update({
        "action": "LONG" if long else "SHORT",
        "confidence": th["tinCay"],
        "entry_zone": [round(price * 0.999, 2), round(price * 1.001, 2)],
        "invalidation": round(stop, 2),
        "invalidation_logic": (f"bên kia mốc {moc:.2f} vừa phá — mốc đổi vai, mất lại là "
                               f"cú phá biên thành phá giả"),
        "targets": [round(tp1, 2), round(tp2, 2)],
        "suggested_risk_pct": 0.5,
        "reason_codes": ["BUNG_NEN", "PHA_BIEN_20_NEN", "BIEN_DONG_GIAN", "KHOI_LUONG_XAC_NHAN"],
        "reasoning": (f"Giá chạm biên 20 nến {moc:.2f} khi ATR đang gấp {ty_atr}× trung vị "
                      f"và khối lượng gấp {ty_kl}× trung bình. Stop {xa:.2f}×ATR đặt bên kia "
                      f"mốc vừa phá, không phải một bội số ATR tính từ giá."),
    })
    return base


# ── Bộ luật thứ năm: biên kép ─────────────────────────────────────────────
THAM_BIEN_KEP: dict[str, Any] = {
    "chamLan": 2,          # mức hỗ trợ phải được thử ít nhất ngần này lần
    "dungSai": 0.008,      # hai đáy coi là CÙNG một mức khi lệch dưới 0,8%
    "khoangCach": 0.6,     # giá phải nằm trong ngần này ATR quanh mức
    "hopToiThieu": 2.0,    # hộp biên phải cao ít nhất ngần này ATR
    "adxToiDa": 25.0,      # còn là biên, chưa thành xu hướng
    "demStop": 0.4,        # stop dưới mức hỗ trợ một khoảng đệm
    "demTp": 1.05,
    "boiTp2": 1.6,
    "tinCay": 0.58,
}


def _muc_da_thu(swings: list, gia: float, dung_sai: float, cham_lan: int) -> tuple | None:
    """Mức giá đã được thử ≥`cham_lan` lần, nằm DƯỚI giá hiện tại.

    Gom các đáy swing gần nhau thành cụm. Một đáy đơn lẻ không phải hỗ trợ — nó
    là một chỗ giá từng quay đầu đúng một lần, và chuyện đó xảy ra ở mọi nơi.
    Hỗ trợ là mức thị trường đã **nhiều lần** từ chối đi thấp hơn.
    """
    ds = sorted(x for x in (swings or []) if isinstance(x, (int, float)) and 0 < x < gia)
    if len(ds) < cham_lan:
        return None
    tot = None
    i = 0
    while i < len(ds):
        cum = [ds[i]]
        j = i + 1
        while j < len(ds) and abs(ds[j] - cum[0]) / cum[0] <= dung_sai:
            cum.append(ds[j])
            j += 1
        if len(cum) >= cham_lan:
            muc = sum(cum) / len(cum)
            # gần giá hiện tại nhất thì mới là mức đang có tác dụng
            if tot is None or muc > tot[0]:
                tot = (muc, len(cum))
        i = j
    return tot


def mock_bien_kep_thesis(state: dict, regime: dict, primary_tf: str,
                         tham: dict | None = None) -> dict:
    """Mua ở mức hỗ trợ ĐÃ ĐƯỢC THỬ NHIỀU LẦN, không ở chỗ chỉ báo bảo là thấp.

    Bộ luật thứ hai cho chế độ RANGE, và nó khác «mua đáy biên» ở đúng một chỗ —
    chỗ quan trọng nhất:

        MOCK_RANGE_V1   vào khi CHỈ BÁO nói giá đang thấp
                        (bbPosition ≤ 0,25 và RSI ≤ 45 và ADX ≤ 20)
        MOCK_BIEN_KEP_V1 vào khi CẤU TRÚC nói có một mức đang đỡ
                        (≥2 đáy swing trùng nhau trong 0,8%, giá đang chạm mức)

    Vì sao đáng thử: đo được ở đây, `MOCK_RANGE_V1` chỉ vào **5 lệnh ngoài mẫu**
    trong 2352 điểm — bốn điều kiện chỉ báo phải đúng cùng lúc thì gần như không
    bao giờ đúng. Một chiến lược không vào lệnh không phải chiến lược thận trọng;
    nó là chiến lược không đo được.

    Và vì sao có thể vẫn thua: chế độ RANGE là chỗ **mọi mức đều bị thử lại**.
    Mức đã đỡ hai lần rồi vẫn có thể vỡ ở lần thứ ba, và khi vỡ thì stop nằm ngay
    dưới đó — chỗ đông người nhất để quét. Đây là giả thuyết, không phải kết
    luận, và nó phải qua cửa duyệt như mọi bộ luật khác.
    """
    th = {**THAM_BIEN_KEP, **(tham or {})}
    p = state["timeframes"][primary_tf]
    price = p["price"]
    atr = p["_raw"]["atr"] or price * 0.01
    prim = regime["primary"]
    adx = p.get("adx")
    r = CONFIG["risk"]

    base = {
        "regime_read": prim,
        "market_summary": f"[biên kép] {prim}, ADX {adx}, giá {price}",
        "scenarios": [
            {"name": "mức đỡ được, bật lên", "probability": 0.45, "description": "hỗ trợ đã thử nhiều lần"},
            {"name": "mức vỡ, quét stop", "probability": 0.4, "description": "chỗ đông người nhất để quét"},
            {"name": "đi ngang quanh mức", "probability": 0.15, "description": "không đi đâu"},
        ],
        "action": "NO_TRADE",
        "confidence": 0.4,
        "entry_zone": None, "invalidation": None,
        "invalidation_logic": "không vào lệnh nên không có điểm vô hiệu hoá",
        "targets": [], "suggested_risk_pct": 0.0,
        "strategy": "MOCK_BIEN_KEP_V1",
        "reason_codes": ["BIEN_KEP"],
        "reasoning": "Chỉ mua ở mức hỗ trợ đã được thử nhiều lần, stop dưới mức đó.",
        "event_risk": "UNKNOWN",
    }

    if prim not in ("RANGE", "TREND_UP"):
        base["reason_codes"].append("CHE_DO_KHONG_HOP")
        return base
    if adx is not None and adx > th["adxToiDa"]:
        # ADX cao nghĩa là đang có xu hướng — mức hỗ trợ trong xu hướng giảm là
        # thứ để đi xuyên qua, không phải thứ để mua.
        base["reason_codes"].append(f"ADX_{adx}_QUA_CAO_KHONG_CON_LA_BIEN")
        return base

    tren, duoi = p.get("range20High"), p.get("range20Low")
    if tren is None or duoi is None or (tren - duoi) < th["hopToiThieu"] * atr:
        base["reason_codes"].append("HOP_BIEN_QUA_HEP")
        return base

    tim = _muc_da_thu(p.get("swingLows"), price, th["dungSai"], th["chamLan"])
    if tim is None:
        base["reason_codes"].append(f"KHONG_CO_MUC_DUOC_THU_{th['chamLan']}_LAN")
        return base
    muc, so_lan = tim

    xa = (price - muc) / atr
    if xa > th["khoangCach"]:
        base["reason_codes"].append(f"CON_CACH_MUC_{xa:.2f}xATR")
        return base

    stop = muc - th["demStop"] * atr
    kc = (price - stop) / atr
    if kc < r["minStopAtr"]:
        stop = price - r["minStopAtr"] * atr
        kc = r["minStopAtr"]
    elif kc > r["maxStopAtr"]:
        base["reason_codes"].append(f"MUC_QUA_XA_{kc:.2f}xATR")
        return base

    tp1, tp2 = _tp_tu_stop(price, stop, True, r, th["demTp"], th["boiTp2"])
    # Mục tiêu vượt hẳn trần hộp thì đó không còn là lệnh trong biên nữa — nó là
    # cược phá biên, và cược phá biên thì stop phải đặt kiểu khác.
    if tp1 > tren + atr:
        base["reason_codes"].append("MUC_TIEU_VUOT_TRAN_HOP")
        base["reasoning"] = (f"Mục tiêu {tp1:.2f} vượt trần hộp {tren:.2f} — cần RR "
                             f"{r['minRR']} nhưng hộp không đủ cao để chứa. Lệnh trong biên "
                             f"mà mục tiêu nằm ngoài biên là hai chiến lược trộn vào nhau.")
        return base

    base.update({
        "action": "LONG",
        "confidence": th["tinCay"],
        "entry_zone": [round(price * 0.999, 2), round(price * 1.001, 2)],
        "invalidation": round(stop, 2),
        "invalidation_logic": (f"dưới mức {muc:.2f} — mức đã đỡ {so_lan} lần; mất nó là "
                               f"luận điểm 'có người mua ở đây' sai"),
        "targets": [round(tp1, 2), round(tp2, 2)],
        "suggested_risk_pct": 0.5,
        "reason_codes": ["BIEN_KEP", f"MUC_DUOC_THU_{so_lan}_LAN", "STOP_DUOI_MUC"],
        "reasoning": (f"Mức {muc:.2f} đã được thử {so_lan} lần; giá đang cách {xa:.2f}×ATR. "
                      f"Hộp biên cao {(tren - duoi) / atr:.1f}×ATR nên còn chỗ cho mục tiêu. "
                      f"Stop {kc:.2f}×ATR dưới mức — không phải một khoảng cách tính từ giá."),
    })
    return base


BO_LUAT = {
    "MOCK_RULES_V1": (mock_thesis, THAM_MAC_DINH),
    "MOCK_RANGE_V1": (mock_range_thesis, THAM_BIEN),
    "MOCK_KEO_LUI_V1": (mock_keo_lui_thesis, THAM_KEO_LUI),
    "MOCK_BUNG_NEN_V1": (mock_bung_nen_thesis, THAM_BUNG_NEN),
    "MOCK_BIEN_KEP_V1": (mock_bien_kep_thesis, THAM_BIEN_KEP),
}


def suy_luan(ma: str, state: dict, regime: dict, primary_tf: str,
             tham: dict | None = None) -> dict:
    ham, _ = BO_LUAT.get(ma, BO_LUAT["MOCK_RULES_V1"])
    return ham(state, regime, primary_tf, tham)


NGU_CANH_CHAT = (
    "\n\n# NGỮ CẢNH VẬN HÀNH\n\n"
    "Bạn đang trả lời người vận hành runtime này qua ô chat trên dashboard. "
    "Trả lời ngắn, thẳng, bằng tiếng Việt. Được phép nói thẳng khi số liệu "
    "chưa đủ để kết luận."
)


def _ma_hop_le(x: str) -> bool:
    """Mã chiến lược: HOA, số, gạch dưới, tối đa 40 ký tự."""
    return (bool(x) and len(x) <= 40
            and all(c.isupper() or c.isdigit() or c == "_" for c in x))


def _don_dep_cli(out: dict, label: str) -> None:
    """Dọn những chỗ đường CLI không ép kiểu được. Sửa TẠI CHỖ.

    Trên đường SDK, `output_config.format` ép JSON đúng lược đồ ở tầng API —
    sai kiểu là không nhận. Đường CLI không có cơ chế ấy: lược đồ chỉ là một
    câu trong lời nhắc, và model làm theo phần lớn nhưng không phải luôn luôn.

    Đo được ở lượt chạy thật ĐẦU TIÊN: `strategy` nhận nguyên một đoạn 300 chữ
    lý lẽ. `journal.performance()` gom thống kê theo trường đó, nên mỗi luận
    điểm sẽ thành một "chiến lược" riêng, và bảng theo-chiến-lược vỡ vụn thành
    hàng chục dòng dùng đúng một lần — không sai con số nào, và vô dụng.

    Sửa thay vì vứt cả luận điểm: phần còn lại vẫn dùng được, và bỏ một lượt
    suy luận đã tốn 40k token vì một trường sai định dạng thì quá đắt.
    """
    ma = out.get("strategy")
    if not isinstance(ma, str):
        return
    if not _ma_hop_le(ma):
        out["strategy"] = "CLI_V1"
        bus.log("brain", "don-dep",
                f"{label}: `strategy` không phải mã ({len(ma)} ký tự) - đổi thành CLI_V1")
        return
    # Và không được là HÀNH ĐỘNG. Đo được trong sổ: NO_TRADE, NO_TRADE_MTF_CONFLICT,
    # NO_TRADE_STAT_GATE… — chúng qua được phép kiểm ký tự (HOA + gạch dưới) nhưng
    # trả lời sai câu hỏi. `strategy` hỏi "bộ luật nào", không hỏi "lần này làm gì";
    # lý do thuộc về `reason_codes`. Trộn lại thì bảng theo-chiến-lược vỡ thành
    # hàng chục dòng dùng một lần, đúng như lần trước.
    if ma.split("_")[0] in ("NO", "LONG", "SHORT") or ma.startswith("NO_TRADE"):
        out["strategy"] = "CLI_V1"
        bus.log("brain", "don-dep",
                f"{label}: `strategy`=«{ma}» là hành động chứ không phải bộ luật"
                f" - đổi thành CLI_V1")

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
        # Mỗi chế độ một câu RIÊNG. Câu cũ chia hai: "claude" thì im, còn lại thì
        # "(không gọi API, không tốn tiền)" — với `cli` thì nửa đầu đúng và nửa
        # sau SAI: nó gọi model thật và tiêu quota gói. Một dòng log trấn an sai
        # là thứ khiến người ta thôi để mắt tới đúng chỗ cần để mắt.
        _giai_thich = {
            "claude": "",
            "cli": " (qua claude CLI — không tốn TIỀN, nhưng CÓ tiêu quota gói)",
            "mock": " (luật thuần, không gọi model, không tốn gì)",
        }
        bus.log("brain", "che-do",
                f"brain = {self.mode.upper()}" + _giai_thich.get(self.mode, ""))

    # System prompt là phần ỔN ĐỊNH của mọi lượt gọi, nên nó được cache. Đặt
    # dữ liệu biến thiên (giá, feature) vào message chứ không vào đây — nhét
    # timestamp vào system prompt là tự huỷ cache mà không có gì báo.
    def _system_text(self) -> str:
        """Lời nhắc hệ thống dưới dạng CHUỖI THUẦN.

        Tách ra vì hai đường tiêu thụ nó khác hình dạng: SDK muốn danh sách
        khối (để gắn `cache_control`), CLI muốn một chuỗi cho
        `--system-prompt`. Trước đây chỉ có `_system()` trả danh sách, và
        đường CLI đưa thẳng danh sách ấy vào `subprocess`:

            TypeError: expected str, bytes or os.PathLike object, not list

        Mọi lượt gọi hỏng, hệ rơi về mock. Và KHÔNG CÓ GÌ trên bảng báo sai —
        đường rơi-về-mock làm đúng việc của nó, bot vẫn vào lệnh, chỉ là bằng
        luật thuần. Chỉ dòng `loi-cli` trong nhật ký là biết. Đây là lý do
        phải đọc nhật ký sau mỗi lần nối một đường mới, chứ không chỉ nhìn
        bảng xem có xanh không.
        """
        return SYSTEM_RULES + ("\n\n# KHO KỸ NĂNG\n\n" + self.skills if self.skills else "")
    def _system(self) -> list[dict]:
        return [{"type": "text", "text": self._system_text(),
                 "cache_control": {"type": "ephemeral"}}]

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

    def _goi_duoc(self) -> bool:
        """Có đường nào tới model thật không.

        Gom về MỘT chỗ. Trước đây câu hỏi này được viết lại ba lần dưới dạng
        `mode != "claude" or not self.client`, nên thêm đường CLI là phải nhớ
        sửa đủ ba chỗ — quên một chỗ thì bộ não lặng lẽ rơi về mock ở đúng chức
        năng đó, và không có gì báo.
        """
        if self.mode == "cli":
            return True
        return self.mode == "claude" and bool(self.client)

    async def _structured_cli(self, *, user: str, schema: dict, label: str) -> dict | None:
        """Một lượt gọi qua `claude` CLI — quota gói, không phải tiền.

        Chạy trong luồng khác: `subprocess.run` chặn, và một lượt mất ~10 giây.
        Để nó chặn vòng lặp async là bỏ lỡ nến, mất SSE, và bảng đứng hình đúng
        khoảng thời gian bộ não đang nghĩ.
        """
        blocked = self.cost.blocked(label)
        if blocked:
            bus.log("brain", "het-han-muc", f"bỏ qua {label}: {blocked}")
            return None
        from . import cli_claude
        try:
            out, usage = await asyncio.to_thread(
                cli_claude.goi, he_thong=self._system_text(), nguoi_dung=user,
                schema=schema, model=self.cfg.get("modelCli", "claude-sonnet-4-6"))
        except Exception as e:  # noqa: BLE001
            self.last_error = f"{type(e).__name__}: {e}"
            bus.log("brain", "loi-cli", f"{label}: {self.last_error}")
            return None
        if not isinstance(out, dict):
            bus.log("brain", "json-hong", f"{label}: phản hồi không phải object")
            return None
        _don_dep_cli(out, label)
        usd = self.cost.record(self.cfg.get("modelCli", "claude-sonnet-4-6"), usage)
        bus.emit("brain", "chi-phi",
                 f"{label} (CLI · quota gói): tương đương ${usd:.4f} · "
                 f"nạp {usage.cache_creation_input_tokens} tok · ra {usage.output_tokens} tok",
                 usd=usd, label=label)
        return out

    async def _structured(self, *, user: str, schema: dict, effort: str, label: str) -> dict | None:
        """Một lượt gọi có schema. Trả về None nếu bị chặn/lỗi/từ chối."""
        if self.mode == "cli":
            return await self._structured_cli(user=user, schema=schema, label=label)
        blocked = self.cost.blocked(label)
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

        if not self._goi_duoc():
            out = mock_thesis(state, regime, primary_tf)
        else:
            out = await self._structured(user=user, schema=THESIS_SCHEMA,
                                         effort=self.cfg.get("effort", "high"), label="thesis")
            if out is None:
                # LỖI bộ não thì rơi về luật thuần để ĐỌC, nhưng KHÔNG được mở
                # vị thế mới.
                #
                # Đã xảy ra: `claude` CLI thoát mã 1 lúc 12:00; hệ rơi về mock;
                # mock ra LONG; risk cho qua; một vị thế thật mở ra kèm OCO. Một
                # tiến trình con chết đã trở thành một quyết định vào lệnh.
                #
                # Lỗi tiến trình không phải bằng chứng gì về thị trường. Và luật
                # thuần ở đây không phải chỗ dựa trung lập: chính nó là
                # MOCK_RULES_V1, đo được −0,047R qua 193 lệnh ngoài mẫu trên 8
                # chợ. Rơi về nó rồi vào lệnh là giao tiền cho một bộ luật đã bị
                # phép đo bác bỏ, vì một lý do chẳng liên quan gì tới thị trường.
                #
                # Vẫn giữ nguyên phần ĐỌC của mock (regime_read, mức giá) — chúng
                # có ích cho người xem bảng. Chỉ chặn phần HÀNH ĐỘNG.
                #
                # Đường HẾT TRẦN thì KHÔNG đi qua đây (xem `_goi_duoc()` ở trên):
                # đó là chế độ suy giảm có chủ ý, người dùng tự đặt trần và biết
                # mình đang đổi gì lấy gì. Lỗi thì không ai chọn.
                out = mock_thesis(state, regime, primary_tf)
                out["reason_codes"].append("FALLBACK_SAU_LOI_BRAIN")
                if out.get("action") != "NO_TRADE":
                    bus.log("brain", "chan-vao-lenh",
                            f"bộ não lỗi → luật thuần đề nghị {out['action']}, "
                            f"đã ép NO_TRADE: lỗi tiến trình không phải lý do vào lệnh")
                    out["action"] = "NO_TRADE"
                    out["reason_codes"].append("EP_NO_TRADE_VI_BRAIN_LOI")
                out["confidence"] = 0.0

        out["symbol"] = state["symbol"]
        # `source` phải nói THẬT ai đã nghĩ ra luận điểm này.
        #
        # Bản cũ chỉ nhận mode "claude"; khi thêm đường "cli" thì mọi quyết định
        # của bộ não THẬT bị ghi là "mock". Sổ luận điểm khi đó nói rằng bộ não
        # chưa từng chạy — và ai đọc lại về sau sẽ tin đúng như thế, vì không có
        # gì mâu thuẫn với nó ngoài mấy dòng chi phí trong nhật ký.
        roi_ve_mock = "FALLBACK_SAU_LOI_BRAIN" in (out.get("reason_codes") or [])
        out["source"] = ("mock" if (roi_ve_mock or self.mode == "mock")
                         else self.mode)      # "claude" hoặc "cli"
        out["regimeFromClassifier"] = regime["primary"]
        out["at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        store.append(store.THESES, out)
        bus.emit("brain", "luan-diem",
                 f"{out['action']} · tin cậy {out['confidence']:.2f} · đọc regime {out['regime_read']} · {out['strategy']}",
                 thesis=out)
        return out

    async def postmortem(self, trade: dict, regime_now: dict) -> dict:
        if not self._goi_duoc():
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
        if not self._goi_duoc():
            yield ("Brain đang ở chế độ **mock** nên không có mô hình để trả lời.\n\n"
                   "Đặt `ANTHROPIC_API_KEY` trong `.env` rồi khởi động lại là chat hoạt động. "
                   "Mọi tầng khác — dữ liệu, chỉ báo, regime, risk engine, sàn giấy, nhật ký — "
                   "vẫn đang chạy thật và bạn xem được ở các panel bên phải.")
            return
        blocked = self.cost.blocked()
        if blocked:
            yield f"Hết hạn mức chi phí hôm nay ({blocked}). Sửa `brain.dailyBudgetUsd` trong `config.json` nếu muốn nới."
            return

        if self.mode == "cli":
            # CLI trả cả câu trong MỘT lượt, không phát từng chữ. Người dùng sẽ
            # thấy khoảng lặng 30-90 giây rồi cả đoạn hiện ra — phải nói trước,
            # nếu không nó trông y hệt như treo máy và người ta bấm lại.
            from . import cli_claude
            yield ("_Đang hỏi bộ não qua Claude CLI (quota gói). Nó trả nguyên đoạn "
                   "chứ không phát từng chữ, thường mất 30-90 giây…_\n\n")
            hoi = (_fmt_state(context) + '\n\n'
                   + (messages[-1].get("content", "") if messages else ""))
            try:
                tra, usage = await asyncio.to_thread(
                    cli_claude.goi,
                    he_thong=self._system_text() + NGU_CANH_CHAT,
                    nguoi_dung=hoi, schema=None,
                    model=self.cfg.get("model", "claude-sonnet-4-6"))
            except Exception as e:  # noqa: BLE001
                self.last_error = f"{type(e).__name__}: {e}"
                bus.log("brain", "loi-cli", f"chat: {self.last_error}")
                yield f"Lỗi khi gọi Claude CLI: {self.last_error}"
                return
            self.cost.record(self.cfg.get("model", "claude-sonnet-4-6"), usage)
            yield str(tra or "(không có nội dung trả về)")
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
