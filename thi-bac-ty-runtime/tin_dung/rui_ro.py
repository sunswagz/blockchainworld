"""Cổng rủi ro CHUYÊN MÔN của ty tín dụng — tầng rủi ro THỨ NHẤT.

Nó chỉ trả lời *"cơ hội này có hợp lệ không"*. Câu *"cho tiền vào đây thì
DANH MỤC ra sao"* thuộc `thi_bac_ty/rui_ro_tong.py` — đừng trả lời hộ.

## `CUA` là HỢP ĐỒNG, không phải chú thích

`bac/rui_ro.py` từng khai ba cửa mà `xet()` không hề đọc tới. Buồng lái bày
chúng dưới nhãn "Cửa rủi ro đang có hiệu lực" trong khi chúng không chặn gì
cả — hỏng im lặng, đúng loại cả runtime này sinh ra để bắt.

Nên ở đây, y như bên ấy: `CUA` liệt kê tường minh, `tom_tat()` LỌC theo nó,
và có phép kiểm dùng dict-gián-điệp bắt `xet()` phải đọc đủ mọi khoá đã khai
— không hơn, không kém.
"""
from __future__ import annotations

#: Cửa đang THẬT SỰ có hiệu lực. Thêm một khoá vào đây mà `xet()` không đọc
#: là bày một cái cửa không chặn gì, và phép kiểm sẽ đỏ.
CUA = ("tvlToiThieuUsd", "suDungToiDa", "thanhKhoanThoatToiThieuUsd",
       "tyLeThuongToiDa", "netToiThieuBps", "apyToiDaPhanTram",
       "tuoiToiDaGiay")

#: Mã → nhãn ngắn. Mã để GỘP thống kê, câu để người đọc hiểu. Trộn hai thứ
#: là chuyện đã cắn thật ở `bac/`: lý do từ chối chứa số nên mỗi lần một
#: chuỗi khác, và bảng "vì sao từ chối" vỡ thành tám dòng nói cùng một điều.
NHAN = {
    "tvl-qua-nho": "TVL quá nhỏ",
    "dung-von-qua-cao": "dùng vốn quá cao — rút không ra",
    "thanh-khoan-thoat-mong": "thanh khoản thoát quá mỏng",
    "lai-chu-yeu-tu-thuong": "lãi chủ yếu từ token thưởng",
    "net-duoi-nguong": "NET sau phí dưới ngưỡng",
    "apy-cao-bat-thuong": "APY cao bất thường — dấu hiệu xấu, không phải cơ hội",
    "du-lieu-cu": "dữ liệu quá cũ",
    "thieu-so-do": "thiếu số đo bắt buộc",
}


class CongRuiRo:
    def __init__(self, cau_hinh: dict) -> None:
        self.c = dict(cau_hinh)

    def xet(self, co) -> tuple[bool, list[tuple[str, str]]]:
        """`(qua, [(mã, câu)])`. Rỗng nghĩa là qua sạch."""
        t = co.thiTruong
        ly: list[tuple[str, str]] = []

        # Thiếu số đo là TỪ CHỐI, không phải bỏ qua. Một thị trường không
        # nói được nó còn bao nhiêu thanh khoản rảnh thì ta không biết đường
        # ra, và không biết đường ra là chưa đo được rủi ro chính của nó.
        if t.suDung is None or t.thanhKhoanRanhUsd is None:
            ly.append(("thieu-so-do",
                       "thiếu tổng cung hoặc tổng vay — không tính được "
                       "dùng vốn lẫn thanh khoản thoát"))

        tvl_min = float(self.c["tvlToiThieuUsd"])
        if t.tvlUsd < tvl_min:
            ly.append(("tvl-qua-nho",
                       f"TVL ${t.tvlUsd / 1e6:.1f}M < ${tvl_min / 1e6:.1f}M"))

        du_max = float(self.c["suDungToiDa"])
        if t.suDung is not None and t.suDung > du_max:
            ly.append(("dung-von-qua-cao",
                       f"dùng vốn {t.suDung:.0%} > trần {du_max:.0%} — "
                       f"thanh khoản rảnh là thứ mọi người cùng chạy tới "
                       f"khi có biến"))

        tk_min = float(self.c["thanhKhoanThoatToiThieuUsd"])
        if t.thanhKhoanRanhUsd is not None and t.thanhKhoanRanhUsd < tk_min:
            ly.append(("thanh-khoan-thoat-mong",
                       f"rút ra được ${t.thanhKhoanRanhUsd / 1e3:.0f}K < "
                       f"${tk_min / 1e3:.0f}K"))

        th_max = float(self.c["tyLeThuongToiDa"])
        if t.tyLeThuong > th_max:
            ly.append(("lai-chu-yeu-tu-thuong",
                       f"{t.tyLeThuong:.0%} lãi đến từ token thưởng > trần "
                       f"{th_max:.0%} — thị trường này đang MUA thanh khoản, "
                       f"không phải đang trả lãi thật"))

        net_min = float(self.c["netToiThieuBps"])
        if co.netBps < net_min:
            ly.append(("net-duoi-nguong",
                       f"NET {co.netBps:.2f} bps < {net_min:.2f} bps"))

        apy_max = float(self.c["apyToiDaPhanTram"])
        if t.apyGocPhanTram > apy_max:
            ly.append(("apy-cao-bat-thuong",
                       f"APY gốc {t.apyGocPhanTram:.1f}% > {apy_max:.0f}% "
                       f"trên một stablecoin — đây là dấu hiệu thị trường "
                       f"sắp cạn thanh khoản, không phải một món hời"))

        tuoi_max = float(self.c["tuoiToiDaGiay"])
        tuoi = t.tuoi_giay()
        if tuoi > tuoi_max:
            ly.append(("du-lieu-cu",
                       f"dữ liệu {tuoi:.0f}s > trần {tuoi_max:.0f}s"))

        return (not ly), ly

    def tom_tat(self) -> dict:
        """CHỈ những cửa có trong `CUA`. Khoá lạ bị lọc, không bày ra."""
        return {k: self.c[k] for k in CUA if k in self.c}
