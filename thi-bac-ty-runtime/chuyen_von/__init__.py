"""CHUYỂN VỐN — bản đồ vốn, và giá của việc dời vốn từ chỗ này sang chỗ kia.

Không phải một ty, và không phải Trung Ương. Cùng hạng với `chuoi_chung/`,
`phai_sinh_chung/`, `san_chung/`: hạ tầng mà nhiều ty đọc.

Ra đời vì BỐN trong năm ty đang tự khai thiếu đúng một khoản chi phí, và
không ty nào tự giải được:

    tin_dung/    chuyen-von-giua-chuoi
    lai_suat/    chuyen-von-giua-chuoi · gas-vao-ra
    on_dinh/     chuyen-von-giua-san   · rut-tien-va-thoi-gian-cho
    co_so/       (không cần — hai chân cùng một sàn)

Bản đồ §18 gọi nó là hạ tầng chứ không phải một bot, và đó là phân loại
đúng: nó không quét cơ hội, không xin vốn, không có `quet()`. Nó trả lời
đúng một câu hỏi cho ty khác hỏi:

    dời $X tài sản A từ ĐIỂM này sang ĐIỂM kia thì mất bao nhiêu, mất bao
    lâu, và có gì tôi KHÔNG đo được không?

Câu cuối mới là phần đáng giá.

## Vì sao nó KHÔNG xoá được cả bốn khai báo

Thử thật ngày 27/08/2026, và ranh giới hoá ra rất sắc:

| cần gì | đọc được không cần khoá? |
|---|---|
| gas bốn chuỗi | ĐƯỢC — RPC công khai `eth_gasPrice` |
| phí + thời gian cầu nối | ĐƯỢC — LI.FI `/v1/quote` |
| phí RÚT của sàn CEX | **KHÔNG** — Binance `-2014`, OKX `50103` |

Nên Router gỡ được `chuyen-von-giua-chuoi` và `gas-vao-ra` bằng số ĐO
ĐƯỢC, còn `chuyen-von-giua-san` thì không. Chỗ đó nó dùng bảng đo tay có
XUẤT XỨ và có HẠN (`bang_do.py`) — và khi bảng quá hạn thì nó trả về
`None` chứ không trả số cũ.

**Một hạ tầng gỡ được ba phần tư mà im lặng về phần tư còn lại thì tệ hơn
là không có nó**: ty sẽ bỏ khai báo `phiConThieu` đi vì tưởng đã có Router
lo, và con số NET lại quay về chỗ hào phóng với chính mình — đúng thứ
`moHinhPhiDuChua` sinh ra để chặn.
"""
