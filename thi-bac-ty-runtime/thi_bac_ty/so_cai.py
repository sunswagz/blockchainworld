"""SỔ CÁI — *vì sao* tôi có những thứ này.

Khác hẳn Danh Mục, và đừng lẫn:

    Danh Mục   "bây giờ tôi có gì?"        — trạng thái, ghi đè liên tục
    Sổ Cái     "tại sao tôi lại có?"       — lịch sử, CHỈ THÊM, không bao giờ sửa

Thiếu Danh Mục thì không biết còn bao nhiêu tiền. Thiếu Sổ Cái thì không bao
giờ trả lời được câu *"tháng trước ta mất tiền ở đâu"* — và một cỗ máy không
trả lời được câu ấy thì không học được gì, chỉ chạy.

## Chỉ THÊM, không bao giờ sửa

Không có `update`, không có `delete`. Ghi sai thì ghi thêm một bút toán ĐẢO,
đúng lối kế toán kép. Cho phép sửa là mở đường cho một cỗ máy tự viết lại
lịch sử của chính nó — và nó sẽ viết lại theo hướng đẹp lên, vì đó là hướng
mọi hàm mục tiêu đều đẩy tới.

## Mỗi bút toán phải trả lời được "ai, vì sao"

    luc · loai · chienLuoc · maToTrinh · soTien · lyDo · chiTiet

`maToTrinh` là sợi chỉ nối ngược về tờ trình đã đẻ ra quyết định này. Không
có nó thì sổ cái là một danh sách con số không truy được nguồn, và mọi phép
chẩn đoán sau này đều dừng ở "có chuyện gì đó đã xảy ra".
"""
from __future__ import annotations

import datetime as _dt
import json
import sqlite3
import threading
from dataclasses import dataclass, field
from pathlib import Path

#: Các loại bút toán. Thêm loại mới thì thêm ở ĐÂY — `kiem()` soi theo bảng
#: này, nên một loại tự bịa sẽ bị chặn ngay lúc ghi thay vì lộ ra sau ba
#: tháng khi ai đó gộp thống kê.
LOAI = (
    "CAP_VON",        # Thị Bạc Ty cấp vốn cho một tờ trình
    "TU_CHOI",        # Rủi Ro Tổng hoặc Phân Bổ từ chối
    "MO_VI_THE",      # một chân đã mở
    "DONG_VI_THE",    # một chân đã đóng
    "FUNDING",        # dòng tiền funding tại một mốc kết toán
    "PHI",            # phí giao dịch
    "TRUOT_GIA",      # trượt giá thực tế so với giá thấy lúc quyết
    "HOAN_VON",       # vốn trả về quỹ sau khi đóng
    "CAU_DAO",        # cầu dao ngắt / đóng lại
    "DIEU_CHINH",     # bút toán ĐẢO để sửa một bút toán sai
)


def bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


KHUON = """
CREATE TABLE IF NOT EXISTS but_toan (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  lucMs      INTEGER NOT NULL,
  luc        TEXT    NOT NULL,
  loai       TEXT    NOT NULL,
  chienLuoc  TEXT,
  maToTrinh  TEXT,
  soTienUsd  REAL    NOT NULL DEFAULT 0,
  lyDo       TEXT    NOT NULL,
  chiTiet    TEXT    NOT NULL DEFAULT '{}',
  daoCua     INTEGER
);
-- Một bút toán chỉ được đảo MỘT lần, và cơ sở dữ liệu là chỗ giữ luật ấy
-- chứ không phải một câu `if` trong `dao()`. Chỉ mục duy nhất còn đúng khi
-- có hai tiến trình cùng ghi, còn câu `if` thì không.
CREATE UNIQUE INDEX IF NOT EXISTS idx_bt_dao ON but_toan(daoCua)
  WHERE daoCua IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_bt_luc  ON but_toan(lucMs);
CREATE INDEX IF NOT EXISTS idx_bt_ma   ON but_toan(maToTrinh);
CREATE INDEX IF NOT EXISTS idx_bt_loai ON but_toan(loai, lucMs);
"""


