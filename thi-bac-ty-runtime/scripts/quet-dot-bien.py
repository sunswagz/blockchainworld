"""Quét ĐỘT BIẾN: đổi từng toán tử so sánh trong một file, chạy phép
kiểm, xem con nào SỐNG SÓT.

    python scripts/quet-dot-bien.py thi_bac_ty/rui_ro_tong.py kiem_rui_ro_tong
    python scripts/quet-dot-bien.py thi_bac_ty/phan_bo.py            # cả suite
    python scripts/quet-dot-bien.py bac/can_loi.py --so-hoc          # lật cả + - * /

Con SỐNG SÓT = một dòng mã sửa sai mà không phép kiểm nào kêu. Không
phải lỗi, nhưng là chỗ mã có thể sai mà không ai biết — và trong một cỗ
máy chia tiền, «không ai biết» là dạng lỗi đắt nhất.

Vì sao cần nó. Một phiếu «1.550/1.550 đạt» không nói phép kiểm CHẠM TỚI
đâu. Lượt quét đầu trên `rui_ro_tong.py` — cái cổng quyết tiền có được
cam kết hay không — cho 10/15 con sống sót, và phần lớn nằm đúng ở
BIÊN: không phép kiểm nào phân biệt được «đúng bằng trần» với «vượt
trần». Sau khi vá: 3/15, cả ba đều tương đương.

BỐN CÁI BẪY đã cắn, đều đã vá trong file này:

1. Đột biến trong CHUỖI. `f"... {x:.2f} > trần ..."` bị đếm là một phép
   so; đổi nó chỉ đổi CHỮ nên con ấy luôn sống sót và luôn vô nghĩa.
2. Đột biến trong DOCSTRING nhiều dòng. Cùng loại, nhưng `_bo_chuoi`
   không thấy vì nháy mở và nháy đóng nằm khác dòng.
3. Đột biến trong CHÚ THÍCH cuối dòng. `# phí ra + phí vào` bị đếm là
   một phép cộng. Cùng họ với hai cái trên, và nó chỉ lộ ra khi bảng lật
   có thêm toán tử SỐ HỌC — chú thích thì đầy `+` và `-`.
4. Tên hàm kiểm GÕ SAI cho ra «SỐNG SÓT 0/15» — một tờ phiếu hoàn hảo,
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

_doi = [x for x in sys.argv[1:] if x != "--so-hoc"]
SO_HOC = "--so-hoc" in sys.argv[1:]
F = _doi[0]
HAM = _doi[1] if len(_doi) > 1 else None

goc = io.open(F, encoding="utf-8").read()
dong = goc.splitlines(keepends=True)

DOI = [(" >= ", " > "), (" <= ", " < "), (" > ", " >= "), (" < ", " <= "),
       (" == ", " != "), (" != ", " == "),
       (" and ", " or "), (" or ", " and ")]

#: Lật cả toán tử SỐ HỌC — bật bằng `--so-hoc`, KHÔNG bật mặc định.
#:
#: Vì sao cần: bảng trên chỉ lật phép SO SÁNH, nên trên một mô-đun toàn
#: phép TÍNH nó gần như không với tới. `bac/can_loi.py` — chỗ tính NET
#: APR, tức phép toán tiền của cả hệ — có đúng **ba** chỗ để lật, và
#: «1/3 sống sót» ở đó không phải bằng chứng về độ phủ: nó là bằng chứng
#: rằng cái thước không có gì để đo. Cùng một bệnh với «phiếu N/N đạt»
#: mà chính bộ quét này sinh ra để chữa, chỉ là ở tầng công cụ.
#:
#: Vì sao KHÔNG bật mặc định: lật số học đẻ ra nhiều con chết vì
#: `ZeroDivisionError` hay `TypeError` — chúng «chết» mà không nói gì về
#: phép kiểm, và chúng làm chậm lượt quét lên nhiều lần. Dùng nó cho
#: những mô-đun TÍNH TIỀN, đừng rải khắp cây.
DOI_SO_HOC = [(" * ", " / "), (" / ", " * "), (" + ", " - "), (" - ", " + ")]
if SO_HOC:
    DOI = DOI + DOI_SO_HOC

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
    # CẮT CHÚ THÍCH sau khi đã bỏ chuỗi. Thứ tự bắt buộc: `#` nằm trong
    # một chuỗi không phải chú thích, và `_bo_chuoi` đã dọn chuỗi rồi nên
    # dấu `#` còn lại là chú thích thật.
    #
    # Không có bước này thì `phiDoiUsd: float   # phí ra + phí vào` bị
    # đếm là một phép CỘNG — đổi nó chỉ đổi CHỮ, nên con ấy luôn sống
    # sót và luôn vô nghĩa, y hệt hai cái bẫy chuỗi đã vá ở trên. Nó lộ
    # ra ngay lượt đầu chạy `--so-hoc`, và nó nằm ở dòng ĐẦU danh sách
    # phải đọc.
    sach = _bo_chuoi(d).split("#", 1)[0]
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


if not _ghi(SAO_LUU, goc):
    print(f"  DỪNG: không ghi nổi bản sao lưu {SAO_LUU} — không quét khi "
          f"chưa có đường lùi.")
    sys.exit(3)

print(f"  {len(ca)} chỗ đem đột biến trong {F}")
song = []
for i, moi, nhan in ca:
    ds = list(dong)
    ds[i] = moi
    if not _ghi(F, "".join(ds)):
        print(f"  DỪNG ở dòng {i + 1}: không ghi nổi bản đột biến.")
        _tra_lai()
        sys.exit(4)
    try:
        r, out = _chay()
    finally:
        if not _tra_lai():
            sys.exit(5)
    bat = "✗" in out or r.returncode != 0
    if not bat:
        song.append((i + 1, nhan, dong[i].strip()[:78]))

# Dọn bản sao lưu CHỈ khi đã trả lại xong xuôi. File ấy còn nằm đó nghĩa
# là lần quét trước chết giữa chừng.
try:
    os.remove(SAO_LUU)
except OSError:
    pass

print(f"  SỐNG SÓT {len(song)}/{len(ca)}")
for ln, nhan, txt in song:
    print(f"    dòng {ln:>4}  [{nhan}]  {txt}")
