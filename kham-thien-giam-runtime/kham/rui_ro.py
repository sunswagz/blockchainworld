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
from .config import CONFIG, che_hieu_luc
from .kho_doi import Kho, nhom_tai_san

_RR = CONFIG["ruiRo"]
_KD = CONFIG["khoDoi"]
_CL = CONFIG["canLoi"]


#: Mọi CỬA của bộ máy rủi ro, khai MỘT chỗ.
#:
#: Có danh mục này thì trả lời được một câu mà trước nay phải đi đọc mã:
#: **cửa nào chưa bao giờ chặn ai?** Ngày 30/08/2026, một phiên phát lại
#: 152.329 khung hình chỉ chạm tới 5 trong 12 cửa; bảy cửa còn lại —
#: gần như toàn bộ phần GIỮ VỐN — không chặn một lần nào, ở mọi mức vốn
#: từ $60 tới $100.000. Chúng có phép kiểm đơn vị, nhưng chưa từng chạy
#: thật một lần.
#:
#: Một cửa không bao giờ chạy thì không phân biệt được với một cửa hỏng.
CUA_RUI_RO = {
    "doi-soat": "chưa đối soát vị thế với sàn sau khi khởi động",
    "cau-dao": "cầu dao đang ngắt",
    "nguon": "nguồn dữ liệu không lành",
    "sang": "cơ hội không qua sàng (net edge / sức chứa / xác suất / cơ hội)",
    "cho-chan-hai": "không đủ thời gian phòng hộ chân hai",
    "tran-thi-truong": "chạm trần mỗi thị trường",
    "ngan-sach-lo-ngay": "hết ngân sách lỗ trong ngày",
    "tran-nhom": "chạm trần mỗi nhóm tài sản",
    "tran-gop": "chạm trần phơi nhiễm GỘP (bốn coin là một cược)",
    "tran-mot-chan": "chạm trần phần nằm trần một chân",
    "chan-qua-han": "còn chân chờ phòng hộ quá hạn",
    "duoi-mot-co": "sau khi siết còn dưới 1 cổ",
    "loi-qua-nho": "sau khi siết lợi kỳ vọng không đáng một lượt khớp",
}


