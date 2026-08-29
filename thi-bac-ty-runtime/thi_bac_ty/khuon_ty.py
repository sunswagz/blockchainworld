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
        #: VÌ SAO cổng ty từ chối — xem `_ghi_ly_do`. Đây là cái lọc LỚN
        #: NHẤT của cả cỗ máy (99,98% cơ hội chết ở đây) và trước lượt này
        #: nó không khai một chữ nào.
        self.soBiTuChoi = 0
        self.soMaBiBo = 0
        self.lyDoTuChoi: dict[str, int] = {}
        self.cauViDu: dict[str, str] = {}
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

    # ── việc THỨ TƯ, không bắt buộc nhưng phải KHAI nếu không làm ─────────
    def ke_toan(self, viThe: list, toTrinh: dict,
                tuGiay: float, denGiay: float):
        """Vị thế này THU/MẤT bao nhiêu kể từ lần kế toán trước.

        Trả `KetToanVong`, hoặc `None` = **ty này chưa biết tự kế toán**.

        `None` KHÔNG phải 0. Trung Ương đếm số vị thế trả `None` và bày ra,
        vì "vị thế này thu 0" và "không ai biết vị thế này thu bao nhiêu"
        là hai câu khác hẳn — mà cộng vào NAV thì cả hai ra cùng con số.

        **Trả lời bằng cái ĐO ĐƯỢC, không bằng cái đã dự đoán.** Tờ trình
        có sẵn `netUocBps` và `giuGio`, nên cộng dồn theo tỉ lệ thời gian
        là ra ngay một đường lãi đẹp — và đó là trả lại chính con số máy
        đã đoán. Đường NAV khi ấy là bản sao của kỳ vọng, không phải của
        thị trường, và khoảng cách giữa hai thứ ấy — thứ đáng học nhất —
        biến mất. Xem `bac/chay_lai.py`.

        Nguồn đúng là dữ liệu ty VỪA QUÉT trong chính vòng này: rate sàn
        đang công bố, APY pool đang trả. Không quét được thì trả
        `KetToanVong(doDuoc=False)` chứ đừng trả 0.

        `viThe` là các chân đang mở (`danh_muc.ViThe`), `toTrinh` là tờ
        trình gốc đã `tom_tat()`, `tuGiay`/`denGiay` là khoảng thời gian
        cần kế toán (giây, đồng hồ hệ thống).
        """
        return None

    @classmethod
    def co_ke_toan(cls) -> bool:
        """Ty này có tự cài `ke_toan()` không. Dùng để KHAI, không để chặn."""
        return cls.ke_toan is not Ty.ke_toan

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
                qua, ly = self.xet(co)
            except Exception as e:                   # noqa: BLE001
                self.loiCuoi = f"xét lỗi: {type(e).__name__}: {e}"
                continue
            if not qua:
                self._ghi_ly_do(ly)
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

    #: Nhiều nhất ngần này MÃ lý do được giữ. Ty tự viết mã của mình, nên
    #: một ty lỡ nhét số vào mã (`"net-thap-2.31"`) sẽ đẻ ra vô hạn khoá.
    #: Trần này biến một lỗi rò bộ nhớ thành một dòng khai «có mã bị bỏ».
    TRAN_MA_LY_DO = 24

    def _ghi_ly_do(self, ly) -> None:
        """Đếm VÌ SAO cổng ty từ chối — theo MÃ, không theo câu.

        Trước lượt này dòng ấy viết `qua, _ = self.xet(co)`: lý do bị vứt
        ngay tại chỗ nó vừa được sinh ra. Hậu quả đo được trên máy sống
        30/08 — cổng ty là cái lọc LỚN NHẤT của cả cỗ máy:

            thanh-khoan   68.936 cơ hội thô  →  14 qua cổng ty
            phai-sinh      4.914             →   7
            quyen-chon     1.983             →   0

        99,98% số cơ hội chết ở đây, và không ai biết vì sao. Bảng «vì sao
        bị từ chối» của buồng lái chỉ đọc Sổ Đăng Ký, mà sổ chỉ có tờ
        trình — thứ chỉ ra đời SAU cổng này. Nên một ty hỏng (ngưỡng đặt
        sai, một trường luôn `None`, nguồn trả rác) trông hệt một ty đang
        từ chối đúng.

        Đếm theo MÃ chứ không theo câu: câu mang số bên trong, và gom theo
        câu thì một nguyên nhân vỡ thành hàng trăm dòng — đúng cái bẫy đã
        cắn ở bảng lý do của Sổ Đăng Ký.

        Một lần từ chối có thể mang NHIỀU mã. Mỗi mã đếm một lần cho lần
        ấy, nên tổng các mã có thể lớn hơn `soBiTuChoi` — mẫu số riêng là
        vì thế.
        """
        self.soBiTuChoi += 1
        thay = set()
        for x in (ly or ()):
            ma = x[0] if isinstance(x, (tuple, list)) and x else x
            ma = str(ma or "").strip() or "(khong-ma)"
            if ma in thay:
                continue
            thay.add(ma)
            if ma not in self.lyDoTuChoi:
                if len(self.lyDoTuChoi) >= self.TRAN_MA_LY_DO:
                    self.soMaBiBo += 1
                    continue
                self.lyDoTuChoi[ma] = 0
            # Câu ví dụ điền khi CHƯA CÓ, không chỉ lúc mã xuất hiện lần
            # đầu. Một mã gặp lần đầu ở dạng TRẦN (chuỗi, không kèm câu)
            # rồi lần sau mới kèm câu thì bản cũ giữ ô ví dụ rỗng vĩnh
            # viễn — mà `bac/ty_perp.py` trả về đúng dạng trần ấy suốt
            # nhiều tháng, nên đây không phải một ca hiếm. Ô ví dụ là
            # manh mối duy nhất người đọc có để hiểu một mã.
            if (ma not in self.cauViDu
                    and isinstance(x, (tuple, list)) and len(x) > 1):
                self.cauViDu[ma] = str(x[1])[:200]
            self.lyDoTuChoi[ma] += 1

    def tom_tat(self) -> dict:
        top = sorted(self.lyDoTuChoi.items(), key=lambda kv: -kv[1])[:5]
        # Mã KHÔNG kèm câu là nửa lời khai. `bac/ty_perp.py` trả về
        # `list(co.lyDoMa)` — mã trần, đúng `list[str]` chứ không phải
        # `list[tuple[str, str]]` mà chữ ký khai — và không ai thấy suốt
        # nhiều tháng vì `mot_luot()` vứt luôn vế thứ hai. Hai lỗi che
        # nhau, và lượt đầu tiên có người đọc vế ấy thì bảng hiện
        # «180× [net-am] » với một khoảng trắng ở cuối.
        thieuCau = sum(1 for k in self.lyDoTuChoi if not self.cauViDu.get(k))
        return {"ma": self.ma, "ho": self.ho, "moTa": self.moTa,
                "vonToiThieuKinhTeUsd": self.vonToiThieuKinhTeUsd,
                "soLuotQuet": self.soLuotQuet, "soCoHoi": self.soCoHoi,
                "soQuaCongTy": self.soQuaCongTy, "soTrinh": self.soTrinh,
                "soTrinhSaiKhuon": self.soTrinhSaiKhuon,
                "soBiTuChoi": self.soBiTuChoi,
                "soMaBiBo": self.soMaBiBo,
                "soMaThieuCau": thieuCau,
                "lyDoTuChoi": [{"ma": k, "so": v,
                                "cau": self.cauViDu.get(k, "")}
                               for k, v in top],
                "loiCuoi": self.loiCuoi}
