"""SỔ TIN — tiêu đề tin theo mã, gắn cờ, chống trùng, và có tuổi.

Ty này không đọc hiểu tin; nó chỉ làm ba việc máy làm được mà không bịa:

    1. giữ tiêu đề + liên kết, chống trùng theo liên kết
    2. gắn cờ theo TỪ KHOÁ — `ket-qua-kinh-doanh`, `fomc`, `tam-ngung`,
       `chia-tach`, `thu-hoi` — để sổ luật hỏi «có cờ nặng nào trong 24 giờ
       không» mà không cần model
    3. liên hệ tin với pool đang theo, qua mã cổ phiếu gốc

Một cờ là một GỢI Ý để người đọc, không phải một phán quyết: máy gắn cờ
`ket-qua-kinh-doanh` cho tiêu đề «NVDA earnings preview» và người quyết có
khai ngày vào `ketQuaKinhDoanh` hay không.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

from .config import THU_MUC

DUONG_TIN = THU_MUC / "tin.jsonl"

CO = (
    ("ket-qua-kinh-doanh", re.compile(r"\b(earnings|quarterly results|guidance|EPS)\b", re.I)),
    ("fomc", re.compile(r"\b(FOMC|Fed|rate (cut|hike)|Powell)\b", re.I)),
    ("tam-ngung", re.compile(r"\b(halt|halted|delist|suspend)", re.I)),
    ("chia-tach", re.compile(r"\b(stock split|split)\b", re.I)),
    ("thu-hoi", re.compile(r"\b(recall|lawsuit|SEC (probe|investigation))\b", re.I)),
    ("sap-nhap", re.compile(r"\b(acquire|acquisition|merger|buyout)\b", re.I)),
)
CO_NANG = ("ket-qua-kinh-doanh", "tam-ngung", "chia-tach")


def gan_co(tieuDe: str) -> list:
    return [ma for ma, rx in CO if rx.search(tieuDe or "")]


def _doc_luc(s: str) -> dt.datetime | None:
    if not s:
        return None
    for f in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
              "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            t = dt.datetime.strptime(s.strip(), f)
            return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
        except ValueError:
            continue
    return None


class SoTin:
    def __init__(self, duong: Path | None = None, giuNgay: int = 14) -> None:
        self.duong = duong or DUONG_TIN
        self.giuNgay = giuNgay
        self._tin: dict[str, dict] = {}
        self._nap()

    def _nap(self) -> None:
        if not self.duong.exists():
            return
        for dong in self.duong.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(dong)
            except ValueError:
                continue
            if d.get("lienKet"):
                self._tin[d["lienKet"]] = d

    def them(self, ds: list) -> int:
        """Thêm tin mới, trả số dòng MỚI. Tin trùng liên kết bỏ qua."""
        moi = []
        for x in ds:
            lk = (x.get("lienKet") or "").strip()
            if not lk or lk in self._tin:
                continue
            t = _doc_luc(x.get("luc", ""))
            d = {"lienKet": lk, "tieuDe": x.get("tieuDe", ""),
                 "ma": (x.get("ma") or "").upper(),
                 "luc": (t or dt.datetime.now(dt.timezone.utc)).isoformat(),
                 "co": gan_co(x.get("tieuDe", ""))}
            self._tin[lk] = d
            moi.append(d)
        if moi:
            self.duong.parent.mkdir(parents=True, exist_ok=True)
            with self.duong.open("a", encoding="utf-8") as f:
                for d in moi:
                    f.write(json.dumps(d, ensure_ascii=False) + "\n")
        return len(moi)

    def moi_nhat(self, ma: str | None = None, n: int = 8) -> list:
        han = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=self.giuNgay)
        ra = []
        for d in self._tin.values():
            if ma and d.get("ma") != ma.upper():
                continue
            try:
                t = dt.datetime.fromisoformat(d["luc"])
            except ValueError:
                continue
            if t >= han:
                ra.append(d)
        ra.sort(key=lambda d: d["luc"], reverse=True)
        return ra[:n]

    def co_nang_gan_day(self, ma: str, gio: float = 24.0) -> list:
        han = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=gio)
        ra = []
        for d in self.moi_nhat(ma, 50):
            try:
                t = dt.datetime.fromisoformat(d["luc"])
            except ValueError:
                continue
            if t >= han and any(c in CO_NANG for c in d.get("co", ())):
                ra.append(d)
        return ra

    def tom_tat(self) -> dict:
        return {"soTin": len(self._tin), "giuNgay": self.giuNgay}
