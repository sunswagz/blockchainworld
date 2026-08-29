/* SINH TỰ ĐỘNG bởi kham-thien-giam-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái Đài Chiêm, để trang tĩnh đọc được mà không cần server
   và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python -m kham.snapshot       ghi một lần rồi thoát
       nút "Ghi lát cắt" ở buồng lái localhost:5186

   Vòng lặp nền KHÔNG tự ghi file này. Trang công khai đọc bản ĐÃ COMMIT,
   nên ghi mỗi vòng cũng không làm site tươi hơn một giây nào — nó chỉ để
   lại một file được theo dõi luôn bẩn. SINH RỒI PHẢI COMMIT thì site mới
   đổi.
*/
window.DAI_CHIEM = {
  "date": "29/08/2026",
  "tomTat": "1 market đã kết toán · kỳ vọng -49.9483$/lệnh",
  "generatedAt": "2026-08-29T20:42:42.830Z",
  "che": "giay",
  "cheKhai": "giay",
  "vong": 1,
  "chayDuocGiay": 0.8890748023986816,
  "thiTruong": [
    {
      "ma": "BTC_5M",
      "theo": true,
      "dongCo": "updown-crypto",
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    },
    {
      "ma": "ETH_5M",
      "theo": true,
      "dongCo": "updown-crypto",
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    },
    {
      "ma": "SOL_5M",
      "theo": true,
      "dongCo": "updown-crypto",
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    },
    {
      "ma": "XRP_5M",
      "theo": true,
      "dongCo": "updown-crypto",
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    },
    {
      "ma": "BTC_150K",
      "theo": true,
      "dongCo": "cham-moc-crypto",
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    },
    {
      "ma": "BTC_15M",
      "theo": false,
      "dongCo": "updown-crypto",
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    }
  ],
  "boQua": {
    "BTC_5M": "chưa bám được khung nào đang ăn thua",
    "ETH_5M": "chưa bám được khung nào đang ăn thua",
    "SOL_5M": "chưa bám được khung nào đang ăn thua",
    "XRP_5M": "chưa bám được khung nào đang ăn thua",
    "BTC_150K": "chưa bám được khung nào đang ăn thua"
  },
  "coHoi": [],
  "kho": {
    "soThiTruong": 0,
    "viThe": [],
    "phoiNhiemNhom": {},
    "phoiNhiemGop": 0.0,
    "tongChuaPhongHoUsd": 0,
    "tongLoKhoaUsd": 0
  },
  "risk": {
    "von": 950.0517497348915,
    "vonBanDau": 1000.0,
    "vonDauNgay": 1000.0,
    "dinhVon": 1000.0,
    "sutVonPct": 4.994825026510853,
    "loNgayUsd": 49.94825026510855,
    "laiRongNgayUsd": -49.94825026510855,
    "loGopNgayUsd": 49.94825026510855,
    "tranLoNgayUsd": 50.0,
    "tranMoiThiTruongUsd": 100.0,
    "tranMoiTaiSanUsd": 200.0,
    "ngatKhanCap": false,
    "lyDoNgat": ""
  },
  "lenh": {
    "tongLenh": 0,
    "daKhop": 0,
    "dangCho": 0,
    "tongPhiUsd": 0,
    "duong": "giay",
    "cuaDangDong": [
      "che ≠ 'that' (đang: 'giay')",
      "datLenh.choPhepLenhThat = false",
      "datLenh.toiXacNhanDaDocRuiRo = false",
      "thiếu POLYMARKET_PRIVATE_KEY trong .env"
    ]
  },
  "hieuChinh": {
    "bang": [
      {
        "o": "0-10",
        "n": 5222,
        "duDoan": 0.038940755698483445,
        "thucTe": 0.0534278054385293,
        "lech": 0.014487049740045853
      },
      {
        "o": "10-20",
        "n": 2829,
        "duDoan": 0.15060746974278225,
        "thucTe": 0.15129020855425945,
        "lech": 0.000682738811477207
      },
      {
        "o": "20-30",
        "n": 3330,
        "duDoan": 0.25157190837641763,
        "thucTe": 0.23153153153153153,
        "lech": -0.020040376844886104
      },
      {
        "o": "30-40",
        "n": 3965,
        "duDoan": 0.35136791339957857,
        "thucTe": 0.32686002522068097,
        "lech": -0.024507888178897597
      },
      {
        "o": "40-50",
        "n": 4969,
        "duDoan": 0.454847024929898,
        "thucTe": 0.4342926142080902,
        "lech": -0.020554410721807803
      },
      {
        "o": "50-60",
        "n": 4631,
        "duDoan": 0.5486320115135455,
        "thucTe": 0.5545238609371625,
        "lech": 0.00589184942361709
      },
      {
        "o": "60-70",
        "n": 3967,
        "duDoan": 0.6480837871467847,
        "thucTe": 0.6617091000756239,
        "lech": 0.013625312928839173
      },
      {
        "o": "70-80",
        "n": 3358,
        "duDoan": 0.7489704072232416,
        "thucTe": 0.7608695652173914,
        "lech": 0.011899157994149756
      },
      {
        "o": "80-90",
        "n": 2883,
        "duDoan": 0.8492937110032727,
        "thucTe": 0.8449531737773153,
        "lech": -0.004340537225957397
      },
      {
        "o": "90-100",
        "n": 5186,
        "duDoan": 0.9611990387453453,
        "thucTe": 0.9541072117238719,
        "lech": -0.007091827021473374
      }
    ],
    "tongMau": 40340,
    "duDeDungKelly": true,
    "saiSoTB": 0.012746952593189831
  },
  "thongKe": {
    "n": 1,
    "chuaCo": false,
    "tiLeThang": 0.0,
    "soThang": 0,
    "soThua": 1,
    "tbThang": 0.0,
    "tbThua": 49.94825026510855,
    "kyVong": -49.94825026510855,
    "tongLaiLo": -49.94825026510855,
    "tongPhi": 0.0,
    "thuaLonNhat": -49.94825026510855,
    "xoaBaoNhieuLanThang": null,
    "duoi5pct": -49.94825026510855,
    "canhBaoDuoi": false
  },
  "chienThuat": [
    {
      "ma": "lech-gia",
      "ten": "Lệch giá định hướng",
      "mota": "Mô hình định giá cao hơn chợ đang bán.",
      "bat": true
    },
    {
      "ma": "cap-theo-thoi",
      "ten": "Cặp theo thời",
      "mota": "Gom hai chân ở hai thời điểm khác nhau.",
      "bat": true
    },
    {
      "ma": "cap-tuc-thi",
      "ten": "Cặp tức thì",
      "mota": "UP + DOWN cùng lúc dưới 1 đô ngay trong sổ.",
      "bat": true
    },
    {
      "ma": "phong-ho",
      "ten": "Định hướng có phòng hộ",
      "mota": "Lõi là cặp, chừa một phần thiên lệch.",
      "bat": true
    },
    {
      "ma": "tao-lap",
      "ten": "Tạo lập",
      "mota": "Yết hai bên, ăn spread, lệch giá theo tồn kho.",
      "bat": true
    },
    {
      "ma": "can-ket-qua",
      "ten": "Cận kết quả",
      "mota": "Mua bên gần chắc thắng. Đuôi lệch — đọc kỹ.",
      "bat": true
    }
  ],
  "vi": {
    "soVi": 0,
    "nga": {},
    "quetLucMs": 1788036162824.8176,
    "gioiHan": "Đặt/huỷ lệnh diễn ra off-chain, nên chỉ thấy được các lần KHỚP. Không dựng lại được vòng đời báo giá, và vì vậy không kết luận được ai là market maker.",
    "vi": []
  },
  "nguon": {
    "gamma-slug": {
      "tuoiMs": null,
      "soLoi": 3,
      "tongLuot": 0,
      "loiCuoi": "ConnectError: [WinError 10054] An existing connection was forcibly closed by the remote host"
    },
    "gamma": {
      "tuoiMs": null,
      "soLoi": 3,
      "tongLuot": 0,
      "loiCuoi": "ConnectError: [WinError 10054] An existing connection was forcibly closed by the remote host"
    },
    "binance-kline": {
      "tuoiMs": null,
      "soLoi": 0,
      "tongLuot": 0,
      "loiCuoi": ""
    }
  },
  "dongSong": {
    "dangNoi": false,
    "soToken": 0,
    "soSo": 0,
    "tinNhan": 0,
    "soLanNoiLai": 0,
    "loiCuoi": "",
    "noiLucMs": 0.0
  },
  "ketToan": {
    "dangCho": 0,
    "daKetToan": 0,
    "soBatDong": 0,
    "soTreo": 0,
    "tienTreoUsd": 0.0,
    "ganDay": [],
    "cho": []
  },
  "doThi": {
    "soNut": 0,
    "zTrungBinh": null,
    "canhBaoDongPha": null,
    "nut": [],
    "noiBat": [],
    "canhChuY": []
  },
  "voDich": {
    "duongKim": {},
    "nguong": {
      "toiThieuMau": 120,
      "bienVuot": 1.15,
      "duoiToiDa": 1.25
    },
    "hoSo": [
      {
        "ma": "khong-nhan",
        "n": 1,
        "kyVong": -49.94825026510855,
        "tongLaiLo": -49.94825026510855,
        "tiLeThang": 0.0,
        "thuaLonNhat": -49.94825026510855,
        "duoi5pct": -49.94825026510855,
        "capNhatLuc": 1788036162.8257363
      }
    ]
  },
  "tienHoa": {
    "ganNhat": null,
    "duong": {
      "soLuot": 37,
      "soLanNhan": 0,
      "soLanTraLai": 1,
      "soLanDungYen": 36,
      "chuoi": [],
      "tongCaiThien": null,
      "ganNhat": {
        "luc": "2026-08-29T20:23:48Z",
        "soKhungBang": 89964,
        "soLenhKetToan": 19,
        "nguonMau": "chay-lai",
        "daThu": 0,
        "trieuChung": [
          {
            "ma": "thieu-mau",
            "nang": 1,
            "moTa": "mới 19 lệnh đã kết toán — chưa đủ để chẩn gì. Chạy thêm, đừng vặn.",
            "bangChung": {
              "n": 19,
              "canToiThieu": 20,
              "nguonMau": "chay-lai"
            },
            "nutGoiY": []
          }
        ],
        "deXuat": [],
        "nhan": null,
        "traLai": [],
        "kyVongTruoc": 22.231841999999993,
        "kyVongSau": null,
        "ghiChu": "không có bệnh nào vượt ngưỡng — không vặn gì. Vòng tiến hoá đứng yên là một kết quả hợp lệ."
      }
    },
    "ngayDaXet": "2026-08-29",
    "ngayDaChay": "",
    "xong": false,
    "dangChay": true,
    "loi": null,
    "soLanThu": 1,
    "toiDaThu": 4,
    "thuLaiSauGiay": null,
    "bat": true,
    "gioUTC": 2
  },
  "quyetChan": {},
  "bang": {
    "soKhung": 1,
    "bat": true,
    "soLoiGhi": 0,
    "loiCuoi": null,
    "duong": "bang-2026-08-29-204242-3968.jsonl.gz",
    "doc": null
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi API nào và không đặt được lệnh nào."
};
