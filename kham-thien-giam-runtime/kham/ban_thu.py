"""Bàn thử: bộ máy chấm dùng chung cho mọi phép thử mô hình.

Năm script `thu-*` từng có năm bản sao của đúng bộ máy này — `nen_ohlc`,
`_lay_nen`, `_brier`, `cap_du_doan`, `cham`, `uoc_tron`. Chúng ra đời bằng
cách chép khung của nhau, và đó chính là cái bệnh cả repo này đi sửa: một
lỗi trong phép chấm thì nằm ở năm chỗ, một cải tiến thì phải sửa năm lần,
và hai bản sẽ lệch nhau vào đúng ngày không ai để ý.

Ở đây nguy hiểm hơn chỗ khác, vì đây là THƯỚC. Thước lệch thì mọi kết luận
đo bằng nó đều lệch, và không con số nào tự khai chuyện ấy.

## Bàn thử này chấm thế nào

Ba tập tách theo THỜI GIAN, không tách ngẫu nhiên — chợ đổi theo ngày, nên
trộn ngày rồi chia là để tương lai rò ngược vào quá khứ:

    HỌC   khớp phép nắn
    CHỌN  xếp hạng ứng viên
    CHỐT  chỉ GẬT hay LẮC, không bao giờ dùng để xếp hạng

Mỗi khung sinh bốn lát cắt τ (240/180/120/60 giây), và **bốn lát ấy chia
chung MỘT kết quả** — nên khoảng tin phải lấy lại theo KHUNG, không theo
cặp. `cham` trả về `mocChot` chính là để chỗ gọi làm được điều đó.

Chỉ nhận τ rơi đúng mốc phút: `floor(t)+1phút` khi làm tròn có thể lấy
chính giá kết toán, và đó là nhìn trộm đáp án.
"""
from __future__ import annotations

import math
import statistics

from .config import CONFIG, DATA_DIR
from .dinh_gia import HieuChinh, dinh_gia
from .nan_lai import khop
from .nguon import nguon

PHUT = 60_000.0

#: Bốn lát cắt τ của mỗi khung 5 phút. Chúng CHIA CHUNG một kết quả.
LAT_CAT = (240.0, 180.0, 120.0, 60.0)



def nen_ohlc(cap: str, tuMs: float, soNen: int) -> dict:
    """{mốc đóng: (mở, cao, thấp, đóng)} — bốn giá, không chỉ giá đóng."""
    moc = int(tuMs // PHUT * PHUT)
    ra: dict = {}
    con = soNen
    while con > 0:
        lo = min(1000, con)
        d = nguon._lay("binance-kline",
                       f"{CONFIG['nguon']['binanceSpot']}/api/v3/klines",
                       {"symbol": cap, "interval": "1m",
                        "startTime": moc, "limit": lo})
        if not isinstance(d, list) or not d:
            break
        for n in d:
            try:
                ra[int(n[0]) + int(PHUT)] = (float(n[1]), float(n[2]),
                                             float(n[3]), float(n[4]))
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


def _lay_nen(oh: dict, T: int, soNen: int):
    ns = [oh.get(T - i * int(PHUT)) for i in range(soNen)]
    if any(x is None or min(x) <= 0 for x in ns):
        return None
    return ns[::-1]


def uoc_tron(oh, T, soNen):
    """σ đương nhiệm: độ lệch chuẩn log-return giá đóng trên lưới phút."""
    c = _lay_nen(oh, T, soNen)
    if c is None:
        return None
    r = [math.log(c[i + 1][3] / c[i][3]) for i in range(len(c) - 1)
         if c[i][3] > 0 and c[i + 1][3] > 0]
    if len(r) < 5:
        return None
    s = statistics.pstdev(r) / math.sqrt(60.0)
    return s if s > 0 else None


def _brier(cap):
    return (sum((p - (1.0 if t else 0.0)) ** 2 for p, t, *_ in cap)
            / max(1, len(cap)))


def cap_du_doan(oh, mocs, ham, soNen, ma: str):
    ra = []
    for T in mocs:
        n0, n5 = oh.get(T), oh.get(T + 5 * int(PHUT))
        if n0 is None or n5 is None:
            continue
        K, het = n0[3], n5[3]
        if abs(het - K) < 1e-12:
            continue
        sig = ham(oh, T, soNen)
        if sig is None:
            continue
        thang = het > K
        for tau in LAT_CAT:
            t = T + int((300.0 - tau) * 1000.0)
            if t % int(PHUT):
                continue
            n = oh.get(t)
            if n is None:
                continue
            gc = dinh_gia(ma, float(n[3]), float(K), tau, sig)
            if gc is not None:
                ra.append((gc.pUp, thang, T))
    return ra


def cham(oh, ba, ham, soNen, ma: str):
    hoc, chon, chot = (cap_du_doan(oh, m, ham, soNen, ma)
                       for m in ba)
    if len(hoc) < 1500 or len(chon) < 500 or len(chot) < 500:
        return None
    hc = HieuChinh(duong=DATA_DIR / "_tam-sigma.json")
    hc.o = {}
    for p, t, *_ in hoc:
        hc.them(p, t)
    pn = khop(hc)

    def nan(cap):
        return [(pn.nan(p) if pn.dung_duoc else p, t) for p, t, *_ in cap]

    return {"n": len(chon), "chon": _brier(nan(chon)),
            "chot": _brier(nan(chot)),
            "saiChot": [(q - (1.0 if t else 0.0)) ** 2 for q, t in nan(chot)],
            "mocChot": [x[-1] for x in chot]}

