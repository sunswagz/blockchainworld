/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime — ĐỪNG SỬA TAY.
   Lát cắt chênh lệch funding giữa các cảng, để trang tĩnh đọc được mà không
   cần server và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python run.py                 ghi mỗi vòng lặp
       python -m bac.snapshot        ghi một lần rồi thoát
*/
window.CANG_PHI = {
  "date": "25/08/2026",
  "tomTat": "30 cặp đã cân · KHÔNG cặp nào qua cửa rủi ro",
  "generatedAt": "2026-08-25T17:13:17.882Z",
  "maChienLuoc": "perp.funding_spread.v1",
  "che": "quan-sat",
  "cheKhai": "quan-sat",
  "vong": 1,
  "chayDuocGiay": 1.0332658290863037,
  "giuGio": 8.0,
  "ma": [
    "BTC",
    "ETH",
    "SOL",
    "XRP",
    "DOGE"
  ],
  "cang": [
    {
      "ten": "hyperliquid",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.159008056640625,
      "treTrungBinhMs": 294.43049999827053,
      "songSot": true
    },
    {
      "ten": "binance",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.2002392578125,
      "treTrungBinhMs": 252.25829999544658,
      "songSot": true
    },
    {
      "ten": "okx",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.2376533203125,
      "treTrungBinhMs": 214.116399998602,
      "songSot": true
    },
    {
      "ten": "bybit",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.02211181640625,
      "treTrungBinhMs": 429.63350000354694,
      "songSot": true
    }
  ],
  "dongHo": {
    "lechMs": 447279.95458984375,
    "lechGiay": 447.2799545898437,
    "daDo": true,
    "dangKeu": true,
    "nguongKeuMs": 5000.0,
    "theoSan": {
      "bybit": 447277.36376953125,
      "binance": 447279.95458984375,
      "okx": 447300.0224609375
    },
    "soMau": 3
  },
  "baoGia": [
    {
      "san": "hyperliquid",
      "ma": "BTC",
      "rate": 1.25e-05,
      "intervalGio": 1.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 78964.0,
      "mocKeMs": 1787680800000,
      "oiUsd": 2883706243.35504,
      "tuoiGiay": 0.1593798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "ETH",
      "rate": 9.8026e-06,
      "intervalGio": 1.0,
      "moiGio": 9.8026e-06,
      "moiNgayBps": 2.352624,
      "markPx": 2465.0,
      "mocKeMs": 1787680800000,
      "oiUsd": 1721843348.501,
      "tuoiGiay": 0.1593798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "SOL",
      "rate": 1.25e-05,
      "intervalGio": 1.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 97.926,
      "mocKeMs": 1787680800000,
      "oiUsd": 473635726.83480006,
      "tuoiGiay": 0.1593798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "DOGE",
      "rate": 1.25e-05,
      "intervalGio": 1.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.088721,
      "mocKeMs": 1787680800000,
      "oiUsd": 66167265.642349996,
      "tuoiGiay": 0.1593798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "XRP",
      "rate": 1.25e-05,
      "intervalGio": 1.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 1.4698,
      "mocKeMs": 1787680800000,
      "oiUsd": 247177524.1488,
      "tuoiGiay": 0.1593798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "binance",
      "ma": "BTC",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 78956.6,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.1493798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "ETH",
      "rate": 6.022e-05,
      "intervalGio": 8.0,
      "moiGio": 7.5275e-06,
      "moiNgayBps": 1.8066000000000002,
      "markPx": 2465.12699679,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.1493798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "SOL",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 97.94,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.1493798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "XRP",
      "rate": 3.572e-05,
      "intervalGio": 8.0,
      "moiGio": 4.465e-06,
      "moiNgayBps": 1.0715999999999999,
      "markPx": 1.46951367,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.1493798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "DOGE",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.08871332,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.1493798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "BTC",
      "rate": 4.25074158509e-05,
      "intervalGio": 8.0,
      "moiGio": 5.3134269813625e-06,
      "moiNgayBps": 1.2752224755269999,
      "markPx": 78950.3,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 18.8193798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "ETH",
      "rate": 6.9408910578e-05,
      "intervalGio": 8.0,
      "moiGio": 8.67611382225e-06,
      "moiNgayBps": 2.08226731734,
      "markPx": 2465.09,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 18.7603798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "SOL",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 97.92,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 17.4383798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "XRP",
      "rate": 4.32043226396e-05,
      "intervalGio": 8.0,
      "moiGio": 5.40054032995e-06,
      "moiNgayBps": 1.296129679188,
      "markPx": 1.4691,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 18.4843798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "DOGE",
      "rate": 2.10944372087e-05,
      "intervalGio": 8.0,
      "moiGio": 2.6368046510875e-06,
      "moiNgayBps": 0.632833116261,
      "markPx": 0.08868,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 17.9523798828125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "BTC",
      "rate": 8.31e-06,
      "intervalGio": 8.0,
      "moiGio": 1.03875e-06,
      "moiNgayBps": 0.2493,
      "markPx": 78944.7,
      "mocKeMs": 1787702400000,
      "oiUsd": 3809478551.06,
      "tuoiGiay": 0.0333798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "DOGE",
      "rate": 2.93e-05,
      "intervalGio": 8.0,
      "moiGio": 3.6625e-06,
      "moiNgayBps": 0.879,
      "markPx": 0.08869,
      "mocKeMs": 1787702400000,
      "oiUsd": 134501990.51,
      "tuoiGiay": 0.0333798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "ETH",
      "rate": -4.032e-05,
      "intervalGio": 8.0,
      "moiGio": -5.04e-06,
      "moiNgayBps": -1.2096,
      "markPx": 2464.97,
      "mocKeMs": 1787702400000,
      "oiUsd": 1919528512.86,
      "tuoiGiay": 0.0333798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "SOL",
      "rate": -3.825e-05,
      "intervalGio": 8.0,
      "moiGio": -4.78125e-06,
      "moiNgayBps": -1.1475,
      "markPx": 97.91,
      "mocKeMs": 1787702400000,
      "oiUsd": 655084694.2,
      "tuoiGiay": 0.0333798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "XRP",
      "rate": 2.73e-05,
      "intervalGio": 8.0,
      "moiGio": 3.4125e-06,
      "moiNgayBps": 0.819,
      "markPx": 1.4693,
      "mocKeMs": 1787702400000,
      "oiUsd": 343160787.0,
      "tuoiGiay": 0.0333798828125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    }
  ],
  "coHoi": [
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 2.10944372087e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.3671668837390003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.789055627913,
      "phiBps": 27.0,
      "netBps": -26.210944372087,
      "netAprPct": -287.0098408743526,
      "lechMarkBps": 4.622296379388997,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 17.933259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 2.37 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.21 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 3.572e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.9284000000000001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.6428,
      "phiBps": 27.0,
      "netBps": -26.3572,
      "netAprPct": -288.61134000000004,
      "lechMarkBps": 1.9482779461233979,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 1.93 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.36 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 4.25074158509e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.7247775244730004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.574925841491,
      "phiBps": 27.0,
      "netBps": -26.425074158509,
      "netAprPct": -289.35456203567355,
      "lechMarkBps": 1.735118352169131,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 18.800259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 1.72 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.43 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 4.32043226396e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.703870320812,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.567956773604,
      "phiBps": 27.0,
      "netBps": -26.432043226396,
      "netAprPct": -289.43087332903616,
      "lechMarkBps": 4.763687093810084,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 18.465259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 1.70 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.43 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -3.825e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 4.1475,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.3825,
      "phiBps": 28.0,
      "netBps": -26.6175,
      "netAprPct": -291.46162499999997,
      "lechMarkBps": 1.6340203027028066,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 0.140259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "NET sau phí -26.62 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -4.032e-05,
      "rateShort": 9.8026e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.5622239999999996,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.187408,
      "phiBps": 28.0,
      "netBps": -26.812592,
      "netAprPct": -293.5978824,
      "lechMarkBps": 0.12170459455209705,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 0.140259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "NET sau phí -26.81 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 6.022e-05,
      "rateShort": 9.8026e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.546024,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.18200799999999998,
      "phiBps": 27.0,
      "netBps": -26.817992,
      "netAprPct": -293.65701240000004,
      "lechMarkBps": 0.5151866882231682,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.55 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.82 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 6.9408910578e-05,
      "rateShort": 9.8026e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.2703566826599999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.09011889421999998,
      "phiBps": 27.0,
      "netBps": -26.90988110578,
      "netAprPct": -294.663198108291,
      "lechMarkBps": 0.3651048966657628,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 18.741259521484373,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.27 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.91 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "binance",
      "rateLong": 1.25e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.0,
      "phiBps": 27.0,
      "netBps": -27.0,
      "netAprPct": -295.65,
      "lechMarkBps": 0.9371798232775432,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.00 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.00 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "SOL",
      "sanLong": "hyperliquid",
      "sanShort": "binance",
      "rateLong": 1.25e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.0,
      "phiBps": 27.0,
      "netBps": -27.0,
      "netAprPct": -295.65,
      "lechMarkBps": 1.4295487731403913,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.00 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.00 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "SOL",
      "sanLong": "hyperliquid",
      "sanShort": "okx",
      "rateLong": 1.25e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.0,
      "phiBps": 27.0,
      "netBps": -27.0,
      "netAprPct": -295.65,
      "lechMarkBps": 0.6127263257866106,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 17.419259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.00 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.00 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "hyperliquid",
      "sanShort": "binance",
      "rateLong": 1.25e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.0,
      "phiBps": 27.0,
      "netBps": -27.0,
      "netAprPct": -295.65,
      "lechMarkBps": 0.8656724358620164,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.00 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.00 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 8.31e-06,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.7507,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.9169000000000002,
      "phiBps": 28.0,
      "netBps": -27.083099999999998,
      "netAprPct": -296.55994499999997,
      "lechMarkBps": 2.4444504957615267,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 0.140259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 2.75 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.08 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 2.10944372087e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.3671668837390003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.789055627913,
      "phiBps": 28.0,
      "netBps": -27.210944372087,
      "netAprPct": -297.95984087435266,
      "lechMarkBps": 3.756623981106318,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 17.933259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 2.37 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.21 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 2.73e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.181,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.7270000000000001,
      "phiBps": 28.0,
      "netBps": -27.273,
      "netAprPct": -298.63935,
      "lechMarkBps": 3.4024020958793164,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 0.140259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 2.18 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.27 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 2.93e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.1210000000000004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.7070000000000001,
      "phiBps": 28.0,
      "netBps": -27.293,
      "netAprPct": -298.85835,
      "lechMarkBps": 3.494710023616278,
      "choMocDauGiay": 2354.8697404785157,
      "tuoiXauNhatGiay": 0.140259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 2.12 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.29 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 4.25074158509e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.7247775244730004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.574925841491,
      "phiBps": 28.0,
      "netBps": -27.425074158509,
      "netAprPct": -300.3045620356735,
      "lechMarkBps": 0.7979385321354431,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 18.800259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 1.72 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.43 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -3.825e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 4.1475,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.3825,
      "phiBps": 29.0,
      "netBps": -27.6175,
      "netAprPct": -302.41162499999996,
      "lechMarkBps": 3.063569057952631,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "NET sau phí -27.62 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -3.825e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 4.1475,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.3825,
      "phiBps": 29.0,
      "netBps": -27.6175,
      "netAprPct": -302.41162499999996,
      "lechMarkBps": 1.0212939794725135,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 17.419259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "NET sau phí -27.62 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -4.032e-05,
      "rateShort": 6.9408910578e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.2918673173400004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.09728910578,
      "phiBps": 29.0,
      "netBps": -27.90271089422,
      "netAprPct": -305.534684291709,
      "lechMarkBps": 0.4868094911637814,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 18.741259521484373,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "NET sau phí -27.90 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 6.022e-05,
      "rateShort": 6.9408910578e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.27566731734,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.09188910578,
      "phiBps": 28.0,
      "netBps": -27.90811089422,
      "netAprPct": -305.593814291709,
      "lechMarkBps": 0.15008179162798027,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 18.741259521484373,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.28 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.91 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 3.572e-05,
      "rateShort": 4.32043226396e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.22452967918800015,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.07484322639600005,
      "phiBps": 28.0,
      "netBps": -27.925156773604,
      "netAprPct": -305.78046667096385,
      "lechMarkBps": 2.815409213011124,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 18.465259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.22 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.93 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -4.032e-05,
      "rateShort": 6.022e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.0162000000000004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.0054,
      "phiBps": 29.0,
      "netBps": -27.9946,
      "netAprPct": -306.5408699999999,
      "lechMarkBps": 0.6368912826754315,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "NET sau phí -27.99 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 0.0001,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.0,
      "phiBps": 28.0,
      "netBps": -28.0,
      "netAprPct": -306.59999999999997,
      "lechMarkBps": 2.042275094454817,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 17.419259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.00 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.00 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 8.31e-06,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.7507,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.9169000000000002,
      "phiBps": 29.0,
      "netBps": -28.083099999999998,
      "netAprPct": -307.50994499999996,
      "lechMarkBps": 1.507270681116461,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 2.75 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.08 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 2.93e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.1210000000000004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.7070000000000001,
      "phiBps": 29.0,
      "netBps": -28.293,
      "netAprPct": -309.80835,
      "lechMarkBps": 2.6290376076381596,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 2.12 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.29 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 8.31e-06,
      "rateShort": 4.25074158509e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.025922475527,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.341974158509,
      "phiBps": 29.0,
      "netBps": -28.658025841491,
      "netAprPct": -313.80538296432644,
      "lechMarkBps": 0.7093321511138188,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 18.800259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 1.03 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.66 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 2.73e-05,
      "rateShort": 4.32043226396e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.4771296791880001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.15904322639600002,
      "phiBps": 29.0,
      "netBps": -28.840956773604,
      "netAprPct": -315.8084766709638,
      "lechMarkBps": 1.3612850530899672,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 18.465259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.48 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.84 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 2.73e-05,
      "rateShort": 3.572e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.25259999999999994,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.08419999999999997,
      "phiBps": 29.0,
      "netBps": -28.9158,
      "netAprPct": -316.62801,
      "lechMarkBps": 1.4541241738537551,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 1.130259521484375,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.25 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.92 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 2.10944372087e-05,
      "rateShort": 2.93e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.246166883739,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.082055627913,
      "phiBps": 29.0,
      "netBps": -28.917944372087,
      "netAprPct": -316.65149087435265,
      "lechMarkBps": 1.127586401309128,
      "choMocDauGiay": 23954.869740478516,
      "tuoiXauNhatGiay": 17.933259521484374,
      "uocLuongMoc": false,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin",
        "chuyen-von",
        "basis-luc-thoat",
        "von-bi-khoa"
      ],
      "duyet": false,
      "lyDo": [
        "chênh lệch thô 0.25 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.92 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:13:17Z"
    }
  ],
  "soDuyet": 0,
  "viSaoTuChoi": {
    "chênh lệch thô quá mỏng": 24,
    "NET sau phí dưới ngưỡng": 30
  },
  "ruiRo": {
    "grossToiThieuBpsNgay": 3.0,
    "netToiThieuBps": 0.5,
    "lechMarkToiDaBps": 40.0,
    "doiHoiHaiMark": true,
    "tuoiToiDaGiay": 90.0,
    "nhanUocLuongMoc": false,
    "doiHoiItNhatMotMoc": true,
    "lechDongHoToiDaGiay": 10.0
  },
  "von": {
    "coHieuLuc": false,
    "moiCoHoiUsd": 100.0,
    "toiDaUsd": 300.0,
    "donBayToiDa": 1.0
  },
  "phiSan": {
    "hyperliquid": {
      "bat": true,
      "phiTakerBps": 4.5,
      "truotGiaBps": 2.0
    },
    "binance": {
      "bat": true,
      "phiTakerBps": 5.0,
      "truotGiaBps": 2.0
    },
    "okx": {
      "bat": true,
      "phiTakerBps": 5.0,
      "truotGiaBps": 2.0
    },
    "bybit": {
      "bat": true,
      "phiTakerBps": 5.5,
      "truotGiaBps": 2.0
    }
  },
  "doDai": [
    {
      "soMau": 2,
      "netTrungBinh": -26.2085849295435,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.3572,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.4257246015125,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.4301459326455,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.6175,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.810192,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.815592000000002,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.908882585462997,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    },
    {
      "soMau": 2,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    },
    {
      "soMau": 2,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "hyperliquid",
      "sanShort": "okx"
    },
    {
      "soMau": 2,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    }
  ],
  "so": {
    "soLuot": 2,
    "luotDauMs": 1787677978979,
    "luotCuoiMs": 1787677997853,
    "soCoHoi": 60,
    "soDuyet": 0,
    "soLoiGhi": 0,
    "loiCuoi": null,
    "duong": "thi-bac-ty.sqlite3",
    "chuaCo": false
  },
  "loiVongCuoi": null,
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi sàn nào và không đặt được lệnh nào."
};
