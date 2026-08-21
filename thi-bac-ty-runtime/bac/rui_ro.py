"""Cổng rủi ro — Python thuần, tất định, có quyền phủ quyết.

Không dòng nào ở đây gọi model, gọi mạng, hay đọc trạng thái ngoài tham số
truyền vào. Đó là điều kiện để cùng một cơ hội luôn cho cùng một phán quyết,
và để phép kiểm dựng lại được mọi tình huống mà không cần sàn nào.

Tám cửa, và mỗi cửa nằm đây vì một cách mất tiền CỤ THỂ:

    1. chênh lệch thô quá mỏng      → không đáng chạm vào
    2. NET sau phí âm               → càng làm càng lỗ
    3. không mốc kết toán nào       → giữ xong thu đúng bằng 0
    4. lệch mark hai sàn quá lớn    → không còn là delta-neutral
    5. thiếu mark một bên           → không biết có lệch hay không
    6. dữ liệu quá cũ               → đang cược vào một thế giới đã qua
    7. mốc kết toán phải đoán       → sai số nằm ngoài tầm đo
    8. đồng hồ máy lệch giờ sàn     → mọi phép đếm mốc sai theo

Cửa 3 và 7 không có trong bản v0.1, và chúng chính là hai cửa mà một scanner
chỉ nhân `spread × giờ` không thể có — nó không biết mốc nằm ở đâu.

Cửa 8 thêm vào ngày 21/08/2026 sau khi đo được đồng hồ máy chậm 6,94 phút so
với cả ba sàn. Xem `dong_ho.py` — nó vừa làm lệch phép đếm mốc, vừa giết cửa
6 trong im lặng.

## Mỗi lý do có MÃ, và mã mới là thứ đem đi đếm

Lý do trả về là một cặp `(mã, câu)`. Câu để người đọc; **mã để gộp**.

Bản đầu chỉ trả về câu, rồi buồng lái cắt chuỗi để gộp — nhưng câu có mang
con số (`"NET sau phí -29.00 bps < ngưỡng 0.50"`), nên mỗi giá trị thành một
khoá riêng. Bảng "vì sao bị chặn" vỡ thành sáu dòng nói cùng một chuyện:

    10  NET sau phí -29.00 bps
     8  NET sau phí -28.00 bps
     6  NET sau phí -27.00 bps        ← đáng lẽ phải là: 30  NET sau phí
     ...

Đúng thứ mà bảng ấy sinh ra để chặn: người vận hành nhìn vào để biết CỬA NÀO
đang chặn, chứ không phải để đọc lại từng con số đã có ở bảng trên.
"""
from __future__ import annotations

from .models import CoHoi

# Không đủ mẫu để nói gì về `netAprPct`, nhưng `netBps` thì luôn có nghĩa.
# Nên mọi ngưỡng ở đây tính bằng bps, không bằng phần trăm năm.
MAC_DINH = {
    "grossToiThieuBpsNgay": 3.0,
    "netToiThieuBps": 0.5,
    "lechMarkToiDaBps": 40.0,
    "doiHoiHaiMark": True,
    "tuoiToiDaGiay": 90.0,
    "nhanUocLuongMoc": False,
    "doiHoiItNhatMotMoc": True,
    "lechDongHoToiDaGiay": 10.0,
}

#: Mã lý do → câu ngắn cho bảng gộp. Buồng lái và cung tĩnh đọc bảng này thay
#: vì tự cắt chuỗi; thêm cửa mới thì thêm MỘT dòng ở đây.
NHAN = {
    "gross-mong": "chênh lệch thô quá mỏng",
    "net-am": "NET sau phí dưới ngưỡng",
    "khong-moc": "không mốc kết toán nào trong cửa sổ giữ",
    "lech-mark": "lệch giá mark hai sàn quá lớn",
    "thieu-mark": "thiếu giá mark một bên",
    "du-lieu-cu": "dữ liệu quá cũ",
    "khong-dau-thoi-gian": "sàn không đóng dấu thời gian",
    "moc-uoc-luong": "mốc kết toán phải đoán",
    "lech-dong-ho": "đồng hồ máy lệch giờ sàn",
}


