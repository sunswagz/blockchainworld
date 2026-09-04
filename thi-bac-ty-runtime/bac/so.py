"""Sổ quét — mọi lượt quét đều ghi lại, kể cả lượt không có cơ hội nào.

Ghi cả lượt trống là chủ ý, và nó quan trọng hơn vẻ ngoài: một tuần không cơ
hội nào là một PHÁT HIỆN (chênh lệch đã đóng, hoặc phí đã ăn hết biên), không
phải một tuần không có dữ liệu. Sổ chỉ ghi lượt "có hàng" sẽ dựng nên một lịch
sử toàn ngày đẹp trời, và mọi phép thống kê trên đó đều lệch theo cùng một
hướng.

Đây là P0 của cả runtime, cùng lý do băng ghi là P0 của Khâm Thiên Giám: không
có lịch sử funding thì không cách nào phân biệt

    30 → 21 → 12 → 3 → 0        chênh lệch đang tắt, vào là muộn
    25 → 28 → 22 → 31 → 27      chênh lệch dai, đáng săn

Hai chuỗi ấy có cùng một giá trị HIỆN TẠI ở vài điểm, và một scanner chỉ nhìn
ảnh chụp lúc này không tài nào tách được chúng.

SQLite chứ không phải JSONL vì ở đây cần TRUY VẤN theo (mã, cặp sàn, khoảng
thời gian) để tính độ dai — đọc tuần tự cả file mỗi lần hỏi thì không dùng
được. Bù lại phải chấp nhận một định dạng nhị phân; `payload` giữ nguyên JSON
để sáu tháng sau vẫn đọc lại được bằng bất cứ công cụ nào.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from thi_bac_ty.nho_tam import NhoTam

from .config import DATA_DIR
from .models import CoHoi

KHUON = """
CREATE TABLE IF NOT EXISTS luot (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  lucMs     INTEGER NOT NULL,
  soBaoGia  INTEGER NOT NULL,
  soCoHoi   INTEGER NOT NULL,
  soDuyet   INTEGER NOT NULL,
  sanLoi    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS co_hoi (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  lucMs     INTEGER NOT NULL,
  ma        TEXT NOT NULL,
  sanLong   TEXT NOT NULL,
  sanShort  TEXT NOT NULL,
  grossBps  REAL NOT NULL,
  netBps    REAL NOT NULL,
  duyet     INTEGER NOT NULL,
  payload   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_co_hoi_ma_luc ON co_hoi(ma, lucMs);
CREATE INDEX IF NOT EXISTS idx_co_hoi_cap    ON co_hoi(ma, sanLong, sanShort, lucMs);
CREATE INDEX IF NOT EXISTS idx_luot_luc      ON luot(lucMs);
"""


class So:
    def __init__(self, duong: Path | None = None) -> None:
        self.duong = duong or (DATA_DIR / "thi-bac-ty.sqlite3")
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        self.soLoiGhi = 0
        self.loiCuoi: str | None = None
        #: `SUM(duyet)` cộng toàn bảng `co_hoi`. Xem `thi_bac_ty.nho_tam`.
        self._nhoThongKe = NhoTam()
        with self._mo() as con:
            con.executescript(KHUON)

    def _mo(self):
        # `timeout` để hai tiến trình (runtime + một lượt hỏi từ buồng lái)
        # không ném `database is locked` ngay lập tức mà chờ nhau.
        return sqlite3.connect(self.duong, timeout=10.0)

    # ── ghi ───────────────────────────────────────────────────────────────
    def ghi_luot(self, coHoi: list[CoHoi], soBaoGia: int, sanLoi: list[str]) -> None:
        """Ghi một lượt quét. KHÔNG ném — sổ hỏng không được giết vòng lặp."""
        luc = int(time.time() * 1000)
        try:
            with self._mo() as con:
                con.execute(
                    "INSERT INTO luot(lucMs,soBaoGia,soCoHoi,soDuyet,sanLoi) "
                    "VALUES(?,?,?,?,?)",
                    (luc, soBaoGia, len(coHoi),
                     sum(1 for c in coHoi if c.duyet),
                     json.dumps(sanLoi, ensure_ascii=False)))
                con.executemany(
                    "INSERT INTO co_hoi(lucMs,ma,sanLong,sanShort,grossBps,"
                    "netBps,duyet,payload) VALUES(?,?,?,?,?,?,?,?)",
                    [(luc, c.ma, c.sanLong, c.sanShort, c.grossBpsNgay,
                      c.netBps, int(c.duyet),
                      json.dumps(c.tom_tat(), ensure_ascii=False))
                     for c in coHoi])
        except (sqlite3.Error, OSError, TypeError, ValueError) as e:
            self.soLoiGhi += 1
            self.loiCuoi = f"{type(e).__name__}: {e}"

    # ── đọc ───────────────────────────────────────────────────────────────
    def gan_day(self, n: int = 50) -> list[dict]:
        try:
            with self._mo() as con:
                hang = con.execute(
                    "SELECT payload FROM co_hoi ORDER BY id DESC LIMIT ?",
                    (int(n),)).fetchall()
            return [json.loads(h[0]) for h in hang]
        except (sqlite3.Error, OSError, json.JSONDecodeError):
            return []

    def do_dai(self, ma: str, sanLong: str, sanShort: str,
               soGio: float = 24.0) -> dict:
        """Chênh lệch của cặp này DAI tới đâu trong `soGio` giờ vừa qua.

        Ba con số, và mỗi con số trả lời một câu khác nhau:

            soMau       có đủ dữ liệu để nói gì chưa
            tiLeDuong   bao nhiêu phần lượt quét thấy NET còn dương
            netTrungBinh mức trung bình, để so với mức HIỆN TẠI

        `tiLeDuong` mới là thứ phân biệt hai chuỗi trong docstring đầu file.
        Một cơ hội NET đang 12 bps mà `tiLeDuong` chỉ 0,2 là một cú loé; NET
        8 bps mà `tiLeDuong` 0,9 thì đáng giá hơn hẳn, dù con số nhỏ hơn.
        """
        tu = int((time.time() - soGio * 3600.0) * 1000)
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT COUNT(*), AVG(netBps), "
                    "       SUM(CASE WHEN netBps > 0 THEN 1 ELSE 0 END) "
                    "FROM co_hoi WHERE ma=? AND sanLong=? AND sanShort=? AND lucMs>=?",
                    (ma, sanLong, sanShort, tu)).fetchone()
        except (sqlite3.Error, OSError):
            return {"soMau": 0, "tiLeDuong": None, "netTrungBinh": None,
                    "soGio": soGio, "duMau": False}
        n = int(h[0] or 0)
        return {
            "soMau": n,
            "netTrungBinh": h[1],
            # Chưa có mẫu thì tỉ lệ là None, KHÔNG phải 0 — 0 đọc thành
            # "chưa bao giờ dương", một kết luận mà dữ liệu không hề nói.
            "tiLeDuong": (int(h[2] or 0) / n) if n else None,
            "soGio": soGio,
            "duMau": n >= 20,
        }

    def thong_ke(self) -> dict:
        """Thống kê sổ. Đọc từ NHỚ TẠM, không quét sổ trong đường gọi.

        `SELECT COUNT(*), SUM(duyet) FROM co_hoi` cộng toàn bảng — đo
        05/09/2026 là **12,5 giây** trên 782.415 dòng, và nó nằm thẳng
        trong `/api/trang-thai`. Chỉ mục không chữa được: `SUM` trên toàn
        bảng phải đọc mọi dòng. Xem `thi_bac_ty.nho_tam`.
        """
        gia, tuoi = self._nhoThongKe.lay(self._thong_ke_nang)
        return {**gia, "thongKeTuoiGiay": round(tuoi, 3),
                "nhoTam": self._nhoThongKe.tom_tat(),
                # Đọc từ bộ nhớ chứ không từ sổ — phải là số SỐNG.
                "soLoiGhi": self.soLoiGhi, "loiCuoi": self.loiCuoi}

    def _thong_ke_nang(self) -> dict:
        try:
            with self._mo() as con:
                luot = con.execute("SELECT COUNT(*), MIN(lucMs), MAX(lucMs) FROM luot").fetchone()
                co = con.execute("SELECT COUNT(*), SUM(duyet) FROM co_hoi").fetchone()
        except (sqlite3.Error, OSError):
            return {"soLuot": 0, "soCoHoi": 0, "soDuyet": 0, "chuaCo": True}
        return {
            "soLuot": int(luot[0] or 0),
            "luotDauMs": luot[1], "luotCuoiMs": luot[2],
            "soCoHoi": int(co[0] or 0), "soDuyet": int(co[1] or 0),
            "duong": self.duong.name,
            "chuaCo": not int(luot[0] or 0),
        }

    def don_cu(self, giuNgay: int = 30) -> int:
        """Xoá bản ghi quá hạn. Trả về số dòng đã xoá."""
        moc = int((time.time() - giuNgay * 86400.0) * 1000)
        try:
            with self._mo() as con:
                a = con.execute("DELETE FROM co_hoi WHERE lucMs < ?", (moc,)).rowcount
                b = con.execute("DELETE FROM luot   WHERE lucMs < ?", (moc,)).rowcount
            return int(a or 0) + int(b or 0)
        except (sqlite3.Error, OSError):
            return 0
