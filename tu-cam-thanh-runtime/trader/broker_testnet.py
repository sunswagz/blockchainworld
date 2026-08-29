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

from .config import CONFIG
from .bus import bus
from .exchange import BinanceError, TestnetClient
from . import store

ACCOUNT_FILE = "account_testnet.json"

# Dấu phiên bản của CÁCH TÍNH VỐN. Tăng khi đổi công thức — sổ tài khoản mang
# dấu này, và lệch dấu thì đỉnh vốn được đặt lại thay vì đem so hai định nghĩa
# khác nhau với nhau.
#   1 = tổng số dư ví (quote + mọi tài sản × giá)
#   2 = tiền quote + các vị thế BOT đang giữ
DINH_NGHIA_VON = 2


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
            # Kiểm MỌI chợ khai trong config, không chỉ chợ chính. Sàn không có
            # cặp đó thì phải biết lúc khởi động, chứ không phải lúc bot vừa
            # quyết định vào lệnh và lệnh bị từ chối.
            self.cho_loi = []
            for _s in (CONFIG.get("symbols") or []):
                try:
                    self.client.filters(_s)
                except BinanceError as e:
                    self.cho_loi.append(f"{_s}: {e}")
            if self.cho_loi:
                bus.log("exec", "testnet-cho-khong-dung-duoc",
                        f"{len(self.cho_loi)} chợ trong config sàn không nhận: "
                        + " · ".join(self.cho_loi[:5]))
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

    def _equity(self, price: float | dict) -> float:
        """Vốn quy về USDT. Đọc từ sàn — sổ của mình không có quyền nói khác.

        `price` nhận một số (một chợ) hoặc {chợ: giá}. Cộng qua mọi tài sản có
        giá: giữ ETH mà chỉ tính BTC là báo vốn thấp hơn thật.
        """
        gia = price if isinstance(price, dict) else {self.symbol: price}
        f = self.client.filters(self.symbol)
        bal = self.client.balances()
        tong = bal.get(f["quote"], {}).get("total", 0.0)
        for sym, g in gia.items():
            try:
                fi = self.client.filters(sym)
            except BinanceError:
                continue
            if fi["quote"] == f["quote"]:
                tong += bal.get(fi["base"], {}).get("total", 0.0) * g
        return tong

    def reset(self) -> dict:
        """Huỷ mọi lệnh treo và xoá sổ vị thế cục bộ.

        KHÔNG nạp lại số dư — số dư testnet do Binance cấp, mình không đặt được.
        Hết tiền thì tạo khoá mới ở testnet.binance.vision.
        """
        if self.ready:
            # Huỷ ở MỌI chợ đang có vị thế, không chỉ chợ chính: reset mà để lại
            # OCO của ETH treo trên sàn là để lại một lệnh mồ côi sẽ khớp lúc nào
            # đó, cho một vị thế mà sổ cục bộ đã xoá.
            for _s in {self.symbol} | {t.get("symbol") or self.symbol
                                       for t in self.state["positions"]}:
                try:
                    self.client.cancel_all(_s)
                except BinanceError as e:
                    bus.log("exec", "testnet-huy-loi", f"{_s}: {e}")
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

        # Chợ lấy từ chính LUẬN ĐIỂM, không từ cấu hình broker. Quét 15 coin mà
        # đặt lệnh bằng symbol cố định là gửi lệnh ETH lên sàn mang mã BTC —
        # sàn khớp, sổ ghi, và không gì báo sai.
        sym = thesis.get("symbol") or self.symbol
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
            # KHUNG lúc mở lệnh. Cùng lý do với bài học chạy lại: một chế độ
            # trên 1h và trên 4h là hai thị trường khác nhau mang chung tên, và
            # sổ giao dịch trộn hai khung lại thì mọi thống kê theo chế độ đều
            # là trung bình của hai thứ không so được với nhau.
            "khung": CONFIG["timeframes"]["primary"],
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
            # Hỏi từng chợ ĐANG có vị thế, không chỉ chợ chính: lệnh OCO của
            # ETH không xuất hiện trong `open_orders("BTCUSDT")`, nên vị thế
            # ETH sẽ trông như đã khớp xong trong khi nó vẫn đang treo.
            open_ids = set()
            for _s in {t.get("symbol") or self.symbol
                       for t in self.state["positions"]}:
                open_ids |= {o.get("orderListId")
                             for o in self.client.open_orders(_s)}
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
            for tr in reversed(self.client.my_trades(
                    trade.get("symbol") or self.symbol, limit=20)):
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
                _s = trade.get("symbol") or self.symbol
                self.client.cancel_all(_s)
                self.client.market_sell(_s, self.client.round_qty(_s, trade["qty"]))
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
            treo = []
            for _s in {self.symbol} | {t.get("symbol") or self.symbol
                                       for t in self.state["positions"]}:
                treo += self.client.open_orders(_s)
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
        # "Vốn bằng 0" và "chưa đọc được vốn" là HAI chuyện khác nhau, và gộp
        # chúng lại đã gây ra một lỗi thật: lúc khởi động, `peakEquity` nạp từ
        # đĩa (73.029) trong khi số dư sàn chưa kịp về nên equity còn 0 ⇒ ngắt
        # mạch tính ra drawdown 100% và CHỐT CỨNG kill switch. Sau đó số dư về
        # đủ, drawdown thật là 0%, nhưng chốt không bao giờ tự mở — bot đứng im
        # vĩnh viễn với một câu thông báo không khớp con số nào trên màn hình.
        # Từ khi có dịch vụ tự chạy, lỗi này lặp lại mỗi lần bật máy.
        da_doc = False
        if self.ready and price:
            try:
                # `price` nhận MỘT SỐ (một chợ) hoặc TỪ ĐIỂN {chợ: giá}.
                #
                # Vốn phải cộng qua MỌI tài sản đang giữ, không chỉ tài sản của
                # chợ chính. Quét 15 coin mà tính vốn bằng "USDT + BTC×giá BTC"
                # là bỏ sót ETH, SOL… đang nắm — vốn thấp hơn thật, và vốn sai
                # thì cỡ vị thế sai ở MỌI lệnh sau đó.
                # VỐN CỦA BOT = tiền quote + giá trị các vị thế NÓ ĐANG GIỮ.
                # KHÔNG phải tổng số dư ví.
                #
                # Ví testnet này có sẵn 1 BTC mà không chiến lược nào mở — 89%
                # "vốn". Đo được: mức sụt giảm 2,39% trong khi giao dịch chỉ lỗ
                # 510 đô; 1.634 đô còn lại, tức 76%, là giá BTC nhúc nhích. Và
                # BTC rơi 10% là vốn rơi 8,9% — gần chạm kill switch 10% MÀ
                # KHÔNG CÓ LỆNH NÀO. Bot bị dừng vì thứ nó không hề mở.
                #
                # Đếm theo vị thế đang theo dõi thì tài sản lạ trong ví không
                # lọt vào: mua BTC là quote giảm và một vị thế xuất hiện, nên
                # hai vế vẫn khớp. Số dư ví vẫn được báo riêng ở `viNgoai` —
                # loại nó khỏi phép tính không có nghĩa là giấu nó đi.
                gia = price if isinstance(price, dict) else {self.symbol: price}
                f = self.client.filters(self.symbol)
                bal = self.client.balances()
                quote = bal.get(f["quote"], {})
                equity = quote.get("total", 0.0)
                for t in self.state["positions"]:
                    g = gia.get(t.get("symbol") or self.symbol)
                    if g:
                        equity += (t.get("qty") or 0.0) * g
                # Tài sản trong ví KHÔNG thuộc vị thế nào — báo ra, không tính vào.
                ngoai = 0.0
                _giu = {}
                for t in self.state["positions"]:
                    _s = t.get("symbol") or self.symbol
                    _giu[_s] = _giu.get(_s, 0.0) + (t.get("qty") or 0.0)
                for sym, g in gia.items():
                    try:
                        fi = self.client.filters(sym)
                    except BinanceError:
                        continue
                    if fi["quote"] != f["quote"]:
                        continue
                    du = bal.get(fi["base"], {}).get("total", 0.0) - _giu.get(sym, 0.0)
                    if du > 0:
                        ngoai += du * g
                s["viNgoai"] = round(ngoai, 2)
                # Tiền MUA ĐƯỢC, không phải vốn: phần USDT đang rảnh. Risk Engine
                # cần con số này để không sinh ra lệnh mà sàn chắc chắn từ chối.
                avail = quote.get("free", 0.0)
                # VỐN CHỈ ĐÁNG TIN KHI ĐỦ GIÁ CHO MỌI VỊ THẾ.
                #
                # Thiếu giá một chợ thì vị thế ở đó được cộng bằng 0, và vốn hụt
                # đúng bằng giá trị của nó. Đã xảy ra ngay lượt khởi động đầu tiên
                # sau khi mở nhiều chợ: bảng báo sụt giảm 17,14% trong khi ba lệnh
                # chỉ rủi ro 141 đô — và ngắt mạch CHỐT CỨNG kill switch vì một
                # con số thoáng qua. Ba giây sau, đủ giá, vốn về 9.495 trên đỉnh
                # 9.500, tức sụt giảm 0,05%. Chốt thì không tự mở.
                #
                # Đây đúng là lỗi file này đã ghi và đã sửa một lần cho trường hợp
                # "chưa hỏi được số dư". Nhiều chợ làm nó tái phát dưới dạng khác:
                # số dư ĐỌC ĐƯỢC, chỉ là chưa đủ giá. "Đọc được" và "đủ" là hai
                # chuyện, và gộp lại thì mất bot.
                _thieu = [t.get("symbol") or self.symbol
                          for t in self.state["positions"]
                          if not gia.get(t.get("symbol") or self.symbol)]
                if _thieu:
                    s["thieuGia"] = sorted(set(_thieu))
                    bus.emit("exec", "von-chua-du-gia",
                             f"chưa có giá cho {sorted(set(_thieu))} — chưa chốt vốn")
                else:
                    da_doc = True
            except BinanceError as e:
                self.last_error = str(e)
        s["equity"] = round(equity, 2)
        s["availableQuote"] = round(avail, 2)
        s["equityKnown"] = da_doc

        # Đỉnh vốn chỉ được cập nhật bằng con số ĐÃ ĐỌC ĐƯỢC.
        # ĐỔI ĐỊNH NGHĨA VỐN thì phải đặt lại ĐỈNH VỐN.
        #
        # Đỉnh cũ (89.587) đo theo "tổng số dư ví"; vốn mới đo theo "tiền quote
        # + vị thế bot giữ" và ra ~9.500. Giữ nguyên đỉnh cũ là ngắt mạch thấy
        # sụt giảm 89% rồi CHỐT CỨNG kill switch ngay lượt đầu — đúng loại lỗi
        # đã xảy ra một lần ở đây.
        #
        # Nhận ra bằng một dấu phiên bản trong chính sổ tài khoản, không bằng
        # ngưỡng đoán mò: ngưỡng kiểu "lệch quá 50% thì đặt lại" sẽ nuốt luôn
        # một cú sụt thật 50%.
        if da_doc and self.state.get("dinhNghiaVon") != DINH_NGHIA_VON:
            _cu = self.state.get("peakEquity", 0.0)
            bus.log("exec", "doi-dinh-nghia-von",
                    f"vốn đổi cách tính (đỉnh cũ {_cu:,.0f} đo theo tổng số dư ví)"
                    f" — đặt lại đỉnh về {equity:,.0f}. Không đặt lại thì ngắt"
                    f" mạch thấy sụt giảm giả và chốt cứng kill switch.")
            self.state["peakEquity"] = equity
            self.state["dinhNghiaVon"] = DINH_NGHIA_VON
        peak = max(self.state.get("peakEquity", 0.0), equity) if da_doc \
            else self.state.get("peakEquity", 0.0)
        self.state["peakEquity"] = peak
        s["peakEquity"] = round(peak, 2)

        open_pnl = 0.0
        positions = []
        # Giá của CHÍNH chợ vị thế đó. Một giá chung ở đây là lãi/lỗ chưa chốt
        # của SOL được tính bằng giá BTC — con số vô nghĩa, và nó chảy thẳng vào
        # `openPnl` rồi lên bảng.
        _gia_map = price if isinstance(price, dict) else (
            {self.symbol: price} if price else {})
        for t in self.state["positions"]:
            p = dict(t)
            _g = _gia_map.get(t.get("symbol") or self.symbol)
            if _g:
                p["unrealizedPnl"] = round((_g - t["entry"]) * t["qty"], 2)
                p["unrealizedR"] = (round(p["unrealizedPnl"] / t["riskAmount"], 2)
                                    if t["riskAmount"] else None)
                open_pnl += p["unrealizedPnl"]
            positions.append(p)
        s["positions"] = positions
        s["openPnl"] = round(open_pnl, 2)
        # Vốn đã gồm giá trị BTC đang giữ, nên không cộng thêm open_pnl lần nữa.
        s["equityMarked"] = s["equity"]
        s["drawdownPct"] = (round(max(0.0, (peak - equity) / peak * 100), 2)
                            if (da_doc and peak) else 0.0)
        s["todayPnl"] = round(self.state.get("dailyPnl", {}).get(_utc_day(), 0.0), 2)
        # Chỉ chốt vốn đầu ngày khi đã đọc được. Ghi 0 vào đây thì trần lỗ ngày
        # bị TẮT LẶNG LẼ suốt ngày hôm đó — `start_of_day > 0` không bao giờ
        # đúng nữa, nên không có gì báo là hàng rào đã biến mất.
        if da_doc:
            s.setdefault("dailyStartEquity", {}).setdefault(_utc_day(), equity)
            self.state.setdefault("dailyStartEquity", {}).setdefault(_utc_day(), equity)
        return s
