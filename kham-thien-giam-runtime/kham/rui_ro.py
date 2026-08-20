"""Risk Engine — Python thuần, không gọi model, có quyền phủ quyết.

Cùng ranh giới trung tâm như `tu-cam-thanh-runtime/trader/risk.py`, và ở đây
còn quan trọng hơn vì vòng lặp chạy mỗi 2 giây chứ không phải mỗi giờ.

    Chiến thuật ĐỀ XUẤT. Risk Engine QUYẾT.

    Và độ tin cậy của mô hình chỉ được dùng để TỪ CHỐI, không bao giờ được
    dùng để NỚI. Mô hình tự tin 99% cũng không mua thêm được một xu rủi ro
    nào. Đừng đề nghị "cho phép đặt to hơn khi mô hình chắc chắn" — cả kiến
    trúc này tồn tại để chặn đúng đề nghị đó.

Mọi phép kiểm ở đây trả về LÝ DO bằng chữ chứ không phải True/False, vì một
lệnh bị chặn mà không nói được vì sao thì sáu tháng nữa không ai dám gỡ luật.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .can_loi import CoHoi
from .config import CONFIG
from .kho_doi import Kho, nhom_tai_san

_RR = CONFIG["ruiRo"]
_KD = CONFIG["khoDoi"]
_CL = CONFIG["canLoi"]


@dataclass
class PhanQuyet:
    cho: bool
    soCoChoPhep: float
    lyDo: list[str] = field(default_factory=list)
    canhBao: list[str] = field(default_factory=list)
    daSiet: bool = False          # có bị cắt bớt so với đề xuất không

    @property
    def tu_choi(self) -> bool:
        return not self.cho


@dataclass
class SucKhoeNguon:
    """Dữ liệu vào có còn dùng được không.

    Một lệnh đặt trên sổ lệnh cũ 4 giây là đặt vào một thị trường không còn
    tồn tại. Đây là loại hỏng KHÔNG ném exception: API vẫn trả 200, số vẫn
    có, chỉ là số của quá khứ.
    """
    tuoiSoLenhMs: float = 0.0
    tuoiGiaNenMs: float = 0.0
    lechDongHoMs: float = 0.0
    thieuNguon: list[str] = field(default_factory=list)

    def van_de(self) -> list[str]:
        v: list[str] = []
        if self.tuoiSoLenhMs > float(_RR["tuoiSoLenhToiDaMs"]):
            v.append(f"sổ lệnh cũ {self.tuoiSoLenhMs:.0f}ms "
                     f"(trần {_RR['tuoiSoLenhToiDaMs']}ms)")
        if self.tuoiGiaNenMs > float(_RR["tuoiGiaNenToiDaMs"]):
            v.append(f"giá nền cũ {self.tuoiGiaNenMs:.0f}ms "
                     f"(trần {_RR['tuoiGiaNenToiDaMs']}ms)")
        if abs(self.lechDongHoMs) > float(_RR["lechDongHoToiDaMs"]):
            v.append(f"đồng hồ lệch {self.lechDongHoMs:+.0f}ms "
                     f"(trần ±{_RR['lechDongHoToiDaMs']}ms)")
        for n in self.thieuNguon:
            v.append(f"mất nguồn {n}")
        return v


class RiskEngine:
    def __init__(self, kho: Kho) -> None:
        self.kho = kho
        self.vonBanDau = float(_RR["vonBanDau"])
        self.von = self.vonBanDau
        self.dinhVon = self.vonBanDau
        self.loNgayUsd = 0.0
        self.ngay = time.strftime("%Y-%m-%d")
        self.ngatKhanCap = False
        self.lyDoNgat = ""

    # ── kế toán ───────────────────────────────────────────────────────────
    def ghi_lai_lo(self, usd: float) -> None:
        hom_nay = time.strftime("%Y-%m-%d")
        if hom_nay != self.ngay:
            self.ngay = hom_nay
            self.loNgayUsd = 0.0
        self.von += usd
        self.dinhVon = max(self.dinhVon, self.von)
        if usd < 0:
            self.loNgayUsd += -usd
        self._soat_ngat()

    @property
    def sutVonPct(self) -> float:
        if self.dinhVon <= 0:
            return 0.0
        return (self.dinhVon - self.von) / self.dinhVon * 100.0

    def _soat_ngat(self) -> None:
        if self.loNgayUsd >= float(_RR["tranLoNgayUsd"]):
            self.ngat("chạm trần lỗ ngày $%.2f" % _RR["tranLoNgayUsd"])
        if self.sutVonPct >= float(_RR["tranSutVonPct"]):
            self.ngat("sụt vốn %.1f%% (trần %.1f%%)"
                      % (self.sutVonPct, _RR["tranSutVonPct"]))

    def ngat(self, lyDo: str) -> None:
        """Cầu dao. Đã ngắt thì chỉ người mở lại được, không tự phục hồi.

        Không tự bật lại là chủ ý: một cầu dao tự đóng sau N phút sẽ đóng
        đúng lúc thứ làm nó nhảy vẫn còn nguyên.
        """
        if not self.ngatKhanCap:
            self.ngatKhanCap = True
            self.lyDoNgat = lyDo

    def mo_lai(self) -> None:
        self.ngatKhanCap = False
        self.lyDoNgat = ""

    # ── cửa duyệt ─────────────────────────────────────────────────────────
    def duyet(self, ch: CoHoi, sucKhoe: SucKhoeNguon,
              conLaiGiay: float, duDeDungKelly: bool) -> PhanQuyet:
        """Cửa duy nhất. Mọi lệnh phải đi qua đây, kể cả lệnh phòng hộ."""
        ly_do: list[str] = []
        canh: list[str] = []

        # 1. cầu dao
        if self.ngatKhanCap:
            return PhanQuyet(False, 0.0, [f"CẦU DAO ĐANG NGẮT: {self.lyDoNgat}"])

        # 2. sức khoẻ nguồn — trước mọi phép tính, vì tính trên số cũ là vô nghĩa
        van_de = sucKhoe.van_de()
        if van_de:
            return PhanQuyet(False, 0.0, ["nguồn không lành: " + "; ".join(van_de)])

        # 3. cơ hội có qua sàng không
        if not ch.dang_lam:
            if ch.netEdge < float(_CL["netEdgeToiThieu"]):
                ly_do.append(f"net edge {ch.netEdge:+.4f} dưới ngưỡng "
                             f"{_CL['netEdgeToiThieu']}")
            if ch.sucChua < float(_CL["sucChuaToiThieu"]):
                ly_do.append(f"sức chứa {ch.sucChua:.0f} dưới ngưỡng "
                             f"{_CL['sucChuaToiThieu']}")
            if ch.xacSuatKhop < float(_CL["xacSuatKhopToiThieu"]):
                ly_do.append(f"xác suất khớp {ch.xacSuatKhop:.0%} quá thấp")
            if ch.nuaDoiMs < float(_CL["nuaDoiToiThieuMs"]):
                ly_do.append(f"cơ hội chỉ sống {ch.nuaDoiMs:.0f}ms")
            return PhanQuyet(False, 0.0, ly_do or ["không qua sàng"])

        # 4. market sắp khoá thì không mở vị thế MỚI
        #    Chân chưa phòng hộ lúc chuông reo là rủi ro trần trụi không gỡ được.
        if conLaiGiay <= float(_KD["giayChoChanHai"]):
            return PhanQuyet(False, 0.0, [
                f"còn {conLaiGiay:.0f}s, không đủ thời gian phòng hộ chân hai "
                f"(cần {_KD['giayChoChanHai']}s)"])

        # ── từ đây là SIẾT chứ không từ chối ─────────────────────────────
        cho_phep = ch.soCo

        # 5. Kelly — chỉ khi mô hình đã được đối chiếu đủ mẫu
        if duDeDungKelly:
            k = self._kelly(ch)
            if k < cho_phep:
                cho_phep = k
                canh.append(f"Kelly cắt còn {k:.0f} cổ")
        else:
            # Chưa đủ mẫu hiệu chỉnh thì dùng lô sàn cố định, KHÔNG dùng Kelly.
            # Kelly trên một xác suất chưa ai kiểm là khuếch đại chính sai lầm
            # của mô hình — mô hình càng tự tin sai thì nó càng đặt to.
            san = float(_CL["sucChuaToiThieu"])
            if cho_phep > san:
                cho_phep = san
                canh.append(f"chưa đủ mẫu hiệu chỉnh, giữ lô sàn {san:.0f} cổ")

        # 6. trần vốn mỗi market
        v = self.kho.lay(ch.ma)
        dang_co = v.tienUp + v.tienDown
        con_duoc = float(_RR["vonToiDaMoiThiTruongUsd"]) - dang_co
        if con_duoc <= 0:
            return PhanQuyet(False, 0.0, [
                f"market {ch.ma} đã dùng ${dang_co:.2f}, chạm trần "
                f"${_RR['vonToiDaMoiThiTruongUsd']}"])
        max_co = con_duoc / max(1e-9, ch.vwap)
        if max_co < cho_phep:
            cho_phep = max_co
            canh.append(f"trần vốn market cắt còn {max_co:.0f} cổ")

        # 7. trần vốn mỗi nhóm tài sản (BTC_5M + BTC_15M cùng một rổ)
        nhom = nhom_tai_san(ch.ma)
        dang_nhom = sum(
            (x.tienUp + x.tienDown) for m, x in self.kho.viThe.items()
            if nhom_tai_san(m) == nhom
        )
        con_nhom = float(_RR["vonToiDaMoiTaiSanUsd"]) - dang_nhom
        if con_nhom <= 0:
            return PhanQuyet(False, 0.0, [
                f"nhóm {nhom} đã dùng ${dang_nhom:.2f}, chạm trần "
                f"${_RR['vonToiDaMoiTaiSanUsd']}"])
        max_nhom = con_nhom / max(1e-9, ch.vwap)
        if max_nhom < cho_phep:
            cho_phep = max_nhom
            canh.append(f"trần vốn nhóm {nhom} cắt còn {max_nhom:.0f} cổ")

        # 8. trần tiền nằm trần một chân
        them_tran = cho_phep * ch.vwap
        dang_tran = self.kho.tong_chua_phong_ho_usd()
        if dang_tran + them_tran > float(_KD["capChuaKhopToiDaUsd"]):
            con = float(_KD["capChuaKhopToiDaUsd"]) - dang_tran
            if con <= 0:
                return PhanQuyet(False, 0.0, [
                    f"đang có ${dang_tran:.2f} nằm trần một chân, chạm trần "
                    f"${_KD['capChuaKhopToiDaUsd']}"])
            cho_phep = con / max(1e-9, ch.vwap)
            canh.append(f"trần chưa phòng hộ cắt còn {cho_phep:.0f} cổ")

        # 9. chân quá hạn chờ — dừng mở thêm cho tới khi dọn xong
        qua_han = v.chan_qua_han()
        if qua_han:
            return PhanQuyet(False, 0.0, [
                f"{len(qua_han)} chân đã chờ quá {_KD['giayChoChanHai']}s "
                f"chưa phòng hộ xong — dọn trước khi mở thêm"])

        # 10. trần lệnh thật
        if CONFIG.get("che") == "that":
            tran = float(CONFIG["datLenh"]["tranMoiLenhUsd"])
            max_that = tran / max(1e-9, ch.vwap)
            if max_that < cho_phep:
                cho_phep = max_that
                canh.append(f"trần lệnh thật ${tran} cắt còn {max_that:.0f} cổ")

        # 11. sau khi siết, cơ hội còn đáng làm không
        if cho_phep < 1:
            return PhanQuyet(False, 0.0, ["sau khi siết còn dưới 1 cổ"])
        if cho_phep * ch.netEdge < 0.01:
            return PhanQuyet(False, 0.0, [
                f"sau khi siết lợi kỳ vọng chỉ ${cho_phep * ch.netEdge:.4f} — "
                f"không đáng một lượt khớp"])

        return PhanQuyet(True, cho_phep, ly_do, canh, daSiet=cho_phep < ch.soCo - 1e-9)

    def _kelly(self, ch: CoHoi) -> float:
        """Kelly phân số. Luôn kẹp không âm và luôn nhân với `kellyPhan` < 1.

        Kelly toàn phần là cực đại tăng trưởng dài hạn VỚI ĐIỀU KIỆN xác suất
        đúng. Xác suất ở đây là ước lượng, nên Kelly toàn phần là quá to —
        `kellyPhan` mặc định 0.2 là chỗ trả giá cho việc mình có thể sai.
        """
        p = min(0.999, max(0.001, ch.fairValue))
        gia = min(0.999, max(0.001, ch.vwap))
        # tiền cược 1 đô ở giá `gia` thắng được (1-gia)/gia
        b = (1.0 - gia) / gia
        if b <= 0:
            return 0.0
        f = (b * p - (1.0 - p)) / b
        f = max(0.0, f) * float(_RR["kellyPhan"])
        von_cho = self.von * f
        return von_cho / max(1e-9, ch.vwap)

    def tom_tat(self) -> dict:
        return {
            "von": self.von,
            "vonBanDau": self.vonBanDau,
            "dinhVon": self.dinhVon,
            "sutVonPct": self.sutVonPct,
            "loNgayUsd": self.loNgayUsd,
            "tranLoNgayUsd": float(_RR["tranLoNgayUsd"]),
            "ngatKhanCap": self.ngatKhanCap,
            "lyDoNgat": self.lyDoNgat,
        }
