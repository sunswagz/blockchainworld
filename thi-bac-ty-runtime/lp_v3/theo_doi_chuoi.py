"""VỊ THẾ TRÊN CHUỖI — đọc NFT Uniswap V3 trong ví NGƯỜI, chỉ bằng địa chỉ công khai.

Vị thế thêm qua OKX DeFi là một NFT của `NonfungiblePositionManager` nằm
trong ví người vận hành. Biết địa chỉ ví là đọc được hết: dải (tick), thanh
khoản, phí chưa thu, token nào — không khoá, không ký, không lệnh. Đây là
đúng ranh giới hiến pháp cho phép: ty THEO DÕI, không cầm ví.

## Bốn phép đọc, và một mẹo

    balanceOf(ví) · tokenOfOwnerByIndex(ví, i)   liệt kê tokenId
    positions(tokenId)                            12 trường của vị thế
    factory().getPool(token0, token1, fee)        pool → slot0 (giá, tick)
    collect(...) qua eth_call TỪ ví               phí CHƯA THU thật

Mẹo cuối: `collect` là hàm ghi, nhưng `eth_call` với `from = ví` mô phỏng
nó và trả về đúng (amount0, amount1) sẽ nhận — không cần tự tính từ
feeGrowth. Không giao dịch nào rời máy.

## Địa chỉ hợp đồng quản lý vị thế KHÔNG đoán

Uniswap V3 trên X Layer (chainId 196) KHÔNG nằm ở địa chỉ canonical
(`0xC364…FE88` không có mã, đo 05/09/2026). Nên địa chỉ phải đến từ một
trong hai chỗ, theo thứ tự: người khai `quanLyViThe`, hoặc suy từ BIÊN NHẬN
của một giao dịch thêm thanh khoản (`txMau`): log `IncreaseLiquidity` phát
ra từ đúng hợp đồng ấy. Không có cả hai thì module này nói «chưa biết hợp
đồng» — không quét bừa.

## Hướng giá

Pool tính token1 mỗi token0; ta cần USD mỗi cổ. Token «cổ» là token có ký
hiệu KHÔNG bắt đầu bằng USD. Nếu cổ là token1 thì mọi giá đảo và hai mép
dải đổi chỗ — chỗ dễ sai nhất, có phép kiểm riêng.
"""
from __future__ import annotations

import datetime as dt
import math
import time

from thi_bac_ty.nguon import Nguon

from .mo_hinh import thanh_khoan_tu_do_la
from .nguon import Q96, giai_ma_chuoi, giai_ma_int24, giai_ma_uint

SEL = {
    "balanceOf": "0x70a08231", "tokenOfOwnerByIndex": "0x2f745c59",
    "positions": "0x99fbab88", "factory": "0xc45a0155", "getPool": "0x1698ee82",
    "collect": "0xfc6f7865", "slot0": "0x3850c7bd",
    "decimals": "0x313ce567", "symbol": "0x95d89b41",
    "allowance": "0xdd62ed3e",
}
#: Trên ngần này thì coi là VÔ HẠN (Bài 6 §12): 2^255 — mọi ví «approve max»
#: đều ở đây hoặc cao hơn.
QUYEN_VO_HAN = 1 << 255
#: keccak("IncreaseLiquidity(uint256,uint128,uint256,uint256)")
TOPIC_INCREASE = "0x3067048beee31b25b2f1681f88dac838c8bba36af25bfb2b7cf7473a5847e35f"
UINT128_MAX = (1 << 128) - 1
#: Nhiều nhất ngần này vị thế SỐNG được trả về, và nhiều nhất `TRAN_QUET`
#: NFT được soi — từ MỚI NHẤT về cũ. Đo 05/09/2026 trên X Layer: ví của bot
#: có 1.287 NFT mà gần hết đã rút cạn (L = 0) — quét từ đầu danh sách là
#: soi 30 cái xác rồi kết luận «không có vị thế», trong khi vị thế sống
#: nằm ở cuối.
TRAN_VI_THE = 30
TRAN_QUET = 60
#: Trên ngần này vị thế thì KHÔNG đi tìm giá vào qua `eth_getLogs` — mỗi
#: vị thế tốn hai lời gọi nặng, và RPC công cộng trả 429 (đo 05/09/2026:
#: một ví 30 NFT làm cả lượt chết ở nút thứ hai). Giá vào là None, không
#: phải 0, và báo cáo nói «chưa đọc được».
TRAN_DOC_GIA_VAO = 10
#: Nghỉ giữa hai lời gọi — nhịp mà rpc.xlayer.tech và xlayerrpc.okx.com
#: chịu được không kêu 429.
NGHI_GIUA_GOI_GIAY = 0.08


