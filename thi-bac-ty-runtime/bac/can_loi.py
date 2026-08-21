"""Cân lợi — từ hai báo giá ra một con số dám xuống tiền.

Thứ tự trừ ở đây không tuỳ tiện. Mỗi khoản trừ đã từng là chỗ một scanner
tuyên bố có lãi trong khi thực tế lỗ:

    funding thực thu       ← đếm theo MỐC, không nhân theo giờ (dongho.py)
      − phí taker vào      × 2 chân
      − phí taker ra       × 2 chân
      − trượt giá          × 4 lần khớp
      ─────────────────────
      = NET EDGE

Bốn khoản chưa có trong bản này, và **phải biết là chưa có** chứ đừng tưởng
đã đủ: chi phí vay coin để short spot, phí chuyển vốn giữa sàn, rủi ro basis
khi hai mark rời nhau lúc thoát, và vốn bị khoá không làm được việc khác.
Chúng đứng trong `README.md` mục "Chưa trừ gì" và trong lộ trình V0.4.
"""
from __future__ import annotations

from itertools import combinations

from .dongho import thu_cap
from .models import BaoGia, CoHoi

BPS = 10_000.0


def phi_khu_hoi_bps(sanLong: str, sanShort: str, phiSan: dict) -> float:
    """Phí + trượt giá cho TRỌN một vòng: vào hai chân, ra hai chân.

    Nhân 2 cho mỗi sàn là vì mỗi chân phải khớp hai lần. Bỏ quên nhân 2 là
    cách rẻ nhất để một chiến lược lỗ trông như lãi — và nó đã từng bị bỏ
    quên trong đúng bản đầu tiên của mọi funding bot từng tồn tại.
    """
    tong = 0.0
    for san in (sanLong, sanShort):
        c = phiSan.get(san) or {}
        moi_lan = float(c.get("phiTakerBps", 0.0)) + float(c.get("truotGiaBps", 0.0))
        tong += moi_lan * 2.0
    return tong


def lech_mark_bps(a: float | None, b: float | None) -> float | None:
    """Hai mark rời nhau bao nhiêu, tính theo bps của trung điểm.

    Trả `None` khi thiếu một bên — và `None` KHÔNG được coi là 0. Thiếu giá
    thì ta không biết hai sàn có đang nhìn cùng một thế giới hay không, và
    "không biết" phải chặn lệnh chứ không được lặng lẽ thành "không lệch".
    """
    if not a or not b or a <= 0 or b <= 0:
        return None
    giua = (a + b) / 2.0
    return abs(a - b) / giua * BPS


def net_apr_pct(netBps: float, giuGio: float) -> float | None:
    """Ngoại suy NET của một vòng giữ ra cả năm — và vì sao nó hay nói dối.

    Phép ngoại suy này giả định ba điều mà thị trường không hứa: chênh lệch
    funding y nguyên, vào lại được ngay sau khi thoát, và mỗi vòng lại trả
    trọn bộ phí. Sai một trong ba là con số sai — thường là sai theo hướng
    đẹp lên.

    Cửa sổ giữ càng ngắn thì hệ số nhân càng lớn, nên một cơ hội giữ 15 phút
    sẽ khoe APR gấp 32 lần một cơ hội giữ 8 giờ có cùng NET. Vì vậy runtime
    này **xếp hạng theo `netBps`**, còn APR chỉ để lên bảng cho người đọc.

    Dưới `giuGio` rất nhỏ thì trả `None` thay vì một số lớn vô nghĩa.
    """
    if giuGio < 0.25:
        return None
    return (netBps / BPS) * (24.0 / giuGio) * 365.0 * 100.0


def tim_co_hoi(bao: list[BaoGia], nowMs: float, giuGio: float,
               phiSan: dict, cong) -> list[CoHoi]:
    """Ghép mọi cặp sàn cho từng tài sản, tính NET, rồi cho qua cổng rủi ro.

    `cong` là một callable `(CoHoi-thô) -> (duyệt, lý do)`. Tách ra khỏi đây
    để cổng rủi ro có quyền phủ quyết ở MỘT chỗ, và để phép kiểm dựng được
    một cổng giả mà không phải dựng cả cấu hình.
    """
    theo_ma: dict[str, list[BaoGia]] = {}
    for b in bao:
        theo_ma.setdefault(b.ma, []).append(b)

    ra: list[CoHoi] = []
    for ma, ds in theo_ma.items():
        for a, b in combinations(ds, 2):
            # Quy ước dấu: funding dương thì LONG trả, SHORT nhận. Nên chân
            # LONG đặt ở sàn funding/giờ THẤP, chân SHORT ở sàn CAO.
            # So bằng `moiGio`, không bằng `rate` thô — đây đúng là chỗ mà
            # 0,08%/8h trông to hơn 0,015%/1h trong khi thực tế nhỏ hơn.
            l, s = sorted((a, b), key=lambda q: q.moiGio)
            ra.append(_mot_cap(ma, l, s, nowMs, giuGio, phiSan, cong))

    # Xếp theo NET, không theo APR và càng không theo funding thô.
    return sorted(ra, key=lambda c: c.netBps, reverse=True)


def _mot_cap(ma: str, l: BaoGia, s: BaoGia, nowMs: float, giuGio: float,
             phiSan: dict, cong) -> CoHoi:
    gross_ngay_bps = (s.moiGio - l.moiGio) * 24.0 * BPS

    cap = thu_cap(nowMs, giuGio,
                  l.rate, l.mocKeMs, l.intervalGio,
                  s.rate, s.mocKeMs, s.intervalGio)
    thu_bps = cap["thu"] * BPS
    phi_bps = phi_khu_hoi_bps(l.san, s.san, phiSan)
    net_bps = thu_bps - phi_bps

    tuoi = [t for t in (l.tuoi_giay(nowMs), s.tuoi_giay(nowMs)) if t is not None]

    tho = CoHoi(
        ma=ma, sanLong=l.san, sanShort=s.san,
        rateLong=l.rate, rateShort=s.rate,
        intervalLongGio=l.intervalGio, intervalShortGio=s.intervalGio,
        grossBpsNgay=gross_ngay_bps, giuGio=giuGio,
        soMocLong=cap["soMocLong"], soMocShort=cap["soMocShort"],
        thuBps=thu_bps, phiBps=phi_bps, netBps=net_bps,
        netAprPct=net_apr_pct(net_bps, giuGio),
        lechMarkBps=lech_mark_bps(l.markPx, s.markPx),
        choMocDauGiay=cap["choMocDauGiay"],
        tuoiXauNhatGiay=max(tuoi) if tuoi else None,
        uocLuongMoc=cap["uocLuong"],
        duyet=False, lyDo=(),
    )
    duyet, ly_do = cong(tho)
    return CoHoi(**{**tho.__dict__, "duyet": duyet, "lyDo": tuple(ly_do)})
