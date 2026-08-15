"""Sinh 5 icon PNG cho cung Tử Cấm Thành.

    python scripts/sinh-icon.py

Vẽ bằng Pillow chứ không chép của cung khác: hai cung dùng chung icon thì trên
màn hình chờ điện thoại chúng là một, và người dùng bấm nhầm mãi mà không hiểu
vì sao. Motif: cổng Ngọ Môn — ba vòm cửa dưới một mái, trên nền son đỏ tường thành.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

SON = (200, 69, 60)        # #C8453C — son đỏ tường thành
SON_TOI = (138, 42, 36)
NEN = (14, 17, 22)         # #0E1116 — nền chung của mọi cung
VANG = (201, 162, 39)      # #C9A227 — ngói lưu ly

OUT = Path(__file__).resolve().parent.parent.parent / "tu-cam-thanh" / "assets" / "icons"


def ve(size: int, nen: tuple | None, vien_pct: float = 0.0) -> Image.Image:
    """Vẽ ở 4× rồi thu nhỏ — khử răng cưa mà không cần antialias thủ công."""
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if nen:
        r = int(S * 0.22)
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=nen)

    # vùng an toàn cho icon maskable: co hình vào trong
    m = S * (0.28 if vien_pct else 0.18)
    w = S - 2 * m
    x0, y0 = m, m

    # mái ngói: hình thang
    mai_h = w * 0.20
    d.polygon(
        [(x0 - w * 0.06, y0 + mai_h), (x0 + w * 0.20, y0),
         (x0 + w * 0.80, y0), (x0 + w * 1.06, y0 + mai_h)],
        fill=VANG,
    )

    # thân thành
    than_y = y0 + mai_h + w * 0.04
    d.rounded_rectangle(
        [x0, than_y, x0 + w, y0 + w],
        radius=int(w * 0.04), fill=SON,
    )

    # ba vòm cửa — cửa giữa cao hơn, đúng lệ Ngọ Môn
    day = y0 + w
    for i, (cx, rong, cao) in enumerate((
        (0.22, 0.13, 0.38),
        (0.50, 0.17, 0.52),
        (0.78, 0.13, 0.38),
    )):
        cw = w * rong
        ch = w * cao
        left = x0 + w * cx - cw / 2
        top = day - ch
        d.rounded_rectangle([left, top, left + cw, day], radius=int(cw / 2), fill=NEN)
        d.rectangle([left, top + cw / 2, left + cw, day], fill=NEN)

    # đường bệ dưới chân thành
    d.rectangle([x0 - w * 0.03, day - w * 0.045, x0 + w * 1.03, day], fill=SON_TOI)

    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    lam = [
        ("icon-192.png", 192, NEN, 0.0),
        ("icon-512.png", 512, NEN, 0.0),
        ("icon-maskable-512.png", 512, NEN, 1.0),   # co vào trong vùng an toàn
        ("apple-touch-icon.png", 180, NEN, 0.0),
        ("favicon-32.png", 32, NEN, 0.0),
    ]
    for ten, size, nen, vien in lam:
        ve(size, nen, vien).save(OUT / ten, "PNG", optimize=True)
        print(f"  {ten}  {size}×{size}")
    print(f"\nđã ghi {len(lam)} icon vào {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
