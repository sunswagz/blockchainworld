"""Quét ĐỘT BIẾN: đổi từng toán tử so sánh trong một file, chạy phép
kiểm, xem con nào SỐNG SÓT.

    python scripts/quet-dot-bien.py kham/rui_ro.py
    python scripts/quet-dot-bien.py kham/rui_ro.py kiem_rui_ro   # một hàm

Con SỐNG SÓT = một dòng mã sửa sai mà không phép kiểm nào kêu. Không
phải lỗi, nhưng là chỗ mã có thể sai mà không ai biết — và trong một cỗ
máy tiêu tiền, «không ai biết» là dạng lỗi đắt nhất.

Bản này CHÉP TỪ `thi-bac-ty-runtime/scripts/quet-dot-bien.py`,
không viết lại. Ba cái bẫy dưới đây đã được vá ở đó bằng máu, và
viết lại là mời chúng quay về. Sửa ở đây thì soi lại bản kia.

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

File đang quét bị GHI ĐÈ rồi trả lại sau mỗi con. Ba điều phải nhớ:

- ĐỪNG chạy song song với một phiên đang sửa cùng file ấy.
- ĐỪNG chạy `git` (rebase, checkout, pull) trên cây làm việc trong lúc
  quét. Đã cắn thật: `git rebase` chạm vào file đúng lúc bộ quét đang
  ghi lại bản gốc, Windows trả `OSError: [Errno 22]`, bộ quét chết, và
  **một con đột biến ở lại trong mã** — trong `trung_uong.py`, giữa cỗ
  máy chia tiền. Nay có bản sao lưu và vòng thử lại, nhưng cách chắc
  chắn nhất vẫn là để nó chạy một mình.
- Bản gốc được chép ra `<file>.goc-quet` TRƯỚC con đột biến đầu tiên,
  và chỉ xoá khi đã trả lại xong xuôi. File ấy còn nằm đó nghĩa là lần
  quét trước chết giữa chừng.
"""
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, ".")

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

# Bản Thị Bạc Ty nhận THAM SỐ VỊ TRÍ (`sys.argv[1]`). Ở cung này có một
# luật: mọi script đo đạc phải khai cờ qua `tham_so.doc`, và bộ kiểm
# canh luật ấy — nó bắt được chính file này ngay lần chạy đầu.
#
# Luật ấy đúng cả ở đây chứ không chỉ là hình thức: với tham số vị trí,
# gõ `--ham=kiem_rui_ro` thay vì `--ham kiem_rui_ro` sẽ khiến chuỗi
# `--ham=...` bị nhận làm TÊN FILE, và bộ quét đi quét một file không
# tồn tại. Cờ có khai thì nó kêu.
CO = tham_so.doc({
    "file": "file đem đột biến, ví dụ kham/rui_ro.py",
    "ham": "chỉ chạy MỘT hàm kiểm, ví dụ kiem_rui_ro (mặc định: cả suite)",
}, ten='quet-dot-bien.py')

F = CO.lay("file", "")
HAM = CO.lay("ham", "") or None
if not F:
    print(chr(10) + "  Thiếu `--file=`. Ví dụ:")
    print("    python scripts/quet-dot-bien.py --file=kham/rui_ro.py")
    print("    python scripts/quet-dot-bien.py --file=kham/rui_ro.py "
          "--ham=kiem_rui_ro" + NL)
    raise SystemExit(1)

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

SAO_LUU = F + ".goc-quet"


def _ghi(duong, noi_dung, lan=6):
    """Ghi, thử lại vài lần.

    Windows khoá file trong tích tắc khi một tiến trình khác chạm vào
    nó — `git`, trình soạn, trình duyệt file — và MỘT lần ghi hỏng ở đây
    để lại một con đột biến trong mã.
    """
    import time as _t
    for k in range(lan):
        try:
            io.open(duong, "w", encoding="utf-8", newline="\n").write(noi_dung)
            return True
        except OSError:
            if k == lan - 1:
                return False
            _t.sleep(0.3 * (k + 1))
    return False


def _tra_lai():
    if _ghi(F, goc):
        return True
    print(f"\n  !! KHÔNG TRẢ LẠI ĐƯỢC {F} — nó ĐANG MANG MỘT CON ĐỘT BIẾN.")
    print(f"  !! Bản gốc nằm ở {SAO_LUU}. Chạy:")
    print(f"  !!     cp '{SAO_LUU}' '{F}'")
    print(f"  !! hoặc `git checkout -- {F}` nếu file ấy đã commit.")
    return False


