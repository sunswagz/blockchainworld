"""GIẢI PHẪU HÀNH VI TRADER — phong cách, kiểu cắt lỗ, cách thoát lệnh.

Ba tầng cuối của tài liệu thiết kế, tất cả đứng trên cùng một nền: ghép từng
lệnh khớp với **chế độ thị trường tại đúng thời điểm** (`che_do_da_coin.py`).

Luật chung của cả file: mỗi kết luận phải **truy được ra con số sinh ra nó**.
Không có nhãn nào được gán mà không kèm bằng chứng và độ tin. Một cái nhãn
"REVERSAL TRADER" không truy được thì tệ hơn không có nhãn — nó nghe như hiểu
biết trong khi chỉ là một lần đoán.

Chỗ CỐ Ý không làm: hỏi "vì sao họ vào lệnh ở đây". Câu đó cần bộ não thật đọc
bối cảnh, và bộ não hiện chưa cắm khoá. Mọi thứ ở đây là thống kê xác định —
chạy hai lần ra cùng một kết quả, và cãi lại được bằng cách xem lại số.
"""
from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Any

from . import che_do_da_coin as CD


def _ghep(fills: list[dict]) -> list[dict]:
    """Ghép lệnh mở ↔ lệnh đóng theo coin, thành các "vòng" hoàn chỉnh.

    `userFills` là dòng khớp lẻ, không phải giao dịch. Một vị thế có thể mở làm
    ba lần và đóng làm bốn lần. Không ghép lại thì "holding time" và "cách thoát"
    đều tính sai — và sai theo hướng làm mọi trader trông như scalper.
    """
    theo_coin: dict[str, list] = defaultdict(list)
    for f in sorted(fills, key=lambda x: x.get("time", 0)):
        theo_coin[f.get("coin", "?")].append(f)

    vong: list[dict] = []
    for coin, ds in theo_coin.items():
        cur: dict | None = None
        for f in ds:
            d = str(f.get("dir", ""))
            px, sz = float(f.get("px", 0) or 0), float(f.get("sz", 0) or 0)
            if d.startswith("Open"):
                if cur is None:
                    cur = {"coin": coin, "huong": "LONG" if "Long" in d else "SHORT",
                           "moLuc": f.get("time"), "vao": px, "sz": sz,
                           "soLanMo": 1, "soLanDong": 0, "pnl": 0.0,
                           "chuDongVao": bool(f.get("crossed")), "thanhLy": False}
                else:
                    # vào thêm — giá vào bình quân theo khối lượng
                    tong = cur["sz"] + sz
                    cur["vao"] = (cur["vao"] * cur["sz"] + px * sz) / tong if tong else px
                    cur["sz"] = tong
                    cur["soLanMo"] += 1
            elif d.startswith("Close") or "Liquidat" in d:
                if cur is None:
                    continue
                cur["soLanDong"] += 1
                cur["pnl"] += float(f.get("closedPnl", 0) or 0)
                cur["dongLuc"] = f.get("time")
                cur["ra"] = px
                if "Liquidat" in d:
                    cur["thanhLy"] = True
                cur["sz"] -= sz
                if cur["sz"] <= 1e-9:
                    cur["giu_gio"] = (cur["dongLuc"] - cur["moLuc"]) / 3_600_000
                    vong.append(cur)
                    cur = None
    return [v for v in vong if v.get("dongLuc")]


def gan_che_do(vong: list[dict]) -> list[dict]:
    """Gắn chế độ thị trường lúc VÀO và lúc RA cho mỗi vòng."""
    for v in vong:
        v["cheDoVao"] = CD.che_do_luc(v["coin"], v["moLuc"])
        v["cheDoRa"] = CD.che_do_luc(v["coin"], v["dongLuc"])
    return vong


