"""VÒNG TIẾN HOÁ của ty V3 — vặn MỘT núm, chấm bằng chạy lại BĂNG, qua cổng.

Chép luật từ `bac/tien_hoa.py`, vì bốn luật ấy là bốn cách tự lừa đã bị bắt:

    1. cửa AN TOÀN không phải núm      (`config.CUA_AN_TOAN`)
    2. một lượt vặn ĐÚNG MỘT núm
    3. bước nhỏ, có trần, không ra ngoài khuôn
    4. nhận chỉ khi ĐỦ MẪU và cải thiện VƯỢT NHIỄU — đứng yên là hợp lệ

## Chạy lại băng chấm cái gì

Với mỗi mã có băng gốc đủ dày, trượt một cửa sổ qua lịch sử: ở mỗi ngày
`i`, đo σ từ 30 phiên trước, dựng dải `±k·σ√τ`, «vào» nếu (phí + thưởng)/LVR
qua ngưỡng, rồi xem `h` phiên sau: văng hay không, IL cuối cửa sổ, phí ×
phần trong dải. NET của một cửa sổ KHÔNG vào là 0 — nên điểm của bộ tham
số là **kỳ vọng NET trên mỗi CƠ HỘI**, và một ngưỡng quá chặt tự trả giá
bằng những cửa sổ nó bỏ qua.

Phí và thưởng lấy từ bảng pool HIỆN TẠI (khai tay) — tức chạy lại này giả
định APR của hôm nay đúng cho cả quá khứ. Đó là cái giá của không có băng
APR; phép chấm này so hai bộ tham số TRÊN CÙNG giả định ấy, nên nó vẫn
phân biệt được «dải hẹp hay rộng», không phân biệt được «APR thật là bao
nhiêu».

Thưởng KHÔNG đưa vào chạy lại: nó hết ngày 07/09 và vặn núm theo một con
số sắp biến mất là học một bài sẽ sai ngay tuần sau.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from . import bang_gia
from .config import CUA_AN_TOAN, THU_MUC
from .mo_hinh import (NGAY_GIAO_DICH_NAM, GIO_NAM, can_dai, dai_doi_xung,
                      il_tai_gia, rong_theo_sigma, sigma_nam,
                      thanh_khoan_tu_do_la)

SO_TIEN_HOA = THU_MUC / "tien-hoa.jsonl"

NUT_VAN = {
    "heSoDai":                {"min": 0.5, "max": 4.0},
    "giuGio":                 {"min": 12.0, "max": 240.0},
    "tiLePhiTrenLvrToiThieu": {"min": 1.0, "max": 4.0},
    "xacSuatVangToiDa":       {"min": 0.2, "max": 0.9},
}
BUOC_TOI_DA = 0.25
SAN_BUOC_KHUON = 0.05
TOI_THIEU_MAU = 30
#: bps kỳ vọng mỗi cơ hội — dưới ngần này là nhiễu
BIEN_VUOT = 5.0
SO_PHIEN_SIGMA = 30


def buoc_van(nut: str, hien: float) -> float:
    k = NUT_VAN[nut]
    return max(abs(hien) * BUOC_TOI_DA,
               (float(k["max"]) - float(k["min"])) * SAN_BUOC_KHUON)


def kep(nut: str, gia: float) -> float:
    k = NUT_VAN[nut]
    return max(float(k["min"]), min(float(k["max"]), gia))


@dataclass
class KetQuaChayLai:
    soCuaSo: int = 0
    soVao: int = 0
    netMoiCoHoiBps: float | None = None     # trung bình trên MỌI cửa sổ
    netMoiLanVaoBps: float | None = None
    tiLeVang: float | None = None
    net: list = field(default_factory=list)  # từng cửa sổ, để ghép cặp A/B

    def tom_tat(self) -> dict:
        return {"soCuaSo": self.soCuaSo, "soVao": self.soVao,
                "netMoiCoHoiBps": self.netMoiCoHoiBps,
                "netMoiLanVaoBps": self.netMoiLanVaoBps,
                "tiLeVang": self.tiLeVang}


def chay_lai(nut: dict, bang: dict, aprPhi: dict) -> KetQuaChayLai:
    """`bang`: `{mã: [giá đóng…]}`; `aprPhi`: `{mã: APR phí gốc (tỉ lệ)}`.
    Mã thiếu APR thì bỏ — không đoán."""
    k = float(nut["heSoDai"])
    h = max(1, int(round(float(nut["giuGio"]) / 24.0 * NGAY_GIAO_DICH_NAM / 365.0)))
    nguong = float(nut["tiLePhiTrenLvrToiThieu"])
    tranVang = float(nut["xacSuatVangToiDa"])
    kq = KetQuaChayLai()
    vang = 0
    for ma, g in bang.items():
        apr = aprPhi.get(ma)
        if apr is None or len(g) < SO_PHIEN_SIGMA + h + 2:
            continue
        for i in range(SO_PHIEN_SIGMA, len(g) - h):
            s = sigma_nam(g[i - SO_PHIEN_SIGMA:i + 1], 10)
            if s is None or s <= 0:
                continue
            P0 = g[i]
            tau = h / NGAY_GIAO_DICH_NAM
            rong = rong_theo_sigma(s, tau, k)
            Pa, Pb = dai_doi_xung(P0, rong)
            kd = can_dai(P0, Pa, Pb, s, tau, h * 24.0 * 365.0 / NGAY_GIAO_DICH_NAM,
                         apr, None, None, 1.0, 0.0, 1.0)
            kq.soCuaSo += 1
            if (kd.tiLePhiTrenLvr is None or kd.tiLePhiTrenLvr < nguong
                    or kd.xacSuatVang["tong"] > tranVang):
                kq.net.append(0.0)
                continue
            L = thanh_khoan_tu_do_la(1.0, P0, Pa, Pb)
            duong = g[i + 1:i + 1 + h]
            trong = sum(1 for x in duong if Pa < x < Pb)
            ra = next((x for x in duong if not (Pa < x < Pb)), None)
            giaCuoi = duong[-1] if ra is None else ra
            il = il_tai_gia(L, P0, giaCuoi, Pa, Pb) * 10_000.0
            phi = (apr * kd.hieuSuat * (h / NGAY_GIAO_DICH_NAM)
                   * (trong / h) * 10_000.0)
            kq.net.append(phi + il)
            kq.soVao += 1
            if ra is not None:
                vang += 1
    if kq.soCuaSo:
        kq.netMoiCoHoiBps = sum(kq.net) / kq.soCuaSo
    if kq.soVao:
        kq.netMoiLanVaoBps = sum(x for x in kq.net if x != 0.0) / kq.soVao
        kq.tiLeVang = vang / kq.soVao
    return kq


def doi_chieu(a: KetQuaChayLai, b: KetQuaChayLai) -> dict:
    """A/B ghép theo CỬA SỔ. Cải thiện = trung bình (b − a); nhiễu = 2 sai
    số chuẩn của hiệu ghép cặp."""
    n = min(len(a.net), len(b.net))
    if n == 0:
        return {"n": 0, "caiThien": None, "nhieu": None, "hon": False}
    d = [b.net[i] - a.net[i] for i in range(n)]
    tb = sum(d) / n
    se = (math.sqrt(sum((x - tb) ** 2 for x in d) / (n - 1) / n)
          if n > 1 else float("inf"))
    return {"n": n, "caiThien": tb, "nhieu": 2.0 * se,
            "hon": n >= TOI_THIEU_MAU and tb > max(BIEN_VUOT, 2.0 * se)}


def mot_luot(nut: dict, bang: dict, aprPhi: dict) -> dict:
    """Thử mỗi núm hai chiều, chọn cái cải thiện nhiều nhất, xét cổng."""
    for c in CUA_AN_TOAN:
        if c in NUT_VAN:
            raise RuntimeError(f"cửa an toàn {c} lọt vào NUT_VAN")
    goc = chay_lai(nut, bang, aprPhi)
    tot = None
    thu = []
    for ten in NUT_VAN:
        hien = float(nut[ten])
        for chieu in (-1.0, 1.0):
            moi = kep(ten, hien + chieu * buoc_van(ten, hien))
            if abs(moi - hien) < 1e-12:
                continue
            ungVien = dict(nut, **{ten: moi})
            kq = chay_lai(ungVien, bang, aprPhi)
            dc = doi_chieu(goc, kq)
            thu.append({"nut": ten, "tu": hien, "den": moi, **dc,
                        "ketQua": kq.tom_tat()})
            if dc["hon"] and (tot is None or dc["caiThien"] > tot["caiThien"]):
                tot = thu[-1]
    ra = {"luc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
          "goc": goc.tom_tat(), "thu": thu, "nhan": tot,
          "ketLuan": ("NHẬN " + f"{tot['nut']} {tot['tu']:.3g} → {tot['den']:.3g} "
                      f"(+{tot['caiThien']:.1f} bps/cơ hội, nhiễu ±{tot['nhieu']:.1f}, "
                      f"n={tot['n']})" if tot else
                      ("TRẢ LẠI — " + ("chưa đủ mẫu" if goc.soCuaSo < TOI_THIEU_MAU
                                        else "không núm nào vượt nhiễu; đứng yên là hợp lệ")))}
    return ra


def ghi_so(ra: dict, duong: Path | None = None) -> None:
    p = duong or SO_TIEN_HOA
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ra, ensure_ascii=False) + "\n")


def doc_so(duong: Path | None = None, n: int = 20) -> list:
    p = duong or SO_TIEN_HOA
    if not p.exists():
        return []
    ra = []
    for dong in p.read_text(encoding="utf-8").splitlines()[-n:]:
        try:
            ra.append(json.loads(dong))
        except ValueError:
            continue
    return ra


def bang_tu_dia(danhSachMa: list, thuMuc: Path | None = None) -> dict:
    return {ma: bang_gia.dong_cua_goc(ma, None, thuMuc) for ma in danhSachMa}
