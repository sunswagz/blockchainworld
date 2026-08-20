/* SINH TỰ ĐỘNG bởi kham-thien-giam-runtime — ĐỪNG SỬA TAY.
   Lát cắt trạng thái Đài Chiêm, để trang tĩnh đọc được mà không cần server
   và không cần khoá nào. Sửa tay thì lượt ghi kế tiếp đè lên.

   Sinh bằng tay (runtime không chạy trên Actions được — xem CLAUDE.md):
       python run.py                 ghi mỗi vòng lặp
       python -m kham.snapshot       ghi một lần rồi thoát
*/
window.DAI_CHIEM = {
  "date": "20/08/2026",
  "tomTat": "0/0 cơ hội qua sàng · chưa có market nào kết toán",
  "generatedAt": "2026-08-20T15:02:57.858Z",
  "che": "giay",
  "cheKhai": "giay",
  "vong": 1,
  "chayDuocGiay": 3.7849833965301514,
  "thiTruong": [
    {
      "ma": "BTC_5M",
      "theo": true,
      "khung": {
        "slug": "btc-updown-5m-1787238300",
        "ma": "BTC_5M",
        "giaiDoan": "dat-cuoc",
        "nhan": "đặt cược",
        "datCuocDuoc": true,
        "conLaiGiay": 122.14199072265625,
        "troiQuaPct": 59.28600309244791,
        "eventStartMs": 1787238300000.0,
        "endMs": 1787238600000.0
      },
      "gia": null,
      "giaNen": 72154.0,
      "cap": null,
      "so": null
    },
    {
      "ma": "ETH_5M",
      "theo": true,
      "khung": {
        "slug": "eth-updown-5m-1787238300",
        "ma": "ETH_5M",
        "giaiDoan": "dat-cuoc",
        "nhan": "đặt cược",
        "datCuocDuoc": true,
        "conLaiGiay": 122.14199072265625,
        "troiQuaPct": 59.28600309244791,
        "eventStartMs": 1787238300000.0,
        "endMs": 1787238600000.0
      },
      "gia": null,
      "giaNen": 2290.96,
      "cap": null,
      "so": null
    },
    {
      "ma": "SOL_5M",
      "theo": false,
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    },
    {
      "ma": "XRP_5M",
      "theo": false,
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    },
    {
      "ma": "BTC_15M",
      "theo": false,
      "khung": null,
      "gia": null,
      "giaNen": null,
      "cap": null,
      "so": null
    }
  ],
  "boQua": {
    "BTC_5M": "chưa đủ mẫu ước lượng σ (1/12)",
    "ETH_5M": "chưa đủ mẫu ước lượng σ (1/12)"
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
    "quetLucMs": 1787238177855.016,
    "gioiHan": "Đặt/huỷ lệnh diễn ra off-chain, nên chỉ thấy được các lần KHỚP. Không dựng lại được vòng đời báo giá, và vì vậy không kết luận được ai là market maker.",
    "vi": []
  },
  "nguon": {
    "gamma-slug": {
      "tuoiMs": 201.52197265625,
      "soLoi": 0,
      "tongLuot": 10,
      "loiCuoi": ""
    },
    "binance": {
      "tuoiMs": 8.976318359375,
      "soLoi": 0,
      "tongLuot": 2,
      "loiCuoi": ""
    }
  },
  "dongSong": {
    "dangNoi": false,
    "soToken": 4,
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
  "quyetChan": {},
  "bang": {
    "soKhung": 1,
    "bat": true
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi API nào và không đặt được lệnh nào."
};
