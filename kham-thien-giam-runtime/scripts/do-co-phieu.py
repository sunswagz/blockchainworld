"""Mô hình Φ(z) có kỹ năng trên NGƯỠNG GIÁ CỔ PHIẾU không?

    python scripts/do-co-phieu.py
    python scripts/do-co-phieu.py --ngay-toi-han=5 --lui=750

## Vì sao đo họ này trước khi dựng động cơ cho nó

`sang-ho-market.py` đếm 1.500 market đang mở ngày 05/09/2026: **690 là
ngưỡng giá cổ phiếu / chỉ số / hàng hoá**, lớn hơn cả crypto (349). Và
slug của chúng —

    aapl-above-290-on-september-4-2026
    will-nvda-reach-200-by-august-31-2026

— là ĐÚNG hình dạng `dinh_gia.py` đang chạy cho crypto: một giá, một
mốc, một hạn, rồi Φ(z). Đổi nguồn giá là xong phần lớn việc.

Nhưng "cùng công thức" KHÔNG có nghĩa là "cùng kỹ năng". Với crypto,
mô hình hơn tỉ lệ nền vì σ ước từ nến phút bắt được chế độ biến động
đang chạy. Cổ phiếu có ba thứ crypto không có, và cả ba đều bẻ Φ(z):

  · **phiên đóng cửa** — giá nhảy qua đêm, và cú nhảy ấy không nằm
    trong σ ước từ giá đóng-đến-đóng;
  · **lịch công bố** — báo cáo quý làm σ của một ngày cụ thể khác hẳn
    σ trung bình, mà mô hình không biết ngày nào;
  · **đuôi dày và lệch** — chỉ số rơi nhanh hơn lên.

Nên phải ĐO, và đo trước khi viết một dòng động cơ nào.

## Cách đo

Với mỗi mã, mỗi phiên `t`: hỏi "giá đóng phiên `t+h` có vượt `K`
không". Mốc `K` rải quanh giá hiện tại theo bội số của σ√τ để quét đủ
dải |z| — chính chỗ |z| nhỏ mới là chỗ có tiền, y như đã thấy ở họ
nhiệt độ (|z| lớn cho kỹ năng +84% ở nơi chợ yết 0,99).

Bốn chỗ dễ tự lừa, đã bịt:

1. **Nhìn trộm tương lai.** σ ước trên cửa sổ kết thúc TRƯỚC `t`. Lệch
   một phiên ở đây là đủ để mọi con số thành rác.
2. **Khối bootstrap là TUẦN, gộp mọi mã.** Hai mã khác nhau trong cùng
   một ngày KHÔNG độc lập — chúng chia chung một nhân tố thị trường.
   Rút từng cặp rời sẽ cho khoảng tin hẹp giả.
3. **σ phải ước trên CỬA SỔ TRƯỢT.** Ở họ nhiệt độ, ước một lần trên
   60% dữ liệu cũ rồi dùng cho 40% mới cho kỹ năng −10,2% — TỆ HƠN tỉ
   lệ nền có ý nghĩa. Chế độ biến động đổi, và một hằng số học từ chế
   độ khác là một phép chỉnh sai.
4. **Hai quãng KHÔNG chồng lấn.** Một quãng đẹp là một lần rút thăm.

## KẾT QUẢ 05/09/2026 — và nó là một câu TRẢ LỜI KHÔNG

10 mã (AAPL MSFT NVDA TSLA AMZN GOOGL META SPY QQQ MU), 60.240 cặp,
~107 khối tuần mỗi lượt. Ô |z| < 0,25 — ô DUY NHẤT có tiền:

    kỳ hạn   quãng        kỹ năng   khoảng tin 95%
    1 phiên  gần đây        +0,5%   [−0,3%, +1,3%]   CHỨA 0
    1 phiên  lùi 565 phiên  +0,7%   [+0,1%, +1,3%]   hẳn dương, sát mép
    5 phiên  gần đây        −1,1%   [−3,8%, +1,5%]   CHỨA 0
    5 phiên  lùi 565 phiên  −1,3%   [−4,5%, +2,0%]   CHỨA 0

Và nó KHÔNG phải chuyện vặn tham số: đổi cửa sổ ước σ sang 20 / 40 /
120 phiên đều cho +0,4% / +0,5% / +0,5%, cả ba đều chứa 0.

Ô kế bên thì có thật và lặp lại được:

    |z| 0,25–0,5   +7,7% / +7,7% (1 phiên)   +5,0% / +4,7% (5 phiên)

cả bốn lượt đều hẳn bên dương. Nhưng đó là chỗ Φ(z) rơi vào 0,60–0,69,
tức chỗ chợ cũng không khó đoán — và bảng này không đo được chợ.

**Kết luận cho lộ trình: ĐỪNG dựng động cơ cổ phiếu chỉ vì nó là họ
đông nhất.** 690 market là con số của bảng SÀNG, không phải của bảng
KỸ NĂNG. So với họ nhiệt độ ở đúng ô ấy (+1,9%, hai quãng không chồng
lấn đều dương), cổ phiếu tệ hơn — và nhiệt độ đã là nhỏ.

Điều bảng này KHÔNG nói: rằng giá cổ phiếu không đoán được. Nó nói ĐÚNG
một chuyện — mô hình log-chuẩn với σ ước từ giá đóng không có lợi thế ở
tiền. Ba đường còn chưa thử, và cả ba đều nhắm vào σ chứ không vào Φ:
biến động NGỤ Ý từ quyền chọn, GARCH, và lịch công bố báo cáo quý. Ai
thử thì đo lại bằng chính script này, hai quãng không chồng lấn.

## Nó KHÔNG trả lời điều gì

Không nói mô hình có hơn GIÁ CHỢ không — để trả lời câu ấy phải có giá
chợ lúc phán, và Polymarket không cho lịch sử giá của những market này.
Đây là điều kiện CẦN: thua cả tỉ lệ nền thì khỏi bàn tiếp.
"""
from __future__ import annotations

