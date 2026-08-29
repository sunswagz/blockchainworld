"""Học và tiến hoá MÔ HÌNH mà không cần chợ — lõi dùng chung.

Ba script `hoc-tu-binance.py`, `tien-hoa-mo-hinh.py`, `tu-nang-cap.py`
đều dựng lại cùng một bộ máy: lấy nến, ước σ, dựng cặp (mô hình nói /
thực tế ra), chia ba tập theo thời gian, chấm Brier. Ba bản sao của một
thứ là ba chỗ để chúng trôi ra khỏi nhau — và cái trôi ấy sẽ lặng lẽ,
vì mỗi bản vẫn chạy được.

Nhưng lý do thật để gom vào module không phải gọn gàng. Nó là: **vòng
ngày trong runtime không với tới được một script.**

`_soat_tien_hoa` chạy `tien_hoa.mot_luot()` — cổng chấm bằng TIỀN. Cổng
ấy cần giá chợ, mà đường tới Polymarket đang đứt, nên nó đứng yên với lý
do "thiếu mẫu" và sẽ đứng yên mãi. Trong khi cổng chấm bằng ĐỘ CHUẨN DỰ
BÁO thì chạy được ngay hôm nay, chỉ cần Binance — và nó nằm ngoài tầm
với của runtime vì nó là một file trong `scripts/`.

Nên: lõi ở đây, script gọi vào đây, và `vong.py` cũng gọi vào đây.

## Hai việc, mỗi ngày một lần

    1. DỰNG LẠI sổ hiệu chỉnh từ Binance   — bảng cũ đi thì Kelly khoá
    2. VẶN một nút mô hình nếu đáng          — ba tập tách theo thời gian

Việc 1 phải chạy trước: việc 2 chấm bằng phép nắn khớp từ chính sổ ấy.
"""
from __future__ import annotations

import math
import random
import statistics
import time

from .chan_doan import NUT_THEO_DUONG, doc_tham_so
from .config import CONFIG, DATA_DIR
from .dinh_gia import HieuChinh, dinh_gia
from .nan_lai import ghi_tho, khop
from .nguon import nguon

PHUT = 60_000.0

#: Lát cắt trong khung ăn thua, giây CÒN LẠI. CHỈ những mốc rơi đúng
#: ranh giới phút: nến 1 phút không cho biết giá ở giữa phút, và làm
#: tròn LÊN là lấy giá của tương lai. Lát τ=30 từng nhận thẳng giá kết
#: toán vì đúng lỗi ấy, và nó hiện ra thành một bảng hiệu chỉnh đẹp
#: hoàn hảo — trông y hệt một mô hình giỏi.
LAT_CAT = (240.0, 180.0, 120.0, 60.0)

#: Nút CHẠM VÀO `pUp`, nên chấm được bằng độ chuẩn dự báo.
#: `dinhGia.batDinhToiThieu` KHÔNG ở đây: nó chạm `batDinh` chứ không
#: chạm `pUp` — vặn nó bằng phép đo này là vặn mù.
NUT_MO_HINH = ("dinhGia.bienDongCuaSoGiay", "dinhGia.sanNenGiay",
               "dinhGia.matPhangCanKetQua", "nanLai.heSoGiamChan")

CHIA_HOC, CHIA_CHON = 0.50, 0.75
BIEN_CHON = 0.995
BIEN_CHOT = 0.999


# ══════════════════════════════════════════════════════════════════════
#  NẾN
# ══════════════════════════════════════════════════════════════════════

def nen_1p(cap: str, tuMs: float, soNen: int) -> dict:
    """{mốc đóng: giá đóng}. Lấy theo LÔ 1000, không hỏi từng mốc."""
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
                ra[int(n[0]) + int(PHUT)] = float(n[4])
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


_NHO_SIGMA: dict = {}


def sigma_tai(theoMoc: dict, T: int, cuaSoGiay: float) -> float | None:
    """σ mỗi giây từ `cuaSoGiay` giây nến 1 phút TRƯỚC T. Có nhớ lại.

    Quét hàng chục ứng viên mà chỉ một nút đụng tới σ, nên ba nút kia
    tính lại y hệt con số cũ hàng trăm nghìn lần. Nhớ theo (mốc, số nến)
    làm một lượt chấm nhanh gấp 3,4 lần.
    """
    soNen = max(2, int(round(cuaSoGiay / 60.0)))
    khoa = (T, soNen)
    if khoa in _NHO_SIGMA:
        return _NHO_SIGMA[khoa]
    gs = [theoMoc.get(T - i * int(PHUT)) for i in range(soNen + 1)]
    if any(g is None or g <= 0 for g in gs):
        _NHO_SIGMA[khoa] = None
        return None
    c = gs[::-1]
    r = [math.log(c[i + 1] / c[i]) for i in range(len(c) - 1)]
    if len(r) < 2:
        _NHO_SIGMA[khoa] = None
        return None
    sd = statistics.pstdev(r)
    ra = (sd / math.sqrt(60.0)) if sd > 0 else None
    _NHO_SIGMA[khoa] = ra
    return ra


