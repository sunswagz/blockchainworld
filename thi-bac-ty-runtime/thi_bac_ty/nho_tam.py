"""NHỚ TẠM — phép đếm CẢ SỔ không được nằm trong đường buồng lái.

Đo làn thật 05/09/2026: `/api/trang-thai` mất **45 giây** một lượt, hai
lần đo liền nhau ra 48,1s và 44,5s. Bốn câu quét toàn sổ nằm thẳng trong
đường ấy, và ba trong bốn không có chỉ mục nào đỡ được vì chúng cộng
TOÀN BỘ bảng:

    12,5s  SELECT COUNT(*), SUM(duyet) FROM co_hoi          782.415 dòng
    12,8s  SELECT loai, COUNT(*), SUM(soTienUsd) ... GROUP BY loai
    10,0s  SELECT chienLuoc, COUNT(*), SUM(soTienUsd) ... GROUP BY
     4,4s  SELECT COUNT(*), MIN(luc), MAX(luc) FROM but_toan  734.899 dòng

Cộng lại ≈ 41 giây, khớp đúng con số đo được ở đầu dây. Sổ chỉ nối thêm
chứ không sửa, nên mấy con số này còn phình mãi — đây là một cái chậm
LỚN DẦN, không phải một cái chậm cố định.

## Vì sao không phải là thêm chỉ mục

`SUM` trên toàn bảng phải đọc mọi dòng dù có chỉ mục hay không. Chỉ mục
chữa được câu CÓ `WHERE` hẹp; ba câu trên không có.

## Luật của lớp này

Lượt ĐẦU tính đồng bộ — không có gì để trả thì phải chờ. Từ lượt sau
luôn trả NGAY bản đang giữ, và nếu nó quá hạn thì làm mới ở một luồng
nền. Buồng lái không bao giờ chờ lần thứ hai.

**Tuổi phải đi kèm giá trị.** Một con số cũ mà trông như số sống là đúng
cái bẫy cả cỗ máy này được dựng để tránh; nơi gọi có nghĩa vụ bày
`tuoiGiay` ra chứ không giấu đi.
"""
from __future__ import annotations

import threading
import time

#: Hạn mặc định cho phép đếm CẢ ĐỜI SỔ. Năm phút.
#:
#: Mấy con số ấy là tổng tích luỹ từ ngày đầu — thêm một bút toán không
#: đổi được chữ số nào đáng kể. Ngắn hơn thì luồng nền chạy gần như liên
#: tục (mỗi lượt tính đã mất ~40 giây), tức đổi một cái chậm nhìn thấy
#: lấy một cái tốn CPU không nhìn thấy.
HAN_MAC_DINH_GIAY = 300.0

#: Tính nhanh hơn ngần này thì KHÔNG đệm — tính lại mỗi lượt.
#:
#: Bộ đệm có một cái giá: dòng vừa ghi bị che tới hết hạn. Trên sổ thật
#: cái giá ấy đáng trả (45 giây mỗi lượt hỏi), nhưng trên một sổ nhỏ thì
#: chỉ còn cái giá mà không còn cái lợi — và bộ kiểm đã bắt đúng chuyện
#: ấy: ghi một bút toán rồi hỏi ngay thì `chuaCo` vẫn báo sổ rỗng.
#:
#: Nên luật là TỰ CHỈNH theo cái đo được, không theo một cờ ai đó phải
#: nhớ bật: rẻ thì trả số sống, đắt thì mới đệm. Sổ phình dần qua ngưỡng
#: thì tự chuyển, không cần ai đổi gì.
NGUONG_DEM_GIAY = 0.25


