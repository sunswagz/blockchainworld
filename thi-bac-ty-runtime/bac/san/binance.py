"""Binance USD-M — và cái bẫy `fundingInfo` chỉ trả về MỘT PHẦN.

`/fapi/v1/fundingInfo` **không** liệt kê mọi symbol. Nó chỉ trả về những symbol
đã bị điều chỉnh trần/sàn hoặc chu kỳ. Symbol không có trong đó dùng chu kỳ mặc
định 8 giờ.

Nghĩa là: `adjusted.get(symbol, 8.0)` là ĐÚNG, nhưng chỉ đúng chừng nào 8 vẫn
là mặc định của sàn. Nếu Binance đổi mặc định mà không ai sửa hằng số này thì
mọi phép chuẩn hoá lệch đi một hệ số — và không có gì báo, vì con số vẫn ra.

Nên ở đây không tin mỗi một nguồn: `nextFundingTime` cũng được dùng để **đối
chứng** chu kỳ. Hai nguồn khớp thì yên tâm; lệch thì tin `fundingInfo` (nó nói
thẳng) nhưng ghi chú lại để buồng lái hiện ra.
"""
from __future__ import annotations

import asyncio
import time

from ..models import BaoGia
from .base import Cang, nguyen_hoac_none, so_hoac_none

#: Chu kỳ mặc định của Binance USD-M khi symbol không có trong `fundingInfo`.
CHU_KY_MAC_DINH_GIO = 8.0

#: Những chu kỳ sàn thực sự dùng. `nextFundingTime` khớp một trong số này thì
#: mới coi là đối chứng được; lệch hết thì đồng hồ đang trôi, đừng suy bừa.
CHU_KY_CO_THAT = (1.0, 2.0, 4.0, 8.0)


class Binance(Cang):
    ten = "binance"
    goc = "https://fapi.binance.com"

    async def _hoi(self, client, ma: list[str]) -> list[BaoGia]:
        r = await client.get(f"{self.goc}/fapi/v1/fundingInfo")
        r.raise_for_status()
        khai = {}
        for hang in (r.json() or []):
            gio = so_hoac_none(hang.get("fundingIntervalHours"))
            if hang.get("symbol") and gio:
                khai[hang["symbol"]] = gio

        async def mot(goc_ma: str):
            sym = f"{goc_ma}USDT"
            rr = await client.get(f"{self.goc}/fapi/v1/premiumIndex",
                                  params={"symbol": sym})
            if rr.status_code == 400:
                return None                       # symbol không niêm yết
            rr.raise_for_status()
            h = rr.json() or {}
            rate = so_hoac_none(h.get("lastFundingRate"))
            if rate is None:
                return None
            moc = nguyen_hoac_none(h.get("nextFundingTime"))
            ts = nguyen_hoac_none(h.get("time")) or int(time.time() * 1000)

            gio = khai.get(sym, CHU_KY_MAC_DINH_GIO)
            ghi = "" if sym in khai else f"chu kỳ mặc định {CHU_KY_MAC_DINH_GIO:g}h"
            doi = _doi_chung(moc, ts)
            if doi is not None and abs(doi - gio) > 1e-9:
                ghi = (ghi + " · " if ghi else "") + \
                      f"mốc kế gợi ý {doi:g}h, lệch bản khai {gio:g}h"
            return BaoGia(
                san=self.ten, ma=goc_ma, rate=rate, intervalGio=gio,
                markPx=so_hoac_none(h.get("markPrice")),
                mocKeMs=moc, nguonTsMs=ts, nhanTsMs=int(time.time() * 1000),
                intervalSuyRa=False, ghiChu=ghi,
            )

        ds = await asyncio.gather(*(mot(x) for x in ma), return_exceptions=True)
        return [x for x in ds if isinstance(x, BaoGia)]


def _doi_chung(mocMs: int | None, tsMs: int | None) -> float | None:
    """Suy chu kỳ từ khoảng cách tới mốc kế — chỉ để ĐỐI CHỨNG, không để dùng.

    Khoảng cách tới mốc kế luôn ≤ chu kỳ, nên nó chỉ chặn dưới. Ta làm tròn
    LÊN tới chu kỳ có thật gần nhất; không chu kỳ nào chứa nổi thì trả None
    thay vì bịa ra một con số.
    """
    if mocMs is None or tsMs is None or mocMs <= tsMs:
        return None
    con = (mocMs - tsMs) / 3_600_000.0
    for g in CHU_KY_CO_THAT:
        if con <= g + 1e-6:
            return g
    return None
