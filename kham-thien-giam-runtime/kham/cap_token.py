"""Cặp token bù trừ — UP và DOWN của cùng một market là MỘT sổ nhìn hai phía.

Đây là chỗ tôi mô hình hoá sai ở bản đầu, và sai hẳn về cấu trúc chứ không
phải sai một con số.

## Đo được trên Polymarket

Một khung BTC 5 phút, đọc `/book` cho cả hai token cùng lúc:

    token UP   : 101 bid, 0 ask   · đỉnh bid 0.9990 x 134255
    token DOWN : 0 bid, 101 ask   · đáy  ask 0.0010 x 134255

Cùng khối lượng, giá cộng lại đúng 1,000. Đó KHÔNG phải trùng hợp: trong
Conditional Token Framework, một cặp UP+DOWN luôn đổi được lấy đúng $1, nên

    mua UP ở giá p   ≡   bán DOWN ở giá (1 − p)

Một lệnh duy nhất nằm trong sổ hiện ra ở CẢ HAI token, soi gương qua trục
0,5. API đã làm sẵn phép soi gương đó.

## Hai hệ quả phải nhớ

1. **Đừng cộng thanh khoản hai token.** "101 mức bên UP cộng 101 mức bên
   DOWN = 202 mức" là đếm hai lần cùng một khối tiền.

2. **Sổ một chiều là chuyện bình thường, không phải hỏng.** UP không có ask
   nghĩa là không ai muốn mua DOWN — hoàn toàn có thể xảy ra. Cái phải
   phát hiện không phải "một chiều" mà là **thang chờ trải cả dải**, thứ
   trông như thanh khoản nhưng không phải báo giá.

## Vì sao có lớp này thay vì sửa thẳng `so_lenh.py`

`so_lenh.py` giữ đúng một việc: toán trên MỘT sổ. Nó không nên biết token
nào bù trừ với token nào — nếu biết thì nó phải mang theo khái niệm market,
và mọi phép kiểm số học của nó sẽ cần dựng cả một market giả để chạy.

Lớp này giữ phần quan hệ. Nó là chỗ duy nhất được phép nói câu "giá của
UP suy ra từ giá của DOWN".
"""
from __future__ import annotations

from dataclasses import dataclass

from .so_lenh import Muc, SoLenh


def soi_guong(so: SoLenh, maMoi: str, benMoi: str) -> SoLenh:
    """Dựng sổ của token đối diện bằng cách soi gương qua trục 0,5.

    bid ở giá p  ->  ask ở giá (1 − p)
    ask ở giá p  ->  bid ở giá (1 − p)

    Dùng khi API chỉ trả một phía, hoặc để KIỂM CHÉO: soi gương sổ UP rồi so
    với sổ DOWN thật; lệch nhau là một trong hai đường đọc có vấn đề.
    """
    return SoLenh(
        ma=maMoi, ben=benMoi,
        bid=sorted((Muc(1.0 - m.gia, m.luong) for m in so.ask),
                   key=lambda x: x.gia, reverse=True),
        ask=sorted((Muc(1.0 - m.gia, m.luong) for m in so.bid),
                   key=lambda x: x.gia),
        nhanLucMs=so.nhanLucMs,
    )


@dataclass
class CapSo:
    """Hai sổ của một market, kèm những phép đo chỉ tồn tại khi có cả hai."""
    ma: str
    up: SoLenh
    down: SoLenh

    # ── sổ có đáng tin không ──────────────────────────────────────────────
    @property
    def dung_duoc(self) -> bool:
        return self.up.dung_duoc or self.down.dung_duoc

    def ly_do_khong_dung(self) -> str | None:
        if self.dung_duoc:
            return None
        u = self.up.ly_do_khong_dung()
        d = self.down.ly_do_khong_dung()
        if u and d and u == d:
            return f"cả hai token: {u}"
        return f"UP: {u or 'ổn'} · DOWN: {d or 'ổn'}"

    # ── kiểm chéo ────────────────────────────────────────────────────────
    def lech_soi_guong(self) -> float | None:
        """Chênh giữa sổ DOWN thật và ảnh soi gương của sổ UP.

        Bằng 0 nghĩa là hai đường đọc nhất quán. Lệch lớn nghĩa là một trong
        hai sổ đã cũ, hoặc API đang trả hai lát cắt ở hai thời điểm khác
        nhau — và khi đó mọi phép cân giá cặp đều dựa trên số không cùng
        thời, thứ hỏng im lặng.

        None khi thiếu dữ liệu để so.
        """
        anh = soi_guong(self.up, self.ma, "DOWN")
        a, b = anh.best_ask, self.down.best_ask
        if a is None or b is None:
            return None
        return abs(a - b)

    # ── giá tổng hợp ─────────────────────────────────────────────────────
    def gia_mua(self, ben: str) -> float | None:
        """Giá tốt nhất để MUA `ben`, đã tính cả đường bù trừ.

        Mua UP có hai lối: ăn ask của token UP, hoặc khớp với người mua DOWN
        (hiện ra thành ask của UP sau khi API soi gương). Lấy lối rẻ hơn.
        """
        so = self.up if ben == "UP" else self.down
        kia = self.down if ben == "UP" else self.up
        truc_tiep = so.best_ask
        qua_bu_tru = (1.0 - kia.best_bid) if kia.best_bid is not None else None
        ds = [x for x in (truc_tiep, qua_bu_tru) if x is not None]
        return min(ds) if ds else None

    @property
    def tong_gia_mua(self) -> float | None:
        """Chi phí mua một CẶP ở giá tốt nhất. Dưới 1,00 là có lệch giá.

        Đây chính là con số `PAIR COST` mà mọi dashboard kiểu này khoe, và
        là thứ `powerwinner` để lại dấu vết: UP 32,9¢ + DOWN 66,2¢ = 99,1¢.
        """
        u, d = self.gia_mua("UP"), self.gia_mua("DOWN")
        if u is None or d is None:
            return None
        return u + d

    def tom_tat(self) -> dict:
        return {
            "ma": self.ma,
            "dungDuoc": self.dung_duoc,
            "lyDo": self.ly_do_khong_dung(),
            "thangCho": self.up.trai_ca_bang or self.down.trai_ca_bang,
            "lechSoiGuong": self.lech_soi_guong(),
            "giaMuaUp": self.gia_mua("UP"),
            "giaMuaDown": self.gia_mua("DOWN"),
            "tongGiaMua": self.tong_gia_mua,
        }