# ── STYLE DETECTOR ────────────────────────────────────────────────────────
def phong_cach(vong: list[dict]) -> dict:
    """Phân loại phong cách. Kèm bằng chứng và độ tin, không gán suông.

    Bốn phong cách, phân biệt bằng những thứ đo được:
      SCALPER    giữ rất ngắn, vào chủ động, nhiều lệnh
      TREND      vào thuận chế độ xu hướng, giữ lâu
      REVERSAL   vào NGƯỢC chiều xu hướng, hoặc vào ở biên
      BREAKOUT   vào đúng lúc chế độ là BREAKOUT
    """
    co_cd = [v for v in vong if v.get("cheDoVao")]
    if len(co_cd) < 10:
        return {"phongCach": None, "viSao": f"chỉ {len(co_cd)} vòng có chế độ — quá ít để kết luận",
                "soVong": len(vong), "soCoCheDo": len(co_cd)}

    giu = [v["giu_gio"] for v in vong if v.get("giu_gio") is not None]
    med = statistics.median(giu) if giu else None
    chu_dong = sum(1 for v in vong if v.get("chuDongVao")) / len(vong)

    dem: dict[str, int] = defaultdict(int)
    thuan = nguoc = bien = 0
    for v in co_cd:
        cd = v["cheDoVao"]["cheDo"]
        dem[cd] += 1
        if cd == "TREND_UP":
            thuan += v["huong"] == "LONG"
            nguoc += v["huong"] == "SHORT"
        elif cd == "TREND_DOWN":
            thuan += v["huong"] == "SHORT"
            nguoc += v["huong"] == "LONG"
        elif cd == "RANGE":
            vt = v["cheDoVao"].get("viTriDai")
            if vt is not None and (vt < 0.3 or vt > 0.7):
                bien += 1

    n = len(co_cd)
    diem = {
        "SCALPER": (1.0 if (med is not None and med < 1.0) else 0.0) * 0.6 + chu_dong * 0.4,
        "TREND": (thuan / n) * 0.7 + (1.0 if (med or 0) > 6 else 0.0) * 0.3,
        "REVERSAL": (nguoc / n) * 0.6 + (bien / n) * 0.4,
        "BREAKOUT": dem["BREAKOUT"] / n,
    }
    ten = max(diem, key=lambda k: diem[k])
    return {
        "phongCach": ten,
        "doTin": round(diem[ten], 3),
        "diem": {k: round(v, 3) for k, v in diem.items()},
        "bangChung": {
            "giuTrungVi_gio": round(med, 2) if med is not None else None,
            "tyLeVaoChuDong": round(chu_dong, 3),
            "thuanXuHuong": round(thuan / n, 3),
            "nguocXuHuong": round(nguoc / n, 3),
            "vaoOBien": round(bien / n, 3),
            "cheDoLucVao": dict(dem),
        },
        "soVong": len(vong), "soCoCheDo": n,
    }


# ── STOP LOSS LIBRARY ─────────────────────────────────────────────────────
# Đủ sáu kiểu tài liệu thiết kế nêu, cộng hai kiểu đo được thêm.
#
# Bản đầu tôi chỉ làm 5 và chỉ 3 trùng với tệp — thiếu VOLATILITY, TRAILING,
# EVENT. Ba cái đó không phải chi tiết trang trí: chúng là ba cách cắt lỗ khác
# hẳn nhau về bản chất, và bỏ chúng thì mọi trader dùng chúng sẽ bị gán nhầm
# sang kiểu gần nhất còn lại.
KIEU_STOP = [
    "STRUCTURAL_STOP",   # cắt khi mất cấu trúc giá (đáy/đỉnh biên)
    "ATR_STOP",          # bội số ATR
    "VOLATILITY_STOP",   # khoảng cắt GIÃN theo biến động — khác ATR ở chỗ nó
                         # thay đổi trong lúc lệnh đang chạy, không cố định lúc vào
    "TRAILING_STOP",     # từng có lãi rồi mới lỗ — stop chạy theo giá
    "TIME_STOP",         # cắt theo thời gian giữ, gần như bất kể giá
    "EVENT_STOP",        # cắt dồn cục quanh một mốc thời gian (tin ra)
    "FIXED_PCT_STOP",    # phần trăm cố định
    "KHONG_CAT",         # không cắt — để sàn thanh lý
]


