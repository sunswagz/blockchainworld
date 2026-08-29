"""MẪU GIÁ — nhận diện hình mẫu biểu đồ bằng hình học, không bằng mắt.

Mười ba mẫu kinh điển, mỗi mẫu là một bộ điều kiện hình học ĐO ĐƯỢC trên chuỗi
đỉnh/đáy swing. Không có mẫu nào ở đây được tin vì sách nói nó đúng; chúng ở đây
để `scripts/do-mau-gia.py` đem ra đo trên lịch sử thật, rồi lò chưng cất mới
quyết định mẫu nào đáng đưa vào trí nhớ.

    ĐẢO CHIỀU   hai đỉnh · hai đáy · vai-đầu-vai · vai-đầu-vai ngược · kim cương
    TIẾP DIỄN   tam giác tăng/giảm/cân · nêm tăng/giảm · cờ · cốc tay cầm
    NÉN         nến trong (inside bar) · nến trùm (outside bar)

BA LUẬT CỦA MODULE NÀY

**1. Mẫu chỉ tính khi ĐÃ XÁC NHẬN.** Một cái "gần giống vai-đầu-vai" chưa phá
cổ áo thì không phải mẫu, nó là một hình thù. Mọi hàm ở đây chỉ trả về mẫu khi
nến cuối cùng của cửa sổ đã phá mức xác nhận — nếu không thì đo lại chính cái
mình vẽ ra, và tỉ lệ thắng sẽ đẹp một cách vô nghĩa.

**2. Mỗi mẫu tự khai điểm vào, stop và mục tiêu.** Không có ba con số đó thì
không đo được gì: "mẫu này đúng 70%" mà không nói đúng tới đâu và sai thì mất
bao nhiêu là một câu rỗng.

**3. Không nhìn về tương lai.** Hàm nhận đúng cửa sổ nến tính tới hiện tại. Chỗ
duy nhất được biết tương lai là script đo, và nó biết để CHẤM ĐIỂM chứ không để
phát hiện.
"""
from __future__ import annotations

from typing import Any, Sequence

from .indicators import atr as _atr, swings

Candle = dict[str, Any]

# Dung sai hình học — đây là chỗ mọi "mẫu giá" tan thành ý kiến cá nhân nếu
# không ghi rõ. Ai đổi số ở đây thì đổi luôn nghĩa của mọi con số đo được.
NGANG = 0.015      # hai mức coi là BẰNG NHAU khi lệch dưới 1,5%
DOC = 0.02         # một đường coi là NGHIÊNG khi lệch trên 2%
HOI_TU = 0.6       # tam giác/nêm: bề rộng cuối phải ≤ 60% bề rộng đầu
CAN_XUNG = 0.35    # vai trái/phải lệch nhau tối đa 35% chiều cao đầu


def _lech(a: float, b: float) -> float:
    return abs(a - b) / ((a + b) / 2) if (a + b) else 0.0


def _mau(ten, loai, huong, vao, stop, muc_tieu, do_tin, coCau, i) -> dict:
    """Một mẫu đã xác nhận. `rr` tính sẵn để lọc nhanh, không phải để tin."""
    rui = abs(vao - stop)
    return {
        "ten": ten, "loai": loai, "huong": huong,
        "vao": round(vao, 2), "stop": round(stop, 2), "mucTieu": round(muc_tieu, 2),
        "rr": round(abs(muc_tieu - vao) / rui, 2) if rui else None,
        "doTin": round(do_tin, 2), "coCau": coCau, "i": i,
    }