@dataclass
class PhanQuyet:
    cho: bool
    soCoChoPhep: float
    lyDo: list[str] = field(default_factory=list)
    canhBao: list[str] = field(default_factory=list)
    daSiet: bool = False          # có bị cắt bớt so với đề xuất không
    ma: str = ""                  # MÃ CỬA đã chặn — xem `CUA_RUI_RO`


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
        #: Vốn lúc ngày mới bắt đầu — gốc của cả ba trần. Xem `_tran`.
        #:
        #: `None` = CHƯA CHỐT, và khi ấy `_tran` rơi về `vonBanDau`. Phải
        #: lười như vậy vì nhiều chỗ đặt `vonBanDau` SAU khi dựng —
        #: `PhienPhatLai(von=...)` và mấy phép kiểm. Chốt cứng ở đây thì
        #: `--von=10000` chạy với trần của tài khoản 1.000 đô, im lặng.
        self.vonDauNgay: float | None = None
        self.laiRongNgayUsd = 0.0
        self.loGopNgayUsd = 0.0
        self.ngay = self._ngay_hien_tai()
        self.ngatKhanCap = False
        self.lyDoNgat = ""
        #: NGẮT VÌ CÁI GÌ — quyết định then có tự mở khi sang ngày hay
        #: không. Xem `ngat`.
        self.loaiNgat = ""
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

    # Neo vào VỐN ĐẦU NGÀY, không vào `vonBanDau`.
    #
    # `vonBanDau` là một hằng số trong config, không bao giờ đổi. Tài
    # khoản mất nửa vốn thì trần "5% lỗ ngày" vẫn là $50 — tức 10% của
    # số còn lại. Rủi ro LỚN LÊN đúng lúc tài khoản YẾU ĐI, ngược hẳn ý
    # nghĩa của một cái trần theo phần trăm.
    #
    # Nhưng cũng KHÔNG neo vào vốn hiện tại: trần lỗ ngày mà chạy theo
    # vốn đang lỗ dần thì nó lùi xa mãi, không bao giờ chạm tới. Một cái
    # trần đuổi theo chính mình thì không phải trần.
    #
    # Vốn ĐẦU NGÀY đúng cả hai: đứng yên trong ngày (nên chạm tới được),
    # và bám theo tài khoản qua các ngày.

    def _tran(self, khoaPct: str, khoaUsd: str, macDinhPct: float,
              khoi: dict | None = None) -> float:
        """`khoi` mặc định là `ruiRo`; truyền vào để dùng cho khối khác.

        Có hai cái trần nữa nằm ở `khoDoi` mà lần đổi sang phần trăm bỏ
        sót — xem `tranChuaPhongHoUsd`.
        """
        kh = _RR if khoi is None else khoi
        pct = kh.get(khoaPct)
        if pct is None:
            cu = kh.get(khoaUsd)
            if cu is not None:
                return float(cu)
            pct = macDinhPct
        goc = self.vonDauNgay if self.vonDauNgay is not None else self.vonBanDau
        return max(0.0, goc) * float(pct) / 100.0

    @property
    def tranMoiThiTruongUsd(self) -> float:
        return self._tran("phanTramMoiThiTruong", "vonToiDaMoiThiTruongUsd", 10.0)

    @property
    def tranMoiTaiSanUsd(self) -> float:
        return self._tran("phanTramMoiTaiSan", "vonToiDaMoiTaiSanUsd", 20.0)

    @property
    def tranPhoiNhiemGopUsd(self) -> float:
        """Trần cho phơi nhiễm crypto GỘP (có tính tương quan chéo).

        Mặc định bằng ĐÚNG trần mỗi nhóm tài sản, và đó là cả lý lẽ: nếu
        cả rổ crypto tương quan gần 1 thì nó đúng là MỘT nhóm tài sản, nên
        phải chịu đúng cái trần của một nhóm.
        """
        return self._tran("phanTramPhoiNhiemGop", "phoiNhiemGopToiDaUsd", 20.0)

    @property
    def tranLoNgayUsd(self) -> float:
        return self._tran("phanTramLoNgay", "tranLoNgayUsd", 5.0)

    # ── HAI TRẦN CÒN SÓT LẠI Ở `khoDoi` ──────────────────────────────────
    #
    # Lần đổi ba trần trên sang phần trăm nêu đúng cái bệnh: "cả ba đều
    # lấy con số hợp lý cho MỘT tài khoản 1.000 đô... nạp thêm vốn thì
    # chúng đứng yên, tức là thêm tiền vào KHÔNG đổi hành vi cỗ máy".
    #
    # Rồi nó dừng ở khối `ruiRo`. Khối `khoDoi` còn nguyên hai cái, và
    # cùng một gốc $1.000: chân trần tối đa $50 (5%), lệch hướng tối đa
    # $100 (10%). Tài khoản $100.000 vẫn chỉ dám ôm $50 chân trần — tức
    # là cỗ máy không lớn lên được, còn tài khoản $200 thì hai cái trần
    # này lớn hơn cả vốn nên chúng không chặn gì hết.
    #
    # Phần trăm giữ đúng tỉ lệ cũ, nên tài khoản 1.000 đô cư xử y hệt.

    @property
    def tranChuaPhongHoUsd(self) -> float:
        """Trần tiền nằm TRẦN một chân (cổng 8)."""
        return self._tran("phanTramChuaPhongHo", "capChuaKhopToiDaUsd",
                          5.0, _KD)

    @property
    def tranLechHuongUsd(self) -> float:
        """Trần cho phần thiên lệch có chủ ý của chiến thuật phòng hộ."""
        return self._tran("phanTramLechHuong", "lechHuongToiDaUsd",
                          10.0, _KD)

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
        # Vốn ĐẦU NGÀY = vốn hiện tại trừ đi lãi lỗ đã xảy ra TRONG ngày.
        # Lấy thẳng `von` là sai: những khoản lỗ của hôm nay đã nằm trong
        # nó rồi, nên trần ngày sẽ co lại theo chính khoản lỗ nó đang đo.
        self.vonDauNgay = von - rong_ngay
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
        # Thứ tự: SỤT VỐN trước. Nếu cả hai điều kiện cùng đúng thì cái
        # ghi vào `loaiNgat` phải là cái NẶNG hơn — `ngat()` chỉ nhận
        # lần gọi đầu, và một then sụt-vốn bị dán nhãn "lo-ngay" sẽ tự
        # mở sáng hôm sau trong khi điều kiện của nó còn nguyên.
        if self.sutVonPct >= float(_RR["tranSutVonPct"]):
            self.ngat("sụt vốn %.1f%% (trần %.1f%%)"
                      % (self.sutVonPct, _RR["tranSutVonPct"]),
                      loai="sut-von")
        if self.loNgayUsd >= self.tranLoNgayUsd:
            self.ngat("chạm trần lỗ ngày $%.2f" % self.tranLoNgayUsd,
                      loai="lo-ngay")

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
        # Chốt lại gốc của ba trần cho ngày mới. Đây là chỗ DUY NHẤT
        # `vonDauNgay` đổi trong lúc chạy — trong ngày nó phải đứng yên.
        self.vonDauNgay = self.von

        # Then đóng vì trần lỗ NGÀY thì mở khi sang ngày. Điều kiện đã
        # hết hiệu lực cùng lúc với bộ đếm ở hai dòng trên; giữ then
        # tiếp là giữ một cái then không còn lý do.
        if self.ngatKhanCap and self.loaiNgat == "lo-ngay":
            self.ngatKhanCap = False
            self.lyDoNgat = ""
            self.loaiNgat = ""
        # …rồi SOÁT LẠI. Nếu sụt vốn vẫn quá trần thì nó ngắt lại NGAY,
        # lần này với đúng nhãn `sut-von` — một điều kiện nhiều ngày
        # không được mở chỉ vì đồng hồ sang ngày.
        self._soat_ngat()
        return True

    def ngat(self, lyDo: str, loai: str = "tay") -> None:
        """Cầu dao. `loai` nói NGẮT VÌ CÁI GÌ, và điều đó có hệ quả.

        Không tự bật lại là chủ ý — một cầu dao tự đóng sau N phút sẽ
        đóng đúng lúc thứ làm nó nhảy vẫn còn nguyên. Nhưng "không tự
        bật lại" phải hiểu theo ĐIỀU KIỆN đã làm nó nhảy, chứ không
        theo đồng hồ:

            lo-ngay   ngân sách lỗ NGÀY. Điều kiện ấy hết hiệu lực khi
                      sang ngày mới — `sang_ngay_moi` đặt lại bộ đếm.
                      Nên giữ then qua đêm là giữ một cái then mà lý do
                      của nó đã biến mất.
            sut-von   sụt từ ĐỈNH vốn. Điều kiện NHIỀU NGÀY, và nó vẫn
                      đúng sáng hôm sau. Then giữ nguyên.

        ## Vì sao chuyện này quan trọng hơn vẻ ngoài

        Bản trước không phân biệt, nên một lần chạm trần lỗ NGÀY giết cỗ
        máy VĨNH VIỄN. Cái trần mang tên "ngày" mà hậu quả là mãi mãi.

        Đo được 05/09/2026 trên băng 12 ngày, vốn $1.000, quét ngân sách
        ngày từ 5% tới 50%:

            ngân sách ngày   cửa sổ   sụt vốn thật   CẦU DAO chặn
                 5%            20        7,32%        120.926
                12%            20       14,10%        118.063
                15%            21       17,03%        116.473
                18%            25       20,23%        113.134
                20%           228        1,44%              0
                50%           229        1,42%              0

        Một vách dốc đứng giữa 18 và 20, và nó KHÔNG phải chuyện đánh
        đổi rủi ro: dưới ngưỡng ấy máy chạm trần ngày ngay ngày đầu rồi
        cài then luôn; từ 20% trở lên nó không chạm lần nào trong 12
        ngày nên không bao giờ cài. Cả quãng ở giữa vừa ít giao dịch
        vừa sụt vốn NẶNG HƠN — vì nó sống thêm được một chút với vị thế
        to hơn rồi mới chết.

        (Một giả thuyết đã bị BÁC trên đường: rằng vách nằm ở chỗ ngân
        sách ngày ≥ trần phơi nhiễm gộp. Thử `ngày 20 · gộp 40` vẫn
        thông, `ngày 10 · gộp 8` vẫn chặn. Trần gộp không liên quan.)
        """
        if not self.ngatKhanCap:
            self.ngatKhanCap = True
            self.lyDoNgat = lyDo
            self.loaiNgat = loai
            self.soLanNgat += 1

    def mo_lai(self) -> None:
        """Mở lại bằng tay. HẠ LUÔN ĐỈNH VỐN về vốn hiện tại.

        ## Vì sao phải hạ đỉnh, đo được chứ không suy đoán

        Bản đầu chỉ xoá `ngatKhanCap` và `lyDoNgat`. Nhưng cầu dao sụt
        vốn ngắt vì `sutVonPct = (đỉnh − vốn) / đỉnh`, và cái đó KHÔNG
        đổi khi xoá cờ. Nên `_soat_ngat` ở lần kết toán kế tiếp ngắt lại
        ngay — kể cả một lệnh LÃI.

        Đo trên đúng số của làn giấy ngày 05/09/2026 (vốn 932,44 · đỉnh
        1.074,71 · trần 10%):

            _soat_ngat()          ⇒ ngắt, sụt 13,24%
            mo_lai()              ⇒ cờ tắt
            kết toán một lệnh +20 ⇒ NGẮT LẠI, sụt 11,38%

        Để thoát hẳn, vốn phải lên 967,24 — nhưng mỗi lần mở tay chỉ
        sống được tới lần kết toán kế tiếp, nên nó không bao giờ đi hết
        được quãng ấy. Đó là một BẾ TẮC: cỗ máy không có đường tự về, và
        cái nút duy nhất để cứu nó thì không cứu được gì. Nó chạy, tốn
        điện, và từ chối mọi cơ hội — 120.926 lần trong một lượt chạy
        lại 12 ngày.

        ## Vì sao hạ đỉnh là ĐÚNG chứ không phải nới tay

        Một cầu dao sụt vốn hỏi: "từ đỉnh gần nhất tới giờ mất bao
        nhiêu?" Người mở lại bằng tay đang nói: "tôi đã xem, tôi CHẤP
        NHẬN khoản sụt này, đo lại từ đây." Không hạ đỉnh thì câu trả
        lời ấy không có chỗ diễn đạt, và cái nút thành đồ trang trí.

        Đây KHÔNG phải nới trần: trần vẫn 10%, và 10% tiếp theo tính từ
        mốc mới. Sụt thêm 10% nữa là lại ngắt.

        Và nó chỉ xảy ra khi có người CỐ Ý bấm — `ngat()` vẫn không tự
        phục hồi, `_soat_ngat` vẫn chạy mỗi lần kết toán.
        """
        self.ngatKhanCap = False
        self.lyDoNgat = ""
        self.loaiNgat = ""
        # Thứ tự quan trọng: hạ đỉnh SAU khi xoá cờ thì `sutVonPct` về 0
        # và lần `_soat_ngat` kế tiếp không có gì để ngắt. Hạ trước, xoá
        # sau cũng ra cùng kết quả — nhưng chỉ xoá cờ mà KHÔNG hạ đỉnh
        # thì đúng là con bọ nói ở trên.
        self.dinhVon = self.von

    def con_thieu_de_thoat_ngat(self) -> float:
        """Còn thiếu bao nhiêu đô nữa thì tự thoát khỏi cầu dao sụt vốn.

        0 nghĩa là không bị cầu dao sụt vốn giữ. Con số này đáng hiện ra
        vì nếu không ai nhìn thấy nó, một cỗ máy đang bế tắc trông y hệt
        một cỗ máy đang thận trọng.
        """
        tran = float(_RR["tranSutVonPct"])
        can = self.dinhVon * (1.0 - tran / 100.0)
        return max(0.0, can - self.von)

    # ── cửa duyệt ─────────────────────────────────────────────────────────
    def duyet(self, ch: CoHoi, sucKhoe: SucKhoeNguon,
              conLaiGiay: float, duDeDungKelly: bool) -> PhanQuyet:
        """Cửa duy nhất. Mọi lệnh phải đi qua đây, kể cả lệnh phòng hộ."""
        ly_do: list[str] = []
        canh: list[str] = []

        # 0. CHƯA ĐỐI SOÁT VỊ THẾ VỚI SÀN — chỉ chặn đường THẬT
        #
        # `Kho` chỉ nằm trong bộ nhớ. Khởi động lại giữa một khung là bot
        # quên mình đang cầm cổ phiếu, trong khi sàn thì không quên. Ở
        # chế độ GIẤY chuyện đó vô hại: vị thế giấy là của riêng ta.
        #
        # Ở chế độ THẬT nó là mối nguy nặng nhất trong cả cỗ máy. Bot mở
        # thêm trên một tài khoản đã có sẵn hàng; hạn mức phơi nhiễm
        # tính trên một tồn kho trống rỗng không có thật; và lần kết
        # toán ấy không vào sổ nên `nap_tu_so` cũng không thấy.
        #
        # Chưa nối được sàn thì không cách nào biết đang cầm gì. Nhưng
        # có một việc làm được ngay, và nó là việc đúng: TỪ CHỐI, có nêu
        # tên. Một lời từ chối đứng đúng chỗ mối nguy còn hơn một giả
        # định im lặng rằng tài khoản đang trống — giả định ấy sai đúng
        # vào lúc nó đắt nhất.
        #
        # Đặt TRƯỚC cầu dao vì nó không phụ thuộc gì cả: chưa biết mình
        # cầm gì thì mọi phép tính phía sau đều tính trên số bịa.
        if che_hieu_luc() == "that" and not getattr(
                self.kho, "daDoiSoatVoiSan", False):
            return PhanQuyet(False, 0.0, [
                "CHƯA ĐỐI SOÁT VỊ THẾ VỚI SÀN sau khi khởi động — không "
                "biết đang cầm gì thì mọi hạn mức phía sau đều tính trên "
                "một tồn kho không có thật"], ma="doi-soat")

        # 1. cầu dao
        if self.ngatKhanCap:
            return PhanQuyet(False, 0.0, [f"CẦU DAO ĐANG NGẮT: {self.lyDoNgat}"], ma="cau-dao")

        # 2. sức khoẻ nguồn — trước mọi phép tính, vì tính trên số cũ là vô nghĩa
        van_de = sucKhoe.van_de()
        if van_de:
            return PhanQuyet(False, 0.0, ["nguồn không lành: " + "; ".join(van_de)], ma="nguon")

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
            return PhanQuyet(False, 0.0, ly_do or ["không qua sàng"], ma="sang")

        # 4. market sắp khoá thì không mở vị thế MỚI
        #    Chân chưa phòng hộ lúc chuông reo là rủi ro trần trụi không gỡ được.
        if conLaiGiay <= float(_KD["giayChoChanHai"]):
            return PhanQuyet(False, 0.0, [
                f"còn {conLaiGiay:.0f}s, không đủ thời gian phòng hộ chân hai "
                f"(cần {_KD['giayChoChanHai']}s)"], ma="cho-chan-hai")

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
                f"${self.tranMoiThiTruongUsd:.2f}"], ma="tran-thi-truong")
        max_co = con_duoc / max(1e-9, ch.vwap)
        if max_co < cho_phep:
            cho_phep = max_co
            canh.append(f"trần vốn market cắt còn {max_co:.0f} cổ")

        # 6b. NGÂN SÁCH LỖ NGÀY CÒN LẠI — trần ngày phải chặn TRƯỚC
        #
        # Trước bản này, trần lỗ ngày chỉ sống ở cổng 1: cầu dao đã ngắt
        # thì từ chối. Tức là nó không bao giờ NGĂN được lần vượt trần —
        # nó chỉ ghi nhận sau khi tiền đã đi.
        #
        # Và hai cái trần không đứng chung được với nhau. Trần mỗi market
        # là 10% vốn; trần lỗ ngày là 5%. Vị thế nhị phân thua thì mất
        # TRỌN số tiền vào. Nên MỘT lệnh cỡ tối đa, thua, là mất gấp đôi
        # ngân sách cả ngày — và không cổng nào ngăn được.
        #
        # Không phải giả thiết. Sổ kết toán ngày 29/08 có đúng một dòng:
        # mua 109,91 cổ UP hết $49,95, thua sạch. Trần ngày $50,00. Một
        # lệnh, một lần, 99,9% ngân sách ngày. Cầu dao chưa kịp ngắt vì
        # nó chỉ được hỏi ở lệnh SAU.
        #
        # Phép chặn dựa trên LỖ XẤU NHẤT, thứ tính chính xác được ở chợ
        # nhị phân: `min(coUp, coDown) − tiềnVào − phí`. Cộng qua mọi
        # market vì một ngày xấu thì chúng xấu cùng nhau.
        #
        # Chân PHÒNG HỘ đi qua tự do: mua chân đối diện làm lỗ xấu nhất
        # GIẢM, nên `dư` không bao giờ âm vì nó. Chặn phòng hộ vì hết
        # ngân sách là để lại một chân trần trụi — làm rủi ro TO RA nhân
        # danh giảm rủi ro.
        tranNgay = self.tranLoNgayUsd
        if tranNgay > 0:
            # `laiRongNgayUsd` âm khi đang lỗ; lãi của ngày KHÔNG được
            # cộng thêm vào ngân sách (lãi chưa rút thì vẫn là tiền đang
            # đặt cược, và một cái trần nới ra theo lãi thì lại là cái
            # trần đuổi theo chính mình).
            # Dùng CHÍNH hai phép mà buồng lái đọc, không tính lại tại
            # chỗ: một cái cổng chặn theo con số A trong khi màn hình
            # hiện con số B là thứ không ai gỡ nổi lúc có chuyện.
            con_ngay = tranNgay + min(0.0, self.laiRongNgayUsd)
            dang_ganh = self.lo_xau_nhat_gop_usd()
            du = self.con_ngan_sach_ngay_usd()
            # Sức chứa phòng hộ: mua tới ngần này cổ bên `ben` thì lỗ xấu
            # nhất còn GIẢM, vì nó lấp vào chân mỏng.
            phong_ho = max(0.0, (v.coDown - v.coUp) if ch.ben == "UP"
                           else (v.coUp - v.coDown))
            if du <= 0:
                if phong_ho < 1:
                    return PhanQuyet(False, 0.0, [
                        f"lỗ xấu nhất đang gánh ${dang_ganh:.2f} đã hết "
                        f"ngân sách lỗ ngày ${con_ngay:.2f} — chỉ còn nhận "
                        "lệnh PHÒNG HỘ"], ma="ngan-sach-lo-ngay")
                if phong_ho < cho_phep:
                    cho_phep = phong_ho
                    canh.append(f"hết ngân sách lỗ ngày, chỉ cho phòng hộ "
                                f"{phong_ho:.0f} cổ")
            else:
                # Chia cho `vwap + phi`, KHÔNG phải `vwap`. Phí cũng là
                # tiền mất, và nó mất KỂ CẢ khi cược thắng.
                #
                # Đo được: phiên phát lại ghi `laiLo −50,95` trên khoản
                # vào $49,95 với trần ngày $50,00 — vượt trần đúng bằng
                # khoản phí $1,00. Cái cổng chiếu theo `vwap` nên nó cho
                # qua một cỡ lệnh mà chính nó vừa cấm.
                gia_that = ch.vwap + max(0.0, float(ch.phi or 0.0))

                # MỘT VỊ THẾ KHÔNG ĐƯỢC TIÊU HẾT NGÂN SÁCH NGÀY
                #
                # `du` là toàn bộ phần ngân sách còn lại, nên cổng này
                # cho một lệnh duy nhất lấy sạch. Đo trên sổ kết toán
                # thật 05/09/2026: lệnh đầu tiên của ngày ăn 100,0% và
                # 107% ngân sách, mọi lệnh cỡ đầy đủ đều nằm ở 87–107%.
                # Sau lệnh ấy, cả ngày không còn gì để vào.
                #
                # Hệ quả không phải "ít giao dịch" mà là MẤT PHÂN TÁN:
                # một vị thế mỗi ngày thì mỗi ngày là một lần tung đồng
                # xu. Lượt chạy lại 12 ngày cho 20 cửa sổ, sụt vốn thật
                # 7,32%, khoảng tin CHỨA 0. Cùng cỗ máy ấy khi không bị
                # trần chặn: 229 cửa sổ, sụt vốn 1,42%, khoảng tin
                # KHÔNG chứa 0. Trần chặt mua an toàn bằng cách giết
                # đúng thứ làm nên an toàn.
                #
                # Nút này KHÔNG nới rủi ro ngày: `du` vẫn chặn tổng, và
                # trần ngày vẫn nguyên. Nó chỉ cấm một lệnh chiếm trọn.
                # Gốc là ngân sách CẢ NGÀY chứ không phải phần CÒN LẠI:
                # lấy phần còn lại thì cỡ lệnh co theo cấp số nhân
                # (25% của 75% của…) và cái đuôi ấy vô nghĩa.
                phan = float(_RR.get("phanNganSachMoiViThe", 1.0))
                duLenh = du if phan >= 1.0 else min(du, tranNgay * phan)
                max_ngay = (duLenh + phong_ho) / max(1e-9, gia_that)
                if max_ngay < cho_phep:
                    cho_phep = max_ngay
                    canh.append(
                        f"ngân sách lỗ ngày còn ${du:.2f} "
                        + (f"(mỗi vị thế tối đa ${tranNgay * phan:.2f}) "
                           if phan < 1.0 else "")
                        + f"cắt còn {max_ngay:.0f} cổ")

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
                f"${self.tranMoiTaiSanUsd:.2f}"], ma="tran-nhom")
        max_nhom = con_nhom / max(1e-9, ch.vwap)
        if max_nhom < cho_phep:
            cho_phep = max_nhom
            canh.append(f"trần vốn nhóm {nhom} cắt còn {max_nhom:.0f} cổ")

        # 7b. TRẦN PHƠI NHIỄM GỘP — bốn cược tương quan là MỘT cược
        #
        # `Kho.phoi_nhiem_gop()` đã tính sẵn con số này từ đầu, có ma
        # trận tương quan hẳn hoi, và docstring của nó nói thẳng: "Trần
        # đặt trên từng market không hề chặn được tình huống đó." Rồi
        # KHÔNG AI CHẶN theo nó — nó chỉ được vẽ lên buồng lái.
        #
        # Khác với `quyet_chan` (nơi ba lớp khác đã che phần nguy hiểm),
        # ở đây KHÔNG có lớp nào khác: trần mỗi market không che, mà trần
        # mỗi nhóm cũng không — bốn crypto nằm ở BỐN nhóm khác nhau
        # (BTC, ETH, SOL, XRP), nên mỗi cái đều "trong hạn mức" trong khi
        # cả rổ là một cược duy nhất vào beta crypto.
        #
        # Trần đặt BẰNG trần mỗi nhóm tài sản, và đó là cả lý lẽ: nếu cả
        # rổ crypto tương quan gần 1 thì nó ĐÚNG LÀ một nhóm tài sản, nên
        # phải chịu đúng cái trần của một nhóm. Không phải một con số mới
        # nghĩ ra — là con số cũ áp cho đúng thứ nó mô tả.
        gop = self.kho.phoi_nhiem_gop()
        tranGop = self.tranPhoiNhiemGopUsd
        if tranGop > 0:
            con_gop = tranGop - gop
            if con_gop <= 0:
                return PhanQuyet(False, 0.0, [
                    f"phơi nhiễm crypto GỘP ${gop:.2f} chạm trần "
                    f"${tranGop:.2f} — bốn market tương quan là MỘT cược, "
                    "trần mỗi market không chặn được chuyện này"], ma="tran-gop")
            max_gop = con_gop / max(1e-9, ch.vwap)
            if max_gop < cho_phep:
                cho_phep = max_gop
                canh.append(f"trần phơi nhiễm gộp cắt còn {max_gop:.0f} cổ")

        # 8. trần tiền nằm trần một chân
        them_tran = cho_phep * ch.vwap
        dang_tran = self.kho.tong_chua_phong_ho_usd()
        tranTran = self.tranChuaPhongHoUsd
        if dang_tran + them_tran > tranTran:
            con = tranTran - dang_tran
            if con <= 0:
                return PhanQuyet(False, 0.0, [
                    f"đang có ${dang_tran:.2f} nằm trần một chân, chạm trần "
                    f"${tranTran:.2f}"], ma="tran-mot-chan")
            cho_phep = con / max(1e-9, ch.vwap)
            canh.append(f"trần chưa phòng hộ cắt còn {cho_phep:.0f} cổ")

        # 9. chân quá hạn chờ — dừng mở thêm cho tới khi dọn xong
        qua_han = v.chan_qua_han()
        if qua_han:
            return PhanQuyet(False, 0.0, [
                f"{len(qua_han)} chân đã chờ quá {_KD['giayChoChanHai']}s "
                f"chưa phòng hộ xong — dọn trước khi mở thêm"], ma="chan-qua-han")

        # 10. trần lệnh thật
        if CONFIG.get("che") == "that":
            tran = float(CONFIG["datLenh"]["tranMoiLenhUsd"])
            max_that = tran / max(1e-9, ch.vwap)
            if max_that < cho_phep:
                cho_phep = max_that
                canh.append(f"trần lệnh thật ${tran} cắt còn {max_that:.0f} cổ")

        # 11. sau khi siết, cơ hội còn đáng làm không
        if cho_phep < 1:
            return PhanQuyet(False, 0.0, ["sau khi siết còn dưới 1 cổ"], ma="duoi-mot-co")
        if cho_phep * ch.netEdge < 0.01:
            return PhanQuyet(False, 0.0, [
                f"sau khi siết lợi kỳ vọng chỉ ${cho_phep * ch.netEdge:.4f} — "
                f"không đáng một lượt khớp"], ma="loi-qua-nho")

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

    def lo_xau_nhat_gop_usd(self) -> float:
        """Tổng lỗ xấu nhất đang gánh, cộng qua mọi market.

        Cộng THẲNG chứ không chiết khấu theo tương quan, và đó là chủ ý:
        đây là câu hỏi "ngày hôm nay xấu nhất thì mất bao nhiêu", mà một
        ngày xấu thì bốn market crypto xấu cùng nhau. Chỗ cần tương quan
        là trần PHƠI NHIỄM (cổng 7b), không phải chỗ này.
        """
        return sum(x.lo_xau_nhat_usd() for x in self.kho.viThe.values())

    def con_ngan_sach_ngay_usd(self) -> float:
        """Ngân sách lỗ ngày còn lại, TRỪ ĐI phần đang gánh chưa kết toán."""
        return (self.tranLoNgayUsd + min(0.0, self.laiRongNgayUsd)
                - self.lo_xau_nhat_gop_usd())

    def tom_tat(self) -> dict:
        return {
            "von": self.von,
            "vonBanDau": self.vonBanDau,
            "vonDauNgay": (self.vonDauNgay if self.vonDauNgay is not None
                           else self.vonBanDau),
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
            # Hai con số của cổng 6b. Chúng đáng hiện ra vì `loNgayUsd`
            # chỉ kể chuyện ĐÃ RỒI: nó không nói cỗ máy đang gánh sẵn
            # bao nhiêu rủi ro chưa kết toán. Một ngày có `loNgayUsd = 0`
            # mà `loXauNhatGopUsd` bằng đúng trần thì trần ấy đã tiêu.
            "loXauNhatGopUsd": self.lo_xau_nhat_gop_usd(),
            "conNganSachNgayUsd": self.con_ngan_sach_ngay_usd(),
            "tranPhoiNhiemGopUsd": self.tranPhoiNhiemGopUsd,
            "tranMoiThiTruongUsd": self.tranMoiThiTruongUsd,
            "tranMoiTaiSanUsd": self.tranMoiTaiSanUsd,
            "ngatKhanCap": self.ngatKhanCap,
            # NGẮT VÌ CÁI GÌ. Không hiện ra thì không ai phân biệt được
            # một then sẽ tự mở sáng mai với một then nằm mãi.
            "loaiNgat": self.loaiNgat,
            # Còn thiếu bao nhiêu để tự thoát cầu dao sụt vốn. Không
            # hiện ra thì một cỗ máy đang BẾ TẮC trông y hệt một cỗ máy
            # đang thận trọng — xem `mo_lai`.
            "conThieuDeThoatUsd": self.con_thieu_de_thoat_ngat(),
            "lyDoNgat": self.lyDoNgat,
        }
