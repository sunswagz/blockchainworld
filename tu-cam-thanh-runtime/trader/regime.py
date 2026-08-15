"""MARKET REGIME — trả lời "thị trường đang là gì?" TRƯỚC khi hỏi "mua hay bán?".

Cố ý viết bằng luật xác định, không gọi model. Ba lý do:

1. Rẻ. Chạy mỗi 20 giây mà gọi model thì hết tiền trước khi có kết quả nào.
2. Ổn định. Cùng một dữ liệu phải ra cùng một regime, nếu không thì thống kê
   "chiến lược nào tốt trong regime nào" là vô nghĩa — mẫu số cứ trôi.
3. Kiểm được. Sai thì sửa được ngưỡng và biết chắc mình vừa sửa gì.

Brain vẫn được phép ĐỌC regime này rồi nói nó sai (trường `regime_read`), và chỗ
lệch nhau đó được ghi lại — đó là dữ liệu để chỉnh ngưỡng, không phải lỗi.
"""
from __future__ import annotations

REGIMES = [
    "TREND_UP", "TREND_DOWN", "RANGE", "BREAKOUT",
    "HIGH_VOLATILITY", "LOW_VOLATILITY", "UNKNOWN",
]


def classify(state: dict, primary_tf: str, context_tf: str) -> dict:
    p = state["timeframes"][primary_tf]
    ctx = state["timeframes"].get(context_tf, {})

    adx = p.get("adx")
    stack = p.get("emaStack")
    struct = p.get("structure")
    volatility = p.get("volatility")
    bb_width = p.get("bbWidthPct")
    vol_ratio = p.get("volumeRatio")
    price = p.get("price")
    hi20, lo20 = p.get("range20High"), p.get("range20Low")

    flags: list[str] = []
    reasons: list[str] = []

    trending = adx is not None and adx >= 22
    weak = adx is not None and adx < 18

    primary = "UNKNOWN"
    if trending and stack == "BULLISH_ALIGNED" and struct in ("UPTREND", "TRANSITION"):
        primary = "TREND_UP"
        reasons.append(f"ADX {adx} ≥ 22, EMA xếp tăng, cấu trúc {struct}")
    elif trending and stack == "BEARISH_ALIGNED" and struct in ("DOWNTREND", "TRANSITION"):
        primary = "TREND_DOWN"
        reasons.append(f"ADX {adx} ≥ 22, EMA xếp giảm, cấu trúc {struct}")
    elif weak:
        primary = "RANGE"
        reasons.append(f"ADX {adx} < 18 — không bên nào kiểm soát")
    else:
        primary = "UNKNOWN"
        reasons.append(f"ADX {adx} ở vùng lưng chừng, EMA {stack}")

    # Breakout đè lên nhãn trên: giá vượt biên 20 nến KÈM khối lượng.
    # Thiếu vế khối lượng thì phần lớn là quét thanh khoản, không phải breakout.
    if price is not None and hi20 is not None and vol_ratio is not None:
        if price > hi20 and vol_ratio > 1.4:
            primary = "BREAKOUT"
            flags.append("BREAKOUT_UP")
            reasons.append(f"giá {price} vượt đỉnh 20 nến {hi20} với volume ×{vol_ratio}")
        elif price < lo20 and vol_ratio > 1.4:
            primary = "BREAKOUT"
            flags.append("BREAKOUT_DOWN")
            reasons.append(f"giá {price} thủng đáy 20 nến {lo20} với volume ×{vol_ratio}")

    if volatility == "HIGH":
        flags.append("HIGH_VOLATILITY")
        reasons.append(f"ATR gấp {p.get('atrRatioVsMedian')}× trung vị")
    elif volatility == "LOW":
        flags.append("LOW_VOLATILITY")
        if bb_width is not None:
            reasons.append(f"dải Bollinger co còn {bb_width}%")

    # Khung lớn nói ngược khung nhỏ là lý do chính đáng để đứng ngoài.
    ctx_stack = ctx.get("emaStack")
    conflict = bool(
        ctx_stack and stack and ctx_stack != "MIXED" and stack != "MIXED" and ctx_stack != stack
    )
    if conflict:
        flags.append("MTF_CONFLICT")
        reasons.append(f"{context_tf} {ctx_stack} ngược {primary_tf} {stack}")

    # Chất lượng regime — dùng để quyết định CÓ ĐÁNG gọi brain không.
    quality = "HIGH"
    if primary == "UNKNOWN" or conflict:
        quality = "LOW"
    elif primary == "RANGE" and volatility == "LOW":
        quality = "MEDIUM"

    return {
        "primary": primary,
        "flags": flags,
        "quality": quality,
        "reasons": reasons,
        "contextTrend": ctx_stack,
        "adx": adx,
        "volatility": volatility,
        "key": f"{primary}|{'+'.join(sorted(flags)) or 'none'}",
    }
