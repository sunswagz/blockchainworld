/* SINH TỰ ĐỘNG bởi tu-cam-thanh-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái của runtime giao dịch, để trang tĩnh đọc được mà không
   cần server và không cần khoá API. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem README):
       python run.py            ghi mỗi vòng lặp
       python -m trader.snapshot   ghi một lần rồi thoát
*/
window.TU_CAM_THANH = {
 "generatedAt": "2026-08-15T08:17:18.474Z",
 "chayTu": "2026-08-15T08:17:16+00:00",
 "vong": 1,
 "tamDung": false,
 "cap": "BTCUSDT",
 "khung": {
  "primary": "1h",
  "context": "4h"
 },
 "gia": 63059.84,
 "nguon": {
  "name": "data-api.binance.vision",
  "live": true,
  "lastOk": "15:17:18",
  "lastError": null
 },
 "cheDo": {
  "primary": "RANGE",
  "flags": [],
  "quality": "HIGH",
  "reasons": [
   "ADX 15.2 < 18 — không bên nào kiểm soát"
  ],
  "contextTrend": "BEARISH_ALIGNED",
  "adx": 15.2,
  "volatility": "NORMAL",
  "key": "RANGE|none"
 },
 "thiTruong": {
  "1h": {
   "price": 63059.84,
   "ema20": 63052.51,
   "ema50": 63201.05,
   "ema200": 63774.3,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 49.2,
   "rsiSlope": -0.51,
   "macdHist": 30.12,
   "macdHistSlope": -4.129,
   "atr": 150.43,
   "atrPct": 0.239,
   "atrRatioVsMedian": 0.69,
   "volatility": "NORMAL",
   "adx": 15.2,
   "plusDI": 17.1,
   "minusDI": 18.3,
   "bbWidthPct": 0.87,
   "bbPosition": 0.63,
   "volumeRatio": 0.19,
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
    63027.89
   ],
   "support": [
    {
     "price": 62733.5,
     "touches": 5
    }
   ],
   "resistance": [
    {
     "price": 63250.6,
     "touches": 9
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
   "range20Low": 62535.24,
   "distToRange20HighPct": 0.3,
   "distToRange20LowPct": 0.83
  },
  "4h": {
   "price": 63059.84,
   "ema20": 63346.52,
   "ema50": 63767.29,
   "ema200": 63932.79,
   "emaStack": "BEARISH_ALIGNED",
   "rsi14": 38.4,
   "rsiSlope": 0.2,
   "macdHist": 10.96,
   "macdHistSlope": 12.34,
   "atr": 375.62,
   "atrPct": 0.596,
   "atrRatioVsMedian": 0.74,
   "volatility": "NORMAL",
   "adx": 30.1,
   "plusDI": 14.2,
   "minusDI": 27.6,
   "bbWidthPct": 2.23,
   "bbPosition": 0.29,
   "volumeRatio": 0.04,
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
  "market_summary": "[mock] RANGE, ADX 15.2, RSI 49.2, EMA BEARISH_ALIGNED",
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
  "at": "2026-08-15T08:17:18+00:00"
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
   "count": 1,
   "wins": 1,
   "winRate": 100.0,
   "expectancyR": 1.5,
   "totalPnl": 75.11,
   "avgWinR": 1.5,
   "avgLossR": null,
   "maxLossR": 1.5
  },
  "byRegime": {
   "RANGE": {
    "count": 1,
    "wins": 1,
    "winRate": 100.0,
    "expectancyR": 1.5,
    "totalPnl": 75.11,
    "avgWinR": 1.5,
    "avgLossR": null,
    "maxLossR": 1.5
   }
  },
  "byStrategy": {
   "MOCK_RULES_V1": {
    "count": 1,
    "wins": 1,
    "winRate": 100.0,
    "expectancyR": 1.5,
    "totalPnl": 75.11,
    "avgWinR": 1.5,
    "avgLossR": null,
    "maxLossR": 1.5
   }
  }
 },
 "giaoDich": [
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
