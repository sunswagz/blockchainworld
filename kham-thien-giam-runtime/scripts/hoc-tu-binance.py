"""Dựng SỔ HIỆU CHỈNH cho mô hình — chỉ cần Binance, không cần chợ.

    python scripts/hoc-tu-binance.py                 # 3 ngày gần nhất
    python scripts/hoc-tu-binance.py --ngay=14
    python scripts/hoc-tu-binance.py --thu           # đo, không ghi

## Vì sao làm được, và vì sao trước đây không ai nghĩ tới

Cỗ máy này đang trống rỗng: chợ bị chặn ở tầng TLS nên không thấy market
nào, sổ kết toán 0 dòng, sổ hiệu chỉnh 0 mẫu, vòng tiến hoá đứng yên vì
"thiếu mẫu". Nghe như phải chờ mạng thông mới học được gì.

Nhưng tách hai câu hỏi ra thì chúng cần hai thứ khác nhau:

    "mô hình đoán đúng chưa?"   cần (S, K, τ, σ) và KẾT QUẢ
    "có tiền không?"            cần thêm GIÁ CHỢ và sổ lệnh

Câu đầu **không cần chợ một chút nào**. `P(UP) = Φ(z)` với
`z = [ln(S/K) − σ²τ/2]/(σ√τ)`, mà S, K, σ đều là giá Binance, còn kết
quả là `giá(T+300) > giá(T)` — cũng Binance. Nên toàn bộ sổ hiệu chỉnh,
đường nắn, và chẩn đoán về chính mô hình dựng được offline, trên bao
nhiêu lịch sử tuỳ ý.

Trước đây không ai nghĩ tới vì sổ hiệu chỉnh được nuôi từ `KetToan` —
tức là chỉ những khung mà bot ĐÃ THEO DÕI mới vào sổ. Ràng buộc đó là
thừa: nó buộc một phép đo về mô hình vào việc bot có kết nối được hay
không.

## Chỉ dựng trong KHUNG ĂN THUA

Mỗi khung `[T, T+300]` lấy nhiều lát cắt (τ = 240, 180, 120, 60, 30s).
Không lấy trong cửa đặt cược: ở đó strike chưa tồn tại và giá trị thật
là đúng 0,5 — xem `scripts/do-cua-nao.py`.

## Điều nó KHÔNG cho biết

Có tiền hay không. Sổ này nói mô hình đoán chuẩn tới đâu; nó không nói
chợ có trả giá sai không, và cũng không nói lệnh có khớp nổi không. Hai
chuyện ấy vẫn phải chờ sổ lệnh thật.
"""
from __future__ import annotations

import math
import statistics
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham.config import CONFIG, DATA_DIR  # noqa: E402
from kham.dinh_gia import HieuChinh, dinh_gia  # noqa: E402
from kham.ket_qua import SoKetQua  # noqa: E402
from kham.nan_lai import ghi_tho, khop  # noqa: E402
from kham.nguon import nguon  # noqa: E402

#: Lát cắt trong khung ăn thua, tính bằng giây CÒN LẠI.
#:
#: CHỈ những mốc rơi đúng ranh giới phút. Nến 1 phút chỉ cho biết giá tại
#: các mốc phút; hỏi giá ở một thời điểm giữa phút thì hoặc phải lấy nến
#: TRƯỚC (giá cũ) hoặc nến SAU (giá của tương lai). Bản đầu lấy nến sau,
#: nên lát τ=30 nhận thẳng giá lúc T+300 — tức là biết trước đáp án. Nó
#: hiện ra thành hai ô đầu và cuối bảng hiệu chỉnh khớp gần như hoàn hảo
#: (lệch −0,000 và −0,008) trên 3.476 mẫu, và tôi suýt đọc đó là mô hình
#: giỏi.
LAT_CAT = (240.0, 180.0, 120.0, 60.0)
PHUT = 60_000.0


def _tham(ten: str, mac_dinh):
    for a in sys.argv[1:]:
        if a.startswith(f"--{ten}="):
            return a.split("=", 1)[1]
    return mac_dinh


THU = "--thu" in sys.argv
SO_NGAY = int(_tham("ngay", "3"))
MA = _tham("ma", "BTC_5M")


