"""Sổ lệnh L2 — và phép đo quan trọng nhất hệ thống: VWAP theo khối lượng.

Đây là chỗ phần lớn chiến lược trông đẹp trên biểu đồ chết trong thực chiến.

Nhìn sổ lệnh này:

        ASK   0.53 x 1000
              0.50 x  400
              0.48 x  200
              0.46 x   80      <- best ask
        -----------------
        BID   0.44 x  300

Fair value mô hình = 0.55. Bảng điều khiển hiện "EDGE = 9c" vì nó lấy
`0.55 - 0.46`. Con số đó ĐÚNG cho đúng 80 cổ phần đầu tiên và sai cho mọi
khối lượng lớn hơn. Muốn 680 cổ thì giá thật là:

        (80 x 0.46 + 200 x 0.48 + 400 x 0.50) / 680 = 0.4894

tức edge thật còn 6,1c chứ không phải 9c — trước khi trừ phí, trượt giá và
sai số mô hình. Muốn cả 1.680 cổ trong sổ thì VWAP lên 0.5136 và edge chỉ
còn 3,6c: khối lượng vừa nhân lên 21 lần thì lợi thế mỗi cổ vừa mất 60%.

(Bốn con số trên do `scripts/selftest.py` tính lại mỗi lượt chạy. Bản viết
tay đầu tiên của chính khối chú thích này ghi 0.4859 và 6,4c — sai, vì tôi
nhẩm tay. Một ví dụ sai trong tài liệu còn tệ hơn không có ví dụ nào, nên
phép kiểm giữ luôn cả mấy con số này.)

Nên module này KHÔNG có hàm nào trả về "giá" mà không hỏi "bao nhiêu cổ".
`vwap_mua(q)` là cửa chính; `best_ask` tồn tại để hiển thị và để đo spread,
không phải để tính lợi thế.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Muc:
    """Một mức giá trong sổ. `gia` theo đô-la trên mỗi cổ, nằm trong 0..1."""
    gia: float
    luong: float


@dataclass
class KetQuaVwap:
    """Kết quả mô phỏng đi qua sổ để gom `muon` cổ."""
    muon: float
    khop: float           # thực sự gom được bao nhiêu; nhỏ hơn muon nếu sổ mỏng
    vwap: float           # giá trung bình theo khối lượng của phần khớp được
    giaCham: float        # mức giá tệ nhất phải chạm tới
    soMuc: int            # đi qua mấy mức
    tacDong: float        # chênh giữa vwap và mức tốt nhất; luôn không âm
    dayDu: bool           # sổ có đủ hàng cho toàn bộ `muon` không

    @property
    def thieu(self) -> float:
        return max(0.0, self.muon - self.khop)


@dataclass
class SoLenh:
    """Sổ lệnh một chiều outcome (UP hoặc DOWN) của một market.

    `bid` xếp giảm dần, giá cao nhất trước — bên người ta sẵn sàng MUA.
    `ask` xếp tăng dần, giá thấp nhất trước — bên người ta sẵn sàng BÁN.
    """
    ma: str
    ben: str                      # "UP" hoặc "DOWN"
    bid: list[Muc] = field(default_factory=list)
    ask: list[Muc] = field(default_factory=list)
    nhanLucMs: float = 0.0

    # ── đọc nhanh ─────────────────────────────────────────────────────────
    @property
    def best_bid(self) -> float | None:
        return self.bid[0].gia if self.bid else None

    @property
    def best_ask(self) -> float | None:
        return self.ask[0].gia if self.ask else None

    @property
    def spread(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return self.best_ask - self.best_bid

    @property
    def giua(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / 2.0

    def do_sau(self, quanh: float = 0.05) -> tuple[float, float]:
        """Tổng khối lượng nằm trong `quanh` đô quanh mức tốt nhất mỗi bên."""
        b = 0.0
        if self.best_bid is not None:
            b = sum(m.luong for m in self.bid if m.gia >= self.best_bid - quanh)
        a = 0.0
        if self.best_ask is not None:
            a = sum(m.luong for m in self.ask if m.gia <= self.best_ask + quanh)
        return b, a

    # ── hai phép đo mà dashboard hay gọi bằng tên kêu ─────────────────────
    def lech(self, quanh: float = 0.05) -> float | None:
        """Order-book imbalance trong khoảng -1..1. Dương là áp lực mua.

        `(bid - ask) / (bid + ask)`. Dashboard người ta hay gọi là "BOOK
        PRESSURE" hay "BOOK MEMBRANE"; nguyên liệu vẫn chỉ là sổ L2.
        """
        b, a = self.do_sau(quanh)
        tong = b + a
        if tong <= 0:
            return None
        return (b - a) / tong

    @property
    def vi_gia(self) -> float | None:
        """Microprice — mid có trọng số theo khối lượng ĐỐI DIỆN.

        Nhiều hàng ở bid nghĩa là giá đang bị đẩy về phía ask, nên khối lượng
        bid đánh trọng số cho giá ASK chứ không phải cho giá bid. Viết ngược
        là microprice chạy sai hướng — một lỗi không bao giờ ném exception,
        chỉ làm mọi tín hiệu dựa trên nó đảo chiều.
        """
        if not self.bid or not self.ask:
            return None
        qb, qa = self.bid[0].luong, self.ask[0].luong
        tong = qb + qa
        if tong <= 0:
            return self.giua
        return (qb * self.ask[0].gia + qa * self.bid[0].gia) / tong

    # ── cửa chính ─────────────────────────────────────────────────────────
    def vwap_mua(self, muon: float) -> KetQuaVwap:
        """Gom `muon` cổ bằng cách ăn dần bên ASK."""
        return _di_qua(self.ask, muon, mua=True)

    def vwap_ban(self, muon: float) -> KetQuaVwap:
        """Xả `muon` cổ bằng cách ăn dần bên BID."""
        return _di_qua(self.bid, muon, mua=False)

    # ── sổ này có dùng được không ─────────────────────────────────────────
    @property
    def hai_chieu(self) -> bool:
        return bool(self.bid) and bool(self.ask)

    @property
    def trai_ca_bang(self) -> bool:
        """Sổ trải gần hết dải 0..1 — dấu hiệu THANG CHỜ, không phải báo giá.

        Đo được trên Polymarket lúc dựng: một khung BTC 5 phút CHƯA MỞ có
        101 mức bid trải từ 0,001 tới 0,999, tổng hơn một triệu cổ. Nhìn số
        thì đó là "thanh khoản khổng lồ"; thực chất là nhà tạo lập rải một
        thang chờ suốt cả dải trước giờ mở, và không mức nào trong đó là
        một báo giá nghiêm túc về xác suất.

        Nguy hiểm nếu không nhận ra: `best_bid` của thang ấy là 0,999, nên
        mọi phép đo spread, microprice và imbalance đều ra số vô nghĩa —
        nhưng ra số, chứ không ra lỗi. Chiến thuật sẽ thấy "chợ tin UP
        99,9%" và mô hình sẽ thấy một lệch giá khổng lồ để ăn.
        """
        muc = self.bid or self.ask
        if len(muc) < 20:
            return False
        gia = [m.gia for m in muc]
        return (max(gia) - min(gia)) > 0.90

    @property
    def dung_duoc(self) -> bool:
        """Chỉ sổ hai chiều, không phải thang chờ, mới đáng để cân."""
        return self.hai_chieu and not self.trai_ca_bang

    def ly_do_khong_dung(self) -> str | None:
        if self.trai_ca_bang:
            return (f"thang chờ trải cả dải ({len(self.bid or self.ask)} mức, "
                    f"biên độ >0,90) — chưa phải báo giá thật")
        if not self.bid and not self.ask:
            return "sổ rỗng"
        if not self.ask:
            return "không có bên bán — không mua được"
        if not self.bid:
            return "không có bên mua — không bán được"
        return None

    def suc_chua(self, gioiHan: float, mua: bool = True) -> float:
        """Gom được nhiều nhất bao nhiêu cổ mà VWAP chưa vượt `gioiHan`.

        Đây là câu trả lời cho "cơ hội này to bằng nào" — thứ mà một con số
        edge trần trụi không nói được. Tài liệu nói rất đúng: edge 10c mà chỉ
        khớp được 4 đô thì kém hơn edge 1,2c khớp được 20.000 đô.

        Tìm bằng chia đôi, vì VWAP đơn điệu theo khối lượng: ăn thêm một mức
        bao giờ cũng làm giá trung bình tệ đi hoặc giữ nguyên, không bao giờ
        tốt lên. Nhờ tính đơn điệu đó phép chia đôi mới đúng.
        """
        muc = self.ask if mua else self.bid
        if not muc:
            return 0.0
        tong = sum(m.luong for m in muc)
        if tong <= 0:
            return 0.0

        # Ăn hết sổ mà VWAP vẫn trong hạn thì sức chứa là cả sổ.
        het = _di_qua(muc, tong, mua=mua)
        if het.khop > 0 and _trong_han(het.vwap, gioiHan, mua):
            return tong
        # Ngay mức đầu tiên đã vượt hạn thì sức chứa bằng 0, không phải "một ít".
        if not _trong_han(muc[0].gia, gioiHan, mua):
            return 0.0

        lo, hi = 0.0, tong
        for _ in range(48):
            giua = (lo + hi) / 2.0
            if giua <= 0:
                break
            r = _di_qua(muc, giua, mua=mua)
            if r.khop > 0 and _trong_han(r.vwap, gioiHan, mua):
                lo = giua
            else:
                hi = giua
        return lo


def _trong_han(gia: float, gioiHan: float, mua: bool) -> bool:
    """Mua thì giá phải không vượt hạn; bán thì phải không thấp hơn hạn."""
    return gia <= gioiHan + 1e-12 if mua else gia >= gioiHan - 1e-12


def _di_qua(muc: list[Muc], muon: float, mua: bool) -> KetQuaVwap:
    """Đi dọc các mức, gom cho đủ `muon`, trả về giá trung bình thật.

    Khớp một phần được coi là bình thường chứ không phải lỗi: sổ mỏng là một
    trạng thái có thật, và `dayDu=False` chính là thứ Risk Engine cần thấy.
    """
    if muon <= 0 or not muc:
        return KetQuaVwap(muon=max(0.0, muon), khop=0.0, vwap=0.0,
                          giaCham=muc[0].gia if muc else 0.0,
                          soMuc=0, tacDong=0.0, dayDu=muon <= 0)

    con = muon
    tien = 0.0
    khop = 0.0
    cham = muc[0].gia
    dem = 0
    for m in muc:
        if con <= 1e-12:
            break
        lay = min(con, m.luong)
        if lay <= 0:
            continue
        tien += lay * m.gia
        khop += lay
        con -= lay
        cham = m.gia
        dem += 1

    if khop <= 0:
        return KetQuaVwap(muon=muon, khop=0.0, vwap=0.0, giaCham=muc[0].gia,
                          soMuc=0, tacDong=0.0, dayDu=False)

    vwap = tien / khop
    best = muc[0].gia
    # Mua: VWAP cao hơn best là bất lợi. Bán: thấp hơn best là bất lợi.
    tac_dong = (vwap - best) if mua else (best - vwap)
    return KetQuaVwap(
        muon=muon, khop=khop, vwap=vwap, giaCham=cham, soMuc=dem,
        tacDong=max(0.0, tac_dong), dayDu=con <= 1e-9,
    )