def quen_sigma() -> None:
    _NHO_SIGMA.clear()


def cap_du_doan(theoMoc: dict, mocs, ma: str, cuaSoGiay: float,
                keoTau: bool = False) -> list:
    """(p, thắng[, τ]) theo THỨ TỰ THỜI GIAN."""
    ra = []
    for T in mocs:
        K = theoMoc.get(T)
        het = theoMoc.get(T + 5 * int(PHUT))
        if K is None or het is None or abs(het - K) < 1e-12:
            continue
        sig = sigma_tai(theoMoc, T, cuaSoGiay)
        if sig is None:
            continue
        thang = het > K
        for tau in LAT_CAT:
            t = T + int((300.0 - tau) * 1000.0)
            if t % int(PHUT):
                continue
            S = theoMoc.get(t)
            if S is None or S <= 0:
                continue
            gc = dinh_gia(ma, float(S), float(K), tau, sig)
            if gc is None:
                continue
            ra.append((gc.pUp, thang, tau) if keoTau else (gc.pUp, thang))
    return ra


def brier(cap) -> float:
    return sum((p - (1.0 if t else 0.0)) ** 2 for p, t in cap) / max(1, len(cap))


def moc_khung(theoMoc: dict) -> list:
    """Chỉ mốc 5 phút — khung THẬT của chợ."""
    return [T for T in sorted(theoMoc) if T % 300_000 == 0]


def ba_tap(mocs: list) -> tuple:
    a, b = int(len(mocs) * CHIA_HOC), int(len(mocs) * CHIA_CHON)
    return mocs[:a], mocs[a:b], mocs[b:]


def bien_theo_ung_vien(so: int) -> float:
    """Biên SIẾT theo số ứng viên — trả lại phần lợi thế của so sánh bội."""
    return 1.0 - (1.0 - BIEN_CHON) / max(1.0, math.log(max(2, so)))


# ══════════════════════════════════════════════════════════════════════
#  VIỆC 1 — DỰNG LẠI SỔ HIỆU CHỈNH
# ══════════════════════════════════════════════════════════════════════

def dung_so_hieu_chinh(soNgay: int = 7, ma: str = "BTC_5M",
                       ghiTho: bool = True) -> dict:
    """Dựng lại `hieu-chinh.json` từ Binance. KHÔNG cộng dồn lên sổ cũ.

    `HieuChinh()` đọc sổ cũ rồi cộng tiếp; chạy hai lần là mọi ô nhân
    đôi. Sai số trung bình không đổi nên nó không lộ ra ở đâu — chỉ `n`
    phình lên, mà `n` là thứ quyết định Kelly có được mở hay không.
    """
    cap = next((t.get("nen") for t in CONFIG["thiTruong"]
                if t.get("ma") == ma), None)
    if not cap:
        return {"loi": f"không có market `{ma}`"}
    cuaSo = float(doc_tham_so("dinhGia.bienDongCuaSoGiay") or 900.0)
    soNen = soNgay * 24 * 60 + int(cuaSo / 60.0) + 20
    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    quen_sigma()
    theoMoc = nen_1p(cap, hetMs - soNen * PHUT, soNen)
    if len(theoMoc) < 400:
        return {"loi": f"chỉ lấy được {len(theoMoc)} nến"}

    if ghiTho:
        tho = DATA_DIR / "hieu-chinh-tho.jsonl"
        if tho.exists():
            tho.unlink()      # `ghi_tho` NỐI THÊM — không xoá thì nhân đôi

    hc = HieuChinh()
    hc.o = {}
    # Quét MỌI mốc phút cho hiệu chỉnh: khung [T, T+300] nào cũng hợp lệ,
    # không cần trùng lưới Polymarket. (Sổ KẾT QUẢ thì ngược lại — chỉ
    # nhận mốc 5 phút, vì nó là danh sách market CÓ THẬT.)
    cap_ = cap_du_doan(theoMoc, sorted(theoMoc), ma, cuaSo)
    for p, t in cap_:
        hc.them(p, t)
        if ghiTho:
            ghi_tho(p, t, ma)
    if not hc.tong_mau:
        return {"loi": "không dựng được cặp nào"}
    hc.ghi()
    pn = khop(hc)
    return {"soCap": len(cap_), "tongMau": hc.tong_mau,
            "saiSoTB": hc.sai_so_tuyet_doi_tb(),
            "duKelly": hc.du_de_dung_kelly(),
            "nanDungDuoc": pn.dung_duoc,
            "nanTruoc": pn.saiTruoc, "nanSau": pn.saiSau}


# ══════════════════════════════════════════════════════════════════════
#  VIỆC 2 — VẶN MỘT NÚT MÔ HÌNH
# ══════════════════════════════════════════════════════════════════════

