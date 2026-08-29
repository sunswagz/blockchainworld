"""CHỢ GIẢ ĐỊNH — dựng khung ăn thua từ Binance để chạy demo được ngay.

Đường tới Polymarket bị chặn ở tầng TLS từ máy này, nên không có sổ lệnh
thật để chạy. Nhưng gần như MỌI thứ khác đều thật và lấy được:

    giá nền, σ, strike, kết quả     Binance — thật 100%
    mô hình, nắn lại, chiến thuật   mã thật, không đổi một dòng
    cầu dao, Kelly, kho, kết toán   mã thật
    spread và độ sâu sổ lệnh        ĐO từ 127.816 lát sổ Polymarket đã ghi

Đúng MỘT thứ phải giả định: **mức giá chợ yết**. Và vì nó là giả định
nên nó được khai thành tham số, có tên, và mỗi tên trả lời một câu hỏi
khác nhau — chứ không nấp trong một hằng số nào đó.

## Ba cái chợ, ba câu hỏi

    cong-bang    chợ yết đúng 0,50 — một chợ không biết gì
    hoan-hao     chợ yết đúng giá trị đã nắn — chợ biết y hệt ta
    tho          chợ yết theo mô hình THÔ, ta dùng bản đã nắn

`cong-bang` là **cận trên**: thắng nó là điều kiện CẦN, không phải đủ.
Chợ thật đo được có kỹ năng +6,6% so với tỉ lệ nền, nên nó khó hơn hẳn
một đồng xu. Thua `cong-bang` thì khỏi bàn tiếp.

`hoan-hao` là **máy dò lỗi**: chợ biết đúng bằng ta thì lợi thế phải
bằng 0 và sau phí phải ÂM. Nếu phiên ấy có lãi thì có lỗi ở đâu đó —
nhìn trộm tương lai, kế toán sai, hoặc sổ giấy quá dễ dãi.

`tho` đo riêng **phép nắn đáng bao nhiêu tiền**, bằng cách cho chợ mắc
đúng cái lỗi mà bảng hiệu chỉnh vừa đo được ở mô hình thô. Đây là một
KỊCH BẢN, không phải một dự báo: chợ thật không mắc đúng lỗi của ta.

## Điều nó không thể thay thế

Không có tác động thị trường, không có trượt giá theo thời gian, không
có chọn lọc bất lợi, và mức giá là giả định. Đây là bàn thử, không phải
sàn.
"""
from __future__ import annotations

import math
import statistics

#: Spread và độ sâu ĐO ĐƯỢC trên 127.816 lát sổ Polymarket thật đã ghi:
#: spread trung vị 2,00¢ (thập phân vị 1,0–6,0¢); ba mức ask đầu cộng lại
#: trung vị 208 cổ (89–1.150). Không bịa, và cũng không lấy con số đẹp
#: nhất — lấy trung vị.
SPREAD = 0.02
SAU_MOI_MUC = 70.0
SO_MUC = 3
BUOC_GIA = 0.01

#: Lát cắt trong khung ăn thua, giây CÒN LẠI. Chỉ mốc rơi đúng ranh giới
#: phút — nến 1 phút không cho biết giá ở giữa phút, và làm tròn lên là
#: lấy giá của tương lai. Xem `scripts/hoc-tu-binance.py`.
LAT_CAT = (240.0, 180.0, 120.0, 60.0)

PHUT = 60_000.0


def _thang(giua: float, ben_up: bool) -> dict:
    """Một bên sổ quanh `giua`, có spread và ba mức sâu dần."""
    m = giua if ben_up else (1.0 - giua)
    m = max(0.02, min(0.98, m))
    bid0 = max(0.01, m - SPREAD / 2.0)
    ask0 = min(0.99, m + SPREAD / 2.0)
    return {
        "luc": 0,
        "bid": [{"gia": round(max(0.001, bid0 - i * BUOC_GIA), 4),
                 "luong": SAU_MOI_MUC} for i in range(SO_MUC)],
        "ask": [{"gia": round(min(0.999, ask0 + i * BUOC_GIA), 4),
                 "luong": SAU_MOI_MUC} for i in range(SO_MUC)],
    }


def sigma_tai(theoMoc: dict, T: int) -> float | None:
    """σ mỗi giây, ước từ 5 nến 1 phút TRƯỚC T — đúng thứ runtime có."""
    gs = [theoMoc.get(T - i * int(PHUT)) for i in range(6)]
    if any(g is None or g <= 0 for g in gs):
        return None
    gs = gs[::-1]
    r = [math.log(gs[i + 1] / gs[i]) for i in range(5)]
    sd = statistics.pstdev(r)
    return (sd / math.sqrt(60.0)) if sd > 0 else None


def dung_khung(theoMoc: dict, ma: str, kieuCho: str,
               pCho=None) -> list[dict]:
    """Sinh khung ăn thua từ nến Binance.

    `pCho(S, K, tau, sigma) -> float | None` là giá chợ cho bên UP. Chỉ
    dùng khi `kieuCho` không phải `cong-bang`. Trả None thì bỏ lát ấy.
    """
    ra: list[dict] = []
    tienTo = ma.split("_")[0].lower()
    for T in sorted(theoMoc):
        if T % 300_000:
            continue                    # chỉ khung THẬT, mốc 5 phút
        K = theoMoc.get(T)
        het = theoMoc.get(T + 5 * int(PHUT))
        if K is None or het is None or abs(het - K) < 1e-12:
            continue
        sig = sigma_tai(theoMoc, T)
        if sig is None:
            continue
        slug = f"{tienTo}-updown-5m-{T // 1000}"
        for tau in LAT_CAT:
            t = T + int((300.0 - tau) * 1000.0)
            S = theoMoc.get(t)
            if S is None or S <= 0:
                continue
            if kieuCho == "cong-bang":
                giua = 0.5
            else:
                giua = pCho(float(S), float(K), tau, sig) if pCho else None
                if giua is None:
                    continue
            ra.append({
                "luc": float(t),
                "thiTruong": [{
                    "ma": ma, "slug": slug, "giaiDoan": "quan-sat",
                    "giaNen": float(S), "giaMo": float(K),
                    "sigmaGiay": sig, "conLaiGiay": tau,
                    "so": {"UP": _thang(giua, True),
                           "DOWN": _thang(giua, False)},
                }],
            })
    ra.sort(key=lambda k: k["luc"])
    return ra
