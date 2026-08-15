"""Nguồn dữ liệu công khai — KHÔNG cần khoá, không tốn tiền.

Bốn nhóm, bốn nhịp khác nhau, và mỗi nhóm hỏng độc lập:

    phái sinh   Binance Futures — funding, open interest, vị thế TOP TRADER
    vĩ mô       Yahoo Finance   — DXY, lợi suất 10 năm, dầu, S&P 500
    tâm lý      alternative.me  — chỉ số Sợ hãi / Tham lam
    sự kiện     GDELT           — tin tức toàn cầu

Ba luật của file này, mỗi luật vì một chuyện có thể hỏng:

1. **Mỗi nguồn hỏng riêng.** Yahoo ngã thì phái sinh vẫn chạy. Gói tất cả
   vào một try là một nguồn ngã kéo cả bảng về trống.
2. **Nhịp riêng cho từng nguồn, và phải TÔN TRỌNG nó.** GDELT ghi rõ 1
   request / 5 giây; vòng lặp chạy 20 giây mà hỏi mỗi lượt là chắc chắn bị
   chặn. Fear & Greed đổi mỗi ngày — hỏi mỗi phút là phí băng thông của
   người khác cho một con số không đổi.
3. **Luôn khai `co`.** Không có dữ liệu thì `co=False` và giao diện hiện
   "chưa có", chứ không hiện 0. Một chỉ số funding bằng 0 và một chỉ số
   funding chưa lấy được là hai chuyện hoàn toàn khác nhau.
"""
from __future__ import annotations

import re
import threading
import time
from typing import Any

import httpx

from .bus import bus

UA = {"User-Agent": "Mozilla/5.0 (compatible; tu-cam-thanh/0.1)"}

# nhịp tối thiểu giữa hai lần hỏi, giây
NHIP = {"phai_sinh": 120, "vi_mo": 300, "tam_ly": 1800, "su_kien": 900}

_cache: dict[str, dict] = {}


def _lay_cache(khoa: str) -> dict | None:
    c = _cache.get(khoa)
    if c and time.time() - c["luc"] < NHIP.get(khoa, 300):
        return c["gt"]
    return None


def _dat_cache(khoa: str, gt: dict) -> dict:
    _cache[khoa] = {"luc": time.time(), "gt": gt}
    return gt


def _f(x: Any) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ── phái sinh ─────────────────────────────────────────────────────────────
def phai_sinh(client: httpx.Client, symbol: str = "BTCUSDT") -> dict:
    """Funding, open interest, và VỊ THẾ TOP TRADER trên Binance Futures.

    `topLongShortPositionRatio` chính là thứ bản thiết kế gọi là "elite trader
    positioning": tỉ lệ long/short của nhóm tài khoản có ký quỹ lớn nhất sàn.
    Công khai, miễn phí, không cần khoá — không phải dựng cả một tầng thu thập
    vị thế mới có.
    """
    if (c := _lay_cache("phai_sinh")) is not None:
        return c

    out: dict[str, Any] = {"co": False, "nguon": "Binance Futures", "loi": []}
    B = "https://fapi.binance.com"

    def hoi(duong: str, tham: dict) -> Any:
        r = client.get(B + duong, params=tham, headers=UA, timeout=12)
        r.raise_for_status()
        return r.json()

    try:
        pi = hoi("/fapi/v1/premiumIndex", {"symbol": symbol})
        fr = _f(pi.get("lastFundingRate"))
        out["funding"] = fr
        out["fundingPct"] = round(fr * 100, 5) if fr is not None else None
        # Funding năm hoá: 3 lượt/ngày × 365. Con số theo lượt quá nhỏ để
        # người đọc thấy được nó đắt hay rẻ.
        out["fundingNamHoa"] = round(fr * 3 * 365 * 100, 2) if fr is not None else None
        out["markPrice"] = _f(pi.get("markPrice"))
        out["co"] = True
    except Exception as e:  # noqa: BLE001
        out["loi"].append(f"funding: {type(e).__name__}")

    try:
        oi = hoi("/futures/data/openInterestHist", {"symbol": symbol, "period": "1h", "limit": 24})
        if oi:
            nay = _f(oi[-1]["sumOpenInterestValue"])
            truoc = _f(oi[0]["sumOpenInterestValue"])
            out["openInterestUsd"] = nay
            out["oiDoi24hPct"] = round((nay - truoc) / truoc * 100, 2) if truoc else None
            out["co"] = True
    except Exception as e:  # noqa: BLE001
        out["loi"].append(f"OI: {type(e).__name__}")

    for ten, duong in (("topTrader", "/futures/data/topLongShortPositionRatio"),
                       ("toanSan", "/futures/data/globalLongShortAccountRatio"),
                       ("taker", "/futures/data/takerlongshortRatio")):
        try:
            d = hoi(duong, {"symbol": symbol, "period": "1h", "limit": 12})
            if not d:
                continue
            cuoi = d[-1]
            if ten == "taker":
                ty = _f(cuoi.get("buySellRatio"))
                out[ten] = {"tyLe": ty, "long": None, "short": None}
            else:
                out[ten] = {
                    "tyLe": _f(cuoi.get("longShortRatio")),
                    "long": _f(cuoi.get("longAccount")),
                    "short": _f(cuoi.get("shortAccount")),
                }
            # xu hướng: tỉ lệ giờ so với 12 giờ trước
            dau = _f(d[0].get("longShortRatio") or d[0].get("buySellRatio"))
            cur = out[ten]["tyLe"]
            out[ten]["doi12h"] = round(cur - dau, 3) if (dau and cur) else None
            out["co"] = True
        except Exception as e:  # noqa: BLE001
            out["loi"].append(f"{ten}: {type(e).__name__}")

    return _dat_cache("phai_sinh", out)


