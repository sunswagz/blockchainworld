"""SỔ ĐĂNG KÝ — vòng đời mọi tờ trình, và cái PHỄU.

Thông Chính Ty lo **thời gian thực**: nhận rồi chuyển đi ngay, hàng đợi có
trần, không giữ lịch sử.

Sổ Đăng Ký lo **lịch sử**: mỗi tờ trình đi qua những trạng thái nào, và cuối
cùng ra sao. Hai việc khác nhau, đừng gộp.

## Cái phễu — thứ duy nhất trả lời được "cỗ máy này có học không"

Sau vài tháng, Sổ Đăng Ký trả lời được câu mà không bảng nào khác trả lời
được:

    phát hiện            18.421
    qua cổng ty           4.301        23%
    qua rủi ro tổng       1.126         6%
    được cấp vốn            382         2%
    có lãi                  271        71% số đã cấp
    dương tính giả          111        29%

Từng con số một mình vô nghĩa. Cả phễu thì nói rất nhiều: cổng ty quá lỏng
hay quá chặt, rủi ro tổng đang chặn ở đâu, và tỉ lệ dương tính giả có đang
giảm theo thời gian không — tức là **cỗ máy có mạnh lên thật không**.

## Trạng thái là một chiều, và có phép kiểm canh

    PHAT_HIEN → DUYET_TY → DUYET_RUI_RO → DA_CAP_VON → DA_MO → DA_DONG
         └──────────┴──────────────┴─── TU_CHOI / HET_HAN / HONG

Không có đường lùi. Một tờ trình đã `TU_CHOI` mà sau đó `DA_CAP_VON` là dấu
hiệu có tầng nào đó đi tắt — và đó đúng là thứ nguy hiểm nhất trong cả kiến
trúc này: một tầng bỏ qua tầng trên nó.
"""
from __future__ import annotations

import datetime as _dt
import json
import sqlite3
import threading
from pathlib import Path

#: Vòng đời. Thứ tự trong tuple này CHÍNH LÀ thứ tự cho phép — `_hop_le()`
#: đọc nó, nên thêm trạng thái là chèn đúng chỗ.
DUONG_DI = ("PHAT_HIEN", "DUYET_TY", "DUYET_RUI_RO", "DA_CAP_VON",
            "DA_MO", "DA_DONG")

#: Trạng thái KẾT THÚC — vào rồi thì không đi tiếp được nữa.
KET_THUC = ("TU_CHOI", "HET_HAN", "HONG")

TAT_CA = DUONG_DI + KET_THUC

KHUON = """
CREATE TABLE IF NOT EXISTS to_trinh (
  ma         TEXT PRIMARY KEY,
  chienLuoc  TEXT NOT NULL,
  ho         TEXT NOT NULL,
  taiSan     TEXT NOT NULL,
  lucTao     TEXT NOT NULL,
  trangThai  TEXT NOT NULL,
  lucDoi     TEXT NOT NULL,
  payload    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chuyen_trang_thai (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  ma        TEXT NOT NULL,
  tu        TEXT,
  den       TEXT NOT NULL,
  luc       TEXT NOT NULL,
  lyDo      TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_tt_tt   ON to_trinh(trangThai);
CREATE INDEX IF NOT EXISTS idx_tt_ty   ON to_trinh(chienLuoc, trangThai);
CREATE INDEX IF NOT EXISTS idx_ct_ma   ON chuyen_trang_thai(ma, id);
"""


def _bay_gio() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


def _hop_le(tu: str | None, den: str) -> bool:
    """Chuyển trạng thái này có được phép không.

    Luật: đi ĐÚNG MỘT BƯỚC tới trên `DUONG_DI`, hoặc rẽ vào một trạng thái
    KẾT THÚC. Từ một trạng thái kết thúc thì không đi đâu được nữa.

    **Một bước, không phải "tới trước là được".** Nới thành `index(den) >
    index(tu)` nghe vô hại — cả hai đều cấm đi lùi — nhưng nó cho phép đúng
    thứ cả sổ này sinh ra để bắt: `PHAT_HIEN → DA_CAP_VON`, tức là vốn tới
    được vị thế mà **Rủi Ro Tổng chưa từng thấy tờ trình**. Cái phễu vẫn in
    ra một bảng đẹp, chỉ có hàng "qua rủi ro tổng" là rỗng, và không ai đọc
    một hàng rỗng thành "có tầng đang đi tắt".

    Đường đi thật chưa bao giờ cần nhảy cóc — `TrungUong.mot_vong()` bước
    từng nấc một. Nên siết ở đây không chặn việc gì đang chạy; nó chỉ biến
    một lời hứa trong tài liệu thành một phép kiểm có răng.
    """
    if den not in TAT_CA:
        return False
    if tu is None:
        return den == "PHAT_HIEN"
    if tu in KET_THUC:
        return False
    if den in KET_THUC:
        return True
    if tu not in DUONG_DI:
        return False
    return DUONG_DI.index(den) == DUONG_DI.index(tu) + 1


