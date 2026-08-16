"""CHẾ ĐỘ THỊ TRƯỜNG CHO MỌI COIN, tra được theo thời điểm.

Đây là mảnh còn thiếu để trả lời câu hỏi quan trọng nhất của Đài quan sát:
**lúc trader đó bấm nút, thị trường đang ở trạng thái nào?**

Không có nó thì mọi thứ khác chỉ là thống kê rời rạc — "giữ 4 giờ", "thắng 52%"
— mà không biết họ giỏi ở đâu và mù ở đâu. Có nó thì phong cách, kiểu cắt lỗ,
ma trận thoát lệnh đều tính ra được.

## Vì sao tính sẵn cả chuỗi thay vì tính từng điểm

Một trader có tới 2000 lệnh khớp. Tính chế độ tại từng thời điểm nghĩa là dựng
lại chỉ báo trên cửa sổ 400 nến, 2000 lần, cho mỗi trader. Thay vào đó: mỗi coin
tính MỘT LẦN cho toàn bộ lịch sử, rồi tra theo mốc thời gian bằng nhị phân. Đúng
mẹo mà `huanluyen.py` dùng, vì cùng một lý do.

## Nguồn nến

`candleSnapshot` của chính Hyperliquid — cùng sàn với `userFills`, nên giá và
mốc thời gian khớp nhau. Lấy từ Binance thì BTC còn khớp, chứ tới alt hay cổ
phiếu `xyz:AAPL` là lệch sàn, lệch giờ, và lệch cả giá.
"""
from __future__ import annotations

import bisect
import time
from typing import Any

import httpx

from .bus import bus
from .config import DATA_DIR
from .features import features_for
from .regime import classify

HL_INFO = "https://api.hyperliquid.xyz/info"
UA = {"User-Agent": "Mozilla/5.0 (compatible; tu-cam-thanh/0.1)"}

TF_CHINH, TF_NGU_CANH = "1h", "4h"
CUA_SO = 400          # bằng candleLimit của bản chạy thật
KHOI_DONG = 210

# Tính chế độ mỗi BUOC nến thay vì từng nến.
#
# Đo được: cửa sổ 120 ngày ⇒ ~2.500 lát × 4 coin × 12 phép chỉ báo, và một hồ sơ
# mất hơn 5 phút. Chế độ thị trường là nhãn CHẬM — nó không đổi theo từng giờ,
# nên lấy độ phân giải 3 giờ là đủ để trả lời "lúc họ bấm nút thì thị trường
# đang thế nào". Nhanh gấp ba, và sai số là tra được nhãn của nến gần đó thay
# vì nến liền trước.
#
# Đây là đánh đổi có ý thức, không phải tiện tay: ghi ở đây để ai đọc kết quả
# biết độ phân giải thật của nó.
BUOC = 3

_kho: dict[str, dict] = {}     # coin → {"moc": [...], "cheDo": [...]}
_nen_cache: dict[str, list] = {}


# Nhịp tối thiểu giữa hai lời gọi nến, và số lần thử lại khi bị chặn nhịp.
#
# Hyperliquid trả 429 khi hỏi quá dày, và một trader có thể cần 24 coin. Trước
# khi có chốt này, lỗi 429 rơi vào khối `except` bao ngoài và biến thành
# `soVong: 0` — nên hồ sơ ghi "trader không đóng lệnh bao giờ" trong khi sự thật
# là **mình gõ cửa quá nhanh**. Tôi đã suýt đi sửa hàm ghép vòng vì tin con số
# đó. Đây là API công khai miễn phí của người ta; chờ 0,25 giây là phép lịch sự
# tối thiểu, và cũng là thứ giữ cho dữ liệu đúng.
NHIP_GIAY = 0.25
THU_LAI = 4
_lan_goi_cuoi = 0.0


