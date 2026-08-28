/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime — ĐỪNG SỬA TAY.
   Lát cắt chênh lệch funding giữa các cảng, để trang tĩnh đọc được mà không
   cần server và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python run.py                 ghi mỗi vòng lặp
       python -m bac.snapshot        ghi một lần rồi thoát
*/
window.CANG_PHI = {
  "date": "28/08/2026",
  "tomTat": "36 cặp đã cân · KHÔNG cặp nào qua cửa rủi ro",
  "generatedAt": "2026-08-28T13:44:20.425Z",
  "maChienLuoc": "perpetual.funding_spread.v1",
  "che": "quan-sat",
  "cheKhai": "quan-sat",
  "vong": 2,
  "chayDuocGiay": 30.748591423034668,
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
      "tongLuot": 2,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.03001318359375,
      "treTrungBinhMs": 245.70393999892985,
      "songSot": true
    },
    {
      "ten": "binance",
      "tongLuot": 2,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.0255146484375,
      "treTrungBinhMs": 368.9224400011881,
      "songSot": true
    },
    {
      "ten": "okx",
      "tongLuot": 2,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.086371826171875,
      "treTrungBinhMs": 208.13055999860808,
      "songSot": true
    },
    {
      "ten": "bybit",
      "tongLuot": 2,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.088366943359375,
      "treTrungBinhMs": 225.38737999857403,
      "songSot": true
    }
  ],
  "dongHo": {
    "lechMs": -18.34716796875,
    "lechGiay": -0.01834716796875,
    "daDo": true,
    "dangKeu": false,
    "nguongKeuMs": 5000.0,
    "theoSan": {
      "bybit": -21.862548828125,
      "binance": -18.34716796875,
      "okx": -8.34130859375
    },
    "soMau": 3
  },
  "baoGia": [
    {
      "san": "hyperliquid",
      "ma": "BTC",
      "rate": 4.1639e-06,
      "intervalGio": 1.0,
      "moiGio": 4.1639e-06,
      "moiNgayBps": 0.9993360000000001,
      "markPx": 79076.0,
      "mocKeMs": 1787925600000,
      "oiUsd": 2825835049.2012796,
      "tuoiGiay": 0.031748779296875,
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
      "markPx": 2497.5,
      "mocKeMs": 1787925600000,
      "oiUsd": 1906637282.6715014,
      "tuoiGiay": 0.031748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "SOL",
      "rate": 3.2654e-06,
      "intervalGio": 1.0,
      "moiGio": 3.2654e-06,
      "moiNgayBps": 0.783696,
      "markPx": 104.69,
      "mocKeMs": 1787925600000,
      "oiUsd": 613702999.8378006,
      "tuoiGiay": 0.031748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "DOGE",
      "rate": 8.5912e-06,
      "intervalGio": 1.0,
      "moiGio": 8.5912e-06,
      "moiNgayBps": 2.061888,
      "markPx": 0.086579,
      "mocKeMs": 1787925600000,
      "oiUsd": 54142553.40286,
      "tuoiGiay": 0.031748779296875,
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
      "markPx": 1.4151,
      "mocKeMs": 1787925600000,
      "oiUsd": 227316300.771,
      "tuoiGiay": 0.031748779296875,
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
      "markPx": 0.1078,
      "mocKeMs": 1787925600000,
      "oiUsd": 3996668.6144000003,
      "tuoiGiay": 0.031748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "binance",
      "ma": "BTC",
      "rate": 6.136e-05,
      "intervalGio": 8.0,
      "moiGio": 7.67e-06,
      "moiNgayBps": 1.8407999999999998,
      "markPx": 79074.57325362,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 0.435748779296875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 4h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "ETH",
      "rate": 9.272e-05,
      "intervalGio": 8.0,
      "moiGio": 1.159e-05,
      "moiNgayBps": 2.7816,
      "markPx": 2497.12517829,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 0.435748779296875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 4h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "SOL",
      "rate": -5.817e-05,
      "intervalGio": 8.0,
      "moiGio": -7.27125e-06,
      "moiNgayBps": -1.7451,
      "markPx": 104.63453999,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 0.435748779296875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 4h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "XRP",
      "rate": -4.33e-06,
      "intervalGio": 8.0,
      "moiGio": -5.4125e-07,
      "moiNgayBps": -0.1299,
      "markPx": 1.41510449,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 0.435748779296875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 4h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "DOGE",
      "rate": 2.015e-05,
      "intervalGio": 8.0,
      "moiGio": 2.51875e-06,
      "moiNgayBps": 0.6044999999999999,
      "markPx": 0.08658785,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 0.435748779296875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế gợi ý 4h, lệch bản khai 8h"
    },
    {
      "san": "binance",
      "ma": "POL",
      "rate": 5e-05,
      "intervalGio": 4.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.10773405,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 0.435748779296875,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "BTC",
      "rate": 0.0001,
      "intervalGio": 8.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 79079.6,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 11.535748779296876,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "ETH",
      "rate": 8.88185384945e-05,
      "intervalGio": 8.0,
      "moiGio": 1.11023173118125e-05,
      "moiNgayBps": 2.6645561548349996,
      "markPx": 2496.95,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 11.449748779296876,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "SOL",
      "rate": 7.1388293388e-06,
      "intervalGio": 8.0,
      "moiGio": 8.9235366735e-07,
      "moiNgayBps": 0.21416488016400004,
      "markPx": 104.63,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 10.115748779296876,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "XRP",
      "rate": 7.26369006365e-05,
      "intervalGio": 8.0,
      "moiGio": 9.0796125795625e-06,
      "moiNgayBps": 2.179107019095,
      "markPx": 1.415,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 11.169748779296874,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "DOGE",
      "rate": 4.53185531178e-05,
      "intervalGio": 8.0,
      "moiGio": 5.664819139725e-06,
      "moiNgayBps": 1.359556593534,
      "markPx": 0.08656,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 10.656748779296874,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "POL",
      "rate": 5e-05,
      "intervalGio": 4.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.10773,
      "mocKeMs": 1787932800000,
      "oiUsd": null,
      "tuoiGiay": 10.586748779296874,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "BTC",
      "rate": 8.81e-05,
      "intervalGio": 8.0,
      "moiGio": 1.10125e-05,
      "moiNgayBps": 2.643,
      "markPx": 79075.82,
      "mocKeMs": 1787932800000,
      "oiUsd": 3872002958.45,
      "tuoiGiay": 0.094748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "DOGE",
      "rate": 0.0,
      "intervalGio": 8.0,
      "moiGio": 0.0,
      "moiNgayBps": 0.0,
      "markPx": 0.08657,
      "mocKeMs": 1787932800000,
      "oiUsd": 130138044.08,
      "tuoiGiay": 0.094748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "ETH",
      "rate": 6.088e-05,
      "intervalGio": 8.0,
      "moiGio": 7.61e-06,
      "moiNgayBps": 1.8264,
      "markPx": 2497.01,
      "mocKeMs": 1787932800000,
      "oiUsd": 1878975079.87,
      "tuoiGiay": 0.094748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "POL",
      "rate": 5e-05,
      "intervalGio": 4.0,
      "moiGio": 1.25e-05,
      "moiNgayBps": 3.0000000000000004,
      "markPx": 0.10773,
      "mocKeMs": 1787932800000,
      "oiUsd": 17409013.3,
      "tuoiGiay": 0.094748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "SOL",
      "rate": -0.00017082,
      "intervalGio": 8.0,
      "moiGio": -2.13525e-05,
      "moiNgayBps": -5.124599999999999,
      "markPx": 104.62,
      "mocKeMs": 1787932800000,
      "oiUsd": 803689605.48,
      "tuoiGiay": 0.094748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "XRP",
      "rate": -3.312e-05,
      "intervalGio": 8.0,
      "moiGio": -4.14e-06,
      "moiNgayBps": -0.9935999999999999,
      "markPx": 1.4149,
      "mocKeMs": 1787932800000,
      "oiUsd": 307155843.36,
      "tuoiGiay": 0.094748779296875,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    }
  ],
  "coHoi": [
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": -4.33e-06,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.1298999999999997,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.0433,
      "phiBps": 27.0,
      "netBps": -25.9567,
      "netAprPct": -284.225865,
      "lechMarkBps": 0.031729156079627605,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "NET sau phí -25.96 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -0.00017082,
      "rateShort": 3.2654e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 5.908295999999999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.969432,
      "phiBps": 28.0,
      "netBps": -26.030568,
      "netAprPct": -285.03471959999996,
      "lechMarkBps": 6.688643638621488,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.07088671875,
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
        "NET sau phí -26.03 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": -5.817e-05,
      "rateShort": 3.2654e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.528796,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.842932,
      "phiBps": 27.0,
      "netBps": -26.157068,
      "netAprPct": -286.4198946,
      "lechMarkBps": 5.298949659954244,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "chênh lệch thô 2.53 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.16 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "okx",
      "rateLong": 4.1639e-06,
      "rateShort": 0.0001,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.000664,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.6668879999999999,
      "phiBps": 27.0,
      "netBps": -26.333112,
      "netAprPct": -288.3475763999999,
      "lechMarkBps": 0.45524786982007853,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 11.51188671875,
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
        "NET sau phí -26.33 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 2.015e-05,
      "rateShort": 8.5912e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.457388,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.485796,
      "phiBps": 27.0,
      "netBps": -26.514204,
      "netAprPct": -290.3305338,
      "lechMarkBps": 1.0221355877283453,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "chênh lệch thô 1.46 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.51 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -3.312e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.9936,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.3312,
      "phiBps": 28.0,
      "netBps": -26.6688,
      "netAprPct": -292.02336,
      "lechMarkBps": 1.4134275618373,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.07088671875,
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
        "NET sau phí -26.67 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "binance",
      "rateLong": 4.1639e-06,
      "rateShort": 6.136e-05,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.8414639999999998,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.28048799999999996,
      "phiBps": 27.0,
      "netBps": -26.719512,
      "netAprPct": -292.57865640000006,
      "lechMarkBps": 0.18042885974470177,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "NET sau phí -26.72 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 7.26369006365e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.8208929809050001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.273630993635,
      "phiBps": 27.0,
      "netBps": -26.726369006365,
      "netAprPct": -292.6537406196968,
      "lechMarkBps": 0.7066888095826225,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 11.14588671875,
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
        "NET sau phí -26.73 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 4.53185531178e-05,
      "rateShort": 8.5912e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.702331406466,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.23411046882200004,
      "phiBps": 27.0,
      "netBps": -26.765889531178,
      "netAprPct": -293.08649036639906,
      "lechMarkBps": 2.1947683653024592,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 10.63288671875,
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
        "chênh lệch thô 0.70 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.77 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 7.1388293388e-06,
      "rateShort": 3.2654e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.569531119836,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.18984370661200003,
      "phiBps": 27.0,
      "netBps": -26.810156293388,
      "netAprPct": -293.5712114125986,
      "lechMarkBps": 5.732849226065572,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 10.09188671875,
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
        "chênh lệch thô 0.57 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.81 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 8.88185384945e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.33544384516500025,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.11181461505500008,
      "phiBps": 27.0,
      "netBps": -26.888185384945,
      "netAprPct": -294.4256299651478,
      "lechMarkBps": 2.20244471363286,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 11.42588671875,
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
        "chênh lệch thô 0.34 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.89 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 9.272e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.21839999999999996,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.07279999999999998,
      "phiBps": 27.0,
      "netBps": -26.9272,
      "netAprPct": -294.85284,
      "lechMarkBps": 1.5009002542546452,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "POL",
      "sanLong": "hyperliquid",
      "sanShort": "binance",
      "rateLong": 1.25e-05,
      "rateShort": 5e-05,
      "intervalLongGio": 1.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 2,
      "thuBps": 0.0,
      "phiBps": 27.0,
      "netBps": -27.0,
      "netAprPct": -295.65,
      "lechMarkBps": 6.119682713706633,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "POL",
      "sanLong": "hyperliquid",
      "sanShort": "okx",
      "rateLong": 1.25e-05,
      "rateShort": 5e-05,
      "intervalLongGio": 1.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 2,
      "thuBps": 0.0,
      "phiBps": 27.0,
      "netBps": -27.0,
      "netAprPct": -295.65,
      "lechMarkBps": 6.495615459564851,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 10.56288671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -0.00017082,
      "rateShort": 7.1388293388e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 5.338764880164001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.779588293388,
      "phiBps": 29.0,
      "netBps": -27.220411706612,
      "netAprPct": -298.0635081874014,
      "lechMarkBps": 0.9557945041807316,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 10.09188671875,
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
        "NET sau phí -27.22 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": -4.33e-06,
      "rateShort": 7.26369006365e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.309007019095,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.769669006365,
      "phiBps": 28.0,
      "netBps": -27.230330993635,
      "netAprPct": -298.1721243803033,
      "lechMarkBps": 0.7384179656208569,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 11.14588671875,
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
        "chênh lệch thô 2.31 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.23 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 0.0,
      "rateShort": 8.5912e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.061888,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.687296,
      "phiBps": 28.0,
      "netBps": -27.312704,
      "netAprPct": -299.07410880000003,
      "lechMarkBps": 1.0395670780667519,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.07088671875,
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
        "chênh lệch thô 2.06 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.31 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": -5.817e-05,
      "rateShort": 7.1388293388e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.9592648801640002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.653088293388,
      "phiBps": 28.0,
      "netBps": -27.346911706612,
      "netAprPct": -299.44868318740146,
      "lechMarkBps": 0.4338995990639196,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 10.09188671875,
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
        "chênh lệch thô 1.96 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.35 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "bybit",
      "rateLong": 4.1639e-06,
      "rateShort": 8.81e-05,
      "intervalLongGio": 1.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.643664,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 1,
      "thuBps": 0.547888,
      "phiBps": 28.0,
      "netBps": -27.452112,
      "netAprPct": -300.6006264,
      "lechMarkBps": 0.02276293753597209,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.07088671875,
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
        "chênh lệch thô 1.64 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.45 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 6.088e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.1736000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.39120000000000005,
      "phiBps": 28.0,
      "netBps": -27.6088,
      "netAprPct": -302.31636,
      "lechMarkBps": 1.962154445580374,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.07088671875,
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
        "chênh lệch thô 1.17 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.61 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "BTC",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 6.136e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.1592000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.3864000000000001,
      "phiBps": 28.0,
      "netBps": -27.613599999999998,
      "netAprPct": -302.36892,
      "lechMarkBps": 0.6356767294342444,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 11.51188671875,
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
        "chênh lệch thô 1.16 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.61 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 2.015e-05,
      "rateShort": 4.53185531178e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.7550565935339999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.25168553117799997,
      "phiBps": 28.0,
      "netBps": -27.748314468822,
      "netAprPct": -303.8440434336009,
      "lechMarkBps": 3.216903934989194,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 10.63288671875,
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
        "chênh lệch thô 0.76 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.75 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -0.00017082,
      "rateShort": -5.817e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.3795,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.1265,
      "phiBps": 29.0,
      "netBps": -27.8735,
      "netAprPct": -305.21482499999996,
      "lechMarkBps": 1.3896941018038202,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "NET sau phí -27.87 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -3.312e-05,
      "rateShort": 7.26369006365e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.1727070190950006,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.057569006365,
      "phiBps": 29.0,
      "netBps": -27.942430993635,
      "netAprPct": -305.96961938030324,
      "lechMarkBps": 0.7067387540194987,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 11.14588671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 8.88185384945e-05,
      "rateShort": 9.272e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.1170438451650003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.0390146150550001,
      "phiBps": 28.0,
      "netBps": -27.960985384945,
      "netAprPct": -306.1727899651478,
      "lechMarkBps": 0.7015444651758659,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 11.42588671875,
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
        "chênh lệch thô 0.12 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.96 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "POL",
      "sanLong": "hyperliquid",
      "sanShort": "bybit",
      "rateLong": 1.25e-05,
      "rateShort": 5e-05,
      "intervalLongGio": 1.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 8,
      "soMocShort": 2,
      "thuBps": 0.0,
      "phiBps": 28.0,
      "netBps": -28.0,
      "netAprPct": -306.59999999999997,
      "lechMarkBps": 6.495615459564851,
      "choMocDauGiay": 940.58811328125,
      "tuoiXauNhatGiay": 0.07088671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "POL",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 5e-05,
      "rateShort": 5e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 2,
      "thuBps": 0.0,
      "phiBps": 28.0,
      "netBps": -28.0,
      "netAprPct": -306.59999999999997,
      "lechMarkBps": 0.3759327832175771,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 10.56288671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 0.0,
      "rateShort": 4.53185531178e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.359556593534,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.453185531178,
      "phiBps": 29.0,
      "netBps": -28.546814468822,
      "netAprPct": -312.58761843360094,
      "lechMarkBps": 1.1552012938250011,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 10.63288671875,
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
        "chênh lệch thô 1.36 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.55 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 6.088e-05,
      "rateShort": 9.272e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.9552000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.31840000000000007,
      "phiBps": 29.0,
      "netBps": -28.6816,
      "netAprPct": -314.06352,
      "lechMarkBps": 0.4612541947217107,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "chênh lệch thô 0.96 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.68 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -3.312e-05,
      "rateShort": -4.33e-06,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.8637,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.2879,
      "phiBps": 29.0,
      "netBps": -28.7121,
      "netAprPct": -314.397495,
      "lechMarkBps": 1.445156717754901,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "chênh lệch thô 0.86 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.71 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 6.088e-05,
      "rateShort": 8.88185384945e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.838156154835,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.279385384945,
      "phiBps": 29.0,
      "netBps": -28.720614615055,
      "netAprPct": -314.4907300348523,
      "lechMarkBps": 0.24029027064854416,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 11.42588671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "BTC",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 6.136e-05,
      "rateShort": 8.81e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.8022000000000001,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.2674,
      "phiBps": 29.0,
      "netBps": -28.7326,
      "netAprPct": -314.62197000000003,
      "lechMarkBps": 0.15766592221034859,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "chênh lệch thô 0.80 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.73 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 0.0,
      "rateShort": 2.015e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.6044999999999999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.20149999999999998,
      "phiBps": 29.0,
      "netBps": -28.7985,
      "netAprPct": -315.34357500000004,
      "lechMarkBps": 2.0617026603182946,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
        "chênh lệch thô 0.60 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.80 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 8.81e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.35700000000000015,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.11900000000000005,
      "phiBps": 29.0,
      "netBps": -28.881,
      "netAprPct": -316.24694999999997,
      "lechMarkBps": 0.4780108073436668,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 11.51188671875,
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
        "chênh lệch thô 0.36 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.88 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "POL",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 5e-05,
      "rateShort": 5e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 2,
      "thuBps": 0.0,
      "phiBps": 29.0,
      "netBps": -29.0,
      "netAprPct": -317.55,
      "lechMarkBps": 0.3759327832175771,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 0.41188671875,
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
      "luc": "2026-08-28T13:44:19Z"
    },
    {
      "ma": "POL",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 5e-05,
      "rateShort": 5e-05,
      "intervalLongGio": 4.0,
      "intervalShortGio": 4.0,
      "grossBpsNgay": 0.0,
      "giuGio": 8.0,
      "soMocLong": 2,
      "soMocShort": 2,
      "thuBps": 0.0,
      "phiBps": 29.0,
      "netBps": -29.0,
      "netAprPct": -317.55,
      "lechMarkBps": 0.0,
      "choMocDauGiay": 8140.58811328125,
      "tuoiXauNhatGiay": 10.56288671875,
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
      "luc": "2026-08-28T13:44:19Z"
    }
  ],
  "toTrinh": [
    {
      "ma": "5ea0dfe945944951",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 5087676.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 43.09602739726027,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 41.34628053016347,
      "netMoiGioBps": 0.05742538962522704,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6687598141710083,
        "giaoThuc": 0.3134573685183911,
        "cang": 0.3134573685183911,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6687598141710083
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 5.24% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $5.1M · dùng vốn 91%",
        "rút ra được $5.1M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 29.2 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "dda033735b164c52",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 34332999.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 42.47449315068493,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 40.724746283588125,
      "netMoiGioBps": 0.05656214761609462,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6594471555074096,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6594471555074096
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 5.17% (thưởng 0.11% KHÔNG tính vào NET)",
        "TVL $34.3M · dùng vốn 91%",
        "rút ra được $34.3M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 29.7 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "62c33d62e88b4397",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 23093105.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 28.059287671232873,
      "phiUocBps": 0.0389532,
      "netUocBps": 28.02033447123287,
      "netMoiGioBps": 0.038917131210045655,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.55057015134176,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.55057015134176
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 3.41% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $23.1M · dùng vốn 87%",
        "rút ra được $23.1M",
        "gas khứ hồi 0.0 bps trên $500 · hoà gas sau 1.0 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "5468c211d923400c",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 247170922.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.970657534246573,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 25.220910667149774,
      "netMoiGioBps": 0.035029042593263574,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6915446201245079,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6915446201245079
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 3.28% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $247.3M · dùng vốn 92%",
        "rút ra được $247.2M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 46.7 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "9185bbbd6fad4b1a",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 206073815.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.582136986301368,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 24.832390119204568,
      "netMoiGioBps": 0.03448943072111746,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.6697016504670684,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.6697016504670684
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 3.23% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $206.2M · dùng vốn 91%",
        "rút ra được $206.1M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 47.4 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "01b2564bd63e4960",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 30946780.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 26.45243835616438,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 24.70269148906758,
      "netMoiGioBps": 0.03430929373481608,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.3036449097386165,
        "giaoThuc": 0.17149991749762206,
        "cang": 0.17149991749762206,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.3036449097386165
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 3.22% (thưởng 4.04% KHÔNG tính vào NET)",
        "TVL $30.9M · dùng vốn 78%",
        "rút ra được $30.9M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 47.6 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "fad511ca79cb4bda",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 7675529.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 25.388383561643835,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 23.638636694547035,
      "netMoiGioBps": 0.03283143985353755,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.5744721155558481,
        "giaoThuc": 0.3134573685183911,
        "cang": 0.3134573685183911,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.5744721155558481
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "TVL $7.7M · dùng vốn 88%",
        "rút ra được $7.7M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 49.6 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "02a8c89efc084889",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 11879280.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 23.5946301369863,
      "phiUocBps": 0.07810961341818919,
      "netUocBps": 23.51652052356811,
      "netMoiGioBps": 0.03266183406051126,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.039246774583181966,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 2.87% (thưởng 0.00% KHÔNG tính vào NET)",
        "TVL $11.9M · dùng vốn 60%",
        "rút ra được $11.9M",
        "gas khứ hồi 0.1 bps trên $500 · hoà gas sau 2.4 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "1c551a24879e4c66",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 27873687.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 25.042191780821916,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 23.292444913725117,
      "netMoiGioBps": 0.032350617935729326,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.47979005482423637,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.47979005482423637
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "APY gốc 3.05% (thưởng 0.12% KHÔNG tính vào NET)",
        "TVL $27.9M · dùng vốn 85%",
        "rút ra được $27.9M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 50.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "08a6462438214925",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 19577165.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 24.30098630136986,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 22.55123943427306,
      "netMoiGioBps": 0.03132116588093481,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.49501680859837355,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.49501680859837355
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "TVL $19.6M · dùng vốn 85%",
        "rút ra được $19.6M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 51.8 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "1e588f6646ca4b9a",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 61205936.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 21.522986301369862,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 19.773239434273062,
      "netMoiGioBps": 0.027462832547601474,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.4505479291701952,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.4505479291701952
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "TVL $61.2M · dùng vốn 84%",
        "rút ra được $61.2M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 58.5 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "fc60017b59fc4338",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 42759694.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 18.96394520547945,
      "phiUocBps": 0.1306620172,
      "netUocBps": 18.833283188279452,
      "netMoiGioBps": 0.026157337761499238,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.2698332413578496,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.2698332413578496
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "TVL $42.8M · dùng vốn 76%",
        "rút ra được $42.8M",
        "gas khứ hồi 0.1 bps trên $500 · hoà gas sau 5.0 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "72cbac283d7c4540",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 116940871.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 17.822876712328767,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 16.073129845231968,
      "netMoiGioBps": 0.022323791451711067,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.07894570718110658,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 70.7 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "58e9828fc1e14125",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "thanhKhoanThoatUsd": 312691701.0,
      "gioVonBiGiu": 720.0,
      "raDuocKhong": true,
      "grossBps": 16.726520547945203,
      "phiUocBps": 1.7497468670968,
      "netUocBps": 14.976773680848403,
      "netMoiGioBps": 0.020801074556733894,
      "giuGio": 720.0,
      "ruiRo": {
        "thiTruong": 0.1,
        "thanhKhoan": 0.05741576809638985,
        "giaoThuc": 0.15,
        "cang": 0.15,
        "thucThi": 0.1,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.15
      },
      "tuoiDuLieuGiay": 27.41293896484375,
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
        "TVL $312.7M · dùng vốn 62%",
        "rút ra được $312.7M",
        "gas khứ hồi 1.7 bps trên $500 · hoà gas sau 75.3 giờ"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "84fe9f74148640dc",
      "luc": "2026-08-28T13:44:19.444Z",
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
      "sucChuaToiDaUsd": 45861.14,
      "khoaVonDenGiay": 2482.2612654008335,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2482.2683634608334,
      "raDuocKhong": null,
      "grossBps": 504.8783668376067,
      "phiUocBps": 0.0,
      "netUocBps": 504.8783668376067,
      "netMoiGioBps": 0.2033939497716895,
      "giuGio": 2482.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.574957275390624,
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
        "lãi CỐ ĐỊNH 17.82%/năm tới đáo hạn",
        "đáo hạn 2026-12-10, còn 103 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.6M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "1683838ecb294775",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 1642.261265123611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1642.2683634608331,
      "raDuocKhong": null,
      "grossBps": 262.8422394685442,
      "phiUocBps": 0.0,
      "netUocBps": 262.8422394685442,
      "netMoiGioBps": 0.16004828767123286,
      "giuGio": 1642.2683634608331,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "đáo hạn 2026-11-05, còn 68 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $17.7M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "927d1c96df2d4e85",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 2650.2612651236113,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2650.2683634608334,
      "raDuocKhong": null,
      "grossBps": 417.3044190601987,
      "phiUocBps": 0.0,
      "netUocBps": 417.3044190601987,
      "netMoiGioBps": 0.15745742009132419,
      "giuGio": 2650.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "đáo hạn 2026-12-17, còn 110 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $6.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "fd37b7d78f9b408f",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 2146.2612651236113,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2146.2683634608334,
      "raDuocKhong": null,
      "grossBps": 286.3888871283422,
      "phiUocBps": 0.0,
      "netUocBps": 286.3888871283422,
      "netMoiGioBps": 0.1334357305936073,
      "giuGio": 2146.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "lãi CỐ ĐỊNH 11.69%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 89 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $7.1M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "a9261478085a45e7",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 2482.2612651236113,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2482.2683634608334,
      "raDuocKhong": null,
      "grossBps": 312.95736783872474,
      "phiUocBps": 0.0,
      "netUocBps": 312.95736783872474,
      "netMoiGioBps": 0.12607716894977167,
      "giuGio": 2482.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "lãi CỐ ĐỊNH 11.04%/năm tới đáo hạn",
        "đáo hạn 2026-12-10, còn 103 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $10.2M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "489eb313035740f6",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 1138.261265123611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1138.2683634608334,
      "raDuocKhong": null,
      "grossBps": 135.6888655259416,
      "phiUocBps": 0.0,
      "netUocBps": 135.3370831719416,
      "netMoiGioBps": 0.11889734224050444,
      "giuGio": 1138.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "lãi CỐ ĐỊNH 10.44%/năm tới đáo hạn",
        "đáo hạn 2026-10-15, còn 47 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $12.0M",
        "phí vào+ra $0.04 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "3bf86cf6fc364b07",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 1138.261265123611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1138.2683634608334,
      "raDuocKhong": null,
      "grossBps": 100.39695886828717,
      "phiUocBps": 0.0,
      "netUocBps": 100.04517651428718,
      "netMoiGioBps": 0.08789243356470534,
      "giuGio": 1138.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "lãi CỐ ĐỊNH 7.73%/năm tới đáo hạn",
        "đáo hạn 2026-10-15, còn 47 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $50.3M",
        "phí vào+ra $0.04 đã TRỪ (Router đo) — trượt giá AMM Pendle thì chưa, xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "82105e130e71494a",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 1306.261265123611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1306.2683634608331,
      "raDuocKhong": null,
      "grossBps": 113.57943773334709,
      "phiUocBps": 0.0,
      "netUocBps": 113.57943773334709,
      "netMoiGioBps": 0.08694954337899544,
      "giuGio": 1306.2683634608331,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "lãi CỐ ĐỊNH 7.62%/năm tới đáo hạn",
        "đáo hạn 2026-10-22, còn 54 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $10.4M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "e2f3439d12304ab5",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "khoaVonDenGiay": 3322.2612651236113,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 3322.2683634608334,
      "raDuocKhong": null,
      "grossBps": 232.95320999682448,
      "phiUocBps": 0.0,
      "netUocBps": 232.95320999682448,
      "netMoiGioBps": 0.07011872146118722,
      "giuGio": 3322.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "lãi CỐ ĐỊNH 6.14%/năm tới đáo hạn",
        "đáo hạn 2027-01-14, còn 138 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $5.7M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "ef72d9d56dd04d76",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "sucChuaToiDaUsd": 34496.93,
      "khoaVonDenGiay": 2146.2612651236113,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2146.2683634608334,
      "raDuocKhong": null,
      "grossBps": 118.28878776317768,
      "phiUocBps": 0.0,
      "netUocBps": 118.28878776317768,
      "netMoiGioBps": 0.05511369863013699,
      "giuGio": 2146.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.574957275390624,
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
        "lãi CỐ ĐỊNH 4.83%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 89 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.4M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "802461323d6e4b0f",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "sucChuaToiDaUsd": 34880.48,
      "khoaVonDenGiay": 2146.2612651236113,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 2146.2683634608334,
      "raDuocKhong": null,
      "grossBps": 114.85916852211321,
      "phiUocBps": 0.0,
      "netUocBps": 114.85916852211321,
      "netMoiGioBps": 0.05351575342465753,
      "giuGio": 2146.2683634608334,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.574957275390624,
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
        "lãi CỐ ĐỊNH 4.69%/năm tới đáo hạn",
        "đáo hạn 2026-11-26, còn 89 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $3.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "7a24fe0f054d4def",
      "luc": "2026-08-28T13:44:19.445Z",
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
      "sucChuaToiDaUsd": 45197.46,
      "khoaVonDenGiay": 1306.261265123611,
      "vonToiThieuKinhTeUsd": 1000.0,
      "thanhKhoanThoatUsd": null,
      "gioVonBiGiu": 1306.2683634608331,
      "raDuocKhong": null,
      "grossBps": 67.37168554985102,
      "phiUocBps": 0.0,
      "netUocBps": 67.37168554985102,
      "netMoiGioBps": 0.05157568493150686,
      "giuGio": 1306.2683634608331,
      "ruiRo": {
        "thiTruong": 0.15,
        "thanhKhoan": 0.45,
        "giaoThuc": 0.21270283839385284,
        "cang": 0.21270283839385284,
        "thucThi": 0.15,
        "cauNoi": 0.0,
        "chuaDo": [],
        "caoNhat": 0.45
      },
      "tuoiDuLieuGiay": 25.57595458984375,
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
        "lãi CỐ ĐỊNH 4.52%/năm tới đáo hạn",
        "đáo hạn 2026-10-22, còn 54 ngày — vốn KHOÁ hết ngần ấy",
        "TVL $4.5M",
        "gas và trượt giá AMM CHƯA trừ — xem phiConThieu"
      ],
      "hopLe": true,
      "loiKhuon": []
    },
    {
      "ma": "46671e00e2c54c0e",
      "luc": "2026-08-28T13:44:19.446Z",
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
          "vonUsd": 500.0,
          "loai": "lp",
          "chuoi": "Polygon"
        }
      ],
      "vonCanUsd": 500.0,
      "sucChuaToiDaUsd": 2288.944,
      "khoaVonDenGiay": 0.0,
      "vonToiThieuKinhTeUsd": 500.0,
      "thanhKhoanThoatUsd": 2288.944,
      "gioVonBiGiu": 168.0,
      "raDuocKhong": true,
      "grossBps": 104.74934246575343,
      "phiUocBps": 0.4205902260979418,
      "netUocBps": 104.32875223965549,
      "netMoiGioBps": 0.621004477616997,
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
      "tuoiDuLieuGiay": 21.537370849609374,
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
        "TVL $1,144,472 · khoi luong/ngay $17,126,105 · vong quay 14.964x",
        "muc phi SUY RA tu apyBase va khoi luong: 1.00 bps — hai con so KHOP nhau",
        "phi goc 54.62%/nam · thuong 0.00% KHONG tinh vao NET",
        "hoa von sau 1 gio",
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
      "soMau": 2479,
      "netTrungBinh": -26.09628631706333,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2183,
      "netTrungBinh": -27.110162378378377,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1829,
      "netTrungBinh": -26.128381178786224,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "SOL",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 675,
      "netTrungBinh": -26.848090972408773,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "okx"
    },
    {
      "soMau": 1656,
      "netTrungBinh": -26.662232014492755,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "DOGE",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2214,
      "netTrungBinh": -27.101508623306234,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 888,
      "netTrungBinh": -26.878916675675672,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    },
    {
      "soMau": 2370,
      "netTrungBinh": -26.37453888047638,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2129,
      "netTrungBinh": -26.378507098108063,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2105,
      "netTrungBinh": -25.995923393535836,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "SOL",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2275,
      "netTrungBinh": -26.500582027756508,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 2299,
      "netTrungBinh": -26.36822507525011,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": true,
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    }
  ],
  "so": {
    "soLuot": 11705,
    "luotDauMs": 1787329908021,
    "luotCuoiMs": 1787924659432,
    "soCoHoi": 362293,
    "soDuyet": 156,
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
        "coHoiTho": 14,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      },
      {
        "ho": "phai-sinh",
        "coHoiTho": 1602,
        "quaCongTy": 0,
        "quaRuiRoTong": 0,
        "daCapVon": 0,
        "vonDangGiuUsd": 0.0
      },
      {
        "ho": "thanh-khoan",
        "coHoiTho": 19726,
        "quaCongTy": 2,
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
        "coHoiTho": 286,
        "quaCongTy": 52,
        "quaRuiRoTong": 4,
        "daCapVon": 4,
        "vonDangGiuUsd": 0.0
      }
    ],
    "navUsd": 1000.0,
    "vonNgoaiDayDu": true,
    "hienPhap": {
      "soDieu": 31,
      "soCanhDuoc": 25,
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
      "loiNhac": "QUET_DUOC nghĩa là quét được NGAY, chỉ chưa thực thi được — mà cả runtime đang moPhong=True, nên KHÔNG ty nào đang thực thi gì cả. «Chưa thực thi được» không phải lý do để không dựng. Cái phân biệt QUET_DUOC với CHAN là dữ liệu công khai không cần khoá."
    },
    "loiNhac": "CHÍN ty, năm họ. Trang này là cửa sổ nhìn vào ty chênh funding; tám ty còn lại chỉ hiện ở đây dưới dạng tổng hợp. Buồng lái đầy đủ chỉ sống ở localhost:5188 và không bao giờ lên site — trang công khai bấm được nút đặt lệnh là khoá đã ra tới trình duyệt."
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi sàn nào và không đặt được lệnh nào."
};