import math
import random
import statistics
import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "ma": "danh sách mã, ngăn bằng dấu phẩy",
    "ngay-toi-han": "hỏi giá đóng cửa sau bao nhiêu PHIÊN",
    "cua-so": "số phiên dùng để ước σ",
    "lui": "bỏ qua bấy nhiêu phiên CUỐI — để đo một quãng CŨ, không "
           "chồng lấn với quãng vừa đo",
    "so-phien": "chỉ dùng bấy nhiêu phiên gần nhất (sau khi đã lùi)",
}, ten='do-co-phieu.py')

#: Mã đem đo. Trộn cổ phiếu đơn lẻ, chỉ số và một quỹ — ba thứ có đuôi
#: khác hẳn nhau, và một kết luận đúng cho AAPL chưa chắc đúng cho SPY.
MA_MAC_DINH = "AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL,META,SPY,QQQ,MU"

MA = [x.strip().upper() for x in CO.lay("ma", MA_MAC_DINH).split(",")
      if x.strip()]
TOI_HAN = int(CO.lay("ngay-toi-han", "1"))
CUA_SO = int(CO.lay("cua-so", "60"))
LUI = int(CO.lay("lui", "0"))
SO_PHIEN = int(CO.lay("so-phien", "500"))

#: Mốc rải theo bội số của σ√τ. Đối xứng quanh 0 để không lẫn kỹ năng
#: với một thiên lệch một chiều.
BOI = (-2.0, -1.5, -1.0, -0.6, -0.3, -0.1, 0.1, 0.3, 0.6, 1.0, 1.5, 2.0)

#: Gom theo |z|. Ô đầu là ô DUY NHẤT có tiền — chỗ chợ chưa chắc.
O_Z = ((0.0, 0.25), (0.25, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.5))

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/"


