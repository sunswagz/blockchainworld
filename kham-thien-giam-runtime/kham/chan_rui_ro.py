"""Chân Rủi Ro — quyết định phải làm gì khi một chân đã khớp mà chân kia chưa.

Tài liệu nói thẳng: **vấn đề lớn nhất bắt đầu SAU cú khớp đầu tiên**. Bản
trước của runtime chỉ PHÁT HIỆN trạng thái chưa phòng hộ (`ChanCho` có đồng
hồ riêng) nhưng không có ai QUYẾT phải làm gì với nó. Phát hiện mà không
quyết thì cái đồng hồ chỉ để nhìn.

    đặt UP 45c + DOWN 49c  ->  cặp 94c, nhìn như arbitrage
    UP   khớp 100%
    DOWN khớp  18%
    chợ dịch, DOWN thành 56c

Bây giờ không có arbitrage nào. Có 82% một vị thế ĐỊNH HƯỚNG trần trụi mà
không ai định mở. Mô hình định giá không sai; hỏng ở khâu thi hành.

## Sáu lối ra, và chọn lối nào là cả vấn đề

    CHO        chân kia còn rẻ, cửa còn dài  -> đợi thêm
    NANG_GIA   nhích giá yết lên một nấc     -> tăng xác suất khớp
    VUOT_SPREAD ăn thẳng vào ask             -> chắc khớp, đắt hơn
    HUY        rút lệnh chờ, giữ nguyên chân đã có
    DONG_CHAN  bán lại chân đã khớp, chịu lỗ nhỏ, thoát hẳn
    CHIU       chấp nhận thành vị thế định hướng có chủ ý

## Nguyên tắc quyết

Ba thứ vào: **còn bao lâu**, **giá cặp nếu bù bây giờ**, **bao nhiêu tiền
đang trần**. Và một luật cứng: khi cửa đặt cược sắp đóng, KHÔNG bao giờ
chọn `CHO` — chân trần lúc chuông reo là rủi ro không gỡ được nữa.

Chỗ dễ sai nhất, và đã suýt viết sai: **bù chân bằng mọi giá là tự tay khoá
lỗ**. Nếu giá cặp sau khi bù vượt 1,00 thì việc "phòng hộ" ấy chốt sẵn một
khoản lỗ, và nó chỉ đổi một rủi ro mở lấy một khoản lỗ chắc chắn. Có lúc
điều đó đúng (khi rủi ro mở quá lớn), nhưng phải là một quyết định CÓ TÊN,
không phải hệ quả phụ của việc "cứ phòng hộ cho an toàn".
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .cap_token import CapSo
from .config import CONFIG
from .kho_doi import ViThe

_KD = CONFIG["khoDoi"]

CHO = "cho"
NANG_GIA = "nang-gia"
VUOT_SPREAD = "vuot-spread"
HUY = "huy"
DONG_CHAN = "dong-chan"
CHIU = "chiu"

NHAN = {
    CHO: "chờ thêm",
    NANG_GIA: "nhích giá yết",
    VUOT_SPREAD: "vượt spread",
    HUY: "huỷ lệnh chờ",
    DONG_CHAN: "đóng chân đã khớp",
    CHIU: "chịu, thành định hướng",
}


@dataclass
class QuyetChan:
    loi: str
    ben: str | None                 # bên cần hành động
    soCo: float
    giaToiDa: float | None          # trần giá được phép trả để bù
    lyDo: list[str] = field(default_factory=list)
    khoaLoUsd: float = 0.0          # bù bây giờ thì khoá sẵn bao nhiêu lỗ

    @property
    def nhan(self) -> str:
        return NHAN.get(self.loi, self.loi)


def quyet(v: ViThe, cap: CapSo, conLaiGiay: float,
          bayGioMs: float | None = None) -> QuyetChan | None:
    """Nhìn một vị thế lệch chân, khuyên nên làm gì. None nếu đã cân bằng.

    ⚠ **LỜI KHUYÊN, KHÔNG PHẢI HÀNH ĐỘNG.** `vong._mot_thi_truong` gọi hàm
    này rồi cất kết quả vào `self.quyetChan[ma]` cho buồng lái đọc — và
    dừng ở đó. Không chỗ nào huỷ lệnh, nâng giá, vượt spread hay đóng
    chân theo nó. Ai đọc tên `quyet` mà tưởng bot tự làm là hiểu sai, nên
    câu này phải nằm ngay đây chứ không nằm trong đầu ai.

    Vì sao vẫn chấp nhận được — ba lớp đã che phần nguy hiểm:

    · `capChuaKhopToiDaUsd` ở RiskEngine chặn MỞ THÊM khi phần trần đã
      quá hạn mức, nên phơi nhiễm một chân bị chặn KÍCH THƯỚC.
    · `cap_theo_thoi` ưu tiên bù chân thiếu ở những ca bù được — tức là
      những ca dễ, khi giá cặp sau khi bù vẫn dưới trần.
    · khung 5 phút tự tất toán, nên một chân trần sống nhiều nhất vài
      phút rồi ngã ngũ.

    Cái KHÔNG có: lối thoát cho ca khó — không ai bán bên thiếu, hoặc đã
    chờ quá lâu. Ở đó `DONG_CHAN` / `CHIU` / `VUOT_SPREAD` / `HUY` là
    những nước đi đúng mà bot không đi. Nối chúng vào là đổi hành vi giao
    dịch thật, nên phải là một quyết định có chủ ý, đo được, chứ không
    phải một lần "sửa cho gọn".
    """
    du = v.dinhHuong
    if abs(du) < 1e-9:
        return None

    ben_thieu = "DOWN" if du > 0 else "UP"
    can = abs(du)
    gia_von_da_co = v.giaVonUp if du > 0 else v.giaVonDown
    gia_bu = cap.gia_mua(ben_thieu)
    tran_cap = float(_KD["giaCapToiDa"])
    tran_tran_usd = float(_KD["capChuaKhopToiDaUsd"])
    han_cho_giay = float(_KD["giayChoChanHai"])

    tran_usd = v.chuaPhongHoUsd
    cho_lau = v.cho_lau_nhat_ms(bayGioMs) / 1000.0
    ly: list[str] = [
        f"lệch {du:+.0f} cổ, ${tran_usd:.2f} đang trần",
        f"đã chờ {cho_lau:.0f}s",
    ]

    # ── không mua được thì chỉ còn hai lối ────────────────────────────────
    if gia_bu is None:
        ly.append(f"không có bên bán {ben_thieu}")
        if conLaiGiay <= han_cho_giay:
            return QuyetChan(DONG_CHAN, "UP" if du > 0 else "DOWN", can, None,
                             ly + ["cửa sắp đóng, không bù được thì thoát"])
        return QuyetChan(CHO, ben_thieu, can, None, ly)

    gia_cap_neu_bu = gia_von_da_co + gia_bu
    khoa_lo = max(0.0, (gia_cap_neu_bu - 1.0)) * can
    ly.append(f"bù ở {gia_bu:.3f} → giá cặp {gia_cap_neu_bu:.4f}")

    # ── cửa sắp đóng: KHÔNG được chờ nữa ─────────────────────────────────
    if conLaiGiay <= han_cho_giay:
        if gia_cap_neu_bu < 1.0:
            return QuyetChan(VUOT_SPREAD, ben_thieu, can, gia_bu,
                             ly + ["cửa sắp đóng, bù vẫn có lãi → ăn thẳng"],
                             khoaLoUsd=0.0)
        # Bù bây giờ là khoá lỗ. So khoản lỗ chắc chắn đó với rủi ro mở.
        rui_ro_mo = can * max(gia_von_da_co, 1.0 - gia_von_da_co)
        if khoa_lo < rui_ro_mo * 0.35:
            return QuyetChan(VUOT_SPREAD, ben_thieu, can, gia_bu,
                             ly + [f"khoá lỗ ${khoa_lo:.2f} nhỏ hơn nhiều so với "
                                   f"rủi ro mở ${rui_ro_mo:.2f} → chốt cho xong"],
                             khoaLoUsd=khoa_lo)
        return QuyetChan(CHIU, None, can, None,
                         ly + [f"bù bây giờ khoá lỗ ${khoa_lo:.2f}, đắt hơn việc "
                               f"chịu định hướng — chịu, có chủ ý"],
                         khoaLoUsd=khoa_lo)

    # ── quá hạn chờ: phải dứt điểm ───────────────────────────────────────
    if cho_lau > han_cho_giay:
        if gia_cap_neu_bu < tran_cap:
            return QuyetChan(VUOT_SPREAD, ben_thieu, can, gia_bu,
                             ly + ["quá hạn chờ, giá còn trong trần → ăn thẳng"],
                             khoaLoUsd=khoa_lo)
        return QuyetChan(NANG_GIA, ben_thieu, can, tran_cap - gia_von_da_co,
                         ly + [f"quá hạn chờ nhưng giá vượt trần cặp {tran_cap} "
                               f"→ nhích yết, đừng đuổi"],
                         khoaLoUsd=khoa_lo)

    # ── tiền trần quá nhiều: siết ngay dù chưa hết giờ ────────────────────
    if tran_usd > tran_tran_usd:
        return QuyetChan(VUOT_SPREAD, ben_thieu, can, gia_bu,
                         ly + [f"${tran_usd:.2f} trần vượt trần ${tran_tran_usd} "
                               f"→ đóng phơi nhiễm trước đã"],
                         khoaLoUsd=khoa_lo)

    # ── bình thường: còn giờ, còn chỗ, giá còn tốt thì đợi ───────────────
    if gia_cap_neu_bu < tran_cap:
        return QuyetChan(CHO, ben_thieu, can, tran_cap - gia_von_da_co,
                         ly + ["còn giờ và giá còn trong trần → đợi khớp thụ động"])

    return QuyetChan(NANG_GIA, ben_thieu, can, tran_cap - gia_von_da_co,
                     ly + [f"giá bù đang vượt trần cặp → chỉ nhích yết tới "
                           f"{tran_cap - gia_von_da_co:.3f}"],
                     khoaLoUsd=khoa_lo)