def _nen(client: httpx.Client, coin: str, interval: str, ngay: int) -> list[dict]:
    global _lan_goi_cuoi

    khoa = f"{coin}|{interval}|{ngay}"
    if khoa in _nen_cache:
        return _nen_cache[khoa]
    now = int(time.time() * 1000)

    r = None
    for lan in range(THU_LAI):
        cho = NHIP_GIAY - (time.time() - _lan_goi_cuoi)
        if cho > 0:
            time.sleep(cho)
        _lan_goi_cuoi = time.time()
        r = client.post(HL_INFO, headers=UA, timeout=60, json={
            "type": "candleSnapshot",
            "req": {"coin": coin, "interval": interval,
                    "startTime": now - ngay * 86_400_000, "endTime": now},
        })
        if r.status_code != 429:
            break
        # Bị chặn nhịp thì lùi dần: 1s, 2s, 4s. Thử lại ngay lập tức chỉ làm
        # mình bị chặn lâu hơn.
        time.sleep(2 ** lan)
    assert r is not None
    r.raise_for_status()
    ra = [{"t": int(x["t"]), "o": float(x["o"]), "h": float(x["h"]),
           "l": float(x["l"]), "c": float(x["c"]), "v": float(x["v"]),
           "closeTime": int(x["T"]), "closed": True}
          for x in (r.json() or [])]
    _nen_cache[khoa] = ra
    return ra


def dung_chuoi(client: httpx.Client, coin: str, ngay: int = 30) -> dict | None:
    """Tính chế độ thị trường cho MỌI nến của một coin, một lần.

    Trả None nếu không đủ nến — và None là câu trả lời trung thực, không phải
    lỗi: coin mới niêm yết thì đúng là chưa có lịch sử để nói gì.

    `ngay=30` là đánh đổi có chủ ý. Để 90 ngày thì mỗi coin phải tính chỉ báo
    trên ~1.950 lát cửa sổ 400 nến, mất ~2 phút mỗi trader và cả phễu thành gần
    nửa tiếng. Với 30 ngày còn ~510 lát, nhanh gấp bốn. Cái mất: lệnh cũ hơn 30
    ngày không tra được chế độ — chúng bị loại khỏi phần giải phẫu và `soCoCheDo`
    nói rõ còn lại bao nhiêu, chứ không bị âm thầm gán bừa một chế độ.
    """
    # Cache theo coin, NHƯNG nhớ cửa sổ đã dựng: trader sau cần xa hơn thì phải
    # dựng lại, không được trả bản ngắn. Không có chốt này thì trader đầu tiên
    # quyết định độ phủ cho tất cả những người sau — và họ ra "0 vòng có chế độ"
    # mà nhìn vào tưởng là dữ liệu của họ có vấn đề.
    cu = _kho.get(coin)
    if cu is not None and cu.get("ngay", 0) >= ngay:
        return cu
    if cu is None and coin in _kho and ngay <= _kho.get(f"{coin}#thu", 0):
        return None      # đã thử với cửa sổ này hoặc dài hơn mà không đủ nến
    try:
        nc = _nen(client, coin, TF_CHINH, ngay)
        nx = _nen(client, coin, TF_NGU_CANH, ngay * 2)
    except Exception as e:  # noqa: BLE001
        bus.log("hoc", "nen-coin-loi", f"{coin}: {type(e).__name__}")
        _kho[coin] = None  # type: ignore[assignment]
        _kho[f"{coin}#thu"] = ngay  # type: ignore[assignment]
        return None
    if len(nc) < KHOI_DONG + 5 or len(nx) < 60:
        _kho[coin] = None  # type: ignore[assignment]
        _kho[f"{coin}#thu"] = ngay  # type: ignore[assignment]
        return None

    moc_x = [x["t"] for x in nx]
    moc: list[int] = []
    che_do: list[dict] = []
    for i in range(KHOI_DONG, len(nc), BUOC):
        lat = nc[max(0, i + 1 - CUA_SO): i + 1]
        j = bisect.bisect_right(moc_x, lat[-1]["t"])
        lat_x = nx[max(0, j - CUA_SO): j]
        if len(lat_x) < 60:
            continue
        st = {"symbol": coin, "price": lat[-1]["c"], "source": {"name": "hl", "live": False},
              "timeframes": {TF_CHINH: features_for(lat), TF_NGU_CANH: features_for(lat_x)}}
        rg = classify(st, TF_CHINH, TF_NGU_CANH)
        p = st["timeframes"][TF_CHINH]
        moc.append(nc[i]["closeTime"])
        che_do.append({
            "cheDo": rg["primary"], "co": rg["flags"], "chatLuong": rg["quality"],
            "adx": p.get("adx"), "rsi": p.get("rsi14"), "atr": p["_raw"]["atr"],
            "gia": p["price"], "viTriDai": p.get("bbPosition"),
            "dayBien": p.get("range20Low"), "dinhBien": p.get("range20High"),
        })
    _kho[coin] = {"moc": moc, "cheDo": che_do, "coin": coin, "ngay": ngay}
    return _kho[coin]


