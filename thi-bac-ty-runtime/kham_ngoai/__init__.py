"""ADAPTER TY cho Khâm Thiên Giám — bước 2 của món nợ hai cỗ máy.

README khai món nợ này ở mục "NỢ KIẾN TRÚC ĐÃ BIẾT", và bốn bước gỡ nó.
Đây là bước 2:

    1. Đừng dựng cỗ máy thứ ba.                          ← đã giữ
    2. Cho `kham/` một adapter `Ty`.                      ← FILE NÀY
    3. `ket_toan.py` sang Sổ Cái, `vi.py` vào Danh Mục.   ← nửa sau đã xong
    4. `dat_lenh.py` chuyển sau cùng.                     ← CHẶN, xem dưới

## Ranh giới đếm: `von_ngoai` lo cái ĐANG GIỮ, file này lo cái CHƯA LẤY

Đây là chỗ dễ hỏng nhất, và nó hỏng theo hướng tệ nhất — đếm hai lần.

Khâm Thiên Giám có `dat_lenh.py` của riêng nó. Nếu adapter này nộp tờ trình
xin vốn cho một cơ hội mà cỗ máy kia ĐANG TỰ LÀM, thì cùng một vị thế được
tính hai lần: một lần là vốn ngoài trong Danh Mục, một lần là vốn Thị Bạc
Ty vừa cấp. Trần `tranMotCang` khi ấy tưởng mình đang chặn ở 30% trong khi
thực tế là 60%.

Nên ranh giới cứng, và nó nằm ở đúng một dòng lọc:

    dangLam = True   → cỗ máy kia đã lấy → `von_ngoai` đếm → adapter BỎ QUA
    dangLam = False  → nó chỉ mới thấy   → adapter nộp tờ trình

Hai đường không giao nhau, và không cơ hội nào rơi vào cả hai.

## Đọc qua HTTP, KHÔNG import — cùng lý do `von_ngoai.py`

Hai runtime là hai tiến trình, hai vòng đời, hai lịch khởi động lại. Import
là buộc chúng thành một. Và `thi_bac_ty/` thì không được biết ty nào tồn
tại, huống hồ cỗ máy nào — nên adapter nằm ở đây, ngoài Trung Ương, đúng
hạng với `bac/` và `co_so/`.

Hệ quả: cỗ máy kia tắt thì `quet()` trả rỗng và ty tự khai là mù. Không
phải lỗi, không phải "không có cơ hội" — hai chuyện ấy trông giống hệt nhau
nếu không ai nói ra, và `chanDoan` nói ra.

## Bước 4 bị CHẶN, và chặn có chủ ý

`dat_lenh.py` chỉ chuyển được khi Điều Phối Thực Thi có lớp ký lệnh thật.
Lớp ấy KHÔNG tồn tại và không được phép tồn tại: `DieuPhoiThucThi.moPhong`
là `True` cứng, không cấu hình nào mở được. Nên bước 4 không phải "chưa
làm" — nó là "không làm được từ phía này", và ghi ra đây để không ai tưởng
đó là một việc còn tồn đọng chờ người rảnh.
"""
