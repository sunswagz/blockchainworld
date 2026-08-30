"""Adapter SDK Polymarket — lớp DUY NHẤT trong repo chạm tới khoá ví.

Cô lập ở đây vì hai lý do, và cả hai đều thật:

1. **SDK sẽ đổi.** `Polymarket/py-clob-client` đời cũ đã bị archive
   25/05/2026 và chính repo đó ghi rõ không nên dùng cho tích hợp mới. SDK
   hợp nhất hiện hành là `Polymarket/py-sdk` (gói `polymarket-client`), và
   Polymarket còn đang trong quá trình chuyển CLOB V2 với contract và
   collateral mới. Bám vào SDK ở một chỗ thì lúc nó đổi chỉ sửa file này.

2. **Khoá ví không được rải khắp nơi.** Chỉ file này đọc
   `POLYMARKET_PRIVATE_KEY`, và nó chỉ được import khi `dat_lenh.py` đã đi
   qua đủ ba cửa. Module này KHÔNG được import ở đầu file bất kỳ đâu khác.

Xác thực Polymarket có hai tầng: L1 dùng chữ ký EIP-712 từ private key để tạo
hoặc suy ra API credentials; L2 dùng API key/secret/passphrase với HMAC-SHA256
cho đặt lệnh, huỷ lệnh và truy vấn trades.
"""
from __future__ import annotations

import os

from .config import CONFIG, ly_do_khong_that


class AdapterPolymarket:
    """Bọc SDK chính thức. Khởi tạo là đã ném nếu thiếu bất cứ thứ gì."""

    def __init__(self) -> None:
        thieu = ly_do_khong_that()
        if thieu:
            # Chốt chặn thứ hai. `dat_lenh.py` đã kiểm rồi, nhưng lớp này có
            # thể bị ai đó import thẳng trong tương lai — và lúc đó không có
            # ai kiểm hộ nữa.
            raise RuntimeError("chưa mở đủ cửa lệnh thật: " + "; ".join(thieu))

        try:
            from polymarket import ClobClient       # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "thiếu gói `polymarket-client`. Cài bằng: "
                "pip install polymarket-client  (bỏ dấu # trong requirements.txt)"
            ) from e

        khoa = os.environ["POLYMARKET_PRIVATE_KEY"]
        self.client = ClobClient(
            host=CONFIG["nguon"]["polymarketClob"],
            key=khoa,
            chain_id=137,                            # Polygon
            funder=os.environ.get("POLYMARKET_FUNDER_ADDRESS") or None,
        )
        # L2: dùng credentials có sẵn nếu đã cấp, không thì suy ra từ L1.
        if os.environ.get("POLYMARKET_API_KEY"):
            self.client.set_api_creds({
                "key": os.environ["POLYMARKET_API_KEY"],
                "secret": os.environ.get("POLYMARKET_API_SECRET", ""),
                "passphrase": os.environ.get("POLYMARKET_API_PASSPHRASE", ""),
            })
        else:
            self.client.set_api_creds(self.client.derive_api_key())

    def dat_lenh(self, ma: str, ben: str, soCo: float, gia: float,
                 laMaker: bool) -> dict:
        """Đặt một lệnh. Trả về dict thống nhất, không phải object của SDK.

        Trả dict là chủ ý: `dat_lenh.py` không được biết hình dạng đối tượng
        của SDK, nếu không thì cô lập ở đây thành vô nghĩa.

        `tokenId` phải do chỗ gọi truyền xuống qua `ma` đã phân giải. Bản này
        để `NotImplementedError` ở đúng chỗ cần một quyết định thật — phân
        giải market sang token id và chọn loại lệnh (GTC/FOK/GTD) tuỳ luật
        của từng market — thay vì đoán một mặc định rồi gửi tiền thật đi theo
        phỏng đoán đó.

        ## BA SỰ THẬT VẬN HÀNH — đọc trước khi viết một dòng nào ở đây

        Đối chiếu docs.polymarket.com ngày 30/08/2026 (trang tài liệu vào
        được trong khi API bị chặn TLS). Ba thứ dưới đây KHÔNG suy ra
        được từ mã hiện có, và mỗi thứ đều làm hỏng lệnh thật theo một
        kiểu im lặng khác nhau:

        **1. HTTP 425 (Too Early) không phải lỗi.** Trong lúc sàn khởi
        động lại, MỌI endpoint liên quan tới lệnh trả 425. Coi nó là lỗi
        vĩnh viễn thì bot tự tắt giữa phiên; coi nó là thất bại của lệnh
        thì bot đặt lại một lệnh có thể đã vào. Phải lùi theo cấp số
        nhân, bắt đầu 1–2 giây.

        **2. Sau MỖI lần khởi động lại, sàn chỉ nhận POST-ONLY trong 2
        phút.** Lệnh không `postOnly` bị TỪ CHỐI. Với khung 5 phút thì
        hai phút ấy là 40% một cửa sổ — mọi chiến thuật vượt spread
        (`lech-gia`, `cap-tuc-thi`) đứng hình trong quãng đó, và chỉ
        `tao-lap` còn đặt được. Bot phải BIẾT mình đang ở trong quãng ấy
        chứ không phải đoán qua chuỗi lệnh bị từ chối.

        **3. `orderMinSize` là của TỪNG market**, đọc từ
        `market.trading` chứ không phải một hằng số. Cổng 11 hiện chặn
        ở "dưới 1 cổ" — một con số ta tự nghĩ ra, không phải luật của
        sàn. Lệnh dưới ngưỡng thật bị CLOB từ chối.

        Và một thứ nữa, không phải bẫy mà là tiền bỏ quên: biểu phí có
        `rebateRate` (crypto 20% phí taker trả lại cho maker). Ta đang
        tính phí maker bằng 0 và KHÔNG tính khoản hoàn — tức là ước
        THIẾU thu nhập của chiến thuật `tao-lap`. Lệch chiều an toàn,
        nhưng nó làm `tao-lap` trông tệ hơn thực khi so với các ngón
        khác.
        """
        raise NotImplementedError(
            "Đường đặt lệnh thật cố ý dừng ở đây cho tới khi băng ghi đủ dài "
            "để chạy lại và đo được net edge THẬT sau phí. Xem lộ trình P0–P10 "
            "trong README: P10 là mốc duy nhất được bật, và nó đứng sau P4 "
            "(chạy lại lịch sử) cùng P9 (Champion/Challenger). Nối vào đây là "
            "nối `client.create_and_post_order` với tokenId đã phân giải."
        )

    def huy_lenh(self, lenhId: str) -> bool:
        raise NotImplementedError("xem ghi chú ở dat_lenh()")

    def so_du(self) -> dict:
        """Đọc số dư — đường ĐỌC, an toàn, dùng để kiểm nối ví."""
        return self.client.get_balance_allowance()