def ma_hoa_uint(n: int) -> str:
    return format(int(n) & ((1 << 256) - 1), "064x")


def ma_hoa_dia_chi(a: str) -> str:
    return str(a).lower().replace("0x", "").rjust(64, "0")


def giai_ma_positions(hexData: str) -> dict:
    """12 trường của `positions(tokenId)`, theo thứ tự ABI Uniswap V3."""
    return {
        "nonce": giai_ma_uint(hexData, 0),
        "operator": "0x" + format(giai_ma_uint(hexData, 1), "040x"),
        "token0": "0x" + format(giai_ma_uint(hexData, 2), "040x"),
        "token1": "0x" + format(giai_ma_uint(hexData, 3), "040x"),
        "fee": giai_ma_uint(hexData, 4),
        "tickLower": giai_ma_int24(hexData, 5),
        "tickUpper": giai_ma_int24(hexData, 6),
        "liquidity": giai_ma_uint(hexData, 7),
        "feeGrowthInside0": giai_ma_uint(hexData, 8),
        "feeGrowthInside1": giai_ma_uint(hexData, 9),
        "tokensOwed0": giai_ma_uint(hexData, 10),
        "tokensOwed1": giai_ma_uint(hexData, 11),
    }


def tim_quan_ly_tu_bien_nhan(bienNhan: dict) -> str | None:
    """Địa chỉ phát log `IncreaseLiquidity` trong biên nhận — chính là
    NonfungiblePositionManager. `None` nếu giao dịch không có log ấy."""
    for lg in (bienNhan or {}).get("logs") or []:
        tp = lg.get("topics") or []
        if tp and str(tp[0]).lower() == TOPIC_INCREASE:
            return str(lg.get("address")).lower()
    return None


def so_luong_tho(L: int, sqrtP: float, tickLower: int, tickUpper: int) -> tuple:
    """(amount0, amount1) THÔ ở giá `sqrtP` (đã chia 2^96), kẹp ngoài dải."""
    sa = 1.0001 ** (tickLower / 2.0)
    sb = 1.0001 ** (tickUpper / 2.0)
    if sqrtP <= sa:
        return L * (sb - sa) / (sa * sb), 0.0
    if sqrtP >= sb:
        return 0.0, L * (sb - sa)
    return L * (sb - sqrtP) / (sqrtP * sb), L * (sqrtP - sa)


def gia_vao_tu_so_luong(amount1: int, L: int, tickLower: int) -> float | None:
    """√P lúc mint suy từ `amount1 = L(√P − √Pa)` — chỉ khi mint TRONG dải
    (amount1 > 0). Trả √P thô, hoặc None."""
    if not L or not amount1 or amount1 <= 0:
        return None
    return amount1 / L + 1.0001 ** (tickLower / 2.0)


def huong_gia(sqrtP: float, tickLower: int, tickUpper: int, d0: int, d1: int,
              coLaToken0: bool) -> tuple:
    """`(P, Pa, Pb)` USD mỗi cổ, đã bù thập phân và đã XOAY nếu cổ là token1."""
    he = 10 ** (d0 - d1)
    p01 = (sqrtP ** 2) * he
    pa01 = (1.0001 ** tickLower) * he
    pb01 = (1.0001 ** tickUpper) * he
    if coLaToken0:
        return p01, pa01, pb01
    return 1.0 / p01, 1.0 / pb01, 1.0 / pa01


