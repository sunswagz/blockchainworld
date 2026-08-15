"""EXECUTION — Binance Spot Testnet.

Cùng giao diện với `PaperBroker` (open/mark/close/snapshot/reset) để `loop.py`
không phải biết mình đang chạy sàn nào. Khác nhau ở ba chỗ căn bản, và cả ba
đều là chỗ sàn giấy đang nói dối một cách tử tế:

**Vốn không do mình giữ sổ.** Sàn giấy tự cộng trừ `equity`; ở đây vốn ĐỌC TỪ
SÀN mỗi vòng (USDT + BTC×giá). Số của mình chỉ là ý kiến, số của sàn mới là sự thật.

**Thoát lệnh do sàn giữ, không do vòng lặp.** Vào lệnh xong là đặt ngay một OCO
(chốt lãi + cắt lỗ). Nếu quản TP/SL bằng vòng lặp Python thì tắt máy, mất điện,
hay một exception là vị thế nằm trần không ai canh. OCO nằm trên sổ lệnh của sàn
và sống tiếp kể cả khi runtime chết.

**Spot không short được.** Bán thứ mình không có là lệnh bị từ chối. Luận điểm
SHORT bị chặn ở Risk Engine (cờ `spot_only`) chứ không để rơi xuống tới đây rồi
mới nổ — chặn muộn thì đã tốn một lượt gọi model.

Còn thiếu ở M0.5, ghi ra để đừng ai tưởng đã có: khớp một phần (partial fill)
chỉ được xử lý thô, và không có cơ chế nối lại vị thế nếu runtime chết đúng lúc
giữa lệnh MARKET và lệnh OCO — xem `doi_soat()`.
"""
from __future__ import annotations

import datetime as _dt
import uuid
from decimal import Decimal

from .bus import bus
from .exchange import BinanceError, TestnetClient
from . import store

ACCOUNT_FILE = "account_testnet.json"


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _utc_day() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")


