"""CHỢ THẬT nằm ở đâu trên thang w — câu treo suốt phiên, nay trả lời được.

    python scripts/do-cho-that.py

`chay-demo.py --quet` dựng một dãy chợ pha giữa hai đầu mút:

    p_chợ = 0,5 + w·(p_mô_hình − 0,5)

w=0 chợ mù, w=1 chợ biết y hệt ta. Phiên giấy hoà vốn quanh w ≈ 1. Câu
còn lại là: **chợ THẬT nằm ở đâu trên thang ấy?**

Suốt phiên câu đó không trả lời được vì băng chưa từng có một dòng sổ
lệnh nào trong khung ăn thua — `_tim_khung` chỉ bám khung đang đặt cược.
Nay có: đường tới Polymarket chập chờn chứ không đứt hẳn, và trong 24
phút thông (14:54–15:18 UTC 29/08) runtime đã ghi được những dòng ấy.

Ít mẫu. Nên phép đo này KHÔNG chốt gì — nó ước lượng, khai rõ khoảng
tin, và nói thẳng là cần bao nhiêu nữa mới chốt được.

## σ trong băng là σ CŨ — nên tính lại

578 dòng ấy được ghi TRƯỚC khi bộ ước σ được sửa. Chúng mang `pUp` tính
từ bộ ước mẫu thô, thứ bị dìm còn 0,875 lần bộ ước lưới phút — σ dìm thì
mô hình TỰ TIN QUÁ, và một mô hình tự tin quá trông như có nhiều lợi thế
hơn thực tế.

Nên phép đo này chấm HAI lần: một lần với `pUp` như đã ghi trong băng,
một lần tính lại bằng bộ ước hiện tại (σ dựng từ nến Binance quanh mốc
khung). Chênh giữa hai lần chính là phần thiên vị mà bộ ước cũ tặng cho
chính mình.

## 1.006 dòng KHÔNG phải 1.006 quan sát

Băng ghi nhịp 2 giây, nên một cửa sổ 5 phút xuất hiện trong hàng chục
dòng. Chấm từng dòng rồi in "1.006 dòng" là trình bày chừng năm chục
quan sát như thể có một nghìn — và Brier trên năm chục sự kiện thì sai
số của chính nó lớn hơn mọi chênh lệch đang bàn.

Đây đúng cái bẫy đã cắn ở `chay_lai` (đếm mỗi cửa sổ 44 lần, ra lãi 2,9
triệu đô trên tài khoản 1.000 đô). Nên: gộp theo SLUG, mỗi cửa sổ một
quan sát, và bootstrap THEO SLUG chứ không theo dòng.

## Ba câu, theo thứ tự

1. **Sổ ấy có thật không**, hay chỉ là thang chờ? Đây là câu chặn: sổ
   không yết giá thì mọi câu sau vô nghĩa.
2. **Chợ định giá tốt tới đâu** — điểm kỹ năng so với tỉ lệ nền, và w
   ước lượng bằng hồi quy p_chợ theo p_mô_hình.
3. **Còn lợi thế ròng nào không** sau spread và phí.
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

import kham  # noqa: F401,E402

from kham import tham_so  # noqa: E402

# Không cờ nào — nhưng vẫn phải TỪ CHỐI cờ lạ. Một cờ gõ sai bị
# nuốt im lặng thì phép đo chạy ở cấu hình khác cấu hình người ta
# yêu cầu, rồi in ra một báo cáo trông hoàn toàn hợp lệ.
tham_so.doc({}, ten='do-cho-that.py')
from kham.bang import NguonKhung, giai_doan_cua  # noqa: E402
from kham.chan_doan import doc_tham_so  # noqa: E402
from kham.chay_lai import dung_so  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.dinh_gia import dinh_gia  # noqa: E402
from kham.hoc_offline import nen_1p, quen_sigma, sigma_tai  # noqa: E402
from kham.ket_qua import moc_tu_slug, so_ket_qua  # noqa: E402


def _p_tinh_lai(dong: list) -> dict:
    """Tính lại `pUp` cho từng dòng bằng bộ ước σ HIỆN TẠI.

    Trả {id(tt): pUp}. Dòng nào không dựng được σ thì vắng mặt — không
    lấp bằng giá trị cũ, vì lấp là trộn hai bộ ước vào một phép đo và
    làm hỏng đúng thứ phép đo này đi tìm.
    """
    cuaSo = float(doc_tham_so("dinhGia.bienDongCuaSoGiay") or 900.0)
    moc = [moc_tu_slug(tt.get("slug") or "") for tt, _su, _sd in dong]
    moc = [m for m in moc if m]
    if not moc:
        return {}
    som, muon = min(moc), max(moc)
    nenTheoCap: dict = {}
    ra: dict = {}
    quen_sigma()
    for tt, _su, _sd in dong:
        ma = tt.get("ma") or ""
        cap = next((t.get("nen") for t in CONFIG["thiTruong"]
                    if t.get("ma") == ma), None)
        T = moc_tu_slug(tt.get("slug") or "")
        S, K = tt.get("giaNen"), tt.get("giaMo")
        tau = tt.get("conLaiGiay")
        if not cap or T is None or not S or not K or tau is None:
            continue
        if cap not in nenTheoCap:
            soNen = int((muon - som) / 60_000.0) + int(cuaSo / 60.0) + 20
            nenTheoCap[cap] = nen_1p(cap, som - cuaSo * 1000.0 - 600_000.0,
                                     max(60, soNen))
        sig = sigma_tai(nenTheoCap[cap], int(T), cuaSo)
        if sig is None:
            continue
        gc = dinh_gia(ma, float(S), float(K), float(tau), sig)
        if gc is not None:
            ra[id(tt)] = gc.pUp
    return ra


def _gop_theo_cua_so(cap: list) -> list:
    """Mỗi CỬA SỔ một quan sát: lấy trung bình giá chợ và `p` trong cửa ấy.

    Không lấy dòng cuối: dòng cuối gần kết quả nhất nên nó dễ nhất, và
    chọn nó là tự cho mình một bài dễ hơn bài thật.
    """
    o: dict = {}
    for slug, g, p, t in cap:
        d = o.setdefault(slug, [0.0, 0.0, 0, t])
        d[0] += g
        d[1] += p
        d[2] += 1
    return [(v[0] / v[2], v[1] / v[2], v[3]) for v in o.values()]


def _cham(cap: list, nhan: str) -> None:
    """Điểm kỹ năng và w, tính THEO CỬA SỔ và kèm khoảng tin.

    `cap` là [(slug, giá chợ, p mô hình, kết quả)].
    """
    import random as _rd

    cs = _gop_theo_cua_so(cap)
    n = len(cs)
    if n < 10:
        print(f"     {nhan}: chỉ {n} cửa sổ — không nói gì được.")
        return
    nen = sum(t for _g, _p, t in cs) / n

    def diem(bo):
        m = len(bo)
        bC = sum((g - t) ** 2 for g, _p, t in bo) / m
        bM = sum((p - t) ** 2 for _g, p, t in bo) / m
        bN = sum((nen - t) ** 2 for _g, _p, t in bo) / m
        return ((bN - bC) / max(1e-9, bN), (bN - bM) / max(1e-9, bN), bC, bM)

    kCho, kMo, bCho, bMo = diem(cs)
    tu = sum((g - 0.5) * (p - 0.5) for g, p, _t in cs)
    mau = sum((p - 0.5) ** 2 for _g, p, _t in cs)
    w = tu / mau if mau > 0 else float("nan")

    # Bootstrap THEO CỬA SỔ — lấy lại theo dòng là giả vờ có nhiều mẫu
    # hơn thực tế, đúng cái bẫy phép đo này vừa sửa.
    rd = _rd.Random(20260830)
    lanC, lanM, lanW = [], [], []
    for _ in range(2000):
        bo = [cs[rd.randrange(n)] for _ in range(n)]
        a, b, _c, _d = diem(bo)
        lanC.append(a)
        lanM.append(b)
        t2 = sum((g - 0.5) * (p - 0.5) for g, p, _t in bo)
        m2 = sum((p - 0.5) ** 2 for _g, p, _t in bo)
        lanW.append(t2 / m2 if m2 > 0 else float("nan"))
    for x in (lanC, lanM, lanW):
        x.sort()
    lo, hi = int(0.025 * 2000), int(0.975 * 2000)

    print(f"     {nhan}   ({n} CỬA SỔ, gộp từ {len(cap):,} dòng)")
    print(f"       kỹ năng chợ    {kCho:+.1%}  "
          f"[{lanC[lo]:+.1%}, {lanC[hi]:+.1%}]")
    print(f"       kỹ năng mô hình{kMo:+.1%}  "
          f"[{lanM[lo]:+.1%}, {lanM[hi]:+.1%}]")
    print(f"       w = {w:.3f}          [{lanW[lo]:.3f}, {lanW[hi]:.3f}]")


def main() -> int:
    dong = []
    for k in NguonKhung(None):
        for tt in (k.get("thiTruong") or []):
            if giai_doan_cua(tt) != "quan-sat":
                continue
            su = dung_so((tt.get("so") or {}).get("UP"), tt.get("ma") or "?", "UP")
            sd = dung_so((tt.get("so") or {}).get("DOWN"), tt.get("ma") or "?",
                         "DOWN")
            if su is None or sd is None:
                continue
            dong.append((tt, su, sd))

    print()
    print("=" * 76)
    print("  CHỢ THẬT NẰM Ở ĐÂU — sổ lệnh khung ăn thua, lần đầu có")
    print("=" * 76)
    print(f"  {len(dong):,} dòng khung ăn thua trong băng")
    if len(dong) < 30:
        print("  Quá ít để nói gì. Cần runtime chạy thêm những lúc mạng thông.\n")
        return 0

    # ── 1. sổ ấy có THẬT không ───────────────────────────────────────
    dungDuoc = [x for x in dong if x[1].dung_duoc or x[2].dung_duoc]
    thangCho = sum(1 for _tt, su, sd in dong
                   if su.trai_ca_bang or sd.trai_ca_bang)
    print()
    print(f"  1. SỔ CÓ THẬT KHÔNG")
    print(f"     dùng được   {len(dungDuoc):>5,} / {len(dong):,} "
          f"({len(dungDuoc)/len(dong):.0%})")
    print(f"     thang chờ   {thangCho:>5,}")
    if not dungDuoc:
        print()
        print("     KHÔNG dòng nào yết giá thật. Khung ăn thua chỉ có thang")
        print("     chờ — nghĩa là cửa ấy KHÔNG giao dịch được, và cả hướng")
        print("     'chuyển sang khung ăn thua' phải xem lại từ đầu.")
        print("=" * 76 + "\n")
        return 0

    sp, giua, sau = [], [], []
    for _tt, su, _sd in dungDuoc:
        b, a = su.best_bid, su.best_ask
        if b is None or a is None or a <= b:
            continue
        sp.append(a - b)
        giua.append((a + b) / 2.0)
        sau.append(sum(m.luong for m in su.ask[:3]))
    if sp:
        print(f"     spread trung vị {statistics.median(sp):.4f} · "
              f"giá giữa trung vị {statistics.median(giua):.3f} · "
              f"sâu 3 mức {statistics.median(sau):,.0f} cổ")

    # ── 2. chợ định giá tốt tới đâu ──────────────────────────────────
    cap = []
    for tt, su, _sd in dungDuoc:
        g = su.giua
        p = tt.get("pUp")
        that = so_ket_qua.lay(tt.get("slug") or "")
        if g is None or p is None or that is None:
            continue
        cap.append((tt.get("slug") or "", float(g), float(p),
                    1 if that else 0))
    print()
    soCuaSo = len({x[0] for x in cap})
    print(f"  2. CHỢ ĐỊNH GIÁ TỐT TỚI ĐÂU   ({soCuaSo} cửa sổ · "
          f"{len(cap):,} dòng)")
    if len(cap) < 30:
        print("     chưa đủ dòng có kết quả để chấm. Khung mới đóng thì kết")
        print("     quả phải chờ — chạy lại `scripts/dung-ket-qua.py` sau.")
        print("=" * 76 + "\n")
        return 0

    _cham(cap, "σ CŨ (như đã ghi trong băng)")

    moi = _p_tinh_lai(dungDuoc)
    cap2 = []
    for tt, su, _sd in dungDuoc:
        g, p = su.giua, moi.get(id(tt))
        that = so_ket_qua.lay(tt.get("slug") or "")
        if g is None or p is None or that is None:
            continue
        cap2.append((tt.get("slug") or "", float(g), float(p),
                     1 if that else 0))
    if len(cap2) >= 30:
        print()
        _cham(cap2, "σ MỚI (tính lại bằng bộ ước hiện tại)")
    else:
        print(f"{chr(10)}     không tính lại được σ cho đủ dòng "
              f"({len(cap2)}) — bỏ qua phần đối chiếu.")

    print()
    print("     Đọc khoảng tin, đừng đọc con số giữa. Với vài chục cửa sổ")
    print("     thì khoảng tin rộng tới mức phần lớn kết luận chưa đứng được.")

    # ── 3. lợi thế ròng ──────────────────────────────────────────────
    from kham.can_loi import can
    from kham.config import CONFIG
    nguong = float(CONFIG["canLoi"]["netEdgeToiThieu"])
    qua = tong = 0
    for tt, su, sd in dungDuoc:
        p = tt.get("pUp")
        if p is None:
            continue
        for ben, pp, so in (("UP", p, su), ("DOWN", 1.0 - p, sd)):
            if not so.dung_duoc:
                continue
            ch = can(tt.get("ma") or "?", ben, "do", pp,
                     float(tt.get("batDinh") or 0.02), so, 100.0)
            if ch is None:
                continue
            tong += 1
            if ch.netEdge >= nguong:
                qua += 1
    print()
    print(f"  3. LỢI THẾ RÒNG   {qua:,}/{tong:,} cơ hội qua sàng "
          f"(ngưỡng {nguong:g})")
    print()
    print(f"  {soCuaSo} CỬA SỔ là rất ít — và cửa sổ mới là đơn vị, không")
    print(f"  phải {len(dong):,} dòng. Đây là ước lượng, không phải kết luận.")
    print("  Đường tới Polymarket chập chờn chứ không đứt hẳn, nên cứ để")
    print("  runtime chạy: mỗi lúc mạng thông là thêm cửa sổ, và khoảng tin")
    print("  hẹp lại.")
    print("=" * 76 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
