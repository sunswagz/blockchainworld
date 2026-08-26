"""BẢN THAM SỐ — tham số có SỐ HIỆU, có lịch sử, và quay lui được.

Trước file này, tham số phân bổ nằm trong `config.json` và trong mặc định
của từng tầng. Đổi chúng là sửa tay một con số, không dấu vết: ba tháng sau
không ai trả lời được *"vì sao trần cảng là 0,45"* — và câu hỏi ấy là câu
đầu tiên người ta hỏi khi có một khoản lỗ.

## Vì sao phải có SỐ HIỆU, không chỉ có giá trị

    RESULT → DIAGNOSIS → PROPOSAL → OFFLINE TEST → ACCEPTANCE GATE
           → VERSIONED PARAMETER → LIVE

Ba mắt cuối chỉ có nghĩa khi tham số là một **bản** chứ không phải một con
số. Có bản thì mới nói được: *"lỗ này xảy ra dưới bản 7, bản 7 được nhận
ngày ấy vì phép đo kia, và quay về bản 6 là một lệnh chứ không phải một
buổi ngồi nhớ lại"*.

## Chỉ THÊM, không sửa — cùng luật với Sổ Cái

Quay lui **không** xoá bản sai. Nó ghi một bản MỚI có nội dung của bản cũ,
và ghi rõ nó quay lui từ đâu. Cùng lý do `so_cai.dao()` không cho `UPDATE`:
một lịch sử sửa được thì không còn là lịch sử.

## `nguoi` không có mặc định

Mọi hàm đổi tham số đều đòi tên người. Cùng luật với `cau_dao.dong_lai()`:
đổi cách chia tiền là hành động có trách nhiệm, và sổ phải ghi được ai làm.
Máy đo, máy đề xuất, máy chặn — nhưng máy không tự ký.
"""
from __future__ import annotations

import datetime as _dt
import json
import sqlite3
import threading
from dataclasses import dataclass, field
from pathlib import Path

KHUON = """
CREATE TABLE IF NOT EXISTS ban_tham_so (
  so       INTEGER PRIMARY KEY AUTOINCREMENT,
  luc      TEXT    NOT NULL,
  nguoi    TEXT    NOT NULL,
  vi       TEXT    NOT NULL,
  thamSo   TEXT    NOT NULL,
  doDuoc   TEXT    NOT NULL DEFAULT 'null',
  chaSo    INTEGER,
  quayLuiVe INTEGER
);
CREATE INDEX IF NOT EXISTS idx_bts_luc ON ban_tham_so(luc);
"""


def _bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


@dataclass(frozen=True)
class BanThamSo:
    so: int
    luc: str
    nguoi: str
    vi: str
    thamSo: dict
    doDuoc: dict | None = None
    chaSo: int | None = None
    quayLuiVe: int | None = None

    def tom_tat(self) -> dict:
        return {"so": self.so, "luc": self.luc, "nguoi": self.nguoi,
                "vi": self.vi, "thamSo": self.thamSo, "doDuoc": self.doDuoc,
                "chaSo": self.chaSo, "quayLuiVe": self.quayLuiVe}


