"""GAS — giá gas thật của bốn chuỗi, từ RPC công khai, không cần khoá.

`eth_gasPrice` trả về wei mỗi đơn vị gas. Muốn ra đô thì cần ba thứ, và
thiếu bất kỳ thứ nào là trả `None`:

    gasPrice (wei)  ×  gasLimit (ước lượng)  ×  giá token gốc (USD)

Thứ ba là chỗ dễ nói dối nhất. `lai_suat/` và `tin_dung/` có giá ETH ở đâu
đó, nhưng đi lấy giá từ một ty là ty gọi ty — điều luật chung cấm. Nên gói
này nhận giá từ NGOÀI VÀO (`giaGocUsd`), và không có giá thì nó nói không
đo được chứ không đoán.

Vì sao không dựng oracle EIP-1559 nhiều tầng: ta không đặt lệnh on-chain
nào cả. Con số ở đây để TRỪ VÀO NET của một cơ hội — để trả lời "dời vốn
tới đó có còn lãi không". Sai một tầng ưu tiên thì lệch vài phần trăm của
một khoản vài đô; quên hẳn gas thì lệch cả trăm phần trăm.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from thi_bac_ty.nguon import Nguon, nguyen_hoac_none

#: RPC công khai, không khoá. Thử ngày 27/08/2026, cả bốn đều trả lời.
RPC = {
    "ethereum": "https://ethereum-rpc.publicnode.com",
    "arbitrum": "https://arbitrum-one-rpc.publicnode.com",
    "base": "https://base-rpc.publicnode.com",
    "polygon": "https://polygon-bor-rpc.publicnode.com",
}

#: Token trả gas của từng chuỗi. Bên gọi phải đưa giá USD của token này.
TOKEN_GOC = {
    "ethereum": "ETH", "arbitrum": "ETH", "base": "ETH", "polygon": "POL",
}

#: `chainId` của LI.FI, để `cau_noi.py` khỏi giữ một bảng thứ hai.
CHAIN_ID = {"ethereum": 1, "arbitrum": 42161, "base": 8453, "polygon": 137}

#: Ước lượng gasLimit theo LOẠI VIỆC, không theo chuỗi — cùng một `transfer`
#: ERC-20 tốn xấp xỉ như nhau ở mọi chuỗi EVM. Đây là ƯỚC LƯỢNG, và mọi
#: chặng dùng nó đều khai `gas-limit-uoc-luong` trong `khongDoDuoc`.
GAS_LIMIT = {
    "chuyen-erc20": 65_000,
    "duyet-erc20": 46_000,
    "gui-vao-cau": 150_000,
    "gui-native": 21_000,
    # Swap trên một AMM có đường đi phức tạp (Pendle PT, Curve nhiều chặng)
    # tốn hơn `transfer` một bậc. Con số này là ƯỚC LƯỢNG THÔ và mọi chặng
    # dùng nó đều khai `gas-limit-uoc-luong` — nhưng ước 350k rồi khai ra
    # vẫn đúng hơn hẳn coi một lượt swap tốn bằng một lượt chuyển.
    "doi-tren-amm": 350_000,
}


@dataclass(frozen=True)
class GiaGas:
    chuoi: str
    weiMoiGas: int | None
    docLucMs: float
    loi: str = ""

    @property
    def gweiMoiGas(self) -> float | None:
        return None if self.weiMoiGas is None else self.weiMoiGas / 1e9

    def tuoi_giay(self, nowMs: float | None = None) -> float:
        now = nowMs if nowMs is not None else time.time() * 1000.0
        return (now - self.docLucMs) / 1000.0

    def usd(self, viec: str, giaGocUsd: float | None) -> float | None:
        """Đô cho một việc. `None` nếu thiếu gas HOẶC thiếu giá token gốc.

        Thiếu giá token mà vẫn trả một con số là ngầm giả định giá bằng 1 —
        đúng loại lỗi mà "None khác 0" sinh ra để chặn.
        """
        lim = GAS_LIMIT.get(viec)
        if (self.weiMoiGas is None or lim is None
                or giaGocUsd is None or giaGocUsd <= 0):
            return None
        return self.weiMoiGas * lim / 1e18 * giaGocUsd

    def tom_tat(self) -> dict:
        return {"chuoi": self.chuoi, "gwei": self.gweiMoiGas,
                "tuoiGiay": self.tuoi_giay(), "loi": self.loi}


class NguonGas(Nguon):
    """Đọc `eth_gasPrice` của bốn chuỗi, song song. Lỗi một chuỗi không
    giết cả lượt — nó thành `weiMoiGas=None`, và cái None ấy chảy lên tận
    `TuyenDuong.phiUsd`."""

    ten = "gas-rpc"

    def __init__(self) -> None:
        super().__init__()
        self.gia: dict[str, GiaGas] = {}
        #: Bao nhiêu lần một lượt đọc hỏng mà ta GIỮ LẠI số cũ. Không đếm
        #: thì "vẫn có gas" và "gas đã cũ" trông giống hệt nhau.
        self.soGiuLai = 0

    async def doc(self, client, chuoi=None) -> dict[str, GiaGas]:
        t0 = time.perf_counter()
        ten = list(chuoi or RPC)
        ra = await asyncio.gather(*(_mot(client, c) for c in ten),
                                  return_exceptions=True)
        tot = 0
        for c, r in zip(ten, ra):
            if isinstance(r, GiaGas) and r.weiMoiGas is not None:
                self.gia[c] = r
                tot += 1
                continue
            # Một lượt RPC hỏng KHÔNG được xoá số đọc được lần trước. Gas
            # đổi theo block, nhưng bậc của nó thì không — và số cũ vẫn
            # dùng được hơn hẳn không có số nào.
            #
            # Đổi lại: số cũ TỰ già đi qua `docLucMs`, nên `tuoi_giay()`
            # nói ra tuổi thật thay vì trẻ lại mỗi lượt hỏi.
            cu = self.gia.get(c)
            if cu is not None and cu.weiMoiGas is not None:
                self.soGiuLai += 1
                continue
            self.gia[c] = GiaGas(
                c, None, time.time() * 1000.0,
                f"{type(r).__name__}: {r}" if isinstance(r, BaseException)
                else (r.loi if isinstance(r, GiaGas) else "trống"))
        if tot:
            self.suc_khoe.ghi_ok((time.perf_counter() - t0) * 1000.0)
        else:
            self.suc_khoe.ghi_loi(RuntimeError("không chuỗi nào trả lời"))
        return self.gia

    def tom_tat(self) -> dict:
        return {**self.suc_khoe.tom_tat(), "soGiuLai": self.soGiuLai,
                "theoChuoi": {c: g.tom_tat() for c, g in self.gia.items()}}


async def _mot(client, chuoi: str) -> GiaGas:
    now = time.time() * 1000.0
    u = RPC.get(chuoi)
    if u is None:
        return GiaGas(chuoi, None, now, f"chưa khai RPC cho chuỗi {chuoi!r}")
    r = await client.post(u, json={"jsonrpc": "2.0", "id": 1,
                                   "method": "eth_gasPrice", "params": []})
    r.raise_for_status()
    v = (r.json() or {}).get("result")
    if not isinstance(v, str) or not v.startswith("0x"):
        return GiaGas(chuoi, None, now, f"`result` không phải hex: {v!r}")
    try:
        w = int(v, 16)
    except ValueError:
        return GiaGas(chuoi, None, now, f"hex hỏng: {v!r}")
    # Gas 0 là RPC hỏng, không phải chuỗi miễn phí.
    n = nguyen_hoac_none(w)
    return GiaGas(chuoi, n if (n or 0) > 0 else None, now,
                  "" if (n or 0) > 0 else f"gasPrice = {w}, coi như hỏng")
