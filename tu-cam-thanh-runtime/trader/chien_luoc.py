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
from .config import CONFIG, DATA_DIR
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


def phan_quyet(cha: dict | None, thu: dict, nhieu_cho: dict | None = None,
               nhieu_lat: dict | None = None) -> dict:
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

    # BẰNG CHỨNG NHIỀU CHỢ — cửa cuối, và là cửa duy nhất nhìn ra ngoài chợ nhà.
    #
    # Đã suýt lọt: MOCK_BIEN_KEP_V1 qua được mọi cửa trên BTCUSDT:4h (+0,109R,
    # 37 lệnh ngoài mẫu, vượt champion −0,05R) — trong khi cùng ngày nó bị đo
    # trên 9 chợ và ra −0,165R qua 104 lệnh, dương ở 1/7 chợ.
    #
    # Mọi cửa khác đều nhìn MỘT chợ, nên chúng không thể bắt được chuyện này.
    # Ba lần trong hệ này, thứ khá ở chợ nhà đều chết ở chợ lạ; cửa này là chỗ
    # duy nhất biến ba lần ấy thành một luật.
    #
    # Truyền VÀO chứ không tự đọc kho: hàm này phải thuần để kiểm được bằng số
    # bịa, và cửa duyệt là chỗ đáng kiểm nhất chứ không phải chỗ khó kiểm nhất.
    if nhieu_cho:
        kv_g = nhieu_cho.get("kyVongR")
        so_cho = nhieu_cho.get("soCho") or 0
        ktin = nhieu_cho.get("khoangTin")
        if kv_g is not None and so_cho >= 3:
            if kv_g <= 0:
                ly_do.append(f"đo trên {so_cho} chợ thì kỳ vọng gộp {kv_g:+.3f}R — "
                             f"khá ở chợ nhà mà âm ở diện rộng là dấu hiệu khớp với "
                             f"lịch sử MỘT chợ, đã xảy ra ba lần ở đây")
            elif ktin and ktin[0] <= 0 <= ktin[1]:
                ly_do.append(f"đo trên {so_cho} chợ được {kv_g:+.3f}R nhưng khoảng "
                             f"tin [{ktin[0]:+.3f}; {ktin[1]:+.3f}] CHỨA 0 — chưa "
                             f"phân biệt được với «không có gì»")

        # NỬA CHẠY ĐƯỢC. Con số gộp ở trên đo CẢ HAI CHIỀU; sàn spot chỉ bán
        # được thứ đang giữ nên `risk.py` chặn SHORT. Hai thứ ấy có thể ngược
        # dấu nhau, và đã ngược:
        #
        #   MOCK_KEO_LUI_V1, 33 chợ 1d chưa từng dùng, nửa ngoài mẫu
        #     cả hai chiều  269 lệnh  +0,205R  khoảng tin [+0,063; +0,354]
        #     riêng SHORT   226 lệnh  +0,303R      ← toàn bộ lợi thế ở đây
        #     riêng LONG     44 lệnh  −0,306R      ← nửa bot thật sự đánh
        #
        # Cửa duyệt cũ nhìn dòng đầu và thấy một bằng chứng mạnh. Nó mạnh thật —
        # về một chiến lược không chạy nổi trên sàn đang dùng.
        #
        # Thiếu số cũng là một lý do từ chối, không phải một lý do bỏ qua: duyệt
        # champion mà không biết nửa chạy được đáng bao nhiêu thì không phải một
        # quyết định, chỉ là một cú tung đồng xu có chữ ký.
        # Bản đầu chỉ soi khi bằng chứng CÓ khai `chayDuoc`. Một bản ghi cũ,
        # ghi trước bản vá này, không có trường ấy — và thế là lách qua đúng cái
        # luật vừa dựng, im lặng. Phép kiểm [48] bắt được vì nó thử chính ca đó.
        #
        # Nên: bằng chứng không nói nửa nào chạy được thì KHÔNG dùng được. Cửa
        # duyệt là chỗ duy nhất tiêu tiền thật; ở đây đóng nhầm rẻ hơn mở nhầm.
        if nhieu_cho.get("chayDuoc") is None:
            ly_do.append("bằng chứng nhiều chợ không khai nửa nào CHẠY ĐƯỢC trên "
                         "sàn đang dùng — số gộp có thể là của nửa SHORT mà sàn "
                         "spot không đánh; chạy lại dau-chien-luoc.py để có")
        elif nhieu_cho.get("chayDuoc") == "LONG":
            cl = nhieu_cho.get("chiLong") or {}
            kv_l, so_l = cl.get("kyVongR"), cl.get("so") or 0
            if kv_l is None or not so_l:
                ly_do.append("chưa đo nửa CHẠY ĐƯỢC (chỉ LONG) — sàn spot không "
                             "đánh được SHORT, mà con số gộp thì gồm cả hai chiều")
            elif kv_l <= 0:
                ly_do.append(f"nửa chạy được trên sàn spot (chỉ LONG) là "
                             f"{kv_l:+.3f}R trên {so_l} lệnh — lợi thế nằm ở nửa "
                             f"SHORT mà bot không đánh được")

    # NHIỀU CỬA SỔ THỜI GIAN. Đây là hàng rào mới nhất, và nó đến từ một phép đo
    # lật ngược cách đọc mọi con số cũ.
    #
    # Đo ngày 30/08 trên ĐÚNG 33 chợ, chỉ đổi cửa sổ (cắt lịch sử ở 2025-01-01):
    #
    #   MOCK_KEO_LUI_V1  cửa sổ muộn  +0,205R/269 lệnh  KT [+0,063; +0,354]
    #                    cửa sổ sớm   −0,254R/208 lệnh  KT [−0,417; −0,127]
    #   MOCK_RULES_V1    cửa sổ muộn  +0,160R/352 lệnh
    #                    cửa sổ sớm   −0,075R/348 lệnh
    #
    # Đổi DẤU, cả hai bộ luật cùng hướng, và khoảng tin cửa sổ sớm không chứa 0.
    # Trong khi đổi CHỢ thì kết quả giữ nguyên (+0,167 → +0,205; +0,117 → +0,160).
    #
    # Nghĩa là 48 chợ KHÔNG phải 48 quan sát độc lập: chúng chia chung một quãng
    # thị trường. "Dương ở 22/30 chợ" đo độ rộng theo trục CHỢ, còn trục gãy là
    # trục THỜI GIAN. Cửa duyệt cũ chỉ nhìn trục kia.
    #
    # `lo-luyen.py` đã đo theo lát thời gian từ lâu — cái thiếu là không ai bắt
    # cửa duyệt tra vào đó. Thiếu số cũng là lý do TỪ CHỐI: duyệt một chiến lược
    # chưa từng bị đổi cửa sổ là duyệt bằng thứ bằng chứng vừa được chứng minh
    # là yếu nhất.
    if not nhieu_lat:
        ly_do.append("chưa đo qua nhiều CỬA SỔ THỜI GIAN — chạy lo-luyen.py để "
                     "có số theo lát; đổi chợ thì kết quả giữ, đổi cửa sổ thì "
                     "nó đã đổi DẤU (đo 30/08, cùng 33 chợ)")
    else:
        _co = nhieu_lat.get("soLatCo") or 0
        _duong = nhieu_lat.get("soLatDuong") or 0
        if _co < 3:
            ly_do.append(f"chỉ {_co} lát thời gian — cần ≥3 mới nói được gì về "
                         f"độ bền qua thời gian")
        elif _duong * 2 <= _co:
            ly_do.append(f"dương ở {_duong}/{_co} lát thời gian — quá nửa số lát "
                         f"là âm, tức con số đẹp thuộc về MỘT quãng thị trường")

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

    # Lấy bằng chứng nhiều chợ từ KHO PHÁT HIỆN — nơi lò chưng cất đã gộp và
    # kèm khoảng tin. Không tự tính lại: hai chỗ tính cùng một thứ rồi sẽ lệch.
    nc = None
    try:
        from . import store as _st

        nc = next(((x.get("so") or {}) for x in _st.read_all(_st.PHAT_HIEN)
                   if x.get("ma") in (f"cho:{c['ma']}", f"cho-gop:{c['ma']}")), None)
    except Exception:  # noqa: BLE001
        nc = None
    # BẰNG CHỨNG NHIỀU LÁT THỜI GIAN, lấy từ kho lò luyện theo BỘ THAM SỐ.
    #
    # Khớp bằng `_ky(tham)` chứ không bằng mã bộ luật: lò dò biến thể tham số
    # của cùng một bộ luật, nên mã giống nhau mà tham số khác là hai thứ khác
    # hẳn. Khớp theo mã là gán bằng chứng của biến thể này cho biến thể kia.
    nl = None
    try:
        import json as _json

        _b = _json.loads((DATA_DIR / "lo-luyen.json").read_text(
            encoding="utf-8")).get("bang") or []
        _th = c.get("tham") or {}
        _lay = lambda x: {"soLatDuong": x.get("soLatDuong"),
                          "soLatCo": x.get("soLatCo"),
                          "kyVongGop": x.get("kyVongGop"),
                          "soLenh": x.get("soLenh")}
        if _th:
            nl = next((_lay(x) for x in _b
                       if _ky(x.get("tham") or {}) == _ky(_th)), None)
        else:
            # `tham` RỖNG nghĩa là "bộ luật ở tham số mặc định" — đúng bằng hàng
            # NỀN của lò (`i == 0`), thứ mọi biến thể được so vào. Khớp bằng
            # `_ky({})` = "mặc-định" thì không bao giờ trúng, vì lò ghi cả bộ
            # tham số đầy đủ vào từng hàng.
            #
            # `dau-chien-luoc.py` tự đề xuất challenger với `tham={}`, nên nếu
            # thiếu nhánh này thì đường TỰ ĐỘNG không bao giờ có bằng chứng lát
            # và cửa duyệt từ chối mọi thứ vì một lý do sai.
            nl = next((_lay(x) for x in _b if x.get("i") == 0), None)
    except Exception:  # noqa: BLE001 — thiếu kho thì cửa duyệt tự từ chối
        nl = None
    pq = phan_quyet(cha_tk, thu_tk, nc, nl)
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
