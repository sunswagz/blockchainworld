"""Họ market NHIỆT ĐỘ có đo được không — và mô hình có kỹ năng ở chỗ CÓ TIỀN không?

    python scripts/do-nhiet-do.py                    10 trạm, 3 năm
    python scripts/do-nhiet-do.py --nam=1 --tram=USW00094728
    python scripts/do-nhiet-do.py --nam=3 --lui=1095   quãng CŨ, không chồng lấn

## Vì sao có file này

Cung này chỉ theo bốn market crypto 5 phút. Không phải vì crypto hấp
dẫn nhất, mà vì nó là họ DUY NHẤT có đủ hai thứ:

    giá trị đúng   tính được bằng công thức đóng (Φ của z)
    sự thật nền    dày, lấy được hàng loạt, miễn phí (nến Binance)

Mọi kỷ luật của cung — Brier, điểm kỹ năng, đường nắn, bootstrap chia
khối — sống nhờ thứ thứ hai. Một market "Fed có hạ lãi suất tháng Ba
không" ngã ngũ ĐÚNG MỘT LẦN; không có gì để chấm lại.

Nhiệt độ là họ đầu tiên ngoài crypto qua được cả hai cửa:

    dự báo      open-meteo (kho lưu trữ) · api.weather.gov (NWS)
    sự thật     NOAA NCEI daily-summaries — nhiệt độ THỰC ĐO tại trạm,
                từng ngày, hàng chục năm, miễn phí, không cần khoá

Và đo được NGAY, không cần Polymarket — y như mô hình crypto được chấm
bằng nến Binance trong lúc đường tới sàn đứt.

## Mô hình

    P(TMAX > K) = Φ( (duBao − thienLech − K) / sigma )

`thienLech` và `sigma` đo TỪNG TRẠM, không đặt tay: dự báo lưới so với
trạm đo có lệch hệ thống riêng của từng nơi (đo được: Phoenix −2,12 °F,
New York −0,02 °F). Và phải ước trên CỬA SỔ TRƯỢT — xem mục dưới.

## Câu hỏi ĐÚNG: ngưỡng đặt QUANH dự báo, không phải ngưỡng cố định

Bản đầu chấm ở 70/75/80/85/90 °F cố định. Sai đề: 85 °F ở Phoenix là
chuyện thường ngày, ở Seattle là kỷ lục. Điểm kỹ năng cao ở ngưỡng XA
dự báo chỉ nói "mô hình biết tháng Tám nóng" — mà chợ cũng biết, và nó
yết 0,99.

Chỗ có tiền là ngưỡng SÁT dự báo. Nên nay sinh ngưỡng theo `duBao + d`
với d ∈ {−4 … +4} °F rồi gom kết quả theo |z| = |duBao − lệch − K| / σ.
Ở |z| nhỏ, tỉ lệ nền tự khắc về 0,5 — và điểm kỹ năng khi ấy đo đúng
thứ đáng đo: mô hình có biết gì hơn một đồng xu không.

## KẾT QUẢ 03/09/2026 — 10 trạm, hai quãng BA NĂM không chồng lấn

Ngưỡng sinh quanh dự báo (±4 °F), gom theo |z|, khối bootstrap là TUẦN
gộp mọi trạm, ước thiên lệch/σ bằng CỬA SỔ TRƯỢT 45 ngày:

    |z|          3 năm gần            3 năm CŨ (lùi 1095)
    0 – 0,25     +1,9%  TỐT HƠN      +1,6%  TỐT HƠN
    0,25 – 0,5   +8,4%  TỐT HƠN      +9,9%  TỐT HƠN
    0,5 – 1     +30,2%  TỐT HƠN     +28,1%  TỐT HƠN
    1 – 1,5     +56,4%  TỐT HƠN     +57,6%  TỐT HƠN
    1,5 – 2,5   +84,3%  TỐT HƠN     +83,9%  TỐT HƠN

Hai quãng trải sáu năm, không chồng lấn, trùng nhau tới dưới một điểm
phần trăm. Đây là bằng chứng mạnh hơn hẳn mọi thứ từng đo cho các nút
của mô hình crypto.

**Nhưng đọc đúng cái ô đầu tiên.** Ở |z| < 0,25 — chỗ chợ thật sự không
chắc và là chỗ DUY NHẤT có tiền — kỹ năng chỉ **+1,9%**. Nó có ý nghĩa
thống kê, và nó nhỏ. Toàn bộ những con số 80% kia nằm ở nơi câu trả lời
gần như đã định sẵn, nơi chợ cũng yết 0,99.

## CỬA SỔ TRƯỢT: bài học, không phải một tham số

Bản đầu ước thiên lệch/σ MỘT LẦN trên tập HỌC (60% dữ liệu cũ) rồi đem
chấm 40% mới. Kết quả:

    |z| 0 – 0,25   tỉ lệ nền 0,345   kỹ năng −10,2%   TỆ HƠN có ý nghĩa

Mô hình **tệ hơn một kẻ chỉ biết tỉ lệ nền**, đúng ở ô quan trọng nhất.
Dấu hiệu chẩn nằm ngay trong bảng: tỉ lệ nền 0,345 chứ không phải 0,5.
Ngưỡng đặt sát dự báo mà chỉ trúng 34,5% nghĩa là mô hình LỆCH TÂM.

Lý do: lệch dự báo đổi theo MÙA. Chia 60/40 theo thời gian tức là học
trên các tháng khác với các tháng đem chấm, nên phép chỉnh mang mùa cũ.
Cửa sổ trượt 45 ngày đưa tỉ lệ nền về 0,489 và kỹ năng về +1,9%.

Cùng tinh thần với `bienDongCuaSoGiay` của crypto — ước σ trên cửa sổ
GẦN ĐÂY, không trên cả lịch sử. Một hằng số học từ quá khứ xa là một
hằng số của một cái chợ (hay một mùa) không còn tồn tại.

## Ba chỗ dễ tự lừa, đã bịt

1. **NHÌN TRỘM.** Nếu "dự báo lưu trữ" thật ra là phân tích lại sau khi
   biết kết quả thì mọi con số thành rác. Chứng bằng cách so với ERA5;
   script DỪNG nếu chúng quá giống nhau.

2. **KHỐI BOOTSTRAP LÀ TUẦN, GỘP MỌI TRẠM.** Nhiệt độ hai ngày liền
   tương quan rất mạnh (một đợt nóng kéo cả tuần), và các thành phố
   cũng tương quan với nhau. Gộp cả tuần × cả nước thành MỘT khối là
   lựa chọn bảo thủ — nó vứt đi phần thông tin độc lập giữa các miền,
   nhưng thà hẹp hơn sự thật còn hơn rộng hơn. Đếm từng ngày từng trạm
   như quan sát độc lập là tự bịa ra gấp mấy trăm lần bằng chứng.

3. **KỸ NĂNG ≠ LỢI NHUẬN.** Điểm kỹ năng so với TỈ LỆ NỀN, không so với
   GIÁ CHỢ. Chợ đọc được đúng bản dự báo ấy. Con số ở đây nói mô hình
   đáng tin tới đâu, KHÔNG nói có tiền.

## Giới hạn phải khai: TẦM NHÌN

Kho lưu dự báo ở tầm nhìn NGẮN (cỡ 0–1 ngày). Market giao dịch trước
3–5 ngày có σ lớn hơn hẳn và kỹ năng nhỏ hơn. Muốn biết chính xác thì
phải ghi dự báo D+1…D+7 mỗi ngày rồi đối chiếu — dựng một cuốn băng cho
họ này. Chưa làm; đừng đọc con số dưới đây như thể đã làm.
"""
from __future__ import annotations

