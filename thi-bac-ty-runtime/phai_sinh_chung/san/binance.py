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

## Open interest trả về bằng COIN, không phải USD

`/fapi/v1/openInterest` trả `openInterest` tính bằng **tài sản gốc** (106801
BTC), không phải đô la. Nhân với mark mới ra USD. Đây đúng cái bẫy
`bac/suc_chua.py` đã ghi sẵn — "đã thấy sàn trả OI bằng số COIN thay vì USD"
— và hậu quả không phải một lỗi mà là một con số nhỏ hơn thật 77.600 lần,
trông vẫn như một con số hợp lệ.

Không có mark thì OI để `None`, KHÔNG để số coin trần. `None` nghĩa là
"không biết"; một con số sai đơn vị nghĩa là "biết sai", và tầng trên không
phân biệt được hai thứ ấy nếu ta không phân biệt ở đây.

Hỏi OI **không được làm hỏng báo giá**: mất OI thì sức chứa thô hơn, mất báo
giá thì mất cả cặp. Nên lời hỏi OI bọc riêng và hỏng thì trả `None`.
"""
from __future__ import annotations

import asyncio
import time

from phai_sinh_chung.models import BaoGia
from .base import Cang, bay_gio_ms, nguyen_hoac_none, so_hoac_none

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
            ts = nguyen_hoac_none(h.get("time")) or int(bay_gio_ms())

            mark = so_hoac_none(h.get("markPrice"))
            oi = await _oi_usd(client, self.goc, sym, mark)

            gio = khai.get(sym, CHU_KY_MAC_DINH_GIO)
            ghi = "" if sym in khai else f"chu kỳ mặc định {CHU_KY_MAC_DINH_GIO:g}h"
            doi = _doi_chung(moc, ts)
            if doi is not None and abs(doi - gio) > 1e-9:
                ghi = (ghi + " · " if ghi else "") + \
                      f"mốc kế gợi ý {doi:g}h, lệch bản khai {gio:g}h"
            return BaoGia(
                san=self.ten, ma=goc_ma, rate=rate, intervalGio=gio,
                markPx=mark, oiUsd=oi,
                mocKeMs=moc, nguonTsMs=ts, nhanTsMs=int(bay_gio_ms()),
                nguonTuSan=True,   # `time` là dấu của sàn
                intervalSuyRa=False, ghiChu=ghi,
            )

        ds = await asyncio.gather(*(mot(x) for x in ma), return_exceptions=True)
        return [x for x in ds if isinstance(x, BaoGia)]


async def _oi_usd(client, goc: str, sym: str,
                  mark: float | None) -> float | None:
    """Open interest quy ra USD, hoặc `None` khi không quy được.

    Bọc kín mọi lỗi: mất OI thì sức chứa của cặp ấy thô hơn, còn để lỗi ném
    lên thì mất luôn báo giá — và mất báo giá là mất cả cặp, đắt hơn hẳn.
    """
    if mark is None:
        return None
    try:
        r = await client.get(f"{goc}/fapi/v1/openInterest",
                             params={"symbol": sym})
        if r.status_code >= 400:
            return None
        coin = so_hoac_none((r.json() or {}).get("openInterest"))
    except Exception:                                     # noqa: BLE001
        return None
    # `openInterest` tính bằng COIN. Không nhân mark là ra một con số nhỏ hơn
    # thật bằng đúng giá một đồng coin — mà vẫn trông như một con số hợp lệ.
    return coin * mark if coin is not None and coin > 0 else None


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