def kieu_cat_lo(vong: list[dict]) -> dict:
    """Trader này cắt lỗ theo kiểu gì. Chọn kiểu có ĐỘ TẢN NHỎ NHẤT.

    Ý tưởng: nếu ai đó luôn cắt ở −2%, thì đo theo % sẽ ra một cụm chặt còn đo
    theo ATR sẽ tản (vì ATR thay đổi theo thời gian). Kiểu nào cho cụm chặt nhất
    chính là kiểu họ thật sự dùng. Đo bằng hệ số biến thiên — độ lệch chuẩn chia
    trung bình — nên so được giữa các thang đo khác nhau.
    """
    lo = [v for v in vong if v.get("pnl", 0) < 0 and v.get("cheDoVao")]
    if len(lo) < 8:
        return {"kieu": None, "viSao": f"chỉ {len(lo)} lệnh lỗ — quá ít để đọc ra kiểu",
                "soLenhLo": len(lo)}

    thanh_ly = sum(1 for v in lo if v.get("thanhLy"))
    pct, atr_boi, giu, atr_ra_boi = [], [], [], []
    cau_truc = trailing = 0
    gio_trong_ngay: dict[int, int] = defaultdict(int)
    for v in lo:
        vao, ra = v.get("vao"), v.get("ra")
        if not vao or not ra:
            continue
        mat = abs(ra - vao) / vao * 100
        pct.append(mat)
        a = v["cheDoVao"].get("atr")
        if a:
            atr_boi.append(abs(ra - vao) / a)
        # ATR LÚC RA, không phải lúc vào: nếu khoảng cắt bám theo ATR lúc thoát
        # thì đó là stop GIÃN theo biến động, khác hẳn stop chốt cứng lúc vào.
        ar = (v.get("cheDoRa") or {}).get("atr")
        if ar:
            atr_ra_boi.append(abs(ra - vao) / ar)
        if v.get("giu_gio") is not None:
            giu.append(v["giu_gio"])
        # cắt ngay dưới đáy biên 20 nến = cắt theo CẤU TRÚC, không theo con số
        day = v["cheDoVao"].get("dayBien")
        dinh = v["cheDoVao"].get("dinhBien")
        moc = day if v["huong"] == "LONG" else dinh
        if moc and vao and abs(ra - moc) / vao < 0.004:
            cau_truc += 1
        # TRAILING: giá đã đi có lãi rồi mới quay lại cắt. Dấu vết là lệnh từng
        # đóng một phần (chốt lãi) trước khi phần còn lại lỗ.
        if v.get("soLanDong", 0) >= 2 and v.get("giu_gio", 0) > 2:
            trailing += 1
        if v.get("dongLuc"):
            gio_trong_ngay[int((v["dongLuc"] / 3_600_000) % 24)] += 1

    def cv(xs: list[float]) -> float | None:
        xs = [x for x in xs if x is not None and x > 0]
        if len(xs) < 5:
            return None
        m = statistics.fmean(xs)
        return statistics.pstdev(xs) / m if m else None

    tan = {"FIXED_PCT_STOP": cv(pct), "ATR_STOP": cv(atr_boi),
           "VOLATILITY_STOP": cv(atr_ra_boi), "TIME_STOP": cv(giu)}
    ty_ct = cau_truc / len(lo)
    ty_tr = trailing / len(lo)

    # EVENT_STOP: các lần cắt dồn cục vào một khung giờ. Tin ra theo lịch (FOMC,
    # CPI) nên nếu quá nửa số lần cắt rơi vào 3 giờ trong ngày thì đó là cắt vì
    # sự kiện, không phải vì giá.
    dong_cuc = 0.0
    if gio_trong_ngay:
        top3 = sorted(gio_trong_ngay.values(), reverse=True)[:3]
        dong_cuc = sum(top3) / len(lo)

    if thanh_ly / len(lo) > 0.3:
        kieu, vi = "KHONG_CAT", f"{thanh_ly}/{len(lo)} lệnh lỗ kết thúc bằng THANH LÝ"
    elif ty_ct > 0.35:
        kieu, vi = "STRUCTURAL_STOP", f"{cau_truc}/{len(lo)} lệnh cắt sát biên 20 nến"
    elif ty_tr > 0.4:
        kieu, vi = "TRAILING_STOP", f"{trailing}/{len(lo)} lệnh từng chốt một phần rồi mới lỗ"
    elif dong_cuc > 0.55 and len(lo) >= 12:
        kieu, vi = "EVENT_STOP", f"{dong_cuc:.0%} số lần cắt dồn vào 3 khung giờ trong ngày"
    else:
        co = {k: v for k, v in tan.items() if v is not None}
        if not co:
            return {"kieu": None, "viSao": "không đo được độ tản của kiểu nào",
                    "soLenhLo": len(lo)}
        kieu = min(co, key=lambda k: co[k])
        # ATR lúc vào và ATR lúc ra thường sát nhau; chỉ gọi là VOLATILITY khi nó
        # thắng ATR_STOP một khoảng rõ, không phải hơn ở chữ số thập phân thứ ba.
        if kieu == "VOLATILITY_STOP" and co.get("ATR_STOP") is not None \
                and co["VOLATILITY_STOP"] > co["ATR_STOP"] * 0.85:
            kieu = "ATR_STOP"
        vi = f"độ tản nhỏ nhất ở {kieu} (hệ số biến thiên {co[kieu]:.2f})"

    return {
        "kieu": kieu, "viSao": vi, "soLenhLo": len(lo),
        "doTan": {k: (round(v, 3) if v is not None else None) for k, v in tan.items()},
        "tyLeCatTheoCauTruc": round(ty_ct, 3),
        "tyLeTrailing": round(ty_tr, 3),
        "doDonCucTheoGio": round(dong_cuc, 3),
        "tyLeThanhLy": round(thanh_ly / len(lo), 3),
        "matTrungBinhPct": round(statistics.fmean(pct), 2) if pct else None,
        "matTrungBinhAtr": round(statistics.fmean(atr_boi), 2) if atr_boi else None,
    }


