"""Tải nến lịch sử về đĩa, để chạy lại không phải gọi mạng mỗi lần.

    python scripts/tai-lich-su.py                      3000 nến, khung trong config
    python scripts/tai-lich-su.py --so 6000
    python scripts/tai-lich-su.py --khung 5m,15m,30m,1h,4h,1d
    python scripts/tai-lich-su.py --coin BTCUSDT,ETHUSDT,SOLUSDT --khung 1h,4h,1d

Binance trả tối đa 1000 nến một lượt, nên phải phân trang lùi theo `endTime`.
Không phân trang thì "3000 nến" lặng lẽ thành 1000 — và một backtest trên 1000
nến 1h chỉ là 6 tuần, quá ngắn để nói được gì về một chiến lược.

VÌ SAO CẦN NHIỀU KHUNG

Đo được trên 1h: stop đủ rộng để sống qua nhiễu và mục tiêu đủ gần để với tới
LOẠI TRỪ NHAU ở minRR 2,0. Đó có thể là sự thật về thị trường, hoặc chỉ là sự
thật về **khung 1h**. Phân biệt hai khả năng ấy chỉ có một cách: đo trên khung
khác. Bốn chiến lược đã dựng có thể đều đúng mà chỉ chạy nhầm khung.

VÌ SAO CẦN NHIỀU COIN

Mọi con số của hệ này tới giờ đứng trên MỘT tài sản. Một thị trường không phải
một mẫu — nó là một quan sát. Chiến lược ăn được ở BTC mà chết ở ETH và SOL thì
đó là chiến lược khớp với lịch sử BTC, không phải chiến lược có lợi thế.

SỐ NẾN TỰ CÂN THEO KHUNG — VÀ CHỖ NÓ CỐ Ý KHÔNG CÂN

Tải cùng một số nến cho mọi khung là sai: 3000 nến 5m phủ 10 ngày, 3000 nến 1d
phủ 8 năm. Nên số nến được suy từ khoảng thời gian muốn phủ.

Nhưng **phủ cùng khoảng thời gian cho mọi khung là bất khả**: 250 ngày trên 5m
là 72.000 nến, nặng đĩa và làm chậm mọi phép đo, mà nhiễu vi cấu trúc của 8
tháng trước cũng không còn giống bây giờ. Nên mỗi khung có SÀN và TRẦN riêng:

    5m   12.000 nến ≈  42 ngày     đủ để đo nhiễu, không cần dài hơn
    15m   8.000 nến ≈  83 ngày
    30m   6.000 nến ≈ 125 ngày
    1h    6.000 nến ≈ 250 ngày     khung đang chạy thật
    4h    3.000 nến ≈ 500 ngày
    1d    1.500 nến ≈ 4 năm        mỗi nến là một ngày thật, càng dài càng quý

Hệ quả phải nhớ khi đọc kết quả: **các khung KHÔNG phủ cùng một đoạn lịch sử.**
Khung 1d thấy cả chu kỳ 2022, khung 5m chỉ thấy sáu tuần gần nhất. So kỳ vọng
giữa hai khung là so hai chế độ thị trường khác nhau, không chỉ hai khung.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

from trader.config import CONFIG  # noqa: E402

KHO = GOC / "data" / "lich-su"
NGUON = ["https://data-api.binance.vision/api/v3/klines",
         "https://api.binance.com/api/v3/klines"]


def tai(client: httpx.Client, symbol: str, tf: str, so: int) -> list[dict]:
    ra: list[list] = []
    het = None
    while len(ra) < so:
        con = min(1000, so - len(ra))
        tham = {"symbol": symbol, "interval": tf, "limit": con}
        if het:
            tham["endTime"] = het
        lo = None
        for u in NGUON:
            try:
                r = client.get(u, params=tham, timeout=20)
                r.raise_for_status()
                lo = r.json()
                break
            except Exception as e:  # noqa: BLE001
                print(f"    {httpx.URL(u).host}: {type(e).__name__}")
        if not lo:
            break
        ra = lo + ra
        het = int(lo[0][0]) - 1
        print(f"    {tf}: {len(ra)}/{so} nến · tới {time.strftime('%Y-%m-%d', time.gmtime(int(lo[0][0]) / 1000))}")
        if len(lo) < con:
            break
        time.sleep(0.3)

    n = len(ra)
    return [{"t": int(x[0]), "o": float(x[1]), "h": float(x[2]), "l": float(x[3]),
             "c": float(x[4]), "v": float(x[5]), "closeTime": int(x[6]), "closed": i < n - 1}
            for i, x in enumerate(ra)]


# Số phút của mỗi khung — dùng để cân số nến cho cùng một khoảng thời gian.
PHUT = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120,
        "4h": 240, "6h": 360, "8h": 480, "12h": 720, "1d": 1440, "3d": 4320, "1w": 10080}

# SÀN và TRẦN theo từng khung. Không có SÀN thì khung dài (1d) chỉ nhận vài trăm
# nến khi `--so` nhỏ; không có TRẦN thì khung ngắn (5m) phình lên hàng trăm nghìn.
# Hai cái này là lý do các khung KHÔNG phủ cùng một đoạn lịch sử — cố ý, và phải
# nhớ khi đọc kết quả so sánh giữa các khung.
# 4h nâng 3000 → 9000 nến (500 ngày → 1499 ngày), để nó phủ ĐÚNG quãng của 1d.
#
# Trần cũ không sai về ý — nó giữ đĩa gọn — nhưng nó làm một phép so trở thành
# bất khả mà không ai thấy: cửa sổ ngoài mẫu của 4h là 150 ngày cuối còn của 1d
# là 450 ngày cuối, nên "4h −0,047R so với 1d +0,117R trên cùng 15 chợ" KHÔNG
# phải so cùng kỳ. Tôi đã dùng đúng câu đó làm đối chứng cho một giả thuyết.
#
# Không phải khung nào cũng phủ được cùng quãng — 5m trong 4 năm là 420.000
# nến. Nên bất biến KHÔNG phải "mọi khung cùng quãng" mà là: hai khung ĐANG
# ĐƯỢC ĐEM SO phải cùng quãng, và mọi bảng phải tự khai quãng của nó
# (`dau-nhieu-cho.json` → trường `quang`).
#
# Giá: 15 coin × 9000 nến 4h ≈ 20 MB. Đã đo, chấp nhận được.
#
# VIỆC ĐÁNG LÀM TIẾP, và vì sao nó CHƯA làm (30/08/2026)
#
# Đo được hôm nay: đổi CHỢ thì kết quả giữ nguyên, đổi CỬA SỔ THỜI GIAN thì nó
# đổi DẤU (MOCK_KEO_LUI_V1 +0,205R → −0,254R trên đúng 33 chợ ấy). Nghĩa là 48
# chợ không phải 48 quan sát độc lập — chúng chia chung một quãng thị trường.
#
# Suy ra: khoản đầu tư DỮ LIỆU đáng giá nhất không phải thêm coin, mà là thêm
# THỜI GIAN. `1d` đang lấy 1500 nến (từ 2022-07); trần đã là 2500, tức thêm
# được ~2,7 năm nữa, phủ cả đoạn gấu 2019–2022 mà hệ này chưa từng nhìn thấy.
#
# Chưa làm vì nó kéo theo hai thứ, và cả hai phải nhúc nhích CÙNG LÚC:
#
#   1. Bất biến ở trên: "hai khung ĐANG ĐƯỢC ĐEM SO phải cùng quãng". 1d lên
#      2500 ngày thì 4h phải lên 15000 nến, tức vượt TRẦN 12000 hiện tại.
#   2. Nâng 4h lên 15000 nến làm việc «đấu nhiều chợ 4h» đắt thêm ~65%, mà nó
#      ĐANG quá hạn 9000s với cache lạnh (đo được: 4 chuỗi trong 53 phút).
#
# Thứ tự đúng khi làm: chờ cache chuỗi 4h ấm (một lượt nghi thức chạy trọn), đo
# lại thời gian thật của việc ấy, RỒI mới nâng cả hai trần. Nâng 1d một mình là
# phá đúng cái bất biến mà đoạn chú thích này được viết ra để giữ.
SAN = {"5m": 12000, "15m": 8000, "30m": 6000, "1h": 2000, "4h": 9000, "1d": 1500}
TRAN = {"5m": 12000, "15m": 8000, "30m": 6000, "1h": 8000, "4h": 12000, "1d": 2500}


def _co(tf: str, so_1h: int, ep: bool = False) -> int:
    """Số nến cần tải cho khung `tf`, đã kẹp trong [SÀN, TRẦN] của chính nó.

    `ep=True` khi người gọi ghi rõ `--so`: khi ấy TRẦN chỉ còn là mặc định, không
    còn là luật. Bản trước kẹp im lặng — `--so 9000 --khung 4h` trả về đúng 3000
    nến và không một dòng nào nói ra, nên "4h chỉ có 500 ngày" trông như sự thật
    về sàn chứ không phải hệ quả của một hằng số trong file này.

    Chỗ đó đã tốn một lập luận sai: chuỗi 4h phủ 500 ngày còn 1d phủ 1500, nên
    cửa sổ ngoài mẫu của hai khung là hai quãng khác nhau (150 ngày cuối so với
    450 ngày cuối) — và tôi đã so kết quả hai khung như thể cùng kỳ.
    """
    p = PHUT.get(tf)
    if not p:
        return so_1h
    # `--so` đếm theo nến 1H, rồi quy đổi. `--so 9000 --khung 4h` nghĩa là 9000
    # GIỜ, tức 2250 nến 4h — không phải 9000 nến 4h. Bất ngờ, nên phải in ra.
    xin = int(so_1h * 60 / p)
    n = max(xin, SAN.get(tf, 400))
    tran = TRAN.get(tf, 20000)
    if ep:
        tran = max(tran, xin)
    ra = min(n, tran)
    # Nói ra MỌI lần con số bị đổi, cả khi SÀN nâng lên lẫn khi TRẦN cắt xuống.
    # Bản trước chỉ canh chiều cắt xuống, nên `--so 9000 --khung 4h` bị SÀN nâng
    # 2250 → 3000 và im lặng: xin nhiều hơn mà nhận ít hơn, không một dòng nào
    # nói ra. "4h chỉ có 500 ngày lịch sử" khi ấy trông như sự thật về sàn giao
    # dịch chứ không phải hệ quả của một hằng số trong chính file này.
    if ra != xin:
        vi = "SÀN nâng lên" if ra > xin else "TRẦN cắt xuống"
        print(f"    ⚠ {tf}: --so {so_1h} quy ra {xin} nến {tf}, {vi} {ra}. "
              f"(SÀN {SAN.get(tf)} · TRẦN {tran}) — muốn {tf} phủ dài hơn thì "
              f"tăng --so, nó đếm theo nến 1H.")
    return ra


def _dsach(co: str, mac_dinh: list[str]) -> list[str]:
    if co not in sys.argv:
        return mac_dinh
    return [x.strip() for x in sys.argv[sys.argv.index(co) + 1].split(",") if x.strip()]


def main() -> None:
    so = 3000
    ep_so = "--so" in sys.argv
    if ep_so:
        so = int(sys.argv[sys.argv.index("--so") + 1])
    coins = _dsach("--coin", [CONFIG["symbol"]])
    tfs = _dsach("--khung", [CONFIG["timeframes"]["primary"],
                             CONFIG["timeframes"]["context"]])

    KHO.mkdir(parents=True, exist_ok=True)
    hong = []
    with httpx.Client(follow_redirects=True) as c:
        for symbol in coins:
            for tf in tfs:
                n = _co(tf, so, ep_so)
                print(f"  {symbol} {tf} — cần {n} nến (≈{n * PHUT.get(tf, 60) / 1440:.0f} ngày)")
                nen = tai(c, symbol, tf, n)
                if not nen:
                    # Cặp không tồn tại trên sàn, hoặc mạng hỏng. Ghi lại và đi
                    # tiếp: một coin hỏng không được làm mất cả mẻ tải.
                    hong.append(f"{symbol} {tf}")
                    print(f"  → KHÔNG TẢI ĐƯỢC {symbol} {tf}\n")
                    continue
                f = KHO / f"{symbol}-{tf}.json"
                f.write_text(json.dumps(nen), encoding="utf-8")
                d0 = time.strftime("%Y-%m-%d", time.gmtime(nen[0]["t"] / 1000))
                d1 = time.strftime("%Y-%m-%d", time.gmtime(nen[-1]["t"] / 1000))
                print(f"  → {f.name}: {len(nen)} nến, {d0} … {d1}\n")
    if hong:
        print("KHÔNG TẢI ĐƯỢC: " + " · ".join(hong))


if __name__ == "__main__":
    main()
