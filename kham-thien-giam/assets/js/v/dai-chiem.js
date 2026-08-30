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
  "date": "30/08/2026",
  "tomTat": "1 market đã kết toán · kỳ vọng -49.9483$/lệnh",
  "generatedAt": "2026-08-30T09:39:47.814Z",
  "che": "giay",
  "cheKhai": "giay",
  "vong": 1,
  "chayDuocGiay": 1.1641249656677246,
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
    "vonDauNgay": 950.0517497348915,
    "dinhVon": 1000.0,
    "sutVonPct": 4.994825026510853,
    "loNgayUsd": 0.0,
    "laiRongNgayUsd": 0.0,
    "loGopNgayUsd": 0.0,
    "tranLoNgayUsd": 47.50258748674458,
    "loXauNhatGopUsd": 0,
    "conNganSachNgayUsd": 47.50258748674458,
    "tranPhoiNhiemGopUsd": 190.01034994697832,
    "tranMoiThiTruongUsd": 95.00517497348916,
    "tranMoiTaiSanUsd": 190.01034994697832,
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
      "chưa đối soát vị thế với SÀN sau khi khởi động",
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
        "n": 20131,
        "duDoan": 0.03929466320191271,
        "thucTe": 0.051760965674829865,
        "lech": 0.012466302472917155
      },
      {
        "o": "10-20",
        "n": 11579,
        "duDoan": 0.1504763290638771,
        "thucTe": 0.1525174885568702,
        "lech": 0.0020411594929931054
      },
      {
        "o": "20-30",
        "n": 13270,
        "duDoan": 0.25154157195982924,
        "thucTe": 0.23556895252449134,
        "lech": -0.015972619435337898
      },
      {
        "o": "30-40",
        "n": 16222,
        "duDoan": 0.351505226541548,
        "thucTe": 0.32647022561952904,
        "lech": -0.025035000922018935
      },
      {
        "o": "40-50",
        "n": 20362,
        "duDoan": 0.45642286652088215,
        "thucTe": 0.43325802966309795,
        "lech": -0.0231648368577842
      },
      {
        "o": "50-60",
        "n": 17030,
        "duDoan": 0.5518268391619328,
        "thucTe": 0.5587199060481504,
        "lech": 0.0068930668862176026
      },
      {
        "o": "60-70",
        "n": 15451,
        "duDoan": 0.648297865496475,
        "thucTe": 0.6582098246068215,
        "lech": 0.009911959110346591
      },
      {
        "o": "70-80",
        "n": 13051,
        "duDoan": 0.748835990185104,
        "thucTe": 0.7584859397747299,
        "lech": 0.00964994958962584
      },
      {
        "o": "80-90",
        "n": 11709,
        "duDoan": 0.8493416225101021,
        "thucTe": 0.8440515842514306,
        "lech": -0.005290038258671581
      },
      {
        "o": "90-100",
        "n": 20947,
        "duDoan": 0.9609994352436009,
        "thucTe": 0.9506373227669833,
        "lech": -0.010362112476617558
      }
    ],
    "tongMau": 159752,
    "duDeDungKelly": true,
    "saiSoTB": 0.012768709645029424
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
    "canhBaoDuoi": false,
    "canhBao": null
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
    "quetLucMs": 1788082787808.9692,
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
    "hoSo": [
      {
        "ma": "khong-nhan",
        "n": 1,
        "kyVong": -49.94825026510855,
        "tongLaiLo": -49.94825026510855,
        "tiLeThang": 0.0,
        "thuaLonNhat": -49.94825026510855,
        "duoi5pct": -49.94825026510855,
        "capNhatLuc": 1788082787.8089693
      }
    ]
  },
  "tienHoa": {
    "ganNhat": null,
    "duong": {
      "soLuot": 48,
      "soLanNhan": 0,
      "soLanTraLai": 1,
      "soLanDungYen": 47,
      "chuoi": [],
      "tongCaiThien": null,
      "ganNhat": {
        "luc": "2026-08-30T02:05:06Z",
        "soKhungBang": 55276,
        "soLenhKetToan": 22,
        "nguonMau": "chay-lai",
        "daThu": 0,
        "trieuChung": [
          {
            "ma": "khoe",
            "nang": 0,
            "moTa": "không triệu chứng nào vượt ngưỡng: kỳ vọng +18.07652, 22 lệnh, đuôi trong hạn",
            "bangChung": {
              "kyVong": 18.076521363636363,
              "n": 22
            },
            "nutGoiY": []
          }
        ],
        "deXuat": [],
        "nhan": null,
        "traLai": [],
        "kyVongTruoc": 18.076521363636363,
        "kyVongSau": null,
        "ghiChu": "không có bệnh nào vượt ngưỡng — không vặn gì. Vòng tiến hoá đứng yên là một kết quả hợp lệ."
      }
    },
    "ngayDaXet": "2026-08-30",
    "ngayDaChay": "2026-08-30",
    "xong": true,
    "dangChay": false,
    "loi": null,
    "soLanThu": 0,
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
    "duong": "bang-2026-08-30-093947-5672.jsonl.gz",
    "doc": null
  },
  "loiNhac": "Đây là LÁT CẮT tĩnh do runtime ở máy ghi ra, không phải số liệu sống. Trang này không gọi API nào và không đặt được lệnh nào."
};
