"""Băng ghi và chạy lại — P0 của lộ trình, và nó phải làm TRƯỚC mô hình.

Lý do P0 đứng trước mọi thứ khác: nếu không lưu sổ lệnh, tick và fill ngay từ
đầu thì ba tháng nữa dù có muốn nghiên cứu cũng không có "ký ức thế giới" nào
để chạy lại. Mô hình viết sau lúc nào cũng được; dữ liệu không quay lại được.

Và không có chạy lại thì không có cách nào biết một thay đổi là TỐT HƠN hay
chỉ là KHÁC ĐI — đúng bài học đã ghi lại ở tu-cam-thanh-runtime.

Định dạng: JSONL một dòng một khung hình, gzip theo ngày. Cố ý thô sơ: thứ
cần là đọc lại được sau sáu tháng bằng bất cứ công cụ nào, không phải nhanh.
"""
from __future__ import annotations

import gzip
import json
import time
from dataclasses import dataclass
from pathlib import Path

from .config import CONFIG, ROOT

_B = CONFIG["bang"]


def _thu_muc() -> Path:
    p = Path(_B["thuMuc"])
    if not p.is_absolute():
        p = ROOT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


class MayGhi:
    """Ghi mỗi khung hình trạng thái xuống đĩa, gộp theo ngày."""

    def __init__(self) -> None:
        self.bat = bool(_B.get("ghi", True))
        self._ngay = ""
        self._f = None
        self.soKhung = 0

    def _mo(self):
        ngay = time.strftime("%Y-%m-%d", time.gmtime())
        if ngay != self._ngay:
            self.dong()
            self._ngay = ngay
            self._f = gzip.open(_thu_muc() / f"bang-{ngay}.jsonl.gz", "at",
                                encoding="utf-8")
        return self._f

    def ghi(self, khung: dict) -> None:
        if not self.bat:
            return
        try:
            f = self._mo()
            f.write(json.dumps(khung, ensure_ascii=False, separators=(",", ":")) + "\n")
            self.soKhung += 1
            # xả mỗi 50 khung — mất tối đa 50 khung nếu máy sập, đổi lại
            # không phải gọi fsync mỗi 2 giây suốt ngày
            if self.soKhung % 50 == 0:
                f.flush()
        except OSError:
            pass

    def dong(self) -> None:
        if self._f is not None:
            try:
                self._f.flush()
                self._f.close()
            except OSError:
                pass
            self._f = None

    def don_cu(self) -> int:
        """Xoá băng quá hạn giữ. Trả về số file đã xoá."""
        gio_han = time.time() - float(_B.get("ngayGiuLai", 30)) * 86400
        xoa = 0
        for p in _thu_muc().glob("bang-*.jsonl.gz"):
            try:
                if p.stat().st_mtime < gio_han:
                    p.unlink()
                    xoa += 1
            except OSError:
                pass
        return xoa


def doc_bang(tuNgay: str | None = None) -> list[dict]:
    """Đọc lại băng. `tuNgay` dạng YYYY-MM-DD; None = mọi ngày."""
    ra: list[dict] = []
    for p in sorted(_thu_muc().glob("bang-*.jsonl.gz")):
        if tuNgay and p.stem.replace("bang-", "").replace(".jsonl", "") < tuNgay:
            continue
        try:
            with gzip.open(p, "rt", encoding="utf-8") as f:
                for d in f:
                    d = d.strip()
                    if d:
                        try:
                            ra.append(json.loads(d))
                        except json.JSONDecodeError:
                            continue
        except OSError:
            continue
    return ra


# `chay_lai` cũ chỉ ĐẾM cơ hội đã ghi trong băng — nó trả về một con số
# trông như backtest nhưng không dựng lại được gì, nên không so được hai bộ
# tham số. Đã thay bằng `kham/chay_lai.py`, chạy lại theo sự kiện thật.
# Module này giờ chỉ còn lo việc GHI và ĐỌC băng.

may_ghi = MayGhi()
