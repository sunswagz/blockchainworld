"""Cổng rủi ro — Python thuần, tất định, có quyền phủ quyết.

Không dòng nào ở đây gọi model, gọi mạng, hay đọc trạng thái ngoài tham số
truyền vào. Đó là điều kiện để cùng một cơ hội luôn cho cùng một phán quyết,
và để phép kiểm dựng lại được mọi tình huống mà không cần sàn nào.

Bảy cửa, và mỗi cửa nằm đây vì một cách mất tiền CỤ THỂ:

    1. chênh lệch thô quá mỏng      → không đáng chạm vào
    2. NET sau phí âm               → càng làm càng lỗ
    3. không mốc kết toán nào       → giữ xong thu đúng bằng 0
    4. lệch mark hai sàn quá lớn    → không còn là delta-neutral
    5. thiếu mark một bên           → không biết có lệch hay không
    6. dữ liệu quá cũ               → đang cược vào một thế giới đã qua
    7. mốc kết toán phải đoán       → sai số nằm ngoài tầm đo

Cửa 3 và 7 không có trong bản v0.1, và chúng chính là hai cửa mà một scanner
chỉ nhân `spread × giờ` không thể có — nó không biết mốc nằm ở đâu.
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
}


class CongRuiRo:
    def __init__(self, cau_hinh: dict | None = None) -> None:
        self.c = {**MAC_DINH, **(cau_hinh or {})}

    def __call__(self, co: CoHoi) -> tuple[bool, list[str]]:
        return self.xet(co)

    def xet(self, co: CoHoi) -> tuple[bool, list[str]]:
        """Trả về `(duyệt, danh sách lý do TỪ CHỐI)`.

        Gom TẤT CẢ lý do chứ không dừng ở cái đầu tiên. Dừng sớm thì người
        vận hành sửa một ngưỡng, chạy lại, gặp lý do thứ hai, sửa tiếp — và
        không bao giờ thấy được bức tranh đầy đủ về vì sao cơ hội này hỏng.
        """
        c, ly = self.c, []

        if co.grossBpsNgay < float(c["grossToiThieuBpsNgay"]):
            ly.append(f"chênh lệch thô {co.grossBpsNgay:.2f} bps/ngày "
                      f"< ngưỡng {float(c['grossToiThieuBpsNgay']):.2f}")

        if co.netBps < float(c["netToiThieuBps"]):
            ly.append(f"NET sau phí {co.netBps:.2f} bps "
                      f"< ngưỡng {float(c['netToiThieuBps']):.2f}")

        if c["doiHoiItNhatMotMoc"] and co.soMocLong == 0 and co.soMocShort == 0:
            cho = co.choMocDauGiay
            ly.append("không mốc kết toán nào rơi vào cửa sổ giữ"
                      + (f" — còn {cho / 3600.0:.1f} giờ nữa mới tới mốc đầu"
                         if cho is not None else ""))

        if co.lechMarkBps is None:
            if c["doiHoiHaiMark"]:
                ly.append("thiếu giá mark một bên — không biết hai sàn có "
                          "đang nhìn cùng một thế giới không")
        elif co.lechMarkBps > float(c["lechMarkToiDaBps"]):
            ly.append(f"lệch mark {co.lechMarkBps:.1f} bps "
                      f"> trần {float(c['lechMarkToiDaBps']):.1f}")

        tuoi_max = float(c["tuoiToiDaGiay"])
        if co.tuoiXauNhatGiay is None:
            ly.append("không sàn nào đóng dấu thời gian — không đo được độ tươi")
        elif co.tuoiXauNhatGiay > tuoi_max:
            ly.append(f"dữ liệu cũ {co.tuoiXauNhatGiay:.0f}s > trần {tuoi_max:.0f}s")

        if co.uocLuongMoc and not c["nhanUocLuongMoc"]:
            ly.append("mốc kết toán phải ĐOÁN vì sàn không công bố — "
                      "sai số nằm ngoài tầm đo")

        return (not ly), ly

    def tom_tat(self) -> dict:
        return dict(self.c)