import json
import math
import random
import statistics
import subprocess
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "tram": "chỉ chạy MỘT trạm, ví dụ USW00094728",
    "nam": "số NĂM lấy về",
    "lui": "lùi mốc kết thúc bấy nhiêu NGÀY — để đo quãng cũ không chồng lấn",
    "cua-so": "số ngày TRƯỢT để ước thiên lệch/σ; 0 = học một lần trên tập HỌC",
}, ten='do-nhiet-do.py')

#: Mười trạm sân bay/thành phố lớn. Chọn theo hai tiêu chí: NOAA có dữ
#: liệu liên tục, và Polymarket từng mở market nhiệt độ cho nơi ấy.
TRAM_BANG = {
    "USW00094728": ("New York (Central Park)", 40.7794, -73.9692),
    "USW00023174": ("Los Angeles (LAX)",       33.9381, -118.3889),
    "USW00094846": ("Chicago (O'Hare)",        41.9950, -87.9336),
    "USW00012839": ("Miami (Intl)",            25.7906, -80.3164),
    "USW00003017": ("Denver (Intl)",           39.8467, -104.6564),
    "USW00023183": ("Phoenix (Sky Harbor)",    33.4278, -112.0039),
    "USW00024233": ("Seattle (SeaTac)",        47.4444, -122.3139),
    "USW00013874": ("Atlanta (Hartsfield)",    33.6300, -84.4425),
    "USW00013743": ("Washington (Reagan)",     38.8483, -77.0342),
    "USW00012960": ("Houston (Hobby)",         29.6375, -95.2822),
}

