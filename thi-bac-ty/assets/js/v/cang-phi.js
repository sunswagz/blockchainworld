/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime — ĐỪNG SỬA TAY.
   Lát cắt chênh lệch funding giữa các cảng, để trang tĩnh đọc được mà không
   cần server và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python run.py                 ghi mỗi vòng lặp
       python -m bac.snapshot        ghi một lần rồi thoát
*/
window.CANG_PHI = {
  "date": "27/08/2026",
  "tomTat": "30 cặp đã cân · KHÔNG cặp nào qua cửa rủi ro",
  "generatedAt": "2026-08-27T14:07:16.183Z",
  "maChienLuoc": "perpetual.funding_spread.v1",
  "che": "quan-sat",
  "cheKhai": "quan-sat",
  "vong": 1,
  "chayDuocGiay": 13.82284951210022,
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
      "tuoiGiay": 12.910337646484376,
      "treTrungBinhMs": 303.16539999330416,
      "songSot": true
    },
    {
      "ten": "binance",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 12.9013623046875,
      "treTrungBinhMs": 311.1536999931559,
      "songSot": true
    },
    {
      "ten": "okx",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 12.594272216796876,
      "treTrungBinhMs": 618.699300015578,
      "songSot": true
    },
    {
      "ten": "bybit",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 12.923815673828125,
      "treTrungBinhMs": 289.0840999898501,
      "songSot": true
    }
  ],
  "dongHo": {
    "lechMs": -10.914794921875,
    "lechGiay": -0.010914794921875,
    "daDo": true,
    "dangKeu": false,
    "nguongKeuMs": 5000.0,
    "theoSan": {
      "bybit": -10.914794921875,
      "binance": -16.98388671875,
      "okx": 9.669677734375
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
      "markPx": 79565.0,
      "mocKeMs": 1787842800000,
      "oiUsd": 3049428170.3628,
      "tuoiGiay": 12.9107060546875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "ETH",
      "rate": 2.1826e-06,
      "intervalGio": 1.0,
      "moiGio": 2.1826e-06,
      "moiNgayBps": 0.5238240000000001,
      "markPx": 2495.1,
      "mocKeMs": 1787842800000,
      "oiUsd": 1732909683.301261,
      "tuoiGiay": 12.9107060546875,
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
      "markPx": 105.67,
      "mocKeMs": 1787842800000,
      "oiUsd": 724524628.3521997,
      "tuoiGiay": 12.9107060546875,
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
      "markPx": 0.08821,
      "mocKeMs": 1787842800000,
      "oiUsd": 56670723.91054,
      "tuoiGiay": 12.9107060546875,
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
      "markPx": 1.440921,
      "mocKeMs": 1787842800000,
      "oiUsd": 240509201.915604,
      "tuoiGiay": 12.9107060546875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "binance",
      "ma": "BTC",
      "rate": 7.711e-05,
      "intervalGio": 8.0,
      "moiGio": 9.63875e-06,
      "moiNgayBps": 2.3133,
      "markPx": 79545.3,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 13.6537060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 2h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "ETH",
      "rate": 2.474e-05,
      "intervalGio": 8.0,
      "moiGio": 3.0925e-06,
      "moiNgayBps": 0.7422000000000001,
      "markPx": 2494.83,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 13.6537060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 2h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "SOL",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 105.61,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 13.6537060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 2h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "XRP",
      "rate": -1.478e-05,
      "intervalGio": 8.0,
      "moiGio": -1.8475e-06,
      "moiNgayBps": -0.4434,
      "markPx": 1.4399,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 13.6537060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 2h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "DOGE",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.08819,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 13.6537060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 2h, lệch bản khai 8h"
    },
    {
      "san": "okx",
      "ma": "BTC",
      "rate": 4.96560232232e-05,
      "intervalGio": 8.0,
      "moiGio": 6.2070029029e-06,
      "moiNgayBps": 1.4896806966960001,
      "markPx": 79547.4,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 56.9577060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "ETH",
      "rate": 3.95650412784e-05,
      "intervalGio": 8.0,
      "moiGio": 4.9456301598e-06,
      "moiNgayBps": 1.186951238352,
      "markPx": 2495.05,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 13.8387060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "SOL",
      "rate": 4.15815112933e-05,
      "intervalGio": 8.0,
      "moiGio": 5.1976889116625e-06,
      "moiNgayBps": 1.247445338799,
      "markPx": 105.58,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 55.5957060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "XRP",
      "rate": -1.65405943882e-05,
      "intervalGio": 8.0,
      "moiGio": -2.067574298525e-06,
      "moiNgayBps": -0.49621783164600003,
      "markPx": 1.4401,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 13.5687060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "DOGE",
      "rate": -5.82751658234e-05,
      "intervalGio": 8.0,
      "moiGio": -7.284395727925e-06,
      "moiNgayBps": -1.748254974702,
      "markPx": 0.08818,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 56.0857060546875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "BTC",
      "rate": 7.77e-05,
      "intervalGio": 8.0,
      "moiGio": 9.7125e-06,
      "moiNgayBps": 2.3310000000000004,
      "markPx": 79548.8,
      "mocKeMs": 1787846400000,
      "oiUsd": 3872654581.85,
      "tuoiGiay": 12.9347060546875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "DOGE",
      "rate": 7.518e-05,
      "intervalGio": 8.0,
      "moiGio": 9.3975e-06,
      "moiNgayBps": 2.2554,
      "markPx": 0.0882,
      "mocKeMs": 1787846400000,
      "oiUsd": 134780800.96,
      "tuoiGiay": 12.9347060546875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "ETH",
      "rate": 1.08e-06,
      "intervalGio": 8.0,
      "moiGio": 1.35e-07,
      "moiNgayBps": 0.032400000000000005,
      "markPx": 2495.14,
      "mocKeMs": 1787846400000,
      "oiUsd": 1908351638.45,
      "tuoiGiay": 12.9347060546875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "SOL",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 105.615,
      "mocKeMs": 1787846400000,
      "oiUsd": 782378609.7,
      "tuoiGiay": 12.9347060546875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "XRP",
      "rate": -3.761e-05,
      "intervalGio": 8.0,
      "moiGio": -4.70125e-06,
      "moiNgayBps": -1.1283,
      "markPx": 1.4399,
      "mocKeMs": 1787846400000,
      "oiUsd": 316468523.16,
      "tuoiGiay": 12.9347060546875,
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
      "rateLong": -5.82751658234e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 4.748254974702,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.582751658234,
      "phiBps": 27.0,
      "netBps": -25.417248341766,
      "netAprPct": -278.31886934233773,
      "lechMarkBps": 3.4015533760419805,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 43.49342651367188,
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
        "NET sau phí -25.42 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": -1.65405943882e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.496217831646,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.165405943882,
      "phiBps": 27.0,
      "netBps": -25.834594056118,
      "netAprPct": -282.8888049144921,
      "lechMarkBps": 5.699368383638722,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 0.976426513671875,
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
        "NET sau phí -25.83 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": -1.478e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.4434000000000005,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.1478000000000002,
      "phiBps": 27.0,
      "netBps": -25.8522,
      "netAprPct": -283.08159,
      "lechMarkBps": 7.08825713225458,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "NET sau phí -25.85 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 4.15815112933e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.7525546612010001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.584184887067,
      "phiBps": 27.0,
      "netBps": -26.415815112933,
      "netAprPct": -289.2531754866163,
      "lechMarkBps": 8.52071005917192,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 43.003426513671876,
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
        "chênh lệch thô 1.75 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.42 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": -5.82751658234e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 4.748254974702,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.582751658234,
      "phiBps": 28.0,
      "netBps": -26.417248341766,
      "netAprPct": -289.26886934233767,
      "lechMarkBps": 1.1339797017644724,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 43.49342651367188,
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
        "NET sau phí -26.42 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 4.96560232232e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.5103193033039999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.503439767768,
      "phiBps": 27.0,
      "netBps": -26.496560232232,
      "netAprPct": -290.13733454294044,
      "lechMarkBps": 2.212272582150206,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 44.36542651367188,
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
        "chênh lệch thô 1.51 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.50 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -3.761e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 4.1283,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.3761,
      "phiBps": 28.0,
      "netBps": -26.6239,
      "netAprPct": -291.53170499999993,
      "lechMarkBps": 7.08825713225458,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 0.342426513671875,
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
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "BTC",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 7.711e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.6867000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.22890000000000005,
      "phiBps": 27.0,
      "netBps": -26.7711,
      "netAprPct": -293.143545,
      "lechMarkBps": 2.4762696066812886,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "chênh lệch thô 0.69 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.77 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "ETH",
      "sanLong": "hyperliquid",
      "sanShort": "okx",
      "rateLong": 2.1826e-06,
      "rateShort": 3.95650412784e-05,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.663127238352,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.221042412784,
      "phiBps": 27.0,
      "netBps": -26.778957587216,
      "netAprPct": -293.2295855800152,
      "lechMarkBps": 0.2003947777109993,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 1.246426513671875,
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
        "chênh lệch thô 0.66 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.78 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "ETH",
      "sanLong": "hyperliquid",
      "sanShort": "binance",
      "rateLong": 2.1826e-06,
      "rateShort": 2.474e-05,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.218376,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.072792,
      "phiBps": 27.0,
      "netBps": -26.927208,
      "netAprPct": -294.8529276,
      "lechMarkBps": 1.082179509532125,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "NET sau phí -26.93 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
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
      "lechMarkBps": 5.679666792881699,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
      "luc": "2026-08-27T14:07:03Z"
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
      "lechMarkBps": 2.2675736961442454,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 4.15815112933e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.7525546612010001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.584184887067,
      "phiBps": 28.0,
      "netBps": -27.415815112933,
      "netAprPct": -300.2031754866164,
      "lechMarkBps": 2.8410436100195215,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 43.003426513671876,
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
        "chênh lệch thô 1.75 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.42 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": -5.82751658234e-05,
      "rateShort": 7.518e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 4.003654974702,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.334551658234,
      "phiBps": 29.0,
      "netBps": -27.665448341766,
      "netAprPct": -302.93665934233775,
      "lechMarkBps": 2.267830819821536,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 43.49342651367188,
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
        "NET sau phí -27.67 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 4.96560232232e-05,
      "rateShort": 7.711e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.8236193033039999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.274539767768,
      "phiBps": 28.0,
      "netBps": -27.725460232232,
      "netAprPct": -303.5937895429404,
      "lechMarkBps": 0.2639970281466426,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 44.36542651367188,
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
        "chênh lệch thô 0.82 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.73 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 7.518e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.7446000000000003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.2482000000000001,
      "phiBps": 28.0,
      "netBps": -27.7518,
      "netAprPct": -303.88221,
      "lechMarkBps": 1.133722578084703,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 0.342426513671875,
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
        "chênh lệch thô 0.74 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.75 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 7.77e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.669,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.223,
      "phiBps": 28.0,
      "netBps": -27.777,
      "netAprPct": -304.15815,
      "lechMarkBps": 2.0362784371936424,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 0.342426513671875,
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
        "chênh lệch thô 0.67 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.78 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 1.08e-06,
      "rateShort": 2.1826e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.49142399999999997,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.163808,
      "phiBps": 28.0,
      "netBps": -27.836192,
      "netAprPct": -304.8063024,
      "lechMarkBps": 0.16031293084085585,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 0.342426513671875,
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
        "chênh lệch thô 0.49 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.84 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 2.474e-05,
      "rateShort": 3.95650412784e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.444751238352,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.148250412784,
      "phiBps": 28.0,
      "netBps": -27.851749587216,
      "netAprPct": -304.9766579800152,
      "lechMarkBps": 0.8817847322991922,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.246426513671875,
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
        "chênh lệch thô 0.44 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.85 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": -1.65405943882e-05,
      "rateShort": -1.478e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.05281783164599997,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.01760594388199999,
      "phiBps": 28.0,
      "netBps": -27.982394056118,
      "netAprPct": -306.4072149144921,
      "lechMarkBps": 1.388888888888736,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "chênh lệch thô 0.05 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.98 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "SOL",
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
      "lechMarkBps": 5.206238019737021,
      "choMocDauGiay": 3176.938573486328,
      "tuoiXauNhatGiay": 0.342426513671875,
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
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 4.15815112933e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.7525546612010001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.584184887067,
      "phiBps": 29.0,
      "netBps": -28.415815112933,
      "netAprPct": -311.1531754866163,
      "lechMarkBps": 3.3144724070168885,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 43.003426513671876,
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
        "chênh lệch thô 1.75 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.42 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 1.08e-06,
      "rateShort": 3.95650412784e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.154551238352,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.38485041278399995,
      "phiBps": 29.0,
      "netBps": -28.615149587216,
      "netAprPct": -313.33588798001523,
      "lechMarkBps": 0.3607077085228849,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.246426513671875,
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
        "chênh lệch thô 1.15 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.62 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 4.96560232232e-05,
      "rateShort": 7.77e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.8413193033040001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.280439767768,
      "phiBps": 29.0,
      "netBps": -28.719560232232,
      "netAprPct": -314.47918454294046,
      "lechMarkBps": 0.17599414693861087,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 44.36542651367188,
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
        "chênh lệch thô 0.84 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.72 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 7.518e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.7446000000000003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.2482000000000001,
      "phiBps": 29.0,
      "netBps": -28.7518,
      "netAprPct": -314.83221,
      "lechMarkBps": 1.1338511253468024,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "chênh lệch thô 0.74 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.75 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 1.08e-06,
      "rateShort": 2.474e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.7098,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.2366,
      "phiBps": 29.0,
      "netBps": -28.7634,
      "netAprPct": -314.95923000000005,
      "lechMarkBps": 1.242492439834089,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "chênh lệch thô 0.71 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.76 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -3.761e-05,
      "rateShort": -1.478e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.6849000000000001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.2283,
      "phiBps": 29.0,
      "netBps": -28.7717,
      "netAprPct": -315.050115,
      "lechMarkBps": 0.0,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "NET sau phí -28.77 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -3.761e-05,
      "rateShort": -1.65405943882e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.632082168354,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.21069405611800002,
      "phiBps": 29.0,
      "netBps": -28.789305943882,
      "netAprPct": -315.2429000855078,
      "lechMarkBps": 1.388888888888736,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 0.976426513671875,
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
        "NET sau phí -28.79 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "BTC",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 7.711e-05,
      "rateShort": 7.77e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.017700000000000188,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.005900000000000062,
      "phiBps": 29.0,
      "netBps": -28.9941,
      "netAprPct": -317.485395,
      "lechMarkBps": 0.4399911750341464,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "chênh lệch thô 0.02 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.99 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    },
    {
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 0.0001,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.0,
      "phiBps": 29.0,
      "netBps": -29.0,
      "netAprPct": -317.55,
      "lechMarkBps": 0.47342880814254495,
      "choMocDauGiay": 6776.938573486328,
      "tuoiXauNhatGiay": 1.061426513671875,
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
        "NET sau phí -29.00 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T14:07:03Z"
    }
  ],
  "toTrinh": [
    {
      "ma": "fa9585a92c9948ff",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 35965334.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 30.7338904109589,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 28.41931353976686,
      "netMoiGioBps": 0.03947126880523175,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6450098070191264,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6450098070191264
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 3.74% (thưởng 0.11% KHÔNG tính vào NET)",
        "TVL $36.0M · dùng vốn 90%",
        "rút ra được $36.0M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 54.2 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "2b5bff5a78ef41f5",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Base"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 25410507.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 27.252246575342465,
      "phiUocBps": 0.038923559999999996,
      "netUocBps": 27.213323015342464,
      "netMoiGioBps": 0.03779628196575342,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.5137807958613987,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.5137807958613987
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 3.32% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $25.4M · dùng vốn 86%",
        "rút ra được $25.4M",
        "gas khứ hồi 0.0 bps trên $500 · hoà gas sau 1.0 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "284bb59329724c0c",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 241093052.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 27.077095890410956,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 24.762519019218914,
      "netMoiGioBps": 0.034392387526692936,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.697532194411224,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.697532194411224
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 3.29% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $241.2M · dùng vốn 92%",
        "rút ra được $241.1M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 61.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "025adce1bc714406",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 29452627.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 27.014958904109587,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 24.700382032917545,
      "netMoiGioBps": 0.034306086156829924,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.32176135631903946,
        "giaoThuc": 0.17177956335401612,
        "cang": 0.17177956335401612,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.32176135631903946
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 3.29% (thưởng 4.11% KHÔNG tính vào NET)",
        "TVL $29.5M · dùng vốn 78%",
        "rút ra được $29.5M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 61.7 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "e249d96ab70a43dc",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 6223523.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.093753424657532,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 23.77917655346549,
      "netMoiGioBps": 0.0330266341020354,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6114575542211518,
        "giaoThuc": 0.3134692978131648,
        "cang": 0.3134692978131648,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6114575542211518
      },
      "tuoiDuLieuGiay": 0.024965087890625,
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
        "APY gốc 3.17% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $6.2M · dùng vốn 89%",
        "rút ra được $6.2M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 63.9 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "610b4cc986d644dc",
      "luc": "2026-08-27T14:07:05.493Z",
      "chienLuoc": "lending.rate_rotation.v1",
      "ho": "tin-dung",
      "taiSan": "USDC",
      "dinhGiaBang": "USDC",
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
          "taiSan": "USDC",
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 246946174.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 25.561315068493148,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 23.246738197301106,
      "netMoiGioBps": 0.03228713638514043,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6132091479174705,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6132091479174705
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 3.11% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $247.1M · dùng vốn 89%",
        "rút ra được $246.9M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 65.2 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "4043479121964b97",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Polygon"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 11663165.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 23.93827397260274,
      "phiUocBps": 0.8,
      "netUocBps": 23.13827397260274,
      "netMoiGioBps": 0.03213649162861491,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.04275731030260311,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 2.91% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $11.7M · dùng vốn 60%",
        "rút ra được $11.7M",
        "gas khứ hồi 0.8 bps trên $500 · hoà gas sau 24.1 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "9b587351fbc140b0",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 27834227.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 25.022219178082185,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 22.707642306890143,
      "netMoiGioBps": 0.031538392092902975,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.47791859591722274,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.47791859591722274
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 3.04% (thưởng 0.12% KHÔNG tính vào NET)",
        "TVL $27.8M · dùng vốn 85%",
        "rút ra được $27.8M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 66.6 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "b4f3990b0c814853",
      "luc": "2026-08-27T14:07:05.493Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 18994136.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 24.559479452054795,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 22.244902580862757,
      "netMoiGioBps": 0.03089569802897605,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.5077505611949202,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.5077505611949202
      },
      "tuoiDuLieuGiay": 0.025962158203125,
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
        "APY gốc 2.99% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $19.0M · dùng vốn 86%",
        "rút ra được $19.0M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 67.9 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "1dd3b65f3b804abe",
      "luc": "2026-08-27T14:07:05.494Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 7582330.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 23.318465753424654,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 21.003888882232616,
      "netMoiGioBps": 0.029172067891989745,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6016922151347037,
        "giaoThuc": 0.3134692978131648,
        "cang": 0.3134692978131648,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6016922151347037
      },
      "tuoiDuLieuGiay": 0.02695947265625,
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
        "APY gốc 2.84% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $7.6M · dùng vốn 89%",
        "rút ra được $7.6M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 71.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "c235be8021bf437e",
      "luc": "2026-08-27T14:07:05.494Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 60783106.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 21.52290410958904,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 19.208327238396997,
      "netMoiGioBps": 0.026678232275551383,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.45052836696573334,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45052836696573334
      },
      "tuoiDuLieuGiay": 0.02695947265625,
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
        "TVL $60.8M · dùng vốn 84%",
        "rút ra được $60.8M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 77.4 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "5c88b8438cc34612",
      "luc": "2026-08-27T14:07:05.494Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Arbitrum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 53431541.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 16.99117808219178,
      "phiUocBps": 0.1297452,
      "netUocBps": 16.86143288219178,
      "netMoiGioBps": 0.02341865678082192,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.1920303000625638,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.1920303000625638
      },
      "tuoiDuLieuGiay": 0.02695947265625,
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
        "APY gốc 2.07% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $53.5M · dùng vốn 72%",
        "rút ra được $53.4M",
        "gas khứ hồi 0.1 bps trên $500 · hoà gas sau 5.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "76386b9306dc4a0e",
      "luc": "2026-08-27T14:07:05.494Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 116957036.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 17.822465753424655,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 15.507888882232615,
      "netMoiGioBps": 0.02153873455865641,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.07892808123601547,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.02695947265625,
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
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 93.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "b319a8fc47584c7a",
      "luc": "2026-08-27T14:07:05.494Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 310495646.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 16.725780821917805,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 14.411203950725765,
      "netMoiGioBps": 0.020015561042674674,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.05739844351785109,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.02695947265625,
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
        "APY gốc 2.03% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $310.5M · dùng vốn 62%",
        "rút ra được $310.5M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 99.6 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "5f6b8eef3fcb469f",
      "luc": "2026-08-27T14:07:05.494Z",
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
          "vonUsd": 500.0,
          "loai": "lending",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 282426640.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 10.283424657534246,
      "phiUocBps": 2.31457687119204,
      "netUocBps": 7.968847786342206,
      "netMoiGioBps": 0.011067844147697507,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.050789118344380296,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.02695947265625,
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
        "APY gốc 1.25% (thưởng 1.36% KHÔNG tính vào NET)",
        "TVL $282.5M · dùng vốn 61%",
        "rút ra được $282.4M",
        "gas khứ hồi 2.3 bps trên $500 · hoà gas sau 162.1 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "7c23dac556ba4eee",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 45833.67,
      "khoaVonDenGiay": 2505.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2505.8812321319447,
      "raDuocKhong": null,
      "grossBps": 510.67027521785326,
      "phiUocBps": 0.0,
      "netUocBps": 510.67027521785326,
      "netMoiGioBps": 0.20378869863013702,
      "giuGio": 2505.8812321319447,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 17.85%/năm tới đáo hạn",
        "đáo hạn 2026-12-10, còn 104 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.6M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "42c04bd8499a4814",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 2673.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2673.8812321319447,
      "raDuocKhong": null,
      "grossBps": 426.15836802336884,
      "phiUocBps": 0.0,
      "netUocBps": 426.15836802336884,
      "netMoiGioBps": 0.15937819634703196,
      "giuGio": 2673.8812321319447,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 13.96%/năm tới đáo hạn",
        "đáo hạn 2026-12-17, còn 111 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $6.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "f2a9329a9f9c4439",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 1665.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1665.8812321319444,
      "raDuocKhong": null,
      "grossBps": 263.7253535882635,
      "phiUocBps": 0.0,
      "netUocBps": 263.7253535882635,
      "netMoiGioBps": 0.1583098173515982,
      "giuGio": 1665.8812321319444,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 13.87%/năm tới đáo hạn",
        "đáo hạn 2026-11-05, còn 69 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $17.7M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "178dd8fecaa64dd1",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 2169.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2169.881232131944,
      "raDuocKhong": null,
      "grossBps": 287.09956193808233,
      "phiUocBps": 0.0,
      "netUocBps": 287.09956193808233,
      "netMoiGioBps": 0.13231118721461185,
      "giuGio": 2169.881232131944,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 11.59%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 90 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $7.1M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "cd166ce24c0d4e7d",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 2505.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2505.8812321319447,
      "raDuocKhong": null,
      "grossBps": 318.0918722310064,
      "phiUocBps": 0.0,
      "netUocBps": 318.0918722310064,
      "netMoiGioBps": 0.1269381278538813,
      "giuGio": 2505.8812321319447,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 11.12%/năm tới đáo hạn",
        "đáo hạn 2026-12-10, còn 104 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $10.2M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "a234462b8b7d43ee",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Arbitrum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 1161.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1161.8812321319444,
      "raDuocKhong": null,
      "grossBps": 137.14124530534926,
      "phiUocBps": 0.0,
      "netUocBps": 136.79193130534927,
      "netMoiGioBps": 0.11773314476760137,
      "giuGio": 1161.8812321319444,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 10.34%/năm tới đáo hạn",
        "đáo hạn 2026-10-15, còn 48 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $11.4M",
        "phí vào+ra $0.03 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "bec96a718eb14862",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 1329.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1329.8812321319444,
      "raDuocKhong": null,
      "grossBps": 124.35649567719834,
      "phiUocBps": 0.0,
      "netUocBps": 124.35649567719834,
      "netMoiGioBps": 0.09350947488584475,
      "giuGio": 1329.8812321319444,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 8.19%/năm tới đáo hạn",
        "đáo hạn 2026-10-22, còn 55 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $10.4M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "f18bc9c487f5435d",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Arbitrum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 1161.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1161.8812321319444,
      "raDuocKhong": null,
      "grossBps": 97.46618446429575,
      "phiUocBps": 0.0,
      "netUocBps": 97.11687046429574,
      "netMoiGioBps": 0.08358588449362873,
      "giuGio": 1161.8812321319444,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 7.35%/năm tới đáo hạn",
        "đáo hạn 2026-10-15, còn 48 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $50.3M",
        "phí vào+ra $0.03 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "eaafea98afcf49a3",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 50000.0,
      "khoaVonDenGiay": 3345.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 3345.8812321319447,
      "raDuocKhong": null,
      "grossBps": 241.3904348517384,
      "phiUocBps": 0.0,
      "netUocBps": 241.3904348517384,
      "netMoiGioBps": 0.07214554794520549,
      "giuGio": 3345.8812321319447,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 6.32%/năm tới đáo hạn",
        "đáo hạn 2027-01-14, còn 139 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $5.6M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "1985d40b5e9c456e",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 34488.94,
      "khoaVonDenGiay": 2169.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2169.881231855,
      "raDuocKhong": null,
      "grossBps": 119.25924861745528,
      "phiUocBps": 0.0,
      "netUocBps": 119.25924861745528,
      "netMoiGioBps": 0.05496118721461187,
      "giuGio": 2169.881231855,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "đáo hạn 2026-11-26, còn 90 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.4M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "380ffb3cc6554f59",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 34715.43,
      "khoaVonDenGiay": 2169.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2169.881231855,
      "raDuocKhong": null,
      "grossBps": 117.25012685129364,
      "phiUocBps": 0.0,
      "netUocBps": 117.25012685129364,
      "netMoiGioBps": 0.054035273972602736,
      "giuGio": 2169.881231855,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 4.73%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 90 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "db2c24c6bb9840d3",
      "luc": "2026-08-27T14:07:07.567Z",
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
          "vonUsd": 1000.0,
          "loai": "yield",
          "chuoi": "Ethereum"
        }
      ],
      "vonCanUsd": 1000.0,
      "sucChuaToiDaUsd": 45392.13,
      "khoaVonDenGiay": 1329.8812313005556,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1329.8812321319444,
      "raDuocKhong": null,
      "grossBps": 68.79448287491861,
      "phiUocBps": 0.0,
      "netUocBps": 68.79448287491861,
      "netMoiGioBps": 0.05172979452054795,
      "giuGio": 1329.8812321319444,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21389236454016164,
        "cang": 0.21389236454016164,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.034908203125,
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
        "lãi CỐ ĐỊNH 4.53%/năm tới đáo hạn",
        "đáo hạn 2026-10-22, còn 55 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    }
  ],
  "soDuyet": 0,
  "viSaoTuChoi": {
    "NET sau phí dưới ngưỡng": 30,
    "chênh lệch thô quá mỏng": 24
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
      "soMau": 3,
      "netTrungBinh": -25.904754735098,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 3,
      "netTrungBinh": -26.445667097124332,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 3,
      "netTrungBinh": -26.181600000000003,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.415815112933,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 3,
      "netTrungBinh": -26.904754735098,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "binance"
    },
    {
      "soMau": 3,
      "netTrungBinh": -26.36601702895433,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 3,
      "netTrungBinh": -26.405133333333335,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.7711,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.778957587216,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "hyperliquid",
      "sanShort": "okx"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.927208,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    },
    {
      "soMau": 3,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    },
    {
      "soMau": 3,
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
    "soLuot": 3,
    "luotDauMs": 1787823346249,
    "luotCuoiMs": 1787839624014,
    "soCoHoi": 90,
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
        "che": "QUAN_SAT",
        "vi": "rót được nhiều nhất $150 < ngưỡng kinh tế $500 — engine này QUAN SÁT cho tới khi vốn đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một điều đã biết trước"
      },
      {
        "ma": "stablecoin.cross_venue.v1",
        "ho": "chenh-lech",
        "che": "QUAN_SAT",
        "vi": "rót được nhiều nhất $150 < ngưỡng kinh tế $200 — engine này QUAN SÁT cho tới khi vốn đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một điều đã biết trước"
      },
      {
        "ma": "yield.pendle_pt.v1",
        "ho": "tin-dung",
        "che": "QUAN_SAT",
        "vi": "rót được nhiều nhất $150 < ngưỡng kinh tế $1,000 — engine này QUAN SÁT cho tới khi vốn đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một điều đã biết trước"
      },
      {
        "ma": "basis.cash_carry.v1",
        "ho": "phai-sinh",
        "che": "QUAN_SAT",
        "vi": "rót được nhiều nhất $150 < ngưỡng kinh tế $200 — engine này QUAN SÁT cho tới khi vốn đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một điều đã biết trước"
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
        "che": "QUAN_SAT",
        "vi": "rót được nhiều nhất $150 < ngưỡng kinh tế $300 — engine này QUAN SÁT cho tới khi vốn đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một điều đã biết trước"
      },
      {
        "ma": "dex.round_trip.v1",
        "ho": "chenh-lech",
        "che": "QUAN_SAT",
        "vi": "rót được nhiều nhất $150 < ngưỡng kinh tế $500 — engine này QUAN SÁT cho tới khi vốn đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một điều đã biết trước"
      },
      {
        "ma": "amm.fee_farming.v1",
        "ho": "thanh-khoan",
        "che": "QUAN_SAT",
        "vi": "rót được nhiều nhất $150 < ngưỡng kinh tế $500 — engine này QUAN SÁT cho tới khi vốn đủ lớn, và ép nó vào lệnh sớm là trả tiền để học một điều đã biết trước"
      }
    ],
    "pheuTheoHo": [
      {
        "ho": "chenh-lech",
        "coHoiTho": 7,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      },
      {
        "ho": "phai-sinh",
        "coHoiTho": 854,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      },
      {
        "ho": "thanh-khoan",
        "coHoiTho": 9854,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      },
      {
        "ho": "tien-doan",
        "coHoiTho": 0,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      },
      {
        "ho": "tin-dung",
        "coHoiTho": 143,
        "quaCongTy": 27,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      }
    ],
    "navUsd": 1000.0,
    "vonNgoaiDayDu": false,
    "hienPhap": {
      "soDieu": 30,
      "soCanhDuoc": 24,
      "soKhongCanhDuoc": 6,
      "soViPham": 0,
      "khongCanhDuoc": [
        "khong-do-bang-so-do",
        "von-ngoai-bat-san",
        "khong-dem-hai-lan",
        "bi-danh-khong-phai-ban-sao",
        "basis-khong-phai-thu-nhap",
        "tu-choi-gioi-hon-phat-hien-nhieu"
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
      "loiNhac": "QUET_DUOC nghĩa là quét được NGAY, chỉ chưa thực thi được — mà cả runtime đang moPhong=True, nên KHÔNG ty nào trong sáu ty hiện có thực thi gì cả. «Chưa thực thi được» không phải lý do để không dựng. Cái phân biệt QUET_DUOC với CHAN là dữ liệu công khai không cần khoá."
    },
    "loiNhac": "CHÍN ty, năm họ. Trang này là cửa sổ nhìn vào ty chênh funding; tám ty còn lại chỉ hiện ở đây dưới dạng tổng hợp. Buồng lái đầy đủ chỉ sống ở localhost:5188 và không bao giờ lên site — trang công khai bấm được nút đặt lệnh là khoá đã ra tới trình duyệt."
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi sàn nào và không đặt được lệnh nào."
};
