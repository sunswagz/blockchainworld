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


# Dấu hiệu một giả thuyết đo trên LỆNH THẬT. Cố ý hẹp.
#
# Cảnh báo "bao lâu mới chốt được" chỉ đúng cho lệnh thật; phép chạy lại sinh
# 200 lệnh trong hai mươi phút. Bản đầu không phân biệt, nên nó nổ ngay ở một
# giả thuyết đo bằng chạy lại và doạ "cần 56 NGÀY" — sai hoàn toàn.
#
# Báo động sai không rẻ hơn im lặng: nó dạy người ta bỏ qua báo động. Nên luật
# là CHỈ kêu khi thấy dấu hiệu rõ ràng của lệnh thật. Bỏ sót thì chỉ mất một
# lời nhắc; kêu nhầm thì mất chính cái cảnh báo.
DAU_LENH_THAT = ("lệnh thật", "lệnh THẬT", "lenh that", "journal.performance",
                 "sổ lệnh", "byStrategy", "expectancyUsd")


def _do_tren_lenh_that(cach_do: str) -> bool:
    t = (cach_do or "").lower()
    if any(x in t for x in ("chạy lại", "chay lai", "ngoài mẫu", "ngoai mau",
                            "dau-chien-luoc", "backtest")):
        return False
    return any(x.lower() in t for x in DAU_LENH_THAT)


def _bao_lau(mau_can: int) -> str | None:
    """Ở nhịp vào lệnh hiện tại, gom đủ ngần này lệnh THẬT mất bao lâu.

    Kỷ luật khai-trước của sổ này hợp với phép chạy lại — đo xong trong một
    buổi — và hợp rất tệ với lệnh thật. `doi-khung-sang-4h` cần 20 lệnh và thu
    được 2 trong 1,5 ngày; ở nhịp đó nó cần hàng tháng, mà cấu hình sẽ đổi
    trước khi nó chốt được. Khi ấy bản khai không sai — nó chỉ vĩnh viễn treo,
    và một giả thuyết treo trông y hệt một giả thuyết đang tiến triển.

    Không CHẶN việc khai: có những câu chỉ lệnh thật trả lời được, và chậm vẫn
    hơn không đo. Chỉ nói ra cái giá, lúc còn kịp đổi cách đo.

    Trả None khi chưa đủ lịch sử để ước — thà im còn hơn đưa một con số bịa.
    """
    import datetime as _d

    # Nhịp GẦN ĐÂY, không phải nhịp cả đời sổ.
    #
    # Bản đầu chia tổng số lệnh cho tổng số ngày: 41 lệnh / 11 ngày = 3,7
    # lệnh/ngày, nên "20 lệnh nữa" ra 5 ngày và cảnh báo không bao giờ nổ. Nhưng
    # phần lớn 41 lệnh ấy đến từ hồi bot còn chạy luật thuần trên 1h và vào lệnh
    # liên tục; nhịp bây giờ là ~1,4. Đúng dạng lỗi đã ghi trong sổ: ngưỡng đo
    # trên tập trôi thì luật chết lặng, và "chưa từng thấy vấn đề" đọc giống hệt
    # "không có vấn đề".
    tat = [t for t in store.read_all(store.TRADES) if t.get("openedAt")]
    if len(tat) < 5:
        return None
    ds = sorted(tat, key=lambda t: t["openedAt"])[-10:]
    moc = [t["openedAt"] for t in ds]
    try:
        dau = _d.datetime.fromisoformat(min(moc))
        cuoi = _d.datetime.fromisoformat(max(moc))
    except ValueError:
        return None
    ngay = (cuoi - dau).total_seconds() / 86400
    if ngay < 1:
        return None
    nhip = len(ds) / ngay
    if nhip <= 0:
        return None
    can = mau_can / nhip
    if can < 14:
        return None
    return (f"cỡ mẫu {mau_can} lệnh THẬT ở nhịp hiện tại ({nhip:.2f} lệnh/ngày "
            f"qua {len(ds)} lệnh gần nhất) cần khoảng {can:.0f} NGÀY. Cấu hình nhiều khả "
            f"năng đổi trước lúc đó, và bản khai sẽ treo vĩnh viễn — treo thì "
            f"trông y hệt đang tiến triển. Cân nhắc một cách đo bằng chạy lại.")

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
    # Cảnh báo tính SAU khi đã ghi: nó không phải điều kiện, chỉ là cái giá.
    return {"ok": True, "banKhai": b,
            "canhBao": (_bao_lau(nguong["mauToiThieu"])
                        if _do_tren_lenh_that(cach_do) else None)}


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

    # THIẾU khoá «mau» là lỗi người gọi, không phải một phán quyết.
    #
    # `_phan_quyet` xử lý mọi thứ không phải số thành KHÔNG_KẾT_LUẬN, nên một
    # lời gọi gõ nhầm tên khoá cho ra "mẫu None < ngưỡng 30 — chưa đủ để nói
    # gì". Câu đó đọc y hệt một phép đo thật sự thiếu mẫu, và vì sổ append-only
    # từ chối chốt lại, bản ghi sai ấy nằm lại VĨNH VIỄN. Đã xảy ra một lần.
    #
    # Phân biệt: «mau» vắng mặt ⇒ từ chối, bảo người gọi đưa vào. «mau» có mặt
    # mà nhỏ ⇒ để `_phan_quyet` phán KHÔNG_KẾT_LUẬN, vì đó là kết quả thật.
    if "mau" not in do_duoc:
        return {"ok": False,
                "viSao": ("số đo thiếu khoá «mau» (cỡ mẫu). Không chốt được: thiếu "
                          "khoá và mẫu quá nhỏ sẽ cho cùng một phán quyết, mà sổ "
                          "append-only không cho chốt lại — bản ghi sai sẽ nằm lại "
                          f"vĩnh viễn. Khoá đã nhận: {sorted(do_duoc)}")}

    pq, mo_ta = _phan_quyet(khai_b["nguong"], do_duoc)
    b = {"loai": "chot", "ma": ma, "luc": _gio(), "dauBanKhai": khai_b["dau"],
         "doDuoc": do_duoc, "phanQuyet": pq, "moTa": mo_ta, "ghiChu": ghi_chu,
         "duDoanCu": khai_b["duDoan"]}
    store.append(store.GIA_THUYET, b)
    return {"ok": True, "phanQuyet": pq, "moTa": mo_ta, "banChot": b}


