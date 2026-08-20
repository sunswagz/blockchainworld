"""Sáu ngón nghề — sáu chiến thuật cắm vào MỘT nền máy.

Điểm quan trọng của kiến trúc này: không xây sáu con bot. Xây một nền máy
(fair value, sổ lệnh, cân lợi, tồn kho, rủi ro, đặt lệnh) rồi cắm sáu chiến
thuật vào. Chúng dùng chung mọi phép đo, nên so sánh được với nhau, và thêm
cái thứ bảy không phải dựng lại gì.

Mỗi chiến thuật chỉ làm đúng một việc: nhìn trạng thái, ĐỀ XUẤT cơ hội. Không
chiến thuật nào được tự đặt lệnh, tự nới trần, hay tự quyết kích thước — đó
là việc của `rui_ro.py`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .can_loi import CoHoi, can, gia_cap
from .config import CONFIG
from .dinh_gia import GiaChuan
from .dongho import CAN_KET_QUA, CUOI_KHUNG, GIUA_KHUNG, GOM_THANH_KHOAN, LatCat
from .kho_doi import ViThe
from .so_lenh import SoLenh

_KD = CONFIG["khoDoi"]
_CL = CONFIG["canLoi"]


@dataclass
class BoiCanh:
    """Mọi thứ một chiến thuật được nhìn. Chỉ đọc."""
    ma: str
    gia: GiaChuan
    soUp: SoLenh
    soDown: SoLenh
    dongHo: LatCat
    viThe: ViThe
    loMacDinh: float = 100.0


# ══════════════════════════════════════════════════════════════════════════
#  1. LỆCH GIÁ ĐỊNH HƯỚNG — ngón cơ bản nhất
# ══════════════════════════════════════════════════════════════════════════

def lech_gia_dinh_huong(bc: BoiCanh) -> list[CoHoi]:
    """Mô hình nói một bên đáng giá hơn chợ đang bán. Mua bên đó.

    Không hỏi "BTC sắp tăng không". Hỏi: "tôi có mua được thứ đáng 54c với
    giá thấp hơn 54c đủ nhiều để sống sót sau phí không".
    """
    if not bc.gia.ro_rang:
        return []
    ra = []
    for ben, p, so in (("UP", bc.gia.pUp, bc.soUp), ("DOWN", bc.gia.pDown, bc.soDown)):
        c = can(bc.ma, ben, "lech-gia", p, bc.gia.batDinh, so, bc.loMacDinh)
        if c:
            ra.append(c)
    return ra


# ══════════════════════════════════════════════════════════════════════════
#  2. CẶP THEO THỜI — arbitrage dựng từ HAI trạng thái chợ khác nhau
# ══════════════════════════════════════════════════════════════════════════

def cap_theo_thoi(bc: BoiCanh) -> list[CoHoi]:
    """Gom DOWN lúc rẻ, đợi chợ đảo rồi gom UP lúc rẻ. Cặp chưa từng tồn tại
    cùng lúc trong sổ, nhưng bot dựng được nó từ hai thời điểm.

    CÁI BẪY, và nó là cái bẫy lớn nhất của cả chiến thuật này: mua DOWN ở 27c
    CHƯA phải arbitrage. Nó là một vị thế DOWN trần trụi cho tới khi UP được
    mua. Nếu BTC cứ đi lên tới hết giờ thì UP rẻ không bao giờ xuất hiện, và
    thứ còn lại trong tay là đúng cái vị thế định hướng mà không ai định mở.

    Nên chiến thuật này chỉ được đề xuất khi:
      · còn đủ thời gian để chân hai kịp khớp
      · số tiền sẽ nằm trần chưa chạm trần `capChuaKhopToiDaUsd`
      · và nó gom TỪNG MẢNG NHỎ chứ không một phát ăn cả lô
    """
    if bc.dongHo.conLaiGiay < float(_KD["giayChoChanHai"]) * 2:
        return []

    v = bc.viThe
    ra: list[CoHoi] = []

    # Đang thiếu chân nào thì ưu tiên bù chân đó — giảm phơi nhiễm là việc
    # đáng giá hơn mở thêm phơi nhiễm mới.
    thieu = None
    if v.dinhHuong > 0:
        thieu = ("DOWN", bc.soDown, bc.gia.pDown)
    elif v.dinhHuong < 0:
        thieu = ("UP", bc.soUp, bc.gia.pUp)

    if thieu:
        ben, so, p = thieu
        can_them = abs(v.dinhHuong)
        gia_von_kia = v.giaVonUp if ben == "DOWN" else v.giaVonDown
        # Chỉ bù nếu giá cặp SAU KHI bù vẫn dưới trần — bù bằng mọi giá là
        # tự tay khoá một khoản lỗ để đổi lấy cảm giác đã phòng hộ.
        tran = float(_KD["giaCapToiDa"]) - gia_von_kia
        if tran > 0:
            suc = so.suc_chua(tran, mua=True)
            lo = min(can_them, suc, bc.loMacDinh)
            if lo >= 1:
                c = can(bc.ma, ben, "cap-theo-thoi/bù", p, bc.gia.batDinh, so, lo)
                if c and c.vwap + gia_von_kia < float(_KD["giaCapToiDa"]):
                    ra.append(c)
        return ra

    # Chưa có chân nào: mở chân đầu, nhưng chỉ khi giá đủ rẻ để chân kia còn
    # chỗ thở. Rẻ ở đây nghĩa là dưới `giaCapToiDa` trừ đi giá bên kia.
    for ben, p, so, so_kia in (("UP", bc.gia.pUp, bc.soUp, bc.soDown),
                               ("DOWN", bc.gia.pDown, bc.soDown, bc.soUp)):
        kia = so_kia.best_ask
        if kia is None:
            continue
        tran = float(_KD["giaCapToiDa"]) - kia
        if tran <= 0:
            continue
        lo = min(bc.loMacDinh, so.suc_chua(tran, mua=True))
        if lo < 1:
            continue
        c = can(bc.ma, ben, "cap-theo-thoi/mở", p, bc.gia.batDinh, so, lo)
        if c:
            ra.append(c)
    return ra


# ══════════════════════════════════════════════════════════════════════════
#  3. CẶP TỨC THÌ — cả hai chân cùng lúc, khi tổng đã dưới 1 đô
# ══════════════════════════════════════════════════════════════════════════

def cap_tuc_thi(bc: BoiCanh) -> list[CoHoi]:
    """UP + DOWN đang cùng lúc dưới 1 đô ngay trong sổ.

    Hiếm, và hiếm là đúng — nếu nó dễ thì đã không còn. Nhưng khi có thì đây
    là ngón ít rủi ro nhất vì payoff cố định ngay khi hai chân khớp.

    Vẫn phải trừ phí: cặp 99,1c cho gross 0,9c, mà phí taker hai chân ở quanh
    giữa bảng giá đã ăn hơn ngần ấy. Cặp 99,1c bằng lệnh thị trường là một
    giao dịch LỖ, và nó lỗ trong khi bảng điều khiển khoe "+0,9c arbitrage".
    """
    lo = bc.loMacDinh
    gc = gia_cap(bc.ma, bc.soUp, bc.soDown, lo)
    if gc is None or gc.netCap <= float(_CL["netEdgeToiThieu"]):
        return []

    # Đề xuất hai chân như hai cơ hội riêng, cùng nhãn — `dat_lenh.py` biết
    # chúng phải đi cùng nhau nhờ nhãn, và `kho_doi.py` đếm đúng cặp.
    ra = []
    for ben, p, so in (("UP", bc.gia.pUp, bc.soUp), ("DOWN", bc.gia.pDown, bc.soDown)):
        c = can(bc.ma, ben, "cap-tuc-thi", p, bc.gia.batDinh, so, gc.soCap)
        if c:
            ra.append(c)
    return ra


# ══════════════════════════════════════════════════════════════════════════
#  4. ĐỊNH HƯỚNG CÓ PHÒNG HỘ
# ══════════════════════════════════════════════════════════════════════════

def dinh_huong_phong_ho(bc: BoiCanh) -> list[CoHoi]:
    """Giữ phần lớn là cặp, chừa một phần nhỏ thiên về bên mô hình thích.

    260 UP + 235 DOWN nghĩa là 235 cặp cộng 25 UP định hướng. Phần cặp đã cố
    định payoff, phần 25 kia là chỗ mô hình được nói.

    Nhưng phần cặp KHÔNG miễn phí: nếu giá cặp là 1,04 đô thì nó đang khoá
    sẵn 4c lỗ, và 25 cổ định hướng phải gỡ đủ chừng ấy trước khi cả vị thế
    mới hoà. Nên chiến thuật này chỉ mở khi giá cặp hiện tại còn dưới trần.
    """
    if not bc.gia.ro_rang:
        return []
    v = bc.viThe
    gc = v.giaCap
    if gc is not None and gc >= float(_KD["giaCapToiDa"]):
        return []       # cặp đang khoá lỗ, đừng đắp thêm

    ben = "UP" if bc.gia.pUp > bc.gia.pDown else "DOWN"
    p = max(bc.gia.pUp, bc.gia.pDown)
    so = bc.soUp if ben == "UP" else bc.soDown

    # Phần thiên lệch tỉ lệ với việc mô hình rõ tới đâu, và có trần cứng.
    do_tin = min(1.0, max(0.0, (abs(p - 0.5) - bc.gia.batDinh) / 0.25))
    lech_cho = min(float(_KD["lechHuongToiDaUsd"]), bc.loMacDinh * do_tin)
    if lech_cho < 1:
        return []
    c = can(bc.ma, ben, "phong-ho", p, bc.gia.batDinh, so, lech_cho)
    return [c] if c else []


# ══════════════════════════════════════════════════════════════════════════
#  5. TẠO LẬP — kiếm spread và maker rebate, không đoán hướng
# ══════════════════════════════════════════════════════════════════════════

def tao_lap(bc: BoiCanh) -> list[CoHoi]:
    """Đặt limit hai bên quanh fair value, ăn spread, điều khiển tồn kho.

    Đây KHÔNG phải dự đoán. Maker không trả phí giao dịch và còn có thể nhận
    rebate, nên cùng một "edge 3c", việc mình là maker hay taker đủ để lật
    chiến lược từ lãi thành lỗ.

    Giá yết phải LỆCH theo tồn kho, không phải đối xứng quanh fair value:

        giá yết = fair value - phạt tồn kho
        phạt    = q x lambda x sigma^2 x tau

    Đang thừa UP thì UP kém hấp dẫn đi (yết mua thấp xuống), còn DOWN có giá
    trị hơn vì nó kéo tồn kho về cân. Đây là khác biệt lớn giữa một hệ thống
    thi hành thật và một con bot cứ thấy tín hiệu dương là mua thêm.
    """
    if bc.dongHo.giaiDoan not in (GOM_THANH_KHOAN, GIUA_KHUNG):
        return []       # sổ quá mỏng lúc mở màn, quá loạn lúc cuối khung

    v = bc.viThe
    sp_up = bc.soUp.spread
    if sp_up is None or sp_up < 0.005:
        return []       # spread hẹp quá thì không còn gì để ăn

    # phạt tồn kho — dấu quan trọng hơn độ lớn
    q = v.dinhHuong
    lam = 0.0015
    phat = q * lam * (bc.gia.sigmaGiay ** 2) * bc.dongHo.conLaiGiay
    phat = max(-0.05, min(0.05, phat))

    ra = []
    for ben, p, so in (("UP", bc.gia.pUp, bc.soUp), ("DOWN", bc.gia.pDown, bc.soDown)):
        dau = -1.0 if ben == "UP" else 1.0
        p_yet = min(0.99, max(0.01, p + dau * phat))
        c = can(bc.ma, ben, "tao-lap", p_yet, bc.gia.batDinh, so,
                bc.loMacDinh * 0.5, laMaker=True)
        if c:
            ra.append(c)
    return ra


# ══════════════════════════════════════════════════════════════════════════
#  6. CẬN KẾT QUẢ — ngón dễ nhìn nhất và nguy hiểm nhất
# ══════════════════════════════════════════════════════════════════════════

def can_ket_qua(bc: BoiCanh) -> list[CoHoi]:
    """Mua bên gần như chắc thắng ở 98,7c, đợi về 1 đô. Lãi 1,3c mỗi lượt.

    ĐÂY LÀ NGÓN PHẢI ĐỌC KỸ NHẤT.

    Phân bố rủi ro lệch khủng khiếp: ăn 1,3c hàng trăm lần, rồi MỘT lần sai
    mất gần trọn 98,7c — tức là xoá sạch khoảng 76 lần thắng. Một tỉ lệ thắng
    99,7% trên bảng điều khiển hoàn toàn không nói lên rằng chiến lược an
    toàn; thứ quyết định là ĐỘ LỚN của những lần thua hiếm hoi đó.

    Và những lần sai không hiếm như người ta tưởng, vì chúng đến từ:
      · một cú BTC ở giây chót
      · sai nguồn giá resolution
      · sai giá mở
      · hiểu sai luật kết toán
      · không kịp huỷ một lệnh limit

    Bốn nguyên nhân cuối KHÔNG PHẢI rủi ro thị trường — chúng là rủi ro vận
    hành, và không mô hình xác suất nào bắt được chúng.

    Nên ở đây: chỉ đề xuất khi mô hình VÀ chợ cùng đồng ý, chỉ với lô nhỏ, và
    `rui_ro.py` vẫn siết thêm lần nữa. Bất định nhảy giá trong `dinh_gia.py`
    đã tự lo phần "giá đang nằm ngay lằn ranh".
    """
    if bc.dongHo.giaiDoan not in (CUOI_KHUNG, CAN_KET_QUA):
        return []
    if not bc.gia.ro_rang:
        return []

    ra = []
    for ben, p, so in (("UP", bc.gia.pUp, bc.soUp), ("DOWN", bc.gia.pDown, bc.soDown)):
        if p < 0.90:
            continue
        ask = so.best_ask
        if ask is None or ask >= 0.995:
            continue     # không còn gì để ăn
        # Chợ cũng phải đồng ý. Mô hình nói 97% mà chợ bán ở 60c thì chênh
        # lệch đó quá lớn để là một sai giá — nhiều khả năng mô hình đang
        # thiếu một thông tin mà chợ đã có.
        if ask < 0.80:
            continue
        c = can(bc.ma, ben, "can-ket-qua", p, bc.gia.batDinh, so,
                min(bc.loMacDinh, float(_CL["sucChuaToiThieu"]) * 2))
        if c:
            c.ghiChu.append("đuôi lệch: một lần sai xoá ~%.0f lần thắng"
                            % (c.vwap / max(1e-9, 1.0 - c.vwap)))
            ra.append(c)
    return ra


# ══════════════════════════════════════════════════════════════════════════
#  SỔ ĐĂNG KÝ
# ══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChienThuat:
    ma: str
    ten: str
    ham: Callable[[BoiCanh], list[CoHoi]]
    mota: str


SO_DANG_KY: list[ChienThuat] = [
    ChienThuat("lech-gia", "Lệch giá định hướng", lech_gia_dinh_huong,
               "Mô hình định giá cao hơn chợ đang bán."),
    ChienThuat("cap-theo-thoi", "Cặp theo thời", cap_theo_thoi,
               "Gom hai chân ở hai thời điểm khác nhau."),
    ChienThuat("cap-tuc-thi", "Cặp tức thì", cap_tuc_thi,
               "UP + DOWN cùng lúc dưới 1 đô ngay trong sổ."),
    ChienThuat("phong-ho", "Định hướng có phòng hộ", dinh_huong_phong_ho,
               "Lõi là cặp, chừa một phần thiên lệch."),
    ChienThuat("tao-lap", "Tạo lập", tao_lap,
               "Yết hai bên, ăn spread, lệch giá theo tồn kho."),
    ChienThuat("can-ket-qua", "Cận kết quả", can_ket_qua,
               "Mua bên gần chắc thắng. Đuôi lệch — đọc kỹ."),
]


def chay_tat_ca(bc: BoiCanh, batTat: dict[str, bool] | None = None) -> list[CoHoi]:
    """Chạy mọi chiến thuật đang bật, gom mọi đề xuất.

    Một chiến thuật ném lỗi KHÔNG được làm chết cả vòng lặp — nó chỉ mất
    lượt đó. Bot không được sập vì một ngón nghề mới thêm vào có bug.
    """
    from .bus import bus
    ra: list[CoHoi] = []
    for ct in SO_DANG_KY:
        if batTat is not None and not batTat.get(ct.ma, True):
            continue
        try:
            ra.extend(ct.ham(bc) or [])
        except Exception as e:                      # noqa: BLE001
            bus.ghi(f"chiến thuật {ct.ma} lỗi: {type(e).__name__}: {e}", loai="loi")
    return ra