# ── vĩ mô ─────────────────────────────────────────────────────────────────
MA_VI_MO = [
    ("DXY", "DX-Y.NYB", "chỉ số đô la"),
    ("US10Y", "^TNX", "lợi suất trái phiếu 10 năm"),
    ("DAU", "CL=F", "dầu WTI"),
    ("SP500", "^GSPC", "S&P 500"),
    ("VANG", "GC=F", "vàng"),
]


def vi_mo(client: httpx.Client) -> dict:
    """DXY, lợi suất, dầu, chứng khoán, vàng — Yahoo Finance, không cần khoá.

    Cùng nguồn `scripts/build-quantrac.mjs` của Đài Quan Trắc đang dùng, nên
    đây không phải một phụ thuộc mới với repo.
    """
    if (c := _lay_cache("vi_mo")) is not None:
        return c

    out: dict[str, Any] = {"co": False, "nguon": "Yahoo Finance", "muc": {}, "loi": []}
    for ma, ky_hieu, ten in MA_VI_MO:
        try:
            r = client.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ky_hieu}",
                           params={"range": "5d", "interval": "1d"}, headers=UA, timeout=12)
            r.raise_for_status()
            kq = r.json()["chart"]["result"][0]
            dong = [x for x in kq["indicators"]["quote"][0]["close"] if x is not None]
            if len(dong) < 2:
                continue
            nay, truoc = dong[-1], dong[-2]
            out["muc"][ma] = {
                "ten": ten, "gia": round(nay, 3),
                "doiPct": round((nay - truoc) / truoc * 100, 2),
            }
            out["co"] = True
        except Exception as e:  # noqa: BLE001
            out["loi"].append(f"{ma}: {type(e).__name__}")

    # Đọc thành "khẩu vị rủi ro". Đây là SUY LUẬN từ số, không phải số —
    # nên ghi rõ là suy luận và cho thấy nó dựa trên mấy chỉ số.
    m = out["muc"]
    diem, dem = 0, 0
    if "DXY" in m:   diem -= m["DXY"]["doiPct"];   dem += 1   # đô mạnh = risk-off
    if "US10Y" in m: diem -= m["US10Y"]["doiPct"] * 0.5; dem += 1
    if "SP500" in m: diem += m["SP500"]["doiPct"] * 1.5; dem += 1
    out["khauVi"] = {
        "diem": round(diem, 2), "soChiSo": dem,
        "nhan": "RISK_ON" if diem > 0.3 else "RISK_OFF" if diem < -0.3 else "TRUNG_TINH",
        "ghiChu": "suy ra từ chiều đổi của DXY, lợi suất và S&P — không phải một chỉ số có sẵn",
    }
    return _dat_cache("vi_mo", out)


