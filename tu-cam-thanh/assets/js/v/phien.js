/* SINH TỰ ĐỘNG bởi tu-cam-thanh-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái của runtime giao dịch, để trang tĩnh đọc được mà không
   cần server và không cần khoá API. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem README):
       python run.py            ghi mỗi vòng lặp
       python -m trader.snapshot   ghi một lần rồi thoát
*/
window.TU_CAM_THANH = {
 "generatedAt": "2026-08-28T15:36:13.733Z",
 "chayTu": "2026-08-28T15:11:10+00:00",
 "vong": 72,
 "tamDung": false,
 "san": "testnet",
 "cheDoSan": "testnet",
 "chiLong": true,
 "cap": "BTCUSDT",
 "khung": {
  "primary": "4h",
  "context": "1d"
 },
 "gia": 79207.98,
 "nguon": {
  "name": "data-api.binance.vision",
  "live": true,
  "lastOk": "22:36:13",
  "lastError": null
 },
 "cheDo": {
  "primary": "TREND_UP",
  "flags": [],
  "quality": "HIGH",
  "reasons": [
   "ADX 37.9 ≥ 22, EMA xếp tăng, cấu trúc TRANSITION"
  ],
  "contextTrend": "MIXED",
  "adx": 37.9,
  "volatility": "NORMAL",
  "key": "TREND_UP|none"
 },
 "thiTruong": {
  "4h": {
   "price": 79207.98,
   "ema20": 79136.62,
   "ema50": 76748.49,
   "ema200": 69510.2,
   "emaStack": "BULLISH_ALIGNED",
   "rsi14": 54.5,
   "rsiSlope": -1.91,
   "macdHist": -159.95,
   "macdHistSlope": -26.27,
   "atr": 1092.79,
   "atrPct": 1.38,
   "atrRatioVsMedian": 1.1,
   "volatility": "NORMAL",
   "adx": 37.9,
   "plusDI": 24.8,
   "minusDI": 16.5,
   "bbWidthPct": 2.98,
   "bbPosition": 0.5,
   "volumeRatio": 1.64,
   "structure": "TRANSITION",
   "swingHighs": [
    80000.0,
    81272.62,
    79174.12,
    81478.87
   ],
   "swingLows": [
    75545.67,
    76670.01,
    77851.0,
    77632.58
   ],
   "support": [
    {
     "price": 79174.12,
     "touches": 1
    },
    {
     "price": 78828.15,
     "touches": 1
    },
    {
     "price": 78052.85,
     "touches": 1
    }
   ],
   "resistance": [
    {
     "price": 79500.0,
     "touches": 1
    },
    {
     "price": 80000.0,
     "touches": 1
    },
    {
     "price": 81375.74,
     "touches": 2
    }
   ],
   "mauGia": {
    "co": false,
    "so": 0,
    "mau": [],
    "mauThuan": false
   },
   "range20High": 81478.87,
   "range20Low": 77632.58,
   "distToRange20HighPct": 2.87,
   "distToRange20LowPct": 1.99
  },
  "1d": {
   "price": 79225.51,
   "ema20": 72730.64,
   "ema50": 68683.89,
   "ema200": 72958.9,
   "emaStack": "MIXED",
   "rsi14": 76.8,
   "rsiSlope": -1.04,
   "macdHist": 1079.27,
   "macdHistSlope": -158.976,
   "atr": 2337.96,
   "atrPct": 2.951,
   "atrRatioVsMedian": 1.03,
   "volatility": "NORMAL",
   "adx": 42.4,
   "plusDI": 43.6,
   "minusDI": 7.7,
   "bbWidthPct": 40.19,
   "bbPosition": 0.81,
   "volumeRatio": 0.73,
   "structure": "UPTREND",
   "swingHighs": [
    65409.56,
    65474.46,
    79500.0,
    81272.62
   ],
   "swingLows": [
    63739.75,
    62742.47,
    62275.0,
    62535.24
   ],
   "support": [
    {
     "price": 67292.15,
     "touches": 1
    },
    {
     "price": 66956.15,
     "touches": 1
    },
    {
     "price": 65570.29,
     "touches": 5
    }
   ],
   "resistance": [
    {
     "price": 79500.0,
     "touches": 1
    },
    {
     "price": 81272.62,
     "touches": 1
    }
   ],
   "mauGia": {
    "co": true,
    "so": 3,
    "mau": [
     {
      "ten": "HAI_ĐÁY",
      "loai": "ĐẢO_CHIỀU",
      "huong": "LONG",
      "rr": 0.63,
      "doTin": 0.86
     },
     {
      "ten": "VAI_ĐẦU_VAI_NGƯỢC",
      "loai": "ĐẢO_CHIỀU",
      "huong": "LONG",
      "rr": 0.64,
      "doTin": 0.91
     },
     {
      "ten": "NẾN_TRÙM_GIẢM",
      "loai": "ĐẢO_CHIỀU",
      "huong": "SHORT",
      "rr": 1.36,
      "doTin": 0.5
     }
    ],
    "mauThuan": true
   },
   "range20High": 81272.62,
   "range20Low": 62535.24,
   "distToRange20HighPct": 2.58,
   "distToRange20LowPct": 21.07
  }
 },
 "luanDiem": {
  "regime_read": "TREND_UP",
  "market_summary": "[mock] TREND_UP, ADX 37.9, RSI 56.1, EMA BULLISH_ALIGNED",
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
  "action": "LONG",
  "confidence": 0.6,
  "entry_zone": [
   79302.61,
   79461.37
  ],
  "invalidation": 77742.81,
  "invalidation_logic": "1.5×ATR ngược hướng — mất vùng này là hết xu hướng ngắn hạn",
  "targets": [
   83199.36,
   85489.78
  ],
  "suggested_risk_pct": 0.5,
  "strategy": "MOCK_RULES_V1",
  "reason_codes": [
   "MOCK_BRAIN",
   "TREND_ALIGNED",
   "ADX_CONFIRMS"
  ],
  "reasoning": "[mock] Thuận TREND_UP với ADX 37.9. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.377%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
  "event_risk": "UNKNOWN",
  "symbol": "BTCUSDT",
  "source": "mock",
  "regimeFromClassifier": "TREND_UP",
  "at": "2026-08-28T15:11:12+00:00"
 },
 "phanQuyet": {
  "approved": true,
  "action": "LONG",
  "rejections": [],
  "rr": 2.1033929966568268,
  "note": "trong hạn mức",
  "position": {
   "side": "LONG",
   "entry": 79381.99,
   "expectedFill": 79501.06,
   "costDragOnEntry": 119.07,
   "stopLoss": 77742.81,
   "targets": [
    83199.36,
    85489.78
   ],
   "qty": 0.02744994628858806,
   "notional": 2182.3,
   "riskAmount": 48.26,
   "riskPct": 0.5,
   "riskBase": 9652.79,
   "riskBaseIsCash": true,
   "riskPctOfEquity": 0.0542,
   "stopDistance": 1758.25,
   "structuralStopDistance": 1639.18,
   "stopAtrMultiple": 1.5,
   "rr": 2.1,
   "suggestedRiskPct": 0.5,
   "riskPctCapped": false,
   "notionalCapped": false
  }
 },
 "taiKhoan": {
  "vonBanDau": 10000,
  "von": 88855.94,
  "vonThucHien": 88855.94,
  "dinhVon": 89587.53,
  "laiLoMo": -4.83,
  "laiLoHomNay": 0.0,
  "drawdownPct": 0.82,
  "soLenhDaDong": 40,
  "viThe": [
   {
    "id": "t_922b195af0",
    "openedAt": "2026-08-28T15:11:12+00:00",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "qty": 0.02744,
    "entry": 79384.0,
    "requestedEntry": 79381.99,
    "stopLoss": 77742.81,
    "targets": [
     83199.36
    ],
    "riskAmount": 45.03,
    "plannedRiskAmount": 48.26,
    "riskPct": 0.5,
    "rr": 2.32,
    "plannedRr": 2.1,
    "stopAtrMultiple": 1.5,
    "feesPaid": 0,
    "regimeAtEntry": "TREND_UP",
    "regimeKey": "TREND_UP|none",
    "strategy": "MOCK_RULES_V1",
    "confidence": 0.6,
    "reasonCodes": [
     "MOCK_BRAIN",
     "TREND_ALIGNED",
     "ADX_CONFIRMS"
    ],
    "thesisSummary": "[mock] Thuận TREND_UP với ADX 37.9. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.377%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
    "status": "OPEN",
    "venue": "binance-spot-testnet",
    "entryOrderId": 9393304,
    "ocoOrderListId": 284358,
    "ocoError": null,
    "unrealizedPnl": -4.83,
    "unrealizedR": -0.11
   }
  ]
 },
 "rui_ro": {
  "dungHan": null,
  "ngatMach": [
   "MAX_POSITIONS: đang giữ 1/1 vị thế"
  ],
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
  "soKyNang": 13
 },
 "thongKe": {
  "overall": {
   "count": 38,
   "wins": 10,
   "winRate": 26.3,
   "expectancyR": -0.202,
   "totalPnl": -358.19,
   "expectancyUsd": -9.43,
   "riskCv": 0.362,
   "riskDeu": false,
   "canhBao": null,
   "avgWinR": 2.61,
   "avgLossR": -1.21,
   "maxLossR": -1.56
  },
  "byRegime": {
   "TREND_UP": {
    "count": 38,
    "wins": 10,
    "winRate": 26.3,
    "expectancyR": -0.202,
    "totalPnl": -358.19,
    "expectancyUsd": -9.43,
    "riskCv": 0.362,
    "riskDeu": false,
    "canhBao": null,
    "avgWinR": 2.61,
    "avgLossR": -1.21,
    "maxLossR": -1.56
   }
  },
  "byStrategy": {
   "MOCK_RULES_V1": {
    "count": 38,
    "wins": 10,
    "winRate": 26.3,
    "expectancyR": -0.202,
    "totalPnl": -358.19,
    "expectancyUsd": -9.43,
    "riskCv": 0.362,
    "riskDeu": false,
    "canhBao": null,
    "avgWinR": 2.61,
    "avgLossR": -1.21,
    "maxLossR": -1.56
   }
  }
 },
 "giaoDich": [
  {
   "id": "t_26bec9c59e",
   "openedAt": "2026-08-21T22:24:15+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03205,
   "entry": 78087.06,
   "requestedEntry": 78139.35,
   "stopLoss": 76767.38,
   "targets": [
    81389.69
   ],
   "riskAmount": 42.3,
   "plannedRiskAmount": 47.73,
   "riskPct": 0.5,
   "rr": 2.5,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 56.5. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.171%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5922448,
   "ocoOrderListId": 182483,
   "ocoError": null,
   "closedAt": "2026-08-21T22:48:49+00:00",
   "exit": 81389.69,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 105.85,
   "pnl": 105.85,
   "rMultiple": 2.5
  },
  {
   "id": "t_392a855d4e",
   "openedAt": "2026-08-21T21:22:31+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03274,
   "entry": 78100.01,
   "requestedEntry": 78100.01,
   "stopLoss": 76751.38,
   "targets": [
    81301.15
   ],
   "riskAmount": 44.15,
   "plannedRiskAmount": 47.99,
   "riskPct": 0.5,
   "rr": 2.37,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 56.8. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.151%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5885340,
   "ocoOrderListId": 181581,
   "ocoError": null,
   "closedAt": "2026-08-21T21:28:50+00:00",
   "exit": 76521.12,
   "exitReason": "STOP_LOSS",
   "grossPnl": -51.69,
   "pnl": -51.69,
   "rMultiple": -1.17
  },
  {
   "id": "t_8413f9bc3a",
   "openedAt": "2026-08-21T19:59:51+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03364,
   "entry": 76994.01,
   "requestedEntry": 76976.76,
   "stopLoss": 75658.71,
   "targets": [
    80108.37
   ],
   "riskAmount": 44.92,
   "plannedRiskAmount": 48.23,
   "riskPct": 0.5,
   "rr": 2.33,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 57.8. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.142%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5838308,
   "ocoOrderListId": 180596,
   "ocoError": null,
   "closedAt": "2026-08-21T20:03:43+00:00",
   "exit": 75581.51,
   "exitReason": "STOP_LOSS",
   "grossPnl": -47.52,
   "pnl": -47.52,
   "rMultiple": -1.06
  },
  {
   "id": "t_8141408e9b",
   "openedAt": "2026-08-21T18:53:25+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03343,
   "entry": 77190.0,
   "requestedEntry": 77174.0,
   "stopLoss": 75839.58,
   "targets": [
    80340.93
   ],
   "riskAmount": 45.14,
   "plannedRiskAmount": 48.49,
   "riskPct": 0.5,
   "rr": 2.33,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 59.7. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.153%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5806527,
   "ocoOrderListId": 179958,
   "ocoError": null,
   "closedAt": "2026-08-21T19:54:37+00:00",
   "exit": 75612.06,
   "exitReason": "STOP_LOSS",
   "grossPnl": -52.75,
   "pnl": -52.75,
   "rMultiple": -1.17
  },
  {
   "id": "t_9244d92a68",
   "openedAt": "2026-08-21T17:53:21+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03357,
   "entry": 77392.01,
   "requestedEntry": 77392.01,
   "stopLoss": 76056.05,
   "targets": [
    80563.2
   ],
   "riskAmount": 44.85,
   "plannedRiskAmount": 48.75,
   "riskPct": 0.5,
   "rr": 2.37,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 62.7. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.151%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5776982,
   "ocoOrderListId": 179404,
   "ocoError": null,
   "closedAt": "2026-08-21T18:03:33+00:00",
   "exit": 75828.46,
   "exitReason": "STOP_LOSS",
   "grossPnl": -52.49,
   "pnl": -52.49,
   "rMultiple": -1.17
  },
  {
   "id": "t_8c0f417944",
   "openedAt": "2026-08-21T16:53:12+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03266,
   "entry": 77486.01,
   "requestedEntry": 77505.93,
   "stopLoss": 76121.75,
   "targets": [
    80778.93
   ],
   "riskAmount": 44.56,
   "plannedRiskAmount": 49.01,
   "riskPct": 0.5,
   "rr": 2.41,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 63.9. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.191%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5750235,
   "ocoOrderListId": 178765,
   "ocoError": null,
   "closedAt": "2026-08-21T17:10:44+00:00",
   "exit": 75893.38,
   "exitReason": "STOP_LOSS",
   "grossPnl": -52.02,
   "pnl": -52.02,
   "rMultiple": -1.17
  },
  {
   "id": "t_ed56df2bc7",
   "openedAt": "2026-08-21T15:53:15+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03237,
   "entry": 77221.99,
   "requestedEntry": 77241.99,
   "stopLoss": 75836.0,
   "targets": [
    80559.55
   ],
   "riskAmount": 44.86,
   "plannedRiskAmount": 49.27,
   "riskPct": 0.5,
   "rr": 2.41,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 66.0. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.213%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5723026,
   "ocoOrderListId": 178062,
   "ocoError": null,
   "closedAt": "2026-08-21T15:58:09+00:00",
   "exit": 75608.49,
   "exitReason": "STOP_LOSS",
   "grossPnl": -52.23,
   "pnl": -52.23,
   "rMultiple": -1.16
  },
  {
   "id": "t_1cfa383fd2",
   "openedAt": "2026-08-21T14:53:14+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03182,
   "entry": 77384.69,
   "requestedEntry": 77373.12,
   "stopLoss": 75932.89,
   "targets": [
    80763.19
   ],
   "riskAmount": 46.2,
   "plannedRiskAmount": 49.53,
   "riskPct": 0.5,
   "rr": 2.33,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 66.7. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.241%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5691422,
   "ocoOrderListId": 177257,
   "ocoError": null,
   "closedAt": "2026-08-21T15:00:34+00:00",
   "exit": 75705.09,
   "exitReason": "STOP_LOSS",
   "grossPnl": -53.44,
   "pnl": -53.44,
   "rMultiple": -1.16
  },
  {
   "id": "t_6633640f2f",
   "openedAt": "2026-08-21T13:53:12+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03173,
   "entry": 77266.88,
   "requestedEntry": 77253.99,
   "stopLoss": 75800.65,
   "targets": [
    80671.02
   ],
   "riskAmount": 46.52,
   "plannedRiskAmount": 49.8,
   "riskPct": 0.5,
   "rr": 2.32,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 67.9. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.254%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5667757,
   "ocoOrderListId": 176486,
   "ocoError": null,
   "closedAt": "2026-08-21T13:55:19+00:00",
   "exit": 75573.24,
   "exitReason": "STOP_LOSS",
   "grossPnl": -53.74,
   "pnl": -53.74,
   "rMultiple": -1.16
  },
  {
   "id": "t_1a36618aa0",
   "openedAt": "2026-08-21T12:53:18+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03277,
   "entry": 77223.66,
   "requestedEntry": 77191.82,
   "stopLoss": 75779.67,
   "targets": [
    80522.06
   ],
   "riskAmount": 47.32,
   "plannedRiskAmount": 50.07,
   "riskPct": 0.5,
   "rr": 2.28,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 69.8. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.220%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5645823,
   "ocoOrderListId": 175750,
   "ocoError": null,
   "closedAt": "2026-08-21T13:24:37+00:00",
   "exit": 75552.33,
   "exitReason": "STOP_LOSS",
   "grossPnl": -54.77,
   "pnl": -54.77,
   "rMultiple": -1.16
  },
  {
   "id": "t_fd3220171e",
   "openedAt": "2026-08-21T11:53:26+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03283,
   "entry": 76726.18,
   "requestedEntry": 76748.01,
   "stopLoss": 75329.96,
   "targets": [
    80088.56
   ],
   "riskAmount": 45.84,
   "plannedRiskAmount": 50.33,
   "riskPct": 0.5,
   "rr": 2.41,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 70.7. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.232%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5625451,
   "ocoOrderListId": 175049,
   "ocoError": null,
   "closedAt": "2026-08-21T12:07:52+00:00",
   "exit": 75103.97,
   "exitReason": "STOP_LOSS",
   "grossPnl": -53.26,
   "pnl": -53.26,
   "rMultiple": -1.16
  },
  {
   "id": "t_5611d918f9",
   "openedAt": "2026-08-21T10:53:19+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03402,
   "entry": 77810.02,
   "requestedEntry": 77796.0,
   "stopLoss": 76425.14,
   "targets": [
    81042.39
   ],
   "riskAmount": 47.11,
   "plannedRiskAmount": 50.61,
   "riskPct": 0.5,
   "rr": 2.33,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 73.8. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.175%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5603727,
   "ocoOrderListId": 174293,
   "ocoError": null,
   "closedAt": "2026-08-21T11:37:38+00:00",
   "exit": 76195.86,
   "exitReason": "STOP_LOSS",
   "grossPnl": -54.91,
   "pnl": -54.91,
   "rMultiple": -1.17
  },
  {
   "id": "t_3e61d286cb",
   "openedAt": "2026-08-21T09:53:13+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03324,
   "entry": 77910.72,
   "requestedEntry": 77938.07,
   "stopLoss": 76525.6,
   "targets": [
    81272.52
   ],
   "riskAmount": 46.04,
   "plannedRiskAmount": 50.85,
   "riskPct": 0.5,
   "rr": 2.43,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 72.8. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.208%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5585617,
   "ocoOrderListId": 173498,
   "ocoError": null,
   "closedAt": "2026-08-21T10:05:11+00:00",
   "exit": 76481.15,
   "exitReason": "STOP_LOSS",
   "grossPnl": -47.52,
   "pnl": -47.52,
   "rMultiple": -1.03
  },
  {
   "id": "t_0db4afbbc5",
   "openedAt": "2026-08-21T08:53:10+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03583,
   "entry": 79258.03,
   "requestedEntry": 79362.96,
   "stopLoss": 78055.81,
   "targets": [
    82482.97
   ],
   "riskAmount": 43.08,
   "plannedRiskAmount": 51.1,
   "riskPct": 0.5,
   "rr": 2.68,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 71.6. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.098%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5563744,
   "ocoOrderListId": 172617,
   "ocoError": null,
   "closedAt": "2026-08-21T08:56:00+00:00",
   "exit": 77821.64,
   "exitReason": "STOP_LOSS",
   "grossPnl": -51.47,
   "pnl": -51.47,
   "rMultiple": -1.19
  },
  {
   "id": "t_450e183da1",
   "openedAt": "2026-08-21T08:09:44+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.0409,
   "entry": 77000.0,
   "requestedEntry": 77063.36,
   "stopLoss": 75923.48,
   "targets": [
    79821.24
   ],
   "riskAmount": 44.03,
   "plannedRiskAmount": 51.35,
   "riskPct": 0.5,
   "rr": 2.62,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 70.0. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (0.986%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5546326,
   "ocoOrderListId": 171911,
   "ocoError": null,
   "closedAt": "2026-08-21T08:27:19+00:00",
   "exit": 75757.27,
   "exitReason": "STOP_LOSS",
   "grossPnl": -50.83,
   "pnl": -50.83,
   "rMultiple": -1.15
  },
  {
   "id": "t_d5b4fef74d",
   "openedAt": "2026-08-21T06:53:10+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.04649,
   "entry": 75646.21,
   "requestedEntry": 75630.01,
   "stopLoss": 74650.92,
   "targets": [
    78043.44
   ],
   "riskAmount": 46.27,
   "plannedRiskAmount": 50.79,
   "riskPct": 0.5,
   "rr": 2.41,
   "plannedRr": 2.11,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 68.6. SL 1.5×ATR, TP1 3.7×ATR — bội số này suy từ ATR/giá hiện tại (0.863%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5508888,
   "ocoOrderListId": 170923,
   "ocoError": null,
   "closedAt": "2026-08-21T08:09:43+00:00",
   "exit": 78043.44,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 111.45,
   "pnl": 111.45,
   "rMultiple": 2.41
  },
  {
   "id": "t_c8e3dce467",
   "openedAt": "2026-08-21T05:53:23+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.04627,
   "entry": 75422.0,
   "requestedEntry": 75404.01,
   "stopLoss": 74413.44,
   "targets": [
    77840.5
   ],
   "riskAmount": 46.67,
   "plannedRiskAmount": 51.08,
   "riskPct": 0.5,
   "rr": 2.4,
   "plannedRr": 2.11,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 67.8. SL 1.5×ATR, TP1 3.7×ATR — bội số này suy từ ATR/giá hiện tại (0.876%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5485232,
   "ocoOrderListId": 170242,
   "ocoError": null,
   "closedAt": "2026-08-21T06:39:53+00:00",
   "exit": 74190.19,
   "exitReason": "STOP_LOSS",
   "grossPnl": -57.0,
   "pnl": -57.0,
   "rMultiple": -1.22
  },
  {
   "id": "t_5a784d98f0",
   "openedAt": "2026-08-21T04:53:30+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.04544,
   "entry": 75004.47,
   "requestedEntry": 75000.0,
   "stopLoss": 74000.88,
   "targets": [
    77452.53
   ],
   "riskAmount": 45.6,
   "plannedRiskAmount": 50.52,
   "riskPct": 0.5,
   "rr": 2.44,
   "plannedRr": 2.11,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 67.0. SL 1.5×ATR, TP1 3.7×ATR — bội số này suy từ ATR/giá hiện tại (0.888%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5465005,
   "ocoOrderListId": 169686,
   "ocoError": null,
   "closedAt": "2026-08-21T05:24:02+00:00",
   "exit": 77452.53,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 111.24,
   "pnl": 111.24,
   "rMultiple": 2.44
  },
  {
   "id": "t_f880b5cf7d",
   "openedAt": "2026-08-21T00:10:41+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.05035,
   "entry": 73490.0,
   "requestedEntry": 73490.0,
   "stopLoss": 72607.91,
   "targets": [
    75689.64
   ],
   "riskAmount": 44.41,
   "plannedRiskAmount": 49.97,
   "riskPct": 0.5,
   "rr": 2.49,
   "plannedRr": 2.11,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 63.0. SL 1.5×ATR, TP1 3.7×ATR — bội số này suy từ ATR/giá hiện tại (0.800%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5377556,
   "ocoOrderListId": 167216,
   "ocoError": null,
   "closedAt": "2026-08-21T04:53:29+00:00",
   "exit": 75689.64,
   "exitReason": "TAKE_PROFIT",
   "grossPnl": 110.75,
   "pnl": 110.75,
   "rMultiple": 2.49
  },
  {
   "id": "t_a866268ccc",
   "openedAt": "2026-08-20T17:10:04+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.04568,
   "entry": 72640.0,
   "requestedEntry": 72676.0,
   "stopLoss": 71685.4,
   "targets": [
    75099.66
   ],
   "riskAmount": 43.61,
   "plannedRiskAmount": 50.23,
   "riskPct": 0.5,
   "rr": 2.58,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 64.9. SL 1.5×ATR, TP1 3.7×ATR — bội số này suy từ ATR/giá hiện tại (0.909%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 5257569,
   "ocoOrderListId": 163291,
   "ocoError": null,
   "closedAt": "2026-08-21T00:10:41+00:00",
   "exit": 71470.34,
   "exitReason": "STOP_LOSS",
   "grossPnl": -53.43,
   "pnl": -53.43,
   "rMultiple": -1.23
  }
 ],
 "baiHoc": [
  {
   "soatLai": null,
   "at": "2026-08-21T22:48:49+00:00",
   "tradeId": "t_26bec9c59e",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": 105.85,
   "rMultiple": 2.5,
   "exitReason": "TAKE_PROFIT",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": true,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": false,
   "classification": "GOOD_TRADE_GOOD_OUTCOME",
   "lesson": "[luật] Chạy tới mục tiêu, setup và cách thoát giữ nguyên.",
   "change_strategy": false,
   "confidence_in_lesson": 0.3
  },
  {
   "soatLai": null,
   "at": "2026-08-21T21:28:50+00:00",
   "tradeId": "t_392a855d4e",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -51.69,
   "rMultiple": -1.17,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -645 qua 31 lệnh (25 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T20:03:43+00:00",
   "tradeId": "t_8413f9bc3a",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -47.52,
   "rMultiple": -1.06,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -593 qua 30 lệnh (24 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T19:54:37+00:00",
   "tradeId": "t_8141408e9b",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -52.75,
   "rMultiple": -1.17,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -545 qua 29 lệnh (23 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T18:03:33+00:00",
   "tradeId": "t_9244d92a68",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -52.49,
   "rMultiple": -1.17,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -493 qua 28 lệnh (22 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T17:10:44+00:00",
   "tradeId": "t_8c0f417944",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -52.02,
   "rMultiple": -1.17,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -440 qua 27 lệnh (21 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T15:58:09+00:00",
   "tradeId": "t_ed56df2bc7",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -52.23,
   "rMultiple": -1.16,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -388 qua 26 lệnh (20 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T15:00:34+00:00",
   "tradeId": "t_1cfa383fd2",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -53.44,
   "rMultiple": -1.16,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -336 qua 25 lệnh (19 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T13:55:19+00:00",
   "tradeId": "t_6633640f2f",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -53.74,
   "rMultiple": -1.16,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -282 qua 24 lệnh (18 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": null,
   "at": "2026-08-21T13:24:37+00:00",
   "tradeId": "t_1a36618aa0",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|HIGH_VOLATILITY",
   "side": "LONG",
   "pnl": -54.77,
   "rMultiple": -1.16,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -229 qua 23 lệnh (17 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  }
 ],
 "theGioi": {
  "luc": 1787930781.9760988,
  "phaiSinh": {
   "fundingNamHoa": 5.67,
   "openInterestUsd": 8404228204.22043,
   "oiDoi24hPct": -3.0,
   "topTrader": {
    "tyLe": 2.0516,
    "long": 0.6723,
    "short": 0.3277,
    "doi12h": -0.045
   },
   "toanSan": {
    "tyLe": 1.0404,
    "long": 0.5099,
    "short": 0.4901,
    "doi12h": 0.115
   },
   "nguon": "Binance Futures"
  },
  "viMo": {
   "muc": {
    "DXY": {
     "ten": "chỉ số đô la",
     "gia": 99.496,
     "doiPct": 0.34
    },
    "US10Y": {
     "ten": "lợi suất trái phiếu 10 năm",
     "gia": 4.694,
     "doiPct": 0.47
    },
    "DAU": {
     "ten": "dầu WTI",
     "gia": 83.18,
     "doiPct": -0.42
    },
    "SP500": {
     "ten": "S&P 500",
     "gia": 7769.6,
     "doiPct": 0.5
    },
    "VANG": {
     "ten": "vàng",
     "gia": 4615.3,
     "doiPct": 0.12
    }
   },
   "khauVi": {
    "diem": 0.18,
    "soChiSo": 3,
    "nhan": "TRUNG_TINH",
    "ghiChu": "suy ra từ chiều đổi của DXY, lợi suất và S&P — không phải một chỉ số có sẵn"
   },
   "nguon": "Yahoo Finance"
  },
  "tamLy": {
   "gt": 73,
   "nhan": "Greed",
   "chuoi": [
    72,
    71,
    66,
    73,
    74,
    65,
    71,
    73
   ]
  },
  "tin": [
   {
    "ma": "FED",
    "soBai": 6,
    "bai": [
     {
      "tieuDe": "Minutes of the Board's discount rate meetings on July 20 and July 29, 2026",
      "nguon": "Fed",
      "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260825a.htm"
     },
     {
      "tieuDe": "Minutes of the Federal Open Market Committee, July 28–29, 2026",
      "nguon": "Fed",
      "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260819a.htm"
     }
    ]
   },
   {
    "ma": "LAM_PHAT",
    "soBai": 4,
    "bai": [
     {
      "tieuDe": "Fed Chair Kevin Warsh at Jackson Hole: 'We have work to do' on inflation",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/markets/2026/08/28/warsh-at-jackson-hole-we-have-work-to-do-on-inflaiton"
     },
     {
      "tieuDe": "Morning Minute: Solana Jumps with Network Inflation Set to Drop",
      "nguon": "Decrypt",
      "url": "https://decrypt.co/376800/morning-minute-solana-jumps-with-network-inflation-set-to-drop"
     }
    ]
   },
   {
    "ma": "QUY_DINH",
    "soBai": 1,
    "bai": [
     {
      "tieuDe": "SEC Proposes New Regulation Crypto Assets",
      "nguon": "SEC",
      "url": "https://www.sec.gov/newsroom/press-releases/2026-76-sec-proposes-new-regulation-crypto-assets"
     }
    ]
   },
   {
    "ma": "ETF",
    "soBai": 3,
    "bai": [
     {
      "tieuDe": "Grayscale says Zcash can challenge Bitcoin’s network effects as privacy demand grows",
      "nguon": "Cointelegraph",
      "url": "https://cointelegraph.com/markets/zcash-bitcoin-network-effects-grayscale-privacy?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
     },
     {
      "tieuDe": "Ethereum ETFs Take $226M in a Day, Almost Matching Bitcoin's Haul",
      "nguon": "Decrypt",
      "url": "https://decrypt.co/376810/ethereum-etfs-take-226m-in-a-day-almost-matching-bitcoins-haul"
     }
    ]
   },
   {
    "ma": "VI_MO",
    "soBai": 5,
    "bai": [
     {
      "tieuDe": "Bitcoin is outperforming stocks and correlating with gold just when it matters most",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/daybook-us/2026/08/28/bitcoin-is-outperforming-stocks-and-correlating-with-gold-just-when-it-matters-most"
     },
     {
      "tieuDe": "Here’s why Warsh’s Jackson Hole speech is a major event for bitcoin and gold",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/markets/2026/08/28/here-s-why-warsh-s-jackson-hole-speech-is-a-major-event-for-bitcoin-and-gold"
     }
    ]
   }
  ],
  "soFeed": 9,
  "soBai": 186
 },
 "huanLuyen": null
};