# ── Nhóm ĐẢO CHIỀU ────────────────────────────────────────────────────────
def hai_dinh(c: Sequence[Candle], s: dict) -> dict | None:
    """Hai đỉnh ngang nhau, đáy giữa là cổ áo. Xác nhận khi đóng dưới cổ áo."""
    h, l = s["highs"], s["lows"]
    if len(h) < 2 or len(l) < 1:
        return None
    d1, d2 = h[-2], h[-1]
    giua = [x for x in l if d1["i"] < x["i"] < d2["i"]]
    if not giua:
        return None
    co = min(giua, key=lambda x: x["price"])
    if _lech(d1["price"], d2["price"]) > NGANG:
        return None
    cao = (d1["price"] + d2["price"]) / 2 - co["price"]
    if cao <= 0:
        return None
    gia = c[-1]["c"]
    if gia >= co["price"]:          # chưa phá cổ áo ⇒ chưa phải mẫu
        return None
    return _mau("HAI_ĐỈNH", "ĐẢO_CHIỀU", "SHORT",
                vao=gia, stop=max(d1["price"], d2["price"]),
                muc_tieu=co["price"] - cao,   # measured move: bằng chiều cao mẫu
                do_tin=1 - _lech(d1["price"], d2["price"]) / NGANG * 0.5,
                coCau={"đỉnh1": d1["price"], "đỉnh2": d2["price"], "cổÁo": co["price"]},
                i=len(c) - 1)


def hai_day(c: Sequence[Candle], s: dict) -> dict | None:
    h, l = s["highs"], s["lows"]
    if len(l) < 2 or len(h) < 1:
        return None
    d1, d2 = l[-2], l[-1]
    giua = [x for x in h if d1["i"] < x["i"] < d2["i"]]
    if not giua:
        return None
    co = max(giua, key=lambda x: x["price"])
    if _lech(d1["price"], d2["price"]) > NGANG:
        return None
    cao = co["price"] - (d1["price"] + d2["price"]) / 2
    if cao <= 0:
        return None
    gia = c[-1]["c"]
    if gia <= co["price"]:
        return None
    return _mau("HAI_ĐÁY", "ĐẢO_CHIỀU", "LONG",
                vao=gia, stop=min(d1["price"], d2["price"]),
                muc_tieu=co["price"] + cao,
                do_tin=1 - _lech(d1["price"], d2["price"]) / NGANG * 0.5,
                coCau={"đáy1": d1["price"], "đáy2": d2["price"], "cổÁo": co["price"]},
                i=len(c) - 1)


def vai_dau_vai(c: Sequence[Candle], s: dict) -> dict | None:
    """Ba đỉnh, giữa cao nhất, hai vai cân nhau. Cổ áo qua hai đáy."""
    h, l = s["highs"], s["lows"]
    if len(h) < 3 or len(l) < 2:
        return None
    vt, dau, vp = h[-3], h[-2], h[-1]
    if not (dau["price"] > vt["price"] and dau["price"] > vp["price"]):
        return None
    day = [x for x in l if vt["i"] < x["i"] < vp["i"]]
    if len(day) < 2:
        return None
    co = (day[0]["price"] + day[-1]["price"]) / 2
    cao = dau["price"] - co
    if cao <= 0:
        return None
    # Hai vai phải cân — lệch quá thì đó là ba đỉnh bất kỳ, không phải vai-đầu-vai
    if abs(vt["price"] - vp["price"]) / cao > CAN_XUNG:
        return None
    gia = c[-1]["c"]
    if gia >= co:
        return None
    return _mau("VAI_ĐẦU_VAI", "ĐẢO_CHIỀU", "SHORT",
                vao=gia, stop=vp["price"], muc_tieu=co - cao,
                do_tin=1 - abs(vt["price"] - vp["price"]) / cao / CAN_XUNG * 0.5,
                coCau={"vaiTrái": vt["price"], "đầu": dau["price"],
                       "vaiPhải": vp["price"], "cổÁo": round(co, 2)},
                i=len(c) - 1)


