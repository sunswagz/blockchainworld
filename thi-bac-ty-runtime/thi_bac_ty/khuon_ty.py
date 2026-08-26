"""KHUÔN TY — thứ một ty mới phải điền, và **chỉ** được điền.

Mười hai thread còn lại sẽ cắm vào đây. Khuôn này tồn tại để mỗi thread biết
chính xác nó được xây cái gì, đầu ra phải là gì, và phần nào **không thuộc
quyền nó**.

## Một ty chỉ có ba việc

    quet()      hỏi thị trường của mình     → dữ liệu thô
    xet()       rủi ro CHUYÊN MÔN của mình  → PASS / REJECT
    trinh()     dịch sang ToTrinh           → nộp Thông Chính Ty

Hết. Không có việc thứ tư.

## Và bảy việc một ty KHÔNG được làm

    ✗ giữ tiền, biết NAV, biết ty khác đang giữ gì
    ✗ tự đặt trần vốn cho mình
    ✗ dựng Rủi Ro Tổng riêng
    ✗ gọi thẳng một ty khác
    ✗ đặt lệnh
    ✗ ghi thẳng vào Sổ Cái
    ✗ đóng/mở cầu dao

Bảy điều ấy thuộc Trung Ương. Không phải vì tập trung cho đẹp, mà vì mỗi
điều trong đó **cần nhìn thấy toàn bộ danh mục** — thứ mà theo định nghĩa
không ty nào nhìn thấy.

## `KHAI` là hợp đồng khai báo

Mỗi ty phải khai `ma`, `ho`, `moTa`. `Ty.kiem_khai()` soi khuôn, và Trung
Ương từ chối đăng ký một ty khai sai — chết ở cửa, không phải chết sau ba
tháng khi thống kê gộp nhầm hai chuỗi mã.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .to_trinh import HO, KHUON_CHIEN_LUOC


class Ty(ABC):
    """Lớp gốc cho mọi ty. Kế thừa và điền ba hàm."""

    #: `<họ>.<tên>.v<số>` — xem `to_trinh.KHUON_CHIEN_LUOC`
    ma: str = ""
    #: một trong `to_trinh.HO`
    ho: str = ""
    moTa: str = ""

    #: **Dưới ngần này thì kinh tế của engine không còn nghĩa.** Bắt buộc.
    #:
    #: Một ty không biết ngưỡng kinh tế của chính nó là một ty chưa nghĩ về
    #: chi phí cố định của mình — và nó sẽ đều đặn trình lên những cơ hội mà
    #: phí ăn sạch, để Rủi Ro Tổng loại hộ. Chuyển việc ấy sang trung ương
    #: là bắt trung ương biết chi phí của từng ngành, thứ nó không biết và
    #: không nên biết.
    #:
    #: Đây KHÔNG phải `phanBo.toiThieuMotLanUsd`: sàn ấy là của HỆ, chung
    #: cho mọi ty. Xem `to_trinh.ToTrinh.vonToiThieuKinhTeUsd`.
    vonToiThieuKinhTeUsd: float | None = None

    def __init__(self) -> None:
        self.soLuotQuet = 0
        self.soCoHoi = 0
        self.soQuaCongTy = 0
        self.soTrinh = 0
        self.soTrinhSaiKhuon = 0
        self.loiCuoi: str | None = None

    # ── ba việc, và chỉ ba ────────────────────────────────────────────────
    @abstractmethod
    def quet(self) -> list:
        """Hỏi thị trường của mình. Trả về danh sách cơ hội THÔ (nội bộ)."""

    @abstractmethod
    def xet(self, co) -> tuple[bool, list[tuple[str, str]]]:
        """Rủi ro CHUYÊN MÔN. `(qua, [(mã, câu)])`.

        Đây là tầng rủi ro THỨ NHẤT, và nó chỉ trả lời câu *"cơ hội này có
        hợp lệ không"*. Câu *"cho tiền vào đây thì danh mục ra sao"* thuộc
        Rủi Ro Tổng — đừng trả lời hộ.
        """

    @abstractmethod
    def trinh(self, co) -> object:
        """Dịch một cơ hội đã qua `xet()` thành `ToTrinh`."""

    # ── khuôn ─────────────────────────────────────────────────────────────
    @classmethod
    def kiem_khai(cls) -> list[str]:
        loi = []
        if not KHUON_CHIEN_LUOC.match(cls.ma or ""):
            loi.append(f"mã {cls.ma!r} sai khuôn <họ>.<tên>.v<số>")
        if cls.ho not in HO:
            loi.append(f"họ {cls.ho!r} không có trong {HO}")
        v = cls.vonToiThieuKinhTeUsd
        if v is None:
            loi.append("chưa khai `vonToiThieuKinhTeUsd` — một ty không biết "
                       "ngưỡng kinh tế của chính nó sẽ đều đặn trình lên "
                       "những cơ hội mà phí ăn sạch, để trung ương loại hộ")
        elif not (v > 0):
            loi.append(f"vốn tối thiểu kinh tế {v} phải > 0")
        if not (cls.moTa or "").strip():
            loi.append("thiếu mô tả — một ty không tự giới thiệu được thì "
                       "người sau đọc sổ đăng ký không biết nó làm gì")
        # Mã phải bắt đầu bằng họ hoặc một tên gần họ. Không ép cứng vì
        # `perpetual` ≠ `phai-sinh`; chỉ nhắc trong `moTa` là đủ.
        return loi

    # ── một lượt trọn vẹn ─────────────────────────────────────────────────
    def mot_luot(self, thong_chinh) -> list:
        """quét → xét → trình. Trung Ương gọi hàm này, không gọi ba hàm kia.

        Trả về danh sách tờ trình đã NỘP THÀNH CÔNG. Ty không được tự làm gì
        với chúng sau đó.
        """
        self.soLuotQuet += 1
        try:
            tho = self.quet()
        except Exception as e:                       # noqa: BLE001
            # Một ty chết KHÔNG được kéo theo Trung Ương và mười hai ty kia.
            self.loiCuoi = f"quét lỗi: {type(e).__name__}: {e}"
            return []

        ra = []
        for co in tho:
            self.soCoHoi += 1
            try:
                qua, _ = self.xet(co)
            except Exception as e:                   # noqa: BLE001
                self.loiCuoi = f"xét lỗi: {type(e).__name__}: {e}"
                continue
            if not qua:
                continue
            self.soQuaCongTy += 1
            try:
                tt = self.trinh(co)
            except Exception as e:                   # noqa: BLE001
                self.loiCuoi = f"trình lỗi: {type(e).__name__}: {e}"
                continue
            if thong_chinh.nop(tt):
                self.soTrinh += 1
                ra.append(tt)
            else:
                self.soTrinhSaiKhuon += 1
                self.loiCuoi = ("tờ trình sai khuôn: "
                                + "; ".join(tt.kiem()[:3]))
        return ra

    def tom_tat(self) -> dict:
        return {"ma": self.ma, "ho": self.ho, "moTa": self.moTa,
                "vonToiThieuKinhTeUsd": self.vonToiThieuKinhTeUsd,
                "soLuotQuet": self.soLuotQuet, "soCoHoi": self.soCoHoi,
                "soQuaCongTy": self.soQuaCongTy, "soTrinh": self.soTrinh,
                "soTrinhSaiKhuon": self.soTrinhSaiKhuon,
                "loiCuoi": self.loiCuoi}
