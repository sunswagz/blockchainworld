"""Cấu hình, đường dẫn, và BA CỬA của chế độ chạy.

Một chỗ duy nhất đọc `config.json` và `.env`, để không phiên nào phải đoán giá
trị đang có hiệu lực là gì.

## Ba cửa, ba nơi khác nhau về bản chất

Một lệnh THẬT chỉ rời khỏi máy khi cả ba cùng mở:

    1. `config.json` → `che: "that"`
    2. `config.json` → `datLenh.toiXacNhanDaDocRuiRo: true`
    3. `.env`        → khoá API của ít nhất một sàn

Ba nơi khác nhau là chủ ý. Một dòng cấu hình duy nhất ngăn giữa mô phỏng và
tiền thật là quá mỏng: sửa nhầm một ký tự, hoặc `git checkout` một file, là
tiền thật bắt đầu chạy mà không ai kịp nhận ra.

Thiếu bất kỳ cửa nào thì **rơi về sổ giấy**, và `ly_do_khong_that()` in ra
đúng cửa nào đang đóng — không rơi trong im lặng.

Riêng bản v0.1 còn thêm một khoá cứng nữa: lớp đặt lệnh CHƯA TỒN TẠI. Ba cửa
mở hết thì runtime vẫn từ chối chạy và nói thẳng còn thiếu gì. Xem `README.md`
mục "Lộ trình" — cửa thứ tư mở ở V0.6, sau khi có máy trạng thái hai chân và
đối soát vị thế.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `TBT_DATA_DIR` tách sổ sách của phép kiểm khỏi sổ sách thật. Không có nó thì
# mọi phép kiểm chạm tới sổ đều ghi vào sổ THẬT, và bảng điều khiển khoe những
# giao dịch chưa từng xảy ra — bài học đã phải trả giá ở tu-cam-thanh-runtime.
DATA_DIR = Path(os.environ.get("TBT_DATA_DIR") or (ROOT / "data"))
WEB_DIR = ROOT / "web"

MAC_DINH = {
    "port": 5188,
    "nhipGiay": 30,
    "che": "quan-sat",
    "cungTinh": "",
    "quet": {
        "ma": ["BTC", "ETH", "SOL", "XRP", "DOGE"],
        "giuGio": 8.0,
        "hetGioHoiGiay": 10.0,
    },
    "san": {
        "hyperliquid": {"bat": True, "phiTakerBps": 4.5, "truotGiaBps": 2.0},
        "binance": {"bat": True, "phiTakerBps": 5.0, "truotGiaBps": 2.0},
        "okx": {"bat": True, "phiTakerBps": 5.0, "truotGiaBps": 2.0},
        "bybit": {"bat": True, "phiTakerBps": 5.5, "truotGiaBps": 2.0},
    },
    "ruiRo": {
        "grossToiThieuBpsNgay": 3.0,
        "netToiThieuBps": 0.5,
        "lechMarkToiDaBps": 40.0,
        "doiHoiHaiMark": True,
        "tuoiToiDaGiay": 90.0,
        "nhanUocLuongMoc": False,
        "doiHoiItNhatMotMoc": True,
        "lechDongHoToiDaGiay": 10.0,
    },
    # Vốn — và từ TBTC-002 khối này **đổi nghĩa**, không chỉ đổi chỗ.
    #
    # Cũ:  "trần ty tự áp cho mình"
    # Nay: "số ty XIN trung ương"
    #
    # Luật của Thị Bạc Ty: không ty nào được tự quyết danh mục. Ty chỉ phát
    # hiện → đánh giá → XIN. Quyền duyệt và chia nằm ở Rủi Ro Tổng và Người
    # Phân Bổ Vốn. Nếu mỗi ty tự giữ trần của mình thì mười ba ty là mười ba
    # đứa đều tưởng tiền trong ví là của mình, và không đứa nào thấy tổng.
    #
    # `coHieuLuc` vẫn False vì chưa có lớp đặt lệnh — không có vị thế nào để
    # mà giới hạn, kể cả trên sổ giấy.
    #
    # Ba con số này từng nằm trong khối `ruiRo`, nên buồng lái bày chúng dưới
    # nhãn "Cửa rủi ro đang có hiệu lực" — trong khi không dòng nào trong
    # `rui_ro.xet()` đọc tới. Ba cái cửa không chặn gì cả, hiện ra như đang
    # chặn. Đúng lớp hỏng im lặng mà cả cung này tồn tại để bắt.
    #
    # Chúng chỉ có nghĩa khi lớp đặt lệnh tồn tại (V0.6): trước đó không có
    # vị thế nào để mà giới hạn, kể cả trên sổ giấy. Giữ lại vì đó là quyết
    # định đã cân nhắc, không phải số bịa — nhưng giữ ở CHỖ KHÁC, kèm cờ.
    "von": {
        "coHieuLuc": False,
        # số XIN cho mỗi cơ hội, không phải trần
        "moiCoHoiUsd": 100.0,
        "toiDaUsd": 300.0,
        "donBayToiDa": 1.0,
    },
    "datLenh": {
        "toiXacNhanDaDocRuiRo": False,
    },
    # Trung Ương — bộ máy Thị Bạc Ty đứng TRÊN ty này. Khối này chỉ ghi đè;
    # giá trị đầy đủ nằm ở `thi_bac_ty/trung_uong.py:MAC_DINH` và ở MAC_DINH
    # của từng tầng. Chép lại đủ bộ ở đây là tạo bản sao thứ hai sẽ lệch.
    #
    # `vonBanDauUsd` là vốn TRÊN SỔ GIẤY. Không lớp đặt lệnh nào tồn tại nên
    # không con số nào ở đây chạm tới tiền thật; `DanhMuc.nguonThat` là False
    # và buồng lái bày cờ đó lên đầu bảng.
    "trungUong": {
        "bat": True,
        # Ty tín dụng — engine THỨ HAI. Cấu hình riêng của nó ở
        # `tin_dung/config.py`; ở đây chỉ có cái công tắc, vì Trung Ương là
        # chỗ duy nhất biết ty nào đang đăng ký.
        #
        # Nhịp riêng: lãi cho vay đổi theo giờ chứ không theo giây, mà quét
        # nó là kéo về hai bảng ~17.000 dòng. Quét mỗi 30 giây là đốt băng
        # thông cho một con số gần như đứng yên.
        "tyTinDung": {"bat": True, "nhipGiay": 900.0},
        # Ty chênh lệch stablecoin — HỌ THỨ BA. Nhịp nhanh hơn hai ty kia
        # vì sổ lệnh giao ngay đổi theo giây, nhưng vẫn thưa hơn nhịp perp:
        # chênh lệch stablecoin tồn tại hàng phút chứ không hàng giây, và
        # cơ hội bắt được sẽ kẹt tồn kho hàng giờ.
        "tyOnDinh": {"bat": True, "nhipGiay": 120.0},
        # Ty lãi suất Pendle PT. Lãi CỐ ĐỊNH và ngày đáo hạn cố định, nên
        # con số gần như đứng yên — hỏi mỗi giờ là quá đủ.
        "tyLaiSuat": {"bat": True, "nhipGiay": 3600.0},
        # Ty cơ sở (cash-and-carry). Nó ĐỌC LẠI báo giá perp của lượt
        # quét này chứ không tự hỏi, nên nhịp phải bằng hoặc thưa hơn
        # nhịp chung — thưa hơn thì nó dùng báo giá cũ, và cửa
        # `tuoiToiDaGiay` của chính nó sẽ chặn.
        "tyCoSo": {"bat": True, "nhipGiay": 60.0},
        # Adapter Khâm Thiên Giám — bước 2 của món nợ hai cỗ máy.
        # Nhịp thưa vì nó chỉ đọc lát cắt của một tiến trình khác;
        # hỏi dồn dập không làm lát cắt ấy mới hơn.
        "tyTienDoan": {"bat": True, "nhipGiay": 90.0},
        # Ty ngang giá quyền chọn. Nhịp thưa vì nó kéo về ~2.000 dòng
        # mỗi lượt cho hai tiền tệ, và ngang giá không đảo theo giây.
        "tyNgangGia": {"bat": True, "nhipGiay": 300.0},

        # ── VỐN NGOÀI ────────────────────────────────────────────────────
        # Kho này có HAI cỗ máy. Khâm Thiên Giám (Polymarket, cổng 5186) có
        # ví riêng, sổ cái riêng và LỚP ĐẶT LỆNH riêng; Thị Bạc Ty không
        # quản nó. Khai ở đây thì Danh Mục THẤY được phần vốn ấy, và mọi
        # trần tính theo NAV mới tính trên tổng thật.
        #
        # Mặc định RỖNG, và đó là một lựa chọn chứ không phải lười: bật lên
        # mà cỗ máy kia không chạy thì cầu dao ngắt vĩnh viễn (`von-ngoai-mu`)
        # và Thị Bạc Ty không cấp đồng nào — đúng về nguyên tắc, nhưng vô
        # dụng khi cỗ máy kia vốn dĩ chỉ chạy lúc cần.
        #
        # LUẬT PHẢI GIỮ: **trước khi mở bất kỳ cửa đặt lệnh nào của Khâm
        # Thiên Giám, BẬT khoá này lên.** Từ giây phút cỗ máy kia chạm tiền
        # thật, `tranMotCang` và `sutVonToiDaPct` của Trung Ương chỉ còn là
        # trần của một nửa gia sản trong khi mọi bảng đọc chúng như trần của
        # cả gia sản.
        #
        # BẬT SẴN, không đợi tới ngày mở cửa đặt lệnh. Một lớp an toàn chỉ
        # được cấu hình vào đúng ngày người ta cần nó là một lớp an toàn
        # không tồn tại: cái ngày ấy là ngày bận nhất, và luật này nằm
        # trong một chú thích mà lúc đó chưa chắc ai đọc.
        #
        # Cỗ máy kia tắt thì `docDuoc=False`, và đó là một TRẠNG THÁI hiện
        # ra trong ảnh chụp — không phải lỗi, không phải 0. Bật sẵn còn có
        # nghĩa là ta thấy nó tắt; để rỗng thì ta không thấy gì cả, và hai
        # chuyện ấy trông giống hệt nhau trên buồng lái.
        "vonNgoai": {
            "kham-thien-giam": "http://127.0.0.1:5186/api/trang-thai",
        },
        # Kết toán Khâm Thiên Giám vào CÙNG một sổ cái — bước 3 của món
        # nợ hai cỗ máy. `von_ngoai` giữ phần TIỀN (phơi nhiễm chỉ-đọc
        # trong Danh Mục), sổ này giữ phần SỰ KIỆN.
        #
        # Bên kia chỉ công bố 12 bản ghi gần nhất, nên `soBoSot` đếm phần
        # rơi giữa hai lượt hỏi. Một sổ nói "tôi thiếu N" tốt hơn hẳn một
        # sổ nói "tôi đủ" trong khi thiếu.
        "soNgoai": {
            "kham-thien-giam": {
                "url": "http://127.0.0.1:5186/api/trang-thai",
                "chienLuoc": "prediction.polymarket.v1",
            },
        },
        "vonBanDauUsd": 1000.0,
        "nguongCauDao": {
            # Rộng hơn cửa `lechDongHoToiDaGiay` của ty (10s) có chủ ý: cửa
            # ty nói "cơ hội này không đáng tin", cầu dao nói "cả cỗ máy
            # đang nhìn sai thế giới". Hai câu khác nhau, hai ngưỡng khác
            # nhau — bằng nhau thì cầu dao ngắt mỗi lần một cơ hội bị loại.
            "lechDongHoToiDaGiay": 60.0,
            "soCangChetToiDa": 1,
            "tuoiToiDaGiay": 300.0,
            "sutVonToiDaPct": 10.0,
        },
    },
    "so": {
        "giuNgay": 30,
    },
    "bang": {
        # Băng ghi NGUYÊN LIỆU để còn chạy lại được. Tắt nó đi là tắt luôn
        # khả năng đo xem một thay đổi tốt hơn hay chỉ khác đi.
        "ghi": True,
        "thuMuc": "bang",
        "ngayGiuLai": 30,
    },
}

#: Tên định danh của chiến lược này, dạng `<lớp>.<chiến lược>.<phiên bản>`.
#:
#: Thị Bạc Ty hiện có ĐÚNG MỘT chiến lược, nên trường này chưa phân biệt được
#: gì — nó tốn một dòng và trả lời một câu hỏi chưa ai hỏi. Giữ vì cái giá là
#: một dòng, còn cái giá của việc thêm nó SAU là đi sửa mọi lát cắt và mọi
#: băng đã ghi để gắn nhãn ngược.
#:
#: **MỘT nguồn duy nhất.** `bac/xuat_to_trinh.py` import hằng số này chứ
#: không khai lại — hai bản sao thì sẽ lệch, và đã lệch thật một lần:
#: lát cắt ghi `perp.…` còn tờ trình ghi `perpetual.…`, hai chuỗi cho
#: cùng một thứ. Sổ đăng ký sau này gộp theo chuỗi ấy, nên lệch một ký
#: tự là hai dòng thống kê cho một chiến lược.
#:
#: Đổi số phiên bản khi công thức `netBps` đổi cách tính — không phải khi vặn
#: ngưỡng. Ngưỡng vặn được là chuyện thường ngày của vòng tiến hoá; công thức
#: đổi thì mọi con số cũ hết so được với số mới, và đó mới là đứt gãy.
MA_CHIEN_LUOC = "perpetual.funding_spread.v1"

CHE_HOP_LE = ("quan-sat", "giay", "that")


def _gop(mac_dinh: dict, tren: dict) -> dict:
    """Gộp sâu, và cấu hình người dùng KHÔNG được xoá khoá mặc định.

    Gộp nông thì đặt `"ruiRo": {"netToiThieuBps": 2}` sẽ vứt sạch sáu cửa còn
    lại về không tồn tại, và cổng rủi ro rơi về giá trị rỗng — tức là mở toang
    trong khi người sửa tưởng mình vừa siết chặt.
    """
    ra = dict(mac_dinh)
    for k, v in (tren or {}).items():
        ra[k] = _gop(ra[k], v) if isinstance(v, dict) and isinstance(ra.get(k), dict) else v
    return ra


def _doc_dotenv() -> None:
    """Đọc `.env` bằng tay — không phụ thuộc thư viện, không đè biến đã có.

    `utf-8-sig` chứ không phải `utf-8`: Notepad trên Windows lưu kèm BOM, và
    khi đó tên biến ĐẦU TIÊN thành "﻿BINANCE_API_KEY". Không lỗi nào
    báo — biến đó coi như không tồn tại, và người dùng ngồi nhìn một runtime
    bảo "thiếu khoá" trong khi khoá nằm sờ sờ trong file.
    """
    p = ROOT / ".env"
    if not p.exists():
        return
    for tho in p.read_text(encoding="utf-8-sig").splitlines():
        d = tho.strip()
        if not d or d.startswith("#") or "=" not in d:
            continue
        k, v = d.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _nap() -> dict:
    _doc_dotenv()
    p = ROOT / "config.json"
    tren = {}
    if p.exists():
        tren = json.loads(p.read_text(encoding="utf-8-sig"))
    c = _gop(MAC_DINH, tren)
    if c["che"] not in CHE_HOP_LE:
        raise ValueError(f"che={c['che']!r} không hợp lệ, phải là một trong {CHE_HOP_LE}")
    return c


CONFIG = _nap()
DATA_DIR.mkdir(parents=True, exist_ok=True)

#: Tên biến môi trường của từng sàn. Chỉ để BIẾT có khoá hay không — không
#: chỗ nào trong runtime đọc giá trị của chúng ở bản v0.1.
KHOA_SAN = {
    "binance": ("BINANCE_API_KEY", "BINANCE_API_SECRET"),
    "okx": ("OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"),
    "bybit": ("BYBIT_API_KEY", "BYBIT_API_SECRET"),
    "hyperliquid": ("HYPERLIQUID_PRIVATE_KEY",),
}


def san_co_khoa() -> dict[str, bool]:
    return {s: all(os.environ.get(k) for k in ks) for s, ks in KHOA_SAN.items()}


def ly_do_khong_that() -> list[str]:
    """Những cửa đang ĐÓNG, viết bằng câu người đọc hiểu ngay."""
    ra = []
    if CONFIG.get("che") != "that":
        ra.append('config.json → che vẫn là "%s", chưa phải "that"' % CONFIG.get("che"))
    if not (CONFIG.get("datLenh") or {}).get("toiXacNhanDaDocRuiRo"):
        ra.append("config.json → datLenh.toiXacNhanDaDocRuiRo chưa bật")
    if not any(san_co_khoa().values()):
        ra.append(".env → chưa sàn nào có đủ khoá API")
    # Cửa thứ tư: lớp đặt lệnh chưa tồn tại. Nó KHÔNG mở được bằng cấu hình,
    # và đó là chủ ý — xem README mục "Lộ trình".
    ra.append("lớp đặt lệnh chưa được viết (V0.6) — chưa có máy trạng thái "
              "hai chân, chưa có đối soát vị thế, chưa có kill switch")
    return ra


def che_hieu_luc() -> str:
    """Chế độ THẬT SỰ đang chạy, sau khi xét đủ mọi cửa.

    Khác `CONFIG["che"]` — đó chỉ là điều người dùng KHAI. Buồng lái phải hiện
    con số này, không hiện bản khai, nếu không nó sẽ nói "THẬT" trong khi mọi
    lệnh đang đi vào sổ giấy.
    """
    khai = CONFIG.get("che", "quan-sat")
    if khai != "that":
        return khai
    return "giay"       # còn cửa đóng thì rơi về sổ giấy, không bao giờ "that"
