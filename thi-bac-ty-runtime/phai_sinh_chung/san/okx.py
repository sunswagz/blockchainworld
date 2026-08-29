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

## Open interest hỏi MỘT LƯỢT cho cả sàn, không hỏi từng mã

`/api/v5/public/open-interest?instType=SWAP` trả về mọi hợp đồng vĩnh cửu
trong một lời hỏi. Hỏi từng mã là sáu lời hỏi để lấy sáu dòng của cùng một
bảng — vô ích, và mỗi lời hỏi thêm là một dịp bị chặn tần suất.

OKX trả sẵn `oiUsd`, khác Binance và Hyperliquid (hai chỗ ấy trả bằng COIN
và phải nhân mark). Vẫn đối chứng `oiCcy × mark` khi có đủ hai số: lệch quá
một nửa thì BỎ, vì lúc ấy ta không biết trường nào đúng — và một sức chứa
sai gấp mấy lần tệ hơn hẳn một sức chứa không có.
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
        oi_bang = await _oi_ca_san(client, self.goc)

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
                markPx=mark, oiUsd=_oi_hop_le(oi_bang.get(inst), mark),
                mocKeMs=moc_dung, nguonTsMs=ts,
                nhanTsMs=now, nguonTuSan=True,   # `ts` là dấu của sàn
                intervalSuyRa=suy_ra, ghiChu=ghi,
            )

        ds = await asyncio.gather(*(mot(x) for x in ma), return_exceptions=True)
        return [x for x in ds if isinstance(x, BaoGia)]


async def _oi_ca_san(client, goc: str) -> dict:
    """`instId` → `(oiUsd, oiCcy)` cho cả sàn, hoặc rỗng nếu hỏi không được.

    Bọc kín: mất OI thì sức chứa thô hơn; để lỗi ném lên thì mất cả lượt báo
    giá của cảng này, tức mất mọi cặp có một chân ở đây.
    """
    try:
        r = await client.get(f"{goc}/api/v5/public/open-interest",
                             params={"instType": "SWAP"})
        if r.status_code >= 400:
            return {}
        ds = (r.json() or {}).get("data") or []
    except Exception:                                     # noqa: BLE001
        return {}
    return {h["instId"]: (so_hoac_none(h.get("oiUsd")),
                          so_hoac_none(h.get("oiCcy")))
            for h in ds if h.get("instId")}


def _oi_hop_le(cap, mark: float | None) -> float | None:
    """OI theo USD, đã ĐỐI CHỨNG với `oiCcy × mark`. `None` khi không tin nổi.

    OKX trả sẵn `oiUsd`, nhưng "trả sẵn" không phải "đã kiểm". Hai trường
    cùng nói một chuyện thì phải khớp nhau; lệch quá một nửa nghĩa là ta
    không biết trường nào đúng, và lúc ấy `None` trung thực hơn — một sức
    chứa sai gấp mấy lần đắt hơn hẳn một sức chứa không có.
    """
    if not cap:
        return None
    usd, ccy = cap
    if usd is None or usd <= 0:
        return (ccy * mark) if (ccy and mark) else None
    if ccy and mark:
        doi = ccy * mark
        if doi > 0 and abs(usd - doi) / doi > 0.5:
            return None
    return usd


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
