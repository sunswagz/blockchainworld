"""LỊCH — phiên Mỹ theo giờ Việt Nam, ngày nghỉ, sự kiện, và chương trình thưởng.

Token cổ phiếu trên X Layer giao dịch 24/7, nhưng GIÁ của nó chỉ được khám
phá từ 9:30 tới 16:00 giờ New York. Ngoài giờ ấy giá trên chuỗi trôi trên
thanh khoản mỏng, và cú «bắt kịp» lúc mở cửa là lúc arbitrageur ăn LP. Nên
mọi quyết định của ty đi qua một câu hỏi trước: **bây giờ là lúc nào của
phiên Mỹ, tính theo giờ Việt Nam?**

Không dùng `zoneinfo` vì Windows của người vận hành không chắc có tzdata;
giờ mùa hè Mỹ là một luật đơn giản (Chủ nhật thứ hai tháng 3 → Chủ nhật đầu
tháng 11) và viết tay được, kèm phép kiểm.

Mọi thứ ở đây là LỊCH, tức là dữ liệu — không phải mã. Ngày nghỉ NYSE và
lịch FOMC 2026 chép ở đây kèm nguồn; sang 2027 phải chép tiếp, và phép kiểm
`kiem_lich_con_han` sẽ kêu khi lịch không phủ tới hôm nay.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

VN = dt.timezone(dt.timedelta(hours=7), "VN")
UTC = dt.timezone.utc

#: Ngày nghỉ NYSE. Nguồn: lịch công bố của NYSE. Sang năm mới thì thêm.
NGHI_NYSE = {
    2026: ("2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
           "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
           "2026-11-26", "2026-12-25"),
}

#: Ngày kết thúc họp FOMC (ngày công bố, 14:00 ET). Nguồn: lịch Fed.
FOMC = {
    2026: ("2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
           "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09"),
}

MO_CUA_ET = dt.time(9, 30)
DONG_CUA_ET = dt.time(16, 0)


def _chu_nhat_thu(nam: int, thang: int, thu: int) -> dt.date:
    d = dt.date(nam, thang, 1)
    lech = (6 - d.weekday()) % 7          # 6 = Chủ nhật
    return d + dt.timedelta(days=lech + 7 * (thu - 1))


def gio_mua_he_my(ngay: dt.date) -> bool:
    """EDT từ Chủ nhật thứ hai tháng 3 tới trước Chủ nhật đầu tháng 11."""
    return _chu_nhat_thu(ngay.year, 3, 2) <= ngay < _chu_nhat_thu(ngay.year, 11, 1)


def mui_gio_et(ngay: dt.date) -> dt.timezone:
    h = -4 if gio_mua_he_my(ngay) else -5
    return dt.timezone(dt.timedelta(hours=h), "EDT" if h == -4 else "EST")


def ngay_nghi(ngay: dt.date) -> bool:
    return ngay.isoformat() in NGHI_NYSE.get(ngay.year, ())


def ngay_giao_dich(ngay: dt.date) -> bool:
    return ngay.weekday() < 5 and not ngay_nghi(ngay)


def lich_con_han(ngay: dt.date) -> bool:
    """Lịch có phủ năm này không — không phủ thì mọi «ngày giao dịch» đều
    sai theo hướng lạc quan (coi ngày nghỉ là ngày thường)."""
    return ngay.year in NGHI_NYSE


def phien_my(ngay: dt.date) -> tuple[dt.datetime, dt.datetime] | None:
    """`(mở, đóng)` của phiên Mỹ ngày ấy, đổi sang giờ VN. `None` nếu nghỉ."""
    if not ngay_giao_dich(ngay):
        return None
    tz = mui_gio_et(ngay)
    mo = dt.datetime.combine(ngay, MO_CUA_ET, tz).astimezone(VN)
    dong = dt.datetime.combine(ngay, DONG_CUA_ET, tz).astimezone(VN)
    return mo, dong


def so_ngay_giao_dich(tu: dt.datetime, den: dt.datetime) -> float:
    """Số ngày giao dịch (có phần lẻ) rơi trong [tu, den].

    Đếm theo GIỜ PHIÊN: một phiên 6,5 giờ là một ngày giao dịch; nửa phiên
    là nửa ngày. Đây là τ cho σ — cửa sổ giữ qua trọn cuối tuần có τ = 0
    theo thước này, và điều đó ĐÚNG với phần giá cổ phiếu, chỉ SAI với phần
    trôi trên chuỗi mà ta chưa đo (xem `ghi chú ngoai-gio` trong ty).
    """
    if den <= tu:
        return 0.0
    tu = tu.astimezone(VN)
    den = den.astimezone(VN)
    tong = 0.0
    d = (tu - dt.timedelta(days=1)).date()
    cuoi = (den + dt.timedelta(days=1)).date()
    while d <= cuoi:
        ph = phien_my(d)
        if ph:
            a, b = max(ph[0], tu), min(ph[1], den)
            if b > a:
                tong += (b - a).total_seconds() / (6.5 * 3600.0)
        d += dt.timedelta(days=1)
    return tong


#: Trạng thái phiên
MO_CUA = "MO_CUA"            # sàn Mỹ đang mở — giá được khám phá
TRUOC_MO = "TRUOC_MO"        # trong 90 phút trước mở — giá chuỗi sắp bị «bắt kịp»
SAU_DONG = "SAU_DONG"        # ngày thường, ngoài giờ
CUOI_TUAN = "CUOI_TUAN"      # cuối tuần hoặc ngày nghỉ — không có phiên


@dataclass(frozen=True)
class SuKien:
    luc: dt.datetime            # giờ VN
    loai: str                   # fomc · ket-qua-kinh-doanh · het-thuong · mo-cua · dong-cua
    ten: str
    ma: str = ""                # mã cổ phiếu liên quan, rỗng = toàn thị trường

    def tom_tat(self) -> dict:
        return {"luc": self.luc.isoformat(), "loai": self.loai,
                "ten": self.ten, "ma": self.ma}


@dataclass(frozen=True)
class BoiCanhPhien:
    luc: dt.datetime
    trangThai: str
    phienKe: tuple | None        # (mở, đóng) kế tiếp hoặc đang diễn ra
    gioToiMo: float | None       # giờ tới lần mở kế (None khi đang mở)
    gioToiDong: float | None
    lichConHan: bool
    suKien: tuple = field(default_factory=tuple)   # trong 7 ngày tới, đã sắp xếp

    def su_kien_trong(self, gio: float, ma: str | None = None) -> list:
        ra = []
        for s in self.suKien:
            if (s.luc - self.luc).total_seconds() / 3600.0 > gio:
                continue
            if s.ma and ma and s.ma.upper() != ma.upper():
                continue
            ra.append(s)
        return ra

    def tom_tat(self) -> dict:
        return {"luc": self.luc.isoformat(), "trangThai": self.trangThai,
                "phienKe": ([x.isoformat() for x in self.phienKe]
                            if self.phienKe else None),
                "gioToiMo": self.gioToiMo, "gioToiDong": self.gioToiDong,
                "lichConHan": self.lichConHan,
                "suKien": [s.tom_tat() for s in self.suKien]}


def boi_canh(luc: dt.datetime | None = None,
             suKienThem: list | None = None,
             ketQuaKinhDoanh: dict | None = None,
             hetThuong: dt.datetime | None = None,
             phutTruocMo: float = 90.0) -> BoiCanhPhien:
    """Bối cảnh phiên tại `luc` (mặc định bây giờ), kèm sự kiện 7 ngày tới.

    `ketQuaKinhDoanh`: `{"NVDA": "2026-11-18", …}` — người vận hành khai;
    không có nguồn miễn phí nào đáng tin cho lịch này, và một lịch bịa thì
    tệ hơn không có. `hetThuong`: giờ chương trình thưởng kết thúc.
    """
    now = (luc or dt.datetime.now(UTC)).astimezone(VN)
    conHan = lich_con_han(now.date())

    # phiên hôm nay, hoặc phiên kế tiếp
    trangThai, phienKe = CUOI_TUAN, None
    d = now.date()
    for _ in range(10):
        ph = phien_my(d)
        if ph and ph[1] > now:
            phienKe = ph
            break
        d += dt.timedelta(days=1)
    gioToiMo = gioToiDong = None
    if phienKe:
        mo, dong = phienKe
        if mo <= now < dong:
            trangThai = MO_CUA
            gioToiDong = (dong - now).total_seconds() / 3600.0
        else:
            gioToiMo = (mo - now).total_seconds() / 3600.0
            if gioToiMo * 60.0 <= phutTruocMo:
                trangThai = TRUOC_MO
            elif ngay_giao_dich(now.date()) and now < mo:
                trangThai = SAU_DONG      # sáng sớm VN của một ngày thường Mỹ
            elif ngay_giao_dich(now.date()):
                trangThai = SAU_DONG
            else:
                trangThai = CUOI_TUAN

    sk = []
    han = now + dt.timedelta(days=7)
    for nam in (now.year, now.year + 1):
        for s in FOMC.get(nam, ()):
            ng = dt.date.fromisoformat(s)
            t = dt.datetime.combine(ng, dt.time(14, 0), mui_gio_et(ng)).astimezone(VN)
            if now <= t <= han:
                sk.append(SuKien(t, "fomc", "FOMC công bố lãi suất"))
    for ma, s in (ketQuaKinhDoanh or {}).items():
        try:
            ng = dt.date.fromisoformat(str(s))
        except ValueError:
            continue
        t = dt.datetime.combine(ng, dt.time(16, 0), mui_gio_et(ng)).astimezone(VN)
        if now <= t <= han:
            sk.append(SuKien(t, "ket-qua-kinh-doanh", f"{ma} công bố kết quả", ma))
    if hetThuong is not None and now <= hetThuong.astimezone(VN) <= han:
        sk.append(SuKien(hetThuong.astimezone(VN), "het-thuong",
                         "chương trình thưởng kết thúc"))
    if phienKe:
        if phienKe[0] > now:
            sk.append(SuKien(phienKe[0], "mo-cua", "sàn Mỹ mở cửa"))
        sk.append(SuKien(phienKe[1], "dong-cua", "sàn Mỹ đóng cửa"))
    for s in (suKienThem or ()):
        if now <= s.luc <= han:
            sk.append(s)
    sk.sort(key=lambda s: s.luc)
    return BoiCanhPhien(luc=now, trangThai=trangThai, phienKe=phienKe,
                        gioToiMo=gioToiMo, gioToiDong=gioToiDong,
                        lichConHan=conHan, suKien=tuple(sk))


def doc_gio_vn(s: str) -> dt.datetime:
    """`"2026-09-07 14:00"` → datetime giờ VN. Chuỗi rỗng → ValueError."""
    return dt.datetime.strptime(s.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=VN)