class DocViTheChuoi(Nguon):
    ten = "rpc-vi-the-chuoi"

    def __init__(self, rpc: list) -> None:
        super().__init__()
        self.rpc = list(rpc)
        self._token: dict = {}
        self._pool: dict = {}
        self.loiCuoiChiTiet: str | None = None
        self.soNftTrongVi: int | None = None
        self.soNftDaSoi = 0
        self.soNftRong = 0
        #: quyền token của ví với hợp đồng quản lý vị thế — điền sau mỗi lượt
        self.quyenToken: list = []

    async def _rpc(self, client, url, method, params):
        """Một lời gọi, thử LẦN LƯỢT mọi nút bắt đầu từ `url`; 429 thì nghỉ
        rồi sang nút kế. Thử theo từng lời gọi chứ không theo cả lượt: lượt
        30 vị thế × 8 lời gọi mà đổi nút giữa chừng rồi làm lại từ đầu là
        tự gấp đôi tải lên đúng nút vừa kêu quá tải."""
        import asyncio
        await asyncio.sleep(NGHI_GIUA_GOI_GIAY)
        thu = [url] + [u for u in self.rpc if u != url]
        loi = None
        for u in thu:
            try:
                r = await client.post(u, json={"jsonrpc": "2.0", "id": 1,
                                               "method": method, "params": params})
                if r.status_code == 429:
                    await asyncio.sleep(1.0)
                    raise RuntimeError(f"429 ở {u}")
                r.raise_for_status()
                j = r.json()
                if "error" in j:
                    raise RuntimeError(str(j["error"])[:200])
                return j.get("result")
            except Exception as e:                            # noqa: BLE001
                loi = e
                self.loiCuoiChiTiet = f"{method} @ {u}: {type(e).__name__}: {e}"[:300]
                continue
        raise RuntimeError(self.loiCuoiChiTiet or str(loi))

    async def _goi(self, client, url, to, data, tu=None):
        th = {"to": to, "data": data}
        if tu:
            th["from"] = tu
        return await self._rpc(client, url, "eth_call", [th, "latest"]) or "0x"

    async def _tk(self, client, url, dia):
        if dia not in self._token:
            d = giai_ma_uint(await self._goi(client, url, dia, SEL["decimals"]))
            s = giai_ma_chuoi(await self._goi(client, url, dia, SEL["symbol"]))
            self._token[dia] = (d, s)
        return self._token[dia]

    async def quan_ly_tu_tx(self, client, txHash: str) -> str | None:
        for url in self.rpc:
            try:
                bn = await self._rpc(client, url, "eth_getTransactionReceipt", [txHash])
                return tim_quan_ly_tu_bien_nhan(bn)
            except Exception as e:                            # noqa: BLE001
                self.loiCuoiChiTiet = f"{type(e).__name__}: {e}"
                continue
        return None

    async def doc(self, client, vi: str = "", quanLy: str = "") -> list:
        if not vi or not quanLy:
            return []
        t0 = time.perf_counter()
        if not self.rpc:
            self.suc_khoe.ghi_loi(RuntimeError("không có RPC nào trong config"))
            return []
        try:
            ra = await self._doc_mot(client, self.rpc[0], vi.lower(), quanLy.lower())
        except Exception as e:                                # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
        self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        return ra

    async def _doc_mot(self, client, url, vi, quanLy) -> list:
        so = giai_ma_uint(await self._goi(client, url, quanLy, SEL["balanceOf"] + ma_hoa_dia_chi(vi)))
        nhaMay = "0x" + (await self._goi(client, url, quanLy, SEL["factory"]))[-40:]
        docGiaVao = int(so) <= TRAN_DOC_GIA_VAO
        self.soNftTrongVi = int(so)
        self.soNftDaSoi = 0
        self.soNftRong = 0
        ra = []
        for i in range(int(so) - 1, max(-1, int(so) - 1 - TRAN_QUET), -1):
            if len(ra) >= TRAN_VI_THE:
                break
            self.soNftDaSoi += 1
            tid = giai_ma_uint(await self._goi(
                client, url, quanLy, SEL["tokenOfOwnerByIndex"] + ma_hoa_dia_chi(vi) + ma_hoa_uint(i)))
            vt = giai_ma_positions(await self._goi(client, url, quanLy, SEL["positions"] + ma_hoa_uint(tid)))
            if vt["liquidity"] == 0 and vt["tokensOwed0"] == 0 and vt["tokensOwed1"] == 0:
                self.soNftRong += 1
                continue                      # NFT rỗng — đã rút hết, chưa đốt
            d0, s0 = await self._tk(client, url, vt["token0"])
            d1, s1 = await self._tk(client, url, vt["token1"])
            khoa = (vt["token0"], vt["token1"], vt["fee"])
            if khoa not in self._pool:
                self._pool[khoa] = "0x" + (await self._goi(
                    client, url, nhaMay, SEL["getPool"] + ma_hoa_dia_chi(vt["token0"])
                    + ma_hoa_dia_chi(vt["token1"]) + ma_hoa_uint(vt["fee"])))[-40:]
            pool = self._pool[khoa]
            s0raw = await self._goi(client, url, pool, SEL["slot0"])
            sqrtP = giai_ma_uint(s0raw, 0) / Q96
            tick = giai_ma_int24(s0raw, 1)
            coLaToken0 = not s0.upper().startswith("USD")
            P, Pa, Pb = huong_gia(sqrtP, vt["tickLower"], vt["tickUpper"], d0, d1, coLaToken0)
            a0, a1 = so_luong_tho(vt["liquidity"], sqrtP, vt["tickLower"], vt["tickUpper"])
            a0h, a1h = a0 / 10 ** d0, a1 / 10 ** d1
            co, usd = (a0h, a1h) if coLaToken0 else (a1h, a0h)
            giaTri = co * P + usd
            # phí chưa thu: mô phỏng collect(tokenId, ví, max, max) TỪ ví
            phi0 = phi1 = None
            try:
                dulieu = (SEL["collect"] + ma_hoa_uint(tid) + ma_hoa_dia_chi(vi)
                          + ma_hoa_uint(UINT128_MAX) + ma_hoa_uint(UINT128_MAX))
                kq = await self._goi(client, url, quanLy, dulieu, tu=vi)
                phi0 = giai_ma_uint(kq, 0) / 10 ** d0
                phi1 = giai_ma_uint(kq, 1) / 10 ** d1
            except Exception:                                 # noqa: BLE001
                pass
            phiUsd = None
            if phi0 is not None:
                pc, pu = (phi0, phi1) if coLaToken0 else (phi1, phi0)
                phiUsd = pc * P + pu
            # giá và giờ VÀO — từ log IncreaseLiquidity đầu tiên của tokenId
            giaMo = moLuc = None
            try:
                if not docGiaVao:
                    raise RuntimeError("ví đông — bỏ qua đọc giá vào")
                logs = await self._rpc(client, url, "eth_getLogs", [{
                    "fromBlock": "0x0", "toBlock": "latest", "address": quanLy,
                    "topics": [TOPIC_INCREASE, "0x" + ma_hoa_uint(tid)]}])
                if logs:
                    lg = logs[0]
                    Lm = giai_ma_uint(lg["data"], 0)
                    am1 = giai_ma_uint(lg["data"], 2)
                    sq = gia_vao_tu_so_luong(am1, Lm, vt["tickLower"])
                    if sq:
                        giaMo = huong_gia(sq, vt["tickLower"], vt["tickUpper"], d0, d1, coLaToken0)[0]
                    kh = await self._rpc(client, url, "eth_getBlockByNumber", [lg["blockNumber"], False])
                    if kh and kh.get("timestamp"):
                        moLuc = dt.datetime.fromtimestamp(int(kh["timestamp"], 16), dt.timezone.utc
                                                          ).isoformat(timespec="seconds").replace("+00:00", "Z")
            except Exception:                                 # noqa: BLE001
                pass
            ra.append({
                "tokenId": str(tid), "quanLy": quanLy, "pool": pool,
                "kyHieu": f"{(s0 if coLaToken0 else s1)}-{(s1 if coLaToken0 else s0)}",
                "kyHieuCo": s0 if coLaToken0 else s1, "coLaToken0": coLaToken0,
                "phiBps": vt["fee"] / 100.0, "tickLower": vt["tickLower"],
                "tickUpper": vt["tickUpper"], "tick": tick,
                "thanhKhoanTho": str(vt["liquidity"]),
                "gia": P, "Pa": Pa, "Pb": Pb, "trongDai": Pa < P < Pb,
                "soCo": co, "soUsd": usd, "giaTriUsd": giaTri,
                "phiChoThuUsd": phiUsd, "giaMo": giaMo, "moLuc": moLuc,
                "L": thanh_khoan_tu_do_la(giaTri, P, Pa, Pb) if giaTri > 0 else 0.0,
                "lucMs": time.time() * 1000.0,
            })
        # QUYỀN TOKEN (Bài 6 §12–14): với mỗi token đã gặp trong vị thế, hỏi
        # allowance(ví, hợp đồng quản lý). Chỉ đọc được người tiêu ta BIẾT;
        # người tiêu lạ cần log Approval mà RPC công cộng không cho quét từ
        # khối 0 — khai là chưa đọc được, không khai là «không có».
        self.quyenToken = []
        for dia, (d, s) in list(self._token.items()):
            try:
                raw = giai_ma_uint(await self._goi(
                    client, url, dia, SEL["allowance"] + ma_hoa_dia_chi(vi) + ma_hoa_dia_chi(quanLy)))
            except Exception:                                 # noqa: BLE001
                continue
            self.quyenToken.append({
                "token": dia, "kyHieu": s, "nguoiTieu": quanLy, "vaiNguoiTieu": "quan-ly-vi-the",
                "soLuong": None if raw >= QUYEN_VO_HAN else raw / 10 ** d,
                "voHan": raw >= QUYEN_VO_HAN, "conQuyen": raw > 0})
        return ra


