"""Cấu hình của ty bể thanh khoản V3 — và danh mục POOL người vận hành theo.

Hai lớp:

    CONFIG          mặc định trong mã — núm, cửa, nhịp
    data/lp-v3/cau-hinh.json   ĐÈ lên, do người vận hành sửa: pool nào theo,
                    địa chỉ pool, ngày kết quả kinh doanh, giờ hết thưởng

Lớp thứ hai nằm trong `data/` (gitignore) vì nó là chuyện của MỘT người
với MỘT ví, không phải mã nguồn. Không có file ấy thì ty chạy với danh mục
mẫu dưới đây — chín pool đọc từ ảnh chụp OKX DeFi ngày 04/09/2026 — và
khai rõ mọi số trong đó là KHAI TAY, có ngày.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: Cùng biến môi trường với cả runtime (`TBT_DATA_DIR`), tự đọc chứ không
#: import `bac/` — ty không được gọi ty khác, kể cả để mượn một đường dẫn.
DATA_DIR = Path(os.environ.get("TBT_DATA_DIR") or (ROOT / "data"))
THU_MUC = DATA_DIR / "lp-v3"
DUONG_CAU_HINH = THU_MUC / "cau-hinh.json"

MA_CHIEN_LUOC = "amm.v3_range.v1"
HO = "thanh-khoan"

#: Núm vòng tiến hoá vặn được nằm trong `nut`; cửa an toàn nằm trong `cua`
#: và KHÔNG BAO GIỜ vào `tien_hoa.NUT_VAN`.
CONFIG = {
    "nhipGiay": 300.0,
    #: Cho vòng tiến hoá của ty tự ghi núm vào `cau-hinh.json` khi qua
    #: cổng. TẮT mặc định — cùng chính sách `bac.config.MAC_DINH`: máy mới
    #: dựng thì KHÔNG tự vặn tham số của chính mình.
    "tuVanTienHoa": False,
    "chuoi": "X Layer",
    "duAn": "uniswap-v3",
    "rpc": ["https://rpc.xlayer.tech", "https://xlayerrpc.okx.com"],
    "hetGioHoiGiay": 20.0,
    "nut": {
        #: bề rộng dải = heSoDai × σ√τ. 1,0 ≈ 68% ở trong dải tới cuối cửa sổ
        #: nếu đi thẳng; xác suất CHẠM thì cao hơn nhiều.
        "heSoDai": 1.5,
        #: cửa sổ giữ dự định, giờ LỊCH
        "giuGio": 72.0,
        #: (phí + thưởng) / LVR phải ≥ ngần này mới VÀO
        "tiLePhiTrenLvrToiThieu": 1.5,
        #: P(văng) trong cửa sổ trên ngần này thì NỚI dải, không vào dải hẹp
        "xacSuatVangToiDa": 0.60,
        #: không VÀO hay ĐỔI DẢI trong ngần này giờ trước sự kiện
        "gioTruocSuKien": 24.0,
    },
    "cua": {
        #: Không có σ thì không xét. Đây là cả lý do ty này tồn tại bên
        #: cạnh `lp_amm/` — bỏ cửa này là quay về đoán.
        "doiHoiSigma": True,
        "soPhienToiThieuChoSigma": 10,
        #: Không đổi dải khi sàn Mỹ đóng: giá chuỗi lúc ấy là giá trên
        #: thanh khoản mỏng, và cú bắt kịp lúc mở cửa là lúc arb ăn LP.
        "khongDoiDaiNgoaiGio": True,
        "tvlToiThieuUsd": 5_000.0,
        #: Rót quá phần này của TVL là TA thành pool; sức chứa tính từ đây.
        "phanTvlToiDa": 0.25,
        "vonToiThieuUsd": 200.0,
        #: 30 giờ: đủ để giá ĐÓNG CỬA hôm qua còn dùng được trong phiên hôm
        #: nay khi chưa có RPC (không có giá trong phiên từ nguồn miễn phí).
        #: Dải đặt quanh giá đóng cửa thì lúc vào PHẢI dịch theo giá đang
        #: hiện ở OKX — báo cáo nhắc câu ấy mỗi lần nguồn giá là `goc`.
        "tuoiGiaToiDaGiay": 30 * 3600.0,
    },
    "von": {"moiCoHoiUsd": 500.0, "phanSucChuaXin": 0.5,
            "tranMotLanUsd": 10_000.0},
    #: Hai giao dịch (mint + burn/collect) trên X Layer, gas rẻ. Khai tay
    #: kèm ngày; Router chưa biết X Layer nên chưa có gas SỐNG.
    "gasVaoRaUsd": {"gia": 0.10, "nguon": "ước lượng X Layer, 04/09/2026"},
    #: Phần thưởng chia theo phí, và OKX chỉ hiện APY TỔNG. Khi chưa có
    #: khối lượng để tách phí gốc, GIẢ ĐỊNH phần này của APY hiển thị là
    #: thưởng. Ghi rõ là giả định, và mọi câu in ra đều nhắc.
    "giaDinhPhanThuong": 0.90,
    #: OKX ghi «APY». Nếu là lãi KÉP thì phải đổi về APR đơn (ln(1+APY))
    #: trước khi nhân với thời gian — 423% APY ≈ 165% APR. Không biết chắc
    #: thì coi là kép: số NHỎ hơn, sai theo hướng thận trọng (Bài 4).
    "apyLaLaiKep": True,
    "chuongTrinh": {
        "ten": "$220K Rewards for X Layer Liquidity Providers",
        "quyUsd": 220_000.0,
        "batDau": "2026-08-24 14:00",
        "ketThuc": "2026-09-07 14:00",
        "luat": ("thưởng chia theo GIỜ theo tỉ lệ phí; đổi vị thế lúc chụp "
                 "ngẫu nhiên là mất thưởng giờ ấy; phải thêm thanh khoản "
                 "qua trang OKX, không qua Uniswap"),
        "nguon": "ảnh chụp OKX DeFi 04/09/2026",
    },
    "ketQuaKinhDoanh": {},
    #: VÍ của người vận hành — CHỈ địa chỉ công khai, chỉ để ĐỌC. Không có
    #: chỗ nào trong ty này nhận khoá riêng, và không được thêm vào.
    #:
    #:   diaChi        0x… ví X Layer đang giữ NFT vị thế
    #:   quanLyViThe   NonfungiblePositionManager trên X Layer — KHÔNG đoán
    #:                 (canonical 0xC364…FE88 không có mã ở chainId 196);
    #:                 để None thì suy từ `txMau`
    #:   txMau         hash một giao dịch THÊM thanh khoản của bạn — log
    #:                 IncreaseLiquidity trong biên nhận chỉ ra hợp đồng
    "vi": {"diaChi": None, "quanLyViThe": None, "txMau": None},
    #: HỒ SƠ MỤC TIÊU của người vận hành (Bài 1: kiểm toán trước khi phân
    #: bổ; Bài 2: điểm tự do = dòng tiền ròng / chi phí). Không khai thì
    #: điểm tự do là None — không phải 0.
    "mucTieu": {
        "chiPhiThangUsd": None,          # chi phí sống mỗi tháng, USD
        "taiSanUuTien": [],              # VD ["BTC", "ETH", "USDG"] — pool ngoài danh sách bị hạ điểm phù hợp
        "sutVonChiuDuocPct": None,       # sụt vốn tối đa chịu được, %
        "khongDonBay": True,
    },
    #: Uniswap V3 CHÍNH THỨC trên X Layer (chainId 196), theo
    #: developers.uniswap.org/docs/protocols/v3/deployments/v3-xlayer-deployments,
    #: đọc 05/09/2026 và đã xác minh có mã trên rpc.xlayer.tech. Dùng khi
    #: người chưa khai `quanLyViThe` lẫn `txMau`; nếu OKX DeFi mint qua một
    #: hợp đồng KHÁC thì ví sẽ đọc ra 0 vị thế — lúc ấy dán `txMau`.
    "uniswapXLayer": {
        "quanLyViThe": "0x315e413A11AB0df498eF83873012430ca36638Ae",
        "nhaMay": "0x4B2ab38DBF28D31D467aA8993f6c2585981D6804",
        "nguon": "developers.uniswap.org · v3-xlayer-deployments · 05/09/2026",
    },
    #: Ký hiệu Yahoo của cổ phiếu gốc. `None` = không có sàn gốc công khai
    #: (SpaceX chưa niêm yết) → σ chỉ tích được từ băng giá chuỗi.
    "coPhieuGoc": {
        "SPCXx": None, "NVDAx": "NVDA", "SPYx": "SPY",
        "ICEx": "ICE", "MRNAx": "MRNA", "SMCIx": "SMCI",
        "RDDTx": "RDDT", "IRENx": "IREN", "CRWVx": "CRWV",
    },
    "pool": [
        # kyHieu · phí bps · TVL · APY hiển thị · khối lượng ngày (None = chưa
        # đọc) · địa chỉ pool (None = chưa dán) — TẤT CẢ khai tay 04/09/2026.
        {"kyHieu": "SPCXx-USDG", "phiBps": 5, "tvlUsd": 381_440.0,
         "apyHienThiPhanTram": 268.91, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "NVDAx-USDG", "phiBps": 5, "tvlUsd": 644_990.0,
         "apyHienThiPhanTram": 183.94, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "SPYx-USDG", "phiBps": 5, "tvlUsd": 637_990.0,
         "apyHienThiPhanTram": 48.55, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "ICEx-USDG", "phiBps": 5, "tvlUsd": 31_670.0,
         "apyHienThiPhanTram": 423.08, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "MRNAx-USDG", "phiBps": 5, "tvlUsd": 35_490.0,
         "apyHienThiPhanTram": 406.04, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "SMCIx-USDG", "phiBps": 5, "tvlUsd": 14_810.0,
         "apyHienThiPhanTram": 386.14, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "RDDTx-USDG", "phiBps": 5, "tvlUsd": 16_730.0,
         "apyHienThiPhanTram": 335.27, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "IRENx-USDG", "phiBps": 5, "tvlUsd": 18_200.0,
         "apyHienThiPhanTram": 319.67, "khoiLuongNgayUsd": None, "diaChi": None},
        {"kyHieu": "CRWVx-USDG", "phiBps": 5, "tvlUsd": 19_900.0,
         "apyHienThiPhanTram": 302.42, "khoiLuongNgayUsd": None, "diaChi": None},
    ],
    "poolKhaiLuc": "2026-09-04",
    "tin": {
        "rss": ["https://feeds.finance.yahoo.com/rss/2.0/headline?s={ma}&region=US&lang=en-US"],
        "giuNgay": 14,
    },
}

#: Cửa an toàn — liệt kê tường minh để phép kiểm bắt được nếu ai đưa một
#: trong số chúng vào `NUT_VAN`.
CUA_AN_TOAN = ("doiHoiSigma", "soPhienToiThieuChoSigma", "khongDoiDaiNgoaiGio",
               "tvlToiThieuUsd", "phanTvlToiDa", "vonToiThieuUsd",
               "tuoiGiaToiDaGiay")


def _tron(goc: dict, de: dict) -> dict:
    ra = copy.deepcopy(goc)
    for k, v in (de or {}).items():
        if isinstance(v, dict) and isinstance(ra.get(k), dict):
            ra[k] = _tron(ra[k], v)
        else:
            ra[k] = copy.deepcopy(v)
    return ra


def nap(duong: Path | None = None) -> dict:
    """CONFIG đè bởi `cau-hinh.json` nếu có. Hỏng cú pháp thì KÊU, không
    im lặng dùng mặc định — người vừa sửa file ấy phải biết nó không ăn."""
    p = duong or DUONG_CAU_HINH
    if not p.exists():
        return copy.deepcopy(CONFIG)
    de = json.loads(p.read_text(encoding="utf-8"))
    return _tron(CONFIG, de)


def ghi(cauHinh: dict, duong: Path | None = None) -> Path:
    p = duong or DUONG_CAU_HINH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cauHinh, ensure_ascii=False, indent=2),
                 encoding="utf-8")
    return p


def ma_goc(kyHieu: str) -> str:
    """`NVDAx-USDG` → `NVDAx`."""
    return str(kyHieu).split("-")[0].strip()
