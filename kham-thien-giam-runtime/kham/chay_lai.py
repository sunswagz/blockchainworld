"""Chạy lại theo sự kiện — chỗ DUY NHẤT biết một thay đổi là tốt hơn hay chỉ khác đi.

Bản trước của `bang.chay_lai()` chỉ ĐẾM cơ hội đã ghi trong băng. Nó trả về
một con số trông như kết quả backtest nhưng không phải: nó không dựng lại
được gì, nên không so được hai bộ tham số. Đúng thứ tài liệu cảnh báo —
"dashboard 100 chỉ số ≠ bot có alpha".

## Cái này khác ở chỗ nào

Băng ghi lưu **lát cắt sổ lệnh thô** cùng giá nền tại mỗi khung hình. Nên
chạy lại được làm đúng nghĩa:

    khung hình trong băng
        -> dựng lại SoLenh từ mức giá/khối lượng thô
        -> tính lại fair value với THAM SỐ MỚI
        -> cân lại net edge trên chính sổ đó
        -> khớp giấy theo VWAP thật của sổ đó
        -> so kết quả với kết quả tham số cũ

Không có bước "dựng lại sổ" thì mọi con số chạy lại chỉ là chép lại quyết
định cũ, và một tham số mới sẽ luôn cho ra y hệt tham số cũ — một backtest
xanh vĩnh viễn, thứ tệ hơn không có backtest.

## Luật chống tự lừa

1. **Không nhìn tương lai.** Mỗi khung hình chỉ được dùng dữ liệu của chính
   nó và các khung TRƯỚC. Kết quả kết toán chỉ dùng để CHẤM, không được
   chảy ngược vào quyết định.
2. **Khớp theo VWAP, không theo best.** Sổ giấy dễ dãi là backtest nói dối
   đúng chiều làm mình tự tin.
3. **Không có mẫu thì nói không có mẫu.** Không nội suy, không lấp.
"""
from __future__ import annotations

import math
from dataclasses import replace, dataclass, field

from .can_loi import can
from .dinh_gia import dinh_gia
from .so_lenh import Muc, SoLenh


from .ket_qua import so_ket_qua as _SO_KQ

@dataclass
class KetQua:
    """Kết quả một lượt chạy lại."""
    ten: str
    soKhung: int = 0
    soCoHoi: int = 0
    soQuaSang: int = 0
    soKhop: int = 0
    tongNetEdge: float = 0.0
    tongLaiLo: float = 0.0
    soThang: int = 0
    soThua: int = 0
    thuaLonNhat: float = 0.0
    boQua: dict[str, int] = field(default_factory=dict)

    @property
    def netEdgeTrungBinh(self) -> float:
        return self.tongNetEdge / self.soCoHoi if self.soCoHoi else 0.0

    @property
    def kyVong(self) -> float:
        return self.tongLaiLo / self.soKhop if self.soKhop else 0.0

    @property
    def tiLeThang(self) -> float:
        n = self.soThang + self.soThua
        return self.soThang / n if n else 0.0

    def tom_tat(self) -> dict:
        return {
            "ten": self.ten, "soKhung": self.soKhung, "soCoHoi": self.soCoHoi,
            "soQuaSang": self.soQuaSang, "soKhop": self.soKhop,
            "netEdgeTrungBinh": self.netEdgeTrungBinh,
            "kyVong": self.kyVong, "tongLaiLo": self.tongLaiLo,
            "tiLeThang": self.tiLeThang, "thuaLonNhat": self.thuaLonNhat,
            "boQua": dict(self.boQua),
        }


def dung_so(d: dict, ma: str, ben: str) -> SoLenh | None:
    """Dựng lại `SoLenh` từ lát cắt thô trong băng."""
    if not isinstance(d, dict):
        return None
    def muc(ds, giam):
        ra = []
        for m in (ds or []):
            try:
                g, l = float(m["gia"]), float(m["luong"])
            except (TypeError, ValueError, KeyError):
                continue
            if l > 0:
                ra.append(Muc(g, l))
        ra.sort(key=lambda x: x.gia, reverse=giam)
        return ra
    return SoLenh(ma=ma, ben=ben, bid=muc(d.get("bid"), True),
                  ask=muc(d.get("ask"), False), nhanLucMs=float(d.get("luc") or 0))