# ── tâm lý ────────────────────────────────────────────────────────────────
def tam_ly(client: httpx.Client) -> dict:
    """Chỉ số Sợ hãi / Tham lam. Đổi mỗi ngày nên nhịp hỏi 30 phút là quá đủ."""
    if (c := _lay_cache("tam_ly")) is not None:
        return c
    out: dict[str, Any] = {"co": False, "nguon": "alternative.me"}
    try:
        r = client.get("https://api.alternative.me/fng/", params={"limit": 8}, headers=UA, timeout=12)
        r.raise_for_status()
        d = r.json()["data"]
        out.update({
            "co": True,
            "gt": int(d[0]["value"]),
            "nhan": d[0]["value_classification"],
            "chuoi": [int(x["value"]) for x in reversed(d)],
            "doi7ngay": int(d[0]["value"]) - int(d[-1]["value"]) if len(d) > 1 else None,
        })
    except Exception as e:  # noqa: BLE001
        out["loi"] = f"{type(e).__name__}"
    return _dat_cache("tam_ly", out)


# ── sự kiện ───────────────────────────────────────────────────────────────
# Nguồn tin: RSS. Đo tại máy này, GDELT chặn theo tải chứ không theo đồng hồ —
# giãn 5,5s rớt 4/5, giãn 8s vẫn rớt 3/5 — nên nó không đủ tin cậy để làm nguồn
# chính. RSS thì không giới hạn nhịp, và ba feed dưới đây là NGUỒN SƠ CẤP: Fed,
# SEC và BLS tự công bố. Tin lãi suất đọc thẳng từ Fed đúng hơn đọc lại qua một
# toà soạn, và sớm hơn.
FEED = [
    ("Fed", "https://www.federalreserve.gov/feeds/press_monetary.xml", "chính sách"),
    ("Fed·all", "https://www.federalreserve.gov/feeds/press_all.xml", "chính sách"),
    ("BLS", "https://www.bls.gov/feed/bls_latest.rss", "số liệu"),
    ("SEC", "https://www.sec.gov/news/pressreleases.rss", "pháp lý"),
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", "crypto"),
    ("Cointelegraph", "https://cointelegraph.com/rss", "crypto"),
    ("Decrypt", "https://decrypt.co/feed", "crypto"),
    ("CNBC", "https://www.cnbc.com/id/10000664/device/rss/rss.html", "thị trường"),
    ("Yahoo", "https://finance.yahoo.com/news/rssindex", "thị trường"),
]

# Phân loại bằng từ khoá. Thô, nhưng KIỂM ĐƯỢC: mỗi bài mang theo từ khoá đã
# khớp nên nhìn là biết vì sao nó nằm ở nhóm đó. Cho một mô hình phân loại ở
# tầng thu thập thì gọn hơn, nhưng lúc nó gán sai sẽ không ai truy ra được.
#
# So khớp theo RANH GIỚI TỪ, không phải chuỗi con. Lần chạy đầu để chuỗi con,
# tin "SEC Charges **Boiler** Room Operator" rơi vào nhóm vĩ mô vì "oil" nằm
# trong "b-oil-er". Loại sai kiểu đó không báo lỗi ở đâu cả — nó chỉ lặng lẽ
# làm bảng tin sai.
CHU_DE = [
    # Cố tình KHÔNG có từ khoá "federal reserve" trần. Fed công bố đủ thứ — án
    # phạt ngân hàng, bổ nhiệm nhân sự — và bắt theo tên cơ quan thì nhóm này
    # thành "mọi thứ Fed nói" thay vì "Fed vừa động vào lãi suất". Chỉ bắt theo
    # CÔNG CỤ CHÍNH SÁCH. Cả dạng số ít lẫn số nhiều, vì `\brate\b` không khớp
    # "rates" — thiếu dạng số nhiều là im lặng bỏ sót đúng tin quan trọng nhất.
    ("FED", ["fomc", "open market committee", "monetary policy", "powell",
             "interest rate", "interest rates", "rate cut", "rate cuts",
             "rate hike", "rate hikes", "rate decision", "cuts rates",
             "raises rates", "basis point", "basis points", "discount rate",
             "fed funds", "federal funds", "quantitative easing",
             "quantitative tightening"], ["USD", "BTC", "chứng khoán"]),
    ("LAM_PHAT", ["inflation", "cpi", "consumer price", "ppi", "producer price",
                  "pce", "jobs report", "payroll", "unemployment", "labor market",
                  "jobless claims"], ["USD", "BTC", "trái phiếu"]),
    # Nhóm DUY NHẤT cần hai điều kiện — xem `KEM` bên dưới.
    ("QUY_DINH", ["regulation", "regulatory", "sec", "cftc", "lawsuit", "charges",
                  "enforcement", "ruling", "approve", "approval", "ban", "license",
                  "genius act", "clarity act", "custody"], ["BTC", "ETH", "sàn"]),
    ("ETF", ["etf", "etfs", "inflow", "inflows", "outflow", "outflows", "blackrock",
             "grayscale", "fidelity", "ibit", "spot bitcoin"], ["BTC", "ETH"]),
    ("VI_MO", ["oil", "opec", "crude", "tariff", "tariffs", "gdp", "recession",
               "treasury yield", "bond yield", "bond yields", "yields",
               "dollar index", "trade war", "trade deficit", "gold"],
     ["dầu", "lạm phát", "tài sản rủi ro"]),
]