class CongRuiRo:
    def __init__(self, cau_hinh: dict | None = None) -> None:
        self.c = {**MAC_DINH, **(cau_hinh or {})}

    def __call__(self, co: CoHoi) -> tuple[bool, list[tuple[str, str]]]:
        return self.xet(co)

    def xet(self, co: CoHoi) -> tuple[bool, list[tuple[str, str]]]:
        """Trả về `(duyệt, danh sách (mã, câu) lý do TỪ CHỐI)`.

        Gom TẤT CẢ lý do chứ không dừng ở cái đầu tiên. Dừng sớm thì người
        vận hành sửa một ngưỡng, chạy lại, gặp lý do thứ hai, sửa tiếp — và
        không bao giờ thấy được bức tranh đầy đủ về vì sao cơ hội này hỏng.
        """
        c, ly = self.c, []

        if co.grossBpsNgay < float(c["grossToiThieuBpsNgay"]):
            ly.append(("gross-mong",
                       f"chênh lệch thô {co.grossBpsNgay:.2f} bps/ngày "
                       f"< ngưỡng {float(c['grossToiThieuBpsNgay']):.2f}"))

        if co.netBps < float(c["netToiThieuBps"]):
            ly.append(("net-am",
                       f"NET sau phí {co.netBps:.2f} bps "
                       f"< ngưỡng {float(c['netToiThieuBps']):.2f}"))

        if c["doiHoiItNhatMotMoc"] and co.soMocLong == 0 and co.soMocShort == 0:
            cho = co.choMocDauGiay
            ly.append(("khong-moc",
                       "không mốc kết toán nào rơi vào cửa sổ giữ"
                       + (f" — còn {cho / 3600.0:.1f} giờ nữa mới tới mốc đầu"
                          if cho is not None else "")))

        if co.lechMarkBps is None:
            if c["doiHoiHaiMark"]:
                ly.append(("thieu-mark",
                           "thiếu giá mark một bên — không biết hai sàn có "
                           "đang nhìn cùng một thế giới không"))
        elif co.lechMarkBps > float(c["lechMarkToiDaBps"]):
            ly.append(("lech-mark",
                       f"lệch mark {co.lechMarkBps:.1f} bps "
                       f"> trần {float(c['lechMarkToiDaBps']):.1f}"))

        tuoi_max = float(c["tuoiToiDaGiay"])
        if co.tuoiXauNhatGiay is None:
            ly.append(("khong-dau-thoi-gian",
                       "không sàn nào đóng dấu thời gian — không đo được độ tươi"))
        elif co.tuoiXauNhatGiay > tuoi_max:
            ly.append(("du-lieu-cu",
                       f"dữ liệu cũ {co.tuoiXauNhatGiay:.0f}s > trần {tuoi_max:.0f}s"))
        elif co.tuoiXauNhatGiay < -float(c["lechDongHoToiDaGiay"]):
            # Tuổi ÂM = dấu thời gian sàn nằm ở tương lai so với đồng hồ ta
            # đang dùng, tức phần bù lệch chưa đủ. Bản đầu kẹp về 0 ở
            # `tuoi_giay()` và biến chuyện này thành "vừa mới tinh" — cửa
            # `tuoiToiDaGiay` đứng đó suốt mà không chặn nổi gì.
            ly.append(("lech-dong-ho",
                       f"tuổi báo giá ÂM {co.tuoiXauNhatGiay:.0f}s — đồng hồ "
                       f"máy lệch giờ sàn, mọi phép đếm mốc đang sai theo"))

        if co.uocLuongMoc and not c["nhanUocLuongMoc"]:
            ly.append(("moc-uoc-luong",
                       "mốc kết toán phải ĐOÁN vì sàn không công bố — "
                       "sai số nằm ngoài tầm đo"))

        return (not ly), ly

    def tom_tat(self) -> dict:
        return dict(self.c)
