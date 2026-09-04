/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime (lp_v3) — ĐỪNG SỬA TAY.
   Lát cắt bể thanh khoản V3: phiên Mỹ, dải đề xuất, quyết định từng pool,
   vị thế đang giữ, bài học tích luỹ. Trang tĩnh chỉ đọc; không nút nào.

   Sinh bằng tay:  cd thi-bac-ty-runtime && python -m bac.snapshot
   SINH RỒI PHẢI COMMIT thì site mới đổi.
*/
window.BE_THANH_KHOAN = {
  "date": "04/09/2026",
  "tomTat": "9 pool · CHO 9",
  "generatedAt": "2026-09-04T20:44:03.288Z",
  "luc": "2026-09-05T03:44:03.288734+07:00",
  "lucVn": "03:44 05/09/2026",
  "phien": {
    "luc": "2026-09-05T03:44:03.288734+07:00",
    "trangThai": "CUOI_TUAN",
    "phienKe": [
      "2026-09-08T20:30:00+07:00",
      "2026-09-09T03:00:00+07:00"
    ],
    "gioToiMo": 88.76575312944445,
    "gioToiDong": null,
    "lichConHan": true,
    "suKien": [
      {
        "luc": "2026-09-07T14:00:00+07:00",
        "loai": "het-thuong",
        "ten": "chương trình thưởng kết thúc",
        "ma": ""
      },
      {
        "luc": "2026-09-08T20:30:00+07:00",
        "loai": "mo-cua",
        "ten": "sàn Mỹ mở cửa",
        "ma": ""
      },
      {
        "luc": "2026-09-09T03:00:00+07:00",
        "loai": "dong-cua",
        "ten": "sàn Mỹ đóng cửa",
        "ma": ""
      }
    ]
  },
  "thuong": {
    "ten": "$220K Rewards for X Layer Liquidity Providers",
    "ketThuc": "2026-09-07 14:00",
    "conGio": 58.26575312944444,
    "luat": "thưởng chia theo GIỜ theo tỉ lệ phí; đổi vị thế lúc chụp ngẫu nhiên là mất thưởng giờ ấy; phải thêm thanh khoản qua trang OKX, không qua Uniswap",
    "quyMoiGioUsd": 654.7619047619048,
    "thuongMoiGioSuyTuApyUsd": 311.46591904109584,
    "kiemCheo": "APY hiển thị của 9 pool đang theo suy ra $311/giờ thưởng, quỹ là $655/giờ → 48% quỹ nằm ở các pool này (phần còn lại ở pool khác, hoặc APY hiển thị KHÔNG phải toàn thưởng)"
  },
  "nguonMu": [
    "giá gốc Stooq: chưa hỏi lần nào (chạy `python run.py` hoặc `python -m lp_v3.hom_nay --moi`)",
    "RPC X Layer: chưa hỏi lần nào (chạy `python run.py` hoặc `python -m lp_v3.hom_nay --moi`)",
    "tin RSS: chưa hỏi lần nào (chạy `python run.py` hoặc `python -m lp_v3.hom_nay --moi`)"
  ],
  "thieuDiaChi": [
    "SPCXx-USDG",
    "NVDAx-USDG",
    "SPYx-USDG",
    "ICEx-USDG",
    "MRNAx-USDG",
    "SMCIx-USDG",
    "RDDTx-USDG",
    "IRENx-USDG",
    "CRWVx-USDG"
  ],
  "thieuKhoiLuong": [
    "SPCXx-USDG",
    "NVDAx-USDG",
    "SPYx-USDG",
    "ICEx-USDG",
    "MRNAx-USDG",
    "SMCIx-USDG",
    "RDDTx-USDG",
    "IRENx-USDG",
    "CRWVx-USDG"
  ],
  "giaDinh": [
    "phần thưởng trong APY hiển thị = 90% (GIẢ ĐỊNH; khai `khoiLuongNgayUsd` để tách thật)",
    "pool tập trung NHƯ TA: phí vị thế = APR pool, không nhân hiệu suất (thận trọng; dán địa chỉ pool để đọc L thật)",
    "P(văng) là CẬN TRÊN; τ đếm theo ngày giao dịch Mỹ, phần trôi ngoài giờ trên chuỗi CHƯA đo"
  ],
  "tomTatHanhDong": {
    "CHO": [
      "SPCXx-USDG",
      "NVDAx-USDG",
      "SPYx-USDG",
      "ICEx-USDG",
      "MRNAx-USDG",
      "SMCIx-USDG",
      "RDDTx-USDG",
      "IRENx-USDG",
      "CRWVx-USDG"
    ]
  },
  "pool": [
    {
      "kyHieu": "SPCXx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 381440.0,
      "apyHienThi": 268.91,
      "aprPhi": 0.26891,
      "aprThuong": 2.4201900000000003,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 10000.0,
      "sucChuaUsd": 95360.0,
      "bienDong": {
        "ma": "SPCXx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "NVDAx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 644990.0,
      "apyHienThi": 183.94,
      "aprPhi": 0.18393999999999996,
      "aprThuong": 1.65546,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 10000.0,
      "sucChuaUsd": 161247.5,
      "bienDong": {
        "ma": "NVDAx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "SPYx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 637990.0,
      "apyHienThi": 48.55,
      "aprPhi": 0.04854999999999999,
      "aprThuong": 0.43695,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 10000.0,
      "sucChuaUsd": 159497.5,
      "bienDong": {
        "ma": "SPYx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "ICEx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 31670.0,
      "apyHienThi": 423.08,
      "aprPhi": 0.42307999999999985,
      "aprThuong": 3.8077199999999998,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 3958.75,
      "sucChuaUsd": 7917.5,
      "bienDong": {
        "ma": "ICEx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "MRNAx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 35490.0,
      "apyHienThi": 406.04,
      "aprPhi": 0.40603999999999996,
      "aprThuong": 3.6543600000000005,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 4436.25,
      "sucChuaUsd": 8872.5,
      "bienDong": {
        "ma": "MRNAx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "SMCIx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 14810.0,
      "apyHienThi": 386.14,
      "aprPhi": 0.38613999999999987,
      "aprThuong": 3.47526,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 1851.25,
      "sucChuaUsd": 3702.5,
      "bienDong": {
        "ma": "SMCIx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "RDDTx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 16730.0,
      "apyHienThi": 335.27,
      "aprPhi": 0.3352699999999999,
      "aprThuong": 3.01743,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 2091.25,
      "sucChuaUsd": 4182.5,
      "bienDong": {
        "ma": "RDDTx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "IRENx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 18200.0,
      "apyHienThi": 319.67,
      "aprPhi": 0.31966999999999995,
      "aprThuong": 2.8770300000000004,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 2275.0,
      "sucChuaUsd": 4550.0,
      "bienDong": {
        "ma": "IRENx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    },
    {
      "kyHieu": "CRWVx-USDG",
      "hanhDong": "CHO",
      "luat": "khong-sigma",
      "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày",
      "biChan": true,
      "gia": null,
      "nguonGia": null,
      "tuoiGiaGio": null,
      "sigma": null,
      "soPhien": 0,
      "nguonSigma": null,
      "tvlUsd": 19900.0,
      "apyHienThi": 302.42,
      "aprPhi": 0.3024199999999999,
      "aprThuong": 2.72178,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 2487.5,
      "sucChuaUsd": 4975.0,
      "bienDong": {
        "ma": "CRWVx",
        "soPhien": 0,
        "sigma10": null,
        "sigma60": null
      },
      "thieu": [
        "sigma",
        "gia"
      ],
      "tin": [],
      "luatKhop": [
        {
          "ma": "khong-sigma",
          "hanhDong": "CHO",
          "lyDo": "σ chưa đo được: có 0 phiên, cần ≥ 10 — chưa có sàn gốc hoặc băng giá chưa đủ dày"
        },
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ]
    }
  ],
  "viThe": [],
  "baiHoc": {
    "luc": "2026-09-04T20:44:03Z",
    "soCap": 0,
    "duMau": [],
    "soChuaDuMau": 0,
    "moHinh": {}
  },
  "kinhNghiem": {
    "soQuyetDinh": 0,
    "soKetCuc": 0,
    "soChuaCham": 0
  },
  "tienHoa": null,
  "nut": {
    "heSoDai": 1.5,
    "giuGio": 72.0,
    "tiLePhiTrenLvrToiThieu": 1.5,
    "xacSuatVangToiDa": 0.6,
    "gioTruocSuKien": 24.0
  }
};