class TestnetBroker:
    """Sàn thật, khớp thật, tiền giả."""

    kind = "testnet"

    def __init__(self, cfg: dict, symbol: str) -> None:
        self.cfg = cfg
        self.symbol = symbol
        self.client = TestnetClient()
        self.state = store.read_json(ACCOUNT_FILE) or self._fresh()
        self.ready = False
        self.last_error: str | None = None
        self._connect()
        self._touch_day()

    # ── kết nối ────────────────────────────────────────────────────────────
    def _fresh(self) -> dict:
        return {"positions": [], "closedCount": 0, "dailyPnl": {},
                "dailyStartEquity": {}, "peakEquity": 0.0, "createdAt": _now()}

    def _connect(self) -> None:
        if not self.client.has_keys:
            self.last_error = ("thiếu BINANCE_TESTNET_KEY / BINANCE_TESTNET_SECRET trong .env — "
                               "lấy ở https://testnet.binance.vision")
            bus.log("exec", "testnet-thieu-khoa", self.last_error)
            return
        try:
            self.client.ping()
            lech = self.client.sync_time()
            f = self.client.filters(self.symbol)
            bal = self.client.balances()
            self.ready = True
            self.last_error = None
            bus.log("exec", "testnet-noi-duoc",
                    f"đã nối Binance Spot Testnet · lệch đồng hồ {lech}ms · "
                    f"bước KL {f['stepSize']} · bước giá {f['tickSize']} · "
                    f"tối thiểu ${f['minNotional']} · số dư: " +
                    ", ".join(f"{k} {v['total']:g}" for k, v in list(bal.items())[:4]))
        except BinanceError as e:
            self.last_error = str(e)
            bus.log("exec", "testnet-loi-noi", self.last_error)
        except Exception as e:  # noqa: BLE001
            self.last_error = f"{type(e).__name__}: {e}"
            bus.log("exec", "testnet-loi-noi", self.last_error)

    # ── sổ sách ────────────────────────────────────────────────────────────
    def _touch_day(self) -> None:
        d = _utc_day()
        self.state.setdefault("dailyPnl", {}).setdefault(d, 0.0)

    def _save(self) -> None:
        store.write_json(ACCOUNT_FILE, self.state)

    def _equity(self, price: float) -> float:
        """Vốn quy về USDT. Đọc từ sàn — sổ của mình không có quyền nói khác."""
        f = self.client.filters(self.symbol)
        bal = self.client.balances()
        quote = bal.get(f["quote"], {}).get("total", 0.0)
        base = bal.get(f["base"], {}).get("total", 0.0)
        return quote + base * price

    def reset(self) -> dict:
        """Huỷ mọi lệnh treo và xoá sổ vị thế cục bộ.

        KHÔNG nạp lại số dư — số dư testnet do Binance cấp, mình không đặt được.
        Hết tiền thì tạo khoá mới ở testnet.binance.vision.
        """
        if self.ready:
            try:
                self.client.cancel_all(self.symbol)
            except BinanceError as e:
                bus.log("exec", "testnet-huy-loi", str(e))
        self.state = self._fresh()
        self._touch_day()
        self._save()
        bus.log("exec", "reset", "đã huỷ lệnh treo và xoá sổ vị thế cục bộ (số dư testnet giữ nguyên)")
        return self.state

    # ── vào lệnh ───────────────────────────────────────────────────────────
    def open(self, pos: dict, thesis: dict, regime: dict) -> dict | None:
        if not self.ready:
            bus.log("exec", "testnet-chua-san-sang", f"bỏ lệnh: {self.last_error}")
            return None
        if pos["side"] != "LONG":
            bus.log("exec", "testnet-tu-choi", "spot không short được — lệnh bị bỏ")
            return None

        sym = self.symbol
        qty = self.client.round_qty(sym, pos["qty"])
        why = self.client.check_order(sym, qty, pos["entry"])
        if why:
            bus.log("exec", "testnet-khong-hop-le", f"bỏ lệnh: {why}")
            return None

        # Đủ USDT để mua không? Thiếu thì báo rõ chứ đừng để sàn trả -2010 khó đọc.
        try:
            f = self.client.filters(sym)
            bal = self.client.balances()
            can = bal.get(f["quote"], {}).get("free", 0.0)
            need = float(qty) * pos["entry"]
            if can < need:
                bus.log("exec", "testnet-thieu-so-du",
                        f"cần {need:.2f} {f['quote']} nhưng chỉ có {can:.2f} — bỏ lệnh")
                return None
        except BinanceError as e:
            bus.log("exec", "testnet-loi-so-du", str(e))
            return None

        # 1. vào lệnh bằng MARKET
        try:
            res = self.client.market_buy(sym, qty)
        except BinanceError as e:
            bus.log("exec", "testnet-loi-vao-lenh", str(e))
            return None

        fills = res.get("fills") or []
        filled_qty = sum(Decimal(x["qty"]) for x in fills) or qty
        cost = sum(Decimal(x["price"]) * Decimal(x["qty"]) for x in fills)
        fill_price = float(cost / filled_qty) if filled_qty else pos["entry"]
        fee = sum(float(x.get("commission", 0)) for x in fills if x.get("commissionAsset") == "USDT")

        # 2. giao việc canh thoát cho SÀN, không cho vòng lặp
        stop = self.client.round_price(sym, pos["stopLoss"])
        # stopLimit đặt dưới stopPrice một chút để lệnh còn khớp được khi giá xuyên nhanh
        stop_limit = self.client.round_price(sym, pos["stopLoss"] * 0.997)
        tp = self.client.round_price(sym, pos["targets"][0], up=True)
        oco_id = None
        oco_err = None
        try:
            oco = self.client.oco_sell(sym, self.client.round_qty(sym, float(filled_qty)),
                                       tp, stop, stop_limit)
            oco_id = oco.get("orderListId")
        except BinanceError as e:
            oco_err = str(e)
            bus.log("exec", "testnet-oco-loi",
                    f"VÀO ĐƯỢC nhưng KHÔNG đặt được OCO: {e} — vị thế đang không có ai canh")

        real_stop_dist = abs(fill_price - float(stop))
        trade = {
            "id": f"t_{uuid.uuid4().hex[:10]}",
            "openedAt": _now(), "symbol": sym, "side": "LONG",
            "qty": float(filled_qty),
            "entry": round(fill_price, 2), "requestedEntry": pos["entry"],
            "stopLoss": float(stop), "targets": [float(tp)],
            "riskAmount": round(real_stop_dist * float(filled_qty), 2),
            "plannedRiskAmount": pos["riskAmount"],
            "riskPct": pos["riskPct"],
            "rr": round(abs(float(tp) - fill_price) / real_stop_dist, 2) if real_stop_dist else None,
            "plannedRr": pos["rr"],
            "stopAtrMultiple": pos["stopAtrMultiple"],
            "feesPaid": round(fee, 4),
            "regimeAtEntry": regime.get("primary"), "regimeKey": regime.get("key"),
            "strategy": thesis.get("strategy"), "confidence": thesis.get("confidence"),
            "reasonCodes": thesis.get("reason_codes", []),
            "thesisSummary": (thesis.get("reasoning") or "")[:600],
            "status": "OPEN",
            "venue": "binance-spot-testnet",
            "entryOrderId": res.get("orderId"),
            "ocoOrderListId": oco_id,
            "ocoError": oco_err,
        }
        self.state["positions"].append(trade)
        self._save()
        bus.log("exec", "mo-vi-the",
                f"LONG {trade['qty']:.6f} @ {trade['entry']:,.2f} · SL {trade['stopLoss']:,.2f} · "
                f"TP {trade['targets'][0]:,.2f} · risk ${trade['riskAmount']} · "
                f"OCO {oco_id if oco_id else 'KHÔNG ĐẶT ĐƯỢC'}",
                trade=trade)
        return trade

    # ── theo dõi & đóng ────────────────────────────────────────────────────
    def mark(self, price: float) -> list[dict]:
        """Sàn giữ lệnh thoát, nên ở đây chỉ HỎI sàn xem đã khớp chưa.

        Khác hẳn sàn giấy — chỗ đó tự so giá với SL/TP. Ở đây tự so là tự bịa:
        khớp hay chưa là việc của sổ lệnh, không phải của biến `price`.
        """
        if not self.ready or not self.state["positions"]:
            return []
        try:
            open_ids = {o.get("orderListId") for o in self.client.open_orders(self.symbol)}
        except BinanceError as e:
            bus.log("exec", "testnet-loi-doc-lenh", str(e))
            return []

        closed = []
        for t in list(self.state["positions"]):
            oco = t.get("ocoOrderListId")
            if oco is None:
                continue  # không có OCO — doi_soat() lo, đừng đoán ở đây
            if oco in open_ids:
                continue  # còn treo
            closed.append(self._settle(t))
        if closed:
            self._save()
        return closed

    def _settle(self, trade: dict, ly_do: str | None = None) -> dict:
        """OCO không còn treo ⇒ đã khớp. Lấy giá thoát THẬT từ lịch sử khớp.

        `ly_do` do người gọi truyền vào thì GIỮ NGUYÊN. Đóng tay mà sổ ghi
        "OCO_FILLED" là nói dối đúng chỗ hậu kiểm đọc: bài học sẽ kết luận về
        một lần chạm stop/mục tiêu chưa từng xảy ra.
        """
        exit_price = None
        fee = 0.0
        reason = ly_do or "OCO_FILLED"
        try:
            for tr in reversed(self.client.my_trades(self.symbol, limit=20)):
                if tr.get("isBuyer"):
                    continue
                exit_price = float(tr["price"])
                if tr.get("commissionAsset") == "USDT":
                    fee = float(tr.get("commission", 0))
                break
        except BinanceError as e:
            bus.log("exec", "testnet-loi-doc-khop", str(e))

        if exit_price is None:
            exit_price = trade["targets"][0]
            reason = "OCO_FILLED_UOC_LUONG"

        # Chỉ ĐOÁN lý do khi người gọi không nói. Đoán đè lên lý do đã biết là
        # biến một sự thật thành một suy luận.
        if ly_do is None:
            reason = ("STOP_LOSS" if exit_price <= trade["stopLoss"] * 1.001
                      else "TAKE_PROFIT" if exit_price >= trade["targets"][0] * 0.999
                      else reason)

        pnl = (exit_price - trade["entry"]) * trade["qty"] - fee
        trade.update({
            "status": "CLOSED", "closedAt": _now(),
            "exit": round(exit_price, 2), "exitReason": reason,
            "grossPnl": round((exit_price - trade["entry"]) * trade["qty"], 2),
            "feesPaid": round(trade["feesPaid"] + fee, 4),
            "pnl": round(pnl, 2),
            "rMultiple": round(pnl / trade["riskAmount"], 2) if trade["riskAmount"] else None,
        })
        self.state["positions"] = [p for p in self.state["positions"] if p["id"] != trade["id"]]
        self.state["closedCount"] = self.state.get("closedCount", 0) + 1
        d = _utc_day()
        self._touch_day()
        self.state["dailyPnl"][d] = round(self.state["dailyPnl"].get(d, 0.0) + pnl, 2)
        # LƯU NGAY tại đây, đừng để người gọi nhớ hộ.
        #
        # Trước đây chỉ `mark()` lưu, còn `close()` thì quên. Đóng tay xong,
        # trong bộ nhớ sổ đã sạch và nhật ký đã ghi — nhưng file trên đĩa vẫn
        # còn vị thế. Tiến trình sau đọc file đó, thấy một vị thế MA, và
        # MAX_POSITIONS chặn mọi lệnh mới. Không lỗi nào báo; nó chỉ im lặng
        # không bao giờ vào lệnh nữa. Chỉ lộ ra khi khởi động lại.
        self._save()
        store.append(store.TRADES, trade)
        bus.log("exec", "dong-vi-the",
                f"{reason} @ {trade['exit']:,.2f} · PnL ${trade['pnl']:+,.2f} ({trade['rMultiple']:+}R)",
                trade=trade)
        return trade

    def close(self, trade: dict, exit_price: float, reason: str) -> dict:
        """Đóng bằng tay: huỷ OCO rồi bán MARKET."""
        if self.ready:
            try:
                self.client.cancel_all(self.symbol)
                self.client.market_sell(self.symbol, self.client.round_qty(self.symbol, trade["qty"]))
            except BinanceError as e:
                bus.log("exec", "testnet-loi-dong", str(e))
        return self._settle(trade, ly_do=reason)

    def doi_soat(self) -> list[str]:
        """Soát lệch giữa sổ cục bộ và sàn. Gọi lúc khởi động.

        Ba chỗ có thể lệch, đều do runtime chết giữa chừng:
          · có vị thế trong sổ nhưng không có OCO nào treo → đã khớp lúc mình tắt
          · có OCO treo nhưng sổ không có vị thế nào     → mồ côi, phải huỷ tay
          · vào được MARKET rồi chết trước khi đặt OCO   → ocoOrderListId là None
        """
        if not self.ready:
            return []
        canh = []
        try:
            treo = self.client.open_orders(self.symbol)
        except BinanceError as e:
            return [f"không đọc được lệnh treo: {e}"]
        ids = {o.get("orderListId") for o in treo}
        for t in self.state["positions"]:
            if t.get("ocoOrderListId") is None:
                canh.append(f"vị thế {t['id']} KHÔNG có OCO — không ai canh, đóng tay hoặc đặt lại")
            elif t["ocoOrderListId"] not in ids:
                canh.append(f"vị thế {t['id']} có OCO {t['ocoOrderListId']} nhưng sàn không còn treo — có thể đã khớp")
        if treo and not self.state["positions"]:
            canh.append(f"{len(treo)} lệnh treo trên sàn mà sổ không có vị thế nào — lệnh mồ côi")
        for c in canh:
            bus.log("exec", "testnet-lech-so", c)
        return canh

    # ── ảnh chụp ───────────────────────────────────────────────────────────
    def snapshot(self, price: float | None = None) -> dict:
        s = dict(self.state)
        s["venue"] = "binance-spot-testnet"
        s["ready"] = self.ready
        s["lastError"] = self.last_error

        equity = 0.0
        avail = 0.0
        if self.ready and price:
            try:
                f = self.client.filters(self.symbol)
                bal = self.client.balances()
                quote = bal.get(f["quote"], {})
                base = bal.get(f["base"], {})
                equity = quote.get("total", 0.0) + base.get("total", 0.0) * price
                # Tiền MUA ĐƯỢC, không phải vốn: phần USDT đang rảnh. Risk Engine
                # cần con số này để không sinh ra lệnh mà sàn chắc chắn từ chối.
                avail = quote.get("free", 0.0)
            except BinanceError as e:
                self.last_error = str(e)
        s["equity"] = round(equity, 2)
        s["availableQuote"] = round(avail, 2)

        peak = max(self.state.get("peakEquity", 0.0), equity)
        self.state["peakEquity"] = peak
        s["peakEquity"] = round(peak, 2)

        open_pnl = 0.0
        positions = []
        for t in self.state["positions"]:
            p = dict(t)
            if price:
                p["unrealizedPnl"] = round((price - t["entry"]) * t["qty"], 2)
                p["unrealizedR"] = (round(p["unrealizedPnl"] / t["riskAmount"], 2)
                                    if t["riskAmount"] else None)
                open_pnl += p["unrealizedPnl"]
            positions.append(p)
        s["positions"] = positions
        s["openPnl"] = round(open_pnl, 2)
        # Vốn đã gồm giá trị BTC đang giữ, nên không cộng thêm open_pnl lần nữa.
        s["equityMarked"] = s["equity"]
        s["drawdownPct"] = round(max(0.0, (peak - equity) / peak * 100), 2) if peak else 0.0
        s["todayPnl"] = round(self.state.get("dailyPnl", {}).get(_utc_day(), 0.0), 2)
        s.setdefault("dailyStartEquity", {}).setdefault(_utc_day(), equity or 0.0)
        return s
