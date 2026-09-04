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
    esport            liquipedia.net MediaWiki API     ~ trả lời được,
                                                         chưa kiểm kết quả
    kinh tế theo lịch FRED / bản công bố chính thức    ~ đúng lịch, THƯA
    bầu cử · địa chính trị · văn hoá                    ✗ không có

## Điều lượt chạy THẬT đầu tiên nói, và nó ngược với dự đoán

Đo 05/09/2026 trên 1.500 market đang mở:

    thể thao ĐIỆN TỬ   843   ngã ngũ ~2 ngày
    thể thao thường    340   ngã ngũ ~2 ngày
    chưa phân loại     159
    crypto              60   ngã ngũ ~1 ngày
    chính trị           53   ngã ngũ ~51 ngày
    nhiệt độ            45   ngã ngũ ~2 ngày

Cung này đang dựng động cơ cho họ 60 market, và vừa dựng thêm một động
cơ cho họ 45 market. Họ 843 market thì chưa có một dòng mã nào.

Đó chính là câu trả lời cho "sao cứ crypto mãi" — và nó không phải câu
trả lời tôi đoán trước khi đo (tôi đoán thời tiết).

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
from kham.nguon import nguon  # noqa: E402

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
    # Nguồn của esport KHÁC hẳn nguồn thể thao thường, và đây là chỗ
    # dễ khai bừa nhất: `thesportsdb` không biết gì về CS2.
    #
    # Đo 05/09/2026 bằng client bền: HLTV chặn bot (ConnectError),
    # PandaScore đòi khoá (403), **Liquipedia MediaWiki API trả 200**.
    #
    # ⚠ CHƯA KIỂM: mới xác nhận API ấy TRẢ LỜI, chưa xác nhận lấy được
    # KẾT QUẢ TỪNG TRẬN ở dạng dùng được. Nên ghi "mong" chứ không ghi
    # "day" — cửa thứ ba mà khai rộng tay thì nó không còn là cửa.
    "esport":    ("liquipedia.net MediaWiki API", "mong",
                  "chưa dựng — nguồn mới xác nhận TRẢ LỜI, chưa xác "
                  "nhận lấy được kết quả trận"),
    # CỔ PHIẾU / CHỈ SỐ / HÀNG HOÁ — họ lớn nhất trong rổ còn SỐNG, và
    # là họ có hình dạng toán học GIỐNG HỆT động cơ crypto đang chạy:
    # một giá, một mốc, một hạn, rồi Φ(z). Đổi nguồn giá là xong phần
    # lớn việc.
    #
    # Đo 05/09/2026 bằng client bền: Yahoo chart API trả 200 kèm giá
    # thật, KHÔNG cần khoá (`query1.finance.yahoo.com/v8/finance/chart/
    # AAPL?range=5d&interval=1d`). Nasdaq và Alpha Vantage cũng 200.
    "co-phieu":  ("Yahoo Finance chart API (không cần khoá)", "day",
                  "chưa dựng — CÙNG hình dạng với updown-crypto"),
    "kinh-te":   ("FRED · bản công bố chính thức", "thua", "chưa dựng"),
    "chinh-tri": (None, "khong", "KHÔNG có nguồn để chấm"),
    "van-hoa":   (None, "khong", "KHÔNG có nguồn để chấm"),
    "khac":      (None, "khong", "chưa phân loại"),
}

from kham.ho_market import ho_cua as _ho  # noqa: E402


