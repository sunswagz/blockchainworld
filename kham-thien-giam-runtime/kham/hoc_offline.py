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
from . import nan_lai
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
#: Nút mà BÀN THỬ BRIER nhìn thấy được. NGUỒN DUY NHẤT — `tu-nang-cap.py`
#: và `tien-hoa-mo-hinh.py` nhập từ đây, không giữ bản sao.
#:
#: Hai nút KHÔNG ở đây, mỗi cái một lý do khác nhau:
#:
#: `dinhGia.batDinhToiThieu` chạm `batDinh` chứ không chạm `pUp`. Bàn
#: thử chấm bằng Brier trên `pUp`, nên vặn nó ở đây là vặn mù.
#:
#: `dinhGia.sanNenGiay` thì chạm `pUp` thật — `tau = max(san, tau_that)`
#: — nhưng bàn thử KHÔNG BAO GIỜ chạm tới nó. Lát cắt nhỏ nhất là 60
#: giây (nến 1 phút không cho lát nào nhỏ hơn rơi đúng mốc phút), còn
#: mép trên của nút là 15 giây. `tau_that` không bao giờ xuống dưới sàn,
#: nên `max` luôn trả `tau_that` và nút không đổi một con số nào.
#:
#: Đo được: quét cả trục 1 → 15 cho Brier GIỐNG HỆT tới 5 chữ số, khoảng
#: tin đúng bằng [0,000000, 0,000000] trên 1.440 khối. Để nó trong danh
#: sách là mỗi lượt tiến hoá tốn ứng viên cho một nút mà thước không
#: nhìn thấy, rồi kết luận "không cải thiện" — nghe như dữ liệu đã nói,
#: thật ra là cái thước đã nói.
#:
#: Nó VẪN đo được, bằng thước khác: vòng tiến hoá ngày chấm bằng LÃI LỖ
#: trên băng, và băng có khung ở mọi τ kể cả sát 0.
NUT_MO_HINH = ("dinhGia.bienDongCuaSoGiay",
                "dinhGia.heSoSigma",
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


def sigma_tai(theoMoc: dict, T: int, cuaSoGiay: float,
              ma: str | None = None) -> float | None:
    """σ mỗi giây tại mốc T. Có nhớ lại.

    DÙNG LẠI `DoBienDong` chứ không tự tính. Hai bản sao của một bộ ước
    là hai chỗ để chúng trôi ra khỏi nhau, và cái trôi ấy lặng — mỗi bản
    vẫn chạy được, chỉ là tham số vặn cho bản này không còn đúng cho bản
    kia. Đã cắn đúng thế một lần: `tu-nang-cap.py` vặn cửa sổ σ trên lưới
    phút trong khi runtime chạy bộ ước mẫu thô, và σ chạy thật chỉ bằng
    0,875 lần σ đã tuning.

    Quét hàng chục ứng viên mà chỉ một nút đụng tới σ, nên nhớ theo
    (CHỢ, mốc, số nến) làm một lượt chấm nhanh gấp 3,4 lần.

    ## Khoá nhớ phải mang MÃ CHỢ, và thiếu mã thì KHÔNG nhớ

    Bản trước nhớ theo `(mốc, số nến)` — không có chợ. `theoMoc` là
    tham số, nên hàm trông như thuần tuý; nhưng bộ nhớ thì chung, và
    `tu-nang-cap.py` chấm BỐN chợ tại CÙNG một mốc trong một tiến
    trình. Chợ đầu tiên ghi khoá, ba chợ sau đọc lại đúng σ của nó.

    Đo được: ETH nhận σ của BTC, lệch **28 lần** (0,00126 so với
    0,0000443). σ là mẫu số của z, nên đó không phải sai số — đó là một
    mô hình khác hẳn. Và `tu-nang-cap.py` là script GHI `config.json`,
    nên mọi nút nó từng vặn đều chấm trên ba phần tư dữ liệu hỏng.

    Không phép kiểm nào đỏ, vì mỗi lời gọi lẻ vẫn trả đúng.

    Nay: `ma` là None thì **không đụng bộ nhớ** — tính lại mỗi lần.
    Đường mặc định luôn ĐÚNG; nhanh là thứ người gọi phải tự khai bằng
    cách nói mình đang hỏi cho chợ nào. Ngược lại (mặc định nhanh, đúng
    phải khai) thì chỗ gọi mới nào cũng là một cái bẫy nữa.
    """
    soNen = max(2, int(round(cuaSoGiay / 60.0)))
    khoa = (ma, T, soNen) if ma else None
    if khoa is not None and khoa in _NHO_SIGMA:
        return _NHO_SIGMA[khoa]
    nen = []
    for i in range(soNen + 1):
        g = theoMoc.get(T - i * int(PHUT))
        if g is None or g <= 0:
            if khoa is not None:
                _NHO_SIGMA[khoa] = None
            return None
        nen.append((float(T - i * int(PHUT)), float(g)))
    bd = DoBienDong()
    bd.mo_dau(nen)
    ra = bd.sigma_giay()
    if khoa is not None:
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
        sig = sigma_tai(theoMoc, T, cuaSoGiay, ma)
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

def dung_so_hieu_chinh(soNgay: int = 7, ma: str | list | None = None,
                       ghiTho: bool = True) -> dict:
    """Dựng lại `hieu-chinh.json` từ Binance. KHÔNG cộng dồn lên sổ cũ.

    `HieuChinh()` đọc sổ cũ rồi cộng tiếp; chạy hai lần là mọi ô nhân
    đôi. Sai số trung bình không đổi nên nó không lộ ra ở đâu — chỉ `n`
    phình lên, mà `n` là thứ quyết định Kelly có được mở hay không.

    ## MỘT đường nắn, khớp trên MỌI chợ — không phải trên chợ đầu tiên

    `dinh_gia` áp một sổ hiệu chỉnh duy nhất cho cả bốn chợ, và
    `scripts/do-nan-chung-hay-rieng.py` đã đo ngoài mẫu rằng như thế là
    đúng: đường CHUNG 1,590c so với bốn đường RIÊNG 1,640c, thắng 2/4
    chợ — không có cớ để tách, vì tách là chia mẫu cho bốn.

    Nhưng "một đường chung" không có nghĩa là "khớp trên một chợ".
    `vong._hoc_offline` truyền `ma` bằng chợ ĐẦU TIÊN đang theo, tức
    luôn là BTC_5M; mà hàm này lại `unlink()` sổ thô trước khi ghi. Nên
    mỗi vòng ngày lặng lẽ thu sổ thô từ bốn chợ về một chợ: đo được
    30/08/2026, file còn đúng 40.336 dòng và 100% là BTC_5M, sau khi
    từng có 228.156 dòng bốn chợ.

    Hậu quả không nằm ở số dòng mà ở chỗ đường nắn ấy được áp cho
    ETH/SOL/XRP — ba chợ có σ khác hẳn BTC (SOL và XRP cỡ 2,4 lần) và
    có sai số hiệu chỉnh riêng (3,0c tới 3,8c thô, tuỳ chợ).

    Nay `ma` nhận cả DANH SÁCH, xoá sổ thô đúng MỘT lần, và mặc định là
    mọi chợ đối chiếu được. Một `HieuChinh` duy nhất gom cả bốn.
    """
    from .ket_qua import thi_truong_doi_chieu_duoc

    if ma is None:
        ds = [str(t["ma"]) for t in thi_truong_doi_chieu_duoc()]
    elif isinstance(ma, str):
        ds = [ma]
    else:
        ds = [str(x) for x in ma]
    if not ds:
        return {"loi": "không có market nào đối chiếu được"}

    capTheoMa = {}
    for m in ds:
        c = next((t.get("nen") for t in CONFIG["thiTruong"]
                  if t.get("ma") == m), None)
        if not c:
            return {"loi": f"không có market `{m}`"}
        capTheoMa[m] = c

    cuaSo = cua_so_sigma()
    soNen = soNgay * 24 * 60 + int(cuaSo / 60.0) + 20
    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT

    if ghiTho:
        # ĐÚNG file mà `ghi_tho` ghi vào, đọc từ `nan_lai` chứ không dựng
        # lại đường dẫn. Hai lối viết cho một file là hai chỗ để chúng
        # trôi khỏi nhau, và lúc trôi thì phần xoá im lặng trượt mục
        # tiêu: sổ cũ ở lại, `ghi_tho` nối tiếp, mọi ô nhân đôi.
        tho = nan_lai.DUONG_THO
        if tho.exists():
            tho.unlink()      # `ghi_tho` NỐI THÊM — không xoá thì nhân đôi
            # XOÁ ĐÚNG MỘT LẦN, ngoài vòng lặp chợ. Trong vòng lặp thì
            # chợ sau xoá mất chợ trước, và sổ còn lại đúng một chợ.

    hc = HieuChinh()
    hc.o = {}
    theoCho: dict = {}
    for m in ds:
        quen_sigma()
        theoMoc = nen_1p(capTheoMa[m], hetMs - soNen * PHUT, soNen)
        if len(theoMoc) < 400:
            # Một chợ hụt nến KHÔNG được giết cả lượt — nhưng phải khai
            # ra, chứ không lặng lẽ khớp trên ba chợ và báo như bốn.
            theoCho[m] = {"loi": f"chỉ lấy được {len(theoMoc)} nến"}
            continue
        # Quét MỌI mốc phút cho hiệu chỉnh: khung [T, T+300] nào cũng
        # hợp lệ, không cần trùng lưới Polymarket. (Sổ KẾT QUẢ thì ngược
        # lại — chỉ nhận mốc 5 phút, vì nó là danh sách market CÓ THẬT.)
        # `keoTau`/`keoMoc`: sổ thô phải mang τ và MỐC KHUNG, không chỉ
        # `(p, thắng)`. Thiếu τ thì không kiểm được "một đường nắn cho cả
        # bốn lát" — câu chưa ai hỏi; thiếu mốc thì mọi khoảng tin dựng
        # từ sổ này đều hẹp hơn sự thật, vì bốn lát của một khung chia
        # chung MỘT kết quả.
        cap_ = cap_du_doan(theoMoc, sorted(theoMoc), m, cuaSo,
                           keoTau=True, keoMoc=True)
        for pp, t, tau, T in cap_:
            hc.them(pp, t)
            if ghiTho:
                ghi_tho(pp, t, m, tau=tau, moc=T)
        theoCho[m] = {"soCap": len(cap_)}

    if not hc.tong_mau:
        return {"loi": "không dựng được cặp nào", "theoCho": theoCho}
    hc.ghi()
    pn = khop(hc)
    soCap = sum(v.get("soCap", 0) for v in theoCho.values())
    return {"soCap": soCap, "tongMau": hc.tong_mau,
            "soCho": sum(1 for v in theoCho.values() if "soCap" in v),
            "theoCho": theoCho,
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


DUONG_NHAT_KY_MO_HINH = DATA_DIR / "tien-hoa-mo-hinh.jsonl"


def _ghi_nhat_ky_mo_hinh(ban: dict) -> None:
    """Ghi lại MỌI phán quyết của cổng mô hình, nhận hay không.

    `tien-hoa.jsonl` ghi vòng chạy trên BĂNG. Cổng mô hình là một vòng
    KHÁC, chạy mỗi đêm trong `_hoc_offline`, và nó GHI ĐƯỢC vào
    `config.json` — mà trước nay không để lại một dòng nào. Nghĩa là
    một tham số của mô hình có thể đổi lúc 02:00 UTC và sáng ra không
    có cách nào biết nó đổi lúc nào, vì sao, trên bằng chứng nào.

    Ghi cả lượt TRẢ LẠI, không chỉ lượt nhận: chuỗi những lần suýt vặn
    mới là thứ nói cho biết cổng đang đứng ở đâu so với ngưỡng.
    """
    try:
        import json as _json
        DUONG_NHAT_KY_MO_HINH.parent.mkdir(parents=True, exist_ok=True)
        d = dict(ban)
        d["luc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        # Cùng file với `scripts/tien-hoa-mo-hinh.py` vì cùng một việc —
        # phán quyết của cổng mô hình. Hai đường có hai hình dạng dòng
        # khác nhau, nên phải phân biệt được nguồn chứ đừng bắt người
        # đọc suy từ việc thiếu trường nào.
        d["nguon"] = "vong-ngay"
        with DUONG_NHAT_KY_MO_HINH.open("a", encoding="utf-8") as f:
            f.write(_json.dumps(d, ensure_ascii=False, default=str) + chr(10))
    except OSError:
        pass


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

    # ── KHOẢNG TIN CHỨA 0 THÌ KHÔNG VẶN ───────────────────────────────
    #
    # Bản trước tính `trongTiengOn`, in nó ra, rồi `ghi_config` BẤT KỂ
    # nó. Cảnh báo dán lên một thay đổi đã xảy ra rồi thì không phải
    # cảnh báo — buồng lái hiện "⚠ nằm trong tiếng ồn" ngay dưới dòng
    # "tiến hoá MÔ HÌNH NHẬN", và config đã đổi.
    #
    # Đo được 30/08/2026: lượt chấm thật trên BTC_5M, 10 ngày, 49 ứng
    # viên, cổng NHẬN `nanLai.heSoGiamChan 0,85 → 0,3` với
    # `tin95 = [-0,000403, +0,000816]` — chứa 0, và nhảy trọn cả dải.
    # Hai cổng CHỌN/CHỐT gật được vì trục ấy PHẲNG: trên một trục phẳng
    # thì mọi ứng viên đều "gật" được, và cỗ máy đi bộ ngẫu nhiên.
    #
    # Chính chỗ này đã viết ra lý do phải có khoảng tin — "qua ngưỡng
    # bằng 0,00001 và qua bằng 0,01 đọc y hệt nhau nếu chỉ ghi chữ
    # NHẬN". Nay dùng nó để QUYẾT, chứ không chỉ để in.
    if ban["trongTiengOn"]:
        ban["lyDo"] = ("hai tập gật nhưng khoảng tin CHỨA 0 — "
                       "không đủ để vặn")
        _ghi_nhat_ky_mo_hinh(ban)
        return ban

    if not thu:
        ghi_config(duong, v)
    ban["nhan"] = {"nut": duong, "tu": hienTai[duong], "den": v}
    ban["lyDo"] = "cả hai tập gật"
    _ghi_nhat_ky_mo_hinh(ban)
    return ban
