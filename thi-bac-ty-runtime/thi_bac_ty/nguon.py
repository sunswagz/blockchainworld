"""DATA WORLD v0.1 — kỷ luật chung khi đọc một nguồn, không phải một schema.

Bản đồ đòi một lớp "Data World" để bốn engine không mỗi cái tự viết một
adapter Binance. Nhưng hiện có **hai** ty, và chúng đọc hai thế giới không
giao nhau: `bac/` đọc bốn sàn perp, `tin_dung/` đọc DefiLlama. Không có
adapter nào trùng để mà gộp.

Nên file này KHÔNG cố dựng một `MarketQuote` vạn năng. Thiết kế một schema
dùng chung từ hai người dùng chẳng chia sẻ gì là đúng loại trừu tượng hoá
suy diễn sẽ phải viết lại ở người dùng thứ ba.

Thứ **thật sự** dùng chung, và đã được `bac/` chứng minh qua hàng nghìn lượt
quét, là **kỷ luật**:

    1. mọi lượt hỏi để lại dấu — hỏng cũng phải để lại dấu
    2. số từ ngoài vào phải qua bộ lọc NaN/inf trước khi thành số
    3. dữ liệu có TUỔI, và tuổi phải đọc được từ bên ngoài

Ba thứ ấy trích ra đây. Ngày Basis hoặc Options tới — chúng cũng đọc
Binance như `bac/` — mới là ngày có hai adapter trùng nhau để mà gộp, và
lúc ấy schema chung sẽ được thiết kế từ ba người dùng THẬT.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod


class SucKhoeNguon:
    """Nguồn này có đang sống không — và đừng để nó chết trong im lặng.

    Một nguồn hỏng mà bảng vẫn hiện đủ những nguồn còn lại thì người xem đọc
    thành *"thị trường không có gì"*, trong khi sự thật là *"mình đang mù một
    mắt"*. Nên mọi lượt hỏi đều để lại dấu ở đây, và buồng lái hiện nó cạnh
    từng nguồn chứ không gộp vào một dòng chung.
    """

    def __init__(self, ten: str) -> None:
        self.ten = ten
        self.tongLuot = 0
        self.soLoi = 0
        self.loiCuoi: str | None = None
        self.lanCuoiOkMs: float = 0.0
        self.treTrungBinhMs: float | None = None

    def ghi_ok(self, treMs: float) -> None:
        self.tongLuot += 1
        self.lanCuoiOkMs = time.time() * 1000.0
        # Trung bình trượt, nghiêng về quá khứ (0,7/0,3): một lượt chậm bất
        # thường không được kéo cả con số đi, nhưng chậm dần thì phải thấy.
        self.treTrungBinhMs = (treMs if self.treTrungBinhMs is None
                               else self.treTrungBinhMs * 0.7 + treMs * 0.3)

    def ghi_loi(self, e: BaseException) -> None:
        self.tongLuot += 1
        self.soLoi += 1
        self.loiCuoi = f"{type(e).__name__}: {e}"

    def tuoi_giay(self) -> float | None:
        """`None` = CHƯA BAO GIỜ đọc được, khác hẳn `0` = vừa đọc xong."""
        if self.lanCuoiOkMs <= 0:
            return None
        return (time.time() * 1000.0 - self.lanCuoiOkMs) / 1000.0

    @property
    def songSot(self) -> bool:
        return self.lanCuoiOkMs > 0

    def tom_tat(self) -> dict:
        return {
            "ten": self.ten, "tongLuot": self.tongLuot, "soLoi": self.soLoi,
            "loiCuoi": self.loiCuoi, "tuoiGiay": self.tuoi_giay(),
            "treTrungBinhMs": self.treTrungBinhMs,
            "songSot": self.songSot,
        }


class Nguon(ABC):
    """Một nguồn dữ liệu. **Chỉ đọc dữ liệu CÔNG KHAI.**

    Không khoá, không ký, không lệnh. Ngày một lớp con cần khoá là ngày nó
    thôi là nguồn và trở thành thứ khác — và thứ khác ấy phải đi qua Điều
    Phối Thực Thi, không qua đây.
    """

    ten: str = "?"

    def __init__(self) -> None:
        self.suc_khoe = SucKhoeNguon(self.ten)

    @abstractmethod
    async def doc(self, client) -> list:
        """Đọc một lượt. Lỗi thì ghi vào `suc_khoe` và trả `[]`, KHÔNG ném.

        Không ném vì một nguồn hỏng không được kéo theo cả vòng quét — nhưng
        `suc_khoe.soLoi` phải tăng, để cái chết ấy đếm được.
        """


def so_hoac_none(v):
    """Số từ ngoài vào, hoặc `None`. Chặn NaN và inf ngay tại cửa.

    NaN lọt vào một phép so sánh sẽ làm mọi so sánh trả về False — kể cả
    `x > tran` lẫn `x <= tran` — nên một cửa rủi ro gặp NaN sẽ *không chặn*
    và cũng *không báo*. Đó là lý do bộ lọc này đứng ở cửa chứ không ở giữa.
    """
    if v in (None, "", "null"):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f and abs(f) != float("inf") else None


def nguyen_hoac_none(v):
    f = so_hoac_none(v)
    return None if f is None else int(f)
