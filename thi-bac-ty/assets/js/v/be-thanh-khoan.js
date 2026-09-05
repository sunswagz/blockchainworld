/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime (lp_v3) — ĐỪNG SỬA TAY.
   Lát cắt bể thanh khoản V3: phiên Mỹ, dải đề xuất, quyết định từng pool,
   vị thế đang giữ, bài học tích luỹ. Trang tĩnh chỉ đọc; không nút nào.

   Sinh bằng tay:  cd thi-bac-ty-runtime && python -m bac.snapshot
   SINH RỒI PHẢI COMMIT thì site mới đổi.
*/
window.BE_THANH_KHOAN = {
  "date": "05/09/2026",
  "tomTat": "9 pool · CHO 9",
  "generatedAt": "2026-09-05T09:52:46.375Z",
  "luc": "2026-09-05T16:52:46.371727+07:00",
  "lucVn": "16:52 05/09/2026",
  "phien": {
    "luc": "2026-09-05T16:52:46.371727+07:00",
    "trangThai": "CUOI_TUAN",
    "phienKe": [
      "2026-09-08T20:30:00+07:00",
      "2026-09-09T03:00:00+07:00"
    ],
    "gioToiMo": 75.62045229805555,
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
    "conGio": 45.12045229805556,
    "luat": "thưởng chia theo GIỜ theo tỉ lệ phí; đổi vị thế lúc chụp ngẫu nhiên là mất thưởng giờ ấy; phải thêm thanh khoản qua trang OKX, không qua Uniswap",
    "quyMoiGioUsd": 654.7619047619048,
    "thuongMoiGioSuyTuApyUsd": 311.46591904109584,
    "kiemCheo": "APY hiển thị của 9 pool đang theo suy ra $311/giờ thưởng, quỹ là $655/giờ → 48% quỹ nằm ở các pool này (phần còn lại ở pool khác, hoặc APY hiển thị KHÔNG phải toàn thưởng)"
  },
  "nguonMu": [
    "giá gốc Yahoo: tiến trình này chưa hỏi; tiến trình khác hỏi lần cuối 16:51 05/09",
    "RPC X Layer: chưa hỏi lần nào (chạy `python run.py` hoặc `python -m lp_v3.hom_nay --moi`)",
    "tin RSS: tiến trình này chưa hỏi; tiến trình khác hỏi lần cuối 16:44 05/09"
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
      "ICEx-USDG",
      "MRNAx-USDG",
      "SMCIx-USDG",
      "RDDTx-USDG",
      "IRENx-USDG",
      "CRWVx-USDG",
      "NVDAx-USDG",
      "SPYx-USDG",
      "SPCXx-USDG"
    ]
  },
  "pool": [
    {
      "kyHieu": "ICEx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 161.25999450683594,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 0.27935554847976396,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 31670.0,
      "apyHienThi": 423.08,
      "aprPhi": 0.42307999999999985,
      "aprThuong": 3.8077199999999998,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 3958.75,
      "sucChuaUsd": 7917.5,
      "bienDong": {
        "ma": "ICEx",
        "soPhien": 251,
        "doi1NgayPct": -2.0232103439740357,
        "doi5NgayPct": -0.6591556164290302,
        "sigma10": 0.2594498626146913,
        "sigma60": 0.2777357474652727,
        "tiLeNoCo": 0.9341608524741029,
        "trangThai": "ON"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 158.27795677194715,
        "Pb": 164.29821535928363,
        "rongPct": 1.8840511943083893,
        "hieuSuat": 107.6518948399661,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 34.77369863013697,
        "thuongBps": 196.12567265930525,
        "netBps": 230.6467663004937,
        "tiLePhiTrenLvr": 2.6751495489251296,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
    {
      "kyHieu": "MRNAx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 145.5500030517578,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 2.3230405560763203,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 35490.0,
      "apyHienThi": 406.04,
      "aprPhi": 0.40603999999999996,
      "aprThuong": 3.6543600000000005,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 4436.25,
      "sucChuaUsd": 8872.5,
      "bienDong": {
        "ma": "MRNAx",
        "soPhien": 251,
        "doi1NgayPct": -2.2301284169561897,
        "doi5NgayPct": 5.478655886399153,
        "sigma10": 0.9692260511440038,
        "sigma60": 2.308911719992542,
        "tiLeNoCo": 0.4197761407470072,
        "trangThai": "CO"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "phi-duoi-lvr",
          "hanhDong": "RUT",
          "lyDo": "phí/LVR 0.30 < 1.50"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 124.62447493968429,
        "Pb": 169.9891084686192,
        "rongPct": 16.790865616245163,
        "hieuSuat": 13.391846101194123,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 33.3731506849315,
        "thuongBps": 188.22650119737241,
        "netBps": 221.37423627227292,
        "tiLePhiTrenLvr": 0.2984534730348578,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
    {
      "kyHieu": "SMCIx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 39.59000015258789,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 0.9250167641593071,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 14810.0,
      "apyHienThi": 386.14,
      "aprPhi": 0.38613999999999987,
      "aprThuong": 3.47526,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 1851.25,
      "sucChuaUsd": 3702.5,
      "bienDong": {
        "ma": "SMCIx",
        "soPhien": 251,
        "doi1NgayPct": 4.541857061566912,
        "doi5NgayPct": 6.7691429276874215,
        "sigma10": 0.6552224882442312,
        "sigma60": 0.9349297806974908,
        "tiLeNoCo": 0.700825347284811,
        "trangThai": "CO"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "phi-duoi-lvr",
          "hanhDong": "RUT",
          "lyDo": "phí/LVR 0.73 < 1.50"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 37.217209775657835,
        "Pb": 42.11406823697613,
        "rongPct": 6.37551925905524,
        "hieuSuat": 32.86226881276529,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 31.73753424657533,
        "thuongBps": 179.00152983044373,
        "netBps": 210.19888851996302,
        "tiLePhiTrenLvr": 0.7294741265997816,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
    {
      "kyHieu": "RDDTx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 154.4600067138672,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 0.8886936791842536,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 16730.0,
      "apyHienThi": 335.27,
      "aprPhi": 0.3352699999999999,
      "aprThuong": 3.01743,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 2091.25,
      "sucChuaUsd": 4182.5,
      "bienDong": {
        "ma": "RDDTx",
        "soPhien": 251,
        "doi1NgayPct": -0.980831287530104,
        "doi5NgayPct": 0.9542527541615664,
        "sigma10": 0.6312944023974633,
        "sigma60": 0.8813448264347739,
        "tiLeNoCo": 0.7162853669331476,
        "trangThai": "CO"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "phi-duoi-lvr",
          "hanhDong": "RUT",
          "lyDo": "phí/LVR 0.66 < 1.50"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 145.55541344307213,
        "Pb": 163.90935321260935,
        "rongPct": 6.117665471973477,
        "hieuSuat": 34.18478754606567,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 27.556438356164374,
        "thuongBps": 155.41990704473216,
        "netBps": 182.49816249593536,
        "tiLePhiTrenLvr": 0.6596589788999616,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
    {
      "kyHieu": "IRENx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 44.68000030517578,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 1.1326034521959878,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 18200.0,
      "apyHienThi": 319.67,
      "aprPhi": 0.31966999999999995,
      "aprThuong": 2.8770300000000004,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 2275.0,
      "sucChuaUsd": 4550.0,
      "bienDong": {
        "ma": "IRENx",
        "soPhien": 251,
        "doi1NgayPct": 7.2749067666040945,
        "doi5NgayPct": 26.036669516480405,
        "sigma10": 1.047949554118179,
        "sigma60": 1.1402202320629566,
        "tiLeNoCo": 0.9190764421204525,
        "trangThai": "ON"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "phi-duoi-lvr",
          "hanhDong": "RUT",
          "lyDo": "phí/LVR 0.49 < 1.50"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 41.423598467309205,
        "Pb": 48.19239518377322,
        "rongPct": 7.86122393600468,
        "hieuSuat": 26.93187269388505,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 26.27424657534246,
        "thuongBps": 148.18827119930066,
        "netBps": 174.02295733508268,
        "tiLePhiTrenLvr": 0.49152025295169394,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
    {
      "kyHieu": "CRWVx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 89.36000061035156,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 1.0315112313588448,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 19900.0,
      "apyHienThi": 302.42,
      "aprPhi": 0.3024199999999999,
      "aprThuong": 2.72178,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 2487.5,
      "sucChuaUsd": 4975.0,
      "bienDong": {
        "ma": "CRWVx",
        "soPhien": 251,
        "doi1NgayPct": 5.676446535410284,
        "doi5NgayPct": 6.090463076059804,
        "sigma10": 0.4586336085740031,
        "sigma60": 1.0228829766843628,
        "tiLeNoCo": 0.44837348849097763,
        "trangThai": "CO"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "phi-duoi-lvr",
          "hanhDong": "RUT",
          "lyDo": "phí/LVR 0.51 < 1.50"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 83.40868314605896,
        "Pb": 95.73595227608304,
        "rongPct": 7.135129389192141,
        "hieuSuat": 29.52171136274584,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 24.85643835616437,
        "thuongBps": 140.19175079329463,
        "netBps": 164.64617909920776,
        "tiLePhiTrenLvr": 0.5114261243705345,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
    {
      "kyHieu": "NVDAx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 230.36000061035156,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 0.40478391465504043,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 644990.0,
      "apyHienThi": 183.94,
      "aprPhi": 0.18393999999999996,
      "aprThuong": 1.65546,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 10000.0,
      "sucChuaUsd": 161247.5,
      "bienDong": {
        "ma": "NVDAx",
        "soPhien": 251,
        "doi1NgayPct": 0.836070775935327,
        "doi5NgayPct": 5.88830033504808,
        "sigma10": 0.5643940259953025,
        "sigma60": 0.40391172562056343,
        "tiLeNoCo": 1.3973202316129265,
        "trangThai": "NO"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "phi-duoi-lvr",
          "hanhDong": "RUT",
          "lyDo": "phí/LVR 0.80 < 1.50"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 224.21323530131806,
        "Pb": 236.6752783790245,
        "rongPct": 2.7414819204463647,
        "hieuSuat": 74.44986352669783,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 15.118356164383556,
        "thuongBps": 85.26840368004304,
        "netBps": 100.2867598444266,
        "tiLePhiTrenLvr": 0.8009909981219314,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
    {
      "kyHieu": "SPYx-USDG",
      "hanhDong": "CHO",
      "luat": "ngoai-gio-khong-doi-dai",
      "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở",
      "biChan": true,
      "gia": 770.1900024414062,
      "nguonGia": "goc",
      "tuoiGiaGio": 12.879537032777778,
      "sigma": 0.12178776924982736,
      "soPhien": 59,
      "nguonSigma": "goc",
      "tvlUsd": 637990.0,
      "apyHienThi": 48.55,
      "aprPhi": 0.04854999999999999,
      "aprThuong": 0.43695,
      "nguonApr": "apy-hien-thi-gia-dinh",
      "vonXinUsd": 10000.0,
      "sucChuaUsd": 159497.5,
      "bienDong": {
        "ma": "SPYx",
        "soPhien": 251,
        "doi1NgayPct": -0.3854237146576178,
        "doi5NgayPct": 0.10918657075786875,
        "sigma10": 0.08189895513847728,
        "sigma60": 0.12561090095110167,
        "tiLeNoCo": 0.6520051565457623,
        "trangThai": "CO"
      },
      "thieu": [],
      "tin": [],
      "luatKhop": [
        {
          "ma": "ngoai-gio-khong-doi-dai",
          "hanhDong": "GIU",
          "lyDo": "phiên đang CUOI_TUAN: đợi sàn Mỹ mở"
        },
        {
          "ma": "phi-duoi-lvr",
          "hanhDong": "RUT",
          "lyDo": "phí/LVR 0.71 < 1.50"
        },
        {
          "ma": "vao-duoc",
          "hanhDong": "VAO",
          "lyDo": "đủ σ, phiên mở, không sự kiện, phí/LVR đủ, P(văng) trong trần: VÀO"
        },
        {
          "ma": "chua-du-so",
          "hanhDong": "CHO",
          "lyDo": "không luật nào khớp: CHỜ và khai thiếu gì"
        }
      ],
      "dai": {
        "Pa": 763.9481750877371,
        "Pb": 776.4828285538701,
        "rongPct": 0.8170485325071031,
        "hieuSuat": 246.28248350509884,
        "pVang": 0.0,
        "ilKyVongBps": 0.0,
        "lvrBps": 0.0,
        "phiBps": 3.9904109589041084,
        "thuongBps": 22.506148736903825,
        "netBps": 26.39655969580793,
        "tiLePhiTrenLvr": 0.7060089554134749,
        "giuGio": 72.0,
        "ghiChu": [
          "phi-KHONG-nhan-hieu-suat-gia-dinh-pool-tap-trung-nhu-ta",
          "thuong-het-sau-45h-trong-cua-so-72h"
        ]
      }
    },
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
    }
  ],
  "viThe": [],
  "baiHoc": {
    "luc": "2026-09-05T09:44:34Z",
    "soCap": 0,
    "duMau": [],
    "soChuaDuMau": 0,
    "moHinh": {}
  },
  "kinhNghiem": {
    "soQuyetDinh": 8,
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