def thanh_vi_the(d: dict):
    """Dict đọc từ chuỗi → `theo_doi.ViThe` (nguồn `chuoi`), để cùng một
    đường cân với vị thế ghi tay."""
    from .theo_doi import ViThe
    return ViThe(ma=f"nft-{d['tokenId']}", kyHieu=d["kyHieu"], Pa=d["Pa"], Pb=d["Pb"],
                 vonUsd=d["giaTriUsd"], giaMo=d.get("giaMo"), moLuc=d.get("moLuc") or "",
                 L=d["L"], ghiChu=f"NFT #{d['tokenId']} · pool {d['pool'][:10]}…",
                 nguon="chuoi", tokenId=d["tokenId"], phiChoThuUsd=d.get("phiChoThuUsd"),
                 giaTriChuoiUsd=d["giaTriUsd"])


def _main() -> int:
    """`python -m lp_v3.theo_doi_chuoi 0xVÍ [0xTX | 0xQUANLY]` — thử một lượt."""
    import asyncio
    import json
    import sys

    import httpx

    from .config import nap
    vi = sys.argv[1] if len(sys.argv) > 1 else ""
    them = sys.argv[2] if len(sys.argv) > 2 else ""
    cfg = nap()
    doc = DocViTheChuoi(cfg.get("rpc") or [])

    async def chay():
        async with httpx.AsyncClient(timeout=25) as c:
            ql = them if len(them) == 42 else ""
            if len(them) == 66:
                ql = await doc.quan_ly_tu_tx(c, them) or ""
                print("quản lý vị thế suy từ tx:", ql or "KHÔNG tìm thấy log IncreaseLiquidity")
            ql = ql or (cfg.get("vi") or {}).get("quanLyViThe") or ""
            if not ql:
                print("chưa biết hợp đồng quản lý vị thế — đưa tx thêm thanh khoản hoặc địa chỉ")
                return 1
            ds = await doc.doc(c, vi, ql)
            print(json.dumps(ds, ensure_ascii=False, indent=1, default=str))
            print("sức khoẻ:", doc.suc_khoe.tom_tat(), doc.loiCuoiChiTiet or "")
            return 0
    return asyncio.run(chay())


if __name__ == "__main__":
    raise SystemExit(_main())
