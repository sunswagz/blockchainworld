"""Suy HỌ MARKET từ slug và câu hỏi. MỘT bản, không có bản sao.

## Con bọ đã sinh ra file này

Bảng dấu hiệu đầu tiên dò bằng CHUỖI CON:

    if any(x in (slug + " " + nhan).lower() for x in tu)

Nó gán họ `crypto` cho một market tên "Something with no family at
all?" — vì "som**eth**ing" chứa `eth`. Ba dấu hiệu ngắn cắn theo đúng
kiểu ấy:

    eth   something · whether · together · method · Ethiopia
    sol   solar · solid · console · resolution · sold
    epl   deploy · replace · people

Hậu quả không dừng ở một nhãn xấu. `sang-ho-market.py` ĐẾM market theo
họ để quyết họ nào đáng dựng động cơ, và `khao-sat-ngay.py` lọc theo họ
để chỉ phán những họ có sự thật nền — nên một market chính trị lọt vào
`crypto` là một phán đoán không bao giờ chấm lại được, nằm trong sổ,
kéo điểm kỹ năng đi mà không ai truy ra vì sao.

## Cách dò đúng: theo TỪ, không theo chuỗi con

Cắt cả slug lẫn câu hỏi thành từ (mọi ký tự không phải chữ-số đều là
dấu cắt — dấu gạch của slug và dấu cách của câu hỏi thành một), rồi:

    dấu hiệu một từ     phải khớp TRỌN một từ
    dấu hiệu nhiều từ   phải khớp một DÃY từ liền nhau
    dấu hiệu tận `-`    khớp TIỀN TỐ của một từ (`temp-` ⇒ temperature)

## Vì sao ở `kham/` chứ không ở `scripts/`

Vì hai script cần nó, và tên file trong `scripts/` mang dấu gạch ngang
nên không nhập chéo được. Bản trước giải bằng cách chép bảng sang cả
hai file kèm một phép kiểm canh cho chúng khớp nhau — nhưng phép kiểm
ấy chỉ canh được HAI BẢNG GIỐNG NHAU, không canh được hai bảng cùng
SAI. Và chúng đã cùng sai.
"""
from __future__ import annotations

import re

#: Dấu hiệu suy họ. Thô, và cố ý thô: nó chỉ để GOM cho người đọc nhìn
#: ra hình dạng, không để quyết định một lệnh nào.
#:
#: Thứ tự CÓ nghĩa — họ nào đứng trước thắng khi một market khớp nhiều
#: họ ("Fed rate cut" khớp cả `kinh-te` lẫn không gì khác, nhưng "Will
#: Bitcoin hit 100k before the election?" khớp cả `crypto` lẫn
#: `chinh-tri`). Crypto đứng đầu vì đó là họ duy nhất cung này có động
#: cơ chạy thật.
DAU_HIEU: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("crypto",    ("btc", "eth", "sol", "xrp", "doge", "bitcoin", "ethereum",
                   "solana", "updown 5m", "updown 15m", "crypto")),
    ("thoi-tiet", ("temperature", "temp-", "highest temp", "weather",
                   "rainfall", "snow", "snowfall", "hurricane")),
    # THỂ THAO ĐIỆN TỬ đứng TRƯỚC thể thao thường, vì `lol` và `cs2`
    # phải thắng trước khi dấu hiệu cấu trúc hay dấu hiệu thể thao
    # thường với tới. Đo 05/09/2026 trên 1.500 market đang mở: 843 là
    # CS2 — hơn NỬA toàn bộ rổ, và bảng bản trước không có một chữ nào
    # về nó, nên nó nằm gọn trong `khac` cùng 86% còn lại.
    #
    # Tách riêng khỏi `the-thao` KHÔNG phải để cho đẹp: nguồn sự thật
    # nền của hai họ khác hẳn nhau, và cửa thứ ba của `sang-ho-market`
    # chỉ có nghĩa khi mỗi họ khai đúng nguồn của mình.
    ("esport",    ("cs2", "csgo", "dota2", "dota", "lol", "valorant",
                   "rocket league", "overwatch", "starcraft", "esport",
                   "esports")),
    ("the-thao",  ("nba", "nfl", "mlb", "nhl", "epl", "ufc", "soccer",
                   "premier league", "world cup", "olympic", "olympics",
                   "atp", "wta", "cricket", "tennis", "golf", "boxing",
                   "formula 1", "nascar", "mma")),
    ("kinh-te",   ("fed", "cpi", "inflation", "unemployment", "gdp",
                   "rate cut", "rate hike", "jobs report", "recession")),
    ("chinh-tri", ("election", "president", "presidential", "senate",
                   "congress", "governor", "primary", "impeach", "impeached",
                   "nominee", "parliament")),
    ("van-hoa",   ("oscar", "oscars", "grammy", "grammys", "emmy", "emmys",
                   "movie", "album", "tiktok", "twitter", "celebrity",
                   "box office")),
)

_CAT = re.compile("[^a-z0-9]+")


def tach_tu(t: str) -> list[str]:
    """Cắt thành từ. Dấu gạch của slug và dấu cách của câu là một."""
    return [x for x in _CAT.split(t.lower()) if x]


def khop(tu: list[str], dau: str) -> bool:
    """Dãy từ `tu` có chứa dấu hiệu `dau` không.

    Tách riêng khỏi `ho_cua` để phép kiểm chọc thẳng vào được — cái
    chết trước nằm đúng ở đây chứ không ở vòng lặp bên ngoài.
    """
    if dau.endswith("-"):
        d = dau[:-1]
        return any(w.startswith(d) for w in tu) if d else False
    c = tach_tu(dau)
    if not c:
        return False
    n = len(c)
    return any(tu[i:i + n] == c for i in range(len(tu) - n + 1))


