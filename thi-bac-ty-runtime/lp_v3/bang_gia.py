"""BĂNG GIÁ tự tích — càng chạy lâu càng biết nhiều, và đó là cách «lăn».

Hai lớp giá cho mỗi mã, ghi ở `data/lp-v3/bang/<mã>.json`:

    goc     giá đóng cửa hằng ngày của cổ phiếu GỐC (Yahoo) — σ đáng tin
            nhất, nhưng chỉ có với mã có sàn gốc công khai; kèm MỘT điểm
            `gocTucThoi` là giá đang giao dịch, tuổi tính bằng phút
    chuoi   giá pool trên chuỗi, lấy mẫu mỗi lượt quét (RPC) — thứ duy nhất
            có với SPCXx, và thứ duy nhất nói được giá NGOÀI GIỜ trôi ra sao

Với mã không có sàn gốc, σ chỉ tích được từ lớp `chuoi`, và ngày đầu nó
KHÔNG có: ty sẽ từ chối mã ấy cho tới khi băng đủ dày, rồi tự nhận lại —
không ai phải nhớ bật gì. Đó là nghĩa của «tự học»: không phải máy thông
minh hơn, mà là hôm nay nó biết một thứ hôm qua chưa biết, và điều ấy đọc
được từ đĩa.

Băng KHÔNG ghi đè: chỉ thêm ngày mới, và chỉ giữ tối đa `GIU_NGAY_GOC` ngày
gốc / `GIU_MAU_CHUOI` mẫu chuỗi để file không lớn vô hạn.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

from .config import THU_MUC
from .mo_hinh import sigma_nam

THU_MUC_BANG = THU_MUC / "bang"
GIU_NGAY_GOC = 400
GIU_MAU_CHUOI = 5000


def _duong(ma: str, thuMuc: Path | None = None) -> Path:
    return (thuMuc or THU_MUC_BANG) / f"{ma.upper()}.json"


def nap(ma: str, thuMuc: Path | None = None) -> dict:
    p = _duong(ma, thuMuc)
    if not p.exists():
        return {"ma": ma.upper(), "goc": [], "chuoi": []}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"ma": ma.upper(), "goc": [], "chuoi": [], "loi": "băng hỏng"}
    d.setdefault("goc", [])
    d.setdefault("chuoi", [])
    return d


def _ghi(d: dict, thuMuc: Path | None = None) -> Path:
    p = _duong(d["ma"], thuMuc)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return p


def ghi_goc(ma: str, dong: list, thuMuc: Path | None = None) -> int:
    """Gộp `[(ngày ISO, giá đóng)]` vào lớp gốc. Trả số ngày MỚI thêm."""
    d = nap(ma, thuMuc)
    co = {x["ngay"]: x for x in d["goc"]}
    moi = 0
    for ngay, gia in dong:
        if gia is None or not (float(gia) > 0):
            continue
        if ngay not in co:
            moi += 1
        co[ngay] = {"ngay": str(ngay), "dong": float(gia)}
    d["goc"] = sorted(co.values(), key=lambda x: x["ngay"])[-GIU_NGAY_GOC:]
    _ghi(d, thuMuc)
    return moi


def ghi_chuoi(ma: str, luc: dt.datetime, gia: float, nguon: str = "rpc",
              thuMuc: Path | None = None) -> None:
    if gia is None or not (float(gia) > 0):
        return
    d = nap(ma, thuMuc)
    d["chuoi"].append({"luc": luc.astimezone(dt.timezone.utc).isoformat(
        timespec="seconds").replace("+00:00", "Z"), "gia": float(gia),
        "nguon": nguon})
    d["chuoi"] = d["chuoi"][-GIU_MAU_CHUOI:]
    _ghi(d, thuMuc)


def ghi_goc_tuc_thoi(ma: str, luc: dt.datetime, gia: float,
                     thuMuc: Path | None = None) -> None:
    """Giá ĐANG giao dịch của sàn gốc (Yahoo `regularMarketPrice`) — một
    điểm duy nhất, ghi đè: nó là «giá bây giờ», không phải lịch sử. Lịch
    sử vẫn là lớp `goc` (đóng cửa) và `chuoi` (mẫu pool)."""
    if gia is None or not (float(gia) > 0):
        return
    d = nap(ma, thuMuc)
    d["gocTucThoi"] = {"luc": luc.astimezone(dt.timezone.utc).isoformat(
        timespec="seconds").replace("+00:00", "Z"), "gia": float(gia)}
    _ghi(d, thuMuc)


def dong_cua_goc(ma: str, soNgay: int | None = None,
                 thuMuc: Path | None = None) -> list:
    g = nap(ma, thuMuc)["goc"]
    g = g if soNgay is None else g[-soNgay:]
    return [x["dong"] for x in g]


def dong_cua_chuoi_theo_ngay(ma: str, thuMuc: Path | None = None) -> list:
    """Mẫu chuỗi gom về MỘT giá mỗi ngày UTC (mẫu cuối ngày) — để σ chuỗi
    so được với σ gốc trên cùng một thang ngày."""
    theoNgay = {}
    for x in nap(ma, thuMuc)["chuoi"]:
        theoNgay[x["luc"][:10]] = x["gia"]
    return [theoNgay[k] for k in sorted(theoNgay)]


def sigma(ma: str, cuaSoNgay: int = 60, toiThieu: int = 10,
          thuMuc: Path | None = None) -> dict:
    """σ năm của mã, ưu tiên lớp GỐC; không có thì lớp CHUỖI; không có nữa
    thì `None` kèm số phiên đang có — để câu «chưa đủ» mang con số."""
    goc = dong_cua_goc(ma, cuaSoNgay, thuMuc)
    s = sigma_nam(goc, toiThieu)
    if s is not None:
        return {"sigma": s, "nguon": "goc", "soPhien": len(goc) - 1,
                "cuaSoNgay": cuaSoNgay}
    ch = dong_cua_chuoi_theo_ngay(ma, thuMuc)[-cuaSoNgay:]
    s = sigma_nam(ch, toiThieu)
    if s is not None:
        return {"sigma": s, "nguon": "chuoi", "soPhien": len(ch) - 1,
                "cuaSoNgay": cuaSoNgay}
    return {"sigma": None, "nguon": None,
            "soPhien": max(len(goc), len(ch)) - 1 if (goc or ch) else 0,
            "cuaSoNgay": cuaSoNgay}


def bien_dong_lien_quan(ma: str, thuMuc: Path | None = None) -> dict:
    """«Biến động liên quan» — thứ người vận hành hỏi mỗi sáng, đo được:
    giá đổi 1 ngày / 5 ngày, và σ ngắn (10) so σ dài (60) — σ đang NỞ hay
    CO. Tỉ lệ > 1,3 là biến động đang cụm lại, dải hôm qua hẹp hơn hôm nay."""
    g = dong_cua_goc(ma, None, thuMuc)
    ra = {"ma": ma, "soPhien": max(0, len(g) - 1)}
    if len(g) >= 2:
        ra["doi1NgayPct"] = (g[-1] / g[-2] - 1.0) * 100.0
    if len(g) >= 6:
        ra["doi5NgayPct"] = (g[-1] / g[-6] - 1.0) * 100.0
    s10 = sigma_nam(g[-11:], 10) if len(g) >= 11 else None
    s60 = sigma_nam(g[-61:], 10) if len(g) >= 20 else None
    ra["sigma10"] = s10
    ra["sigma60"] = s60
    if s10 and s60:
        ra["tiLeNoCo"] = s10 / s60
        ra["trangThai"] = ("NO" if s10 / s60 > 1.3 else
                           "CO" if s10 / s60 < 0.75 else "ON")
    if len(g) >= 21 and s60:
        ra["doi20NgayPct"] = (g[-1] / g[-21] - 1.0) * 100.0
        ra["xuHuong"] = xu_huong(g[-21:], s60)
    return ra


def xu_huong(g: list, sigmaNam: float) -> dict | None:
    """Bài 8 §9: LP là BÁN tài sản đang tăng, MUA tài sản đang giảm — xu hướng
    một chiều mạnh là lúc LP thua HOLD; đi ngang là lúc LP thắng. Đo bằng
    z = ln(g[-1]/g[0]) / (σ·√(n/252)); |z| > 2 là mạnh.

    CHỈ ĐO, chưa có luật đọc: thước mới phải có mẫu (so alpha LP giữa hai
    chế độ) rồi mới thành cửa — không đặt ngưỡng chặn khi chưa đo được nó
    có nói đúng không."""
    if len(g) < 2 or not sigmaNam or g[0] <= 0 or g[-1] <= 0:
        return None
    n = len(g) - 1
    z = math.log(g[-1] / g[0]) / (sigmaNam * math.sqrt(n / 252.0))
    return {"z": z, "soPhien": n,
            "nhan": "TANG_MANH" if z > 2.0 else "GIAM_MANH" if z < -2.0 else "DAO_DONG",
            "canh": False}


def gia_moi_nhat(ma: str, thuMuc: Path | None = None,
                 now: dt.datetime | None = None) -> dict:
    """Giá mới nhất giữa hai lớp, kèm nguồn và tuổi — tuổi là thứ cửa
    `gia-cu` đọc. `now` truyền vào được để phép kiểm đứng ở một giờ cố
    định."""
    d = nap(ma, thuMuc)
    now = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    ung = []
    if d["chuoi"]:
        x = d["chuoi"][-1]
        try:
            t = dt.datetime.fromisoformat(x["luc"].replace("Z", "+00:00"))
            ung.append((t, x["gia"], "chuoi"))
        except ValueError:
            pass
    if d["goc"]:
        x = d["goc"][-1]
        # giá đóng cửa: mốc 16:00 New York ≈ 20:00–21:00 UTC; lấy 21:00 UTC
        # để tuổi hơi GIÀ hơn thật chứ không trẻ hơn
        try:
            t = dt.datetime.fromisoformat(x["ngay"]).replace(
                hour=21, tzinfo=dt.timezone.utc)
            ung.append((t, x["dong"], "goc"))
        except ValueError:
            pass
    if d.get("gocTucThoi"):
        x = d["gocTucThoi"]
        try:
            t = dt.datetime.fromisoformat(x["luc"].replace("Z", "+00:00"))
            ung.append((t, x["gia"], "goc-tuc-thoi"))
        except ValueError:
            pass
    if not ung:
        return {"gia": None, "nguon": None, "tuoiGiay": None}
    t, gia, ng = max(ung, key=lambda u: u[0])
    return {"gia": gia, "nguon": ng, "luc": t.isoformat(),
            "tuoiGiay": max(0.0, (now - t).total_seconds())}