class NhoTam:
    """Giữ kết quả một phép tính nặng, và khai tuổi của nó."""

    def __init__(self, hanGiay: float = HAN_MAC_DINH_GIAY,
                 nguongDemGiay: float = NGUONG_DEM_GIAY) -> None:
        self.hanGiay = float(hanGiay)
        #: Tham số chứ không hằng số toàn cục: phép kiểm phải ép được cả
        #: hai đường (đệm / không đệm) mà không phải `sleep` cho đủ chậm —
        #: một phép kiểm dựa trên `sleep` là một phép kiểm sẽ chớp đỏ.
        self.nguongDemGiay = float(nguongDemGiay)
        self._gia = None
        self._lucMs = 0.0
        self._khoa = threading.Lock()
        self._dangLam = False
        self.soLanTinh = 0
        self.soLanTraCu = 0
        #: Lượt tính gần nhất mất bao lâu — thước quyết định có đệm không.
        self.giayTinhCuoi = 0.0
        self.loiCuoi: str | None = None
        #: Luồng nền gần nhất. Giữ lại để phép kiểm `join()` được — không
        #: có nó thì đường làm-mới-ở-nền chỉ kiểm được bằng `sleep`, và
        #: một phép kiểm dựa trên `sleep` là một phép kiểm sẽ chớp đỏ.
        self.luongCuoi: threading.Thread | None = None
        #: Cách CHẠY lượt làm mới. Mặc định là dựng luồng nền; phép kiểm
        #: thay bằng một hàm chạy thẳng để ép được đường "nền đã xong
        #: TRƯỚC khi `lay()` trả về" — đường duy nhất phân biệt được bản
        #: chụp-trước với bản đọc-sau, và là đường đã có một con bọ thật.
        self.chay = None

    # ── đọc ───────────────────────────────────────────────────────────────
    def tuoi_giay(self) -> float:
        if not self._lucMs:
            return float("inf")
        return (time.time() * 1000.0 - self._lucMs) / 1000.0

    def qua_han(self) -> bool:
        return self.tuoi_giay() > self.hanGiay

    def dang_dem(self) -> bool:
        """Có đang đệm không — theo cái ĐO ĐƯỢC, không theo cờ khai."""
        return self.giayTinhCuoi > self.nguongDemGiay

    def lay(self, tinh):
        """`(giá trị, tuổi giây)`. Chỉ lượt đầu tiên là chờ."""
        with self._khoa:
            co = self._lucMs > 0.0
            qua = self.qua_han()
            khoi = co and qua and not self._dangLam and self.dang_dem()
            if khoi:
                self._dangLam = True
            # CHỤP trước khi dựng luồng nền. Đọc `self._gia` sau lúc ấy là
            # một cuộc đua: luồng nền kịp ghi đè thì hàm này trả về bản
            # MỚI trong khi vừa khai tuổi của bản CŨ — hai con số lệch
            # nhau mà không ai thấy. Bộ kiểm bắt được đúng chỗ này.
            gia, tuoi = self._gia, self.tuoi_giay()
        if not co:
            self._tinh(tinh)
            return self._gia, self.tuoi_giay()
        # Rẻ thì không đệm: tính lại ngay, và tuổi coi như 0. Đây là đường
        # đi của mọi sổ nhỏ, kể cả sổ của bộ kiểm.
        if not self.dang_dem():
            self._tinh(tinh)
            return self._gia, self.tuoi_giay()
        if khoi:
            if self.chay is not None:
                self.chay(lambda: self._tinh_nen(tinh))
            else:
                t = threading.Thread(target=self._tinh_nen, args=(tinh,),
                                     daemon=True)
                self.luongCuoi = t
                t.start()
        if qua:
            self.soLanTraCu += 1
        return gia, tuoi

    # ── tính ──────────────────────────────────────────────────────────────
    def _tinh(self, tinh) -> None:
        t0 = time.time()
        try:
            gia = tinh()
        except Exception as e:                            # noqa: BLE001
            # Giữ NGUYÊN bản cũ. Một lần tính hỏng không được biến con số
            # đang có thành `None`: buồng lái sẽ hiện ô trống và người đọc
            # kết luận «sổ rỗng» thay vì «lượt làm mới vừa hỏng».
            self.loiCuoi = f"{type(e).__name__}: {str(e)[:120]}"
            return
        self.giayTinhCuoi = time.time() - t0
        self._gia = gia
        self._lucMs = time.time() * 1000.0
        self.soLanTinh += 1
        self.loiCuoi = None

    def _tinh_nen(self, tinh) -> None:
        try:
            self._tinh(tinh)
        finally:
            with self._khoa:
                self._dangLam = False

    def tom_tat(self) -> dict:
        return {"tuoiGiay": round(self.tuoi_giay(), 3)
                if self._lucMs else None,
                "hanGiay": self.hanGiay, "soLanTinh": self.soLanTinh,
                "soLanTraCu": self.soLanTraCu, "loiCuoi": self.loiCuoi,
                "giayTinhCuoi": round(self.giayTinhCuoi, 4),
                "dangDem": self.dang_dem(),
                "nguongDemGiay": self.nguongDemGiay}