def _client():
    import httpx
    return httpx.Client(
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (compatible; kham-thien-giam/0.1)"})


def lay_gia(c, ma: str, lanThu: int = 8) -> list[tuple[int, float]] | None:
    """[(ngày unix, giá đóng)] — 5 năm phiên ngày. None khi chịu.

    Thử lại nhiều lượt: đường ra của máy này chập chờn ở khâu MỞ kết
    nối chứ không phải bị chặn (xem `//proxyChanDoan` trong config).
    """
    for i in range(lanThu):
        try:
            r = c.get(YAHOO + ma, params={"range": "5y", "interval": "1d"})
            r.raise_for_status()
            d = r.json()["chart"]["result"][0]
            ts = d["timestamp"]
            dong = d["indicators"]["quote"][0]["close"]
            ra = [(int(t), float(g)) for t, g in zip(ts, dong)
                  if g is not None and g > 0]
            return ra or None
        except Exception:                            # noqa: BLE001
            if i == lanThu - 1:
                return None
            time.sleep(min(4.0, 0.5 * (i + 1)))
    return None


def sigma_tai(gia: list, i: int, soPhien: int) -> float | None:
    """σ MỖI PHIÊN, ước trên `soPhien` phiên KẾT THÚC TRƯỚC `i`.

    `gia[i]` KHÔNG được tham gia: nó là giá lúc quyết định, và log-return
    dẫn tới nó chứa thông tin của phiên đang xét. Lấy nhầm một phiên ở
    đây là nhìn trộm, và nó cho một kết quả rất đẹp.
    """
    if i - soPhien - 1 < 0:
        return None
    c = [gia[j][1] for j in range(i - soPhien - 1, i)]
    r = [math.log(c[k + 1] / c[k]) for k in range(len(c) - 1)]
    if len(r) < 10:
        return None
    sd = statistics.pstdev(r)
    return sd if sd > 0 else None


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def dung_cap(gia: list, soPhien: int, toiHan: int) -> list[dict]:
    """Sinh (p mô hình, kết quả thật, z, tuần) cho mọi phiên dùng được."""
    ra = []
    for i in range(soPhien + 2, len(gia) - toiHan):
        sg = sigma_tai(gia, i, soPhien)
        if sg is None:
            continue
        S = gia[i][1]
        het = gia[i + toiHan][1]
        tau = float(toiHan)
        sq = sg * math.sqrt(tau)
        if sq <= 0:
            continue
        tuan = time.strftime("%Y-W%W", time.gmtime(gia[i][0]))
        for b in BOI:
            K = S * math.exp(b * sq)
            # z của mô hình chuẩn log-chuẩn không trôi:
            #     P(S_T > K) = Φ( (ln(S/K) − σ²τ/2) / (σ√τ) )
            z = (math.log(S / K) - 0.5 * sg * sg * tau) / sq
            ra.append({"p": _phi(z), "that": het > K, "z": z, "tuan": tuan})
    return ra


def khoang_tin(hieu: list, khoi: list, n: int = 4000, hat: int = 5):
    """Bootstrap chia KHỐI. Khối = TUẦN, gộp mọi mã.

    Hai mã khác nhau trong cùng một ngày KHÔNG độc lập — chúng chia
    chung một nhân tố thị trường. Rút từng cặp rời cho khoảng tin hẹp
    giả, và cái hẹp giả ấy sẽ nói "có ý nghĩa" về một thứ không có.
    """
    theo: dict = {}
    for h, k in zip(hieu, khoi):
        theo.setdefault(k, []).append(h)
    ks = list(theo.values())
    if len(ks) < 8:
        return None
    rng = random.Random(hat)
    tb = []
    for _ in range(n):
        m = []
        for _ in range(len(ks)):
            m.extend(rng.choice(ks))
        tb.append(statistics.fmean(m))
    tb.sort()
    return tb[int(0.025 * n)], tb[int(0.975 * n)], len(ks)


def main() -> int:
    print()
    print("=" * 78)
    print("  MÔ HÌNH Φ(z) TRÊN NGƯỠNG GIÁ CỔ PHIẾU — CÓ KỸ NĂNG KHÔNG?")
    print("=" * 78)
    print(f"  {len(MA)} mã · tới hạn {TOI_HAN} phiên · σ trên {CUA_SO} phiên"
          f" · lùi {LUI} phiên · dùng {SO_PHIEN} phiên")
    print()

    c = _client()
    cap: list[dict] = []
    hong = []
    for ma in MA:
        g = lay_gia(c, ma)
        if not g:
            hong.append(ma)
            continue
        if LUI:
            g = g[:-LUI] if LUI < len(g) else []
        g = g[-(SO_PHIEN + CUA_SO + TOI_HAN + 4):]
        n0 = len(cap)
        cap.extend(dung_cap(g, CUA_SO, TOI_HAN))
        print(f"    {ma:<7} {len(g):>5} phiên → {len(cap) - n0:>6} cặp",
              flush=True)
    if hong:
        print(f"    KHÔNG lấy được: {', '.join(hong)}")
    if len(cap) < 500:
        print(f"\n  chỉ {len(cap)} cặp. Không đủ để nói gì.\n")
        return 1

    print()
    print(f"  {len(cap):,} cặp · "
          f"{len({x['tuan'] for x in cap}):,} khối tuần")
    print()
    print(f"    {'|z|':<12}{'số cặp':>9}{'tỉ lệ nền':>11}{'Brier MH':>10}"
          f"{'Brier nền':>11}{'kỹ năng':>9}   khoảng tin 95%")
    print("    " + "─" * 86)

    for lo, hi in O_Z:
        o = [x for x in cap if lo <= abs(x["z"]) < hi]
        if len(o) < 200:
            print(f"    {f'{lo:g}–{hi:g}':<12}{len(o):>9}   (chưa đủ cặp)")
            continue
        that = [1.0 if x["that"] else 0.0 for x in o]
        nen = statistics.fmean(that)
        bMH = [(x["p"] - t) ** 2 for x, t in zip(o, that)]
        bNen = [(nen - t) ** 2 for t in that]
        hieu = [a - b for a, b in zip(bMH, bNen)]
        kt = khoang_tin(hieu, [x["tuan"] for x in o])
        ky = (1 - statistics.fmean(bMH) / statistics.fmean(bNen)
              if statistics.fmean(bNen) > 0 else float("nan"))
        # Khoảng tin của HIỆU Brier (mô hình − nền). ÂM là tốt, nên đổi
        # dấu và đảo mép để đọc cùng chiều với cột kỹ năng.
        if kt is None:
            ct = "  (chưa đủ khối)"
        else:
            lo2, hi2, sk = kt
            bn = statistics.fmean(bNen)
            ct = (f"  [{-hi2 / bn * 100:+6.1f}%, {-lo2 / bn * 100:+6.1f}%]"
                  f"  {sk} khối"
                  + ("   ← HẲN BÊN DƯƠNG" if hi2 < 0 else
                     "   ← CHỨA 0" if lo2 < 0 < hi2 else
                     "   ← HẲN BÊN ÂM"))
        print(f"    {f'{lo:g}–{hi:g}':<12}{len(o):>9}{nen:>11.3f}"
              f"{statistics.fmean(bMH):>10.4f}{statistics.fmean(bNen):>11.4f}"
              f"{ky * 100:>8.1f}%{ct}")

    print()
    print("  ĐỌC KỸ: ô |z| LỚN cho kỹ năng đẹp một cách vô nghĩa — ở đó")
    print("  chợ cũng yết 0,99 và không ai trả tiền cho ta vì biết điều")
    print("  hiển nhiên. Ô ĐẦU (|z| < 0,25) là ô duy nhất có tiền, và ở")
    print("  họ nhiệt độ nó chỉ cho +1,9%.")
    print()
    print("  Và bảng này KHÔNG nói mô hình hơn GIÁ CHỢ — nó chỉ nói mô")
    print("  hình hơn TỈ LỆ NỀN. Đó là điều kiện CẦN: thua cả tỉ lệ nền")
    print("  thì khỏi bàn tiếp.")
    print()
    print("  Chạy lại với `--lui` bằng số phiên vừa dùng để có một quãng")
    print("  KHÔNG CHỒNG LẤN. Một quãng đẹp là một lần rút thăm.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
