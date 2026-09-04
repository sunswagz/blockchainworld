"""SÀNG HỌ MARKET — họ nào đáng dựng động cơ, trả lời bằng BA CON SỐ.

    python scripts/sang-ho-market.py
    python scripts/sang-ho-market.py --tu-tep=data/gamma-mau.json
    python scripts/sang-ho-market.py --ghi=data/gamma-mau.json

## Câu hỏi nó trả lời, và câu nó KHÔNG trả lời

Polymarket rộng: chính trị, thể thao, kinh tế, văn hoá, khoa học,
crypto. Câu hỏi tự nhiên là "hôm nay nên tham gia lĩnh vực nào".

Đó là câu SAI, và sai theo một kiểu đắt. Quét vài trăm market rồi chọn
cái trông ngon nhất là một lượt rút thăm vài trăm lần — cùng cỗ máy đã
buộc cổng tiến hoá phải siết biên theo `log(số ứng viên)`, phóng to
mười lần, và bỏ mất thứ duy nhất bắt được nó là dòng kết quả để chấm
lại. Nó sẽ trông rất thông minh và mất tiền, mà phải mấy tháng mới biết.

Câu ĐÚNG là câu về HỌ, không về hôm nay: **họ nào có đủ điều kiện để
đo?** Vì mọi kỷ luật của cung này — Brier, điểm kỹ năng, đường nắn,
bootstrap chia khối — chỉ chạy được khi có kết quả DÀY để chấm lại.

Ba cửa, và một họ phải qua CẢ BA:

    1. SỐ LƯỢNG    mỗi tuần có bao nhiêu market?
    2. NHỊP NGÃ NGŨ  chúng ngã ngũ theo lịch, hay mỗi năm một lần?
    3. SỰ THẬT NỀN  có nguồn ĐỘC LẬP, lấy được, để chấm không?

Cửa thứ ba là cửa giết nhiều họ nhất, và nó không thương lượng được:

    crypto up/down    nến Binance                      ✓ dày, miễn phí
    nhiệt độ          NOAA NCEI, từng ngày, hàng chục năm  ✓ ĐÃ DỰNG
    thể thao          statsapi.mlb.com · thesportsdb   ✓ dày
    kinh tế theo lịch FRED / bản công bố chính thức    ~ đúng lịch, THƯA
    bầu cử · địa chính trị · văn hoá                    ✗ không có

Nghịch lý phải nói thẳng: những họ MẠNH nhất lại là những họ mô hình
ngôn ngữ đóng góp ÍT nhất (chúng có nguồn số). Những họ nó đóng góp
nhiều nhất lại là những họ KHÔNG có cách nào đo xem nó đóng góp thật
hay chỉ nghe hay.

## Chưa chạy được, và lý do nằm ngoài mã

Cần `gamma-api.polymarket.com` — đúng tên máy đang bị bộ lọc mạng chặn
(xem `//proxyChanDoan` trong config.json). Script này VẪN được viết và
kiểm bằng `--tu-tep`, để lúc có lối ra thì chỉ việc chạy, chứ không
phải bắt đầu nghĩ.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "tu-tep": "đọc từ file JSON đã lưu thay vì gọi mạng",
    "ghi": "lưu bản tải về ra file, để lần sau chạy offline",
    "so-market": "số market tối đa lấy về",
}, ten='sang-ho-market.py')

from kham.config import CONFIG  # noqa: E402

TU_TEP = CO.lay("tu-tep", "")
GHI = CO.lay("ghi", "")
SO_MARKET = int(CO.lay("so-market", "2000"))

#: NGUỒN SỰ THẬT NỀN theo họ — cửa thứ ba, và là cửa giết nhiều họ nhất.
#:
#: Đây là BẢNG KHAI, không phải suy đoán lúc chạy: một họ chỉ được ghi
#: "có nguồn" khi đã có người chỉ ra nguồn ấy lấy được từ máy này. Đo
#: 02–03/09/2026 bằng `curl`: NOAA, statsapi.mlb.com, thesportsdb đều
#: trả 200; `api.football-data.org` bị giết ở tầng TLS như Polymarket.
NGUON_SU_THAT = {
    "crypto":    ("nến Binance", "day", "ĐÃ DỰNG (updown-crypto)"),
    "thoi-tiet": ("NOAA NCEI daily-summaries", "day", "ĐÃ DỰNG (nhiet-do-nguong)"),
    "the-thao":  ("statsapi.mlb.com · thesportsdb", "day", "chưa dựng"),
    "kinh-te":   ("FRED · bản công bố chính thức", "thua", "chưa dựng"),
    "chinh-tri": (None, "khong", "KHÔNG có nguồn để chấm"),
    "van-hoa":   (None, "khong", "KHÔNG có nguồn để chấm"),
    "khac":      (None, "khong", "chưa phân loại"),
}

from kham.ho_market import ho_cua as _ho  # noqa: E402


def _tai(so: int) -> list | None:
    """Lấy danh sách market từ Gamma. None nghĩa là không tới được."""
    goc = CONFIG["nguon"]["polymarketGamma"]
    ra: list = []
    buoc = 500
    for lech in range(0, so, buoc):
        u = (f"{goc}/markets?limit={min(buoc, so - lech)}&offset={lech}"
             f"&order=endDate&ascending=false")
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "40", u],
                               capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            return None
        if not r.stdout:
            return None if not ra else ra
        try:
            d = json.loads(r.stdout)
        except json.JSONDecodeError:
            return None if not ra else ra
        if not isinstance(d, list) or not d:
            break
        ra.extend(d)
        if len(d) < buoc:
            break
    return ra or None


def _ngay(x) -> str:
    return str(x or "")[:10]


def main() -> int:
    print()
    print("=" * 80)
    print("  SÀNG HỌ MARKET — họ nào đáng dựng động cơ")
    print("=" * 80)

    if TU_TEP:
        try:
            ds = json.loads(Path(TU_TEP).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  không đọc được {TU_TEP}: {e}\n")
            return 1
        print(f"  đọc {len(ds):,} market từ {TU_TEP}")
    else:
        print(f"  gọi Gamma (tối đa {SO_MARKET:,} market)…", flush=True)
        ds = _tai(SO_MARKET)
        if not ds:
            print()
            print("  KHÔNG TỚI ĐƯỢC `gamma-api.polymarket.com`.")
            print()
            print("  Đây là chuyện của ĐƯỜNG MẠNG, không phải của mã. Bộ lọc")
            print("  trên máy này khớp theo TÊN MÁY: `docs.polymarket.com`")
            print("  cùng miền vẫn thông, còn gamma/clob/data-api thì chết ở")
            print("  bắt tay TLS. Đổi DNS hay đổi IP đều vô ích — xem")
            print("  `//proxyChanDoan` trong config.json.")
            print()
            print("  Có lối ra rồi thì điền `nguon.proxy` và chạy lại. Muốn")
            print("  thử script này ngay thì dùng `--tu-tep=<file JSON>`.")
            print()
            return 3
        print(f"  lấy được {len(ds):,} market")
        if GHI:
            Path(GHI).parent.mkdir(parents=True, exist_ok=True)
            Path(GHI).write_text(json.dumps(ds, ensure_ascii=False),
                                 encoding="utf-8")
            print(f"  đã lưu ra {GHI}")

    # ── gom theo họ ───────────────────────────────────────────────────
    theoHo: dict = {}
    for m in ds:
        if not isinstance(m, dict):
            continue
        ho = _ho(str(m.get("slug") or ""), str(m.get("question") or ""))
        theoHo.setdefault(ho, []).append(m)

    print()
    print(f"    {'họ':<12}{'market':>8}{'đã ngã ngũ':>12}{'sống TB':>10}"
          f"   nguồn sự thật nền")
    print("    " + "─" * 74)

    xep = []
    for ho, ms in sorted(theoHo.items(), key=lambda x: -len(x[1])):
        song = []
        for m in ms:
            a, b = _ngay(m.get("startDate")), _ngay(m.get("endDate"))
            if len(a) == 10 and len(b) == 10 and b > a:
                import datetime as dt
                try:
                    song.append((dt.date.fromisoformat(b)
                                 - dt.date.fromisoformat(a)).days)
                except ValueError:
                    pass
        daXong = sum(1 for m in ms if m.get("closed") or m.get("resolved"))
        tb = statistics.median(song) if song else None
        nguon, day, ghiChu = NGUON_SU_THAT.get(ho, (None, "khong", "?"))
        print(f"    {ho:<12}{len(ms):>8}{daXong:>12}"
              f"{(f'{tb:.0f}n' if tb is not None else '—'):>10}"
              f"   {ghiChu}")
        xep.append((ho, len(ms), daXong, tb, day, nguon, ghiChu))

    # ── PHÁN QUYẾT: qua cả ba cửa hay không ───────────────────────────
    print()
    print("  BA CỬA — một họ phải qua CẢ BA mới đáng dựng động cơ:")
    print()
    for ho, n, daXong, tb, day, nguon, ghiChu in xep:
        c1 = n >= 50
        c2 = tb is not None and tb <= 45          # ngã ngũ trong 45 ngày
        c3 = day == "day"
        dat = c1 and c2 and c3
        print(f"    {ho:<12} số lượng {'✓' if c1 else '✗'}  "
              f"nhịp {'✓' if c2 else '✗'}  "
              f"sự thật nền {'✓' if c3 else '✗'}   "
              + ("→ ĐÁNG DỰNG" if dat else "→ không"))
        if c3 and nguon:
            print(f"                 nguồn: {nguon}")

    print()
    print("  ĐỌC KỸ: bảng này KHÔNG nói họ nào có tiền. Nó nói họ nào")
    print("  ĐO ĐƯỢC — tức họ nào mà một kết luận sai sẽ lộ ra trong vài")
    print("  tuần thay vì vài năm. Đó là điều kiện CẦN, và ở cung này nó")
    print("  là điều kiện duy nhất từng ngăn được một kết luận đẹp mà sai.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
