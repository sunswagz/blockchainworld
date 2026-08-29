"""EXECUTION — sàn giấy (paper broker).

M0 chạy trên tiền giả nhưng tính phí và trượt giá thật, vì bỏ hai thứ đó ra thì
mọi thống kê win-rate sau này đều lạc quan giả tạo và không ai phát hiện được.

Vòng đời một vị thế ở đây rất hẹp: mở → chạm SL hoặc chạm TP1 → đóng.
Trailing, chốt từng phần, dời SL về hoà vốn — để dành mốc sau; thêm bây giờ là
thêm nhánh chưa có nhật ký nào kiểm chứng.
"""
from __future__ import annotations

import datetime as _dt
import uuid

from .config import CONFIG
from .bus import bus
from . import store


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _utc_day() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


class PaperBroker:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.state = store.read_json(store.ACCOUNT) or self._fresh()
        self._touch_day()

    def _fresh(self) -> dict:
        eq = self.cfg["startingEquity"]
        return {
            "equity": eq, "cash": eq, "peakEquity": eq,
            "positions": [], "closedCount": 0,
            "dailyPnl": {}, "dailyStartEquity": {},
            "createdAt": _now(),
        }

    def reset(self) -> dict:
        self.state = self._fresh()
        self._touch_day()
        self._save()
        bus.log("exec", "reset", "tài khoản paper đã đặt lại")
        return self.state

    def _touch_day(self) -> None:
        d = _utc_day()
        self.state.setdefault("dailyPnl", {}).setdefault(d, 0.0)
        self.state.setdefault("dailyStartEquity", {}).setdefault(d, self.state["equity"])

    def _save(self) -> None:
        store.write_json(store.ACCOUNT, self.state)

    # ── Mở vị thế ─────────────────────────────────────────────────────────
    def open(self, pos: dict, thesis: dict, regime: dict) -> dict:
        bps = (self.cfg["feeBps"] + self.cfg["slippageBps"]) / 10_000
        # Trượt giá luôn đi NGƯỢC chiều mình: long khớp cao hơn, short khớp thấp hơn.
        fill = pos["entry"] * (1 + bps) if pos["side"] == "LONG" else pos["entry"] * (1 - bps)
        fee = pos["notional"] * self.cfg["feeBps"] / 10_000

        # Risk Engine tính size trên giá YÊU CẦU; lệnh khớp ở giá ĐÃ TRƯỢT.
        # Ghi lại rủi ro theo giá khớp thật, vì R-multiple là tín hiệu học chính
        # của hậu kiểm — ghi theo giá yêu cầu là mọi bài học đều dựa trên một
        # mẫu số đẹp hơn thực tế, và không có gì báo.
        real_stop_dist = abs(fill - pos["stopLoss"])
        real_risk = real_stop_dist * pos["qty"]
        real_rr = (abs(pos["targets"][0] - fill) / real_stop_dist) if real_stop_dist > 0 else None

        trade = {
            "id": f"t_{uuid.uuid4().hex[:10]}",
            "openedAt": _now(),
            "symbol": thesis.get("symbol"),
            "side": pos["side"],
            "qty": pos["qty"],
            "entry": round(fill, 2),
            "requestedEntry": pos["entry"],
            "stopLoss": pos["stopLoss"],
            "targets": pos["targets"],
            "riskAmount": round(real_risk, 2),
            "plannedRiskAmount": pos["riskAmount"],
            "slippageCostOnRisk": round(real_risk - pos["riskAmount"], 2),
            "riskPct": pos["riskPct"],
            "rr": round(real_rr, 2) if real_rr else None,
            "plannedRr": pos["rr"],
            "stopAtrMultiple": pos["stopAtrMultiple"],
            "feesPaid": round(fee, 2),
            "regimeAtEntry": regime.get("primary"),
            "regimeKey": regime.get("key"),
            # KHUNG lúc mở lệnh. Cùng lý do với bài học chạy lại: một chế độ
            # trên 1h và trên 4h là hai thị trường khác nhau mang chung tên, và
            # sổ giao dịch trộn hai khung lại thì mọi thống kê theo chế độ đều
            # là trung bình của hai thứ không so được với nhau.
            "khung": CONFIG["timeframes"]["primary"],
            "strategy": thesis.get("strategy"),
            "confidence": thesis.get("confidence"),
            "reasonCodes": thesis.get("reason_codes", []),
            "thesisSummary": thesis.get("reasoning", "")[:600],
            "status": "OPEN",
        }
        self.state["positions"].append(trade)
        self.state["cash"] -= fee
        self._save()
        bus.log("exec", "mo-vi-the",
                f"{trade['side']} {trade['qty']:.6f} @ {trade['entry']:,.2f} · SL {trade['stopLoss']:,.2f} · "
                f"TP1 {trade['targets'][0]:,.2f} · risk ${trade['riskAmount']} (kế hoạch ${pos['riskAmount']}) · RR {trade['rr']}",
                trade=trade)
        return trade

    # ── Cập nhật theo giá & đóng khi chạm ─────────────────────────────────
    def mark(self, price: float | dict) -> list[dict]:
        """Chạm SL/TP thì đóng. Trong một nến, nếu cả hai cùng nằm trong biên độ,
        giả định SL chạm trước — đó là giả định BI QUAN, cố ý: mọi giả định lạc
        quan trong backtest đều quay lại thành lỗ thật.

        `price` nhận MỘT SỐ (một chợ, cách cũ) hoặc MỘT TỪ ĐIỂN {chợ: giá}.

        Bản cũ chỉ nhận một số và áp nó lên MỌI vị thế. Đúng chừng nào bot còn
        đánh một coin. Mở ra nhiều coin thì nó thành hỏng nặng và im lặng: vị
        thế ETH bị chấm bằng giá BTC, chạm stop ở một mức chẳng liên quan gì,
        và sổ giao dịch ghi lại một con số lãi/lỗ hoàn toàn bịa.

        Vị thế nào KHÔNG có giá của chính chợ nó thì BỎ QUA, không chấm. Thà
        giữ một vị thế thêm một vòng còn hơn đóng nó ở giá của coin khác — và
        đó là lý do chỗ này không có đường "rơi về giá mặc định".
        """
        closed = []
        for t in list(self.state["positions"]):
            if isinstance(price, dict):
                gia = price.get(t.get("symbol"))
                if gia is None:
                    continue
            else:
                gia = price
            hit = None
            if t["side"] == "LONG":
                if gia <= t["stopLoss"]:
                    hit = ("STOP_LOSS", t["stopLoss"])
                elif gia >= t["targets"][0]:
                    hit = ("TAKE_PROFIT", t["targets"][0])
            else:
                if gia >= t["stopLoss"]:
                    hit = ("STOP_LOSS", t["stopLoss"])
                elif gia <= t["targets"][0]:
                    hit = ("TAKE_PROFIT", t["targets"][0])
            if hit:
                closed.append(self.close(t, hit[1], hit[0]))
        if closed:
            self._save()
        return closed

    def close(self, trade: dict, exit_price: float, reason: str) -> dict:
        bps = (self.cfg["feeBps"] + self.cfg["slippageBps"]) / 10_000
        fill = exit_price * (1 - bps) if trade["side"] == "LONG" else exit_price * (1 + bps)
        direction = 1 if trade["side"] == "LONG" else -1
        gross = (fill - trade["entry"]) * direction * trade["qty"]
        fee = fill * trade["qty"] * self.cfg["feeBps"] / 10_000
        pnl = gross - fee

        trade.update({
            "status": "CLOSED",
            "closedAt": _now(),
            "exit": round(fill, 2),
            "exitReason": reason,
            "grossPnl": round(gross, 2),
            "feesPaid": round(trade["feesPaid"] + fee, 2),
            "pnl": round(pnl, 2),
            "rMultiple": round(pnl / trade["riskAmount"], 2) if trade["riskAmount"] else None,
            "holdingMinutes": _minutes_between(trade["openedAt"], _now()),
        })

        self.state["positions"] = [p for p in self.state["positions"] if p["id"] != trade["id"]]
        self.state["equity"] += pnl
        self.state["cash"] += pnl
        self.state["peakEquity"] = max(self.state.get("peakEquity", 0), self.state["equity"])
        self.state["closedCount"] = self.state.get("closedCount", 0) + 1
        d = _utc_day()
        self._touch_day()
        self.state["dailyPnl"][d] = round(self.state["dailyPnl"].get(d, 0.0) + pnl, 2)
        self._save()

        store.append(store.TRADES, trade)
        bus.log("exec", "dong-vi-the",
                f"{reason} @ {trade['exit']:,.2f} · PnL ${trade['pnl']:+,.2f} ({trade['rMultiple']:+}R) · equity ${self.state['equity']:,.2f}",
                trade=trade)
        return trade

    def snapshot(self, price: float | None = None) -> dict:
        s = dict(self.state)
        open_pnl = 0.0
        positions = []
        # Giá của CHÍNH chợ vị thế đó — sàn giấy cũng giữ nhiều chợ được. Một
        # giá chung ở đây là lãi/lỗ chưa chốt của SOL tính bằng giá BTC.
        _gm = price if isinstance(price, dict) else ({"*": price} if price else {})
        for t in self.state["positions"]:
            p = dict(t)
            _g = _gm.get(t.get("symbol")) or _gm.get("*")
            if _g:
                d = 1 if t["side"] == "LONG" else -1
                p["unrealizedPnl"] = round((_g - t["entry"]) * d * t["qty"], 2)
                p["unrealizedR"] = round(p["unrealizedPnl"] / t["riskAmount"], 2) if t["riskAmount"] else None
                open_pnl += p["unrealizedPnl"]
            positions.append(p)
        s["positions"] = positions
        s["openPnl"] = round(open_pnl, 2)
        # Sàn giấy giữ toàn bộ vốn bằng tiền mặt nên "mua được" = "vốn". Vẫn khai
        # ra để Risk Engine chỉ có MỘT đường tính, không phải rẽ nhánh theo sàn.
        s["availableQuote"] = round(self.state["cash"], 2)
        # Sàn giấy tự giữ sổ nên vốn LUÔN biết. Vẫn khai tường minh thay vì dựa
        # vào giá trị mặc định của Risk Engine: hôm nào mặc định đổi chiều thì
        # sàn giấy im lặng đi theo, và phép kiểm sẽ vẫn xanh.
        s["equityKnown"] = True
        s["equityMarked"] = round(self.state["equity"] + open_pnl, 2)
        peak = self.state.get("peakEquity", self.state["equity"]) or 1
        s["drawdownPct"] = round(max(0.0, (peak - s["equityMarked"]) / peak * 100), 2)
        s["todayPnl"] = round(self.state.get("dailyPnl", {}).get(_utc_day(), 0.0), 2)
        return s


def _minutes_between(a: str, b: str) -> int:
    try:
        return int((_dt.datetime.fromisoformat(b) - _dt.datetime.fromisoformat(a)).total_seconds() // 60)
    except Exception:  # noqa: BLE001
        return 0
