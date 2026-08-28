"""Nguồn dữ liệu — Polymarket (đọc) và Binance (đọc). Không đường nào ghi.

Polymarket mở gần như toàn bộ "hệ thần kinh" cho phần mềm: Gamma API cho
metadata/discovery, CLOB API cho giá và sổ lệnh, Data API cho hoạt động tài
khoản, WebSocket cho realtime. Phần ĐỌC không cần xác thực gì cả — đó là lý
do một người có thể dựng cả cái terminal này mà chưa từng nối ví.

Module này CỐ Ý chỉ có đường đọc. Đặt lệnh nằm ở `dat_lenh.py` và phải đi qua
ba cửa của `config.py`. Tách như vậy để một lần đọc nhầm code không bao giờ
biến thành một lệnh gửi đi.

── Về SDK ────────────────────────────────────────────────────────────────
`Polymarket/py-clob-client` đời cũ đã bị archive 25/05/2026 và chính repo ghi
rõ không nên dùng cho tích hợp mới. SDK hợp nhất hiện hành là
`Polymarket/py-sdk`, gói `polymarket-client`.

Ở đây dùng thẳng HTTP cho phần đọc — ít phụ thuộc hơn, và phần đọc thì API
ổn định. Chỗ nào cần SDK (ký lệnh) thì `dat_lenh.py` bọc nó sau một adapter,
để SDK đổi thì chỉ sửa adapter chứ không sửa cả hệ thống.
"""
from __future__ import annotations

import datetime as _dt
import time
from dataclasses import dataclass, field

from .bus import bus
from .config import CONFIG
from .so_lenh import Muc, SoLenh

_NG = CONFIG["nguon"]
_HET_GIO = float(_NG["hetGioGiay"])


def _httpx():
    """Nạp httpx muộn, để thiếu gói vẫn import được module mà kiểm được."""
    try:
        import httpx
        return httpx
    except ImportError:
        return None


# Lùi thời gian khi một nguồn hỏng liên tiếp. Ba lần đầu còn hỏi ngay —
# mạng chập chờn là chuyện thường. Từ lần thứ tư thì giãn gấp đôi mỗi lần,
# trần 60 giây: đủ thưa để không hỏi dồn, đủ dày để nguồn sống lại là biết
# trong vòng một phút.
LOI_TRUOC_KHI_LUI = 3
NGHI_DAU_MS = 2_000.0
NGHI_TOI_DA_MS = 60_000.0


@dataclass
class TrangThaiNguon:
    """Sức khoẻ từng nguồn — thứ Risk Engine đọc để quyết có cho lệnh đi không."""
    ten: str
    lanCuoiMs: float = 0.0
    soLoi: int = 0
    loiCuoi: str = ""
    tongLuot: int = 0
    nghiToiMs: float = 0.0        # lùi thời gian sau nhiều lần hỏng liên tiếp

    def tuoi_ms(self) -> float:
        if self.lanCuoiMs <= 0:
            return float("inf")
        return time.time() * 1000.0 - self.lanCuoiMs

    def dat(self) -> None:
        self.lanCuoiMs = time.time() * 1000.0
        self.tongLuot += 1
        self.soLoi = 0
        self.nghiToiMs = 0.0

    def loi(self, e: str) -> None:
        self.soLoi += 1
        self.loiCuoi = e[:200]
        # LÙI THỜI GIAN. Không có nó, một nguồn chết sẽ bị hỏi lại mỗi
        # nhịp 2 giây, mãi mãi — đo được: 2.140 lần hỏng liên tiếp, không
        # một lần thành công, và nhật ký chỉ còn là một cột lỗi trôi qua.
        #
        # Hỏi dồn như thế không vô hại: nếu phía kia chặn vì tần suất thì
        # chính việc hỏi lại đang giữ cho cửa đóng, và ta tự làm mình mù
        # lâu hơn.
        if self.soLoi >= LOI_TRUOC_KHI_LUI:
            n = self.soLoi - LOI_TRUOC_KHI_LUI
            cho = min(NGHI_TOI_DA_MS, NGHI_DAU_MS * (2 ** min(n, 10)))
            self.nghiToiMs = time.time() * 1000.0 + cho

    def dang_nghi(self) -> bool:
        return time.time() * 1000.0 < self.nghiToiMs

    def lanh(self, tranMs: float) -> bool:
        return self.tuoi_ms() <= tranMs and self.soLoi < 3


