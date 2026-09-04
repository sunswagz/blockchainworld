"""`inf`/`nan` → `None` trước khi ra JSON — bản của RIÊNG ty này.

`bac/sach.py` làm đúng việc này, nhưng một ty không được import `bac/`
(hiến pháp `ty-khong-goi-ty`), và `thi_bac_ty/` không có bản dùng chung.
Tám dòng, chép có khai: ngày `thi_bac_ty/` có bản chung thì trỏ tới đó và
xoá file này.
"""
from __future__ import annotations

import math


def lam_sach(x):
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: lam_sach(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [lam_sach(v) for v in x]
    return x