def _bay_gio_iso() -> str:
    """Mốc `end_date_min` cho Gamma: bây giờ, theo ISO UTC."""
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tai_json(url: str, tham: dict, lanThu: int = 14):
    """GET qua CLIENT BỀN của runtime, thử lại khi nối hỏng. None = chịu.

    ## Vì sao không gọi `curl` mỗi lượt, và vì sao chuyện này từng bị
    ## chẩn đoán SAI thành "bị chặn"

    Từ máy này, MỞ một kết nối tới `*.polymarket.com` hỏng rất thường:
    đo 05/09/2026 bằng `httpx.get` (mỗi lượt một kết nối mới) được
    **3/12**, `curl` được **0/4**. Nhìn con số ấy rất giống một bộ lọc
    theo tên miền, và nó ĐÃ được ghi vào config lẫn sổ tay là "chặn theo
    SNI, đổi DNS hay IP đều vô ích, chỉ proxy mới xong".

    Sai. Đo lại bằng MỘT `httpx.Client` giữ nguyên qua cả loạt:
    **13/15**. Runtime đạt 672/679 vì nó vẫn luôn làm vậy. Hỏng nằm ở
    khâu THIẾT LẬP kết nối; kết nối đã dựng thì chạy bình thường.

    Bài học đắt hơn con số: một tỉ lệ hỏng cao đo bằng công cụ SAI trông
    y hệt một bức tường, và cái kết luận ấy bảo mọi phiên sau bỏ cuộc.

    Nên ở đây dùng đúng `nguon.client()` của runtime — cùng client, cùng
    proxy khai trong config, cùng User-Agent — và thử lại vài lần.
    """
    import time as _t

    c = nguon.client()
    if c is None:
        return None
    for i in range(lanThu):
        try:
            r = c.get(url, params=tham)
            r.raise_for_status()
            return r.json()
        except Exception:                            # noqa: BLE001
            if i == lanThu - 1:
                return None
            # Tỉ lệ nối được đo là ~25% mỗi lượt MỞ MỚI. Sáu lượt cho
            # 1 − 0,75^6 = 82% — tức cứ năm lần chạy thì một lần chịu
            # thua dù đường vẫn bình thường. Mười bốn lượt cho 98%.
            # Trần 4 giây để cả loạt không quá một phút.
            _t.sleep(min(4.0, 0.5 * (i + 1)))
    return None


def _tai(so: int) -> list | None:
    """Lấy danh sách market từ Gamma. None nghĩa là không tới được."""
    goc = CONFIG["nguon"]["polymarketGamma"]
    ra: list = []
    # Gamma chặn `limit` ở 100 và LẶNG LẼ cắt xuống — khai 500 thì
    # trang thứ hai bắt đầu ở offset 500 và bỏ mất 400 market ở giữa,
    # mà bảng in ra vẫn trông đầy đủ.
    buoc = 100
    for lech in range(0, so, buoc):
        # `closed=false` + endDate TĂNG DẦN: đó là rổ đang giao dịch
        # được, đúng thứ câu hỏi này hỏi. Sắp GIẢM dần thì trang đầu
        # toàn market bầu cử hết hạn sau ba năm, và bảng sẽ nói cung
        # này nên dựng động cơ chính trị.
        d = _tai_json(f"{goc}/markets",
                      {"limit": min(buoc, so - lech), "offset": lech,
                       "closed": "false", "order": "endDate",
                       "ascending": "true",
                       # THIẾU `end_date_min` thì `ascending=true` moi
                       # trúng market ĐÃ QUÁ HẠN mà cờ vẫn `active` —
                       # đã ghi trong sổ tay, và tôi vừa đi qua nó một
                       # lần. Bảng đếm sẽ phồng lên bằng xác market.
                       "end_date_min": _bay_gio_iso()})
        if d is None:
            return ra or None
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
            print("  KHÔNG TỚI ĐƯỢC `gamma-api.polymarket.com` sau nhiều")
            print("  lượt thử.")
            print()
            print("  Đường tới host này CHẬP CHỜN chứ không bị chặn: mở kết")
            print("  nối mới hỏng phần lớn số lần, nhưng một kết nối đã dựng")
            print("  thì chạy bình thường (đo 05/09/2026: kết nối mới 3/12,")
            print("  client bền 13/15, runtime 672/679). Script này đã dùng")
            print("  client bền của runtime và thử lại 6 lượt — hỏng cả 6 thì")
            print("  lúc này đường thật sự tắc, thử lại sau.")
            print()
            print("  Muốn chạy ngay không cần mạng thì dùng `--tu-tep=<file>`.")
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
