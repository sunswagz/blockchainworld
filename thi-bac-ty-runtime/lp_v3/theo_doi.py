"""SỔ VỊ THẾ của NGƯỜI — máy không đặt lệnh, người đặt ở OKX rồi ghi vào đây.

Chương trình thưởng đòi thêm thanh khoản qua trang OKX, và ty này không có
ví. Nên vòng đời một vị thế là:

    người mở ở OKX  →  `mo()` ghi sổ  →  máy theo dõi mỗi lượt
                    →  máy khuyên     →  người rút ở OKX  →  `dong()` ghi kết cục

Sổ là JSONL chỉ-thêm (`data/lp-v3/vi-the.jsonl`): mở là một dòng, đóng là
một dòng khác trỏ vào mã mở. Không sửa dòng cũ — cùng luật Sổ Cái.

Mỗi lần đóng ghi cả PHÍ THU và THƯỞNG THU người đọc từ OKX, vì đó là hai
con số ĐO ĐƯỢC duy nhất trong cả đường: mọi thứ khác ở ty này là mô hình,
và sổ kinh nghiệm lấy khoảng cách giữa mô hình với hai con số ấy làm bài
học.
"""
from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from .config import THU_MUC
from .mo_hinh import gia_tri, il_tai_gia, so_luong, thanh_khoan_tu_do_la

DUONG_SO = THU_MUC / "vi-the.jsonl"


def _bay_gio() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(
        timespec="seconds").replace("+00:00", "Z")


@dataclass
class ViThe:
    ma: str
    kyHieu: str
    Pa: float
    Pb: float
    vonUsd: float
    giaMo: float
    moLuc: str
    L: float
    ghiChu: str = ""
    maQuyetDinh: str = ""          # quyết định nào của máy dẫn tới lần mở này
    #: `tay` = người ghi ở buồng lái · `chuoi` = đọc từ NFT trong ví
    nguon: str = "tay"
    tokenId: str | None = None
    phiChoThuUsd: float | None = None      # phí chưa thu, đo bằng collect mô phỏng
    giaTriChuoiUsd: float | None = None    # giá trị đọc thẳng từ chuỗi
    dongLuc: str | None = None
    giaDong: float | None = None
    phiThuUsd: float | None = None
    thuongThuUsd: float | None = None
    lyDoDong: str = ""

    @property
    def dangMo(self) -> bool:
        return self.dongLuc is None

    def danh_gia(self, giaHienTai: float) -> dict:
        """Trạng thái ở giá này: trong dải?, giá trị, IL so HODL, hai lượng.

        Vị thế đọc từ chuỗi có thể KHÔNG biết giá mở (mint ngoài dải, hoặc
        RPC không cho `eth_getLogs`): IL và lệch giá là None, không phải 0."""
        x, y = so_luong(self.L, giaHienTai, self.Pa, self.Pb)
        coGiaMo = self.giaMo is not None and self.giaMo > 0
        return {"trongDai": self.Pa < giaHienTai < self.Pb,
                "giaTriUsd": gia_tri(self.L, giaHienTai, self.Pa, self.Pb),
                "ilPct": (il_tai_gia(self.L, self.giaMo, giaHienTai, self.Pa, self.Pb) * 100.0
                          if coGiaMo else None),
                "x": x, "y": y,
                "lechGiaPct": (giaHienTai / self.giaMo - 1.0) * 100.0 if coGiaMo else None,
                "gioGiu": _gio_tu(self.moLuc) if self.moLuc else None,
                "nguon": self.nguon, "tokenId": self.tokenId,
                "phiChoThuUsd": self.phiChoThuUsd,
                # HIỆU QUẢ VỐN (Bài 2): phí trên mỗi đô la vốn, quy về THÁNG.
                # Pool $10.000 kiếm $300 thua pool $2.000 kiếm $180. Chỉ tính
                # được khi biết phí và giờ giữ; phí chưa thu là phí từ lần
                # thu cuối, nên đây là CẬN DƯỚI khi đã từng thu.
                "hieuQuaVonThangPct": (
                    self.phiChoThuUsd / self.vonUsd * (720.0 / _gio_tu(self.moLuc)) * 100.0
                    if (self.phiChoThuUsd is not None and self.vonUsd and self.moLuc
                        and _gio_tu(self.moLuc) > 1.0) else None)}

    def tom_tat(self) -> dict:
        return {k: getattr(self, k) for k in (
            "ma", "kyHieu", "Pa", "Pb", "vonUsd", "giaMo", "moLuc", "L",
            "ghiChu", "maQuyetDinh", "dongLuc", "giaDong", "phiThuUsd",
            "thuongThuUsd", "lyDoDong", "nguon", "tokenId", "phiChoThuUsd",
            "giaTriChuoiUsd")} | {"dangMo": self.dangMo}


def _gio_tu(iso: str) -> float:
    try:
        t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return 0.0
    return (dt.datetime.now(dt.timezone.utc) - t).total_seconds() / 3600.0


