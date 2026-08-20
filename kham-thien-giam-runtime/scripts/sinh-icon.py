"""Sinh 5 icon PNG cho cung Khâm Thiên Giám.

    python scripts/sinh-icon.py

Vẽ bằng Pillow chứ không chép của cung khác: hai cung dùng chung icon thì trên
màn hình chờ điện thoại chúng là một, và người dùng bấm nhầm mãi mà không hiểu
vì sao.

Motif: **hỗn thiên nghi** — quả cầu vòng, khí cụ chính của Khâm Thiên Giám để
đo vị trí tinh tú. Một vòng ngoài (tí ngọ), một vòng nghiêng (hoàng đạo), một
lõi sáng ở giữa. Nền xanh thiên văn #7FB2E8 trên nền chung #07090D.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import chỉ để lấy lớp ép UTF-8 trong `kham/__init__.py`, không dùng gì khác.
# Console Windows mặc định cp1252 và sẽ ném UnicodeEncodeError ở dòng print
# cuối — đúng sau khi đã ghi xong cả 5 icon, nên thoát khác 0 trong khi việc
# đã xong. Script nào in tiếng Việt cũng phải đi qua đây.
import kham  # noqa: F401

from PIL import Image, ImageDraw

LAM = (127, 178, 232)       # #7FB2E8 — xanh thiên văn, màu hiệu của cung
LAM_TOI = (58, 96, 143)
NEN = (7, 9, 13)            # #07090D — nền của cung
VANG = (232, 163, 61)       # #E8A33D — sao ở tâm

OUT = Path(__file__).resolve().parent.parent.parent / "kham-thien-giam" / "assets" / "icons"


def _ellipse_nghieng(d, cx, cy, r, nghieng, day, mau):
    """Vẽ một vòng tròn nhìn nghiêng — ellipse xoay quanh tâm.

    Pillow không xoay ellipse được, nên vẽ bằng đa giác 96 điểm. Đủ mượt ở
    mức 4x rồi thu nhỏ, và không phải thêm phụ thuộc nào.
    """
    goc = math.radians(nghieng)
    cos_g, sin_g = math.cos(goc), math.sin(goc)
    diem = []
    for i in range(97):
        t = 2 * math.pi * i / 96
        x, y = r * math.cos(t), r * 0.34 * math.sin(t)
        diem.append((cx + x * cos_g - y * sin_g, cy + x * sin_g + y * cos_g))
    d.line(diem, fill=mau, width=day, joint="curve")


def ve(size: int, nen: tuple | None, maskable: bool = False) -> Image.Image:
    """Vẽ ở 4x rồi thu nhỏ — khử răng cưa mà không cần antialias thủ công."""
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if nen:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=nen)

    # Vùng an toàn cho icon maskable: hệ điều hành có thể cắt tới 20% mỗi
    # cạnh, nên hình phải co vào trong nhiều hơn.
    m = S * (0.30 if maskable else 0.19)
    cx = cy = S / 2
    r = (S - 2 * m) / 2
    day = max(2, int(S * 0.030))

    # vòng ngoài — kinh tuyến tí ngọ, đứng thẳng
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LAM, width=day)

    # vòng xích đạo — nằm ngang, nhìn nghiêng
    _ellipse_nghieng(d, cx, cy, r * 0.98, 0, day, LAM_TOI)

    # vòng hoàng đạo — nghiêng 23,5 độ, đúng độ nghiêng trục Trái Đất
    _ellipse_nghieng(d, cx, cy, r * 0.98, 23.5, day, LAM)

    # trục cực
    d.line([(cx, cy - r * 1.06), (cx, cy + r * 1.06)], fill=LAM_TOI,
           width=max(1, int(day * 0.62)))

    # sao ở tâm
    rs = r * 0.15
    d.ellipse([cx - rs, cy - rs, cx + rs, cy + rs], fill=VANG)

    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    if not OUT.parent.parent.joinpath("index.html").exists():
        print(f"Không thấy cung ở {OUT.parent.parent} — chạy từ trong repo.")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    bo = [
        ("icon-192.png", 192, NEN, False),
        ("icon-512.png", 512, NEN, False),
        ("icon-maskable-512.png", 512, NEN, True),
        ("apple-touch-icon.png", 180, NEN, False),
        ("favicon-32.png", 32, NEN, False),
    ]
    for ten, kich, nen, mask in bo:
        img = ve(kich, nen, mask)
        # PNG nền đục: nhỏ hơn, và mọi icon ở đây đều có nền nên không mất gì
        img.convert("RGB").save(OUT / ten, "PNG", optimize=True)
        print(f"  {ten:26s} {kich}x{kich}")
    print(f"Đã ghi 5 icon vào {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
