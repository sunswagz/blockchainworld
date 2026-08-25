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
  "generatedAt": "2026-08-25T17:38:42.769Z",
  "maChienLuoc": "perpetual.funding_spread.v1",
  "che": "quan-sat",
  "cheKhai": "quan-sat",
  "vong": 1,
  "chayDuocGiay": 0.9602034091949463,
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
      "tuoiGiay": 0.012108154296875,
      "treTrungBinhMs": 359.75249999319203,
      "songSot": true
    },
    {
      "ten": "binance",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.02307861328125,
      "treTrungBinhMs": 347.2107999987202,
      "songSot": true
    },
    {
      "ten": "okx",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.051498779296875,
      "treTrungBinhMs": 317.3518999974476,
      "songSot": true
    },
    {
      "ten": "bybit",
      "tongLuot": 1,
      "soLoi": 0,
      "loiCuoi": null,
      "tuoiGiay": 0.09446142578125,
      "treTrungBinhMs": 274.0321000019321,
      "songSot": true
    }
  ],
  "dongHo": {
    "lechMs": 447272.13623046875,
    "lechGiay": 447.27213623046873,
    "daDo": true,
    "dangKeu": true,
    "nguongKeuMs": 5000.0,
    "theoSan": {
      "bybit": 447261.5119628906,
      "binance": 447272.13623046875,
      "okx": 447283.22509765625
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
      "markPx": 79154.0,
      "mocKeMs": 1787680800000,
      "oiUsd": 2868012203.3646,
      "tuoiGiay": 0.01267236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": "mốc kế suy từ quy ước kết toán hàng giờ"
    },
    {
      "san": "hyperliquid",
      "ma": "ETH",
      "rate": 1.00356e-05,
      "intervalGio": 1.0,
      "moiGio": 1.00356e-05,
      "moiNgayBps": 2.408544,
      "markPx": 2467.8,
      "mocKeMs": 1787680800000,
      "oiUsd": 1721268900.3337197,
      "tuoiGiay": 0.01267236328125,
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
      "markPx": 98.082,
      "mocKeMs": 1787680800000,
      "oiUsd": 474953047.7245201,
      "tuoiGiay": 0.01267236328125,
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
      "markPx": 0.088676,
      "mocKeMs": 1787680800000,
      "oiUsd": 66055281.61836801,
      "tuoiGiay": 0.01267236328125,
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
      "markPx": 1.474101,
      "mocKeMs": 1787680800000,
      "oiUsd": 246854150.43001202,
      "tuoiGiay": 0.01267236328125,
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
      "markPx": 79150.0,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.03667236328125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "ETH",
      "rate": 5.548e-05,
      "intervalGio": 8.0,
      "moiGio": 6.935e-06,
      "moiNgayBps": 1.6643999999999999,
      "markPx": 2467.66,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.03667236328125,
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
      "markPx": 98.05147851,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.03667236328125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "binance",
      "ma": "XRP",
      "rate": 5.322e-05,
      "intervalGio": 8.0,
      "moiGio": 6.6525e-06,
      "moiNgayBps": 1.5966,
      "markPx": 1.47402943,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.03667236328125,
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
      "markPx": 0.0886606,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 1.03667236328125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "BTC",
      "rate": 4.03526625404e-05,
      "intervalGio": 8.0,
      "moiGio": 5.04408281755e-06,
      "moiNgayBps": 1.2105798762120001,
      "markPx": 79138.4,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 8.63467236328125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "ETH",
      "rate": 6.06877860007e-05,
      "intervalGio": 8.0,
      "moiGio": 7.5859732500875e-06,
      "moiNgayBps": 1.8206335800210003,
      "markPx": 2467.65,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 8.56867236328125,
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
      "markPx": 98.01,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 7.27467236328125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "XRP",
      "rate": 5.23778981729e-05,
      "intervalGio": 8.0,
      "moiGio": 6.5472372716125e-06,
      "moiNgayBps": 1.5713369451869998,
      "markPx": 1.4737,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 8.27267236328125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "okx",
      "ma": "DOGE",
      "rate": 2.49532924128e-05,
      "intervalGio": 8.0,
      "moiGio": 3.1191615516e-06,
      "moiNgayBps": 0.748598772384,
      "markPx": 0.08863,
      "mocKeMs": 1787702400000,
      "oiUsd": null,
      "tuoiGiay": 7.70367236328125,
      "nguonTuSan": true,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "BTC",
      "rate": 1.183e-05,
      "intervalGio": 8.0,
      "moiGio": 1.47875e-06,
      "moiNgayBps": 0.3549,
      "markPx": 79134.07,
      "mocKeMs": 1787702400000,
      "oiUsd": 3818139743.43,
      "tuoiGiay": 0.10367236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "DOGE",
      "rate": 5.44e-05,
      "intervalGio": 8.0,
      "moiGio": 6.8e-06,
      "moiNgayBps": 1.6320000000000001,
      "markPx": 0.08863,
      "mocKeMs": 1787702400000,
      "oiUsd": 134490027.67,
      "tuoiGiay": 0.10367236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "ETH",
      "rate": -5.202e-05,
      "intervalGio": 8.0,
      "moiGio": -6.5025e-06,
      "moiNgayBps": -1.5606,
      "markPx": 2467.42,
      "mocKeMs": 1787702400000,
      "oiUsd": 1922219271.59,
      "tuoiGiay": 0.10367236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "SOL",
      "rate": -2.975e-05,
      "intervalGio": 8.0,
      "moiGio": -3.71875e-06,
      "moiNgayBps": -0.8925,
      "markPx": 98.021,
      "mocKeMs": 1787702400000,
      "oiUsd": 658848700.42,
      "tuoiGiay": 0.10367236328125,
      "nguonTuSan": false,
      "intervalSuyRa": false,
      "ghiChu": ""
    },
    {
      "san": "bybit",
      "ma": "XRP",
      "rate": 7.363e-05,
      "intervalGio": 8.0,
      "moiGio": 9.20375e-06,
      "moiNgayBps": 2.2089,
      "markPx": 1.4737,
      "mocKeMs": 1787702400000,
      "oiUsd": 344644072.28,
      "tuoiGiay": 0.10367236328125,
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
      "rateLong": 2.49532924128e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.2514012276160003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.750467075872,
      "phiBps": 27.0,
      "netBps": -26.249532924128,
      "netAprPct": -287.43238551920166,
      "lechMarkBps": 5.1887696975854585,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 7.69468994140625,
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
        "chênh lệch thô 2.25 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.25 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 4.03526625404e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.7894201237880003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.596473374596,
      "phiBps": 27.0,
      "netBps": -26.403526625403998,
      "netAprPct": -289.11861654817375,
      "lechMarkBps": 1.9710358804346666,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 8.62568994140625,
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
        "chênh lệch thô 1.79 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.40 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 5.23778981729e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.4286630548130002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.47622101827100005,
      "phiBps": 27.0,
      "netBps": -26.523778981729,
      "netAprPct": -290.43537984993253,
      "lechMarkBps": 2.7206721213548386,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 8.26368994140625,
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
        "chênh lệch thô 1.43 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.52 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 5.322e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.4034,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.46780000000000005,
      "phiBps": 27.0,
      "netBps": -26.5322,
      "netAprPct": -290.52759,
      "lechMarkBps": 0.4855280436152262,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 1.02768994140625,
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
        "chênh lệch thô 1.40 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.53 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -5.202e-05,
      "rateShort": 1.00356e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.9691439999999996,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.323048,
      "phiBps": 28.0,
      "netBps": -26.676952,
      "netAprPct": -292.11262439999996,
      "lechMarkBps": 1.5399516130997568,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 0.09468994140625,
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
        "NET sau phí -26.68 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": -2.975e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 3.8925000000000005,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 1.2975,
      "phiBps": 28.0,
      "netBps": -26.7025,
      "netAprPct": -292.392375,
      "lechMarkBps": 6.221220481072991,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 0.09468994140625,
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
        "NET sau phí -26.70 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid",
      "rateLong": 5.548e-05,
      "rateShort": 1.00356e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.7441439999999999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.24804799999999996,
      "phiBps": 27.0,
      "netBps": -26.751952,
      "netAprPct": -292.9338744,
      "lechMarkBps": 0.5673230053544246,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 1.02768994140625,
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
        "NET sau phí -26.75 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid",
      "rateLong": 6.06877860007e-05,
      "rateShort": 1.00356e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.5879104199789997,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.19597013999299992,
      "phiBps": 27.0,
      "netBps": -26.804029860007,
      "netAprPct": -293.5041269670767,
      "lechMarkBps": 0.6078473087564089,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 8.55968994140625,
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
        "chênh lệch thô 0.59 bps/ngày < ngưỡng 3.00",
        "NET sau phí -26.80 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
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
      "lechMarkBps": 0.5053567818880129,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 1.02768994140625,
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
      "luc": "2026-08-25T17:38:42Z"
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
      "lechMarkBps": 3.1123182265328553,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 1.02768994140625,
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
      "luc": "2026-08-25T17:38:42Z"
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
      "lechMarkBps": 7.343491830364168,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 7.26568994140625,
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
      "luc": "2026-08-25T17:38:42Z"
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
      "lechMarkBps": 1.7368101113925436,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 1.02768994140625,
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
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 1.183e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 2.6451000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.8817,
      "phiBps": 28.0,
      "netBps": -27.1183,
      "netAprPct": -296.94538500000004,
      "lechMarkBps": 2.518193569482907,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 0.09468994140625,
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
        "chênh lệch thô 2.65 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.12 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 2.49532924128e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.2514012276160003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.750467075872,
      "phiBps": 28.0,
      "netBps": -27.249532924128,
      "netAprPct": -298.3823855192016,
      "lechMarkBps": 3.45195966396477,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 7.69468994140625,
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
        "chênh lệch thô 2.25 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.25 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 4.03526625404e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.7894201237880003,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.596473374596,
      "phiBps": 28.0,
      "netBps": -27.403526625403998,
      "netAprPct": -300.0686165481738,
      "lechMarkBps": 1.4656791021964743,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 8.62568994140625,
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
        "chênh lệch thô 1.79 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.40 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 5.44e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 1.368,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.456,
      "phiBps": 28.0,
      "netBps": -27.544,
      "netAprPct": -301.6068,
      "lechMarkBps": 5.1887696975854585,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 0.09468994140625,
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
        "chênh lệch thô 1.37 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.54 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -2.975e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.8925000000000005,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.2975,
      "phiBps": 29.0,
      "netBps": -27.7025,
      "netAprPct": -303.342375,
      "lechMarkBps": 3.1089024050298044,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 1.02768994140625,
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
        "NET sau phí -27.70 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -2.975e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.8925000000000005,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.2975,
      "phiBps": 29.0,
      "netBps": -27.7025,
      "netAprPct": -303.342375,
      "lechMarkBps": 1.1222714774699594,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 7.26568994140625,
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
        "NET sau phí -27.70 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "XRP",
      "sanLong": "bybit",
      "sanShort": "hyperliquid",
      "rateLong": 7.363e-05,
      "rateShort": 1.25e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 1.0,
      "grossBpsNgay": 0.7911000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 8,
      "thuBps": 0.26370000000000005,
      "phiBps": 28.0,
      "netBps": -27.7363,
      "netAprPct": -303.7124850000001,
      "lechMarkBps": 2.7206721213548386,
      "choMocDauGiay": 829.9723100585937,
      "tuoiXauNhatGiay": 0.09468994140625,
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
        "chênh lệch thô 0.79 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.74 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": -5.202e-05,
      "rateShort": 6.06877860007e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.381233580021,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.127077860007,
      "phiBps": 29.0,
      "netBps": -27.872922139993,
      "netAprPct": -305.20849743292337,
      "lechMarkBps": 0.9321043065246013,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 8.55968994140625,
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
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": -5.202e-05,
      "rateShort": 5.548e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 3.2249999999999996,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 1.075,
      "phiBps": 29.0,
      "netBps": -27.925,
      "netAprPct": -305.77875000000006,
      "lechMarkBps": 0.9726286098696748,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 1.02768994140625,
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
        "NET sau phí -27.93 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "okx",
      "rateLong": 5.548e-05,
      "rateShort": 6.06877860007e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.15623358002100013,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.05207786000700004,
      "phiBps": 28.0,
      "netBps": -27.947922139993,
      "netAprPct": -306.02974743292333,
      "lechMarkBps": 0.04052430343692101,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 8.55968994140625,
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
        "chênh lệch thô 0.16 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.95 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "binance",
      "rateLong": 5.23778981729e-05,
      "rateShort": 5.322e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.025263054813000146,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.008421018271000048,
      "phiBps": 28.0,
      "netBps": -27.991578981729,
      "netAprPct": -306.50778984993246,
      "lechMarkBps": 2.235144085120967,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 8.26368994140625,
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
        "chênh lệch thô 0.03 bps/ngày < ngưỡng 3.00",
        "NET sau phí -27.99 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
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
      "lechMarkBps": 4.231173845593006,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 7.26568994140625,
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
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 1.183e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 2.6451000000000002,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.8817,
      "phiBps": 29.0,
      "netBps": -28.1183,
      "netAprPct": -307.895385,
      "lechMarkBps": 2.012836793998665,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 1.02768994140625,
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
        "chênh lệch thô 2.65 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.12 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "bybit",
      "sanShort": "binance",
      "rateLong": 5.44e-05,
      "rateShort": 0.0001,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 1.368,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.456,
      "phiBps": 29.0,
      "netBps": -28.544,
      "netAprPct": -312.5568,
      "lechMarkBps": 3.45195966396477,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 1.02768994140625,
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
        "chênh lệch thô 1.37 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.54 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 2.49532924128e-05,
      "rateShort": 5.44e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.8834012276159999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.294467075872,
      "phiBps": 29.0,
      "netBps": -28.705532924128,
      "netAprPct": -314.32558551920164,
      "lechMarkBps": 0.0,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 7.69468994140625,
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
        "chênh lệch thô 0.88 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.71 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "BTC",
      "sanLong": "bybit",
      "sanShort": "okx",
      "rateLong": 1.183e-05,
      "rateShort": 4.03526625404e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.855679876212,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.285226625404,
      "phiBps": 29.0,
      "netBps": -28.714773374596,
      "netAprPct": -314.4267684518262,
      "lechMarkBps": 0.5471576958377151,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 8.62568994140625,
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
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "bybit",
      "rateLong": 5.23778981729e-05,
      "rateShort": 7.363e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.6375630548129999,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.212521018271,
      "phiBps": 29.0,
      "netBps": -28.787478981729,
      "netAprPct": -315.2228948499325,
      "lechMarkBps": 0.0,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 8.26368994140625,
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
        "chênh lệch thô 0.64 bps/ngày < ngưỡng 3.00",
        "NET sau phí -28.79 bps < ngưỡng 0.50"
      ],
      "lyDoMa": [
        "gross-mong",
        "net-am"
      ],
      "luc": "2026-08-25T17:38:42Z"
    },
    {
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "bybit",
      "rateLong": 5.322e-05,
      "rateShort": 7.363e-05,
      "intervalLongGio": 8.0,
      "intervalShortGio": 8.0,
      "grossBpsNgay": 0.6122999999999998,
      "giuGio": 8.0,
      "soMocLong": 1,
      "soMocShort": 1,
      "thuBps": 0.20409999999999995,
      "phiBps": 29.0,
      "netBps": -28.7959,
      "netAprPct": -315.315105,
      "lechMarkBps": 2.235144085120967,
      "choMocDauGiay": 22429.972310058594,
      "tuoiXauNhatGiay": 1.02768994140625,
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
      "luc": "2026-08-25T17:38:42Z"
    }
  ],
  "toTrinh": [],
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
      "soMau": 1,
      "netTrungBinh": -26.249532924128,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "DOGE",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.403526625403998,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.523778981729,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.5322,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "XRP",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.676952,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.7025,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "bybit",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.751952,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "binance",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -26.804029860007,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "ETH",
      "sanLong": "okx",
      "sanShort": "hyperliquid"
    },
    {
      "soMau": 1,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "BTC",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    },
    {
      "soMau": 1,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "hyperliquid",
      "sanShort": "binance"
    },
    {
      "soMau": 1,
      "netTrungBinh": -27.0,
      "tiLeDuong": 0.0,
      "soGio": 24.0,
      "duMau": false,
      "ma": "SOL",
      "sanLong": "hyperliquid",
      "sanShort": "okx"
    },
    {
      "soMau": 1,
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
    "soLuot": 1,
    "luotDauMs": 1787679522756,
    "luotCuoiMs": 1787679522756,
    "soCoHoi": 30,
    "soDuyet": 0,
    "soLoiGhi": 0,
    "loiCuoi": null,
    "duong": "thi-bac-ty.sqlite3",
    "chuaCo": false
  },
  "loiVongCuoi": null,
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi sàn nào và không đặt được lệnh nào."
};
