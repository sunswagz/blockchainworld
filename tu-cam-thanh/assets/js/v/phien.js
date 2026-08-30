/* SINH TỰ ĐỘNG bởi tu-cam-thanh-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái của runtime giao dịch, để trang tĩnh đọc được mà không
   cần server và không cần khoá API. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem README):
       python run.py            ghi mỗi vòng lặp
       python -m trader.snapshot   ghi một lần rồi thoát
*/
window.TU_CAM_THANH = {
 "generatedAt": "2026-08-30T00:02:03.585Z",
 "chayTu": "2026-08-29T21:12:23+00:00",
 "vong": 474,
 "tamDung": false,
 "san": "testnet",
 "cheDoSan": "testnet",
 "chiLong": true,
 "cap": "BTCUSDT",
 "khung": {
  "primary": "4h",
  "context": "1d"
 },
 "gia": 78212.29,
 "nguon": {
  "name": "data-api.binance.vision",
  "live": true,
  "lastOk": "07:02:02",
  "lastError": null
 },
 "cheDo": {
  "primary": "UNKNOWN",
  "flags": [],
  "quality": "LOW",
  "reasons": [
   "ADX 21.8 ở vùng lưng chừng, EMA BULLISH_ALIGNED"
  ],
  "contextTrend": "MIXED",
  "adx": 21.8,
  "volatility": "NORMAL",
  "key": "UNKNOWN|none"
 },
 "thiTruong": {
  "4h": {
   "price": 78212.29,
   "ema20": 78373.479,
   "ema50": 77064.187,
   "ema200": 70209.984,
   "emaStack": "BULLISH_ALIGNED",
   "rsi14": 49.3,
   "rsiSlope": 1.08,
   "macdHist": -170.7,
   "macdHistSlope": 52.867,
   "atr": 784.20637,
   "atrPct": 1.003,
   "atrRatioVsMedian": 0.74,
   "volatility": "NORMAL",
   "adx": 21.8,
   "plusDI": 23.0,
   "minusDI": 20.3,
   "bbWidthPct": 4.7651411,
   "bbPosition": 0.36,
   "volumeRatio": 0.0,
   "structure": "DOWNTREND",
   "swingHighs": [
    81272.62,
    79174.12,
    81478.87,
    78330.0
   ],
   "swingLows": [
    76670.01,
    77851.0,
    77632.58,
    76888.0
   ],
   "support": [
    {
     "price": 78052.85,
     "touches": 1
    },
    {
     "price": 77677.18,
     "touches": 3
    },
    {
     "price": 76888.0,
     "touches": 1
    }
   ],
   "resistance": [
    {
     "price": 78330.0,
     "touches": 1
    },
    {
     "price": 78828.15,
     "touches": 1
    },
    {
     "price": 79174.12,
     "touches": 1
    }
   ],
   "mauGia": {
    "co": false,
    "so": 0,
    "mau": [],
    "mauThuan": false
   },
   "range20High": 81478.87,
   "range20Low": 76888.0,
   "distToRange20HighPct": 4.18,
   "distToRange20LowPct": 1.69
  },
  "1d": {
   "price": 78212.29,
   "ema20": 73619.008,
   "ema50": 69367.287,
   "ema200": 73073.658,
   "emaStack": "MIXED",
   "rsi14": 71.4,
   "rsiSlope": -3.54,
   "macdHist": 509.79,
   "macdHistSlope": -265.567,
   "atr": 2174.5578,
   "atrPct": 2.78,
   "atrRatioVsMedian": 0.97,
   "volatility": "NORMAL",
   "adx": 42.8,
   "plusDI": 38.7,
   "minusDI": 11.8,
   "bbWidthPct": 39.275497,
   "bbPosition": 0.73,
   "volumeRatio": 0.0,
   "structure": "UPTREND",
   "swingHighs": [
    65474.46,
    79500.0,
    81272.62,
    81478.87
   ],
   "swingLows": [
    62742.47,
    62275.0,
    62535.24,
    76888.0
   ],
   "support": [
    {
     "price": 76888.0,
     "touches": 1
    },
    {
     "price": 67292.15,
     "touches": 1
    },
    {
     "price": 66956.15,
     "touches": 1
    }
   ],
   "resistance": [
    {
     "price": 79500.0,
     "touches": 1
    },
    {
     "price": 81375.745,
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
   "range20Low": 62535.24,
   "distToRange20HighPct": 4.18,
   "distToRange20LowPct": 20.04
  }
 },
 "luanDiem": null,
 "phanQuyet": null,
 "taiKhoan": {
  "vonBanDau": 10000,
  "von": 9719.05,
  "vonThucHien": 9719.05,
  "dinhVon": 9724.67,
  "laiLoMo": 8.82,
  "laiLoHomNay": 0.0,
  "drawdownPct": 0.06,
  "soLenhDaDong": 46,
  "viThe": [
   {
    "id": "t_d3d64675eb",
    "openedAt": "2026-08-29T16:49:59+00:00",
    "symbol": "SOLUSDT",
    "side": "LONG",
    "qty": 9.711,
    "entry": 105.04,
    "requestedEntry": 105.04,
    "stopLoss": 101.64,
    "targets": [
     112.67
    ],
    "riskAmount": 33.02,
    "plannedRiskAmount": 34.55,
    "riskPct": 0.5,
    "rr": 2.24,
    "plannedRr": 2.1,
    "stopAtrMultiple": 1.5,
    "feesPaid": 0,
    "regimeAtEntry": "TREND_UP",
    "regimeKey": "TREND_UP|none",
    "khung": "4h",
    "strategy": "MOCK_RULES_V1",
    "confidence": 0.6,
    "reasonCodes": [
     "MOCK_BRAIN",
     "TREND_ALIGNED",
     "ADX_CONFIRMS",
     "HET_TRAN_DUNG_LUAT_THUAN"
    ],
    "thesisSummary": "[mock] Thuận TREND_UP với ADX 36.2. SL 1.5×ATR, TP1 3.4×ATR — bội số này suy từ ATR/giá hiện tại (2.155%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
    "status": "OPEN",
    "venue": "binance-spot-testnet",
    "entryOrderId": 1382525,
    "ocoOrderListId": 303090,
    "ocoError": null,
    "unrealizedPnl": 4.37,
    "unrealizedR": 0.13
   },
   {
    "id": "t_9fa9a550c3",
    "openedAt": "2026-08-29T17:28:39+00:00",
    "symbol": "BNBUSDT",
    "side": "LONG",
    "qty": 2.349,
    "entry": 691.37,
    "requestedEntry": 691.23,
    "stopLoss": 679.73,
    "targets": [
     718.65
    ],
    "riskAmount": 27.34,
    "plannedRiskAmount": 29.45,
    "riskPct": 0.5,
    "rr": 2.34,
    "plannedRr": 2.1,
    "stopAtrMultiple": 1.5,
    "feesPaid": 0,
    "regimeAtEntry": "TREND_UP",
    "regimeKey": "TREND_UP|none",
    "khung": "4h",
    "strategy": "MOCK_RULES_V1",
    "confidence": 0.6,
    "reasonCodes": [
     "MOCK_BRAIN",
     "TREND_ALIGNED",
     "ADX_CONFIRMS",
     "HET_TRAN_DUNG_LUAT_THUAN"
    ],
    "thesisSummary": "[mock] Thuận TREND_UP với ADX 27.3. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.109%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
    "status": "OPEN",
    "venue": "binance-spot-testnet",
    "entryOrderId": 3024893,
    "ocoOrderListId": 304336,
    "ocoError": null,
    "unrealizedPnl": 2.35,
    "unrealizedR": 0.09
   },
   {
    "id": "t_ca4aa0c3d2",
    "openedAt": "2026-08-29T21:10:55+00:00",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "qty": 0.02556,
    "entry": 78130.0,
    "requestedEntry": 78129.99,
    "stopLoss": 76865.24,
    "targets": [
     81155.13
    ],
    "riskAmount": 32.33,
    "plannedRiskAmount": 35.33,
    "riskPct": 0.5,
    "rr": 2.39,
    "plannedRr": 2.1,
    "stopAtrMultiple": 1.5,
    "feesPaid": 0,
    "regimeAtEntry": "TREND_UP",
    "regimeKey": "TREND_UP|none",
    "khung": "4h",
    "strategy": "MOCK_RULES_V1",
    "confidence": 0.6,
    "reasonCodes": [
     "MOCK_BRAIN",
     "TREND_ALIGNED",
     "ADX_CONFIRMS",
     "HET_TRAN_DUNG_LUAT_THUAN"
    ],
    "thesisSummary": "[mock] Thuận TREND_UP với ADX 23.0. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.079%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
    "status": "OPEN",
    "venue": "binance-spot-testnet",
    "entryOrderId": 9772656,
    "ocoOrderListId": 309125,
    "ocoError": null,
    "unrealizedPnl": 2.1,
    "unrealizedR": 0.06
   }
  ]
 },
 "rui_ro": {
  "dungHan": null,
  "ngatMach": [],
  "gioiHan": {
   "startingEquity": 10000,
   "maxRiskPerTradePct": 0.5,
   "_maxOpenPositions": "4 = trần tổng rủi ro 2,0% chia cho 0,5% mỗi lệnh. Hai con số này phải đi cùng nhau: để 1 thì quét nhiều chợ vô nghĩa, để 10 thì trần tổng chặn ở lệnh thứ 5 và bốn lệnh sau chỉ tốn công quét.",
   "maxOpenPositions": 4,
   "_maxTongRuiRoPct": "TỔNG rủi ro đang mở, tính bằng % vốn. Khác maxRiskPerTradePct: cái đó canh MỘT lệnh. Khi maxOpenPositions=1 thì hai con số là một; mở nhiều coin thì chúng tách hẳn, và 15 lệnh crypto không phải 15 cược độc lập — chúng thua cùng nhau.",
   "maxTongRuiRoPct": 2.0,
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
  "cheDo": "cli",
  "model": "claude-sonnet-4-6",
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
   "count": 43,
   "wins": 10,
   "winRate": 23.3,
   "expectancyR": -0.313,
   "totalPnl": -584.9,
   "expectancyUsd": -13.6,
   "riskCv": 0.365,
   "riskDeu": false,
   "canhBao": null,
   "avgWinR": 2.61,
   "avgLossR": -1.2,
   "maxLossR": -1.56
  },
  "byRegime": {
   "TREND_UP": {
    "count": 43,
    "wins": 10,
    "winRate": 23.3,
    "expectancyR": -0.313,
    "totalPnl": -584.9,
    "expectancyUsd": -13.6,
    "riskCv": 0.365,
    "riskDeu": false,
    "canhBao": null,
    "avgWinR": 2.61,
    "avgLossR": -1.2,
    "maxLossR": -1.56
   }
  },
  "byStrategy": {
   "MOCK_RULES_V1": {
    "count": 43,
    "wins": 10,
    "winRate": 23.3,
    "expectancyR": -0.313,
    "totalPnl": -584.9,
    "expectancyUsd": -13.6,
    "riskCv": 0.365,
    "riskDeu": false,
    "canhBao": null,
    "avgWinR": 2.61,
    "avgLossR": -1.2,
    "maxLossR": -1.56
   }
  },
  "kyThuat": {
   "so": 1,
   "tien": 284.32,
   "lyDo": [
    "DONG_TAY_VI_KHONG_CO_STOP"
   ],
   "ghiChu": "Lệnh đóng KỸ THUẬT (an toàn / can thiệp tay), KHÔNG tính vào kỳ vọng chiến lược. Tiền vẫn vào tài khoản thật."
  }
 },
 "giaoDich": [
  {
   "id": "t_7e94f98d08",
   "openedAt": "2026-08-29T20:10:19+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.02474,
   "entry": 66574.58,
   "requestedEntry": 78241.03,
   "stopLoss": 76987.93,
   "targets": [
    81242.23
   ],
   "riskAmount": 257.63,
   "plannedRiskAmount": 33.91,
   "riskPct": 0.5,
   "rr": 1.41,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "khung": "4h",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS",
    "HET_TRAN_DUNG_LUAT_THUAN"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 23.0. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.068%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 9758120,
   "ocoOrderListId": null,
   "ocoError": "Binance -2010: The relationship of the prices for the orders is not correct.",
   "closedAt": "2026-08-29T21:06:01+00:00",
   "exit": 78066.94,
   "exitReason": "DONG_TAY_VI_KHONG_CO_STOP",
   "grossPnl": 284.32,
   "pnl": 284.32,
   "rMultiple": 1.1
  },
  {
   "id": "t_f41ef0b355",
   "openedAt": "2026-08-29T17:31:27+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.01491,
   "entry": 78009.63,
   "requestedEntry": 78009.63,
   "stopLoss": 76696.2,
   "targets": [
    81136.42
   ],
   "riskAmount": 19.58,
   "plannedRiskAmount": 21.33,
   "riskPct": 0.5,
   "rr": 2.38,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "khung": "4h",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS",
    "HET_TRAN_DUNG_LUAT_THUAN"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 24.0. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.122%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 9726581,
   "ocoOrderListId": 304408,
   "ocoError": null,
   "closedAt": "2026-08-29T20:10:15+00:00",
   "exit": 76477.51,
   "exitReason": "STOP_LOSS",
   "grossPnl": -22.84,
   "pnl": -22.84,
   "rMultiple": -1.17
  },
  {
   "id": "t_f2c3d12fc2",
   "openedAt": "2026-08-29T16:49:34+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.0332,
   "entry": 78021.07,
   "requestedEntry": 78021.07,
   "stopLoss": 76707.64,
   "targets": [
    81147.91
   ],
   "riskAmount": 43.61,
   "plannedRiskAmount": 47.5,
   "riskPct": 0.5,
   "rr": 2.38,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "khung": "4h",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS",
    "HET_TRAN_DUNG_LUAT_THUAN"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 24.0. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.122%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 9718582,
   "ocoOrderListId": 303067,
   "ocoError": null,
   "closedAt": "2026-08-29T20:10:15+00:00",
   "exit": 76477.51,
   "exitReason": "STOP_LOSS",
   "grossPnl": -51.25,
   "pnl": -51.25,
   "rMultiple": -1.18
  },
  {
   "id": "t_8aabdf10e5",
   "openedAt": "2026-08-29T12:00:15+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.03338,
   "entry": 77584.67,
   "requestedEntry": 77584.67,
   "stopLoss": 76270.54,
   "targets": [
    80710.92
   ],
   "riskAmount": 43.87,
   "plannedRiskAmount": 47.76,
   "riskPct": 0.5,
   "rr": 2.38,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "khung": "4h",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS",
    "FALLBACK_SAU_LOI_BRAIN"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 25.7. SL 1.5×ATR, TP1 3.6×ATR — bội số này suy từ ATR/giá hiện tại (1.129%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 9661161,
   "ocoOrderListId": 298091,
   "ocoError": null,
   "closedAt": "2026-08-29T15:01:51+00:00",
   "exit": 76041.72,
   "exitReason": "STOP_LOSS",
   "grossPnl": -51.5,
   "pnl": -51.5,
   "rMultiple": -1.17
  },
  {
   "id": "t_9f59e306e6",
   "openedAt": "2026-08-28T16:08:40+00:00",
   "symbol": "BTCUSDT",
   "side": "LONG",
   "qty": 0.02824,
   "entry": 78122.03,
   "requestedEntry": 78174.7,
   "stopLoss": 76592.38,
   "targets": [
    81866.95
   ],
   "riskAmount": 43.2,
   "plannedRiskAmount": 48.01,
   "riskPct": 0.5,
   "rr": 2.45,
   "plannedRr": 2.1,
   "stopAtrMultiple": 1.5,
   "feesPaid": 0.0,
   "regimeAtEntry": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "strategy": "MOCK_RULES_V1",
   "confidence": 0.6,
   "reasonCodes": [
    "MOCK_BRAIN",
    "TREND_ALIGNED",
    "ADX_CONFIRMS",
    "FALLBACK_SAU_LOI_BRAIN"
   ],
   "thesisSummary": "[mock] Thuận TREND_UP với ADX 35.8. SL 1.5×ATR, TP1 3.5×ATR — bội số này suy từ ATR/giá hiện tại (1.349%) để RR còn ≥2.0 sau khi trừ phí và trượt giá, không phải con số ghi cứng.",
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 9411849,
   "ocoOrderListId": 285460,
   "ocoError": null,
   "closedAt": "2026-08-28T16:21:52+00:00",
   "exit": 76362.6,
   "exitReason": "STOP_LOSS",
   "grossPnl": -49.69,
   "pnl": -49.69,
   "rMultiple": -1.15
  },
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
   "feesPaid": 0.0,
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
   "status": "CLOSED",
   "venue": "binance-spot-testnet",
   "entryOrderId": 9393304,
   "ocoOrderListId": 284358,
   "ocoError": null,
   "closedAt": "2026-08-28T16:08:40+00:00",
   "exit": 77509.58,
   "exitReason": "STOP_LOSS",
   "grossPnl": -51.43,
   "pnl": -51.43,
   "rMultiple": -1.14
  },
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
  }
 ],
 "baiHoc": [
  {
   "soatLai": null,
   "at": "2026-08-29T20:10:15+00:00",
   "tradeId": "t_f41ef0b355",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "side": "LONG",
   "pnl": -22.84,
   "rMultiple": -1.17,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": false,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "BAD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] Rủi ro 20 lệch 0.4× so với trung bình sổ (51) — R của lệnh này không so được với các lệnh khác. KHÔNG PHẢI LỆNH NÀY XUI: 4/43 lệnh trong sổ cược lệch quá 1,6× so với mức thường. Rủi ro đang bị quyết định bởi khoảng cách stop và trần tiền mua được, không bởi mức rủi ro đã chọn — đó là tật của cách tính kích thước, sửa ở đó chứ không sửa ở tín hiệu vào lệnh. KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|none đã lỗ -46 qua 11 lệnh (8 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.7
  },
  {
   "soatLai": null,
   "at": "2026-08-29T20:10:15+00:00",
   "tradeId": "t_f2c3d12fc2",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "side": "LONG",
   "pnl": -51.25,
   "rMultiple": -1.18,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": false,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|none đã lỗ -46 qua 11 lệnh (8 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6
  },
  {
   "soatLai": true,
   "at": "2026-08-29T15:01:51+00:00",
   "tradeId": "t_8aabdf10e5",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "side": "LONG",
   "pnl": -51.5,
   "rMultiple": -1.17,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": true,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] Dính stop trong biên độ bình thường — một lệnh thua không đồng nghĩa một quyết định sai.",
   "change_strategy": false,
   "confidence_in_lesson": 0.3,
   "soatLaiLuc": null
  },
  {
   "soatLai": true,
   "at": "2026-08-28T16:21:52+00:00",
   "tradeId": "t_9f59e306e6",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "side": "LONG",
   "pnl": -49.69,
   "rMultiple": -1.15,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": true,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] Dính stop trong biên độ bình thường — một lệnh thua không đồng nghĩa một quyết định sai.",
   "change_strategy": false,
   "confidence_in_lesson": 0.3,
   "soatLaiLuc": null
  },
  {
   "soatLai": true,
   "at": "2026-08-28T16:08:40+00:00",
   "tradeId": "t_922b195af0",
   "symbol": "BTCUSDT",
   "regime": "TREND_UP",
   "regimeKey": "TREND_UP|none",
   "side": "LONG",
   "pnl": -51.43,
   "rMultiple": -1.14,
   "exitReason": "STOP_LOSS",
   "strategy": "MOCK_RULES_V1",
   "regime_appropriate": true,
   "entry_valid": true,
   "size_valid": true,
   "stop_placement_valid": true,
   "thesis_was_wrong": true,
   "classification": "GOOD_TRADE_BAD_OUTCOME",
   "lesson": "[luật] Dính stop trong biên độ bình thường — một lệnh thua không đồng nghĩa một quyết định sai.",
   "change_strategy": false,
   "confidence_in_lesson": 0.3,
   "soatLaiLuc": null
  },
  {
   "soatLai": true,
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
   "confidence_in_lesson": 0.3,
   "soatLaiLuc": null
  },
  {
   "soatLai": true,
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
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -539 qua 32 lệnh (25 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6,
   "soatLaiLuc": null
  },
  {
   "soatLai": true,
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
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -539 qua 32 lệnh (25 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6,
   "soatLaiLuc": null
  },
  {
   "soatLai": true,
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
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -539 qua 32 lệnh (25 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6,
   "soatLaiLuc": null
  },
  {
   "soatLai": true,
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
   "lesson": "[luật] KHÔNG PHẢI LỆNH NÀY XUI: chế độ TREND_UP|HIGH_VOLATILITY đã lỗ -539 qua 32 lệnh (25 thua) — chiến lược này không ăn được trong chế độ đó, hãy ngừng vào lệnh ở đây thay vì chỉnh tham số.",
   "change_strategy": true,
   "confidence_in_lesson": 0.6,
   "soatLaiLuc": null
  }
 ],
 "theGioi": {
  "luc": 1788047895.9153678,
  "phaiSinh": {
   "fundingNamHoa": 9.1,
   "openInterestUsd": 8424053324.202,
   "oiDoi24hPct": 2.52,
   "topTrader": {
    "tyLe": 2.0855,
    "long": 0.6759,
    "short": 0.3241,
    "doi12h": 0.028
   },
   "toanSan": {
    "tyLe": 1.1906,
    "long": 0.5435,
    "short": 0.4565,
    "doi12h": 0.02
   },
   "nguon": "Binance Futures"
  },
  "viMo": {
   "muc": {
    "DXY": {
     "ten": "chỉ số đô la",
     "gia": 99.16,
     "doiPct": -0.01
    },
    "US10Y": {
     "ten": "lợi suất trái phiếu 10 năm",
     "gia": 4.672,
     "doiPct": 0.17
    },
    "DAU": {
     "ten": "dầu WTI",
     "gia": 83.4,
     "doiPct": -0.16
    },
    "SP500": {
     "ten": "S&P 500",
     "gia": 7730.99,
     "doiPct": 0.72
    },
    "VANG": {
     "ten": "vàng",
     "gia": 4478.1,
     "doiPct": -2.85
    }
   },
   "khauVi": {
    "diem": 1.01,
    "soChiSo": 3,
    "nhan": "RISK_ON",
    "ghiChu": "suy ra từ chiều đổi của DXY, lợi suất và S&P — không phải một chỉ số có sẵn"
   },
   "nguon": "Yahoo Finance"
  },
  "tamLy": {
   "gt": 68,
   "nhan": "Greed",
   "chuoi": [
    71,
    66,
    73,
    74,
    65,
    71,
    73,
    68
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
    "soBai": 5,
    "bai": [
     {
      "tieuDe": "Fed Chair Kevin Warsh at Jackson Hole: 'We have work to do' on inflation",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/markets/2026/08/28/warsh-at-jackson-hole-we-have-work-to-do-on-inflaiton"
     },
     {
      "tieuDe": "Bitcoin dips to $78.4K as Fed’s Warsh downplays softer inflation prints",
      "nguon": "Cointelegraph",
      "url": "https://cointelegraph.com/markets/bitcoin-dips-fed-warsh-dismisses-recent-low-inflation-prints?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
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
    "soBai": 2,
    "bai": [
     {
      "tieuDe": "Bitcoin ETFs end 9-day inflow streak as BTC dips below $78K",
      "nguon": "Cointelegraph",
      "url": "https://cointelegraph.com/markets/bitcoin-etf-end-9-day-inflow-streak-btc-below-78k?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
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
    "soBai": 6,
    "bai": [
     {
      "tieuDe": "Ditching 'digital gold': BPI study suggests everyday Americans prefer control and micro-investing",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/business/2026/08/28/ditch-digital-gold-bpi-study-suggests-everyday-americans-prefer-control-and-micro-investing"
     },
     {
      "tieuDe": "Bitcoin is outperforming stocks and correlating with gold just when it matters most",
      "nguon": "CoinDesk",
      "url": "https://www.coindesk.com/daybook-us/2026/08/28/bitcoin-is-outperforming-stocks-and-correlating-with-gold-just-when-it-matters-most"
     }
    ]
   }
  ],
  "soFeed": 9,
  "soBai": 186
 },
 "huanLuyen": null,
 "phatHien": [
  {
   "ma": "khung-nao-do-noi",
   "nguon": "do-khung",
   "mau": 40953,
   "doTin": "CAO",
   "khung": null,
   "cheDo": null,
   "so": {
    "theoKhung": {
     "5m": -21.6,
     "15m": -12.5,
     "30m": -10.1,
     "1h": -6.3,
     "4h": -3.4,
     "1d": -1.7
    },
    "totNhat": "1d",
    "teNhat": "5m"
   },
   "cau": "Khoảng cách tới hoà vốn ở mục tiêu 2R, đo bằng CÁCH VÀO NGẪU NHIÊN trên 3 coin (40,953 điểm vào): 1d -1.7đ · 4h -3.4đ · 1h -6.3đ · 30m -10.1đ · 15m -12.5đ · 5m -21.6đ. Khung càng dài càng gần hoà vốn. Ở 1d chỉ cần bộ chọn điểm vào thêm 1.7 điểm phần trăm là dương; ở 5m cần thêm 21.6 điểm — khoảng cách đó không điểm vào nào lấp nổi. Đây là TRẦN TRÊN lạc quan (khi mục tiêu và stop cùng nằm trong một nến, phần thắng tính cho mục tiêu), nên thực tế còn thấp hơn. CÁC KHUNG KHÔNG PHỦ CÙNG QUÃNG (5m 42ng · 15m 83ng · 30m 125ng · 1h 250ng · 1d 1499ng · 4h 1500ng), nên bảng này so BỐN NĂM với BỐN MƯƠI "
  },
  {
   "ma": "khung-ngan-chet-vi-phi",
   "nguon": "do-khung",
   "mau": 40953,
   "doTin": "CAO",
   "khung": null,
   "cheDo": null,
   "so": {
    "khung": [
     "5m"
    ]
   },
   "cau": "Khung 5m kém hoà vốn tới -22 điểm phần trăm ở 2R. Nguyên nhân là chi phí: phí và trượt giá tính theo % GIÁ nên không đổi, còn biên độ mỗi nến thì nhỏ dần theo khung — cùng một khoản phí ăn phần R ngày càng lớn. Không chiến lược nào bù được chỗ đó."
  },
  {
   "ma": "mau-gia-tong",
   "nguon": "mau-gia",
   "mau": 22997,
   "doTin": "CAO",
   "khung": "4h",
   "cheDo": null,
   "so": {
    "soMau": 14,
    "soAm": 13,
    "soCho": 15
   },
   "cau": "14 mẫu giá kinh điển đã đem đo trên 135000 nến khung 4h trên 15 chợ độc lập (22997 lần xuất hiện, đã gộp trùng): 13/14 có kỳ vọng ÂM sau phí, dùng đúng điểm vào/stop/mục tiêu mà chính mẫu khai. Mẫu giá ở đây là BỐI CẢNH để đọc, không phải tín hiệu để bấm."
  },
  {
   "ma": "mau-gia-xau",
   "nguon": "mau-gia",
   "mau": 5126,
   "doTin": "CAO",
   "khung": "4h",
   "cheDo": null,
   "so": {
    "ten": "NẾN_TRONG_TĂNG",
    "kyVongR": -0.184
   },
   "cau": "NẾN_TRONG_TĂNG (đo trên 135000 nến khung 4h trên 15 chợ độc lập): kỳ vọng -0.184R qua 5126 lần, thắng 32.4%, MFE trung vị chỉ 0.79R — một nửa số lần nó còn không đi nổi 0.79R về phía mình trước khi kết thúc. Thấy mẫu này thì đừng coi là lý do vào lệnh."
  },
  {
   "ma": "huong",
   "nguon": "do-huong",
   "mau": 2069,
   "doTin": "CAO",
   "khung": null,
   "cheDo": null,
   "so": {
    "kyVongR": -0.1459250535331906,
    "caHaiR": -0.01672885451909135,
    "chenhDoShort": 0.12919619901409926,
    "soCho": 48
   },
   "cau": "Chiến lược có HAI NỬA và bot chạy thật chỉ chạy được một. Trên 48 chợ, dữ liệu 2022-07-13 → 2026-08-29: cả hai chiều -0.0167R qua 2069 lệnh · CHỈ LONG -0.1459R qua 934 lệnh · riêng LONG -0.1474R/935 · riêng SHORT +0.0911R/1134. Nửa SHORT đóng góp +0.1292R mỗi lệnh, và sàn SPOT không đánh được nửa đó — nên mọi con số «cả hai chiều» ở các phát hiện khác nói về một chiến lược bot không chạy nổi. Đọc chúng bằng cột CHỈ LONG. Con số short đến từ CHẠY LẠI: khớp đúng giá đặt, không phí vay, không rủi ro bị ép đóng — thực tế sẽ xấu hơn."
  },
  {
   "ma": "mau-gia-rr-thap",
   "nguon": "mau-gia",
   "mau": 2029,
   "doTin": "CAO",
   "khung": "4h",
   "cheDo": null,
   "so": {
    "ten": "HAI_ĐỈNH",
    "rr": 0.53,
    "tyLeThang": 55.9
   },
   "cau": "HAI_ĐỈNH (đo trên 135000 nến khung 4h trên 15 chợ độc lập): thắng 55.9% và chạm đích 71.8% — nghe rất tốt — nhưng kỳ vọng vẫn -0.040R qua 2029 lần, vì luật đặt mục tiêu kinh điển của nó cho RR chỉ 0.53. Đích gần hơn cả stop thì thắng bao nhiêu cũng không đủ."
  },
  {
   "ma": "lo-luyen-champion",
   "nguon": "lo-luyen",
   "mau": 946,
   "doTin": "CAO",
   "khung": null,
   "cheDo": null,
   "so": {
    "kyVongR": -0.1517,
    "soLatDuong": 0,
    "soLat": 4
   },
   "cau": "Champion đo trên 48 chợ × 4 lát thời gian (CHỈ LONG — đúng không gian sàn spot cho phép): dương 0/4 lát, gộp -0.1517R qua 946 lệnh. Từng lát: -0.49 -0.06 -0.10 -0.42. Lát là quãng thời gian LIÊN TIẾP — dương ở một lát và âm ở lát khác nghĩa là kết quả phụ thuộc chế độ thị trường, không phải lợi thế."
  },
  {
   "ma": "bo-pha",
   "nguon": "bo-pha",
   "mau": 256,
   "doTin": "CAO",
   "khung": null,
   "cheDo": null,
   "so": {
    "tat": [
     "phi-x2",
     "phi-x3",
     "lo",
     "bien"
    ],
    "thua": []
   },
   "cau": "MOCK_RULES_V1 trên BTCUSDT:4h: gốc -0.070R qua 256 lệnh. TẮT TIẾNG khi phi-x2, phi-x3, lo, bien — không phải thua, mà là không còn lệnh nào qua nổi cửa RR khi chi phí đội lên. Lợi thế (nếu có) nằm GỌN trong giả định chi phí, nên mọi con số dương chỉ đúng chừng nào phí đúng bằng mức đã giả định. "
  },
  {
   "ma": "bac-bo:1d-song-o-cua-so-khac",
   "nguon": "gia-thuyet",
   "mau": 166,
   "doTin": "CAO",
   "khung": null,
   "cheDo": null,
   "so": {
    "phanQuyet": "BÁC_BỎ"
   },
   "cau": "BÁC BỎ — Champion trên 1d được +0,117R gộp qua 230 lệnh, dương 11/15 chợ. Nhưng 15 chợ ấy dùng CHUNG một cửa sổ ngoài mẫu (khoảng 06/2025–08/2026), mà crypto tương quan cao — nên con số đó có thể chỉ là «450 ngày vừa rồi thuận» nói mười lăm lần. Nó có sống ở một cửa sổ thời gian KHÁC không? Dự đoán lúc chưa biết: CÓ, sẽ sống. Lần trước tôi đoán sai theo hướng bi quan nên lần này phải nói rõ vì sao đổi ý: đã có sẵn một phép ĐỐI CHỨNG mạnh. Cùng 15 chợ, cùng đúng khoảng thời gian đó, khung 4h cho −0,047R còn 1d cho +0,117R. Nếu nguyên nhân là cửa sổ thuận thì 4h cũng phải đẹp lên — nó không. Vậy"
  },
  {
   "ma": "dong-thuan-lech",
   "nguon": "dai-quan-sat",
   "mau": 122,
   "doTin": "CAO",
   "khung": null,
   "cheDo": null,
   "so": {
    "phanTramLongDauNguoi": 90.2,
    "phanTramLongVon": 17.5
   },
   "cau": "BTC: 90.2% số ĐẦU NGƯỜI đang LONG nhưng chỉ 17.5% số VỐN đang LONG, trên 122 vị thế. Đám đông và tiền lớn đang đứng hai phía. Đây là BỐI CẢNH, không phải lệnh: nó nói chỗ đông người ở đâu, không nói ai đúng."
  },
  {
   "ma": "champion",
   "nguon": "chien-luoc",
   "mau": 85,
   "doTin": "CAO",
   "khung": "4h",
   "cheDo": null,
   "so": {
    "kyVongR": -0.05,
    "tyLeThang": 34.1,
    "heSoLoiNhuan": 0.93,
    "cho": "BTCUSDT:4h",
    "sutGiamToiDaPct": 6.68,
    "tham": {}
   },
   "cau": "Chiến lược đang cầm quyền (MOCK_RULES_V1 · Thuận xu hướng): kỳ vọng -0.050R qua 85 lệnh chạy lại, thắng 34.1%, hệ số lợi nhuận 0.93, sụt giảm tối đa 6.68%. KỲ VỌNG ÂM: chính bản chiến lược đang chạy đã lỗ trên lịch sử. Mọi lệnh nó đề xuất đều xuất phát từ đây — kết quả tốt lẻ tẻ là phương sai, không phải bằng chứng ngược lại. (đo trên BTCUSDT:4h)"
  },
  {
   "ma": "chuoi-thua",
   "nguon": "chien-luoc",
   "mau": 85,
   "doTin": "CAO",
   "khung": "4h",
   "cheDo": null,
   "so": {
    "chuoiThuaDaiNhat": 8
   },
   "cau": "Chuỗi thua dài nhất đo được: 8 lệnh liên tiếp qua 85 lệnh chạy lại. Đây mới là con số quyết định mức rủi ro mỗi lệnh — không phải kỳ vọng. Sống sót qua chuỗi thua là điều kiện để kỳ vọng có cơ hội hiện ra."
  },
  {
   "ma": "khop-troi",
   "nguon": "chien-luoc",
   "mau": 85,
   "doTin": "CAO",
   "khung": "4h",
   "cheDo": null,
   "so": {
    "khopTroi": -0.029
   },
   "cau": "Khớp trội -0.029: chênh lệch giữa điểm TRONG mẫu và điểm NGOÀI mẫu của bộ tham số cầm quyền. Càng lớn thì nó càng học thuộc quá khứ thay vì học quy luật — và phần học thuộc sẽ không lặp lại."
  },
  {
   "ma": "cua-thoat",
   "nguon": "chien-luoc",
   "mau": 85,
   "doTin": "CAO",
   "khung": "4h",
   "cheDo": null,
   "so": {
    "theoLyDoThoat": {
     "TP": 26,
     "SL": 53,
     "HET_HAN": 6
    }
   },
   "cau": "53/85 lệnh chạy lại thoát bằng STOP LOSS (62%), chỉ 26 lệnh chạm mục tiêu. Tỉ lệ này nói vấn đề nằm ở điểm VÀO hoặc ở chỗ đặt stop, không nằm ở mục tiêu."
  }
 ]
};
