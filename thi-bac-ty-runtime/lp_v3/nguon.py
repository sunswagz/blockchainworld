"""Ba nguồn CÔNG KHAI, không khoá — và mỗi nguồn để lại dấu khi hỏng.

    NguonStooq    giá đóng cửa hằng ngày cổ phiếu gốc (CSV, không khoá)
    NguonRpcPool  slot0 · liquidity · fee · decimals · symbol của pool V3
                  qua JSON-RPC thô — không web3, không ABI ngoài, năm
                  selector viết tay
    NguonRss      tiêu đề tin theo mã (RSS Yahoo)

Không nguồn nào được ném: hỏng thì `suc_khoe.ghi_loi` và trả rỗng, để lượt
quét vẫn đi tiếp trên những gì còn đọc được, và buồng lái hiện đúng con mắt
nào đang mù.

Chưa nguồn nào trong ba được thử SỐNG từ nơi viết file này (sandbox chặn
mọi đường ra). Hình dạng đầu vào — cột CSV Stooq, mã hoá ABI của slot0,
thẻ `item` RSS — đều là chuẩn công khai và có phép kiểm trên mẫu cố định;
nhưng lượt chạy đầu ở máy thật là lượt đo, không phải lượt tin.
"""
from __future__ import annotations

import datetime as dt
import time
import xml.etree.ElementTree as ET

from thi_bac_ty.nguon import Nguon, so_hoac_none

# ── Stooq ────────────────────────────────────────────────────────────────

STOOQ = "https://stooq.com/q/d/l/?s={ma}&i=d"


def doc_csv_stooq(vanBan: str) -> list:
    """`Date,Open,High,Low,Close,Volume` → `[(ngày, đóng)]`. Bỏ dòng hỏng."""
    ra = []
    for i, dong in enumerate(str(vanBan).splitlines()):
        o = [x.strip() for x in dong.split(",")]
        if i == 0 and o and o[0].lower() == "date":
            continue
        if len(o) < 5:
            continue
        gia = so_hoac_none(o[4])
        if gia is None or gia <= 0:
            continue
        try:
            dt.date.fromisoformat(o[0])
        except ValueError:
            continue
        ra.append((o[0], gia))
    return ra


class NguonStooq(Nguon):
    ten = "stooq-gia-goc"

    async def doc(self, client, ma: str = "") -> list:
        if not ma:
            return []
        t0 = time.perf_counter()
        try:
            r = await client.get(STOOQ.format(ma=ma))
            r.raise_for_status()
            ra = doc_csv_stooq(r.text)
            if not ra:
                raise ValueError("CSV rỗng hoặc không đúng cột")
        except Exception as e:                                # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
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
