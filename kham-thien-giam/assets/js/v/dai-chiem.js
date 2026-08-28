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
  "date": "28/08/2026",
  "tomTat": "0/0 cơ hội qua sàng · chưa có market nào kết toán",
  "generatedAt": "2026-08-28T14:43:57.585Z",
  "che": "giay",
  "cheKhai": "giay",
  "vong": 12,
  "chayDuocGiay": 67.15608143806458,
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
    "BTC_5M": "không thấy khung nào có tiền tố `btc-updown-5m-`",
    "ETH_5M": "không thấy khung nào có tiền tố `eth-updown-5m-`",
    "SOL_5M": "không thấy khung nào có tiền tố `sol-updown-5m-`",
    "XRP_5M": "không thấy khung nào có tiền tố `xrp-updown-5m-`"
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
    "von": 1000.0,
    "vonBanDau": 1000.0,
    "dinhVon": 1000.0,
    "sutVonPct": 0.0,
    "loNgayUsd": 0.0,
    "tranLoNgayUsd": 50.0,
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
        "n": 589,
        "duDoan": 0.03567655517694267,
        "thucTe": 0.013582342954159592,
        "lech": -0.022094212222783075
      },
      {
        "o": "10-20",
        "n": 213,
        "duDoan": 0.14593793471688066,
        "thucTe": 0.03286384976525822,
        "lech": -0.11307408495162244
      },
      {
        "o": "20-30",
        "n": 146,
        "duDoan": 0.2495080550708295,
        "thucTe": 0.1095890410958904,
        "lech": -0.13991901397493908
      },
      {
        "o": "30-40",
        "n": 119,
        "duDoan": 0.344521686245824,
        "thucTe": 0.15126050420168066,
        "lech": -0.19326118204414336
      },
      {
        "o": "40-50",
        "n": 129,
        "duDoan": 0.4509768542507742,
        "thucTe": 0.3643410852713178,
        "lech": -0.0866357689794564
      },
      {
        "o": "50-60",
        "n": 117,
        "duDoan": 0.5483998044875736,
        "thucTe": 0.5470085470085471,
        "lech": -0.0013912574790265753
      },
      {
        "o": "60-70",
        "n": 111,
        "duDoan": 0.6496898241459863,
        "thucTe": 0.7477477477477478,
        "lech": 0.09805792360176147
      },
      {
        "o": "70-80",
        "n": 124,
        "duDoan": 0.7520413804834248,
        "thucTe": 0.8790322580645161,
        "lech": 0.1269908775810913
      },
      {
        "o": "80-90",
        "n": 213,
        "duDoan": 0.8540271029531943,
        "thucTe": 0.9671361502347418,
        "lech": 0.11310904728154747
      },
      {
        "o": "90-100",
        "n": 781,
        "duDoan": 0.9676134163085717,
        "thucTe": 0.9923175416133163,
        "lech": 0.02470412530474464
      }
    ],
    "tongMau": 2542,
    "duDeDungKelly": true,
    "saiSoTB": 0.06368244154002006
  },
  "thongKe": {
    "n": 0,
    "chuaCo": true
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
    "quetLucMs": 1787928171514.1628,
    "gioiHan": "Đặt/huỷ lệnh diễn ra off-chain, nên chỉ thấy được các lần KHỚP. Không dựng lại được vòng đời báo giá, và vì vậy không kết luận được ai là market maker.",
    "vi": []
  },
  "nguon": {
    "gamma-slug": {
      "tuoiMs": null,
      "soLoi": 4,
      "tongLuot": 0,
      "loiCuoi": "ConnectTimeout: _ssl.c:993: The handshake operation timed out"
    },
    "gamma": {
      "tuoiMs": null,
      "soLoi": 4,
      "tongLuot": 0,
      "loiCuoi": "ConnectError: [WinError 10054] An existing connection was forcibly closed by the remote host"
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
    "hoSo": []
  },
  "tienHoa": {
    "ganNhat": null,
    "duong": {
      "soLuot": 14,
      "soLanNhan": 0,
      "soLanTraLai": 0,
      "soLanDungYen": 14,
      "chuoi": [],
      "tongCaiThien": null,
      "ganNhat": {
        "luc": "2026-08-28T14:37:22Z",
        "soKhungBang": 114629,
        "soLenhKetToan": 0,
        "trieuChung": [
          {
            "ma": "thieu-mau",
            "nang": 1,
            "moTa": "mới 0 lệnh đã kết toán — chưa đủ để chẩn gì. Chạy thêm, đừng vặn.",
            "bangChung": {
              "n": 0,
              "canToiThieu": 20
            },
            "nutGoiY": []
          }
        ],
        "deXuat": [],
        "nhan": null,
        "traLai": [],
        "kyVongTruoc": null,
        "kyVongSau": null,
        "ghiChu": "không có bệnh nào vượt ngưỡng — không vặn gì. Vòng tiến hoá đứng yên là một kết quả hợp lệ."
      }
    },
    "ngayDaXet": "2026-08-28",
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
    "soKhung": 11,
    "bat": true,
    "soLoiGhi": 0,
    "loiCuoi": null,
    "duong": "bang-2026-08-28-144251-48288.jsonl.gz"
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi API nào và không đặt được lệnh nào."
};
