"""Chạy một PHIÊN GIẤY trọn vẹn trên băng đã ghi — tiền ảo, kế toán thật.

    python scripts/chay-phat-lai.py
    python scripts/chay-phat-lai.py --von=25000
    python scripts/chay-phat-lai.py --von=100000 --tu=2026-08-25

Dữ liệu là THẬT: sổ lệnh Polymarket thô đã ghi từng khung hình, giá nền
Binance, σ đo được lúc đó, và kết quả từng cửa sổ dựng từ nến Binance.
Không con số nào ở đây do máy bịa ra.

Tiền là ẢO, muốn bao nhiêu thì đặt bấy nhiêu. Kế toán thì đúng như một
hệ thật: giá vốn, phí, lãi lỗ từng cửa sổ, đường vốn, sụt vốn đỉnh-đáy,
tỉ lệ thắng, và cầu dao rủi ro có quyền ngắt giữa chừng.

## Sổ sách viết vào THƯ MỤC RIÊNG

`data/phat-lai/`. Sổ kết toán mô phỏng KHÔNG được lẫn vào sổ thật: một
dòng giả trong sổ thật là một con số sai chảy vào chẩn đoán, vào Kelly,
vào cổng tiến hoá, và không ai gỡ ra được nữa.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))


from kham import tham_so  # noqa: E402

CO = tham_so.doc({
    "mo-lai-moi-ngay": tham_so.BAT,
    "tu": "chỉ chạy băng từ ngày này (YYYY-MM-DD)",
    "von": "vốn ảo ban đầu, USD",
}, ten='chay-phat-lai.py')


VON = CO.lay("von")
MO_LAI = CO.co("mo-lai-moi-ngay")
TU_NGAY = CO.lay("tu")

# Sổ sách của phiên ghi vào thư mục RIÊNG. Tách bằng ĐƯỜNG DẪN, không
# bằng `KTG_DATA_DIR`: băng và sổ kết quả vẫn phải đọc từ chỗ thật, nên
# đổi cả `DATA_DIR` là cắt luôn nguồn dữ liệu của chính phiên này.
RIENG = GOC / "data" / "phat-lai"
RIENG.mkdir(parents=True, exist_ok=True)

import kham  # noqa: F401,E402
from kham import tham_so  # noqa: E402  (đặt lại bảng mã console)
from kham.bang import NguonKhung  # noqa: E402
from kham.config import CONFIG  # noqa: E402
from kham.phat_lai import PhienPhatLai  # noqa: E402


def _khoang_tin(kq) -> None:
    """Khoảng tin 95% cho tổng lãi lỗ, lấy lại THEO CỬA SỔ.

    Một con số "+3,30%" đứng trơ thì đọc như kết luận. Trên BẢY cửa sổ
    nó là tiếng ồn, và chuyện ấy phải hiện ra ngay cạnh con số chứ
    không nằm trong đầu người viết. Cùng luật đã ghi trong CLAUDE.md:
    **bootstrap theo KHUNG, không theo cặp** — bốn lát cắt τ của một
    khung chia chung MỘT kết quả, nên đơn vị lấy lại là cửa sổ.

    Đã có tiền lệ đắt: lấy lại theo cặp cho khoảng tin hẹp hơn 2,18 lần
    và nó ĐÃ làm sai một kết luận đã ghi vào tài liệu.
    """
    import random

    v = list(kq.laiLoTungCuaSo)
    n = len(v)
    if n < 3:
        print(f"    khoảng tin          — chỉ {n} cửa sổ, không nói được gì")
        return
    rd = random.Random(20260830)
    lan = []
    for _ in range(4000):
        lan.append(sum(v[rd.randrange(n)] for _ in range(n)))
    lan.sort()
    lo, hi = lan[int(0.025 * 4000)], lan[int(0.975 * 4000)]
    print(f"    khoảng tin 95%      [{_tien(lo)}, {_tien(hi)}]"
          f"   ({n} cửa sổ)")
    if lo <= 0 <= hi:
        print("      ↳ khoảng tin CHỨA 0 — con số lãi ở trên CHƯA nói được")
        print("        rằng cỗ máy này có lãi. Cần thêm cửa sổ, đừng vặn gì")
        print("        theo nó.")

def _tien(x: float) -> str:
    return f"{'-' if x < 0 else ''}${abs(x):,.2f}"


def main() -> int:
    von = float(VON) if VON else float(CONFIG["ruiRo"]["vonBanDau"])
    print()
    print("=" * 78)
    print("  PHIÊN PHÁT LẠI — dữ liệu THẬT, tiền ẢO, kế toán THẬT")
    print("=" * 78)
    print(f"  vốn ban đầu : {_tien(von)}")
    print(f"  băng        : {'từ ' + TU_NGAY if TU_NGAY else 'toàn bộ'}")
    print(f"  sổ ghi vào  : {RIENG}")
    print()

    p = PhienPhatLai(von=von, thuMucSo=RIENG, moLaiMoiNgay=MO_LAI)
    print(f"  phép nắn    : {p.phepNan.tongMau} mẫu · "
          f"dùng được {p.phepNan.dung_duoc}")
    print()

    t0 = time.time()

    def nhip(kq) -> None:
        print(f"    {kq.soKhungHinh:>7} khung · {kq.soCuaSo:>5} cửa sổ · "
              f"{kq.soKhop:>5} khớp · {kq.soKetToan:>5} kết toán · "
              f"vốn {_tien(kq.von)} · {time.time()-t0:.0f}s", flush=True)

    kq = p.chay(NguonKhung(TU_NGAY), moiBuoc=nhip)

    print()
    print("  " + "─" * 74)
    print(f"  KẾT QUẢ SAU {kq.soKhungHinh:,} KHUNG HÌNH  ({time.time()-t0:.0f}s)")
    print("  " + "─" * 74)
    print(f"    cửa sổ thấy được   {kq.soCuaSo:>10,}")
    print(f"    lệnh đề xuất       {kq.soLenh:>10,}")
    print(f"    khớp               {kq.soKhop:>10,}")
    print(f"    rủi ro từ chối     {kq.soTuChoiRuiRo:>10,}")
    print(f"    cửa sổ kết toán    {kq.soKetToan:>10,}")
    print()
    print(f"    vốn ban đầu        {_tien(kq.von0):>10}")
    print(f"    vốn cuối           {_tien(kq.von):>10}")
    print(f"    lãi lỗ             {_tien(kq.tongLaiLo):>10}   "
          f"({kq.loiNhuanPct:+.2f}%)")
    print(f"    phí đã trả         {_tien(kq.tongPhi):>10}")
    print(f"    đỉnh vốn           {_tien(kq.dinhVon):>10}")
    print(f"    sụt vốn đỉnh-đáy   {kq.sutVonPct:>9.2f}%")
    print(f"    thắng / thua       {kq.soThang:>5,} / {kq.soThua:<5,}  "
          f"({kq.tiLeThang:.1%})")
    print(f"    lỗ nặng nhất       {_tien(kq.thuaLonNhat):>10}")
    if kq.soTreo:
        print(f"    TREO               {_tien(kq.tienTreoUsd):>10}   "
              f"({kq.soTreo} cửa sổ đóng mà không có kết quả — tiền đã "
              f"tiêu, KHÔNG nằm trong con số lãi lỗ trên)")
    if kq.soKetToan:
        print(f"    lãi lỗ mỗi cửa sổ  {_tien(kq.tongLaiLo/kq.soKetToan):>10}")
        _khoang_tin(kq)
    print(f"    số ngày băng       {kq.soNgay+1:>10,}")
    # Phép nắn khai ở ĐẦU là "0 mẫu", và người đọc dễ tưởng nó ấm lên dần
    # trong phiên. Phải khai lại ở CUỐI: sổ hiệu chỉnh của phiên giấy là
    # sổ RIÊNG, khởi đầu rỗng cố ý (dùng bảng nắn khớp trên kết quả phiên
    # chưa thấy là nhìn trộm tương lai), nên với bảy cửa sổ nó chưa bao
    # giờ đủ để bật.
    print(f"    phép nắn cuối phiên {p.phepNan.tongMau:>9,} mẫu · "
          f"{'CÓ dùng' if p.phepNan.dung_duoc else 'KHÔNG bật'}"
          f" · khớp lại {p.soLanKhopNan} lần")
    if not p.phepNan.dung_duoc:
        print("      ↳ con số lãi lỗ trên là của mô hình THÔ, chưa nắn.")
    # VỐN CÓ ẢNH HƯỞNG GÌ KHÔNG — câu này phải trả lời, không thì
    # `--von=100000` cho +0,02% và người đọc kết luận sai.
    duKelly = p.hieuChinh.du_de_dung_kelly()
    print(f"    Kelly              {'BẬT' if duKelly else 'TẮT'}"
          f" ({p.hieuChinh.tong_mau:,} mẫu hiệu chỉnh trong phiên)")
    if not duKelly:
        print("      ↳ Kelly TẮT ⇒ cỡ lệnh ghim ở LÔ SÀN, KHÔNG theo vốn.")
        print("        Nên đổi `--von` chỉ đổi mẫu số của phần trăm, không")
        print("        đổi một lệnh nào: $1.000 và $100.000 cho ĐÚNG cùng")
        print("        một chuỗi lệnh và cùng số đô lãi lỗ.")
        print("        Đây là chủ ý: Kelly trên một xác suất chưa ai kiểm")
        print("        thì khuếch đại chính sai lầm của mô hình. Sổ hiệu")
        print("        chỉnh của phiên khởi đầu RỖNG (cố ý, để khỏi nhìn")
        print("        trộm tương lai), nên nó nguội suốt phiên ngắn.")
        print("        Máy CHẠY THẬT thì khác: nó có sổ hiệu chỉnh tích")
        print("        sẵn, Kelly mở, và cỡ lệnh CÓ theo vốn.")
    print()

    if not kq.soCuaSo:
        print("  ⚠ BĂNG NÀY KHÔNG CÓ DÒNG NÀO THUỘC KHUNG ĂN THUA.")
        print()
        print("    Phiên chỉ chạy trên dòng `giaiDoan == quan-sat` — nơi")
        print("    strike đã cố định và mô hình định giá được. Dòng cửa đặt")
        print("    cược mang `giaMo` = giá lúc T−300, và đó KHÔNG phải strike")
        print("    (xem scripts/do-strike.py). Định giá bằng nó rồi chấm bằng")
        print("    sổ kết quả đúng thì ra +191% với tỉ lệ thắng 26% — một con")
        print("    số thuyết phục về không có gì.")
        print()
        print("    Băng tám ngày đầu chỉ có cửa đặt cược, vì `_tim_khung` chưa")
        print("    bao giờ bám khung đang ăn thua. Runtime nay có bám; chạy")
        print("    tiếp vài ngày rồi phiên này mới có gì để đo.")
        print()

    if kq.boQua:
        print("  VÌ SAO ĐỨNG NGOÀI (nhiều nhất trước):")
        for ly, n in sorted(kq.boQua.items(), key=lambda x: -x[1])[:8]:
            print(f"    {n:>9,} × {ly}")
        print()
    if kq.lyDoTuChoi:
        print("  RỦI RO TỪ CHỐI VÌ:")
        for ly, n in sorted(kq.lyDoTuChoi.items(), key=lambda x: -x[1])[:8]:
            print(f"    {n:>9,} × {ly}")
        print()

    # ── CỬA NÀO CHƯA CHẶN LẦN NÀO ─────────────────────────────────────
    #
    # Một cửa không bao giờ chạy thì không phân biệt được với một cửa
    # hỏng. Đo ngày 30/08/2026: phiên 152.329 khung hình chỉ chạm 5
    # trong 13 cửa, và tám cửa im lặng là gần như trọn phần GIỮ VỐN —
    # trần mỗi thị trường, trần nhóm, trần phơi nhiễm gộp, ngân sách lỗ
    # ngày. Hạ vốn xuống $60 cũng không đánh thức được chúng: chúng chỉ
    # chặn khi tồn kho đã tích tới trần, mà băng này chỉ có 22 cửa sổ
    # trong 9 ngày nên vị thế đóng trước khi chồng lên nhau.
    #
    # In ra mỗi lượt, chứ không để ai phải đi hỏi. Đây là một GIỚI HẠN
    # của phiên giấy, không phải một lỗi — nhưng nó phải nhìn thấy được.
    from kham.rui_ro import CUA_RUI_RO
    im = [m for m in CUA_RUI_RO if not kq.cuaDaChan.get(m)]
    print(f"  CỬA RỦI RO: {len(CUA_RUI_RO) - len(im)}/{len(CUA_RUI_RO)}"
          f" cửa đã chặn ít nhất một lần")
    if im:
        print("    CHƯA CHẶN LẦN NÀO trong phiên này — chưa được chạy thật:")
        for m in im:
            print(f"      · {m:<20} {CUA_RUI_RO[m]}")
        print("    (chúng có phép kiểm đơn vị; đây là khoảng trống ĐẦU-CUỐI)")
    print()

    if kq.ngatLucKhung:
        con = kq.soKhungHinh - kq.ngatLucKhung
        print(f"  ⚠ CẦU DAO NGẮT ở khung {kq.ngatLucKhung:,} — {kq.ngatLyDo}")
        print(f"    còn {con:,} khung ({con/max(1,kq.soKhungHinh):.0%} băng) chạy "
              f"sau đó mà KHÔNG đặt lệnh nào.")
        if not MO_LAI:
            print("    Cầu dao không tự phục hồi — đó là chủ ý. Muốn mô phỏng")
            print("    một người sáng nào cũng mở lại: --mo-lai-moi-ngay")
        print(f"    số lần ngắt {p.risk.soLanNgat} · số lần mở lại {kq.soLanMoLai}")
        print()

    print("  Đọc con số này như một CẬN TRÊN. Ba thứ phiên giấy không có:")
    print("    · tác động thị trường — sổ đã ghi không biết ta tồn tại")
    print("    · trượt giá theo thời gian — lệnh thật mất quãng nửa giây")
    print("      mới tới sàn, `do_tre.py` đã đo")
    print("    · chọn lọc bất lợi — người bán ở giá đó có thể biết thứ ta chưa")
    print("=" * 78)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
