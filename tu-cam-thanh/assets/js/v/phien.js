/* SINH TỰ ĐỘNG bởi tu-cam-thanh-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái của runtime giao dịch, để trang tĩnh đọc được mà không
   cần server và không cần khoá API. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem README):
       python run.py            ghi mỗi vòng lặp
       python -m trader.snapshot   ghi một lần rồi thoát
*/
window.TU_CAM_THANH = {
 "generatedAt": "2026-08-15T17:27:04.327Z",
 "chayTu": "2026-08-15T17:01:54+00:00",
 "vong": 73,
 "tamDung": false,
 "san": "testnet",
 "cheDoSan": "testnet",
 "chiLong": true,
 "cap": "BTCUSDT",
 "khung": {
  "primary": "1h",
  "context": "4h"
 },
 "gia": 63070.49,
 "nguon": {
  "name": "data-api.binance.vision",
  "live": true,
  "lastOk": "00:27:04",
  "lastError": null
 },
 "cheDo": {
  "primary": "RANGE",
  "flags": [
   "LOW_VOLATILITY"
  ],
  "quality": "MEDIUM",
  "reasons": [
   "ADX 15.8 < 18 — không bên nào kiểm soát",
   "dải Bollinger co còn 0.36%"
  ],
  "contextTrend": "BEARISH_ALIGNED",
  "adx": 15.8,
  "volatility": "LOW",
  "key": "RANGE|LOW_VOLATILITY"
 },
 "thiTruong": {
  "1h": {
   "price": 63070.49,
   "ema20": 63053.6,
   "ema50": 63154.84,
   "ema200": 63707.37,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 50.5,
   "rsiSlope": 0.51,
   "macdHist": 13.08,
   "macdHistSlope": 0.384,
   "atr": 115.12,
   "atrPct": 0.183,
   "atrRatioVsMedian": 0.53,
   "volatility": "LOW",
   "adx": 15.8,
   "plusDI": 16.4,
   "minusDI": 20.2,
   "bbWidthPct": 0.36,
   "bbPosition": 0.58,
   "volumeRatio": 0.24,
   "structure": "UPTREND",
   "swingHighs": [
    63617.45,
    63247.05,
    63066.13,
    63187.98
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
     "price": 63278.44,
     "touches": 8
    },
    {
     "price": 63631.08,
     "touches": 5
    },
    {
     "price": 63972.34,
     "touches": 3
    }
   ],
   "range20High": 63187.98,
   "range20Low": 62800.0,
   "distToRange20HighPct": 0.19,
   "distToRange20LowPct": 0.43
  },
  "4h": {
   "price": 63070.49,
   "ema20": 63296.09,
   "ema50": 63713.48,
   "ema200": 63916.84,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 39.6,
   "rsiSlope": 0.27,
   "macdHist": 28.37,
   "macdHistSlope": 9.22,
   "atr": 348.2,
   "atrPct": 0.552,
   "atrRatioVsMedian": 0.69,
   "volatility": "NORMAL",
   "adx": 30.7,
   "plusDI": 13.9,
   "minusDI": 27.6,
   "bbWidthPct": 1.7,
   "bbPosition": 0.33,
   "volumeRatio": 0.15,
   "structure": "TRANSITION",
   "swingHighs": [
    64515.43,
    64500.0,
    64010.0,
    63247.05
   ],
   "swingLows": [
    63310.34,
    62802.27,
    62535.24,
    62920.0
   ],
   "support": [
    {
     "price": 62861.13,
     "touches": 2
    },
    {
     "price": 62535.24,
     "touches": 1
    }
   ],
   "resistance": [
    {
     "price": 63265.13,
     "touches": 3
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
   "distToRange20HighPct": 2.27,
   "distToRange20LowPct": 0.85
  }
 },
 "luanDiem": {
  "regime_read": "RANGE",
  "market_summary": "[mock] RANGE, ADX 15.8, RSI 52.2, EMA BEARISH_ALIGNED",
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
  "at": "2026-08-15T17:01:56+00:00"
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
  "von": 73070.49,
  "vonThucHien": 73070.49,
  "dinhVon": 73100.69,
  "laiLoMo": 0.0,
  "laiLoHomNay": -0.0,
  "drawdownPct": 0.04,
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
   "count": 10,
   "wins": 7,
   "winRate": 70.0,
   "expectancyR": 1.014,
   "totalPnl": 463.77,
   "avgWinR": 1.45,
   "avgLossR": 0.0,
   "maxLossR": 0
  },
  "byRegime": {
   "RANGE": {
    "count": 10,
    "wins": 7,
    "winRate": 70.0,
    "expectancyR": 1.014,
    "totalPnl": 463.77,
    "avgWinR": 1.45,
    "avgLossR": 0.0,
    "maxLossR": 0
   }
  },
  "byStrategy": {
   "MOCK_RULES_V1": {
    "count": 7,
    "wins": 7,
    "winRate": 100.0,
    "expectancyR": 1.449,
    "totalPnl": 463.77,
    "avgWinR": 1.45,
    "avgLossR": null,
    "maxLossR": 1.4
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
   "id": "t_9d533893f2",
   "openedAt": "2026-08-15T16:53:01+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.1574584716894351,
   "entry": 63191.26,
   "requestedEntry": 63096.62,
   "stopLoss": 62927.64,
   "targets": [
    63718.52,
    63997.85
   ],
   "riskAmount": 41.51,
   "plannedRiskAmount": 41.51,
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
   "closedAt": "2026-08-15T16:53:01+00:00",
   "exit": 63622.94,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 67.97,
   "pnl": 57.95,
   "rMultiple": 1.4,
   "holdingMinutes": 0
  },
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
 "baiHoc": [],
 "theGioi": {
  "luc": 1786814223.3312566,
  "phaiSinh": {
   "fundingNamHoa": 4.92,
   "openInterestUsd": 7052187705.819402,
   "oiDoi24hPct": -0.5,
   "topTrader": {
    "tyLe": 1.4699,
    "long": 0.5951,
    "short": 0.4049,
    "doi12h": -0.012
   },
   "toanSan": {
    "tyLe": 2.076,
    "long": 0.6749,
    "short": 0.3251,
    "doi12h": 0.023
   },
   "nguon": "Binance Futures"
  },
  "viMo": {
   "muc": {
    "DXY": {
     "ten": "chỉ số đô la",
     "gia": 99.67,
     "doiPct": -0.29
    },
    "US10Y": {
     "ten": "lợi suất trái phiếu 10 năm",
     "gia": 4.696,
     "doiPct": 1.19
    },
    "DAU": {
     "ten": "dầu WTI",
     "gia": 82.4,
     "doiPct": 1.42
    },
    "SP500": {
     "ten": "S&P 500",
     "gia": 7785.76,
     "doiPct": -0.17
    },
    "VANG": {
     "ten": "vàng",
     "gia": 4380.4,
     "doiPct": 0.38
    }
   },
   "khauVi": {
    "diem": -0.56,
    "soChiSo": 3,
    "nhan": "RISK_OFF",
    "ghiChu": "suy ra từ chiều đổi của DXY, lợi suất và S&P — không phải một chỉ số có sẵn"
   },
   "nguon": "Yahoo Finance"
  },
  "tamLy": {
   "gt": 34,
   "nhan": "Fear",
   "chuoi": [
    30,
    31,
    30,
    29,
    27,
    29,
    29,
    34
   ]
  },
  "tin": [
   {
    "ma": "FED",
    "soBai": 6,
    "bai": [
     {
      "tieuDe": "Federal Reserve issues FOMC statement",
      "nguon": "Fed",
      "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"
     },
     {
      "tieuDe": "Minutes of the Board's discount rate meetings on June 8 and June 17, 2026",
      "nguon": "Fed",
      "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260714a.htm"
     }
    ]
   },
   {
    "ma": "LAM_PHAT",
    "soBai": 1,
    "bai": [
     {
      "tieuDe": "Bitcoin slips as U.S. inflation fails to spark gains, ETFs see August's first two-day drawdown",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/markets/2026/08/14/bitcoin-slips-as-u-s-inflation-fails-to-spark-gains-etfs-see-august-s-first-two-day-drawdown"
     }
    ]
   },
   {
    "ma": "QUY_DINH",
    "soBai": 5,
    "bai": [
     {
      "tieuDe": "Tokenization stocks slip as SEC delay puts 'speed bump' in crypto’s Wall Street push",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/markets/2026/08/14/tokenization-stocks-slip-as-sec-delay-puts-speed-bump-in-crypto-s-wall-street-push"
     },
     {
      "tieuDe": "SEC cancels long-awaited proposal of Reg Crypto, postponing meeting without new date",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/policy/2026/08/13/sec-cancels-long-awaited-proposal-of-reg-crypto-postponing-meeting-without-new-date"
     }
    ]
   },
   {
    "ma": "ETF",
    "soBai": 6,
    "bai": [
     {
      "tieuDe": "Swiss mega-bank UBS ramps up its Bitcoin exposure with a massive 24-fold surge in ETF call options",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/business/2026/08/15/swiss-mega-bank-ubs-ramps-up-its-bitcoin-exposure-with-a-massive-24-fold-surge-in-etf-call-options"
     },
     {
      "tieuDe": "Paul Tudor Jones’ investment firm increases stake in BlackRock's bitcoin ETF after year of selling",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/business/2026/08/15/paul-tudor-jones-investment-firm-increases-blackrock-s-bitcoin-etf-stake-after-year-of-selling"
     }
    ]
   },
   {
    "ma": "VI_MO",
    "soBai": 2,
    "bai": [
     {
      "tieuDe": "Fear is fading across markets, be it bitcoin, stocks, gold or bonds",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/daybook-us/2026/08/14/volatility-exits-crypto-tradfi-markets-even-as-u-s-iran-risks-linger-sovereign-debt-rises"
     },
     {
      "tieuDe": "Amex Green vs. Amex Gold: Tons of benefits and rewards for foodies and travelers",
      "nguon": "Yahoo",
      "url": "https://finance.yahoo.com/personal-finance/credit-cards/comparison/amex-green-vs-gold-174325977.html"
     }
    ]
   }
  ],
  "soFeed": 9,
  "soBai": 186
 },
 "huanLuyen": {
  "viec": "quet",
  "xong": 1786813332.0640948,
  "totNhat": {
   "bo": {
    "stopAtr": 2.5,
    "demTp": 1.3,
    "adxToiThieu": 0,
    "chanBienDongCao": false
   },
   "trongMau": {
    "so": 50,
    "soThang": 21,
    "soThua": 29,
    "tyLeThang": 42.0,
    "kyVongR": 0.085,
    "tongR": 4.26,
    "trungBinhThangR": 1.475,
    "trungBinhThuaR": -0.922,
    "heSoLoiNhuan": 1.16,
    "sutGiamToiDaPct": 3.92,
    "chuoiThuaDaiNhat": 8,
    "vonDau": 10000,
    "vonCuoi": 10203.07,
    "loiNhuanPct": 2.03,
    "trungBinhNenGiu": 30.3,
    "theoLyDoThoat": {
     "TP": 10,
     "SL": 23,
     "HET_HAN": 17
    }
   },
   "ngoaiMau": {
    "so": 27,
    "soThang": 6,
    "soThua": 21,
    "tyLeThang": 22.2,
    "kyVongR": -0.645,
    "tongR": -17.43,
    "trungBinhThangR": 0.731,
    "trungBinhThuaR": -1.039,
    "heSoLoiNhuan": 0.2,
    "sutGiamToiDaPct": 8.38,
    "chuoiThuaDaiNhat": 5,
    "vonDau": 10000,
    "vonCuoi": 9162.25,
    "loiNhuanPct": -8.38,
    "trungBinhNenGiu": 24.1,
    "theoLyDoThoat": {
     "TP": 0,
     "SL": 18,
     "HET_HAN": 9
    }
   },
   "khopTroi": 0.73
  },
  "ketLuan": "bộ tốt nhất trong mẫu (+0.085R) rơi xuống -0.645R khi ra ngoài mẫu — ĐỪNG áp dụng (bộ đang dùng: -0.666R trên 44 lệnh)",
  "soToHop": 72,
  "mocCat": 2800,
  "tongNen": 4000
 }
};
