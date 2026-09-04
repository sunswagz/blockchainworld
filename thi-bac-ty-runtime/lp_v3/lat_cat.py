"""Lát cắt bể thanh khoản → cung tĩnh: `thi-bac-ty/assets/js/v/be-thanh-khoan.js`.

Cùng cơ chế `bac/snapshot.py`: sinh tay rồi COMMIT; nằm ở `assets/js/v/`
(mạng-trước) nên không cần nâng CACHE_VERSION. `date` và `tomTat` đứng
đầu object — Cổng Thành chỉ đọc 900 byte đầu.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .hom_nay import dung
from .lam_sach import lam_sach as sach

_TUONG_DOI = ("assets", "js", "v", "be-thanh-khoan.js")

HEADER = """/* SINH TỰ ĐỘNG bởi thi-bac-ty-runtime (lp_v3) — ĐỪNG SỬA TAY.
   Lát cắt bể thanh khoản V3: phiên Mỹ, dải đề xuất, quyết định từng pool,
   vị thế đang giữ, bài học tích luỹ. Trang tĩnh chỉ đọc; không nút nào.

   Sinh bằng tay:  cd thi-bac-ty-runtime && python -m bac.snapshot
   SINH RỒI PHẢI COMMIT thì site mới đổi.
*/
"""


def dung_lat_cat(ty, now: dt.datetime | None = None) -> dict:
    bc = dung(ty, now, coHoi=ty.coHoi or None)
    gio = dt.datetime.now(dt.timezone.utc)
    hd = bc.get("tomTatHanhDong") or {}
    tom = " · ".join(f"{k} {len(v)}" for k, v in hd.items()) or "chưa cân pool nào"
    return {"date": gio.strftime("%d/%m/%Y"),
            "tomTat": f"{len(bc.get('pool') or [])} pool · {tom}",
            "generatedAt": gio.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            **{k: v for k, v in bc.items()}}


def ghi_cua_ty(t, cung: Path) -> Path | None:
    """`bac/snapshot.py` gọi qua `ty.ghi_lat_cat(cung)` — duck typing, không
    import gói này."""
    d = cung.joinpath(*_TUONG_DOI)
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(HEADER + "window.BE_THANH_KHOAN = "
                 + json.dumps(sach(dung_lat_cat(t)), ensure_ascii=False, indent=2)
                 + ";\n", encoding="utf-8")
    return d
