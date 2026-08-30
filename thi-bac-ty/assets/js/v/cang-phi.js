/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime — ĐỪNG SỬA TAY.
   Lát cắt chênh lệch funding giữa các cảng, để trang tĩnh đọc được mà không
   cần server và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python -m bac.snapshot        quét một lượt, ghi, rồi thoát
       nút "Ghi lát cắt" ở buồng lái localhost:5188

   Vòng lặp nền KHÔNG tự ghi file này. Trang công khai đọc bản ĐÃ COMMIT,
   nên ghi mỗi 30 giây không làm site tươi hơn một giây nào — nó chỉ để
   lại một file được theo dõi luôn bẩn. SINH RỒI PHẢI COMMIT thì site mới
   đổi.
*/
window.CANG_PHI = {
  "date": "30/08/2026",
  "tomTat": "36 cặp đã cân · KHÔNG cặp nào qua cửa rủi ro",
  "generatedAt": "2026-08-30T03:07:59.339Z",
  "maChienLuoc": "perpetual.funding_spread.v1",
  "che": "quan-sat",
  "cheKhai": "quan-sat",
  "vong": 1,
  "chayDuocGiay": 14.254052877426147,
  "giuGio": 8.0,
  "ma": [
    "BTC",
    "ETH",
    "SOL",
    "XRP",
    "DOGE",
    "POL"
  ],
  "cang": [
    {
      "ten": "hyperliquid",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 13.33063818359375,
      "treTrungBinhMs": 185.30209999880753,
      "songSot": true
    },
    {
      "ten": "binance",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 13.0424736328125,
      "treTrungBinhMs": 473.00550001091324,
      "songSot": true
    },
    {
      "ten": "okx",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 13.084359619140624,
      "treTrungBinhMs": 430.2495000010822,
      "songSot": true
    },
    {
      "ten": "bybit",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 13.212448486328125,
      "treTrungBinhMs": 301.89460000838153,
      "songSot": true
    }
  ],
  "dongHo": {
    "lechMs": -97.72119140625,
    "lechGiay": -0.09772119140625,
    "daDo": true,
    "dangKeu": false,
    "nguongKeuMs": 5000.0,
    "theoSan": {
      "bybit": -106.61376953125,
      "binance": -97.72119140625,
      "okx": -85.1669921875
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
      "markPx": 78039.0,
      "mocKeMs": 1788062400000,
      "oiUsd": 2898960215.68998,
      "tuoiGiay": 13.332634033203124,
      "nguonTsMs": 1788059265876,
      "nhanTsMs": 1788059265876,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "ETH",
      "rate": 1.25e-05,
      "intervalGio": 1.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 2454.0,
      "mocKeMs": 1788062400000,
      "oiUsd": 1926760600.1351986,
      "tuoiGiay": 13.332634033203124,
      "nguonTsMs": 1788059265876,
      "nhanTsMs": 1788059265876,
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
      "markPx": 104.96,
      "mocKeMs": 1788062400000,
      "oiUsd": 639779529.8816,
      "tuoiGiay": 13.332634033203124,
      "nguonTsMs": 1788059265876,
      "nhanTsMs": 1788059265876,
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
      "markPx": 0.084937,
      "mocKeMs": 1788062400000,
      "oiUsd": 54026944.908342,
      "tuoiGiay": 13.332634033203124,
      "nguonTsMs": 1788059265876,
      "nhanTsMs": 1788059265876,
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
      "markPx": 1.3921,
      "mocKeMs": 1788062400000,
      "oiUsd": 223435204.49859998,
      "tuoiGiay": 13.332634033203124,
      "nguonTsMs": 1788059265876,
      "nhanTsMs": 1788059265876,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "POL",
      "rate": 1.25e-05,
      "intervalGio": 1.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.10415,
      "mocKeMs": 1788062400000,
      "oiUsd": 3839488.7085,
      "tuoiGiay": 13.332634033203124,
      "nguonTsMs": 1788059265876,
      "nhanTsMs": 1788059265876,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "binance",
      "ma": "BTC",
      "rate": 9.706e-05,
      "intervalGio": 8.0,
      "moiGio": 1.21325e-05,
      "moiNgayBps": 2.9118,
      "markPx": 78036.07438531,
      "mocKeMs": 1788076800000,
      "oiUsd": 8454340196.176504,
      "tuoiGiay": 14.208634033203126,
      "nguonTsMs": 1788059265000,
      "nhanTsMs": 1788059266044,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "ETH",
      "rate": 5.179e-05,
      "intervalGio": 8.0,
      "moiGio": 6.47375e-06,
      "moiNgayBps": 1.5537,
      "markPx": 2452.97,
      "mocKeMs": 1788076800000,
      "oiUsd": 5793467752.61358,
      "tuoiGiay": 14.208634033203126,
      "nguonTsMs": 1788059265000,
      "nhanTsMs": 1788059266124,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "SOL",
      "rate": -2.052e-05,
      "intervalGio": 8.0,
      "moiGio": -2.565e-06,
      "moiNgayBps": -0.6156,
      "markPx": 104.94137697,
      "mocKeMs": 1788076800000,
      "oiUsd": 893194062.861926,
      "tuoiGiay": 14.208634033203126,
      "nguonTsMs": 1788059265000,
      "nhanTsMs": 1788059266166,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "XRP",
      "rate": 1.344e-05,
      "intervalGio": 8.0,
      "moiGio": 1.68e-06,
      "moiNgayBps": 0.4032,
      "markPx": 1.3913,
      "mocKeMs": 1788076800000,
      "oiUsd": 433662173.42756,
      "tuoiGiay": 14.208634033203126,
      "nguonTsMs": 1788059265000,
      "nhanTsMs": 1788059266132,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "DOGE",
      "rate": 2.05e-05,
      "intervalGio": 8.0,
      "moiGio": 2.5625e-06,
      "moiNgayBps": 0.615,
      "markPx": 0.08491525,
      "mocKeMs": 1788076800000,
      "oiUsd": 224005354.472935,
      "tuoiGiay": 14.208634033203126,
      "nguonTsMs": 1788059265000,
      "nhanTsMs": 1788059266126,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "POL",
      "rate": 2.901e-05,
      "intervalGio": 4.0,
      "moiGio": 7.2525e-06,
      "moiNgayBps": 1.7406,
      "markPx": 0.1040851,
      "mocKeMs": 1788062400000,
      "oiUsd": 23155074.9622367,
      "tuoiGiay": 14.208634033203126,
      "nguonTsMs": 1788059265000,
      "nhanTsMs": 1788059266127,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 1h, lệch bản khai 4h"
    },
    {
      "san": "okx",
      "ma": "BTC",
      "rate": 3.20031195792e-05,
      "intervalGio": 8.0,
      "moiGio": 4.0003899474e-06,
      "moiNgayBps": 0.960093587376,
      "markPx": 78033.2,
      "mocKeMs": 1788076800000,
      "oiUsd": 2220601561.8899503,
      "tuoiGiay": 35.42763403320313,
      "nguonTsMs": 1788059243781,
      "nhanTsMs": 1788059266042,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "ETH",
      "rate": 3.33760353077e-05,
      "intervalGio": 8.0,
      "moiGio": 4.1720044134625e-06,
      "moiNgayBps": 1.001281059231,
      "markPx": 2453.26,
      "mocKeMs": 1788076800000,
      "oiUsd": 1527142824.0945637,
      "tuoiGiay": 35.34163403320313,
      "nguonTsMs": 1788059243867,
      "nhanTsMs": 1788059266071,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "SOL",
      "rate": -4.30799791624e-05,
      "intervalGio": 8.0,
      "moiGio": -5.3849973953e-06,
      "moiNgayBps": -1.292399374872,
      "markPx": 104.92,
      "mocKeMs": 1788076800000,
      "oiUsd": 334191277.6192002,
      "tuoiGiay": 34.056634033203125,
      "nguonTsMs": 1788059245152,
      "nhanTsMs": 1788059266048,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "XRP",
      "rate": 7.04369950296e-05,
      "intervalGio": 8.0,
      "moiGio": 8.8046243787e-06,
      "moiNgayBps": 2.113109850888,
      "markPx": 1.3914,
      "mocKeMs": 1788076800000,
      "oiUsd": 104437874.77199991,
      "tuoiGiay": 35.074634033203125,
      "nguonTsMs": 1788059244134,
      "nhanTsMs": 1788059266085,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "DOGE",
      "rate": 7.17553754492e-05,
      "intervalGio": 8.0,
      "moiGio": 8.96942193115e-06,
      "moiNgayBps": 2.1526612634760003,
      "markPx": 0.08492,
      "mocKeMs": 1788076800000,
      "oiUsd": 89436741.65669997,
      "tuoiGiay": 34.57863403320312,
      "nguonTsMs": 1788059244630,
      "nhanTsMs": 1788059266123,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "POL",
      "rate": -0.0001143090418779,
      "intervalGio": 4.0,
      "moiGio": -2.8577260469475e-05,
      "moiNgayBps": -6.858542512674,
      "markPx": 0.10404,
      "mocKeMs": 1788062400000,
      "oiUsd": 4418793.319,
      "tuoiGiay": 34.50063403320313,
      "nguonTsMs": 1788059244708,
      "nhanTsMs": 1788059266120,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "BTC",
      "rate": 6.334e-05,
      "intervalGio": 8.0,
      "moiGio": 7.9175e-06,
      "moiNgayBps": 1.9002000000000001,
      "markPx": 78031.95,
      "mocKeMs": 1788076800000,
      "oiUsd": 3889422018.78,
      "tuoiGiay": 13.222634033203125,
      "nguonTsMs": 1788059265986,
      "nhanTsMs": 1788059265986,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "DOGE",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.08493,
      "mocKeMs": 1788076800000,
      "oiUsd": 130815043.28,
      "tuoiGiay": 13.222634033203125,
      "nguonTsMs": 1788059265986,
      "nhanTsMs": 1788059265986,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "ETH",
      "rate": 1.246e-05,
      "intervalGio": 8.0,
      "moiGio": 1.5575e-06,
      "moiNgayBps": 0.37379999999999997,
      "markPx": 2452.95,
      "mocKeMs": 1788076800000,
      "oiUsd": 1858538866.72,
      "tuoiGiay": 13.222634033203125,
      "nguonTsMs": 1788059265986,
      "nhanTsMs": 1788059265986,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "POL",
      "rate": 2.001e-05,
      "intervalGio": 4.0,
      "moiGio": 5.0025e-06,
      "moiNgayBps": 1.2006,
      "markPx": 0.10408,
      "mocKeMs": 1788062400000,
      "oiUsd": 17026107.9,
      "tuoiGiay": 13.222634033203125,
      "nguonTsMs": 1788059265986,
      "nhanTsMs": 1788059265986,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "SOL",
      "rate": -8.7e-06,
      "intervalGio": 8.0,
      "moiGio": -1.0875e-06,
      "moiNgayBps": -0.26099999999999995,
      "markPx": 104.934,
      "mocKeMs": 1788076800000,
      "oiUsd": 770373957.87,
      "tuoiGiay": 13.222634033203125,
      "nguonTsMs": 1788059265986,
      "nhanTsMs": 1788059265986,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "XRP",
      "rate": 7.498e-05,
      "intervalGio": 8.0,
      "moiGio": 9.3725e-06,
      "moiNgayBps": 2.2494,
      "markPx": 1.3916,
      "mocKeMs": 1788076800000,
      "oiUsd": 307259483.01,
      "tuoiGiay": 13.222634033203125,
      "nguonTsMs": 1788059265986,
      "nhanTsMs": 1788059265986,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    }
  ],
  "coHoi": [
    {
      "ma": "POL",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": -0.0001143090418779,
      "rateShort": 1.25e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 9.858542512674001,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 8,
      "thuBps": 3.286180837558,
      "phiBps": 27.0,
      "netBps": -23.713819162442,
      "netAprPct": -259.6663198287399,
      "lechMarkBps": 10.56727028195522,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 21.46015576171875,
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
        "NET sau phí -23.71 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "POL",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": -0.0001143090418779,
      "rateShort": 2.901e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 8.599142512674,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 2,
      "thuBps": 2.866380837558,
      "phiBps": 28.0,
      "netBps": -25.133619162442,
      "netAprPct": -275.21312982873985,
      "lechMarkBps": 4.333931851564875,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 21.46015576171875,
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
        "NET sau phí -25.13 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": -4.30799791624e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 4.292399374872001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.430799791624,
      "phiBps": 27.0,
      "netBps": -25.569200208376,
      "netAprPct": -279.98274228171726,
      "lechMarkBps": 3.811701924908714,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 21.01615576171875,
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
        "NET sau phí -25.57 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": -2.052e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.6156,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.2052,
      "phiBps": 27.0,
      "netBps": -25.7948,
      "netAprPct": -282.45306,
      "lechMarkBps": 1.7744552483485825,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "NET sau phí -25.79 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 1.344e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.5968000000000004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.8656000000000001,
      "phiBps": 27.0,
      "netBps": -26.1344,
      "netAprPct": -286.17168,
      "lechMarkBps": 5.74836530861473,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 2.60 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.13 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 2.05e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.3850000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.795,
      "phiBps": 27.0,
      "netBps": -26.205,
      "netAprPct": -286.94475,
      "lechMarkBps": 2.561049382625304,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 2.39 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.20 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "POL",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": -0.0001143090418779,
      "rateShort": 2.001e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 8.059142512674,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 2,
      "thuBps": 2.686380837558,
      "phiBps": 29.0,
      "netBps": -26.313619162442,
      "netAprPct": -288.13412982873984,
      "lechMarkBps": 3.843936190660412,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 21.46015576171875,
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
        "NET sau phí -26.31 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 3.20031195792e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.039906412624,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.679968804208,
      "phiBps": 27.0,
      "netBps": -26.320031195792,
      "netAprPct": -288.20434159392244,
      "lechMarkBps": 0.743245754209002,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 22.38715576171875,
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
        "chênh lệch thô 2.04 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.32 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 3.33760353077e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.998718940769,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.6662396469230001,
      "phiBps": 27.0,
      "netBps": -26.333760353077,
      "netAprPct": -288.35467586619313,
      "lechMarkBps": 3.0159396486013854,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 22.30115576171875,
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
        "chênh lệch thô 2.00 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.33 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 5.179e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.4463000000000004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.4821000000000001,
      "phiBps": 27.0,
      "netBps": -26.5179,
      "netAprPct": -290.37100499999997,
      "lechMarkBps": 4.198110035317926,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 1.45 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.52 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "POL",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 2.901e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.2594000000000003,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 8,
      "thuBps": 0.41980000000000006,
      "phiBps": 27.0,
      "netBps": -26.5802,
      "netAprPct": -291.05319000000003,
      "lechMarkBps": 6.233339144073849,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 1.26 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.58 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 7.04369950296e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.886890149112,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.29563004970400003,
      "phiBps": 27.0,
      "netBps": -26.704369950296,
      "netAprPct": -292.41285095574125,
      "lechMarkBps": 5.029638943775267,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 22.03415576171875,
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
        "chênh lệch thô 0.89 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.70 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 7.17553754492e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.847338736524,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.282446245508,
      "phiBps": 27.0,
      "netBps": -26.717553754492,
      "netAprPct": -292.55721361168736,
      "lechMarkBps": 2.0016837692886518,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 21.53815576171875,
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
        "chênh lệch thô 0.85 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.72 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -8.7e-06,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.261,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.087,
      "phiBps": 28.0,
      "netBps": -26.913,
      "netAprPct": -294.69735,
      "lechMarkBps": 2.4774409940251982,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 0.29215576171875,
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
        "NET sau phí -26.91 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "BTC",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 9.706e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.08820000000000028,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.029400000000000093,
      "phiBps": 27.0,
      "netBps": -26.9706,
      "netAprPct": -295.32807,
      "lechMarkBps": 0.37489838803831704,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 0.09 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.97 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 1.246e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.6262000000000003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.8754000000000001,
      "phiBps": 28.0,
      "netBps": -27.1246,
      "netAprPct": -297.01437000000004,
      "lechMarkBps": 4.2796441781562145,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 0.29215576171875,
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
        "chênh lệch thô 2.63 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.12 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 3.20031195792e-05,
      "rateShort": 9.706e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.951706412624,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.6505688042079999,
      "phiBps": 28.0,
      "netBps": -27.349431195792,
      "netAprPct": -299.4762715939224,
      "lechMarkBps": 0.3683473664272773,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 22.38715576171875,
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
        "chênh lệch thô 1.95 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.35 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "POL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 2.001e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.7994,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 8,
      "thuBps": 0.5998,
      "phiBps": 28.0,
      "netBps": -27.4002,
      "netAprPct": -300.03219,
      "lechMarkBps": 6.723334774047986,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 0.29215576171875,
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
        "chênh lệch thô 1.80 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.40 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 1.344e-05,
      "rateShort": 7.04369950296e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.7099098508880002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.5699699502960001,
      "phiBps": 28.0,
      "netBps": -27.430030049704,
      "netAprPct": -300.3588290442588,
      "lechMarkBps": 0.7187264167893699,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 22.03415576171875,
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
        "chênh lệch thô 1.71 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.43 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 2.05e-05,
      "rateShort": 7.17553754492e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.5376612634760003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.512553754492,
      "phiBps": 28.0,
      "netBps": -27.487446245508,
      "netAprPct": -300.98753638831255,
      "lechMarkBps": 0.5593656205054971,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 21.53815576171875,
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
        "chênh lệch thô 1.54 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.49 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 6.334e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.0998,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.36660000000000004,
      "phiBps": 28.0,
      "netBps": -27.6334,
      "netAprPct": -302.58573,
      "lechMarkBps": 0.9034352645387127,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 0.29215576171875,
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
        "chênh lệch thô 1.10 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.63 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 7.498e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.7506,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.25020000000000003,
      "phiBps": 28.0,
      "netBps": -27.7498,
      "netAprPct": -303.86031,
      "lechMarkBps": 3.5923411287131874,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 0.29215576171875,
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
        "chênh lệch thô 0.75 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.75 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": -4.30799791624e-05,
      "rateShort": -2.052e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.676799374872,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.22559979162399998,
      "phiBps": 28.0,
      "netBps": -27.774400208376,
      "netAprPct": -304.12968228171724,
      "lechMarkBps": 2.037246711008417,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 21.01615576171875,
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
        "chênh lệch thô 0.68 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.77 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 3.33760353077e-05,
      "rateShort": 5.179e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.5524189407689999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.18413964692299994,
      "phiBps": 28.0,
      "netBps": -27.815860353077,
      "netAprPct": -304.58367086619313,
      "lechMarkBps": 1.1821704241359186,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 22.30115576171875,
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
        "NET sau phí -27.82 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "hyperliquid",
      "sanShort": "bybit",
      "rateLong": 1.25e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.0,
      "phiBps": 28.0,
      "netBps": -28.0,
      "netAprPct": -306.59999999999997,
      "lechMarkBps": 0.8241742068786901,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 0.29215576171875,
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
        "NET sau phí -28.00 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 2.05e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.3850000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.795,
      "phiBps": 29.0,
      "netBps": -28.205,
      "netAprPct": -308.84475,
      "lechMarkBps": 1.7368751849118904,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 2.39 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.20 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 1.344e-05,
      "rateShort": 7.498e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.8462000000000003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.6154000000000001,
      "phiBps": 29.0,
      "netBps": -28.3846,
      "netAprPct": -310.81136999999995,
      "lechMarkBps": 2.156024291206777,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 1.85 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.38 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 1.246e-05,
      "rateShort": 5.179e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.1799,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.3933,
      "phiBps": 29.0,
      "netBps": -28.6067,
      "netAprPct": -313.24336500000004,
      "lechMarkBps": 0.08153414650048028,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 1.18 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.61 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": -4.30799791624e-05,
      "rateShort": -8.7e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.0313993748719998,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.343799791624,
      "phiBps": 29.0,
      "netBps": -28.656200208376,
      "netAprPct": -313.78539228171724,
      "lechMarkBps": 1.3342609623829706,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 21.01615576171875,
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
        "NET sau phí -28.66 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 6.334e-05,
      "rateShort": 9.706e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.0115999999999998,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.33719999999999994,
      "phiBps": 29.0,
      "netBps": -28.6628,
      "netAprPct": -313.85766,
      "lechMarkBps": 0.5285368769479295,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 1.01 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.66 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 3.20031195792e-05,
      "rateShort": 6.334e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.940106412624,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.313368804208,
      "phiBps": 29.0,
      "netBps": -28.686631195792,
      "netAprPct": -314.11861159392237,
      "lechMarkBps": 0.1601895105986186,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 22.38715576171875,
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
        "chênh lệch thô 0.94 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.69 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 7.17553754492e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.847338736524,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.282446245508,
      "phiBps": 29.0,
      "netBps": -28.717553754492,
      "netAprPct": -314.45721361168734,
      "lechMarkBps": 1.1775095672664115,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 21.53815576171875,
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
        "chênh lệch thô 0.85 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.72 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 1.246e-05,
      "rateShort": 3.33760353077e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.6274810592310001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.209160353077,
      "phiBps": 29.0,
      "netBps": -28.790839646923,
      "netAprPct": -315.2596941338069,
      "lechMarkBps": 1.263704570331886,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 22.30115576171875,
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
        "chênh lệch thô 0.63 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.79 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "POL",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 2.001e-05,
      "rateShort": 2.901e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 0.5399999999999999,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 2,
      "thuBps": 0.17999999999999997,
      "phiBps": 29.0,
      "netBps": -28.82,
      "netAprPct": -315.57900000000006,
      "lechMarkBps": 0.48999568131199694,
      "choMocDauGiay": 3133.831844238281,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 0.54 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.82 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": -2.052e-05,
      "rateShort": -8.7e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.3546,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.1182,
      "phiBps": 29.0,
      "netBps": -28.8818,
      "netAprPct": -316.25570999999997,
      "lechMarkBps": 0.7029857534026192,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 1.16815576171875,
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
        "chênh lệch thô 0.35 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.88 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 7.04369950296e-05,
      "rateShort": 7.498e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.13629014911200002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.045430049704000004,
      "phiBps": 29.0,
      "netBps": -28.954569950296,
      "netAprPct": -317.0525409557412,
      "lechMarkBps": 1.4372978799854688,
      "choMocDauGiay": 17533.83184423828,
      "tuoiXauNhatGiay": 22.03415576171875,
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
        "chênh lệch thô 0.14 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.95 bps < ngưỡng 2.75"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-30T03:07:46Z"
    }
  ],
  "toTrinh": [
    {
      "ma": "3aeeb5caef324639",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
      "cang": [
        "compound-v3"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "compound-v3",
          "taiSan": "USDC",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 35953444.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 31.99323287671233,
      "phiUocBps": 0.279403904988,
      "netUocBps": 31.71382897172433,
      "netMoiGioBps": 0.04404698468295046,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6465503023807165,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6465503023807165
      },
      "tuoiDuLieuGiay": 0.041397705078125,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "compound-v3 trên Ethereum",
        "APY gốc 3.89% (thưởng 0.10% KHÔNG tính vào NET)",
        "TVL $36.0M · dùng vốn 90%",
        "rút ra được $36.0M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 6.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "97badf2b02b44865",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
      "cang": [
        "aave-v3"
      ],
      "chuoi": [
        "Base"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "aave-v3",
          "taiSan": "USDC",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Base"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 24322235.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 28.293041095890413,
      "phiUocBps": 0.0382824,
      "netUocBps": 28.254758695890413,
      "netMoiGioBps": 0.03924272041095891,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.5330987379439388,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.5330987379439388
      },
      "tuoiDuLieuGiay": 0.041397705078125,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "aave-v3 trên Base",
        "APY gốc 3.44% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $24.3M · dùng vốn 87%",
        "rút ra được $24.3M",
        "gas khứ hồi 0.0 bps trên $500 · hoà gas sau 1.0 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "e931a49a0deb4397",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDT",
      "dinhGiaBang": "USDT",
      "cang": [
        "aave-v3"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "aave-v3",
          "taiSan": "USDT",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 249117933.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 27.616931506849312,
      "phiUocBps": 0.279403904988,
      "netUocBps": 27.33752760186131,
      "netMoiGioBps": 0.037968788335918484,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6900479390027916,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6900479390027916
      },
      "tuoiDuLieuGiay": 0.041397705078125,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "aave-v3 trên Ethereum",
        "APY gốc 3.36% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $249.3M · dùng vốn 92%",
        "rút ra được $249.1M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 7.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "9c70900f507a4953",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
      "cang": [
        "dolomite"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "dolomite",
          "taiSan": "USDC",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 30578478.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.711013698630133,
      "phiUocBps": 0.279403904988,
      "netUocBps": 26.43160979364213,
      "netMoiGioBps": 0.03671056915783629,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.31193015117821943,
        "giaoThuc": 0.1729567565367267,
        "cang": 0.1729567565367267,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.31193015117821943
      },
      "tuoiDuLieuGiay": 0.041397705078125,
      "tinCay": 0.6,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "dolomite trên Ethereum",
        "APY gốc 3.25% (thưởng 4.16% KHÔNG tính vào NET)",
        "TVL $30.6M · dùng vốn 78%",
        "rút ra được $30.6M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 7.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "e2587083fe2744d6",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
      "cang": [
        "euler-v2"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "euler-v2",
          "taiSan": "USDC",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 6970084.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 25.392821917808217,
      "phiUocBps": 0.279403904988,
      "netUocBps": 25.113418012820215,
      "netMoiGioBps": 0.034879747240028076,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.5747013649887385,
        "giaoThuc": 0.31417153707121875,
        "cang": 0.31417153707121875,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.5747013649887385
      },
      "tuoiDuLieuGiay": 0.040399658203125,
      "tinCay": 0.65,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "euler-v2 trên Ethereum",
        "APY gốc 3.09% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $7.0M · dùng vốn 88%",
        "rút ra được $7.0M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 7.9 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "ad6ffbe1eaef4c61",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDT",
      "dinhGiaBang": "USDT",
      "cang": [
        "compound-v3"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "compound-v3",
          "taiSan": "USDT",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 30020204.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 24.748109589041093,
      "phiUocBps": 0.279403904988,
      "netUocBps": 24.46870568405309,
      "netMoiGioBps": 0.03398431345007374,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.45264896230083107,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45264896230083107
      },
      "tuoiDuLieuGiay": 0.041397705078125,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "compound-v3 trên Ethereum",
        "APY gốc 3.01% (thưởng 0.11% KHÔNG tính vào NET)",
        "TVL $30.0M · dùng vốn 84%",
        "rút ra được $30.0M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 8.1 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "7b9ccd69029c4451",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
      "cang": [
        "euler-v2"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "euler-v2",
          "taiSan": "USDC",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 5196781.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 24.467424657534245,
      "phiUocBps": 0.279403904988,
      "netUocBps": 24.188020752546244,
      "netMoiGioBps": 0.03359447326742534,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.640764080349243,
        "giaoThuc": 0.31417153707121875,
        "cang": 0.31417153707121875,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.640764080349243
      },
      "tuoiDuLieuGiay": 0.040399658203125,
      "tinCay": 0.65,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "euler-v2 trên Ethereum",
        "APY gốc 2.98% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $5.2M · dùng vốn 90%",
        "rút ra được $5.2M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 8.2 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "3de96991d442443f",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "DAI",
      "dinhGiaBang": "DAI",
      "cang": [
        "aave-v3"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "aave-v3",
          "taiSan": "DAI",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 19466738.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 24.347260273972605,
      "phiUocBps": 0.279403904988,
      "netUocBps": 24.067856368984604,
      "netMoiGioBps": 0.033427578290256395,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.49740431666268514,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.49740431666268514
      },
      "tuoiDuLieuGiay": 0.041397705078125,
      "tinCay": 0.65,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "aave-v3 trên Ethereum",
        "APY gốc 2.96% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $19.5M · dùng vốn 85%",
        "rút ra được $19.5M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 8.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "a529c9bcc3ba41fb",
      "luc": "2026-08-30T03:07:48.944Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
      "cang": [
        "aave-v3"
      ],
      "chuoi": [
        "Polygon"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "aave-v3",
          "taiSan": "USDC",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Polygon"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 12125249.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 23.233150684931505,
      "phiUocBps": 0.07530227270132113,
      "netUocBps": 23.157848412230184,
      "netMoiGioBps": 0.0321636783503197,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.035694671026235955,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.041397705078125,
      "tinCay": 0.65,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "aave-v3 trên Polygon",
        "APY gốc 2.83% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $12.1M · dùng vốn 59%",
        "rút ra được $12.1M",
        "gas khứ hồi 0.1 bps trên $500 · hoà gas sau 2.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "8a4c36c54e87449d",
      "luc": "2026-08-30T03:07:48.945Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDT",
      "dinhGiaBang": "USDT",
      "cang": [
        "sparklend"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "sparklend",
          "taiSan": "USDT",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 61763299.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 21.523068493150685,
      "phiUocBps": 0.279403904988,
      "netUocBps": 21.243664588162684,
      "netMoiGioBps": 0.029505089705781504,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.45057975653403326,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45057975653403326
      },
      "tuoiDuLieuGiay": 0.04239501953125,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "sparklend trên Ethereum",
        "APY gốc 2.62% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $61.8M · dùng vốn 84%",
        "rút ra được $61.8M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 9.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "8d6713eff73d4d12",
      "luc": "2026-08-30T03:07:48.945Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
      "cang": [
        "aave-v3"
      ],
      "chuoi": [
        "Arbitrum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "aave-v3",
          "taiSan": "USDC",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Arbitrum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 42309895.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 18.94627397260274,
      "phiUocBps": 0.1276973256,
      "netUocBps": 18.81857664700274,
      "netMoiGioBps": 0.026136912009726027,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.2691194122719564,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.2691194122719564
      },
      "tuoiDuLieuGiay": 0.04239501953125,
      "tinCay": 1.0,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "aave-v3 trên Arbitrum",
        "APY gốc 2.31% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $42.4M · dùng vốn 76%",
        "rút ra được $42.3M",
        "gas khứ hồi 0.1 bps trên $500 · hoà gas sau 4.9 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "1489bd53a20b4a59",
      "luc": "2026-08-30T03:07:48.945Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "DAI",
      "dinhGiaBang": "DAI",
      "cang": [
        "sparklend"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "sparklend",
          "taiSan": "DAI",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 116961893.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 17.823123287671233,
      "phiUocBps": 0.279403904988,
      "netUocBps": 17.543719382683232,
      "netMoiGioBps": 0.02436627692039338,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.0789501280460992,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.04239501953125,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "sparklend trên Ethereum",
        "APY gốc 2.17% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $117.3M · dùng vốn 64%",
        "rút ra được $117.0M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 11.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "bb70d05f685d4cec",
      "luc": "2026-08-30T03:07:48.945Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDS",
      "dinhGiaBang": "USDS",
      "cang": [
        "sparklend"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "sparklend",
          "taiSan": "USDS",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 268392183.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 16.72635616438356,
      "phiUocBps": 0.279403904988,
      "netUocBps": 16.44695225939556,
      "netMoiGioBps": 0.0228429892491605,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.05742512077383149,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.04239501953125,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "sparklend trên Ethereum",
        "APY gốc 2.04% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $268.5M · dùng vốn 62%",
        "rút ra được $268.4M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 12.0 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "16ee6198c7094f19",
      "luc": "2026-08-30T03:07:48.945Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDE",
      "dinhGiaBang": "USDE",
      "cang": [
        "aave-v3"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "aave-v3",
          "taiSan": "USDE",
          "vonUsd": 25000.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 231601457.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 15.80745205479452,
      "phiUocBps": 0.279403904988,
      "netUocBps": 15.528048149806521,
      "netMoiGioBps": 0.021566733541397945,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.09663884367750256,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.04239501953125,
      "tinCay": 0.6,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "chuyen-von-giua-chuoi",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-doi-stable"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "duong-cong-lai-suat",
        "do-sau-thi-truong-that"
      ],
      "bangChung": [
        "aave-v3 trên Ethereum",
        "APY gốc 1.92% (thưởng 1.52% KHÔNG tính vào NET)",
        "TVL $231.7M · dùng vốn 66%",
        "rút ra được $231.6M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 12.7 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "a3f6fd15e11c4d82",
      "luc": "2026-08-30T03:07:51.305Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "REUSDE",
      "dinhGiaBang": "REUSDE",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "REUSDE",
          "vonUsd": 22934.260000000002,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 22934.260000000002,
      "sucChuaToiDaUsd": 45868.520000000004,
      "khoaVonDenGio": 2444.869081817222,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2444.8690823711113,
      "raDuocKhong": null,
      "grossBps": 505.35081109573537,
      "phiUocBps": 0.0,
      "netUocBps": 505.35081109573537,
      "netMoiGioBps": 0.20669851598173516,
      "giuGio": 2444.8690823711113,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.039891357421875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-reUSDe-10DEC2026",
        "lãi CỐ ĐỊNH 18.11%/năm tới đáo hạn",
        "đáo hạn 2026-12-10, còn 102 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.6M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "757e7106858f4327",
      "luc": "2026-08-30T03:07:51.305Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "APYUSD",
      "dinhGiaBang": "APYUSD",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "APYUSD",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 1604.8690818172222,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1604.8690826480556,
      "raDuocKhong": null,
      "grossBps": 256.7759387517248,
      "phiUocBps": 0.0,
      "netUocBps": 256.7759387517248,
      "netMoiGioBps": 0.15999805936073058,
      "giuGio": 1604.8690826480556,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.039891357421875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-apyUSD-05NOV2026",
        "lãi CỐ ĐỊNH 14.02%/năm tới đáo hạn",
        "đáo hạn 2026-11-05, còn 67 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $18.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "717b6ade4d0544c1",
      "luc": "2026-08-30T03:07:51.305Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "USD3",
      "dinhGiaBang": "USD3",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "USD3",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 2612.869081817222,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2612.8690823711113,
      "raDuocKhong": null,
      "grossBps": 411.3828147466481,
      "phiUocBps": 0.0,
      "netUocBps": 411.3828147466481,
      "netMoiGioBps": 0.15744486301369864,
      "giuGio": 2612.8690823711113,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.039891357421875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-USD3-17DEC2026",
        "lãi CỐ ĐỊNH 13.79%/năm tới đáo hạn",
        "đáo hạn 2026-12-17, còn 109 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $6.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "765c67a76da84240",
      "luc": "2026-08-30T03:07:51.305Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "STRUSD",
      "dinhGiaBang": "STRUSD",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "STRUSD",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 2108.869081817222,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2108.8690826480556,
      "raDuocKhong": null,
      "grossBps": 281.70976162373614,
      "phiUocBps": 0.0,
      "netUocBps": 281.70976162373614,
      "netMoiGioBps": 0.13358333333333336,
      "giuGio": 2108.8690826480556,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.039891357421875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-strUSD-26NOV2026",
        "lãi CỐ ĐỊNH 11.70%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 88 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $7.1M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "6d9796eb82da4f5d",
      "luc": "2026-08-30T03:07:51.305Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "REUSD",
      "dinhGiaBang": "REUSD",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "REUSD",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 2444.869081817222,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2444.8690826480556,
      "raDuocKhong": null,
      "grossBps": 308.35632210254465,
      "phiUocBps": 0.0,
      "netUocBps": 308.35632210254465,
      "netMoiGioBps": 0.12612385844748858,
      "giuGio": 2444.8690826480556,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.039891357421875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-reUSD-10DEC2026",
        "lãi CỐ ĐỊNH 11.05%/năm tới đáo hạn",
        "đáo hạn 2026-12-10, còn 102 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $10.4M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "b9fbe0c45a76434f",
      "luc": "2026-08-30T03:07:51.305Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "SUSDAI",
      "dinhGiaBang": "SUSDAI",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Arbitrum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "SUSDAI",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Arbitrum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 1100.8690818172222,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1100.8690826480556,
      "raDuocKhong": null,
      "grossBps": 132.3450736120993,
      "phiUocBps": 0.0,
      "netUocBps": 132.00127312009928,
      "netMoiGioBps": 0.11990642229917149,
      "giuGio": 1100.8690826480556,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.039891357421875,
      "tinCay": 1.0,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "truot-gia-tren-amm-pendle",
        "thue",
        "router:gas-limit-uoc-luong"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Arbitrum · For buying PT-sUSDai-15OCT2026",
        "lãi CỐ ĐỊNH 10.53%/năm tới đáo hạn",
        "đáo hạn 2026-10-15, còn 46 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $11.9M",
        "phí vào+ra $0.03 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "43299542efe14701",
      "luc": "2026-08-30T03:07:51.306Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "USDAI",
      "dinhGiaBang": "USDAI",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Arbitrum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "USDAI",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Arbitrum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 1100.8690815402779,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1100.8690826480556,
      "raDuocKhong": null,
      "grossBps": 99.61897539068056,
      "phiUocBps": 0.0,
      "netUocBps": 99.27517489868056,
      "netMoiGioBps": 0.0901789108836464,
      "giuGio": 1100.8690826480556,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.04188671875,
      "tinCay": 1.0,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "truot-gia-tren-amm-pendle",
        "thue",
        "router:gas-limit-uoc-luong"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Arbitrum · For buying PT-USDai-15OCT2026",
        "lãi CỐ ĐỊNH 7.93%/năm tới đáo hạn",
        "đáo hạn 2026-10-15, còn 46 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $50.3M",
        "phí vào+ra $0.03 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "a8ad549f01904cbb",
      "luc": "2026-08-30T03:07:51.306Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "SIERRA",
      "dinhGiaBang": "SIERRA",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "SIERRA",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 1268.8690815402776,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1268.8690826480556,
      "raDuocKhong": null,
      "grossBps": 103.83752477352476,
      "phiUocBps": 0.0,
      "netUocBps": 103.83752477352476,
      "netMoiGioBps": 0.08183470319634703,
      "giuGio": 1268.8690826480556,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.040888671875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-SIERRA-22OCT2026",
        "lãi CỐ ĐỊNH 7.17%/năm tới đáo hạn",
        "đáo hạn 2026-10-22, còn 53 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $14.8M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "810d606d8b7b4f2c",
      "luc": "2026-08-30T03:07:51.306Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "USDAT",
      "dinhGiaBang": "USDAT",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "USDAT",
          "vonUsd": 25000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 25000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGio": 3284.869081540278,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 3284.8690823711113,
      "raDuocKhong": null,
      "grossBps": 228.60588896994568,
      "phiUocBps": 0.0,
      "netUocBps": 228.60588896994568,
      "netMoiGioBps": 0.06959360730593607,
      "giuGio": 3284.8690823711113,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.040888671875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-USDat-14JAN2027",
        "lãi CỐ ĐỊNH 6.10%/năm tới đáo hạn",
        "đáo hạn 2027-01-14, còn 137 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $5.7M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "3f0d351f98694394",
      "luc": "2026-08-30T03:07:51.306Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "SUSDS",
      "dinhGiaBang": "SUSDS",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "SUSDS",
          "vonUsd": 17352.65,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 17352.65,
      "sucChuaToiDaUsd": 34705.3,
      "khoaVonDenGio": 2108.869081540278,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2108.8690823711113,
      "raDuocKhong": null,
      "grossBps": 115.89487447723815,
      "phiUocBps": 0.0,
      "netUocBps": 115.89487447723815,
      "netMoiGioBps": 0.05495593607305936,
      "giuGio": 2108.8690823711113,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.040888671875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-sUSDS-26NOV2026",
        "lãi CỐ ĐỊNH 4.81%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 88 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "e418ba236f1a43db",
      "luc": "2026-08-30T03:07:51.306Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "SRUSDE",
      "dinhGiaBang": "SRUSDE",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "SRUSDE",
          "vonUsd": 22514.595,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 22514.595,
      "sucChuaToiDaUsd": 45029.19,
      "khoaVonDenGio": 1268.8690815402776,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1268.869082371111,
      "raDuocKhong": null,
      "grossBps": 68.2951401817999,
      "phiUocBps": 0.0,
      "netUocBps": 68.2951401817999,
      "netMoiGioBps": 0.05382363013698631,
      "giuGio": 1268.869082371111,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.040888671875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-srUSDe-22OCT2026",
        "lãi CỐ ĐỊNH 4.71%/năm tới đáo hạn",
        "đáo hạn 2026-10-22, còn 53 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "ebc651d7bba64eea",
      "luc": "2026-08-30T03:07:51.306Z",
      "chienLuoc": "yield.pendle_pt.v1",
      "ho": "tin-dung",
      "taiSan": "SUSDE",
      "dinhGiaBang": "SUSDE",
      "cang": [
        "pendle"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CHO_VAY",
          "cang": "pendle",
          "taiSan": "SUSDE",
          "vonUsd": 17854.72,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 17854.72,
      "sucChuaToiDaUsd": 35709.44,
      "khoaVonDenGio": 2108.869081540278,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2108.8690823711113,
      "raDuocKhong": null,
      "grossBps": 112.67475657246693,
      "phiUocBps": 0.0,
      "netUocBps": 112.67475657246693,
      "netMoiGioBps": 0.05342899543378996,
      "giuGio": 2108.8690823711113,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21051766825256635,
        "cang": 0.21051766825256635,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.040888671875,
      "tinCay": 0.75,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "gas-vao-ra",
        "truot-gia-tren-amm-pendle",
        "chuyen-von-giua-chuoi",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-amm-pendle"
      ],
      "bangChung": [
        "Pendle PT trên Ethereum · For buying PT-sUSDe-26NOV2026",
        "lãi CỐ ĐỊNH 4.68%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 88 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.6M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "bd3f8d62c1f64ec7",
      "luc": "2026-08-30T03:07:57.078Z",
      "chienLuoc": "amm.fee_farming.v1",
      "ho": "thanh-khoan",
      "taiSan": "SUSDE-USDT",
      "dinhGiaBang": "USD",
      "cang": [
        "uniswap-v4"
      ],
      "chuoi": [
        "Ethereum"
      ],
      "chan": [
        {
          "ben": "CAP_THANH_KHOAN",
          "cang": "uniswap-v4",
          "taiSan": "SUSDE-USDT",
          "vonUsd": 1224.304,
          "loai": "lp",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1224.304,
      "sucChuaToiDaUsd": 2448.608,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 2448.608,
      "gioVonBiGiu": 168.0,
      "raDuocKhong": true,
      "grossBps": 43.548112328767125,
      "phiUocBps": 1.5044825653199998,
      "netUocBps": 42.04362976344713,
      "netMoiGioBps": 0.25025970097289957,
      "giuGio": 168.0,
      "ruiRo": {
        "thiTruong": 0.35,
        "thanhKhoan": 0.3,
        "giaoThuc": 0.45,
        "cang": 0.1,
        "thucThi": 0.3,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.724649658203125,
      "tinCay": 0.9,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "ton-that-vo-thuong-du-neo",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-vao-ra-vi-the",
        "router:gas-limit-uoc-luong"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-that-cua-pool",
        "phan-tram-pool-ta-chiem"
      ],
      "bangChung": [
        "uniswap-v4 · Ethereum · SUSDE-USDT · ilRisk=no",
        "TVL $1,224,304 · khoi luong/ngay $7,541,181 · vong quay 6.160x",
        "muc phi SUY RA tu apyBase va khoi luong: 1.01 bps — hai con so KHOP nhau",
        "phi goc 22.71%/nam · thuong 0.00% KHONG tinh vao NET",
        "hoa von sau 6 gio",
        "TON THAT VO THUONG KHONG DUOC UOC. Ty nay chi nhan cap NEO nhau (ilRisk=no), va ke ca the thi IL cung KHONG bang 0 — stablecoin mat neo la IL that. Xem `ton-that-vo-thuong-du-neo`."
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "0d6fe9ef8f01417d",
      "luc": "2026-08-30T03:07:57.078Z",
      "chienLuoc": "amm.fee_farming.v1",
      "ho": "thanh-khoan",
      "taiSan": "USDC-USDT",
      "dinhGiaBang": "USD",
      "cang": [
        "uniswap-v3"
      ],
      "chuoi": [
        "Polygon"
      ],
      "chan": [
        {
          "ben": "CAP_THANH_KHOAN",
          "cang": "uniswap-v3",
          "taiSan": "USDC-USDT",
          "vonUsd": 1166.011,
          "loai": "lp",
          "chuoi": "Polygon"
        }
      ],
      "vonCanUsd": 1166.011,
      "sucChuaToiDaUsd": 2332.022,
      "khoaVonDenGio": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 2332.022,
      "gioVonBiGiu": 168.0,
      "raDuocKhong": true,
      "grossBps": 31.171517808219182,
      "phiUocBps": 0.40547377608403673,
      "netUocBps": 30.766044032135145,
      "netMoiGioBps": 0.1831312144769949,
      "giuGio": 168.0,
      "ruiRo": {
        "thiTruong": 0.35,
        "thanhKhoan": 0.3,
        "giaoThuc": 0.45,
        "cang": 0.1,
        "thucThi": 0.3,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.724649658203125,
      "tinCay": 0.9,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "ton-that-vo-thuong-du-neo",
        "gia-token-thuong",
        "thue",
        "truot-gia-khi-vao-ra-vi-the",
        "router:gas-limit-uoc-luong"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-that-cua-pool",
        "phan-tram-pool-ta-chiem"
      ],
      "bangChung": [
        "uniswap-v3 · Polygon · USDC-USDT · ilRisk=no",
        "TVL $1,166,011 · khoi luong/ngay $5,192,331 · vong quay 4.453x",
        "muc phi SUY RA tu apyBase va khoi luong: 1.00 bps — hai con so KHOP nhau",
        "phi goc 16.25%/nam · thuong 0.00% KHONG tinh vao NET",
        "hoa von sau 2 gio",
        "TON THAT VO THUONG KHONG DUOC UOC. Ty nay chi nhan cap NEO nhau (ilRisk=no), va ke ca the thi IL cung KHONG bang 0 — stablecoin mat neo la IL that. Xem `ton-that-vo-thuong-du-neo`."
      ],
      "hopLe": true,
      "loiKhuon": []
    }
  ],
  "soDuyet": 0,
  "viSaoTuChoi": {
    "NET sau phí dưới ngưỡng": 36,
    "chênh lệch thô quá mỏng": 30
  },
  "ruiRo": {
    "grossToiThieuBpsNgay": 3.0,
    "netToiThieuBps": 2.75,
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
      "soMau": 1,
      "netTrungBinh": -23.713819162442,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "POL",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -25.133619162442,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "POL",
      "sanLong": "okx",
      "sanShort": "binance"
    },
    {
      "soMau": 1,
      "netTrungBinh": -25.569200208376,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -25.7948,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.1344,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.205,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.313619162442,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "POL",
      "sanLong": "okx",
      "sanShort": "bybit"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.320031195792,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.333760353077,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.5179,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.5802,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "POL",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.704369950296,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    }
  ],
  "so": {
    "soLuot": 4,
    "luotDauMs": 1787823346249,
    "luotCuoiMs": 1788059267244,
    "soCoHoi": 126,
    "soDuyet": 0,
    "soLoiGhi": 0,
    "loiCuoi": null,
    "duong": "thi-bac-ty.sqlite3",
    "chuaCo": false
  },
  "loiVongCuoi": null,
  "trungUong": {
    "co": true,
    "soTy": 9,
    "ty": [
      {
        "ma": "perpetual.funding_spread.v1",
        "ho": "phai-sinh",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "lending.rate_rotation.v1",
        "ho": "tin-dung",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "stablecoin.cross_venue.v1",
        "ho": "chenh-lech",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "yield.pendle_pt.v1",
        "ho": "tin-dung",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "basis.cash_carry.v1",
        "ho": "phai-sinh",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "prediction.polymarket.v1",
        "ho": "tien-doan",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "options.put_call_parity.v1",
        "ho": "phai-sinh",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "dex.round_trip.v1",
        "ho": "chenh-lech",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      },
      {
        "ma": "amm.fee_farming.v1",
        "ho": "thanh-khoan",
        "che": "GIAY",
        "vi": "đủ vốn để cấp — trên SỔ GIẤY. Lớp ký lệnh chưa tồn tại, nên THẬT chưa với tới được"
      }
    ],
    "pheuTheoHo": [
      {
        "ho": "chenh-lech",
        "coHoiTho": 7,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0,
        "soTuChoi": 0,
        "lyDoTuChoi": []
      },
      {
        "ho": "phai-sinh",
        "coHoiTho": 689,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0,
        "soTuChoi": 0,
        "lyDoTuChoi": []
      },
      {
        "ho": "thanh-khoan",
        "coHoiTho": 9765,
        "quaCongTy": 2,
        "quaRuiRoTong": 2,
        "daCapVon": 2,
        "vonDangGiuUsd": 2390.31,
        "soTuChoi": 0,
        "lyDoTuChoi": []
      },
      {
        "ho": "tien-doan",
        "coHoiTho": 0,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0,
        "soTuChoi": 0,
        "lyDoTuChoi": []
      },
      {
        "ho": "tin-dung",
        "coHoiTho": 144,
        "quaCongTy": 26,
        "quaRuiRoTong": 4,
        "daCapVon": 4,
        "vonDangGiuUsd": 5000.0,
        "soTuChoi": 21,
        "lyDoTuChoi": [
          {
            "ma": "khoa-von-lau",
            "lyDo": "khoa-von-lau: khoá vốn 2109 giờ > trần 720 giờ — khoá lâu là từ chối mọi cơ hội tốt hơn xuất hiện trong ngần ấy thời gian",
            "so": 12,
            "soCauKhac": 7
          },
          {
            "ma": "duoi-von-toi-thieu",
            "lyDo": "duoi-von-toi-thieu: chỉ cấp được 0.00 USD nhưng engine này cần tối thiểu 500.00 USD mới kinh tế có nghĩa — QUAN SÁT, không ép vào lệnh (trần một ty lending.rate_rotation.v1: còn 0.00 USD)",
            "so": 7,
            "soCauKhac": 2
          },
          {
            "ma": "diem-rui-ro-cao",
            "lyDo": "diem-rui-ro-cao: điểm rủi ro 0.69 > trần 0.60",
            "so": 2,
            "soCauKhac": 2
          }
        ]
      }
    ],
    "navUsd": 9999.671991749405,
    "vonNgoaiDayDu": true,
    "hienPhap": {
      "soDieu": 34,
      "soCanhDuoc": 29,
      "soKhongCanhDuoc": 5,
      "soViPham": 0,
      "khongCanhDuoc": [
        "khong-do-bang-so-do",
        "von-ngoai-bat-san",
        "khong-dem-hai-lan",
        "bi-danh-khong-phai-ban-sao",
        "basis-khong-phai-thu-nhap"
      ]
    },
    "dongCoChuaCo": {
      "soDongCo": 6,
      "soChan": 3,
      "soQuetDuoc": 0,
      "soSanSang": 0,
      "soDaDung": 3,
      "theoTrangThai": {
        "CHAN": [
          "thanh-ly",
          "jit",
          "mev"
        ],
        "QUET_DUOC": [],
        "SAN_SANG": [],
        "DA_DUNG": [
          "dex-arb",
          "lp-v3",
          "quyen-chon"
        ]
      },
      "loiNhac": "QUET_DUOC nghĩa là quét được NGAY, chỉ chưa thực thi được — mà cả runtime đang moPhong=True, nên KHÔNG ty nào đang thực thi gì cả. «Chưa thực thi được» không phải lý do để không dựng. Cái phân biệt QUET_DUOC với CHAN là dữ liệu công khai không cần khoá."
    },
    "loiNhac": "CHÍN ty, năm họ. Trang này là cửa sổ nhìn vào ty chênh funding; tám ty còn lại chỉ hiện ở đây dưới dạng tổng hợp. Buồng lái đầy đủ chỉ sống ở localhost:5188 và không bao giờ lên site — trang công khai bấm được nút đặt lệnh là khoá đã ra tới trình duyệt."
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi sàn nào và không đặt được lệnh nào."
};