@dataclass
class ButToan:
    loai: str
    lyDo: str
    soTienUsd: float = 0.0
    chienLuoc: str | None = None
    maToTrinh: str | None = None
    chiTiet: dict = field(default_factory=dict)
    luc: str = field(default_factory=bay_gio)
    #: Bút toán này đang ĐẢO bút toán số mấy. Chỉ `dao()` đặt trường này —
    #: đặt tay là tự mở lại đúng cái cửa mà chỉ mục duy nhất vừa đóng.
    daoCua: int | None = None

    def kiem(self) -> list[str]:
        loi = []
        if self.loai not in LOAI:
            loi.append(f"loại {self.loai!r} không có trong bảng LOAI")
        if not self.lyDo.strip():
            loi.append("bút toán KHÔNG có lý do — sổ cái tồn tại để trả lời "
                       "'vì sao', một dòng không lý do là một con số câm")
        return loi

    def tom_tat(self) -> dict:
        return {"loai": self.loai, "lyDo": self.lyDo,
                "soTienUsd": self.soTienUsd, "chienLuoc": self.chienLuoc,
                "maToTrinh": self.maToTrinh, "chiTiet": self.chiTiet,
                "luc": self.luc, "daoCua": self.daoCua}


class SoCai:
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
    def ghi(self, bt: ButToan) -> bool:
        """Ghi một bút toán. Trả về False nếu sai khuôn hoặc ghi hỏng.

        KHÔNG ném: sổ cái hỏng không được giết vòng lặp đang chạy. Nhưng
        `soLoiGhi` đếm ra được, và buồng lái hiện nó — một sổ cái ngừng ghi
        trong im lặng là mất trắng khả năng truy nguyên.
        """
        loi = bt.kiem()
        if loi:
            self.soLoiGhi += 1
            self.loiCuoi = "; ".join(loi)
            return False
        try:
            with self._khoa, self._mo() as con:
                con.execute(
                    "INSERT INTO but_toan(lucMs,luc,loai,chienLuoc,maToTrinh,"
                    "soTienUsd,lyDo,chiTiet,daoCua) VALUES(?,?,?,?,?,?,?,?,?)",
                    (_ms(bt.luc), bt.luc, bt.loai, bt.chienLuoc, bt.maToTrinh,
                     float(bt.soTienUsd), bt.lyDo,
                     json.dumps(bt.chiTiet, ensure_ascii=False), bt.daoCua))
            return True
        except (sqlite3.Error, OSError, TypeError, ValueError) as e:
            self.soLoiGhi += 1
            self.loiCuoi = f"{type(e).__name__}: {e}"
            return False

    def dao(self, maButToan: int, lyDo: str) -> bool:
        """Đảo một bút toán sai. **Cách DUY NHẤT để sửa sổ cái.**

        Không `UPDATE`, không `DELETE`. Bút toán sai vẫn nằm đó, và bên cạnh
        nó là bút toán đảo với lý do — người đọc sau này thấy được cả cái sai
        lẫn việc nó đã được nhận ra.

        **Mỗi bút toán chỉ đảo được một lần**, và luật ấy do chỉ mục duy nhất
        `idx_bt_dao` giữ chứ không do câu `if` dưới đây. Không có nó thì gọi
        `dao()` ba lần biến một khoản thu 12,5 nhầm thành một khoản LỖ 25 —
        sổ vẫn cân, mọi dòng vẫn có lý do, và con số thì sai.

        **Không đảo được một bút toán ĐẢO.** Lỡ đảo nhầm thì viết một bút
        toán mới bằng `ghi()` kèm lý do của nó; nối đuôi đảo-của-đảo thì
        người đọc phải cộng cả chuỗi mới biết cuối cùng còn lại bao nhiêu.
        """
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT loai,chienLuoc,maToTrinh,soTienUsd,lyDo "
                    "FROM but_toan WHERE id=?", (int(maButToan),)).fetchone()
        except (sqlite3.Error, OSError):
            return False
        if not h:
            return False
        if h[0] == "DIEU_CHINH":
            self.soLoiGhi += 1
            self.loiCuoi = (f"#{maButToan} là một bút toán ĐẢO — đảo của đảo "
                            f"thì phải cộng cả chuỗi mới biết còn lại bao nhiêu")
            return False
        return self.ghi(ButToan(
            loai="DIEU_CHINH", soTienUsd=-float(h[3]),
            chienLuoc=h[1], maToTrinh=h[2],
            lyDo=f"đảo bút toán #{maButToan}: {lyDo}",
            chiTiet={"daoCua": int(maButToan), "loaiGoc": h[0],
                     "lyDoGoc": h[4]},
            daoCua=int(maButToan)))

    # ── đọc ───────────────────────────────────────────────────────────────
    def gan_day(self, n: int = 100, loai: str | None = None) -> list[dict]:
        try:
            with self._mo() as con:
                if loai:
                    h = con.execute(
                        "SELECT id,luc,loai,chienLuoc,maToTrinh,soTienUsd,"
                        "lyDo,chiTiet FROM but_toan WHERE loai=? "
                        "ORDER BY id DESC LIMIT ?", (loai, int(n))).fetchall()
                else:
                    h = con.execute(
                        "SELECT id,luc,loai,chienLuoc,maToTrinh,soTienUsd,"
                        "lyDo,chiTiet FROM but_toan "
                        "ORDER BY id DESC LIMIT ?", (int(n),)).fetchall()
        except (sqlite3.Error, OSError):
            return []
        return [{"id": r[0], "luc": r[1], "loai": r[2], "chienLuoc": r[3],
                 "maToTrinh": r[4], "soTienUsd": r[5], "lyDo": r[6],
                 "chiTiet": _json(r[7])} for r in h]

    def theo_to_trinh(self, ma: str) -> list[dict]:
        """Cả đời một tờ trình, theo thứ tự thời gian. Sợi chỉ truy nguyên."""
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT id,luc,loai,chienLuoc,maToTrinh,soTienUsd,lyDo,"
                    "chiTiet FROM but_toan WHERE maToTrinh=? ORDER BY id",
                    (ma,)).fetchall()
        except (sqlite3.Error, OSError):
            return []
        return [{"id": r[0], "luc": r[1], "loai": r[2], "chienLuoc": r[3],
                 "maToTrinh": r[4], "soTienUsd": r[5], "lyDo": r[6],
                 "chiTiet": _json(r[7])} for r in h]

    def tong_theo_loai(self) -> dict:
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT loai, COUNT(*), SUM(soTienUsd) "
                    "FROM but_toan GROUP BY loai").fetchall()
        except (sqlite3.Error, OSError):
            return {}
        return {r[0]: {"so": r[1], "tongUsd": r[2] or 0.0} for r in h}

    def lai_lo_theo_chien_luoc(self) -> dict:
        """Lãi lỗ gộp theo ty. Đây là câu trả lời cho 'ty nào đang kiếm được'.

        Chỉ cộng những loại thật sự là DÒNG TIỀN — cấp vốn và hoàn vốn không
        phải lãi lỗ, chúng là chuyển vốn. Gộp nhầm chúng vào là mỗi lần cấp
        $100 lại thành lỗ $100 trên bảng.
        """
        DONG_TIEN = ("FUNDING", "PHI", "TRUOT_GIA", "DIEU_CHINH")
        try:
            with self._mo() as con:
                h = con.execute(
                    f"SELECT chienLuoc, COUNT(*), SUM(soTienUsd) "
                    f"FROM but_toan WHERE loai IN "
                    f"({','.join('?' * len(DONG_TIEN))}) "
                    f"GROUP BY chienLuoc", DONG_TIEN).fetchall()
        except (sqlite3.Error, OSError):
            return {}
        return {(r[0] or "?"): {"soButToan": r[1], "laiLoUsd": r[2] or 0.0}
                for r in h}

    def tom_tat(self) -> dict:
        try:
            with self._mo() as con:
                n, dau, cuoi = con.execute(
                    "SELECT COUNT(*), MIN(luc), MAX(luc) FROM but_toan"
                ).fetchone()
        except (sqlite3.Error, OSError):
            return {"soButToan": 0, "chuaCo": True}
        return {"soButToan": int(n or 0), "butDau": dau, "butCuoi": cuoi,
                "theoLoai": self.tong_theo_loai(),
                "laiLoTheoTy": self.lai_lo_theo_chien_luoc(),
                "soLoiGhi": self.soLoiGhi, "loiCuoi": self.loiCuoi,
                "duong": self.duong.name, "chuaCo": not int(n or 0)}


def _ms(iso: str) -> int:
    try:
        return int(_dt.datetime.fromisoformat(
            iso.replace("Z", "+00:00")).timestamp() * 1000)
    except (ValueError, AttributeError):
        return 0


def _json(s):
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}
