"""Đúc bài học từ lịch sử chạy lại, để trí nhớ ngữ nghĩa không phải chờ hàng tháng.

Vấn đề nó giải: bài học chỉ sinh ra khi một lệnh THẬT đóng lại. Mà ở chế độ
RANGE với sàn spot chỉ-LONG, số lệnh thật có thể là **không** — đo tại đây: 38
luận điểm liên tiếp đều NO_TRADE, 0 bài học, trong khi phòng huấn luyện chạy lại
133 lệnh trong 0,01 giây. Trí nhớ đứng im trong khi dữ liệu thì có sẵn.

**Ranh giới quan trọng nhất của file này: bài học chạy lại KHÔNG được trộn vào
bài học thật.** Chúng ở file riêng, mang cờ `tuChayLai` riêng, và khi vào prompt
thì được dán nhãn rõ. Trộn vào là lặp lại đúng cái lỗi vừa dọn hôm nay — sổ giao
dịch bị 14 lệnh giả của selftest làm sai lệch mà không ai phân biệt được.

Chúng khác nhau ở chỗ nào, và vì sao phải nói ra:

    lệnh thật      có trượt giá thật, có khớp một phần, có nhảy giá qua stop
    lệnh chạy lại  khớp đúng giá đặt cộng một khoản trượt cố định

Nên bài học chạy lại đáng tin về **cấu trúc** ("chế độ này lỗ đều", "chốt non")
và KHÔNG đáng tin về **độ lớn**. Nhãn ở prompt nói đúng điều đó.
"""
from __future__ import annotations

import datetime as _dt
from collections import defaultdict
from typing import Any

from . import store
from .bus import bus

NGUON = "chay-lai"


def _phan_loai(t: dict, nguong_r: float) -> tuple[str, bool, str]:
    """(phân loại, luận điểm có sai không, câu bài học).

    Giữ đúng cách phân loại của hậu kiểm thật: **tách quyết định khỏi kết quả**.
    Một lệnh dính stop theo đúng quy trình vẫn là quyết định tốt; học theo tiền
    lãi/lỗ thay vì theo chất lượng quyết định thì cuối cùng sẽ học ra cờ bạc.
    """
    r = t.get("R") or 0
    thang = r > 0
    ly_do = t.get("lyDo")

    if ly_do == "TP":
        return ("GOOD_TRADE_GOOD_OUTCOME", False,
                f"Chạy tới mục tiêu sau {t['soNenGiu']} nến ở chế độ {t['regime']}. "
                f"Thu {r:+.2f}R.")
    if ly_do == "SL":
        return ("GOOD_TRADE_BAD_OUTCOME", False,
                f"Dính stop sau {t['soNenGiu']} nến ở chế độ {t['regime']} ({r:+.2f}R). "
                f"Nằm trong biên độ bình thường — một lệnh thua không phải một quyết định sai.")
    # Hết hạn giữ mà chưa chạm đâu: đây mới là dấu hiệu setup có vấn đề, vì mục
    # tiêu đặt xa hơn tầm với của biến động trong khoảng thời gian đó.
    return ("QUESTIONABLE_SETUP", True,
            f"Hết {t['soNenGiu']} nến mà không chạm SL lẫn TP ở chế độ {t['regime']} "
            f"({r:+.2f}R). Mục tiêu đang đặt xa hơn thứ biến động cho phép.")


