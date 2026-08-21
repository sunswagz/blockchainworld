"""Đồng hồ — và vì sao đồng hồ MÁY không dùng được ở đây.

## Chuyện đã đo được, 21/08/2026

    máy nói      15:54:43 UTC
    Binance nói  16:01:40 UTC
    OKX nói      16:01:40 UTC
    Bybit nói    16:01:40 UTC

Ba sàn độc lập lệch y hệt nhau **416,2 giây** so với máy. Không phải sàn sai —
**đồng hồ máy chậm 6,94 phút**.

Ở hầu hết chương trình, lệch 7 phút là chuyện vặt. Ở đây nó nằm đúng đường
tim, và nó hỏng theo hai đường, cả hai đều im lặng:

### 1. Đếm mốc lệch đi cả một lần kết toán

`mocKeMs` do SÀN gửi (giờ sàn). `now` lấy từ máy (giờ máy). So hai thứ ở hai
đồng hồ khác nhau thì gần biên là lật hẳn kết quả:

    thật:  16:01 — mốc 16:00 vừa qua, mốc kế là 00:00
    máy:   15:54 — tưởng mốc 16:00 còn 6 phút nữa

Một cửa sổ giữ 30 phút: đồng hồ máy nói "thu trọn một chu kỳ", sự thật là
"không mốc nào". Đó chính là con số mà cả `dongho.py` sinh ra để đếm cho
đúng — đếm đúng trên một cái đồng hồ sai thì vẫn ra số sai.

### 2. Cửa "dữ liệu cũ" bị vô hiệu, và trông như đang chạy tốt

`tuoi_giay()` bản đầu viết `max(0.0, (now − nguonTs) / 1000)`. Dấu thời gian
của sàn nằm ở TƯƠNG LAI so với đồng hồ máy, nên hiệu ra âm, và `max(0, …)`
kẹp nó về 0 — tức "vừa mới tinh". Đo thật:

    binance      tuoi_giay() = 0.0    (thô: −416 giây)
    okx          tuoi_giay() = 0.0    (thô: −370 giây)

Cửa `tuoiToiDaGiay = 90` **không bao giờ nổ được** cho hai sàn ấy, dù cấy vào
một báo giá cũ 10 phút. Một cửa rủi ro đứng đó, hiện trong bảng cấu hình, và
không chặn gì cả.

## Nên: đo lệch, bù lệch, và KHAI ra

Module này giữ một ước lượng lệch giữa đồng hồ máy và đồng hồ sàn, lấy từ
chính những dấu thời gian các adapter đã nhận về — không tốn thêm lượt hỏi
nào.

Nửa vòng khứ hồi (~50–100 ms) bị bỏ qua có chủ ý: nó nhỏ hơn ba bậc so với
thứ đang đo. Làm phức tạp thêm để bù một sai số 0,05 giây trong khi sai số
thật là 416 giây là tối ưu nhầm chỗ.

**Trung vị, không phải trung bình.** Một sàn trả về dấu thời gian hỏng sẽ kéo
trung bình đi bao xa tuỳ nó muốn; trung vị thì cần quá nửa số sàn cùng sai
mới lay chuyển được.
"""
from __future__ import annotations

import statistics
import threading
import time

#: Lệch quá ngần này thì buồng lái phải kêu. 5 giây đã là nhiều với một máy
#: có đồng bộ NTP; 7 phút là dấu hiệu NTP tắt hẳn.
NGUONG_KEU_MS = 5_000.0

#: Mẫu cũ hơn ngần này thì bỏ — đồng hồ máy có thể vừa được chỉnh lại.
HAN_MAU_GIAY = 600.0


class DongHo:
    def __init__(self) -> None:
        self._khoa = threading.Lock()
        self._mau: dict[str, tuple[float, float]] = {}   # sàn → (lệch ms, lúc)

    def ghi_mau(self, san: str, sanNowMs: float, guiMs: float, nhanMs: float) -> None:
        """Ghi một mẫu lệch. `sanNowMs` phải là GIỜ HIỆN TẠI của sàn.

        Bù nửa vòng khứ hồi: dấu sàn đóng ở đâu đó giữa lúc ta gửi và lúc ta
        nhận, nên mốc so sánh đúng là trung điểm.

        **Chỉ dùng endpoint giờ máy chủ.** Bản đầu lấy `ts` đi kèm báo giá
        funding của OKX làm mẫu — nhưng trường đó là giờ SINH DỮ LIỆU, không
        phải giờ hiện tại. Hậu quả đo được: OKX báo lệch 379s trong khi
        Binance báo 416s, hai sàn "lệch nhau 37 giây" mà thật ra chúng khớp
        nhau — chỉ là ta đang so hai đại lượng khác nhau.
        """
        with self._khoa:
            self._mau[san] = (sanNowMs - (guiMs + nhanMs) / 2.0, time.time())

    def _con_han(self) -> list[float]:
        moc = time.time() - HAN_MAU_GIAY
        return [d for d, luc in self._mau.values() if luc >= moc]

    def lech_ms(self) -> float | None:
        """Máy chậm hơn sàn bao nhiêu mili giây. None = chưa đo được."""
        with self._khoa:
            ds = self._con_han()
        return statistics.median(ds) if ds else None

    def bay_gio_ms(self) -> float:
        """Giờ SÀN, ước lượng. Đây là đồng hồ mọi phép đếm mốc phải dùng."""
        return time.time() * 1000.0 + (self.lech_ms() or 0.0)

    def tom_tat(self) -> dict:
        with self._khoa:
            mau = {k: v[0] for k, v in self._mau.items()}
        l = self.lech_ms()
        return {
            "lechMs": l,
            "lechGiay": None if l is None else l / 1000.0,
            "daDo": l is not None,
            "dangKeu": l is not None and abs(l) > NGUONG_KEU_MS,
            "nguongKeuMs": NGUONG_KEU_MS,
            "theoSan": mau,
            "soMau": len(mau),
        }


#: Endpoint giờ máy chủ của từng sàn. Hyperliquid không công bố cái nào, nên
#: nó không góp mẫu — ba sàn còn lại là quá đủ cho một phép lấy trung vị.
NGUON_GIO = {
    "binance": ("https://fapi.binance.com/fapi/v1/time",
                lambda j: float(j["serverTime"])),
    "okx": ("https://www.okx.com/api/v5/public/time",
            lambda j: float(j["data"][0]["ts"])),
    "bybit": ("https://api.bybit.com/v5/market/time",
              lambda j: float(j["result"]["timeNano"]) / 1e6),
}


async def do_lech(client, dh: "DongHo") -> int:
    """Hỏi giờ máy chủ ba sàn, ghi mẫu. Trả về số mẫu lấy được.

    KHÔNG ném: đo được đồng hồ là chuyện tốt, không đo được cũng không phải
    lý do để cả lượt quét chết. Không mẫu nào thì `lech_ms()` trả None và
    buồng lái hiện "chưa đo được" — khác hẳn với "đã đo, khớp".
    """
    import asyncio

    async def mot(san, url, lay):
        gui = time.time() * 1000.0
        r = await client.get(url)
        nhan = time.time() * 1000.0
        r.raise_for_status()
        dh.ghi_mau(san, lay(r.json()), gui, nhan)

    ket = await asyncio.gather(
        *(mot(s, u, f) for s, (u, f) in NGUON_GIO.items()),
        return_exceptions=True)
    return sum(1 for k in ket if not isinstance(k, BaseException))


dong_ho = DongHo()