@dataclass
class ThamSo:
    """Bộ tham số đem thử. Mặc định lấy từ config đang chạy."""
    ten: str
    netEdgeToiThieu: float
    bienAnToan: float
    loCo: float = 100.0
    sanNenGiay: float | None = None
    # Phép nắn đem thử. None = mô hình thô. Có đây thì A/B được chính
    # phép nắn trên băng thật — trước đó nó chỉ được đo trên chính bảng
    # hiệu chỉnh đã sinh ra nó, tức là tự chấm bài mình.
    phepNan: object | None = None


def mot_luot(khung: list[dict], ts: ThamSo) -> KetQua:
    """Chạy lại toàn bộ băng với MỘT bộ tham số."""
    kq = KetQua(ten=ts.ten)
    # MỖI CỬA SỔ CHỈ VÀO MỘT LẦN.
    #
    # Băng ghi nhịp 2 giây, nên một khung 5 phút xuất hiện trong ~44 khung
    # hình. Bản đầu chấm từng khung hình một, tức là đếm cùng một cửa sổ
    # thành 44 lệnh độc lập — và ra lãi 2,9 TRIỆU đô trên một tài khoản
    # 1.000 đô mà không ai chớp mắt.
    #
    # Sai đó không chỉ phóng đại con số: nó còn làm lệch cả phép SO SÁNH,
    # vì hai bộ tham số vào lệnh ở những khung hình khác nhau thì bị đếm
    # lặp khác nhau. Một phép chạy lại đếm lặp thì không bác bỏ được gì.
    #
    # Vào MỘT lần cho mỗi (cửa sổ, bên), tại khung hình ĐẦU TIÊN mà cơ hội
    # qua sàng — đúng hành vi của máy thật: thấy tín hiệu thì vào, không
    # vào lại mỗi hai giây.
    daVao: set[tuple[str, str]] = set()

    def bo(ly: str) -> None:
        kq.boQua[ly] = kq.boQua.get(ly, 0) + 1

    for k in khung:
        kq.soKhung += 1
        for tt in (k.get("thiTruong") or []):
            ma = tt.get("ma") or "?"
            so_tho = tt.get("so") or {}
            su = dung_so(so_tho.get("UP"), ma, "UP")
            sd = dung_so(so_tho.get("DOWN"), ma, "DOWN")
            if su is None or sd is None:
                bo("thiếu sổ"); continue
            if not (su.dung_duoc or sd.dung_duoc):
                bo("thang chờ / sổ một chiều"); continue

            gia = tt.get("giaNen"); mo = tt.get("giaMo")
            sig = tt.get("sigmaGiay"); tau = tt.get("conLaiGiay")
            if not all(isinstance(x, (int, float)) for x in (gia, mo, sig, tau)):
                bo("thiếu nguyên liệu định giá"); continue

            gc = dinh_gia(ma, float(gia), float(mo), float(tau), float(sig))
            if gc is None:
                bo("định giá trả None"); continue
            if ts.phepNan is not None and getattr(ts.phepNan, "dung_duoc", False):
                p_nan = ts.phepNan.nan(gc.pUp)
                gc = replace(gc, pUp=p_nan, pDown=1.0 - p_nan)

            for ben, p, so in (("UP", gc.pUp, su), ("DOWN", gc.pDown, sd)):
                if not so.dung_duoc:
                    continue
                ch = can(ma, ben, ts.ten, p, gc.batDinh, so, ts.loCo)
                if ch is None:
                    bo("sổ không có hàng"); continue
                kq.soCoHoi += 1
                kq.tongNetEdge += ch.netEdge
                if ch.netEdge < ts.netEdgeToiThieu:
                    continue
                khoa = (tt.get("slug") or ma, ben)
                if khoa in daVao:
                    bo("cửa sổ này đã vào rồi"); continue
                daVao.add(khoa)
                kq.soQuaSang += 1

                # Kết quả chỉ dùng để CHẤM, không chảy ngược vào quyết định.
                #
                # Lấy từ SỔ KẾT QUẢ, không từ băng. Băng ghi khung hình lúc
                # nó đang diễn ra nên không thể chứa kết quả — mãi năm phút
                # sau mới biết, và lúc đó dòng băng đã nằm trong một file
                # gzip đã đóng. Đo được: 5.854 bản ghi thị trường trong
                # băng, KHÔNG cái nào có `upThang`. Nên trước bản này,
                # `soKhop` luôn bằng 0 và cỗ máy chạy lại chưa từng chấm
                # được một khung nào — kể cả khi cổng tiến hoá hỏi nó.
                that = tt.get("upThang")
                if that is None:
                    that = _SO_KQ.lay(tt.get("slug") or "")
                if that is None:
                    bo("chưa có kết quả cho slug này"); continue
                kq.soKhop += 1
                tra = 1.0 if (bool(that) == (ben == "UP")) else 0.0
                lai = (tra - ch.vwap - ch.phi) * ch.soCo
                kq.tongLaiLo += lai
                if lai > 0:
                    kq.soThang += 1
                else:
                    kq.soThua += 1
                    kq.thuaLonNhat = min(kq.thuaLonNhat, lai)
    return kq


