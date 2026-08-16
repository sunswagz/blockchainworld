"""Chạy phễu quan sát trader ở luồng nền, lưu hồ sơ ra đĩa.

Phễu, đúng như tài liệu thiết kế mô tả — và lý do nó phải là phễu rất cụ thể:
leaderboard có **41.794 trader**, mà mỗi hồ sơ sâu tốn 2 lời gọi API. Lấy hết
là 83.588 lời gọi và vài giờ. Nên:

    41.794 trader          leaderboard, một lời gọi ~34 MB
        ↓ lọc vốn ≥ 50k, có volume
    vài nghìn
        ↓ lấy mẫu BA nhóm: đỉnh · giữa · ĐANG LỖ
    ~36 trader
        ↓ lấy đường vốn + lệnh khớp  (2 lời gọi mỗi người)
    hồ sơ đầy đủ + điểm chất lượng

Nhóm "đang lỗ" không phải để cho vui: nó là thứ chặn thiên lệch kẻ sống sót.
Nếu hồ sơ người thua trông giống hệt hồ sơ người thắng ở mọi chỉ số ta đo, thì
điều đó có nghĩa là **ta đang đo sai thứ** — và đó là phát hiện đáng giá hơn
một bảng xếp hạng đẹp.
"""
from __future__ import annotations

import threading
import time
from typing import Any

import httpx

from . import dai_quan_sat as DQ, store
from .bus import bus

KHO = "trader-ho-so.json"

_trang_thai: dict[str, Any] = {"trangThai": "chưa chạy", "phanTram": 0, "viec": None,
                               "batDau": None, "xong": None, "loi": None}
_luong: threading.Thread | None = None


def trang_thai() -> dict:
    return {**_trang_thai, "kho": tom_tat()}


def tom_tat() -> dict:
    d = store.read_json(KHO, None)
    if not d:
        return {"co": False}
    hs = d.get("traders") or []
    theo_hang: dict[str, int] = {}
    for t in hs:
        theo_hang[t["diem"]["hang"]] = theo_hang.get(t["diem"]["hang"], 0) + 1
    return {
        "co": True, "luc": d.get("luc"), "soTrader": len(hs),
        "tongLeaderboard": d.get("tongLeaderboard"),
        "theoHang": theo_hang,
        "soNghiNgoAnMay": sum(1 for t in hs if t["anMay"]["nghiNgo"]),
        "theoNhom": {n: sum(1 for t in hs if t["nhom"] == n)
                     for n in ("dinh", "giua", "dangLo")},
    }


def ho_so_day_du() -> dict:
    return store.read_json(KHO, {"traders": []})


def _chay(moi_nhom: int) -> None:
    try:
        _trang_thai.update(trangThai="đang chạy", batDau=time.time(), loi=None, phanTram=1,
                           viec="tải leaderboard Hyperliquid (~34 MB)")
        with httpx.Client(follow_redirects=True) as c:
            lb = DQ.leaderboard(c)
            _trang_thai.update(phanTram=15, viec=f"lọc và lấy mẫu từ {len(lb):,} trader")
            mau = DQ.lay_mau(lb, moi_nhom)

            can = [(n, t) for n in ("dinh", "giua", "dangLo") for t in mau[n]]
            ra: list[dict] = []
            for i, (nhom, t) in enumerate(can):
                _trang_thai.update(
                    phanTram=15 + round((i / max(1, len(can))) * 80),
                    viec=f"hồ sơ {i + 1}/{len(can)} · {nhom} · {t['diaChi'][:10]}…")
                ct: dict[str, Any] = {}
                try:
                    dv = DQ.duong_von(c, t["diaChi"])
                    lich = (dv.get("allTime") or {}).get("accountValueHistory") or []
                    ct["sutGiamPct"] = DQ.sut_giam(lich)
                    if len(lich) >= 2:
                        ct["soNgay"] = round((lich[-1][0] - lich[0][0]) / 86_400_000, 1)
                    fills = DQ.lenh_khop(c, t["diaChi"])
                    hs = DQ.ho_so(fills)
                    ct["soLenh"] = hs.get("soLenh")
                    ct["soLanThanhLy"] = hs.get("soLanThanhLy")
                    ct["kyLuat"] = DQ.ky_luat(hs)
                except Exception as e:  # noqa: BLE001 — một trader hỏng không được kéo cả mẻ
                    hs = {"soLenh": 0, "loi": f"{type(e).__name__}"}
                ra.append({
                    **t, "nhom": nhom, "hoSo": hs,
                    "diem": DQ.cham_diem(t, ct),
                    "anMay": DQ.an_may(hs),
                })
                time.sleep(0.25)   # đừng nện API công khai của người ta

            _trang_thai.update(phanTram=97, viec="lấy lead trader OKX")
            try:
                okx = DQ.okx_lead(c)
            except Exception:  # noqa: BLE001
                okx = []

        ra.sort(key=lambda x: -x["diem"]["diem"])
        store.write_json(KHO, {
            "luc": time.time(), "tongLeaderboard": mau["tong"],
            "traders": ra, "okx": okx,
        })
        _trang_thai.update(trangThai="xong", phanTram=100, xong=time.time(),
                           viec=f"{len(ra)} hồ sơ · {len(okx)} lead trader OKX")
        bus.emit("hoc", "quan-sat-xong",
                 f"dựng {len(ra)} hồ sơ trader từ {mau['tong']:,} ứng viên")
    except Exception as e:  # noqa: BLE001
        _trang_thai.update(trangThai="lỗi", loi=f"{type(e).__name__}: {e}", xong=time.time())
        bus.log("hoc", "quan-sat-loi", f"phễu quan sát hỏng: {e}")


def bat_dau(moi_nhom: int = 12) -> dict:
    global _luong
    if _trang_thai["trangThai"] == "đang chạy":
        return {"ok": False, "vi_sao": "đang chạy"}
    _luong = threading.Thread(target=_chay, args=(moi_nhom,),
                              name="quan-sat-trader", daemon=True)
    _luong.start()
    return {"ok": True}
