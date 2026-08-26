"""Cấu hình ty CHÊNH LỆCH — nhánh stablecoin. Họ thứ BA của Thị Bạc Ty."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MA_CHIEN_LUOC = "stablecoin.cross_venue.v1"
HO = "chenh-lech"

MAC_DINH = {
    "quet": {
        # Cặp stablecoin có mặt ở cả ba sàn dưới dạng giao ngay.
        "cap": ["USDC/USDT"],
        "san": ["binance", "okx", "bybit"],
        "hetGioHoiGiay": 12.0,

        # ── CHU KỲ VỐN, không phải thời gian giao dịch ────────────────────
        #
        # Một lệnh mua-bán chéo sàn xong trong vài giây. Nếu khai `giuGio`
        # bằng vài giây thì NET mỗi giờ nhảy lên hàng nghìn bps, và ty này
        # chiếm sạch bảng xếp hạng của mọi ty khác.
        #
        # Con số ấy sẽ là dối. Sau một lượt, tồn kho lệch: sàn rẻ hết USDT,
        # sàn đắt đầy USDC. Muốn làm lượt nữa phải hoặc CHỜ chênh lệch đảo
        # chiều, hoặc CHUYỂN VỐN giữa hai sàn — mà chuyển vốn thì tốn phí,
        # tốn thời gian, và runtime này chưa làm được.
        #
        # Nên `giuGio` ở đây là "bao lâu thì đồng vốn ấy sẵn sàng cho lượt
        # sau", không phải "lệnh chạy mất bao lâu". Khai thấp là tự cho mình
        # điểm cao ở một thước mình không đạt được.
        "chuKyVonGio": 24.0,
    },

    "ruiRo": {
        # ── $0,97 KHÔNG phải arbitrage. Nó có thể là DEPEG. ──────────────
        # Cửa này là cửa quan trọng nhất của ty. Chênh lệch càng lớn thì
        # càng có khả năng nó không phải sai giá tạm thời mà là thị trường
        # đang định giá lại rủi ro của chính đồng tiền ấy — và bên đứng ra
        # "arbitrage" sẽ là bên ôm đồng đang chết.
        "lechNeoToiDaBps": 60.0,
        "chenhThoToiThieuBps": 1.0,
        "netToiThieuBps": 0.5,
        # Sổ lệnh mỏng thì con số chênh lệch trên đỉnh sổ là ảo.
        "sauSoLenhToiThieuUsd": 20_000.0,
        "tuoiToiDaGiay": 20.0,
        # Hai sàn cùng một chênh lệch nhưng một bên không giao dịch được thì
        # không phải cơ hội — cần cả hai chân cùng sống.
        "doiHoiHaiSanSong": True,
    },

    # Phí taker giao ngay, bps mỗi chiều. Cặp stablecoin ở nhiều sàn được
    # miễn phí, nhưng KHÔNG mặc định là 0: giả định miễn phí mà thật ra
    # không phải là cách biến một cơ hội âm thành một cơ hội dương trên
    # giấy.
    "phiTakerBps": {"binance": 1.0, "okx": 8.0, "bybit": 10.0, "_khac": 10.0},

    "von": {"moiCoHoiUsd": 200.0},
    # Rót được bao nhiêu: lấy phần đỉnh sổ lệnh, vì sâu hơn đỉnh thì ta
    # không nhìn thấy. Đây là chặn dưới, và tờ trình khai rõ điều đó.
    "sucChua": {"phanDinhSo": 0.30, "tranUsd": 25_000.0},
}


def _gop(a: dict, b: dict) -> dict:
    ra = dict(a)
    for k, v in (b or {}).items():
        ra[k] = _gop(a[k], v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return ra


def _nap() -> dict:
    p = ROOT / "on-dinh.json"
    if not p.exists():
        return dict(MAC_DINH)
    try:
        return _gop(MAC_DINH, json.loads(p.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError):
        return dict(MAC_DINH)


CONFIG = _nap()