def doi_chieu(khung: list[dict], a: ThamSo, b: ThamSo) -> dict:
    """Chạy hai bộ tham số trên CÙNG băng rồi so. Đây mới là backtest."""
    ka, kb = mot_luot(khung, a), mot_luot(khung, b)

    def hon(x: float, y: float) -> str:
        if abs(x - y) < 1e-12:
            return "bằng"
        return "A" if x > y else "B"

    du_mau = min(ka.soKhop, kb.soKhop) >= 30
    return {
        "A": ka.tom_tat(), "B": kb.tom_tat(),
        "duMau": du_mau,
        "soSanh": {
            "kyVong": hon(ka.kyVong, kb.kyVong),
            "tongLaiLo": hon(ka.tongLaiLo, kb.tongLaiLo),
            "thuaLonNhat": hon(ka.thuaLonNhat, kb.thuaLonNhat),
            "soQuaSang": hon(ka.soQuaSang, kb.soQuaSang),
        },
        "ketLuan": _ket_luan(ka, kb, du_mau),
    }


def _ket_luan(a: KetQua, b: KetQua, duMau: bool) -> str:
    if not duMau:
        return (f"CHƯA ĐỦ MẪU để kết luận — A khớp {a.soKhop}, B khớp "
                f"{b.soKhop}, cần ít nhất 30 mỗi bên. Chạy thêm băng.")
    if abs(a.kyVong - b.kyVong) < 1e-9:
        return "hai bộ tham số cho kỳ vọng như nhau — thay đổi không có tác dụng"
    thang = a if a.kyVong > b.kyVong else b
    thua = b if thang is a else a
    # Kỳ vọng cao hơn mà đuôi xấu hơn thì KHÔNG được gọi là tốt hơn.
    if abs(thang.thuaLonNhat) > abs(thua.thuaLonNhat) * 1.25:
        return (f"`{thang.ten}` kỳ vọng cao hơn ({thang.kyVong:+.5f} vs "
                f"{thua.kyVong:+.5f}) NHƯNG thua lớn nhất tệ hơn "
                f"(${thang.thuaLonNhat:.2f} vs ${thua.thuaLonNhat:.2f}) — "
                f"khác đi, chưa chắc tốt hơn")
    return (f"`{thang.ten}` tốt hơn: kỳ vọng {thang.kyVong:+.5f} vs "
            f"{thua.kyVong:+.5f} trên {thang.soKhop} lệnh, đuôi không xấu hơn")