def che_do_tai(client: httpx.Client, coin: str, moc_can: list[int],
               ngay: int = 150) -> int:
    """Tính chế độ CHỈ TẠI những mốc cần, thay vì dựng cả chuỗi.

    Đây là bản sửa một sai lầm thiết kế của chính tôi. `dung_chuoi()` tính chế
    độ cho MỌI nến trong cửa sổ — hợp lý khi cần tra 2000 lần, và tôi đã cho là
    vậy vì `userFills` trả 2000 dòng. Nhưng sau khi `_ghep()` dồn dòng khớp
    thành vòng, một trader chỉ còn vài chục vòng, mỗi vòng cần đúng 2 mốc.

    Đo được: một trader 48 vòng ⇒ cần 96 điểm, mà `dung_chuoi` tính ~14.400
    điểm cho 12 coin × cửa sổ 150 ngày. Gấp 150 lần công việc, và nó biến một
    phép đo vài giây thành một phễu chạy hàng chục phút.

    Cách này còn gỡ luôn thế lưỡng nan cửa sổ: chi phí tỉ lệ với SỐ VÒNG chứ
    không với ĐỘ DÀI cửa sổ, nên kéo cửa sổ ra 150 ngày gần như miễn phí.
    """
    if not moc_can:
        return 0
    kho = _kho.setdefault(f"{coin}#diem", {})   # type: ignore[assignment]
    try:
        nc = _nen(client, coin, TF_CHINH, ngay)
        nx = _nen(client, coin, TF_NGU_CANH, ngay * 2)
    except Exception as e:  # noqa: BLE001
        bus.log("hoc", "nen-coin-loi", f"{coin}: {type(e).__name__}")
        return 0
    if len(nc) < KHOI_DONG + 5 or len(nx) < 60:
        return 0

    moc_c = [x["closeTime"] for x in nc]
    moc_x = [x["t"] for x in nx]
    xong = 0
    for t in moc_can:
        if t in kho:
            xong += 1
            continue
        # nến ĐÃ ĐÓNG gần nhất trước t — không nhìn trộm nến đang chạy
        i = bisect.bisect_left(moc_c, t) - 1
        if i < KHOI_DONG:
            continue
        lat = nc[max(0, i + 1 - CUA_SO): i + 1]
        j = bisect.bisect_right(moc_x, lat[-1]["t"])
        lat_x = nx[max(0, j - CUA_SO): j]
        if len(lat_x) < 60:
            continue
        st = {"symbol": coin, "price": lat[-1]["c"], "source": {"name": "hl", "live": False},
              "timeframes": {TF_CHINH: features_for(lat), TF_NGU_CANH: features_for(lat_x)}}
        rg = classify(st, TF_CHINH, TF_NGU_CANH)
        p = st["timeframes"][TF_CHINH]
        kho[t] = {
            "cheDo": rg["primary"], "co": rg["flags"], "chatLuong": rg["quality"],
            "adx": p.get("adx"), "rsi": p.get("rsi14"), "atr": p["_raw"]["atr"],
            "gia": p["price"], "viTriDai": p.get("bbPosition"),
            "dayBien": p.get("range20Low"), "dinhBien": p.get("range20High"),
        }
        xong += 1
    return xong


def che_do_diem(coin: str, t: int) -> dict | None:
    """Tra chế độ đã tính bằng `che_do_tai`. Khớp CHÍNH XÁC mốc."""
    return (_kho.get(f"{coin}#diem") or {}).get(t)


def che_do_luc(coin: str, t: int) -> dict | None:
    """Chế độ thị trường của `coin` tại thời điểm `t` (ms).

    Tra nến ĐÃ ĐÓNG gần nhất TRƯỚC `t`. Lấy nến chứa `t` là nhìn trộm: người
    trade lúc 12:43 không biết nến 12:00–13:00 sẽ đóng ở đâu.
    """
    # Ưu tiên điểm đã tính đúng mốc (`che_do_tai`), rồi mới tới chuỗi dựng sẵn.
    diem = che_do_diem(coin, t)
    if diem is not None:
        return diem
    k = _kho.get(coin)
    if not k or not isinstance(k, dict) or "moc" not in k:
        return None
    i = bisect.bisect_left(k["moc"], t) - 1
    if i < 0:
        return None
    return k["cheDo"][i]


def coin_da_dung() -> list[str]:
    return [c for c, v in _kho.items() if v and isinstance(v, dict)]


def don() -> None:
    _kho.clear()
    _nen_cache.clear()
