"""ĐIỀU PHỐI THỰC THI — hợp đồng lệnh, và máy trạng thái hai chân.

**Chưa đặt lệnh thật.** Không khoá nào, không SDK sàn nào, không đường nào
chạm tới ví. File này định nghĩa **hợp đồng** và **máy trạng thái**, và chạy
được ở chế độ mô phỏng để máy trạng thái ấy được kiểm trước khi có tiền.

## Ty KHÔNG tự đặt lệnh

Ty chỉ tạo `YChiThucThi` — ý chí: "mở delta-neutral, LONG $500 Hyperliquid,
SHORT $500 Binance". Điều Phối Thực Thi mới lo:

    kiểm số dư · API còn sống không · làm mới giá · trượt giá ·
    chia cỡ lệnh · THỨ TỰ hai chân · khớp một phần · thử lại ·
    huỷ · quay lui · đối soát

## Vì sao máy trạng thái, chứ không phải hai lời gọi hàm

Tuyệt đối KHÔNG viết:

    short_binance()      # khớp
    long_hyperliquid()   # TRƯỢT

Giữa hai dòng ấy BTC giảm 1%. Vị thế từ delta-neutral thành **short một
chiều** — không phải "lãi ít hơn", mà là một loại rủi ro HOÀN TOÀN KHÁC với
thứ ty vừa trình lên và Rủi Ro Tổng vừa duyệt.

Đây là *legging risk*, và nó là cách mất tiền nhanh nhất trong nghề chênh
lệch giá. Nên phải là một máy trạng thái có đường lùi:

    CHO ──► GIU_VON ──► MO_CHAN_A ──► MO_CHAN_B ──► DA_PHONG_HO ──► GIU
                             │              │
                          hỏng           hỏng
                             │              │
                             ▼              ▼
                        HOAN_VON      CHUA_PHONG_HO
                                            │
                                  ┌─────────┼─────────┐
                               thử lại   sàn khác   ĐÓNG GẤP
                                            │
                                            ▼
                                          PHANG

## Trạng thái nguy hiểm nhất có tên riêng

`CHUA_PHONG_HO` — một chân đã vào, chân kia chưa. Nó có **đồng hồ đếm
ngược**: quá `tranChuaPhongHoGiay` mà chưa xong thì ĐÓNG GẤP, không hỏi.

Một vị thế chưa phòng hộ để lâu là một cược một chiều mà không ai cố ý đặt.
Đó là lý do hằng số ấy nhỏ, và là lý do nó không có chế độ "chờ thêm chút".
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field

TRANG_THAI = (
    "CHO", "GIU_VON", "MO_CHAN_A", "MO_CHAN_B", "DA_PHONG_HO", "GIU",
    "DANG_DONG", "PHANG", "DA_DOI_SOAT",
    "CHUA_PHONG_HO", "HOAN_VON", "HONG",
)

#: Từ trạng thái nào đi được tới đâu. Máy trạng thái chỉ đi theo bảng này —
#: một đường chuyển không có ở đây là một lỗ hổng, không phải một lối tắt.
DUONG = {
    "CHO": ("GIU_VON", "HONG"),
    "GIU_VON": ("MO_CHAN_A", "HOAN_VON", "HONG"),
    "MO_CHAN_A": ("MO_CHAN_B", "HOAN_VON", "HONG"),
    "MO_CHAN_B": ("DA_PHONG_HO", "CHUA_PHONG_HO", "HONG"),
    "CHUA_PHONG_HO": ("DA_PHONG_HO", "DANG_DONG", "HONG"),
    "DA_PHONG_HO": ("GIU", "DANG_DONG", "HONG"),
    "GIU": ("DANG_DONG", "HONG"),
    "DANG_DONG": ("PHANG", "HONG"),
    "PHANG": ("DA_DOI_SOAT", "HONG"),
    "DA_DOI_SOAT": (),
    "HOAN_VON": (),
    "HONG": (),
}

#: Quá ngần này giây ở `CHUA_PHONG_HO` thì ĐÓNG GẤP. Nhỏ có chủ ý.
TRAN_CHUA_PHONG_HO_GIAY = 30.0


@dataclass
class YChiThucThi:
    """Ty tạo cái này. Ty KHÔNG được tạo lệnh."""
    maToTrinh: str
    chienLuoc: str
    chan: tuple                      # các `to_trinh.Chan`
    vonUsd: float
    lyDo: str = ""
    luc: str = field(default_factory=lambda: _bay_gio())

    def kiem(self) -> list[str]:
        loi = []
        if len(self.chan) < 1:
            loi.append("ý chí không có chân nào")
        if self.vonUsd <= 0:
            loi.append(f"vốn {self.vonUsd} phải > 0")
        if len(self.chan) > 1:
            ben = {c.ben for c in self.chan}
            if len(ben) == 1:
                loi.append(f"nhiều chân cùng một bên ({ben}) — đây KHÔNG phải "
                           f"delta-neutral, khai rõ nếu cố ý")
        return loi

    def tom_tat(self) -> dict:
        return {"maToTrinh": self.maToTrinh, "chienLuoc": self.chienLuoc,
                "vonUsd": self.vonUsd, "lyDo": self.lyDo, "luc": self.luc,
                "chan": [c.tom_tat() for c in self.chan]}


@dataclass
class PhienThucThi:
    """Một lần thực thi, đi qua máy trạng thái."""
    y_chi: YChiThucThi
    trangThai: str = "CHO"
    chanDaMo: list = field(default_factory=list)
    lichSu: list = field(default_factory=list)
    vaoChuaPhongHoLuc: float | None = None
    ghiChu: str = ""

    def chuyen(self, den: str, lyDo: str = "") -> bool:
        if den not in DUONG.get(self.trangThai, ()):
            self.lichSu.append({"luc": _bay_gio(), "tu": self.trangThai,
                                "den": den, "lyDo": lyDo, "chan": True,
                                "vi": "đường chuyển KHÔNG có trong bảng DUONG"})
            return False
        self.lichSu.append({"luc": _bay_gio(), "tu": self.trangThai,
                            "den": den, "lyDo": lyDo, "chan": False})
        self.trangThai = den
        if den == "CHUA_PHONG_HO":
            import time
            self.vaoChuaPhongHoLuc = time.time()
        elif den in ("DA_PHONG_HO", "DANG_DONG", "PHANG"):
            self.vaoChuaPhongHoLuc = None
        return True

    def qua_han_phong_ho(self, nowGiay: float | None = None) -> bool:
        """Đang ở `CHUA_PHONG_HO` quá lâu chưa? → phải ĐÓNG GẤP."""
        if self.trangThai != "CHUA_PHONG_HO" or self.vaoChuaPhongHoLuc is None:
            return False
        import time
        now = nowGiay if nowGiay is not None else time.time()
        return (now - self.vaoChuaPhongHoLuc) > TRAN_CHUA_PHONG_HO_GIAY

    @property
    def xong(self) -> bool:
        return not DUONG.get(self.trangThai, ())

    def tom_tat(self) -> dict:
        return {"yChi": self.y_chi.tom_tat(), "trangThai": self.trangThai,
                "xong": self.xong, "soChanDaMo": len(self.chanDaMo),
                "quaHanPhongHo": self.qua_han_phong_ho(),
                "ghiChu": self.ghiChu, "lichSu": self.lichSu[-20:]}


class DieuPhoiThucThi:
    """Chạy máy trạng thái. Ở bản này **mô phỏng**, không lệnh nào rời máy."""

    def __init__(self, moPhong: bool = True) -> None:
        #: Luôn True ở bản này, và không cấu hình nào đổi được — lớp ký lệnh
        #: chưa tồn tại. Giữ tham số để chữ ký hàm không đổi khi V0.6 tới.
        self.moPhong = True
        self.soPhien = 0
        self.soPhangGap = 0

    def chay(self, y: YChiThucThi, so_cai=None,
             chanBHong: bool = False) -> PhienThucThi:
        """Chạy trọn một phiên. `chanBHong` để phép kiểm cấy lỗi legging.

        Mô phỏng nhưng đi ĐÚNG máy trạng thái thật — mục đích là để đường lùi
        được kiểm trước khi có tiền, chứ không phải để có một con số đẹp.
        """
        from .so_cai import ButToan
        p = PhienThucThi(y)
        self.soPhien += 1

        loi = y.kiem()
        if loi:
            p.chuyen("HONG", "; ".join(loi))
            return p

        p.chuyen("GIU_VON", "vốn đã được Thị Bạc Ty cấp")
        p.chuyen("MO_CHAN_A", f"mở chân 1/{len(y.chan)}")
        p.chanDaMo.append(y.chan[0])
        if so_cai:
            so_cai.ghi(ButToan("MO_VI_THE",
                               f"[MÔ PHỎNG] chân A {y.chan[0].ben} "
                               f"{y.chan[0].cang}", 0.0, y.chienLuoc,
                               y.maToTrinh, {"chan": y.chan[0].tom_tat()}))

        if len(y.chan) == 1:
            p.chuyen("MO_CHAN_B", "chỉ một chân — không cần phòng hộ")
            p.chuyen("DA_PHONG_HO", "một chân, đã xong")
            p.chuyen("GIU", "vào xong")
            return p

        p.chuyen("MO_CHAN_B", f"mở chân 2/{len(y.chan)}")
        if chanBHong:
            # ĐÂY là nhánh đáng giá nhất của cả file.
            p.chuyen("CHUA_PHONG_HO",
                     "chân B KHÔNG khớp — vị thế đang MỘT CHIỀU")
            p.ghiChu = ("chân A đã vào, chân B trượt. Đây không phải 'lãi ít "
                        "hơn', đây là một cược một chiều không ai cố ý đặt.")
            if so_cai:
                so_cai.ghi(ButToan("MO_VI_THE",
                                   "CHƯA PHÒNG HỘ — chân B không khớp", 0.0,
                                   y.chienLuoc, y.maToTrinh,
                                   {"nguyHiem": True}))
            # Đường lùi: đóng gấp chân đã mở. Không thử lại ở bản mô phỏng —
            # thử lại cần giá mới, mà giá mới cần gọi sàn.
            p.chuyen("DANG_DONG", "ĐÓNG GẤP chân đã mở")
            p.chuyen("PHANG", "đã phẳng, không còn phơi nhiễm một chiều")
            p.chuyen("DA_DOI_SOAT", "[MÔ PHỎNG] đối soát bỏ qua")
            self.soPhangGap += 1
            if so_cai:
                so_cai.ghi(ButToan("DONG_VI_THE",
                                   "đóng gấp sau khi chân B hỏng", 0.0,
                                   y.chienLuoc, y.maToTrinh, {"phangGap": True}))
            return p

        p.chanDaMo.append(y.chan[1])
        p.chuyen("DA_PHONG_HO", "hai chân đã vào, delta ≈ 0")
        p.chuyen("GIU", "vào xong")
        if so_cai:
            so_cai.ghi(ButToan("MO_VI_THE",
                               f"[MÔ PHỎNG] chân B {y.chan[1].ben} "
                               f"{y.chan[1].cang} — đã phòng hộ", 0.0,
                               y.chienLuoc, y.maToTrinh,
                               {"chan": y.chan[1].tom_tat()}))
        return p

    def tom_tat(self) -> dict:
        return {"moPhong": self.moPhong, "soPhien": self.soPhien,
                "soPhangGap": self.soPhangGap,
                "tranChuaPhongHoGiay": TRAN_CHUA_PHONG_HO_GIAY,
                "loiNhac": "Lớp ký lệnh CHƯA TỒN TẠI. Không cấu hình nào "
                           "biến mô phỏng thành thật ở bản này."}


def _bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")
