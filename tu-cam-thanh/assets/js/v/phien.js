/* SINH TỰ ĐỘNG bởi tu-cam-thanh-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái của runtime giao dịch, để trang tĩnh đọc được mà không
   cần server và không cần khoá API. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem README):
       python run.py            ghi mỗi vòng lặp
       python -m trader.snapshot   ghi một lần rồi thoát
*/
window.TU_CAM_THANH = {
 "generatedAt": "2026-08-15T14:59:48.417Z",
 "chayTu": "2026-08-15T14:29:19+00:00",
 "vong": 88,
 "tamDung": false,
 "san": "testnet",
 "cheDoSan": "testnet",
 "chiLong": true,
 "cap": "BTCUSDT",
 "khung": {
  "primary": "1h",
  "context": "4h"
 },
 "gia": 63045.7,
 "nguon": {
  "name": "data-api.binance.vision",
  "live": true,
  "lastOk": "21:59:48",
  "lastError": null
 },
 "cheDo": {
  "primary": "RANGE",
  "flags": [
   "LOW_VOLATILITY"
  ],
  "quality": "MEDIUM",
  "reasons": [
   "ADX 17.5 < 18 — không bên nào kiểm soát",
   "dải Bollinger co còn 0.42%"
  ],
  "contextTrend": "BEARISH_ALIGNED",
  "adx": 17.5,
  "volatility": "LOW",
  "key": "RANGE|LOW_VOLATILITY"
 },
 "thiTruong": {
  "1h": {
   "price": 63045.7,
   "ema20": 63041.89,
   "ema50": 63158.65,
   "ema200": 63720.82,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 49.3,
   "rsiSlope": -0.08,
   "macdHist": 10.76,
   "macdHistSlope": -1.04,
   "atr": 120.28,
   "atrPct": 0.191,
   "atrRatioVsMedian": 0.55,
   "volatility": "LOW",
   "adx": 17.5,
   "plusDI": 14.3,
   "minusDI": 22.4,
   "bbWidthPct": 0.42,
   "bbPosition": 0.55,
   "volumeRatio": 0.13,
   "structure": "TRANSITION",
   "swingHighs": [
    63247.05,
    63066.13,
    63187.98,
    63080.88
   ],
   "swingLows": [
    62830.0,
    62800.0,
    62920.0,
    62946.58
   ],
   "support": [
    {
     "price": 62790.58,
     "touches": 7
    }
   ],
   "resistance": [
    {
     "price": 63256.49,
     "touches": 9
    },
    {
     "price": 63631.08,
     "touches": 5
    },
    {
     "price": 64004.5,
     "touches": 2
    }
   ],
   "range20High": 63187.98,
   "range20Low": 62800.0,
   "distToRange20HighPct": 0.23,
   "distToRange20LowPct": 0.39
  },
  "4h": {
   "price": 63045.7,
   "ema20": 63314.61,
   "ema50": 63737.57,
   "ema200": 63924.1,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 38.5,
   "rsiSlope": 0.15,
   "macdHist": 17.36,
   "macdHistSlope": 10.029,
   "atr": 367.66,
   "atrPct": 0.583,
   "atrRatioVsMedian": 0.73,
   "volatility": "NORMAL",
   "adx": 30.7,
   "plusDI": 13.4,
   "minusDI": 28.1,
   "bbWidthPct": 2.16,
   "bbPosition": 0.31,
   "volumeRatio": 0.28,
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
   "distToRange20HighPct": 2.31,
   "distToRange20LowPct": 0.81
  }
 },
 "luanDiem": {
  "regime_read": "RANGE",
  "market_summary": "[mock] RANGE, ADX 17.5, RSI 48.9, EMA BEARISH_ALIGNED",
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
  "at": "2026-08-15T14:53:09+00:00"
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
  "von": 73045.7,
  "vonThucHien": 73045.7,
  "dinhVon": 73051.42,
  "laiLoMo": 0.0,
  "laiLoHomNay": -0.0,
  "drawdownPct": 0.01,
  "soLenhDaDong": 2,
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
   "count": 9,
   "wins": 6,
   "winRate": 66.7,
   "expectancyR": 0.971,
   "totalPnl": 405.82,
   "avgWinR": 1.46,
   "avgLossR": 0.0,
   "maxLossR": 0
  },
  "byRegime": {
   "RANGE": {
    "count": 9,
    "wins": 6,
    "winRate": 66.7,
    "expectancyR": 0.971,
    "totalPnl": 405.82,
    "avgWinR": 1.46,
    "avgLossR": 0.0,
    "maxLossR": 0
   }
  },
  "byStrategy": {
   "MOCK_RULES_V1": {
    "count": 6,
    "wins": 6,
    "winRate": 100.0,
    "expectancyR": 1.457,
    "totalPnl": 405.82,
    "avgWinR": 1.46,
    "avgLossR": null,
    "maxLossR": 1.44
   },
   "THU_MOT_LENH": {
    "count": 3,
    "wins": 0,
    "winRate": 0.0,
    "expectancyR": 0.0,
    "totalPnl": 0.0,
    "avgWinR": null,
    "avgLossR": 0.0,
    "maxLossR": 0
   }
  }
 },
 "giaoDich": [
  {
   "id": "t_0ab1e922f9",
   "openedAt": "2026-08-15T14:15:08+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.00063,
   "entry": 63010.01,
   "requestedEntry": 63010.0,
   "stopLoss": 62817.77,
   "targets": [
    63711.41
   ],
   "riskAmount": 0.12,
   "plannedRiskAmount": 0.12,
   "riskPct": 0.5,
   "rr": 3.65,
   "plannedRr": 2.12,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "RANGE",
   "regimeKey": "RANGE|LOW_VOLATILITY",
   "strategy": "THU_MOT_LENH",
   "confidence": 0.75,
   "reasonCodes": [
    "THU_TAY"
   ],
   "thesisSummary": "Lệnh thử đường ống, không phải tín hiệu.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 3346838,
   "ocoOrderListId": 104536,
   "ocoError": null,
   "closedAt": "2026-08-15T14:15:09+00:00",
   "exit": 63010.0,
   "exitReason": "THU_XONG",
   "grossPnl": -0.0,
   "pnl": -0.0,
   "rMultiple": -0.0
  },
  {
   "id": "t_0273081956",
   "openedAt": "2026-08-15T14:12:08+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.00063,
   "entry": 63029.87,
   "requestedEntry": 63029.87,
   "stopLoss": 62839.77,
   "targets": [
    63726.9
   ],
   "riskAmount": 0.12,
   "plannedRiskAmount": 0.12,
   "riskPct": 0.5,
   "rr": 3.67,
   "plannedRr": 2.12,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "RANGE",
   "regimeKey": "RANGE|LOW_VOLATILITY",
   "strategy": "THU_MOT_LENH",
   "confidence": 0.75,
   "reasonCodes": [
    "THU_TAY"
   ],
   "thesisSummary": "Lệnh thử đường ống, không phải tín hiệu.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 3346295,
   "ocoOrderListId": 104517,
   "ocoError": null,
   "closedAt": "2026-08-15T14:14:50+00:00",
   "exit": 63029.86,
   "exitReason": "DOI_SO_DONG_TAY",
   "grossPnl": -0.0,
   "pnl": -0.0,
   "rMultiple": -0.0
  },
  {
   "id": "t_0273081956",
   "openedAt": "2026-08-15T14:12:08+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.00063,
   "entry": 63029.87,
   "requestedEntry": 63029.87,
   "stopLoss": 62839.77,
   "targets": [
    63726.9
   ],
   "riskAmount": 0.12,
   "plannedRiskAmount": 0.12,
   "riskPct": 0.5,
   "rr": 3.67,
   "plannedRr": 2.12,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "RANGE",
   "regimeKey": "RANGE|LOW_VOLATILITY",
   "strategy": "THU_MOT_LENH",
   "confidence": 0.75,
   "reasonCodes": [
    "THU_TAY"
   ],
   "thesisSummary": "Lệnh thử đường ống, không phải tín hiệu.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 3346295,
   "ocoOrderListId": 104517,
   "ocoError": null,
   "closedAt": "2026-08-15T14:12:09+00:00",
   "exit": 63029.86,
   "exitReason": "OCO_FILLED",
   "grossPnl": -0.0,
   "pnl": -0.0,
   "rMultiple": -0.0
  },
  {
   "id": "t_a0c719bdef",
   "openedAt": "2026-08-15T14:11:00+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.15760029457512972,
   "entry": 63134.4,
   "requestedEntry": 63039.84,
   "stopLoss": 62850.23,
   "targets": [
    63702.74,
    64051.1
   ],
   "riskAmount": 44.79,
   "plannedRiskAmount": 44.79,
   "slippageCostOnRisk": -0.0,
   "riskPct": 0.5,
   "rr": 2.0,
   "plannedRr": 2.0,
   "stopAtrMultiple": 1.5,
   "feesPaid": 19.97,
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
   "closedAt": "2026-08-15T14:11:00+00:00",
   "exit": 63607.19,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 74.51,
   "pnl": 64.49,
   "rMultiple": 1.44,
   "holdingMinutes": 0
  },
  {
   "id": "t_d5b132ea11",
   "openedAt": "2026-08-15T14:10:43+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.15760029457512972,
   "entry": 63134.4,
   "requestedEntry": 63039.84,
   "stopLoss": 62850.23,
   "targets": [
    63702.74,
    64051.1
   ],
   "riskAmount": 44.79,
   "plannedRiskAmount": 44.79,
   "slippageCostOnRisk": -0.0,
   "riskPct": 0.5,
   "rr": 2.0,
   "plannedRr": 2.0,
   "stopAtrMultiple": 1.5,
   "feesPaid": 19.97,
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
   "closedAt": "2026-08-15T14:10:43+00:00",
   "exit": 63607.19,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 74.51,
   "pnl": 64.49,
   "rMultiple": 1.44,
   "holdingMinutes": 0
  },
  {
   "id": "t_9648cf635a",
   "openedAt": "2026-08-15T14:06:44+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.1583968791252982,
   "entry": 63132.56,
   "requestedEntry": 63038.0,
   "stopLoss": 62848.39,
   "targets": [
    63700.89,
    64049.26
   ],
   "riskAmount": 45.01,
   "plannedRiskAmount": 45.01,
   "slippageCostOnRisk": 0.0,
   "riskPct": 0.5,
   "rr": 2.0,
   "plannedRr": 2.0,
   "stopAtrMultiple": 1.5,
   "feesPaid": 20.07,
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
   "closedAt": "2026-08-15T14:06:44+00:00",
   "exit": 63605.34,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 74.89,
   "pnl": 64.81,
   "rMultiple": 1.44,
   "holdingMinutes": 0
  },
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