def _cham(theoMoc, ba, ma, cuaSo) -> dict | None:
    hoc, chon, chot = (cap_du_doan(theoMoc, m, ma, cuaSo) for m in ba)
    if len(hoc) < 1500 or len(chon) < 500 or len(chot) < 500:
        return None
    hc = HieuChinh(duong=DATA_DIR / "_tam-hoc-offline.json")
    hc.o = {}
    for p, t in hoc:
        hc.them(p, t)
    pn = khop(hc)

    def nan(cap):
        return [(pn.nan(p) if pn.dung_duoc else p, t) for p, t in cap]

    return {"chon": brier(nan(chon)), "chot": brier(nan(chot)),
            "saiChot": [(q - (1.0 if t else 0.0)) ** 2 for q, t in nan(chot)]}


def mot_luot_mo_hinh(soNgay: int = 10, ma: str = "BTC_5M",
                     thu: bool = False) -> dict:
    """Một lượt vặn nút mô hình. Trả về phán quyết, có ghi config nếu nhận.

    Ba tập tách theo THỜI GIAN. Tập CHỐT chỉ GẬT hay LẮC về ứng viên đã
    chọn — không bao giờ dùng để xếp hạng, vì dùng để xếp hạng là biến
    nó thành tập chọn thứ hai và mất luôn tác dụng.
    """
    from .tien_hoa import _dat_tham_so, ghi_config

    cap = next((t.get("nen") for t in CONFIG["thiTruong"]
                if t.get("ma") == ma), None)
    if not cap:
        return {"loi": f"không có market `{ma}`"}
    cuaSo0 = float(doc_tham_so("dinhGia.bienDongCuaSoGiay") or 900.0)
    soNen = soNgay * 24 * 60 + int(cuaSo0 / 60.0) + 20
    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    quen_sigma()
    theoMoc = nen_1p(cap, hetMs - soNen * PHUT, soNen)
    if len(theoMoc) < 1200:
        return {"loi": f"chỉ lấy được {len(theoMoc)} nến"}
    ba = ba_tap(moc_khung(theoMoc))
    goc = _cham(theoMoc, ba, ma, cuaSo0)
    if goc is None:
        return {"loi": "chưa đủ cặp để chấm"}

    hienTai = {d: float(doc_tham_so(d) or 0.0) for d in NUT_MO_HINH}
    ungVien = []
    for duong in NUT_MO_HINH:
        n = NUT_THEO_DUONG.get(duong)
        if n is None:
            continue
        v = float(n.thap)
        while v <= n.cao + 1e-9:
            if abs(v - hienTai[duong]) > 1e-12:
                ungVien.append((duong, round(v, 6)))
            v += n.buoc

    tot = None
    for duong, v in ungVien:
        if duong == "dinhGia.bienDongCuaSoGiay":
            r = _cham(theoMoc, ba, ma, v)
        else:
            cu = _dat_tham_so(duong, v)
            try:
                r = _cham(theoMoc, ba, ma, cuaSo0)
            finally:
                _dat_tham_so(duong, cu)
        if r is not None and (tot is None or r["chon"] < tot[2]["chon"]):
            tot = (duong, v, r)

    ban = {"ma": ma, "soNgay": soNgay, "soUngVien": len(ungVien),
           "chonGoc": goc["chon"], "chotGoc": goc["chot"], "nhan": None}
    if tot is None:
        ban["lyDo"] = "không ứng viên nào chấm được"
        return ban

    duong, v, r = tot
    bien = bien_theo_ung_vien(len(ungVien))
    ban.update({"nut": duong, "tu": hienTai[duong], "den": v, "bien": bien,
                "chonMoi": r["chon"], "chotMoi": r["chot"]})
    if r["chon"] >= goc["chon"] * bien:
        ban["lyDo"] = "thua ở tập CHỌN"
        return ban
    if r["chot"] >= goc["chot"] * BIEN_CHOT:
        ban["lyDo"] = "tập CHỐT không gật"
        return ban

    # Khoảng tin có cặp: "qua ngưỡng bằng 0,00001" và "qua bằng 0,01"
    # đọc y hệt nhau nếu chỉ ghi chữ NHẬN.
    hieu = [x - y for x, y in zip(goc["saiChot"], r["saiChot"])]
    n_ = len(hieu)
    rd = random.Random(20260829)
    lan = sorted(sum(hieu[rd.randrange(n_)] for _ in range(n_)) / n_
                 for _ in range(2000))
    ban["chenhChot"] = sum(hieu) / n_
    ban["tin95"] = [lan[int(0.025 * len(lan))], lan[int(0.975 * len(lan))]]
    ban["trongTiengOn"] = ban["tin95"][0] <= 0 <= ban["tin95"][1]

    if not thu:
        ghi_config(duong, v)
    ban["nhan"] = {"nut": duong, "tu": hienTai[duong], "den": v}
    ban["lyDo"] = "cả hai tập gật"
    return ban
