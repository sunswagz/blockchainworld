"""Đếm mốc kết toán — thân hàm ở `phai_sinh_chung/dongho.py`.

Chuyển ra ngoài khi ty Cơ Sở (basis) tới: nó cũng thu funding tại mốc, và
hai lựa chọn còn lại đều sai — chép sang (hai bản sao sẽ lệch nhau đúng vào
ngày ai đó sửa một bản) hay để ty mới import ty này (điều luật chung cấm).

Giữ `bac.dongho` làm bí danh vì mã và phép kiểm đã gọi nó ở nhiều chỗ; đổi
tên chỉ để cho gọn là một lần sửa rủi ro không đổi lấy gì.
"""
from phai_sinh_chung.dongho import (  # noqa: F401
    GIO_MS, LichMoc, dem_moc, moi_gio, moi_ngay, thu_cap, thu_thuc)