def vai_dau_vai_nguoc(c: Sequence[Candle], s: dict) -> dict | None:
    h, l = s["highs"], s["lows"]
    if len(l) < 3 or len(h) < 2:
        return None
    vt, dau, vp = l[-3], l[-2], l[-1]
    if not (dau["price"] < vt["price"] and dau["price"] < vp["price"]):
        return None
    dinh = [x for x in h if vt["i"] < x["i"] < vp["i"]]
    if len(dinh) < 2:
        return None
    co = (dinh[0]["price"] + dinh[-1]["price"]) / 2
    cao = co - dau["price"]
    if cao <= 0:
        return None
    if abs(vt["price"] - vp["price"]) / cao > CAN_XUNG:
        return None
    gia = c[-1]["c"]
    if gia <= co:
        return None
    return _mau("VAI_ĐẦU_VAI_NGƯỢC", "ĐẢO_CHIỀU", "LONG",
                vao=gia, stop=vp["price"], muc_tieu=co + cao,
                do_tin=1 - abs(vt["price"] - vp["price"]) / cao / CAN_XUNG * 0.5,
                coCau={"vaiTrái": vt["price"], "đầu": dau["price"],
                       "vaiPhải": vp["price"], "cổÁo": round(co, 2)},
                i=len(c) - 1)


# ── Nhóm TAM GIÁC & NÊM ───────────────────────────────────────────────────
def _hai_duong(s: dict) -> tuple | None:
    """Hai đường biên gần nhất: (đỉnh cũ, đỉnh mới, đáy cũ, đáy mới)."""
    h, l = s["highs"], s["lows"]
    if len(h) < 2 or len(l) < 2:
        return None
    return h[-2], h[-1], l[-2], l[-1]


def tam_giac_va_nem(c: Sequence[Candle], s: dict) -> dict | None:
    """Bốn mẫu hội tụ, phân biệt bằng DẤU của hai độ dốc.

        đỉnh ngang  + đáy lên    → tam giác TĂNG      (phá lên)
        đỉnh xuống  + đáy ngang  → tam giác GIẢM      (phá xuống)
        đỉnh xuống  + đáy lên    → tam giác CÂN       (theo hướng phá)
        đỉnh lên    + đáy lên    → NÊM TĂNG           (phá xuống — ngược trực giác)
        đỉnh xuống  + đáy xuống  → NÊM GIẢM           (phá lên)

    Nêm là chỗ dễ đọc sai nhất: giá vẫn đang tạo đỉnh cao hơn mà mẫu lại báo
    giảm. Lý do là bề rộng đang co — mỗi nhịp tăng yếu dần so với nhịp trước.
    """
    bo = _hai_duong(s)
    if not bo:
        return None
    h0, h1, l0, l1 = bo
    rong0, rong1 = h0["price"] - l0["price"], h1["price"] - l1["price"]
    if rong0 <= 0 or rong1 <= 0:
        return None
    hoi_tu = rong1 / rong0 <= HOI_TU

    dh = (h1["price"] - h0["price"]) / h0["price"]
    dl = (l1["price"] - l0["price"]) / l0["price"]
    gia = c[-1]["c"]
    cao = rong0

    ngang_h, ngang_l = abs(dh) < DOC, abs(dl) < DOC

    if ngang_h and dl > DOC:
        if gia <= h1["price"]:
            return None
        return _mau("TAM_GIÁC_TĂNG", "TIẾP_DIỄN", "LONG", gia, l1["price"],
                    h1["price"] + cao, 0.7 if hoi_tu else 0.55,
                    {"trần": h1["price"], "đáyLên": l1["price"], "hộiTụ": hoi_tu}, len(c) - 1)
    if ngang_l and dh < -DOC:
        if gia >= l1["price"]:
            return None
        return _mau("TAM_GIÁC_GIẢM", "TIẾP_DIỄN", "SHORT", gia, h1["price"],
                    l1["price"] - cao, 0.7 if hoi_tu else 0.55,
                    {"sàn": l1["price"], "đỉnhXuống": h1["price"], "hộiTụ": hoi_tu}, len(c) - 1)
    if dh < -DOC and dl > DOC and hoi_tu:
        if gia > h1["price"]:
            return _mau("TAM_GIÁC_CÂN", "TIẾP_DIỄN", "LONG", gia, l1["price"],
                        gia + cao, 0.6, {"phá": "lên", "cao": round(cao, 2)}, len(c) - 1)
        if gia < l1["price"]:
            return _mau("TAM_GIÁC_CÂN", "TIẾP_DIỄN", "SHORT", gia, h1["price"],
                        gia - cao, 0.6, {"phá": "xuống", "cao": round(cao, 2)}, len(c) - 1)
        return None
    if dh > DOC and dl > DOC and hoi_tu:
        if gia >= l1["price"]:
            return None
        return _mau("NÊM_TĂNG", "ĐẢO_CHIỀU", "SHORT", gia, h1["price"],
                    gia - cao, 0.6, {"cảHaiĐườngLên": True, "bềRộngCo": round(rong1 / rong0, 2)},
                    len(c) - 1)
    if dh < -DOC and dl < -DOC and hoi_tu:
        if gia <= h1["price"]:
            return None
        return _mau("NÊM_GIẢM", "ĐẢO_CHIỀU", "LONG", gia, l1["price"],
                    gia + cao, 0.6, {"cảHaiĐườngXuống": True, "bềRộngCo": round(rong1 / rong0, 2)},
                    len(c) - 1)
    return None