# ── EXIT MATRIX CHÉO TRADER ───────────────────────────────────────────────
def ma_tran_cheo(traders: list[dict], toi_thieu: int = 3) -> dict:
    """Ma trận **chéo trader**: mỗi ô = ai giỏi nhất ở (cách thoát × chế độ).

    Đây mới là thứ tài liệu thiết kế mô tả, và là thứ khác hẳn ma trận trong
    một người: bản trong-một-người trả lời "anh này thoát kiểu gì thì ăn", còn
    bản chéo trả lời **"khi thị trường đang thế này và ta muốn thoát kiểu này
    thì nên hỏi ai"** — tức là điều kiện cần để có một đội chuyên gia.

    Bản đầu tôi làm nhầm sang bản trong-một-người.
    """
    o: dict[tuple[str, str], list] = defaultdict(list)
    for t in traders:
        vong = t.get("_vong") or []
        lai = [v for v in vong if v.get("pnl", 0) > 0 and v.get("cheDoVao")]
        gom: dict[tuple[str, str], list] = defaultdict(list)
        for v in lai:
            gom[(kieu_thoat(v), v["cheDoVao"]["cheDo"])].append(v["pnl"])
        for k, ps in gom.items():
            if len(ps) >= toi_thieu:
                o[k].append({"diaChi": t.get("diaChi"), "diem": (t.get("diem") or {}).get("diem"),
                             "so": len(ps), "trungBinh": round(statistics.fmean(ps), 2),
                             "tong": round(sum(ps), 2)})

    ra: dict[str, dict] = defaultdict(dict)
    for (kieu, cd), ds in o.items():
        # Xếp theo lãi TRUNG BÌNH mỗi lệnh, không theo tổng: tổng thiên vị người
        # vốn lớn, mà ta đang tìm người GIỎI chứ không phải người to.
        ds.sort(key=lambda x: -x["trungBinh"])
        ra[kieu][cd] = {"gioiNhat": ds[0], "soUngVien": len(ds)}
    return {
        "co": bool(ra), "maTran": dict(ra),
        "toiThieuMoiO": toi_thieu,
        "ghiChu": ("Mỗi ô là trader có lãi trung bình cao nhất ở (cách thoát × chế độ). "
                   "Ô chỉ có 1 ứng viên thì chưa so được với ai — đọc như gợi ý, "
                   "không phải kết luận."),
    }


