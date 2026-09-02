"""Động cơ NHIỆT ĐỘ — họ market đầu tiên ngoài crypto.

    P(TMAX > K) = Φ( (duBao − thienLech − K) / sigma )

Cùng hình dạng với `dinh_gia.dinh_gia` của crypto — một dự báo, một
mốc, và một bất định đo được — nên toàn bộ máy phía sau (cân lợi, rủi
ro, tồn kho, kế toán, chạy lại, hiệu chỉnh) dùng lại nguyên vẹn. Đó là
điểm của `dong_co.py`: thêm một HỌ là thêm một plugin, không phải một
bot mới.

## Vì sao họ này qua được cửa, còn bầu cử thì không

Cửa vào của một họ không phải "AI có phán được không" mà là hai câu:

    giá trị đúng   có tính được không, từ nguồn lấy được?
    sự thật nền    có DÀY không, có hàng loạt không?

Nhiệt độ:  dự báo từ open-meteo/NWS · thực đo từ NOAA NCEI, từng ngày,
           hàng chục năm, miễn phí, không cần khoá.
Bầu cử:    không công thức, và ngã ngũ ĐÚNG MỘT LẦN.

Mọi kỷ luật của cung — Brier, điểm kỹ năng, đường nắn, bootstrap chia
khối — sống nhờ vế thứ hai.

## Con số đã đo (`scripts/do-nhiet-do.py`, 10 trạm, hai quãng 3 năm)

Gom theo |z| = |duBao − thienLech − K| / sigma, khối bootstrap là TUẦN:

    |z| 0 – 0,25    kỹ năng  +1,9% / +1,6%     ← chỗ chợ KHÔNG chắc
    |z| 0,5 – 1     kỹ năng +30,2% / +28,1%
    |z| 1,5 – 2,5   kỹ năng +84,3% / +83,9%    ← chỗ chợ yết 0,99

Hai quãng KHÔNG chồng lấn, trải sáu năm, trùng nhau dưới một điểm phần
trăm. Nhưng con số đáng đọc là ô ĐẦU: ở chỗ duy nhất có tiền, mô hình
chỉ hơn tỉ lệ nền **1,9%**.

## THIÊN LỆCH và SIGMA phải ước trên CỬA SỔ TRƯỢT

Đo được: ước một lần trên 60% dữ liệu cũ rồi dùng cho 40% mới thì ở ô
|z| < 0,25 kỹ năng ra **−10,2%** — TỆ HƠN tỉ lệ nền có ý nghĩa. Vì lệch
dự báo đổi theo MÙA, nên một hằng số học từ mùa khác là một phép chỉnh
sai. Cửa sổ trượt 45 ngày đưa nó về +1,9%.

Và thiên lệch khác nhau rất nhiều theo NƠI (Phoenix −2,12 °F, New York
−0,02 °F), nên một tham số toàn cục ở đây là sai.

## Về việc mượn `GiaChuan`

`GiaChuan` sinh ra cho crypto nên tên trường mang mùi crypto. Ánh xạ ở
đây, khai thẳng để không ai đọc nhầm:

    giaHienTai  ←  dự báo (°F)          giaMo    ←  ngưỡng K (°F)
    sigmaGiay   ←  sigma sai số (°F)    tauGiay  ←  số ngày tới hạn

Ba tên ấy NÓI SAI ĐƠN VỊ. Đổi tên trường thì phải sửa cả cung, nên thay
vì thế: `giaiTrinh` mang tên đúng (`duBaoF`, `nguongF`, `sigmaF`,
`thienLechF`, `ngayToiHan`), và mọi chỗ đọc số của họ này phải đọc từ
`giaiTrinh`, đừng đọc `sigmaGiay` rồi tưởng là mỗi giây.
"""
from __future__ import annotations

import math

from .dinh_gia import GiaChuan, o_hieu_chinh

#: Bất định tối thiểu. Cùng vai trò `dinhGia.batDinhToiThieu` của crypto:
#: một mô hình nói "chắc 100%" là mô hình chưa tính hết chuyện chưa biết.
BAT_DINH_TOI_THIEU = 0.015

#: Kẹp p khỏi 0/1. Sai số dự báo KHÔNG phải Gauss ở đuôi — một đợt gió
#: biển đổi chiều làm lệch 8 °F, và Φ nói chuyện ấy có xác suất 1e-9.
MAT_PHANG = 0.005


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def dinh_gia_nhiet_do(ma: str, duBao: float, nguong: float,
                      thienLech: float, sigmaF: float,
                      ngayToiHan: float = 0.0) -> GiaChuan | None:
    """P(nhiệt độ cao nhất VƯỢT `nguong`). None khi thiếu nguyên liệu.

    Trả None chứ không trả 0,5 — cùng lý do như bên crypto: 0,5 trông
    như một câu trả lời và sẽ lặng lẽ chảy vào phép tính edge, còn None
    thì buộc chỗ gọi phải xử lý.
    """
    if not all(isinstance(x, (int, float)) for x in
               (duBao, nguong, thienLech, sigmaF)):
        return None
    if not all(math.isfinite(float(x)) for x in
               (duBao, nguong, thienLech, sigmaF)):
        return None
    if sigmaF <= 0:
        return None

    tam = float(duBao) - float(thienLech)
    z = (tam - float(nguong)) / float(sigmaF)
    p = _phi(z)

    # ── bất định ──────────────────────────────────────────────────────
    #
    # Hai nguồn, cùng cách chia như crypto:
    #
    #  · THAM SỐ — sigma là một ƯỚC LƯỢNG trên cửa sổ trượt, nên nó có
    #    sai số riêng. Lệch sigma 15% thì p lệch bao nhiêu: đo bằng đạo
    #    hàm số, không đoán.
    #  · NHẢY — sai số dự báo có đuôi dày hơn Gauss (gió biển đổi
    #    chiều, giông). Phần này lớn nhất khi z gần 0, đúng chỗ một cú
    #    lệch nhỏ lật hẳn kết quả.
    b_tham = abs(_phi((tam - nguong) / (sigmaF * 1.15)) - p)
    b_nhay = 0.5 * math.exp(-0.5 * z * z) * 0.12
    batDinh = max(BAT_DINH_TOI_THIEU, b_tham + b_nhay)

    daPhang = False
    if p < MAT_PHANG:
        p, daPhang = MAT_PHANG, True
    elif p > 1.0 - MAT_PHANG:
        p, daPhang = 1.0 - MAT_PHANG, True

    return GiaChuan(
        ma=ma, pUp=p, pDown=1.0 - p,
        batDinh=batDinh, batDinhThamSo=b_tham, ruiRoNhay=b_nhay,
        z=z,
        # ⚠ ba trường dưới MANG TÊN CỦA CRYPTO và sai đơn vị ở họ này.
        # Tên đúng nằm trong `giaiTrinh`.
        sigmaGiay=float(sigmaF), tauGiay=float(ngayToiHan),
        tauDungSan=False, daMatPhang=daPhang,
        giaHienTai=float(duBao), giaMo=float(nguong),
        oHieuChinh=o_hieu_chinh(p),
        giaiTrinh={
            "hoMarket": "nhiet-do",
            "duBaoF": float(duBao),
            "nguongF": float(nguong),
            "thienLechF": float(thienLech),
            "sigmaF": float(sigmaF),
            "duBaoDaChinhF": tam,
            "ngayToiHan": float(ngayToiHan),
            "congThuc": "P = Phi((duBao - thienLech - K) / sigmaF)",
        })
