"""Sổ nhật ký và thống kê — và bốn con số phải đứng cạnh tỉ lệ thắng.

Tỉ lệ thắng một mình là con số dễ khoe nhất và ít nghĩa nhất trong cả hệ
thống. `powerwinner` có tỉ lệ thắng 51% mà vẫn lãi lớn; một bot cận-kết-quả
có tỉ lệ thắng 99,7% mà vẫn có thể lỗ sạch. Nên ở đây tỉ lệ thắng KHÔNG BAO
GIỜ được trả về một mình — hàm `thong_ke()` luôn kèm:

    kỳ vọng        P(thắng)xTBthắng - P(thua)xTBthua - phí
    thua lớn nhất  một lần sai xoá bao nhiêu lần thắng
    đuôi           trung bình 5% lần tệ nhất
    số lần thua    hiếm không có nghĩa là nhỏ
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .config import DATA_DIR


@dataclass
class GhiKetToan:
    """Một market đã kết toán — đơn vị của mọi phép hậu kiểm."""
    luc: str
    ma: str
    upThang: bool
    coUp: float
    coDown: float
    tienVao: float          # tổng đã trả
    tienRa: float           # tổng nhận về khi kết toán
    phiUsd: float
    laiLo: float
    giaCap: float | None
    chienThuat: list[str] = field(default_factory=list)
    pDuDoan: float | None = None


class So:
    def __init__(self, duong: Path | None = None) -> None:
        self.duong = duong or (DATA_DIR / "ket-toan.jsonl")
        self.duong.parent.mkdir(parents=True, exist_ok=True)

    def ghi(self, g: GhiKetToan) -> None:
        with self.duong.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(g), ensure_ascii=False) + "\n")

    def doc(self, gioiHan: int | None = None) -> list[dict]:
        if not self.duong.exists():
            return []
        ra = []
        with self.duong.open(encoding="utf-8") as f:
            for d in f:
                d = d.strip()
                if not d:
                    continue
                try:
                    ra.append(json.loads(d))
                except json.JSONDecodeError:
                    continue
        return ra[-gioiHan:] if gioiHan else ra


def thong_ke(ds: list[dict]) -> dict:
    """Thống kê đầy đủ. Không bao giờ trả tỉ lệ thắng mà thiếu phần đuôi."""
    if not ds:
        return {"n": 0, "chuaCo": True}

    lai = [float(g.get("laiLo") or 0.0) for g in ds]
    thang = [x for x in lai if x > 0]
    thua = [x for x in lai if x < 0]
    n = len(lai)

    tb_thang = sum(thang) / len(thang) if thang else 0.0
    tb_thua = abs(sum(thua) / len(thua)) if thua else 0.0
    p_thang = len(thang) / n

    ky_vong = p_thang * tb_thang - (1 - p_thang) * tb_thua

    # đuôi: trung bình 5% lần tệ nhất (ít nhất 1 mẫu)
    sap = sorted(lai)
    k = max(1, int(n * 0.05))
    duoi = sum(sap[:k]) / k

    thua_lon_nhat = min(lai) if lai else 0.0
    # một lần thua lớn nhất xoá bao nhiêu lần thắng trung bình
    xoa = abs(thua_lon_nhat) / tb_thang if tb_thang > 0 else None

    tk = {
        "n": n,
        "chuaCo": False,
        "tiLeThang": p_thang,
        "soThang": len(thang),
        "soThua": len(thua),
        "tbThang": tb_thang,
        "tbThua": tb_thua,
        "kyVong": ky_vong,
        "tongLaiLo": sum(lai),
        "tongPhi": sum(float(g.get("phiUsd") or 0.0) for g in ds),
        "thuaLonNhat": thua_lon_nhat,
        "xoaBaoNhieuLanThang": xoa,
        "duoi5pct": duoi,
        "canhBaoDuoi": xoa is not None and xoa > 20,
    }
    # CÂU cảnh báo đi kèm NGAY TRONG DỮ LIỆU, không để mỗi chỗ hiển thị
    # tự viết lại. `dong_canh_bao` có sẵn từ đầu và KHÔNG AI GỌI — trong
    # khi `web/app.js` chép tay đúng câu ấy bằng JavaScript. Hai bản của
    # một câu thì sớm muộn lệch nhau, và câu này là thứ chặn người đọc
    # hiểu sai con số nguy hiểm nhất trong cả hệ: TỈ LỆ THẮNG.
    #
    # Vào dữ liệu thì mọi nơi hiện `tiLeThang` — buồng lái, ảnh chụp
    # công khai, bất cứ thứ gì đọc `/api/trang-thai` — đều có nó đi kèm,
    # không ai phải nhớ tự thêm.
    tk["canhBao"] = dong_canh_bao(tk)
    return tk


def dong_canh_bao(tk: dict) -> str | None:
    """Một câu tiếng người cho phần đuôi. None nếu chưa đủ dữ liệu."""
    if tk.get("chuaCo") or not tk.get("canhBaoDuoi"):
        return None
    return (f"tỉ lệ thắng {tk['tiLeThang']:.1%} nhưng MỘT lần thua lớn nhất "
            f"xoá {tk['xoaBaoNhieuLanThang']:.0f} lần thắng — "
            f"tỉ lệ thắng ở đây không nói lên điều gì về an toàn")


def bay_gio() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