# ── Nhóm CỜ (cột cờ + đoạn nghỉ hẹp) ──────────────────────────────────────
def co(c: Sequence[Candle], s: dict, atr_now: float,
       cot_toi_thieu: float = 3.0, nghi: int = 8) -> dict | None:
    """Một nhịp mạnh (cột cờ) rồi nghỉ hẹp, phá tiếp theo hướng cột.

    Phân biệt với tam giác bằng CỘT: không có nhịp mạnh trước thì đoạn hẹp đó
    chỉ là thị trường đang chán, không phải cờ.
    """
    if len(c) < nghi + 12 or not atr_now:
        return None
    doan = c[-nghi:]
    cot = c[-(nghi + 10):-nghi]
    if not cot:
        return None
    di = cot[-1]["c"] - cot[0]["c"]
    if abs(di) < cot_toi_thieu * atr_now:
        return None
    tren = max(x["h"] for x in doan)
    duoi = min(x["l"] for x in doan)
    if (tren - duoi) > 1.5 * atr_now:      # đoạn nghỉ phải HẸP
        return None
    gia = c[-1]["c"]
    if di > 0 and gia > tren:
        return _mau("CỜ_TĂNG", "TIẾP_DIỄN", "LONG", gia, duoi, gia + abs(di),
                    0.65, {"cột": round(abs(di) / atr_now, 1), "nghỉ": nghi}, len(c) - 1)
    if di < 0 and gia < duoi:
        return _mau("CỜ_GIẢM", "TIẾP_DIỄN", "SHORT", gia, tren, gia - abs(di),
                    0.65, {"cột": round(abs(di) / atr_now, 1), "nghỉ": nghi}, len(c) - 1)
    return None


# ── Nhóm NÉN ở mức NẾN ────────────────────────────────────────────────────
def nen_trong(c: Sequence[Candle], atr_now: float) -> dict | None:
    """Nến trong (inside bar): cả biên độ nằm gọn trong nến trước.

    Không có hướng riêng — nó chỉ nói THỊ TRƯỜNG ĐANG NÉN. Hướng lấy theo nến
    mẹ, và stop đặt ở phía kia nến mẹ. Đây là mẫu duy nhất ở đây xác nhận NGAY
    tại nến hình thành, nên nó cũng là mẫu dễ bị nhiễu nhất.
    """
    if len(c) < 2 or not atr_now:
        return None
    me, con = c[-2], c[-1]
    if not (con["h"] <= me["h"] and con["l"] >= me["l"]):
        return None
    if (me["h"] - me["l"]) < 0.8 * atr_now:   # nến mẹ phải đủ lớn
        return None
    len_me = me["c"] >= me["o"]
    gia = con["c"]
    if len_me:
        return _mau("NẾN_TRONG_TĂNG", "NÉN", "LONG", gia, me["l"],
                    gia + (me["h"] - me["l"]), 0.45,
                    {"biênMẹ": [me["l"], me["h"]]}, len(c) - 1)
    return _mau("NẾN_TRONG_GIẢM", "NÉN", "SHORT", gia, me["h"],
                gia - (me["h"] - me["l"]), 0.45,
                {"biênMẹ": [me["l"], me["h"]]}, len(c) - 1)


