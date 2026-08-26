"""OKX — cảng có chu kỳ ĐỔI ĐƯỢC giữa chừng, nên phải đọc chu kỳ mỗi lượt.

OKX đã triển khai cơ chế tự động rút ngắn chu kỳ kết toán từ 8 giờ xuống 4h,
2h hoặc 1h tuỳ điều kiện thị trường. Nghĩa là **không được đóng cứng 8 giờ**
cho cảng này: cùng một instId, sáng nay 8h, chiều nay có thể 4h, và một hằng
số trong mã sẽ sai đúng vào ngày biến động mạnh — đúng ngày chênh lệch funding
đáng giá nhất.

Chu kỳ suy từ `nextFundingTime − fundingTime`. Hai mốc ấy do sàn công bố nên
đây là ĐO, không phải đoán — vì vậy `intervalSuyRa` để False. Chỉ khi hai mốc
thiếu hoặc cho ra một khoảng vô lý thì mới rơi về mặc định, và lúc đó cờ bật
lên để cổng rủi ro chặn.

Giá mark lấy từ `/api/v5/public/mark-price`, KHÔNG lấy `last` của ticker. Bản
v0.1 lấy `last` rồi so với `markPrice` của Binance: `last` là giá khớp cuối,
nhảy theo từng lệnh lẻ; `mark` là giá sàn dùng để thanh lý. So hai thứ đó với
nhau ra một độ lệch pha trộn giữa lệch thật và tiếng ồn vi cấu trúc, rồi cổng
`lechMarkToiDaBps` chặn nhầm hoặc thả nhầm theo.
"""
from __future__ import annotations

import asyncio
import time

from phai_sinh_chung.models import BaoGia
from .base import Cang, bay_gio_ms, nguyen_hoac_none, so_hoac_none

CHU_KY_MAC_DINH_GIO = 8.0
CHU_KY_CO_THAT = (1.0, 2.0, 4.0, 8.0)


class OKX(Cang):
    ten = "okx"
    goc = "https://www.okx.com"

    async def _hoi(self, client, ma: list[str]) -> list[BaoGia]:
        async def mot(goc_ma: str):
            inst = f"{goc_ma}-USDT-SWAP"
            a, b = await asyncio.gather(
                client.get(f"{self.goc}/api/v5/public/funding-rate",
                           params={"instId": inst}),
                client.get(f"{self.goc}/api/v5/public/mark-price",
                           params={"instId": inst, "instType": "SWAP"}),
                return_exceptions=True,
            )
            if isinstance(a, BaseException) or a.status_code >= 400:
                return None
            fr = ((a.json() or {}).get("data") or [None])[0]
            if not fr:
                return None

            mark = None
            if not isinstance(b, BaseException) and b.status_code < 400:
                mp = ((b.json() or {}).get("data") or [None])[0]
                if mp:
                    mark = so_hoac_none(mp.get("markPx"))

            rate = so_hoac_none(fr.get("fundingRate"))
            if rate is None:
                return None
            moc = nguyen_hoac_none(fr.get("fundingTime"))
            moc_ke = nguyen_hoac_none(fr.get("nextFundingTime"))
            ts = nguyen_hoac_none(fr.get("ts")) or int(bay_gio_ms())

            gio, suy_ra = _chu_ky(moc, moc_ke)
            # `fundingRate` gắn với `fundingTime`. Mốc ấy còn ở phía trước thì
            # nó chính là lần kết toán sắp tới; đã trôi qua thì lần sắp tới là
            # `nextFundingTime` — nhưng khi đó mức áp dụng là `nextFundingRate`
            # chứ không phải `fundingRate`, nên ghi chú lại cho rõ.
            now = int(bay_gio_ms())
            if moc is not None and moc > now:
                moc_dung, ghi = moc, ""
            else:
                moc_dung = moc_ke
                ghi = "mốc hiện tại đã qua — dùng mốc kế, mức có thể đã đổi"
            if suy_ra:
                ghi = (ghi + " · " if ghi else "") + \
                      f"không suy được chu kỳ, tạm dùng {CHU_KY_MAC_DINH_GIO:g}h"

            return BaoGia(
                san=self.ten, ma=goc_ma, rate=rate, intervalGio=gio,
                markPx=mark, mocKeMs=moc_dung, nguonTsMs=ts,
                nhanTsMs=now, nguonTuSan=True,   # `ts` là dấu của sàn
                intervalSuyRa=suy_ra, ghiChu=ghi,
            )

        ds = await asyncio.gather(*(mot(x) for x in ma), return_exceptions=True)
        return [x for x in ds if isinstance(x, BaoGia)]


def _chu_ky(mocMs: int | None, mocKeMs: int | None) -> tuple[float, bool]:
    """Chu kỳ đo từ hai mốc sàn công bố. Trả `(giờ, có_phải_đoán_không)`.

    Chỉ nhận những chu kỳ sàn thật sự dùng. Một khoảng 6,97 giờ là dấu hiệu
    đồng hồ trôi hoặc dữ liệu lẫn, không phải một chu kỳ mới — làm tròn về
    giá trị hợp lệ gần nhất, và chỉ khi đủ gần.
    """
    if mocMs is not None and mocKeMs is not None and mocKeMs > mocMs:
        gio = (mocKeMs - mocMs) / 3_600_000.0
        for g in CHU_KY_CO_THAT:
            if abs(gio - g) <= 0.05 * g:
                return g, False
    return CHU_KY_MAC_DINH_GIO, True
