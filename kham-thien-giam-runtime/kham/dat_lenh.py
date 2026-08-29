"""Đặt lệnh — sổ giấy khớp trên sổ lệnh THẬT, và cổng lệnh thật có ba khoá.

Ba đường ra, và chỉ một đường chạm tới tiền:

    quan-sat   không có vị thế nào. Chỉ đo.
    giay       khớp mô phỏng, nhưng đi qua ĐÚNG sổ lệnh thật, ĐÚNG phí thật,
               ĐÚNG trượt giá. Tiền giả, vật lý thật.
    that       lệnh rời khỏi máy. Cần cả ba cửa của config.py.

Sổ giấy ở đây cố tình KHÔNG dễ dãi. Một backtest cho khớp trọn lô ở best ask
là một backtest nói dối, và nó nói dối đúng chiều làm mình tự tin. Nên sổ giấy
này khớp theo VWAP đi qua từng mức, từ chối phần sổ không đủ hàng, tính phí
taker thật, và với lệnh maker thì nó KHÔNG cho khớp ngay — phải đợi.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from .bus import bus
from .can_loi import CoHoi, phi_maker, phi_taker
from .config import CONFIG, che_hieu_luc, ly_do_khong_that
from .kho_doi import ChanCho, Kho
from .so_lenh import SoLenh

_PHI = CONFIG["phi"]
_KD = CONFIG["khoDoi"]


@dataclass
class Lenh:
    id: str
    ma: str
    ben: str
    chienThuat: str
    soCo: float
    giaDat: float
    laMaker: bool
    datLucMs: float
    trangThai: str = "cho"          # cho | khop | khop-mot-phan | huy | tu-choi
    soCoKhop: float = 0.0
    giaKhop: float = 0.0
    phiUsd: float = 0.0
    khopLucMs: float = 0.0
    duong: str = "giay"             # giay | that
    ghiChu: str = ""
    #: Giá trị hợp lý mô hình gán cho BÊN NÀY lúc đặt lệnh. Đi theo lệnh
    #: để tới được sổ kết toán: sổ chỉ ghi niềm tin lúc GẦN ĐÓNG, nên
    #: không nói được cỗ máy đã tin gì lúc nó tiêu tiền.
    pMoHinh: float | None = None

    @property
    def tienUsd(self) -> float:
        return self.soCoKhop * self.giaKhop

    def tom_tat(self) -> dict:
        return {
            "id": self.id, "ma": self.ma, "ben": self.ben,
            "chienThuat": self.chienThuat, "soCo": self.soCo,
            "giaDat": self.giaDat, "laMaker": self.laMaker,
            "trangThai": self.trangThai, "soCoKhop": self.soCoKhop,
            "giaKhop": self.giaKhop, "phiUsd": self.phiUsd,
            "tienUsd": self.tienUsd, "duong": self.duong,
            "datLucMs": self.datLucMs, "khopLucMs": self.khopLucMs,
            "ghiChu": self.ghiChu,
        }


class CongLenh:
    """Cổng duy nhất mà một lệnh đi qua để rời khỏi hệ thống."""

    def __init__(self, kho: Kho) -> None:
        self.kho = kho
        self.lenh: list[Lenh] = []
        self.dangCho: list[Lenh] = []
        self._sdk = None
        self._sdkLoi = ""

    # ── cửa chính ─────────────────────────────────────────────────────────
    def dat(self, ch: CoHoi, soCo: float, so: SoLenh) -> Lenh:
        """Đặt một lệnh. Đường đi do `che_hieu_luc()` quyết, không do ai gọi."""
        l = Lenh(
            id=uuid.uuid4().hex[:12], ma=ch.ma, ben=ch.ben,
            chienThuat=ch.chienThuat, soCo=soCo,
            giaDat=ch.vwap if not ch.laMaker else _gia_yet_maker(so, ch),
            laMaker=ch.laMaker, datLucMs=time.time() * 1000.0,
            pMoHinh=ch.fairValue,
        )
        self.lenh.append(l)

        che = che_hieu_luc()
        if che == "quan-sat":
            l.trangThai = "tu-choi"
            l.ghiChu = "chế độ quan-sat: chỉ đo, không có vị thế"
            return l

        if che == "that":
            l.duong = "that"
            return self._dat_that(l, so)

        l.duong = "giay"
        return self._dat_giay(l, so)

    # ── sổ giấy ───────────────────────────────────────────────────────────
    def _dat_giay(self, l: Lenh, so: SoLenh) -> Lenh:
        if l.laMaker:
            # Maker KHÔNG khớp ngay. Nó nằm chờ người khác tới ăn — và đó
            # chính là đánh đổi của việc không trả phí. Sổ giấy nào cho lệnh
            # maker khớp tức thì là sổ giấy tặng không cả phí lẫn spread, tức
            # là cho chiến thuật `tao-lap` một lợi thế không có thật.
            l.trangThai = "cho"
            self.dangCho.append(l)
            bus.ghi(f"[giấy] yết maker {l.ben} {l.soCo:.0f}@{l.giaDat:.4f} {l.ma}",
                    loai="lenh")
            return l

        r = so.vwap_mua(l.soCo)
        if r.khop <= 0:
            l.trangThai = "tu-choi"
            l.ghiChu = "sổ không có hàng"
            return l

        l.soCoKhop = r.khop
        l.giaKhop = r.vwap
        l.phiUsd = phi_taker(r.vwap, r.khop)
        l.khopLucMs = time.time() * 1000.0
        l.trangThai = "khop" if r.dayDu else "khop-mot-phan"
        if not r.dayDu:
            l.ghiChu = f"sổ chỉ đủ {r.khop:.0f}/{l.soCo:.0f}"

        self._ghi_kho(l)
        bus.ghi(f"[giấy] khớp {l.ben} {l.soCoKhop:.0f}@{l.giaKhop:.4f} "
                f"phí ${l.phiUsd:.4f} {l.ma}", loai="khop")
        return l

    def soat_cho(self, soTheoMa: dict[str, dict[str, SoLenh]]) -> list[Lenh]:
        """Soát các lệnh maker đang chờ xem có ai tới ăn chưa.

        Quy ước khớp của sổ giấy: lệnh mua ở giá G khớp khi best ask tụt
        xuống chạm G. Đó là mô phỏng thận trọng — thực tế còn phải xếp hàng
        sau các lệnh cùng giá đã nằm trước, nên sổ giấy này vẫn LẠC QUAN hơn
        đời thật. Ghi rõ ở đây để không ai đọc kết quả sổ giấy như kết quả thật.
        """
        xong: list[Lenh] = []
        for l in list(self.dangCho):
            so = (soTheoMa.get(l.ma) or {}).get(l.ben)
            if so is None:
                continue
            # quá hạn chờ thì huỷ, đừng để treo mãi
            if (time.time() * 1000.0 - l.datLucMs) > float(_KD["giayChoChanHai"]) * 1000.0:
                l.trangThai = "huy"
                l.ghiChu = "hết hạn chờ khớp"
                self.dangCho.remove(l)
                xong.append(l)
                continue
            ask = so.best_ask
            if ask is not None and ask <= l.giaDat + 1e-9:
                l.soCoKhop = l.soCo
                l.giaKhop = l.giaDat
                l.phiUsd = phi_maker(l.giaDat, l.soCo)
                l.khopLucMs = time.time() * 1000.0
                l.trangThai = "khop"
                self.dangCho.remove(l)
                self._ghi_kho(l)
                xong.append(l)
                bus.ghi(f"[giấy] maker khớp {l.ben} {l.soCo:.0f}@{l.giaKhop:.4f} "
                        f"phí ${l.phiUsd:.4f} {l.ma}", loai="khop")
        return xong

    def huy(self, lenhId: str) -> bool:
        for l in list(self.dangCho):
            if l.id == lenhId:
                l.trangThai = "huy"
                l.ghiChu = "huỷ tay"
                self.dangCho.remove(l)
                return True
        return False

    def _ghi_kho(self, l: Lenh) -> None:
        """Ghi vào tồn kho theo GIÁ KHỚP, không phải giá đặt.

        Đây đúng cái bẫy đã cắn tu-cam-thanh-runtime lần đầu: ghi rủi ro theo
        giá yêu cầu thay vì giá khớp. R-multiple là mẫu số của mọi phép hậu
        kiểm, và sai mẫu số là học sai toàn bộ — mà không phép kiểm nào đỏ.
        """
        if l.soCoKhop <= 0:
            return
        v = self.kho.lay(l.ma)
        # Phí phải ĐI THEO vào vị thế. Bản trước tính nó, in nó ra
        # nhật ký, rồi bỏ rơi — nên lãi lỗ ở `ket_toan` đẹp hơn sự
        # thật đúng bằng khoản phí, ở CẢ chế độ giấy lẫn chế độ thật.
        v.ghi_khop(l.ben, l.soCoKhop, l.giaKhop, l.phiUsd, l.pMoHinh)

        # Chân của một cặp thì phải vào sổ chờ, để đồng hồ chưa-phòng-hộ chạy.
        if l.chienThuat.startswith("cap-") and abs(v.dinhHuong) > 0:
            ben_du = "UP" if v.dinhHuong > 0 else "DOWN"
            v.choCap = [c for c in v.choCap if c.ben == ben_du]
            if not v.choCap:
                v.choCap.append(ChanCho(
                    ben=ben_du, soCo=abs(v.dinhHuong),
                    giaTrungBinh=v.giaVonUp if v.dinhHuong > 0 else v.giaVonDown,
                    moLucMs=time.time() * 1000.0, capMongMuon=v.daGhepCap,
                ))
            else:
                v.choCap[0].soCo = abs(v.dinhHuong)
        elif abs(v.dinhHuong) <= 1e-9:
            v.choCap.clear()

    # ── lệnh thật ─────────────────────────────────────────────────────────
    def _dat_that(self, l: Lenh, so: SoLenh) -> Lenh:
        """Đường tới tiền thật. Bọc SDK sau adapter, không rải SDK khắp nơi.

        Vì sao bọc: `py-clob-client` đời cũ đã bị Polymarket archive
        25/05/2026 và họ đang trong quá trình CLOB V2. SDK sẽ còn đổi. Bọc
        sau một adapter thì lúc đó chỉ sửa đúng hàm này, không sửa cả hệ thống.
        """
        thieu = ly_do_khong_that()
        if thieu:
            # Không im lặng rơi về giấy. Nói rõ cửa nào đóng, rồi mới rơi.
            l.ghiChu = "chưa mở đủ cửa lệnh thật: " + "; ".join(thieu)
            bus.ghi("từ chối lệnh thật — " + l.ghiChu, loai="canh")
            l.duong = "giay"
            return self._dat_giay(l, so)

        sdk = self._nap_sdk()
        if sdk is None:
            l.trangThai = "tu-choi"
            l.ghiChu = f"không nạp được SDK Polymarket: {self._sdkLoi}"
            bus.ghi(l.ghiChu, loai="loi")
            return l

        try:
            ket_qua = sdk.dat_lenh(
                ma=l.ma, ben=l.ben, soCo=l.soCo, gia=l.giaDat, laMaker=l.laMaker,
            )
        except Exception as e:                      # noqa: BLE001
            l.trangThai = "tu-choi"
            l.ghiChu = f"sàn từ chối: {type(e).__name__}: {e}"
            bus.ghi(l.ghiChu, loai="loi")
            return l

        l.soCoKhop = float(ket_qua.get("soCoKhop") or 0.0)
        l.giaKhop = float(ket_qua.get("giaKhop") or 0.0)
        l.phiUsd = float(ket_qua.get("phiUsd") or 0.0)
        l.khopLucMs = time.time() * 1000.0
        l.trangThai = ket_qua.get("trangThai") or (
            "khop" if l.soCoKhop >= l.soCo - 1e-9 else "khop-mot-phan")
        if l.soCoKhop > 0:
            self._ghi_kho(l)
        bus.ghi(f"[THẬT] {l.trangThai} {l.ben} {l.soCoKhop:.0f}@{l.giaKhop:.4f} {l.ma}",
                loai="khop")
        return l

    def _nap_sdk(self):
        """Nạp adapter SDK. Chỉ chạm tới khi đã qua ba cửa."""
        if self._sdk is not None:
            return self._sdk
        try:
            from .sdk_polymarket import AdapterPolymarket
            self._sdk = AdapterPolymarket()
            return self._sdk
        except Exception as e:                      # noqa: BLE001
            self._sdkLoi = f"{type(e).__name__}: {e}"
            return None

    # ── báo cáo ───────────────────────────────────────────────────────────
    def tom_tat(self) -> dict:
        khop = [l for l in self.lenh if l.trangThai in ("khop", "khop-mot-phan")]
        return {
            "tongLenh": len(self.lenh),
            "daKhop": len(khop),
            "dangCho": len(self.dangCho),
            "tongPhiUsd": sum(l.phiUsd for l in khop),
            "duong": che_hieu_luc(),
            "cuaDangDong": ly_do_khong_that(),
            "ganDay": [l.tom_tat() for l in self.lenh[-25:]],
        }


def _gia_yet_maker(so: SoLenh, ch: CoHoi) -> float:
    """Giá yết cho lệnh maker: đứng TRONG spread, nhích hơn best bid một nấc.

    Yết đúng bằng best bid là xếp sau toàn bộ hàng đã nằm ở đó. Yết vượt qua
    best ask thì không còn là maker nữa — nó thành taker và mất luôn ưu đãi
    phí, tức là mất đúng thứ khiến chiến thuật này có lãi.
    """
    le = float(_PHI["leChonNhoNhat"])
    bb, ba = so.best_bid, so.best_ask
    if bb is None or ba is None:
        return min(0.99, max(0.01, ch.fairValue))
    yet = bb + le
    if yet >= ba:
        yet = ba - le
    return min(0.99, max(0.01, min(yet, ch.fairValue)))