def nen_trum(c: Sequence[Candle], atr_now: float) -> dict | None:
    """Nến trùm (outside bar): biên độ trùm cả nến trước, đóng về một phía."""
    if len(c) < 2 or not atr_now:
        return None
    truoc, nay = c[-2], c[-1]
    if not (nay["h"] > truoc["h"] and nay["l"] < truoc["l"]):
        return None
    than = nay["h"] - nay["l"]
    if than < 1.2 * atr_now:
        return None
    gan_dinh = (nay["c"] - nay["l"]) / than
    if gan_dinh >= 0.7:
        return _mau("NẾN_TRÙM_TĂNG", "ĐẢO_CHIỀU", "LONG", nay["c"], nay["l"],
                    nay["c"] + than, 0.5, {"đóngỞ": round(gan_dinh, 2)}, len(c) - 1)
    if gan_dinh <= 0.3:
        return _mau("NẾN_TRÙM_GIẢM", "ĐẢO_CHIỀU", "SHORT", nay["c"], nay["h"],
                    nay["c"] - than, 0.5, {"đóngỞ": round(gan_dinh, 2)}, len(c) - 1)
    return None


# ── Cốc tay cầm ───────────────────────────────────────────────────────────
def coc_tay_cam(c: Sequence[Candle], s: dict, atr_now: float) -> dict | None:
    """Đáy tròn rồi một nhịp chỉnh nông, phá miệng cốc.

    Điều kiện "tròn" ở đây đo bằng: đáy nằm gần GIỮA cốc, và hai vành cốc ngang
    nhau. Cốc mà đáy lệch hẳn về một bên là chữ V — thứ khác hẳn, và không nên
    gọi chung tên.
    """
    h, l = s["highs"], s["lows"]
    if len(h) < 2 or len(l) < 2 or not atr_now:
        return None
    vt, vp = h[-2], h[-1]
    day = [x for x in l if vt["i"] < x["i"] < vp["i"]]
    if not day:
        return None
    d = min(day, key=lambda x: x["price"])
    if _lech(vt["price"], vp["price"]) > NGANG:
        return None
    sau = (vt["price"] + vp["price"]) / 2 - d["price"]
    if sau < 2 * atr_now:
        return None
    # đáy phải nằm gần giữa: lệch tâm ≤ 30% chiều dài cốc
    dai = vp["i"] - vt["i"]
    if dai <= 0 or abs((d["i"] - vt["i"]) / dai - 0.5) > 0.3:
        return None
    tay = [x for x in c[vp["i"]:] if True]
    if len(tay) < 2:
        return None
    day_tay = min(x["l"] for x in tay)
    if (vp["price"] - day_tay) > sau * 0.5:    # tay cầm phải NÔNG
        return None
    gia = c[-1]["c"]
    if gia <= vp["price"]:
        return None
    return _mau("CỐC_TAY_CẦM", "TIẾP_DIỄN", "LONG", gia, day_tay,
                vp["price"] + sau, 0.65,
                {"miệng": round((vt["price"] + vp["price"]) / 2, 2),
                 "đáy": d["price"], "sâu": round(sau, 2)}, len(c) - 1)


