"""Kho Đối — tồn kho hai chiều, và chỗ bot sống chết sau cú khớp đầu tiên.

Bot định hướng thường chỉ có một chân: mua rồi giữ. Bot thị trường tiên đoán
có HAI chân phải khớp, và tài liệu nói rất đúng rằng vấn đề lớn nhất bắt đầu
SAU cú khớp đầu tiên chứ không phải trước nó.

        đặt UP 45c + DOWN 49c   ->  cặp 94c, nhìn như arbitrage
        UP khớp 100%
        DOWN khớp 18%
        chợ dịch, DOWN thành 56c

        bây giờ không có arbitrage nào cả.
        có 82% một vị thế ĐỊNH HƯỚNG trần trụi mà không ai định mở.

Mô hình định giá không hề sai. Hỏng nằm ở khâu thi hành. Nên tồn kho phải tách
làm ba phần, và phần thứ ba có đồng hồ riêng:

    ĐÃ GHÉP CẶP     min(UP, DOWN)      payoff đã cố định, chỉ còn hỏi giá cặp
    ĐỊNH HƯỚNG      UP - DOWN          thiên lệch có chủ ý
    CHƯA PHÒNG HỘ   chân chờ chân kia  RỦI RO THẬT, và nó đang chạy đồng hồ
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .config import CONFIG

_KD = CONFIG["khoDoi"]


@dataclass
class ChanCho:
    """Một chân đã khớp đang chờ chân kia. Có đồng hồ riêng vì nó là rủi ro."""
    ben: str
    soCo: float
    giaTrungBinh: float
    moLucMs: float
    capMongMuon: float

    def tuoi_ms(self, bayGioMs: float | None = None) -> float:
        return (bayGioMs or time.time() * 1000.0) - self.moLucMs

    def qua_han(self, bayGioMs: float | None = None) -> bool:
        return self.tuoi_ms(bayGioMs) > float(_KD["giayChoChanHai"]) * 1000.0


@dataclass
class ViThe:
    """Tồn kho của MỘT market."""
    ma: str
    coUp: float = 0.0
    coDown: float = 0.0
    tienUp: float = 0.0      # tổng tiền đã trả cho UP
    tienDown: float = 0.0
    #: Phí đã trả cho vị thế này. `tienUp`/`tienDown` là tiền HÀNG, không
    #: gồm phí — nên nếu không giữ riêng khoản này thì phí biến mất khỏi
    #: mọi phép tính lãi lỗ. Nó ĐÃ biến mất: `dat_lenh` tính phí, in phí
    #: ra nhật ký, rồi thả nó xuống đất; `ket_toan._ghi_so` ghi thẳng
    #: `phiUsd=0.0`. Cả sổ kết toán, cầu dao lỗ ngày lẫn con số lãi trên
    #: buồng lái đều ĐẸP HƠN sự thật đúng bằng khoản phí — trong phiên
    #: giấy chạy hết băng, phí là $2,93 trên $32,99 lãi, tức 9%.
    phiUsd: float = 0.0
    #: Niềm tin của mô hình LÚC VÀO LỆNH, quy về P(UP), trọng số theo
    #: tiền. Hai trường thô để cộng dồn được qua nhiều lần khớp.
    #:
    #: Sổ kết toán vốn chỉ ghi `pDuDoan` — mà `ket_toan` cố ý giữ dự
    #: đoán GẦN LÚC ĐÓNG nhất, "vì đó là lúc mô hình biết nhiều nhất".
    #: Đúng cho việc chấm mô hình, nhưng nó KHÔNG phải con số đã tiêu
    #: tiền. Nhìn một dòng thua trong sổ, không cách nào biết đó là
    #: cược đúng mà xui hay cược ngược dấu — mà đấy đúng là câu vòng
    #: tiến hoá cần trả lời.
    #:
    #: Đo được trên sổ thật: dòng duy nhất ngày 29/08 ghi `pDuDoan
    #: 0,0438` cạnh một lệnh MUA UP giá $0,4545. Đọc thẳng thì như một
    #: lỗi dấu tày trời; thật ra là hai thời điểm khác nhau bị in cạnh
    #: nhau. Ghi cả hai thì hết mơ hồ.
    pVaoTichLuy: float = 0.0
    tienCoP: float = 0.0
    choCap: list[ChanCho] = field(default_factory=list)

    # ── giá vốn ───────────────────────────────────────────────────────────
    @property
    def giaVonUp(self) -> float:
        return self.tienUp / self.coUp if self.coUp > 0 else 0.0

    @property
    def giaVonDown(self) -> float:
        return self.tienDown / self.coDown if self.coDown > 0 else 0.0

    # ── ba phần ───────────────────────────────────────────────────────────
    @property
    def daGhepCap(self) -> float:
        return min(self.coUp, self.coDown)

    @property
    def dinhHuong(self) -> float:
        """Dương = thiên UP, âm = thiên DOWN."""
        return self.coUp - self.coDown

    @property
    def giaCap(self) -> float | None:
        """Giá vốn một cặp. Trên 1,00 là cặp ĐANG KHOÁ LỖ.

        Tính từ GIÁ VỐN THẬT (tiền đã trả / số cổ đã nhận), không phải từ giá
        yết lúc đặt lệnh. Đây đúng cái bẫy đã cắn tu-cam-thanh-runtime: ghi
        rủi ro theo giá yêu cầu thay vì giá khớp thì mẫu số của mọi phép hậu
        kiểm sai, và sai mẫu số là học sai toàn bộ.
        """
        if self.daGhepCap <= 0:
            return None
        return self.giaVonUp + self.giaVonDown

    @property
    def capKhoaLo(self) -> bool:
        gc = self.giaCap
        return gc is not None and gc > 1.0

    @property
    def loKhoaUsd(self) -> float:
        """Cặp đang khoá sẵn bao nhiêu lỗ. 0 nếu cặp có lãi."""
        gc = self.giaCap
        if gc is None or gc <= 1.0:
            return 0.0
        return (gc - 1.0) * self.daGhepCap

    # ── chưa phòng hộ ─────────────────────────────────────────────────────
    @property
    def chuaPhongHoUsd(self) -> float:
        """Bao nhiêu đô đang nằm trần một chân.

        Đo bằng ĐÔ chứ không bằng số cổ: 100 cổ ở 5c và 100 cổ ở 95c là hai
        mức rủi ro khác nhau 19 lần. Trần trong config cũng đặt bằng đô.
        """
        du = abs(self.dinhHuong)
        if du <= 0:
            return 0.0
        gia = self.giaVonUp if self.dinhHuong > 0 else self.giaVonDown
        return du * gia

    def cho_lau_nhat_ms(self, bayGioMs: float | None = None) -> float:
        if not self.choCap:
            return 0.0
        return max(c.tuoi_ms(bayGioMs) for c in self.choCap)

    def chan_qua_han(self, bayGioMs: float | None = None) -> list[ChanCho]:
        return [c for c in self.choCap if c.qua_han(bayGioMs)]

    # ── ghi khớp ──────────────────────────────────────────────────────────
    def ghi_khop(self, ben: str, soCo: float, giaKhop: float,
                 phiUsd: float = 0.0, pMoHinh: float | None = None) -> None:
        """Ghi một lần khớp. `giaKhop` phải là giá KHỚP, không phải giá đặt.

        `phiUsd` là phí của CHÍNH lần khớp này. Mặc định 0 cho những chỗ
        chỉ dựng tồn kho để đo phơi nhiễm (phơi nhiễm không quan tâm phí);
        đường đặt lệnh THẬT phải truyền vào.

        `pMoHinh` là giá trị hợp lý mô hình gán cho CHÍNH BÊN đang mua,
        tại thời điểm đặt lệnh. Quy về P(UP) ngay tại đây — một chân
        DOWN mua ở p=0,55 nghĩa là mô hình tin P(UP)=0,45 — vì nếu để
        hai quy ước cùng chạy trong sổ thì sớm muộn có người cộng nhầm.
        """
        if soCo <= 0:
            return
        self.phiUsd += max(0.0, float(phiUsd or 0.0))
        if pMoHinh is not None:
            try:
                pUp = float(pMoHinh) if ben == "UP" else 1.0 - float(pMoHinh)
            except (TypeError, ValueError):
                pUp = None
            if pUp is not None:
                tien = soCo * giaKhop
                self.pVaoTichLuy += pUp * tien
                self.tienCoP += tien
        if ben == "UP":
            self.coUp += soCo
            self.tienUp += soCo * giaKhop
        else:
            self.coDown += soCo
            self.tienDown += soCo * giaKhop

    def gia_tri_khi_ket_qua(self, upThang: bool) -> float:
        """Vị thế này trả về bao nhiêu đô khi market kết thúc."""
        return self.coUp if upThang else self.coDown

    def lai_lo_khi_ket_qua(self, upThang: bool) -> float:
        """Lãi lỗ RÒNG — đã trừ phí. Xem ghi chú ở `phiUsd`."""
        return (self.gia_tri_khi_ket_qua(upThang)
                - (self.tienUp + self.tienDown) - self.phiUsd)

    def don(self) -> None:
        """Khung đã xong: tồn kho về 0. MỘT chỗ, vì đã sót một lần rồi.

        `ket_toan` dọn vị thế ở HAI nơi, mỗi nơi một danh sách gán tay.
        Khi `phiUsd` ra đời, một trong hai nơi quên nó, nên phí của khung
        cũ chảy sang khung mới. Mỗi trường mới thêm vào `ViThe` lại là
        một lần bốc thăm xem có ai nhớ sửa cả hai chỗ không.

        Không dùng `__init__` lại: `Kho` giữ tham chiếu tới chính đối
        tượng này, thay bằng cái mới thì chỗ nào đang cầm bản cũ sẽ nhìn
        thấy tồn kho ma.
        """
        self.coUp = self.coDown = 0.0
        self.tienUp = self.tienDown = 0.0
        self.phiUsd = 0.0
        self.pVaoTichLuy = 0.0
        self.tienCoP = 0.0
        self.choCap.clear()

    @property
    def pVaoTb(self) -> float | None:
        """P(UP) mô hình tin lúc vào lệnh, bình quân theo TIỀN.

        Theo tiền chứ không theo số cổ: một lệnh $40 và một lệnh $2 không
        được nói bằng nhau về việc cỗ máy đã tin cái gì.
        """
        if self.tienCoP <= 0:
            return None
        return self.pVaoTichLuy / self.tienCoP

    @property
    def giaVaoTb(self) -> float | None:
        """Giá bình quân một cổ, gộp cả hai chân. Cặp kín thì vượt 1,00."""
        co = self.coUp + self.coDown
        if co <= 0:
            return None
        return (self.tienUp + self.tienDown) / co

    def lo_xau_nhat_usd(self) -> float:
        """Mất nhiều nhất bao nhiêu nếu khung này quay ra chiều xấu nhất.

        Thị trường nhị phân chỉ có hai kết cục, nên "xấu nhất" tính được
        CHÍNH XÁC, không phải ước:

            UP thắng   →  lãi lỗ = coUp   − tiềnVào − phí
            DOWN thắng →  lãi lỗ = coDown − tiềnVào − phí
            xấu nhất   =  min(coUp, coDown) − tiềnVào − phí

        Trả số DƯƠNG là số đô có thể mất; số 0 nghĩa là cặp đã ghép kín,
        chiều nào cũng không lỗ.

        Có phép này thì trần lỗ ngày mới chặn được TRƯỚC. Không có nó,
        trần lỗ ngày chỉ biết kêu sau khi tiền đã đi.
        """
        xau = min(self.coUp, self.coDown) - (self.tienUp + self.tienDown)             - self.phiUsd
        return max(0.0, -xau)

    def lo_xau_nhat_khi_mua(self, ben: str, soCo: float,
                            gia: float) -> float:
        """Lỗ xấu nhất SAU KHI mua thêm `soCo` cổ bên `ben` giá `gia`.

        Tách khỏi `lo_xau_nhat_usd` vì cổng rủi ro phải hỏi câu "nếu tôi
        mua thì sao", chứ hỏi "hiện giờ thế nào" thì đã muộn.

        Mua chân ĐỐI DIỆN là PHÒNG HỘ — nó làm số này GIẢM. Cổng nào chặn
        theo số này sẽ tự động không bao giờ chặn một lệnh phòng hộ, và
        đó là chủ ý: chặn phòng hộ vì hết ngân sách lỗ là để lại một chân
        trần trụi, tức là làm rủi ro TO RA nhân danh giảm rủi ro.
        """
        up = self.coUp + (soCo if ben == "UP" else 0.0)
        down = self.coDown + (0.0 if ben == "UP" else soCo)
        tien = self.tienUp + self.tienDown + soCo * gia
        return max(0.0, tien + self.phiUsd - min(up, down))

    def tom_tat(self) -> dict:
        return {
            "ma": self.ma,
            "coUp": self.coUp, "coDown": self.coDown,
            "giaVonUp": self.giaVonUp, "giaVonDown": self.giaVonDown,
            "daGhepCap": self.daGhepCap,
            "dinhHuong": self.dinhHuong,
            "giaCap": self.giaCap,
            "capKhoaLo": self.capKhoaLo,
            "loKhoaUsd": self.loKhoaUsd,
            "chuaPhongHoUsd": self.chuaPhongHoUsd,
            "choLauNhatMs": self.cho_lau_nhat_ms(),
            "soChanCho": len(self.choCap),
            "laiNeuUp": self.lai_lo_khi_ket_qua(True),
            "laiNeuDown": self.lai_lo_khi_ket_qua(False),
        }


# ══════════════════════════════════════════════════════════════════════════
#  TOÀN KHO — nhiều market, và cái bẫy tương quan
# ══════════════════════════════════════════════════════════════════════════

# Market khác nhau nhưng cùng chịu một cú. BTC_5M và BTC_15M là hai hợp đồng
# riêng, nhưng cùng long UP thì đó thực chất là MỘT cược vào Bitcoin. Và khi
# cả crypto cùng lao xuống thì ETH, SOL đi theo BTC.
# Bảng cứng này TỪNG là một lỗ hổng, và nó lộ ra đúng lúc bật thêm market:
# `XRP_5M` không có trong bảng nên nó rơi về nhánh mặc định và tự thành một
# nhóm tên "XRP_5M", không tương quan với ai. Tức là bật thêm một đồng coin
# đã lặng lẽ tạo một túi phơi nhiễm mà trần gộp không nhìn thấy.
#
# Nay suy từ mã nến trong config (`BTCUSDT` → `BTC`), nên thêm market là tự
# có nhóm. Bảng cứng chỉ còn để đè khi cần.
_NHOM_DE = {"BTC_5M": "BTC", "BTC_15M": "BTC", "ETH_5M": "ETH",
            "ETH_15M": "ETH", "SOL_5M": "SOL", "SOL_15M": "SOL"}

_HAU_TO = ("USDT", "USDC", "BUSD", "USD")


def nhom_tai_san(ma: str) -> str:
    if ma in _NHOM_DE:
        return _NHOM_DE[ma]
    for tt in CONFIG.get("thiTruong") or []:
        if tt.get("ma") != ma:
            continue
        nen = (tt.get("nen") or "").upper()
        for h in _HAU_TO:
            if nen.endswith(h):
                return nen[: -len(h)]
        if nen:
            return nen
    return ma.split("_")[0] or ma


# Hệ số tương quan giả định giữa các nhóm khi tính phơi nhiễm gộp. Đây là
# LUẬN chứ không phải số đo — khi `bang.py` ghi đủ thì thay bằng tương quan
# thật. Để cao hơn thực tế là an toàn hơn: nó làm trần siết sớm.
TUONG_QUAN = {("BTC", "ETH"): 0.85, ("BTC", "SOL"): 0.80, ("ETH", "SOL"): 0.85}

# Cặp KHÔNG có trong bảng thì lấy mức này, chứ KHÔNG lấy 0.
#
# Mặc định 0 nghĩa là "hai thứ này bù trừ hoàn toàn cho nhau" — một khẳng
# định rất mạnh, và nó được đưa ra chỉ vì có người quên gõ một dòng vào
# bảng. Sai theo hướng đó làm trần nới ra đúng lúc cần siết. Mặc định cao
# thì sai theo hướng siết sớm, và đó là hướng chịu được.
TUONG_QUAN_MAC_DINH = 0.75


def he_so_tuong_quan(a: str, b: str) -> float:
    if a == b:
        return 1.0
    v = TUONG_QUAN.get((a, b))
    if v is None:
        v = TUONG_QUAN.get((b, a))
    return TUONG_QUAN_MAC_DINH if v is None else v


class Kho:
    """Tồn kho toàn bộ, và phơi nhiễm gộp sau khi tính tương quan."""

    def __init__(self) -> None:
        self.viThe: dict[str, ViThe] = {}

    def lay(self, ma: str) -> ViThe:
        return self.viThe.setdefault(ma, ViThe(ma=ma))

    def phoi_nhiem_theo_nhom(self) -> dict[str, float]:
        """Phơi nhiễm định hướng theo đô, gộp theo nhóm tài sản."""
        ra: dict[str, float] = {}
        for ma, v in self.viThe.items():
            nhom = nhom_tai_san(ma)
            du = v.dinhHuong
            if du == 0:
                continue
            gia = v.giaVonUp if du > 0 else v.giaVonDown
            ra[nhom] = ra.get(nhom, 0.0) + (du * gia if du > 0 else -abs(du) * gia)
        return ra

    def phoi_nhiem_gop(self) -> float:
        """Phơi nhiễm crypto gộp, có tính tương quan chéo.

        Bốn market riêng lẻ mỗi cái 800 đô nhìn như bốn cược nhỏ. Nếu cả bốn
        cùng long và cùng tương quan gần 1 thì thực chất là MỘT cược 3.200 đô
        — và lúc crypto cùng lao xuống thì cả bốn cùng chết. Trần đặt trên
        từng market không hề chặn được tình huống đó.

        Đo bằng chuẩn bậc hai có ma trận tương quan: sqrt(x' C x). Tương quan
        bằng 0 thì kết quả bằng căn tổng bình phương (bù trừ nhiều); tương
        quan bằng 1 thì bằng đúng tổng (không bù trừ gì).
        """
        e = self.phoi_nhiem_theo_nhom()
        nhoms = list(e.keys())
        if not nhoms:
            return 0.0
        tong = 0.0
        for i, a in enumerate(nhoms):
            for j, b in enumerate(nhoms):
                tong += e[a] * e[b] * he_so_tuong_quan(a, b)
        return (tong ** 0.5) if tong > 0 else 0.0

    def tong_chua_phong_ho_usd(self) -> float:
        return sum(v.chuaPhongHoUsd for v in self.viThe.values())

    def tong_lo_khoa_usd(self) -> float:
        return sum(v.loKhoaUsd for v in self.viThe.values())

    def tom_tat(self) -> dict:
        return {
            "soThiTruong": len(self.viThe),
            "viThe": [v.tom_tat() for v in self.viThe.values()],
            "phoiNhiemNhom": self.phoi_nhiem_theo_nhom(),
            "phoiNhiemGop": self.phoi_nhiem_gop(),
            "tongChuaPhongHoUsd": self.tong_chua_phong_ho_usd(),
            "tongLoKhoaUsd": self.tong_lo_khoa_usd(),
        }
