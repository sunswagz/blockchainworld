"""Ty BỂ THANH KHOẢN V3 — cấp thanh khoản tập trung trên một DẢI giá.

Ty thứ mười của Thị Bạc Ty, ty thứ hai của họ `thanh-khoan`. Khác hẳn
`lp_amm/` (chỉ nhận cặp NEO nhau vì không ước được tổn thất vô thường): ty
này nhận cặp BIẾN ĐỘNG — cổ phiếu token hoá (NVDAx, SPYx…) so với USDG trên
X Layer — nhưng chỉ khi ĐO ĐƯỢC σ, vì với σ trong tay thì tổn thất vô
thường, LVR và xác suất văng dải đều là phép tính chứ không phải phỏng đoán.

    mo_hinh.py     toán V3 · σ · IL · LVR · xác suất văng dải — KHÔNG mạng
    lich.py        phiên Mỹ theo giờ Việt Nam · ngày nghỉ · sự kiện · thưởng
    quyet_dinh.py  sổ luật «lúc nào làm gì», viết dạng CHẠY ĐƯỢC
    nguon.py       giá gốc (Stooq) · trạng thái pool (RPC X Layer) · tin (RSS)
    bang_gia.py    băng giá tự tích — càng chạy lâu càng biết nhiều
    theo_doi.py    vị thế NGƯỜI đang giữ ở OKX — máy theo dõi, không đặt lệnh
    kinh_nghiem.py sổ kinh nghiệm: quyết định → kết cục → bài học
    tien_hoa.py    tự vặn núm bằng chạy lại băng, qua cổng, ghi sổ
    ty_bien_do.py  ty: quet · xet · trinh · ke_toan
    ngay.py        vòng ngày: sáng · trước mở cửa Mỹ · sau đóng cửa
    hom_nay.py     `python -m lp_v3.hom_nay` — một trang: giờ này nên làm gì
"""
