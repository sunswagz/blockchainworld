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
  "tomTat": "0/0 cơ hội qua sàng · chưa có market nào kết toán",
  "generatedAt": "2026-08-29T13:22:58.712Z",
  "che": "giay",
  "cheKhai": "giay",
  "vong": 1,
  "chayDuocGiay": 0.9870736598968506,
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
    "von": 1000.0,
    "vonBanDau": 1000.0,
    "dinhVon": 1000.0,
    "sutVonPct": 0.0,
    "loNgayUsd": 0.0,
    "laiRongNgayUsd": 0.0,
    "loGopNgayUsd": 0.0,
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
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "10-20",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "20-30",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "30-40",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "40-50",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "50-60",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "60-70",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "70-80",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "80-90",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      },
      {
        "o": "90-100",
        "n": 0,
        "duDoan": null,
        "thucTe": null,
        "lech": null
      }
    ],
    "tongMau": 0,
    "duDeDungKelly": false,
    "saiSoTB": null
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
    "quetLucMs": 1788009778706.4365,
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
    "hoSo": []
  },
  "tienHoa": {
    "ganNhat": null,
    "duong": {
      "soLuot": 3,
      "soLanNhan": 0,
      "soLanTraLai": 0,
      "soLanDungYen": 3,
      "chuoi": [],
      "tongCaiThien": null,
      "ganNhat": {
        "luc": "2026-08-20T15:44:24Z",
        "soKhungBang": 0,
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
    "duong": "bang-2026-08-29-132258-7412.jsonl.gz"
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi API nào và không đặt được lệnh nào."
};
