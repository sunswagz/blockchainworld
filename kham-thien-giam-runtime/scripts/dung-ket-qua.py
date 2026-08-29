"""Dựng lại KẾT QUẢ cho mọi khung đã ghi trong băng — chỉ cần Binance.

    python scripts/dung-ket-qua.py            # dựng, ghi vào data/ket-qua.jsonl
    python scripts/dung-ket-qua.py --thu      # chỉ đếm, không ghi

## Định nghĩa ĐÚNG, sau khi đo

Slug là `<coin>-updown-5m-T`. Bản đầu của script này chấm:

    UP thắng ⟺ giá(T+300) > giaMo-trong-băng   với giaMo = giá(T−300)

Sai. `scripts/do-strike.py` chấm điểm chính chợ trên ba giả thuyết, mẫu
ngẫu nhiên trải cả băng, đối chứng bằng tỉ lệ nền:

                              tỉ lệ nền   Brier chợ   ĐIỂM KỸ NĂNG
    (A) giá(T+300)>giá(T−300)     48,9%      0,3466       −38,7%
    (B) giá(T+300)>giá(T)         49,1%      0,2333        +6,6%
    (C) giá(T)    >giá(T−300)     50,1%      0,4177       −67,1%

Chỉ (B) có kỹ năng dương, khoảng tin 95% có cặp [+0,066, +0,163].
**Strike là giá lúc T.** Nên nay:

    UP thắng ⟺ giá(T+300) > giá(T),  cả hai lấy từ nến 1 phút Binance

Không đọc `giaMo` của băng nữa: trường ấy là giá lúc T−300 và nó KHÔNG
phải strike. Đọc nó vào đây chính là cách sai cũ lọt qua.

## Vì sao phải cất bản cũ đi thay vì đè

Sổ cũ 2.615 dòng dựng trên (A), và mọi thứ ăn theo nó — bảng hiệu chỉnh,
đường nắn, kỳ vọng của cổng tiến hoá, lãi lỗ của phiên phát lại — đều
lệch theo. Cất nó lại `ket-qua-dinh-nghia-A.jsonl` để còn đối chiếu được
hai đời sổ; xoá là mất luôn khả năng kiểm lại chính kết luận này.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402  (đặt lại bảng mã console)
from kham.bang import BaoCaoDoc, lan_luot  # noqa: E402
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.ket_qua import SoKetQua, moc_tu_slug  # noqa: E402
from kham.nguon import nguon  # noqa: E402

THU = "--thu" in sys.argv
NEN = {t["ma"]: t.get("nen") for t in CONFIG["thiTruong"]}
SONG = {t["ma"]: float(t.get("phutSong", 5)) * 60.0 for t in CONFIG["thiTruong"]}


def main() -> int:
    duong = DATA_DIR / "ket-qua.jsonl"
    cu = DATA_DIR / "ket-qua-dinh-nghia-A.jsonl"
    if duong.exists() and not cu.exists() and not THU:
        duong.rename(cu)
        print(f"\n  Cất sổ cũ (định nghĩa A) sang {cu.name}")

    so = SoKetQua(duong)
    print(f"\n  Sổ kết quả hiện có: {so.tom_tat()}")

    # Quét băng theo DÒNG chứ không nạp cả vào bộ nhớ. Chỉ cần SLUG và MÃ
    # — `giaMo` của băng không còn được dùng, vì nó là giá lúc T−300 chứ
    # không phải strike.
    print("  Quét băng lấy slug…")
    bao = BaoCaoDoc()
    khung: dict[str, str] = {}
    soDong = 0
    for k in lan_luot(None, bao):
        soDong += 1
        for tt in (k.get("thiTruong") or []):
            slug, ma = tt.get("slug"), tt.get("ma")
            if slug and ma:
                khung.setdefault(slug, ma)

    print(f"  {soDong} khung hình · {len(khung)} slug khác nhau")
    print(f"  băng: {bao.soFile} file, {bao.soFileHong} hỏng, "
          f"{bao.soFileCutDuoi} cụt đuôi, bỏ {bao.soByteBoQua} byte")

    can = [(s, m) for s, m in khung.items() if so.lay(s) is None]
    print(f"  cần dựng: {len(can)} (đã có {len(khung) - len(can)})")
    if THU:
        print("\n  --thu: dừng ở đây, không ghi gì.\n")
        return 0
    if not can:
        print("\n  Không có gì để dựng.\n")
        return 0

    xong = bo = 0
    t0 = time.time()
    for i, (slug, ma) in enumerate(sorted(can), 1):
        cap = NEN.get(ma)
        T = moc_tu_slug(slug)
        if not cap or T is None:
            bo += 1
            continue
        het = T + SONG.get(ma, 300.0) * 1000.0
        # Khung chưa kết thúc thì CHƯA có kết quả — đừng hỏi, đừng ghi.
        if het > time.time() * 1000.0:
            bo += 1
            continue
        mo = nguon.gia_dong_khung(cap, float(T))        # STRIKE THẬT
        dong = nguon.gia_dong_khung(cap, het)
        if mo is None or dong is None or abs(dong - mo) < 1e-9:
            # Bằng nhau thì luật kết toán của sàn quyết, mình đừng đoán.
            bo += 1
            continue
        so.them(slug, dong > mo, mo, dong, "tu-tinh")
        xong += 1
        if i % 50 == 0:
            print(f"    {i}/{len(can)} · dựng {xong} · bỏ {bo} "
                  f"· {time.time()-t0:.0f}s", flush=True)

    print(f"\n  Dựng xong {xong} kết quả, bỏ {bo}.")
    print(f"  Sổ kết quả nay: {so.tom_tat()}")
    print("\n  NHẮC: sổ hiệu chỉnh `hieu-chinh.json` vẫn là bảng dựng trên")
    print("  định nghĩa CŨ. Nó phải được dựng lại hoặc bỏ đi — mọi thứ ăn")
    print("  theo nó (đường nắn, Kelly, chẩn đoán) đang nói về một câu hỏi")
    print("  khác.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