def duc(kq: dict, *, tham: dict | None = None, toi_da: int = 400) -> dict:
    """Biến kết quả `huanluyen.chay_lai()` thành bài học, ghi vào kho RIÊNG.

    Ghi ĐÈ chứ không nối thêm: chạy lại cùng một đoạn dữ liệu hai lần thì bài
    học thứ hai không phải kiến thức mới, chỉ là bản sao. Nối thêm là tự nhân
    bản trí nhớ, và `recall()` sẽ tưởng một mẫu lặp lại 5 lần là bằng chứng mạnh
    trong khi nó chỉ là một lần bấm nút 5 lượt.
    """
    lenh = kq.get("lenh") or []
    if not lenh:
        return {"so": 0, "viSao": "lượt chạy lại không có lệnh nào"}

    r = kq["thongKe"]
    luc = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    ra: list[dict] = []

    for t in lenh[-toi_da:]:
        pl, sai, cau = _phan_loai(t, r.get("kyVongR") or 0)
        ra.append({
            "at": luc, "tuChayLai": True, "nguon": NGUON,
            "tradeId": f"cl_{t['i']}", "symbol": kq.get("symbol"),
            "luc": t["t"], "regime": t["regime"], "regimeKey": t["regimeKey"],
            "side": t["side"], "pnl": t["pnl"], "rMultiple": t["R"],
            "exitReason": t["lyDo"], "strategy": "MOCK_RULES_V1",
            "soNenGiu": t["soNenGiu"],
            "regime_appropriate": t["regime"] in ("TREND_UP", "TREND_DOWN"),
            "entry_valid": True, "size_valid": True, "stop_placement_valid": True,
            "thesis_was_wrong": sai,
            "classification": pl,
            "lesson": cau,
            "change_strategy": False,   # một lệnh không bao giờ đủ cớ — xem `gop()`
            "confidence_in_lesson": 0.2,
            "tham": tham or {},
        })

    store.write_all(store.LESSONS_CHAY_LAI, ra)
    gop = _gop(ra, kq)
    if gop:
        store.append(store.LESSONS_CHAY_LAI, gop)
        ra.append(gop)

    bus.emit("memory", "duc-bai-hoc-lich-su",
             f"đúc {len(ra)} bài học từ {len(lenh)} lệnh chạy lại"
             + (" · kèm 1 kết luận theo mẫu lặp lại" if gop else ""))
    return {"so": len(ra), "coKetLuan": bool(gop)}


def _gop(ra: list[dict], kq: dict) -> dict | None:
    """Một bài học DUY NHẤT rút từ mẫu lặp lại — thứ được phép đòi đổi chiến lược.

    Đây là chỗ khác biệt thật giữa hậu kiểm từng lệnh và học từ lịch sử: một
    lệnh thua chẳng nói lên gì, nhưng "chế độ này lỗ đều qua 53 lệnh" thì có.
    Chỉ bài học loại này mới được đặt `change_strategy = True`.
    """
    theo = kq.get("theoRegime") or {}
    du = [(k, v) for k, v in theo.items() if v["so"] >= 10]
    if not du:
        return None
    du.sort(key=lambda x: x[1]["trungBinhR"])
    te, ten_te = du[0][1], du[0][0]
    if te["trungBinhR"] >= 0:
        return None

    return {
        "at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "tuChayLai": True, "nguon": NGUON, "tradeId": "cl_ket_luan",
        "regime": ten_te.split("|")[0], "regimeKey": ten_te,
        "side": None, "pnl": None, "rMultiple": round(te["trungBinhR"], 3),
        "exitReason": None, "strategy": "MOCK_RULES_V1",
        "regime_appropriate": False, "entry_valid": True, "size_valid": True,
        "stop_placement_valid": True, "thesis_was_wrong": True,
        "classification": "REPEATED_PATTERN",
        "lesson": (f"Chế độ {ten_te} lỗ đều qua {te['so']} lệnh chạy lại: trung bình "
                   f"{te['trungBinhR']:+.3f}R, thắng {te['tyLeThang']}%. Đây là MẪU LẶP "
                   f"LẠI, không phải một lệnh xui — đứng ngoài chế độ này là cải thiện "
                   f"rẻ nhất, vì nó không cần thêm tín hiệu nào mới."),
        "change_strategy": True,
        "confidence_in_lesson": 0.6,
    }


def thong_ke() -> dict:
    """Kho bài học chạy lại đang có gì."""
    ds = store.read_all(store.LESSONS_CHAY_LAI)
    theo = defaultdict(int)
    for l in ds:
        theo[l.get("classification", "?")] += 1
    doi = [l for l in ds if l.get("change_strategy")]
    return {
        "so": len(ds), "theoPhanLoai": dict(theo),
        "soDoiChienLuoc": len(doi),
        "ketLuan": [l["lesson"] for l in doi],
        "luc": ds[-1]["at"] if ds else None,
    }


def xoa() -> int:
    """Dọn kho bài học chạy lại. Không đụng bài học thật."""
    n = len(store.read_all(store.LESSONS_CHAY_LAI))
    store.write_all(store.LESSONS_CHAY_LAI, [])
    bus.emit("memory", "xoa-bai-hoc-lich-su", f"đã dọn {n} bài học chạy lại")
    return n
