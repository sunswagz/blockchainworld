"""Ba nguồn CÔNG KHAI, không khoá — và mỗi nguồn để lại dấu khi hỏng.

    NguonGiaGoc   giá đóng cửa hằng ngày + giá đang giao dịch (Yahoo chart)
    NguonRpcPool  slot0 · liquidity · fee · decimals · symbol của pool V3
                  qua JSON-RPC thô — không web3, không ABI ngoài, năm
                  selector viết tay
    NguonRss      tiêu đề tin theo mã (RSS Yahoo)

Không nguồn nào được ném: hỏng thì `suc_khoe.ghi_loi` và trả rỗng, để lượt
quét vẫn đi tiếp trên những gì còn đọc được, và buồng lái hiện đúng con mắt
nào đang mù.

Cả ba đã thử SỐNG từ máy vận hành ngày 05/09/2026: Yahoo chart 200/JSON,
RSS 200/XML, RPC X Layer trả số khối. Stooq (nguồn đầu) chết ở lượt thử
ấy — trang chắn JavaScript — và bị thay. Hình dạng đầu vào có phép kiểm
trên mẫu cố định; sức khoẻ sống đọc ở `suc_khoe` từng nguồn.
"""
from __future__ import annotations

import datetime as dt
import time
import xml.etree.ElementTree as ET

from thi_bac_ty.nguon import Nguon, so_hoac_none

# ── Yahoo chart: giá đóng cửa hằng ngày + giá ĐANG giao dịch ───────────
#
# Stooq từng là nguồn đầu tiên; thử SỐNG ngày 05/09/2026 thì nó trả một
# trang «This site requires JavaScript to verify your browser» — CSV rỗng
# 8/8 lượt. Yahoo chart trả JSON không cần khoá, và cho thêm một thứ Stooq
# không có: `regularMarketPrice` + `regularMarketTime` — giá của phiên ĐANG
# diễn ra, tuổi tính bằng phút. Không có nó thì trong phiên ty chỉ có giá
# đóng cửa hôm qua, và mọi dải đều đặt quanh một con số đã cũ nửa ngày.

YAHOO_CHART = ("https://query1.finance.yahoo.com/v8/finance/chart/{ma}"
               "?range=1y&interval=1d")
#: Yahoo từ chối UA lạ; UA trình duyệt là điều kiện để nguồn này sống.
UA_TRINH_DUYET = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "thi-bac-ty/lp-v3 (+public data only)")


def doc_yahoo_chart(j: dict) -> tuple[list, tuple | None]:
    """`(dãy (ngày, đóng), (giờ, giá) tức thời hoặc None)` từ JSON chart.

    Ngày lấy theo giờ SÀN (`meta.gmtoffset`), không theo UTC: phiên Mỹ mở
    13:30 UTC, đóng 20:00 UTC — vẫn cùng ngày, nhưng lệch một giờ ở mốc
    nửa đêm là lệch một ngày trong băng. Dòng nào thiếu giá đóng (ngày
    nghỉ giữa chuỗi) thì bỏ, không điền 0.
    """
    try:
        r = (j.get("chart") or {}).get("result") or []
        r = r[0]
        meta = r.get("meta") or {}
        ts = r.get("timestamp") or []
        dong = ((r.get("indicators") or {}).get("quote") or [{}])[0].get("close") or []
    except (AttributeError, IndexError, TypeError):
        return [], None
    lech = int(so_hoac_none(meta.get("gmtoffset")) or 0)
    ra = []
    for t, g in zip(ts, dong):
        g = so_hoac_none(g)
        if g is None or g <= 0:
            continue
        ngay = dt.datetime.fromtimestamp(int(t) + lech, dt.timezone.utc).date()
        ra.append((ngay.isoformat(), g))
    tuc = None
    gia = so_hoac_none(meta.get("regularMarketPrice"))
    luc = so_hoac_none(meta.get("regularMarketTime"))
    if gia is not None and gia > 0 and luc:
        tuc = (dt.datetime.fromtimestamp(int(luc), dt.timezone.utc), gia)
    return ra, tuc


class NguonGiaGoc(Nguon):
    """Giá cổ phiếu gốc — Yahoo chart. Trả `[(ngày, đóng)]`; giá tức thời
    nằm ở `self.tucThoi[ma]` sau mỗi lượt đọc thành công."""

    ten = "yahoo-gia-goc"

    def __init__(self) -> None:
        super().__init__()
        self.tucThoi: dict = {}

    async def doc(self, client, ma: str = "") -> list:
        if not ma:
            return []
        t0 = time.perf_counter()
        try:
            r = await client.get(YAHOO_CHART.format(ma=ma),
                                 headers={"User-Agent": UA_TRINH_DUYET})
            r.raise_for_status()
            ra, tuc = doc_yahoo_chart(r.json())
            if not ra:
                raise ValueError("JSON không có dãy giá đóng")
        except Exception as e:                                # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
        if tuc is not None:
            self.tucThoi[ma] = tuc
        self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        return ra


# ── RPC pool V3 ──────────────────────────────────────────────────────────

SEL = {
    "slot0": "0x3850c7bd", "liquidity": "0x1a686502", "fee": "0xddca3f43",
    "token0": "0x0dfe1681", "token1": "0xd21220a7",
    "decimals": "0x313ce567", "symbol": "0x95d89b41",
}
Q96 = 2 ** 96


def giai_ma_uint(hexData: str, viTri: int = 0) -> int:
    h = str(hexData)[2:] if str(hexData).startswith("0x") else str(hexData)
    return int(h[viTri * 64:(viTri + 1) * 64] or "0", 16)


