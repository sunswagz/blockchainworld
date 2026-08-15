"""RISK ENGINE — bức tường cứng giữa Claude và tiền.

Nguyên tắc duy nhất của file này: **nó không tranh luận với Claude.**

Claude được phép phân tích, suy luận, đề xuất lệnh, đề xuất SL/TP, giải thích.
Claude KHÔNG được phép: tự ý bỏ stop loss, tự tăng position, tự tăng đòn bẩy,
gấp thếp, hay vượt giới hạn drawdown. `confidence = 0.99` cũng không mua thêm
được một xu rủi ro nào — confidence chỉ dùng để TỪ CHỐI (dưới ngưỡng thì loại),
không bao giờ dùng để nới.

Toàn bộ file là Python thuần, không gọi model, không đọc mạng. Đọc hết trong
một lượt là biết chắc số tiền tối đa có thể mất trong một lệnh.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

EPS = 1e-9


def _utc_day() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


class RiskEngine:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.halted_reason: str | None = None  # kill switch thủ công hoặc do drawdown

    # ── Ngắt mạch: kiểm TRƯỚC mọi thứ khác ────────────────────────────────
    def circuit_breakers(self, account: dict) -> list[str]:
        c, out = self.cfg, []
        if self.halted_reason:
            out.append(f"HALTED: {self.halted_reason}")

        equity = account["equity"]
        peak = account.get("peakEquity", equity)
        dd_pct = 0.0 if peak <= 0 else (peak - equity) / peak * 100
        if dd_pct >= c["maxDrawdownPct"]:
            reason = f"drawdown {dd_pct:.2f}% ≥ trần {c['maxDrawdownPct']}%"
            self.halted_reason = reason  # dính trần drawdown là dừng hẳn, không tự mở lại
            out.append(f"KILL_SWITCH: {reason}")

        day = _utc_day()
        day_pnl = account.get("dailyPnl", {}).get(day, 0.0)
        start_of_day = account.get("dailyStartEquity", {}).get(day, equity)
        if start_of_day > 0:
            loss_pct = -day_pnl / start_of_day * 100
            if loss_pct >= c["maxDailyLossPct"]:
                out.append(f"DAILY_LOSS: lỗ {loss_pct:.2f}% hôm nay ≥ trần {c['maxDailyLossPct']}% — nghỉ tới 00:00 UTC")

        if len(account.get("positions", [])) >= c["maxOpenPositions"]:
            out.append(f"MAX_POSITIONS: đang giữ {len(account['positions'])}/{c['maxOpenPositions']} vị thế")
        return out

    # ── Thẩm định một luận điểm ───────────────────────────────────────────
    def evaluate(self, thesis: dict, state: dict, account: dict, atr: float | None) -> dict:
        c = self.cfg
        rejections: list[str] = []
        action = thesis.get("action", "NO_TRADE")

        if action == "NO_TRADE":
            return {"approved": False, "action": "NO_TRADE",
                    "rejections": [], "note": "brain chủ động không vào lệnh", "position": None}

        rejections += self.circuit_breakers(account)

        price = float(state["price"])
        requested = _pick_entry(thesis, price)
        # Thẩm định trên GIÁ KHỚP DỰ KIẾN, không phải giá yêu cầu.
        #
        # Trượt giá và phí luôn đẩy điểm vào đi ngược mình: stop xa thêm, mục tiêu
        # gần lại. Gác RR trên giá yêu cầu là gác một con số không bao giờ xảy ra —
        # đo thật trên BTC 1H thấy RR "2.0" thành 1.15 sau 15bps. Cái trần 2.0 khi
        # đó chỉ là hư cấu, và nó hư cấu theo hướng cho lệnh đi qua.
        cost_bps = (c["feeBps"] + c["slippageBps"]) / 10_000
        side = 1 if action == "LONG" else -1
        entry = requested * (1 + cost_bps) if side == 1 else requested * (1 - cost_bps)

        sl = thesis.get("invalidation")
        targets = [t for t in (thesis.get("targets") or []) if isinstance(t, (int, float))]
        conf = float(thesis.get("confidence") or 0)

        # — Tính hợp lệ hình học của lệnh —
        if sl is None:
            rejections.append("THIẾU_SL: không có điểm vô hiệu hoá luận điểm")
        if not targets:
            rejections.append("THIẾU_TP: không có mục tiêu nào")

        if sl is not None:
            if side == 1 and sl >= entry:
                rejections.append(f"SL_SAI_PHÍA: long mà SL {sl} ≥ entry {entry}")
            if side == -1 and sl <= entry:
                rejections.append(f"SL_SAI_PHÍA: short mà SL {sl} ≤ entry {entry}")
        for t in targets:
            if side == 1 and t <= entry:
                rejections.append(f"TP_SAI_PHÍA: long mà TP {t} ≤ entry {entry}")
            if side == -1 and t >= entry:
                rejections.append(f"TP_SAI_PHÍA: short mà TP {t} ≥ entry {entry}")

        # HAI khoảng cách cho HAI câu hỏi khác nhau — đừng gộp:
        #   structural_dist (từ giá tham chiếu) → "stop có nằm trong vùng nhiễu không?"
        #                                          Đó là câu hỏi về cấu trúc giá.
        #   stop_dist       (từ giá khớp)       → "mất bao nhiêu tiền?"
        #                                          Đó là câu hỏi về kế toán.
        # Gộp lại thì luật SL-quá-hẹp chết hẳn: riêng trượt giá ở đây đã 0.6×ATR,
        # tự nó vượt ngưỡng 0.3, nên không stop nào còn bị coi là hẹp nữa.
        stop_dist = abs(entry - sl) if sl is not None else None
        structural_dist = abs(requested - sl) if sl is not None else None

        # — SL phải hợp lý so với biến động thực tế —
        # Quá hẹp thì chết vì nhiễu; quá rộng thì một lệnh nuốt cả tuần lãi.
        if structural_dist and atr:
            k = structural_dist / atr
            if k < c["minStopAtr"] - EPS:
                rejections.append(f"SL_QUÁ_HẸP: {k:.2f}×ATR < {c['minStopAtr']}×ATR — sẽ chết vì nhiễu")
            if k > c["maxStopAtr"] + EPS:
                rejections.append(f"SL_QUÁ_RỘNG: {k:.2f}×ATR > {c['maxStopAtr']}×ATR")

        # — Risk/Reward tính trên TP ĐẦU TIÊN, không phải TP xa nhất —
        # Lấy TP xa nhất là cách tự lừa mình: RR đẹp trên giấy, chốt non trên thực tế.
        # EPS: luật là "RR ≥ ngưỡng", nhưng 3·ATR / 1.5·ATR trong dấu phẩy động
        # ra 1.9999999999999998 và bị chặn nhầm. Nới đúng một phần tỉ để so sánh
        # khớp với luật đã viết — không phải nới luật.
        rr = None
        if stop_dist and targets:
            rr = abs(targets[0] - entry) / stop_dist
            if rr < c["minRR"] - EPS:
                rejections.append(f"RR_THẤP: {rr:.2f} < tối thiểu {c['minRR']}")

        if conf < c["minConfidence"] - EPS:
            rejections.append(f"CONFIDENCE_THẤP: {conf:.2f} < {c['minConfidence']}")

        if rejections:
            return {"approved": False, "action": action, "rejections": rejections,
                    "rr": rr, "position": None,
                    "note": "; ".join(rejections[:3])}

        # — Sizing: TÍNH LẠI TỪ ĐẦU, không đọc đề xuất của brain —
        # Brain có gợi ý `suggested_risk_pct`, ở đây nó bị cắt trần chứ không được tin.
        suggested = float(thesis.get("suggested_risk_pct") or c["maxRiskPerTradePct"])
        risk_pct = min(max(suggested, 0.0), c["maxRiskPerTradePct"])
        capped = suggested > c["maxRiskPerTradePct"]

        risk_amount = account["equity"] * risk_pct / 100
        qty = risk_amount / stop_dist
        notional = qty * entry
        max_notional = account["equity"] * c["maxNotionalPctOfEquity"] / 100
        notional_capped = False
        if notional > max_notional:
            qty = max_notional / entry
            notional = max_notional
            risk_amount = qty * stop_dist
            notional_capped = True

        return {
            "approved": True,
            "action": action,
            "rejections": [],
            "rr": rr,
            "note": (f"đã hạ risk {suggested}% → {risk_pct}% theo trần" if capped else "trong hạn mức"),
            "position": {
                "side": action,
                "entry": round(requested, 2),
                "expectedFill": round(entry, 2),
                "costDragOnEntry": round(abs(entry - requested), 2),
                "stopLoss": round(sl, 2),
                "targets": [round(t, 2) for t in targets],
                "qty": qty,
                "notional": round(notional, 2),
                "riskAmount": round(risk_amount, 2),
                "riskPct": round(risk_pct, 4),
                "stopDistance": round(stop_dist, 2),
                "structuralStopDistance": round(structural_dist, 2),
                "stopAtrMultiple": round(structural_dist / atr, 2) if atr else None,
                "rr": round(rr, 2) if rr else None,
                "suggestedRiskPct": suggested,
                "riskPctCapped": capped,
                "notionalCapped": notional_capped,
            },
        }


def _pick_entry(thesis: dict, price: float) -> float:
    """Vùng entry của brain chỉ dùng khi giá HIỆN TẠI còn nằm trong đó.

    Giá đã chạy khỏi vùng mà vẫn khớp ở mép vùng là tự vẽ ra một mức vào lệnh
    không tồn tại — RR sau đó sai theo, và sai theo hướng có lợi cho mình.
    """
    zone = thesis.get("entry_zone") or []
    nums = [float(z) for z in zone if isinstance(z, (int, float))]
    if len(nums) == 2:
        lo, hi = min(nums), max(nums)
        if lo <= price <= hi:
            return price
    return price
