"""Cấu hình ty TÍN DỤNG. Đọc từ `tin-dung.json` nếu có, gộp lên mặc định."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: `<họ>.<tên>.v<số>` — một nguồn duy nhất, như `bac.config.MA_CHIEN_LUOC`.
#: Chép chuỗi này ra chỗ thứ hai là mở đường cho `lending.` và `lend.` cùng
#: tồn tại, và ba tháng sau thống kê gộp nhầm hai ty thành một.
MA_CHIEN_LUOC = "lending.rate_rotation.v1"
HO = "tin-dung"

MAC_DINH = {
    # ── quét ─────────────────────────────────────────────────────────────
    "quet": {
        # CHỈ stablecoin ở bản này. Cho vay ETH thì phơi nhiễm giá ETH là
        # RỦI RO CHÍNH, không phải lãi suất — và một ty tên "chênh lệch lãi
        # suất" mà thu nhập chủ yếu đến từ hướng giá là một ty nói dối tên
        # của chính nó.
        "taiSan": ["USDC", "USDT", "DAI", "USDS", "USDE"],
        # Không bắc cầu ở bản này, nên chỉ nhận chuỗi ta coi là đã có vốn.
        # Thêm chuỗi mới mà chưa có đường chuyển vốn tới đó là dựng ra
        # những cơ hội KHÔNG vào được.
        "chuoi": ["Ethereum", "Arbitrum", "Base", "Optimism", "Polygon"],
        # Cửa sổ giữ giả định. Lãi cho vay chảy liên tục, nên "giữ bao lâu"
        # là một LỰA CHỌN, không phải sự thật của thị trường — và nó quyết
        # định gas phân bổ trên bao nhiêu giờ. 30 ngày.
        "giuGio": 720.0,
        "hetGioHoiGiay": 30.0,
    },

    # ── cửa rủi ro CHUYÊN MÔN của ty này (tầng 1) ────────────────────────
    "ruiRo": {
        "tvlToiThieuUsd": 5_000_000.0,
        # Dùng vốn cao thì rút không ra. 0,92 nghĩa là chỉ còn 8% thanh
        # khoản rảnh — và 8% ấy là thứ mọi người cùng chạy tới khi có biến.
        "suDungToiDa": 0.92,
        "thanhKhoanThoatToiThieuUsd": 250_000.0,
        # Lãi chủ yếu đến từ token thưởng là lãi sẽ bốc hơi. Ta chỉ tính
        # `apyBase`, nhưng tỉ lệ thưởng cao vẫn là tín hiệu thị trường ấy
        # đang mua thanh khoản chứ không phải đang trả lãi thật.
        "tyLeThuongToiDa": 0.60,
        "netToiThieuBps": 5.0,
        # APY cao bất thường trên một stablecoin KHÔNG phải cơ hội, nó là
        # dấu hiệu có gì đó sai: thị trường sắp mất thanh khoản, hoặc đang
        # trả để giữ chân người rút.
        "apyToiDaPhanTram": 40.0,
        "tuoiToiDaGiay": 900.0,
    },

    # ── mô hình phí ──────────────────────────────────────────────────────
    # Gas vào + gas ra, ước theo chuỗi. Đây là ƯỚC LƯỢNG THÔ và mọi tờ
    # trình khai điều đó — gas thật đổi theo tắc nghẽn, và không có oracle
    # gas nào trong runtime này.
    "gasUsd": {
        "Ethereum": 6.0, "Arbitrum": 0.15, "Base": 0.05,
        "Optimism": 0.05, "Polygon": 0.02, "_khac": 1.0,
    },

    "von": {
        "moiCoHoiUsd": 200.0,
    },
    # Rót được bao nhiêu mà không dìm chính lãi suất mình vừa thấy. Chưa có
    # đường cong lãi suất nên đây là proxy thô trên thanh khoản rảnh, và
    # `moHinhSucChuaDuChua=False` khai đúng điều đó.
    "sucChua": {
        "phanThanhKhoanRanh": 0.02,
        "tranUsd": 50_000.0,
    },
}


def _gop(a: dict, b: dict) -> dict:
    ra = dict(a)
    for k, v in (b or {}).items():
        ra[k] = _gop(a[k], v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return ra


def _nap() -> dict:
    p = ROOT / "tin-dung.json"
    if not p.exists():
        return dict(MAC_DINH)
    try:
        return _gop(MAC_DINH, json.loads(p.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError):
        return dict(MAC_DINH)


CONFIG = _nap()