def giai_ma_int24(hexData: str, viTri: int) -> int:
    v = giai_ma_uint(hexData, viTri)
    return v - (1 << 256) if v >= (1 << 255) else v


def giai_ma_chuoi(hexData: str) -> str:
    """ABI `string` — hoặc `bytes32` với token cổ (chép cả hai dạng)."""
    h = str(hexData)[2:] if str(hexData).startswith("0x") else str(hexData)
    if len(h) == 64:
        return bytes.fromhex(h).rstrip(b"\x00").decode("utf-8", "replace")
    try:
        lech = int(h[:64], 16) * 2
        dai = int(h[lech:lech + 64], 16) * 2
        return bytes.fromhex(h[lech + 64:lech + 64 + dai]).decode("utf-8", "replace")
    except (ValueError, IndexError):
        return ""


def gia_tu_sqrt(sqrtPriceX96: int, thapPhan0: int, thapPhan1: int) -> float:
    """Giá token1 mỗi token0, đã bù thập phân."""
    p = (sqrtPriceX96 / Q96) ** 2
    return p * (10 ** (thapPhan0 - thapPhan1))


class NguonRpcPool(Nguon):
    """Đọc MỘT pool. Kết quả đã xoay để `gia` là USD mỗi token cổ phiếu."""

    ten = "rpc-x-layer-pool"

    def __init__(self, rpc: list) -> None:
        super().__init__()
        self.rpc = list(rpc)
        self._tokenCache: dict = {}

    async def _goi(self, client, url, to, data):
        r = await client.post(url, json={"jsonrpc": "2.0", "id": 1,
                                         "method": "eth_call",
                                         "params": [{"to": to, "data": data},
                                                    "latest"]})
        r.raise_for_status()
        j = r.json()
        if "error" in j:
            raise RuntimeError(j["error"])
        return j.get("result") or "0x"

    async def _token(self, client, url, dia):
        if dia in self._tokenCache:
            return self._tokenCache[dia]
        d = giai_ma_uint(await self._goi(client, url, dia, SEL["decimals"]))
        s = giai_ma_chuoi(await self._goi(client, url, dia, SEL["symbol"]))
        self._tokenCache[dia] = (d, s)
        return d, s

    async def doc(self, client, diaChi: str = "", kyHieuCo: str = "") -> list:
        if not diaChi:
            return []
        t0 = time.perf_counter()
        loi = None
        for url in self.rpc:
            try:
                s0 = await self._goi(client, url, diaChi, SEL["slot0"])
                sqrtP = giai_ma_uint(s0, 0)
                tick = giai_ma_int24(s0, 1)
                L = giai_ma_uint(await self._goi(client, url, diaChi, SEL["liquidity"]))
                phi = giai_ma_uint(await self._goi(client, url, diaChi, SEL["fee"]))
                t0a = "0x" + (await self._goi(client, url, diaChi, SEL["token0"]))[-40:]
                t1a = "0x" + (await self._goi(client, url, diaChi, SEL["token1"]))[-40:]
                d0, s0n = await self._token(client, url, t0a)
                d1, s1n = await self._token(client, url, t1a)
                gia01 = gia_tu_sqrt(sqrtP, d0, d1)
                # Xoay: muốn USD mỗi token cổ. Token cổ là token có ký hiệu
                # trùng `kyHieuCo`, hoặc token KHÔNG phải USD nếu chưa khai.
                coLaToken0 = (s0n.upper() == kyHieuCo.upper() if kyHieuCo
                              else not s0n.upper().startswith("USD"))
                gia = gia01 if coLaToken0 else (1.0 / gia01 if gia01 else None)
                self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
                return [{"diaChi": diaChi, "sqrtPriceX96": sqrtP, "tick": tick,
                         "thanhKhoan": L, "phiBps": phi / 100.0,
                         "token0": {"diaChi": t0a, "thapPhan": d0, "kyHieu": s0n},
                         "token1": {"diaChi": t1a, "thapPhan": d1, "kyHieu": s1n},
                         "coLaToken0": coLaToken0, "gia01": gia01, "gia": gia,
                         "rpc": url,
                         "lucMs": time.time() * 1000.0}]
            except Exception as e:                            # noqa: BLE001
                loi = e
                continue
        self.suc_khoe.ghi_loi(loi or RuntimeError("không RPC nào trả lời"))
        return []


# ── RSS ──────────────────────────────────────────────────────────────────

def doc_rss(vanBan: str) -> list:
    """`[{tieuDe, lienKet, luc}]` từ RSS 2.0 hoặc Atom. Lỗi XML → rỗng."""
    try:
        goc = ET.fromstring(vanBan)
    except ET.ParseError:
        return []
    ra = []
    for it in goc.iter():
        tag = it.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        d = {}
        for c in it:
            t = c.tag.split("}")[-1]
            if t == "title":
                d["tieuDe"] = (c.text or "").strip()
            elif t == "link":
                d["lienKet"] = (c.text or c.get("href") or "").strip()
            elif t in ("pubDate", "published", "updated"):
                d["luc"] = (c.text or "").strip()
        if d.get("tieuDe"):
            ra.append(d)
    return ra


class NguonRss(Nguon):
    ten = "rss-tin"

    async def doc(self, client, url: str = "", ma: str = "") -> list:
        if not url:
            return []
        t0 = time.perf_counter()
        try:
            r = await client.get(url)
            r.raise_for_status()
            ra = doc_rss(r.text)
        except Exception as e:                                # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
        self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        for x in ra:
            x["ma"] = ma
        return ra
