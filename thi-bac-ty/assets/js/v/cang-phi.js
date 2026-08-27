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
  "generatedAt": "2026-08-27T09:37:30.488Z",
  "maChienLuoc": "perpetual.funding_spread.v1",
  "che": "quan-sat",
  "cheKhai": "quan-sat",
  "vong": 1,
  "chayDuocGiay": 11.915255308151245,
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
      "tuoiGiay": 11.219966552734375,
      "treTrungBinhMs": 150.03560000332072,
      "songSot": true
    },
    {
      "ten": "binance",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 11.084229736328124,
      "treTrungBinhMs": 285.12859999318607,
      "songSot": true
    },
    {
      "ten": "okx",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 11.15603662109375,
      "treTrungBinhMs": 212.81990001443774,
      "songSot": true
    },
    {
      "ten": "bybit",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 11.13908349609375,
      "treTrungBinhMs": 230.0573000102304,
      "songSot": true
    }
  ],
  "dongHo": {
    "lechMs": -19.474609375,
    "lechGiay": -0.019474609375,
    "daDo": true,
    "dangKeu": false,
    "nguongKeuMs": 5000.0,
    "theoSan": {
      "bybit": -25.22802734375,
      "binance": -19.474609375,
      "okx": -7.472900390625
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
      "markPx": 80277.5,
      "mocKeMs": 1787824800000,
      "oiUsd": 3046787624.4569,
      "tuoiGiay": 11.221667236328125,
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
      "markPx": 2543.7,
      "mocKeMs": 1787824800000,
      "oiUsd": 1837955063.5165215,
      "tuoiGiay": 11.221667236328125,
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
      "markPx": 104.8908,
      "mocKeMs": 1787824800000,
      "oiUsd": 646291853.4154322,
      "tuoiGiay": 11.221667236328125,
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
      "markPx": 0.089228,
      "mocKeMs": 1787824800000,
      "oiUsd": 57643215.3248,
      "tuoiGiay": 11.221667236328125,
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
      "markPx": 1.443,
      "mocKeMs": 1787824800000,
      "oiUsd": 239048153.448,
      "tuoiGiay": 11.221667236328125,
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
      "markPx": 80241.30115217,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 11.970667236328126,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "ETH",
      "rate": 9.219e-05,
      "intervalGio": 8.0,
      "moiGio": 1.152375e-05,
      "moiNgayBps": 2.7657,
      "markPx": 2543.10331008,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 11.970667236328126,
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
      "markPx": 104.81,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 11.970667236328126,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "XRP",
      "rate": 3.412e-05,
      "intervalGio": 8.0,
      "moiGio": 4.265e-06,
      "moiNgayBps": 1.0235999999999998,
      "markPx": 1.4417,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 11.970667236328126,
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
      "markPx": 0.08922066,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 11.970667236328126,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "BTC",
      "rate": 3.01385255192e-05,
      "intervalGio": 8.0,
      "moiGio": 3.7673156899e-06,
      "moiNgayBps": 0.904155765576,
      "markPx": 80239.9,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 76.45766723632812,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "ETH",
      "rate": 7.95342268374e-05,
      "intervalGio": 8.0,
      "moiGio": 9.941778354675e-06,
      "moiNgayBps": 2.386026805122,
      "markPx": 2542.98,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 76.36266723632812,
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
      "markPx": 104.76,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 75.02966723632812,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "XRP",
      "rate": 7.4863859447e-05,
      "intervalGio": 8.0,
      "moiGio": 9.357982430875e-06,
      "moiNgayBps": 2.24591578341,
      "markPx": 1.4415,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 76.06866723632812,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "DOGE",
      "rate": 1.48106548656e-05,
      "intervalGio": 8.0,
      "moiGio": 1.8513318582e-06,
      "moiNgayBps": 0.444319645968,
      "markPx": 0.08918,
      "mocKeMs": 1787846400000,
      "oiUsd": null,
      "tuoiGiay": 75.53466723632812,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "BTC",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 80242.88,
      "mocKeMs": 1787846400000,
      "oiUsd": 3968698980.15,
      "tuoiGiay": 11.145667236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "DOGE",
      "rate": 2.152e-05,
      "intervalGio": 8.0,
      "moiGio": 2.69e-06,
      "moiNgayBps": 0.6456000000000001,
      "markPx": 0.0892,
      "mocKeMs": 1787846400000,
      "oiUsd": 138623062.38,
      "tuoiGiay": 11.145667236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "ETH",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 2542.89,
      "mocKeMs": 1787846400000,
      "oiUsd": 2021433304.73,
      "tuoiGiay": 11.145667236328125,
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
      "markPx": 104.802,
      "mocKeMs": 1787846400000,
      "oiUsd": 764583441.65,
      "tuoiGiay": 11.145667236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "XRP",
      "rate": -7.215e-05,
      "intervalGio": 8.0,
      "moiGio": -9.01875e-06,
      "moiNgayBps": -2.1645000000000003,
      "markPx": 1.4419,
      "mocKeMs": 1787846400000,
      "oiUsd": 322570481.03,
      "tuoiGiay": 11.145667236328125,
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
      "rateLong": 1.48106548656e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.5556803540320003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.8518934513440001,
      "phiBps": 27.0,
      "netBps": -26.148106548656,
      "netAprPct": -286.32176670778324,
      "lechMarkBps": 5.380924622214964,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 64.45143481445312,
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
        "chênh lệch thô 2.56 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.15 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -7.215e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 5.1645,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.7215,
      "phiBps": 28.0,
      "netBps": -26.2785,
      "netAprPct": -287.749575,
      "lechMarkBps": 7.625914243128711,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.138434814453125,
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
        "NET sau phí -26.28 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 3.01385255192e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.0958442344240003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.698614744808,
      "phiBps": 27.0,
      "netBps": -26.301385255192,
      "netAprPct": -288.0001685443524,
      "lechMarkBps": 4.684850365132481,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 65.37443481445312,
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
        "chênh lệch thô 2.10 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.30 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 3.412e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.9764000000000004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.6588000000000002,
      "phiBps": 27.0,
      "netBps": -26.3412,
      "netAprPct": -288.43614,
      "lechMarkBps": 9.013068949978013,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.887434814453125,
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
        "chênh lệch thô 1.98 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.34 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 7.4863859447e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.7540842165900002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.2513614055300001,
      "phiBps": 27.0,
      "netBps": -26.74863859447,
      "netAprPct": -292.8975926094465,
      "lechMarkBps": 10.40041601664106,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 64.98543481445313,
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
        "NET sau phí -26.75 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 7.95342268374e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.6139731948780004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.20465773162600012,
      "phiBps": 27.0,
      "netBps": -26.795342268374,
      "netAprPct": -293.40899783869526,
      "lechMarkBps": 2.8309231168455646,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 65.27943481445313,
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
        "chênh lệch thô 0.61 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.80 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 9.219e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.23430000000000026,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.07810000000000009,
      "phiBps": 27.0,
      "netBps": -26.9219,
      "netAprPct": -294.794805,
      "lechMarkBps": 2.3460310282388552,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.887434814453125,
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
        "chênh lệch thô 0.23 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.92 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
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
      "lechMarkBps": 4.510231520566669,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.887434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
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
      "lechMarkBps": 7.706217620533296,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.887434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
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
      "lechMarkBps": 12.477891808664083,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 63.94643481445313,
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
      "luc": "2026-08-27T09:37:18Z"
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
      "lechMarkBps": 0.822645572122363,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.887434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 1.48106548656e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.5556803540320003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.8518934513440001,
      "phiBps": 28.0,
      "netBps": -27.148106548656,
      "netAprPct": -297.2717667077832,
      "lechMarkBps": 4.558279100536727,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 64.45143481445312,
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
        "chênh lệch thô 2.56 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.15 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 2.152e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.3544,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.7848,
      "phiBps": 28.0,
      "netBps": -27.2152,
      "netAprPct": -298.00644,
      "lechMarkBps": 3.1385208599547436,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.138434814453125,
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
        "chênh lệch thô 2.35 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.22 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 3.01385255192e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.0958442344240003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.698614744808,
      "phiBps": 28.0,
      "netBps": -27.301385255192,
      "netAprPct": -298.9501685443524,
      "lechMarkBps": 0.17461885378994751,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 65.37443481445312,
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
        "chênh lệch thô 2.10 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.30 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -7.215e-05,
      "rateShort": 7.4863859447e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 4.4104157834099995,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.4701385944699998,
      "phiBps": 29.0,
      "netBps": -27.52986140553,
      "netAprPct": -301.4519823905535,
      "lechMarkBps": 2.7745023236453905,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 64.98543481445313,
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
        "NET sau phí -27.53 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 3.412e-05,
      "rateShort": 7.4863859447e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.22231578341,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.40743859446999997,
      "phiBps": 28.0,
      "netBps": -27.59256140553,
      "netAprPct": -302.1385473905535,
      "lechMarkBps": 1.3873473917867507,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 64.98543481445313,
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
        "chênh lệch thô 1.22 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.59 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 7.95342268374e-05,
      "rateShort": 9.219e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.3796731948780001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.12655773162600004,
      "phiBps": 28.0,
      "netBps": -27.873442268374,
      "netAprPct": -305.2141928386952,
      "lechMarkBps": 0.48489209665765637,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 65.27943481445313,
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
        "chênh lệch thô 0.38 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.87 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -7.215e-05,
      "rateShort": 3.412e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.1881,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.0627,
      "phiBps": 29.0,
      "netBps": -27.9373,
      "netAprPct": -305.913435,
      "lechMarkBps": 1.387154945207227,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 0.887434814453125,
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
        "NET sau phí -27.94 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "BTC",
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
      "lechMarkBps": 4.313470974837631,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.138434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "ETH",
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
      "lechMarkBps": 3.1848448567702348,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.138434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
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
      "lechMarkBps": 8.4695325733637,
      "choMocDauGiay": 1361.1115651855469,
      "tuoiXauNhatGiay": 0.138434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
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
      "lechMarkBps": 4.771675335209921,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 63.94643481445313,
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
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 2.152e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.3544,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.7848,
      "phiBps": 29.0,
      "netBps": -28.2152,
      "netAprPct": -308.95644,
      "lechMarkBps": 2.31587530278072,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 0.887434814453125,
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
        "chênh lệch thô 2.35 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.22 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 3.01385255192e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.0958442344240003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.698614744808,
      "phiBps": 29.0,
      "netBps": -28.301385255192,
      "netAprPct": -309.9001685443524,
      "lechMarkBps": 0.37137940905690664,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 65.37443481445312,
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
        "chênh lệch thô 2.10 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.30 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 7.95342268374e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.6139731948780004,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.20465773162600012,
      "phiBps": 29.0,
      "netBps": -28.795342268374,
      "netAprPct": -315.30899783869535,
      "lechMarkBps": 0.35392174790211123,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 65.27943481445313,
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
        "chênh lệch thô 0.61 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.80 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 9.219e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.23430000000000026,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.07810000000000009,
      "phiBps": 29.0,
      "netBps": -28.9219,
      "netAprPct": -316.6948050000001,
      "lechMarkBps": 0.8388138441998874,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 0.887434814453125,
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
        "chênh lệch thô 0.23 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.92 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 1.48106548656e-05,
      "rateShort": 2.152e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.20128035403199998,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.06709345134400001,
      "phiBps": 29.0,
      "netBps": -28.932906548656,
      "netAprPct": -316.8153267077832,
      "lechMarkBps": 2.242403856935321,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 64.45143481445312,
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
        "chênh lệch thô 0.20 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.93 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "BTC",
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
      "lechMarkBps": 0.1967605552988588,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 0.887434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
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
      "lechMarkBps": 0.7633150773806427,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 0.887434814453125,
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
      "luc": "2026-08-27T09:37:18Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
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
      "lechMarkBps": 4.008360294328322,
      "choMocDauGiay": 22961.111565185547,
      "tuoiXauNhatGiay": 63.94643481445313,
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
      "luc": "2026-08-27T09:37:18Z"
    }
  ],
  "toTrinh": [
    {
      "ma": "c6266cd2404f4fe7",
      "luc": "2026-08-27T09:37:20.925Z",
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
      "thanhKhoanThoatUsd": 35011025.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 36.86687671232877,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 35.91269781114417,
      "netMoiGioBps": 0.049878746959922456,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6525321465196153,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6525321465196153
      },
      "tuoiDuLieuGiay": 0.020944580078125,
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
        "APY gốc 4.49% (thưởng 0.11% KHÔNG tính vào NET)",
        "TVL $35.0M · dùng vốn 90%",
        "rút ra được $35.0M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 18.6 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "bcce55bec0e04bf0",
      "luc": "2026-08-27T09:37:20.925Z",
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
      "thanhKhoanThoatUsd": 24229862.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 27.639698630136987,
      "phiUocBps": 0.2596646428701,
      "netUocBps": 27.380033987266888,
      "netMoiGioBps": 0.03802782498231512,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.5313569612703138,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.5313569612703138
      },
      "tuoiDuLieuGiay": 0.020944580078125,
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
        "APY gốc 3.36% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $24.2M · dùng vốn 86%",
        "rút ra được $24.2M",
        "gas khứ hồi 0.3 bps trên $500 · hoà gas sau 6.8 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "339b12759a9e4ae0",
      "luc": "2026-08-27T09:37:20.925Z",
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
      "thanhKhoanThoatUsd": 235479776.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 27.185342465753422,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 26.23116356456882,
      "netMoiGioBps": 0.036432171617456696,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.7036601469047433,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.7036601469047433
      },
      "tuoiDuLieuGiay": 0.020944580078125,
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
        "APY gốc 3.31% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $235.6M · dùng vốn 92%",
        "rút ra được $235.5M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 25.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "5ff7ea8dc5264521",
      "luc": "2026-08-27T09:37:20.925Z",
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
      "thanhKhoanThoatUsd": 29653166.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.934328767123286,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 25.980149865938685,
      "netMoiGioBps": 0.036083541480470396,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.31914202200494607,
        "giaoThuc": 0.17326348491723054,
        "cang": 0.17326348491723054,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.31914202200494607
      },
      "tuoiDuLieuGiay": 0.020944580078125,
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
        "APY gốc 3.28% (thưởng 4.11% KHÔNG tính vào NET)",
        "TVL $29.7M · dùng vốn 78%",
        "rút ra được $29.7M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 25.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "603d135900384410",
      "luc": "2026-08-27T09:37:20.925Z",
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
      "thanhKhoanThoatUsd": 6224952.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.09194520547945,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 25.13776630429485,
      "netMoiGioBps": 0.03491356431152062,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6113630194753604,
        "giaoThuc": 0.31180804380332294,
        "cang": 0.31180804380332294,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6113630194753604
      },
      "tuoiDuLieuGiay": 0.020944580078125,
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
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 26.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "4e302dc4a8a54ffb",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 226780953.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.071397260273972,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 25.11721835908937,
      "netMoiGioBps": 0.03488502549873524,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6412454682367005,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6412454682367005
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "APY gốc 3.17% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $226.9M · dùng vốn 90%",
        "rút ra được $226.8M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 26.4 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "81cee793f3614e75",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 29954827.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 24.730356164383558,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 23.776177263198957,
      "netMoiGioBps": 0.03302246842110966,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.45102964132644097,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45102964132644097
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "APY gốc 3.01% (thưởng 0.12% KHÔNG tính vào NET)",
        "TVL $30.0M · dùng vốn 84%",
        "rút ra được $30.0M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 27.8 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "9333ff6ff1454e2d",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 19022457.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 24.541561643835614,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 23.587382742651013,
      "netMoiGioBps": 0.03276025380923752,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.5068490707546138,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.5068490707546138
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 28.0 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "7c2475ae8cb54c57",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 11661839.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 23.931945205479447,
      "phiUocBps": 0.8,
      "netUocBps": 23.131945205479447,
      "netMoiGioBps": 0.03212770167427701,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.04268971849078777,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
      "ma": "172b1debee664527",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 7582814.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 23.317643835616437,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 22.363464934431835,
      "netMoiGioBps": 0.03106036796448866,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6016478608820106,
        "giaoThuc": 0.31180804380332294,
        "cang": 0.31180804380332294,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6016478608820106
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 29.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "5b429a888cb146aa",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 116943860.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 17.82271232876712,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 16.86853342758252,
      "netMoiGioBps": 0.023428518649420166,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.07893433155729186,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "rút ra được $116.9M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 38.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "3f4272c6d9c9427c",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 53775839.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 16.901260273972603,
      "phiUocBps": 0.13248403584,
      "netUocBps": 16.768776238132602,
      "netMoiGioBps": 0.023289966997406392,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.1887042187706515,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.1887042187706515
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "APY gốc 2.06% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $53.8M · dùng vốn 72%",
        "rút ra được $53.8M",
        "gas khứ hồi 0.1 bps trên $500 · hoà gas sau 5.6 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "78315dd26f5943b9",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 309439084.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 16.72594520547945,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 15.771766304294852,
      "netMoiGioBps": 0.021905230978187293,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.05740200163906945,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "TVL $309.5M · dùng vốn 62%",
        "rút ra được $309.4M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 41.1 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "b6bda824790a4631",
      "luc": "2026-08-27T09:37:20.926Z",
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
      "thanhKhoanThoatUsd": 278323985.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 10.471315068493151,
      "phiUocBps": 0.9541789011845999,
      "netUocBps": 9.517136167308552,
      "netMoiGioBps": 0.013218244676817432,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.05593584515148199,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 0.021942138671875,
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
        "APY gốc 1.27% (thưởng 1.34% KHÔNG tính vào NET)",
        "TVL $278.4M · dùng vốn 62%",
        "rút ra được $278.3M",
        "gas khứ hồi 1.0 bps trên $500 · hoà gas sau 65.6 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "3ab22f6726104fee",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "sucChuaToiDaUsd": 45829.04,
      "khoaVonDenGiay": 2510.3770761686114,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2510.377076730278,
      "raDuocKhong": null,
      "grossBps": 511.5864775377909,
      "phiUocBps": 0.0,
      "netUocBps": 511.5864775377909,
      "netMoiGioBps": 0.203788698630137,
      "giuGio": 2510.377076730278,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "đáo hạn 2026-12-10, còn 105 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.6M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "cd76e4098af04ade",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "khoaVonDenGiay": 2678.3770761686114,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2678.377076730278,
      "raDuocKhong": null,
      "grossBps": 426.11419961658714,
      "phiUocBps": 0.0,
      "netUocBps": 426.11419961658714,
      "netMoiGioBps": 0.15909417808219178,
      "giuGio": 2678.377076730278,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "lãi CỐ ĐỊNH 13.94%/năm tới đáo hạn",
        "đáo hạn 2026-12-17, còn 112 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $6.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "511922d5c26d4c73",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "khoaVonDenGiay": 1670.377076168611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1670.3770767302778,
      "raDuocKhong": null,
      "grossBps": 263.74243425303206,
      "phiUocBps": 0.0,
      "netUocBps": 263.74243425303206,
      "netMoiGioBps": 0.15789394977168952,
      "giuGio": 1670.3770767302778,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "lãi CỐ ĐỊNH 13.83%/năm tới đáo hạn",
        "đáo hạn 2026-11-05, còn 70 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $17.3M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "5cd59e720bf84719",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "khoaVonDenGiay": 2174.377076168611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2174.3770767302776,
      "raDuocKhong": null,
      "grossBps": 287.99177591482237,
      "phiUocBps": 0.0,
      "netUocBps": 287.99177591482237,
      "netMoiGioBps": 0.13244794520547945,
      "giuGio": 2174.3770767302776,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "lãi CỐ ĐỊNH 11.60%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 91 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $7.1M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "cf670d1490244ad8",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "khoaVonDenGiay": 2510.3770761686114,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2510.377076730278,
      "raDuocKhong": null,
      "grossBps": 324.74736501125517,
      "phiUocBps": 0.0,
      "netUocBps": 324.74736501125517,
      "netMoiGioBps": 0.12936198630136986,
      "giuGio": 2510.377076730278,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "lãi CỐ ĐỊNH 11.33%/năm tới đáo hạn",
        "đáo hạn 2026-12-10, còn 105 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $10.2M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "fba7c66756234810",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "khoaVonDenGiay": 1166.377076168611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1166.3770767302778,
      "raDuocKhong": null,
      "grossBps": 137.87162898451615,
      "phiUocBps": 0.0,
      "netUocBps": 137.51494119571615,
      "netMoiGioBps": 0.11789921453293117,
      "giuGio": 1166.3770767302778,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "lãi CỐ ĐỊNH 10.35%/năm tới đáo hạn",
        "đáo hạn 2026-10-15, còn 49 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $11.4M",
        "phí vào+ra $0.04 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "0b36e5a628ed4ceb",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "khoaVonDenGiay": 1334.377076168611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1334.3770767302778,
      "raDuocKhong": null,
      "grossBps": 124.71596928463218,
      "phiUocBps": 0.0,
      "netUocBps": 124.71596928463218,
      "netMoiGioBps": 0.09346381278538812,
      "giuGio": 1334.3770767302778,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "đáo hạn 2026-10-22, còn 56 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $10.4M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "c0c8fdfd4b4b4233",
      "luc": "2026-08-27T09:37:22.525Z",
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
      "khoaVonDenGiay": 1166.377076168611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1166.3770770072224,
      "raDuocKhong": null,
      "grossBps": 97.85317824590729,
      "phiUocBps": 0.0,
      "netUocBps": 97.49649045710729,
      "netMoiGioBps": 0.08358916887090329,
      "giuGio": 1166.3770770072224,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "đáo hạn 2026-10-15, còn 49 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $50.3M",
        "phí vào+ra $0.04 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "b966de094df441ae",
      "luc": "2026-08-27T09:37:22.526Z",
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
      "khoaVonDenGiay": 3350.3770761686114,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 3350.377076730278,
      "raDuocKhong": null,
      "grossBps": 237.73640847671277,
      "phiUocBps": 0.0,
      "netUocBps": 237.73640847671277,
      "netMoiGioBps": 0.07095810502283105,
      "giuGio": 3350.377076730278,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.01897705078125,
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
        "lãi CỐ ĐỊNH 6.22%/năm tới đáo hạn",
        "đáo hạn 2027-01-14, còn 140 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $5.6M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "de1dd2cdc15e4f22",
      "luc": "2026-08-27T09:37:22.526Z",
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
      "sucChuaToiDaUsd": 34490.19,
      "khoaVonDenGiay": 2174.377075890278,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2174.3770767302776,
      "raDuocKhong": null,
      "grossBps": 119.506097372772,
      "phiUocBps": 0.0,
      "netUocBps": 119.506097372772,
      "netMoiGioBps": 0.05496107305936073,
      "giuGio": 2174.3770767302776,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.019979736328125,
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
        "đáo hạn 2026-11-26, còn 91 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.4M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "629e1da7cd494b29",
      "luc": "2026-08-27T09:37:22.526Z",
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
      "sucChuaToiDaUsd": 34717.19,
      "khoaVonDenGiay": 2174.377075890278,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2174.3770767302776,
      "raDuocKhong": null,
      "grossBps": 117.4930610608676,
      "phiUocBps": 0.0,
      "netUocBps": 117.4930610608676,
      "netMoiGioBps": 0.05403527397260274,
      "giuGio": 2174.3770767302776,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.019979736328125,
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
        "đáo hạn 2026-11-26, còn 91 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "cca5a6e836c04353",
      "luc": "2026-08-27T09:37:22.526Z",
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
      "sucChuaToiDaUsd": 45389.88,
      "khoaVonDenGiay": 1334.3770758902779,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1334.3770767302778,
      "raDuocKhong": null,
      "grossBps": 68.62095047545579,
      "phiUocBps": 0.0,
      "netUocBps": 68.62095047545579,
      "netMoiGioBps": 0.05142545662100457,
      "giuGio": 1334.3770767302778,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21422058206553785,
        "cang": 0.21422058206553785,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 0.019979736328125,
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
        "lãi CỐ ĐỊNH 4.50%/năm tới đáo hạn",
        "đáo hạn 2026-10-22, còn 56 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "c1233a8f828b44c5",
      "luc": "2026-08-27T09:37:22.999Z",
      "chienLuoc": "basis.cash_carry.v1",
      "ho": "phai-sinh",
      "taiSan": "BTC",
      "dinhGiaBang": "USDT",
      "cang": [
        "binance"
      ],
      "chuoi": [],
      "chan": [
        {
          "ben": "LONG",
          "cang": "binance",
          "taiSan": "BTC",
          "vonUsd": 100.0,
          "loai": "spot",
          "chuoi": null
        },
        {
          "ben": "SHORT",
          "cang": "binance",
          "taiSan": "BTC",
          "vonUsd": 100.0,
          "loai": "perp",
          "chuoi": null
        }
      ],
      "vonCanUsd": 200.0,
      "sucChuaToiDaUsd": null,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 200.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 168.0,
      "raDuocKhong": null,
      "grossBps": 21.000000000000004,
      "phiUocBps": 20.0,
      "netUocBps": 1.0000000000000036,
      "netMoiGioBps": 0.005952380952380974,
      "giuGio": 168.0,
      "ruiRo": {
        "thiTruong": 0.05,
        "thanhKhoan": null,
        "giaoThuc": 0.05,
        "cang": 0.25,
        "thucThi": 0.25,
        "cauNoi": 0.0,
        "chuaDo": [
          "thanhKhoan"
        ],
        "caoNhat": 0.25
      },
      "tuoiDuLieuGiay": 4.978333740234375,
      "tinCay": 0.5096322538971199,
      "moHinhPhiDuChua": false,
      "phiConThieu": [
        "vay-coin-neu-ban-khong-giao-ngay",
        "basis-luc-thoat",
        "von-bi-khoa",
        "thue"
      ],
      "moHinhSucChuaDuChua": false,
      "sucChuaConThieu": [
        "do-sau-so-lenh-perp"
      ],
      "bangChung": [
        "binance: mua giao ngay 80,237.89 · bán khống perp mark 80,241.30",
        "basis +0.4 bps — KHÔNG tính vào NET, perp không đáo hạn nên không có gì bảo đảm nó hội tụ",
        "funding +0.0013%/giờ · chu kỳ 8h · giữ 168h chứa 21 MỐC",
        "gross +21.00 − phí 20.00 (4 lần taker) = NET +1.00 bps",
        "GIẢ ĐỊNH: mức funding hiện tại giữ nguyên suốt 21 mốc (168 giờ). Nó không giữ nguyên — độ tin đã hạ theo độ dài cửa sổ."
      ],
      "hopLe": true,
      "loiKhuon": []
    }
  ],
  "soDuyet": 0,
  "viSaoTuChoi": {
    "chênh lệch thô quá mỏng": 27,
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
      "netTrungBinh": -26.148507931764,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.295749999999998,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.300745427315498,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.3463,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.7512036176275,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.792983923129,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2,
      "netTrungBinh": -26.914900000000003,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "binance",
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
    },
    {
      "soMau": 2,
      "netTrungBinh": -27.148507931764,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "binance"
    }
  ],
  "so": {
    "soLuot": 2,
    "luotDauMs": 1787823346249,
    "luotCuoiMs": 1787823439615,
    "soCoHoi": 60,
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
        "coHoiTho": 850,
        "quaCongTy": 1,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      },
      {
        "ho": "thanh-khoan",
        "coHoiTho": 9861,
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
        "quaCongTy": 26,
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