class KhoThamSo:
    def __init__(self, duong: Path) -> None:
        self.duong = Path(duong)
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        self._khoa = threading.Lock()
        self.soLoiGhi = 0
        self.loiCuoi: str | None = None
        with self._mo() as con:
            con.executescript(KHUON)

    def _mo(self):
        return sqlite3.connect(self.duong, timeout=10.0)

    # ── ghi ───────────────────────────────────────────────────────────────
    def dat(self, thamSo: dict, nguoi: str, vi: str,
            doDuoc: dict | None = None,
            quayLuiVe: int | None = None) -> BanThamSo | None:
        """Ghi một bản MỚI. Trả về bản vừa ghi, hoặc None nếu ghi hỏng.

        `nguoi` và `vi` đều bắt buộc và đều phải có nội dung: một bản tham số
        không nói được ai đổi và vì sao thì đúng bằng không có lịch sử.
        """
        if not (nguoi or "").strip():
            self.soLoiGhi += 1
            self.loiCuoi = "thiếu tên người — đổi tham số là hành động có trách nhiệm"
            return None
        if not (vi or "").strip():
            self.soLoiGhi += 1
            self.loiCuoi = "thiếu lý do — một bản không giải thích được thì không kiểm toán được"
            return None
        cha = self.hien_hanh()
        luc = _bay_gio()
        try:
            with self._khoa, self._mo() as con:
                cur = con.execute(
                    "INSERT INTO ban_tham_so(luc,nguoi,vi,thamSo,doDuoc,"
                    "chaSo,quayLuiVe) VALUES(?,?,?,?,?,?,?)",
                    (luc, nguoi.strip(), vi.strip(),
                     json.dumps(thamSo, ensure_ascii=False),
                     json.dumps(doDuoc, ensure_ascii=False),
                     cha.so if cha else None, quayLuiVe))
                so = int(cur.lastrowid)
        except (sqlite3.Error, OSError, TypeError, ValueError) as e:
            self.soLoiGhi += 1
            self.loiCuoi = f"{type(e).__name__}: {e}"
            return None
        return BanThamSo(so, luc, nguoi.strip(), vi.strip(), thamSo, doDuoc,
                         cha.so if cha else None, quayLuiVe)

    def quay_lui(self, veSo: int, nguoi: str, vi: str = "") -> BanThamSo | None:
        """Quay về nội dung của bản `veSo` bằng cách ghi một bản MỚI.

        Không xoá bản sai, không sửa bản sai. Người đọc sau này thấy được cả
        bản đã sai lẫn việc nó đã bị quay lui — xoá đi thì chỉ thấy hiện tại.
        """
        cu = self.ban(veSo)
        if cu is None:
            self.soLoiGhi += 1
            self.loiCuoi = f"không có bản #{veSo}"
            return None
        return self.dat(cu.thamSo, nguoi,
                        vi.strip() or f"quay lui về bản #{veSo}",
                        {"quayLuiTu": (self.hien_hanh().so
                                       if self.hien_hanh() else None)},
                        quayLuiVe=veSo)

    # ── đọc ───────────────────────────────────────────────────────────────
    def _dung(self, r) -> BanThamSo:
        return BanThamSo(int(r[0]), r[1], r[2], r[3], _json(r[4]),
                         _json(r[5]), r[6], r[7])

    def hien_hanh(self) -> BanThamSo | None:
        try:
            with self._mo() as con:
                r = con.execute(
                    "SELECT so,luc,nguoi,vi,thamSo,doDuoc,chaSo,quayLuiVe "
                    "FROM ban_tham_so ORDER BY so DESC LIMIT 1").fetchone()
        except (sqlite3.Error, OSError):
            return None
        return self._dung(r) if r else None

    def ban(self, so: int) -> BanThamSo | None:
        try:
            with self._mo() as con:
                r = con.execute(
                    "SELECT so,luc,nguoi,vi,thamSo,doDuoc,chaSo,quayLuiVe "
                    "FROM ban_tham_so WHERE so=?", (int(so),)).fetchone()
        except (sqlite3.Error, OSError):
            return None
        return self._dung(r) if r else None

    def lich_su(self, n: int = 30) -> list[dict]:
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT so,luc,nguoi,vi,thamSo,doDuoc,chaSo,quayLuiVe "
                    "FROM ban_tham_so ORDER BY so DESC LIMIT ?",
                    (int(n),)).fetchall()
        except (sqlite3.Error, OSError):
            return []
        return [self._dung(r).tom_tat() for r in h]

    def khac_biet(self, a: int, b: int) -> dict:
        """Bản `b` đổi những núm nào so với bản `a`. Rỗng = không đổi gì."""
        ba, bb = self.ban(a), self.ban(b)
        if ba is None or bb is None:
            return {}
        ra: dict[str, dict] = {}
        for k in set(_phang(ba.thamSo)) | set(_phang(bb.thamSo)):
            x = _phang(ba.thamSo).get(k)
            y = _phang(bb.thamSo).get(k)
            if x != y:
                ra[k] = {"tu": x, "den": y}
        return ra

    def tom_tat(self) -> dict:
        h = self.hien_hanh()
        try:
            with self._mo() as con:
                n = con.execute("SELECT COUNT(*) FROM ban_tham_so").fetchone()[0]
        except (sqlite3.Error, OSError):
            n = 0
        return {"soBan": int(n or 0),
                "hienHanh": h.tom_tat() if h else None,
                "soLoiGhi": self.soLoiGhi, "loiCuoi": self.loiCuoi,
                "duong": self.duong.name}


def _phang(d: dict, tien: str = "") -> dict:
    """`{"a": {"b": 1}}` → `{"a.b": 1}`. Để so hai bản theo từng núm."""
    ra = {}
    for k, v in (d or {}).items():
        duong = f"{tien}.{k}" if tien else str(k)
        if isinstance(v, dict):
            ra.update(_phang(v, duong))
        else:
            ra[duong] = v
    return ra


def _json(s):
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return None
