"""SỔ GIẢ THUYẾT — khai TRƯỚC khi đo, chốt SAU khi đo, và giữ cả cái sai.

Hai chuyện khác nhau mà kho `phat-hien.jsonl` không làm được, vì nó là ẢNH CHỤP
trạng thái hiện tại và bị ghi đè mỗi lần chưng cất:

**1. Không có gì ngăn việc dời cột mốc.** Tôi hình thành một giả thuyết, chạy
phép đo, rồi viết kết luận. Không ai — kể cả tôi — kiểm được là kết luận ấy có
đúng thứ tôi định tìm hay không, hay tôi đã lặng lẽ đổi tiêu chí sau khi thấy số.
Cách chữa mượn từ thử nghiệm lâm sàng: **ghi dự đoán và ngưỡng TRƯỚC**, chốt
niêm, rồi mới đo.

**2. Kết quả ÂM bị vứt đi.** Lò chưng cất chỉ giữ cái đang đúng. Mọi thứ đã thử
và thất bại biến mất, nên lượt sau có thể thử lại đúng cái đó. Kết quả âm là thứ
đắt nhất đã mua được — nó tốn đúng bằng kết quả dương mà không ai cất.

CÁCH CHỐNG DỜI CỘT MỐC

`chot()` **không sửa** bản khai. Nó ghi một bản ghi THỨ HAI trỏ về bản đầu. Hai
bản nằm cạnh nhau trong sổ append-only, nên đọc lại là thấy ngay dự đoán lúc
chưa biết gì và kết quả lúc đã biết. Muốn gian phải sửa file bằng tay, và sửa
file bằng tay thì `git` nhìn thấy.

Phán quyết do **hàm thuần** tính từ (ngưỡng đã khai, số đo được) — không có chỗ
nào cho một câu chữ khéo léo chen vào giữa.

    khai()  → ghi dự đoán + cách đo + ngưỡng, trước khi chạy
    chot()  → ghi số đo được, máy tự so với ngưỡng
    tra()   → «cái này đã thử chưa?» — tra TRƯỚC khi tốn công thử lại
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json

from . import store

# Toán tử cho phép trong ngưỡng. Cố ý ít: ngưỡng phải đơn giản đến mức không
# cãi được. Cần một điều kiện phức tạp thì tách thành hai giả thuyết.
TOAN_TU = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
}


def _gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _dau(d: dict) -> str:
    """Vân tay của bản khai — để chốt không thể trỏ nhầm sang bản đã sửa."""
    loi = json.dumps({k: d[k] for k in ("ma", "cauHoi", "duDoan", "cachDo", "nguong")},
                     ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(loi.encode()).hexdigest()[:16]


def khai(ma: str, cau_hoi: str, du_doan: str, cach_do: str,
         nguong: dict, boi_canh: dict | None = None) -> dict:
    """Khai một giả thuyết TRƯỚC khi đo.

    `nguong` phải máy đọc được:

        {"truong": "kyVongR", "toanTu": ">", "giaTri": 0.0, "mauToiThieu": 20}

    Viết ngưỡng bằng câu chữ là để dành chỗ cho việc diễn giải lại sau khi thấy
    số — đúng thứ sổ này sinh ra để chặn.
    """
    if nguong.get("toanTu") not in TOAN_TU:
        return {"ok": False, "viSao": f"toán tử phải thuộc {sorted(TOAN_TU)}"}
    for k in ("truong", "giaTri", "mauToiThieu"):
        if k not in nguong:
            return {"ok": False, "viSao": f"ngưỡng thiếu «{k}»"}
    if any(x["ma"] == ma and x["loai"] == "khai" for x in store.read_all(store.GIA_THUYET)):
        return {"ok": False, "viSao": f"mã «{ma}» đã được khai — dùng mã khác hoặc chốt cái cũ"}

    b = {"loai": "khai", "ma": ma, "luc": _gio(), "cauHoi": cau_hoi,
         "duDoan": du_doan, "cachDo": cach_do, "nguong": nguong,
         "boiCanh": boi_canh or {}}
    b["dau"] = _dau(b)
    store.append(store.GIA_THUYET, b)
    return {"ok": True, "banKhai": b}


def _phan_quyet(nguong: dict, do_duoc: dict) -> tuple[str, str]:
    """Hàm THUẦN. Không đọc gì ngoài hai tham số, không ghi gì."""
    mau = do_duoc.get("mau")
    if not isinstance(mau, (int, float)) or mau < nguong["mauToiThieu"]:
        return ("KHÔNG_KẾT_LUẬN",
                f"mẫu {mau} < ngưỡng {nguong['mauToiThieu']} đã khai — chưa đủ để nói gì. "
                f"Đây KHÔNG phải bác bỏ: chưa đo đủ và đo ra sai là hai chuyện.")
    x = do_duoc.get(nguong["truong"])
    if not isinstance(x, (int, float)):
        return ("KHÔNG_KẾT_LUẬN",
                f"không đọc được trường «{nguong['truong']}» trong số đo")
    dat = TOAN_TU[nguong["toanTu"]](x, nguong["giaTri"])
    mo_ta = f"{nguong['truong']}={x} {nguong['toanTu']} {nguong['giaTri']} · mẫu {mau}"
    return ("XÁC_NHẬN" if dat else "BÁC_BỎ", mo_ta)


def chot(ma: str, do_duoc: dict, ghi_chu: str = "") -> dict:
    """Chốt một giả thuyết bằng số đo được. KHÔNG sửa bản khai."""
    ds = store.read_all(store.GIA_THUYET)
    khai_b = next((x for x in ds if x["ma"] == ma and x["loai"] == "khai"), None)
    if khai_b is None:
        return {"ok": False, "viSao": f"chưa khai giả thuyết «{ma}» — không chốt được cái "
                                      f"chưa có dự đoán, vì khi đó mọi kết quả đều 'đúng'"}
    if any(x["ma"] == ma and x["loai"] == "chot" for x in ds):
        return {"ok": False, "viSao": f"«{ma}» đã chốt rồi — chốt lại là dời cột mốc"}
    if _dau(khai_b) != khai_b.get("dau"):
        return {"ok": False, "viSao": f"bản khai «{ma}» đã bị sửa sau khi ghi (vân tay lệch)"}

    pq, mo_ta = _phan_quyet(khai_b["nguong"], do_duoc)
    b = {"loai": "chot", "ma": ma, "luc": _gio(), "dauBanKhai": khai_b["dau"],
         "doDuoc": do_duoc, "phanQuyet": pq, "moTa": mo_ta, "ghiChu": ghi_chu,
         "duDoanCu": khai_b["duDoan"]}
    store.append(store.GIA_THUYET, b)
    return {"ok": True, "phanQuyet": pq, "moTa": mo_ta, "banChot": b}


def doc() -> list[dict]:
    """Ghép khai với chốt thành từng giả thuyết trọn vẹn."""
    ds = store.read_all(store.GIA_THUYET)
    khai_ds = {x["ma"]: x for x in ds if x["loai"] == "khai"}
    chot_ds = {x["ma"]: x for x in ds if x["loai"] == "chot"}
    ra = []
    for ma, k in khai_ds.items():
        c = chot_ds.get(ma)
        ra.append({**k, "daChot": c is not None,
                   "phanQuyet": (c or {}).get("phanQuyet"),
                   "doDuoc": (c or {}).get("doDuoc"),
                   "moTa": (c or {}).get("moTa"),
                   "chotLuc": (c or {}).get("luc")})
    return ra


def tra(tu_khoa: str = "") -> list[dict]:
    """«Cái này đã thử chưa?» — hàm đáng gọi NHẤT trong module này.

    Gọi nó trước khi tốn công dựng một phép đo. Kết quả ÂM đã lưu là thứ tiết
    kiệm được nhiều thời gian nhất, và cũng là thứ duy nhất trong nghề này mà
    không ai chịu cất.
    """
    t = (tu_khoa or "").lower()
    ra = [g for g in doc()
          if not t or t in g["ma"].lower() or t in g["cauHoi"].lower()
          or t in (g.get("duDoan") or "").lower()]
    return sorted(ra, key=lambda g: g["luc"], reverse=True)


def tom_tat() -> dict:
    ds = doc()
    dem: dict[str, int] = {}
    for g in ds:
        k = g["phanQuyet"] or "ĐANG_MỞ"
        dem[k] = dem.get(k, 0) + 1
    return {"tong": len(ds), "theoPhanQuyet": dem,
            "dangMo": [g["ma"] for g in ds if not g["daChot"]]}
