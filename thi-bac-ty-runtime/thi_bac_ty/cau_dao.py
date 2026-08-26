"""CẦU DAO — quyền DỪNG TẤT CẢ, đứng cao hơn mọi ty.

Không ty nào được phép tự quyết định "thôi hôm nay nghỉ" cho cả hệ thống, và
cũng không ty nào được phép chạy tiếp khi cầu dao đã ngắt.

## Mười điều kiện, và chúng đều nói cùng một câu

    RPC hỏng · API sàn chập chờn · ĐỒNG HỒ LỆCH · lệch tài khoản ·
    lệch số dư · oracle lệch giá · sụt vốn quá ngưỡng · khoá riêng có vấn đề ·
    đòn bẩy ngoài dự tính · dữ liệu đứng

Câu chung: **"ta không còn chắc mình đang nhìn đúng thế giới"**. Và khi không
chắc mình nhìn đúng, thứ tệ nhất có thể làm là tiếp tục hành động tự tin.

**Bốn** trong mười điều kiện ấy runtime đã đo được, nên chúng nối vào đây
ngay, không phải chờ:

    lệch đồng hồ    `bac/dong_ho.py` — đã đo 447 giây thật
    dữ liệu đứng    tuổi báo giá theo từng cảng
    API chập chờn   `SucKhoe` của từng cảng
    sụt vốn         NAV so với vốn ban đầu trong `DanhMuc`

**Sáu điều kiện còn lại CHƯA nối, và liệt kê ra đây là có chủ ý.** Một cầu
dao kể tên mười điều kiện rồi chỉ canh bốn thì người đọc tưởng mình được
che mười — đúng lớp "bày cửa mà không nối" mà `bac/rui_ro.py` đã dính một
lần. Nên: sáu cái dưới đây KHÔNG được canh, và cạnh mỗi cái là thứ còn
thiếu để canh được.

    RPC hỏng            chưa có kết nối chuỗi nào
    lệch tài khoản      chưa đọc số dư sàn (`DanhMuc.nguonThat` = False)
    lệch số dư          như trên
    oracle lệch giá     chưa lấy giá oracle, mới có mark của sàn
    khoá riêng hỏng     KHÔNG có khoá nào trong runtime này
    đòn bẩy ngoài dự tính  chưa có vị thế thật để mà đo đòn bẩy

Cả sáu đều chờ cùng một thứ: **lớp đặt lệnh**. Ngày nó tồn tại là ngày phải
quay lại đây trước khi quay lại bất cứ đâu khác.

## Ngắt thì TỰ ĐỘNG, đóng lại thì PHẢI CÓ NGƯỜI

Đây là chỗ bất đối xứng có chủ ý. Ngắt tự động vì máy phát hiện nhanh hơn
người. Đóng lại phải có người vì máy không phân biệt được *"sự cố đã qua"*
với *"sự cố vẫn còn nhưng tín hiệu tạm im"* — và cái thứ hai chính là lúc
đóng lại thì mất tiền.

Ngoại lệ duy nhất: điều kiện có `tuMo=True` thì tự đóng lại khi hết — dành
cho những thứ đo được trực tiếp và không mơ hồ (đồng hồ đã khớp lại).
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass(frozen=True)
class LyDoNgat:
    ma: str
    moTa: str
    tuMo: bool = False        # True = tự đóng lại khi điều kiện hết
    luc: str = ""

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "moTa": self.moTa, "tuMo": self.tuMo,
                "luc": self.luc}


class CauDao:
    def __init__(self) -> None:
        self._khoa = threading.Lock()
        self._ngat: dict[str, LyDoNgat] = {}
        self.soLanNgat = 0
        self.lichSu: list[dict] = []

    # ── trạng thái ────────────────────────────────────────────────────────
    @property
    def dang_ngat(self) -> bool:
        with self._khoa:
            return bool(self._ngat)

    def cho_phep(self) -> tuple[bool, tuple[str, ...]]:
        """`(được phép hành động không, lý do đang chặn)`.

        Mọi tầng có thể cam kết vốn PHẢI gọi hàm này trước. Không gọi thì cầu
        dao chỉ là một biến không ai đọc.
        """
        with self._khoa:
            return (not self._ngat,
                    tuple(f"{l.ma}: {l.moTa}" for l in self._ngat.values()))

    # ── ngắt / đóng ───────────────────────────────────────────────────────
    def ngat(self, ma: str, moTa: str, tuMo: bool = False,
             so_cai=None) -> bool:
        """Ngắt vì một lý do. Trả về True nếu đây là lý do MỚI."""
        from .so_cai import ButToan
        with self._khoa:
            moi = ma not in self._ngat
            self._ngat[ma] = LyDoNgat(ma, moTa, tuMo, _bay_gio())
            if moi:
                self.soLanNgat += 1
                self.lichSu.append({"luc": _bay_gio(), "viec": "NGAT",
                                    "ma": ma, "moTa": moTa})
                self.lichSu = self.lichSu[-200:]
        if moi and so_cai:
            so_cai.ghi(ButToan("CAU_DAO", f"NGẮT — {ma}: {moTa}", 0.0,
                               None, None, {"tuMo": tuMo}))
        return moi

    def het_ly_do(self, ma: str) -> bool:
        """Điều kiện đã hết. Chỉ gỡ được nếu lý do ấy khai `tuMo=True`."""
        with self._khoa:
            l = self._ngat.get(ma)
            if l is None or not l.tuMo:
                return False
            del self._ngat[ma]
            self.lichSu.append({"luc": _bay_gio(), "viec": "TU_MO", "ma": ma,
                                "moTa": l.moTa})
            return True

    def dong_lai(self, ma: str, nguoi: str, so_cai=None) -> bool:
        """Người vận hành đóng lại một lý do. **Phải có tên người.**

        Không có tham số `nguoi` mặc định: đóng cầu dao là một hành động có
        trách nhiệm, và sổ cái phải ghi được ai đã làm.
        """
        from .so_cai import ButToan
        with self._khoa:
            l = self._ngat.pop(ma, None)
            if l is None:
                return False
            self.lichSu.append({"luc": _bay_gio(), "viec": "DONG_LAI",
                                "ma": ma, "nguoi": nguoi})
        if so_cai:
            so_cai.ghi(ButToan("CAU_DAO", f"ĐÓNG LẠI — {ma}, bởi {nguoi}",
                               0.0, None, None, {"lyDoGoc": l.moTa}))
        return True

    # ── tự soát từ trạng thái runtime ─────────────────────────────────────
    def tu_soat(self, *, lechDongHoGiay: float | None,
                cangChet: list[str], tuoiXauNhatGiay: float | None,
                sutVonPct: float | None, nguong: dict,
                so_cai=None) -> list[str]:
        """Soi trạng thái hiện tại, ngắt hoặc gỡ. Trả về lý do vừa ngắt.

        Gọi mỗi lượt. Đây là chỗ ba thứ runtime đã đo được nối vào cầu dao.
        """
        moi = []

        # 1. đồng hồ — tự mở lại được vì đo trực tiếp và không mơ hồ
        tran_dh = float(nguong.get("lechDongHoToiDaGiay", 60.0))
        if lechDongHoGiay is None:
            if self.ngat("dong-ho-chua-do",
                         "CHƯA đo được lệch đồng hồ — mọi phép đếm mốc đang "
                         "chạy trên giờ máy", True, so_cai):
                moi.append("dong-ho-chua-do")
        else:
            self.het_ly_do("dong-ho-chua-do")
            if abs(lechDongHoGiay) > tran_dh:
                if self.ngat("dong-ho-lech",
                             f"đồng hồ lệch {lechDongHoGiay:.0f}s > trần "
                             f"{tran_dh:.0f}s", True, so_cai):
                    moi.append("dong-ho-lech")
            else:
                self.het_ly_do("dong-ho-lech")

        # 2. cảng chết — mù một mắt thì không được cam kết vốn
        toi_da_chet = int(nguong.get("soCangChetToiDa", 0))
        if len(cangChet) > toi_da_chet:
            if self.ngat("cang-chet",
                         f"{len(cangChet)} cảng không lấy được dữ liệu: "
                         f"{', '.join(cangChet)}", True, so_cai):
                moi.append("cang-chet")
        else:
            self.het_ly_do("cang-chet")

        # 3. dữ liệu đứng
        tran_tuoi = float(nguong.get("tuoiToiDaGiay", 300.0))
        if tuoiXauNhatGiay is not None and tuoiXauNhatGiay > tran_tuoi:
            if self.ngat("du-lieu-dung",
                         f"báo giá cũ nhất {tuoiXauNhatGiay:.0f}s > trần "
                         f"{tran_tuoi:.0f}s", True, so_cai):
                moi.append("du-lieu-dung")
        else:
            self.het_ly_do("du-lieu-dung")

        # 4. sụt vốn — KHÔNG tự mở lại. Sụt vốn là hậu quả, không phải tín
        #    hiệu; nó "hết" không có nghĩa là nguyên nhân đã hết.
        tran_sut = float(nguong.get("sutVonToiDaPct", 10.0))
        if sutVonPct is not None and sutVonPct > tran_sut:
            if self.ngat("sut-von",
                         f"sụt vốn {sutVonPct:.1f}% > trần {tran_sut:.1f}% — "
                         f"phải có người xem lại mới đóng lại được",
                         False, so_cai):
                moi.append("sut-von")
        return moi

    def tom_tat(self) -> dict:
        with self._khoa:
            return {
                "dangNgat": bool(self._ngat),
                "lyDo": [l.tom_tat() for l in self._ngat.values()],
                "soLanNgat": self.soLanNgat,
                "lichSu": self.lichSu[-20:],
            }


def _bay_gio() -> str:
    import datetime as dt
    return dt.datetime.now(dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")
