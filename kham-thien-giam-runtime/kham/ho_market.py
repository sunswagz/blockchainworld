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
    ("the-thao",  ("nba", "nfl", "mlb", "nhl", "epl", "ufc", "soccer",
                   "premier league", "world cup", "olympic", "olympics")),
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


def ho_cua(slug: str, nhan: str = "") -> str:
    """Họ của một market. `khac` khi không dấu hiệu nào khớp."""
    tu = tach_tu(str(slug) + " " + str(nhan))
    for ho, ds in DAU_HIEU:
        if any(khop(tu, x) for x in ds):
            return ho
    return "khac"