# Điều kiện KÈM: chủ đề có mặt ở đây phải khớp thêm một từ trong danh sách này
# thì mới được nhận. "Quy định" mà chỉ xét từ pháp lý thì nuốt trọn mọi án lừa
# đảo thường của SEC; mà chỉ xét từ crypto thì nuốt mọi tin crypto. Phải cả hai.
KEM = {
    "QUY_DINH": ["crypto", "cryptocurrency", "bitcoin", "btc", "ether", "ethereum",
                 "digital asset", "stablecoin", "token", "blockchain", "coinbase",
                 "binance", "ripple", "xrp"],
}

_RE: dict[str, Any] = {}
_RE_KEM: dict[str, Any] = {}


def _doc_feed(client: httpx.Client, url: str) -> list[dict]:
    """Đọc một feed RSS/Atom. Dùng ElementTree của stdlib — không thêm gói."""
    import xml.etree.ElementTree as ET

    r = client.get(url, headers=UA, timeout=15)
    r.raise_for_status()
    goc = ET.fromstring(r.content)
    ra = []
    # RSS <item> và Atom <entry> — hai chuẩn, cùng ý nghĩa
    for m in goc.iter():
        the = m.tag.rsplit("}", 1)[-1]
        if the not in ("item", "entry"):
            continue
        d: dict[str, Any] = {}
        for con in m:
            t = con.tag.rsplit("}", 1)[-1]
            if t == "title":
                d["tieuDe"] = (con.text or "").strip()
            elif t == "link":
                d["url"] = (con.text or con.get("href") or "").strip()
            elif t in ("pubDate", "published", "updated", "date"):
                d.setdefault("luc", (con.text or "").strip())
        if d.get("tieuDe"):
            ra.append(d)
    return ra


def _xep_chu_de(tieu_de: str) -> list[tuple[str, str]]:
    """Trả về [(mã chủ đề, từ khoá đã khớp)] — kèm từ khoá để soát được."""
    def bien(ds):
        return [(k, re.compile(r"\b" + re.escape(k) + r"\b", re.I)) for k in ds]

    if not _RE:
        for ma, khoa, _ in CHU_DE:
            _RE[ma] = bien(khoa)
        for ma, ds in KEM.items():
            _RE_KEM[ma] = bien(ds)

    t = tieu_de or ""
    ra = []
    for ma, _, _ in CHU_DE:
        khop = next((k for k, r in _RE[ma] if r.search(t)), None)
        if not khop:
            continue
        if ma in _RE_KEM:
            k2 = next((k for k, r in _RE_KEM[ma] if r.search(t)), None)
            if not k2:
                continue
            khop = f"{khop} + {k2}"
        ra.append((ma, khop))
    return ra


