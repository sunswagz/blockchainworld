"""Sinh 5 icon PNG cho cung Thị Bạc Ty.

    python scripts/sinh-icon.py

Vẽ bằng Pillow chứ không chép của cung khác: hai cung dùng chung icon thì trên
màn hình chờ điện thoại chúng là một, và người dùng bấm nhầm mãi mà không hiểu
vì sao.

Motif: **cân thương bạc trên sóng** — đòn cân của ty thị bạc, hai đĩa lệch nhau
đúng một nấc (chênh lệch giữa hai cảng), đặt trên ba lằn sóng. Màu hiệu #D9A441
(vàng đồng cân) trên nền chung #07090D.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import chỉ để lấy lớp ép UTF-8 trong `bac/__init__.py`. Console Windows mặc
# định cp1252 và sẽ ném UnicodeEncodeError ở dòng print cuối — đúng SAU khi đã
# ghi xong cả 5 icon, nên thoát khác 0 trong khi việc đã xong.
import bac  # noqa: F401

from PIL import Image, ImageDraw

VANG = (217, 164, 65)          # #D9A441 — vàng đồng cân, màu hiệu của cung
VANG_MO = (140, 106, 42)
NEN = (7, 9, 13)               # #07090D — nền chung cả site
LAM = (90, 169, 230)           # sóng

RA = Path(__file__).resolve().parent.parent.parent / "thi-bac-ty" / "assets" / "icons"


def ve(canh: int, dem_le: float = 0.14) -> Image.Image:
    """Một icon vuông cạnh `canh`. `dem_le` là phần lề chừa cho maskable."""
    # Vẽ ở 4× rồi thu nhỏ: Pillow không có khử răng cưa cho đường thẳng, nên
    # đây là cách rẻ nhất để cạnh không bị răng. Bỏ bước này thì icon 192px
    # trông sắc nét ở chỗ dày và rách ở chỗ mảnh.
    S = canh * 4
    im = Image.new("RGB", (S, S), NEN)
    d = ImageDraw.Draw(im)

    m = S * dem_le                     # lề
    w = S - 2 * m                      # bề rộng dùng được
    cx = S / 2
    day = max(2.0, w * 0.035)          # bề dày nét

    # ── ba lằn sóng dưới đáy ─────────────────────────────────────────────
    for i in range(3):
        y = m + w * (0.78 + i * 0.085)
        buoc = w / 4.0
        diem = []
        x = m
        while x <= m + w:
            diem.append((x, y))
            x += buoc / 8.0
        # sóng hình sin thô bằng tay — không cần math, chỉ cần gợn
        song = []
        for j, (px, py) in enumerate(diem):
            lech = (1 if (j // 4) % 2 == 0 else -1) * (w * 0.012)
            song.append((px, py + lech))
        d.line(song, fill=LAM if i == 0 else VANG_MO,
               width=int(day * 0.7), joint="curve")

    # ── trụ cân ──────────────────────────────────────────────────────────
    dinh = m + w * 0.10
    day_tru = m + w * 0.72
    d.line([(cx, dinh), (cx, day_tru)], fill=VANG, width=int(day))
    d.line([(cx - w * 0.13, day_tru), (cx + w * 0.13, day_tru)],
           fill=VANG, width=int(day))

    # ── đòn cân LỆCH — chênh lệch giữa hai cảng, đó là cả ý của cung ─────
    trai_y = dinh + w * 0.10
    phai_y = dinh + w * 0.02
    tx, px_ = cx - w * 0.34, cx + w * 0.34
    d.line([(tx, trai_y), (px_, phai_y)], fill=VANG, width=int(day))
    d.ellipse([cx - day, dinh - day, cx + day, dinh + day], fill=VANG)

    # ── hai đĩa treo ─────────────────────────────────────────────────────
    for x, y, r in ((tx, trai_y, w * 0.115), (px_, phai_y, w * 0.115)):
        treo = y + w * 0.13
        d.line([(x, y), (x, treo)], fill=VANG_MO, width=int(day * 0.6))
        d.arc([x - r, treo - r * 0.55, x + r, treo + r * 1.15],
              start=0, end=180, fill=VANG, width=int(day))

    return im.resize((canh, canh), Image.LANCZOS)


def main() -> int:
    RA.mkdir(parents=True, exist_ok=True)
    bo = [
        ("icon-192.png", 192, 0.14),
        ("icon-512.png", 512, 0.14),
        # maskable: hệ điều hành cắt tới 20% mỗi mép, nên chừa lề rộng hơn.
        # Dùng chung lề với icon thường là logo bị gọt mất hai đầu đòn cân.
        ("icon-maskable-512.png", 512, 0.26),
        ("apple-touch-icon.png", 180, 0.14),
        ("favicon-32.png", 32, 0.10),
    ]
    for ten, canh, le in bo:
        ve(canh, le).save(RA / ten, "PNG", optimize=True)
        print(f"  ✓ {ten}  {canh}×{canh}")
    print(f"\nĐã ghi {len(bo)} icon vào {RA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