class SoViThe:
    def __init__(self, duong: Path | None = None) -> None:
        self.duong = duong or DUONG_SO
        self._vt: dict[str, ViThe] = {}
        self._nap()

    def _nap(self) -> None:
        if not self.duong.exists():
            return
        for dong in self.duong.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(dong)
            except ValueError:
                continue
            if d.get("loai") == "mo":
                v = {k: d[k] for k in d if k != "loai" and k in ViThe.__dataclass_fields__}
                self._vt[d["ma"]] = ViThe(**v)
            elif d.get("loai") == "dong" and d.get("ma") in self._vt:
                x = self._vt[d["ma"]]
                x.dongLuc, x.giaDong = d.get("luc"), d.get("giaDong")
                x.phiThuUsd, x.thuongThuUsd = d.get("phiThuUsd"), d.get("thuongThuUsd")
                x.lyDoDong = d.get("lyDoDong", "")

    def _ghi(self, d: dict) -> None:
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        with self.duong.open("a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    def mo(self, kyHieu: str, Pa: float, Pb: float, vonUsd: float,
           giaMo: float, ghiChu: str = "", maQuyetDinh: str = "",
           moLuc: str | None = None) -> ViThe:
        if not (0 < Pa < Pb) or not (giaMo > 0) or not (vonUsd > 0):
            raise ValueError("dải, giá mở và vốn phải dương, Pa < Pb")
        v = ViThe(ma=uuid.uuid4().hex[:10], kyHieu=kyHieu, Pa=float(Pa),
                  Pb=float(Pb), vonUsd=float(vonUsd), giaMo=float(giaMo),
                  moLuc=moLuc or _bay_gio(),
                  L=thanh_khoan_tu_do_la(float(vonUsd), float(giaMo),
                                         float(Pa), float(Pb)),
                  ghiChu=ghiChu, maQuyetDinh=maQuyetDinh)
        self._vt[v.ma] = v
        self._ghi({"loai": "mo", **{k: getattr(v, k) for k in (
            "ma", "kyHieu", "Pa", "Pb", "vonUsd", "giaMo", "moLuc", "L",
            "ghiChu", "maQuyetDinh")}})
        return v

    def dong(self, ma: str, giaDong: float, phiThuUsd: float | None = None,
             thuongThuUsd: float | None = None, lyDoDong: str = "") -> ViThe:
        v = self._vt.get(ma)
        if v is None:
            raise KeyError(f"không có vị thế {ma!r}")
        if not v.dangMo:
            raise ValueError(f"vị thế {ma} đã đóng lúc {v.dongLuc}")
        v.dongLuc, v.giaDong = _bay_gio(), float(giaDong)
        v.phiThuUsd = None if phiThuUsd is None else float(phiThuUsd)
        v.thuongThuUsd = None if thuongThuUsd is None else float(thuongThuUsd)
        v.lyDoDong = lyDoDong
        self._ghi({"loai": "dong", "ma": ma, "luc": v.dongLuc,
                   "giaDong": v.giaDong, "phiThuUsd": v.phiThuUsd,
                   "thuongThuUsd": v.thuongThuUsd, "lyDoDong": lyDoDong})
        return v

    def dang_mo(self, kyHieu: str | None = None) -> list:
        return [v for v in self._vt.values()
                if v.dangMo and (kyHieu is None or v.kyHieu == kyHieu)]

    def da_dong(self) -> list:
        return [v for v in self._vt.values() if not v.dangMo]

    def lay(self, ma: str) -> ViThe | None:
        return self._vt.get(ma)

    def tom_tat(self) -> dict:
        return {"soDangMo": len(self.dang_mo()), "soDaDong": len(self.da_dong()),
                "vonDangMoUsd": sum(v.vonUsd for v in self.dang_mo())}


def ket_cuc(v: ViThe) -> dict | None:
    """Kết cục ĐO ĐƯỢC của một vị thế đã đóng — đầu vào của sổ kinh nghiệm.

    `laiLoUsd` = giá trị lúc đóng − vốn + phí + thưởng; IL tách riêng để bài
    học phân biệt được «mô hình IL sai» với «phí thấp hơn dự». Phí hoặc
    thưởng người chưa ghi thì để None và tổng cũng None — không cộng 0.
    """
    if v.dangMo or v.giaDong is None:
        return None
    dg = v.danh_gia(v.giaDong)
    giaTri = dg["giaTriUsd"]
    hodl = sum(a * b for a, b in zip(so_luong(v.L, v.giaMo, v.Pa, v.Pb),
                                     (v.giaDong, 1.0)))
    ilUsd = giaTri - hodl
    tong = None
    if v.phiThuUsd is not None:
        tong = giaTri - v.vonUsd + v.phiThuUsd + (v.thuongThuUsd or 0.0)
    gio = 0.0
    try:
        a = dt.datetime.fromisoformat(v.moLuc.replace("Z", "+00:00"))
        b = dt.datetime.fromisoformat(v.dongLuc.replace("Z", "+00:00"))
        gio = max(0.0, (b - a).total_seconds() / 3600.0)
    except ValueError:
        pass
    return {"ma": v.ma, "kyHieu": v.kyHieu, "gioGiu": gio,
            "vangDai": not (v.Pa < v.giaDong < v.Pb),
            "ilUsd": ilUsd, "ilBps": ilUsd / v.vonUsd * 10_000.0,
            "phiThuUsd": v.phiThuUsd, "thuongThuUsd": v.thuongThuUsd,
            "laiLoUsd": tong,
            "laiLoBps": None if tong is None else tong / v.vonUsd * 10_000.0,
            "giaDoiPct": dg["lechGiaPct"]}
