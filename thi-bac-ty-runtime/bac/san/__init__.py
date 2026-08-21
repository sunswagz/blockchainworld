"""Bốn cảng: Hyperliquid, Binance, OKX, Bybit.

Mỗi cảng công bố funding theo một khuôn khác nhau, và **cả bốn đều không nói
cùng một đơn vị**. Việc của gói này là đưa chúng về đúng một kiểu `BaoGia`,
mang theo `intervalGio` thật và `mocKeMs` thật — hai thứ mà mọi phép tính
phía sau dựa vào.

Nguyên tắc chung, và nó quan trọng hơn từng adapter:

  * **Không adapter nào được đoán thầm.** Suy ra được thì suy, nhưng phải bật
    `intervalSuyRa` để cổng rủi ro biết mà hạ tin cậy.
  * **Không adapter nào được ném ra ngoài.** Một cảng chết không được kéo theo
    ba cảng còn sống; `SucKhoe` ghi lại lỗi rồi trả về danh sách rỗng.
  * **`markPx` phải là GIÁ MARK.** Lấy giá khớp cuối (`last`) là so hai đại
    lượng khác nhau: `last` nhảy theo từng lệnh lẻ, `mark` là giá dùng để
    thanh lý. Bản v0.1 lấy `last` của OKX rồi so với `markPrice` của Binance,
    và độ lệch tính ra là một hỗn hợp của lệch thật lẫn tiếng ồn vi cấu trúc.
"""
from .base import Cang, SucKhoe          # noqa: F401
from .binance import Binance             # noqa: F401
from .bybit import Bybit                 # noqa: F401
from .hyperliquid import Hyperliquid     # noqa: F401
from .okx import OKX                     # noqa: F401

TAT_CA = {
    "hyperliquid": Hyperliquid,
    "binance": Binance,
    "okx": OKX,
    "bybit": Bybit,
}