# ── EXIT STRATEGY MATRIX ──────────────────────────────────────────────────
def kieu_thoat(v: dict) -> str:
    """Cách thoát của MỘT vòng lãi."""
    if v.get("soLanDong", 0) >= 3:
        return "SCALE_OUT"
    if (v.get("giu_gio") or 0) > 24:
        return "TRAILING_DAI"
    if v.get("soLanDong", 0) == 1 and (v.get("giu_gio") or 0) <= 24:
        return "FIXED_TP"
    return "KHAC"


def ma_tran_thoat(vong: list[dict]) -> dict:
    """Ma trận: kiểu thoát × chế độ thị trường → hiệu quả.

    Đây là thứ tài liệu thiết kế gọi "EXIT STRATEGY MATRIX", và là thứ trả lời
    được câu hỏi thật sự hữu ích: *cách thoát nào ăn ở chế độ nào* — chứ không
    phải "cách thoát nào tốt nhất", vì câu đó không có đáp án.
    """
    lai = [v for v in vong if v.get("pnl", 0) > 0 and v.get("cheDoVao")]
    if len(lai) < 8:
        return {"co": False, "viSao": f"chỉ {len(lai)} lệnh lãi — chưa đủ dựng ma trận"}

    o: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for v in lai:
        o[kieu_thoat(v)][v["cheDoVao"]["cheDo"]].append(v["pnl"])

    ra: dict[str, dict] = {}
    for k, theo_cd in o.items():
        ra[k] = {cd: {"so": len(ps), "tongPnl": round(sum(ps), 2),
                      "trungBinh": round(statistics.fmean(ps), 2)}
                 for cd, ps in theo_cd.items()}
    return {"co": True, "maTran": ra, "soLenhLai": len(lai),
            "ghiChu": "ô có dưới 5 lệnh chỉ là nhiễu — đừng đọc thành quy luật"}


# ── ĐA DẠNG CHẾ ĐỘ ────────────────────────────────────────────────────────
def da_dang_che_do(vong: list[dict]) -> dict:
    """Trader này ăn được ở mấy chế độ thị trường, và ăn ở đâu.

    Đây chính là thành phần 5% trọng số trước đây phải để trống. Giờ tính được
    vì đã có chế độ thị trường cho mọi coin.
    """
    co = [v for v in vong if v.get("cheDoVao")]
    if len(co) < 10:
        return {"diem": None, "viSao": f"chỉ {len(co)} vòng có chế độ"}

    theo: dict[str, dict] = defaultdict(lambda: {"so": 0, "thang": 0, "pnl": 0.0})
    for v in co:
        g = theo[v["cheDoVao"]["cheDo"]]
        g["so"] += 1
        g["thang"] += 1 if v["pnl"] > 0 else 0
        g["pnl"] += v["pnl"]

    du = {k: g for k, g in theo.items() if g["so"] >= 5}
    an = [k for k, g in du.items() if g["pnl"] > 0]
    # Điểm 0..1: ăn được ở càng nhiều chế độ càng bền. 3+ chế độ là rất bền.
    diem = min(1.0, len(an) / 3) if du else 0.0
    return {
        "diem": round(diem, 3),
        "cheDoAnDuoc": an,
        "cheDoDuMau": list(du),
        "chiTiet": {k: {**g, "tyLeThang": round(g["thang"] / g["so"] * 100, 1),
                        "pnl": round(g["pnl"], 2)} for k, g in theo.items()},
        "soVongCoCheDo": len(co),
    }


