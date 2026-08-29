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
from .dinh_gia import DoBienDong, HieuChinh, dinh_gia
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


def cua_so_sigma() -> float:
    """Cửa sổ ước σ, giây. MỘT chỗ duy nhất trả lời — kể cả khi thiếu khoá.

    Bốn chỗ từng tự đọc khoá này, và một trong bốn rơi về **300** trong
    khi ba chỗ kia rơi về **900**:

        hoc_offline (×2)        or 900.0
        do-cho-that.py          or 900.0
        tien-hoa-mo-hinh.py     or 300.0     ← lệch

    Khoá đang có trong config nên mặc định chưa bao giờ được dùng tới, và
    chính vì thế nó nằm im. Ngày ai đó đổi tên khoá hoặc chạy với một
    config tối giản thì `tien-hoa-mo-hinh` đo bằng cửa sổ 300s trong khi
    cả hệ dùng 900s — và cổng tiến hoá sẽ kết luận về một cỗ máy không
    tồn tại. Đúng lớp lỗi "hai đường nói khác nhau" đã gặp nhiều lần.

    Mặc định 900 vì đó là giá trị vòng tự nâng cấp đã ĐO và chọn.
    """
    return float(doc_tham_so("dinhGia.bienDongCuaSoGiay") or 900.0)


def sigma_tai(theoMoc: dict, T: int, cuaSoGiay: float) -> float | None:
    """σ mỗi giây tại mốc T. Có nhớ lại.

    DÙNG LẠI `DoBienDong` chứ không tự tính. Hai bản sao của một bộ ước
    là hai chỗ để chúng trôi ra khỏi nhau, và cái trôi ấy lặng — mỗi bản
    vẫn chạy được, chỉ là tham số vặn cho bản này không còn đúng cho bản
    kia. Đã cắn đúng thế một lần: `tu-nang-cap.py` vặn cửa sổ σ trên lưới
    phút trong khi runtime chạy bộ ước mẫu thô, và σ chạy thật chỉ bằng
    0,875 lần σ đã tuning.

    Quét hàng chục ứng viên mà chỉ một nút đụng tới σ, nên nhớ theo
    (mốc, số nến) làm một lượt chấm nhanh gấp 3,4 lần.
    """
    soNen = max(2, int(round(cuaSoGiay / 60.0)))
    khoa = (T, soNen)
    if khoa in _NHO_SIGMA:
        return _NHO_SIGMA[khoa]
    nen = []
    for i in range(soNen + 1):
        g = theoMoc.get(T - i * int(PHUT))
        if g is None or g <= 0:
            _NHO_SIGMA[khoa] = None
            return None
        nen.append((float(T - i * int(PHUT)), float(g)))
    bd = DoBienDong()
    bd.mo_dau(nen)
    ra = bd.sigma_giay()
    _NHO_SIGMA[khoa] = ra
    return ra


def quen_sigma() -> None:
    _NHO_SIGMA.clear()


def cap_du_doan(theoMoc: dict, mocs, ma: str, cuaSoGiay: float,
                keoTau: bool = False, keoMoc: bool = False) -> list:
    """(p, thắng[, τ][, mốc khung]) theo THỨ TỰ THỜI GIAN.

    `keoMoc` để người gọi gộp được theo KHUNG. Bốn lát cắt của một khung
    chia chung MỘT kết quả, nên chúng không phải bốn quan sát độc lập —
    và bootstrap theo cặp là tự cho mình gấp bốn lần độ chắc chắn.
    """
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
            x = [gc.pUp, thang]
            if keoTau:
                x.append(tau)
            if keoMoc:
                x.append(T)
            ra.append(tuple(x))
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
    cuaSo = cua_so_sigma()
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

def khoang_tin_theo_khoi(hieu: list, moc: list | None,
                         soLan: int = 2000) -> tuple:
    """Khoảng tin 95% cho trung bình `hieu`, lấy lại theo KHỐI.

    Bốn lát cắt (τ = 240/180/120/60) của một khung chia chung MỘT kết
    quả, nên chúng không phải bốn quan sát độc lập. Lấy lại theo từng
    cặp là giả vờ có gấp bốn số quan sát thực, và khoảng tin hẹp đi theo
    căn của cái giả vờ ấy — tức cổng dễ NHẬN một thay đổi chỉ là tiếng
    ồn.

    Cùng cái bẫy đã cắn ở `chay_lai` (đếm mỗi cửa sổ 44 lần, ra lãi 2,9
    triệu đô) và ở `do-cho-that.py` (1.006 dòng hoá ra là 14 cửa sổ).
    Lần này nó nằm đúng chỗ ghi vào `config.json`.

    Trả (thấp, cao, số khối). `moc` thiếu thì mỗi cặp là một khối — vẫn
    chạy, nhưng khoảng tin sẽ hẹp hơn sự thật, nên người gọi nên đưa mốc.
    """
    if not hieu:
        return (0.0, 0.0, 0)
    khoi: dict = {}
    for h, m in zip(hieu, moc or range(len(hieu))):
        khoi.setdefault(m, []).append(h)
    ds = list(khoi.values())
    soK = len(ds)
    rd = random.Random(20260829)
    lan = []
    for _ in range(soLan):
        t = 0.0
        c = 0
        for _k in range(soK):
            b = ds[rd.randrange(soK)]
            t += sum(b)
            c += len(b)
        lan.append(t / max(1, c))
    lan.sort()
    return (lan[int(0.025 * soLan)], lan[int(0.975 * soLan)], soK)


def _cham(theoMoc, ba, ma, cuaSo) -> dict | None:
    hoc, chon = (cap_du_doan(theoMoc, m, ma, cuaSo) for m in ba[:2])
    chot = cap_du_doan(theoMoc, ba[2], ma, cuaSo, keoMoc=True)
    if len(hoc) < 1500 or len(chon) < 500 or len(chot) < 500:
        return None
    hc = HieuChinh(duong=DATA_DIR / "_tam-hoc-offline.json")
    hc.o = {}
    for p, t in hoc:
        hc.them(p, t)
    pn = khop(hc)

    def nan(cap):
        return [(pn.nan(p) if pn.dung_duoc else p, t) for p, t, *_ in cap]

    return {"chon": brier(nan(chon)), "chot": brier(nan(chot)),
            "saiChot": [(q - (1.0 if t else 0.0)) ** 2 for q, t in nan(chot)],
            # Mốc khung của TỪNG cặp ở tập CHỐT, để bootstrap gộp theo
            # KHUNG. Bốn lát cắt của một khung chia chung một kết quả.
            "mocChot": [x[-1] for x in chot]}


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
    cuaSo0 = cua_so_sigma()
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
    thap, cao, soK = khoang_tin_theo_khoi(hieu, goc.get("mocChot"))
    ban["chenhChot"] = sum(hieu) / n_
    ban["soKhoiChot"] = soK
    ban["tin95"] = [thap, cao]
    ban["trongTiengOn"] = ban["tin95"][0] <= 0 <= ban["tin95"][1]

    if not thu:
        ghi_config(duong, v)
    ban["nhan"] = {"nut": duong, "tu": hienTai[duong], "den": v}
    ban["lyDo"] = "cả hai tập gật"
    return ban
