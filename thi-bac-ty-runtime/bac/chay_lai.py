"""Chạy lại — và phép đo DUY NHẤT dám gọi là hậu kiểm.

## Vì sao "đếm cơ hội" không phải backtest

Cách dễ nhất, và vô dụng nhất: đi qua băng, đếm xem có bao nhiêu cơ hội qua
cửa. Con số ấy trông như backtest và không chứng minh được gì — nó chỉ nói
ngưỡng của ta lỏng hay chặt, không nói ta ĐÚNG hay SAI.

Phép đo thật phải trả lời: **cơ hội ấy, nếu vào thật, thu được bao nhiêu?**

## Đo funding THỰC NHẬN, bằng chính băng

Băng ghi báo giá mỗi 30 giây, nên nó chứa sẵn câu trả lời — chỉ cần nhìn TỚI
TRƯỚC thay vì nhìn tại chỗ:

    tại khung t   : ta thấy cơ hội, dự đoán thu `thuBps`
    tại các mốc   : trong [t, t+H], mỗi lần kết toán rơi vào đó,
                    tra băng lấy funding rate SÀN CÔNG BỐ ngay lúc ấy
    cộng lại      : đó là `thuThucBps` — tiền thật sự chảy

`thuBps` là DỰ ĐOÁN (giả định rate hiện tại giữ nguyên tới lúc kết toán).
`thuThucBps` là ĐO ĐƯỢC. Khoảng cách giữa hai con số ấy chính là thứ đáng
học, và không có băng thì không đo được nó.

## Ba chỗ xấp xỉ, khai ra để không ai tưởng đây là sổ sách thật

1. **Rate tại mốc lấy từ khung gần mốc nhất**, không phải rate sàn thật sự
   áp lúc kết toán. Băng nhịp 30 giây nên sai lệch nhỏ, nhưng có thật.
2. **Không mô phỏng khớp lệnh.** Phí và trượt giá vẫn là tham số, không phải
   độ sâu sổ lệnh. Nên `netThucBps` là **chặn trên**.
3. **Không có vốn, không có tồn kho.** Mỗi cơ hội xét độc lập; không mô
   phỏng chuyện vốn đã kẹt ở cơ hội khác.

Ba chỗ ấy đều làm kết quả ĐẸP HƠN sự thật. Nhớ điều đó trước khi tin một con
số dương.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .can_loi import phi_khu_hoi_bps, tim_co_hoi
from .dongho import dem_moc
from .models import BaoGia
from .rui_ro import CongRuiRo

BPS = 10_000.0

#: Khung cách mốc kết toán xa hơn ngần này thì không dùng để tra rate — thà
#: bỏ một mốc còn hơn gán cho nó một con số của mười phút trước.
DUNG_SAI_MOC_MS = 120_000.0

#: Cứ ngần này khung thì NHƯỜNG một nhịp cho luồng khác.
#:
#: Hậu kiểm chạy ở luồng nền, nhưng "luồng nền" trong Python KHÔNG có nghĩa
#: là không cản ai: mã Python thuần giữ GIL, và một lượt chạy lại 460.000 cơ
#: hội giữ nó gần như liên tục. Đo thật 29/08: cổng 5188 chết **110 giây**
#: kể từ lúc máy lên — buồng lái không mở được, vòng quét không quay, và cầu
#: dao đo tuổi dữ liệu nên nó sắp ngắt vì chính phép đo của mình.
#:
#: `sleep` một khoảng RẤT NGẮN thì nhả GIL thật (`sleep(0)` không chắc nhả
#: trên Windows). 14.000 khung ÷ 200 = 70 lần nhường × 0,5 ms = 35 ms cho cả
#: lượt — không đáng kể so với 30 giây, mà đổi lại cỗ máy vẫn sống.
NHUONG_MOI_KHUNG = 200
NHUONG_GIAY = 0.0005


@dataclass
class ThamSo:
    """Một bộ tham số đem ra thử. Chỉ chứa thứ VẶN ĐƯỢC.

    Phí không nằm ở đây, và đó là chủ ý: phí là sự thật về thế giới, không
    phải núm để vặn. Cho vòng tiến hoá vặn phí xuống là dạy nó cách tự vẽ ra
    lợi nhuận — nó sẽ tìm ra ngay, vì đó là đường dễ nhất tới điểm cao.
    """
    ten: str = "hiện tại"
    giuGio: float = 8.0
    ruiRo: dict = field(default_factory=dict)


@dataclass
class KetQua:
    ten: str
    soKhung: int = 0
    soCoHoi: int = 0
    soQuaCua: int = 0
    soDoDuoc: int = 0          # số cơ hội hậu kiểm được (có đủ băng phía sau)
    tongThuDuDoanBps: float = 0.0
    tongThuThucBps: float = 0.0
    tongNetThucBps: float = 0.0
    soLai: int = 0
    soLo: int = 0
    netThucTeNhatBps: float = 0.0
    boQua: dict = field(default_factory=dict)

    @property
    def ky_vong_bps(self) -> float | None:
        """NET thực trung bình mỗi cơ hội. None khi chưa đo được cái nào."""
        return self.tongNetThucBps / self.soDoDuoc if self.soDoDuoc else None

    @property
    def sai_so_du_doan_bps(self) -> float | None:
        """Dự đoán lệch thực nhận bao nhiêu, trung bình. Dương = ta lạc quan."""
        if not self.soDoDuoc:
            return None
        return (self.tongThuDuDoanBps - self.tongThuThucBps) / self.soDoDuoc

    @property
    def ti_le_lai(self) -> float | None:
        return self.soLai / self.soDoDuoc if self.soDoDuoc else None

    def tom_tat(self) -> dict:
        return {
            "ten": self.ten, "soKhung": self.soKhung, "soCoHoi": self.soCoHoi,
            "soQuaCua": self.soQuaCua, "soDoDuoc": self.soDoDuoc,
            "kyVongBps": self.ky_vong_bps,
            "saiSoDuDoanBps": self.sai_so_du_doan_bps,
            "tiLeLai": self.ti_le_lai,
            "soLai": self.soLai, "soLo": self.soLo,
            "netThucTeNhatBps": self.netThucTeNhatBps if self.soDoDuoc else None,
            "tongNetThucBps": self.tongNetThucBps,
            "boQua": dict(self.boQua),
            # Không bao giờ trả tỉ lệ lãi mà thiếu phần đuôi. Tỉ lệ lãi một
            # mình là con số dễ khoe nhất và ít nghĩa nhất: 95% lãi mỗi lần
            # 1 bps mà 5% lỗ mỗi lần 40 bps là một chiến lược thua.
            "duMau": self.soDoDuoc >= 30,
        }


# ══════════════════════════════════════════════════════════════════════════
#  DỰNG LẠI BÁO GIÁ TỪ BĂNG
# ══════════════════════════════════════════════════════════════════════════
def dung_bao_gia(d: dict, lucMs: float | None = None) -> BaoGia | None:
    """Dựng lại `BaoGia` từ một bản ghi thô trong băng.

    Trả `None` thay vì ném khi bản ghi thiếu trường: băng sáu tháng trước có
    thể thiếu trường mới thêm, và một khung hỏng không được giết cả lượt chạy
    lại. Nhưng KHÔNG bịa giá trị thay thế — thiếu `intervalGio` thì bỏ hẳn
    báo giá đó, vì đoán bừa chu kỳ là đúng cái lỗi mà cả cung này tồn tại để
    chặn.
    """
    if not isinstance(d, dict):
        return None
    try:
        gio = float(d["intervalGio"])
        if not (gio > 0):
            return None
        return BaoGia(
            san=str(d["san"]), ma=str(d["ma"]),
            rate=float(d["rate"]), intervalGio=gio,
            markPx=_so(d.get("markPx")), mocKeMs=_nguyen(d.get("mocKeMs")),
            oiUsd=_so(d.get("oiUsd")),
            nguonTsMs=_dau_thoi_gian(d, lucMs),
            nhanTsMs=_nguyen(d.get("nhanTsMs")),
            nguonTuSan=bool(d.get("nguonTuSan", False)),
            intervalSuyRa=bool(d.get("intervalSuyRa", False)),
            ghiChu=str(d.get("ghiChu") or ""),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _so(v):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f and abs(f) != float("inf") else None


def _nhuong() -> None:
    """Nhả GIL cho luồng khác chạy. Xem `NHUONG_MOI_KHUNG`."""
    import time as _t
    _t.sleep(NHUONG_GIAY)


def _nguyen(v):
    f = _so(v)
    return None if f is None else int(f)


def _dau_thoi_gian(d: dict, lucMs: float | None) -> int | None:
    """Dấu thời gian nguồn của báo giá, DẪN LẠI được từ băng cũ.

    Băng ghi trước 29/08/2026 không có `nguonTsMs` — chỉ có `tuoiGiay`. Mà
    tuổi ấy được tính đúng bằng `(luc − nguonTsMs) / 1000` với CÙNG một
    `luc` mà khung mang theo (xem `vong.py`: `"luc": now` và
    `b.tom_tat(now)` dùng chung một biến). Nên đảo ngược lại là một phép
    DẪN CHÍNH XÁC, không phải một phép đoán — và nó cứu 188 giờ băng khỏi
    bị vứt.

    Ưu tiên dấu ghi thẳng khi có: dẫn lại chỉ để đọc bản cũ, không để thay
    bản mới. Thiếu cả hai thì trả `None`, và cổng rủi ro chặn — đúng như
    nó vẫn làm, chứ không phải bịa ra một dấu.
    """
    thang = _nguyen(d.get("nguonTsMs"))
    if thang is not None:
        return thang
    tuoi = _so(d.get("tuoiGiay"))
    if tuoi is None or lucMs is None:
        return None
    return int(lucMs - tuoi * 1000.0)


# ══════════════════════════════════════════════════════════════════════════
#  TRA RATE TẠI MỘT MỐC
# ══════════════════════════════════════════════════════════════════════════
class TraCuu:
    """Chỉ mục băng theo (mã, sàn) để tra rate tại một thời điểm bất kỳ.

    Dựng một lần rồi dùng lại cho mọi cơ hội. Không có chỉ mục thì mỗi lần
    tra là quét lại cả băng, và một băng một ngày × vài trăm cơ hội biến
    phép hậu kiểm thành thứ không ai đợi nổi.
    """

    def __init__(self, khung: list[dict]) -> None:
        self.bang: dict[tuple[str, str], list[tuple[float, float]]] = {}
        for i, k in enumerate(khung):
            if i % NHUONG_MOI_KHUNG == 0:
                _nhuong()
            luc = _so(k.get("luc"))
            if luc is None:
                continue
            for d in (k.get("baoGia") or []):
                san, ma = d.get("san"), d.get("ma")
                r = _so(d.get("rate"))
                if san and ma and r is not None:
                    self.bang.setdefault((ma, san), []).append((luc, r))
        for v in self.bang.values():
            v.sort()

    def rate_tai(self, ma: str, san: str, mocMs: float) -> float | None:
        """Rate sàn công bố tại khung gần `mocMs` nhất, hoặc None.

        `None` khi băng không phủ tới đó — và None phải được xử như "không
        đo được", không phải như 0. Coi nó là 0 là bịa ra một lần kết toán
        không trả gì, và mọi thống kê phía sau lệch theo hướng bi quan giả.
        """
        ds = self.bang.get((ma, san))
        if not ds:
            return None
        lo, hi = 0, len(ds) - 1
        while lo < hi:
            giua = (lo + hi) // 2
            if ds[giua][0] < mocMs:
                lo = giua + 1
            else:
                hi = giua
        ung = [ds[i] for i in (lo - 1, lo, lo + 1) if 0 <= i < len(ds)]
        if not ung:
            return None
        luc, r = min(ung, key=lambda x: abs(x[0] - mocMs))
        return r if abs(luc - mocMs) <= DUNG_SAI_MOC_MS else None


# ══════════════════════════════════════════════════════════════════════════
#  MỘT LƯỢT CHẠY LẠI
# ══════════════════════════════════════════════════════════════════════════
def mot_luot(khung: list[dict], ts: ThamSo, phiSan: dict) -> KetQua:
    """Chạy lại toàn bộ băng với MỘT bộ tham số, và hậu kiểm từng cơ hội."""
    kq = KetQua(ten=ts.ten)
    tra = TraCuu(khung)
    cong = CongRuiRo(ts.ruiRo)

    for i, k in enumerate(khung):
        # Nhường GIL theo NHỊP KHUNG, không theo thời gian: đếm khung thì
        # tất định — chạy lại cùng một cuốn băng cho cùng một kết quả và
        # cùng một số lần nhường. Nhường theo đồng hồ thì hai lượt trên cùng
        # dữ liệu khác nhau, và một phép hậu kiểm không tất định thì không
        # còn là bằng chứng.
        if i % NHUONG_MOI_KHUNG == 0:
            _nhuong()
        luc = _so(k.get("luc"))
        if luc is None:
            continue
        kq.soKhung += 1
        bao = [b for b in (dung_bao_gia(d, luc)
                           for d in (k.get("baoGia") or []))
               if b is not None]
        if len(bao) < 2:
            continue

        for co in tim_co_hoi(bao, luc, ts.giuGio, phiSan, cong):
            kq.soCoHoi += 1
            for m in co.lyDoMa:
                kq.boQua[m] = kq.boQua.get(m, 0) + 1
            if not co.duyet:
                continue
            kq.soQuaCua += 1

            thuc = _thu_thuc_te(tra, co, luc, ts.giuGio)
            if thuc is None:
                continue        # băng không phủ hết cửa sổ giữ — không đoán
            kq.soDoDuoc += 1
            net = thuc * BPS - co.phiBps
            kq.tongThuDuDoanBps += co.thuBps
            kq.tongThuThucBps += thuc * BPS
            kq.tongNetThucBps += net
            if net > 0:
                kq.soLai += 1
            else:
                kq.soLo += 1
            kq.netThucTeNhatBps = min(kq.netThucTeNhatBps, net) \
                if kq.soDoDuoc > 1 else net
    return kq


def _thu_thuc_te(tra: TraCuu, co, lucMs: float, giuGio: float) -> float | None:
    """Funding THỰC NHẬN của một cặp, tra từ băng tại từng mốc kết toán.

    Trả `None` khi băng không phủ đủ — thà không đo còn hơn đo một nửa rồi
    gọi đó là kết quả.
    """
    tong = 0.0
    # Dấu theo đúng quy ước ở `dongho.py`: SHORT nhận, LONG trả. Viết thành
    # một vòng lặp hai chân chứ không tách nhánh theo dấu của rate — mỗi lần
    # có người tách nhánh là một lần nhánh âm lặng lẽ đảo dấu.
    for san, dau in ((co.sanShort, +1.0), (co.sanLong, -1.0)):
        for m in _cac_moc(lucMs, giuGio, co, san):
            r = tra.rate_tai(co.ma, san, m)
            if r is None:
                return None
            tong += dau * r
    return tong


def _cac_moc(lucMs: float, giuGio: float, co, san: str) -> list[float]:
    """Các mốc kết toán của MỘT chân, trong cửa sổ giữ."""
    if san == co.sanShort:
        so, interval = co.soMocShort, co.intervalShortGio
    else:
        so, interval = co.soMocLong, co.intervalLongGio
    if so <= 0:
        return []
    # `dem_moc` đã tính số mốc; ở đây dựng lại đúng vị trí của chúng bằng
    # cùng một hàm, để hai chỗ không thể lệch nhau.
    lich = dem_moc(lucMs, giuGio, None, interval)
    if lich.mocDauMs is None:
        return []
    buoc = interval * 3_600_000.0
    return [lich.mocDauMs + i * buoc for i in range(so)]


# ══════════════════════════════════════════════════════════════════════════
#  ĐỐI CHIẾU HAI BỘ THAM SỐ
# ══════════════════════════════════════════════════════════════════════════
def doi_chieu(khung: list[dict], a: ThamSo, b: ThamSo, phiSan: dict) -> dict:
    """Chạy HAI bộ tham số trên CÙNG một băng rồi so. Đây mới là backtest.

    Chạy hai bộ trên hai băng khác nhau là so hai thế giới khác nhau, và mọi
    khác biệt đọc được đều có thể chỉ là chợ hôm ấy khác chợ hôm nay.
    """
    ka, kb = mot_luot(khung, a, phiSan), mot_luot(khung, b, phiSan)

    def hon(x: float | None, y: float | None) -> str:
        if x is None or y is None:
            return "chưa đủ mẫu"
        if abs(x - y) < 1e-9:
            return "bằng"
        return "A" if x > y else "B"

    du_mau = min(ka.soDoDuoc, kb.soDoDuoc) >= 30
    return {
        "A": ka.tom_tat(), "B": kb.tom_tat(),
        "duMau": du_mau,
        "toiThieuMau": 30,
        "kyVongHon": hon(ka.ky_vong_bps, kb.ky_vong_bps),
        "caiThienBps": (None if ka.ky_vong_bps is None or kb.ky_vong_bps is None
                        else kb.ky_vong_bps - ka.ky_vong_bps),
        "ghiChu": ("đủ mẫu để so" if du_mau else
                   f"CHƯA đủ mẫu — cần ≥30 cơ hội hậu kiểm được ở CẢ HAI bên, "
                   f"đang có A={ka.soDoDuoc} B={kb.soDoDuoc}"),
    }
