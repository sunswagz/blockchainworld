"""Hyperliquid — một lượt hỏi lấy trọn cả sàn.

`metaAndAssetCtxs` trả về `[meta, ctxs]` song song theo chỉ số: `meta.universe[i]`
mô tả tài sản thứ i, `ctxs[i]` là trạng thái của nó. Ghép sai chỉ số là gán
funding của SOL cho BTC — một lỗi không hề giống lỗi, vì mọi con số vẫn hợp lệ.
Nên ở đây dùng `zip(..., strict=True)`: lệch độ dài thì NỔ ngay lúc ghép, thay
vì lặng lẽ cắt ngắn theo danh sách ngắn hơn rồi lệch nhãn từ đó về sau.

`ctx["funding"]` là mức MỖI GIỜ — Hyperliquid kết toán hàng giờ, khác hẳn ba
cảng còn lại. Chính chỗ này là ví dụ kinh điển: 0,015%/1h của Hyperliquid LỚN
hơn 0,08%/8h của Binance, dù nhìn con số thô thì ngược lại.
"""
from __future__ import annotations

import time

from ..models import BaoGia
from .base import Cang, bay_gio_ms, moc_tron_gio_ke, so_hoac_none


class Hyperliquid(Cang):
    ten = "hyperliquid"
    url = "https://api.hyperliquid.xyz/info"

    async def _hoi(self, client, ma: list[str]) -> list[BaoGia]:
        muon = set(ma)
        r = await client.post(self.url, json={"type": "metaAndAssetCtxs"})
        r.raise_for_status()
        goi = r.json()
        if not isinstance(goi, list) or len(goi) != 2:
            raise ValueError(f"metaAndAssetCtxs trả về khuôn lạ: {type(goi).__name__}")
        meta, ctxs = goi
        vu_tru = (meta or {}).get("universe") or []

        now = bay_gio_ms()
        ra: list[BaoGia] = []
        for ts, ctx in zip(vu_tru, ctxs, strict=True):
            ten = (ts or {}).get("name")
            if ten not in muon:
                continue
            mark = so_hoac_none((ctx or {}).get("markPx"))
            oi = so_hoac_none((ctx or {}).get("openInterest"))
            rate = so_hoac_none((ctx or {}).get("funding"))
            if rate is None:
                continue
            ra.append(BaoGia(
                san=self.ten, ma=ten,
                rate=rate,
                intervalGio=1.0,
                markPx=mark,
                # Sàn không trả mốc kế trong lượt hỏi này. Kết toán theo giờ
                # là quy ước công bố của sàn, nên mốc kế là đầu giờ kế tiếp —
                # suy từ QUY ƯỚC chứ không phải từ dữ liệu, và ghi chú nói rõ
                # điều đó để không ai tưởng đây là số sàn gửi về.
                mocKeMs=moc_tron_gio_ke(now),
                oiUsd=(oi * mark) if (oi is not None and mark is not None) else None,
                nguonTsMs=int(now),
                nhanTsMs=int(now),
                nguonTuSan=False,   # sàn không đóng dấu trong lượt hỏi này
                intervalSuyRa=False,
                ghiChu="mốc kế suy từ quy ước kết toán hàng giờ",
            ))
        return ra
