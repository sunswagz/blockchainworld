"""Bybit linear perp — chu kỳ nằm ở một endpoint KHÁC với funding.

`/v5/market/tickers` cho `fundingRate`, `markPrice`, `nextFundingTime` nhưng
KHÔNG cho chu kỳ. Chu kỳ nằm ở `/v5/market/instruments-info`, trường
`fundingInterval`, đơn vị **phút** — không phải giờ.

Nhầm đơn vị ở đây là một lỗi hạng nặng và hoàn toàn im lặng: đọc 480 rồi coi
là 480 giờ thì funding/giờ nhỏ đi 60 lần, Bybit tụt xuống cuối mọi bảng xếp
hạng và không bao giờ được ghép cặp. Không lỗi nào báo — chỉ là một cảng tự
nhiên biến mất khỏi kết quả.

Hai endpoint đều nhận `category=linear` và trả về CẢ SÀN trong một lượt khi
không truyền `symbol`. Hỏi trọn gói rẻ hơn hỏi từng mã, và quan trọng hơn: nó
cho ta một ảnh chụp NHẤT QUÁN, thay vì bốn ảnh chụp cách nhau vài trăm mili
giây rồi đem so với nhau.
"""
from __future__ import annotations

import time

from ..models import BaoGia
from .base import Cang, bay_gio_ms, nguyen_hoac_none, so_hoac_none

CHU_KY_MAC_DINH_PHUT = 480.0          # 8 giờ


class Bybit(Cang):
    ten = "bybit"
    goc = "https://api.bybit.com"

    async def _hoi(self, client, ma: list[str]) -> list[BaoGia]:
        muon = {f"{x}USDT": x for x in ma}

        r = await client.get(f"{self.goc}/v5/market/instruments-info",
                             params={"category": "linear", "limit": 1000})
        r.raise_for_status()
        phut: dict[str, float] = {}
        for h in (((r.json() or {}).get("result") or {}).get("list") or []):
            v = so_hoac_none(h.get("fundingInterval"))     # ĐƠN VỊ: PHÚT
            if h.get("symbol") in muon and v and v > 0:
                phut[h["symbol"]] = v

        t = await client.get(f"{self.goc}/v5/market/tickers",
                             params={"category": "linear"})
        t.raise_for_status()
        now = int(bay_gio_ms())
        ra: list[BaoGia] = []
        for h in (((t.json() or {}).get("result") or {}).get("list") or []):
            sym = h.get("symbol")
            if sym not in muon:
                continue
            rate = so_hoac_none(h.get("fundingRate"))
            if rate is None:
                continue
            p = phut.get(sym)
            ra.append(BaoGia(
                san=self.ten, ma=muon[sym], rate=rate,
                intervalGio=(p or CHU_KY_MAC_DINH_PHUT) / 60.0,
                markPx=so_hoac_none(h.get("markPrice")),
                mocKeMs=nguyen_hoac_none(h.get("nextFundingTime")),
                oiUsd=so_hoac_none(h.get("openInterestValue")),
                # Tickers không đóng dấu thời gian cho từng dòng. Dấu duy nhất
                # đo được là lúc mình nhận — khai đúng như vậy, chứ đừng gán
                # `now` rồi để tầng trên tưởng đó là dấu của sàn.
                nguonTsMs=now, nhanTsMs=now, nguonTuSan=False,
                intervalSuyRa=p is None,
                ghiChu=("" if p is not None
                        else f"thiếu fundingInterval, tạm dùng "
                             f"{CHU_KY_MAC_DINH_PHUT / 60:g}h"),
            ))
        return ra