SO_NAM = float(CO.lay("nam", "3"))
LUI = int(CO.lay("lui", "0"))
MOT_TRAM = CO.lay("tram", "")
CUA_SO = int(CO.lay("cua-so", "0"))

CHIA_HOC = 0.60
LECH_NGUONG = (-4, -3, -2, -1, 0, 1, 2, 3, 4)      # °F quanh dự báo
O_Z = ((0.0, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.5))


def _lay(u: str) -> object | None:
    """Gọi bằng `curl`, KHÔNG bằng httpx, và THỬ LẠI.

    Đo 02/09/2026: hai host open-meteo chập chờn qua httpx trên máy này
    — treo bắt tay TLS, hoặc đọc quá hạn sau 43 giây — trong khi `curl`
    trả 200 đều. NOAA thì cả hai đều nhanh.

    Và phải thử lại: một lượt chạy đã trả rỗng khiến phép đo báo "khớp
    0 ngày", rồi lượt sau trả đủ 366 ngày. Không thử lại thì người đọc
    đi tìm lỗi trong mã, chỗ không có lỗi nào.
    """
    for lan in range(4):
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "120", u],
                               capture_output=True, text=True, timeout=180)
        except (OSError, subprocess.SubprocessError):
            r = None
        if r is not None and r.stdout:
            try:
                return json.loads(r.stdout)
            except json.JSONDecodeError:
                pass
        if lan < 3:
            import time as _t
            _t.sleep(2.0 * (lan + 1))
    return None


def _ngay_lui(n: int) -> str:
    import datetime as dt
    return (dt.date.today() - dt.timedelta(days=n)).isoformat()


def _ngay(u: str, khoa: str) -> dict:
    d = _lay(u)
    if not isinstance(d, dict) or "daily" not in d:
        return {}
    dd = d["daily"]
    return {t: v for t, v in zip(dd["time"], dd[khoa]) if v is not None}


def _du_bao(lat, lon, tu, den) -> dict:
    return _ngay(
        f"https://historical-forecast-api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&start_date={tu}&end_date={den}"
        f"&daily=temperature_2m_max&temperature_unit=fahrenheit"
        f"&timezone=auto", "temperature_2m_max")


def _era5(lat, lon, tu, den) -> dict:
    return _ngay(
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}&start_date={tu}&end_date={den}"
        f"&daily=temperature_2m_max&temperature_unit=fahrenheit"
        f"&timezone=auto", "temperature_2m_max")


def _thuc_do(tram, tu, den) -> dict:
    d = _lay(f"https://www.ncei.noaa.gov/access/services/data/v1"
             f"?dataset=daily-summaries&stations={tram}"
             f"&startDate={tu}&endDate={den}&dataTypes=TMAX&format=json")
    ra = {}
    for r in (d or []):
        try:
            ra[r["DATE"]] = float(r["TMAX"]) / 10.0 * 9 / 5 + 32
        except (TypeError, ValueError, KeyError):
            continue
    return ra


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _tuan(ngay: str) -> str:
    """Khối bootstrap = TUẦN, GỘP mọi trạm. Bảo thủ, và cố ý."""
    import datetime as dt
    y, w, _ = dt.date.fromisoformat(ngay).isocalendar()
    return f"{y}-{w:02d}"