def nen_1p(cap: str, tuMs: float, soNen: int) -> list[tuple[float, float]]:
    """`soNen` nến 1 phút liên tiếp kể từ `tuMs`. [(mốc đóng, close)].

    Lấy theo LÔ chứ không từng cái: một khung 5 phút cần 11 mốc giá, và
    hỏi từng mốc một thì 3 ngày dữ liệu là hơn 9.000 lời gọi mạng.
    """
    moc = int(tuMs // PHUT * PHUT)
    ra: list[tuple[float, float]] = []
    con = soNen
    while con > 0:
        lo = min(1000, con)
        d = nguon._lay("binance-kline",
                       f"{CONFIG['nguon']['binanceSpot']}/api/v3/klines",
                       {"symbol": cap, "interval": "1m",
                        "startTime": moc, "limit": lo})
        if not isinstance(d, list) or not d:
            break
        for n in d:
            try:
                ra.append((float(n[0]) + PHUT, float(n[4])))
            except (TypeError, ValueError, IndexError):
                pass
        moc = int(d[-1][0]) + int(PHUT)
        con -= len(d)
        if len(d) < lo:
            break
    return ra


def _sai_tb(cap, nan=None) -> float:
    """Sai số tuyệt đối trung bình theo Ô — cùng thước `HieuChinh` dùng."""
    hc = HieuChinh(duong=Path("/khong-ton-tai/khong-ghi.json"))
    for p, t in cap:
        hc.them(nan.nan(p) if nan is not None else p, t)
    return hc.sai_so_tuyet_doi_tb() or 0.0


def _ngoai_mau(cap: list) -> None:
    """Đường nắn có học được QUY LUẬT không, hay chỉ thuộc bảng.

    Chia theo THỜI GIAN, 70/30. Khớp trên phần đầu, chấm trên phần đuôi
    mà đường khớp chưa từng thấy. Đây là phép kiểm DUY NHẤT phân biệt hai
    chuyện đó, và nếu bỏ nó thì con số "2,82 → 0,85" chỉ là tự chấm bài
    mình: đường nắn khớp từ bảng nào thì tất nhiên khớp với bảng ấy.

    Không chia ngẫu nhiên: bốn lát cắt của cùng một khung có CHUNG một
    kết quả, nên rải chúng hai bên vách là để bên đuôi biết trước đáp án
    của bên đầu.
    """
    n = len(cap)
    if n < 2000:
        print(f"{chr(10)}  NGOÀI MẪU: chỉ {n:,} cặp, chưa đủ để chia. Bỏ qua.")
        return
    cat = int(n * 0.7)
    dau, duoi = cap[:cat], cap[cat:]

    hcDau = HieuChinh(duong=Path("/khong-ton-tai/khong-ghi.json"))
    for p, t in dau:
        hcDau.them(p, t)
    pn = khop(hcDau)

    print()
    print("  NGOÀI MẪU — chia theo THỜI GIAN 70/30")
    print(f"    khớp trên {len(dau):,} cặp đầu, chấm trên {len(duoi):,} "
          "cặp đuôi")
    if not pn.dung_duoc:
        print("    đường khớp từ phần đầu KHÔNG dùng được. Không kết luận.")
        return
    a1, a2 = _sai_tb(dau), _sai_tb(dau, pn)
    b1, b2 = _sai_tb(duoi), _sai_tb(duoi, pn)
    print(f"    phần ĐẦU  (đã thấy)    thô {a1*100:.2f} → nắn {a2*100:.2f} điểm"
          f"   ({'GIẢM' if a2 < a1 else 'TĂNG'})")
    print(f"    phần ĐUÔI (chưa thấy)  thô {b1*100:.2f} → nắn {b2*100:.2f} điểm"
          f"   ({'GIẢM' if b2 < b1 else 'TĂNG'})")
    print()
    if b2 < b1:
        print("    → Phần đuôi KHÁ HƠN: phép nắn học được quy luật, không")
        print("      thuộc bảng. Khoảng cách giữa hai mức giảm chính là phần")
        print("      khớp quá — nay là một con số, không phải một nỗi lo.")
    else:
        print("    → Phần đuôi KHÔNG khá hơn: đường nắn đang THUỘC BẢNG.")
        print("      Đừng bật nó lên. Siết giảm chấn hoặc lấy thêm mẫu.")


def main() -> int:
    cap = next((t.get("nen") for t in CONFIG["thiTruong"]
                if t.get("ma") == MA), None)
    if not cap:
        print(f"\n  Không có market `{MA}` trong config.\n")
        return 1

    hetMs = int(time.time() * 1000.0 // PHUT * PHUT) - PHUT
    soNen = SO_NGAY * 24 * 60 + 10
    tuMs = hetMs - soNen * PHUT

    print()
    print("=" * 74)
    print("  HỌC TỪ BINANCE — sổ hiệu chỉnh không cần chợ")
    print("=" * 74)
    print(f"  {MA} ({cap}) · {SO_NGAY} ngày · lấy {soNen:,} nến 1 phút…",
          flush=True)

    if not THU:
        # `ghi_tho` NỐI THÊM. Không xoá trước thì mỗi lần chạy lại nhân
        # đôi số cặp thô, và phép kiểm ngoài mẫu chia 70/30 trên một danh
        # sách có mỗi cặp hai lần thì phần đuôi chứa đúng thứ phần đầu đã
        # thấy — tự chấm bài mình mà vẫn trông như ngoài mẫu.
        tho = DATA_DIR / "hieu-chinh-tho.jsonl"
        if tho.exists():
            tho.unlink()

    nen = nen_1p(cap, tuMs, soNen)
    if len(nen) < 400:
        print(f"  Chỉ lấy được {len(nen)} nến. Không đủ. Dừng.\n")
        return 1
    print(f"  đã lấy {len(nen):,} nến "
          f"({(nen[-1][0]-nen[0][0])/3_600_000:.1f} giờ)")

    theoMoc = {int(m): g for m, g in nen}
    mocs = sorted(theoMoc)

    # σ ước từ 5 nến trước mốc T — đúng thứ runtime có lúc chạy thật.
    def sigma_tai(T: int) -> float | None:
        gs = [theoMoc.get(T - i * int(PHUT)) for i in range(6)]
        if any(g is None or g <= 0 for g in gs):
            return None
        gs = gs[::-1]
        r = [math.log(gs[i + 1] / gs[i]) for i in range(5)]
        sd = statistics.pstdev(r)
        return (sd / math.sqrt(60.0)) if sd > 0 else None

    # DỰNG LẠI TỪ ĐẦU, không cộng dồn.
    #
    # `HieuChinh()` đọc sổ cũ trên đĩa rồi cộng tiếp vào đó. Chạy script
    # này hai lần là mọi ô nhân đôi: lần thứ hai in ra "80.552 mẫu" trong
    # khi chỉ có 40.276 cặp thật. Sai số trung bình không đổi nên nó KHÔNG
    # lộ ra ở đâu — chỉ có `n` phình lên, mà `n` là thứ quyết định Kelly
    # có được mở hay không.
    #
    # Script này dựng lại toàn bộ sổ từ Binance mỗi lần chạy, nên sổ cũ
    # không có gì đáng giữ.
    hc = HieuChinh()
    hc.o = {}
    soKq = SoKetQua()
    cap_mau = 0
    bo = 0
    # Giữ mọi cặp theo THỨ TỰ THỜI GIAN để còn chia được đầu/đuôi. Chia
    # ngẫu nhiên là gian lận ở đây: hai lát cắt của cùng một khung nằm
    # hai bên vách thì bên đuôi biết trước đáp án của bên đầu.
    cap_theo_thoi: list[tuple[float, bool]] = []
    for T in mocs:
        # Khung [T, T+300]: cần giá tại T và tại T+300.
        K = theoMoc.get(T)
        het = theoMoc.get(T + 5 * int(PHUT))
        if K is None or het is None or abs(het - K) < 1e-12:
            bo += 1
            continue
        sig = sigma_tai(T)
        if sig is None:
            bo += 1
            continue
        thang = het > K
        slug = f"{MA.split('_')[0].lower()}-updown-5m-{T // 1000}"
        soKq.them(slug, thang, K, het, "tu-tinh")
        for tau in LAT_CAT:
            # Giá tại thời điểm còn `tau` giây = mốc T + (300 − tau), và
            # mốc ấy rơi đúng ranh giới phút nên tra thẳng được. KHÔNG
            # làm tròn lên: làm tròn lên là lấy giá của tương lai.
            t = T + int((300.0 - tau) * 1000.0)
            if t % int(PHUT):
                continue
            S = theoMoc.get(t)
            if S is None or S <= 0:
                continue
            gc = dinh_gia(MA, float(S), float(K), tau, sig)
            if gc is None:
                continue
            hc.them(gc.pUp, thang)
            cap_theo_thoi.append((gc.pUp, thang))
            if not THU:
                ghi_tho(gc.pUp, thang, MA)
            cap_mau += 1

    print(f"  dựng {cap_mau:,} cặp (mô hình nói, thực tế ra) · bỏ {bo:,} mốc")
    if not cap_mau:
        print("\n  Không dựng được cặp nào.\n")
        return 1

    print()
    print("  BẢNG HIỆU CHỈNH")
    print("    ô        n      mô hình nói   thực tế ra    lệch")
    for h in hc.bang():
        if not h.get("n"):
            continue
        print(f"    {h['o']:<8} {h['n']:>6}   {h['duDoan']:>10.3f}   "
              f"{h['thucTe']:>10.3f}   {h['lech']:>+7.3f}")
    print()
    sai = hc.sai_so_tuyet_doi_tb()
    print(f"    tổng mẫu {hc.tong_mau:,} · sai số tuyệt đối trung bình "
          f"{(sai or 0)*100:.2f} điểm")
    print(f"    đủ để dùng Kelly: {hc.du_de_dung_kelly()}")

    pn = khop(hc)
    print()
    print(f"  ĐƯỜNG NẮN (trong mẫu): {pn.tongMau:,} mẫu · dùng được "
          f"{pn.dung_duoc} · sai {pn.saiTruoc*100:.2f} → "
          f"{pn.saiSau*100:.2f} điểm")

    _ngoai_mau(cap_theo_thoi)

    if THU:
        print("\n  --thu: KHÔNG ghi sổ.\n")
        return 0
    hc.ghi()
    print(f"\n  Đã ghi {hc.duong}")
    print(f"  Sổ kết quả: {soKq.tom_tat()}")
    print()
    print("  NHẮC: sổ này nói MÔ HÌNH đoán chuẩn tới đâu. Nó KHÔNG nói chợ")
    print("  có trả giá sai không, và cũng không nói lệnh có khớp nổi không.")
    print("  Hai chuyện ấy vẫn phải chờ sổ lệnh thật.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
