"""PHIÊN PHÁT LẠI — cả cỗ máy chạy thật, trên băng thật, bằng tiền ảo.

    python -m kham.phat_lai                     chạy, vốn lấy từ config
    python -m kham.phat_lai --von=25000         tự thêm vốn bao nhiêu tuỳ ý
    python -m kham.phat_lai --tu=2026-08-25     chỉ phần băng từ ngày đó

## Vì sao cần thứ này, và nó KHÁC `chay_lai` ở đâu

`chay_lai` là một cái thước: nó chấm điểm một bộ tham số, và nó cố tình
đi tắt — không sổ lệnh chờ, không tồn kho, không cầu dao rủi ro, không
sổ kết toán. Đúng cho việc so A với B, sai cho câu hỏi "cỗ máy này kiếm
được bao nhiêu".

Phiên phát lại thì ngược lại: nó gọi ĐÚNG những bộ phận mà bản chạy
thật gọi —

    dinh_gia / dong_co   định giá, rồi NẮN theo sổ hiệu chỉnh
    chien_thuat          năm ngón nghề đề xuất
    rui_ro.duyet         Kelly, phơi nhiễm nhóm, cầu dao, sức khoẻ nguồn
    dat_lenh.CongLenh    khớp giấy theo VWAP THẬT của sổ THẬT, có phí
    kho_doi.Kho          tồn kho, giá vốn, chân lẻ
    ket_toan             kết quả thật, lãi lỗ thật, sổ hiệu chỉnh

— và chỉ thay đúng hai thứ mà máy này không với tới được: **đồng hồ**
(lấy từ băng, không lấy từ tường) và **nguồn** (đọc băng, không gọi
mạng).

## Dữ liệu là THẬT. Tiền là ảo. Kế toán là thật.

Băng ghi sổ lệnh Polymarket thô ở từng khung hình, cùng giá nền Binance
và σ đo được lúc đó. Kết quả từng khung nằm ở `data/ket-qua.jsonl`, dựng
từ nến Binance. Không con số nào ở đây do máy này bịa ra.

Vốn thì tuỳ ý — `--von`. Đó là cả điểm của một phiên giấy: xem cỗ máy
xoay xở thế nào với 1.000 đô và với 100.000 đô, mà không mất đồng nào.

## Ba điều nó KHÔNG chứng minh được, khai trước

1. **Không có tác động thị trường.** Ta ăn vào sổ đã ghi mà sổ ấy không
   biết ta tồn tại. Lô càng to thì con số càng lạc quan.
2. **Không có trượt giá theo thời gian.** Sổ là ảnh chụp lúc ấy; lệnh
   thật mất vài trăm mili-giây mới tới sàn, và `do_tre.py` đo được độ
   trễ nền→sàn quãng nửa giây.
3. **Không có chọn lọc bất lợi.** Người bán ở giá đó có thể biết thứ ta
   chưa biết.

Nên đọc kết quả phiên này như một CẬN TRÊN, không phải một lời hứa.

## Sổ sách viết vào thư mục RIÊNG

`KTG_DATA_DIR` trỏ sang `data/phat-lai/` — sổ kết toán mô phỏng KHÔNG
được lẫn vào sổ thật. Một dòng giả trong sổ thật là một con số sai chảy
vào chẩn đoán, vào Kelly, vào cổng tiến hoá, mãi mãi.
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field, replace

from .bang import NguonKhung, giai_doan_cua
from .can_loi import CoHoi, phi_taker
from .cap_token import CapSo
from .chay_lai import dung_so
from .chien_thuat import BoiCanh, chay_tat_ca
from .config import CONFIG
from .dinh_gia import HieuChinh
from .dong_co import goi as goi_dong_co
from .dongho import LatCat, giai_doan_theo_thoi_gian
from .kho_doi import Kho
from .nan_lai import khop as khop_nan
from .rui_ro import RiskEngine, SucKhoeNguon
from .so import GhiKetToan, So

# Sổ lệnh chờ (maker) trong phiên phát lại: một lệnh yết ra được coi là
# khớp khi khung sau có best ask tụt xuống tới giá yết. Cùng quy ước với
# `CongLenh.soat_cho` của bản chạy thật.
from .so_lenh import SoLenh

#: Khớp lại đường nắn sau mỗi ngần này lần kết toán. Không khớp
#: mỗi lần: PAVA chạy trên cả bảng, và bảng chỉ dày thêm một mẫu
#: thì đường nắn gần như không đổi.
NHIP_KHOP_NAN = 25


@dataclass
class ViKhung:
    """Một cửa sổ đang mở trong phiên — tồn kho và tiền của riêng nó."""
    slug: str
    ma: str
    coUp: float = 0.0
    coDown: float = 0.0
    tienUp: float = 0.0
    tienDown: float = 0.0
    phi: float = 0.0
    chienThuat: list = field(default_factory=list)
    pDuDoanUp: float | None = None
    lucCuoiMs: float = 0.0

    @property
    def tienVao(self) -> float:
        return self.tienUp + self.tienDown

    def gia_tri(self, upThang: bool) -> float:
        return self.coUp if upThang else self.coDown

    @property
    def gia_cap(self) -> float | None:
        """Giá vốn một CẶP, nếu có cả hai chân. Trên $1 là khoá lỗ sẵn."""
        n = min(self.coUp, self.coDown)
        if n <= 0:
            return None
        return (self.tienUp / self.coUp) + (self.tienDown / self.coDown)


@dataclass
class KetQuaPhien:
    von0: float = 0.0
    von: float = 0.0
    dinhVon: float = 0.0
    soKhungHinh: int = 0
    soCuaSo: int = 0
    soLenh: int = 0
    soKhop: int = 0
    soTuChoiRuiRo: int = 0
    soKetToan: int = 0
    soThang: int = 0
    soThua: int = 0
    tongPhi: float = 0.0
    tongLaiLo: float = 0.0
    thuaLonNhat: float = 0.0
    # Cửa sổ đóng mà không có kết quả: tiền đã tiêu, không chấm được.
    # KHÔNG phải lỗ — cổ phần vẫn ngã ngũ trên sàn — nhưng phải hiện ra,
    # vì nó là phần lãi lỗ mà con số cuối cùng KHÔNG bao gồm.
    soTreo: int = 0
    tienTreoUsd: float = 0.0
    soNgay: int = 0
    soLanMoLai: int = 0
    # Cầu dao ngắt lúc nào, và còn bao nhiêu băng chưa chạy khi ấy. Không
    # có hai con số này thì một phiên đứng im từ ngày thứ hai đọc y hệt
    # một phiên "không có cơ hội nào".
    ngatLucKhung: int = 0
    ngatLyDo: str = ""
    #: Lãi lỗ của TỪNG cửa sổ. Không phải trang trí: `tongLaiLo` một mình
    #: không nói được nó chắc tới đâu, và bảy cửa sổ thì "+3,30%" là một
    #: con số nghe như kết luận mà thật ra là tiếng ồn. Có danh sách này
    #: thì lấy lại được khoảng tin — THEO CỬA SỔ, đúng luật đã ghi trong
    #: CLAUDE.md, vì bốn lát cắt của một khung chia chung MỘT kết quả.
    laiLoTungCuaSo: list = field(default_factory=list)
    duongVon: list = field(default_factory=list)
    lyDoTuChoi: dict = field(default_factory=dict)
    cuaDaChan: dict = field(default_factory=dict)
    boQua: dict = field(default_factory=dict)

    @property
    def sutVonPct(self) -> float:
        return 0.0 if self.dinhVon <= 0 else (self.dinhVon - self.von) / self.dinhVon * 100.0

    @property
    def loiNhuanPct(self) -> float:
        return 0.0 if self.von0 <= 0 else (self.von - self.von0) / self.von0 * 100.0

    @property
    def tiLeThang(self) -> float:
        n = self.soThang + self.soThua
        return 0.0 if not n else self.soThang / n

    def tom_tat(self) -> dict:
        return {
            "von0": self.von0, "von": self.von, "dinhVon": self.dinhVon,
            "loiNhuanPct": self.loiNhuanPct, "sutVonPct": self.sutVonPct,
            "soKhungHinh": self.soKhungHinh, "soCuaSo": self.soCuaSo,
            "soLenh": self.soLenh, "soKhop": self.soKhop,
            "soTuChoiRuiRo": self.soTuChoiRuiRo,
            "soKetToan": self.soKetToan, "soThang": self.soThang,
            "soThua": self.soThua, "tiLeThang": self.tiLeThang,
            "tongPhi": self.tongPhi, "tongLaiLo": self.tongLaiLo,
            "thuaLonNhat": self.thuaLonNhat,
            "soTreo": self.soTreo, "tienTreoUsd": self.tienTreoUsd,
            "soNgay": self.soNgay, "soLanMoLai": self.soLanMoLai,
            "ngatLucKhung": self.ngatLucKhung, "ngatLyDo": self.ngatLyDo,
            "lyDoTuChoi": dict(self.lyDoTuChoi), "boQua": dict(self.boQua),
            "cuaDaChan": dict(self.cuaDaChan),
        }


def _don_so_phien(tm) -> None:
    """Xoá sổ của PHIÊN TRƯỚC trong `tm`. Chỉ gọi cho thư mục riêng.

    `So.ghi` luôn NỐI THÊM — đúng cho sổ thật, sai cho phiên phát lại.
    Phiên phát lại chạy đi chạy lại trên cùng một cuộn băng, nên mỗi lần
    chạy lại ghi lại đúng những cửa sổ ấy. Đo được trên đĩa 30/08/2026:

        33 dòng sổ · chỉ 6 mốc thời gian RIÊNG BIỆT · một mốc lặp 8 lần
        tổng lãi lỗ đọc từ file: $165,89 — gấp năm lần sự thật $32,99

    Báo cáo trong phiên vẫn đúng vì nó đếm trên `kq` của phiên. Nhưng
    thứ CÒN LẠI TRÊN ĐĨA là thuốc độc: ai đọc file ấy để chấm phiên giấy
    sẽ thấy một con số gấp năm. Đúng cái bẫy đã cắn ở `chay_lai` (đếm
    mỗi cửa sổ 44 lần → +2,9 triệu đô trên tài khoản 1.000 đô), lần này
    ở một file khác.

    Sổ hiệu chỉnh cũng phải xoá, và lý do NẶNG HƠN: nếu phiên trước để
    lại `hieu-chinh.json`, phiên sau khai sinh đã có bảng nắn khớp trên
    kết quả của chính quãng băng nó sắp chạy — tức NHÌN TRỘM TƯƠNG LAI.
    Hiện chưa xảy ra vì 17 mẫu không đủ để ghi, nhưng băng dày thêm là
    nó xảy ra, và xảy ra im lặng.
    """
    from .config import DATA_DIR as _DD
    for ten in ("ket-toan.jsonl", "hieu-chinh.json"):
        f = tm / ten
        # Chặn cứng: KHÔNG bao giờ được chạm sổ thật. Một lỗi truyền
        # `thuMucSo` sai ở đây là xoá sạch sổ kết toán thật.
        try:
            if f.resolve().parent == _DD.resolve():
                raise RuntimeError(
                    f"từ chối xoá {f} — đó là thư mục sổ THẬT")
        except OSError:
            pass
        if f.exists():
            f.unlink()

class PhienPhatLai:
    """Một phiên giấy TRỌN VẸN trên băng đã ghi.

    Gọi đúng những bộ phận bản chạy thật gọi — định giá qua sổ đăng ký
    động cơ, nắn theo sổ hiệu chỉnh, năm ngón chiến thuật, cầu dao rủi
    ro, khớp giấy theo VWAP thật, tồn kho, kết toán, sổ. Chỉ thay hai
    thứ: đồng hồ lấy từ băng, và nguồn đọc băng thay vì gọi mạng.
    """

    def __init__(self, von: float | None = None,
                 batTat: dict | None = None,
                 thuMucSo=None,
                 moLaiMoiNgay: bool = False,
                 moiHieuChinh: dict | None = None,
                 moiHetMs: float = 0.0) -> None:
        """`thuMucSo`: nơi ghi sổ kết toán và sổ hiệu chỉnh của PHIÊN NÀY.

        Bắt buộc tách khỏi sổ thật. Một dòng mô phỏng lẫn vào sổ thật là
        một con số sai chảy vào chẩn đoán, vào Kelly, vào cổng tiến hoá —
        và không ai gỡ ra được nữa vì nhìn nó giống hệt một dòng thật.

        Tách bằng ĐƯỜNG DẪN chứ không bằng `KTG_DATA_DIR`: băng và sổ kết
        quả vẫn phải đọc từ chỗ thật, nên đổi cả `DATA_DIR` là cắt luôn
        nguồn dữ liệu của chính phiên này.

        ## `None` KHÔNG còn nghĩa là "sổ thật"

        Đoạn trên viết "bắt buộc tách khỏi sổ thật" từ lâu, rồi để mặc
        định làm đúng ngược lại: `thuMucSo=None` cho `So(None)`, tức
        `DATA_DIR/ket-toan.jsonl` — CHÍNH sổ thật. Một luật nằm trong
        văn xuôi thì không giữ được gì.

        Nó đã cắn: hai lần trong một buổi, một phiên phát lại nối 14 dòng
        mô phỏng vào sổ kết toán thật. Sổ ấy là thứ `RiskEngine.nap_tu_so`
        đọc lúc khởi động để dựng lại vốn, đỉnh vốn và lỗ ngày — nên vốn
        ảo của phiên chạy lại trở thành vốn "thật" của cầu dao. Không lỗi
        nào ném ra; mọi con số vẫn đúng cú pháp.

        Nay `None` trỏ vào `data/phat-lai/khong-ten`, và trỏ vào chính
        `DATA_DIR` thì NÉM. Ném chứ không cảnh báo: `_don_so_phien` xoá
        sạch sổ trong thư mục ấy trước khi chạy, nên nhắm sai chỗ này
        không phải là bẩn sổ, mà là mất sổ.
        """
        from pathlib import Path as _P

        from .config import DATA_DIR as _DD
        tm = _P(thuMucSo) if thuMucSo else _P(_DD) / "phat-lai" / "khong-ten"
        if tm.resolve() == _P(_DD).resolve():
            raise ValueError(
                "PhienPhatLai: thuMucSo trỏ thẳng vào DATA_DIR — phiên mô "
                "phỏng sẽ XOÁ rồi ghi đè sổ kết toán thật")
        tm.mkdir(parents=True, exist_ok=True)
        _don_so_phien(tm)
        self.kho = Kho()
        # ĐỒNG HỒ CỦA BĂNG, không phải đồng hồ tường. Trần lỗ NGÀY cần một
        # ranh giới ngày; chạy lại tám ngày bằng đồng hồ tường thì với nó
        # mãi mãi là một ngày, `loNgayUsd` cộng dồn suốt, chạm trần, và
        # cầu dao dính luôn. Đo được: khớp đứng hẳn ở 397 lệnh trong khi
        # băng còn hơn một trăm nghìn khung phía sau.
        self.lucMs = 0.0
        self.risk = RiskEngine(self.kho, dongHo=lambda: self.lucMs / 1000.0)
        self.moLaiMoiNgay = bool(moLaiMoiNgay)
        if von is not None:
            # Tiền ảo, tự thêm bao nhiêu tuỳ ý — nhưng phải đặt CẢ BA mốc.
            # `sutVonPct` đo từ `dinhVon`, cầu dao ngày đo từ `vonBanDau`;
            # đặt mỗi `von` thì phiên khai sinh đã mang một khoản sụt vốn
            # bịa, và cầu dao có thể ngắt trước cả lệnh đầu tiên.
            self.risk.vonBanDau = float(von)
            self.risk.von = float(von)
            self.risk.dinhVon = float(von)
            # Gốc của ba trần cũng phải theo, không thì phiên $100.000
            # chạy với trần của tài khoản $1.000.
            self.risk.vonDauNgay = float(von)
        # `tm` không bao giờ còn là None, nên không còn nhánh nào rơi
        # về sổ thật nữa.
        self.hieuChinh = HieuChinh(tm / "hieu-chinh.json")

        # ── MỒI sổ hiệu chỉnh, và vì sao nó KHÔNG phải gian lận ───────
        #
        # Phiên giấy khai sinh với sổ hiệu chỉnh RỖNG. Cố ý — nhưng cái
        # giá của nó lớn hơn người viết tưởng: `du_de_dung_kelly()` trả
        # False suốt phiên ngắn, nên cỡ lệnh ghim ở LÔ SÀN, nên `--von`
        # KHÔNG đổi một lệnh nào. Đo được: $1.000 và $100.000 cho đúng
        # cùng một chuỗi lệnh và cùng số đô lãi lỗ.
        #
        # Tức phiên giấy đang đo một cỗ máy KHÁC với cỗ máy chạy thật:
        # máy thật có sổ hiệu chỉnh tích sẵn từ trước, Kelly mở, cỡ lệnh
        # theo vốn, và do đó CHẠM tới những trần vốn mà phiên giấy không
        # bao giờ chạm (đo được: 2/13 cửa rủi ro từng chặn ai).
        #
        # Mồi bằng dữ liệu TRƯỚC băng thì đúng bằng thứ máy thật có, và
        # không nhìn trộm gì cả. Nhưng "trước" phải được CANH chứ không
        # phải hứa: `moiHetMs` là mốc cuối của dữ liệu mồi, và khung đầu
        # tiên của băng phải nằm SAU nó. Sai một chiều là mọi con số lãi
        # lỗ của phiên thành rác, im lặng.
        self.moiHetMs = float(moiHetMs or 0.0)
        self._daSoatMoi = False
        if moiHieuChinh:
            if not self.moiHetMs:
                raise ValueError(
                    "mồi hiệu chỉnh phải kèm `moiHetMs` — không có mốc "
                    "cuối thì không canh được chuyện nhìn trộm tương lai")
            self.hieuChinh.o = {k: dict(v) if isinstance(v, dict) else v
                                for k, v in moiHieuChinh.items()}
        self.so = So(tm / "ket-toan.jsonl")
        self.thuMucSo = tm
        self.phepNan = khop_nan(self.hieuChinh)
        self.batTat = batTat
        self.mo: dict[str, ViKhung] = {}
        self.kq = KetQuaPhien(von0=self.risk.von, von=self.risk.von,
                              dinhVon=self.risk.von)
        self.soLanKhopNan = 0     # số lần THẬT SỰ khớp lại
        self._soLanGoiKhop = 0    # số lần được gọi, kể cả lần bỏ qua
        from .ket_qua import so_ket_qua
        self._kqThat = so_ket_qua

    # ── ghi chú vì sao đứng ngoài ─────────────────────────────────────
    def _bo(self, ly: str) -> None:
        self.kq.boQua[ly] = self.kq.boQua.get(ly, 0) + 1

    def _dai_song_giay(self, ma: str) -> float:
        """Khung này dài bao nhiêu giây. Cần cho GIAI ĐOẠN, không phải trang trí."""
        for t in CONFIG["thiTruong"]:
            if t.get("ma") == ma:
                return float(t.get("phutSong", 5)) * 60.0
        return 300.0

    def _ma_dong_co(self, ma: str) -> str:
        for t in CONFIG["thiTruong"]:
            if t.get("ma") == ma:
                return t.get("dongCo") or "updown-crypto"
        return "updown-crypto"

    # ── một khung hình của một market ─────────────────────────────────
    def _mot_khung(self, tt: dict, luc: float) -> None:
        # CHỈ chạy trên dòng KHUNG ĂN THUA. Đây là chỗ nghiêm khắc nhất
        # của cả module, và nó cố ý làm phiên trả về SỐ KHÔNG trên băng cũ.
        #
        # Dòng cửa đặt cược mang `giaMo` = giá lúc T−300, và đó KHÔNG phải
        # strike (`scripts/do-strike.py`). Định giá bằng nó rồi chấm bằng
        # sổ kết quả ĐÚNG là ghép một mô hình sai với một đáp án đúng —
        # tệ hơn cả hai đều sai, vì con số ra trông rất thuyết phục. Đã đo:
        # ghép như thế ra +191% với tỉ lệ thắng 26%.
        #
        # Băng tám ngày đầu KHÔNG có dòng nào thuộc khung ăn thua, nên
        # phiên chạy trên nó sẽ ra 0 cửa sổ, 0 lệnh, 0 lãi lỗ. Đó là câu
        # trả lời ĐÚNG: chưa có dữ liệu để đo. Một con số đẹp dựng trên dữ
        # liệu sai thì tệ hơn hẳn không có số.
        if giai_doan_cua(tt) != "quan-sat":
            self._bo("dòng cửa đặt cược — mô hình không định giá được ở đó")
            return
        ma = tt.get("ma") or "?"
        slug = tt.get("slug") or ma
        soTho = tt.get("so") or {}
        su = dung_so(soTho.get("UP"), ma, "UP")
        sd = dung_so(soTho.get("DOWN"), ma, "DOWN")
        if su is None or sd is None:
            self._bo("thiếu sổ")
            return
        # DÙNG CHUNG phép kiểm với đường chạy thật. Bản trước tự viết
        # `su.dung_duoc or sd.dung_duoc` ở đây, nên nó bỏ sót đúng phần
        # `CapSo` biết mà từng sổ riêng không biết: hai sổ có nói về CÙNG
        # MỘT LÚC không. Hai đường tự kiểm theo hai cách là hai đường sẽ
        # lệch nhau — hôm nay đã gặp chuyện ấy hai lần rồi.
        capSo = CapSo(ma, su, sd)
        if not capSo.dung_duoc:
            self._bo(capSo.ly_do_khong_dung() or "sổ không dùng được")
            return

        gia, mo = tt.get("giaNen"), tt.get("giaMo")
        sig, tau = tt.get("sigmaGiay"), tt.get("conLaiGiay")
        if not all(isinstance(x, (int, float)) for x in (gia, mo, sig, tau)):
            self._bo("thiếu nguyên liệu định giá")
            return
        tau = float(tau)

        # Định giá QUA SỔ ĐĂNG KÝ ĐỘNG CƠ — đúng mối nối bản chạy thật đi.
        maDC = self._ma_dong_co(ma)
        gc, viSao = goi_dong_co(maDC, ma, giaHienTai=float(gia),
                                giaMo=float(mo), tauGiay=tau,
                                sigmaGiay=float(sig), tinHieu=None)
        if gc is None:
            self._bo(f"động cơ từ chối: {viSao or 'không rõ'}")
            return

        # Nắn lại ĐÚNG chỗ bản chạy thật nắn: trước khi ai dùng con số.
        if self.phepNan.dung_duoc:
            pN = self.phepNan.nan(gc.pUp)
            if abs(pN - gc.pUp) > 1e-9:
                gc = replace(gc, pUp=pN, pDown=1.0 - pN)

        v = self.mo.get(slug)
        if v is None:
            v = ViKhung(slug=slug, ma=ma)
            self.mo[slug] = v
            self.kq.soCuaSo += 1
        v.pDuDoanUp = gc.pUp
        v.lucCuoiMs = luc

        # Chiến thuật thật — năm ngón nghề, không phải một phép so ngưỡng.
        # GIAI ĐOẠN phải tính thật, không đóng cứng.
        #
        # Bản trước truyền `giaiDoan="dat-cuoc"` — một chuỗi KHÔNG nằm
        # trong bốn giai đoạn hợp lệ (`gom` / `giua` / `cuoi` / `can-ket`).
        # Mà hai chiến thuật soi thẳng trường ấy:
        #
        #     tao-lap      đòi giaiDoan ∈ (gom, giua)
        #     can-ket-qua  đòi giaiDoan ∈ (cuoi, can-ket)
        #
        # nên cả hai lặng lẽ trả rỗng suốt phiên. Đếm được: trong 1.018
        # lượt gọi chiến thuật, chỉ `lech-gia`, `phong-ho`, `cap-*` đề
        # xuất — hai ngón nghề kia ĐÚNG 0 lần. Con số lãi lỗ của phiên
        # giấy vì thế là của một cỗ máy KHÁC cỗ máy đang chạy thật.
        #
        # Đây đúng cái lỗi `vong.py` đã sửa và ghi chú dài dòng ở bước 7 —
        # sửa một nơi mà không quét tìm bản sao thì nó ở lại nơi kia.
        #
        # `tongGiay` cũng phải là ĐỘ DÀI KHUNG, không phải `max(tau, 1)`:
        # lấy tau thì `troiQuaPct` luôn bằng 0 và lối đo theo TỈ LỆ của
        # `_giai_doan` mất tác dụng, chỉ còn lối tuyệt đối.
        tong = self._dai_song_giay(ma)
        lc = LatCat(conLaiGiay=tau, tongGiay=tong,
                    giaiDoan=giai_doan_theo_thoi_gian(tau, tong),
                    troiQuaPct=min(100.0, max(0.0, (1.0 - tau / tong) * 100.0)),
                    lechDongHoMs=0.0, tuoiDuLieuMs=0.0)
        bc = BoiCanh(ma=ma, gia=gc, soUp=su, soDown=sd, dongHo=lc,
                     viThe=self.kho.lay(ma),
                     tranLechHuongUsd=self.risk.tranLechHuongUsd)
        deXuat = chay_tat_ca(bc, self.batTat)
        if not deXuat:
            self._bo("không chiến thuật nào đề xuất")
            return

        # Rủi ro quyết. Nguồn coi như LÀNH: băng đã ghi được thì lúc ấy nó
        # lành. Bịa ra một nguồn ốm ở đây là tự chặn mình bằng số giả.
        sk = SucKhoeNguon(tuoiSoLenhMs=0.0, tuoiGiaNenMs=0.0,
                          lechDongHoMs=0.0, thieuNguon=[])
        duKelly = self.hieuChinh.du_de_dung_kelly()
        for ch in deXuat:
            pq = self.risk.duyet(ch, sk, tau, duKelly)
            if not pq.cho or pq.soCoChoPhep < 1:
                self.kq.soTuChoiRuiRo += 1
                # Đếm theo MÃ CỬA, không chỉ theo câu chữ. Câu chữ mang
                # số tiền nên mỗi lần một khác, và một cửa chặn 500 lần
                # trông như 500 lý do riêng lẻ. Mã thì đếm được, và quan
                # trọng hơn: nó cho biết cửa nào KHÔNG chặn lần nào.
                if pq.ma:
                    d = self.kq.cuaDaChan
                    d[pq.ma] = d.get(pq.ma, 0) + 1
                for l in (pq.lyDo or ["không rõ"]):
                    self.kq.lyDoTuChoi[_dau_cau(l)] = \
                        self.kq.lyDoTuChoi.get(_dau_cau(l), 0) + 1
                continue
            self._khop(ch, pq.soCoChoPhep, su if ch.ben == "UP" else sd, v)

    # ── khớp giấy: VWAP THẬT của sổ THẬT, có phí ──────────────────────
    def _khop(self, ch: CoHoi, soCo: float, so: SoLenh, v: ViKhung) -> None:
        self.kq.soLenh += 1
        if ch.laMaker:
            # Maker KHÔNG khớp tức thì — nó nằm chờ người khác tới ăn, và
            # đó chính là đánh đổi của việc không trả phí. Cho nó khớp ngay
            # là tặng không cả phí lẫn spread cho chiến thuật `tao-lap`.
            self._bo("lệnh maker: phiên này chưa mô phỏng hàng chờ")
            return
        r = so.vwap_mua(soCo)
        if r.khop <= 0:
            self._bo("sổ không có hàng")
            return
        tien = r.vwap * r.khop
        ph = phi_taker(r.vwap, r.khop)
        self.kq.soKhop += 1
        self.kq.tongPhi += ph
        v.phi += ph
        if ch.ben == "UP":
            v.coUp += r.khop
            v.tienUp += tien
        else:
            v.coDown += r.khop
            v.tienDown += tien
        if ch.chienThuat not in v.chienThuat:
            v.chienThuat.append(ch.chienThuat)
        # Vào tồn kho chung để `quyet_chan` và phơi nhiễm nhóm nhìn thấy.
        self.kho.lay(ch.ma).ghi_khop(ch.ben, r.khop, r.vwap,
                                     pMoHinh=ch.fairValue)

    # ── kết toán một cửa sổ ───────────────────────────────────────────
    def _ket_toan(self, slug: str) -> None:
        v = self.mo.pop(slug, None)
        if v is None:
            return
        that = self._kqThat.lay(slug)
        if that is None:
            # KHÔNG được bỏ đi mà giữ tồn kho lại. `RiskEngine` đọc chính
            # `Kho` để tính "market này đã dùng bao nhiêu trên trần", nên
            # một cửa sổ không ra kết quả mà không trả lại hạn mức là
            # market ấy CHẾT cho tới hết phiên.
            #
            # Đo được: khớp đứng hẳn ở 398 lệnh trong khi cửa sổ vẫn mở
            # thêm hàng nghìn. 12 khung thiếu kết quả trên 2.627 là đủ
            # khoá cả bốn market. Cùng chỗ hỏng ấy có trong bản chạy
            # thật — xem `KetToan._bo_theo_doi`.
            self._bo("cửa sổ đóng mà chưa có kết quả")
            self.kq.soTreo += 1
            self.kq.tienTreoUsd += v.tienVao
            self._tra_ton_kho(v.ma)
            return

        # Sổ hiệu chỉnh nhận CẢ khi không có vị thế — cùng lý do bản chạy
        # thật: chỉ ghi những ca mình đã chọn vào là tự thiên lệch đúng
        # chiều làm mô hình trông giỏi hơn thực tế.
        if v.pDuDoanUp is not None:
            self.hieuChinh.them(v.pDuDoanUp, bool(that))
        if v.coUp <= 0 and v.coDown <= 0:
            return

        tienRa = v.gia_tri(bool(that))
        lai = tienRa - v.tienVao - v.phi
        self.kq.soKetToan += 1
        self.kq.tongLaiLo += lai
        self.kq.laiLoTungCuaSo.append(lai)
        if lai > 0:
            self.kq.soThang += 1
        else:
            self.kq.soThua += 1
            self.kq.thuaLonNhat = min(self.kq.thuaLonNhat, lai)
        truocNgat = self.risk.ngatKhanCap
        self.risk.ghi_lai_lo(lai)
        if self.risk.ngatKhanCap and not truocNgat:
            self.kq.ngatLucKhung = self.kq.soKhungHinh
            self.kq.ngatLyDo = self.risk.lyDoNgat
        self.kq.von = self.risk.von
        self.kq.dinhVon = max(self.kq.dinhVon, self.risk.von)
        self.kq.duongVon.append({"luc": v.lucCuoiMs, "slug": slug,
                                 "laiLo": round(lai, 6),
                                 "von": round(self.risk.von, 4)})
        self.so.ghi(GhiKetToan(
            luc=time.strftime("%Y-%m-%dT%H:%M:%SZ",
                              time.gmtime(max(0.0, v.lucCuoiMs) / 1000.0)),
            ma=v.ma, upThang=bool(that), coUp=v.coUp, coDown=v.coDown,
            tienVao=v.tienVao, tienRa=tienRa, phiUsd=v.phi, laiLo=lai,
            giaCap=v.gia_cap, chienThuat=list(v.chienThuat),
            pDuDoan=v.pDuDoanUp,
            # `v` là tồn kho riêng của đường chạy lại; hai trường này
            # sống ở tồn kho CHUNG (`kho_doi.ViThe`), nơi `ghi_khop`
            # cộng dồn chúng. Đọc TRƯỚC khi trả tồn kho.
            pLucVao=self.kho.lay(v.ma).pVaoTb,
            giaVaoTb=self.kho.lay(v.ma).giaVaoTb))
        self._tra_ton_kho(v.ma)
        self._khop_lai_nan()

    def _tra_ton_kho(self, ma: str) -> None:
        """Cửa sổ đóng thì tồn kho của market ấy về 0, dù chấm được hay không."""
        # Chỗ dọn tồn kho THỨ BA, và nó đã quên `phiUsd` sẵn từ trước —
        # đúng thứ `ViThe.don()` sinh ra để chặn.
        self.kho.lay(ma).don()

    # ── khớp lại đường nắn trong lúc chạy ─────────────────────────────
    def _khop_lai_nan(self) -> None:
        """Khớp lại mỗi `NHIP_KHOP_NAN` lần kết toán.

        Bản chạy thật khớp lại mỗi 10 phút (`vong._soat_nan_lai`) vì sổ
        hiệu chỉnh dày thêm liên tục, và một đường nắn khớp từ 300 mẫu
        mà dùng mãi cho 30.000 mẫu thì chính nó thành thứ lạc hậu nhất
        trong hệ. Phiên phát lại khớp MỘT LẦN lúc khai sinh thì mô phỏng
        một cỗ máy không học — tức là không phải cỗ máy đang chạy.

        Phiên bắt đầu với sổ hiệu chỉnh RỖNG, cố ý: `hieu-chinh.json`
        thật được tích từ chính quãng băng này, nên mượn nó về là để
        quyết định ở phút thứ nhất dựa trên kết quả của ngày thứ tám.
        Khởi đầu lạnh chậm hơn, và đó là cái giá của một con số đứng được.
        """
        # Đếm RIÊNG số lần gọi và số lần THẬT SỰ khớp lại. Bản trước dùng
        # một biến cho cả hai, tên là `soLanKhopNan` mà đếm số lần GỌI —
        # nên báo cáo cuối phiên nói "khớp lại 7 lần" trong khi nó khớp
        # lại ĐÚNG 0 lần, và `phepNan` vẫn là bản 0 mẫu lúc khai sinh.
        # Một bộ đếm mang tên việc A mà đếm việc B thì mọi câu đọc từ nó
        # đều sai, kể cả khi con số đúng.
        self._soLanGoiKhop += 1
        if self._soLanGoiKhop % NHIP_KHOP_NAN:
            return
        self.phepNan = khop_nan(self.hieuChinh)
        self.soLanKhopNan += 1

    # ── ranh giới ngày ────────────────────────────────────────────────
    def _nhip_ngay(self) -> None:
        """Sang ngày mới thì bộ đếm lỗ ngày về 0.

        Phải gọi mỗi khung, không phải chỉ khi có lệnh kết toán: ranh
        giới ngày trôi qua kể cả trong một đêm không giao dịch gì, và
        `ghi_lai_lo` thì chỉ chạy khi có kết toán.
        """
        if not self.risk.sang_ngay_moi():
            return
        self.kq.soNgay += 1
        if self.moLaiMoiNgay and self.risk.ngatKhanCap:
            # Mô phỏng một người vận hành sáng nào cũng nhìn bảng rồi mở
            # lại cầu dao. KHÔNG bật mặc định: cầu dao không tự phục hồi
            # là chủ ý của bản chạy thật, và một phiên tự mở lại mỗi ngày
            # đo một cỗ máy có người trực chứ không phải cỗ máy để không.
            self.kq.soLanMoLai += 1
            self.risk.mo_lai()

    # ── chạy cả băng ──────────────────────────────────────────────────
    def chay(self, nguonKhung, moiBuoc=None) -> KetQuaPhien:
        """Quét băng theo thứ tự thời gian. `moiBuoc(kq)` gọi mỗi 5.000 khung."""
        for k in nguonKhung:
            self.kq.soKhungHinh += 1
            luc = float(k.get("luc") or 0.0)
            if luc > 0:
                # CANH mồi ngay ở khung ĐẦU TIÊN có thời gian. Mồi lấn
                # sang tương lai của băng là nhìn trộm, và nó không lộ
                # ra ở bất kỳ con số nào — chỉ làm mọi thứ đẹp lên.
                if self.moiHetMs and not self._daSoatMoi:
                    self._daSoatMoi = True
                    # `<=`, không phải `<`: khung ĐÚNG BẰNG mốc cuối
                    # của mồi là cùng một thời điểm với nến cuối đã dùng
                    # để khớp bảng nắn. Cho qua là mở một khe bằng đúng
                    # một khoảnh khắc, và khe ấy không lộ ra ở con số
                    # nào — chỉ làm mọi thứ đẹp lên. Cửa canh thì nên
                    # nghiêng về phía TỪ CHỐI.
                    if luc <= self.moiHetMs:
                        raise RuntimeError(
                            "mồi hiệu chỉnh kết thúc SAU khung đầu của "
                            f"băng ({self.moiHetMs:.0f} > {luc:.0f}) — "
                            "đó là nhìn trộm tương lai, từ chối chạy")
                self.lucMs = luc
                self._nhip_ngay()
            dangSong = set()
            for tt in (k.get("thiTruong") or []):
                slug = tt.get("slug") or tt.get("ma") or "?"
                dangSong.add(slug)
                self._mot_khung(tt, luc)
            # Cửa sổ biến khỏi băng là nó đã đóng cửa đặt cược → kết toán.
            for slug in [s for s in self.mo if s not in dangSong]:
                self._ket_toan(slug)
            if moiBuoc and self.kq.soKhungHinh % 5000 == 0:
                moiBuoc(self.kq)
        for slug in list(self.mo):
            self._ket_toan(slug)
        self.kq.von = self.risk.von
        # Khớp lần cuối trước khi ai đọc báo cáo. Không có dòng này thì
        # `phepNan` in ra là bản của lần khớp gần nhất — có thể là bản
        # 0 mẫu lúc khai sinh — trong khi sổ hiệu chỉnh đã dày lên
        # suốt phiên. Báo cáo đọc một cỗ máy không phải cỗ máy vừa chạy.
        self.phepNan = khop_nan(self.hieuChinh)
        return self.kq


def _dau_cau(l: str) -> str:
    """Gom lý do từ chối thành NHÓM, không đếm từng câu có số riêng.

    "net edge +0,0031 dưới ngưỡng 0,015" và "net edge +0,0072 dưới ngưỡng
    0,015" là cùng một lý do; đếm riêng thì bảng lý do dài hàng nghìn dòng
    và không nói được gì.
    """
    tu = l.split()
    return " ".join(tu[:2]) if len(tu) >= 2 else l