def _khoang_tin(hieu: list[float], khoi: list[str], soLan: int = 2000):
    if not hieu:
        return (0.0, 0.0, 0)
    nhom: dict = {}
    for h, k in zip(hieu, khoi):
        nhom.setdefault(k, []).append(h)
    ds = list(nhom.values())
    rd = random.Random(20260903)
    lan = []
    for _ in range(soLan):
        t = c = 0.0
        for _k in range(len(ds)):
            b = ds[rd.randrange(len(ds))]
            t += sum(b)
            c += len(b)
        lan.append(t / max(1.0, c))
    lan.sort()
    return (lan[int(0.025 * soLan)], lan[int(0.975 * soLan)], len(ds))


def _cham(cap: list, ten: str) -> None:
    """cap = [(p, thắng, khối)]. In một dòng chấm điểm có khoảng tin."""
    if len(cap) < 200:
        print(f"    {ten:<16}{len(cap):>7}  chưa đủ mẫu")
        return
    nen = sum(1 for _, t, _ in cap if t) / len(cap)
    if nen <= 0.0 or nen >= 1.0:
        print(f"    {ten:<16}{len(cap):>7}  mọi ngày cùng kết quả")
        return
    saiN = [(nen - (1.0 if t else 0.0)) ** 2 for _, t, _ in cap]
    saiM = [(p - (1.0 if t else 0.0)) ** 2 for p, t, _ in cap]
    bN, bM = statistics.fmean(saiN), statistics.fmean(saiM)
    ky = 1 - bM / bN if bN > 0 else float("nan")
    thap, cao, soK = _khoang_tin([saiM[i] - saiN[i] for i in range(len(cap))],
                                 [c[2] for c in cap])
    dau = "TỐT HƠN" if cao < 0 else ("TỆ HƠN" if thap > 0 else "chứa 0")
    print(f"    {ten:<16}{len(cap):>7}{nen:>10.3f}{bN:>10.4f}{bM:>10.4f}"
          f"{ky:>+9.1%}  [{thap:+.4f}, {cao:+.4f}] {soK}t → {dau}")