class SoDangKy:
    def __init__(self, duong: Path) -> None:
        self.duong = Path(duong)
        self.duong.parent.mkdir(parents=True, exist_ok=True)
        self._khoa = threading.Lock()
        self.soChuyenSai = 0
        self.chuyenSaiCuoi: str | None = None
        with self._mo() as con:
            con.executescript(KHUON)

    def _mo(self):
        return sqlite3.connect(self.duong, timeout=10.0)

    # ── ghi ───────────────────────────────────────────────────────────────
    def ghi_nhan(self, tt) -> bool:
        """Ghi một tờ trình mới ở trạng thái PHAT_HIEN."""
        try:
            with self._khoa, self._mo() as con:
                if con.execute("SELECT 1 FROM to_trinh WHERE ma=?",
                               (tt.ma,)).fetchone():
                    return False
                luc = _bay_gio()
                con.execute(
                    "INSERT INTO to_trinh(ma,chienLuoc,ho,taiSan,lucTao,"
                    "trangThai,lucDoi,payload) VALUES(?,?,?,?,?,?,?,?)",
                    (tt.ma, tt.chienLuoc, tt.ho, tt.taiSan, tt.luc,
                     "PHAT_HIEN", luc,
                     json.dumps(tt.tom_tat(), ensure_ascii=False)))
                con.execute(
                    "INSERT INTO chuyen_trang_thai(ma,tu,den,luc,lyDo) "
                    "VALUES(?,?,?,?,?)",
                    (tt.ma, None, "PHAT_HIEN", luc, "ty nộp lên Thông Chính"))
            return True
        except (sqlite3.Error, OSError, TypeError, ValueError):
            return False

    def chuyen(self, ma: str, den: str, lyDo: str = "") -> bool:
        """Chuyển trạng thái. False nếu đường đi không hợp lệ.

        Chuyển sai KHÔNG được ghi vào sổ, nhưng `soChuyenSai` đếm ra — một
        tầng đi tắt phải hiện thành con số, không được im.
        """
        try:
            with self._khoa, self._mo() as con:
                h = con.execute("SELECT trangThai FROM to_trinh WHERE ma=?",
                                (ma,)).fetchone()
                if not h:
                    self.soChuyenSai += 1
                    self.chuyenSaiCuoi = f"{ma}: chưa có trong sổ"
                    return False
                tu = h[0]
                if not _hop_le(tu, den):
                    self.soChuyenSai += 1
                    self.chuyenSaiCuoi = (
                        f"{ma}: {tu} → {den} KHÔNG hợp lệ — có tầng nào đó "
                        f"đang đi tắt")
                    return False
                luc = _bay_gio()
                con.execute(
                    "UPDATE to_trinh SET trangThai=?, lucDoi=? WHERE ma=?",
                    (den, luc, ma))
                con.execute(
                    "INSERT INTO chuyen_trang_thai(ma,tu,den,luc,lyDo) "
                    "VALUES(?,?,?,?,?)", (ma, tu, den, luc, lyDo))
            return True
        except (sqlite3.Error, OSError):
            return False

    # ── đọc ───────────────────────────────────────────────────────────────
    def phieu(self, ma: str) -> dict | None:
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT ma,chienLuoc,ho,taiSan,lucTao,trangThai,lucDoi,"
                    "payload FROM to_trinh WHERE ma=?", (ma,)).fetchone()
                if not h:
                    return None
                ls = con.execute(
                    "SELECT tu,den,luc,lyDo FROM chuyen_trang_thai "
                    "WHERE ma=? ORDER BY id", (ma,)).fetchall()
        except (sqlite3.Error, OSError):
            return None
        return {"ma": h[0], "chienLuoc": h[1], "ho": h[2], "taiSan": h[3],
                "lucTao": h[4], "trangThai": h[5], "lucDoi": h[6],
                "toTrinh": _json(h[7]),
                "duongDi": [{"tu": r[0], "den": r[1], "luc": r[2],
                             "lyDo": r[3]} for r in ls]}

    def pheu(self, chienLuoc: str | None = None) -> dict:
        """Cái phễu — xem docstring đầu file."""
        try:
            with self._mo() as con:
                if chienLuoc:
                    h = con.execute(
                        "SELECT den, COUNT(DISTINCT ma) FROM chuyen_trang_thai "
                        "WHERE ma IN (SELECT ma FROM to_trinh WHERE chienLuoc=?) "
                        "GROUP BY den", (chienLuoc,)).fetchall()
                else:
                    h = con.execute(
                        "SELECT den, COUNT(DISTINCT ma) FROM chuyen_trang_thai "
                        "GROUP BY den").fetchall()
        except (sqlite3.Error, OSError):
            return {}
        dem = {r[0]: r[1] for r in h}
        pd = dem.get("PHAT_HIEN", 0)
        ra = {t: dem.get(t, 0) for t in TAT_CA}
        # Tỉ lệ sống sót qua từng cửa. `None` khi mẫu số bằng 0 — không phải
        # 0%, vì "chưa có tờ nào" khác hẳn "không tờ nào qua".
        ra["tiLe"] = {
            t: (dem.get(t, 0) / pd if pd else None)
            for t in DUONG_DI[1:] + KET_THUC
        }
        ra["phatHien"] = pd
        return ra

    def ly_do_tu_choi(self, dinh: int = 5) -> dict[str, list[dict]]:
        """VÌ SAO mỗi họ bị từ chối — không chỉ BAO NHIÊU.

        Phễu theo họ nói được «họ phái-sinh có 2115 cơ hội và không được
        đồng nào». Nó KHÔNG nói được vì sao, mà đó mới là câu quyết định:
        cổng ty quá chặt là một việc, hết chỗ vì trần vị thế lại là việc
        hoàn toàn khác — cái đầu sửa bằng vặn ngưỡng, cái sau sửa bằng
        nhường chỗ, và nhìn vào một con số 0 thì hai cái ấy giống hệt nhau.

        Lý do là CÂU chứ không phải MÃ, nên hai lý do gần giống nhau sẽ
        nằm tách. Phần lớn chỗ tách là do tên cảng dính trong câu («hết
        chỗ ở trần cảng pendle») — mà đó là thông tin, không phải nhiễu.
        Chỗ nào tách thật sự vô ích thì phải đổi bên GHI thành mã, không
        phải đoán ở bên ĐỌC.
        """
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT t.ho, c.lyDo, COUNT(*) AS n "
                    "FROM chuyen_trang_thai c JOIN to_trinh t ON t.ma = c.ma "
                    "WHERE c.den = 'TU_CHOI' AND c.lyDo != '' "
                    "GROUP BY t.ho, c.lyDo ORDER BY t.ho, n DESC").fetchall()
        except (sqlite3.Error, OSError):
            return {}
        ra: dict[str, list[dict]] = {}
        for ho, ly, dem in h:
            ds = ra.setdefault(ho, [])
            if len(ds) < int(dinh):
                ds.append({"lyDo": ly, "so": int(dem)})
        return ra

    def theo_trang_thai(self, tt: str, n: int = 50) -> list[dict]:
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT ma,chienLuoc,taiSan,lucDoi,payload FROM to_trinh "
                    "WHERE trangThai=? ORDER BY lucDoi DESC LIMIT ?",
                    (tt, int(n))).fetchall()
        except (sqlite3.Error, OSError):
            return []
        return [{"ma": r[0], "chienLuoc": r[1], "taiSan": r[2],
                 "lucDoi": r[3], "toTrinh": _json(r[4])} for r in h]

    def don_cu(self, giuNgay: int = 90) -> int:
        """Xoá tờ trình đã KẾT THÚC quá hạn. Tờ đang sống thì không đụng."""
        moc = (_dt.datetime.now(_dt.timezone.utc)
               - _dt.timedelta(days=giuNgay)).isoformat()
        try:
            with self._khoa, self._mo() as con:
                q = ",".join("?" * len(KET_THUC))
                ma = [r[0] for r in con.execute(
                    f"SELECT ma FROM to_trinh WHERE trangThai IN ({q}) "
                    f"AND lucDoi < ?", (*KET_THUC, moc)).fetchall()]
                if not ma:
                    return 0
                p = ",".join("?" * len(ma))
                con.execute(f"DELETE FROM chuyen_trang_thai WHERE ma IN ({p})", ma)
                con.execute(f"DELETE FROM to_trinh WHERE ma IN ({p})", ma)
                return len(ma)
        except (sqlite3.Error, OSError):
            return 0

    def tom_tat(self) -> dict:
        try:
            with self._mo() as con:
                n = con.execute("SELECT COUNT(*) FROM to_trinh").fetchone()[0]
                theo = {r[0]: r[1] for r in con.execute(
                    "SELECT trangThai, COUNT(*) FROM to_trinh "
                    "GROUP BY trangThai").fetchall()}
                ty = {r[0]: r[1] for r in con.execute(
                    "SELECT chienLuoc, COUNT(*) FROM to_trinh "
                    "GROUP BY chienLuoc").fetchall()}
        except (sqlite3.Error, OSError):
            return {"soToTrinh": 0, "chuaCo": True}
        return {"soToTrinh": int(n or 0), "theoTrangThai": theo,
                "theoTy": ty, "pheu": self.pheu(),
                "soChuyenSai": self.soChuyenSai,
                "chuyenSaiCuoi": self.chuyenSaiCuoi,
                "duong": self.duong.name, "chuaCo": not int(n or 0)}


def _json(s):
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}
