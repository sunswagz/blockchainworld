"""CHAMPION / CHALLENGER — chiến lược mới phải THẮNG bản đang chạy mới được lên.

Không có tầng này thì "cải tiến" là một từ không kiểm chứng được: đổi tham số,
thấy con số đẹp hơn, áp dụng. Mà con số đẹp hơn thì **luôn** tìm được nếu dò đủ
lâu — đó là cực trị của nhiễu, không phải lợi thế. Đường cong sát thủ bắt đầu
đúng từ chỗ đó, và nó không bao giờ trông giống một sai lầm khi đang xảy ra.

Cửa duyệt ở đây là một hàm thuần, cố tình viết cứng:

    1. Đủ mẫu NGOÀI mẫu     — dưới ngần này lệnh thì mọi con số là nhiễu
    2. Kỳ vọng ngoài mẫu > champion   — so trên CÙNG đoạn dữ liệu
    3. Kỳ vọng ngoài mẫu phải DƯƠNG   — thắng một champion đang lỗ vẫn là lỗ
    4. Khớp trội dưới ngưỡng          — đẹp trong mẫu rồi rơi ngoài mẫu là ảo giác
    5. Sụt giảm không tệ hơn nhiều    — kỳ vọng nhỉnh hơn mà chịu đau gấp đôi
                                         thì đó không phải cải tiến

Điều quan trọng nhất về cửa này: **nó chặn được cả những thứ tôi tự đề xuất.**
Chiến lược biên `MOCK_RANGE_V1` vào hệ thống với tư cách challenger và phải đi
qua đúng năm điều kiện trên như mọi challenger khác.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

from . import store
from .config import CONFIG
from .brain import BO_LUAT
from .bus import bus

SO = "chien-luoc.json"

# Ngưỡng của cửa duyệt. Để ở đây, tường minh, chứ không rải trong thân hàm —
# nới một cái trong này là một quyết định phải nhìn thấy được trong git diff.
CUA = {
    "toiThieuLenhNgoaiMau": 20,
    "khopTroiToiDa": 0.35,        # R
    "sutGiamXauHonToiDa": 1.5,    # lần
    "vuotToiThieu": 0.05,         # R — nhỉnh hơn dưới mức này coi như hoà
}


def _moi() -> dict:
    return {
        "champion": {
            "ma": "MOCK_RULES_V1", "ten": "Thuận xu hướng",
            "tham": {}, "phienBan": 1,
            "tuLuc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "ketQua": None,
        },
        "challengers": [],
        "lichSu": [],
    }


def doc() -> dict:
    d = store.read_json(SO, None)
    return d if d else _moi()


def ghi(d: dict) -> dict:
    # Sổ tự đóng dấu lần ghi cuối. Bàn giao đo tuổi kho bằng mtime của file, mà
    # mtime nói "file bị chạm", không nói "số bên trong được đo lại". Một lượt
    # đấu hỏng nửa chừng vẫn chạm file và làm sổ trông tươi.
    d["luc"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    store.write_json(SO, d)
    return d


def de_xuat(ma: str, ten: str, tham: dict | None = None, ghi_chu: str = "") -> dict:
    """Đăng ký một challenger. Chưa chạy gì — chỉ ghi ý định."""
    if ma not in BO_LUAT:
        return {"ok": False, "viSao": f"không có bộ luật «{ma}». Có: {list(BO_LUAT)}"}
    d = doc()
    khoa = f"{ma}#{_ky(tham or {})}"
    if any(c["khoa"] == khoa for c in d["challengers"]):
        return {"ok": False, "viSao": "challenger này đã có trong sổ"}
    d["challengers"].append({
        "khoa": khoa, "ma": ma, "ten": ten, "tham": tham or {},
        "ghiChu": ghi_chu, "trangThai": "chưa đo",
        "deXuatLuc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "ketQua": None, "phanQuyet": None,
    })
    ghi(d)
    bus.emit("hoc", "challenger-moi", f"đăng ký challenger «{ten}» ({ma})")
    return {"ok": True, "khoa": khoa}


def _ky(tham: dict) -> str:
    return ",".join(f"{k}={tham[k]}" for k in sorted(tham)) or "mặc-định"


def phan_quyet(cha: dict | None, thu: dict) -> dict:
    """Cửa duyệt. Hàm THUẦN — đưa vào hai bộ thống kê ngoài mẫu, trả phán quyết.

    Thuần để kiểm được bằng số bịa, không cần chạy cả cỗ máy. Cửa duyệt là chỗ
    duy nhất quyết định cái gì được chạy bằng tiền, nên nó phải là chỗ dễ kiểm
    nhất chứ không phải chỗ khó nhất.
    """
    ly_do: list[str] = []
    n = thu.get("so") or 0
    kv = thu.get("kyVongR")
    kv_cha = (cha or {}).get("kyVongR")

    if n < CUA["toiThieuLenhNgoaiMau"]:
        ly_do.append(f"chỉ {n} lệnh ngoài mẫu, cần ≥{CUA['toiThieuLenhNgoaiMau']} — "
                     f"dưới ngần này mọi con số là nhiễu")
    if kv is None:
        ly_do.append("không có kỳ vọng ngoài mẫu để so")
    else:
        if kv <= 0:
            ly_do.append(f"kỳ vọng ngoài mẫu {kv:+.3f}R không dương — "
                         f"thắng một champion đang lỗ thì vẫn là lỗ")
        if kv_cha is not None and kv < kv_cha + CUA["vuotToiThieu"]:
            ly_do.append(f"kỳ vọng {kv:+.3f}R không vượt champion {kv_cha:+.3f}R "
                         f"quá {CUA['vuotToiThieu']}R")

    kt = thu.get("khopTroi")
    if kt is not None and kt > CUA["khopTroiToiDa"]:
        ly_do.append(f"khớp trội {kt:.3f}R > {CUA['khopTroiToiDa']}R — "
                     f"phần lớn cái đẹp nằm trong mẫu, không mang ra ngoài được")

    sg, sg_cha = thu.get("sutGiamToiDaPct"), (cha or {}).get("sutGiamToiDaPct")
    if sg is not None and sg_cha not in (None, 0) and sg > sg_cha * CUA["sutGiamXauHonToiDa"]:
        ly_do.append(f"sụt giảm {sg:.1f}% so với {sg_cha:.1f}% của champion — "
                     f"đau hơn {CUA['sutGiamXauHonToiDa']}× thì không phải cải tiến")

    return {
        "qua": not ly_do,
        "lyDo": ly_do,
        "tomTat": ("đủ điều kiện lên champion"
                   if not ly_do else f"bị chặn bởi {len(ly_do)} điều kiện"),
        "nguong": dict(CUA),
    }


def danh_gia(khoa: str, chay: Any) -> dict:
    """Đo challenger, so với champion trên CÙNG đoạn ngoài mẫu, rồi phán quyết.

    `chay(ma, tham)` là hàm gọi ngược do tầng trên đưa vào — nó biết cách nạp nến
    và gọi `huanluyen`. Để `chien_luoc.py` không phụ thuộc vào `huanluyen.py`,
    nhờ vậy cửa duyệt kiểm được độc lập.
    """
    d = doc()
    c = next((x for x in d["challengers"] if x["khoa"] == khoa), None)
    if not c:
        return {"ok": False, "viSao": "không có challenger này"}

    cha_tk = chay(d["champion"]["ma"], d["champion"].get("tham") or {})
    thu_tk = chay(c["ma"], c.get("tham") or {})

    # CHỢ mà con số này được đo trên. Lần thứ tư trong hệ này một kho đo ghi kết
    # quả mà không ghi bối cảnh: cầu dao, bài học chạy lại, bảng mẫu giá, và giờ
    # là sổ chiến lược. Champion ghi "+0,032R qua 26 lệnh" — đúng cho BTCUSDT:4h
    # và vô nghĩa ở mọi chợ khác, nhưng không có gì trong bản ghi nói ra điều đó.
    cho = f"{CONFIG['symbol']}:{CONFIG['timeframes']['primary']}"
    for tk in (cha_tk, thu_tk):
        if isinstance(tk, dict):
            tk.setdefault("cho", cho)
            tk.setdefault("khung", CONFIG["timeframes"]["primary"])

    pq = phan_quyet(cha_tk, thu_tk)
    c.update({"trangThai": "đã đo", "ketQua": thu_tk, "phanQuyet": pq,
              "doLuc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")})
    d["champion"]["ketQua"] = cha_tk
    ghi(d)
    bus.emit("hoc", "danh-gia-challenger",
             f"«{c['ten']}»: {pq['tomTat']}"
             + (f" · ngoài mẫu {thu_tk.get('kyVongR'):+.3f}R" if thu_tk.get("kyVongR") is not None else ""))
    return {"ok": True, "champion": cha_tk, "challenger": thu_tk, "phanQuyet": pq}


def duyet(khoa: str) -> dict:
    """Cho challenger lên thay champion. CHỈ khi cửa duyệt đã cho qua.

    Không có đường vòng: không tham số `--force`, không cờ bỏ qua. Muốn lên mà
    chưa qua cửa thì phải sửa ngưỡng trong `CUA`, và việc đó để lại dấu vết
    trong git.
    """
    d = doc()
    c = next((x for x in d["challengers"] if x["khoa"] == khoa), None)
    if not c:
        return {"ok": False, "viSao": "không có challenger này"}
    if not c.get("phanQuyet"):
        return {"ok": False, "viSao": "chưa đo — chạy đánh giá trước"}
    if not c["phanQuyet"]["qua"]:
        return {"ok": False, "viSao": "chưa qua cửa duyệt",
                "lyDo": c["phanQuyet"]["lyDo"]}

    cu = dict(d["champion"])
    d["lichSu"].append({
        "luc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "thay": cu["ma"], "bang": c["ma"], "tham": c["tham"],
        "vi": c["phanQuyet"]["tomTat"], "ketQua": c["ketQua"],
    })
    d["champion"] = {
        "ma": c["ma"], "ten": c["ten"], "tham": c["tham"],
        "phienBan": cu.get("phienBan", 1) + 1,
        "tuLuc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "ketQua": c["ketQua"],
    }
    d["challengers"] = [x for x in d["challengers"] if x["khoa"] != khoa]
    ghi(d)
    bus.log("hoc", "len-champion",
            f"«{c['ten']}» thay «{cu['ten']}» làm champion (bản {d['champion']['phienBan']})")
    return {"ok": True, "champion": d["champion"]}


def go(khoa: str) -> dict:
    d = doc()
    n = len(d["challengers"])
    d["challengers"] = [x for x in d["challengers"] if x["khoa"] != khoa]
    ghi(d)
    return {"ok": len(d["challengers"]) < n}