#: Slug của một TRẬN ĐẤU CÓ LỊCH: mã giải, hai mã đội, rồi ngày.
#:
#:     bl2-h96-ksc-2025-11-28-h96      es2-cor-cad-2025-11-30-cor
#:
#: Đây là dấu hiệu CẤU TRÚC, không phải từ khoá — và nó cần thiết vì mã
#: giải thì vô hạn (bl2, es2, rt1, inf1, lph, crint…). Không ai gõ hết
#: được vào một bảng, và mỗi mã thiếu là một market rơi vào "khac".
#:
#: Đòi ĐỦ ba phần (mã giải + hai mã đội + ngày y-m-d) nên nó không quơ
#: bừa: một slug thường như `will-israel-launch-a-major-ground-offensive`
#: không có ngày ở dạng ấy.
#: Tháng và ngày phải là tháng và ngày THẬT. Bản đầu viết `[0-1][0-9]`
#: cho tháng — nhận cả `2025-13-28`, và phép kiểm bắt được ngay. Một
#: mẫu lỏng ở đây gán nhãn `the-thao` cho slug bất kỳ có ba đoạn chữ
#: rồi ba đoạn số, và bộ phân loại quơ bừa còn tệ hơn bộ bỏ sót: nó
#: gán nhãn một cách tự tin.
_TRAN_CO_LICH = re.compile(
    r"^[a-z]{2,5}[0-9]?-[a-z0-9]{2,5}-[a-z0-9]{2,5}-"
    r"(19|20)[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])(-|$)")


def la_tran_co_lich(slug: str) -> bool:
    """Slug có dạng một trận đấu đã lên lịch không."""
    return bool(_TRAN_CO_LICH.match(str(slug).lower()))


#: Market NGƯỠNG GIÁ: `<mã>-<động từ giá>-...`
#:
#:     aapl-above-290-on-september-4-2026
#:     will-nvda-reach-200-by-august-31-2026
#:     will-msft-close-between-500-and-505-week-september-4-2026
#:
#: Đây là dấu hiệu theo NGỮ CẢNH, và ngữ cảnh mới là thứ làm nó an
#: toàn. Ba mã trong danh sách dưới là từ tiếng Anh thường — `open`
#: (Opendoor), `mu` (Micron), `meta` — nên khớp chúng như từ trần sẽ
#: gán nhãn cổ phiếu cho hàng loạt market chẳng liên quan. Đòi ngay
#: sau mã phải là một động từ giá thì chuyện ấy không xảy ra.
_NGUONG_GIA = re.compile(
    r"^(?:will-)?([a-z]{1,5})-"
    r"(above|below|reach|close|dip|hit|up|down)(-|$)")

#: Mã CRYPTO gặp trong market ngưỡng giá. Chúng phải về họ `crypto` —
#: nguồn sự thật của chúng là nến Binance, không phải sàn chứng khoán,
#: và cửa thứ ba của `sang-ho-market` chỉ có nghĩa khi khai đúng nguồn.
MA_CRYPTO = frozenset((
    "btc", "eth", "sol", "xrp", "doge", "bnb", "hype", "zec", "ltc",
    "ada", "avax", "link", "dot", "matic", "trx", "sui", "ton"))

#: Mã CỔ PHIẾU / CHỈ SỐ / HÀNG HOÁ. Rút từ chính 1.500 market đang mở
#: (đo 05/09/2026): 719/779 market chưa phân loại khớp mẫu ngưỡng giá,
#: và đây là toàn bộ mã xuất hiện.
MA_TAI_CHINH = frozenset((
    # cổ phiếu
    "aapl", "abnb", "amzn", "coin", "googl", "hood", "meta", "msft",
    "mstr", "mu", "nflx", "nvda", "open", "pltr", "rklb", "spcx",
    "tsla", "amd", "intc", "baba", "uber", "sofi", "gme", "amc",
    # chỉ số và quỹ
    "spx", "spy", "qqq", "djia", "rut", "nya", "dxy", "ewy", "skhy",
    "iwm", "vix",
    # hàng hoá
    "wti", "ng", "gold", "xau", "brent"))


def ma_nguong_gia(slug: str) -> str | None:
    """Mã của một market ngưỡng giá, hoặc None nếu slug không phải dạng ấy."""
    g = _NGUONG_GIA.match(str(slug).lower())
    return g.group(1) if g else None


def ho_cua(slug: str, nhan: str = "") -> str:
    """Họ của một market. `khac` khi không dấu hiệu nào khớp."""
    tu = tach_tu(str(slug) + " " + str(nhan))
    for ho, ds in DAU_HIEU:
        if any(khop(tu, x) for x in ds):
            return ho
    # Dấu hiệu cấu trúc xét SAU cùng: một trận `cs2-...` đã được bảng
    # trên bắt rồi, và thứ tự này giữ cho bảng vẫn là nơi quyết định
    # chính — dấu hiệu cấu trúc chỉ vét phần bảng không với tới.
    ma = ma_nguong_gia(slug)
    if ma is not None:
        if ma in MA_CRYPTO:
            return "crypto"
        if ma in MA_TAI_CHINH:
            return "co-phieu"
    if la_tran_co_lich(slug):
        return "the-thao"
    return "khac"