def su_kien(client: httpx.Client, moi_chu_de: int = 6) -> dict:
    """Tin tức, gom từ RSS rồi xếp vào chủ đề.

    Ở đây CHỈ lấy và xếp tin. Biến tin thành chuỗi nhân quả có xác suất là việc
    của bộ não — trộn hai thứ vào nhau thì không ai soát được cái nào sai.
    """
    if (c := _lay_cache("su_kien")) is not None:
        return c

    tat: list[dict] = []
    song, loi = [], []
    for ten, url, loai in FEED:
        try:
            muc = _doc_feed(client, url)
            for m in muc[:25]:
                m.update({"nguon": ten, "loai": loai})
            tat.extend(muc[:25])
            song.append(ten)
        except Exception as e:  # noqa: BLE001
            loi.append(f"{ten}: {type(e).__name__}")

    nhom: dict[str, list] = {ma: [] for ma, _, _ in CHU_DE}
    da_xep = set()
    for i, b in enumerate(tat):
        for ma, khop in _xep_chu_de(b["tieuDe"]):
            da_xep.add(i)
            if len(nhom[ma]) < moi_chu_de:
                nhom[ma].append({**b, "khop": khop})

    out = {
        "co": bool(tat),
        "nguon": "RSS · " + ", ".join(song) if song else "RSS",
        "soFeed": len(song), "tongFeed": len(FEED), "soBai": len(tat),
        "chuDe": [{"ma": ma, "anhHuong": ah, "khoa": khoa[:4],
                   "soBai": len(nhom[ma]), "bai": nhom[ma]}
                  for ma, khoa, ah in CHU_DE],
        # Tin không rơi vào chủ đề nào vẫn giữ lại: bỏ hẳn thì lúc thị trường
        # động vì một lý do chưa có trong danh sách từ khoá, phòng này im lặng.
        "khac": [b for i, b in enumerate(tat) if i not in da_xep][:8],
        "loi": loi,
    }
    return _dat_cache("su_kien", out)


# ── gom ───────────────────────────────────────────────────────────────────
def tat_ca(symbol: str = "BTCUSDT", gom_su_kien: bool = True) -> dict:
    """Gom mọi nguồn. Không ném lỗi — nguồn nào hỏng thì `co=False` nguồn đó."""
    with httpx.Client(follow_redirects=True) as c:
        d = {
            "phaiSinh": phai_sinh(c, symbol),
            "viMo": vi_mo(c),
            "tamLy": tam_ly(c),
            "suKien": su_kien(c) if gom_su_kien else (_lay_cache("su_kien") or {"co": False}),
        }
    hong = [k for k, v in d.items() if not v.get("co")]
    if hong:
        bus.emit("data", "nguon-ngoai-hong", "nguồn chưa lấy được: " + ", ".join(hong))
    return d


# ── vòng nền ──────────────────────────────────────────────────────────────
_kho: dict[str, Any] = {"co": False, "luc": None, "dangLay": False}
_luong: threading.Thread | None = None


def kho() -> dict:
    """Bản gom gần nhất. **Đọc tức thì, không chạm mạng.**

    Vòng giao dịch tuyệt đối không được đứng chờ Yahoo hay GDELT: đo thật, một
    lượt gom đầy đủ mất ~97 giây, trong khi nhịp tick là 20 giây. Gọi thẳng
    `tat_ca()` trong tick là mỗi vòng đều trễ hạn, và một sự cố mạng bên ngoài
    hoá thành sự cố giao dịch. Nên tầng này chỉ đọc thứ luồng nền đã đặt sẵn.
    """
    return _kho


def _vong(symbol: str, nhip: int) -> None:
    while True:
        try:
            _kho["dangLay"] = True
            d = tat_ca(symbol)
            d.update({"co": True, "luc": time.time(), "dangLay": False})
            _kho.clear()
            _kho.update(d)
        except Exception as e:  # noqa: BLE001
            _kho["dangLay"] = False
            bus.emit("data", "nguon-vong-loi", f"vòng nguồn ngoài lỗi: {type(e).__name__}")
        time.sleep(nhip)


def bat_dau(symbol: str = "BTCUSDT", nhip: int = 900) -> None:
    """Khởi động luồng nền. Gọi nhiều lần cũng chỉ có một luồng."""
    global _luong
    if _luong and _luong.is_alive():
        return
    _luong = threading.Thread(target=_vong, args=(symbol, nhip),
                              name="nguon-ngoai", daemon=True)
    _luong.start()
    bus.emit("data", "nguon-vong-chay", f"vòng nguồn ngoài chạy, nhịp {nhip}s")