# ── Cổng ──────────────────────────────────────────────────────────────────
BO_MAU = (
    ("hai_dinh", hai_dinh), ("hai_day", hai_day),
    ("vai_dau_vai", vai_dau_vai), ("vai_dau_vai_nguoc", vai_dau_vai_nguoc),
    ("tam_giac_va_nem", tam_giac_va_nem), ("coc_tay_cam", coc_tay_cam),
)



# Đếm lần một BỘ DÒ ném lỗi. Bộ dò hỏng cho ra 0 lần xuất hiện, và "0 lần" đọc
# y hệt "mẫu này hiếm" — bảng vẫn đủ dòng, vẫn có cỡ mẫu, vẫn xanh.
LOI_DO: dict[str, int] = {}
LOI_DO_VIDU: dict[str, str] = {}
def nhan_dien(c: Sequence[Candle], lr: int = 2) -> list[dict]:
    """Mọi mẫu ĐÃ XÁC NHẬN tại nến cuối của cửa sổ `c`.

    Trả về danh sách vì nhiều mẫu có thể cùng xác nhận một lúc — và chuyện đó
    tự nó là thông tin: hai mẫu cùng hướng là một kiểu, hai mẫu ngược hướng là
    một kiểu hẳn khác, và gộp lại thành "một tín hiệu" là bịa.
    """
    if len(c) < 30:
        return []
    s = swings(c, lr)
    a = _atr(c, 14)
    atr_now = a[-1] if a and a[-1] else None
    ra = []

    def _thu(ten, goi):
        """Gọi một bộ dò, ĐẾM lần hỏng thay vì nuốt im lặng.

        Bộ dò hỏng cho ra 0 lần xuất hiện, và "0 lần" đọc y hệt "mẫu này hiếm".
        Bảng mẫu giá khi đó vẫn đủ 14 dòng, vẫn có cỡ mẫu, vẫn xanh — chỉ một
        dòng nói dối. Với 22.997 lần xuất hiện trên 15 chợ, đó là nguồn bằng
        chứng lớn thứ hai của cả hệ.

        Vẫn nuốt lỗi để một bộ dò hỏng không giết cả lượt quét — nhưng đếm vào
        `LOI_DO`, và `do-mau-gia.py` in ra ở cuối bảng.
        """
        try:
            return goi()
        except (KeyError, IndexError, TypeError, ZeroDivisionError) as e:
            LOI_DO[ten] = LOI_DO.get(ten, 0) + 1
            LOI_DO_VIDU.setdefault(ten, f"{type(e).__name__}: {e}")
            return None

    for _ten, ham in BO_MAU:
        m = _thu(_ten, (lambda h=ham: h(c, s, atr_now) if h in (coc_tay_cam,)
                        else h(c, s)))
        if m:
            ra.append(m)
    for ham in (co,):
        m = _thu(ham.__name__, lambda h=ham: h(c, s, atr_now))
        if m:
            ra.append(m)
    for ham in (nen_trong, nen_trum):
        m = _thu(ham.__name__, lambda h=ham: h(c, atr_now))
        if m:
            ra.append(m)
    return ra


def tom_tat(ds: list[dict]) -> dict:
    """Gói gọn cho prompt và cho bảng: có mẫu nào, có mâu thuẫn nhau không."""
    if not ds:
        return {"co": False, "so": 0, "mau": [], "mauThuan": False}
    huong = {m["huong"] for m in ds}
    return {
        "co": True, "so": len(ds),
        "mau": [{"ten": m["ten"], "loai": m["loai"], "huong": m["huong"],
                 "rr": m["rr"], "doTin": m["doTin"]} for m in ds],
        # Hai mẫu ngược hướng cùng xác nhận KHÔNG triệt tiêu nhau thành "trung
        # tính" — nó có nghĩa là hình học đang mâu thuẫn, và đó là lúc phải đứng
        # ngoài chứ không phải lúc lấy trung bình.
        "mauThuan": len(huong) > 1,
    }
