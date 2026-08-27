"""NHẬP SỔ NGOÀI — kết toán của cỗ máy khác vào MỘT sổ cái duy nhất.

Bước 3 của món nợ hai cỗ máy: *"chuyển `ket_toan.py` sang `so_cai.py`"*.

Chuyển theo nghĩa đen thì không làm được, và đó không phải sự lười: hai
runtime là hai tiến trình, hai vòng đời. Bắt cỗ máy kia ghi thẳng vào SQLite
của Thị Bạc Ty là hai tiến trình cùng ghi một file, và là buộc chúng thành
một — đúng thứ `von_ngoai.py` đã từ chối làm và nêu lý do.

Nhưng **mục đích** của bước 3 thì đạt được: một sổ của sự thật, một lãi lỗ,
một NAV. Cách đạt là ĐỌC kết toán cỗ máy kia rồi ghi vào sổ này, y hệt lối
`von_ngoai.py` đọc ví nó.

## Hai chuyện phải làm đúng, và cái thứ hai mới khó

**1 · Không đếm hai lần.** Cỗ máy kia đưa cùng một bản ghi ở mọi lượt hỏi.
Ghi lại mỗi lượt là nhân lãi lỗ lên gấp số lượt hỏi. Nên mỗi bản ghi có một
KHOÁ ổn định — `<nguồn>:<slug>:<luc>` — và sổ nhập nhớ khoá nào đã vào.

**2 · Bỏ sót phải TỰ LỘ RA.** `/api/trang-thai` chỉ đưa **12 bản ghi gần
nhất**. Kết toán hơn 12 lần giữa hai lượt hỏi thì phần giữa mất hẳn, và mất
trong im lặng — sổ vẫn cân, vẫn không lỗi, chỉ thiếu tiền.

Nên sổ nhập theo dõi `daKetToan` — tổng số bản ghi cỗ máy kia tự đếm. Số ấy
nhảy nhiều hơn số bản ghi mới ta nhận được thì **có bỏ sót**, và nó đi vào
`soBoSot` chứ không biến mất. Một sổ cái nói "tôi đủ" trong khi thiếu thì
tệ hơn hẳn một sổ cái nói "tôi thiếu N bản ghi".

Đây là cùng một bài học `moHinhPhiDuChua` dạy ở tầng cơ hội, nâng lên tầng
sổ sách: con số không tự nói nó thiếu gì thì người đọc phải đoán, và họ sẽ
đoán là nó đủ.

## Trung Ương KHÔNG biết cỗ máy nào tồn tại

Lớp này nhận `(ten, url)` từ ngoài vào, đúng như `DocVonNgoai`. Không dòng
MÃ nào ở đây nhắc tên một cỗ máy hay một ty; cấu hình nằm ở `bac/config.py`,
ngoài Trung Ương.

Văn giải thích thì được nêu tên — `von_ngoai.py` kể thẳng chuyện Khâm Thiên
Giám, và đó là tài liệu tốt. Ràng buộc nằm ở chỗ MÃ không phụ thuộc, không
ở chỗ văn xuôi phải câm.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from .so_cai import ButToan

HET_GIO_GIAY = 4.0

#: Bao lâu hỏi lại. Kết toán không xảy ra theo giây, và hỏi dồn dập không
#: làm bản ghi tới sớm hơn.
NHIP_GIAY = 120.0


class NhapSoNgoai:
    """Đọc kết toán một cỗ máy ngoài, ghi vào Sổ Cái, KHÔNG đếm hai lần."""

    def __init__(self, ten: str, url: str, chienLuoc: str,
                 duongDan: str = "ketToan") -> None:
        self.ten = ten
        self.url = url
        #: Mã chiến lược để `lai_lo_theo_chien_luoc()` gộp đúng chỗ.
        self.chienLuoc = chienLuoc
        self.duongDan = duongDan
        self._daVao: set[str] = set()
        self.soDaVao = 0
        self.soBoSot = 0
        self.soLoi = 0
        self.docDuoc = False
        self.vi = ""
        self.lanCuoiMs = 0.0
        self._demTruoc: int | None = None
        self._lanHoi = 0.0

    # ── đọc ─────────────────────────────────────────────────────────────
    def _doc(self) -> dict | None:
        try:
            rq = urllib.request.Request(
                self.url, headers={"User-Agent": "thi-bac-ty/0.1 (read-only)"})
            with urllib.request.urlopen(rq, timeout=HET_GIO_GIAY) as r:
                d = json.load(r)
            self.docDuoc, self.vi = True, ""
            self.lanCuoiMs = time.time() * 1000.0
            return d if isinstance(d, dict) else None
        except (urllib.error.URLError, OSError, ValueError) as e:
            self.docDuoc = False
            self.soLoi += 1
            self.vi = f"{type(e).__name__}: {str(e)[:90]}"
            return None

    def den_han(self) -> bool:
        return time.time() - self._lanHoi >= NHIP_GIAY

    # ── nhập ────────────────────────────────────────────────────────────
    def nhap(self, soCai) -> dict:
        """Một lượt nhập. Trả về những gì đã xảy ra, kể cả phần bỏ sót."""
        self._lanHoi = time.time()
        d = self._doc()
        if d is None:
            return {"moi": 0, "boSot": 0, "docDuoc": False, "vi": self.vi}

        kt = d.get(self.duongDan) or {}
        ganDay = kt.get("ganDay") or []
        dem = kt.get("daKetToan")

        moi = 0
        for x in ganDay:
            k = self._khoa(x)
            if k in self._daVao:
                continue
            bt = self._but_toan(x, k)
            if bt is None or not soCai.ghi(bt):
                continue
            self._daVao.add(k)
            self.soDaVao += 1
            moi += 1

        boSot = self._do_bo_sot(dem, len(ganDay), moi)
        return {"moi": moi, "boSot": boSot, "docDuoc": True,
                "daKetToanBenKia": dem, "vi": ""}

    def _do_bo_sot(self, dem, soThay: int, soMoi: int) -> int:
        """Cỗ máy kia đếm được bao nhiêu, ta nhận được bao nhiêu.

        Chỉ đo được khi bên kia CÔNG BỐ tổng số. Không công bố thì ta không
        biết mình thiếu — và `boSotDoDuoc=False` nói đúng câu ấy thay vì để
        `soBoSot=0` giả vờ là không thiếu gì.
        """
        if not isinstance(dem, int):
            return 0
        truoc, self._demTruoc = self._demTruoc, dem
        if truoc is None:
            return 0
        # Bên kia cắt `xong` xuống 200 nên `daKetToan` có thể GIẢM — và
        # `max(0, ...)` dưới đây đã lo chuyện ấy: `tang` âm thì hiệu càng
        # âm, và kẹp về 0.
        #
        # Bản đầu còn một nhánh `if tang <= 0: return 0` đứng trước. Phép
        # cấy lỗi ngược cho thấy gỡ nó đi thì KHÔNG phép kiểm nào đỏ — nó
        # là văn giải thích đội lốt logic, và một nhánh không đổi được kết
        # quả làm người đọc tưởng có hai lớp bảo vệ trong khi chỉ có một.
        sot = max(0, (dem - truoc) - max(soMoi, 0))
        # Chỉ tính là bỏ sót khi cửa sổ `ganDay` đã đầy — chưa đầy thì ta
        # thấy hết mọi thứ bên kia có, và chênh lệch tới từ chỗ khác.
        if sot and soThay >= 12:
            self.soBoSot += sot
            return sot
        return 0

    @property
    def boSotDoDuoc(self) -> bool:
        return self._demTruoc is not None

    def _khoa(self, x: dict) -> str:
        return f"{self.ten}:{x.get('slug')}:{x.get('luc')}"

    def _but_toan(self, x: dict, khoa: str) -> ButToan | None:
        """Một bản ghi kết toán → một bút toán.

        `soTienUsd = 0` có chủ ý và phải nói rõ: cỗ máy kia công bố KẾT QUẢ
        (`upThang`) chứ không công bố lãi lỗ từng lần trong `ganDay`. Ghi
        một con số bịa vào cột tiền là làm hỏng đúng thứ sổ cái sinh ra để
        giữ, nên cột tiền để 0 và `chiTiet` nói thẳng là chưa có.

        Phần TIỀN của cỗ máy kia vẫn được thấy — qua `von_ngoai.py`, dưới
        dạng phơi nhiễm chỉ-đọc trong Danh Mục. Sổ này giữ phần SỰ KIỆN.
        """
        slug = x.get("slug")
        if not slug:
            return None
        return ButToan(
            loai="DONG_VI_THE",
            lyDo=f"kết toán ngoài · {self.ten} · {slug}",
            soTienUsd=0.0,
            chienLuoc=self.chienLuoc,
            maToTrinh=None,
            chiTiet={
                "nguon": self.ten, "khoa": khoa, "slug": slug,
                "ma": x.get("ma"), "upThang": x.get("upThang"),
                "pDuDoan": x.get("pDuDoan"), "coViThe": x.get("coViThe"),
                "batDong": x.get("batDong"), "lucBenKia": x.get("luc"),
                "tienChuaCo": ("cỗ máy kia không công bố lãi lỗ từng lần "
                               "trong `ganDay` — xem von_ngoai cho phần "
                               "tiền"),
            })

    # ── khai báo ────────────────────────────────────────────────────────
    def tom_tat(self) -> dict:
        return {
            "ten": self.ten, "url": self.url, "chienLuoc": self.chienLuoc,
            "docDuoc": self.docDuoc, "vi": self.vi, "soLoi": self.soLoi,
            "soDaVao": self.soDaVao,
            "soBoSot": self.soBoSot,
            "boSotDoDuoc": self.boSotDoDuoc,
            "daKetToanBenKia": self._demTruoc,
            "loiNhac": (
                "Bên kia chỉ đưa 12 bản ghi gần nhất. Kết toán hơn 12 lần "
                "giữa hai lượt hỏi thì phần giữa mất hẳn — `soBoSot` đếm ra "
                "được, và một sổ nói «tôi thiếu N» tốt hơn hẳn một sổ nói "
                "«tôi đủ» trong khi thiếu."),
        }
