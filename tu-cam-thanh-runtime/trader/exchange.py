"""Client REST có ký cho Binance Spot **Testnet**.

Chỉ testnet. Base URL cắm cứng, không đọc từ config, không có cờ nào bật sang
mainnet. Một biến `base_url` đọc từ file cấu hình là một dòng sửa nhầm giữa
mainnet và testnet — và ở đây "sửa nhầm" nghĩa là gửi lệnh thật bằng tiền thật.
Muốn chạy mainnet thì phải viết một class khác và tự chịu trách nhiệm.

Ba thứ file này lo, vì thiếu cái nào cũng hỏng theo kiểu khó lần:

1. **Lệch đồng hồ.** Binance từ chối request có `timestamp` lệch quá
   `recvWindow` (lỗi -1021). Máy Windows lệch vài giây là chuyện thường. Nên
   đo offset với `/time` lúc khởi động và cộng vào mọi request đã ký.
2. **Bộ lọc sàn.** `LOT_SIZE.stepSize`, `PRICE_FILTER.tickSize`,
   `NOTIONAL.minNotional`. Gửi khối lượng lẻ hơn stepSize là lỗi -1013, và nó
   chỉ nổ lúc đặt lệnh chứ không nổ lúc tính.
3. **Làm tròn XUỐNG.** Khối lượng luôn làm tròn xuống bội của stepSize. Làm
   tròn lên là vượt trần rủi ro mà Risk Engine vừa tính — đúng thứ cả bức
   tường sinh ra để chặn.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from decimal import ROUND_DOWN, ROUND_UP, Decimal
from typing import Any
from urllib.parse import urlencode

import httpx

BASE = "https://testnet.binance.vision"


class BinanceError(RuntimeError):
    def __init__(self, code: int | None, msg: str) -> None:
        super().__init__(f"Binance {code}: {msg}" if code else msg)
        self.code = code
        self.msg = msg


class TestnetClient:
    def __init__(self, key: str | None = None, secret: str | None = None) -> None:
        self.key = key or os.environ.get("BINANCE_TESTNET_KEY") or ""
        self.secret = secret or os.environ.get("BINANCE_TESTNET_SECRET") or ""
        self._offset_ms = 0
        self._filters: dict[str, dict] = {}
        self._client = httpx.Client(base_url=BASE, timeout=15.0)

    # ── nền ────────────────────────────────────────────────────────────────
    @property
    def has_keys(self) -> bool:
        return bool(self.key and self.secret)

    def close(self) -> None:
        self._client.close()

    def _raise(self, r: httpx.Response) -> None:
        try:
            j = r.json()
        except Exception:  # noqa: BLE001
            raise BinanceError(None, f"HTTP {r.status_code}: {r.text[:200]}") from None
        raise BinanceError(j.get("code"), j.get("msg", r.text[:200]))

    def _get(self, path: str, params: dict | None = None) -> Any:
        r = self._client.get(path, params=params or {})
        if r.status_code != 200:
            self._raise(r)
        return r.json()

    def _signed(self, method: str, path: str, params: dict, _retried: bool = False) -> Any:
        if not self.has_keys:
            raise BinanceError(None, "chưa có BINANCE_TESTNET_KEY / BINANCE_TESTNET_SECRET")
        p = {k: v for k, v in params.items() if v is not None}
        p["timestamp"] = int(time.time() * 1000) + self._offset_ms
        p.setdefault("recvWindow", 5000)
        query = urlencode(p, doseq=True)
        sig = hmac.new(self.secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        url = f"{path}?{query}&signature={sig}"
        r = self._client.request(method, url, headers={"X-MBX-APIKEY": self.key})
        if r.status_code == 200:
            return r.json()

        # -1021 = timestamp ngoài recvWindow. Đồng hồ máy trôi trong lúc chạy là
        # chuyện thường (máy này lệch sẵn ~7 phút), nên đo lại offset rồi thử ĐÚNG
        # MỘT LẦN. Thử vô hạn thì một lỗi khác cũng thành vòng lặp gửi lệnh —
        # ở đây "gửi lệnh" nghĩa là đặt lệnh mua thật.
        try:
            code = r.json().get("code")
        except Exception:  # noqa: BLE001
            code = None
        if code == -1021 and not _retried:
            self.sync_time()
            return self._signed(method, path, params, _retried=True)
        self._raise(r)

    # ── công khai ──────────────────────────────────────────────────────────
    def ping(self) -> bool:
        self._get("/api/v3/ping")
        return True

    def sync_time(self) -> int:
        """Đo lệch đồng hồ giữa máy này và sàn. Trả về ms lệch."""
        before = time.time() * 1000
        srv = self._get("/api/v3/time")["serverTime"]
        after = time.time() * 1000
        # bù nửa vòng mạng để offset không tính cả độ trễ vào
        self._offset_ms = int(srv - (before + after) / 2)
        return self._offset_ms

    def price(self, symbol: str) -> float:
        return float(self._get("/api/v3/ticker/price", {"symbol": symbol})["price"])

    def filters(self, symbol: str) -> dict:
        """Bộ lọc của một cặp, cache lại — exchangeInfo hiếm khi đổi trong một phiên."""
        if symbol in self._filters:
            return self._filters[symbol]
        info = self._get("/api/v3/exchangeInfo", {"symbol": symbol})
        s = info["symbols"][0]
        out = {
            "status": s["status"],
            "base": s["baseAsset"],
            "quote": s["quoteAsset"],
            "ocoAllowed": s.get("ocoAllowed", False),
            "orderTypes": s.get("orderTypes", []),
            "stepSize": None, "minQty": None,
            "tickSize": None, "minNotional": None,
        }
        for f in s["filters"]:
            t = f["filterType"]
            if t == "LOT_SIZE":
                out["stepSize"] = Decimal(f["stepSize"])
                out["minQty"] = Decimal(f["minQty"])
            elif t == "PRICE_FILTER":
                out["tickSize"] = Decimal(f["tickSize"])
            elif t in ("NOTIONAL", "MIN_NOTIONAL"):
                out["minNotional"] = Decimal(f["minNotional"])
        self._filters[symbol] = out
        return out

    # ── làm tròn theo bộ lọc ───────────────────────────────────────────────
    @staticmethod
    def _quantize(value: float, step: Decimal, rounding: str) -> Decimal:
        if not step or step == 0:
            return Decimal(str(value))
        return (Decimal(str(value)) / step).quantize(Decimal(1), rounding=rounding) * step

    def round_qty(self, symbol: str, qty: float) -> Decimal:
        """Làm tròn XUỐNG. Lên là vượt trần rủi ro Risk Engine vừa tính."""
        return self._quantize(qty, self.filters(symbol)["stepSize"], ROUND_DOWN)

    def round_price(self, symbol: str, price: float, up: bool = False) -> Decimal:
        return self._quantize(price, self.filters(symbol)["tickSize"], ROUND_UP if up else ROUND_DOWN)

    def check_order(self, symbol: str, qty: Decimal, price: float) -> str | None:
        """Trả về lý do lệnh KHÔNG hợp lệ, hoặc None nếu hợp lệ."""
        f = self.filters(symbol)
        if f["status"] != "TRADING":
            return f"cặp {symbol} đang {f['status']}"
        if f["minQty"] and qty < f["minQty"]:
            return f"khối lượng {qty} < minQty {f['minQty']}"
        notional = qty * Decimal(str(price))
        if f["minNotional"] and notional < f["minNotional"]:
            return f"giá trị lệnh {notional:.2f} < minNotional {f['minNotional']}"
        return None

    # ── đã ký ──────────────────────────────────────────────────────────────
    def account(self) -> dict:
        return self._signed("GET", "/api/v3/account", {})

    def balances(self) -> dict[str, dict]:
        out = {}
        for b in self.account()["balances"]:
            free, locked = float(b["free"]), float(b["locked"])
            if free or locked:
                out[b["asset"]] = {"free": free, "locked": locked, "total": free + locked}
        return out

    def market_buy(self, symbol: str, qty: Decimal) -> dict:
        return self._signed("POST", "/api/v3/order", {
            "symbol": symbol, "side": "BUY", "type": "MARKET",
            "quantity": format(qty, "f"),
        })

    def market_sell(self, symbol: str, qty: Decimal) -> dict:
        return self._signed("POST", "/api/v3/order", {
            "symbol": symbol, "side": "SELL", "type": "MARKET",
            "quantity": format(qty, "f"),
        })

    def oco_sell(self, symbol: str, qty: Decimal, take_profit: Decimal, stop: Decimal,
                 stop_limit: Decimal) -> dict:
        """Một lệnh OCO SELL = chốt lãi + cắt lỗ, khớp cái nào thì huỷ cái kia.

        Đây là thứ giữ cho vị thế vẫn được bảo vệ khi runtime tắt. Quản TP bằng
        vòng lặp Python thì tắt máy là mất chốt lãi lẫn cắt lỗ.

        Thử endpoint mới trước, rơi về endpoint cũ nếu sàn chưa có — hai bản
        cùng tồn tại một thời gian và testnet không phải lúc nào cũng theo kịp.
        """
        common = {
            "symbol": symbol,
            "side": "SELL",
            "quantity": format(qty, "f"),
        }
        try:
            return self._signed("POST", "/api/v3/orderList/oco", {
                **common,
                "aboveType": "LIMIT_MAKER",
                "abovePrice": format(take_profit, "f"),
                "belowType": "STOP_LOSS_LIMIT",
                "belowStopPrice": format(stop, "f"),
                "belowPrice": format(stop_limit, "f"),
                "belowTimeInForce": "GTC",
            })
        except BinanceError as e:
            if e.code not in (-1121, -1102, -1104, -1128, None) and e.code != -2011:
                # lỗi thật (số dư, bộ lọc…) thì đừng thử lại endpoint cũ
                raise
            return self._signed("POST", "/api/v3/order/oco", {
                **common,
                "price": format(take_profit, "f"),
                "stopPrice": format(stop, "f"),
                "stopLimitPrice": format(stop_limit, "f"),
                "stopLimitTimeInForce": "GTC",
            })

    def open_orders(self, symbol: str) -> list[dict]:
        return self._signed("GET", "/api/v3/openOrders", {"symbol": symbol})

    def cancel_all(self, symbol: str) -> Any:
        try:
            return self._signed("DELETE", "/api/v3/openOrders", {"symbol": symbol})
        except BinanceError as e:
            if e.code == -2011:  # không có lệnh nào để huỷ
                return []
            raise

    def my_trades(self, symbol: str, limit: int = 20) -> list[dict]:
        return self._signed("GET", "/api/v3/myTrades", {"symbol": symbol, "limit": limit})