def main() -> int:
    den = _ngay_lui(LUI + 2)                  # NOAA chậm 1–2 ngày
    tu = _ngay_lui(LUI + 2 + int(SO_NAM * 365))
    bang = ({MOT_TRAM: TRAM_BANG[MOT_TRAM]} if MOT_TRAM in TRAM_BANG
            else TRAM_BANG)

    print()
    print("=" * 82)
    print("  HỌ NHIỆT ĐỘ — mô hình có kỹ năng ở chỗ CÓ TIỀN không")
    print("=" * 82)
    print(f"  {len(bang)} trạm · {tu} .. {den}"
          + (f"  (lùi {LUI} ngày)" if LUI else ""))
    print()

    tat: list[tuple] = []          # (ngày, trạm, dựBáo, thật)
    ngoNhinTrom = 0
    soSanhEra = 0
    for tram, (ten, lat, lon) in bang.items():
        du = _du_bao(lat, lon, tu, den)
        that = _thuc_do(tram, tu, den)
        k = sorted(set(du) & set(that))
        er = _era5(lat, lon, tu, den) if k else {}
        kk = [x for x in k if x in er]
        if len(kk) >= 100:
            soSanhEra += 1
            trung = sum(1 for x in kk if abs(du[x] - er[x]) < 0.05)
            if trung > len(kk) * 0.05:
                ngoNhinTrom += 1
        print(f"    {ten:<26}{len(k):>6} ngày"
              + ("" if len(k) >= 200 else "   ⚠ ít"))
        for x in k:
            tat.append((x, tram, du[x], that[x]))

    if soSanhEra and ngoNhinTrom:
        print()
        print(f"  ⚠ DỪNG: {ngoNhinTrom}/{soSanhEra} trạm có dự báo QUÁ GIỐNG")
        print("    ERA5 — nghi kho lưu trữ là kết quả trá hình.")
        return 2
    if soSanhEra:
        print(f"  chứng KHÔNG nhìn trộm: {soSanhEra} trạm đều khác ERA5 rõ")
    if len(tat) < 2000:
        print(f"\n  chỉ {len(tat)} mẫu — không đủ.\n")
        return 1

    tat.sort()
    cat = int(len(tat) * CHIA_HOC)
    hoc, chot = tat[:cat], tat[cat:]

    # ── thiên lệch và σ: MỘT LẦN hay TRƯỢT ────────────────────────────
    #
    # Học một lần trên tập HỌC là học trên các THÁNG KHÁC. Lệch dự báo
    # đổi theo mùa, nên một hằng số học từ 60% dữ liệu cũ đem dùng cho
    # 40% mới là dùng một phép chỉnh của mùa khác — và nó lộ ra đúng
    # chỗ đau nhất: ô |z| nhỏ, nơi lệch tâm ăn thẳng vào xác suất.
    #
    # `--cua-so=N` ước lại từ N ngày TRƯỚC mỗi mẫu, cùng tinh thần với
    # `bienDongCuaSoGiay` của crypto: ước σ trên cửa sổ gần đây, không
    # trên cả lịch sử.
    theoTram: dict = {}
    for _, tram, du, that in hoc:
        theoTram.setdefault(tram, []).append(du - that)
    ts = {t: (statistics.fmean(v), statistics.pstdev(v))
          for t, v in theoTram.items() if len(v) >= 60}

    lichSu: dict = {}
    for ngay, tram, du, that in tat:
        lichSu.setdefault(tram, []).append((ngay, du - that))
    for t in lichSu:
        lichSu[t].sort()

    def _uoc(tram: str, ngay: str):
        """(thiên lệch, σ) dùng cho mẫu này. Chỉ đọc dữ liệu TRƯỚC `ngay`."""
        if CUA_SO <= 0:
            return ts.get(tram)
        import datetime as dt
        d0 = dt.date.fromisoformat(ngay)
        tuNg = (d0 - dt.timedelta(days=CUA_SO)).isoformat()
        v = [e for n, e in lichSu.get(tram, []) if tuNg <= n < ngay]
        if len(v) < 30:
            return ts.get(tram)
        return (statistics.fmean(v), statistics.pstdev(v))
    print()
    print(f"  HỌC {len(hoc):,} mẫu · CHỐT {len(chot):,} mẫu (tách theo THỜI GIAN)")
    print(f"  ước thiên lệch/σ: " + (f"CỬA SỔ TRƯỢT {CUA_SO} ngày"
          if CUA_SO > 0 else "một lần trên tập HỌC"))
    print(f"  thiên lệch/σ theo trạm (°F):")
    for t, (b, s) in sorted(ts.items(), key=lambda x: x[1][1]):
        print(f"    {TRAM_BANG[t][0]:<26}{b:+7.2f}{s:>8.2f}")

    # sinh ngưỡng QUANH dự báo, gom theo |z|
    theoO: dict = {}
    for ngay, tram, du, that in chot:
        u = _uoc(tram, ngay)
        if u is None:
            continue
        b, s = u
        if s <= 0:
            continue
        for d in LECH_NGUONG:
            K = round(du) + d
            z = (du - b - K) / s
            p = _phi(z)
            for lo, hi in O_Z:
                if lo <= abs(z) < hi:
                    theoO.setdefault((lo, hi), []).append(
                        (p, that > K, _tuan(ngay)))
                    break

    print()
    print("  Ngưỡng sinh quanh dự báo (±4 °F), gom theo |z| — khối là TUẦN:")
    print()
    print(f"    {'|z|':<16}{'n':>7}{'tỉ lệ nền':>10}{'Brier nền':>10}"
          f"{'Brier MH':>10}{'kỹ năng':>9}  khoảng tin 95%")
    for lo, hi in O_Z:
        _cham(theoO.get((lo, hi), []), f"{lo:g} – {hi:g}")

    print()
    print("  ĐỌC KỸ:")
    print("   · Ô |z| NHỎ là chỗ chợ thật sự không chắc, và là chỗ duy")
    print("     nhất có tiền. Ô |z| lớn thì chợ cũng yết 0,99.")
    print("   · Điểm kỹ năng so với TỈ LỆ NỀN, KHÔNG so với giá chợ.")
    print("     Muốn biết có lợi thế hay không thì cần Polymarket.")
    print("   · Tầm nhìn ở đây NGẮN (0–1 ngày). Market giao dịch trước")
    print("     3–5 ngày có σ lớn hơn hẳn.")
    print("=" * 82)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
