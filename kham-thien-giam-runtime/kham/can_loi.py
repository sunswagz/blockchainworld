"""Cân Lợi — biến "lợi thế trên giấy" thành "lợi thế ăn được".

Câu treo trên tường của cả runtime này:

        CORRELATION    khong phai ALPHA
        SIGNAL         khong phai ALPHA
        LATENCY        khong phai ALPHA
        ACCURACY       khong phai ALPHA

        NET EXECUTABLE EDGE  =  ALPHA

Nghiên cứu OpenMarket (07/2026) ghép 727 triệu bản ghi Polymarket–Binance ở
mức mili-giây, 43 đặc trưng vi cấu trúc, walk-forward đàng hoàng. Họ XÁC NHẬN
Polymarket phản ứng trễ sau Binance, trung vị khoảng 347 ms. Và mô hình của họ
vẫn KHÔNG tạo được lợi thế giao dịch ngoài mẫu sau phí và trượt giá.

Tức là: tín hiệu có thật, độ trễ có thật, và cả hai cộng lại vẫn có thể ra một
chiến lược lỗ. Chỗ chênh lệch nằm đúng ở module này.

## Công thức

        netEdge(q) = fairValue
                   - vwap(q)          <- giá THẬT cho q cổ, không phải best ask
                   - phi(q)           <- maker 0, taker theo giá
                   - truotGia
                   - batDinhMoHinh    <- sigma ước lượng có thể lệch
                   - bienAnToan       <- chỗ trả giá cho mọi thứ chưa nghĩ ra

Năm khoản trừ. Bỏ bất kỳ khoản nào cũng ra một con số đẹp hơn và sai hơn.

## Một cơ hội không bao giờ chỉ là một con số

`netEdge` một mình vô dụng. Cơ hội 10c mà chỉ khớp được 4 đô thì kém hơn cơ
hội 1,2c khớp được 20.000 đô. Nên mọi cơ hội ở đây đều mang theo `sucChua`
(khớp được bao nhiêu), `xacSuatKhop` (có khớp không), và `nuaDoiMs` (sống được
bao lâu trước khi chợ ăn mất).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .config import CONFIG
from .so_lenh import SoLenh

_PHI = CONFIG["phi"]
_CL = CONFIG["canLoi"]


# ══════════════════════════════════════════════════════════════════════════
#  PHÍ
# ══════════════════════════════════════════════════════════════════════════

def phi_taker(gia: float, soCo: float) -> float:
    """Phí taker Polymarket, tính bằng ĐÔ-LA cho cả lô.

    ĐÃ ĐỐI CHIẾU tài liệu chính thức ngày 30/08/2026 —
    docs.polymarket.com/trading/fees (API bị chặn ở tầng TLS, nhưng
    trang tài liệu thì vào được):

        fee = C × feeRate × p × (1 − p)

    `C` là số cổ, `p` là giá cổ. Hạng mục Crypto: **feeRate = 0,07**.
    Maker không bao giờ bị thu phí. Phí làm tròn 5 chữ số thập phân, và
    dưới 0,00001 USDC thì về 0.

    ## Bản cũ sai CẢ HAI vế, và sai cùng một chiều

    Bản trước viết `heSo × min(p, 1−p) × soCo` với `heSo = 0,02`. Hình
    dạng `min(p, 1−p)` cũng đạt đỉnh ở 50% và về 0 ở hai đầu, nên nó
    trông đúng — nhưng nó KHÔNG phải hàm của Polymarket, và hệ số cũng
    lệch. Đo trên 100 cổ:

           p    ta tính   Polymarket   thiếu
        0,01     $0,020      $0,069    71,1%
        0,10     $0,200      $0,630    68,3%
        0,25     $0,500      $1,313    61,9%
        0,50     $1,000      $1,750    42,9%

    Thiếu 43–71% ở MỌI mức giá, và luôn thiếu chứ không bao giờ thừa.
    Nghĩa là mọi `netEdge` từ trước tới nay đều lạc quan đúng chừng ấy —
    đúng cái "lệch im lặng" mà danh sách trước cổng cảnh báo, và nay đo
    được thay vì phỏng đoán.

    Bảng phí chính thức (Crypto, 100 cổ) nằm trong bộ kiểm làm phép canh:
    khớp tới từng xu là cách duy nhất chắc rằng cả DẠNG HÀM lẫn hệ số
    đều đúng, chứ không phải một trong hai.

    ## Chưa đối chiếu được: hạng mục của TỪNG market

    Bảng phí đổi theo hạng mục (Crypto 0,07 · Sports 0,05 · Finance
    0,04 · Geopolitics 0). Cả năm market đang theo đều là crypto nên
    0,07 đúng cho chúng. Nhưng hạng mục THẬT nằm trong `Market Details`
    của API — thứ đang bị chặn. Thêm market ngoài crypto thì phải đọc
    lại hệ số từ đó, đừng dùng lại con số này.
    """
    if soCo <= 0:
        return 0.0
    p = min(max(gia, 0.0), 1.0)
    ph = float(_PHI["takerHeSo"]) * p * (1.0 - p) * soCo
    ph = round(ph, 5)
    return ph if ph >= 1e-5 else 0.0


def phi_maker(gia: float, soCo: float) -> float:
    """Phí maker. Bằng 0 theo biểu phí hiện hành — và đó là cả một chiến lược.

    Chênh lệch maker/taker đủ lớn để lật một chiến lược từ lãi thành lỗ. Cặp
    UP 32,9c + DOWN 66,2c = 99,1c cho gross 0,9c mỗi cặp; ăn cả hai chân bằng
    lệnh thị trường là mất sạch vào phí taker và trượt giá. Cũng đúng cặp ấy
    mà đặt limit chờ khớp thì phí bằng 0 và còn có thể nhận rebate.
    """
    return float(_PHI["makerBps"]) / 10_000.0 * gia * max(0.0, soCo)


# ══════════════════════════════════════════════════════════════════════════
#  CƠ HỘI
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class CoHoi:
    """Một cơ hội đã cân đủ mọi khoản trừ. Đây là thứ Risk Engine nhận."""
    ma: str
    ben: str                # "UP" | "DOWN"
    chienThuat: str
    fairValue: float
    giaCho: float           # best ask, chỉ để hiển thị
    vwap: float             # giá THẬT cho soCo cổ
    soCo: float

    grossEdge: float
    phi: float              # quy về mỗi cổ
    truotGia: float
    batDinhMoHinh: float
    bienAnToan: float
    netEdge: float

    sucChua: float
    xacSuatKhop: float
    nuaDoiMs: float
    laMaker: bool
    dayDu: bool
    ghiChu: list[str] = field(default_factory=list)

    @property
    def loiUsd(self) -> float:
        """Kỳ vọng lợi nhuận bằng đô, nếu khớp trọn."""
        return self.netEdge * self.soCo

    @property
    def dang_lam(self) -> bool:
        """Có vượt mọi ngưỡng tối thiểu không.

        Đây chỉ là cửa SÀNG, không phải cửa duyệt. Cửa duyệt ở `rui_ro.py`.
        """
        return (
            self.netEdge >= float(_CL["netEdgeToiThieu"])
            and self.sucChua >= float(_CL["sucChuaToiThieu"])
            and self.xacSuatKhop >= float(_CL["xacSuatKhopToiThieu"])
            and self.nuaDoiMs >= float(_CL["nuaDoiToiThieuMs"])
        )


def can(
    ma: str,
    ben: str,
    chienThuat: str,
    fairValue: float,
    batDinh: float,
    so: SoLenh,
    soCo: float,
    laMaker: bool = False,
    nuaDoiMs: float | None = None,
) -> CoHoi | None:
    """Cân một cơ hội mua `soCo` cổ ở `ben`. None nếu sổ không có gì để ăn."""
    if soCo <= 0 or so is None:
        return None

    r = so.vwap_mua(soCo)
    if r.khop <= 0:
        return None

    ghi: list[str] = []
    if not r.dayDu:
        ghi.append(f"sổ chỉ đủ {r.khop:.0f}/{soCo:.0f} cổ")

    # Cân trên phần THỰC SỰ khớp được, không phải phần mong muốn. Cân trên
    # `soCo` khi sổ chỉ có `r.khop` là tự cho mình một lợi thế không tồn tại.
    thuc = r.khop
    vwap = r.vwap

    gross = fairValue - vwap

    phi_do = phi_maker(vwap, thuc) if laMaker else phi_taker(vwap, thuc)
    phi_moi_co = phi_do / thuc if thuc > 0 else 0.0

    # Maker không trả trượt giá vì nó không vượt spread — nó ĐỢI. Đổi lại
    # xác suất khớp thấp hơn, và điều đó tính riêng ở `_xac_suat_khop`.
    truot = 0.0 if laMaker else float(_PHI["truotGiaBps"]) / 10_000.0

    an_toan = float(_CL["bienAnToan"])
    net = gross - phi_moi_co - truot - batDinh - an_toan

    # Sức chứa: gom được nhiều nhất bao nhiêu cổ mà net edge vẫn dương.
    # Trần giá = fair trừ hết các khoản trừ; vượt trần là hết lợi thế.
    #
    # ⚠ Trần này là XẤP XỈ, và đây là chỗ khai ra sai số của nó. `phi_moi_co`
    # được tính ở `vwap` của lô hiện tại, nhưng phí mỗi cổ phụ thuộc GIÁ:
    # `heSo * min(p, 1-p)`. Đi sâu vào sổ thì p đổi, nên phí mỗi cổ ở mép
    # trần không đúng bằng phí ở vwap đang cầm.
    #
    # Giải chính xác được, và có dạng đóng:
    #
    #     p < 0,5 :  p* = (fair - c) / (1 + heSo)
    #     p ≥ 0,5 :  p* = (fair - heSo - c) / (1 - heSo)
    #     với c = trượt giá + bất định + biên an toàn
    #
    # Đã đo chênh giữa hai cách, với heSo 0,02 và c ≈ 0,0188:
    #
    #     fair 0,35 → trần cao hơn thật 0,049 cent   (RỘNG RÃI)
    #     fair 0,45 → cao hơn 0,045 cent             (RỘNG RÃI)
    #     fair 0,60 → thấp hơn thật 0,045 cent       (chặt hơn cần)
    #     fair 0,90 → thấp hơn 0,058 cent            (chặt hơn cần)
    #
    # Dưới 50c thì xấp xỉ này NỚI TAY — chiều nguy hiểm. Nhưng 0,05 cent
    # nằm gọn trong biên an toàn 0,8 cent vốn dựng ra đúng cho loại sai số
    # này, tức nhỏ hơn nó mười sáu lần. Nên giữ dạng xấp xỉ cho dễ đọc, và
    # ghi con số ra đây để người sau khỏi phải đo lại — và cũng để biết
    # rằng nếu `bienAnToan` có ngày bị vặn xuống dưới ~0,1 cent thì chỗ
    # này phải đổi sang dạng đóng ở trên.
    tran = fairValue - phi_moi_co - truot - batDinh - an_toan
    suc_chua = so.suc_chua(tran, mua=True)

    if nuaDoiMs is None:
        nua_doi = _nua_doi(so, gross)
    else:
        nua_doi = nuaDoiMs

    return CoHoi(
        ma=ma, ben=ben, chienThuat=chienThuat,
        fairValue=fairValue, giaCho=so.best_ask or vwap, vwap=vwap, soCo=thuc,
        grossEdge=gross, phi=phi_moi_co, truotGia=truot,
        batDinhMoHinh=batDinh, bienAnToan=an_toan, netEdge=net,
        sucChua=suc_chua,
        xacSuatKhop=_xac_suat_khop(so, laMaker, thuc),
        nuaDoiMs=nua_doi, laMaker=laMaker, dayDu=r.dayDu, ghiChu=ghi,
    )


def _xac_suat_khop(so: SoLenh, laMaker: bool, soCo: float) -> float:
    """Ước lượng thô khả năng khớp được.

    Taker gần như chắc khớp — nó vượt spread và ăn hàng đang nằm sẵn; chỉ trừ
    hao cho việc hàng biến mất giữa lúc quyết định và lúc lệnh tới sàn.

    Maker thì phải ĐỢI người khác tới ăn, nên xác suất phụ thuộc spread rộng
    hay hẹp (spread rộng thì lệnh mình nằm sâu, lâu tới lượt) và lô mình đặt
    to hay nhỏ so với độ sâu sẵn có.
    """
    if not laMaker:
        return 0.94

    sp = so.spread
    if sp is None or sp <= 0:
        return 0.5
    # spread càng hẹp, lệnh maker càng gần chỗ giao dịch thật sự xảy ra
    diem_spread = max(0.0, min(1.0, 1.0 - sp / 0.05))
    b, a = so.do_sau()
    day = b + a
    diem_lo = 1.0 if day <= 0 else max(0.0, min(1.0, 1.0 - soCo / max(1.0, day)))
    return max(0.05, min(0.92, 0.35 + 0.4 * diem_spread + 0.25 * diem_lo))


def _nua_doi(so: SoLenh, gross: float) -> float:
    """Cơ hội này sống được bao lâu, tính bằng mili-giây.

    Không đo được trực tiếp nếu chưa có băng ghi, nên đây là ước lượng theo
    hình dạng sổ: lệch giá lớn mà sổ mỏng thì biến rất nhanh (người khác cũng
    thấy, và ăn trước). Lệch nhỏ trong sổ dày thì sống lâu hơn.

    Khi `bang.py` đã ghi đủ, `chay_lai.py` đo được con số THẬT và chỗ này nên
    được thay bằng số đo. Ước lượng là để có cái dùng ngay, không phải để
    dùng mãi — nên nó nằm riêng một hàm chứ không rải vào giữa `can()`.
    """
    b, a = so.do_sau()
    day = b + a
    if day <= 0:
        return 0.0
    # gross lớn thì áp lực cạnh tranh lớn -> tan nhanh
    ap_luc = max(0.05, min(4.0, abs(gross) / 0.02))
    return max(50.0, min(5000.0, 1200.0 * math.sqrt(day / 500.0) / ap_luc))


# ══════════════════════════════════════════════════════════════════════════
#  GIÁ CẶP — nền của mọi chiến thuật arbitrage
# ══════════════════════════════════════════════════════════════════════════

@dataclass
class GiaCap:
    """Chi phí gom một CẶP đủ UP+DOWN, và lợi thế còn lại sau phí."""
    ma: str
    soCap: float
    vwapUp: float
    vwapDown: float
    giaCap: float           # vwapUp + vwapDown
    phiCap: float
    grossCap: float         # 1.0 - giaCap
    netCap: float           # grossCap - phiCap
    dayDu: bool

    @property
    def khoa_lo(self) -> bool:
        """Cặp này đang KHOÁ MỘT KHOẢN LỖ chứ không phải bảo vệ gì.

        Đây là chỗ tài liệu nói rất đúng và rất dễ bỏ qua: giữ cả hai chiều
        không tự động nghĩa là an toàn. UP trung bình 55c + DOWN trung bình
        49c = 1,04 đô cho một cặp chỉ trả về đúng 1 đô. Phần "đã phòng hộ" ấy
        đang lỗ sẵn 4c, và phần định hướng còn lại phải gỡ đủ 4c đó trước khi
        cả vị thế mới hoà.

        Nên bảng điều khiển không được khoe "đã phòng hộ 91%" — nó phải khoe
        `giaCap`. Một con số nói mình an toàn trong khi đang lỗ là con số tệ
        hơn không có.
        """
        return self.giaCap > 1.0


def gia_cap(ma: str, soUp: SoLenh, soDown: SoLenh, soCap: float) -> GiaCap | None:
    """Chi phí thật để gom `soCap` cặp, đi qua cả hai sổ."""
    if soCap <= 0 or soUp is None or soDown is None:
        return None
    ru = soUp.vwap_mua(soCap)
    rd = soDown.vwap_mua(soCap)
    if ru.khop <= 0 or rd.khop <= 0:
        return None

    # Số cặp thật = phần nhỏ hơn. Lấy trung bình hai chân là bịa ra những cặp
    # không tồn tại — một chân dư thì đó là vị thế định hướng, không phải cặp.
    that = min(ru.khop, rd.khop)
    gia = ru.vwap + rd.vwap
    phi = (phi_taker(ru.vwap, that) + phi_taker(rd.vwap, that)) / max(1e-9, that)
    gross = 1.0 - gia
    return GiaCap(
        ma=ma, soCap=that, vwapUp=ru.vwap, vwapDown=rd.vwap, giaCap=gia,
        phiCap=phi, grossCap=gross, netCap=gross - phi,
        dayDu=ru.dayDu and rd.dayDu,
    )
