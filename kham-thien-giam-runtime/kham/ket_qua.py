"""Sổ KẾT QUẢ theo slug — mảnh còn thiếu để chạy lại chấm được điểm.

## Chỗ hở

`chay_lai.mot_luot()` chấm mỗi khung bằng dòng này:

    that = tt.get("upThang")
    if that is None:
        continue

Nhưng băng ghi KHÔNG có `upThang`. Đo trên băng thật: 5.854 bản ghi thị
trường, **0 cái có kết quả**. Nên `soKhop` luôn bằng 0, `tongLaiLo` luôn
bằng 0, và cỗ máy chạy lại chưa từng chấm được một khung nào.

Hệ quả nặng hơn nó trông: **cổng của vòng tiến hoá dựa vào chạy lại để
phán một đề xuất là tốt hơn hay chỉ khác đi.** Cổng ấy chưa bao giờ có gì
để so. Đây là chỗ tắc thứ HAI, độc lập với chuyện "chưa có lệnh nào kết
toán" — sửa một cái không mở được cái kia.

## Vì sao băng không thể tự chứa kết quả

Băng ghi khung hình lúc nó ĐANG diễn ra. Kết quả thì mãi sau mới biết —
với khung 5 phút là năm phút sau, và lúc đó dòng băng cũ đã nằm im trong
một file gzip đã đóng. Không sửa ngược được, và cũng không nên: một cuốn
băng sửa được là một cuốn băng không tin được.

Nên kết quả đi sổ RIÊNG, nối với băng bằng `slug`.

## Và dựng lại được cho cả băng cũ

Kết quả một khung Up/Down là `giá đóng khung > giá mở khung`. Cả hai đều
lấy từ Binance, và `giaMo` thì băng đã ghi sẵn. Nghĩa là không cần
Polymarket để dựng lại kết quả cho mọi khung đã ghi — xem
`scripts/dung-ket-qua.py`.

Điều đó quan trọng hơn nghe tưởng: nó có nghĩa là băng đã ghi suốt tuần
qua KHÔNG mất, dù suốt thời gian đó chưa lệnh nào được đặt.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import DATA_DIR

DUONG = DATA_DIR / "ket-qua.jsonl"

#: `btc-updown-5m-1787243400` → mốc eventStart theo giây.
_SLUG_MOC = re.compile(r"-(\d{9,13})$")


def moc_tu_slug(slug: str) -> float | None:
    """Mốc eventStart (ms) đọc từ đuôi slug.

    Polymarket đặt slug khung ngắn theo mốc thời gian, nên slug tự nó là
    một cái đồng hồ. Dùng được chỗ này vì nó KHÔNG cần gọi mạng — băng cũ
    dựng lại được cả khi sàn không với tới.
    """
    m = _SLUG_MOC.search(slug or "")
    if not m:
        return None
    v = int(m.group(1))
    return float(v * 1000 if v < 1e12 else v)


def ket_thuc_tu_slug(slug: str, songGiay: float = 300.0) -> float | None:
    moc = moc_tu_slug(slug)
    return None if moc is None else moc + songGiay * 1000.0


class SoKetQua:
    """Nối băng với kết quả. Đọc một lần, tra bằng slug."""

    def __init__(self, duong: Path | None = None) -> None:
        self.duong = duong or DUONG
        self.o: dict[str, dict] = {}
        self._doc()

    def _doc(self) -> None:
        if not self.duong.exists():
            return
        for dong in self.duong.read_text(encoding="utf-8").splitlines():
            if not dong.strip():
                continue
            try:
                d = json.loads(dong)
            except json.JSONDecodeError:
                continue          # một dòng hỏng không được kéo cả sổ theo
            s = d.get("slug")
            if s:
                self.o[s] = d

    def them(self, slug: str, upThang: bool, giaMo: float | None = None,
             giaDong: float | None = None, nguon: str = "tu-tinh") -> None:
        if not slug:
            return
        d = {"slug": slug, "upThang": bool(upThang), "nguon": nguon}
        if giaMo is not None:
            d["giaMo"] = giaMo
        if giaDong is not None:
            d["giaDong"] = giaDong
        cu = self.o.get(slug)
        # Ghi đè im lặng là mất dấu bất đồng. Nếu đã có kết quả KHÁC cho
        # cùng một slug thì giữ cái cũ và đánh dấu — hai nguồn nói ngược
        # nhau là tin đáng đọc, không phải chuyện để dọn.
        if cu is not None and bool(cu.get("upThang")) != bool(upThang):
            cu["batDong"] = True
            cu["nguonKhac"] = nguon
            self._noi(cu)
            return
        if cu is not None:
            return
        self.o[slug] = d
        self._noi(d)

    def _noi(self, d: dict) -> None:
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        with self.duong.open("a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    def lay(self, slug: str) -> bool | None:
        d = self.o.get(slug)
        return None if d is None else bool(d.get("upThang"))

    def tom_tat(self) -> dict:
        bd = sum(1 for d in self.o.values() if d.get("batDong"))
        up = sum(1 for d in self.o.values() if d.get("upThang"))
        return {"soSlug": len(self.o), "soUp": up,
                "soDown": len(self.o) - up, "soBatDong": bd}


so_ket_qua = SoKetQua()
