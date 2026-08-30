"""Đường nắn CHUNG cho bốn chợ, hay bốn đường RIÊNG? Đo NGOÀI MẪU.

    python scripts/do-nan-chung-hay-rieng.py

`dinh_gia` áp một sổ hiệu chỉnh DUY NHẤT cho cả bốn chợ. Câu ấy chưa
bao giờ được kiểm — trước hôm nay sổ thô chỉ có MỘT chợ, nên không có
gì để so.

Chia 70/30 theo THỨ TỰ trong sổ thô (mỗi chợ ghi liền mạch theo thời
gian), khớp trên 70 đầu, chấm trên 30 đuôi. Chấm bằng SAI SỐ HIỆU CHỈNH
tuyệt đối theo ô — cùng thước mà `hoc-tu-binance` dùng.

## Kết quả 30/08/2026 — 228.156 mẫu, bốn chợ

    chợ        ngoài mẫu     THÔ   nắn RIÊNG   nắn CHUNG   ai hơn
    BTC_5M        17.260   3,312c      1,804c      1,608c   CHUNG
    ETH_5M        17.261   3,846c      2,115c      2,180c   RIÊNG
    SOL_5M        16.876   3,016c      1,233c      1,147c   CHUNG
    XRP_5M        17.051   3,086c      1,395c      1,411c   RIÊNG

    gộp bốn chợ   68.448               1,640c      1,590c

Đường CHUNG nhỉnh hơn (1,590c so với 1,640c) và thắng 2/4 chợ. Chênh
lệch nhỏ và chia đều hai phía, nên đây KHÔNG phải bằng chứng đường
chung tốt hơn — nó là bằng chứng **không có cớ để tách ra**. Tách thành
bốn là chia mẫu cho bốn, và bốn phép khớp trên mẫu nhỏ hơn thì mỗi cái
nhiễu hơn. Giữ nguyên một sổ, nay có số đỡ chứ không phải mặc định.

Con số đáng chú ý hơn nằm ở cột THÔ: 3,0–3,8c ngoài mẫu, nắn xuống
1,1–2,2c. Phép nắn có tác dụng thật, và đây là ngoài mẫu chứ không
phải tự chấm bài mình.

Chạy ở đâu có DỮ LIỆU: script đọc `data/hieu-chinh-tho.jsonl` của thư
mục hiện hành. Chạy trong một worktree chỉ có mẫu BTC thì nó báo "hoà"
trên đúng một chợ, và câu ấy không trả lời gì cả.
"""
import collections
import json
import sys

sys.path.insert(0, ".")

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

# Không nhận cờ nào, nhưng vẫn khai qua `tham_so.doc`: đó là chỗ DUY
# NHẤT biết một cờ có thật hay không, nên script nào bỏ qua nó thì gõ
# sai cờ sẽ bị NUỐT LẶNG thay vì báo lỗi. Và nó cho `--help` miễn phí.
tham_so.doc({}, ten='do-nan-chung-hay-rieng.py')
from kham.dinh_gia import HieuChinh
from kham.nan_lai import DUONG_THO, khop

theo = collections.defaultdict(list)
for d in DUONG_THO.read_text(encoding="utf-8").splitlines():
    if not d.strip():
        continue
    try:
        g = json.loads(d)
        theo[str(g.get("ma") or "?")].append((float(g["p"]), bool(g["thang"])))
    except (ValueError, KeyError, TypeError):
        pass

def so_moi(cap):
    hc = HieuChinh(duong=None); hc.o = {}
    for p, t in cap:
        hc.them(p, t)
    return hc

def sai(pn, cap):
    """Sai số hiệu chỉnh tuyệt đối trung bình theo ô, SAU khi nắn."""
    hc = HieuChinh(duong=None); hc.o = {}
    for p, t in cap:
        hc.them(pn.nan(p) if pn is not None and pn.dung_duoc else p, t)
    tong = n = 0.0
    for _k, d in (hc.o or {}).items():
        m = int(d.get("n", 0))
        if m < 30:
            continue
        tong += abs(d["tongP"] / m - d["thang"] / m) * m
        n += m
    return (tong / n) if n else float("nan")

cho = sorted(theo)
hoc_gop, chot = [], {}
for m in cho:
    c = theo[m]
    k = int(len(c) * 0.7)
    hoc_gop += c[:k]
    chot[m] = c[k:]

pn_gop = khop(so_moi(hoc_gop))
print()
print(f"  Đường CHUNG khớp trên {len(hoc_gop):,} mẫu · dùng được {pn_gop.dung_duoc}")
print()
print(f"  {'chợ':10} {'ngoài mẫu':>10} {'THÔ':>9} {'nắn RIÊNG':>11} {'nắn CHUNG':>11}   ai hơn")
tong_r = tong_c = tong_n = 0.0
for m in cho:
    c = theo[m]; k = int(len(c) * 0.7)
    pn_r = khop(so_moi(c[:k]))
    s_tho = sai(None, chot[m])
    s_r = sai(pn_r, chot[m])
    s_c = sai(pn_gop, chot[m])
    n = len(chot[m])
    tong_n += n; tong_r += s_r * n; tong_c += s_c * n
    ai = "RIÊNG" if s_r < s_c else ("CHUNG" if s_c < s_r else "hoà")
    print(f"  {m:10} {n:>10,} {s_tho*100:>8.3f}c {s_r*100:>10.3f}c "
          f"{s_c*100:>10.3f}c   {ai}")
print()
print(f"  {'gộp bốn chợ':10} {tong_n:>10,.0f} {'':>9} "
      f"{tong_r/tong_n*100:>10.3f}c {tong_c/tong_n*100:>10.3f}c")
print()
