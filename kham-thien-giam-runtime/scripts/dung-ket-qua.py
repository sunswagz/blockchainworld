"""Dựng lại KẾT QUẢ cho mọi khung đã ghi trong băng — chỉ cần Binance.

    python scripts/dung-ket-qua.py            # dựng, ghi vào data/ket-qua.jsonl
    python scripts/dung-ket-qua.py --thu      # chỉ đếm, không ghi

Băng ghi khung hình lúc nó đang diễn ra, nên không có kết quả. Kết quả
mãi năm phút sau mới biết, và lúc đó dòng băng đã nằm trong một file gzip
đã đóng.

Nhưng kết quả một khung Up/Down là `giá đóng khung > giá mở khung`, mà:

    giaMo   — băng đã ghi sẵn
    giaDong — nến 1 phút của Binance tại lúc khung kết thúc
    lúc kết thúc — đọc từ ĐUÔI SLUG (`btc-updown-5m-1787243400`)

Cả ba đều không cần Polymarket. Nên toàn bộ băng ghi được suốt tuần qua
vẫn dựng lại được, dù suốt thời gian đó chưa một lệnh nào được đặt và
đường tới sàn thì đang đứt.

Đây là thứ mở khoá cho `chay_lai` chấm được điểm, và qua đó mở khoá cổng
của vòng tiến hoá — cái cổng từ trước tới nay chưa từng có gì để so.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402  (đặt lại bảng mã console)
from kham.bang import BaoCaoDoc, lan_luot  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.ket_qua import SoKetQua, ket_thuc_tu_slug  # noqa: E402
from kham.nguon import nguon  # noqa: E402

THU = "--thu" in sys.argv
NEN = {t["ma"]: t.get("nen") for t in CONFIG["thiTruong"]}
SONG = {t["ma"]: float(t.get("phutSong", 5)) * 60.0 for t in CONFIG["thiTruong"]}


def main() -> int:
    so = SoKetQua()
    print(f"\n  Sổ kết quả hiện có: {so.tom_tat()}")

    # Quét băng theo DÒNG chứ không nạp cả vào bộ nhớ: băng đã 29 MB và
    # còn dày lên mỗi ngày; nạp hết vào RAM là một cái bẫy chờ sẵn.
    print("  Quét băng…")
    bao = BaoCaoDoc()
    khung: dict[str, dict] = {}
    soDong = 0
    for k in lan_luot(None, bao):
        soDong += 1
        for tt in (k.get("thiTruong") or []):
            slug, ma = tt.get("slug"), tt.get("ma")
            mo = tt.get("giaMo")
            if not slug or not ma or not isinstance(mo, (int, float)):
                continue
            # Giữ bản ghi ĐẦU TIÊN thấy: `giaMo` là hằng số của khung, nên
            # bản nào cũng như nhau, nhưng lấy bản đầu thì kết quả không
            # phụ thuộc thứ tự đọc file.
            khung.setdefault(slug, {"slug": slug, "ma": ma, "giaMo": float(mo)})

    print(f"  {soDong} khung hình · {len(khung)} slug khác nhau")
    print(f"  băng: {bao.soFile} file, {bao.soFileHong} hỏng, "
          f"{bao.soFileCutDuoi} cụt đuôi, bỏ {bao.soByteBoQua} byte")

    can = [v for s, v in khung.items() if so.lay(s) is None]
    print(f"  cần dựng: {len(can)} (đã có {len(khung) - len(can)})")
    if THU:
        print("\n  --thu: dừng ở đây, không ghi gì.\n")
        return 0
    if not can:
        print("\n  Không có gì để dựng.\n")
        return 0

    xong = bo = 0
    t0 = time.time()
    for i, v in enumerate(sorted(can, key=lambda x: x["slug"]), 1):
        cap = NEN.get(v["ma"])
        het = ket_thuc_tu_slug(v["slug"], SONG.get(v["ma"], 300.0))
        if not cap or het is None:
            bo += 1
            continue
        # Khung chưa kết thúc thì CHƯA có kết quả — đừng hỏi, và đừng ghi.
        if het > time.time() * 1000.0:
            bo += 1
            continue
        dong = nguon.gia_dong_khung(cap, het)
        if dong is None or abs(dong - v["giaMo"]) < 1e-9:
            # Bằng nhau thì luật kết toán của sàn quyết, mình đừng đoán.
            bo += 1
            continue
        so.them(v["slug"], dong > v["giaMo"], v["giaMo"], dong, "tu-tinh")
        xong += 1
        if i % 50 == 0:
            print(f"    {i}/{len(can)} · dựng {xong} · bỏ {bo} "
                  f"· {time.time()-t0:.0f}s")

    print(f"\n  Dựng xong {xong} kết quả, bỏ {bo}.")
    print(f"  Sổ kết quả nay: {so.tom_tat()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
