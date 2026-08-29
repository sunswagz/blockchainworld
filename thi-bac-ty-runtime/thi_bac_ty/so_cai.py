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
    "NAP_VON",        # CHỦ bỏ thêm vốn vào (hoặc rút ra) — KHÔNG phải lãi
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

    #: Giữ ngắn hơn ngần này giờ thì lần đóng ấy KHÔNG vào bảng đối chiếu.
    #: Cùng con số với `trung_uong.TOI_THIEU_GIO_DOI_CHIEU`, cố ý khai lại
    #: ở đây thay vì import: sổ cái không được biết Trung Ương tồn tại.
    #: Phép kiểm đòi hai con số bằng nhau, nên lệch là đỏ chứ không trôi.
    TOI_THIEU_GIO_TI_SUAT = 0.25

    def du_doan_va_thuc(self) -> dict:
        """LỜI HỨA vs THỰC NHẬN, theo ty — hậu kiểm cho tám ty KHÔNG có băng.

        Ty chênh funding ghi băng nên chạy lại được. Tám ty còn lại không
        có băng, và trước lượt này không có phép hậu kiểm nào cả — nghĩa là
        **những ty ĐANG kiếm được tiền lại là những ty không ai đối chiếu**,
        còn ty duy nhất bị đối chiếu thì hoá ra đang lỗ. Đúng chiều ngược
        với chiều cần.

        Chúng không cần băng: tờ trình lúc mở đã hứa `netUocBps` trong
        `giuGio` giờ, và sổ vị thế lúc đóng biết đã thu thật bao nhiêu
        trong bao lâu. `_bps_gio_du_doan` quy cả hai về bps MỖI GIỜ —
        so bps trần thì một vị thế đóng sớm luôn "thua" lời hứa của cả cửa
        sổ, và cái thua ấy chỉ nói nó đóng sớm chứ không nói nó dở.

        Chỉ đếm những lần đóng có ĐỦ HAI vế. Một bên thiếu thì không có gì
        để so, và đưa nó vào với vế thiếu coi như 0 là bịa ra một lời hứa
        chưa ai hứa.
        """
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT chienLuoc, chiTiet FROM but_toan "
                    "WHERE loai = 'DONG_VI_THE'").fetchall()
        except (sqlite3.Error, OSError):
            return {}
        ra: dict = {}
        for cl, ct in h:
            try:
                d = json.loads(ct or "{}")
            except (TypeError, ValueError):
                continue
            du, thuc = d.get("duDoanBpsGio"), d.get("thucBpsGio")
            o = ra.setdefault(cl, {"soDong": 0, "soDoiChieuDuoc": 0,
                                   "soGiuQuaNgan": 0, "soTuSoNgoai": 0,
                                   "soThieuVe": 0,
                                   "tongDuDoan": 0.0, "tongThuc": 0.0})
            # Kết toán NHẬP TỪ cỗ máy khác không phải lần đóng của ty này.
            # `nhap_so_ngoai` cố ý đổ chúng vào CÙNG một sổ cái — đúng, vì
            # gia sản là một. Nhưng câu «ty này có giữ lời không» thì chỉ
            # hỏi được về những lần CHÍNH NÓ đóng.
            #
            # Đo thật 29/08: bảng ghi «prediction.polymarket.v1 đóng 41»
            # trong khi ty ấy chưa tự đóng lần nào — cả 41 đều là kết toán
            # của Khâm Thiên Giám. Đếm gộp là gán lời hứa cho người không
            # hứa.
            if d.get("nguon"):
                o["soTuSoNgoai"] += 1
                continue
            o["soDong"] += 1
            # Luật «giữ quá ngắn thì không quy ra bps mỗi giờ» phải áp ở CẢ
            # HAI phía. Bên GHI đã chặn từ 29/08, nhưng những dòng ghi
            # TRƯỚC đó vẫn nằm trong sổ và vẫn kéo bình quân đi — bảng hiện
            # «thực −2.618 bps/giờ» suốt ba tháng cho tới khi chúng bị dọn.
            #
            # Luật này nói về việc con số CÓ NGHĨA hay không, chứ không nói
            # về lúc nào mã được sửa. Nên đọc cũng phải lọc.
            gio = d.get("daGiuGio")
            if gio is not None and float(gio) < self.TOI_THIEU_GIO_TI_SUAT:
                o["soGiuQuaNgan"] += 1
                continue
            if du is None or thuc is None:
                # Vế thiếu là một ĐÁM RIÊNG, không phải phần dư vô
                # danh. Đo 29/08: 78 lần đóng ở đây chỉ mang
                # `moLuc/moPhong/vonDaCapUsd` — dòng ghi TRƯỚC khi
                # bút toán đóng biết khai hứa và thực. Chúng không
                # phải «giữ quá ngắn», cũng không phải «của máy
                # khác», nên trước lượt này chúng biến mất khỏi mọi
                # phép cộng và bảng hiện «8/282» — người đọc trừ ra
                # 274 lần thất bại trong khi 209 trong số đó đã có
                # tên. Một mẫu số không giải thích được là một mẫu
                # số nói dối.
                o["soThieuVe"] += 1
                continue
            o["soDoiChieuDuoc"] += 1
            o["tongDuDoan"] += float(du)
            o["tongThuc"] += float(thuc)
        for o in ra.values():
            o.setdefault("soGiuQuaNgan", 0)
            o.setdefault("soTuSoNgoai", 0)
            o.setdefault("soThieuVe", 0)
            k = o["soDoiChieuDuoc"]
            # `None` khi chưa đối chiếu được lần nào — không phải 0. Một ty
            # chưa đóng vị thế nào chưa nói được gì về mình.
            o["duDoanBpsGio"] = o["tongDuDoan"] / k if k else None
            o["thucBpsGio"] = o["tongThuc"] / k if k else None
            o["lechBpsGio"] = ((o["tongDuDoan"] - o["tongThuc"]) / k
                               if k else None)
        return ra

    def lai_lo_tach_khoan(self) -> dict:
        """Lãi lỗ theo ty, TÁCH ra từng khoản — và đó là điểm của hàm này.

        Con số gộp nói dối theo một cách khó thấy. Đo trên máy đang chạy
        ngày 29/08: ty xoay lãi cho vay hiện **−3,19 USD**, trông như một
        chiến lược đang mất tiền. Tách ra thì nó là **+0,9 thu funding trừ
        4,1 phí VÀO LỆNH** — và phần lớn phí ấy không do chiến lược sinh
        ra, mà do **runtime bị khởi động lại**.

        Vị thế mô phỏng không sống qua một lần restart: `doi_soat_vi_the`
        đóng chúng ở sổ, rồi vòng sau mở lại từ đầu và trả phí vào lệnh
        lần nữa. Mười lăm lần deploy trong một buổi chiều là mười lăm lần
        vào lệnh — chi phí VẬN HÀNH, không phải chi phí chiến lược.

        Gộp hai thứ ấy vào một con số là bắt người đọc kết luận sai về
        chiến lược vì một chuyện của người vận hành. Nên bảng này tách:

            thuUsd          FUNDING — tiền chiến lược thật sự sinh ra
            phiVaoUsd       PHI có `phiUocBps` trong chiTiet → phí vào lệnh
            phiKhacUsd      PHI còn lại — phí phát sinh trong kỳ
            truotGiaUsd     TRUOT_GIA
            dieuChinhUsd    DIEU_CHINH — bút toán đảo

        `soLanVaoLenh` đếm luôn số lần vào lệnh, để chia ra phí mỗi lần.
        """
        # Danh sách truy vấn DỰNG TỪ bảng xử lý, không chép tay.
        #
        # Bản đầu viết thẳng bốn tên vào SQL, và phép cấy lỗi ngược lộ ra
        # chỗ hở: nhét thêm `CAP_VON` vào truy vấn thì nó rơi qua mọi
        # nhánh `elif` và **biến mất khỏi mọi tổng** — không phép kiểm nào
        # đỏ, vì con số vẫn cộng ra một kết quả trông bình thường.
        #
        # Sửa bằng một ô "loại lạ" thì thành một nhánh không phép kiểm nào
        # với tới được, tức là một nhánh chết. Sửa đúng là bỏ bản chép:
        # thêm một loại vào đây BUỘC phải thêm chỗ cộng cho nó.
        KHOAN = {"FUNDING": "thuUsd", "TRUOT_GIA": "truotGiaUsd",
                 "DIEU_CHINH": "dieuChinhUsd",
                 "PHI": None,       # None = tách tiếp thành vào-lệnh / trong-kỳ
                 # `DONG_VI_THE` KHÔNG mang tiền (soTienUsd = 0) — nó chỉ
                 # ở đây để ĐẾM. Bỏ nó ra khỏi mọi khoản cộng bằng cách
                 # trỏ vào một ô riêng.
                 "DONG_VI_THE": "_dem_dong"}
        try:
            with self._mo() as con:
                h = con.execute(
                    "SELECT chienLuoc, loai, soTienUsd, chiTiet "
                    "FROM but_toan WHERE loai IN "
                    f"({','.join('?' * len(KHOAN))})", tuple(KHOAN)).fetchall()
        except (sqlite3.Error, OSError):
            return {}
        ra: dict = {}
        for chienLuoc, loai, tien, ct in h:
            k = chienLuoc or "?"
            o = ra.setdefault(k, {"thuUsd": 0.0, "phiVaoUsd": 0.0,
                                  "phiKhacUsd": 0.0, "truotGiaUsd": 0.0,
                                  "dieuChinhUsd": 0.0, "soLanVaoLenh": 0,
                                  "soLanDong": 0, "soButToan": 0})
            o["soButToan"] += 1
            v = float(tien or 0.0)
            o_ten = KHOAN[loai]              # KeyError = truy vấn lệch bảng
            if o_ten == "_dem_dong":
                # Kết toán NHẬP TỪ cỗ máy khác không phải lần đóng của ty
                # này — cùng bộ lọc `du_doan_va_thuc()` đã phải đặt sáng
                # nay, và chính con số mới này lôi nó ra ánh sáng: ty tiên
                # đoán hiện «vào 1 · đóng 50 · tỉ lệ 50,00», tức năm mươi
                # lần đóng của Khâm Thiên Giám đối lại một lần vào lệnh
                # của ta. Một tỉ lệ như thế không nói về churn, nó chỉ nói
                # rằng hai cỗ máy đang bị cộng chung.
                if not (_json(ct) or {}).get("nguon"):
                    o["soLanDong"] += 1
            elif o_ten is not None:
                o[o_ten] += v
            elif "phiUocBps" in (_json(ct) or {}):
                o["phiVaoUsd"] += v
                o["soLanVaoLenh"] += 1
            else:
                o["phiKhacUsd"] += v
        for o in ra.values():
            o["laiLoUsd"] = (o["thuUsd"] + o["phiVaoUsd"] + o["phiKhacUsd"]
                             + o["truotGiaUsd"] + o["dieuChinhUsd"])
            # Lãi lỗ CHIẾN LƯỢC: bỏ phí vào lệnh ra, vì phần lớn nó do
            # khởi động lại chứ không do quyết định của ty.
            o["laiLoChienLuocUsd"] = (o["thuUsd"] + o["phiKhacUsd"]
                                      + o["truotGiaUsd"]
                                      + o["dieuChinhUsd"])
            o["phiMoiLanVaoUsd"] = (o["phiVaoUsd"] / o["soLanVaoLenh"]
                                    if o["soLanVaoLenh"] else None)
            # VÀO bao nhiêu lần / ĐÓNG bao nhiêu lần — hai con số này cạnh
            # nhau mới phân biệt được hai thứ hoàn toàn khác nhau mà cùng
            # trả phí vào lệnh:
            #
            #   vào 289 · đóng 282   gần như mọi vị thế đã đóng rồi mở
            #                        lại — CHURN, chi phí vận hành
            #   vào  48 · đóng   0   bốn tám vị thế MỚI — chi phí bình
            #                        thường của việc rót vốn
            #
            # Không có mẫu số ấy thì triệu chứng `phi-vao-an-het` kêu mãi
            # bằng một con số cộng dồn cả đời, kể cả sau khi churn đã hết.
            # Một cảnh báo không bao giờ tắt được là một cảnh báo người ta
            # học cách bỏ qua.
            o["tiLeDongTrenVao"] = (o["soLanDong"] / o["soLanVaoLenh"]
                                    if o["soLanVaoLenh"] else None)
        return ra

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
