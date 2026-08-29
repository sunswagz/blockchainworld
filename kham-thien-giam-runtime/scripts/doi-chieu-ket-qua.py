r"""Sổ kết quả có đúng không? Tính lại từ nến Binance LẤY MỚI rồi so.

    python scripts/doi-chieu-ket-qua.py --ngay=7

## Vì sao cần

Sổ kết quả là NỀN của mọi thứ: Brier, điểm kỹ năng, phép nắn, cổng tiến
hoá, chạy lại — tất cả tra sổ này để biết khung nào thắng. Sai một dòng ở
đây là sai mọi con số phía sau, và sai im lặng.

Mà đo được: **100% dòng trong sổ có nguồn `tu-tinh`** — tự tính bằng cách
so giá Binance ở hai mốc, chưa dòng nào do sàn xác nhận. Toàn bộ hệ đứng
trên một sự thật do chính mình tính ra.

## Phép này kiểm được gì, và KHÔNG kiểm được gì

KIỂM ĐƯỢC: dòng ghi trong sổ có tái lập được không. Lúc ghi, giá lấy từ
một mẫu ở thời điểm ấy — có thể là mẫu lỗi, mẫu trễ, hay một nến chưa
đóng. Lấy nến mới hôm nay rồi tính lại thì mọi chuyện đó lộ ra.

KHÔNG KIỂM ĐƯỢC: **quy ước của SÀN**. Nếu Polymarket kết toán bằng một
nguồn giá khác, hay lấy mốc khác một giây, thì phép này vẫn báo "khớp
100%" trong khi cả sổ sai. Câu ấy chỉ trả lời được bằng cách hỏi sàn, và
nó nằm trong danh sách PHẢI ĐÚNG TRƯỚC KHI MỞ BA CỔNG.

Nói cách khác: đây là phép kiểm TÍNH NHẤT QUÁN, không phải phép kiểm tính
đúng. Biết rõ nó kiểm được gì mới dùng nó đúng.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

N = chr(10)
GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "ma": "mã thị trường, ví dụ BTC_5M",
    "ngay": "chỉ đối chiếu khung trong ngần này ngày gần nhất",
}, ten='doi-chieu-ket-qua.py')

from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.ket_qua import moc_tu_slug  # noqa: E402
from kham.nguon import nguon  # noqa: E402

PHUT = 60_000.0
MA = CO.lay("ma", "BTC_5M")
SO_NGAY = float(CO.lay("ngay", "7"))


def nen_1p(cap: str, tuMs: float, soNen: int) -> dict:
    """{mốc đóng ms: giá đóng}."""
    moc = int(tuMs // PHUT * PHUT)
    ra: dict = {}
    con = soNen
    while con > 0:
        lo = min(1000, con)
        d = nguon._lay("binance-kline",
                       CONFIG["nguon"]["binanceSpot"] + "/api/v3/klines",
                       {"symbol": cap, "interval": "1m",
                        "startTime": moc, "limit": lo})
        if not isinstance(d, list) or not d:
            break
        for n in d:
            try:
                ra[int(n[0]) + int(PHUT)] = float(n[4])
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


def main() -> int:
    tt = next((t for t in CONFIG["thiTruong"] if t.get("ma") == MA), None)
    if not tt:
        print(N + "  Không có market `" + MA + "`." + N)
        return 1
    cap = tt.get("nen")
    tienTo = (tt.get("tienTo") or "").rstrip("-")
    song = float(tt.get("phutSong", 5)) * 60.0

    f = DATA_DIR / "ket-qua.jsonl"
    if not f.exists():
        print(N + "  Chưa có sổ kết quả." + N)
        return 1

    print()
    print("=" * 76)
    print("  ĐỐI CHIẾU SỔ KẾT QUẢ với nến Binance lấy mới")
    print("=" * 76)
    print("  " + MA + " (" + str(cap) + ") · tiền tố `" + tienTo
          + "` · khung " + format(song / 60.0, "g") + " phút")

    han = time.time() * 1000.0 - SO_NGAY * 86400_000.0
    ds = []
    for dong in f.read_text(encoding="utf-8").splitlines():
        if not dong.strip():
            continue
        try:
            d = json.loads(dong)
        except ValueError:
            continue
        s = d.get("slug") or ""
        if tienTo and not s.startswith(tienTo):
            continue
        m = moc_tu_slug(s)
        if m is None or m < han:
            continue
        ds.append((m, d))
    ds.sort(key=lambda x: x[0])
    if len(ds) < 10:
        print("  chỉ có " + str(len(ds)) + " khung trong hạn — không đủ." + N)
        return 1

    som, muon = ds[0][0], ds[-1][0]
    tong = int((muon - som) / PHUT) + int(song / 60.0) + 20
    print("  " + format(len(ds), ",") + " khung trong sổ · lấy "
          + format(tong, ",") + " nến…", flush=True)
    oh = nen_1p(cap, som - PHUT, tong)
    print("  lấy được " + format(len(oh), ",") + " nến")

    khop = lech = thieu = hoa = 0
    viDu = []
    for m, d in ds:
        a = oh.get(int(m))
        b = oh.get(int(m) + int(song * 1000.0))
        if a is None or b is None:
            thieu += 1
            continue
        if abs(b - a) < 1e-12:
            # Hoà tuyệt đối: sàn có quy ước riêng cho ca này, ta KHÔNG
            # đoán. Đếm riêng chứ không tính là lệch.
            hoa += 1
            continue
        moi = b > a
        if moi == bool(d.get("upThang")):
            khop += 1
        else:
            lech += 1
            if len(viDu) < 5:
                viDu.append((d.get("slug"), d.get("upThang"), moi, a, b))

    # MỘT dòng máy đọc được, in trước phần cho người đọc.
    #
    # `kham-suc-khoe.py` từng phải dò văn xuôi để lấy mấy con số này, và
    # nó bắt nhầm ngay lần chạy đầu: câu cảnh báo *"vẫn báo khớp 100%
    # trong khi cả sổ sai"* bị xuống dòng thành một dòng bắt đầu bằng
    # "khớp", và trang khám in câu ấy vào chỗ đáng lẽ là một con số.
    #
    # Dò văn xuôi khéo hơn không phải cách chữa. Cách chữa là cho công cụ
    # NÓI một dòng dành cho máy — chữ cho người, số cho máy, tách hẳn.
    print()
    print(f"KETLUAN khop={khop} lech={lech} hoa={hoa} thieu={thieu}")
    print("    khớp        " + format(khop, ">8,"))
    print("    LỆCH        " + format(lech, ">8,")
          + ("   ← mỗi dòng ở đây là một con số sai chảy vào mọi phép chấm"
             if lech else ""))
    print("    hoà tuyệt đối " + format(hoa, ">6,")
          + "   (không đoán — sàn có quy ước riêng)")
    print("    thiếu nến   " + format(thieu, ">8,"))
    for s, cu, moi, a, b in viDu:
        print("      " + str(s) + ": sổ ghi " + str(cu) + " · tính lại "
              + str(moi) + " · " + format(a, ",.2f") + " → "
              + format(b, ",.2f"))

    print()
    if lech:
        print("  SỔ CÓ DÒNG SAI. Mọi điểm Brier, điểm kỹ năng và kết luận")
        print("  tiến hoá dựng trên quãng này đều phải đo lại sau khi sửa.")
    elif khop:
        print("  Sổ TÁI LẬP ĐƯỢC hoàn toàn trên quãng đã kiểm.")
        print()
        print("  Nhắc lại giới hạn của phép này: nó kiểm TÍNH NHẤT QUÁN,")
        print("  không kiểm tính ĐÚNG. Nếu quy ước kết toán của sàn khác ta")
        print("  — nguồn giá khác, mốc lệch một giây — thì phép này vẫn báo")
        print("  khớp 100% trong khi cả sổ sai. Câu ấy chỉ hỏi sàn mới ra.")
    print()
    return 2 if lech else 0


if __name__ == "__main__":
    raise SystemExit(main())
