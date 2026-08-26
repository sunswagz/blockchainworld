"""Lệch đồng hồ máy/sàn — thân hàm ở `phai_sinh_chung/dong_ho.py`.

MỘT đồng hồ dùng chung cho cả họ phái sinh, không phải một đồng hồ mỗi ty.
Hai ty đo lệch riêng là hai phần bù khác nhau cho cùng một cái đồng hồ, và
chúng sẽ đếm mốc ra hai kết quả khác nhau trên cùng một khung thời gian.
"""
from phai_sinh_chung.dong_ho import (  # noqa: F401
    NGUON_GIO, NGUONG_KEU_MS, DongHo, do_lech, dong_ho)
