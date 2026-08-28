"""Kiểm phép nắn NGOÀI MẪU — phép thử duy nhất phân biệt học với thuộc lòng.

    python scripts/kiem-nan-ngoai-mau.py

Tới giờ phép nắn mới được đo hai cách, và cả hai đều chưa đủ:

1. Trên chính bảng hiệu chỉnh đã sinh ra nó (6,37 → 1,91 điểm). Đường
   khớp từ bảng đó thì tất nhiên khớp với bảng đó — tự chấm bài mình.
2. Chạy lại trên băng (thắng 64,3% → 72,1%). Khá hơn, nhưng băng ấy CŨNG
   là quãng đã sinh ra bảng hiệu chỉnh. Vẫn trong mẫu.

Vì thiếu bằng chứng ngoài mẫu nên phép nắn phải đi kèm giảm chấn 0,7 —
chỉ dám đi bảy phần mười đường. Khiêm tốn đúng chỗ, nhưng có giá.

## Nay kiểm được thật, không cần chờ thêm ngày nào

Sổ kết quả có 2.615 khung; băng có `pUp` của mô hình cho từng khung. Ghép
lại được TỪNG CẶP (mô hình đoán, thực tế ra) — đúng thứ sổ hiệu chỉnh
không lưu, vì nó chỉ giữ tổng theo ô.

Có cặp thô thì chia được theo THỜI GIAN: khớp trên phần đầu, chấm trên
phần đuôi mà đường khớp chưa từng thấy. Chia theo thời gian chứ không
ngẫu nhiên — chợ đổi theo ngày, nên trộn ngày rồi chia là để tương lai rò
rỉ ngược vào quá khứ.

## Đọc kết quả

    sai số phần đuôi GIẢM → học được quy luật, có cớ bỏ bớt giảm chấn
    sai số phần đuôi TĂNG → học thuộc bảng, giữ giảm chấn hoặc bỏ hẳn
    xấp xỉ nhau           → chưa đủ bằng chứng, đừng đổi gì
"""
from __future__ import annotations

import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham.bang import BaoCaoDoc, lan_luot  # noqa: E402
from kham.dinh_gia import o_hieu_chinh  # noqa: E402
from kham.ket_qua import moc_tu_slug, so_ket_qua  # noqa: E402
from kham.nan_lai import PhepNan, khop  # noqa: E402

TY_LE_KHOP = 0.7          # phần đầu để khớp, phần đuôi để chấm


class _SoGia:
    """Sổ hiệu chỉnh dựng từ một tập cặp thô, để `khop()` dùng lại được."""

    def __init__(self, cap):
        self.o: dict[str, dict] = {}
        for p, that in cap:
            d = self.o.setdefault(o_hieu_chinh(p),
                                  {"n": 0, "thang": 0, "tongP": 0.0})
            d["n"] += 1
            d["thang"] += 1 if that else 0
            d["tongP"] += p


def sai_so(pn, cap) -> float:
    """Sai số tuyệt đối trung bình theo Ô, không theo từng cặp.

    Theo từng cặp thì vô nghĩa: thực tế là 0 hoặc 1 còn dự đoán là 0,73 —
    sai số ấy đo ĐỘ KHÓ của bài toán, không đo độ đúng của mô hình. Gom
    theo ô rồi so tần suất mới là thứ hiệu chỉnh nói.
    """
    o: dict[str, list] = {}
    for p, that in cap:
        q = pn.nan(p) if pn is not None else p
        d = o.setdefault(o_hieu_chinh(q), [0, 0, 0.0])
        d[0] += 1
        d[1] += 1 if that else 0
        d[2] += q
    tong = sum(d[0] for d in o.values())
    if not tong:
        return 0.0
    return sum(abs(d[2] / d[0] - d[1] / d[0]) * d[0] for d in o.values()) / tong


def main() -> int:
    print()
    print("  Ghép cặp (mô hình đoán, thực tế ra) từ băng + sổ kết quả…")
    dau: dict = {}
    bao = BaoCaoDoc()
    for k in lan_luot(None, bao):
        for tt in (k.get("thiTruong") or []):
            slug, pm = tt.get("slug"), tt.get("pUp")
            if not slug or not isinstance(pm, (int, float)) or slug in dau:
                continue
            m = moc_tu_slug(slug)
            if m is not None:
                # Bản ghi ĐẦU TIÊN của mỗi khung, khớp với cách sổ hiệu
                # chỉnh vẫn ghi: ý kiến mô hình lúc khung được ghi danh.
                dau[slug] = (m, float(pm))

    cap = [(m, pm, so_ket_qua.lay(s)) for s, (m, pm) in dau.items()]
    cap = [(m, pm, t) for m, pm, t in cap if t is not None]
    cap.sort(key=lambda x: x[0])
    print(f"  {len(dau)} khung có pUp · {len(cap)} khung có CẢ kết quả")
    if len(cap) < 300:
        print("  Chưa đủ cặp để chia đôi cho tử tế. Dừng.")
        return 0

    n = int(len(cap) * TY_LE_KHOP)
    hoc = [(pm, t) for _m, pm, t in cap[:n]]
    thu = [(pm, t) for _m, pm, t in cap[n:]]
    print(f"  chia theo THỜI GIAN: {len(hoc)} khớp · {len(thu)} chấm")

    pn = khop(_SoGia(hoc))
    print(f"  đường nắn khớp trên phần đầu: {pn.tongMau} mẫu · "
          f"dùng được {pn.dung_duoc}")
    if not pn.dung_duoc:
        print("  Không khớp được thì không có gì để chấm.")
        return 0

    print()
    print("  " + "-" * 64)
    for ten, tap in (("phần ĐẦU (đã thấy)", hoc),
                     ("phần ĐUÔI (chưa thấy)", thu)):
        a, b = sai_so(None, tap), sai_so(pn, tap)
        dh = "GIẢM" if b < a else ("TĂNG" if b > a else "bằng")
        print(f"  {ten:24} thô {a*100:5.2f} → nắn {b*100:5.2f} điểm  ({dh})")
    print("  " + "-" * 64)
    print()

    a, b = sai_so(None, thu), sai_so(pn, thu)
    if b < a * 0.9:
        print("  → Phần đuôi KHÁ HƠN rõ rệt. Phép nắn học được quy luật")
        print("    chứ không thuộc bảng. Có cơ sở bỏ bớt giảm chấn.")
    elif b > a:
        print("  → Phần đuôi TỆ ĐI. Đó là thuộc bảng. Giữ giảm chấn,")
        print("    hoặc bỏ hẳn phép nắn.")
    else:
        print("  → Khá hơn nhưng chưa rõ rệt. Chưa đủ cớ đổi gì.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