def chu_thich(ma: str, chu: str) -> dict:
    """GHI CHÚ THÊM vào một bản khai — không sửa nó, chỉ nối vào sau.

    Bản khai bất biến là đúng: sửa dự đoán sau khi thấy số là toàn bộ thứ sổ này
    sinh ra để chặn. Nhưng BỐI CẢNH thì vẫn tích tụ sau lúc khai, và nó không
    phải dự đoán.

    Ca thật, 30/08: bản khai «keo-lui-short-tien-tuong» không ghi KHUNG, và làn
    demo chạy hai giờ đầu trên khung 4h — đúng cái khung mà chính bộ luật ấy đã
    bị bác bỏ. Không sửa được bản khai, mà cũng không được im: người đọc sổ về
    sau phải thấy chuyện đó nằm cạnh bản khai chứ không nằm trong một lời commit.

    Ghi chú KHÔNG đổi phán quyết và không đổi vân tay bản khai. Nó là một bản
    ghi riêng, có mốc thời gian riêng, nối vào sổ append-only như mọi bản khác.
    """
    ds = doc()
    b_khai = next((x for x in ds if x.get("ma") == ma and x.get("loai") == "khai"), None)
    if not b_khai:
        return {"ok": False, "viSao": f"chưa có bản khai «{ma}»"}
    if not (chu or "").strip():
        return {"ok": False, "viSao": "ghi chú rỗng"}
    b = {"loai": "chu-thich", "ma": ma, "luc": _gio(),
         "dauBanKhai": b_khai.get("dau"), "chuThich": chu.strip()}
    store.append(store.GIA_THUYET, b)
    return {"ok": True, "banGhi": b}


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
