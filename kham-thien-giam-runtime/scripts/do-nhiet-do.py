"""Họ market NHIỆT ĐỘ có đo được không — và mô hình có kỹ năng thật không?

    python scripts/do-nhiet-do.py
    python scripts/do-nhiet-do.py --tram=USW00023174 --lat=33.94 --lon=-118.41
    python scripts/do-nhiet-do.py --ngay=730 --lui=365

## Vì sao có file này

Cung này chỉ theo bốn market crypto 5 phút. Không phải vì crypto hấp
dẫn nhất, mà vì nó là họ DUY NHẤT có đủ hai thứ:

    giá trị đúng   tính được bằng công thức đóng (Φ của z)
    sự thật nền    dày, lấy được hàng loạt, miễn phí (nến Binance)

Mọi kỷ luật của cung — Brier, điểm kỹ năng, đường nắn, bootstrap chia
khối — sống nhờ thứ thứ hai. Một market "Fed có hạ lãi suất tháng Ba
không" ngã ngũ ĐÚNG MỘT LẦN; không có gì để chấm lại.

Nhiệt độ là họ đầu tiên ngoài crypto qua được cả hai cửa ấy:

    dự báo      api.weather.gov (NWS chính thức) · open-meteo lưu trữ
    sự thật     NOAA NCEI daily-summaries — nhiệt độ THỰC ĐO tại trạm,
                từng ngày, hàng chục năm, miễn phí, không cần khoá

Và quan trọng: **đo được NGAY, không cần Polymarket.** Giống hệt cách
mô hình crypto được chấm bằng nến Binance trong lúc đường tới sàn đứt.

## Mô hình

    P(TMAX > K) = Φ( (duBao − thienLech − K) / sigma )

`thienLech` và `sigma` KHÔNG đặt tay: chúng đo từ tập HỌC. Dự báo lưới
so với trạm đo có lệch hệ thống (lưới không phải trạm), và phần lệch ấy
là thứ học được.

## Ba chỗ dễ tự lừa, đã bịt

1. **NHÌN TRỘM.** Nếu "dự báo lưu trữ" thật ra là phân tích lại sau khi
   đã biết kết quả thì mọi con số thành rác. Kiểm bằng cách so dự báo
   với ERA5: 4/362 ngày trùng khít (<0,05 °F), lệch tuyệt đối trung
   bình 1,83 °F ⇒ nó là một sản phẩm KHÁC, không phải kết quả trá hình.
   Phép kiểm ấy chạy ngay trong script này.

2. **KHỐI BOOTSTRAP LÀ TUẦN, KHÔNG PHẢI NGÀY.** Nhiệt độ hai ngày liền
   tương quan rất mạnh — một đợt nóng kéo cả tuần. Đếm 362 ngày như 362
   quan sát độc lập là tự bịa ra gấp mấy lần bằng chứng, đúng cái bẫy
   đã cắn cung này BỐN lần ở chiều khác (bốn lát τ của một khung).

3. **KỸ NĂNG ≠ LỢI NHUẬN.** Điểm kỹ năng ở đây so với TỈ LỆ NỀN, tức so
   với một kẻ chỉ biết "tháng Tám thường nóng". Chợ cũng đọc được dự
   báo ấy. Con số cao ở đây KHÔNG nói có tiền — nó nói mô hình đáng tin
   để mang ra so với giá chợ, và chỉ thế thôi.

## Giới hạn phải khai: TẦM NHÌN

Kho `historical-forecast-api` lưu dự báo ở tầm nhìn NGẮN (cỡ 0–1 ngày).
Market nào giao dịch trước 3–5 ngày thì σ thật LỚN HƠN con số ở đây, và
điểm kỹ năng nhỏ hơn. Muốn biết chính xác thì phải ghi dự báo D+1…D+7
mỗi ngày rồi đối chiếu — tức dựng một cuốn băng cho họ này, y như băng
sổ lệnh của crypto. Chưa làm, và đừng đọc con số dưới đây như thể đã
làm.
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
    "tram": "mã trạm NOAA, mặc định USW00094728 (Central Park, NYC)",
    "lat": "vĩ độ điểm dự báo",
    "lon": "kinh độ điểm dự báo",
    "ngay": "số ngày lấy về",
    "lui": "lùi mốc kết thúc bấy nhiêu ngày — để đo quãng CŨ, không chồng lấn",
}, ten='do-nhiet-do.py')

TRAM = CO.lay("tram", "USW00094728")
LAT = float(CO.lay("lat", "40.7794"))
LON = float(CO.lay("lon", "-73.9692"))
SO_NGAY = int(CO.lay("ngay", "365"))
LUI = int(CO.lay("lui", "0"))

CHIA_HOC = 0.60
NGUONG_F = (70, 75, 80, 85, 90)


def _lay(u: str) -> object | None:
    """Gọi bằng `curl`, KHÔNG bằng httpx.

    Đo 02/09/2026: `api.open-meteo.com` và `historical-forecast-api`
    chập chờn qua httpx trên máy này — bắt tay TLS treo, hoặc đọc quá
    hạn sau 43 giây — trong khi `curl` trả 200 đều. NOAA thì cả hai đều
    nhanh. Đây là chuyện của đường mạng máy này, không phải của mã, nên
    dùng lối đi CHẠY ĐƯỢC và ghi rõ vì sao.
    """
    # THỬ LẠI, vì host này CHẬP CHỜN chứ không hỏng hẳn. Một lượt chạy
    # đã trả rỗng rồi lượt sau trả đủ 366 ngày — không thử lại thì phép
    # đo báo "chỉ khớp 0 ngày" và người đọc đi tìm lỗi trong mã.
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


def _du_bao(tu: str, den: str) -> dict:
    d = _lay(f"https://historical-forecast-api.open-meteo.com/v1/forecast"
             f"?latitude={LAT}&longitude={LON}&start_date={tu}&end_date={den}"
             f"&daily=temperature_2m_max&temperature_unit=fahrenheit"
             f"&timezone=America/New_York")
    if not isinstance(d, dict) or "daily" not in d:
        return {}
    dd = d["daily"]
    return {t: v for t, v in zip(dd["time"], dd["temperature_2m_max"])
            if v is not None}


def _era5(tu: str, den: str) -> dict:
    d = _lay(f"https://archive-api.open-meteo.com/v1/archive"
             f"?latitude={LAT}&longitude={LON}&start_date={tu}&end_date={den}"
             f"&daily=temperature_2m_max&temperature_unit=fahrenheit"
             f"&timezone=America/New_York")
    if not isinstance(d, dict) or "daily" not in d:
        return {}
    dd = d["daily"]
    return {t: v for t, v in zip(dd["time"], dd["temperature_2m_max"])
            if v is not None}


def _thuc_do(tu: str, den: str) -> dict:
    d = _lay(f"https://www.ncei.noaa.gov/access/services/data/v1"
             f"?dataset=daily-summaries&stations={TRAM}"
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
    """Khối bootstrap = TUẦN. Hai ngày liền nhau không độc lập."""
    import datetime as dt
    d = dt.date.fromisoformat(ngay)
    y, w, _ = d.isocalendar()
    return f"{y}-{w:02d}"


def _khoang_tin(hieu: list[float], khoi: list[str], soLan: int = 2000):
    """Khoảng tin 95% cho trung bình `hieu`, lấy lại theo KHỐI."""
    if not hieu:
        return (0.0, 0.0, 0)
    nhom: dict = {}
    for h, k in zip(hieu, khoi):
        nhom.setdefault(k, []).append(h)
    ds = list(nhom.values())
    rd = random.Random(20260902)
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


def main() -> int:
    den = _ngay_lui(LUI + 2)          # NOAA chậm 1–2 ngày
    tu = _ngay_lui(LUI + 2 + SO_NGAY)

    print()
    print("=" * 78)
    print("  HỌ NHIỆT ĐỘ — mô hình có kỹ năng thật không")
    print("=" * 78)
    print(f"  trạm {TRAM} · điểm ({LAT}, {LON})")
    print(f"  {tu} .. {den}" + (f"  (lùi {LUI} ngày)" if LUI else ""))
    print("  lấy dự báo lưu trữ, ERA5, và thực đo NOAA…", flush=True)

    du, er, that = _du_bao(tu, den), _era5(tu, den), _thuc_do(tu, den)
    k = sorted(set(du) & set(that))
    if len(k) < 120:
        print(f"  chỉ khớp {len(k)} ngày — không đủ.\n")
        return 1
    print(f"  {len(k)} ngày khớp cả dự báo lẫn thực đo")

    # ── CHỨNG 1: dự báo KHÔNG phải kết quả trá hình ───────────────────
    kk = [x for x in k if x in er]
    if len(kk) >= 100:
        trung = sum(1 for x in kk if abs(du[x] - er[x]) < 0.05)
        lech = statistics.fmean(abs(du[x] - er[x]) for x in kk)
        ok = trung < len(kk) * 0.05 and lech > 0.5
        print(f"  dự báo vs ERA5: {trung}/{len(kk)} ngày trùng khít · "
              f"lệch |TB| {lech:.2f} °F  → "
              + ("KHÁC HẲN, không phải nhìn trộm" if ok
                 else "⚠ QUÁ GIỐNG — nghi nhìn trộm, DỪNG"))
        if not ok:
            print()
            return 2
    else:
        print("  ⚠ không đủ ERA5 để chứng 'không nhìn trộm'")

    cat = int(len(k) * CHIA_HOC)
    hoc, chot = k[:cat], k[cat:]
    tb = statistics.fmean(du[x] - that[x] for x in hoc)
    sd = statistics.pstdev(du[x] - that[x] for x in hoc)
    print(f"  HỌC {len(hoc)} ngày → thiên lệch {tb:+.2f} °F · σ {sd:.2f} °F")
    print(f"  CHỐT {len(chot)} ngày (ngoài mẫu, sau HỌC về thời gian)")
    print()
    print(f"    {'ngưỡng':>8}{'n':>6}{'tỉ lệ nền':>11}{'Brier nền':>11}"
          f"{'Brier MH':>10}{'kỹ năng':>10}   khoảng tin 95% (theo TUẦN)")

    for K in NGUONG_F:
        cap = [(_phi((du[x] - tb - K) / sd), that[x] > K, _tuan(x))
               for x in chot]
        nen = sum(1 for _, t, _ in cap) and \
            sum(1 for _, t, _ in cap if t) / len(cap)
        if nen <= 0.0 or nen >= 1.0:
            print(f"    {K:>8}{len(cap):>6}{nen:>11.3f}"
                  f"        — mọi ngày cùng một kết quả, không chấm được")
            continue
        saiN = [(nen - (1.0 if t else 0.0)) ** 2 for _, t, _ in cap]
        saiM = [(p - (1.0 if t else 0.0)) ** 2 for p, t, _ in cap]
        bN, bM = statistics.fmean(saiN), statistics.fmean(saiM)
        ky = 1 - bM / bN if bN > 0 else float("nan")
        hieu = [saiM[i] - saiN[i] for i in range(len(cap))]
        thap, cao, soK = _khoang_tin(hieu, [c[2] for c in cap])
        dau = "TỐT HƠN" if cao < 0 else ("TỆ HƠN" if thap > 0 else "chứa 0")
        print(f"    {K:>8}{len(cap):>6}{nen:>11.3f}{bN:>11.4f}{bM:>10.4f}"
              f"{ky:>+9.1%}   [{thap:+.4f}, {cao:+.4f}] {soK} tuần → {dau}")

    print()
    print("  ĐỌC KỸ — ba điều con số trên KHÔNG nói:")
    print("   · KHÔNG nói có tiền. Điểm kỹ năng so với TỈ LỆ NỀN, mà chợ")
    print("     cũng đọc được đúng bản dự báo ấy. Muốn biết có lợi thế")
    print("     hay không thì phải so với GIÁ CHỢ — cần Polymarket.")
    print("   · Tầm nhìn ở đây NGẮN (kho lưu dự báo cỡ 0–1 ngày). Market")
    print("     giao dịch trước 3–5 ngày có σ lớn hơn hẳn.")
    print("   · Ngưỡng xa (70, 75) gần như tất định nên điểm kỹ năng cao")
    print("     mà vô dụng — chợ yết 0,99. Chỗ đáng nhìn là ngưỡng SÁT")
    print("     dự báo, nơi kỹ năng thấp đi và bất định mới là thật.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