def giai_phau(fills: list[dict]) -> dict:
    """Chạy cả bốn tầng cho một trader. Cần `che_do_da_coin` đã dựng chuỗi."""
    vong = gan_che_do(_ghep(fills))
    return {
        "soVong": len(vong),
        "phongCach": phong_cach(vong),
        "catLo": kieu_cat_lo(vong),
        "maTranThoat": ma_tran_thoat(vong),
        "daDangCheDo": da_dang_che_do(vong),
        "mauLapLai": mau_lap_lai(vong),
        # Giữ lại vòng để dựng ma trận CHÉO trader ở tầng trên. Không kèm ra
        # ngoài file JSON — `phien_quan_sat` bỏ trước khi lưu.
        "_vong": vong,
    }


# ── PATTERN ENGINE ────────────────────────────────────────────────────────
def mau_lap_lai(vong: list[dict], toi_thieu: int = 5) -> dict:
    """Tìm HÀNH VI LẶP LẠI — thứ tài liệu gọi "giải ngược hành vi giao dịch".

    Ranh giới: chỉ nhận một mẫu khi nó **lặp đủ nhiều VÀ ăn tiền**. Một điều
    kiện xuất hiện 30 lần mà hoà vốn thì đó là thói quen, không phải lợi thế —
    và nhầm hai thứ đó là cách nhanh nhất để học được một mê tín.

    Mỗi mẫu mang theo số lần, tỉ lệ thắng, lãi trung bình, nên cãi lại được.
    """
    co = [v for v in vong if v.get("cheDoVao") and v.get("pnl") is not None]
    if len(co) < 12:
        return {"co": False, "viSao": f"chỉ {len(co)} vòng đủ dữ kiện — quá ít để nói lặp lại"}

    def dk(v: dict) -> list[str]:
        c, d = v["cheDoVao"], []
        d.append(f"chế độ={c['cheDo']}")
        d.append(f"hướng={v['huong']}")
        d.append("vào chủ động" if v.get("chuDongVao") else "vào bị động")
        rsi = c.get("rsi")
        if rsi is not None:
            d.append("RSI<35" if rsi < 35 else "RSI>65" if rsi > 65 else "RSI giữa")
        vt = c.get("viTriDai")
        if vt is not None:
            d.append("ở đáy dải" if vt < 0.3 else "ở đỉnh dải" if vt > 0.7 else "giữa dải")
        adx = c.get("adx")
        if adx is not None:
            d.append("ADX≥25" if adx >= 25 else "ADX<18" if adx < 18 else "ADX giữa")
        for co_ in c.get("co") or []:
            d.append(f"cờ={co_}")
        return d

    # Đếm từng điều kiện, rồi các CẶP điều kiện. Cặp mới là chỗ hành vi thật lộ
    # ra: "mua khi RSI thấp" là tầm thường, "mua khi RSI thấp TRONG xu hướng
    # tăng" mới là một quyết định.
    don: dict[str, list] = defaultdict(list)
    cap: dict[tuple[str, str], list] = defaultdict(list)
    for v in co:
        ds = dk(v)
        for a in ds:
            don[a].append(v["pnl"])
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)):
                cap[(ds[i], ds[j])].append(v["pnl"])

    def gom(items, ten) -> list[dict]:
        ra = []
        for k, ps in items:
            if len(ps) < toi_thieu:
                continue
            tb = statistics.fmean(ps)
            if tb <= 0:
                continue
            ra.append({
                "mau": k if isinstance(k, str) else " + ".join(k),
                "loai": ten, "soLan": len(ps),
                "tyLePhu": round(len(ps) / len(co) * 100, 1),
                "tyLeThang": round(sum(1 for p in ps if p > 0) / len(ps) * 100, 1),
                "laiTrungBinh": round(tb, 2),
            })
        return ra

    tat = gom(don.items(), "đơn") + gom(cap.items(), "cặp")
    tat.sort(key=lambda x: -(x["laiTrungBinh"] * x["soLan"]))
    return {
        "co": bool(tat), "soVongXet": len(co),
        "mau": tat[:12],
        "ghiChu": ("Chỉ giữ mẫu lặp ≥%d lần VÀ có lãi trung bình dương. Đây là "
                   "tương quan trong quá khứ, chưa phải nguyên nhân — phải qua "
                   "backtest rồi cửa duyệt champion mới được dùng." % toi_thieu),
    }
