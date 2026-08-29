"""THÔNG CHÍNH TY — nơi mọi tờ trình đi qua.

Thông Chính Ty là sở quan nhận mọi tờ trình từ các nha môn rồi chuyển lên
trên. Không nha môn nào được trình thẳng, và không nha môn nào được nói
chuyện riêng với nha môn khác.

    KHÔNG:  Perp → Lending → DEX          (mười ba ty gọi chéo nhau)

    MÀ:     Perp ────┐
            Lending ─┤
            DEX ─────┼──►  THÔNG CHÍNH TY  ──►  Trung Ương
            Yield ───┤
            …    ────┘

Vì sao cấm gọi chéo: mười ba ty gọi thẳng nhau là 13×12 = 156 đường có thể
có, và mỗi đường là một chỗ hai ty ngầm phụ thuộc vào nhau. Qua một cửa thì
chỉ có 13 đường, và Trung Ương thấy hết.

## Đây KHÔNG phải `bac/bus.py`

`bac/bus.py` là sổ nhật ký trong RAM cho buồng lái đọc. Trùng chữ "bus"
trong tiếng Anh nhưng khác hẳn việc: nó không nhận tờ trình, không có ai
đăng ký, và không cơ hội nào đi qua nó.

## Trong tiến trình trước, IPC sau

Hiện mọi ty chạy chung một tiến trình nên đây chỉ là một hàng đợi trong bộ
nhớ. Ngày nào MEV cần tiến trình riêng (nó cần dưới giây), chỗ này thành
ranh giới IPC thật — nhưng **hợp đồng không đổi**, vì các ty vốn đã chỉ biết
`nop()` chứ không biết ai nhận.

Thiết kế trong-tiến-trình trước là có chủ ý: dựng IPC khi mới có một ty là
dựng một đường ống cho một người đi.
"""
from __future__ import annotations

import threading
from collections import deque


class ThongChinh:
    """Hàng đợi tờ trình, có trần, an toàn nhiều luồng."""

    def __init__(self, tran: int = 2000) -> None:
        self._khoa = threading.Lock()
        self._hang: deque = deque(maxlen=tran)
        self.tongNhan = 0
        self.tongSaiKhuon = 0
        self.tongTran = 0            # số tờ bị đẩy ra vì hàng đầy
        self.theoTy: dict[str, int] = {}
        self.saiKhuonTheoTy: dict[str, int] = {}

    def nop(self, tt) -> bool:
        """Ty nộp một tờ trình. False nếu sai khuôn — **chết ở cửa**.

        Tờ sai khuôn không được vào hàng, và đó là chủ ý: để nó trôi vào
        trong thì ba tháng sau có người gộp thống kê và không hiểu vì sao
        `netUocBps` của vài trăm bản ghi là `None`. Chết ở cửa thì lỗi hiện
        ra ngay tại ty đã gửi, kèm tên ty.
        """
        if not tt.hop_le:
            with self._khoa:
                self.tongSaiKhuon += 1
                k = tt.chienLuoc or "?"
                self.saiKhuonTheoTy[k] = self.saiKhuonTheoTy.get(k, 0) + 1
            return False
        with self._khoa:
            if len(self._hang) == self._hang.maxlen:
                self.tongTran += 1
            self._hang.append(tt)
            self.tongNhan += 1
            self.theoTy[tt.chienLuoc] = self.theoTy.get(tt.chienLuoc, 0) + 1
        return True

    # Từng có `dang_ky_nghe()` và một vòng phát tin cho người nghe ở đây.
    # Không tầng nào đăng ký, chưa bao giờ — nên mỗi lần nộp tờ trình đều
    # sao chép một danh sách rỗng dưới khoá, hai nghìn lần mỗi vòng, cho một
    # tính năng không ai dùng. Gỡ đi. Cần phát tin thì `bus.ghi()` đã có
    # sẵn và đang chạy thật; dựng lại một đường thứ hai chỉ vì nó nghe hay
    # là dựng một đường không ai đi.

    def lay_het(self) -> list:
        """Lấy trọn hàng đợi và dọn sạch. Trung Ương gọi mỗi lượt."""
        with self._khoa:
            ra = list(self._hang)
            self._hang.clear()
            return ra

    def tom_tat(self) -> dict:
        with self._khoa:
            return {
                "dangCho": len(self._hang), "tran": self._hang.maxlen,
                "tongNhan": self.tongNhan,
                "tongSaiKhuon": self.tongSaiKhuon,
                "tongTran": self.tongTran,
                "theoTy": dict(self.theoTy),
                "saiKhuonTheoTy": dict(self.saiKhuonTheoTy),
            }