class Nguon:
    """Gom mọi lời gọi ra ngoài vào một chỗ, kèm sổ sức khoẻ."""

    def __init__(self) -> None:
        self.trangThai: dict[str, TrangThaiNguon] = {}
        self._client = None

    def _ts(self, ten: str) -> TrangThaiNguon:
        return self.trangThai.setdefault(ten, TrangThaiNguon(ten))

    def client(self):
        hx = _httpx()
        if hx is None:
            return None
        if self._client is None:
            # ĐƯỜNG RA phải khai được và NHÌN THẤY được.
            #
            # 21–28/08/2026: cả ba host của Polymarket (gamma, clob, và cả
            # WebSocket) đều bị đóng ở tầng TLS từ máy này — TCP 443 bắt
            # tay xong mới bị giết, chỉ nhắm đúng tên miền ấy. Binance thì
            # bình thường. Đó là chuyện của đường mạng, không phải của mã.
            #
            # Cái mã LÀM ĐƯỢC là đừng bắt người vận hành sửa mã để đổi
            # đường ra. `httpx` vốn đã tôn trọng HTTPS_PROXY, nhưng biến
            # môi trường thì vô hình: không ai nhìn buồng lái mà biết
            # runtime đang đi lối nào. Nay khai trong config, và lối đang
            # dùng hiện ngay trên bảng sức khoẻ nguồn.
            kw = {"timeout": _HET_GIO,
                  "headers": {"User-Agent": "kham-thien-giam/0.1"}}
            if self.proxy:
                kw["proxy"] = self.proxy
            self._client = hx.Client(**kw)
        return self._client

    @property
    def proxy(self) -> str | None:
        """Lối ra khai trong config, hoặc từ biến môi trường."""
        import os
        p = (_NG.get("proxy") or "").strip()
        return p or os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or None

    def dong(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def _lay(self, ten: str, url: str, tham: dict | None = None):
        ts = self._ts(ten)
        if ts.dang_nghi():
            return None                 # đang lùi, đừng hỏi dồn
        c = self.client()
        if c is None:
            self._ts(ten).loi("thiếu httpx")
            return None
        try:
            r = c.get(url, params=tham)
            r.raise_for_status()
            self._ts(ten).dat()
            return r.json()
        except Exception as e:                      # noqa: BLE001
            self._ts(ten).loi(f"{type(e).__name__}: {e}")
            bus.ghi(f"nguồn {ten} lỗi: {type(e).__name__}", loai="loi")
            return None

    # ── Binance: giá nền ──────────────────────────────────────────────────
    def gia_binance(self, cap: str) -> float | None:
        for goc in (_NG["binanceSpot"], _NG["binanceDuPhong"]):
            d = self._lay("binance", f"{goc}/api/v3/ticker/price", {"symbol": cap})
            if d and "price" in d:
                try:
                    return float(d["price"])
                except (TypeError, ValueError):
                    pass
        return None

    def gia_mo_khung(self, cap: str, batDauMs: float) -> float | None:
        """Giá lúc MỞ khung — chính là strike K của market Up/Down.

        Không lấy từ Gamma: market Up/Down không phải lúc nào cũng khai
        `openPrice`, và khi thiếu thì mô hình mất mẫu số. Nến 1 phút của
        Binance có `open` đúng tại mốc đó và luôn có.

        Sai một chút ở K là sai TOÀN BỘ mô hình: `ln(S/K)` là tử số của
        z-score, mà ở khung 5 phút thì `ln(S/K)` chỉ cỡ 1e-3. Lệch K đi
        0,05% là lệch tử số đi một nửa — và không phép kiểm nào đỏ.
        """
        moc = int(batDauMs // 60_000 * 60_000)
        for goc in (_NG["binanceSpot"], _NG["binanceDuPhong"]):
            d = self._lay("binance-kline", f"{goc}/api/v3/klines",
                          {"symbol": cap, "interval": "1m",
                           "startTime": moc, "limit": 1})
            if isinstance(d, list) and d and len(d[0]) > 1:
                try:
                    return float(d[0][1])       # [openTime, OPEN, high, low, ...]
                except (TypeError, ValueError, IndexError):
                    pass
        return None

    def gia_dong_khung(self, cap: str, ketThucMs: float) -> float | None:
        """Giá lúc ĐÓNG khung — vế còn lại của phép so kết toán.

        Lấy nến 1 phút BẮT ĐẦU tại phút cuối của khung rồi đọc `close` của
        nó. Khung 5 phút kết thúc đúng mốc phút nên nến đó đóng đúng lúc.

        Đây là ĐƯỜNG ĐỘC LẬP với sàn, cố ý vậy: nó tồn tại để phát hiện bất
        đồng, nên không được dùng chung nguồn với `outcomePrices`.
        """
        moc = int((ketThucMs - 60_000) // 60_000 * 60_000)
        for goc in (_NG["binanceSpot"], _NG["binanceDuPhong"]):
            d = self._lay("binance-kline", f"{goc}/api/v3/klines",
                          {"symbol": cap, "interval": "1m",
                           "startTime": moc, "limit": 1})
            if isinstance(d, list) and d and len(d[0]) > 4:
                try:
                    return float(d[0][4])       # [openTime,o,h,l,CLOSE,...]
                except (TypeError, ValueError, IndexError):
                    pass
        return None

    def moc_thoi_gian_binance(self) -> tuple[float, float, float] | None:
        """(mốc sàn ms, gửi ms, nhận ms) — nguyên liệu hiệu chỉnh đồng hồ."""
        c = self.client()
        if c is None:
            return None
        gui = time.time() * 1000.0
        try:
            r = c.get(f"{_NG['binanceSpot']}/api/v3/time")
            r.raise_for_status()
            nhan = time.time() * 1000.0
            return float(r.json()["serverTime"]), gui, nhan
        except Exception as e:                      # noqa: BLE001
            self._ts("binance-time").loi(str(e))
            return None

    # ── Polymarket: tìm market ────────────────────────────────────────────
    def tim_theo_tien_to(self, tienTo: str, gioiHan: int = 400) -> list[dict]:
        """Tìm khung đang sống theo TIỀN TỐ slug, xếp theo hạn gần nhất.

        Ba chi tiết ở đây, cả ba đều là bug đã cắn thật lúc dựng:

        1. **Tiền tố, không phải slug đầy đủ.** Polymarket đặt cho MỖI KHUNG
           một slug riêng kèm mốc Unix của khung:

               btc-updown-5m-1787215500
               btc-updown-5m-1787215800

           Nên `slug=bitcoin-up-or-down` trả về đúng 0 kết quả, mãi mãi. Và
           nó hỏng IM LẶNG theo kiểu tệ nhất: Gamma trả HTTP 200 với mảng
           rỗng, nên sổ sức khoẻ ghi "12 lượt, 0 lỗi" trong khi runtime chưa
           từng thấy một market nào. Không lỗi nào để thấy — chỉ một bảng
           điều khiển trống mà mọi đèn đều xanh.

        2. **`end_date_min` là bắt buộc.** Không có nó, `ascending=true` trả
           về những market ĐÃ QUÁ HẠN mà vẫn còn cờ `active/closed=false` —
           đo được lúc dựng: khung cũ nhất kết thúc cách hiện tại hơn 5.000
           giờ. Runtime khi đó tưởng đồng hồ máy sai, trong khi đồng hồ máy
           đúng (đã đối chiếu Binance `serverTime` và header `Date` của
           chính Polymarket) — thứ sai là câu truy vấn.

        3. **Giới hạn phải rộng.** Polymarket mở khung 5 phút cho rất nhiều
           cặp cùng lúc (btc, eth, sol, xrp, doge, zec, bnb, hype…). Lấy 80
           kết quả đầu theo hạn tăng dần thì có lúc chưa chạm tới BTC, và
           runtime báo "không thấy market nào" trong khi market có thật.
        """
        moc = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        d = self._lay("gamma", f"{_NG['polymarketGamma']}/markets",
                      {"active": "true", "closed": "false", "limit": gioiHan,
                       "order": "endDate", "ascending": "true",
                       "end_date_min": moc})
        if not isinstance(d, list):
            return []
        return [m for m in d
                if (m.get("slug") or "").startswith(tienTo) and not m.get("closed")]

    def tim_theo_slug(self, slug: str) -> dict | None:
        """Một market, hỏi đúng slug. Dùng cho họ khung DÀI.

        Họ Lên/Xuống phải dựng slug từ mốc thời gian vì mỗi 5 phút là một
        market mới. Họ chạm mốc thì ngược lại: MỘT market sống hàng tháng,
        slug cố định, khai thẳng trong config. Không có gì để dựng.
        """
        d = self._lay("gamma", f"{_NG['gamma']}/markets", {"slug": slug})
        if isinstance(d, list) and d:
            return d[0]
        return None

    def dinh_da_qua(self, cap: str, tuMs: float, lenTren: bool = True,
                    denMs: float | None = None) -> float | None:
        """Đỉnh cao nhất (hoặc đáy thấp nhất) đã đi qua kể từ `tuMs`.

        Đây là tham số BẮT BUỘC của động cơ chạm mốc, và là bẫy chết người
        của họ market ấy: ta chỉ nhìn thấy giá HIỆN TẠI. Nếu tháng trước
        giá đã vọt qua mốc rồi quay về thì market đã ngã ngũ, còn công
        thức vẫn vui vẻ trả ra một xác suất nhỏ xinh.

        Nến NGÀY, không nến phút: một market bốn tháng là ~120 nến ngày
        (một lượt gọi) so với ~170.000 nến phút (hàng trăm lượt). Và đỉnh
        của nến ngày ĐÚNG BẰNG đỉnh của các nến phút trong ngày đó — không
        mất mát gì, vì `high` đã là cực trị.
        """
        moc = int(tuMs // 86_400_000 * 86_400_000)
        for goc in (_NG["binanceSpot"], _NG["binanceDuPhong"]):
            d = self._lay("binance-kline", f"{goc}/api/v3/klines",
                          {"symbol": cap, "interval": "1d",
                           "startTime": moc, "limit": 1000})
            if not isinstance(d, list) or not d:
                continue
            try:
                if lenTren:
                    return max(float(r[2]) for r in d if len(r) > 2)
                return min(float(r[3]) for r in d if len(r) > 3)
            except (TypeError, ValueError, IndexError):
                continue
        return None

    def tim_khung_dung_slug(self, tienTo: str, songGiay: float = 300.0,
                            soKhung: int = 4) -> list[dict]:
        """Dựng thẳng slug từ mốc thời gian rồi hỏi đúng slug đó.

        Vì sao không dùng `tim_theo_tien_to` cho việc này: **Gamma chặn cứng
        100 kết quả** bất kể `limit` xin bao nhiêu (đã đo: xin 400, trả 100;
        xin 500, trả 100). Polymarket mở khung 5 phút cho rất nhiều cặp cùng
        lúc — btc, eth, sol, xrp, doge, zec, bnb, hype… — nên 100 kết quả
        đầu theo hạn tăng dần CÓ LÚC không chạm tới cặp mình cần.

        Và nó hỏng theo kiểu tệ nhất: lúc được lúc không. Chạy thử tay lúc
        14:48 thấy 1 khung, runtime chạy lúc 15:0x thấy 0 khung, cùng một
        đoạn code. Một lỗi phụ thuộc thời điểm thì không tái hiện được, và
        không tái hiện được thì rất khó tin là mình đã sửa xong.

        May là slug có quy luật chặt: `<coin>-updown-5m-<unix eventStart>`,
        và eventStart luôn rơi đúng bội số của độ dài khung. Nên tính thẳng
        vài mốc kế tiếp rồi hỏi từng slug một — vài lời gọi, nhưng chắc
        chắn, và không phụ thuộc vào việc cặp của mình có lọt top 100 không.
        """
        gio = _dt.datetime.now(_dt.timezone.utc).timestamp()
        b = int(songGiay)
        moc_gan = int(gio // b * b)
        ra: list[dict] = []
        # Lùi một khung: khung đang trong cửa đặt cược có eventStart Ở TƯƠNG
        # LAI, nhưng lùi một bước cho chắc khi đồng hồ lệch vài giây.
        for i in range(-1, soKhung):
            m = self.market_theo_slug(f"{tienTo}{moc_gan + i * b}")
            if m and not m.get("closed"):
                ra.append(m)
        return ra

    def market_sap_het(self, gioiHan: int = 40) -> list[dict]:
        """Các market đang sống, sắp xếp theo thời điểm kết thúc gần nhất.

        Đây là nguyên liệu của "RESOLUTION GRID" trong mấy dashboard người ta
        khoe: chỉ là danh sách market sắp hết hạn cùng giá hai bên.
        """
        d = self._lay("gamma", f"{_NG['polymarketGamma']}/markets",
                      {"active": "true", "closed": "false", "limit": gioiHan,
                       "order": "endDate", "ascending": "true"})
        return d if isinstance(d, list) else []

    def market_theo_slug(self, slug: str) -> dict | None:
        """Một market theo slug đầy đủ — dùng để hỏi KẾT QUẢ sau khi đóng.

        KHÔNG lọc `closed=false` ở đây: chỗ này cố ý hỏi những market ĐÃ
        đóng, vì đó mới là lúc `outcomePrices` có giá trị.
        """
        d = self._lay("gamma-slug", f"{_NG['polymarketGamma']}/markets",
                      {"slug": slug, "limit": 1})
        if isinstance(d, list) and d:
            return d[0]
        return None

    # ── Polymarket: sổ lệnh ───────────────────────────────────────────────
    def so_lenh(self, ma: str, ben: str, tokenId: str) -> SoLenh | None:
        """Sổ L2 của một token outcome."""
        d = self._lay("clob-book", f"{_NG['polymarketClob']}/book",
                      {"token_id": tokenId})
        if not isinstance(d, dict):
            return None
        return doc_so(ma, ben, d)

    def gia_giua(self, tokenId: str) -> float | None:
        d = self._lay("clob-mid", f"{_NG['polymarketClob']}/midpoint",
                      {"token_id": tokenId})
        if isinstance(d, dict) and "mid" in d:
            try:
                return float(d["mid"])
            except (TypeError, ValueError):
                return None
        return None

    # ── Polymarket: hoạt động ví (chỉ QUAN SÁT) ───────────────────────────
    def hoat_dong_vi(self, diaChiHoacTen: str, gioiHan: int = 100) -> list[dict]:
        d = self._lay("data-activity", f"{_NG['polymarketData']}/activity",
                      {"user": diaChiHoacTen, "limit": gioiHan})
        return d if isinstance(d, list) else []

    def vi_the_vi(self, diaChiHoacTen: str, gioiHan: int = 100) -> list[dict]:
        d = self._lay("data-positions", f"{_NG['polymarketData']}/positions",
                      {"user": diaChiHoacTen, "limit": gioiHan})
        return d if isinstance(d, list) else []

    def tom_tat(self) -> dict:
        # `tuoi_ms()` trả inf cho nguồn chưa gọi lần nào — đúng để so sánh
        # trong rui_ro.py, nhưng inf không gửi qua JSON được. None ở đây có
        # nghĩa "chưa gọi lần nào", khác hẳn 0 nghĩa "vừa gọi xong".
        return {t.ten: {"tuoiMs": (t.tuoi_ms() if t.lanCuoiMs > 0 else None),
                        "soLoi": t.soLoi, "tongLuot": t.tongLuot,
                        "loiCuoi": t.loiCuoi}
                for t in self.trangThai.values()}

    def duong_ra(self) -> dict:
        """Runtime đang đi lối nào. Hiện trên bảng sức khoẻ nguồn.

        Biến môi trường thì vô hình: không ai nhìn buồng lái mà biết
        `HTTPS_PROXY` có đang được dùng hay không, nên một máy đi lối khác
        với máy bên cạnh mà cả hai đều trông giống hệt nhau.
        """
        p = self.proxy
        return {"coProxy": bool(p),
                # Không in nguyên chuỗi: proxy hay có user:mật khẩu trong
                # URL, và buồng lái tuy chỉ chạy ở localhost nhưng lát cắt
                # thì đi lên site.
                "moTa": (p.split("@")[-1] if p else "đường thẳng")}


def doc_so(ma: str, ben: str, d: dict) -> SoLenh:
    """Đổi JSON sổ lệnh CLOB thành `SoLenh`.

    Hai điều phải làm đúng, và cả hai đều hỏng im lặng nếu làm sai:

    1. **Thứ tự.** API không hứa trả về đã sắp. `bid` phải giảm dần, `ask`
       phải tăng dần, vì mọi phép VWAP đi tuần tự từ đầu danh sách. Sổ chưa
       sắp thì VWAP tính ra một con số hoàn toàn có nghĩa và hoàn toàn sai.

    2. **Bỏ mức rỗng.** Mức khối lượng 0 vẫn chiếm chỗ trong danh sách và làm
       `soMuc` đếm sai, kéo theo mọi phép đo độ sâu.
    """
    def muc(ds, giam_dan: bool) -> list[Muc]:
        ra: list[Muc] = []
        for m in (ds or []):
            try:
                g = float(m.get("price"))
                l = float(m.get("size"))
            except (TypeError, ValueError, AttributeError):
                continue
            if l > 0 and 0.0 <= g <= 1.0:
                ra.append(Muc(g, l))
        ra.sort(key=lambda x: x.gia, reverse=giam_dan)
        return ra

    return SoLenh(
        ma=ma, ben=ben,
        bid=muc(d.get("bids"), giam_dan=True),
        ask=muc(d.get("asks"), giam_dan=False),
        nhanLucMs=time.time() * 1000.0,
    )


nguon = Nguon()
