"""Đồ Thị Chợ — so mỗi market với FAIR VALUE CỦA CHÍNH NÓ, không so giá thô.

Đây là phiên bản có nghĩa của cái "EDGE MATRIX" / "quả cầu neural" mà các
dashboard hay khoe. Nguyên liệu chỉ là mấy con số đã có; giá trị nằm ở chỗ
so cho đúng.

## Cái sai mà đồ thị này tồn tại để chặn

Một cú BTC đi lên. Khung 5 phút hiện tại nhảy UP từ 50¢ lên 68¢, trong khi
khung 5 phút KẾ TIẾP còn quanh 54¢. Phản xạ tự nhiên: "khung sau rẻ, mua".

Sai. Hai khung có **strike khác nhau** và **thời gian còn lại khác nhau**,
nên giá thô của chúng không so được với nhau. Khung sau rẻ hơn có thể vì nó
ĐÁNG rẻ hơn.

Cách so đúng là quy mỗi khung về độ lệch của CHÍNH NÓ:

    lech = fairValue(khung) − giaCho(khung)

rồi mới đem các `lech` so với nhau. Một khung lệch +7 điểm trong khi cả rổ
lệch trung bình +1 điểm là một tín hiệu; một khung giá 54¢ cạnh một khung
giá 68¢ thì không nói lên gì cả.

## Chuẩn hoá theo độ ồn

Ngay cả `lech` cũng chưa so được thẳng: khung sắp đóng có bất định lớn hơn
hẳn khung mới mở, nên +5 điểm ở hai chỗ không cùng ý nghĩa. Chia cho bất
định của chính khung đó:

    z = lech / batDinh

Đây chính là "Relative Score" mà tài liệu gợi ý, viết bằng đại lượng runtime
đã có sẵn thay vì cần một chuỗi lịch sử chưa tồn tại.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .kho_doi import he_so_tuong_quan, nhom_tai_san


@dataclass
class Nut:
    """Một khung trên đồ thị."""
    ma: str
    slug: str
    nhom: str                    # BTC / ETH / SOL...
    conLaiGiay: float
    fairUp: float
    giaChoUp: float | None
    batDinh: float
    thanhKhoan: float = 0.0

    @property
    def lech(self) -> float | None:
        if self.giaChoUp is None:
            return None
        return self.fairUp - self.giaChoUp

    @property
    def z(self) -> float | None:
        l = self.lech
        if l is None or self.batDinh <= 0:
            return None
        return l / self.batDinh


@dataclass
class Canh:
    """Quan hệ giữa hai nút."""
    a: str
    b: str
    tuongQuan: float
    lechZ: float                 # |z_a − z_b|
    cungNhom: bool

    @property
    def dang_chu_y(self) -> bool:
        """Hai khung tương quan cao mà lệch z lớn — chỗ đáng nhìn.

        Tương quan cao nghĩa là chúng chịu chung một cú. Nếu chung một cú mà
        một cái đã phản ứng còn cái kia chưa, đó là chênh lệch có nguyên
        nhân cấu trúc chứ không phải nhiễu.
        """
        return self.tuongQuan >= 0.75 and self.lechZ >= 1.5


class DoThi:
    def __init__(self) -> None:
        self.nut: dict[str, Nut] = {}

    def dat(self, n: Nut) -> None:
        self.nut[n.ma] = n

    def xoa(self, ma: str) -> None:
        self.nut.pop(ma, None)

    # ── phép đo ───────────────────────────────────────────────────────────
    def canh(self) -> list[Canh]:
        ds = [n for n in self.nut.values() if n.z is not None]
        ra: list[Canh] = []
        for i, a in enumerate(ds):
            for b in ds[i + 1:]:
                tq = he_so_tuong_quan(a.nhom, b.nhom)
                if tq <= 0:
                    continue
                ra.append(Canh(a.ma, b.ma, tq, abs(a.z - b.z),
                               a.nhom == b.nhom))
        return ra

    def z_trung_binh(self) -> float | None:
        zs = [n.z for n in self.nut.values() if n.z is not None]
        return sum(zs) / len(zs) if zs else None

    def noi_bat(self, toiThieuZ: float = 1.0) -> list[Nut]:
        """Khung lệch nhiều nhất so với PHẦN CÒN LẠI của rổ.

        Trừ đi z trung bình trước khi xếp hạng: nếu cả rổ cùng lệch +2 thì
        đó là mô hình đang lệch hệ thống, không phải một cơ hội. Chỉ phần
        lệch RIÊNG của một khung mới đáng gọi là tín hiệu.

        ## "PHẦN CÒN LẠI" nghĩa là BỎ CHÍNH NÓ RA

        Bản trước trừ đi `z_trung_binh()` — trung bình có tính CẢ nút đang
        xét. Chính nút ấy kéo trung bình về phía mình, nên độ lệch đo được
        bị co lại đúng hệ số (n−1)/n:

            n = 3 → 0,667      n = 5 → 0,800
            n = 4 → 0,750      n = 8 → 0,875

        Cung này theo 4–5 chợ, nên mọi điểm nổi bật bị hạ 20–25% trong khi
        ngưỡng `toiThieuZ` thì cố định. Với 4 chợ, một khung phải lệch
        1,33σ so với phần còn lại mới được báo là 1,0σ — cả vùng
        [1,0 · 1,33) bị bỏ sót, LẶNG.

        Docstring nói "PHẦN CÒN LẠI" từ đầu; chỉ có phép tính là không
        làm thế.

        Một nút DUY NHẤT thì "phần còn lại" không tồn tại — trả rỗng, chứ
        không phải trả 0 rồi coi như nó bình thường.
        """
        zs = [n.z for n in self.nut.values() if n.z is not None]
        if len(zs) < 2:
            return []
        tong = sum(zs)
        con = len(zs) - 1
        ds = [(abs(n.z - (tong - n.z) / con), n)
              for n in self.nut.values() if n.z is not None]
        ds.sort(key=lambda x: -x[0])
        return [n for d, n in ds if d >= toiThieuZ]

    def canh_bao_dong_pha(self) -> str | None:
        """Cả rổ cùng lệch một chiều — dấu hiệu mô hình sai, không phải cơ hội.

        Đây là phép tự vấn quan trọng nhất của đồ thị. Nếu BTC, ETH và SOL
        cùng cho thấy "chợ rẻ hơn mô hình 2 sigma" thì khả năng cao hơn hẳn
        là mô hình đang lệch — chứ không phải ba chợ độc lập cùng sai một
        kiểu vào cùng một lúc.
        """
        zs = [n.z for n in self.nut.values() if n.z is not None]
        if len(zs) < 3:
            return None
        tb = sum(zs) / len(zs)
        cung_dau = all(z > 0 for z in zs) or all(z < 0 for z in zs)
        if cung_dau and abs(tb) >= 1.5:
            return (f"cả {len(zs)} khung cùng lệch {tb:+.1f}σ một chiều — "
                    f"nhiều khả năng MÔ HÌNH lệch, không phải chợ sai")
        return None

    def tom_tat(self) -> dict:
        canh = self.canh()
        return {
            "soNut": len(self.nut),
            "zTrungBinh": self.z_trung_binh(),
            "canhBaoDongPha": self.canh_bao_dong_pha(),
            "nut": [
                {"ma": n.ma, "slug": n.slug, "nhom": n.nhom,
                 "conLaiGiay": n.conLaiGiay, "fairUp": n.fairUp,
                 "giaChoUp": n.giaChoUp, "lech": n.lech, "z": n.z}
                for n in self.nut.values()
            ],
            "noiBat": [n.ma for n in self.noi_bat()],
            "canhChuY": [
                {"a": c.a, "b": c.b, "tuongQuan": c.tuongQuan, "lechZ": c.lechZ}
                for c in canh if c.dang_chu_y
            ],
        }


do_thi = DoThi()


def nhom_cua(ma: str) -> str:
    return nhom_tai_san(ma)