# ── BẢN SAO LƯU CÒN SÓT = LƯỢT TRƯỚC CHẾT GIỮA CHỪNG ─────────────────
#
# `_tra_lai()` chạy trong `finally` sau mỗi con, nên lượt quét bình
# thường luôn dọn sạch. Nhưng `finally` KHÔNG chạy khi tiến trình bị
# giết — hết giờ, Ctrl-C đúng lúc, máy tắt. Khi ấy `F` nằm lại trên đĩa
# MANG MỘT CON ĐỘT BIẾN, và `<file>.goc-quet` còn đó.
#
# Chạy tiếp trong tình trạng ấy là hỏng vĩnh viễn: dòng dưới sẽ ghi đè
# bản sao lưu bằng nội dung HIỆN TẠI của `F` — tức bằng chính con đột
# biến — và đường lùi biến mất. Sau đó mọi con đều được so với một bản
# "gốc" đã sai, nên bộ quét sẽ báo rất nhiều con CHẾT: mã hỏng sẵn nên
# phép kiểm đỏ sẵn. Một phiếu điểm đẹp dựng trên một file hỏng.
#
# Chú thích cuối file đã nói đúng chuyện này ("File ấy còn nằm đó nghĩa
# là lần quét trước chết giữa chừng") nhưng không có gì hành động theo.
if os.path.exists(SAO_LUU):
    print()
    print(f"  DỪNG: {SAO_LUU} còn nằm đó — lượt quét TRƯỚC chết giữa")
    print(f"  chừng, nên {F} rất có thể đang mang một con đột biến.")
    print("  Khôi phục rồi hãy quét lại:")
    print(f"      cp '{SAO_LUU}' '{F}' && rm '{SAO_LUU}'")
    print(f"  hoặc `git checkout -- {F}` rồi xoá bản sao lưu.")
    print()
    sys.exit(6)

if not _ghi(SAO_LUU, goc):
    print(f"  DỪNG: không ghi nổi bản sao lưu {SAO_LUU} — không quét khi "
          f"chưa có đường lùi.")
    sys.exit(3)

print(f"  {len(ca)} chỗ đem đột biến trong {F}")
song = []
for i, moi, nhan in ca:
    ds = list(dong)
    ds[i] = moi
    moi_tho = "".join(ds)
    if not _ghi(F, moi_tho):
        print(f"  DỪNG ở dòng {i + 1}: không ghi nổi bản đột biến.")
        _tra_lai()
        sys.exit(4)

    # ── CHỨNG rằng con đột biến THẬT SỰ nằm trên đĩa ─────────────────
    #
    # Ai đó khác đụng vào file giữa lúc quét thì kết quả thành RÁC, và
    # rác theo chiều nguy nhất: nếu file bị trả về bản GỐC thì bài kiểm
    # xanh và con đột biến bị đếm là SỐNG; nếu bị để lại bản đột biến
    # của lượt trước thì bài kiểm đỏ và con này bị đếm là CHẾT.
    #
    # Đã xảy ra thật 30/08/2026: một lượt quét `vong.py` chạy trong khi
    # tôi `git rebase --autostash` để commit việc khác. Autostash cất
    # rồi trả lại file giữa chừng, và lượt quét ấy báo 16/50 sống.
    # Quét lại khi cây yên tĩnh: 41/50. Con số đầu KHÔNG phải một phép
    # đo, nó là một tai nạn — và nó lệch về phía TRÔNG ĐẸP HƠN.
    try:
        tren_dia = io.open(F, encoding="utf-8").read()
    except OSError:
        tren_dia = None
    if tren_dia != moi_tho:
        print()
        print(f"  DỪNG ở dòng {i + 1}: file trên đĩa KHÔNG phải bản")
        print("  đột biến vừa ghi — có thứ khác đang đụng vào nó (git,")
        print("  trình soạn, một phiên khác). Mọi con số từ đây sẽ là rác.")
        _tra_lai()
        sys.exit(8)
    try:
        r, out = _chay()
    finally:
        if not _tra_lai():
            sys.exit(5)
    bat = "✗" in out or r.returncode != 0
    if not bat:
        song.append((i + 1, nhan, dong[i].strip()[:78]))

# Dọn bản sao lưu CHỈ khi file đã TRỞ LẠI ĐÚNG TỪNG BYTE. Xoá theo niềm
# tin là bỏ mất đường lùi đúng lúc cần nó nhất — và một con đột biến sót
# lại trong mã thì lần chạy sau không phân biệt được với mã thật.
try:
    lai = io.open(F, encoding="utf-8").read()
except OSError:
    lai = None
if lai != goc:
    print()
    print(f"  !! {F} KHÔNG trở lại đúng bản gốc sau lượt quét.")
    print(f"  !! GIỮ bản sao lưu {SAO_LUU}. Khôi phục bằng:")
    print(f"  !!     cp '{SAO_LUU}' '{F}'")
    print()
    sys.exit(7)
try:
    os.remove(SAO_LUU)
except OSError:
    pass

print(f"  SỐNG SÓT {len(song)}/{len(ca)}")
for ln, nhan, txt in song:
    print(f"    dòng {ln:>4}  [{nhan}]  {txt}")
