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
    def __init__(self, kho: Kho, dongHo=None) -> None:
        """`dongHo`: hàm trả về epoch giây. Mặc định là đồng hồ tường.

        Phải nhận được từ ngoài, vì trần lỗ NGÀY cần một ranh giới ngày —
        và chạy lại băng tám ngày bằng đồng hồ tường thì với nó mãi mãi
        là một ngày. Hậu quả không phải "số hơi lệch": `loNgayUsd` cộng
        dồn suốt tám ngày, chạm trần, `ngat()` bật cờ, và cờ ấy dính —
        nên cả phiên đứng im từ đó. Đo được: khớp đứng hẳn ở 397 lệnh
        trong khi băng còn hơn một trăm nghìn khung phía sau.

        Nói cách khác: một cỗ máy rủi ro lấy ngày từ đồng hồ tường thì
        KHÔNG hậu kiểm được. Nó không sai lúc chạy thật, nhưng nó làm
        mọi phép đo về chính nó thành vô nghĩa.
        """
        self.kho = kho
        self.dongHo = dongHo or time.time
        self.vonBanDau = float(_RR["vonBanDau"])
        self.von = self.vonBanDau
        self.dinhVon = self.vonBanDau
        self.laiRongNgayUsd = 0.0
        self.loGopNgayUsd = 0.0
        self.ngay = self._ngay_hien_tai()
        self.ngatKhanCap = False
        self.lyDoNgat = ""
        self.soLanNgat = 0

    def _ngay_hien_tai(self) -> str:
        return time.strftime("%Y-%m-%d", time.gmtime(self.dongHo()))

    # ── TRẦN THEO PHẦN TRĂM VỐN, không phải đô-la cứng ───────────────────
    #
    # Ba trần này từng khai bằng đô-la, và cả ba đều lấy con số hợp lý
    # cho MỘT tài khoản 1.000 đô: $100 mỗi market, $200 mỗi nhóm, $50 lỗ
    # ngày. Nạp thêm vốn thì chúng đứng yên — tức là thêm tiền vào KHÔNG
    # đổi hành vi cỗ máy, chỉ làm cầu dao ngày ngắt sớm hơn về tỉ lệ.
    # Đo được: chạy phiên giấy với 10.000 đô thì cầu dao ngắt ở mức lỗ
    # 0,51% sau đúng hai cửa sổ.
    #
    # Phần trăm giữ nguyên tỉ lệ cũ (10 / 20 / 5) nên tài khoản 1.000 đô
    # cư xử Y HỆT như trước; chỗ khác là nó nay biết co giãn.
    #
    # Khoá `...Usd` cũ vẫn đọc được nếu ai đó cố ý muốn một trần tuyệt
    # đối — nhưng chỉ khi KHÔNG khai phần trăm, và đọc bằng `.get` chứ
    # không bằng `[...]`: một khoá thiếu mà ném KeyError ở đây là giết
    # cả vòng lặp, đúng lớp lỗi vừa vá ở `nguon.py`.

    def _tran(self, khoaPct: str, khoaUsd: str, macDinhPct: float) -> float:
        pct = _RR.get(khoaPct)
        if pct is None:
            cu = _RR.get(khoaUsd)
            if cu is not None:
                return float(cu)
            pct = macDinhPct
        return self.vonBanDau * float(pct) / 100.0

    @property
    def tranMoiThiTruongUsd(self) -> float:
        return self._tran("phanTramMoiThiTruong", "vonToiDaMoiThiTruongUsd", 10.0)

    @property
    def tranMoiTaiSanUsd(self) -> float:
        return self._tran("phanTramMoiTaiSan", "vonToiDaMoiTaiSanUsd", 20.0)

    @property
    def tranLoNgayUsd(self) -> float:
        return self._tran("phanTramLoNgay", "tranLoNgayUsd", 5.0)

    # ── kế toán ───────────────────────────────────────────────────────────
    def nap_tu_so(self, ds: list[dict]) -> dict:
        """Dựng lại vốn, đỉnh vốn và lỗ ngày TỪ SỔ KẾT TOÁN.

        `__init__` đặt `von = vonBanDau` từ config và không đọc gì cả,
        nên **mỗi lần khởi động lại là quên sạch**. Đo được trên máy:
        sổ ghi một lệnh lỗ $49,95 mà buồng lái vẫn khai `von 1.000` và
        `sutVonPct 0,0%`.

        Ba cầu dao dựa trên đúng những con số ấy:

            tranLoNgayUsd   lỗ RÒNG trong ngày
            tranSutVonPct   sụt từ ĐỈNH vốn
            von             cỡ lệnh theo Kelly

        Nên một bot vừa chạm trần lỗ ngày, bị khởi động lại (sập, cập
        nhật, hay người bấm), sẽ có NGAY một ngân sách lỗ mới nguyên.
        Đó là lỗ hổng kiểm soát rủi ro kinh điển, và nó im lặng: buồng
        lái hiện những con số đẹp và đúng cú pháp.

        Dựng lại từ SỔ chứ không thêm một file trạng thái mới: sổ kết
        toán đã là nguồn sự thật, và hai nguồn sự thật thì sớm muộn lệch
        nhau. Đổi lại phải đi qua cả sổ, nhưng chỉ một lần lúc khởi
        động.

        Trả về bản tóm tắt những gì đã dựng lại, để chỗ gọi KHAI RA —
        một lần khôi phục im lặng cũng khó tin như một lần quên im lặng.
        """
        hom_nay = self._ngay_hien_tai()
        von = self.vonBanDau
        dinh = self.vonBanDau
        rong_ngay = 0.0
        gop_ngay = 0.0
        n = 0
        for g in (ds or []):
            try:
                lai = float(g.get("laiLo"))
            except (TypeError, ValueError):
                continue
            n += 1
            von += lai
            dinh = max(dinh, von)
            # Ngày lấy từ mốc ghi trong sổ, KHÔNG lấy đồng hồ máy: đọc
            # lại một sổ cũ thì mọi dòng đều thành "hôm nay".
            if str(g.get("luc") or "")[:10] == hom_nay:
                rong_ngay += lai
                if lai < 0:
                    gop_ngay += -lai
        self.von = von
        self.dinhVon = dinh
        self.ngay = hom_nay
        self.laiRongNgayUsd = rong_ngay
        self.loGopNgayUsd = gop_ngay
        # Dựng lại xong thì phải SOÁT: nếu sổ cho thấy đã quá trần thì
        # cầu dao phải ngắt NGAY, chứ không đợi lệnh kế tiếp.
        self._soat_ngat()
        return {"soDong": n, "von": von, "dinhVon": dinh,
                "laiRongNgayUsd": rong_ngay, "ngatKhanCap": self.ngatKhanCap,
                "lyDoNgat": self.lyDoNgat}

    def ghi_lai_lo(self, usd: float) -> None:
        """Ghi một lần kết toán vào vốn và vào sổ ngày.

        ## `loNgayUsd` là lãi lỗ RÒNG của ngày, không phải tổng các lần lỗ

        Bản đầu cộng dồn `-usd` mỗi lần lỗ và không bao giờ trừ đi lần
        lãi. Với một cỗ máy đặt hàng chục lệnh một ngày thì tổng các lần
        lỗ luôn lớn, bất kể ngày ấy tốt hay xấu — nên cái trần mang tên
        "lỗ ngày" thực ra chặn theo ĐỘ BẬN, không theo mức thua.

        Đo được trên phiên phát lại: cầu dao ngắt ở khung 5.000 với lý do
        "chạm trần lỗ ngày $500" trong khi vốn đang là $12.896 trên
        $10.000 — tức là nó chặn một ngày **lãi 29%**. Rồi cả bảy ngày
        băng còn lại chạy mà không đặt nổi một lệnh.

        Một cái trần nói "lỗ" mà nhảy lúc đang lãi thì không đo thứ tên
        nó nói. Nay `loNgayUsd` là mức thua RÒNG (0 nếu ngày đang lãi),
        còn tổng gộp các lần lỗ vẫn giữ ở `loGopNgayUsd` — nó là số đo
        độ chao, đáng đọc, chỉ không đáng dùng làm cầu dao.
        """
        self.sang_ngay_moi()
        self.von += usd
        self.dinhVon = max(self.dinhVon, self.von)
        self.laiRongNgayUsd += usd
        if usd < 0:
            self.loGopNgayUsd += -usd
        self._soat_ngat()

    @property
    def loNgayUsd(self) -> float:
        """Mức THUA ròng hôm nay. Ngày đang lãi thì bằng 0."""
        return max(0.0, -self.laiRongNgayUsd)

    @property
    def sutVonPct(self) -> float:
        if self.dinhVon <= 0:
            return 0.0
        return (self.dinhVon - self.von) / self.dinhVon * 100.0

    def _soat_ngat(self) -> None:
        if self.loNgayUsd >= self.tranLoNgayUsd:
            self.ngat("chạm trần lỗ ngày $%.2f" % self.tranLoNgayUsd)
        if self.sutVonPct >= float(_RR["tranSutVonPct"]):
            self.ngat("sụt vốn %.1f%% (trần %.1f%%)"
                      % (self.sutVonPct, _RR["tranSutVonPct"]))

    def sang_ngay_moi(self) -> bool:
        """Ngày mới thì bộ đếm lỗ ngày về 0. Trả True nếu vừa sang ngày.

        Tách khỏi `ghi_lai_lo` vì ranh giới ngày trôi qua kể cả khi không
        có lệnh nào kết toán — và khi đó `ghi_lai_lo` không được gọi, nên
        bộ đếm không bao giờ reset.
        """
        hom_nay = self._ngay_hien_tai()
        if hom_nay == self.ngay:
            return False
        self.ngay = hom_nay
        self.laiRongNgayUsd = 0.0
        self.loGopNgayUsd = 0.0
        return True

    def ngat(self, lyDo: str) -> None:
        """Cầu dao. Đã ngắt thì chỉ người mở lại được, không tự phục hồi.

        Không tự bật lại là chủ ý: một cầu dao tự đóng sau N phút sẽ đóng
        đúng lúc thứ làm nó nhảy vẫn còn nguyên.
        """
        if not self.ngatKhanCap:
            self.ngatKhanCap = True
            self.lyDoNgat = lyDo
            self.soLanNgat += 1

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
        con_duoc = self.tranMoiThiTruongUsd - dang_co
        if con_duoc <= 0:
            return PhanQuyet(False, 0.0, [
                f"market {ch.ma} đã dùng ${dang_co:.2f}, chạm trần "
                f"${self.tranMoiThiTruongUsd:.2f}"])
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
        con_nhom = self.tranMoiTaiSanUsd - dang_nhom
        if con_nhom <= 0:
            return PhanQuyet(False, 0.0, [
                f"nhóm {nhom} đã dùng ${dang_nhom:.2f}, chạm trần "
                f"${self.tranMoiTaiSanUsd:.2f}"])
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
            # Lãi lỗ RÒNG hôm nay, và tổng gộp các lần lỗ. Cầu dao đọc
            # con số ròng; con số gộp là thước ĐỘ CHAO — đáng đọc, chỉ
            # không đáng dùng làm cầu dao, vì nó lớn theo độ bận chứ
            # không theo mức thua.
            "laiRongNgayUsd": self.laiRongNgayUsd,
            "loGopNgayUsd": self.loGopNgayUsd,
            "tranLoNgayUsd": self.tranLoNgayUsd,
            "tranMoiThiTruongUsd": self.tranMoiThiTruongUsd,
            "tranMoiTaiSanUsd": self.tranMoiTaiSanUsd,
            "ngatKhanCap": self.ngatKhanCap,
            "lyDoNgat": self.lyDoNgat,
        }
