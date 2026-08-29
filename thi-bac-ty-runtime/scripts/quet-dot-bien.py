"""Quét ĐỘT BIẾN: đổi từng toán tử so sánh trong một file, chạy phép
kiểm, xem con nào SỐNG SÓT.

    python scripts/quet-dot-bien.py thi_bac_ty/rui_ro_tong.py kiem_rui_ro_tong
    python scripts/quet-dot-bien.py thi_bac_ty/phan_bo.py            # cả suite

Con SỐNG SÓT = một dòng mã sửa sai mà không phép kiểm nào kêu. Không
phải lỗi, nhưng là chỗ mã có thể sai mà không ai biết — và trong một cỗ
máy chia tiền, «không ai biết» là dạng lỗi đắt nhất.

Vì sao cần nó. Một phiếu «1.550/1.550 đạt» không nói phép kiểm CHẠM TỚI
đâu. Lượt quét đầu trên `rui_ro_tong.py` — cái cổng quyết tiền có được
cam kết hay không — cho 10/15 con sống sót, và phần lớn nằm đúng ở
BIÊN: không phép kiểm nào phân biệt được «đúng bằng trần» với «vượt
trần». Sau khi vá: 3/15, cả ba đều tương đương.

BA CÁI BẪY đã cắn, đều đã vá trong file này:

1. Đột biến trong CHUỖI. `f"... {x:.2f} > trần ..."` bị đếm là một phép
   so; đổi nó chỉ đổi CHỮ nên con ấy luôn sống sót và luôn vô nghĩa.
2. Đột biến trong DOCSTRING nhiều dòng. Cùng loại, nhưng `_bo_chuoi`
   không thấy vì nháy mở và nháy đóng nằm khác dòng.
3. Tên hàm kiểm GÕ SAI cho ra «SỐNG SÓT 0/15» — một tờ phiếu hoàn hảo,
   vì mọi con đột biến đều chết bằng cùng một `AttributeError` chưa
   từng chạm tới file đang quét. Nay có bước CHỨNG: chạy bản gốc
   trước, bản gốc trượt thì dừng và nói ra.

Thước đo hỏng thì điểm đẹp. Điểm đẹp là lúc phải nghi thước.

File đang quét bị GHI ĐÈ rồi trả lại sau mỗi con. Đừng chạy nó song
song với một phiên đang sửa cùng file ấy, và đừng chạy khi cây làm việc
còn thay đổi chưa commit ở file đó.
"""
import io
import os
import re
import subprocess
import sys

F = sys.argv[1]
HAM = sys.argv[2] if len(sys.argv) > 2 else None

goc = io.open(F, encoding="utf-8").read()
dong = goc.splitlines(keepends=True)

DOI = [(" >= ", " > "), (" <= ", " < "), (" > ", " >= "), (" < ", " <= "),
       (" == ", " != "), (" != ", " == "),
       (" and ", " or "), (" or ", " and ")]

def _bo_chuoi(d):
    """Xoá phần nằm trong nháy, để không đột biến chữ in ra.

    Không có bước này thì `f"... {x:.2f} > trần ..."` bị đếm là một phép
    so — đổi nó chỉ đổi CHỮ, nên con đột biến ấy luôn sống sót và luôn vô
    nghĩa. Bốn trong mười bốn con «sống sót» của lượt quét đầu là loại ấy,
    và chúng làm loãng đúng danh sách mình cần đọc.
    """
    return re.sub(r"(\"(?:[^\"\\\\]|\\\\.)*\"|'(?:[^'\\\\]|\\\\.)*')", '""', d)


# Bỏ hẳn thân chuỗi NHIỀU DÒNG. `_bo_chuoi` chỉ thấy nháy nằm gọn trên
# một dòng, nên một dòng văn xuôi giữa docstring («tổng được phép =
# $1.200 > $1.000 có») bị đếm là một phép so. Con đột biến ấy chỉ đổi
# CHỮ nên luôn sống sót — và nó nằm ngay đầu danh sách mình phải đọc.
trong_chuoi = False
bo_qua = set()
for i, d in enumerate(dong):
    dem = d.count('"' * 3) + d.count("'" * 3)
    if trong_chuoi:
        bo_qua.add(i)
    if dem % 2 == 1:
        if not trong_chuoi:
            bo_qua.add(i)
        trong_chuoi = not trong_chuoi

ca = []
for i, d in enumerate(dong):
    t = d.strip()
    if i in bo_qua:
        continue
    if not t or t.startswith("#") or t.startswith('"""') or t.startswith("'''"):
        continue
    sach = _bo_chuoi(d)
    for a, b in DOI:
        if a in sach:
            # Đổi trong bản GỐC, nhưng chỉ khi bản đã bỏ chuỗi cũng có nó.
            j = sach.index(a)
            ca.append((i, d[:j] + d[j:].replace(a, b, 1),
                       a.strip() + " -> " + b.strip()))
            break

def _chay():
    lenh = ("import sys;sys.path[:0]=['.','scripts'];import selftest as st;"
            + (f"st.{HAM}()" if HAM else "st.main()"))
    r = subprocess.run([sys.executable, "-c", lenh],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=900,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return r, (r.stdout or "") + (r.stderr or "")


# ── CHỨNG: bản GỐC phải XANH trước đã ──────────────────────────────────
#
# Không có bước này thì một cái tên hàm gõ sai cho ra "SỐNG SÓT 0/15" —
# một tờ phiếu hoàn hảo, vì mọi con đột biến đều "chết" bằng cùng một lỗi
# AttributeError chưa từng chạm tới file đang quét. Đã cắn thật: quét
# `xoay_cho.py` với `kiem_xoay_cho`, một hàm không tồn tại.
#
# Thước đo hỏng thì điểm đẹp. Điểm đẹp là lúc phải nghi thước.
_r0, _o0 = _chay()
if "✗" in _o0 or _r0.returncode != 0:
    print(f"  DỪNG: bản GỐC đã TRƯỢT, nên mọi con đột biến sẽ 'chết' vì lý "
          f"do chẳng liên quan gì tới {F}.")
    print("  " + (_o0.strip().splitlines() or ["(không có gì in ra)"])[-1])
    sys.exit(2)

print(f"  {len(ca)} chỗ đem đột biến trong {F}")
song = []
for i, moi, nhan in ca:
    ds = list(dong)
    ds[i] = moi
    io.open(F, "w", encoding="utf-8", newline="\n").write("".join(ds))
    try:
        r, out = _chay()
    finally:
        io.open(F, "w", encoding="utf-8", newline="\n").write(goc)
    bat = "✗" in out or r.returncode != 0
    if not bat:
        song.append((i + 1, nhan, dong[i].strip()[:78]))

print(f"  SỐNG SÓT {len(song)}/{len(ca)}")
for ln, nhan, txt in song:
    print(f"    dòng {ln:>4}  [{nhan}]  {txt}")
