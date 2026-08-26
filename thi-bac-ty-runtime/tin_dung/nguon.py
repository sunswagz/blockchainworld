"""Nguồn: DefiLlama Yields. Chỉ dữ liệu CÔNG KHAI, không khoá nào.

Hai đường, và phải GHÉP chúng lại mới đủ:

    /pools        apyBase, apyReward, tvlUsd, chain, project, symbol
    /lendBorrow   totalSupplyUsd, totalBorrowUsd, ltv       ← khoá theo `pool`

Đường thứ hai là đường quan trọng: không có `totalSupply − totalBorrow` thì
không biết **rút ra được bao nhiêu**, và một cơ hội cho vay mà không biết
đường ra là một cơ hội chưa đo được rủi ro chính của nó.

Ghép theo `pool` (id của DefiLlama). Pool nào chỉ có ở một bảng thì BỎ, và
số bị bỏ đếm ra được — bỏ trong im lặng thì một ngày nguồn đổi khoá, ta sẽ
thấy "hôm nay thị trường không có gì" thay vì thấy "ta đang mù".
"""
from __future__ import annotations

import time

from thi_bac_ty.nguon import Nguon, so_hoac_none

from .models import ThiTruongVay

DUONG_POOLS = "https://yields.llama.fi/pools"
DUONG_LENDBORROW = "https://yields.llama.fi/lendBorrow"


class DefiLlama(Nguon):
    ten = "defillama"

    def __init__(self) -> None:
        super().__init__()
        self.soBoVìThieuGhep = 0
        self.soDoc = 0

    async def doc(self, client, taiSan=(), chuoi=()) -> list[ThiTruongVay]:
        """Đọc một lượt, trả về các thị trường ĐÃ GHÉP đủ hai bảng."""
        t0 = time.perf_counter()
        try:
            po, lb = await _hai_duong(client)
        except Exception as e:                            # noqa: BLE001
            self.suc_khoe.ghi_loi(e)
            return []
        self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        self.soDoc += 1

        # TVL toàn giao thức, cộng TRƯỚC khi lọc — lọc rồi mới cộng thì
        # Aave chỉ còn TVL của mấy pool stablecoin ta quan tâm, và rủi ro
        # hợp đồng lại bị suy từ một con số không phải của giao thức.
        tvl_gt: dict[str, float] = {}
        for x in po:
            k = x.get("project")
            v = so_hoac_none(x.get("tvlUsd"))
            if k and v:
                tvl_gt[k] = tvl_gt.get(k, 0.0) + v

        muon_ts = {t.upper() for t in taiSan} if taiSan else None
        muon_ch = {c.lower() for c in chuoi} if chuoi else None
        vay = {x.get("pool"): x for x in lb if x.get("pool")}

        ra: list[ThiTruongVay] = []
        bo = 0
        for p in po:
            sym = (p.get("symbol") or "").upper()
            ch = p.get("chain") or ""
            if muon_ts is not None and sym not in muon_ts:
                continue
            if muon_ch is not None and ch.lower() not in muon_ch:
                continue
            goc = so_hoac_none(p.get("apyBase"))
            if goc is None:
                continue
            v = vay.get(p.get("pool"))
            if v is None:
                # Không ghép được thì KHÔNG dựng thị trường: thiếu bảng vay
                # là thiếu đúng con số nói ta rút ra được bao nhiêu.
                bo += 1
                continue
            ra.append(ThiTruongVay(
                ma=str(p.get("pool")),
                giaoThuc=str(p.get("project") or "?"),
                chuoi=str(ch or "?"),
                taiSan=sym or "?",
                apyGocPhanTram=goc,
                apyThuongPhanTram=so_hoac_none(p.get("apyReward")) or 0.0,
                tvlUsd=so_hoac_none(p.get("tvlUsd")) or 0.0,
                tvlGiaoThucUsd=tvl_gt.get(p.get("project")),
                tongCungUsd=so_hoac_none(v.get("totalSupplyUsd")),
                tongVayUsd=so_hoac_none(v.get("totalBorrowUsd")),
            ))
        self.soBoVìThieuGhep = bo
        return ra

    def tom_tat(self) -> dict:
        return {**self.suc_khoe.tom_tat(),
                "soDoc": self.soDoc,
                "soBoViThieuGhep": self.soBoVìThieuGhep,
                "duong": [DUONG_POOLS, DUONG_LENDBORROW]}


async def _hai_duong(client):
    """Hỏi hai đường SONG SONG.

    Không phải để nhanh: hỏi tuần tự là hai ảnh chụp ở hai thời điểm, rồi
    ghép chúng như thể cùng lúc. Cùng lý do `bac/vong.py` hỏi bốn cảng song
    song — và cùng cái lỗi mà `dong_ho.py` sinh ra để chặn.
    """
    import asyncio
    a, b = await asyncio.gather(client.get(DUONG_POOLS),
                                client.get(DUONG_LENDBORROW))
    a.raise_for_status()
    b.raise_for_status()
    return _mang(a.json()), _mang(b.json())


def _mang(d):
    if isinstance(d, dict):
        d = d.get("data", [])
    return d if isinstance(d, list) else []
