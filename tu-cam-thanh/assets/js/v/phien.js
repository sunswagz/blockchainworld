/* SINH TỰ ĐỘNG bởi tu-cam-thanh-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái của runtime giao dịch, để trang tĩnh đọc được mà không
   cần server và không cần khoá API. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem README):
       python run.py            ghi mỗi vòng lặp
       python -m trader.snapshot   ghi một lần rồi thoát
*/
window.TU_CAM_THANH = {
 "generatedAt": "2026-08-15T13:52:39.605Z",
 "chayTu": "2026-08-15T13:52:38+00:00",
 "vong": 1,
 "tamDung": false,
 "san": "paper",
 "cheDoSan": "paper",
 "chiLong": false,
 "cap": "BTCUSDT",
 "khung": {
  "primary": "1h",
  "context": "4h"
 },
 "gia": 63060.34,
 "nguon": {
  "name": "data-api.binance.vision",
  "live": true,
  "lastOk": "20:52:39",
  "lastError": null
 },
 "cheDo": {
  "primary": "RANGE",
  "flags": [
   "LOW_VOLATILITY"
  ],
  "quality": "MEDIUM",
  "reasons": [
   "ADX 16.7 < 18 — không bên nào kiểm soát",
   "dải Bollinger co còn 0.45%"
  ],
  "contextTrend": "BEARISH_ALIGNED",
  "adx": 16.7,
  "volatility": "LOW",
  "key": "RANGE|LOW_VOLATILITY"
 },
 "thiTruong": {
  "1h": {
   "price": 63060.34,
   "ema20": 63041.64,
   "ema50": 63168.29,
   "ema200": 63735.33,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 50.1,
   "rsiSlope": 0.3,
   "macdHist": 13.75,
   "macdHistSlope": -1.248,
   "atr": 134.14,
   "atrPct": 0.213,
   "atrRatioVsMedian": 0.62,
   "volatility": "LOW",
   "adx": 16.7,
   "plusDI": 14.9,
   "minusDI": 21.4,
   "bbWidthPct": 0.45,
   "bbPosition": 0.63,
   "volumeRatio": 0.5,
   "structure": "UPTREND",
   "swingHighs": [
    63617.45,
    63247.05,
    63066.13,
    63187.98
   ],
   "swingLows": [
    62535.24,
    62830.0,
    62800.0,
    62920.0
   ],
   "support": [
    {
     "price": 62764.58,
     "touches": 6
    }
   ],
   "resistance": [
    {
     "price": 63278.44,
     "touches": 8
    },
    {
     "price": 63626.92,
     "touches": 6
    },
    {
     "price": 63972.34,
     "touches": 3
    }
   ],
   "range20High": 63247.05,
   "range20Low": 62800.0,
   "distToRange20HighPct": 0.3,
   "distToRange20LowPct": 0.41
  },
  "4h": {
   "price": 63060.34,
   "ema20": 63316.0,
   "ema50": 63738.14,
   "ema200": 63924.24,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 39.0,
   "rsiSlope": 0.31,
   "macdHist": 18.3,
   "macdHistSlope": 10.341,
   "atr": 367.66,
   "atrPct": 0.583,
   "atrRatioVsMedian": 0.73,
   "volatility": "NORMAL",
   "adx": 30.7,
   "plusDI": 13.4,
   "minusDI": 28.1,
   "bbWidthPct": 2.16,
   "bbPosition": 0.32,
   "volumeRatio": 0.13,
   "structure": "DOWNTREND",
   "swingHighs": [
    64515.43,
    64500.0,
    64010.0,
    63247.05
   ],
   "swingLows": [
    63238.0,
    63310.34,
    62802.27,
    62535.24
   ],
   "support": [
    {
     "price": 62802.27,
     "touches": 1
    },
    {
     "price": 62535.24,
     "touches": 1
    }
   ],
   "resistance": [
    {
     "price": 63279.35,
     "touches": 4
    },
    {
     "price": 64051.15,
     "touches": 7
    },
    {
     "price": 64573.67,
     "touches": 4
    }
   ],
   "range20High": 64500.0,
   "range20Low": 62535.24,
   "distToRange20HighPct": 2.28,
   "distToRange20LowPct": 0.83
  }
 },
 "luanDiem": {
  "regime_read": "RANGE",
  "market_summary": "[mock] RANGE, ADX 16.7, RSI 50.1, EMA BEARISH_ALIGNED",
  "scenarios": [
   {
    "name": "tiếp diễn",
    "probability": 0.4,
    "description": "giữ hướng hiện tại"
   },
   {
    "name": "quét thanh khoản rồi hồi",
    "probability": 0.35,
    "description": "thủng biên rồi lấy lại"
   },
   {
    "name": "đảo chiều",
    "probability": 0.25,
    "description": "mất cấu trúc"
   }
  ],
  "action": "NO_TRADE",
  "confidence": 0.4,
  "entry_zone": null,
  "invalidation": null,
  "invalidation_logic": "không vào lệnh nên không có điểm vô hiệu hoá",
  "targets": [],
  "suggested_risk_pct": 0.0,
  "strategy": "MOCK_RULES_V1",
  "reason_codes": [
   "MOCK_BRAIN",
   "NO_CLEAR_TREND"
  ],
  "reasoning": "Bộ não giả lập: chỉ vào lệnh khi xu hướng rõ và các khung không mâu thuẫn.",
  "event_risk": "UNKNOWN",
  "symbol": "BTCUSDT",
  "source": "mock",
  "regimeFromClassifier": "RANGE",
  "at": "2026-08-15T13:52:39+00:00"
 },
 "phanQuyet": {
  "approved": false,
  "action": "NO_TRADE",
  "rejections": [],
  "note": "brain chủ động không vào lệnh",
  "position": null
 },
 "taiKhoan": {
  "vonBanDau": 10000,
  "von": 10000.0,
  "vonThucHien": 10000,
  "dinhVon": 10000,
  "laiLoMo": 0.0,
  "laiLoHomNay": 0.0,
  "drawdownPct": 0.0,
  "soLenhDaDong": 0,
  "viThe": []
 },
 "rui_ro": {
  "dungHan": null,
  "ngatMach": [],
  "gioiHan": {
   "startingEquity": 10000,
   "maxRiskPerTradePct": 0.5,
   "maxOpenPositions": 1,
   "maxDailyLossPct": 2.0,
   "maxDrawdownPct": 10.0,
   "minRR": 2.0,
   "minConfidence": 0.55,
   "minStopAtr": 0.3,
   "maxStopAtr": 3.0,
   "maxNotionalPctOfEquity": 100,
   "feeBps": 10,
   "slippageBps": 5
  }
 },
 "boNao": {
  "cheDo": "mock",
  "model": "claude-opus-5",
  "homNay": {
   "usd": 0.0,
   "calls": 0,
   "inputTokens": 0,
   "outputTokens": 0,
   "cacheReadTokens": 0,
   "cacheWriteTokens": 0
  },
  "hanMucUsd": 5.0,
  "soKyNang": 11
 },
 "thongKe": {
  "overall": {
   "count": 3,
   "wins": 3,
   "winRate": 100.0,
   "expectancyR": 1.473,
   "totalPnl": 212.03,
   "avgWinR": 1.47,
   "avgLossR": null,
   "maxLossR": 1.46
  },
  "byRegime": {
   "RANGE": {
    "count": 3,
    "wins": 3,
    "winRate": 100.0,
    "expectancyR": 1.473,
    "totalPnl": 212.03,
    "avgWinR": 1.47,
    "avgLossR": null,
    "maxLossR": 1.46
   }
  },
  "byStrategy": {
   "MOCK_RULES_V1": {
    "count": 3,
    "wins": 3,
    "winRate": 100.0,
    "expectancyR": 1.473,
    "totalPnl": 212.03,
    "avgWinR": 1.47,
    "avgLossR": null,
    "maxLossR": 1.46
   }
  }
 },
 "giaoDich": [
  {
   "id": "t_8a47849991",
   "openedAt": "2026-08-15T13:52:35+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.15834076483413426,
   "entry": 63154.93,
   "requestedEntry": 63060.34,
   "stopLoss": 62859.13,
   "targets": [
    63746.53,
    64133.45
   ],
   "riskAmount": 46.84,
   "plannedRiskAmount": 46.84,
   "slippageCostOnRisk": -0.0,
   "riskPct": 0.5,
   "rr": 2.0,
   "plannedRr": 2.0,
   "stopAtrMultiple": 1.5,
   "feesPaid": 20.08,
   "regimeAtEntry": "RANGE",
   "regimeKey": "RANGE|LOW_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.8,
   "reasonCodes": [
    "MOCK_BRAIN",
    "NO_CLEAR_TREND"
   ],
   "thesisSummary": "Bộ não giả lập: chỉ vào lệnh khi xu hướng rõ và các khung không mâu thuẫn.",
   "status": "CLOSED",
   "closedAt": "2026-08-15T13:52:35+00:00",
   "exit": 63650.91,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 78.53,
   "pnl": 68.46,
   "rMultiple": 1.46,
   "holdingMinutes": 0
  },
  {
   "id": "t_864c2bd8b0",
   "openedAt": "2026-08-15T13:50:14+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.15834076483413426,
   "entry": 63154.93,
   "requestedEntry": 63060.34,
   "stopLoss": 62859.13,
   "targets": [
    63746.53,
    64133.45
   ],
   "riskAmount": 46.84,
   "plannedRiskAmount": 46.84,
   "slippageCostOnRisk": -0.0,
   "riskPct": 0.5,
   "rr": 2.0,
   "plannedRr": 2.0,
   "stopAtrMultiple": 1.5,
   "feesPaid": 20.08,
   "regimeAtEntry": "RANGE",
   "regimeKey": "RANGE|LOW_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.8,
   "reasonCodes": [
    "MOCK_BRAIN",
    "NO_CLEAR_TREND"
   ],
   "thesisSummary": "Bộ não giả lập: chỉ vào lệnh khi xu hướng rõ và các khung không mâu thuẫn.",
   "status": "CLOSED",
   "closedAt": "2026-08-15T13:50:14+00:00",
   "exit": 63650.91,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 78.53,
   "pnl": 68.46,
   "rMultiple": 1.46,
   "holdingMinutes": 0
  },
  {
   "id": "t_f88096d887",
   "openedAt": "2026-08-15T08:16:48+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.15613395310404296,
   "entry": 63154.43,
   "requestedEntry": 63059.84,
   "stopLoss": 62834.19,
   "targets": [
    63794.91,
    64263.3
   ],
   "riskAmount": 50.0,
   "plannedRiskAmount": 50.0,
   "slippageCostOnRisk": 0.0,
   "riskPct": 0.5,
   "rr": 2.0,
   "plannedRr": 2.0,
   "stopAtrMultiple": 1.5,
   "feesPaid": 19.81,
   "regimeAtEntry": "RANGE",
   "regimeKey": "RANGE|none",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.8,
   "reasonCodes": [
    "MOCK_BRAIN",
    "NO_CLEAR_TREND"
   ],
   "thesisSummary": "Bộ não giả lập: chỉ vào lệnh khi xu hướng rõ và các khung không mâu thuẫn.",
   "status": "CLOSED",
   "closedAt": "2026-08-15T08:16:48+00:00",
   "exit": 63699.22,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 85.06,
   "pnl": 75.11,
   "rMultiple": 1.5,
   "holdingMinutes": 0
  }
 ],
 "baiHoc": []
};
